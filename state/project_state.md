# Project State

## Current status

TASK-214 BIS DSR credit-cycle Phase 2 repository expansion is complete and uncommitted. Do not stage, commit, push, clean, restore, delete, or move files without explicit authorization.

TASK-213 BIS WS_CBPOL policy-rate Phase 2 expansion was previously published to `origin/main` in commit `abc42f6d1d57c8af8981e150a269991647637a5a`.

## Recent completed work

- TASK-214 selected BIS quarterly debt-service ratios (`BIS:WS_DSR`) over credit-to-GDP gaps because DSR fills the Repository Atlas debt-service burden gap and better pressure-tests borrower-sector dimensional semantics.
- Frozen candidate universe: 32 accepted non-aggregate territories, 66 exact provider-advertised country-sector series, 3 borrower sectors (`H`, `N`, `P`), 44 quarters from 2015-Q1 through 2025-Q4, 2,904 candidate cells.
- Preserved request URL/parameters, raw SDMX XML, raw HTTP/acquisition metadata, SDMX header/dataset metadata, normalized artifact, manifest, reports, checksums, and load SQL.
- Loaded canonical PostgreSQL facts through source `BIS_PUBLIC_SDMX_API`, provider dataset `BIS:WS_DSR`, snapshot/as-of key `bis-ws-dsr-snapshot-prepared-20260712t150728z`, run key `task-214-bis-dsr-credit-cycle-phase2`.
- Snapshot/as-of identity is derived from BIS SDMX `Prepared` timestamp and is not an official BIS publication release.
- Canonical DSR indicator identities remove only territory and preserve borrower sector, unit, and frequency:
  - `BIS:WS_DSR:DEBT_SERVICE_RATIO:HOUSEHOLDS_NPISHS:PERCENT:Q`
  - `BIS:WS_DSR:DEBT_SERVICE_RATIO:NONFINANCIAL_CORPORATIONS:PERCENT:Q`
  - `BIS:WS_DSR:DEBT_SERVICE_RATIO:PRIVATE_NONFINANCIAL_SECTOR:PERCENT:Q`

## Verification snapshot

- Loaded facts: 2,904; provider-valued: 2,904; explicit-missing: 0.
- PostgreSQL verification: staging/facts 2,904/2,904; observed/missing 2,904/0; indicators/territories/periods 3/32/44; failed quality 0; duplicate canonical-key groups 0.
- Same-run idempotence rerun: zero repository growth; repository total fact count after TASK-214: 10,602,315.
- Net fact growth relative to completed TASK-213 baseline: +2,904 facts.
- Later-snapshot coexistence simulation inserted one hypothetical later snapshot in a transaction and rolled back.
- Focused TASK-214 tests: `6 passed in 0.41s`.
- Focused TASK-214 + BIS/TASK-213 compatibility tests: `25 passed in 0.58s`.
- Full suite: `808 passed in 870.73s (0:14:30)`.
- JSON/checksum reconciliation: `json_validated=7 checksum_entries=9 checksum_mismatches=0`.
- Governance: coherence `0 block(s), 0 warning(s)`; context health `0 block(s), 0 warning(s)`; architecture-reality audit `0 block(s), 0 warning(s)`; `git diff --check` exit `0`.
- Prediction-quality verdict: Accurate.

## Architecture verdict

Reaffirmed. The existing scalar substrate preserved BIS DSR semantics because each complete provider series key can become a stable source-scoped scalar indicator after removing only territory. `DSR_BORROWERS`, unit, and frequency participate in indicator identity; provider-native dimensions and attributes are preserved in attributes/source payload.

No BIS substrate extraction was implemented. TASK-057, TASK-213, and TASK-214 show repeated BIS source/snapshot/series-key responsibilities, but the stable cross-dataflow contract is not yet proven enough to justify even a narrow shared BIS substrate.

## Guardrails

TASK-208 BLS, TASK-209/TASK-211 WEO, TASK-213 published files, FRED-detour files, and unrelated working-tree changes must not be reopened or included. Do not begin another ingestion campaign. Do not stage, commit, clean, restore, delete, or push without explicit authorization.
