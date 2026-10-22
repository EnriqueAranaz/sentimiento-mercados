"""Parsers de listados. Cada uno recibe el contenido descargado y devuelve una lista de Item.

Solo se extrae titular, URL, fecha y (si es pública en el listado) la entradilla.
Nunca se descarga ni se guarda el cuerpo de los artículos.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from urllib.parse import urljoin

import feedparser
from bs4 import BeautifulSoup

from .modelos import Item, limpiar_texto, normalizar_url, parsear_fecha

MAX_RESUMEN = 1000


def rss(contenido: bytes, base_url: str, cfg: dict) -> list[Item]:
    feed = feedparser.parse(contenido)
    items = []
    for e in feed.entries:
        url, titulo = e.get("link"), limpiar_texto(e.get("title"))
        if not url or not titulo:
            continue
        fecha = parsear_fecha(e.get("published") or e.get("updated"))
        if fecha is None and (e.get("published_parsed") or e.get("updated_parsed")):
            st = e.get("published_parsed") or e.get("updated_parsed")
            fecha = datetime(*st[:6], tzinfo=timezone.utc)
        items.append(Item(
            url=normalizar_url(url),
            titulo=titulo,
            publicado_en=fecha,
            resumen=limpiar_texto(e.get("summary"), MAX_RESUMEN),
            seccion=cfg.get("seccion"),
        ))
    return items


def sitemap_news(contenido: bytes, base_url: str, cfg: dict) -> list[Item]:
    """Sitemap de Google News (<news:title>, <news:publication_date>)."""
    xml = BeautifulSoup(contenido, "xml")
    items = []
    for u in xml.find_all("url"):
        loc, titulo = u.find("loc"), u.find("title")
        if not loc or not titulo:
            continue
        fecha = u.find("publication_date") or u.find("lastmod")
        items.append(Item(
            url=normalizar_url(loc.get_text(strip=True)),
            titulo=limpiar_texto(titulo.get_text()),
            publicado_en=parsear_fecha(fecha.get_text(strip=True)) if fecha else None,
            seccion=cfg.get("seccion"),
        ))
    return items


def html_enlaces(contenido: bytes, base_url: str, cfg: dict) -> list[Item]:
    """Listado HTML genérico: enlaces que casan con `selector` y `patron_url`. Sin fecha."""
    soup = BeautifulSoup(contenido, "lxml")
    patron = re.compile(cfg["patron_url"])
    vistos: dict[str, Item] = {}
    for a in soup.select(cfg["selector"]):
        if a.find_parent("aside"):  # columnas laterales: "lo más leído", promociones...
            continue
        url = urljoin(base_url, a.get("href", ""))
        titulo = limpiar_texto(a.get_text(" "))
        if titulo and patron.match(url) and url not in vistos:
            vistos[url] = Item(url=normalizar_url(url), titulo=titulo, seccion=cfg.get("seccion"))
    return list(vistos.values())


def tradingview_json(contenido: bytes, base_url: str, cfg: dict) -> list[Item]:
    """TradingView incrusta en el HTML (renderizado en servidor) bloques JSON "items":[...]."""
    html = contenido.decode("utf-8", "replace")
    dec = json.JSONDecoder()
    vistos: dict[str, Item] = {}
    for m in re.finditer(r'"items":\[\{"id"', html):
        try:
            bloque, _ = dec.raw_decode(html, m.start() + len('"items":'))
        except json.JSONDecodeError:
            continue
        for n in bloque:
            if not isinstance(n, dict) or "storyPath" not in n or "title" not in n:
                continue
            url = normalizar_url(urljoin(base_url, n["storyPath"]))
            if url in vistos:
                continue
            publicado = n.get("published")
            proveedor = (n.get("provider") or {}).get("name")
            simbolos = [s["symbol"] for s in n.get("relatedSymbols") or [] if isinstance(s, dict) and s.get("symbol")]
            vistos[url] = Item(
                url=url,
                titulo=limpiar_texto(n["title"]),
                publicado_en=datetime.fromtimestamp(publicado, tz=timezone.utc) if publicado else None,
                seccion=f"{cfg.get('seccion')}/{proveedor}" if proveedor else cfg.get("seccion"),
                simbolos=list(dict.fromkeys(simbolos)) or None,
            )
    return list(vistos.values())


_FECHA_RANKIA = re.compile(r"\((\d{2}/\d{2}/\d{2} \d{2}:\d{2})\)")
_NUM_ABREV = re.compile(r"^(\d+(?:[.,]\d+)?)\s*([KkMm]?)$")


def _numero_abreviado(texto: str) -> int | None:
    """'52' -> 52, '3,93K' -> 3930, '346K' -> 346000 (Rankia abrevia: valor aproximado), '-' -> 0."""
    if texto.strip() == "-":  # hilo sin respuestas
        return 0
    m = _NUM_ABREV.match(texto.strip())
    if not m:
        return None
    num, sufijo = m.groups()
    if not sufijo:
        return int(num.replace(".", "").replace(",", ""))
    return round(float(num.replace(",", ".")) * (1_000 if sufijo.lower() == "k" else 1_000_000))


def rankia_foro(contenido: bytes, base_url: str, cfg: dict) -> list[Item]:
    """Listado de hilos del foro. Solo título, URL, fecha de última actividad y nº de respuestas.

    No se guardan autores, extractos de mensajes ni ningún otro dato personal.
    """
    soup = BeautifulSoup(contenido, "lxml")
    items = []
    for fila in soup.select("tr"):
        enlace = fila.select_one("h5 a[href*='/temas/']")
        if not enlace:
            continue
        url = urljoin(base_url, enlace["href"].split("?", 1)[0])
        celdas = fila.find_all("td", recursive=False)
        n_resp = _numero_abreviado(celdas[2].get_text(strip=True)) if len(celdas) >= 3 else None
        m = _FECHA_RANKIA.search(fila.get_text(" "))
        items.append(Item(
            url=normalizar_url(url),
            titulo=limpiar_texto(enlace.get_text(" ")),
            # Fecha del último mensaje (hora de Madrid -> UTC): el listado no muestra la de creación.
            publicado_en=parsear_fecha(m.group(1)) if m else None,
            fecha_estimada=True,
            seccion=cfg.get("seccion"),
            n_respuestas=n_resp,
        ))
    return items


PARSERS = {
    "rss": rss,
    "sitemap_news": sitemap_news,
    "html_enlaces": html_enlaces,
    "tradingview_json": tradingview_json,
    "rankia_foro": rankia_foro,
}
