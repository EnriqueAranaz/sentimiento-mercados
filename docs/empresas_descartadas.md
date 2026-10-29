# Empresas descartadas

Son cotizadas que el agente propuso y que se decidió **no dar de alta** en la tabla `empresas`. Las aplica el
agente clasificador según la sección 14 de `docs/criterios_clasificacion.md` (v3.9):

- Si la noticia solo trata de una empresa descartada, **no es relevante**, con motivo *Fuera de alcance (Latam, India…)*.
- Si la noticia tiene otros objetos, se anotan esos y la empresa descartada no.
- No se vuelven a proponer en `empresas_nuevas`.

Criterios generales de alta y descarte:
- **Se dan de alta** las grandes y medianas de EE. UU. y Europa, y **todas las españolas del Mercado Continuo**,
  aunque sean pequeñas.
- **Se descartan** las microcotizadas y las pequeñas extranjeras, los bancos regionales de EE. UU., las españolas de
  **BME Growth** o **Euronext Growth** (mercados de crecimiento) y las que no cotizan.
- El criterio es el **tamaño**: se descartan los bancos regionales **pequeños** de EE. UU., no los bancos de EE. UU.
  medianos o grandes (U.S. Bancorp o PNC se dan de alta).

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
| Photocure | OSL:PHO | Pequeña extranjera | 28/10/2026 |
| Hunting | LSE:HTG | Pequeña extranjera | 28/10/2026 |
| Condis | — | No cotiza | 28/10/2026 |
| OPay | — | No cotiza | 28/10/2026 |
| Virtualware | EURONEXT:ALVIR | Cotiza en mercado de crecimiento | 28/10/2026 |
| Aktia Bank | OMXHEX:AKTIA | Pequeña extranjera | 28/10/2026 |
| Morguard | TSX:MRC | Pequeña extranjera | 28/10/2026 |
| Wendy's | NASDAQ:WEN | Pequeña extranjera | 28/10/2026 |
| Corticeira Amorim | EURONEXT:COR | Pequeña extranjera | 28/10/2026 |
| HomeTrust Bancshares | NYSE:HTB | Banco regional de EE. UU. | 28/10/2026 |
| Versant Media | NASDAQ:VSNT | Pequeña (menos de ~4.000 M) | 28/10/2026 |
