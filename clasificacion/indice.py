"""Índice de sentimiento v1 (definición en docs/indice_sentimiento.md).

Recalcula TODO el histórico a partir de v_afectaciones y v_cobertura y lo guarda en indice_sentimiento y
indice_divergencia (borra e inserta las filas de VERSION_INDICE).

Uso:
    python clasificacion/indice.py                 # recalcula y guarda
    python clasificacion/indice.py --sin-guardar   # recalcula y muestra el general, sin escribir en Supabase
"""
from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone

from comun import conectar, todas

VERSION_INDICE = "1.1"  # 1.1: divergencia por objetos, inicio 22/10, sectores a 20 días
FECHA_INICIO = date(2026, 10, 22)  # inicio de la ingesta automática: no hay filas antes ni se usan datos anteriores
DIAS_VENTANA = 5
DIAS_VENTANA_SECTOR = 20
MIN_DATOS = 5            # mínimo de datos por componente (afectaciones en C1/C4, unidades en C2/C3)
MIN_AFECTACIONES = {"general": 20}
MIN_AFECTACIONES_RESTO = 10
MIN_UNIDADES_DIVERGENCIA = 5
MIN_COBERTURA = 90.0     # pct_clasificado mínimo de cada día de la ventana
PESOS = {"c1": 40, "c2": 30, "c3": 15, "c4": 15}

GLOBAL_EXCLUIDOS = {"Petróleo", "Materias primas", "Divisas"}
GLOBAL_GENERAL = {"Mercados", "Economía"}
LINEAS = {
    "narrativa": {"Opinión / prensa", "Rumor / según fuentes", "Mercado"},
    "hechos": {"Hecho (empresa o dato oficial)", "Analista"},
    "total": None,  # todos los orígenes
}
GEO = {  # alcance: (objetos de Mercado, valores de empresas.mercado)
    "espana": ({"Ibex 35", "España"}, {"Ibex 35"}),
    "europa": ({"Europa", "DAX", "Francia", "Reino Unido", "Italia", "Portugal", "Alemania", "España", "Ibex 35"},
               {"Europa", "DAX", "Ibex 35"}),
    "eeuu": ({"EE. UU."}, {"EE. UU."}),
}


def a_dia_mercado(d: date) -> date:
    """Sábado y domingo cuentan para el lunes siguiente."""
    return d + timedelta(days=7 - d.weekday()) if d.weekday() >= 5 else d


def ventana(d: date, n: int = DIAS_VENTANA) -> list[date]:
    """Los n días de mercado (lunes a viernes) que terminan en d."""
    dias, x = [], d
    while len(dias) < n:
        if x.weekday() < 5:
            dias.append(x)
        x -= timedelta(days=1)
    return dias[::-1]


def excluida(a: dict) -> bool:
    return ((a["ambito"] == "Global" and a["objeto"] in GLOBAL_EXCLUIDOS)
            or (a["ambito"] == "Empresa" and not a["en_universo"]))


def en_alcance(a: dict, alcance: str) -> bool:
    amb = a["ambito"]
    if alcance == "general":
        return True
    if alcance.startswith("sector:"):
        return amb in ("Sector", "Empresa") and a["sector"] == alcance[7:]
    objetos, mercados = GEO[alcance]
    return (amb == "Mercado" and a["objeto"] in objetos) or (amb == "Empresa" and a.get("mercado") in mercados)


def unidad(a: dict) -> str:
    """Objeto al que se refiere una afectación: empresa (por ticker), sector u objeto de Mercado o Global."""
    if a["ambito"] == "Empresa":
        return "E:" + (a.get("ticker") or a["objeto"])
    if a["ambito"] == "Sector":
        return "S:" + a["sector"]
    return a["ambito"][0] + ":" + a["objeto"]


def divergencia(afs: list[dict]) -> tuple[float | None, int]:
    """Media, entre los objetos con afectaciones de narrativa Y de hechos, de (media narrativa − media hechos) / 2,
    en puntos de la escala del índice (× 50). Devuelve (valor o None si hay menos de MIN_UNIDADES_DIVERGENCIA, n)."""
    valores: dict[str, dict[str, list[int]]] = defaultdict(lambda: {"narrativa": [], "hechos": []})
    for a in afs:
        for linea in ("narrativa", "hechos"):
            if a["origen"] in LINEAS[linea]:
                valores[unidad(a)][linea].append(a["valor"])
    difs = [(sum(v["narrativa"]) / len(v["narrativa"]) - sum(v["hechos"]) / len(v["hechos"])) / 2
            for v in valores.values() if v["narrativa"] and v["hechos"]]
    if len(difs) < MIN_UNIDADES_DIVERGENCIA:
        return None, len(difs)
    return round(sum(difs) / len(difs) * 50, 1), len(difs)


def componentes(afs: list[dict], alcance: str) -> tuple[dict[str, float | None], int]:
    """C1..C4 (None si hay menos de MIN_DATOS) y nº de unidades."""
    c: dict[str, float | None] = dict.fromkeys(PESOS)
    if not alcance.startswith("sector:"):
        mercado = [a["valor"] for a in afs if a["ambito"] in ("Mercado", "Global")]
        if len(mercado) >= MIN_DATOS:
            c["c1"] = sum(v / 2 for v in mercado) / len(mercado)
    unidades: dict[str, list[int]] = defaultdict(list)
    for a in afs:
        if a["ambito"] in ("Empresa", "Sector"):
            unidades[unidad(a)].append(a["valor"])
    medias = [sum(v) / len(v) for v in unidades.values()]
    if len(medias) >= MIN_DATOS:
        c["c2"] = sum(medias) / len(medias) / 2
        c["c3"] = (sum(m > 0 for m in medias) - sum(m < 0 for m in medias)) / len(medias)
    if len(afs) >= MIN_DATOS:
        c["c4"] = (sum(a["valor"] == 2 for a in afs) - sum(a["valor"] == -2 for a in afs)) / len(afs)
    return c, len(medias)


def valor_indice(c: dict[str, float | None]) -> float | None:
    usados = [k for k, v in c.items() if v is not None]
    if not usados:
        return None
    media = sum(PESOS[k] * c[k] for k in usados) / sum(PESOS[k] for k in usados)
    return round((media + 1) * 50, 1)


def cobertura_por_dia(filas: list[dict]) -> dict[date, float]:
    """pct_clasificado por día de mercado, sumando fuentes (y el fin de semana en el lunes)."""
    tot, clas = defaultdict(int), defaultdict(int)
    for f in filas:
        d = a_dia_mercado(date.fromisoformat(f["dia"]))
        tot[d] += f["n_articulos"]
        clas[d] += f["n_clasificados"]
    return {d: 100.0 * clas[d] / tot[d] for d in tot if tot[d]}


def calcular(afectaciones: list[dict], cobertura: dict[date, float],
             sectores: list[str]) -> tuple[list[dict], list[dict]]:
    """Filas de indice_sentimiento e indice_divergencia para todos los días de mercado con datos desde FECHA_INICIO.
    La divergencia solo se calcula para general y los alcances geográficos.

    afectaciones: filas de v_afectaciones con `mercado` de la empresa añadido.
    """
    afs = [{**a, "dm": a_dia_mercado(date.fromisoformat(a["dia"]))} for a in afectaciones if not excluida(a)]
    afs = [a for a in afs if a["dm"] >= FECHA_INICIO]
    if not afs:
        return [], []
    por_dia = defaultdict(list)
    for a in afs:
        por_dia[a["dm"]].append(a)
    inicio, fin = min(por_dia), max(por_dia)
    alcances = ["general", *GEO, *(f"sector:{s}" for s in sectores)]
    filas, divergencias, d = [], [], inicio
    while d <= fin:
        if d.weekday() < 5:
            for alcance in alcances:
                n_dias = DIAS_VENTANA_SECTOR if alcance.startswith("sector:") else DIAS_VENTANA
                dias = [x for x in ventana(d, n_dias) if x >= FECHA_INICIO]
                sin_cobertura = [x for x in dias if cobertura.get(x, 0.0) < MIN_COBERTURA]
                del_alcance = [a for x in dias for a in por_dia.get(x, []) if en_alcance(a, alcance)]
                # días de la ventana con alguna afectación (de cualquier alcance): marca ventanas incompletas
                ventana_info = {"ventana_dias": n_dias, "dias_con_datos": sum(1 for x in dias if por_dia.get(x))}
                for linea, origenes in LINEAS.items():
                    sel = [a for a in del_alcance if origenes is None or a["origen"] in origenes]
                    filas.append({**fila(d, alcance, linea, sel, sin_cobertura), **ventana_info})
                if not alcance.startswith("sector:"):
                    divergencias.append({**fila_divergencia(d, alcance, del_alcance, sin_cobertura),
                                         "dias_con_datos": ventana_info["dias_con_datos"]})
        d += timedelta(days=1)
    return filas, divergencias


def fila(d: date, alcance: str, linea: str, afs: list[dict], sin_cobertura: list[date]) -> dict:
    c, n_unidades = componentes(afs, alcance)
    valor = valor_indice(c)
    minimo = MIN_AFECTACIONES.get(alcance, MIN_AFECTACIONES_RESTO)
    motivo = None
    if len(afs) < minimo:
        motivo = f"menos de {minimo} afectaciones ({len(afs)})"
    elif sin_cobertura:
        motivo = "cobertura < 90 % en " + ", ".join(x.strftime("%d/%m") for x in sin_cobertura)
    elif valor is None:
        motivo = "ningún componente con datos suficientes"
    publicado = motivo is None
    return {
        "dia_mercado": d.isoformat(), "alcance": alcance, "linea": linea,
        "valor": valor if publicado else None,
        **{k: (round(v, 4) if v is not None else None) for k, v in c.items()},
        "componentes_usados": [k for k, v in c.items() if v is not None],
        "n_afectaciones": len(afs), "n_unidades": n_unidades,
        "publicado": publicado, "motivo_no_publicado": motivo,
        "version_indice": VERSION_INDICE,
        "versiones_criterios": ", ".join(sorted({a["version_criterios"] for a in afs})) or None,
    }


def fila_divergencia(d: date, alcance: str, afs: list[dict], sin_cobertura: list[date]) -> dict:
    valor, n = divergencia(afs)
    motivo = None
    if valor is None:
        motivo = f"sin dato: menos de {MIN_UNIDADES_DIVERGENCIA} objetos con narrativa y hechos ({n})"
    elif sin_cobertura:
        motivo = "cobertura < 90 % en " + ", ".join(x.strftime("%d/%m") for x in sin_cobertura)
    return {"dia_mercado": d.isoformat(), "alcance": alcance, "valor": valor if motivo is None else None,
            "n_unidades_divergencia": n, "publicado": motivo is None, "motivo_no_publicado": motivo,
            "version_indice": VERSION_INDICE}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--sin-guardar", action="store_true", help="no escribe en Supabase")
    args = ap.parse_args()
    db = conectar()
    mercado = {e["nombre"]: e["mercado"] for e in todas(db, "empresas", "id,nombre,mercado")}
    afs = todas(db, "v_afectaciones", "id,dia,ambito,objeto,sector,ticker,en_universo,valor,origen,version_criterios")
    for a in afs:
        a["mercado"] = mercado.get(a["objeto"]) if a["ambito"] == "Empresa" else None
    cobertura = cobertura_por_dia(todas(db, "v_cobertura", "dia,fuente,n_articulos,n_clasificados", orden="dia"))
    sectores = [s["nombre"] for s in db.table("sectores").select("nombre").execute().data]
    filas, divergencias = calcular(afs, cobertura, sorted(sectores))
    print(f"índice {VERSION_INDICE}: {len(filas)} filas ({sum(f['publicado'] for f in filas)} publicadas) · "
          f"divergencia: {len(divergencias)} filas ({sum(f['publicado'] for f in divergencias)} publicadas)")
    if args.sin_guardar:
        for f in filas:
            if f["alcance"] == "general":
                print(f"  {f['dia_mercado']} {f['linea']:<9} {f['valor'] if f['publicado'] else '—':>5} "
                      f"n={f['n_afectaciones']:>3} {f['motivo_no_publicado'] or ''}")
        for f in divergencias:
            if f["alcance"] == "general":
                print(f"  {f['dia_mercado']} divergencia {f['valor'] if f['publicado'] else '—':>5} "
                      f"unidades={f['n_unidades_divergencia']:>3} {f['motivo_no_publicado'] or ''}")
        return 0
    ahora = datetime.now(timezone.utc).isoformat()
    for tabla, datos in (("indice_sentimiento", filas), ("indice_divergencia", divergencias)):
        db.table(tabla).delete().eq("version_indice", VERSION_INDICE).execute()
        for i in range(0, len(datos), 500):
            db.table(tabla).insert([{**f, "calculado_en": ahora} for f in datos[i:i + 500]]).execute()
    print("guardado en indice_sentimiento e indice_divergencia")
    return 0


if __name__ == "__main__":
    sys.exit(main())
