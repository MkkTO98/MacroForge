# OECD/SDMX codelist and label enrichment

## Result

- Source: OECD_NAAG — OECD annual national accounts / NAAG Chapter 1 GDP dataflow
- Provider dataset code: `OECD.SDD.NAD,DSD_NAAG@DF_NAAG_I`
- Endpoint: `https://sdmx.oecd.org/public/rest/v1/dataflow/OECD.SDD.NAD/all/latest`
- Content type: `application/vnd.sdmx.structure+xml; version=2.1; charset=utf-8`
- Raw bytes: 2516
- Raw SHA-256: `fd0fd040345fed0de31cd9db8f968bf536e2a50e05e661a1d53636493d6dfda2`
- Scope boundary: No PostgreSQL schema change, no live `macro` database write, and not a generalized SDMX/source framework.

## Bounded labels

| concept | code | label | description |
| --- | --- | --- | --- |
| MEASURE | B1GQ | Gross domestic product | GDP, expenditure approach, current prices. |
| REF_AREA | AUS | Australia |  |
| REF_AREA | USA | United States |  |
| UNIT_MEASURE | USD_EXC | US dollars, exchange rate converted |  |
| UNIT_MEASURE | USD_PPP | US dollars, PPP converted |  |
| CONF_STATUS | F | Free for publication |  |
| OBS_STATUS | A | Normal value |  |
| DECIMALS | 2 |  | No codelist label found in bounded structure fixture. |

## Limitations

- Bounded to currently observed OECD/SDMX smoke-slice codes; not a broad codelist harvest.
- DECIMALS is preserved as an observed attribute value when no codelist entry is present.
- No PostgreSQL schema change or live macro write is implied by this metadata evidence.
