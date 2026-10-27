-- Criterios v3.5: dos motivos nuevos de no relevancia, detrás de "Otros" (orden 9).
-- Idempotente: se puede ejecutar más de una vez.
insert into public.motivos_no_relevancia (nombre, orden) values
    ('Precio sin causa', 10),
    ('Análisis técnico', 11)
on conflict (nombre) do nothing;
