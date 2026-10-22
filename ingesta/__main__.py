"""Ingesta de titulares de mercados.

Uso:
    python -m ingesta [--franja apertura|cierre|manual] [--solo CLAVE ...] [--dry-run] [--muestras N]
"""
from __future__ import annotations

import argparse
import logging
import os
import sys
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path

import yaml
from dotenv import load_dotenv

from .almacen import crear_almacen
from .http import BloqueoError, ClienteEducado, RobotsError
from .modelos import MADRID, Item
from .parsers import PARSERS

RAIZ = Path(__file__).resolve().parent.parent
log = logging.getLogger("ingesta")


@dataclass
class Resultado:
    nombre: str
    tipo_acceso: str
    fuente_id: int
    estado: str = "ok"
    paginas: int = 0
    leidos: int = 0
    nuevos: int = 0
    avisos: list[str] = field(default_factory=list)
    muestras: list[Item] = field(default_factory=list)


def ahora() -> datetime:
    return datetime.now(timezone.utc)


def recorrer_listado(listado: dict, cliente: ClienteEducado, almacen, max_paginas: int,
                     limite_fecha: datetime | None, vistos: dict[str, Item]) -> tuple[int, bool, list[Item]]:
    """Recorre las páginas de un listado hasta tocar terreno ya capturado.

    Devuelve (páginas leídas, frontera encontrada, items leídos en este listado).
    """
    parser = PARSERS[listado["parser"]]
    corte = listado.get("corte", "url")
    paginas = max_paginas if listado.get("url_pagina") else 1
    leidos: list[Item] = []
    for n in range(1, paginas + 1):
        url = listado["url"] if n == 1 else listado["url_pagina"].format(n=n)
        r = cliente.get(url)
        items = parser(r.content, str(r.url), listado)
        if not items:
            if n == 1:
                raise ValueError(f"listado vacío en {url} (¿ha cambiado el HTML?)")
            return n, False, leidos
        for it in items:
            vistos.setdefault(it.url, it)
        leidos.extend(items)

        if corte == "fecha":
            fechas = [it.publicado_en for it in items if it.publicado_en]
            # Ordenado por última actividad: basta con mirar el último elemento con fecha.
            if limite_fecha and fechas and fechas[-1] <= limite_fecha:
                return n, True, leidos
        elif almacen.urls_conocidas([it.url for it in items]):
            return n, True, leidos
    return paginas, False, leidos


def procesar_fuente(fuente: dict, fuente_id: int, cliente: ClienteEducado, almacen, franja: str,
                    max_paginas: int, n_muestras: int) -> Resultado:
    res = Resultado(fuente["nombre"], fuente["tipo_acceso"], fuente_id)
    inicio = ahora()
    ultima = almacen.ultima_ejecucion(fuente_id)
    primera = not almacen.tiene_articulos(fuente_id)
    vistos: dict[str, Item] = {}
    hilos: dict[str, int | None] = {}  # hilos de foro vistos en esta ejecución -> nº de respuestas
    fallos = 0

    for listado in fuente["listados"]:
        etiqueta = listado.get("seccion") or listado["url"]
        try:
            limite = ultima or (inicio - timedelta(hours=24))
            pags, frontera, items = recorrer_listado(listado, cliente, almacen, max_paginas, limite, vistos)
        except BloqueoError as e:
            fallos += 1
            res.avisos.append(f"[{etiqueta}] BLOQUEADO: {e}")
            log.error("%s · %s · bloqueado: %s", fuente["nombre"], etiqueta, e)
            continue
        except RobotsError as e:
            fallos += 1
            res.avisos.append(f"[{etiqueta}] {e}")
            log.error("%s · %s · %s", fuente["nombre"], etiqueta, e)
            continue
        except Exception as e:  # noqa: BLE001 — una fuente rota no debe parar las demás
            fallos += 1
            res.avisos.append(f"[{etiqueta}] {type(e).__name__}: {e}")
            log.exception("%s · %s · error", fuente["nombre"], etiqueta)
            continue

        res.paginas += pags
        if listado["parser"] == "rankia_foro":
            hilos.update({it.url: it.n_respuestas for it in items})
        log.info("%s · %s · páginas=%d leídos=%d frontera=%s", fuente["nombre"], etiqueta, pags, len(items), frontera)

        if not frontera and listado.get("detecta_hueco", True):
            fechas = [it.publicado_en for it in items if it.publicado_en]
            if ultima and fechas and min(fechas) <= ultima:
                pass  # no hay URL conocida, pero las fechas ya solapan con la ejecución anterior
            elif primera:
                res.avisos.append(f"[{etiqueta}] primera ejecución: sin referencia previa para detectar huecos")
            else:
                res.estado = "parcial"
                res.avisos.append(
                    f"[{etiqueta}] posible hueco: {pags} página(s) leídas sin encontrar URLs ya guardadas"
                )

    if fallos == len(fuente["listados"]):
        res.estado = "error"
    elif fallos:
        res.estado = "parcial"

    filas = [
        {
            "fuente_id": fuente_id,
            "url": it.url,
            "titulo": it.titulo,
            "resumen": it.resumen,
            "seccion": it.seccion,
            "n_respuestas": it.n_respuestas,
            "publicado_en": (it.publicado_en or inicio).isoformat(),
            "fecha_estimada": it.publicado_en is None or it.fecha_estimada,
            "simbolos": it.simbolos,
        }
        for it in vistos.values()
    ]
    res.leidos = len(filas)
    if filas:
        try:
            conocidas = almacen.urls_conocidas([f["url"] for f in filas])
            res.nuevos = almacen.insertar_articulos(filas)
            nuevos = [it for it in vistos.values() if it.url not in conocidas]
            res.muestras = (nuevos or list(vistos.values()))[:n_muestras]
        except Exception as e:  # noqa: BLE001
            res.estado = "error"
            res.avisos.append(f"error guardando artículos: {e}")
            log.exception("%s · error guardando", fuente["nombre"])

    ejecucion_id = almacen.registrar_ejecucion({
        "inicio": inicio.isoformat(),
        "fin": ahora().isoformat(),
        "franja": franja,
        "fuente_id": fuente_id,
        "estado": res.estado,
        "n_leidos": res.leidos,
        "n_nuevos": res.nuevos,
        "paginas_leidas": res.paginas,
        "error_msg": "; ".join(res.avisos)[:2000] or None,
    })

    if hilos:
        # Una fila por hilo visto, exista o no de antes: es la serie temporal de actividad.
        try:
            ids = almacen.ids_articulos(list(hilos))
            almacen.insertar_actividad([
                {"articulo_id": ids[url], "ejecucion_id": ejecucion_id, "n_respuestas": n}
                for url, n in hilos.items() if url in ids
            ])
            log.info("%s · actividad registrada para %d hilos", res.nombre, len(ids))
        except Exception as e:  # noqa: BLE001
            res.avisos.append(f"error registrando rankia_actividad: {e}")
            if res.estado == "ok":
                res.estado = "parcial"
            almacen.actualizar_ejecucion(ejecucion_id, {"estado": res.estado, "error_msg": "; ".join(res.avisos)[:2000]})
            log.exception("%s · error registrando actividad", res.nombre)

    log.info("%s · estado=%s páginas=%d leídos=%d nuevos=%d", res.nombre, res.estado, res.paginas, res.leidos, res.nuevos)
    return res


def imprimir_resumen(resultados: list[Resultado], inactivas: list[dict]) -> None:
    print("\n" + "=" * 100)
    print(f"{'FUENTE':<16}{'ACCESO':<8}{'ESTADO':<9}{'PÁGINAS':>8}{'LEÍDOS':>8}{'NUEVOS':>8}")
    print("-" * 100)
    for r in resultados:
        print(f"{r.nombre:<16}{r.tipo_acceso:<8}{r.estado:<9}{r.paginas:>8}{r.leidos:>8}{r.nuevos:>8}")
    for f in inactivas:
        print(f"{f['nombre']:<16}{f['tipo_acceso']:<8}{'inactiva':<9}{'-':>8}{'-':>8}{'-':>8}")
    print("=" * 100)
    for r in resultados:
        print(f"\n## {r.nombre} ({r.estado})")
        for a in r.avisos:
            print(f"   ! {a}")
        for it in r.muestras:
            fecha = it.publicado_en.astimezone(MADRID).strftime("%d/%m %H:%M") if it.publicado_en else "sin fecha"
            print(f"   - [{fecha}] {it.titulo}")
    for f in inactivas:
        print(f"\n## {f['nombre']} (inactiva)\n   ! {f.get('motivo', '')}")


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="ingesta", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--franja", choices=["apertura", "cierre", "manual"], default=os.environ.get("FRANJA", "manual"))
    ap.add_argument("--solo", nargs="*", metavar="CLAVE", help="procesar solo estas fuentes (por clave)")
    ap.add_argument("--dry-run", action="store_true", help="no usa Supabase: guarda en data/dry_run.json")
    ap.add_argument("--muestras", type=int, default=5, help="titulares de ejemplo por fuente en el resumen")
    ap.add_argument("--config", default=str(RAIZ / "config" / "sources.yaml"))
    args = ap.parse_args(argv)

    load_dotenv(RAIZ / ".env")
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)-7s %(message)s", datefmt="%H:%M:%S")
    for ruidoso in ("httpx", "httpcore", "hpack"):
        logging.getLogger(ruidoso).setLevel(logging.WARNING)

    cfg = yaml.safe_load(Path(args.config).read_text("utf-8"))
    d = cfg.get("defaults", {})
    fuentes = cfg["fuentes"]

    almacen = crear_almacen(args.dry_run, RAIZ / "data" / "dry_run.json")
    ids = almacen.sincronizar_fuentes(fuentes)

    seleccion = [f for f in fuentes if not args.solo or f["clave"] in args.solo]
    activas = [f for f in seleccion if f.get("activa", True)]
    inactivas = [f for f in seleccion if not f.get("activa", True)]
    for f in inactivas:
        log.info("%s · desactivada: %s", f["nombre"], f.get("motivo", ""))

    log.info("Franja=%s · fuentes activas=%d · %s", args.franja, len(activas), "DRY-RUN" if args.dry_run else "Supabase")
    cliente = ClienteEducado(d.get("user_agent", "BolsaSentimentBot/0.1"), d.get("timeout_s", 20), d.get("intervalo_dominio_s", 1.0))
    try:
        resultados = [
            procesar_fuente(f, ids[f["nombre"]], cliente, almacen, args.franja, d.get("max_paginas", 10), args.muestras)
            for f in activas
        ]
    finally:
        cliente.close()

    imprimir_resumen(resultados, inactivas)

    alertas = fuentes_con_errores_seguidos(resultados, almacen)
    for nombre in alertas:
        log.error("ALERTA · %s acumula %d ejecuciones seguidas con estado 'error' (la fuente sigue activa)",
                  nombre, ERRORES_SEGUIDOS_ALERTA)
    if resultados and all(r.estado == "error" for r in resultados):
        return 1
    return 2 if alertas else 0


ERRORES_SEGUIDOS_ALERTA = 3


def fuentes_con_errores_seguidos(resultados: list[Resultado], almacen) -> list[str]:
    """Fuentes cuyas últimas N ejecuciones (incluida la actual) son todas 'error'. No las desactiva."""
    alertas = []
    for r in resultados:
        estados = almacen.ultimos_estados(r.fuente_id, ERRORES_SEGUIDOS_ALERTA)
        if len(estados) == ERRORES_SEGUIDOS_ALERTA and all(e == "error" for e in estados):
            alertas.append(r.nombre)
    return alertas


if __name__ == "__main__":
    sys.exit(main())
