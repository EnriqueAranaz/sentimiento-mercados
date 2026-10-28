# Índice de sentimiento v1

**Versión del índice: `1.0`** (columna `version_indice`). Lo calcula `clasificacion/indice.py` a partir de las
noticias ya clasificadas; no clasifica nada. Escala de 0 a 100, donde 50 es neutro. Por ahora **no hay bandas con
nombre** ("miedo", "euforia"…): se calibrarán con 2-3 meses de datos.

## Datos y fechas

- **Fuente:** `v_afectaciones`, que solo trae noticias relevantes (las no relevantes no tienen afectaciones).
- **dia:** día de publicación en hora de Madrid, igual que en las vistas actuales.
- **dia_mercado:** el sábado y el domingo cuentan para el lunes siguiente. Los festivos se ignoran: todos los días de
  lunes a viernes son días de mercado.
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

Son **5 días de mercado**, terminando en el día calculado. Se juntan todas las afectaciones de la ventana y no se hace
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

## Almacenamiento

- **Tabla `indice_sentimiento`:** una fila por dia_mercado × alcance × línea × version_indice. Columnas: valor, c1–c4
  (null si se omitió), componentes_usados, n_afectaciones, n_unidades, publicado, motivo_no_publicado y
  versiones_criterios (las versiones de criterios presentes en la ventana).
- **Vista `v_indice`:** una fila por dia_mercado × alcance, con indice_narrativa, indice_hechos, indice_total,
  divergencia y n de cada línea. La divergencia es narrativa − hechos y solo se rellena si las dos están publicadas.
- **Recálculo:** `indice.py` recalcula todo el histórico en cada ejecución. Borra e inserta las filas de su
  `version_indice`, así que una reclasificación nunca deja datos viejos.

## Uso

```
python clasificacion/indice.py              # recalcula y guarda
python clasificacion/indice.py --sin-guardar   # recalcula y muestra, sin escribir en Supabase
```

Se ejecuta como último paso de `/clasificar`.
