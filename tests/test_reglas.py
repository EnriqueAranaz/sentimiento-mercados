from ingesta.reglas import compilar_alias, detectar

EMPRESAS = [
    {"id": 1, "nombre": "Santander", "alias": ["Santander", "Banco Santander"], "ticker": "BME:SAN"},
    {"id": 2, "nombre": "Acciona", "alias": ["Acciona"], "ticker": "BME:ANA"},
    {"id": 3, "nombre": "Acciona Energía", "alias": ["Acciona Energía", "Acciona Energia"], "ticker": "BME:ANE"},
    {"id": 4, "nombre": "Meta", "alias": ["Meta", "Meta Platforms", "Facebook"], "ticker": "NASDAQ:META"},
    {"id": 5, "nombre": "Dia", "alias": ["Dia"], "ticker": "BME:DIA"},
    {"id": 6, "nombre": "Telefónica", "alias": ["Telefónica", "Telefonica"], "ticker": "BME:TEF"},
    {"id": 7, "nombre": "Procter & Gamble", "alias": ["Procter & Gamble", "P&G"], "ticker": "NYSE:PG"},
    {"id": 8, "nombre": "Huntington", "alias": ["Huntington Bancshares"], "ticker": "NASDAQ:HBAN"},
]
ALIAS = compilar_alias(EMPRESAS)
POR_TICKER = {e["ticker"]: e for e in EMPRESAS}


def _det(titulo, seccion=None, simbolos=None):
    dets, cripto = detectar({"id": 1, "titulo": titulo, "seccion": seccion, "simbolos": simbolos}, ALIAS, POR_TICKER)
    return {(d["tipo"], d["objeto"], d["metodo"]) for d in dets}, cripto


def test_alias_sin_mayusculas_ni_tildes_y_palabra_completa():
    dets, _ = _det("TELEFONICA y banco santander suben; el santanderismo no cuenta")
    assert ("empresa", "Telefónica", "alias") in dets
    assert ("empresa", "Santander", "alias") in dets
    assert len([d for d in dets if d[0] == "empresa"]) == 2


def test_gana_el_alias_mas_largo():
    dets, _ = _det("Acciona Energía dispara su beneficio")
    assert ("empresa", "Acciona Energía", "alias") in dets
    assert not any(d[1] == "Acciona" for d in dets)


def test_alias_sensibles_exigen_mayuscula():
    dets, _ = _det("El Ibex cumple su meta del día")
    assert not any(d[0] == "empresa" for d in dets)
    dets, _ = _det("Meta y Dia caen en bolsa")
    assert {("empresa", "Meta", "alias"), ("empresa", "Dia", "alias")} <= dets


def test_puntuacion_en_alias_y_simbolos_de_tradingview():
    dets, _ = _det("P&G eleva previsiones", simbolos=["NASDAQ:HBAN"])
    assert ("empresa", "Procter & Gamble", "alias") in dets
    assert ("empresa", "Huntington", "simbolo") in dets


def test_mercados_y_globales():
    dets, _ = _det("Wall Street y el Ibex caen mientras el Brent sube y el oro marca récord; el euro/dólar, plano")
    assert {("mercado", "EE. UU.", "palabra"), ("mercado", "Ibex 35", "palabra"), ("global", "Petróleo", "palabra"),
            ("global", "Materias primas", "palabra"), ("global", "Divisas", "palabra")} <= dets
    dets, _ = _det("El S&P 500 y el Nasdaq cierran en máximos")
    assert ("mercado", "EE. UU.", "palabra") in dets


def test_cripto_por_seccion_y_por_titular():
    assert _det("Cualquier titular", seccion="news/Beincrypto")[1] is True
    assert _det("El bitcoin pierde los 80.000 dólares")[1] is True
    assert _det("Las stablecoins ganan peso")[1] is True
    assert _det("Santander gana un 10% más")[1] is False
