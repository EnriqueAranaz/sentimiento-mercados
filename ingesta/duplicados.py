"""Duplicados de la misma fuente, antes de guardar.

- `clave_url` (Bolsamanía, CapitalBolsa): el número del artículo en la URL (--NNN.html) es la clave de la noticia; la
  misma noticia llega por el archivo y por el sitemap con slugs distintos. Una clave = una noticia, y manda su última
  versión: si la clave ya está guardada con el mismo titular normalizado, la fila se ignora; si el titular cambió, se
  actualiza la existente (titulo_anterior, titulo y resumen nuevos; publicado_en igual) y se borra su clasificación
  para que vuelva a quedar pendiente.
- `duplicado_por_titulo_h` (TradingView): Reuters reenvía la misma noticia con otro identificador. Si hay un artículo de
  la misma fuente con el mismo titular normalizado en esas horas, se inserta con duplicado_de = id del primero.
"""
from __future__ import annotations

import re
from datetime import datetime, timedelta


def clave_de_url(url: str, patron: str) -> str | None:
    m = re.search(patron, url)
    return m.group(1) if m else None


def titular_normalizado(titulo: str) -> str:
    """Minúsculas, sin espacios dobles ni puntuación final."""
    t = re.sub(r"\s+", " ", (titulo or "").replace("​", "").lower()).strip()
    return re.sub(r"[\s.,;:!?…]+$", "", t)


def _fecha(fila: dict) -> datetime:
    return datetime.fromisoformat(str(fila["publicado_en"]).replace("Z", "+00:00"))


def guardar_articulos(filas: list[dict], fuente: dict, fuente_id: int, almacen) -> tuple[list[dict], list[dict]]:
    """Guarda las filas aplicando las reglas de duplicado de la fuente.

    Devuelve (insertadas, actualizadas): las nuevas con su id, y las existentes cuyo titular se reescribió.
    """
    actualizadas: list[dict] = []
    patron = fuente.get("clave_url")
    if patron:
        vistas: set[str] = set()
        propias = []
        for f in filas:
            f["clave_fuente"] = clave_de_url(f["url"], patron)
            if f["clave_fuente"] and f["clave_fuente"] in vistas:
                continue  # misma noticia por otro listado en este lote
            vistas.add(f["clave_fuente"])
            propias.append(f)
        guardadas = almacen.por_clave(fuente_id, [f["clave_fuente"] for f in propias if f["clave_fuente"]])
        filas = []
        for f in propias:
            previa = guardadas.get(f["clave_fuente"])
            if previa is None:
                filas.append(f)
            elif titular_normalizado(previa["titulo"]) != titular_normalizado(f["titulo"]):
                actualizadas.append(almacen.actualizar_titular(previa["id"], f["titulo"], f.get("resumen"), previa["titulo"]))

    horas = fuente.get("duplicado_por_titulo_h")
    if not horas or not filas:
        return almacen.insertar_articulos(filas), actualizadas

    ventana = timedelta(hours=horas)
    filas = sorted(filas, key=_fecha)
    previos: dict[str, list[tuple[int, datetime]]] = {}
    for r in almacen.recientes(fuente_id, min(_fecha(f) for f in filas) - ventana):
        if r.get("duplicado_de") is None:
            previos.setdefault(titular_normalizado(r["titulo"]), []).append((r["id"], _fecha(r)))

    def primero(f: dict) -> int | None:
        fecha = _fecha(f)
        cerca = [i for i, d in previos.get(titular_normalizado(f["titulo"]), []) if abs(fecha - d) < ventana]
        return min(cerca) if cerca else None

    # Primero los originales, para tener su id; luego los reenvíos del mismo lote.
    vistos_lote: set[str] = set()
    originales, reenvios = [], []
    for f in filas:
        t = titular_normalizado(f["titulo"])
        f["duplicado_de"] = primero(f)
        (reenvios if f["duplicado_de"] is None and t in vistos_lote else originales).append(f)
        vistos_lote.add(t)
    nuevos = almacen.insertar_articulos(originales)
    for n in nuevos:
        if n.get("duplicado_de") is None:
            previos.setdefault(titular_normalizado(n["titulo"]), []).append((n["id"], _fecha(n)))
    for f in reenvios:
        f["duplicado_de"] = primero(f)
    return nuevos + (almacen.insertar_articulos(reenvios) if reenvios else []), actualizadas
