---
description: Clasifica los titulares pendientes con el agente clasificador-noticias y los carga en Supabase
argument-hint: "[particion k/n opcional]"
---

Lanza el subagente `clasificador-noticias` para clasificar los titulares pendientes siguiendo
`docs/criterios_clasificacion.md`, por lotes de 100, cargándolos con `clasificacion/cargar.py`.

Si se ha indicado una partición ($ARGUMENTS), pásasela al agente para que use `--particion` en `pendientes.py`.

Cuando el agente termine, recalcula el índice de sentimiento (último paso; ver `docs/indice_sentimiento.md`):
`.venv\Scripts\python.exe clasificacion\indice.py`

Y comprueba las empresas propuestas pendientes de decisión:
`.venv\Scripts\python.exe clasificacion\decidir_empresas.py --estado`

Y el tamaño de la base (plan gratuito: 500 MB):
`.venv\Scripts\python.exe clasificacion\tamano_bd.py`

Después muéstrame su informe: noticias clasificadas, pendientes que quedan, % de relevantes,
reparto por origen, empresas nuevas propuestas y dudas, la línea final de `indice.py` (filas y publicadas) y la
línea de `tamano_bd.py` (MB usados y %). Termina con un **aviso** visible con el número de empresas propuestas pendientes de decisión y de noticias afectadas (salida de `decidir_empresas.py --estado`), si hay alguna.
