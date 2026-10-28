# Índice de sentimiento v1

**Versión del índice: `1.1`** (columna `version_indice`). La 1.1 cambia tres cosas respecto a la 1.0: la divergencia, el inicio del histórico (22/10/2026) y la ventana de 20 días en los sectores. Lo calcula `clasificacion/indice.py` a partir de las
noticias ya clasificadas; no clasifica nada. Escala de 0 a 100, donde 50 es neutro. Por ahora **no hay bandas con
nombre** ("miedo", "euforia"…): se calibrarán con 2-3 meses de datos.

## Datos y fechas

- **Fuente:** `v_afectaciones`, que solo trae noticias relevantes (las no relevantes no tienen afectaciones).
- **dia:** día de publicación en hora de Madrid, igual que en las vistas actuales.
- **dia_mercado:** el sábado y el domingo cuentan para el lunes siguiente. Los festivos se ignoran: todos los días de
  lunes a viernes son días de mercado.
- **Inicio del histórico (`FECHA_INICIO` en `indice.py`): 22/10/2026**, el día en que empezó la ingesta automática.
  No se generan filas, ni del índice ni de la divergencia, con dia_mercado anterior. Tampoco se usan datos
  anteriores: una ventana que incluya días previos solo cuenta desde esa fecha, y la condición de cobertura también.
- **Exclusiones:**
  - Global · Petróleo, Global · Materias primas y Global · Divisas.
  - Las afectaciones de Empresa con `en_universo = false`.
  - Las de Sector entran todas.

## Líneas

No se pondera por origen: cada grupo de orígenes forma su propia línea.

| Línea | Orígenes |
|---|---|
| `narrativa` | Opinión / prensa · Rumor / según fuentes · Mercado |
| `hechos` | Hecho (empresa o dato oficial) · Analista |
| `total` | Todos (solo informativa) |

## Alcances

| Alcance | Mercado | Global | Empresas (del universo) | Sector |
|---|---|---|---|---|
| `general` | todos | Mercados, Economía | todas | todos |
| `espana` | Ibex 35, España | — | `mercado` = Ibex 35 | — |
| `europa` | Europa, DAX, Francia, Reino Unido, Italia, Portugal, Alemania, España, Ibex 35 | — | `mercado` = Europa, DAX o Ibex 35 | — |
| `eeuu` | EE. UU. | — | `mercado` = EE. UU. | — |
| `sector:<nombre>` (uno por cada uno de los 17 sectores) | — | — | las de ese sector | ese sector |

- `empresas.mercado` sale del ticker: BME → Ibex 35, XETR → DAX, el resto de bolsas europeas → Europa, NYSE/NASDAQ →
  EE. UU. y lo demás → Otros. Japón, Corea, Asia, Canadá y las empresas de "Otros" solo entran en `general`.
- Global · Mercados y Global · Economía entran solo en `general`.
- Las afectaciones de Sector entran en `general` y en su sector, nunca en los alcances geográficos.

## Ventana

Son **5 días de mercado** terminando en el día calculado, y **20 en los alcances de sector**, que tienen menos
noticias. Cada fila guarda la ventana usada en `ventana_dias`.

`dias_con_datos` es el número de días de mercado de la ventana, desde `FECHA_INICIO`, que tienen al menos una
afectación (de cualquier alcance, tras las exclusiones). Así el panel puede marcar las ventanas incompletas
(`dias_con_datos < ventana_dias`), como las primeras tras el 22/10. No cambia la publicación. Se guarda en
`indice_sentimiento` y en `indice_divergencia`, y sale en `v_indice` junto a `ventana_dias`. Se juntan todas las afectaciones de la ventana y no se hace
la media de las medias diarias.

## Componentes

Todos los componentes van de −1 a +1.

| | Componente | Peso | Cálculo |
|---|---|---|---|
| C1 | Mercado | 40 | Media de valor/2 de las afectaciones de Mercado y de Global (Mercados, Economía) del alcance. No aplica a los alcances de sector. |
| C2 | Empresas y sectores | 30 | Las unidades son cada empresa (por ticker) y cada sector. Se calcula la media de valor de cada unidad en la ventana, después la media simple entre unidades, y se divide entre 2. Cada empresa cuenta igual, tenga una noticia o diez. |
| C3 | Amplitud | 15 | (unidades con media > 0 − unidades con media < 0) / número de unidades. |
| C4 | Intensidad | 15 | (afectaciones con valor +2 − afectaciones con valor −2) / total de afectaciones del alcance y la línea. |

Si un componente tiene **menos de 5 datos**, se omite y su peso se reparte entre los demás, en proporción. Cuentan
como datos las afectaciones en C1 y C4, y las unidades en C2 y C3. Los componentes usados se guardan en
`componentes_usados`.

## Valor

```
indice = (Σ peso·C / Σ pesos usados + 1) × 50      redondeado a 1 decimal
```

El valor se publica solo si se cumplen las tres condiciones siguientes:
1. La ventana tiene al menos **20 afectaciones** en `general`, o **10** en el resto de alcances.
2. Todos los días de mercado de la ventana tienen **pct_clasificado ≥ 90 %**, según `v_cobertura`. Se suman todas las
   fuentes y, en el lunes, también el sábado y el domingo. Un día sin artículos no cumple.
3. Queda al menos un componente con datos suficientes.

Si no se cumple alguna, `publicado = false`, `valor = null` y `motivo_no_publicado` explica por qué. **Nunca se pone
50 por defecto.**

## Divergencia (desde 1.1)

La divergencia mide si la narrativa es más optimista o más pesimista que los hechos **sobre los mismos objetos**. En
la 1.0 era la resta de los índices de narrativa y hechos, pero cada índice habla de cosas distintas: los hechos son
sobre todo empresas con resultados y contratos, y la narrativa, sobre todo mercados. Esa resta medía más qué tipo de
noticia cae en cada línea que una diferencia de tono. La 1.1 compara cada objeto consigo mismo.

Se calcula solo para los alcances **general, espana, europa y eeuu**. Para los sectores no se calcula ni se guarda. Se
hace por alcance y ventana, con las mismas exclusiones que el índice:
1. **Unidad:** cada objeto. Puede ser una empresa (por ticker), un sector o un objeto de Mercado o de Global
   (Mercados, Economía). Solo entran los objetos del alcance.
2. Solo cuentan los objetos que tienen **al menos una afectación de narrativa y al menos una de hechos** en la ventana.
3. Para cada uno: `(media de valor en narrativa − media de valor en hechos) / 2`.
4. `divergencia = media simple de esas diferencias × 50`, en puntos de la misma escala que el índice. Negativa
   significa que la narrativa es más pesimista que los hechos sobre esos mismos objetos.
5. Se guarda `n_unidades_divergencia`. Con menos de **5** objetos comunes no se publica ("sin dato"). Tampoco se
   publica si la ventana no cumple la cobertura del 90 %.

Los índices de narrativa, hechos y total no cambian.

## Almacenamiento

- **Tabla `indice_sentimiento`:** una fila por dia_mercado × alcance × línea × version_indice. Columnas: ventana_dias, valor, c1–c4
  (null si se omitió), componentes_usados, n_afectaciones, n_unidades, publicado, motivo_no_publicado y
  versiones_criterios (las versiones de criterios presentes en la ventana).
- **Tabla `indice_divergencia`:** una fila por dia_mercado × alcance × version_indice, con valor,
  n_unidades_divergencia, publicado y motivo_no_publicado.
- **Vista `v_indice`:** versión 1.1, una fila por dia_mercado × alcance. Lleva ventana_dias, indice_narrativa, indice_hechos,
  indice_total, divergencia (de `indice_divergencia`), n de cada línea y n_unidades_divergencia.
- **Recálculo:** `indice.py` recalcula todo el histórico en cada ejecución. Borra e inserta las filas de su
  `version_indice` en las dos tablas, así que una reclasificación nunca deja datos viejos. Las filas de la 1.0 se
  quedan como estaban.

## Uso

```
python clasificacion/indice.py              # recalcula y guarda
python clasificacion/indice.py --sin-guardar   # recalcula y muestra, sin escribir en Supabase
```

Se ejecuta como último paso de `/clasificar`.
