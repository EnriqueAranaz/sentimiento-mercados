-- Índice de sentimiento 1.1: ventana usada por cada fila (5 días de mercado; 20 en los alcances de sector) y días de
-- esa ventana con datos (para que el panel marque las ventanas incompletas: dias_con_datos < ventana_dias).
-- Ejecutar una vez en el SQL Editor del proyecto Supabase dedicado. Idempotente.

begin;

alter table public.indice_sentimiento add column if not exists ventana_dias smallint not null default 5;
alter table public.indice_sentimiento add column if not exists dias_con_datos integer;
alter table public.indice_divergencia add column if not exists dias_con_datos integer;

drop view if exists public.v_indice;
create view public.v_indice with (security_invoker = true) as
select i.dia_mercado,
       i.alcance,
       max(i.ventana_dias)                                        as ventana_dias,
       max(i.dias_con_datos)                                      as dias_con_datos,
       max(i.valor) filter (where i.linea = 'narrativa')          as indice_narrativa,
       max(i.valor) filter (where i.linea = 'hechos')             as indice_hechos,
       max(i.valor) filter (where i.linea = 'total')              as indice_total,
       max(d.valor)                                               as divergencia,  -- null si no se publica o no se calcula
       max(i.n_afectaciones) filter (where i.linea = 'narrativa') as n_narrativa,
       max(i.n_afectaciones) filter (where i.linea = 'hechos')    as n_hechos,
       max(i.n_afectaciones) filter (where i.linea = 'total')     as n_total,
       max(d.n_unidades_divergencia)                              as n_unidades_divergencia
from public.indice_sentimiento i
left join public.indice_divergencia d
       on d.dia_mercado = i.dia_mercado and d.alcance = i.alcance and d.version_indice = i.version_indice
where i.version_indice = '1.1'
group by i.dia_mercado, i.alcance;

grant select on public.v_indice to anon;

commit;
