# Project State

## Current status

TASK-215 BIS credit-to-GDP-gap Phase 2 repository expansion is complete and uncommitted. Do not stage, commit, push, clean, restore, delete, or move files without explicit authorization.

TASK-214 BIS WS_DSR debt-service-ratio expansion was previously published to `origin/main` in commit `7f190e2d534333914c2cb40f4600aae270173ed5`.

## Recent completed work

- TASK-215 selected BIS quarterly credit-to-GDP gaps (`BIS:WS_CREDIT_GAP`) for private non-financial sector credit from all lenders because it fills the leverage-cycle/excessive-credit monitoring gap and pressure-tests BIS five-dimension series keys without ingesting unrelated credit measures.
- Provider structure investigation found dataflow `WS_CREDIT_GAP` v1.0 with series-key dimensions `FREQ`, `BORROWERS_CTY`, `TC_BORROWERS`, `TC_LENDERS`, `CG_DTYPE`; `BORROWERS_CTY` is the territory dimension, `TC_BORROWERS` and `TC_LENDERS` are sector dimensions, and `CG_DTYPE` is the credit-gap measure dimension.
- Frozen candidate universe: 43 accepted territories, 43 exact provider-advertised series, selected dimensions `Q/P/A/C`, 64 quarters from 2010-Q1 through 2025-Q4, 2,752 candidate cells, and `XM` Euro area aggregate excluded.
- Preserved request URL/parameters, raw SDMX XML, raw HTTP/acquisition metadata, SDMX header/dataset metadata, normalized artifact, manifest, reports, checksums, and load SQL.
- Loaded canonical PostgreSQL facts through source `BIS_PUBLIC_SDMX_API`, provider dataset `BIS:WS_CREDIT_GAP`, snapshot/as-of key `bis-ws-credit-gap-snapshot-prepared-20260712t162752z`, run key `task-215-bis-credit-gap-phase2`.
- Snapshot/as-of identity is derived from BIS SDMX `Prepared` timestamp and is not an official BIS publication release.
- Canonical credit-gap indicator identity removes only territory and preserves borrower sector, lender sector, measure, unit, and frequency:
  - `BIS:WS_CREDIT_GAP:CREDIT_TO_GDP_GAP_ACTUAL_MINUS_TREND:PRIVATE_NONFINANCIAL_SECTOR:ALL_SECTORS:PERCENTAGE_POINTS:Q`

## Verification snapshot

- Loaded facts: 2,752; provider-valued: 2,752; explicit-missing: 0.
- PostgreSQL verification: staging/facts 2,752/2,752; observed/missing 2,752/0; indicators/territories/periods 1/43/64; failed quality 0; duplicate canonical-key groups 0.
- Same-run idempotence rerun: zero repository growth; repository total fact count after TASK-215: 10,605,067.
- Net fact growth relative to completed TASK-214 baseline: +2,752 facts.
- Later-snapshot coexistence simulation inserted one hypothetical later snapshot in a transaction and rolled back.
- Focused TASK-215 + BIS/TASK-213/TASK-214 compatibility tests: `32 passed in 0.57s`.
- Artifact/checksum reconciliation: `checksum_entries=10 checksum_failures=[]`.
- Final full suite/governance verification is recorded in `context/latest_handoff.md`.
- Prediction-quality verdict: Accurate.

## Architecture verdict

Reaffirmed. The existing scalar substrate preserved BIS credit-gap semantics because each complete provider series key can become a stable source-scoped scalar indicator after removing only territory. `TC_BORROWERS`, `TC_LENDERS`, `CG_DTYPE`, unit, and frequency participate in indicator identity; provider-native dimensions and attributes are preserved in attributes/source payload.

TASK-215 extracted a narrow BIS-specific helper substrate in `src/macroforge/bis_sdmx.py` based on repeated evidence across TASK-057, TASK-213, TASK-214, and TASK-215. The extraction is intentionally limited to stable BIS evidence-handling responsibilities and does not create a universal SDMX adapter, generic provider framework, universal campaign engine, generic financial ontology, or speculative multidimensional schema.

## Guardrails

TASK-208 BLS, TASK-209/TASK-211 WEO, completed TASK-213/TASK-214 published files, FRED-detour files, and unrelated working-tree changes must not be reopened or included except narrowly required shared BIS compatibility work. Do not begin another ingestion campaign. Do not stage, commit, clean, restore, delete, or push without explicit authorization.
