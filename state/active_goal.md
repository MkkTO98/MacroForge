# Active Goal

Current active task: TASK-215 BIS credit-to-GDP-gap Phase 2 repository expansion.

Status: Completed; do not stage, commit, push, clean, restore, delete, or move files without explicit authorization.

## Completed outcome

TASK-215 implemented a coherent BIS quarterly credit-to-GDP-gap capability for leverage-cycle monitoring, excessive-credit detection, financial-vulnerability assessment, and monetary-transmission analysis.

Implemented capability:

- Source: `BIS_PUBLIC_SDMX_API`
- Dataset: `BIS:WS_CREDIT_GAP`
- Snapshot/as-of: `bis-ws-credit-gap-snapshot-prepared-20260712t162752z`
- Snapshot meaning: acquired BIS SDMX response snapshot from provider `Prepared`, not official BIS publication release.
- Run: `task-215-bis-credit-gap-phase2`
- Frequency: quarterly
- Periods: 2010-Q1 through 2025-Q4
- Candidate series: 43 exact provider-advertised private-nonfinancial-sector/all-lenders/credit-gap series
- Candidate cells: 2,752
- Loaded facts: 2,752
- Provider-valued facts: 2,752
- Explicit missing: 0
- Territories: 43 accepted territories
- Aggregate exclusions: `XM` Euro area aggregate
- Canonical credit-gap indicators: 1 source-scoped percentage-point indicator
- Acquisition errors: 0
- Incompatible series: 0
- Duplicate canonical-key groups: 0
- Failed quality checks: 0
- Same-run idempotence growth: 0
- Later-snapshot coexistence simulation rows: 1
- Repository total after task: 10,605,067 curated facts
- Net fact growth relative to completed TASK-214 baseline: +2,752 facts

## Architecture verdict

Reaffirmed. The scalar substrate preserved BIS credit-gap semantics because each selected complete provider series key became a stable source-scoped scalar indicator after removing only territory. `TC_BORROWERS=P`, `TC_LENDERS=A`, `CG_DTYPE=C`, unit, and frequency remain in indicator identity and row semantics; provider-native dimensions/attributes remain in attributes/source payload.

TASK-215 extracted a narrow BIS-specific helper substrate in `src/macroforge/bis_sdmx.py` after repeated evidence from TASK-057, TASK-213, TASK-214, and TASK-215. The extraction is limited to BIS source constants, Prepared-derived acquired snapshot keys, SDMX response metadata, attempt/raw publication invariants, quarterly periods, series-key territory-removal helpers, and hash/path helpers. It is not a universal SDMX adapter, generic provider framework, campaign engine, financial ontology, or multidimensional schema.

## Verification snapshot

- Focused TASK-215 + BIS/TASK-213/TASK-214 compatibility tests: `32 passed in 0.57s`.
- Artifact/checksum reconciliation: `checksum_entries=10 checksum_failures=[]`.
- PostgreSQL verification: staging/facts 2,752/2,752; observed/missing 2,752/0; indicators/territories/periods 1/43/64; failed quality 0; duplicate canonical-key groups 0; repository facts 10,605,067.
- Same-run idempotence rerun: zero repository growth.
- Later-snapshot coexistence simulation: 1 row inserted in rollback transaction.
- Final full suite and governance verification are recorded in `context/latest_handoff.md`.

## Scope protection

Do not touch completed TASK-208, TASK-209/TASK-211 WEO, TASK-213/TASK-214 published files, FRED-detour files, or unrelated working-tree paths except explicitly authorized shared BIS compatibility work. Do not stage, commit, push, clean, restore, delete, or move files without explicit authorization.
