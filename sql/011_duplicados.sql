-- Artículos duplicados de la misma fuente: clave por fuente y marca duplicado_de (sin borrar nada).
--   clave_fuente  número del artículo en la URL (--NNN.html) en Bolsamanía y CapitalBolsa: la misma noticia llega
--                 por el archivo y por el sitemap con slugs distintos. UNIQUE (fuente_id, clave_fuente).
--   duplicado_de  id del artículo vivo cuando este es una copia (choque de clave al rellenar, o reenvío de Reuters
--                 en TradingView con el mismo titular en 48 h). Las vistas lo excluyen; la clasificación se conserva.
--   titulo_anterior  titular previo cuando la fuente reescribe el artículo (manda la última versión).
-- Ejecutar una vez en el SQL Editor del proyecto Supabase dedicado. Idempotente.

begin;

alter table public.articulos
    add column if not exists clave_fuente text,
    add column if not exists duplicado_de bigint references public.articulos (id),
    add column if not exists titulo_anterior text;   -- titular previo cuando la fuente reescribe el artículo

create index if not exists articulos_duplicado_de_idx on public.articulos (duplicado_de) where duplicado_de is not null;

-- Rellenar clave_fuente. Misma fuente + misma clave = una sola noticia; queda viva una fila, que se lleva la clave,
-- y las demás se marcan con duplicado_de = la viva:
--   - mismo titular normalizado (BBVA 23947612, Endesa 23936781): sigue viva la primera (menor id);
--   - titular reescrito (petróleo 23913103, Volvo 23913355, HSBC 23928202): manda la última versión (mayor id), que
--     guarda en titulo_anterior el titular de la antigua.
with c as (
    select ar.id, ar.fuente_id, ar.titulo, substring(ar.url from '--(\d+)\.html$') as clave,
           regexp_replace(regexp_replace(lower(btrim(ar.titulo)), '\s+', ' ', 'g'), '[\s.,;:!?…]+$', '') as titular
    from public.articulos ar
    join public.fuentes f on f.id = ar.fuente_id
    where f.nombre in ('Bolsamanía', 'CapitalBolsa')
), g as (
    select c.*,
           case when min(titular) over w = max(titular) over w then min(id) over w else max(id) over w end as vivo,
           count(*) over w as n
    from c
    where clave is not null
    window w as (partition by fuente_id, clave)
), anterior as (  -- titular de la versión antigua, para la viva cuando el titular cambió
    select g.vivo, (array_agg(g.titulo order by g.id desc))[1] as titulo
    from g
    where g.id <> g.vivo
      and g.titular <> (select g2.titular from g g2 where g2.id = g.vivo)
    group by g.vivo
)
update public.articulos a
set clave_fuente   = case when g.id = g.vivo then g.clave end,
    duplicado_de   = case when g.id <> g.vivo then g.vivo end,
    titulo_anterior = case when g.id = g.vivo then coalesce((select an.titulo from anterior an where an.vivo = g.id),
                                                           a.titulo_anterior) else a.titulo_anterior end
from g
where a.id = g.id;

create unique index if not exists articulos_fuente_clave_uk
    on public.articulos (fuente_id, clave_fuente) where clave_fuente is not null;

-- Reenvíos de Reuters en TradingView (mismo titular en menos de 48 h), diagnosticados el 29/10/2026.
-- (duplicado, primero)
update public.articulos a
set duplicado_de = v.primero
from (values (854, 226), (2463, 241), (3403, 853), (2563, 2058), (2906, 2058), (2558, 2067), (2894, 2459),
             (2885, 2555), (3399, 2942), (3406, 2974), (6355, 5837), (7190, 5837), (6828, 6258), (7192, 6262),
             (7191, 6724), (8594, 8115), (10038, 9014), (9519, 9043), (9574, 9101)) as v (id, primero)
where a.id = v.id;

-- Vistas: igual que en 009, sin los duplicados.
create or replace view public.v_afectaciones with (security_invoker = true) as
select a.id,
       a.articulo_id,
       (ar.publicado_en at time zone 'Europe/Madrid')::date as dia,
       ar.publicado_en,
       f.nombre                                   as fuente,
       ar.titulo,
       c.tema,
       a.ambito,
       a.objeto,
       a.sector,
       e.ticker,
       case when a.ambito = 'Empresa' then coalesce(e.en_universo, false) end as en_universo,
       a.valor,
       case a.valor when -2 then 'Muy negativo' when -1 then 'Negativo' when 0 then 'Neutral'
                    when 1 then 'Positivo' when 2 then 'Muy positivo' end as impacto,
       c.origen,
       a.metodo,
       a.version_criterios,
       public.dia_mercado((ar.publicado_en at time zone 'Europe/Madrid')::date) as dia_mercado
from public.afectaciones a
join public.clasificacion c on c.articulo_id = a.articulo_id
join public.articulos ar    on ar.id = a.articulo_id
join public.fuentes f       on f.id = ar.fuente_id
left join public.empresas e on e.id = a.empresa_id
where ar.duplicado_de is null;

create or replace view public.v_no_relevantes with (security_invoker = true) as
select c.articulo_id,
       (ar.publicado_en at time zone 'Europe/Madrid')::date as dia,
       ar.publicado_en,
       f.nombre as fuente,
       ar.seccion,
       ar.titulo,
       c.motivo_no_relevante,
       c.metodo,
       c.version_criterios,
       public.dia_mercado((ar.publicado_en at time zone 'Europe/Madrid')::date) as dia_mercado
from public.clasificacion c
join public.articulos ar on ar.id = c.articulo_id
join public.fuentes f    on f.id = ar.fuente_id
where not c.relevante
  and ar.duplicado_de is null;

-- Un duplicado no cuenta como artículo ni como pendiente.
create or replace view public.v_cobertura with (security_invoker = true) as
select (ar.publicado_en at time zone 'Europe/Madrid')::date as dia,
       f.nombre                                                   as fuente,
       count(*)                                                   as n_articulos,
       count(c.articulo_id)                                       as n_clasificados,
       count(*) - count(c.articulo_id)                            as n_pendientes,
       round(100.0 * count(c.articulo_id) / count(*), 1)          as pct_clasificado,
       count(*) filter (where c.relevante)                        as n_relevantes,
       count(*) filter (where not c.relevante)                    as n_no_relevantes,
       public.dia_mercado((ar.publicado_en at time zone 'Europe/Madrid')::date) as dia_mercado
from public.articulos ar
join public.fuentes f            on f.id = ar.fuente_id
left join public.clasificacion c on c.articulo_id = ar.id
where ar.duplicado_de is null
group by 1, 2;

grant select on public.v_afectaciones, public.v_no_relevantes, public.v_cobertura to anon;

commit;
