-- Fase 1, ampliación: tickers de TradingView.
-- Ejecutar una vez en el SQL Editor, después de 001_schema.sql.

-- Tickers relacionados (p. ej. {NASDAQ:AAPL,BME:SAN}). Solo los rellena TradingView; nulo en el resto.
alter table public.articulos add column if not exists simbolos text[];
