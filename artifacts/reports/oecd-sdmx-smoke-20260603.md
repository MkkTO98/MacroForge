# OECD/SDMX smoke evidence slice

## Result

- Source: OECD_NAAG — OECD annual national accounts / NAAG Chapter 1 GDP dataflow
- Provider dataset code: `OECD.SDD.NAD,DSD_NAAG@DF_NAAG_I`
- Endpoint: `https://sdmx.oecd.org/public/rest/v1/data/OECD.SDD.NAD,DSD_NAAG@DF_NAAG_I/.?startPeriod=2020&endPeriod=2021`
- Content type: `application/vnd.sdmx.genericdata+xml; version=2.1; charset=utf-8`
- Raw bytes: 1002311
- Raw SHA-256: `d81d56186d66adddf487a08389d75607af3d9da4fccfd08c690f810337d76a31`
- Observations: 8 observations
- Scope boundary: No PostgreSQL schema change and no live `macro` database write.

## Source contract mapping

- `source_code`: `OECD_NAAG`
- `provider_dataset_code`: `OECD.SDD.NAD,DSD_NAAG@DF_NAAG_I`
- `indicator_code`: SDMX `MEASURE`
- `territory_code`: SDMX `REF_AREA`
- `period`: SDMX observation `TIME_PERIOD`
- `frequency`: SDMX `FREQ`
- `value`: SDMX `ObsValue.value`
- `unit`: SDMX `UNIT_MEASURE`
- `attributes`: SDMX observation attributes such as `CONF_STATUS`, `DECIMALS`, and `OBS_STATUS`
- `source_payload`: preserved series dimensions, observation dimension, and original observation value

## Normalized rows

| indicator | territory | period | frequency | unit | value |
| --- | --- | --- | --- | --- | ---: |
| B1GQ | AUS | 2020 | A | USD_EXC | 1439.0230643897 |
| B1GQ | USA | 2020 | A | USD_EXC | 21375.281 |
| B1GQ | AUS | 2021 | A | USD_EXC | 1755.45328534911 |
| B1GQ | USA | 2021 | A | USD_EXC | 23725.645 |
| B1GQ | AUS | 2020 | A | USD_PPP | 1461.06600664252 |
| B1GQ | USA | 2020 | A | USD_PPP | 21375.281 |
| B1GQ | AUS | 2021 | A | USD_PPP | 1674.32946449161 |
| B1GQ | USA | 2021 | A | USD_PPP | 23725.645 |

## Schema pressure

No immediate schema change is required for this smoke evidence slice. Future PostgreSQL promotion should revisit codelist labels/descriptions and richer attribute-set handling before changing migrations.
