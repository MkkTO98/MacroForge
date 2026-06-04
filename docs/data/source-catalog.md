# Source Catalog

## Accepted v1 source

### World Bank WDI

Status: accepted first source for v1.

Reason: public/no-key, broad macro coverage, low friction, and sufficient complexity to exercise geography, indicator, period, unit, source metadata, raw checksums, and validation.

Initial smoke target:

- Countries: USA, DNK
- Indicators: GDP and population
- Years: 2020-2021
- Expected rough shape: 2 countries x 2 indicators x 2 years = 8 observations before missing-data handling.

## Deferred candidates

- FRED: useful second source, likely requires API-key policy decision.
- OECD, IMF, Eurostat: later macro expansion.
- UN WPP/UNPD: historically discussed but data endpoint/token friction makes it a poor first source.
- SEC/filings/fundamentals/equities: later research expansion, not v1 data substrate.
