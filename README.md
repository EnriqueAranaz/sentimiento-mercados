# Panel de sentimiento de mercados — Fase 1: ingesta

Captura dos veces al día (9:30 y 18:00, hora de Madrid) los **titulares** de medios y portales
financieros en español y los guarda en Supabase. No hay análisis de sentimiento todavía
(eso es la fase 2) y **nunca se guarda el cuerpo de los artículos**.

## Estructura

```
config/sources.yaml          fuentes y listados (fuente de verdad, se sincroniza con la tabla `fuentes`)
sql/001_schema.sql           tablas fuentes / articulos / ejecuciones, índices y RLS
sql/002_ampliacion.sql       articulos.simbolos (tickers de TradingView)
ingesta/
  __main__.py                orquestador y CLI (python -m ingesta)
  http.py                    cliente educado: User-Agent, timeout, 1 pet/s por dominio, robots.txt, detección de bloqueos
  robots.py                  intérprete de robots.txt con comodines (* y $)
  parsers.py                 rss, sitemap_news, html_enlaces, tradingview_json y fecha real de la página del artículo
  almacen.py                 Supabase o JSON local (--dry-run)
  modelos.py                 Item, fechas (Europe/Madrid -> UTC), normalización de URLs
.github/workflows/ingesta.yml  programación en GitHub Actions
tests/                       tests de robots.txt y fechas
exportar_snapshot.py         exporta todas las tablas de Supabase a un Excel (exports/, no se sube a GitHub)
```

## Puesta en marcha

1. Crear un proyecto Supabase dedicado y ejecutar en el SQL Editor, en orden, `sql/001_schema.sql` y
   `sql/002_ampliacion.sql`.
2. Local:
   ```bash
   python -m venv .venv
   .venv/Scripts/pip install -r requirements.txt     # Windows (Linux/Mac: .venv/bin/pip)
   cp .env.example .env                              # y rellenar SUPABASE_URL y SUPABASE_SERVICE_ROLE_KEY
   .venv/Scripts/python -m ingesta                   # ejecución manual contra Supabase
   ```
3. GitHub: en *Settings → Secrets and variables → Actions* crear `SUPABASE_URL` y
   `SUPABASE_SERVICE_ROLE_KEY`. También se puede lanzar a mano desde *Actions → Ingesta de titulares →
   Run workflow*, eligiendo la franja (`manual` por defecto; `apertura`/`cierre` para recuperar una
   ejecución perdida).

### Programación (cron-job.org)

El workflow **no** usa el programador de GitHub (`schedule`): en las pruebas lanzó en hora de Chile
pese a `timezone: Europe/Madrid` y otras veces no lanzó nada. Lo dispara **cron-job.org** (gratuito),
con dos tareas en zona horaria `Europe/Madrid`:

| Tarea | Hora | Cuerpo |
|---|---|---|
| Ingesta apertura | 09:30 | `{"ref":"main","inputs":{"franja":"apertura"}}` |
| Ingesta cierre | 18:00 | `{"ref":"main","inputs":{"franja":"cierre"}}` |

Ambas hacen `POST https://api.github.com/repos/EnriqueAranaz/sentimiento-mercados/actions/workflows/ingesta.yml/dispatches`
con los encabezados `Authorization: Bearer <token>`, `Accept: application/vnd.github+json`,
`X-GitHub-Api-Version: 2022-11-28` y `Content-Type: application/json`. GitHub responde `204` si la acepta.

- **Token**: *fine-grained* de GitHub, solo para este repositorio y con el único permiso **Actions: Read and write**.
  Caduca (máx. 1 año): al caducar, GitHub responde `401` y cron-job.org avisa por email. Se renueva en
  GitHub y se cambia el encabezado `Authorization` de las dos tareas.
- **Versión de la API**: `2022-11-28` tiene fin de soporte el 10/03/2028; antes de esa fecha, cambiar el
  encabezado a la versión vigente (p. ej. `2026-03-10`) y probar.
- **Si una ejecución no llega**: lanzarla a mano desde GitHub con su franja.

### Opciones de la CLI

| Opción | Uso |
|---|---|
| `--franja apertura\|cierre\|manual` | Etiqueta de la ejecución (por defecto `manual`) |
| `--solo expansion bolsamania` | Procesa solo esas fuentes (por `clave`) |
| `--dry-run` | No toca Supabase: guarda en `data/dry_run.json` (útil para probar una fuente nueva). Con `--solo`, prueba la fuente aunque tenga `activa: false` |
| `--muestras N` | Nº de titulares de ejemplo por fuente en el resumen (5 por defecto) |

## Exportar una foto de la base de datos a Excel

```bash
.venv/Scripts/pip install -r requirements-export.txt   # solo la primera vez (añade openpyxl)
.venv/Scripts/python exportar_snapshot.py
```

Genera `exports/snapshot_AAAA-MM-DD_HHMM.xlsx` (hora de Madrid) con:

- **resumen**: filas por tabla, artículos por fuente y día (día de publicación en hora de Madrid) y las últimas 10 ejecuciones.
- **una hoja por tabla** del esquema `public` (`articulos`, `ejecuciones`, `fuentes`...). Las tablas se
  descubren solas: si se añade una tabla nueva, aparece sin tocar el script.

Las fechas salen en hora de Madrid como fechas de Excel (`dd/mm/aaaa hh:mm:ss`), y los tickers (`simbolos`) separados por comas.
Usa las credenciales de `.env`. La carpeta `exports/` está en `.gitignore`: los Excel no se suben a GitHub.

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
   - `html_enlaces` — listado HTML genérico; requiere `selector` (CSS) y `patron_url` (regex de URL de artículo).
     Si `patron_url` tiene un grupo `(?P<seccion>...)`, la sección se toma de la URL de cada artículo.
     No da fecha: con `fecha_desde_articulo: true` en la fuente se abre la página de cada artículo nuevo
     (1 pet/s) y se toma la fecha real (`article:published_time` o JSON-LD `datePublished`); si no se
     consigue, se guarda la hora de captura con `fecha_estimada=true`.
   - `tradingview_json` — específico.

   Para excluir contenido (p. ej. promoción de un servicio de pago), `excluir_titulo` en la fuente: regex
   sobre el titular; los que casan no se guardan.

   Paginación (solo HTML): añadir `url_pagina: https://.../listado?page={n}`. Si la web tiene archivo
   por días, usar `url_dia` / `url_dia_pagina` con `{fecha}` y `{n}` (ver Bolsamanía): se recorre desde hoy
   hasta el día de la ejecución anterior. En ambos casos se para al encontrar una URL ya guardada;
   máximo `max_paginas` (10 por defecto, configurable por listado).
   Si un listado no es la vía principal de la fuente (una sola página complementaria), poner
   `detecta_hueco: false` para que no marque la ejecución como `parcial`.
3. **Probar sin base de datos**: `python -m ingesta --dry-run --solo mimedio` (dos veces: la segunda debe dar `nuevos=0` y `frontera=True`).
4. Hacer commit. La siguiente ejecución crea/actualiza la fila en `fuentes` automáticamente.

## Cómo desactivar una fuente

Poner `activa: false` (y un `motivo`) en `config/sources.yaml` y hacer commit. En la siguiente ejecución
la fila de `fuentes` se actualiza a `activa=false` y la fuente deja de leerse. Sus artículos ya guardados
se conservan. No se borra nada de la base de datos.

## Estados de una ejecución (`ejecuciones.estado`)

- `ok` — se encontró terreno ya capturado (URL conocida o fecha anterior a la última ejecución), o se
  recorrió un archivo por días completo hasta el día de la ejecución anterior, o el listado indica que no
  hay novedades (sitemap con `<no_news>`).
- `parcial` — se llegó al máximo de páginas (o al final de un RSS) sin tocar terreno conocido → **puede haber
  un hueco**; o falló alguno de los listados de la fuente. El detalle va en `error_msg`.
  Un día sin publicaciones (fin de semana) **no** es un hueco.
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

## Fuentes actuales (octubre 2026)

| Fuente | Estado | Acceso | Notas |
|---|---|---|---|
| Expansión | activa | RSS `e00-expansion.uecdn.es/rss/` `mercados.xml` y `empresas.xml` | ~50 + ~50 entradas. Titular + entradilla pública. `seccion`: mercados / empresas |
| Cinco Días | activa | RSS `feeds.elpais.com` (mercados-financieros y companias) | El HTML da 403 a bots; los feeds oficiales sí responden. ~28 + ~30 entradas. `seccion`: mercados-financieros / empresas |
| Bolsamanía | activa | HTML: archivo diario + sitemap de noticias + listados de sección | Principal: `/noticias/ultimas/AAAA-MM-DD/N` (completo, ~35-40 noticias por día laborable). Agrupa por día de creación: las programadas para días posteriores llegan por el sitemap y los listados. Fecha real desde el JSON-LD del artículo |
| CapitalBolsa | activa | HTML: archivo diario de Minuto a minuto + listados de sección + sitemap | Sección de Bolsamanía (mismo dominio, comparte 1 pet/s). ~36 noticias/día; sección tomada de la URL; fecha real del JSON-LD; excluida la promoción de CB Premium (sección `destacadas` y titulares que la anuncian) |
| TradingView | activa | HTML (JSON incrustado) | ~110 noticias por lectura (~1 día); sin paginación porque "cargar más" requiere JS |
| El Economista | **inactiva** | — | Akamai: 403 en todo (incluido robots.txt y RSS) |
| Investing.com | **inactiva** | — | Cloudflare: 403 en HTML y robots.txt; el RSS solo trae 10 entradas (~40 min) |
