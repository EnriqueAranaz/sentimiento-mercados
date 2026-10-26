# Criterios de clasificación de titulares

**Versión de criterios: `v3`** (modelo del Excel `referencia/clasificacion_titulares_2026-10-26_v3.xlsx`, 26/10/2026).
Este documento es la **única fuente de criterios** del agente clasificador. Las secciones 1 a 7 son copia íntegra
de la hoja *Criterios* del Excel; la sección 8 son ejemplos reales del Excel, clasificados a mano.
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
