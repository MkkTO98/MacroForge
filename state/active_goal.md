# Active Goal

## Current active goal
No active implementation in progress.

## Most recent completed task
TASK-213 BIS WS_CBPOL central-bank policy-rate Phase 2 repository expansion, corrected and followed by bounded pre-publication obsolete-metadata cleanup.

## Outcome
TASK-213 now represents a corrected broad monthly monetary-policy repository capability: 37 accepted territories including HK/HKG, 138 monthly periods from 2015-M01 through 2026-M06, 5,106 loaded facts, 5,082 provider-valued observations, and 24 explicit-missing cells. `XM` is an aggregate selection exclusion, not a provider failure. Provider exclusions and acquisition errors are both 0.

Canonical indicator identity was corrected from territory-encoded `BIS:WS_CBPOL:M.<REF_AREA>` rows to one source-scoped indicator: `BIS:WS_CBPOL:CENTRAL_BANK_POLICY_RATE:PERCENT:M`. Territory identity now carries `REF_AREA` semantics, while country-specific title/source/compilation/status/confidentiality remain preserved as attributes/source payload.

Snapshot/release identity was corrected from query-window-derived `bis-ws-cbpol-current-snapshot-2015m01-2026m06` to provider-prepared snapshot key `bis-ws-cbpol-snapshot-prepared-20260712t114554z`. No BIS publication date was fabricated.

## Final verification snapshot
- Focused TASK-213 + TASK-057 BIS compatibility + cleanup invariant tests: `19 passed in 0.57s`.
- Full suite: `802 passed in 845.70s (0:14:05)`.
- PostgreSQL post-cleanup verification: staging/facts `5,106/5,106`; provider-valued/explicit-missing `5,082/24`; territories/periods `37/138`; HK facts `138`; failed quality checks `0`; duplicate canonical-key groups `0`.
- Source/dataset/snapshot verification after cleanup: canonical BIS source rows `1`; canonical snapshot rows `1`; obsolete window-bound snapshot rows `0`.
- Indicator verification after cleanup: canonical policy-rate indicator rows `1`; obsolete country-encoded indicators `0`.
- Same-run idempotence: repository growth `0`; repository total fact count unchanged at `10,599,411`.
- JSON/checksum reconciliation: `json_validated=9 checksum_entries=9 checksum_mismatches=0`.
- Governance: coherence `0 block(s), 0 warning(s)`; context health `0 block(s), 0 warning(s)`; architecture-reality audit `0 block(s), 0 warning(s)`; `git diff --check` exit `0`.
- Later-snapshot coexistence simulation: `later_snapshot_simulation_rows|1`, rolled back.

## Guardrails
TASK-208, TASK-209, TASK-211, BLS, WEO, and FRED-detour files were not reopened. TASK-213 is not staged, committed, or pushed. The working tree still contains unrelated pre-existing changes; preserve them and stage only the bounded TASK-213 set if publication is later authorized.
