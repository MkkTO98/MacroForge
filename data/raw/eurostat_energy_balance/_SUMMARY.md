# data/raw/eurostat_energy_balance Summary

Status: TASK-064 bounded raw evidence fixture.

This directory contains the recorded Eurostat JSON-stat fixture used by the bounded energy-balance evidence slice.

## Fixture

- `eurostat-nrg-bal-c-de-fr-2022-2023-ktoe-pprd-imp-exp-fce-total-ra000.json`

## Source

Provider: Eurostat dissemination API.
Dataset: `nrg_bal_c` — Complete energy balances.

Query scope:

- countries: `DE`, `FR`;
- periods: `2022`, `2023`;
- unit: `KTOE`;
- energy balance components: `PPRD`, `IMP`, `EXP`, `FC_E`;
- energy products/fuels: `TOTAL`, `RA000`.

Expected observations: 32.

## Non-goals

This fixture does not imply broad Eurostat Energy support, generic JSON-stat infrastructure, generic energy infrastructure, canonical energy semantics, canonical loading, derived balances, unit conversion, or KnowledgeForge interpretation.
