---
description: Clasifica los titulares pendientes con el agente clasificador-noticias y los carga en Supabase
argument-hint: "[particion k/n opcional]"
---

Lanza el subagente `clasificador-noticias` para clasificar los titulares pendientes siguiendo
`docs/criterios_clasificacion.md`, por lotes de 100, cargándolos con `clasificacion/cargar.py`.

Si se ha indicado una partición ($ARGUMENTS), pásasela al agente para que use `--particion` en `pendientes.py`.

Cuando el agente termine, recalcula el índice de sentimiento (último paso; ver `docs/indice_sentimiento.md`):
`.venv\Scripts\python.exe clasificacion\indice.py`

Después muéstrame su informe: noticias clasificadas, pendientes que quedan, % de relevantes,
reparto por origen, empresas nuevas propuestas y dudas, y la línea final de `indice.py` (filas y publicadas).
