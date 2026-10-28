-- dia_mercado en las vistas: sábado y domingo cuentan para el lunes siguiente (la misma regla que
-- clasificacion/indice.py: a_dia_mercado). Una sola definición en la función public.dia_mercado.
-- Ejecutar una vez en el SQL Editor del proyecto Supabase dedicado. Idempotente.

begin;

create or replace function public.dia_mercado(d date) returns date
language sql immutable as $$
    select case extract(isodow from d) when 6 then d + 2 when 7 then d + 1 else d end
$$;

-- Las vistas se redefinen igual que antes, con dia_mercado añadida al final.
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
left join public.empresas e on e.id = a.empresa_id;

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
where not c.relevante;

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
group by 1, 2;  -- dia_mercado sale de dia (columna 1), así que no hace falta agruparla

grant execute on function public.dia_mercado(date) to anon;
grant select on public.v_afectaciones, public.v_no_relevantes, public.v_cobertura to anon;

commit;
