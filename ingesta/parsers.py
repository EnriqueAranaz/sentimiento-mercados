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


class SinNovedades(Exception):
    """El listado está vacío a propósito (p. ej. sitemap con <no_news> en fin de semana): no es un error."""


def sitemap_news(contenido: bytes, base_url: str, cfg: dict) -> list[Item]:
    """Sitemap de Google News (<news:title>, <news:publication_date>)."""
    xml = BeautifulSoup(contenido, "xml")
    if not xml.find("url") and xml.find("no_news"):
        raise SinNovedades("el sitemap indica <no_news>: sin noticias recientes")
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


PARSERS = {
    "rss": rss,
    "sitemap_news": sitemap_news,
    "html_enlaces": html_enlaces,
    "tradingview_json": tradingview_json,
}


def _date_published(nodo) -> str | None:
    """Busca datePublished en un bloque JSON-LD (objeto, lista o @graph)."""
    if isinstance(nodo, list):
        return next((f for f in map(_date_published, nodo) if f), None)
    if isinstance(nodo, dict):
        if isinstance(nodo.get("datePublished"), str):
            return nodo["datePublished"]
        return _date_published(nodo.get("@graph"))
    return None


def fecha_de_articulo(contenido: bytes) -> datetime | None:
    """Fecha real de publicación de una página de artículo.

    Se toma de <meta property="article:published_time"> o, si no está (caso de Bolsamanía),
    del `datePublished` del JSON-LD. Solo se lee la cabecera de metadatos: el cuerpo no se guarda.
    """
    soup = BeautifulSoup(contenido, "lxml")
    meta = soup.find("meta", attrs={"property": "article:published_time"})
    if meta and meta.get("content"):
        return parsear_fecha(meta["content"])
    for script in soup.find_all("script", type="application/ld+json"):
        try:
            valor = _date_published(json.loads(script.string or ""))
        except json.JSONDecodeError:
            continue
        if valor:
            return parsear_fecha(valor)
    return None
