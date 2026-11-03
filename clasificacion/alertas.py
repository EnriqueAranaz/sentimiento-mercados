"""Empresas con peores (y mejores) noticias de los últimos días de mercado, para el informe de /clasificar.

Lo mismo que la pestaña Alertas del panel: por empresa, titulares en -2 / +2 y suma del tono.

Uso:
    python clasificacion/alertas.py               # últimos 5 días de mercado, solo universo
    python clasificacion/alertas.py --dias 20 --todas
"""
from __future__ import annotations

import argparse
import sys
from collections import defaultdict

from comun import conectar, todas

N = 5


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dias", type=int, default=5, help="días de mercado hacia atrás (5 por defecto)")
    ap.add_argument("--todas", action="store_true", help="incluye empresas fuera del universo")
    args = ap.parse_args()
    afs = [a for a in todas(conectar(), "v_afectaciones", "id,articulo_id,dia_mercado,objeto,ambito,en_universo,valor")
           if a["ambito"] == "Empresa" and (args.todas or a["en_universo"])]
    dias = sorted({a["dia_mercado"] for a in afs})[-args.dias:]
    por = defaultdict(list)
    for a in afs:
        if a["dia_mercado"] in dias:
            por[a["objeto"]].append(a["valor"])

    def linea(signo: int) -> str:
        filas = [(o, sum(v == 2 * signo for v in vs), sum(vs), len(vs)) for o, vs in por.items() if sum(vs) * signo > 0]
        filas.sort(key=lambda f: (-f[1], -f[2] * signo))
        return " · ".join(f"{o} ({f} en {2 * signo:+d} de {n} afectaciones)" for o, f, _, n in filas[:N]) or "ninguna"

    alcance = "todas las empresas" if args.todas else "universo"
    print(f"Peores noticias ({len(dias)} días de mercado, {alcance}): {linea(-1)}")
    print(f"Mejores noticias: {linea(1)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
