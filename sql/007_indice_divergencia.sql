-- Índice de sentimiento 1.1: divergencia por objetos comunes a narrativa y hechos (docs/indice_sentimiento.md).
-- Ejecutar una vez en el SQL Editor del proyecto Supabase dedicado. Idempotente.

begin;

create table if not exists public.indice_divergencia (
    dia_mercado             date        not null,
    alcance                 text        not null,
    valor                   numeric(5, 1) check (valor between -100 and 100),  -- puntos de la escala del índice
    n_unidades_divergencia  integer     not null,
    publicado               boolean     not null,
    motivo_no_publicado     text,
    version_indice          text        not null,
    calculado_en            timestamptz not null default now(),
    primary key (dia_mercado, alcance, version_indice),
    check (publicado = (valor is not null)),
    check (publicado or motivo_no_publicado is not null)
);
alter table public.indice_divergencia enable row level security;
drop policy if exists "panel: lectura" on public.indice_divergencia;
create policy "panel: lectura" on public.indice_divergencia for select to anon using (true);

-- v_indice pasa a la versión 1.1 y toma la divergencia de indice_divergencia (ya no es la resta de índices).
drop view if exists public.v_indice;
create view public.v_indice with (security_invoker = true) as
select i.dia_mercado,
       i.alcance,
       max(i.valor) filter (where i.linea = 'narrativa')          as indice_narrativa,
       max(i.valor) filter (where i.linea = 'hechos')             as indice_hechos,
       max(i.valor) filter (where i.linea = 'total')              as indice_total,
       max(d.valor)                                               as divergencia,  -- null si no se publica
       max(i.n_afectaciones) filter (where i.linea = 'narrativa') as n_narrativa,
       max(i.n_afectaciones) filter (where i.linea = 'hechos')    as n_hechos,
       max(i.n_afectaciones) filter (where i.linea = 'total')     as n_total,
       max(d.n_unidades_divergencia)                              as n_unidades_divergencia
from public.indice_sentimiento i
left join public.indice_divergencia d
       on d.dia_mercado = i.dia_mercado and d.alcance = i.alcance and d.version_indice = i.version_indice
where i.version_indice = '1.1'
group by i.dia_mercado, i.alcance;

grant select on public.v_indice, public.indice_divergencia to anon;

commit;
