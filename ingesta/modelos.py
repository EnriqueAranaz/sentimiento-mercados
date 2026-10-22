from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from zoneinfo import ZoneInfo

MADRID = ZoneInfo("Europe/Madrid")

_PARAMS_RASTREO = re.compile(r"^(utm_|_ptid$|ref$|fbclid$|gclid$|ns_|cmpid$|ssm$)", re.I)


@dataclass
class Item:
    url: str
    titulo: str
    publicado_en: datetime | None = None  # aware; se convierte a UTC al guardar
    resumen: str | None = None
    seccion: str | None = None
    n_respuestas: int | None = None
    fecha_estimada: bool = False  # True si publicado_en no es la fecha real de publicación
    simbolos: list[str] | None = None  # tickers relacionados (solo TradingView)


def a_utc(fecha: datetime) -> datetime:
    """Fechas sin zona se interpretan como hora de Madrid."""
    if fecha.tzinfo is None:
        fecha = fecha.replace(tzinfo=MADRID)
    return fecha.astimezone(timezone.utc)


def parsear_fecha(texto: str | None) -> datetime | None:
    if not texto:
        return None
    texto = texto.strip()
    try:
        return a_utc(datetime.fromisoformat(texto.replace("Z", "+00:00")))
    except ValueError:
        pass
    try:
        return a_utc(parsedate_to_datetime(texto))
    except (TypeError, ValueError, IndexError):
        pass
    for fmt in ("%Y-%m-%d %H:%M:%S", "%d/%m/%y %H:%M", "%d/%m/%Y %H:%M"):
        try:
            return a_utc(datetime.strptime(texto, fmt))
        except ValueError:
            continue
    return None


def normalizar_url(url: str) -> str:
    """Quita fragmento y parámetros de rastreo para que la misma noticia no se duplique."""
    p = urlsplit(url.strip())
    query = urlencode([(k, v) for k, v in parse_qsl(p.query, keep_blank_values=True) if not _PARAMS_RASTREO.match(k)])
    return urlunsplit((p.scheme.lower(), p.netloc.lower(), p.path, query, ""))


def limpiar_texto(texto: str | None, max_len: int | None = None) -> str | None:
    if not texto:
        return None
    from bs4 import BeautifulSoup

    limpio = BeautifulSoup(texto, "html.parser").get_text(" ", strip=True)
    limpio = re.sub(r"\s+", " ", limpio).strip()
    if max_len and len(limpio) > max_len:
        limpio = limpio[: max_len - 1].rstrip() + "…"
    return limpio or None
