"""Utilidades comunes de los scripts de clasificación manual (pendientes.py y cargar.py)."""
from __future__ import annotations

import os
import sys
import unicodedata
from pathlib import Path
from zoneinfo import ZoneInfo

from dotenv import load_dotenv

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

# Versión de los criterios: una única constante, en ingesta/reglas.py (la usan las reglas y la clasificación manual).
from ingesta.reglas import VERSION_CRITERIOS  # noqa: E402,F401  (se reexporta)

LOTES = RAIZ / "clasificacion" / "lotes"
MADRID = ZoneInfo("Europe/Madrid")
OBJETOS_GLOBAL = ("Mercados", "Economía", "Petróleo", "Materias primas", "Divisas")
AMBITOS = ("Global", "Mercado", "Sector", "Empresa")


def conectar():
    from supabase import create_client

    load_dotenv(RAIZ / ".env")
    return create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_ROLE_KEY"])


def todas(db, tabla: str, columnas: str, orden: str = "id") -> list[dict]:
    filas, desde = [], 0
    while True:
        lote = db.table(tabla).select(columnas).order(orden).range(desde, desde + 999).execute().data
        filas += lote
        if len(lote) < 1000:
            return filas
        desde += 1000


def catalogos(db) -> dict[str, set[str]]:
    return {t: {r["nombre"] for r in db.table(t).select("nombre").execute().data}
            for t in ("sectores", "temas", "origenes", "motivos_no_relevancia")}


def clave(texto: str) -> str:
    """Comparación de nombres sin mayúsculas ni tildes."""
    t = unicodedata.normalize("NFKD", texto or "")
    return " ".join("".join(c for c in t if not unicodedata.combining(c)).casefold().split())


class IndiceEmpresas:
    """Busca empresas por nombre, alias o ticker."""

    def __init__(self, empresas: list[dict]):
        self.empresas = empresas
        self.por_clave: dict[str, dict] = {}
        for e in empresas:
            for n in [e["nombre"], *(e.get("alias") or [])]:
                self.por_clave.setdefault(clave(n), e)
            if e.get("ticker"):
                self.por_clave.setdefault(clave(e["ticker"]), e)

    def buscar(self, *candidatos: str | None) -> dict | None:
        for c in candidatos:
            if c and clave(c) in self.por_clave:
                return self.por_clave[clave(c)]
        return None
