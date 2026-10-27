import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "clasificacion"))

from cargar import validar  # noqa: E402
from comun import IndiceEmpresas, clave  # noqa: E402

CAT = {
    "sectores": {"Banca", "Tecnología", "Consumo y distribución"},
    "temas": {"Resultados", "Mercado", "Fusiones y OPAs"},
    "origenes": {"Hecho (empresa o dato oficial)", "Mercado", "Rumor / según fuentes"},
    "motivos_no_relevancia": {"Cripto", "Otros"},
}
IDX = IndiceEmpresas([{"id": 1, "nombre": "Santander", "alias": ["Santander", "Banco Santander"],
                       "ticker": "BME:SAN", "sector": "Banca"}])
NUEVAS = {clave("Condis"): {"nombre": "Condis", "sector": "Consumo y distribución"}}


def _v(c):
    return validar(c, CAT, IDX, NUEVAS, {1, 2, 3})


def test_relevante_valido_con_alias_y_empresa_nueva():
    err, afs = _v({"articulo_id": 1, "relevante": True, "tema": "Fusiones y OPAs", "origen": "Rumor / según fuentes",
                   "afectaciones": [{"ambito": "Empresa", "objeto": "Banco Santander", "sector": "Banca", "valor": 1},
                                    {"ambito": "Empresa", "objeto": "Condis", "sector": "Consumo y distribución", "valor": 0},
                                    {"ambito": "Global", "objeto": "Petróleo", "sector": None, "valor": -1}]})
    assert err == []
    assert afs[0]["empresa_id"] == 1 and afs[0]["objeto"] == "Santander"
    assert afs[1]["empresa_id"] is None


def test_empresa_nombrada_excluye_sector():
    err, _ = _v({"articulo_id": 1, "relevante": True, "tema": "Mercado", "origen": "Mercado",
                 "afectaciones": [{"ambito": "Empresa", "objeto": "Santander", "sector": "Banca", "valor": -1},
                                  {"ambito": "Sector", "objeto": "Banca", "sector": "Banca", "valor": -1}]})
    assert any("11 e" in e for e in err)
    err, _ = _v({"articulo_id": 1, "relevante": True, "tema": "Mercado", "origen": "Mercado",
                 "afectaciones": [{"ambito": "Sector", "objeto": "Banca", "sector": "Banca", "valor": -1}]})
    assert err == []


def test_no_relevante_necesita_motivo_valido():
    assert _v({"articulo_id": 2, "relevante": False, "motivo_no_relevante": "Cripto"})[0] == []
    assert _v({"articulo_id": 2, "relevante": False, "motivo_no_relevante": "cripto"})[0]
    assert _v({"articulo_id": 2, "relevante": False})[0]


def test_errores_de_catalogo_valor_sector_y_empresa():
    err, _ = _v({"articulo_id": 3, "relevante": True, "tema": "Resultado", "origen": "Hecho",
                 "afectaciones": [{"ambito": "Empresa", "objeto": "Acme", "sector": "Banca", "valor": 3},
                                  {"ambito": "Mercado", "objeto": "Ibex 35", "sector": "Banca", "valor": 0},
                                  {"ambito": "Global", "objeto": "Bolsas", "valor": 0},
                                  {"ambito": "Empresa", "objeto": "Santander", "sector": None, "valor": 0}]})
    texto = " | ".join(err)
    for esperado in ("tema no válido", "origen no válido", "fuera de -2..2", "empresa desconocida",
                     "Mercado no lleva sector", "objeto de Global no válido", "sector obligatorio"):
        assert esperado in texto, esperado


def test_relevante_sin_afectaciones_y_articulo_inexistente():
    assert "al menos 1 afectación" in " ".join(_v({"articulo_id": 1, "relevante": True, "tema": "Mercado",
                                                    "origen": "Mercado", "afectaciones": []})[0])
    assert _v({"articulo_id": 99, "relevante": False, "motivo_no_relevante": "Otros"})[0]


def test_no_relevante_con_afectaciones_se_rechaza():
    err, _ = _v({"articulo_id": 2, "relevante": False, "motivo_no_relevante": "Otros",
                 "afectaciones": [{"ambito": "Global", "objeto": "Mercados", "sector": None, "valor": -1}]})
    assert any("no lleva tema, origen ni afectaciones" in e for e in err)


def test_version_criterios_unica_y_documentada():
    import comun
    from ingesta import reglas

    assert comun.VERSION_CRITERIOS is reglas.VERSION_CRITERIOS
    cabecera = (Path(__file__).resolve().parent.parent / "docs" / "criterios_clasificacion.md").read_text("utf-8")[:400]
    assert f"`{reglas.VERSION_CRITERIOS}`" in cabecera
