"""Valida y carga en Supabase un lote clasificado por el agente (clasificacion/lotes/clasificado_<n>.json).

Formato de entrada:
{
  "lote": 7, "version_criterios": "v3.5",
  "clasificaciones": [
    {"articulo_id": 123, "relevante": true, "tema": "Resultados", "origen": "Hecho (empresa o dato oficial)",
     "afectaciones": [{"ambito": "Empresa", "objeto": "Santander", "sector": "Banca", "valor": 1}]},
    {"articulo_id": 124, "relevante": false, "motivo_no_relevante": "Cripto"}
  ],
  "empresas_nuevas": [{"nombre": "Elecnor", "sector": "Construcción e infraestructuras", "ticker": "BME:ENO",
                       "en_universo": false, "comentario": "..."}]
}

Validación (si un artículo no la pasa, no se carga y se lista en <fichero>.rechazados.json):
  catálogos exactos · valor entre -2 y 2 · sector obligatorio en Sector y Empresa (y vacío en Global y Mercado) ·
  empresa existente o anotada en empresas_nuevas · relevante con ≥1 afectación · no relevante con motivo.
Los válidos se guardan con metodo 'manual' y version_criterios; si ya había clasificación, se sustituye.

Uso:  python clasificacion/cargar.py clasificacion/lotes/clasificado_7.json
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from comun import (AMBITOS, LOTES, OBJETOS_GLOBAL, VERSION_CRITERIOS, IndiceEmpresas, catalogos, clave,
                   conectar, todas)

PROPUESTAS = LOTES / "empresas_nuevas_propuestas.json"


def validar(c: dict, cat: dict, idx: IndiceEmpresas, nuevas: dict, ids_validos: set[int]) -> tuple[list[str], list]:
    """Devuelve (errores, afectaciones normalizadas)."""
    err, afs = [], []
    if c.get("articulo_id") not in ids_validos:
        return [f"articulo_id {c.get('articulo_id')} no existe"], []
    if not isinstance(c.get("relevante"), bool):
        return ["'relevante' debe ser true o false"], []
    if not c["relevante"]:
        if c.get("motivo_no_relevante") not in cat["motivos_no_relevancia"]:
            err.append(f"motivo no válido: {c.get('motivo_no_relevante')!r}")
        if c.get("tema") or c.get("origen") or c.get("afectaciones"):
            err.append("una noticia no relevante no lleva tema, origen ni afectaciones")
        return err, []
    if c.get("motivo_no_relevante"):
        err.append("una noticia relevante no lleva motivo de no relevancia")
    if c.get("tema") not in cat["temas"]:
        err.append(f"tema no válido: {c.get('tema')!r}")
    if c.get("origen") not in cat["origenes"]:
        err.append(f"origen no válido: {c.get('origen')!r}")
    if not c.get("afectaciones"):
        err.append("una noticia relevante necesita al menos 1 afectación")
    vistos = set()
    for i, a in enumerate(c.get("afectaciones") or [], 1):
        p = f"afectación {i}:"
        amb, obj, sec, val = a.get("ambito"), (a.get("objeto") or "").strip(), a.get("sector"), a.get("valor")
        if amb not in AMBITOS:
            err.append(f"{p} ámbito no válido {amb!r}")
            continue
        if not isinstance(val, int) or isinstance(val, bool) or not -2 <= val <= 2:
            err.append(f"{p} valor {val!r} fuera de -2..2")
        empresa_id = None
        if amb in ("Global", "Mercado"):
            if sec:
                err.append(f"{p} {amb} no lleva sector")
            if amb == "Global" and obj not in OBJETOS_GLOBAL:
                err.append(f"{p} objeto de Global no válido {obj!r} (válidos: {', '.join(OBJETOS_GLOBAL)})")
            if amb == "Mercado" and not obj:
                err.append(f"{p} Mercado sin objeto")
            sec = None
        else:
            if sec not in cat["sectores"]:
                err.append(f"{p} sector obligatorio y válido en {amb}; recibido {sec!r}")
            if amb == "Sector":
                obj = obj or sec
                if obj != sec:
                    err.append(f"{p} en Sector el objeto debe ser el sector ({sec!r}), no {obj!r}")
            else:
                emp = idx.buscar(a.get("empresa"), obj, a.get("ticker"))
                if emp:
                    empresa_id, obj = emp["id"], emp["nombre"]
                    if sec != emp["sector"]:
                        err.append(f"{p} {obj} es del sector {emp['sector']!r}, no {sec!r}")
                elif clave(obj) not in nuevas:
                    err.append(f"{p} empresa desconocida {obj!r}: usar el nombre de la tabla o anotarla en empresas_nuevas")
        if (amb, obj) in vistos:
            err.append(f"{p} afectación repetida ({amb} · {obj})")
        vistos.add((amb, obj))
        afs.append({"ambito": amb, "objeto": obj, "sector": sec, "empresa_id": empresa_id, "valor": val})
    ambitos = {a["ambito"] for a in afs}
    if {"Empresa", "Sector"} <= ambitos:
        err.append("si el titular nombra una empresa, la afectación va a la empresa y no lleva Sector (criterios 11 e)")
    return err, afs


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2
    ruta = Path(sys.argv[1])
    datos = json.loads(ruta.read_text("utf-8"))
    version = datos.get("version_criterios")
    if version != VERSION_CRITERIOS:
        print(f"version_criterios {version!r} no coincide con la vigente {VERSION_CRITERIOS!r}: no se carga nada.")
        return 1

    db = conectar()
    cat = catalogos(db)
    idx = IndiceEmpresas(todas(db, "empresas", "id,nombre,alias,ticker,sector"))
    nuevas = {}
    for e in datos.get("empresas_nuevas") or []:
        if e.get("nombre") and not idx.buscar(e["nombre"], e.get("ticker")):
            nuevas[clave(e["nombre"])] = e
    clasif = datos.get("clasificaciones") or []
    ids = [c.get("articulo_id") for c in clasif if isinstance(c.get("articulo_id"), int)]
    validos = set()
    for i in range(0, len(ids), 100):
        validos |= {r["id"] for r in db.table("articulos").select("id").in_("id", ids[i:i + 100]).execute().data}

    cargados, rechazados, usadas = 0, [], {}
    ahora = datetime.now(timezone.utc).isoformat()
    for c in clasif:
        errores, afs = validar(c, cat, idx, nuevas, validos)
        if errores:
            rechazados.append({"clasificacion": c, "errores": errores})
            continue
        aid = c["articulo_id"]
        db.table("clasificacion").upsert({
            "articulo_id": aid, "relevante": c["relevante"],
            "motivo_no_relevante": None if c["relevante"] else c["motivo_no_relevante"],
            "tema": c.get("tema") if c["relevante"] else None,
            "origen": c.get("origen") if c["relevante"] else None,
            "metodo": "manual", "version_criterios": VERSION_CRITERIOS, "clasificado_en": ahora,
        }, on_conflict="articulo_id").execute()
        db.table("afectaciones").delete().eq("articulo_id", aid).execute()
        if afs:
            db.table("afectaciones").insert([{**a, "articulo_id": aid, "metodo": "manual",
                                              "version_criterios": VERSION_CRITERIOS} for a in afs]).execute()
        for a in afs:
            if a["ambito"] == "Empresa" and a["empresa_id"] is None:
                usadas[clave(a["objeto"])] = nuevas[clave(a["objeto"])]
        cargados += 1

    if rechazados:
        destino = ruta.with_suffix(".rechazados.json")
        destino.write_text(json.dumps({"lote": datos.get("lote"), "version_criterios": version,
                                       "rechazados": rechazados}, ensure_ascii=False, indent=1), "utf-8")
    if usadas:  # acumula las propuestas para que el usuario las apruebe
        previas = json.loads(PROPUESTAS.read_text("utf-8")) if PROPUESTAS.exists() else {}
        for k, e in usadas.items():
            previas.setdefault(k, {**e, "lotes": []})
            previas[k]["lotes"] = sorted(set(previas[k]["lotes"]) | {datos.get("lote")})
        PROPUESTAS.write_text(json.dumps(previas, ensure_ascii=False, indent=1), "utf-8")

    print(f"Lote {datos.get('lote')}: cargados {cargados} · rechazados {len(rechazados)} · "
          f"empresas nuevas usadas {len(usadas)}")
    for r in rechazados:
        print(f"  RECHAZADO {r['clasificacion'].get('articulo_id')}: {'; '.join(r['errores'])}")
    for e in usadas.values():
        print(f"  EMPRESA NUEVA: {e['nombre']} · sector propuesto {e.get('sector')!r} · ticker propuesto "
              f"{e.get('ticker')!r} · en_universo {e.get('en_universo', False)}")
    if rechazados:
        print(f"Rechazados guardados en {ruta.with_suffix('.rechazados.json')}: corregir y volver a cargar.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
