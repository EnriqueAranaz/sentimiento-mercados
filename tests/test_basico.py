from datetime import datetime, timezone

from ingesta.modelos import normalizar_url, parsear_fecha
from ingesta.robots import Robots

UA = "BolsaSentimentBot/0.1 (contacto)"

ROBOTS = """
User-agent: Applebot-Extended
Disallow: /

User-agent: *
Disallow: /login
Disallow: /*.json$
Disallow: /*orden=
Disallow: /secciones/*/editar
"""


def test_robots_comodines():
    r = Robots(ROBOTS)
    assert r.permitido("https://www.ejemplo.com/secciones/bolsa/noticias?page=2", UA)
    assert r.permitido("https://www.ejemplo.com/titulares/feed.rss", UA)
    assert not r.permitido("https://www.ejemplo.com/login", UA)
    assert not r.permitido("https://www.ejemplo.com/api/x.json", UA)
    assert r.permitido("https://www.ejemplo.com/api/x.json?a=1", UA)  # `$` ancla el final
    assert not r.permitido("https://www.ejemplo.com/secciones/bolsa?orden=3", UA)
    assert not r.permitido("https://www.ejemplo.com/secciones/bolsa/editar", UA)


def test_robots_allow_gana_en_empate_y_regla_mas_larga():
    r = Robots("User-agent: *\nDisallow: /ed/\nAllow: /ed/premium.html\n")
    assert r.permitido("https://x.com/ed/premium.html", UA)
    assert not r.permitido("https://x.com/ed/otro.html", UA)


def test_robots_grupo_especifico():
    r = Robots("User-agent: BolsaSentimentBot\nDisallow: /\n\nUser-agent: *\nDisallow:\n")
    assert not r.permitido("https://x.com/a", UA)
    assert r.permitido("https://x.com/a", "OtroBot/1.0")


def test_fechas_a_utc():
    utc = timezone.utc
    # Hora de Madrid sin zona (verano, UTC+2) y (invierno, UTC+1)
    assert parsear_fecha("22/10/26 20:06") == datetime(2026, 10, 22, 18, 6, tzinfo=utc)
    assert parsear_fecha("05/12/26 10:00") == datetime(2026, 12, 5, 9, 0, tzinfo=utc)
    assert parsear_fecha("Thu, 22 Oct 2026 17:41:57 +0200") == datetime(2026, 10, 22, 15, 41, 57, tzinfo=utc)
    assert parsear_fecha("2026-10-22T18:27+02:00") == datetime(2026, 10, 22, 16, 27, tzinfo=utc)
    assert parsear_fecha("Thu, 22 Oct 2026 15:51:14 GMT") == datetime(2026, 10, 22, 15, 51, 14, tzinfo=utc)


def test_fecha_de_articulo_meta_y_json_ld():
    from ingesta.parsers import fecha_de_articulo

    utc = timezone.utc
    meta = b'<html><head><meta property="article:published_time" content="2026-10-22T17:46:53+02:00"></head></html>'
    assert fecha_de_articulo(meta) == datetime(2026, 10, 22, 15, 46, 53, tzinfo=utc)
    # Bolsamanía: sin meta, fecha en JSON-LD (también dentro de @graph o de una lista)
    ld = b'<script type="application/ld+json">{"@type":"NewsArticle","datePublished":"2026-10-26T06:00:00+01:00"}</script>'
    assert fecha_de_articulo(ld) == datetime(2026, 10, 26, 5, 0, tzinfo=utc)
    graph = b'<script type="application/ld+json">{"@graph":[{"@type":"WebPage"},{"datePublished":"2026-10-26T06:00:00+01:00"}]}</script>'
    assert fecha_de_articulo(graph) == datetime(2026, 10, 26, 5, 0, tzinfo=utc)
    assert fecha_de_articulo(b"<html><body>sin fecha</body></html>") is None


class _Resp:
    def __init__(self, url, html):
        import httpx

        self.url, self.content = httpx.URL(url), html.encode()


class _ClienteFalso:
    """Simula el archivo diario: {url: [urls de noticias]}; páginas no listadas = vacías."""

    def __init__(self, paginas):
        self.paginas, self.pedidas = paginas, []

    def get(self, url):
        self.pedidas.append(url)
        enlaces = "".join(f'<article><h2><a href="{u}">Titular de prueba {i}</a></h2></article>'
                          for i, u in enumerate(self.paginas.get(url, [])))
        return _Resp(url, f"<html><body>{enlaces}</body></html>")


ARCHIVO = {
    "url_dia": "https://b.com/noticias/ultimas/{fecha}",
    "url_dia_pagina": "https://b.com/noticias/ultimas/{fecha}/{n}",
    "parser": "html_enlaces",
    "seccion": "ultimas",
    "selector": "article h2 a",
    "patron_url": r"^https://b\.com/noticias/.+--\d+\.html$",
}


def _noticia(i):
    return f"https://b.com/noticias/mercados/n--{i}.html"


def _recorrer(paginas, conocidas, ultima, max_paginas=10, hoy="2026-10-26"):
    from unittest import mock

    from ingesta import __main__ as m
    from ingesta.almacen import AlmacenLocal

    almacen = mock.Mock(spec=AlmacenLocal)
    almacen.urls_conocidas.side_effect = lambda urls: {u for u in urls if u in conocidas}
    cliente = _ClienteFalso(paginas)
    with mock.patch.object(m, "ahora", return_value=datetime.fromisoformat(hoy + "T10:00:00+00:00")):
        pags, frontera, items = m.recorrer_archivo_diario({**ARCHIVO, "max_paginas": max_paginas}, cliente, almacen,
                                                          10, ultima, {})
    return pags, frontera, [it.url for it in items], cliente.pedidas


def test_archivo_diario_para_en_url_conocida_del_dia_anterior():
    base = "https://b.com/noticias/ultimas/"
    paginas = {
        base + "2026-10-26": [_noticia(9), _noticia(8)],
        base + "2026-10-25": [_noticia(7), _noticia(6)],  # 6 ya estaba guardada
        base + "2026-10-25/2": [_noticia(5)],
    }
    pags, frontera, urls, pedidas = _recorrer(paginas, {_noticia(6)}, datetime(2026, 10, 25, 16, 0, tzinfo=timezone.utc))
    assert frontera is True
    assert urls == [_noticia(9), _noticia(8), _noticia(7), _noticia(6)]
    assert base + "2026-10-25/2" not in pedidas  # no sigue tras encontrar terreno conocido


def test_archivo_diario_fin_de_semana_vacio_no_es_hueco():
    # Lunes; última ejecución el sábado y nada publicado sábado ni domingo: se cubre todo, sin hueco.
    base = "https://b.com/noticias/ultimas/"
    paginas = {base + "2026-10-26": [_noticia(9)]}
    pags, frontera, urls, pedidas = _recorrer(paginas, set(), datetime(2026, 10, 24, 16, 0, tzinfo=timezone.utc))
    assert frontera is True
    assert urls == [_noticia(9)]
    assert pedidas[-1] == base + "2026-10-24"  # bajó hasta el día de la última ejecución


def test_archivo_diario_hueco_si_se_agotan_las_paginas():
    base = "https://b.com/noticias/ultimas/"
    paginas = {base + "2026-10-26" + ("" if n == 1 else f"/{n}"): [_noticia(100 - n)] for n in range(1, 6)}
    pags, frontera, urls, pedidas = _recorrer(paginas, set(), datetime(2026, 10, 25, 16, 0, tzinfo=timezone.utc),
                                              max_paginas=3)
    assert (pags, frontera) == (3, False)


def test_html_enlaces_seccion_desde_url_y_excluye_destacadas():
    from ingesta.parsers import html_enlaces

    base = "https://www.bolsamania.com/capitalbolsa/noticias/"
    html = "".join(f'<article><h2><a href="{base}{p}">Titular de prueba {i}</a></h2></article>'
                   for i, p in enumerate(["bolsa/a--1.html", "economia/b--2.html", "destacadas/c--3.html"])).encode()
    cfg = {"seccion": "minuto-a-minuto", "selector": "article h2 a",
           "patron_url": r"^https://www\.bolsamania\.com/capitalbolsa/noticias/(?!destacadas/)(?P<seccion>[a-z0-9-]+)/[^?#]+--\d+\.html$"}
    assert [(it.url.rsplit("/", 2)[-2], it.seccion) for it in html_enlaces(html, base, cfg)] == [
        ("bolsa", "bolsa"), ("economia", "economia")]


def test_excluir_por_titulo_promocion_de_pago():
    from ingesta.__main__ import excluir_por_titulo
    from ingesta.modelos import Item

    titulos = ["La empresa de drones que podría duplicar su valor: descubra gratis esta idea de CB Premium",
               "Gratis el Servicio Premium Capital Bolsa: vean cómo trabajan los gestores",
               "El Ibex sube un 1% con la banca"]
    vistos = {f"u{i}": Item(url=f"u{i}", titulo=t) for i, t in enumerate(titulos)}
    assert excluir_por_titulo(vistos, r"(?i)\bCB Premium\b|Servicio Premium|Capital ?Bolsa Premium") == 2
    assert [it.titulo for it in vistos.values()] == ["El Ibex sube un 1% con la banca"]


def test_tradingview_extrae_simbolos():
    from ingesta.parsers import tradingview_json

    html = (
        '<script>x = {"items":[{"id":"a","title":"Santander sube","storyPath":"/news/a/","published":1792699440,'
        '"relatedSymbols":[{"symbol":"BME:SAN"},{"symbol":"NYSE:SAN"},{"symbol":"BME:SAN"}],'
        '"provider":{"name":"Reuters"}},'
        '{"id":"b","title":"Sin tickers","storyPath":"/news/b/","published":1792699440,"provider":{"name":"TradingView"}}]};'
        "</script>"
    ).encode()
    items = {it.titulo: it for it in tradingview_json(html, "https://es.tradingview.com/news/", {"seccion": "news"})}
    assert items["Santander sube"].simbolos == ["BME:SAN", "NYSE:SAN"]
    assert items["Santander sube"].seccion == "news/Reuters"
    assert items["Sin tickers"].simbolos is None


def test_alerta_tres_errores_seguidos(tmp_path):
    from ingesta.__main__ import Resultado, fuentes_con_errores_seguidos
    from ingesta.almacen import AlmacenLocal

    almacen = AlmacenLocal(tmp_path / "db.json")
    ids = almacen.sincronizar_fuentes([
        {"nombre": n, "tipo_acceso": "rss", "tipo_fuente": "medio", "url": "u", "idioma": "es", "activa": True}
        for n in ("A", "B", "C")
    ])
    historial = {"A": ["error", "error", "error"], "B": ["error", "ok", "error", "error"], "C": ["error", "error"]}
    for nombre, estados in historial.items():
        for i, estado in enumerate(estados):
            almacen.registrar_ejecucion({"inicio": f"2026-10-2{i}T09:30:00+00:00", "fuente_id": ids[nombre], "estado": estado})
    resultados = [Resultado(n, "rss", ids[n], estado="error") for n in ("A", "B", "C")]
    assert fuentes_con_errores_seguidos(resultados, almacen) == ["A"]


def test_sitemap_no_news_no_es_error():
    import pytest

    from ingesta.parsers import SinNovedades, sitemap_news

    cab = '<?xml version="1.0"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:news="http://www.google.com/schemas/sitemap-news/0.9">'
    with pytest.raises(SinNovedades):
        sitemap_news((cab + "<no_news>no news</no_news></urlset>").encode(), "https://x.com/sitemap.xml", {})
    # Vacío sin la marca <no_news>: devuelve lista vacía y el orquestador lo trata como posible cambio de formato.
    assert sitemap_news((cab + "</urlset>").encode(), "https://x.com/sitemap.xml", {}) == []


def test_normalizar_url_quita_rastreo():
    assert normalizar_url("https://WWW.x.com/a.html?utm_source=tw&id=3#c") == "https://www.x.com/a.html?id=3"
