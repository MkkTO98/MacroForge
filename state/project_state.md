# Project State

## Current status

TASK-216 IMF BOP Phase 2 current-account repository expansion is complete, verified, and uncommitted. Focused verification, full suite, JSON/checksum validation, PostgreSQL verification, same-run idempotence, later-snapshot coexistence, and governance closeout are complete.

Do not stage, commit, push, clean, restore, delete, or move files without explicit authorization.

## Recent completed work

- TASK-216 selected IMF BOP annual current-account monitoring rather than another BIS campaign or small proof because it fills a first-order external-sector capability gap and complements existing BOP financial-account/IIP/reserves/WDI external evidence.
- Provider structure investigation found IMF external SDMX 2.1 BOP dataflow `BOP` v21.0.0 / DSD v24.0.0 with selected series-key dimensions `COUNTRY`, `BOP_ACCOUNTING_ENTRY`, `INDICATOR`, `UNIT`, `FREQUENCY`. Territory is `COUNTRY`; material non-territory dimensions are preserved in indicator identity/attributes.
- Frozen candidate universe: 214 accepted canonical countries, 5 current-account components (`CAB`, `G`, `S`, `IN1`, `IN2`), annual frequency, USD scale 6, 2010-2024, 1,070 exact provider-advertised series, 16,050 expected cells.
- Preserved request URLs/parameters, metadata response, raw SDMX XML chunks, raw HTTP/acquisition metadata, response headers, timestamps, checksums, normalized artifact, manifest, reports, and load SQL.
- Loaded canonical PostgreSQL facts through source `IMF_SDMX_BOP_API_V1`, provider dataset `IMF:BOP`, as-of key `imf-bop-asof-20260711t231424302015100z`, run key `task-216-imf-bop-current-account-phase2`.
- Actual result: 14,475 loaded facts = 13,600 provider-valued + 875 explicit-missing; 105 whole-series absences; 0 acquisition errors; 0 incompatible series.

TASK-215 BIS credit-to-GDP-gap Phase 2 was previously completed and remains uncommitted; do not mix TASK-215 publication boundary with TASK-216 unless explicitly authorized.

## Verification snapshot

TASK-216 completed verification:

- Focused TASK-216 + existing IMF BOP compatibility tests after closeout regressions: `32 passed in 4.19s`.
- Full suite: `838 passed in 828.83s (0:13:48)`.
- JSON/checksum reconciliation: `json_validated=6 checksum_entries=29 checksum_mismatches=0`.
- PostgreSQL verification: source/release/staging/facts/observed/missing/indicators/territories/periods/failed-quality/duplicate-groups/BOP-as-of-coexistence-rows = `1|1|14475|14475|13600|875|5|193|15|0|0|2`.
- Same-run idempotence: second load growth 0 and facts remained 14,475.
- Later-snapshot coexistence: simulated release key `imf-bop-asof-simulated-later-snapshot-task216` coexists with active BOP as-of key.
- Prediction-quality verdict: Mostly Accurate.
- Final context health, coherence, architecture-reality audit, and `git diff --check`: clean with 0 warnings.

## Architecture verdict

TASK-216 reaffirms current architecture. The existing scalar/revision-aware substrate preserved BOP as-of/release evidence, source/dataset/run separation, unit semantics, annual periods, explicit-missing facts, lineage/quality evidence, duplicate prevention, and idempotent loads. No canonical ambiguity, repository-class mismatch, release/vintage loss, provider-semantics loss, scaling failure, or repeated operational friction justified schema redesign.

No IMF-BOP shared substrate was extracted. Revisit only after another BOP/IIP relationship campaign confirms stable, source-specific responsibilities without freezing earlier campaign-specific identity drift.

## Guardrails

Do not reopen BIS, BLS, WEO, FRED-detour files, completed campaigns, trade, companies, or financial assets. Do not stage, commit, clean, restore, delete, move, or push without explicit authorization. Preserve unrelated working-tree changes.
