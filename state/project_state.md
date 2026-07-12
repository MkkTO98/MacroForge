# Project State

## Current status
No active implementation in progress. TASK-213 BIS WS_CBPOL central-bank policy-rate Phase 2 repository expansion is complete, corrected, verified, and followed by authorized bounded obsolete-metadata cleanup; it is not staged/committed/pushed.

## Recent completed work
- TASK-213 selected the already proven BIS WS_CBPOL path as the next Phase 2 diverse-source macroeconomic enrichment campaign.
- Corrected candidate universe: 37 accepted BIS territory reference areas including HK/HKG, monthly periods 2015-M01 through 2026-M06, one central-bank policy-rate measure, 5,106 candidate cells.
- Corrected entity accounting: `XM` is an aggregate selection exclusion; unsupported entities, mapping failures, provider exclusions, and acquisition errors are all 0.
- Preserved provider request URL/parameters, raw SDMX XML, raw HTTP/acquisition metadata, provider header/dataset metadata, normalized artifact, manifest, reports, checksums, and load SQL.
- Loaded canonical PostgreSQL facts through source `BIS_PUBLIC_SDMX_API`, provider dataset `BIS:WS_CBPOL`, snapshot/release key `bis-ws-cbpol-snapshot-prepared-20260712t114554z`, run key `task-213-bis-cbpol-policy-rate-phase2`.
- Corrected canonical indicator identity to one source-scoped indicator independent of territory: `BIS:WS_CBPOL:CENTRAL_BANK_POLICY_RATE:PERCENT:M`.

## Verification snapshot
- Loaded facts: 5,106; provider-valued: 5,082; explicit-missing: 24.
- PostgreSQL post-cleanup verification: staging/facts 5,106/5,106; observed/missing 5,082/24; indicators/territories/periods 1/37/138; HK facts 138; failed quality 0; duplicate canonical-key groups 0.
- Same-run idempotence rerun: zero repository growth; repository total fact count unchanged at 10,599,411.
- Later-snapshot coexistence simulation inserted one hypothetical later snapshot in a transaction and rolled back.
- Focused TASK-213 plus TASK-057 BIS compatibility plus cleanup invariant tests: `19 passed in 0.57s`.
- Full suite: `802 passed in 845.70s (0:14:05)`.
- JSON/checksum reconciliation: `json_validated=9 checksum_entries=9 checksum_mismatches=0`.
- Governance: coherence `0 block(s), 0 warning(s)`; context health `0 block(s), 0 warning(s)`; architecture-reality audit `0 block(s), 0 warning(s)`; `git diff --check` exit `0`.
- Prediction-quality verdict after correction: Mixed, because scale/provider behavior were close but identity modelling and Hong Kong selection were wrong.

## Metadata cleanup note
Authorized bounded pre-publication cleanup was completed after the full reference audit passed:
- legacy window-bound release row: deleted exactly 1 row after 0 external `dataset_release_id` references across discovered relations.
- legacy country-encoded indicators: deleted exactly 36 rows after 0 external `indicator_id` references and 0 exact-code references outside `curated.dim_indicator`.
- canonical BIS source, canonical `BIS:WS_CBPOL` snapshot, canonical policy-rate indicator, TASK-213 staging/facts, lineage, quality, and run records remain preserved.

## Guardrails
TASK-208 BLS, TASK-209/TASK-211 WEO, BLS, WEO, FRED-detour files, and unrelated working-tree changes must not be reopened or included. Do not stage, commit, clean, restore, delete, or push without explicit authorization.
