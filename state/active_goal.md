# Active Goal

Current active task: TASK-216 IMF BOP Phase 2 current-account repository expansion.

Status: Complete and verified; uncommitted. Do not stage, commit, push, clean, restore, delete, or move files without explicit authorization.

## Completed outcome

TASK-216 scaled the previously proven bounded IMF BOP path into a broad annual current-account monitoring capability.

Implemented capability:

- Source: `IMF_SDMX_BOP_API_V1`
- Provider dataset: `IMF:BOP`
- Dataflow/Data structure: `BOP` v21.0.0 / DSD v24.0.0
- Provider-derived as-of/release key: `imf-bop-asof-20260711t231424302015100z`
- Run: `task-216-imf-bop-current-account-phase2`
- Frequency: annual
- Periods: 2010 through 2024
- Accounting entry: `NETCD_T` = net credit less debit
- Unit/scale: `USD_SCALE_6` = US dollars, millions
- Selected components: CAB, goods, services, primary income, secondary income
- Accepted territories frozen before values: 214 canonical countries
- Exact provider-advertised series: 1,070
- Candidate cells: 16,050
- Loaded facts: 14,475
- Provider-valued facts: 13,600
- Explicit missing facts: 875
- Whole-series absences: 105 series / 1,575 candidate cells
- Acquisition errors: 0
- Incompatible series: 0
- Duplicate canonical-key groups: 0
- Failed quality checks: 0
- Same-run idempotence growth: 0
- Simulated later-snapshot coexistence: verified

## Architecture verdict

Reaffirmed. The selected IMF BOP current-account family fits the existing scalar/revision-aware substrate because each complete provider series key becomes a stable source-scoped scalar indicator after removing only territory while preserving accounting entry, component, unit, scale, frequency, provider attributes, and as-of evidence.

No IMF-BOP shared substrate was extracted. Repeated BOP mechanics exist, but earlier bounded BOP implementations used campaign-specific identity conventions; extracting now would risk freezing drift. Revisit only after one more BOP/IIP relationship campaign confirms stable responsibilities.

## Verification snapshot

- Focused TASK-216 + existing IMF BOP compatibility tests after closeout regressions: `32 passed in 4.19s`.
- Full suite: `838 passed in 828.83s (0:13:48)`.
- JSON/checksum reconciliation: `json_validated=6 checksum_entries=29 checksum_mismatches=0`.
- PostgreSQL verification tuple: `1|1|14475|14475|13600|875|5|193|15|0|0|2` = source/release/staging/facts/observed/missing/indicators/territories/periods/failed-quality/duplicate-groups/BOP-as-of-coexistence-rows.
- Final context health, coherence, architecture-reality audit, and `git diff --check`: clean with 0 warnings.

## Scope protection

Do not touch BIS, BLS, WEO, FRED-detour, completed campaigns, trade, company, financial-asset, or unrelated working-tree files. Do not stage, commit, push, clean, restore, delete, or move files without explicit authorization.
