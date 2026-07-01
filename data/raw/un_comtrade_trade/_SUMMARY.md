# data/raw/un_comtrade_trade Summary

Status: TASK-060 bounded raw evidence fixture.

This directory contains the recorded UN Comtrade public preview JSON fixture used by the bounded international-trade domain expansion slice.

## Fixture

- `un-comtrade-usa-jpn-total-goods-2023-import-export.json`
  - Source: UN Comtrade public preview API.
  - Type/frequency/classification: commodities, annual, HS.
  - Reporter: USA (`reporterCode=842`).
  - Partner: Japan (`partnerCode=392`).
  - Product: `TOTAL` / All Commodities.
  - Directions: imports and exports (`flowCode=M,X`).
  - Period: 2023.
  - Expected observations: 2.
  - Recorded values: import = 151,580,564,290; export = 76,154,045,176.

## Boundaries

- Evidence-only fixture for TASK-060.
- No broad UN Comtrade support.
- No generic trade infrastructure.
- No product classification framework.
- No quantity/volume interpretation.
- No mirror trade reconciliation.
- No canonical loading.
