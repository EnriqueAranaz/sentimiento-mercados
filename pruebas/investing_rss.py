"""Prueba de los feeds RSS de es.investing.com con el cliente educado del proyecto.

Uso: python investing_rss.py <salida.json> <id> [<id> ...]   (ids de /rss/news_<id>.rss)
Imprime por feed: estado HTTP, título, nº de entradas, periodo (hora de Madrid) y guarda las entradas en JSON.
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import feedparser

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))  # raíz del repo (para usarlo desde pruebas/)
sys.path.insert(0, r"C:\Bolsa")
from ingesta.http import BloqueoError, ClienteEducado  # noqa: E402

UA = "BolsaSentimentBot/0.1 (proyecto personal de seguimiento de titulares; contacto: aranaz.enrique@gmail.com)"
MADRID = ZoneInfo("Europe/Madrid")
cli = ClienteEducado(UA, timeout_s=20, intervalo_dominio_s=1.0)
salida, ids = sys.argv[1], sys.argv[2:]
resultado = {}
print(f"Ejecutado {datetime.now(MADRID):%d/%m %H:%M} (Madrid)")
for i in ids:
    url = f"https://es.investing.com/rss/news_{i}.rss"
    try:
        r = cli.get(url)
    except BloqueoError as e:
        print(f"news_{i:<4} BLOQUEADO {e}")
        continue
    except Exception as e:  # noqa: BLE001
        print(f"news_{i:<4} ERROR {type(e).__name__}: {str(e)[:60]}")
        continue
    feed = feedparser.parse(r.content)
    if not feed.entries:
        print(f"news_{i:<4} {r.status_code} sin entradas ({feed.feed.get('title')})")
        continue
    entradas = []
    for e in feed.entries:
        st = e.get("published_parsed")
        fecha = datetime(*st[:6], tzinfo=timezone.utc) if st else None
        entradas.append({"titulo": e.get("title"), "url": e.get("link"), "publicado": e.get("published"),
                         "fecha_utc": fecha.isoformat() if fecha else None, "autor": e.get("author")})
    fechas = sorted(x["fecha_utc"] for x in entradas if x["fecha_utc"])
    a = lambda s: datetime.fromisoformat(s).astimezone(MADRID).strftime("%d/%m %H:%M")  # noqa: E731
    print(f"news_{i:<4} {r.status_code} entradas={len(entradas):>3}  {a(fechas[0]) if fechas else '-'} -> "
          f"{a(fechas[-1]) if fechas else '-'}  '{feed.feed.get('title')}'")
    resultado[i] = {"titulo": feed.feed.get("title"), "entradas": entradas}
Path(salida).write_text(json.dumps(resultado, ensure_ascii=False, indent=1), "utf-8")
