# TASK-207 — Phase 2 Diverse-Source BLS U.S. Monthly Labor Campaign

Status: complete
Date: 2026-07-10
Type: Phase 2 diverse-source macroeconomic repository expansion / BLS monthly scalar campaign

## Objective

Begin MacroForge Phase 2 with one substantive diverse-source macroeconomic repository-expansion campaign after accepting that bulk WDI annual-scalar Phase 1 is no longer the default.

Preserved boundaries:

- No trade, company, or financial-asset construction.
- No residual WDI campaign scheduling.
- No new prioritization framework, scoring system, source taxonomy, or orchestration layer.
- No canonical redesign.
- Source-specific normalization and loading only.

## Selection

Selected source: BLS public API v2.

Selected domain: U.S. monthly labor-market level, rate, payroll, wage, hours, and labor-demand indicators.

Selected capability: timely U.S. labor-market monitoring at monthly frequency, materially different from WDI annual country-year coverage.

Why strongest Phase 2 execution target:

- Adds higher-frequency observations absent from the existing WDI annual-scalar repository.
- Uses an already proven bounded source family: BLS labor core, payroll, wages/hours, and JOLTS slices already existed as bounded source-specific implementations.
- Expands an accepted source-specific path into a substantive repository campaign rather than choosing novelty for architectural variety.
- Exercises existing monthly scalar canonical substrate without forcing revision, trade, company, asset, or unfamiliar dimensional semantics.

## Frozen pre-execution prediction

Artifact: `artifacts/reports/task-207-bls-us-labor-monthly-frozen-selection-prediction.json`

Prediction summary:

- Selected source/domain: BLS public API v2 / U.S. monthly labor market.
- Expected capability gain: timely monthly U.S. labor monitoring not supplied by WDI annual coverage.
- Expected repository class: source-specific monthly scalar time-series observations in the existing curated fact substrate.
- Expected scale: approximately 1,900-2,050 observations, allowing BLS availability variation.
- Principal provider risks: unregistered BLS API 10-year limit, current-year edge availability, provider warning messages.
- Expected friction: low to moderate; chunked live acquisition and source-specific loader required, but no framework redesign expected.
- Existing architecture predicted to suffice: yes.

The prediction was frozen before executing the BLS campaign.

## Candidate / release / series scope

Provider endpoint: `https://api.bls.gov/publicAPI/v2/timeseries/data/`

Acquisition windows:

- 2010-2019
- 2020-2026

Requested series: 12

- `LNS14000000` — unemployment rate
- `LNS11300000` — labor force participation rate
- `LNS12000000` — civilian employment level
- `LNS11000000` — civilian labor force level
- `LNS12300060` — employment-population ratio
- `LNS13000000` — unemployment level
- `CES0000000001` — all employees, total nonfarm
- `CES0500000001` — all employees, total private
- `CES0500000003` — average hourly earnings, total private
- `CES0500000002` — average weekly hours, total private
- `JTS000000000000000JOL` — job openings, total nonfarm
- `JTS000000000000000HIR` — hires, total nonfarm

## Artifacts

Raw provider evidence:

- `data/raw/task207_bls_us_labor_monthly_phase2_campaign/task-207-bls-us-labor-monthly-2010-2026.json`
- chunk artifacts under `data/raw/task207_bls_us_labor_monthly_phase2_campaign/`

Normalized evidence:

- `data/processed/task207_bls_us_labor_monthly_phase2_campaign/task-207-bls-us-labor-monthly-normalized.json`
- `data/processed/task207_bls_us_labor_monthly_phase2_campaign/task-207-bls-us-labor-monthly-manifest.json`

Reports:

- `artifacts/reports/task-207-bls-us-labor-monthly-frozen-selection-prediction.json`
- `artifacts/reports/task-207-bls-us-labor-monthly-provider-evidence-report.json`
- `artifacts/reports/task-207-bls-us-labor-monthly-postgresql-load-report.json`
- `artifacts/reports/task-207-bls-us-labor-monthly-prediction-evaluation.json`
- `artifacts/reports/task-207-bls-us-labor-monthly-artifact-checksums.txt`

Implementation and tests:

- `tools/task207_bls_us_labor_monthly_phase2_campaign.py`
- `tests/test_task207_bls_us_labor_monthly_phase2_campaign.py`

## Results

Candidate series: 12
Compatible series: 12
Provider exclusions: 0
Unresolved acquisition errors: 0
Provider warning messages: catalog-data warnings for JOLTS series only; observations were returned and normalized.

Normalized observations: 2,374
Observed values: 2,368
Explicit missing values: 6
Canonical facts loaded for TASK-207 run: 2,374
Territory: USA
Frequency: monthly
Period coverage: 2010-M01 through 2026-M06
Distinct monthly periods loaded: 198
Units: 5
Series loaded: 12

Repository state after TASK-207:

- curated facts: 10,555,773
- indicators: 1,423
- sources: 2
- pipeline runs: 39
- lineage events: 78
- quality checks: 79

Initial TASK-207 repository growth from pre-campaign state:

- facts: +2,374
- indicators: +12
- monthly periods: +198
- sources: +1
- pipeline runs: +1
- lineage events: +2
- quality checks: +3

## PostgreSQL verification

Run key: `task-207-bls-us-labor-monthly-phase2`

Run-scoped counts:

- staging rows: 2,374
- fact rows: 2,374
- indicators: 12
- periods: 198
- lineage events: 2
- quality checks: 3
- failed quality checks: 0

Duplicate canonical key groups: 0

Idempotence:

- same-scope rerun completed with zero net repository growth;
- final idempotence report records `idempotent: true`.

## Prediction evaluation

Artifact: `artifacts/reports/task-207-bls-us-labor-monthly-prediction-evaluation.json`

Verdict: Mostly Accurate.

Comparison:

- predicted scale: about 1,900-2,050 observations;
- actual scale: 2,374 observations;
- predicted compatible coverage: 12 BLS monthly series with possible edge variation;
- actual compatible coverage: 12 / 12 series;
- predicted provider exclusions/acquisition errors: possible edge warnings;
- actual: no provider exclusions, no acquisition errors, BLS catalog warnings for JOLTS metadata only;
- predicted friction: low to moderate;
- actual friction: moderate, because BLS unregistered API range behavior required deterministic two-window acquisition.

The discrepancy reflects provider limits/variability more than missing source understanding.

## Architecture verdict

Architecture remains frozen / evidence-maintained.

The existing source-specific acquisition/normalization boundary, monthly scalar period dimension, source-specific staging table, `meta.pipeline_run`, lineage, quality, and `curated.fact_observation` substrate sufficed.

No contradiction was observed:

- no canonical ambiguity;
- no repository-class mismatch;
- no inability to preserve provider period/unit/frequency/source payload semantics;
- no scaling failure;
- no repeated operational friction requiring a new architecture layer.

## Verification

Completed verification before closeout:

- `python3 -m py_compile tools/task207_bls_us_labor_monthly_phase2_campaign.py tests/test_task207_bls_us_labor_monthly_phase2_campaign.py` — passed.
- `PYTHONPATH=src:. uvx pytest -q tests/test_task207_bls_us_labor_monthly_phase2_campaign.py` — `5 passed in 0.08s`.
- `PYTHONPATH=src:. uvx pytest -q` — `736 passed in 517.45s (0:08:37)`.
- TASK-207 JSON report validation — `task-207 BLS json reports valid: 4`.
- Run-scoped PostgreSQL verification query returned `2374|2374|12|198|2|3|0`.
- Final coherence/context/architecture/git checks are recorded in `context/latest_handoff.md`.

## Next recommended Phase 2 direction

Continue Phase 2 diverse-source macroeconomic enrichment with another already proven, non-WDI bounded source path that adds a material macro capability absent from WDI annual-scalar coverage.

Recommended next target: IMF or ALFRED/FRED-style macro source with either external-sector/accounting depth or revision/vintage history, selected by capability gap and existing bounded implementation maturity.

Do not advance to trade, companies, or financial assets yet.
