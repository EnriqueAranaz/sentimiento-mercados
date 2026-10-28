import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "clasificacion"))

import indice  # noqa: E402
from indice import a_dia_mercado, calcular, componentes, divergencia, valor_indice, ventana  # noqa: E402

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
    filas = calcular([af("Mercado", "Ibex 35", 1, dia="2026-10-25")], COBERTURA_OK, [])[0]
    assert {f["dia_mercado"] for f in filas} == {LUNES.isoformat()}


def test_exclusiones():
    afs = [af("Global", "Petróleo", 2), af("Global", "Divisas", 2), af("Global", "Materias primas", 2),
           af("Empresa", "Chica", 2, sector="Banca", ticker="BME:CH", en_universo=False, mercado="Ibex 35"),
           af("Sector", "Banca", -1, sector="Banca"), af("Mercado", "Ibex 35", -1)]
    f = general(calcular(afs, COBERTURA_OK, ["Banca"])[0])
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
    f = general(calcular(pocas, COBERTURA_OK, [])[0])
    assert not f["publicado"] and f["valor"] is None and "menos de 20" in f["motivo_no_publicado"]
    assert f["c1"] is not None  # los componentes se guardan aunque no se publique

    bastantes = [af("Mercado", "Ibex 35", 1)] * 20
    assert general(calcular(bastantes, COBERTURA_OK, [])[0])["valor"] == round((40 * 0.5 / 55 + 1) * 50, 1)  # C1 y C4
    cobertura_mala = {**COBERTURA_OK, date(2026, 10, 22): 85.0}
    f = general(calcular(bastantes, cobertura_mala, [])[0])
    assert not f["publicado"] and f["valor"] is None and "22/10" in f["motivo_no_publicado"]


def test_lineas_separan_origenes():
    afs = [af("Mercado", "Ibex 35", -2, origen="Opinión / prensa")] * 20 + [af("Mercado", "Ibex 35", 2,
                                                                                origen="Analista")] * 20
    filas = calcular(afs, COBERTURA_OK, [])[0]
    assert general(filas, "narrativa")["valor"] == 0.0
    assert general(filas, "hechos")["valor"] == 100.0
    assert general(filas, "total")["n_afectaciones"] == 40


def test_divergencia_compara_los_mismos_objetos(monkeypatch):
    afs = [af("Mercado", "Ibex 35", -2, origen="Opinión / prensa"), af("Mercado", "Ibex 35", 0, origen="Analista"),
           emp("Santander", 1, origen="Rumor / según fuentes"), emp("Santander", 1, origen="Hecho (empresa o dato oficial)"),
           emp("Santander", 2, origen="Hecho (empresa o dato oficial)"),
           emp("BBVA", 2, origen="Hecho (empresa o dato oficial)")]  # BBVA solo tiene hechos: no entra
    assert divergencia(afs) == (None, 2)  # menos de 5 objetos: sin dato
    monkeypatch.setattr(indice, "MIN_UNIDADES_DIVERGENCIA", 1)
    # Ibex: (-2 - 0) / 2 = -1 · Santander: (1 - 1.5) / 2 = -0.25 · media -0.625 × 50
    assert divergencia(afs) == (-31.2, 2)


def test_sin_filas_ni_datos_antes_de_fecha_inicio():
    afs = [af("Mercado", "Ibex 35", -2, dia="2026-10-20")] * 30 + [af("Mercado", "Ibex 35", 1, dia="2026-10-22")] * 20
    filas, divergencias = calcular(afs, COBERTURA_OK, [])
    assert min(f["dia_mercado"] for f in filas + divergencias) == "2026-10-22"
    f = general(filas, dia=date(2026, 10, 22))
    assert f["n_afectaciones"] == 20 and f["publicado"]  # la ventana solo usa datos desde el 22/10
    assert f["ventana_dias"] == 5 and f["dias_con_datos"] == 1  # ventana incompleta: solo el 22/10 tiene datos
    assert all(d["dias_con_datos"] == 1 for d in divergencias)


def test_sin_divergencia_en_sectores():
    afs = [af("Sector", "Banca", 1, sector="Banca")] * 10
    filas, divergencias = calcular(afs, COBERTURA_OK, ["Banca"])
    assert any(f["alcance"] == "sector:Banca" for f in filas)
    assert {d["alcance"] for d in divergencias} == {"general", "espana", "europa", "eeuu"}


def test_sectores_con_ventana_de_20_dias():
    viernes = date(2026, 11, 13)  # 20 días de mercado hacia atrás llegan al 19/10; 5 días, solo al 09/11
    cobertura = {d: 100.0 for d in indice.ventana(viernes, 20)}
    afs = [af("Sector", "Banca", 1, sector="Banca", dia="2026-10-22")] * 10 + [af("Mercado", "Ibex 35", 1,
                                                                                    dia="2026-11-13")]
    filas, _ = calcular(afs, cobertura, ["Banca"])
    sector = next(f for f in filas if f["alcance"] == "sector:Banca" and f["linea"] == "total"
                  and f["dia_mercado"] == viernes.isoformat())
    assert sector["ventana_dias"] == 20 and sector["n_afectaciones"] == 10 and sector["publicado"]
    assert general(filas, dia=viernes)["ventana_dias"] == 5 and general(filas, dia=viernes)["n_afectaciones"] == 1
