# Criterios de clasificación de titulares

**Versión de criterios: `v3.5`** (modelo del Excel `referencia/clasificacion_titulares_2026-10-26_v3.xlsx`, 26/10/2026,
más las aclaraciones de las secciones 9 a 12). Es el valor que va en `version_criterios`.
Este documento es la **única fuente de criterios** del agente clasificador. Las secciones 1 a 7 son copia íntegra
de la hoja *Criterios* del Excel; la sección 8 son ejemplos reales del Excel, clasificados a mano; las secciones 9 a 12
son aclaraciones posteriores, que **prevalecen** sobre lo anterior si hay conflicto (la más reciente sobre las demás).
**Principio de la v3.5 (sección 12): el precio narrado no es noticia.**
Los nombres de ámbitos, objetos de Global, sectores, temas, orígenes y motivos deben usarse **exactamente** como aparecen aquí.

## 1. Estructura

- Cada titular tiene una clasificación: si es **relevante** y, si lo es, su **tema** y su **origen**; si no lo es, su **motivo de no relevancia**.
- Cada titular relevante tiene **una o varias afectaciones**: una por cada cosa a la que afecta (ámbito + objeto + impacto). Un titular puede tener varias.

## 2. Ámbitos

| Ámbito | Qué es |
|---|---|
| **Global** | Lo que mueve a todos los mercados. Objetos: **Mercados** (bolsas en general), **Economía** (macro mundial), **Petróleo**, **Materias primas** (oro, metales, agrícolas), **Divisas**. |
| **Mercado** | Un índice o una región: **Ibex 35**, **DAX**, **Europa**, **EE. UU.**, y otros países o zonas (**Francia**, **Reino Unido**, **Japón**, **Asia**, **Corea**). La macro de un país va a su mercado (España → Ibex 35, Alemania → DAX). |
| **Sector** | Noticias de un sector en conjunto ("la banca", "las tecnológicas", "las energéticas"). Las noticias de una empresa concreta van a Empresa, pero cada empresa lleva su sector en la columna sector, para poder agregar. |
| **Empresa** | Una empresa cotizada concreta, con su ticker. en_universo = Sí si está en Ibex 35, DAX 40, Euro Stoxx 50 / Stoxx Europe 50, o entre las ~50 mayores de EE. UU. y del mundo. |

En Global y Mercado no hay sector. En Sector, el objeto es el propio sector. En Empresa, el sector es el de la empresa.

## 3. Sectores (17)

Banca · Seguros y servicios financieros · Petróleo y gas · Eléctricas, renovables y redes · Tecnología · Semiconductores · Telecomunicaciones · Inmobiliario · Construcción e infraestructuras · Automóvil · Transporte y turismo · Consumo y distribución · Lujo, moda y cosmética · Salud y farmacia · Industria, defensa y aeroespacial · Materiales, química y minería · Medios y entretenimiento

## 4. Impacto (tono del texto)

| Valor | Etiqueta | Cuándo |
|---|---|---|
| **-2** | Muy negativo | Lenguaje fuerte o hechos graves: desplome, hundimiento, "implosiona", caída ≥5% (≥2% en un índice), liquidación, quiebra, profit warning, multa histórica, beneficio −20% o peor. |
| **-1** | Negativo | Desfavorable normal: cae, baja, rebaja de recomendación, beneficio a la baja, dudas. |
| **0** | Neutral | Informativo o mixto: dividendo ordinario, nombramientos, acuerdos sin valoración, "bate previsiones pero cae". |
| **1** | Positivo | Favorable normal: sube, eleva, supera previsiones, mejora de recomendación, contrato. |
| **2** | Muy positivo | Lenguaje fuerte: se dispara, pulveriza, récord, beneficio +20% o más. |

**Regla.** El impacto se lee en el tono del titular hacia ese objeto, no en lo que haría la cotización. En materias primas, el tono es sobre su precio (petróleo al alza = Positivo para el objeto Petróleo). Solo se asigna lo que el titular menciona o es evidente; no se deducen efectos de segundo orden.

## 5. Origen (de dónde sale la noticia)

| Origen | Qué incluye |
|---|---|
| **Hecho (empresa o dato oficial)** | Resultados, previsiones, comunicados, decisiones de reguladores o tribunales, datos macro oficiales. Incluye caídas de precio explicadas por un hecho de la empresa. |
| **Analista** | Recomendaciones, precios objetivo y visiones de bancos, gestoras, agencias de rating e instituciones. |
| **Rumor / según fuentes** | "Según fuentes", "informa el WSJ", "estudia", "explora", "negocia": hechos aún no confirmados por la empresa. |
| **Opinión / prensa** | Columnas, análisis de prensa, explicaciones ("¿por qué…?"), análisis técnico (soportes, resistencias) y declaraciones de terceros. |
| **Mercado** | Movimientos de precio y crónicas de mercado sin un hecho concreto detrás. |

**Para qué.** Permite comprobar si, cerca de un suelo, lo negativo viene sobre todo de opinión y rumor y el precio deja de reaccionar (tesis de Enrique).

## 6. Temas (10)

Resultados · Recomendación / análisis · Macro · Materias primas · Fusiones y OPAs · Regulación y sanciones · Geopolítica · Mercado · Corporativo · Deuda y bonos

## 7. Motivos de no relevancia (9)

Cripto · Finanzas personales · Divulgativo / genérico · Sin objeto identificable · Fuera de alcance (Latam, India…) · Política sin efecto de mercado · Agenda / convocatoria · Empresa no cotizada · Otros

Desde v3.5 hay dos más (sección 12): **Precio sin causa** · **Análisis técnico**.

Fuentes del modelo: Expansión, Cinco Días, Bolsamanía y TradingView (después se añadió CapitalBolsa). Rankia quedó excluida.

## 8. Ejemplos reales (Excel v3)

Formato: `ámbito · objeto [· sector] → valor`. La línea *Clave* señala qué regla decide el caso.

### 8.1 Varias afectaciones con tonos distintos

1. **Inditex arrebata el trono a Santander de mayor valor de la Bolsa española** (Expansión)
   Relevante · Tema *Mercado* · Origen *Mercado*
   - Empresa · Inditex · Lujo, moda y cosmética → **1**
   - Empresa · Santander · Banca → **-1**
   *Clave:* el mismo titular es favorable para uno y desfavorable para otro; cada objeto lleva su propio tono.

2. **Las Bolsas mundiales se desploman ante la subida del precio del petróleo** (Expansión)
   Relevante · Tema *Materias primas* · Origen *Mercado*
   - Global · Mercados → **-2**
   - Global · Petróleo → **1**
   *Clave:* en materias primas el tono es sobre su precio: el petróleo sube → positivo para Petróleo, aunque hunda las bolsas.

3. **Caídas en Wall Street tras los resultados de Meta y Tesla y con el petróleo al alza** (Bolsamanía)
   Relevante · Tema *Mercado* · Origen *Mercado*
   - Mercado · EE. UU. → **-1**
   - Empresa · Meta · Tecnología → **-1**
   - Empresa · Tesla · Automóvil → **-1**
   - Global · Petróleo → **1**

4. **Ferrovial mete presión a ACS y Acciona con las autopistas por 60.000 millones de dólares ganadas en EE UU** (Cinco Días)
   Relevante · Tema *Corporativo* · Origen *Hecho (empresa o dato oficial)*
   - Empresa · Ferrovial · Construcción e infraestructuras → **1**
   - Empresa · ACS · Construcción e infraestructuras → **-1**
   - Empresa · Acciona · Construcción e infraestructuras → **-1**

5. **Tensión en los mercados: la prima de riesgo francesa se dispara, la tecnología cae con fuerza y el Ibex baja el 2%** (Cinco Días)
   Relevante · Tema *Mercado* · Origen *Mercado*
   - Mercado · Ibex 35 → **-2**
   - Mercado · Francia → **-2**
   - Sector · Tecnología · Tecnología → **-2**
   *Clave:* caída ≥2% en un índice = -2; "se dispara" la prima de riesgo es malo para Francia.

6. **La moderación del petróleo levanta la presión sobre la deuda soberana e impulsa las Bolsas** (Cinco Días)
   Relevante · Tema *Materias primas* · Origen *Mercado*
   - Global · Petróleo → **-1**
   - Global · Mercados → **1**

### 8.2 Sector frente a Empresa

7. **Barclays otorga potenciales del 6% al 23% a los bancos del Ibex** (Expansión)
   Relevante · Tema *Recomendación / análisis* · Origen *Analista*
   - Sector · Banca · Banca → **1**
   *Clave:* habla de los bancos en conjunto, sin nombrarlos → Sector.

8. **Santander, BBVA y Sabadell disparan la venta de cédulas al máximo en diez años** (Expansión)
   Relevante · Tema *Corporativo* · Origen *Hecho (empresa o dato oficial)*
   - Empresa · Santander · Banca → **0**
   - Empresa · BBVA · Banca → **0**
   - Empresa · Sabadell · Banca → **0**
   *Clave:* empresas nombradas → una afectación de Empresa por cada una (con su sector). Emitir deuda es informativo: 0.

9. **Basilea se impone a los bancos y fuerza cambios para evitar que maquillen sus datos** (Expansión)
   Relevante · Tema *Regulación y sanciones* · Origen *Hecho (empresa o dato oficial)*
   - Sector · Banca · Banca → **-1**

10. **Los inversores huyen de los centros de datos: la deuda se hunde y las salidas a Bolsa se cancelan** (Cinco Días)
    Relevante · Tema *Mercado* · Origen *Mercado*
    - Sector · Tecnología · Tecnología → **-2**

### 8.3 Materias primas

11. **La impecable directriz alcista del petróleo** (Expansión)
    Relevante · Tema *Materias primas* · Origen *Opinión / prensa*
    - Global · Petróleo → **1**
    *Clave:* análisis técnico → Opinión / prensa; el tono sobre el precio es alcista.

12. **El oro cae a mínimo de más de dos meses por el temor a la inflación** (TradingView)
    Relevante · Tema *Materias primas* · Origen *Mercado*
    - Global · Materias primas → **-1**

13. **Newmont supera las previsiones de beneficios trimestrales gracias al aumento de los precios del oro** (TradingView)
    Relevante · Tema *Resultados* · Origen *Hecho (empresa o dato oficial)*
    - Empresa · Newmont · Materiales, química y minería → **1**
    - Global · Materias primas → **1**
    *Clave:* el titular menciona la subida del oro, así que también se asigna (no es un efecto deducido).

### 8.4 Opinión frente a Mercado frente a Hecho

14. **Indra y el muro de los 65-66 euros** (Expansión)
    Relevante · Tema *Mercado* · Origen *Opinión / prensa*
    - Empresa · Indra · Industria, defensa y aeroespacial → **0**
    *Clave:* resistencias técnicas → Opinión / prensa; sin tono claro → 0.

15. **Déficit, polarización política y falta de reformas: ¿Por qué la prima de riesgo de Francia se dispara?** (Cinco Días)
    Relevante · Tema *Deuda y bonos* · Origen *Opinión / prensa*
    - Mercado · Francia → **-2**
    *Clave:* explicación "¿por qué…?" → Opinión / prensa, aunque hable de un movimiento de mercado.

16. **Los disturbios inflaman la prima de riesgo de Francia, en máximos desde 2012** (Cinco Días)
    Relevante · Tema *Deuda y bonos* · Origen *Mercado*
    - Mercado · Francia → **-2**
    *Clave:* mismo asunto que el 15, pero contado como movimiento de precio → Mercado.

17. **Merlin acusa en el Ibex el 'efecto CoreWeave'** (Expansión)
    Relevante · Tema *Mercado* · Origen *Mercado*
    - Empresa · Merlin Properties · Inmobiliario → **-1**

18. **El beneficio de Tesla se desploma un 43% en el tercer trimestre** (Expansión)
    Relevante · Tema *Resultados* · Origen *Hecho (empresa o dato oficial)*
    - Empresa · Tesla · Automóvil → **-2**
    *Clave:* beneficio −20% o peor → -2; resultados → Hecho.

19. **EEUU impone una multa histórica de 25.000 millones de dólares a Meta** (Expansión)
    Relevante · Tema *Regulación y sanciones* · Origen *Hecho (empresa o dato oficial)*
    - Empresa · Meta · Tecnología → **-2**

### 8.5 Rumores y analistas

20. **Moderna se desploma un 24% tras filtraciones no verificadas sobre su vacuna contra el melanoma** (Expansión)
    Relevante · Tema *Corporativo* · Origen *Rumor / según fuentes*
    - Empresa · Moderna · Salud y farmacia → **-2**
    *Clave:* la caída la explica una filtración no confirmada → Rumor, no Mercado ni Hecho.

21. **CVC explora una oferta por Verisure sólo un año después de su OPV** (Expansión)
    Relevante · Tema *Fusiones y OPAs* · Origen *Rumor / según fuentes*
    - Empresa · Verisure · Industria, defensa y aeroespacial → **1**
    - Empresa · CVC Capital Partners · Seguros y servicios financieros → **0**
    *Clave:* "explora" → rumor; para la opada una oferta es positiva, para quien compra es neutral.

22. **Según una fuente, BASF ha presentado una oferta de 24 euros por acción al consejo de administración de Evonik** (TradingView)
    Relevante · Tema *Fusiones y OPAs* · Origen *Rumor / según fuentes*
    - Empresa · Evonik · Materiales, química y minería → **1**
    - Empresa · BASF · Materiales, química y minería → **0**

23. **Morgan Stanley deja sin potencial a Redeia por la presión de la deuda** (Expansión)
    Relevante · Tema *Recomendación / análisis* · Origen *Analista*
    - Empresa · Redeia · Eléctricas, renovables y redes → **-1**

24. **El crecimiento mundial se mantiene sólido; la inversión en IA se está extendiendo al resto de la economía** (TradingView)
    Relevante · Tema *Macro* · Origen *Analista*
    - Global · Economía → **1**

### 8.6 No relevantes: un ejemplo de cada motivo

25. **JPMorgan: el bitcoin subirá más a largo plazo que Wall Street y el oro** (Expansión) → No relevante · **Cripto**
    *Clave:* aunque cite a JPMorgan, Wall Street y el oro, la noticia es sobre bitcoin.
26. **Euríbor hoy, 20 de octubre: El Euríbor pone rumbo fijo al 3,3%** (Expansión) → No relevante · **Finanzas personales**
27. **¿Qué oportunidades y qué riesgos supone la IA para los mercados?** (Expansión) → No relevante · **Divulgativo / genérico**
28. **Los mejores y peores valores en términos de valor y momentum** (Expansión) → No relevante · **Sin objeto identificable**
29. **Actividad económica de Argentina -1,7% en agosto: INDEC** (TradingView) → No relevante · **Fuera de alcance (Latam, India…)**
30. **Brufau (Repsol) asegura que prohibir el motor de combustión ha causado un "daño irreparable" y ha envejecido el parque** (Expansión) → No relevante · **Política sin efecto de mercado**
    *Clave:* que aparezca una empresa no basta: es una declaración política sin efecto sobre Repsol.
31. **Ramaco Resources, Inc. (METC) fija la publicación de resultados del tercer trimestre de 2026 para el 3 de noviembre tras el cierre** (TradingView) → No relevante · **Agenda / convocatoria**
32. **La CNMC investiga a Exolum por posible abuso de posición dominante** (Expansión) → No relevante · **Empresa no cotizada**
33. **La CNMV multa con un millón de euros a la sociedad de valores del exCEO del Banco Popular** (Cinco Días) → No relevante · **Otros**

## 9. Aclaraciones v2 (tras el piloto de 300 noticias; prevalecen sobre lo anterior)

**a) Cotizadas fuera de alcance.** Si la cotización principal de la empresa es en Latam, India o Asia (Bimbo, Bradesco,
Grupo Aeroportuario del Sureste…): no relevante, motivo **Fuera de alcance (Latam, India…)**, salvo que la noticia afecte
a una empresa o mercado de nuestro alcance (p. ej. Brasil → Santander o Ibex). Si la cotización principal es en
EE. UU. o Europa (Nu Holdings), es relevante.
- *El tráfico de Grupo Aeroportuario del Sureste, S.A.B. de C.V. (ASUR/B) cae 1.2% interanual en el tercer trimestre* → No relevante · **Fuera de alcance (Latam, India…)**
- *Nu Holdings Ltd. (NU): el CTO Eric Young renunciará* → Relevante · *Corporativo* · *Hecho (empresa o dato oficial)* · Empresa · Nu Holdings · Banca → **0** (cotiza en NYSE)
- *La victoria de Lula penaliza al IBEX 35 en el arranque de una semana de alto voltaje* → Relevante · *Mercado* · *Mercado* · Mercado · Ibex 35 → **-1** (Brasil afecta a un mercado de nuestro alcance)

**b) Cotizada pequeña con noticia rutinaria** (bancos regionales de EE. UU., dividendos ordinarios): relevante, con la
empresa fuera del universo (`en_universo = false`). No hay motivo nuevo: el panel la filtra por universo.
- *Avidia Bancorp, Inc. (AVBC) registra BPA de $0.47 en el tercer trimestre frente a $0.39; declara un dividendo de $0.06* → Relevante · *Resultados* · *Hecho (empresa o dato oficial)* · Empresa · Avidia Bancorp · Banca → **2** (BPA +20%)
- *L3Harris Technologies (LHX) declara un dividendo trimestral de $1.25* → Relevante · *Corporativo* · *Hecho (empresa o dato oficial)* · Empresa · L3Harris · Industria, defensa y aeroespacial → **0**

**c) Listas y sucesos.** Titulares que son solo una lista de tickers o recopilatorios sin contenido: **Sin objeto
identificable**. Catástrofes, sucesos y flujos de mercancías sin efecto de mercado explícito: **Otros**.
- *American Express, Gorman-Rupp, Moderna* → No relevante · **Sin objeto identificable**
- *Taiwán se paraliza ante la llegada del tifón Champi, con casi 1.000 vuelos cancelados* → No relevante · **Otros**
- *Un cargamento de diésel ruso se dirige a EEUU tras el acuerdo Putin-Trump, según datos* → No relevante · **Otros**

**d) Solo empresas cotizadas.** Las afectaciones de Empresa son solo para cotizadas. Las no cotizadas que aparecen en
una noticia relevante no se anotan. Si la noticia solo trata de no cotizadas: no relevante, motivo **Empresa no cotizada**
(una empresa que prepara su salida a bolsa todavía no cotiza).
- *Carrefour estudia la compra de Condis para crecer en Cataluña* → Relevante · *Fusiones y OPAs* · *Rumor / según fuentes* · Empresa · Carrefour · Consumo y distribución → **0** (Condis no se anota)
- *Las gasolineras de Moeve amplían el plazo de su programa de descuento* → No relevante · **Empresa no cotizada**
- *OPay, respaldada por SoftBank, prevé una valoración de hasta 4.400 millones de dólares en su salida a bolsa en EEUU* → No relevante · **Empresa no cotizada**

**e) Divisas.** Una moneda concreta va al **Mercado** de su zona (euro → Europa, dólar → EE. UU., yen → Japón,
libra → Reino Unido), con el tono sobre esa moneda (se debilita = negativo; se fortalece = positivo).
Global · Divisas solo cuando el titular habla del mercado de divisas en general.
- *Pistas para invertir ahora con un euro bajo presión* → Relevante · *Mercado* · *Opinión / prensa* · Mercado · Europa → **-1**
- *Yen se dispara por preocupación por el petróleo, la IA y Francia* → Relevante · *Mercado* · *Mercado* · Mercado · Japón → **2** · Mercado · Francia → **-1** · Sector · Tecnología → **-1**

**f) Macro sin adjetivo.** El tono se fija por lo que el dato significa para la economía por convención: inflación o
precios al alza = negativo; paro a la baja o empleo fuerte = positivo; PMI o confianza por encima de lo previsto =
positivo, por debajo = negativo. Si no hay dirección clara: **0**.
- *Los precios industriales en España suben un 18,3% interanual en septiembre* → Relevante · *Macro* · *Hecho (empresa o dato oficial)* · Mercado · Ibex 35 → **-1**
- *El crecimiento de la eurozona cae a su nivel más bajo en cuatro meses, según el PMI* → Relevante · *Macro* · *Hecho (empresa o dato oficial)* · Mercado · Europa → **-1**

## 10. Aclaraciones v3 (tras la clasificación completa; prevalecen sobre todo lo anterior)

**a) La IA es un tema, no un sector.** Sector · Tecnología solo cuando el titular nombra el sector o sus valores
("las tecnológicas", "sector tecnológico", "valores tecnológicos"). El miedo a la IA sin más va a Global · Mercados o
a las empresas citadas.
- *Yen se dispara por preocupación por el petróleo, la IA y Francia* → Mercado · Japón → **2** · Mercado · Francia → **-1** (**sin** Sector · Tecnología)
- *Las tecnológicas moderan su caída en Asia y el crudo toca máximos de cinco meses* → Sector · Tecnología · Tecnología → **-1** · Mercado · Asia → **-1** · Global · Petróleo → **1** (nombra "las tecnológicas")
- *Las bolsas asiáticas se mantienen cerca de su mínimo de tres meses ante los temores sobre la financiación de la IA* → Mercado · Asia → **-1** (sin Sector · Tecnología)

**b) Salidas a bolsa.** Una empresa con OPV anunciada o folleto registrado (Anthropic) se trata como cotizada: la
noticia es relevante y se anota (Anthropic está en el universo). OpenAI, igual solo si el titular habla de su salida a
bolsa o de su cotización; si no, es no cotizada. SpaceX cotiza.
- *Anthropic registra el folleto para salir a bolsa y muestra pérdidas de 80.700 millones hasta junio* → Relevante · *Corporativo* · *Hecho (empresa o dato oficial)* · Empresa · Anthropic · Tecnología → **-1**
- *OpenAI y la NASK de Polonia colaboran en la investigación sobre la seguridad de la inteligencia artificial* → No relevante · **Empresa no cotizada** (no habla de su salida a bolsa)

**c) Grandes empresas mundiales.** Las ~50 mayores del mundo (TSMC, Samsung, SK Hynix, Tencent, Toyota…) son
excepción a "Asia = Fuera de alcance": son relevantes y están en el universo.
- *Bankinter eleva el objetivo de TSMC a 530 dólares: las claves de su apuesta por el fabricante de chips* → Relevante · *Recomendación / análisis* · *Analista* · Empresa · TSMC · Semiconductores → **1**
- *SK Hynix anunciará este miércoles medidas para aumentar la rentabilidad para los accionistas* → Relevante · *Corporativo* · *Hecho (empresa o dato oficial)* · Empresa · SK Hynix · Semiconductores → **1**

**d) Rentabilidad de los bonos.** Sube = negativo para su mercado; baja = positivo; salvo que el titular atribuya la
bajada a miedo o a huida a refugio, que es negativo.
- *Los rendimientos del Tesoro repuntan pese a las menores apuestas de subida de tipos* → Mercado · EE. UU. → **-1**
- *Rendimiento bonos Tesoro EEUU se hunde ya que resurgen temores sobre sostenibilidad del auge de la IA* → Mercado · EE. UU. → **-1** (bajada por miedo) · Global · Mercados → **-1** (miedo a la IA, regla a)

**e) Objetos de Mercado permitidos.** Además de Ibex 35, DAX, Europa y EE. UU.: países europeos (Francia, Italia,
Portugal, Alemania…), Reino Unido, Canadá, Japón, Corea, China, Australia y Asia. Israel, Latam, India y similares:
**Fuera de alcance (Latam, India…)**, salvo efecto en lo nuestro.
- *El TSX sube gracias a las ganancias del sector tecnológico tras la solicitud de salida a bolsa de Anthropic…* → Mercado · Canadá → **1** · Empresa · Anthropic → **1** · Global · Petróleo → **-1** (Anthropic está nombrada: regla 11 e)
- *Los mercados israelíes ven potencial alcista en la derrota de Netanyahu, tras tres años de repunte* → No relevante · **Fuera de alcance (Latam, India…)**

**f) Mismo dato, distinto verbo.** Puede tener distinto valor: es correcto, se puntúa el tono del texto.
- *La inflación industrial se dispara al 18,3% en septiembre por la energía y marca récord en casi cuatro años* → Mercado · Ibex 35 → **-2**
- *Los precios industriales en España suben un 18,3% interanual en septiembre* → Mercado · Ibex 35 → **-1**

**g) Filiales no cotizadas.** Se asignan a su matriz cotizada (Audi → Volkswagen, Iberia → IAG, Genentech → Roche).
- *Datos clave: VOW: planta de Audi en EE. UU. por $4.2 mil millones; pausa de VE en India; 12 mil recortes de empleo* → Empresa · Volkswagen · Automóvil → **0**
- *Genentech informa una reducción del 43.1% de la proteinuria en fase III en la nefropatía por IgA* → Empresa · Roche · Salud y farmacia → **1**

**h) Datos de un sector en un país.** Van al ámbito **Sector**; el Mercado del país solo si el titular habla de su
economía o de su bolsa en conjunto.
- *Los coches eléctricos se disparan más del 70% en Europa y suponen casi un tercio del mercado* → Sector · Automóvil · Automóvil → **2**
- *La compraventa de vivienda sube un 3,4% en agosto, con su mejor cifra en este mes desde 2024* → Sector · Inmobiliario · Inmobiliario → **1** (no Ibex 35)

**i) El titular manda en el tono.** El resumen solo sirve para identificar objetos, nunca para fijar el valor.
- *Bankinter eleva su beneficio un 11%, hasta los 901 millones* → Empresa · Bankinter · Banca → **1** (aunque el resumen diga que cae en bolsa)

## 11. Aclaraciones v3.4 (prevalecen sobre todo lo anterior)

**a) Grupos de valores de IA.** "Sector de la IA", "neoclouds", "centros de datos", "valores de IA" y expresiones
similares cuentan como nombrar un grupo de valores tecnológicos → **Sector · Tecnología**.
**Pero si en el titular aparece el nombre de una empresa, la afectación va a esa empresa** (y no a Sector · Tecnología; ver e).
- *Por qué Musk cree que más de 200 neoclouds de IA podrían fracasar* → Sector · Tecnología · Tecnología → **-1**
- *Euro se hunde por preocupación sobre deuda francesa; yen sube tras caída del sector de la IA* → … · Sector · Tecnología · Tecnología → **-1**
- *Acciones de CoreWeave, Nebius e Iren caen tras aviso de Musk sobre 200 neoclouds* → Empresa · CoreWeave → **-1** · Empresa · Nebius → **-1** · Empresa · IREN → **-1** (sin Sector · Tecnología)
- *Merlin se desinfla ante el giro de expectativas en los centros de datos* → Empresa · Merlin Properties · Inmobiliario → **-1** (sin Sector · Tecnología)

**b) Bonos sin país.** Global · Mercados con tema *Deuda y bonos* (no se crea un objeto nuevo).
- *Regresa la rentabilidad de la deuda* → Relevante · *Deuda y bonos* · *Opinión / prensa* · Global · Mercados → **-1** (rentabilidad al alza, sección 10 d)

**c) Fuerzas opuestas sobre el mismo objeto** en el titular: **0**.
- *La deuda de EEUU, de amenaza para los mercados a refugio predilecto* → Mercado · EE. UU. → **0**

**d) Filial cuya matriz cotizada está fuera de alcance** (Jaguar → Tata Motors, que cotiza en India): la noticia queda
**Fuera de alcance (Latam, India…)**.
- *Jaguar va a retirar del mercado unos 94 000 vehículos en EEUU por un problema con la cámara de visión trasera, según la NHTSA* → No relevante · **Fuera de alcance (Latam, India…)**

**e) Empresa nombrada, siempre a la empresa.** Si el titular nombra específicamente una empresa, la afectación se
atribuye a esa empresa **siempre**, y esa noticia no lleva afectación de **Sector** (de ningún sector), aunque el
titular mencione también el sector ("las tecnológicas", "la banca", "las telecos"…). El ámbito Sector queda para
noticias del sector en conjunto que no nombran ninguna empresa. Mercados y objetos de Global se anotan igual que antes.
- *El alto costo de la IA pasa la cuenta a Meta y a otras acciones tecnológicas* → Empresa · Meta · Tecnología → **-1** (sin Sector · Tecnología)
- *JP Morgan recorta Telefónica a 'infraponderar' y alerta del riesgo de crédito en las telecos* → Empresa · Telefónica · Telecomunicaciones → **-1** (sin Sector · Telecomunicaciones)
- *Enagás y Amadeus lideran la semana en el Ibex; Solaria se desploma y la banca sufre* → Empresa · Enagás → **1** · Empresa · Amadeus → **1** · Empresa · Solaria → **-2** (sin Sector · Banca)

**f) Cotizadas japonesas.** Quedan **Fuera de alcance (Latam, India…)**, salvo las grandes mundiales del universo
(Toyota…, sección 10 c). Japón sigue siendo un objeto de Mercado válido para noticias de su bolsa o su economía.
- *La japonesa GMO se desploma en Bolsa después de un ciberataque* → No relevante · **Fuera de alcance (Latam, India…)**

**g) Analistas.** Cuando un banco, gestora o analista opina sobre una empresa, la afectada es **esa empresa**, en
positivo o negativo según la opinión; la entidad que opina **no** se anota (aunque sea cotizada). Origen *Analista*.
- *Morgan Stanley deja sin potencial a Redeia por la presión de la deuda* → Empresa · Redeia · Eléctricas, renovables y redes → **-1** (Morgan Stanley no se anota)
- *Bankinter eleva el objetivo de TSMC a 530 dólares: las claves de su apuesta por el fabricante de chips* → Empresa · TSMC · Semiconductores → **1** (Bankinter no se anota)

## 12. v3.5 Precio sin causa y análisis técnico (prevalece sobre todo lo anterior)

### Precio sin causa → no relevante, motivo "Precio sin causa"
Titulares que solo cuentan un movimiento o un nivel de precio, sin una causa concreta. Incluye:
- Solo el movimiento o el nivel: "El Ibex intenta resistir cerca de los 19.000 puntos", "Wall Street cierra en baja para terminar complicada semana", "El petróleo se repliega tras tocar máximos de mayo", "El Dow y el S&P 500 caen, mientras que el sector tecnológico se estabiliza".
- Causas genéricas: cautela, incertidumbre, nervios, recogida de beneficios, "semana complicada", "jornada de volatilidad".
- Precio explicado por el precio del mismo objeto o de sus componentes: "arrastrado por la banca", "las ventas de tecnológicas provocan…", "las tecnológicas moderan su caída".
- Récords, rankings e hitos de precio: "Inditex arrebata el trono a Santander como mayor valor del Ibex", "El mejor día del año para el S&P 500".
- Acompañamiento sin relación causal: "El Ibex abre con un alza del 0,4%… con el petróleo a más de 114 dólares".

### Precio con causa → relevante, como hasta ahora
El movimiento se atribuye a algo concreto:
- Un hecho: "La victoria de Lula tumba a Telefónica y Santander", "CoreWeave, Nebius e Iren caen tras aviso de Musk", "Caídas en Wall Street tras los resultados de Meta y Tesla".
- Un miedo o una expectativa con nombre: "…ante los temores sobre la financiación de la IA", "Los disturbios en Francia agravan los temores de una crisis de deuda".
- Otra variable de mercado distinta del objeto: "El oro sufre por el alza del petróleo", "El Treasury llega al 5,34%: las compañías que más sufren".

La causa puede estar en el titular o en el resumen. El tono sigue saliendo solo del titular (regla v3.3).

Origen Mercado (redefinido): movimiento de precio con causa atribuida por la prensa. Si la causa es un hecho de la empresa o un dato oficial y el titular trata del hecho, el origen sigue siendo Hecho.

### Análisis técnico → no relevante, motivo "Análisis técnico"
Titulares cuyo contenido es la lectura técnica del precio: soportes, resistencias, directrices, niveles clave, sobrecompra o sobreventa, figuras, rupturas, patrones estacionales o electorales (Halloween, midterms) y consultorios de análisis técnico. Va a "Análisis técnico" aunque lo firme un analista o un bróker. Ejemplos: "Santander se la juega en soportes clave", "El Ibex ataca niveles clave de soporte", "Puig rompe resistencias y apunta más alto", "Los chips: cerca de soportes y muy sobrevendido", "Halloween llega al rescate de los alcistas". Excepción: si el titular técnico trae una causa concreta ("el petróleo rompe resistencias por los ataques hutíes"), se clasifica por la causa con las reglas anteriores.

### No cambia
- Agenda / convocatoria sigue igual ("Futuros del Nasdaq +160: 5 claves antes de la apertura", "Día de PMI y cautela en bolsa").
- Un análisis fundamental o un artículo que explica el porqué de una caída ("Por qué Bankinter cae un 7,56%") sigue siendo relevante, con su origen correspondiente.

### Ejemplos anteriores que la v3.5 deja superados
Estos ejemplos de secciones anteriores ya no se aplican tal como están escritos:
- 8.1 n.º 1, *Inditex arrebata el trono a Santander…* → No relevante · **Precio sin causa** (ranking de precio).
- 8.3 n.º 11, *La impecable directriz alcista del petróleo* → No relevante · **Análisis técnico**.
- 8.4 n.º 14, *Indra y el muro de los 65-66 euros* → No relevante · **Análisis técnico**.
- 10 a, *Las tecnológicas moderan su caída en Asia y el crudo toca máximos de cinco meses* → No relevante · **Precio sin causa**.
- La definición de **Mercado** en la sección 5 ("movimientos de precio y crónicas de mercado sin un hecho concreto detrás") queda sustituida por la de esta sección: un movimiento sin causa ya no es relevante.
