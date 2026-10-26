-- Fase 1: esquema de ingesta de titulares.
-- Ejecutar una vez en el SQL Editor del proyecto Supabase dedicado.

create table if not exists public.fuentes (
    id            bigint generated always as identity primary key,
    nombre        text not null unique,
    tipo_acceso   text not null check (tipo_acceso in ('rss', 'html')),
    tipo_fuente   text not null check (tipo_fuente in ('medio', 'portal', 'comunidad')),
    url           text not null,
    idioma        text not null default 'es',
    activa        boolean not null default true,
    creado_en     timestamptz not null default now()
);

create table if not exists public.articulos (
    id              bigint generated always as identity primary key,
    fuente_id       bigint not null references public.fuentes (id),
    url             text not null unique,
    titulo          text not null,
    resumen         text,
    seccion         text,
    publicado_en    timestamptz not null,
    fecha_estimada  boolean not null default false,
    capturado_en    timestamptz not null default now()
);

create index if not exists articulos_publicado_en_idx on public.articulos (publicado_en);
create index if not exists articulos_fuente_id_idx    on public.articulos (fuente_id);

create table if not exists public.ejecuciones (
    id              bigint generated always as identity primary key,
    inicio          timestamptz not null,
    fin             timestamptz,
    franja          text not null check (franja in ('apertura', 'cierre', 'manual')),
    fuente_id       bigint references public.fuentes (id),
    estado          text not null check (estado in ('ok', 'error', 'parcial')),
    n_leidos        integer not null default 0,
    n_nuevos        integer not null default 0,
    paginas_leidas  integer not null default 0,
    error_msg       text
);

create index if not exists ejecuciones_fuente_inicio_idx on public.ejecuciones (fuente_id, inicio desc);

-- RLS activado y sin políticas: solo la service role key (que ignora RLS) puede leer/escribir.
-- La clave anon/publishable no tiene acceso a nada.
alter table public.fuentes     enable row level security;
alter table public.articulos   enable row level security;
alter table public.ejecuciones enable row level security;
