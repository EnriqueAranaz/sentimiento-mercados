"""Duplicados de la misma fuente (ingesta/duplicados.py y sql/011)."""
import os
import sys
from pathlib import Path

import pytest
from dotenv import load_dotenv

from ingesta.almacen import AlmacenLocal
from ingesta.duplicados import guardar_articulos, titular_normalizado

RAIZ = Path(__file__).resolve().parent.parent
BOLSAMANIA = {"nombre": "Bolsamanía", "clave_url": r"--(\d+)\.html$"}
TRADINGVIEW = {"nombre": "TradingView", "duplicado_por_titulo_h": 48}


def _fila(url, titulo, fecha, fuente_id=1):
    return {"fuente_id": fuente_id, "url": url, "titulo": titulo, "publicado_en": fecha}


def test_bolsamania_archivo_y_sitemap_una_sola_fila(tmp_path):
    almacen = AlmacenLocal(tmp_path / "db.json")
    base = "https://www.bolsamania.com/noticias/empresas/"
    archivo = _fila(base + "bbva-cae-con-fuerza-tras-sus-resultados--23947612.html", "BBVA cae con fuerza", "2026-10-29T08:19:24+00:00")
    sitemap = _fila(base + "bbva-cae-fuerza-resultados--23947612.html", "BBVA cae con fuerza", "2026-10-29T08:29:00+00:00")
    # en el mismo lote
    assert len(guardar_articulos([dict(archivo), dict(sitemap)], BOLSAMANIA, 1, almacen)[0]) == 1
    # y en una ejecución posterior, con el mismo titular: se ignora
    assert guardar_articulos([dict(sitemap)], BOLSAMANIA, 1, almacen) == ([], [])
    assert [a["clave_fuente"] for a in almacen.datos["articulos"].values()] == ["23947612"]


def test_reenvio_de_reuters_se_marca(tmp_path):
    almacen = AlmacenLocal(tmp_path / "db.json")
    url = "https://es.tradingview.com/news/reuters.com,2026:newsml_{}:0/"
    t = "El S&P 500 y el Nasdaq cierran con fuertes caídas"
    [primero], _ = guardar_articulos([_fila(url.format("L8N4682TG"), t, "2026-10-22T20:01:32+00:00")], TRADINGVIEW, 1, almacen)
    assert primero["duplicado_de"] is None
    # ejecución posterior, mismo titular con otro espacio y punto final
    [segundo], _ = guardar_articulos([_fila(url.format("L8N4682WY"), t + " .", "2026-10-22T20:49:09+00:00")], TRADINGVIEW, 1, almacen)
    assert segundo["duplicado_de"] == primero["id"]
    # dentro del mismo lote
    lote = [_fila(url.format("A1"), "Otra noticia", "2026-10-23T10:00:00+00:00"),
            _fila(url.format("A2"), "Otra  noticia", "2026-10-23T11:00:00+00:00")]
    a, b = sorted(guardar_articulos(lote, TRADINGVIEW, 1, almacen)[0], key=lambda x: x["id"])
    assert a["duplicado_de"] is None and b["duplicado_de"] == a["id"]
    # pasadas las 48 h no es reenvío
    [tarde], _ = guardar_articulos([_fila(url.format("A3"), "Otra noticia", "2026-10-26T12:00:00+00:00")], TRADINGVIEW, 1, almacen)
    assert tarde["duplicado_de"] is None


def test_columna_diaria_de_bolsamania_no_se_marca(tmp_path):
    almacen = AlmacenLocal(tmp_path / "db.json")
    base = "https://www.bolsamania.com/noticias/analisis-tecnico/valores-destacados-al-cierre-del-mercado-norteamericano--{}.html"
    t = "Valores destacados al cierre del mercado norteamericano"
    lote1, _ = guardar_articulos([_fila(base.format(23937035), t, "2026-10-28T09:09:00+00:00")], BOLSAMANIA, 1, almacen)
    lote2, _ = guardar_articulos([_fila(base.format(23945439), t, "2026-10-29T07:39:37+00:00")], BOLSAMANIA, 1, almacen)
    assert len(lote1) == len(lote2) == 1
    assert all("duplicado_de" not in a for a in lote1 + lote2)  # la regla por titular es solo de TradingView


def test_misma_clave_titular_reescrito_actualiza_la_fila(tmp_path):
    almacen = AlmacenLocal(tmp_path / "db.json")
    base = "https://www.bolsamania.com/noticias/empresas/{}--23928202.html"
    [hsbc], _ = guardar_articulos([_fila(base.format("hsbc-anuncia-recompra"), "HSBC anuncia una recompra de hasta 1.000 millones",
                                         "2026-10-27T07:00:00+00:00")], BOLSAMANIA, 1, almacen)
    nueva = _fila(base.format("hsbc-cae-con-fuerza"), "HSBC cae con fuerza tras sus resultados", "2026-10-27T09:30:00+00:00")
    nueva["resumen"] = "La debilidad en Wealth eclipsa la recompra"
    insertadas, actualizadas = guardar_articulos([nueva], BOLSAMANIA, 1, almacen)
    assert insertadas == [] and len(actualizadas) == 1
    a = actualizadas[0]
    assert a["id"] == hsbc["id"] and a["titulo"] == "HSBC cae con fuerza tras sus resultados"
    assert a["titulo_anterior"] == "HSBC anuncia una recompra de hasta 1.000 millones"
    assert a["resumen"] == "La debilidad en Wealth eclipsa la recompra"
    assert a["publicado_en"] == "2026-10-27T07:00:00+00:00"   # la fecha de publicación no cambia
    assert almacen.datos["sin_clasificar"] == [hsbc["id"]]    # se borra su clasificación: vuelve a pendientes
    assert len(almacen.datos["articulos"]) == 1


def test_titular_normalizado():
    assert titular_normalizado("  BBVA  cae​ con fuerza… ") == "bbva cae con fuerza"


@pytest.mark.skipif(not (load_dotenv(RAIZ / ".env") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")),
                    reason="sin credenciales de Supabase")
def test_v_cobertura_no_cuenta_duplicados():
    sys.path.insert(0, str(RAIZ / "clasificacion"))
    from comun import conectar, todas

    db = conectar()
    arts = todas(db, "articulos", "id,duplicado_de")
    dups = [a for a in arts if a["duplicado_de"] is not None]
    assert dups, "no hay duplicados marcados (¿está ejecutada sql/011?)"
    cob = todas(db, "v_cobertura", "dia,fuente,n_articulos", orden="dia")
    assert sum(c["n_articulos"] for c in cob) == len(arts) - len(dups)
    ids = {a["id"] for a in dups}
    for vista in ("v_afectaciones", "v_no_relevantes"):
        assert not ids & {r["articulo_id"] for r in todas(db, vista, "articulo_id", orden="articulo_id")}


@pytest.mark.skipif(not os.environ.get("SUPABASE_SERVICE_ROLE_KEY"), reason="sin credenciales de Supabase")
def test_migracion_011_manda_la_ultima_version():
    sys.path.insert(0, str(RAIZ / "clasificacion"))
    from comun import conectar

    db = conectar()
    filas = {a["id"]: a for a in db.table("articulos").select("id,clave_fuente,duplicado_de,titulo_anterior")
             .in_("id", [9756, 9776, 8823, 9313, 2028, 2835, 2428, 2836, 7899, 8362]).execute().data}
    for viva, copia in ((9756, 9776), (8823, 9313)):              # mismo titular: sigue la primera
        assert filas[copia]["duplicado_de"] == viva and filas[viva]["duplicado_de"] is None
        assert filas[viva]["clave_fuente"] and filas[copia]["clave_fuente"] is None
    for antigua, nueva in ((2028, 2835), (2428, 2836), (7899, 8362)):  # titular reescrito: manda la nueva
        assert filas[antigua]["duplicado_de"] == nueva and filas[nueva]["duplicado_de"] is None
        assert filas[nueva]["clave_fuente"] and filas[nueva]["titulo_anterior"]
