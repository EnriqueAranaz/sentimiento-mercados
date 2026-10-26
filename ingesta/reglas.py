"""Reglas mecánicas de clasificación (fase 2, parte A).

Se ejecutan al final de cada ingesta sobre los artículos nuevos y dejan:
  - `detecciones`: pistas de empresas (por alias o símbolo de TradingView), mercados y objetos globales;
  - `clasificacion`: SOLO para cripto (relevante = false, motivo 'Cripto', metodo 'reglas').
Tono, origen, tema y relevancia del resto los decide el agente clasificador (ver docs/criterios_clasificacion.md).

Uso manual, sobre todos los artículos ya guardados:
    python -m ingesta.reglas --todos
"""
from __future__ import annotations

import logging
import re
import sys
import unicodedata
from dataclasses import dataclass

log = logging.getLogger("ingesta.reglas")

VERSION_CRITERIOS = "v3"  # versión de docs/criterios_clasificacion.md (modelo del Excel v3, 26/10/2026)

# Alias que también son palabras comunes en español: solo cuentan escritos con la mayúscula del nombre.
ALIAS_SENSIBLES = {"Meta", "Dia", "DIA", "Visa", "Colonial", "Acciona", "Continental", "BAT", "Orange", "ING"}

MERCADOS = [  # (objeto, patrón sobre el titular normalizado en minúsculas)
    ("Ibex 35", r"\bibex\b"),
    ("DAX", r"\bdax\b"),
    ("Europa", r"\beuro\s*stoxx\b|\bstoxx\b|\bbolsas europeas\b|\bparques europeos\b"),
    ("EE. UU.", r"\bwall street\b|\bs p\b|\bs p 500\b|\bnasdaq\b|\bdow jones\b"),
    ("Francia", r"\bcac\b"),
    ("Reino Unido", r"\bftse\b"),
    ("Japón", r"\bnikkei\b|\btopix\b"),
    ("Corea", r"\bkospi\b"),
    ("Asia", r"\bhang seng\b|\bbolsas asiaticas\b|\bmercados asiaticos\b"),
]
GLOBALES = [
    ("Petróleo", r"\bpetroleo\b|\bbrent\b|\bcrudo\b|\bwti\b|\bopep\b"),
    ("Materias primas", r"\boro\b|\bplata\b|\bcobre\b|\baluminio\b|\bniquel\b|\blitio\b|\bmaterias primas\b"
                        r"|\btrigo\b|\bcacao\b"),
    ("Divisas", r"\beuro\s+dolar\b|\beurodolar\b|\b(el|del) (euro|dolar)\b|\byen\b|\byuan\b|\blibra esterlina\b"
                r"|\bfranco suizo\b|\bdivisas?\b"),
    ("Economía", r"\beconomia (mundial|global)\b|\bfmi\b|\brecesion (mundial|global)\b"),
    ("Mercados", r"\b(bolsas|mercados) (mundiales|globales)\b"),
]
SECCIONES_CRIPTO = {"news/Beincrypto", "news/Cointelegraph"}
CRIPTO = re.compile(
    r"\b(bitcoin|btc|ethereum|ether|xrp|ripple|solana|dogecoin|cardano|stablecoins?|criptomonedas?|criptodivisas?"
    r"|criptoactivos?|cripto|memecoins?|altcoins?|etf (de|sobre) bitcoin)\b"
)


def transformar(texto: str) -> str:
    """Quita tildes y cambia la puntuación por espacios, conservando longitud y mayúsculas."""
    return "".join(
        (unicodedata.normalize("NFKD", c)[0] if c.isalnum() else " ") for c in texto
    )


@dataclass
class _Alias:
    regex: re.Pattern
    empresa: dict
    sensible: bool


def compilar_alias(empresas: list[dict]) -> list[_Alias]:
    out = []
    for e in empresas:
        for alias in e.get("alias") or [e["nombre"]]:
            tokens = transformar(alias).split()
            if not tokens:
                continue
            sensible = alias in ALIAS_SENSIBLES
            cuerpo = r"\s+".join(re.escape(t if sensible else t.lower()) for t in tokens)
            out.append(_Alias(re.compile(rf"(?<![A-Za-z0-9]){cuerpo}(?![A-Za-z0-9])"), e, sensible))
    return out


def detectar(articulo: dict, alias: list[_Alias], por_ticker: dict[str, dict]) -> tuple[list[dict], bool]:
    """Devuelve (detecciones, es_cripto) para un artículo {id, titulo, seccion, simbolos}."""
    titulo = transformar(articulo.get("titulo") or "")
    minus = titulo.lower()
    candidatos = []
    for a in alias:
        for m in a.regex.finditer(titulo if a.sensible else minus):
            candidatos.append((m.start(), m.end(), a.empresa))
    # Solapes: gana el alias más largo ("Acciona Energía" frente a "Acciona").
    candidatos.sort(key=lambda c: c[1] - c[0], reverse=True)
    ocupado: list[tuple[int, int]] = []
    vistos: dict[str, dict] = {}
    for ini, fin, emp in candidatos:
        if any(ini < f and fin > i for i, f in ocupado):
            continue
        ocupado.append((ini, fin))
        vistos.setdefault(emp["nombre"], {"tipo": "empresa", "empresa_id": emp["id"], "objeto": emp["nombre"],
                                          "metodo": "alias"})
    for s in articulo.get("simbolos") or []:
        emp = por_ticker.get(s.upper())
        if emp:
            vistos.setdefault(emp["nombre"], {"tipo": "empresa", "empresa_id": emp["id"], "objeto": emp["nombre"],
                                              "metodo": "simbolo"})
    dets = list(vistos.values())
    for tipo, lista in (("mercado", MERCADOS), ("global", GLOBALES)):
        for objeto, patron in lista:
            if re.search(patron, minus):
                dets.append({"tipo": tipo, "empresa_id": None, "objeto": objeto, "metodo": "palabra"})
    es_cripto = articulo.get("seccion") in SECCIONES_CRIPTO or bool(CRIPTO.search(minus))
    return dets, es_cripto


def cargar_empresas(db) -> list[dict]:
    return db.table("empresas").select("id,nombre,alias,ticker").execute().data


def aplicar(db, articulos: list[dict], empresas: list[dict] | None = None) -> dict:
    """Aplica las reglas a `articulos` ({id, titulo, seccion, simbolos}) y guarda detecciones y cripto."""
    empresas = empresas if empresas is not None else cargar_empresas(db)
    alias = compilar_alias(empresas)
    por_ticker = {e["ticker"].upper(): e for e in empresas if e.get("ticker")}
    detecciones, cripto = [], []
    for art in articulos:
        dets, es_cripto = detectar(art, alias, por_ticker)
        detecciones += [{"articulo_id": art["id"], **d} for d in dets]
        if es_cripto:
            cripto.append({"articulo_id": art["id"], "relevante": False, "motivo_no_relevante": "Cripto",
                           "metodo": "reglas", "version_criterios": VERSION_CRITERIOS})
    for i in range(0, len(detecciones), 500):
        db.table("detecciones").upsert(detecciones[i:i + 500], on_conflict="articulo_id,tipo,objeto",
                                       ignore_duplicates=True).execute()
    for i in range(0, len(cripto), 500):  # nunca pisa una clasificación existente (p. ej. manual)
        db.table("clasificacion").upsert(cripto[i:i + 500], on_conflict="articulo_id",
                                         ignore_duplicates=True).execute()
    return {"articulos": len(articulos), "detecciones": len(detecciones), "cripto": len(cripto),
            "con_empresa": len({d["articulo_id"] for d in detecciones if d["tipo"] == "empresa"})}


def main() -> int:
    import os
    from pathlib import Path

    from dotenv import load_dotenv
    from supabase import create_client

    if "--todos" not in sys.argv:
        print(__doc__)
        return 2
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)-7s %(message)s", datefmt="%H:%M:%S")
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
    db = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"])
    empresas = cargar_empresas(db)
    total, desde = {"articulos": 0, "detecciones": 0, "cripto": 0, "con_empresa": 0}, 0
    while True:
        lote = (db.table("articulos").select("id,titulo,seccion,simbolos").order("id")
                .range(desde, desde + 999).execute().data)
        if not lote:
            break
        for k, v in aplicar(db, lote, empresas).items():
            total[k] += v
        desde += len(lote)
        log.info("reglas · %d artículos procesados", desde)
    log.info("reglas · total: %s", total)
    return 0


if __name__ == "__main__":
    sys.exit(main())
