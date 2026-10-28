---
description: Aprueba o descarta empresas propuestas por el agente y reclasifica sus noticias
argument-hint: "aprobar: Nombre, Nombre · descartar: Nombre (motivo)"
---

Aplica la decisión de Enrique sobre las empresas propuestas ($ARGUMENTS). Si no se indica nada, muestra primero
`.venv\Scripts\python.exe clasificacion\decidir_empresas.py --estado` y pregunta qué aprobar y qué descartar.

1. Ejecuta `clasificacion\decidir_empresas.py` con un `--aprobar "Nombre"` por cada aprobada y un `--descartar "Nombre"`
   por cada descartada, con su `--motivo` (microcotizada, banco regional de EE. UU., pequeña de menos de ~4.000 M…).
   Si las descartadas tienen motivos distintos, una ejecución por motivo. El script da de alta las aprobadas
   (`semilla_empresas.py`), añade las descartadas a `docs/empresas_descartadas.md` y exporta sus noticias a un
   `clasificacion\lotes\pendiente_<n>.json`.
2. Si exportó noticias, lanza el subagente `clasificador-noticias` solo sobre ese `pendiente_<n>.json` (no sobre los
   pendientes normales), siguiendo los criterios: las aprobadas ya se anotan; las noticias de descartadas pasan a
   Fuera de alcance o se quedan con sus otros objetos.
3. Ejecuta `.venv\Scripts\python.exe clasificacion\indice.py`.
4. Informa: aprobadas, descartadas, noticias reclasificadas y cómo quedan, y la línea final de `indice.py`.
