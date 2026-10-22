-- Fase 1, ampliación: tickers de TradingView y evolución de la actividad de los hilos de Rankia.
-- Ejecutar una vez en el SQL Editor, después de 001_schema.sql.

-- Tickers relacionados (p. ej. {NASDAQ:AAPL,BME:SAN}). Solo los rellena TradingView; nulo en el resto.
alter table public.articulos add column if not exists simbolos text[];

-- articulos.n_respuestas conserva el valor de la primera captura.
-- La evolución se registra aquí: una fila por hilo visto en cada ejecución, aunque ya existiera.
create table if not exists public.rankia_actividad (
    id            bigint generated always as identity primary key,
    articulo_id   bigint not null references public.articulos (id),
    ejecucion_id  bigint not null references public.ejecuciones (id),
    n_respuestas  integer,
    capturado_en  timestamptz not null default now()
);

create index if not exists rankia_actividad_articulo_capturado_idx
    on public.rankia_actividad (articulo_id, capturado_en);

-- Igual que el resto: RLS sin políticas, solo accesible con la secret/service role key.
alter table public.rankia_actividad enable row level security;
