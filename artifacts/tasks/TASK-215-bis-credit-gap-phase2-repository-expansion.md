# TASK-215 — BIS credit-to-GDP-gap Phase 2 repository expansion

Status: completed

## Objective

Implement a coherent cross-country BIS credit-to-GDP-gap capability for leverage-cycle monitoring, excessive-credit detection, financial-vulnerability assessment, and monetary-transmission analysis.

The task also made the mandatory evidence-based decision about whether repeated BIS implementation evidence across TASK-057, TASK-213, TASK-214, and TASK-215 justifies a narrow shared BIS substrate.

## Provider structure investigated before freezing scope

Provider dataflow:

- Source: `BIS_PUBLIC_SDMX_API`
- Provider dataset: `BIS:WS_CREDIT_GAP`
- BIS dataflow: `WS_CREDIT_GAP`
- Dataflow version: `1.0`
- API endpoint family: BIS SDMX v2 data API
- Series-key dimensions: `FREQ`, `BORROWERS_CTY`, `TC_BORROWERS`, `TC_LENDERS`, `CG_DTYPE`
- Territory dimension: `BORROWERS_CTY`
- Borrower-sector dimension: `TC_BORROWERS`
- Lender-sector dimension: `TC_LENDERS`
- Measure dimension: `CG_DTYPE`
- Selected frequency: quarterly `Q`
- Selected unit: percentage points (`UNIT_MEASURE=770`, `UNIT_MULT=0`)
- Available provider entities observed: 44 areas/entities
- Provider aggregate excluded: `XM` Euro area aggregate
- Provider series count observed across all `CG_DTYPE` values: 132
- Temporal coverage observed across provider response: 1947-Q4 through 2025-Q4

The dimensions do not match either WS_CBPOL or WS_DSR. The campaign therefore kept dataflow-specific semantics task-local while extracting only stable BIS evidence-handling helpers.

## Frozen candidate universe

Frozen before value acquisition in:

- `artifacts/reports/task-215-bis-credit-gap-frozen-pre-execution-prediction.json`

Selected capability:

- Quarterly credit-to-GDP gap for private non-financial sector credit from all lenders.

Selection:

- `FREQ=Q`
- `TC_BORROWERS=P` private non-financial sector
- `TC_LENDERS=A` all sectors
- `CG_DTYPE=C` credit-to-GDP gap actual minus trend
- Periods: 2010-Q1 through 2025-Q4
- Candidate periods: 64
- Accepted territories: 43
- Candidate provider-advertised series: 43
- Candidate cells: 2,752

Excluded:

- `XM` Euro area aggregate, classified as provider aggregate selection exclusion.

## Frozen prediction

Prediction quality verdict: Accurate.

Predicted:

- Candidate cells: 2,752
- Provider-valued facts: 2,752
- Explicit-missing facts: 0
- Aggregate exclusions: 1
- Unsupported entities: 0
- Mapping failures: 0
- Incompatible series: 0
- Acquisition errors: 0
- Expected PostgreSQL fact growth: 2,752
- Expected scalar compatibility: compatible if only `BORROWERS_CTY` is removed and `Q/P/A/C`, unit, and frequency remain in indicator identity.

Actual:

- Candidate cells: 2,752
- Provider-valued facts: 2,752
- Explicit-missing facts: 0
- Aggregate exclusions: 1
- Mapping failures: 0
- Incompatible series: 0
- Acquisition errors: 0

## Canonical identities

- Source: `BIS_PUBLIC_SDMX_API`
- Dataset: `BIS:WS_CREDIT_GAP`
- Snapshot/as-of: `bis-ws-credit-gap-snapshot-prepared-20260712t162752z`
- Run: `task-215-bis-credit-gap-phase2`
- Snapshot meaning: acquired BIS SDMX response identity derived from provider `Prepared`; not an official publication release and not query-window identity.

Canonical indicator:

- `BIS:WS_CREDIT_GAP:CREDIT_TO_GDP_GAP_ACTUAL_MINUS_TREND:PRIVATE_NONFINANCIAL_SECTOR:ALL_SECTORS:PERCENTAGE_POINTS:Q`

Territory is excluded from indicator identity. Material non-territory dimensions are preserved in the source-scoped indicator identity and row attributes/source payload.

## Artifacts

Raw active evidence:

- `data/raw/task215_bis_credit_gap_phase2_campaign/active/task-215-bis-credit-gap-2010q1-2025q4-raw.xml`
- `data/raw/task215_bis_credit_gap_phase2_campaign/active/task-215-bis-credit-gap-2010q1-2025q4-raw-metadata.json`

Processed active evidence:

- `data/processed/task215_bis_credit_gap_phase2_campaign/active/task-215-bis-credit-gap-normalized.json`
- `data/processed/task215_bis_credit_gap_phase2_campaign/active/task-215-bis-credit-gap-manifest.json`

Reports:

- `artifacts/reports/task-215-bis-credit-gap-artifact-checksums.txt`
- `artifacts/reports/task-215-bis-credit-gap-frozen-pre-execution-prediction.json`
- `artifacts/reports/task-215-bis-credit-gap-load.sql`
- `artifacts/reports/task-215-bis-credit-gap-postgresql-load-report.json`
- `artifacts/reports/task-215-bis-credit-gap-prediction-evaluation.json`
- `artifacts/reports/task-215-bis-credit-gap-provider-structure-and-evidence-report.json`
- `artifacts/reports/task-215-bis-substrate-extraction-decision.json`

## PostgreSQL results

First promotion:

- Staging rows: 2,752
- Fact rows: 2,752
- Observed facts: 2,752
- Explicit-missing facts: 0
- Indicators: 1
- Territories: 43
- Periods: 64
- Lineage events: 2
- Quality checks: 4
- Failed quality checks: 0
- Duplicate canonical-key groups: 0
- Later-snapshot coexistence simulation rows: 1
- Fact growth over TASK-214 baseline: 2,752
- Repository facts after load: 10,605,067

Same-run idempotent reload:

- Repository growth: 0 facts

## BIS substrate extraction decision

Decision: extract a narrow BIS-specific substrate.

Implemented boundary:

- `src/macroforge/bis_sdmx.py`

Extracted only stable repeated BIS responsibilities:

- canonical BIS public API source constants;
- Prepared-derived acquired-response snapshot key construction, now narrowed to reject missing or malformed `Prepared` evidence rather than falling back to speculative raw-checksum snapshot keys;
- SDMX Header/DataSet metadata extraction;
- attempt-specific raw evidence acquisition plus atomic active raw promotion;
- quarterly period helper;
- series-key helper that removes only the territory dimension;
- common hashing/path helpers.

Evidence base:

- TASK-057: bounded WS_CBPOL proof exposed BIS source/release/territory/series-key concerns.
- TASK-213: scaled WS_CBPOL corrected country-encoded indicator identity and Hong Kong exclusion risk.
- TASK-214: WS_DSR confirmed Prepared-derived snapshot identity and territory-removal indicator rule across a different BIS dimension pattern.
- TASK-215: WS_CREDIT_GAP confirmed the same stable invariants with a five-dimension series key while preserving dataflow-specific semantics task-local.

Rejected explicitly:

- universal SDMX adapter;
- generic provider framework;
- universal campaign engine;
- generic financial ontology;
- speculative multidimensional schema.

## Architecture verdict

Reaffirmed.

The existing scalar fact substrate is compatible with the selected BIS credit-gap capability because each provider series is a quarterly percentage-point scalar after removing only territory and retaining `TC_BORROWERS`, `TC_LENDERS`, `CG_DTYPE`, unit, and frequency in indicator identity/semantics.

No architecture reopening is required.

## Verification

Completed focused verification:

- Dedicated BIS substrate tests: `PYTHONPATH=src:. uvx pytest -q tests/test_bis_sdmx.py`
- Result: 15 passed.
- TASK-215 + BIS/TASK-213/TASK-214 compatibility: `PYTHONPATH=src:. uvx pytest -q tests/test_task215_bis_credit_gap_phase2_campaign.py tests/test_task214_bis_dsr_credit_cycle_phase2_campaign.py tests/test_bis_cbpol.py tests/test_task213_bis_cbpol_policy_rate_phase2_campaign.py tests/test_task213_bis_cbpol_metadata_cleanup.py`
- Result: 32 passed.

Artifact/DB verification completed:

- JSON/checksum validation: `json_validated=8 checksum_entries=10 checksum_mismatches=0`;
- candidate reconciliation: 2,752 rows;
- source/dataset/snapshot verification: passed;
- staging/fact agreement: passed;
- observed/missing/indicator/territory/period counts: 2,752 / 0 / 1 / 43 / 64;
- failed quality checks: 0;
- idempotence: same-run growth 0;
- later-snapshot coexistence: passed;
- duplicate canonical-key groups: 0;
- repository facts: 10,605,067.

Full-suite and final governance verification:

- Full suite: `830 passed in 805.95s (0:13:25)`.
- Coherence: 0 blocks, 0 warnings.
- Context health: 0 blocks, 0 warnings.
- Architecture-reality audit: 0 blocks, 0 warnings.
- `git diff --check`: clean.

## Scope protection

No staging, commit, push, clean, restore, move, or delete was performed.

Completed BLS, WEO, TASK-213, TASK-214, FRED-detour, trade, company, financial-asset, and unrelated working-tree files were not modified except for the intentional shared BIS helper extraction and normal project state/summary closeout files.
