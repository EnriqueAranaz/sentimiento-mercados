-- Lectura pública (solo SELECT) para el cuadro de mando, que usa la clave publishable (rol anon).
-- No da permiso de escritura: insertar, modificar y borrar sigue siendo solo de la service role / secret key.
-- Las vistas son security_invoker, así que necesitan estas políticas en las tablas que leen.

begin;

create policy "panel: lectura" on public.fuentes               for select to anon using (true);
create policy "panel: lectura" on public.articulos             for select to anon using (true);
create policy "panel: lectura" on public.clasificacion         for select to anon using (true);
create policy "panel: lectura" on public.afectaciones          for select to anon using (true);
create policy "panel: lectura" on public.empresas              for select to anon using (true);
create policy "panel: lectura" on public.sectores              for select to anon using (true);
create policy "panel: lectura" on public.temas                 for select to anon using (true);
create policy "panel: lectura" on public.origenes              for select to anon using (true);
create policy "panel: lectura" on public.motivos_no_relevancia for select to anon using (true);

grant select on public.v_afectaciones, public.resumen_diario, public.resumen_total,
                public.resumen_sectores, public.resumen_origen to anon;

commit;
