-- Fase 2: clasificación de titulares (reglas mecánicas + clasificación manual por agente).
-- Solo crea objetos nuevos; no modifica ni borra nada existente.
-- Los valores de los catálogos son EXACTAMENTE los de referencia/clasificacion_titulares_2026-10-26_v3.xlsx.

begin;

-- ------------------------------------------------------------------ catálogos
create table if not exists public.sectores (
    nombre  text primary key,
    orden   smallint not null
);
insert into public.sectores (nombre, orden) values
    ('Banca', 1), ('Seguros y servicios financieros', 2), ('Petróleo y gas', 3),
    ('Eléctricas, renovables y redes', 4), ('Tecnología', 5), ('Semiconductores', 6),
    ('Telecomunicaciones', 7), ('Inmobiliario', 8), ('Construcción e infraestructuras', 9),
    ('Automóvil', 10), ('Transporte y turismo', 11), ('Consumo y distribución', 12),
    ('Lujo, moda y cosmética', 13), ('Salud y farmacia', 14), ('Industria, defensa y aeroespacial', 15),
    ('Materiales, química y minería', 16), ('Medios y entretenimiento', 17)
on conflict (nombre) do nothing;

create table if not exists public.temas (
    nombre  text primary key,
    orden   smallint not null
);
insert into public.temas (nombre, orden) values
    ('Resultados', 1), ('Recomendación / análisis', 2), ('Macro', 3), ('Materias primas', 4),
    ('Fusiones y OPAs', 5), ('Regulación y sanciones', 6), ('Geopolítica', 7), ('Mercado', 8),
    ('Corporativo', 9), ('Deuda y bonos', 10)
on conflict (nombre) do nothing;

create table if not exists public.origenes (
    nombre  text primary key,
    orden   smallint not null
);
insert into public.origenes (nombre, orden) values
    ('Hecho (empresa o dato oficial)', 1), ('Analista', 2), ('Rumor / según fuentes', 3),
    ('Opinión / prensa', 4), ('Mercado', 5)
on conflict (nombre) do nothing;

create table if not exists public.motivos_no_relevancia (
    nombre  text primary key,
    orden   smallint not null
);
insert into public.motivos_no_relevancia (nombre, orden) values
    ('Cripto', 1), ('Finanzas personales', 2), ('Divulgativo / genérico', 3), ('Sin objeto identificable', 4),
    ('Fuera de alcance (Latam, India…)', 5), ('Política sin efecto de mercado', 6), ('Agenda / convocatoria', 7),
    ('Empresa no cotizada', 8), ('Otros', 9)
on conflict (nombre) do nothing;

-- ------------------------------------------------------------------ empresas
create table if not exists public.empresas (
    id           bigint generated always as identity primary key,
    nombre       text not null unique,
    alias        text[] not null default '{}',
    ticker       text unique,                       -- formato TradingView (BME:SAN); nulo si no cotiza o no se conoce
    sector       text not null references public.sectores (nombre),
    mercado      text not null check (mercado in ('Ibex 35', 'DAX', 'Europa', 'EE. UU.', 'Otros')),
    en_universo  boolean not null default false,
    creado_en    timestamptz not null default now()
);

-- ------------------------------------------------------------------ detecciones (pistas de las reglas)
create table if not exists public.detecciones (
    id           bigint generated always as identity primary key,
    articulo_id  bigint not null references public.articulos (id) on delete cascade,
    tipo         text not null check (tipo in ('empresa', 'mercado', 'global')),
    empresa_id   bigint references public.empresas (id),
    objeto       text not null,
    metodo       text not null check (metodo in ('alias', 'simbolo', 'palabra')),
    creado_en    timestamptz not null default now(),
    unique (articulo_id, tipo, objeto),
    check ((tipo = 'empresa') = (empresa_id is not null))
);
create index if not exists detecciones_articulo_idx on public.detecciones (articulo_id);

-- ------------------------------------------------------------------ clasificación (una por noticia)
create table if not exists public.clasificacion (
    articulo_id          bigint primary key references public.articulos (id) on delete cascade,
    relevante            boolean not null,
    motivo_no_relevante  text references public.motivos_no_relevancia (nombre),
    tema                 text references public.temas (nombre),
    origen               text references public.origenes (nombre),
    metodo               text not null check (metodo in ('reglas', 'manual')),
    version_criterios    text not null,
    clasificado_en       timestamptz not null default now(),
    -- relevante: tema y origen, sin motivo · no relevante: motivo, sin tema ni origen
    check (
        (relevante and motivo_no_relevante is null and tema is not null and origen is not null)
        or (not relevante and motivo_no_relevante is not null and tema is null and origen is null)
    )
);

-- ------------------------------------------------------------------ afectaciones (una por objeto afectado)
create table if not exists public.afectaciones (
    id                 bigint generated always as identity primary key,
    articulo_id        bigint not null references public.clasificacion (articulo_id) on delete cascade,
    ambito             text not null check (ambito in ('Global', 'Mercado', 'Sector', 'Empresa')),
    objeto             text not null,
    sector             text references public.sectores (nombre),
    empresa_id         bigint references public.empresas (id),
    valor              smallint not null check (valor between -2 and 2),
    metodo             text not null check (metodo in ('reglas', 'manual')),
    version_criterios  text not null,
    check ((ambito in ('Global', 'Mercado')) = (sector is null)),
    check (ambito <> 'Sector' or objeto = sector),
    check (ambito <> 'Global' or objeto in ('Mercados', 'Economía', 'Petróleo', 'Materias primas', 'Divisas')),
    check (ambito = 'Empresa' or empresa_id is null)
);
create index if not exists afectaciones_articulo_idx on public.afectaciones (articulo_id);
create index if not exists afectaciones_ambito_objeto_idx on public.afectaciones (ambito, objeto);

-- ------------------------------------------------------------------ vistas (equivalentes a las hojas del Excel)
-- Base: una fila por afectación con día de publicación (Madrid), origen/tema de la noticia y universo de la empresa.
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
       a.version_criterios
from public.afectaciones a
join public.clasificacion c on c.articulo_id = a.articulo_id
join public.articulos ar    on ar.id = a.articulo_id
join public.fuentes f       on f.id = ar.fuente_id
left join public.empresas e on e.id = a.empresa_id;

-- resumen_diario: por día, ámbito y objeto (empresas: solo las del universo)
create or replace view public.resumen_diario with (security_invoker = true) as
select dia, ambito, objeto,
       count(*)                                         as n_afectaciones,
       round(avg(valor), 3)                             as impacto_medio,
       round(avg((valor < 0)::int), 3)                  as pct_negativas
from public.v_afectaciones
where ambito <> 'Empresa' or en_universo
group by dia, ambito, objeto;

-- resumen_total: por ámbito y objeto, todo el periodo (empresas: solo las del universo)
create or replace view public.resumen_total with (security_invoker = true) as
select ambito, objeto,
       count(*)                                         as n_afectaciones,
       round(avg(valor), 3)                             as impacto_medio,
       round(avg((valor < 0)::int), 3)                  as pct_negativas,
       round(avg((valor > 0)::int), 3)                  as pct_positivas
from public.v_afectaciones
where ambito <> 'Empresa' or en_universo
group by ambito, objeto;

-- resumen_sectores: noticias del sector en conjunto + noticias de empresas del universo de ese sector
create or replace view public.resumen_sectores with (security_invoker = true) as
with x as (
    select sector, ambito, valor from public.v_afectaciones
    where ambito = 'Sector' or (ambito = 'Empresa' and en_universo)
)
select s.nombre                                                         as sector,
       count(x.*) filter (where x.ambito = 'Sector')                    as n_noticias_sector,
       round(avg(x.valor) filter (where x.ambito = 'Sector'), 3)        as impacto_medio_sector,
       count(x.*) filter (where x.ambito = 'Empresa')                   as n_noticias_empresas,
       round(avg(x.valor) filter (where x.ambito = 'Empresa'), 3)       as impacto_medio_empresas,
       count(x.*)                                                       as n_total,
       round(avg(x.valor), 3)                                           as impacto_medio_total,
       round(avg((x.valor < 0)::int), 3)                                as pct_negativas_total
from public.sectores s
left join x on x.sector = s.nombre
group by s.nombre, s.orden
order by s.orden;

-- resumen_origen: tono por origen (todas las afectaciones) y columna Banca (sector + bancos del universo)
create or replace view public.resumen_origen with (security_invoker = true) as
with banca as (
    select * from public.v_afectaciones
    where sector = 'Banca' and (ambito = 'Sector' or (ambito = 'Empresa' and en_universo))
)
select o.nombre                                                        as origen,
       (select count(*) from public.v_afectaciones v where v.origen = o.nombre)                       as n_afectaciones,
       (select round(avg(valor), 3) from public.v_afectaciones v where v.origen = o.nombre)           as impacto_medio,
       (select round(avg((valor < 0)::int), 3) from public.v_afectaciones v where v.origen = o.nombre) as pct_negativas,
       (select count(*) from banca b where b.origen = o.nombre)                                       as n_banca,
       (select round(avg(valor), 3) from banca b where b.origen = o.nombre)                           as impacto_medio_banca,
       (select round(avg((valor < 0)::int), 3) from banca b where b.origen = o.nombre)                as pct_negativas_banca
from public.origenes o
order by o.orden;

-- ------------------------------------------------------------------ RLS en todo (sin políticas: solo service role)
alter table public.sectores               enable row level security;
alter table public.temas                  enable row level security;
alter table public.origenes               enable row level security;
alter table public.motivos_no_relevancia  enable row level security;
alter table public.empresas               enable row level security;
alter table public.detecciones            enable row level security;
alter table public.clasificacion          enable row level security;
alter table public.afectaciones           enable row level security;

commit;
