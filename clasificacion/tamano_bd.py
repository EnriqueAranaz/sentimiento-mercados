"""Tamaño de la base de datos frente al límite del plan gratuito de Supabase (500 MB). Necesita sql/012.

Uso:
    python clasificacion/tamano_bd.py
"""
from __future__ import annotations

import sys

from comun import conectar

LIMITE_MB = 500


def main() -> int:
    t = conectar().rpc("tamano_bd").execute().data
    mb = lambda b: b / 1024 / 1024  # noqa: E731
    total = mb(t["total"])
    mayores = sorted(t["tablas"].items(), key=lambda x: -x[1])[:4]
    print(f"Base de datos: {total:.1f} MB de {LIMITE_MB} MB ({100 * total / LIMITE_MB:.1f} %) · "
          + " · ".join(f"{n} {mb(b):.1f} MB" for n, b in mayores))
    return 0


if __name__ == "__main__":
    sys.exit(main())
