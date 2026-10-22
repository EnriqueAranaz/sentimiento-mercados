from datetime import datetime, timezone

from ingesta.modelos import normalizar_url, parsear_fecha
from ingesta.robots import Robots

UA = "BolsaSentimentBot/0.1 (contacto)"

RANKIA = """
User-agent: Applebot-Extended
Disallow: /

User-agent: *
Disallow: /login
Disallow: /*.json$
Disallow: /*page_ultimos=
Disallow: /foros/*/responder
"""


def test_robots_comodines():
    r = Robots(RANKIA)
    assert r.permitido("https://www.rankia.com/foros/bolsa/temas?page=2", UA)
    assert r.permitido("https://www.rankia.com/titulares/feed.rss", UA)
    assert not r.permitido("https://www.rankia.com/login", UA)
    assert not r.permitido("https://www.rankia.com/api/x.json", UA)
    assert r.permitido("https://www.rankia.com/api/x.json?a=1", UA)  # `$` ancla el final
    assert not r.permitido("https://www.rankia.com/foros/bolsa?page_ultimos=3", UA)
    assert not r.permitido("https://www.rankia.com/foros/bolsa/responder", UA)


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


def test_numero_abreviado_rankia():
    from ingesta.parsers import _numero_abreviado

    assert _numero_abreviado("52") == 52
    assert _numero_abreviado("3,93K") == 3930
    assert _numero_abreviado("346K") == 346000
    assert _numero_abreviado("1,2M") == 1200000
    assert _numero_abreviado("") is None


def test_normalizar_url_quita_rastreo():
    assert normalizar_url("https://WWW.x.com/a.html?utm_source=tw&id=3#c") == "https://www.x.com/a.html?id=3"
