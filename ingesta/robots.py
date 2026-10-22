"""Intérprete de robots.txt (RFC 9309) con comodines `*` y `$`.

`urllib.robotparser` no soporta comodines, que usan Expansión, Rankia o Cinco Días,
así que se implementa aquí: regla más larga gana y, en empate, Allow.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from urllib.parse import urlsplit


@dataclass
class _Grupo:
    agentes: list[str] = field(default_factory=list)
    reglas: list[tuple[bool, str]] = field(default_factory=list)  # (allow, patrón)


def _patron_a_regex(patron: str) -> re.Pattern:
    ancla = patron.endswith("$")
    if ancla:
        patron = patron[:-1]
    cuerpo = "".join(".*" if c == "*" else re.escape(c) for c in patron)
    return re.compile("^" + cuerpo + ("$" if ancla else ""))


class Robots:
    def __init__(self, texto: str | None, permitir_todo: bool = False, denegar_todo: bool = False):
        self.permitir_todo = permitir_todo
        self.denegar_todo = denegar_todo
        self.grupos: list[_Grupo] = self._parsear(texto or "")

    @staticmethod
    def _parsear(texto: str) -> list[_Grupo]:
        grupos: list[_Grupo] = []
        actual: _Grupo | None = None
        ultimo_fue_agente = False
        for linea in texto.splitlines():
            linea = linea.split("#", 1)[0].strip()
            if ":" not in linea:
                continue
            clave, valor = (p.strip() for p in linea.split(":", 1))
            clave = clave.lower()
            if clave == "user-agent":
                if actual is None or not ultimo_fue_agente:
                    actual = _Grupo()
                    grupos.append(actual)
                actual.agentes.append(valor.lower())
                ultimo_fue_agente = True
            elif clave in ("allow", "disallow") and actual is not None:
                ultimo_fue_agente = False
                if valor:  # "Disallow:" vacío no restringe nada
                    actual.reglas.append((clave == "allow", valor))
            else:
                ultimo_fue_agente = False
        return grupos

    def _grupo_para(self, user_agent: str) -> list[tuple[bool, str]]:
        token = user_agent.split("/", 1)[0].strip().lower()
        especificas = [g for g in self.grupos if any(a != "*" and a in token for a in g.agentes)]
        if especificas:
            return [r for g in especificas for r in g.reglas]
        return [r for g in self.grupos if "*" in g.agentes for r in g.reglas]

    def permitido(self, url: str, user_agent: str) -> bool:
        if self.denegar_todo:
            return False
        if self.permitir_todo:
            return True
        partes = urlsplit(url)
        ruta = (partes.path or "/") + (f"?{partes.query}" if partes.query else "")
        mejor: tuple[int, bool] | None = None
        for allow, patron in self._grupo_para(user_agent):
            if _patron_a_regex(patron).match(ruta):
                clave = (len(patron), allow)
                if mejor is None or clave > mejor:
                    mejor = clave
        return True if mejor is None else mejor[1]
