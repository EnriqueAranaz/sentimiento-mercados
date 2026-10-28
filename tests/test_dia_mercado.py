"""dia_mercado de Supabase (sql/009) frente a indice.a_dia_mercado. Necesita .env; si no hay, se salta."""
import os
import sys
from datetime import date, timedelta
from pathlib import Path

import pytest
from dotenv import load_dotenv

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ / "clasificacion"))
load_dotenv(RAIZ / ".env")
pytestmark = pytest.mark.skipif(not os.environ.get("SUPABASE_SERVICE_ROLE_KEY"), reason="sin credenciales de Supabase")

from indice import a_dia_mercado  # noqa: E402


@pytest.fixture(scope="module")
def db():
    from comun import conectar

    return conectar()


def test_funcion_sql_igual_que_python(db):
    for i in range(14):  # dos semanas completas
        d = date(2026, 10, 19) + timedelta(days=i)
        assert db.rpc("dia_mercado", {"d": d.isoformat()}).execute().data == a_dia_mercado(d).isoformat(), d


@pytest.mark.parametrize("vista,clave", [("v_afectaciones", "id"), ("v_no_relevantes", "articulo_id"),
                                         ("v_cobertura", "dia")])
def test_vistas_igual_que_python(db, vista, clave):
    from comun import todas

    filas = todas(db, vista, "dia,dia_mercado", orden=clave)
    assert filas
    for f in filas:
        assert f["dia_mercado"] == a_dia_mercado(date.fromisoformat(f["dia"])).isoformat(), f
