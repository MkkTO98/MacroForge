# data/raw/wdi_demographics Summary

Status: TASK-061 bounded raw evidence fixture.

This directory contains the recorded World Bank WDI JSON fixture used by the bounded demographic foundation evidence slice.

## Fixture

- `wdi-demographic-foundation-usa-jpn-2022-2023.json`

## Source

World Bank API v2, one compact no-key query per demographic foundation indicator.

Indicators:

- `SP.POP.TOTL` — total population
- `SP.POP.GROW` — annual population growth
- `SP.POP.0014.TO.ZS` — population ages 0-14 (% of total population)
- `SP.POP.1564.TO.ZS` — population ages 15-64 (% of total population)
- `SP.POP.65UP.TO.ZS` — population ages 65 and above (% of total population)
- `SP.DYN.TFRT.IN` — fertility rate, total (births per woman)
- `SP.DYN.LE00.IN` — life expectancy at birth, total (years)
- `SP.URB.TOTL.IN.ZS` — urban population (% of total population)

Bounded filters:

- countries: USA and Japan
- periods: 2022 and 2023
- expected rows: 32

## Scope boundary

This is immutable evidence for TASK-061 only. It is not broad WDI demographic support, a demographic database, a projection system, a generic demographic framework, canonical loading, or KnowledgeForge semantics.
