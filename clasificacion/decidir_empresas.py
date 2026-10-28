"""Empresas propuestas por el agente: estado y decisión (aprobar o descartar).

Las propuestas se acumulan en clasificacion/lotes/empresas_nuevas_propuestas.json (las escribe cargar.py, con los ids
de las noticias que las nombran). Una propuesta está pendiente de decisión si no está en la tabla `empresas` ni en
docs/empresas_descartadas.md.

Uso:
    python clasificacion/decidir_empresas.py --estado
    python clasificacion/decidir_empresas.py --aprobar "Elecnor" --aprobar "Coinbase"
    python clasificacion/decidir_empresas.py --descartar "Condis" --motivo "No cotiza"

Al decidir:
  - las aprobadas se añaden a clasificacion/empresas_aprobadas.json y se dan de alta con semilla_empresas.py;
  - las descartadas se añaden a docs/empresas_descartadas.md, con el motivo y la fecha;
  - ambas salen de las propuestas, y sus noticias se exportan para reclasificar
    (pendientes.py --ids … --reclasificar --forzar). Después hay que clasificarlas con el agente y ejecutar indice.py
    (el comando /decidir-empresas lo hace todo seguido).
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime

from comun import (DESCARTADAS, LOTES, MADRID, PROPUESTAS, RAIZ, IndiceEmpresas, clave, conectar, descartadas,
                   todas)

APROBADAS = RAIZ / "clasificacion" / "empresas_aprobadas.json"


def pendientes_de_decision(propuestas: dict, idx: IndiceEmpresas, fuera: set[str]) -> dict[str, dict]:
    return {k: e for k, e in propuestas.items() if not idx.buscar(e["nombre"], e.get("ticker")) and k not in fuera}


def fila_descartada(e: dict, motivo: str, fecha: str) -> str:
    return f"| {e['nombre']} | {e.get('ticker') or '—'} | {motivo} | {fecha} |"


def leer_propuestas() -> dict:
    return json.loads(PROPUESTAS.read_text("utf-8")) if PROPUESTAS.exists() else {}


def estado(db) -> int:
    idx = IndiceEmpresas(todas(db, "empresas", "id,nombre,alias,ticker,sector"))
    pend = pendientes_de_decision(leer_propuestas(), idx, descartadas())
    noticias = {i for e in pend.values() for i in e.get("articulos") or []}
    print(f"Empresas propuestas pendientes de decisión: {len(pend)} · noticias afectadas: {len(noticias)}")
    for e in sorted(pend.values(), key=lambda e: e["nombre"].casefold()):
        print(f"  {e['nombre']} · {e.get('ticker') or 'sin ticker'} · {e.get('sector')} · "
              f"{len(e.get('articulos') or [])} noticias · {e.get('comentario', '')}")
    if pend:
        print("Para decidir: /decidir-empresas (o clasificacion/decidir_empresas.py --aprobar … / --descartar … --motivo …)")
    return 0


def decidir(db, aprobar: list[str], descartar: list[str], motivo: str | None) -> int:
    propuestas = leer_propuestas()
    idx = IndiceEmpresas(todas(db, "empresas", "id,nombre,alias,ticker,sector"))
    pend = pendientes_de_decision(propuestas, idx, descartadas())
    elegidas = {}
    for nombre in aprobar + descartar:
        if clave(nombre) not in pend:
            print(f"{nombre!r} no es una propuesta pendiente (ver --estado). No se cambia nada.")
            return 1
        elegidas[clave(nombre)] = pend[clave(nombre)]
    if descartar and not motivo:
        print("Falta --motivo para las descartadas (p. ej. «Microcotizada»). No se cambia nada.")
        return 1

    if aprobar:
        lista = json.loads(APROBADAS.read_text("utf-8"))
        for nombre in aprobar:
            e = elegidas[clave(nombre)]
            lista.append({"nombre": e["nombre"], "ticker": e.get("ticker"), "sector": e["sector"],
                          "en_universo": bool(e.get("en_universo", False))})
        lista.sort(key=lambda e: e["nombre"].casefold())
        APROBADAS.write_text(json.dumps(lista, ensure_ascii=False, indent=1) + "\n", "utf-8")
        subprocess.run([sys.executable, str(RAIZ / "clasificacion" / "semilla_empresas.py")], check=True)
    if descartar:
        fecha = datetime.now(MADRID).strftime("%d/%m/%Y")
        texto = DESCARTADAS.read_text("utf-8").rstrip("\n")
        filas = [fila_descartada(elegidas[clave(n)], motivo, fecha) for n in descartar]
        DESCARTADAS.write_text(texto + "\n" + "\n".join(filas) + "\n", "utf-8")

    ids = sorted({i for e in elegidas.values() for i in e.get("articulos") or []})
    for k in elegidas:
        propuestas.pop(k)
    PROPUESTAS.write_text(json.dumps(propuestas, ensure_ascii=False, indent=1), "utf-8")
    print(f"Aprobadas: {len(aprobar)} · descartadas: {len(descartar)} · noticias a reclasificar: {len(ids)}")
    if ids:
        ruta = LOTES / f"reclasificar_empresas_{datetime.now(MADRID):%Y%m%d_%H%M}.json"
        ruta.write_text(json.dumps(ids), "utf-8")
        subprocess.run([sys.executable, str(RAIZ / "clasificacion" / "pendientes.py"), "--ids", str(ruta),
                        "--reclasificar", "--forzar", "--lote", str(max(100, len(ids)))], check=True)
        print(f"Siguiente paso: clasificar con el agente el pendiente_<n>.json recién exportado ({ruta.name}) y "
              "ejecutar clasificacion/indice.py.")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--estado", action="store_true", help="propuestas pendientes de decisión y noticias afectadas")
    ap.add_argument("--aprobar", action="append", default=[], metavar="NOMBRE")
    ap.add_argument("--descartar", action="append", default=[], metavar="NOMBRE")
    ap.add_argument("--motivo", help="motivo de las descartadas (microcotizada, banco regional de EE. UU., …)")
    args = ap.parse_args()
    db = conectar()
    if args.aprobar or args.descartar:
        return decidir(db, args.aprobar, args.descartar, args.motivo)
    return estado(db)


if __name__ == "__main__":
    sys.exit(main())
