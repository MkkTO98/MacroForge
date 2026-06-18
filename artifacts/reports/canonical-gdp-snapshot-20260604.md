# Canonical GDP Snapshot

Status: succeeded
Generated: 2026-06-04T00:00:00Z
Database safety: isolated_temporary_database

No unit conversion or frequency aggregation is performed.
Core report queries use curated canonical tables plus meta source/dataset/lineage/quality metadata only.

## Coverage

Sources: EUROSTAT_NAMQ_GDP, OECD_NAAG, WDI
Fact rows total: 20
Territories: AUS, DEU, DNK, FRA, USA
Frequencies: A, Q
Periods: 2020, 2021, 2023 Q1, 2023 Q2
Units: CP_MEUR, unknown, USD_EXC, USD_PPP

## Missingness

Expected bounded observations: 16
Observed observations: 16
Missing observations: 0

## Data quality

Duplicate fact grains: 0
Failing quality checks: 0
Core query boundary: curated_and_meta_only

## Source lineage

| Source | Dataset releases | Lineage events | Latest artifact |
| --- | --- | --- | --- |
| EUROSTAT_NAMQ_GDP | 1 | 2 | staging.eurostat_namq_observation |
| OECD_NAAG | 1 | 2 | staging.oecd_sdmx_observation |
| WDI | 1 | 2 | staging.wdi_observation |

## GDP observations

| Source | Territory | Period | Frequency | Indicator | Unit | Value |
| --- | --- | --- | --- | --- | --- | --- |
| EUROSTAT_NAMQ_GDP | DEU | 2023 Q1 | Q | B1GQ | CP_MEUR | 1043520.0 |
| EUROSTAT_NAMQ_GDP | DEU | 2023 Q2 | Q | B1GQ | CP_MEUR | 1031880.0 |
| EUROSTAT_NAMQ_GDP | FRA | 2023 Q1 | Q | B1GQ | CP_MEUR | 684762.7 |
| EUROSTAT_NAMQ_GDP | FRA | 2023 Q2 | Q | B1GQ | CP_MEUR | 706147.7 |
| OECD_NAAG | AUS | 2020 | A | B1GQ | USD_EXC | 1439.0230643897 |
| OECD_NAAG | AUS | 2020 | A | B1GQ | USD_PPP | 1461.06600664252 |
| OECD_NAAG | AUS | 2021 | A | B1GQ | USD_EXC | 1755.45328534911 |
| OECD_NAAG | AUS | 2021 | A | B1GQ | USD_PPP | 1674.32946449161 |
| OECD_NAAG | USA | 2020 | A | B1GQ | USD_EXC | 21375.281 |
| OECD_NAAG | USA | 2020 | A | B1GQ | USD_PPP | 21375.281 |
| OECD_NAAG | USA | 2021 | A | B1GQ | USD_EXC | 23725.645 |
| OECD_NAAG | USA | 2021 | A | B1GQ | USD_PPP | 23725.645 |
| WDI | DNK | 2020 | A | NY.GDP.MKTP.CD | unknown | 355631021931.621 |
| WDI | DNK | 2021 | A | NY.GDP.MKTP.CD | unknown | 406110162088.054 |
| WDI | USA | 2020 | A | NY.GDP.MKTP.CD | unknown | 21060473613000 |
| WDI | USA | 2021 | A | NY.GDP.MKTP.CD | unknown | 23315080560000 |
