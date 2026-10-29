-- Tamaño de la base de datos (límite del plan gratuito: 500 MB), para el informe de /clasificar.
-- Solo para la clave secreta (service_role); el panel no la usa.
-- Ejecutar una vez en el SQL Editor del proyecto Supabase dedicado. Idempotente.

begin;

create or replace function public.tamano_bd() returns jsonb
language sql stable as $$
    select jsonb_build_object(
        'total', pg_database_size(current_database()),
        'tablas', (select jsonb_object_agg(c.relname, pg_total_relation_size(c.oid))
                   from pg_class c join pg_namespace n on n.oid = c.relnamespace
                   where n.nspname = 'public' and c.relkind = 'r'))
$$;

revoke execute on function public.tamano_bd() from public, anon, authenticated;
grant execute on function public.tamano_bd() to service_role;

commit;
