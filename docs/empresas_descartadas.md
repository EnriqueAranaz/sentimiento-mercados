# Empresas descartadas

Son cotizadas que el agente propuso y que se decidió **no dar de alta** en la tabla `empresas`. Las aplica el
agente clasificador según la sección 14 de `docs/criterios_clasificacion.md` (v3.9):

- Si la noticia solo trata de una empresa descartada, **no es relevante**, con motivo *Fuera de alcance (Latam, India…)*.
- Si la noticia tiene otros objetos, se anotan esos y la empresa descartada no.
- No se vuelven a proponer en `empresas_nuevas`.

`clasificacion/cargar.py` lee la primera columna de esta tabla. Si se añade una empresa, hay que mantener el formato.

| Empresa | Ticker | Motivo | Decisión |
|---|---|---|---|
| Pennon Group | LSE:PNN | Pequeña (menos de ~4.000 M) | 27/10/2026 |
| SES | EURONEXT:SESG | Pequeña (menos de ~4.000 M) | 27/10/2026 |
| Canal+ | LSE:CAN | Pequeña (menos de ~4.000 M) | 27/10/2026 |
| Implantica | OMXSTO:IMP_A_SDB | Microcotizada | 27/10/2026 |
| Tieto | OMXHEX:TIETO | Pequeña (menos de ~4.000 M) | 27/10/2026 |
| TechTarget | NASDAQ:TTGT | Microcotizada | 27/10/2026 |
| Ceconomy | XETR:CEC | Pequeña (menos de ~4.000 M) | 27/10/2026 |
| UniFirst | NYSE:UNF | Pequeña (menos de ~4.000 M) | 27/10/2026 |
| Woodlands Financial Services | OTC:WDFN | Banco regional de EE. UU. | 27/10/2026 |
| GomSpace | OMXSTO:GOMX | Microcotizada | 27/10/2026 |
| Artiva Biotherapeutics | NASDAQ:ARTV | Microcotizada | 27/10/2026 |
| Blueharbor Bank | OTC:BLHK | Banco regional de EE. UU. | 27/10/2026 |
| Auburn National Bancorporation | NASDAQ:AUBN | Banco regional de EE. UU. | 27/10/2026 |
| MidCap Financial Investment | NASDAQ:MFIC | Microcotizada | 27/10/2026 |
