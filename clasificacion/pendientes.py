"""Exporta un lote de artículos pendientes de clasificar a clasificacion/lotes/pendiente_<n>.json.

Pendiente = sin clasificación, o clasificado solo por 'reglas' con un motivo distinto de 'Cripto'.
Cada artículo lleva sus detecciones (pistas de las reglas) para ayudar al agente.

Uso:
    python clasificacion/pendientes.py --lote 100     # exporta hasta 100
    python clasificacion/pendientes.py --estado       # solo cuenta clasificados y pendientes
    python clasificacion/pendientes.py --lote 100 --particion 2/4   # solo ids con id % 4 == 2 (agentes en paralelo)
    python clasificacion/pendientes.py --lote 100 --ids lista.json  # solo esos articulo_id (piloto)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

from comun import LOTES, MADRID, VERSION_CRITERIOS, conectar, todas


def articulos(db) -> list[dict]:
    """Artículos sin los duplicados (duplicado_de no nulo): no se clasifican ni cuentan como pendientes."""
    arts = todas(db, "articulos", "id,fuente_id,seccion,publicado_en,titulo,resumen,simbolos,duplicado_de")
    return [a for a in arts if a["duplicado_de"] is None]


def pendientes(db) -> tuple[list[dict], dict]:
    clas = todas(db, "clasificacion", "articulo_id,metodo,motivo_no_relevante", orden="articulo_id")
    hechos = {c["articulo_id"] for c in clas
              if c["metodo"] == "manual" or c["motivo_no_relevante"] == "Cripto"}
    arts = articulos(db)
    pend = [a for a in arts if a["id"] not in hechos]
    ids = {a["id"] for a in arts}
    clas = [c for c in clas if c["articulo_id"] in ids]  # sin las clasificaciones de los duplicados
    estado = {
        "articulos": len(arts),
        "clasificados_manual": sum(c["metodo"] == "manual" for c in clas),
        "cripto_por_reglas": sum(c["metodo"] == "reglas" and c["motivo_no_relevante"] == "Cripto" for c in clas),
        "pendientes": len(pend),
    }
    return pend, estado


def siguiente_numero() -> int:
    nums = [int(m.group(1)) for p in LOTES.glob("pendiente_*.json") if (m := re.search(r"_(\d+)\.json$", p.name))]
    return max([x for x in nums if x < 1000], default=0) + 1


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--lote", type=int, default=100)
    ap.add_argument("--estado", action="store_true")
    ap.add_argument("--particion", help="k/n: solo artículos con id %% n == k, para repartir entre agentes")
    ap.add_argument("--ids", help="fichero JSON con una lista de articulo_id: solo esos (p. ej. un piloto)")
    ap.add_argument("--reclasificar", action="store_true",
                    help="con --ids: exporta esos artículos aunque ya estén clasificados (revisión con criterios nuevos)")
    ap.add_argument("--forzar", action="store_true",
                    help="con --reclasificar: incluye también los ya clasificados con la versión vigente "
                         "(p. ej. tras aprobar o descartar empresas)")
    args = ap.parse_args()

    db = conectar()
    pend, estado = pendientes(db)
    if args.ids:
        elegidos = set(json.loads(Path(args.ids).read_text("utf-8")))
        if args.reclasificar:  # para no repetir dentro de una revisión, se saltan los ya revisados con la versión vigente
            revisados = {c["articulo_id"] for c in todas(db, "clasificacion", "articulo_id,version_criterios",
                                                          orden="articulo_id")
                         if c["version_criterios"] == VERSION_CRITERIOS and not args.forzar}
            todos = articulos(db)
            pend = [a for a in todos if a["id"] in elegidos and a["id"] not in revisados]
        else:
            pend = [a for a in pend if a["id"] in elegidos]
        estado["pendientes_de_la_lista"] = len(pend)
    if args.particion:
        k, n = map(int, args.particion.split("/"))
        pend = [a for a in pend if a["id"] % n == k]
        estado["pendientes_particion"] = len(pend)
    print(json.dumps(estado, ensure_ascii=False))
    if args.estado or not pend:
        if not pend:
            print("No quedan artículos pendientes.")
        return 0

    lote = pend[: args.lote]
    ids = [a["id"] for a in lote]
    fuentes = {f["id"]: f["nombre"] for f in db.table("fuentes").select("id,nombre").execute().data}
    empresas = {e["id"]: e for e in todas(db, "empresas", "id,nombre,ticker,sector,en_universo")}
    dets: dict[int, list] = {}
    for i in range(0, len(ids), 100):
        for d in db.table("detecciones").select("articulo_id,tipo,objeto,metodo,empresa_id") \
                .in_("articulo_id", ids[i:i + 100]).execute().data:
            pista = {"tipo": d["tipo"], "objeto": d["objeto"], "metodo": d["metodo"]}
            if d["empresa_id"]:
                e = empresas[d["empresa_id"]]
                pista.update(ticker=e["ticker"], sector=e["sector"], en_universo=e["en_universo"])
            dets.setdefault(d["articulo_id"], []).append(pista)

    LOTES.mkdir(parents=True, exist_ok=True)
    if args.particion:  # cada partición numera en su bloque (k+1)*1000+1…, para que los agentes no choquen
        n = (int(args.particion.split("/")[0]) + 1) * 1000 + 1
        while (LOTES / f"pendiente_{n}.json").exists():
            n += 1
    else:
        n = siguiente_numero()
    salida = LOTES / f"pendiente_{n}.json"
    datos = {
        "lote": n,
        "version_criterios": VERSION_CRITERIOS,
        "generado_en": datetime.now(MADRID).strftime("%Y-%m-%d %H:%M"),
        "pendientes_totales": len(pend),
        "articulos": [
            {
                "articulo_id": a["id"],
                "fuente": fuentes.get(a["fuente_id"]),
                "seccion": a["seccion"],
                "fecha": datetime.fromisoformat(a["publicado_en"]).astimezone(MADRID).strftime("%Y-%m-%d %H:%M"),
                "titulo": a["titulo"],
                "resumen": a["resumen"],
                "simbolos": a["simbolos"],
                "pistas": dets.get(a["id"], []),
            }
            for a in lote
        ],
    }
    salida.write_text(json.dumps(datos, ensure_ascii=False, indent=1), "utf-8")
    print(f"Lote {n}: {len(lote)} artículos -> {salida}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
