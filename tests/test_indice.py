import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "clasificacion"))

from indice import a_dia_mercado, calcular, componentes, valor_indice, ventana  # noqa: E402

LUNES = date(2026, 10, 26)
COBERTURA_OK = {d: 100.0 for d in ventana(LUNES)}


def af(ambito, objeto, valor, dia="2026-10-26", origen="Mercado", sector=None, ticker=None, en_universo=None,
       mercado=None):
    return {"dia": dia, "ambito": ambito, "objeto": objeto, "sector": sector, "ticker": ticker,
            "en_universo": en_universo, "valor": valor, "origen": origen, "version_criterios": "v3.8",
            "mercado": mercado}


def emp(nombre, valor, **kw):
    return af("Empresa", nombre, valor, sector="Banca", ticker=f"BME:{nombre[:3].upper()}", en_universo=True,
              mercado="Ibex 35", **kw)


def general(filas, linea="total", dia=LUNES):
    return next(f for f in filas if f["alcance"] == "general" and f["linea"] == linea
                and f["dia_mercado"] == dia.isoformat())


def test_fin_de_semana_cuenta_para_el_lunes():
    assert a_dia_mercado(date(2026, 10, 24)) == LUNES   # sábado
    assert a_dia_mercado(date(2026, 10, 25)) == LUNES   # domingo
    assert a_dia_mercado(date(2026, 10, 23)) == date(2026, 10, 23)
    assert ventana(LUNES) == [date(2026, 10, 20), date(2026, 10, 21), date(2026, 10, 22), date(2026, 10, 23), LUNES]
    filas = calcular([af("Mercado", "Ibex 35", 1, dia="2026-10-25")], COBERTURA_OK, [])
    assert {f["dia_mercado"] for f in filas} == {LUNES.isoformat()}


def test_exclusiones():
    afs = [af("Global", "Petróleo", 2), af("Global", "Divisas", 2), af("Global", "Materias primas", 2),
           af("Empresa", "Chica", 2, sector="Banca", ticker="BME:CH", en_universo=False, mercado="Ibex 35"),
           af("Sector", "Banca", -1, sector="Banca"), af("Mercado", "Ibex 35", -1)]
    f = general(calcular(afs, COBERTURA_OK, ["Banca"]))
    assert f["n_afectaciones"] == 2  # solo el Sector y el Mercado


def test_cada_empresa_cuenta_igual_en_c2():
    afs = [emp("Santander", 2)] * 10 + [emp(n, -2) for n in ("BBVA", "Caixabank", "Sabadell", "Bankinter")]
    c, n_unidades = componentes(afs, "espana")
    assert n_unidades == 5
    assert c["c2"] == ((2 - 2 * 4) / 5) / 2      # media entre unidades, no entre afectaciones
    assert c["c3"] == (1 - 4) / 5


def test_componente_omitido_reparte_pesos():
    # 5 empresas y ninguna afectación de Mercado: C1 se omite y el resto pesa 30/15/15 sobre 60.
    afs = [emp(n, 1) for n in ("Santander", "BBVA", "Caixabank", "Sabadell", "Bankinter")]
    c, _ = componentes(afs, "espana")
    assert c["c1"] is None and c["c2"] == 0.5 and c["c3"] == 1.0 and c["c4"] == 0.0
    assert valor_indice(c) == round(((30 * 0.5 + 15 * 1.0 + 15 * 0.0) / 60 + 1) * 50, 1)  # 75.0


def test_sin_dato_por_minimo_y_por_cobertura():
    pocas = [af("Mercado", "Ibex 35", 1)] * 19
    f = general(calcular(pocas, COBERTURA_OK, []))
    assert not f["publicado"] and f["valor"] is None and "menos de 20" in f["motivo_no_publicado"]
    assert f["c1"] is not None  # los componentes se guardan aunque no se publique

    bastantes = [af("Mercado", "Ibex 35", 1)] * 20
    assert general(calcular(bastantes, COBERTURA_OK, []))["valor"] == round((40 * 0.5 / 55 + 1) * 50, 1)  # C1 y C4
    cobertura_mala = {**COBERTURA_OK, date(2026, 10, 22): 85.0}
    f = general(calcular(bastantes, cobertura_mala, []))
    assert not f["publicado"] and f["valor"] is None and "22/10" in f["motivo_no_publicado"]


def test_lineas_separan_origenes():
    afs = [af("Mercado", "Ibex 35", -2, origen="Opinión / prensa")] * 20 + [af("Mercado", "Ibex 35", 2,
                                                                                origen="Analista")] * 20
    filas = calcular(afs, COBERTURA_OK, [])
    assert general(filas, "narrativa")["valor"] == 0.0
    assert general(filas, "hechos")["valor"] == 100.0
    assert general(filas, "total")["n_afectaciones"] == 40
