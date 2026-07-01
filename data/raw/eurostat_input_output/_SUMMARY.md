# data/raw/eurostat_input_output Summary

Status: TASK-062 bounded raw evidence fixture.

This directory contains the recorded Eurostat JSON-stat fixture used by the bounded input-output matrix evidence slice.

## Fixture

- `eurostat-naio-10-cp1700-de-fr-2020-dom-imp-cpa-a01-cpa-c10-12.json`

## Source

Provider: Eurostat dissemination API.

Dataset:

- `naio_10_cp1700` — symmetric input-output table at basic prices, product by product.

Bounded filters:

- `geo`: `DE`, `FR`
- `time`: `2020`
- `unit`: `MIO_EUR`
- `stk_flow`: `DOM`, `IMP`
- `prd_use`: `CPA_A01`, `CPA_C10-12`
- `prd_ava`: `CPA_A01`, `CPA_C10-12`
- `freq`: `A`

## Evidence role

This fixture supports TASK-062. It intentionally introduces matrix-shaped product-by-product input-output evidence while remaining source-specific and bounded.

The fixture is not broad Eurostat NAIO support, not a supply-use/input-output framework, not a CPA classification framework, not canonical loading, and not KnowledgeForge semantics.
