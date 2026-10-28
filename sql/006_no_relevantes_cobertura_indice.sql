-- No relevantes, cobertura de la clasificación e índice de sentimiento v1 (docs/indice_sentimiento.md).
-- Ejecutar una vez en el SQL Editor del proyecto Supabase dedicado. Idempotente.

begin;

-- ------------------------------------------------------------------ no relevantes
-- Una fila por noticia no relevante, con el mismo día de publicación (Madrid) que v_afectaciones.
create or replace view public.v_no_relevantes with (security_invoker = true) as
select c.articulo_id,
       (ar.publicado_en at time zone 'Europe/Madrid')::date as dia,
       ar.publicado_en,
       f.nombre as fuente,
       ar.seccion,
       ar.titulo,
       c.motivo_no_relevante,
       c.metodo,
       c.version_criterios
from public.clasificacion c
join public.articulos ar on ar.id = c.articulo_id
join public.fuentes f    on f.id = ar.fuente_id
where not c.relevante;

-- ------------------------------------------------------------------ cobertura
-- Una fila por día de publicación (Madrid) y fuente: cuánto se ha clasificado.
create or replace view public.v_cobertura with (security_invoker = true) as
select (ar.publicado_en at time zone 'Europe/Madrid')::date as dia,
       f.nombre                                                   as fuente,
       count(*)                                                   as n_articulos,
       count(c.articulo_id)                                       as n_clasificados,
       count(*) - count(c.articulo_id)                            as n_pendientes,
       round(100.0 * count(c.articulo_id) / count(*), 1)          as pct_clasificado,
       count(*) filter (where c.relevante)                        as n_relevantes,
       count(*) filter (where not c.relevante)                    as n_no_relevantes
from public.articulos ar
join public.fuentes f            on f.id = ar.fuente_id
left join public.clasificacion c on c.articulo_id = ar.id
group by 1, 2;

-- ------------------------------------------------------------------ índice de sentimiento
create table if not exists public.indice_sentimiento (
    dia_mercado          date        not null,
    alcance              text        not null,   -- general, espana, europa, eeuu, sector:<nombre>
    linea                text        not null check (linea in ('narrativa', 'hechos', 'total')),
    valor                numeric(4, 1) check (valor between 0 and 100),
    c1                   numeric,                -- componentes en -1..1; null si se omitió
    c2                   numeric,
    c3                   numeric,
    c4                   numeric,
    componentes_usados   text[]      not null default '{}',
    n_afectaciones       integer     not null,
    n_unidades           integer     not null,
    publicado            boolean     not null,
    motivo_no_publicado  text,
    version_indice       text        not null,
    versiones_criterios  text,
    calculado_en         timestamptz not null default now(),
    primary key (dia_mercado, alcance, linea, version_indice),
    check (publicado = (valor is not null)),
    check (publicado or motivo_no_publicado is not null)
);
alter table public.indice_sentimiento enable row level security;
drop policy if exists "panel: lectura" on public.indice_sentimiento;
create policy "panel: lectura" on public.indice_sentimiento for select to anon using (true);

-- Una fila por día de mercado y alcance (versión 1.0), con las tres líneas lado a lado.
create or replace view public.v_indice with (security_invoker = true) as
select dia_mercado,
       alcance,
       max(valor) filter (where linea = 'narrativa')          as indice_narrativa,
       max(valor) filter (where linea = 'hechos')             as indice_hechos,
       max(valor) filter (where linea = 'total')              as indice_total,
       max(valor) filter (where linea = 'narrativa')
         - max(valor) filter (where linea = 'hechos')         as divergencia,  -- null si falta alguna
       max(n_afectaciones) filter (where linea = 'narrativa') as n_narrativa,
       max(n_afectaciones) filter (where linea = 'hechos')    as n_hechos,
       max(n_afectaciones) filter (where linea = 'total')     as n_total
from public.indice_sentimiento
where version_indice = '1.0'
group by dia_mercado, alcance;

grant select on public.v_no_relevantes, public.v_cobertura, public.v_indice, public.indice_sentimiento to anon;

commit;
