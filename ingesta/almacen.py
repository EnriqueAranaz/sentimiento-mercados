"""Persistencia: Supabase (producción) o un JSON local (--dry-run, para probar sin base de datos)."""
from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path

CAMPOS_FUENTE = ("nombre", "tipo_acceso", "tipo_fuente", "url", "idioma", "activa")
_LOTE = 50


class AlmacenSupabase:
    def __init__(self, url: str, service_role_key: str):
        from supabase import create_client

        self.db = create_client(url, service_role_key)

    def sincronizar_fuentes(self, fuentes: list[dict]) -> dict[str, int]:
        filas = [{k: f[k] for k in CAMPOS_FUENTE} for f in fuentes]
        res = self.db.table("fuentes").upsert(filas, on_conflict="nombre").execute()
        return {r["nombre"]: r["id"] for r in res.data}

    def urls_conocidas(self, urls: list[str]) -> set[str]:
        conocidas: set[str] = set()
        for i in range(0, len(urls), _LOTE):
            res = self.db.table("articulos").select("url").in_("url", urls[i:i + _LOTE]).execute()
            conocidas.update(r["url"] for r in res.data)
        return conocidas

    def tiene_articulos(self, fuente_id: int) -> bool:
        res = self.db.table("articulos").select("id").eq("fuente_id", fuente_id).limit(1).execute()
        return bool(res.data)

    def ultima_ejecucion(self, fuente_id: int) -> datetime | None:
        res = (
            self.db.table("ejecuciones").select("inicio")
            .eq("fuente_id", fuente_id).in_("estado", ["ok", "parcial"])
            .order("inicio", desc=True).limit(1).execute()
        )
        return datetime.fromisoformat(res.data[0]["inicio"]) if res.data else None

    def insertar_articulos(self, filas: list[dict]) -> int:
        nuevos = 0
        for i in range(0, len(filas), _LOTE):
            res = (
                self.db.table("articulos")
                .upsert(filas[i:i + _LOTE], on_conflict="url", ignore_duplicates=True)  # ON CONFLICT (url) DO NOTHING
                .execute()
            )
            nuevos += len(res.data)
        return nuevos

    def registrar_ejecucion(self, fila: dict) -> None:
        self.db.table("ejecuciones").insert(fila).execute()


class AlmacenLocal:
    """Simula la base de datos en un JSON para ejecutar sin Supabase."""

    def __init__(self, ruta: Path):
        self.ruta = ruta
        self.datos = json.loads(ruta.read_text("utf-8")) if ruta.exists() else {"fuentes": {}, "articulos": {}, "ejecuciones": []}

    def _guardar(self) -> None:
        self.ruta.parent.mkdir(parents=True, exist_ok=True)
        self.ruta.write_text(json.dumps(self.datos, ensure_ascii=False, indent=1, default=str), "utf-8")

    def sincronizar_fuentes(self, fuentes: list[dict]) -> dict[str, int]:
        for f in fuentes:
            previo = self.datos["fuentes"].get(f["nombre"], {})
            self.datos["fuentes"][f["nombre"]] = {
                **{k: f[k] for k in CAMPOS_FUENTE},
                "id": previo.get("id", len(self.datos["fuentes"]) + 1),
            }
        self._guardar()
        return {n: f["id"] for n, f in self.datos["fuentes"].items()}

    def urls_conocidas(self, urls: list[str]) -> set[str]:
        return {u for u in urls if u in self.datos["articulos"]}

    def tiene_articulos(self, fuente_id: int) -> bool:
        return any(a["fuente_id"] == fuente_id for a in self.datos["articulos"].values())

    def ultima_ejecucion(self, fuente_id: int) -> datetime | None:
        inicios = [e["inicio"] for e in self.datos["ejecuciones"] if e["fuente_id"] == fuente_id and e["estado"] in ("ok", "parcial")]
        return datetime.fromisoformat(max(inicios)) if inicios else None

    def insertar_articulos(self, filas: list[dict]) -> int:
        nuevos = 0
        for f in filas:
            if f["url"] not in self.datos["articulos"]:
                self.datos["articulos"][f["url"]] = f
                nuevos += 1
        self._guardar()
        return nuevos

    def registrar_ejecucion(self, fila: dict) -> None:
        self.datos["ejecuciones"].append(fila)
        self._guardar()


def crear_almacen(dry_run: bool, ruta_local: Path):
    if dry_run:
        return AlmacenLocal(ruta_local)
    url, key = os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        raise SystemExit("Faltan SUPABASE_URL / SUPABASE_SERVICE_ROLE_KEY (en .env o en los secrets). Usa --dry-run para probar sin base de datos.")
    return AlmacenSupabase(url, key)
