"""Cliente HTTP educado: User-Agent identificable, timeout, 1 petición/s por dominio y robots.txt."""
from __future__ import annotations

import logging
import re
import time
from urllib.parse import urlsplit

import httpx

from .robots import Robots

log = logging.getLogger(__name__)

# Marcas de páginas de desafío. Se buscan en el <title> o son específicas de Cloudflare,
# para no confundir con páginas normales que cargan scripts de reCAPTCHA.
_MARCAS_BLOQUEO = ("/cdn-cgi/challenge-platform", "cf-chl-")
_TITULOS_BLOQUEO = ("just a moment", "attention required", "access denied", "captcha", "are you a robot")


class BloqueoError(Exception):
    """La web bloquea el acceso automatizado (403/429, Cloudflare, captcha...). No se reintenta."""


class RobotsError(Exception):
    """robots.txt no permite la URL."""


class ClienteEducado:
    def __init__(self, user_agent: str, timeout_s: float = 20, intervalo_dominio_s: float = 1.0):
        self.user_agent = user_agent
        self.intervalo = intervalo_dominio_s
        self._ultima: dict[str, float] = {}
        self._robots: dict[str, Robots] = {}
        self._http = httpx.Client(
            headers={
                "User-Agent": user_agent,
                "Accept-Language": "es-ES,es;q=0.9",
            },
            timeout=timeout_s,
            follow_redirects=True,
        )

    def close(self) -> None:
        self._http.close()

    def _esperar_turno(self, host: str) -> None:
        espera = self._ultima.get(host, 0) + self.intervalo - time.monotonic()
        if espera > 0:
            time.sleep(espera)
        self._ultima[host] = time.monotonic()

    def _robots_de(self, url: str) -> Robots:
        p = urlsplit(url)
        origen = f"{p.scheme}://{p.netloc}"
        if origen not in self._robots:
            self._esperar_turno(p.netloc)
            try:
                r = self._http.get(origen + "/robots.txt")
                if r.status_code == 200:
                    robots = Robots(r.text)
                elif 400 <= r.status_code < 500:
                    # RFC 9309 §2.3.1.3: robots.txt "no disponible" (4xx) => sin restricciones.
                    # Si además la web bloquea, lo detectará la petición del listado.
                    log.debug("robots.txt de %s devuelve %s: sin restricciones (RFC 9309)", origen, r.status_code)
                    robots = Robots(None, permitir_todo=True)
                else:
                    robots = Robots(None, denegar_todo=True)
            except httpx.HTTPError as e:
                log.warning("No se pudo leer robots.txt de %s (%s): se asume prohibido", origen, e)
                robots = Robots(None, denegar_todo=True)
            self._robots[origen] = robots
        return self._robots[origen]

    def get(self, url: str) -> httpx.Response:
        if not self._robots_de(url).permitido(url, self.user_agent):
            raise RobotsError(f"robots.txt no permite {url}")
        host = urlsplit(url).netloc
        self._esperar_turno(host)
        r = self._http.get(url)
        if r.status_code in (401, 403, 429) or (r.status_code == 503 and "cloudflare" in r.headers.get("server", "").lower()):
            raise BloqueoError(f"HTTP {r.status_code} en {url}")
        r.raise_for_status()
        if "html" in r.headers.get("content-type", ""):
            inicio = r.text[:8000].lower()
            titulo = re.search(r"<title[^>]*>(.*?)</title>", inicio, re.S)
            if any(m in inicio for m in _MARCAS_BLOQUEO) or (
                titulo and any(t in titulo.group(1) for t in _TITULOS_BLOQUEO)
            ):
                raise BloqueoError(f"página de desafío/captcha en {url}")
        return r
