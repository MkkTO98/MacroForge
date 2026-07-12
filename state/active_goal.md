# Active Goal

Current active task: TASK-217 IMF IIP Phase 2 external-position stock repository expansion.

Status: Implemented and locally verified; unpublished. Do not stage, commit, push, clean, restore, delete, or move files without explicit authorization.

## Selection outcome

After the completed and published TASK-216 IMF BOP current-account expansion, the active backlog was re-entered using project state, capability evidence, recent reports, PostgreSQL coverage, and existing implementation confidence. TASK-217 was selected over additional BOP, BIS, WDI, cleanup, or architecture work because broad IMF IIP external-position stocks close a larger external-sector balance-sheet gap, complement TASK-216 current-account flows, and reuse proven IMF SDMX scalar/revision-aware boundaries without architectural novelty.

## Implemented outcome

TASK-217 scaled the previously bounded IMF IIP position-stock path into a broad annual external-position stock monitoring capability.

Implemented capability:

- Source: `IMF_SDMX_IIP_API_V1`
- Provider dataset: `IMF:IIP`
- Dataflow/Data structure: `IIP` v13.0.0 / DSD_BOP v24.0.0
- Provider-derived as-of key: `imf-iip-asof-20260711t233032958933600z`
- Run: `task-217-imf-iip-external-position-phase2`
- Frequency: annual
- Periods: 2010 through 2024
- Unit/scale: `USD_SCALE_6` = US dollars, millions
- Selected position series:
  - `A_P.IIP` external asset positions
  - `L_P.IIP` external liability positions
  - `NETAL_P.NIIP` net international investment position
- Accepted territories frozen before values: 214 canonical countries
- Exact provider-advertised series: 642
- Candidate cells: 9,630
- Loaded facts: 7,695
- Provider-valued facts: 6,969
- Explicit missing facts: 726
- Whole-series absences: 129 series / 1,935 candidate cells
- Acquisition errors: 0
- Incompatible series: 0
- Duplicate canonical-key groups: 0
- Failed quality checks: 0
- Same-run idempotence growth: 0
- Simulated later-as-of coexistence: verified

## Architecture verdict

Reaffirmed. The selected IMF IIP stock-position family fits the existing scalar/revision-aware substrate because each complete provider series key becomes a stable source-scoped scalar indicator after removing only territory while preserving accounting entry, position measure, unit, scale, frequency, provider attributes, and provider-derived as-of evidence.

No IMF-IIP shared substrate was extracted. Repeated IMF SDMX mechanics are visible across TASK-216 and TASK-217, but extraction would still risk freezing task-local identity drift from older bounded implementations. Keep architecture frozen and revisit only after another source-specific external-sector campaign demonstrates stable repeated contracts and measurable future-risk reduction.

## Verification snapshot

- Focused TASK-217 + IMF IIP/BOP compatibility tests: `37 passed in 18.78s`.
- JSON/checksum reconciliation: `checksum_entries=29 checksum_mismatches=0 json_validated=6`.
- PostgreSQL verification tuple: `1|1|7695|7695|6969|726|3|171|15|0|0|10627237` = source/release/staging/facts/observed/missing/indicators/territories/periods/failed-quality/duplicate-groups/total repository facts.
- Same-run idempotence report: second load growth `0` with 7,695 run-scoped facts.
- Later-as-of coexistence simulation: `coexistence|2` inside rollback.

## Scope protection

Unrelated pre-existing working-tree changes remain outside TASK-217 and must be preserved untouched. Do not touch BIS, BLS, WEO, FRED-detour, completed campaigns, trade, company, financial-asset, or unrelated working-tree files. Do not stage, commit, push, clean, restore, delete, or move files without explicit authorization.
