# Project State

## Current status

TASK-217 IMF IIP Phase 2 external-position stock repository expansion is implemented, locally verified, and unpublished. Focused verification, JSON/checksum validation, PostgreSQL verification, same-run idempotence, later-as-of coexistence simulation, and task/state closeout updates are complete.

Do not stage, commit, push, clean, restore, delete, or move files without explicit authorization.

## Recent completed work

- TASK-216 IMF BOP Phase 2 current-account expansion was completed, committed, and pushed as `d27d3acd72bbf73a8099b416d14865c96cd4c286` with local HEAD equal to `origin/main`; its 40-file publication set is durable.
- TASK-217 was selected from the active backlog after inspecting state, handoff, backlog, capability atlas, recent reports, PostgreSQL coverage, and working-tree status. It outranked another BOP/BIS/WDI/cleanup task because broad IMF IIP stock positions close a first-order external-sector balance-sheet gap and complement TASK-216 current-account flows using already proven IMF SDMX boundaries.
- Provider structure investigation found IMF external SDMX 2.1 IIP dataflow `IIP` v13.0.0 / DSD_BOP v24.0.0 with selected series-key dimensions `COUNTRY`, `BOP_ACCOUNTING_ENTRY`, `INDICATOR`, `UNIT`, `FREQUENCY`. Territory is `COUNTRY`; material non-territory dimensions are preserved in indicator identity/attributes.
- Frozen candidate universe: 214 accepted canonical countries, 3 selected position series (`A_P.IIP`, `L_P.IIP`, `NETAL_P.NIIP`), annual frequency, USD scale 6, 2010-2024, 642 exact provider-advertised series, 9,630 expected cells.
- Preserved request URLs/parameters, metadata response, raw SDMX XML chunks, raw HTTP/acquisition metadata, response headers, timestamps, checksums, normalized artifact, manifest, reports, and load SQL.
- Loaded canonical PostgreSQL facts through source `IMF_SDMX_IIP_API_V1`, provider dataset `IMF:IIP`, as-of key `imf-iip-asof-20260711t233032958933600z`, run key `task-217-imf-iip-external-position-phase2`.
- Actual TASK-217 result: 7,695 loaded facts = 6,969 provider-valued + 726 explicit-missing; 129 whole-series absences (1,935 candidate cells); 0 acquisition errors; 0 incompatible series.

TASK-215 BIS credit-to-GDP-gap Phase 2 remains unpublished/uncommitted outside the TASK-217 boundary; do not mix publication boundaries unless explicitly authorized.

## Verification snapshot

TASK-217 completed verification so far:

- Focused TASK-217 + existing IMF IIP/BOP compatibility tests: `37 passed in 18.78s`.
- JSON/checksum reconciliation: `checksum_entries=29 checksum_mismatches=0 json_validated=6`.
- PostgreSQL verification: source/release/staging/facts/observed/missing/indicators/territories/periods/failed-quality/duplicate-groups/total-repository-facts = `1|1|7695|7695|6969|726|3|171|15|0|0|10627237`.
- Same-run idempotence: second load growth 0 and facts remained 7,695.
- Later-as-of coexistence: simulated release key `imf-iip-asof-simulated-later-snapshot-task217` coexists with active IIP as-of key inside rollback (`coexistence|2`).
- Prediction-quality verdict: Mixed; scale/cell count was exact, but provider-valued facts were lower and whole-series absences higher than expected.

## Architecture verdict

TASK-217 reaffirms current architecture. The existing scalar/revision-aware substrate preserved IIP as-of evidence, source/dataset/run separation, unit semantics, annual periods, explicit-missing facts, lineage/quality evidence, duplicate prevention, and idempotent loads. No canonical ambiguity, repository-class mismatch, release/vintage loss, provider-semantics loss, scaling failure, or repeated operational friction justified schema redesign.

No IMF-IIP shared substrate was extracted. Revisit only after another source-specific external-sector campaign demonstrates stable repeated contracts and measurable future-risk reduction without freezing older campaign-specific identity drift.

## Guardrails

Do not reopen BIS, BLS, WEO, FRED-detour files, completed campaigns, trade, companies, or financial assets. Do not stage, commit, clean, restore, delete, move, or push without explicit authorization. Preserve unrelated working-tree changes.
