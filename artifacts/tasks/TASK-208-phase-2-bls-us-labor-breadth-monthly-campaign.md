# TASK-208 — Phase 2 BLS U.S. Labor-Market Breadth Monthly Campaign

Status: complete; clean retry regenerated artifacts after BLS threshold reset and final verification passed
Date: 2026-07-11
Type: Phase 2 diverse-source macroeconomic repository expansion / BLS monthly scalar breadth campaign

## Objective

Scale the proven TASK-207 BLS monthly labor-market path from a 12-series proof into a coherent, materially broader U.S. labor-market capability without creating new framework, schema, taxonomy, orchestration, trade, company, or financial-asset architecture.

TASK-207 is accepted as closed. Non-blocking local limitation: four failed FRED-detour files remain untracked locally and were not touched by TASK-208.

## Capability and candidate population

Selected capability: broader monthly U.S. labor-market monitoring across participation margins, unemployment-duration pressure, industry payroll employment, sector hours/earnings, JOLTS separations, and industry job-openings signals.

Candidate population: 36 additional seasonally-adjusted monthly BLS series selected from BLS public API v2 organization:

- CPS/LNS participation and unemployment-duration margins: 4 candidates.
- CES industry/supersector payroll employment: 14 candidates.
- CES industry hours and earnings: 6 candidates.
- JOLTS total separations and sector job openings: 12 candidates.

The 12 TASK-207 proof series were excluded from this incremental TASK-208 candidate population to avoid simply re-running the proof. TASK-208 therefore expands the BLS labor capability rather than duplicating the proof scope.

## Frozen prediction

Artifact: `artifacts/reports/task-208-bls-us-labor-breadth-monthly-frozen-selection-prediction.json`

Prediction summary:

- Expected candidate series: 36.
- Expected compatible series: 34-36.
- Expected observations: about 6,500-7,100 monthly rows.
- Expected coverage: 2010-M01 through approximately 2026-M06.
- Expected provider/execution difficulties: BLS public API 25-series cap, 10-year request-window cap, JOLTS catalog warnings, possible invalid/unavailable JOLTS sector series, current-year edge availability.
- Expected architecture compatibility: existing source-specific BLS monthly scalar path should suffice.

## Series included

Compatible loaded series: 36.

CPS/LNS:

- `LNS15000000` — not in labor force level.
- `LNS12600000` — employed part time for economic reasons.
- `LNS13023621` — unemployed less than 5 weeks.
- `LNS13023557` — unemployed 27 weeks and over.

CES payroll employment:

- `CES0600000001` — goods-producing.
- `CES1000000001` — mining and logging.
- `CES2000000001` — construction.
- `CES3000000001` — manufacturing.
- `CES4000000001` — trade, transportation, and utilities.
- `CES4200000001` — wholesale trade.
- `CES4300000001` — retail trade.
- `CES5000000001` — information.
- `CES5500000001` — financial activities.
- `CES6000000001` — professional and business services.
- `CES6500000001` — education and health services.
- `CES7000000001` — leisure and hospitality.
- `CES8000000001` — other services.
- `CES9000000001` — government.

CES hours/earnings:

- `CES3000000002`, `CES3000000003` — manufacturing weekly hours / hourly earnings.
- `CES2000000002`, `CES2000000003` — construction weekly hours / hourly earnings.
- `CES6000000002`, `CES6000000003` — professional and business services weekly hours / hourly earnings.

JOLTS:

- `JTS000000000000000TSR` — total separations.
- `JTS000000000000000QUR` — quits.
- `JTS000000000000000LDR` — layoffs and discharges.
- `JTS000000000000000OSR` — other separations.
- `JTS100000000000000JOL` — mining and logging job openings.
- `JTS300000000000000JOL` — manufacturing job openings.
- `JTS400000000000000JOL` — trade, transportation, and utilities job openings.
- `JTS600000000000000JOL` — professional and business services job openings.
- `JTS700000000000000JOL` — education and health services job openings.
- `JTS900000000000000JOL` — government job openings.

## Series excluded

Provider exclusions: 0 after corrected retry.

The initially excluded JOLTS construction and information job-opening identifiers were candidate-construction errors, not genuine provider exclusions. The corrected identifiers were acquired and loaded:

- `JTS230000000000000JOL` — construction job openings.
- `JTS510000000000000JOL` — information job openings.

No acquisition errors remain unresolved. The corrected provider report records `status=complete`, 36 compatible series, 0 provider exclusions, and 0 acquisition errors.

## Acquisition and evidence

Acquisition used deterministic BLS public API chunks:

- 24-series chunks, below the public API 25-series cap.
- Year windows: 2010-2019 and 2020-2026, respecting the 10-year request-window cap.

Raw evidence:

- `data/raw/task208_bls_us_labor_breadth_monthly_phase2_campaign/task-208-bls-us-labor-breadth-monthly-2010-2026.json`
- per-series-chunk/per-window raw responses under `data/raw/task208_bls_us_labor_breadth_monthly_phase2_campaign/`

Processed evidence:

- `data/processed/task208_bls_us_labor_breadth_monthly_phase2_campaign/task-208-bls-us-labor-breadth-monthly-normalized.json`
- `data/processed/task208_bls_us_labor_breadth_monthly_phase2_campaign/task-208-bls-us-labor-breadth-monthly-manifest.json`

Reports:

- `artifacts/reports/task-208-bls-us-labor-breadth-monthly-frozen-selection-prediction.json`
- `artifacts/reports/task-208-bls-us-labor-breadth-monthly-provider-evidence-report.json`
- `artifacts/reports/task-208-bls-us-labor-breadth-monthly-postgresql-load-report.json`
- `artifacts/reports/task-208-bls-us-labor-breadth-monthly-prediction-evaluation.json`
- `artifacts/reports/task-208-bls-us-labor-breadth-monthly-artifact-checksums.txt`

## Results

- Candidate series: 36.
- Compatible series: 36.
- Provider exclusions: 0.
- Acquisition errors: 0.
- Normalized observations: 7,116.
- Observed values: 7,112.
- Explicit missing values: 4.
- Frequency: monthly only.
- Seasonal adjustment: all selected series are seasonally adjusted (`SA`), preserved in attributes.
- Temporal coverage: 2010-M01 through 2026-M06.
- Distinct monthly periods: 198.
- Unit count: 4.

## PostgreSQL loading

Run key: `task-208-bls-us-labor-breadth-monthly-phase2`

Initial repository counts before TASK-208:

- facts: 10,555,773
- indicators: 1,423
- periods: 233
- sources: 2
- runs: 39
- lineage events: 78
- quality checks: 79

Repository counts after TASK-208:

- facts: 10,562,495
- indicators: 1,457
- periods: 233
- sources: 3
- runs: 40
- lineage events: 80
- quality checks: 82

Initial TASK-208 growth:

- facts: +6,722
- indicators: +34
- periods: +0, because monthly periods already existed from TASK-207
- sources: +1
- runs: +1
- lineage events: +2
- quality checks: +3

Run-scoped PostgreSQL verification:

```text
staging|facts|indicators|periods|lineage|quality|failed_quality
6722|6722|34|198|2|3|0
```

Duplicate canonical key groups for the TASK-208 source: 0.

Idempotence: same-scope rerun produced zero net repository growth and `idempotent: true`.

## Prediction evaluation

Artifact: `artifacts/reports/task-208-bls-us-labor-breadth-monthly-prediction-evaluation.json`

Verdict: Mixed.

- Predicted observations: about 6,500-7,100.
- Actual observations after corrected retry: 7,116.
- Predicted compatible coverage: 34-36 compatible series from 36 candidates.
- Actual compatible coverage: 36 compatible series from 36 candidates.
- Predicted provider exclusions: 0-2 invalid/unavailable JOLTS industry series.
- Actual provider exclusions after corrected retry: 0.
- Predicted acquisition errors: none after deterministic chunking.
- Actual acquisition errors after retry: 0.
- Predicted friction: moderate public API chunking and JOLTS warnings.
- Actual friction: moderate plus one temporary BLS daily-threshold retry blocker.

The broad capability and architecture prediction were directionally right, but the initial JOLTS exclusion classification exposed candidate-construction error rather than provider unavailability.

## Architecture verdict

Architecture remains frozen / evidence-maintained.

The existing source-specific BLS monthly scalar acquisition/normalization boundary, monthly period dimension, source-specific staging table, curated fact substrate, run-scoped lineage, quality checks, duplicate-key verification, and idempotent same-run replacement sufficed.

No contradiction appeared:

- no canonical ambiguity;
- no repository-class mismatch;
- no inability to preserve provider period, unit, seasonal-adjustment, series, or source-payload semantics;
- no scaling failure;
- no repeated operational friction requiring a new framework.

## Final verification

Completed verification after clean retry:

```text
PYTHONPATH=src:. python3 tools/task208_bls_us_labor_breadth_monthly_phase2_campaign.py run --load --database macroforge
# {"acquisition_errors": 0, "loaded": true, "row_count": 7116, "series": 36, "source": "BLS", "task": "TASK-208"}

python3 -m py_compile tools/task207_bls_us_labor_monthly_phase2_campaign.py tools/task208_bls_us_labor_breadth_monthly_phase2_campaign.py tests/test_task208_bls_us_labor_breadth_monthly_phase2_campaign.py
PYTHONPATH=src:. uvx pytest -q tests/test_task208_bls_us_labor_breadth_monthly_phase2_campaign.py
# 10 passed in 0.13s

TASK-208 JSON validation
# task-208 json-ok 7

PostgreSQL run-scoped verification
# staging|facts|indicators|periods|lineage|quality|failed_quality|duplicate_canonical_key_groups|canonical_bls_source_rows
# 7116|7116|36|198|2|3|0|0|1
```

Full suite: `788 passed in 828.43s`. Final governance after state/handoff edits: context health 0 blocks/0 warnings; coherence 0 blocks/0 warnings; architecture-reality audit 0 blocks/0 warnings; `git diff --check` passed.

## Next recommendation

Further BLS scaling is still possible, but the next stronger Phase 2 action is likely another diverse macroeconomic source if it adds a materially different capability: IMF external-sector/accounting depth or ALFRED/FRED revision/vintage/timeliness evidence. BLS labor breadth is now meaningfully stronger, so marginal value should be compared against non-labor macro gaps before another BLS expansion.

Do not advance to trade, companies, or financial assets yet.

## Source-identity and candidate-integrity correction

Audit artifact: `artifacts/reports/task-208-source-identity-candidate-integrity-audit.md`.

A bounded correction found two issues before commit:

1. TASK-207 and TASK-208 had created separate campaign-specific BLS source identities even though both use the same BLS public API v2 source. The database has been corrected to reuse canonical source `BLS_PUBLIC_API_V2` (`source_id=5cf90ebf-1fb0-4a64-a58e-f6dc1e95ead4`) for both runs. The duplicate TASK-208 BLS source was deleted only after confirming it had no facts, staging rows, pipeline runs, or lineage references.
2. The original TASK-208 excluded JOLTS identifiers were candidate-construction errors, not provider exclusions:
   - `JTS200000000000000JOL` corrected to `JTS230000000000000JOL` for construction job openings.
   - `JTS500000000000000JOL` corrected to `JTS510000000000000JOL` for information job openings.

Corrected PostgreSQL state after the successful correction load:

```text
staging_rows|fact_rows|indicators|periods|lineage|quality|failed_quality|duplicate_canonical_key_groups
7116|7116|36|198|2|3|0|0
```

Clean retry result: after the BLS daily threshold reset, TASK-208 regenerated raw/processed/report/checksum artifacts from provider evidence, loaded the corrected 36-series campaign idempotently, and preserved the previous blocked attempts under attempt-specific raw directories.

Revised prediction-quality verdict: Mixed. The broad capability and architecture prediction were directionally right, but the original JOLTS exclusion classification was wrong. The retry has no unresolved provider blocker.
