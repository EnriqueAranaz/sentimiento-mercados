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
| Eutelsat | EURONEXT:ETL | Pequeña extranjera | 29/10/2026 |
| Werner Enterprises | NASDAQ:WERN | Pequeña extranjera | 29/10/2026 |
| F&M Bank | OTC:FMBM | Banco regional pequeño de EE. UU. | 29/10/2026 |
| Northeast Indiana Bancorp | OTC:NIDB | Banco regional pequeño de EE. UU. | 29/10/2026 |
| Oxford Bank Corporation | OTC:OXBC | Banco regional pequeño de EE. UU. | 29/10/2026 |
| CareView Communications | OTC:CRVW | Microcotizada | 29/10/2026 |
| Fortune Minerals | TSX:FT | Microcotizada | 29/10/2026 |
| Median Technologies | EURONEXT:ALMDT | Cotiza en mercado de crecimiento | 29/10/2026 |
| Perrigo | NYSE:PRGO | Pequeña (menos de ~4.000 M) | 29/10/2026 |
| LLYC | BME:LLYC | Cotiza en mercado de crecimiento | 30/10/2026 |
| Algonquin Power & Utilities | TSX:AQN | Pequeña extranjera | 31/10/2026 |
| Hinge Health | NYSE:HNGE | Pequeña (menos de ~4.000 M) | 03/11/2026 |
| Hiscox | LSE:HSX | Pequeña (menos de ~4.000 M) | 03/11/2026 |
| Insight Enterprises | NASDAQ:NSIT | Pequeña (menos de ~4.000 M) | 03/11/2026 |
| Iveco Group | MIL:IVG | Comprada por Tata Motors (India) | 03/11/2026 |
| Teva Pharmaceutical | NYSE:TEVA | Fuera de alcance (Israel) | 03/11/2026 |
| CVR Energy | NYSE:CVI | Pequeña (menos de ~4.000 M) | 04/11/2026 |
| Coupang | NYSE:CPNG | Negocio en Asia (Corea), aunque cotice en NYSE | 05/11/2026 |
| Cipher Digital | NASDAQ:CIFR | Minería de bitcoin (cripto) | 05/11/2026 |
| Greencoat Renewables | — | Pequeña extranjera | 05/11/2026 |
| CEVASA | BME:CEV | Microcotizada (fixing) | 06/11/2026 |
| Caris Life Sciences | NASDAQ:CAI | Pequeña (menos de ~4.000 M) | 06/11/2026 |
| Datavault AI | NASDAQ:DVLT | Microcotizada | 06/11/2026 |
| Gold Reserve | TSXV:GRZ | Microcotizada | 06/11/2026 |
| Tetragon Financial Group | EURONEXT:TFG | Pequeña (menos de ~4.000 M) | 06/11/2026 |
| Extreme Networks | NASDAQ:EXTR | Pequeña (menos de ~4.000 M) | 06/11/2026 |
| Under Armour | NYSE:UA | Pequeña (menos de ~4.000 M) | 06/11/2026 |
| Firefly Aerospace | NASDAQ:FLY | Pequeña (menos de ~4.000 M) | 06/11/2026 |
| Associated Banc-Corp | NYSE:ASB | Banco regional de EE. UU. | 06/11/2026 |
| Carmila | EURONEXT:CARM | Pequeña (menos de ~4.000 M) | 08/11/2026 |
| Organon | NYSE:OGN | Pequeña (menos de ~4.000 M) | 08/11/2026 |
| Man Group | LSE:EMG | Pequeña (menos de ~4.000 M) | 08/11/2026 |
| NextDecade | NASDAQ:NEXT | Pequeña (menos de ~4.000 M) | 08/11/2026 |
| EverCommerce | NASDAQ:EVCM | Pequeña (menos de ~4.000 M) | 08/11/2026 |
| Innodata | NASDAQ:INOD | Pequeña (menos de ~4.000 M) | 08/11/2026 |
| Voyager Technologies | NYSE:VOYG | Pequeña (menos de ~4.000 M) | 08/11/2026 |
| Mach Natural Resources | NYSE:MNR | Pequeña (menos de ~4.000 M) | 08/11/2026 |
| Westshore Terminals | TSX:WTE | Pequeña (menos de ~4.000 M) | 08/11/2026 |
| FIGS | NYSE:FIGS | Pequeña (menos de ~4.000 M) | 08/11/2026 |
| Biglari Holdings | NYSE:BH | Pequeña (menos de ~4.000 M) | 08/11/2026 |
| Pollard Banknote | TSX:PBL | Pequeña (menos de ~4.000 M) | 08/11/2026 |
| AngioDynamics | NASDAQ:ANGO | Pequeña (menos de ~4.000 M) | 08/11/2026 |
| Holley | NYSE:HLLY | Pequeña (menos de ~4.000 M) | 08/11/2026 |
| Taiga Building Products | TSX:TBL | Pequeña (menos de ~4.000 M) | 08/11/2026 |
| Runway Growth Finance | NASDAQ:RWAY | Pequeña (menos de ~4.000 M) | 08/11/2026 |
| Big Rock Brewery | TSX:BR | Microcotizada | 08/11/2026 |
| Avalon Holdings | AMEX:AWX | Microcotizada | 08/11/2026 |
| Chicago Rivet & Machine | AMEX:CVR | Microcotizada | 08/11/2026 |
| Quoin Pharmaceuticals | NASDAQ:QNRX | Microcotizada | 08/11/2026 |
| TEN Holdings | NASDAQ:XHLD | Microcotizada | 08/11/2026 |
| bioAffinity Technologies | NASDAQ:BIAF | Microcotizada | 08/11/2026 |
| Karnalyte Resources | TSX:KRN | Microcotizada | 08/11/2026 |
| Light AI | NEO:ALGO | Microcotizada | 08/11/2026 |
| ZYUS Life Sciences | TSXV:ZYUS | Microcotizada | 08/11/2026 |
| Soligenix | NASDAQ:SNGX | Microcotizada | 08/11/2026 |
| YYForce | NASDAQ:YFOR | Microcotizada | 08/11/2026 |
| FB Bancorp | NASDAQ:FBLA | Banco regional pequeño de EE. UU. | 08/11/2026 |
| Codan | ASX:CDA | Pequeña (menos de ~4.000 M) | 09/11/2026 |
| Titan America | NYSE:TTAM | Pequeña (menos de ~4.000 M) | 09/11/2026 |
| Apple Hospitality REIT | NYSE:APLE | Pequeña (menos de ~4.000 M) | 09/11/2026 |
| Openlane | NYSE:OPLN | Pequeña (menos de ~4.000 M) | 09/11/2026 |
| Delek US Holdings | NYSE:DK | Pequeña (menos de ~4.000 M) | 09/11/2026 |
| Alight | NYSE:ALIT | Pequeña (menos de ~4.000 M) | 09/11/2026 |
| Sable Offshore | NYSE:SOC | Pequeña (menos de ~4.000 M) | 09/11/2026 |
| Kestra Medical Technologies | NASDAQ:KMTS | Pequeña (menos de ~4.000 M) | 09/11/2026 |
| Vir Biotechnology | NASDAQ:VIR | Pequeña (menos de ~4.000 M) | 09/11/2026 |
| United States Antimony | AMEX:UAMY | Pequeña (menos de ~4.000 M) | 09/11/2026 |
| SI-BONE | NASDAQ:SIBN | Pequeña (menos de ~4.000 M) | 09/11/2026 |
| The Children's Place | NASDAQ:PLCE | Microcotizada | 09/11/2026 |
| Zura Bio | NASDAQ:ZURA | Microcotizada | 09/11/2026 |
| Realbotix | TSXV:XBOT | Microcotizada | 09/11/2026 |
| Sypris Solutions | NASDAQ:SYPR | Microcotizada | 09/11/2026 |
| Innovative Eyewear | NASDAQ:LUCY | Microcotizada | 09/11/2026 |
| Ternium | NYSE:TX | Negocio en Latam (México y Argentina), aunque cotice en NYSE | 09/11/2026 |
| Onterris | NYSE:ONT | Tamaño no verificado; sin interés | 09/11/2026 |
| Greenfire Resources | NYSE:GFR | Pequeña (menos de ~4.000 M) | 09/11/2026 |
| Via Transportation | NYSE:VIA | Pequeña (menos de ~4.000 M) | 12/11/2026 |
| Cactus | NYSE:WHD | Pequeña (menos de ~4.000 M) | 12/11/2026 |
| Resideo Technologies | NYSE:REZI | Pequeña (menos de ~4.000 M) | 12/11/2026 |
| StubHub | NYSE:STUB | Pequeña (menos de ~4.000 M) | 12/11/2026 |
| ITV | LSE:ITV | Pequeña (menos de ~4.000 M) | 12/11/2026 |
| Digi International | NASDAQ:DGII | Pequeña (menos de ~4.000 M) | 12/11/2026 |
| Energy Vault | NYSE:NRGV | Pequeña (menos de ~4.000 M) | 12/11/2026 |
| Diodes | NASDAQ:DIOD | Pequeña (menos de ~4.000 M) | 12/11/2026 |
| Burford Capital | NYSE:BUR | Pequeña (menos de ~4.000 M) | 12/11/2026 |
| Kyivstar Group | NASDAQ:KYIV | Pequeña (menos de ~4.000 M) | 12/11/2026 |
| Capri Holdings | NYSE:CPRI | Pequeña (menos de ~4.000 M) | 12/11/2026 |
| B&M European Value Retail | LSE:BME | Pequeña (menos de ~4.000 M) | 12/11/2026 |
| IWG | LSE:IWG | Pequeña (menos de ~4.000 M) | 12/11/2026 |
| Savills | LSE:SVS | Pequeña (menos de ~4.000 M) | 12/11/2026 |
| WEBTOON Entertainment | NASDAQ:WBTN | Pequeña (menos de ~4.000 M) | 12/11/2026 |
| ArcBest | NASDAQ:ARCB | Pequeña (menos de ~4.000 M) | 12/11/2026 |
| Grocery Outlet | NASDAQ:GO | Pequeña (menos de ~4.000 M) | 12/11/2026 |
| Sally Beauty | NYSE:SBH | Pequeña (menos de ~4.000 M) | 12/11/2026 |
| Teekay Tankers | NYSE:TNK | Pequeña (menos de ~4.000 M) | 12/11/2026 |
| Lumexa Imaging | NASDAQ:LMRI | Pequeña (menos de ~4.000 M) | 12/11/2026 |
| Lithium Americas | NYSE:LAC | Pequeña (menos de ~4.000 M) | 12/11/2026 |
| Atalaya Mining | LSE:ATYM | Pequeña (menos de ~4.000 M) | 12/11/2026 |
| Avio | MIL:AVIO | Pequeña (menos de ~4.000 M) | 12/11/2026 |
| Vesuvius | LSE:VSVS | Pequeña (menos de ~4.000 M) | 12/11/2026 |
| Meren Energy | TSX:MER | Pequeña (menos de ~4.000 M) | 12/11/2026 |
| CorMedix | NASDAQ:CRMD | Pequeña (menos de ~4.000 M) | 12/11/2026 |
| EVgo | NASDAQ:EVGO | Pequeña (menos de ~4.000 M) | 12/11/2026 |
| loanDepot | NYSE:LDI | Pequeña (menos de ~4.000 M) | 12/11/2026 |
| NGL Energy Partners | NYSE:NGL | Pequeña (menos de ~4.000 M) | 12/11/2026 |
| Ballard Power Systems | NASDAQ:BLDP | Pequeña (menos de ~4.000 M) | 12/11/2026 |
| Mutares | XETR:MUX | Pequeña (menos de ~4.000 M) | 12/11/2026 |
| Valneva | EURONEXT:VLA | Microcotizada | 12/11/2026 |
| B&G Foods | NYSE:BGS | Microcotizada | 12/11/2026 |
| Carlsmed | NASDAQ:CARL | Microcotizada | 12/11/2026 |
| Agilyx | OSL:AGLX | Microcotizada | 12/11/2026 |
| Repay Holdings | NASDAQ:RPAY | Microcotizada | 12/11/2026 |
| Senseonics | NASDAQ:SENS | Microcotizada | 12/11/2026 |
| Surrozen | NASDAQ:SRZN | Microcotizada | 12/11/2026 |
| Douglas Elliman | NYSE:DOUG | Microcotizada | 12/11/2026 |
| American Rebel | NASDAQ:AREB | Microcotizada | 12/11/2026 |
| BridgeBio Oncology Therapeutics | NASDAQ:BBOT | Microcotizada | 12/11/2026 |
| Palisade Bio | NASDAQ:PALI | Microcotizada | 12/11/2026 |
| Inovio Pharmaceuticals | NASDAQ:INO | Microcotizada | 12/11/2026 |
| Exagen | NASDAQ:XGN | Microcotizada | 12/11/2026 |
| SHF Holdings | NASDAQ:SHFS | Microcotizada | 12/11/2026 |
| Rocket One | NASDAQ:RKTO | Microcotizada | 12/11/2026 |
| Black Rock Coffee Bar | NASDAQ:BRCB | Microcotizada | 12/11/2026 |
| Draganfly | NASDAQ:DPRO | Microcotizada | 12/11/2026 |
| Eupraxia Pharmaceuticals | TSX:EPRX | Microcotizada | 12/11/2026 |
| Gevo | NASDAQ:GEVO | Microcotizada | 12/11/2026 |
| Satellogic | NASDAQ:SATL | Microcotizada | 12/11/2026 |
| Spire Global | NYSE:SPIR | Microcotizada | 12/11/2026 |
| iBio | NASDAQ:IBIO | Microcotizada | 12/11/2026 |
| OptimizeRx | NASDAQ:OPRX | Microcotizada | 12/11/2026 |
| BC Partners Lending | NASDAQ:BCIC | Microcotizada | 12/11/2026 |
| AGI Inc | NYSE:AGBK | Microcotizada | 12/11/2026 |
| Alibaba | NYSE:BABA | Negocio en Asia (China), aunque cotice en NYSE | 12/11/2026 |
| Digi Spain | BME:DIGIS | Duplicado de Digi Communications (ya en la tabla) | 12/11/2026 |
| Gulfport Energy | NYSE:GPOR | Pequeña (menos de ~4.000 M) | 14/11/2026 |
| Ashland | NYSE:ASH | Pequeña (menos de ~4.000 M) | 14/11/2026 |
| NGEx Minerals | TSX:NGEX | Pequeña (menos de ~4.000 M) | 14/11/2026 |
| CG Oncology | NASDAQ:CGON | Pequeña (menos de ~4.000 M) | 14/11/2026 |
| Denali Therapeutics | NASDAQ:DNLI | Pequeña (menos de ~4.000 M) | 14/11/2026 |
| Mobico Group | LSE:MCG | Pequeña (menos de ~4.000 M) | 14/11/2026 |
| Fnac Darty | EURONEXT:FNAC | Pequeña (menos de ~4.000 M) | 14/11/2026 |
| Altri | ELI:ALTR | Pequeña (menos de ~4.000 M) | 14/11/2026 |
| BW LPG | OSL:BWLPG | Pequeña (menos de ~4.000 M) | 14/11/2026 |
| Okeanis Eco Tankers | NYSE:ECO | Pequeña (menos de ~4.000 M) | 14/11/2026 |
| Uniti Group | NASDAQ:UNIT | Pequeña (menos de ~4.000 M) | 14/11/2026 |
| Cogent Communications | NASDAQ:CCOI | Pequeña (menos de ~4.000 M) | 14/11/2026 |
| Papa John's | NASDAQ:PZZA | Pequeña (menos de ~4.000 M) | 14/11/2026 |
| Driven Brands | NASDAQ:DRVN | Pequeña (menos de ~4.000 M) | 14/11/2026 |
| Agios Pharmaceuticals | NASDAQ:AGIO | Pequeña (menos de ~4.000 M) | 14/11/2026 |
| Alphatec Holdings | NASDAQ:ATEC | Pequeña (menos de ~4.000 M) | 14/11/2026 |
| Ardent Health | NYSE:ARDT | Pequeña (menos de ~4.000 M) | 14/11/2026 |
| Beam Therapeutics | NASDAQ:BEAM | Pequeña (menos de ~4.000 M) | 14/11/2026 |
| BioCryst Pharmaceuticals | NASDAQ:BCRX | Pequeña (menos de ~4.000 M) | 14/11/2026 |
| Evommune | NYSE:EVMN | Pequeña (menos de ~4.000 M) | 14/11/2026 |
| Alumis | NASDAQ:ALMS | Pequeña (menos de ~4.000 M) | 14/11/2026 |
| Heartflow | NASDAQ:HTFL | Pequeña (menos de ~4.000 M) | 14/11/2026 |
| Immatics | NASDAQ:IMTX | Pequeña (menos de ~4.000 M) | 14/11/2026 |
| Novocure | NASDAQ:NVCR | Pequeña (menos de ~4.000 M) | 14/11/2026 |
| AbCellera Biologics | NASDAQ:ABCL | Pequeña (menos de ~4.000 M) | 14/11/2026 |
| Cullinan Therapeutics | NASDAQ:CGEM | Pequeña (menos de ~4.000 M) | 14/11/2026 |
| GH Research | NASDAQ:GHRS | Pequeña (menos de ~4.000 M) | 14/11/2026 |
| Crescent Biopharma | NASDAQ:CBIO | Pequeña (menos de ~4.000 M) | 14/11/2026 |
| EyePoint | NASDAQ:EYPT | Pequeña (menos de ~4.000 M) | 14/11/2026 |
| SS Innovations International | NASDAQ:SSII | Pequeña (menos de ~4.000 M) | 14/11/2026 |
| GO Residential REIT | TSX:GO.U | Pequeña (menos de ~4.000 M) | 14/11/2026 |
| AEVEX | NYSE:AVEX | Pequeña (menos de ~4.000 M) | 14/11/2026 |
| Forgent Power Solutions | NYSE:FPS | Pequeña (menos de ~4.000 M) | 14/11/2026 |
| FuelCell Energy | NASDAQ:FCEL | Pequeña (menos de ~4.000 M) | 14/11/2026 |
| Stamper Oil & Gas | TSXV:STMP | Microcotizada | 14/11/2026 |
| American Shared Hospital Services | AMEX:AMS | Microcotizada | 14/11/2026 |
| Presurance Holdings | NASDAQ:PRHI | Microcotizada | 14/11/2026 |
| Candel Therapeutics | NASDAQ:CADL | Microcotizada | 14/11/2026 |
| Horizon Technology Finance | NASDAQ:HRZN | Microcotizada | 14/11/2026 |
| Angel Studios | NYSE:ANGX | Microcotizada | 14/11/2026 |
| Fractyl Health | NASDAQ:GUTS | Microcotizada | 14/11/2026 |
| KinderCare Learning | NYSE:KLC | Microcotizada | 14/11/2026 |
| LifeMD | NASDAQ:LFMD | Microcotizada | 14/11/2026 |
| Intellinetics | AMEX:INLX | Microcotizada | 14/11/2026 |
| Toppoint Holdings | AMEX:TOPP | Microcotizada | 14/11/2026 |
| Blue Chip Capital Group | OTC:BCCG | Microcotizada | 14/11/2026 |
| Kapsch TrafficCom | VIE:KTCG | Microcotizada | 14/11/2026 |
| Eurobattery Minerals | NGM:BAT | Microcotizada | 14/11/2026 |
| Avalo Therapeutics | NASDAQ:AVTX | Microcotizada | 14/11/2026 |
| BioAge Labs | NASDAQ:BIOA | Microcotizada | 14/11/2026 |
| Context Therapeutics | NASDAQ:CNTX | Microcotizada | 14/11/2026 |
| Larimar Therapeutics | NASDAQ:LRMR | Microcotizada | 14/11/2026 |
| PepGen | NASDAQ:PEPG | Microcotizada | 14/11/2026 |
| Hannun | BME:HNN | Cotiza en mercado de crecimiento | 14/11/2026 |
| CNB Financial | NASDAQ:CCNE | Banco regional pequeño de EE. UU. | 14/11/2026 |
