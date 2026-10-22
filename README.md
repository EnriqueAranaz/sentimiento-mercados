# Panel de sentimiento de mercados — Fase 1: ingesta

Captura dos veces al día (9:30 y 18:00, hora de Madrid) los **titulares** de medios, portales y
comunidad financiera en español y los guarda en Supabase. No hay análisis de sentimiento todavía
(eso es la fase 2) y **nunca se guarda el cuerpo de los artículos**.

## Estructura

```
config/sources.yaml          fuentes y listados (fuente de verdad, se sincroniza con la tabla `fuentes`)
sql/001_schema.sql           tablas fuentes / articulos / ejecuciones, índices y RLS
sql/002_ampliacion.sql       articulos.simbolos (tickers de TradingView) y tabla rankia_actividad
ingesta/
  __main__.py                orquestador y CLI (python -m ingesta)
  http.py                    cliente educado: User-Agent, timeout, 1 pet/s por dominio, robots.txt, detección de bloqueos
  robots.py                  intérprete de robots.txt con comodines (* y $)
  parsers.py                 rss, sitemap_news, html_enlaces, tradingview_json, rankia_foro
  almacen.py                 Supabase o JSON local (--dry-run)
  modelos.py                 Item, fechas (Europe/Madrid -> UTC), normalización de URLs
.github/workflows/ingesta.yml  programación en GitHub Actions
tests/                       tests de robots.txt y fechas
```

## Puesta en marcha

1. Crear un proyecto Supabase dedicado y ejecutar en el SQL Editor, en orden, `sql/001_schema.sql` y `sql/002_ampliacion.sql`.
2. Local:
   ```bash
   python -m venv .venv
   .venv/Scripts/pip install -r requirements.txt     # Windows (Linux/Mac: .venv/bin/pip)
   cp .env.example .env                              # y rellenar SUPABASE_URL y SUPABASE_SERVICE_ROLE_KEY
   .venv/Scripts/python -m ingesta                   # ejecución manual contra Supabase
   ```
3. GitHub: en *Settings → Secrets and variables → Actions* crear `SUPABASE_URL` y
   `SUPABASE_SERVICE_ROLE_KEY`. El workflow se lanza solo a las 9:30 (`apertura`) y 18:00
   (`cierre`) hora de Madrid, y a mano desde *Actions → Ingesta de titulares → Run workflow* (`manual`).

### Opciones de la CLI

| Opción | Uso |
|---|---|
| `--franja apertura\|cierre\|manual` | Etiqueta de la ejecución (por defecto `manual`) |
| `--solo expansion rankia` | Procesa solo esas fuentes (por `clave`) |
| `--dry-run` | No toca Supabase: guarda en `data/dry_run.json` (útil para probar una fuente nueva) |
| `--muestras N` | Nº de titulares de ejemplo por fuente en el resumen (5 por defecto) |

## Cómo añadir una fuente

1. **Comprobar viabilidad**: leer `https://dominio/robots.txt`; buscar RSS propio (`<link rel="alternate" type="application/rss+xml">`
   en el HTML, o `/rss`, `/feed`), o un sitemap de noticias. Si la web devuelve 403/429, muestra
   Cloudflare/captcha o necesita JavaScript para pintar las noticias, **no se añade** (o se añade con `activa: false`
   y el `motivo`). Nada de navegadores headless ni de saltarse protecciones.
2. **Añadir el bloque** en `config/sources.yaml`:
   ```yaml
   - nombre: Mi Medio            # único; es la clave de la tabla `fuentes`
     clave: mimedio              # para --solo
     tipo_fuente: medio          # medio | portal | comunidad
     tipo_acceso: rss            # rss | html
     url: https://mimedio.es/mercados/
     idioma: es
     activa: true
     motivo: "RSS oficial, ~40 entradas"
     listados:
       - url: https://mimedio.es/rss/mercados.xml
         parser: rss
         seccion: mercados
   ```
   Parsers disponibles:
   - `rss` — cualquier RSS/Atom (titular, fecha y entradilla).
   - `sitemap_news` — sitemap de Google News (`<news:title>`, `<news:publication_date>`).
   - `html_enlaces` — listado HTML genérico; requiere `selector` (CSS) y `patron_url` (regex de URL de artículo). No da fecha → `fecha_estimada=true`.
   - `tradingview_json`, `rankia_foro` — específicos.

   Paginación (solo HTML): añadir `url_pagina: https://.../listado?page={n}`. Se recorren páginas hasta
   encontrar una URL ya guardada (`corte: url`, por defecto) o, en listados ordenados por actividad
   como los foros, hasta pasar la fecha de la ejecución anterior (`corte: fecha`); máximo `max_paginas` (10).
   Si un listado no es la vía principal de la fuente (una sola página complementaria), poner
   `detecta_hueco: false` para que no marque la ejecución como `parcial`.
3. **Probar sin base de datos**: `python -m ingesta --dry-run --solo mimedio` (dos veces: la segunda debe dar `nuevos=0` y `frontera=True`).
4. Hacer commit. La siguiente ejecución crea/actualiza la fila en `fuentes` automáticamente.

## Cómo desactivar una fuente

Poner `activa: false` (y un `motivo`) en `config/sources.yaml` y hacer commit. En la siguiente ejecución
la fila de `fuentes` se actualiza a `activa=false` y la fuente deja de leerse. Sus artículos ya guardados
se conservan. No se borra nada de la base de datos.

## Estados de una ejecución (`ejecuciones.estado`)

- `ok` — se encontró terreno ya capturado (URL conocida o fecha anterior a la última ejecución).
- `parcial` — se llegó al máximo de páginas (o al final de un RSS) sin tocar terreno conocido → **puede haber
  un hueco**; o falló alguno de los listados de la fuente. El detalle va en `error_msg`.
- `error` — fallaron todos los listados (bloqueo, robots.txt, cambio de HTML, red...) o no se pudo guardar.

La primera ejecución de cada fuente no tiene referencia previa: queda `ok` con un aviso en `error_msg`.

## Códigos de salida y alerta

Se procesan siempre todas las fuentes; el código de salida se decide al final:

- `0` — normal (aunque alguna fuente haya quedado `parcial` o `error` puntualmente).
- `1` — todas las fuentes activas han terminado en `error` en esta ejecución.
- `2` — **alerta**: alguna fuente acumula 3 ejecuciones seguidas (incluida la actual) con estado `error`.
  Se registra en el log como `ALERTA · ...` y el workflow de GitHub aparece en rojo (GitHub avisa por email).
  La fuente **no** se desactiva: hay que revisarla y, si procede, poner `activa: false` a mano.

## Datos adicionales

- `articulos.simbolos` (`text[]`): tickers que TradingView asocia a la noticia (p. ej. `{NASDAQ:AAPL}`). Nulo en el resto de fuentes.
- `rankia_actividad`: en cada ejecución, una fila por cada hilo del foro visto (`articulo_id`, `ejecucion_id`, `n_respuestas`,
  `capturado_en`), aunque el hilo ya existiera. `articulos.n_respuestas` conserva el valor de la primera captura; la evolución
  está aquí. Rankia abrevia las cifras grandes ("3,93K"), así que en hilos muy largos el valor es aproximado.

## Fuentes actuales (octubre 2026)

| Fuente | Estado | Acceso | Notas |
|---|---|---|---|
| Expansión | activa | RSS `e00-expansion.uecdn.es/rss/` `mercados.xml` y `empresas.xml` | ~50 + ~50 entradas. Titular + entradilla pública. `seccion`: mercados / empresas |
| Cinco Días | activa | RSS `feeds.elpais.com` (mercados-financieros y companias) | El HTML da 403 a bots; los feeds oficiales sí responden. ~28 + ~30 entradas. `seccion`: mercados-financieros / empresas |
| Bolsamanía | activa | sitemap de noticias + HTML | RSS de solo 20 entradas (~5 h): se usa el sitemap (fecha exacta) + listados Últimas/Mercados/Empresas/Internacional (sin fecha) |
| TradingView | activa | HTML (JSON incrustado) | ~110 noticias por lectura (~1 día); sin paginación porque "cargar más" requiere JS |
| Rankia | activa | HTML (foro) + RSS (blogs) | Foro de Bolsa con corte por fecha. Solo título, URL, fecha de último mensaje y nº de respuestas |
| El Economista | **inactiva** | — | Akamai: 403 en todo (incluido robots.txt y RSS) |
| Investing.com | **inactiva** | — | Cloudflare: 403 en HTML y robots.txt; el RSS solo trae 10 entradas (~40 min) |
