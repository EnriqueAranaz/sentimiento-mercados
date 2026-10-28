-- Criterios v3.9 (aclaración): motivo para las noticias que solo tratan de una empresa propuesta y todavía no dada
-- de alta. Cuando se aprueba la empresa, la noticia se reclasifica; si se descarta, pasa a "Fuera de alcance".
-- Idempotente: se puede ejecutar más de una vez.
insert into public.motivos_no_relevancia (nombre, orden) values
    ('Empresa pendiente de alta', 12)
on conflict (nombre) do nothing;
