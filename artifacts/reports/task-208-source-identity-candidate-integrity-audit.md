# TASK-208 Source-Identity and Candidate-Integrity Audit

Date: 2026-07-11
Status: correction applied and clean artifact re-acquisition completed after BLS daily request-threshold reset; TASK-208 is commit-ready as a bounded file set.

## Source-count growth explanation

Before correction, PostgreSQL had three `meta.source` rows:

| source_id | source_code | source_name | TASK-207 facts | TASK-208 facts | verdict |
| --- | --- | --- | ---: | ---: | --- |
| `16447781-407d-4154-b71b-2dd40eafdb0f` | `WDI` | World Bank World Development Indicators | 0 | 0 | unrelated genuine source |
| `5cf90ebf-1fb0-4a64-a58e-f6dc1e95ead4` | `BLS_US_LABOR_MONTHLY_PHASE2` | BLS U.S. Labor Monthly Phase 2 Campaign | 2,374 | 0 | campaign-specific duplicate identity |
| `ef022250-da55-4042-8242-61a10e55fd0d` | `BLS_US_LABOR_BREADTH_MONTHLY_PHASE2` | BLS U.S. Labor Breadth Monthly Phase 2 Campaign | 0 | 6,722 | campaign-specific duplicate identity |

Cause: TASK-207 and TASK-208 used campaign-specific `SOURCE_CODE` constants even though both target the same semantic provider/API: BLS public API v2. Dataset/release/run metadata already distinguishes campaign scope, so separate `meta.source` identities were not justified.

Correction applied:

- Canonicalized TASK-207's BLS source row to `BLS_PUBLIC_API_V2` / `BLS Public API v2`.
- Patched TASK-207 and TASK-208 scripts to use `SOURCE_CODE='BLS_PUBLIC_API_V2'` and `SOURCE_NAME='BLS Public API v2'`.
- Reloaded corrected TASK-208 into the canonical BLS source.
- Verified the former TASK-208 duplicate source had no facts, staging rows, pipeline runs, or lineage references.
- Removed only the unreferenced duplicate source, its unreferenced dataset release, and its unreferenced campaign-specific indicators in a transaction.

After correction, source count is 2: `BLS_PUBLIC_API_V2` and `WDI`.

Canonical BLS source after correction:

| source_id | source_code | source_name | source_home_url | TASK-207 facts | TASK-208 facts | total BLS facts |
| --- | --- | --- | --- | ---: | ---: | ---: |
| `5cf90ebf-1fb0-4a64-a58e-f6dc1e95ead4` | `BLS_PUBLIC_API_V2` | BLS Public API v2 | https://www.bls.gov/ | 2,374 | 7,116 | 9,490 |

## JOLTS candidate-integrity audit

Original excluded identifiers:

| original identifier | intended meaning | audit verdict | corrected identifier | corrected DB evidence |
| --- | --- | --- | --- | --- |
| `JTS200000000000000JOL` | Construction job openings | candidate-construction error; BLS preserved messages said "Series does not exist" | `JTS230000000000000JOL` | 197 monthly observations, 2010-M01 through 2026-M05 |
| `JTS500000000000000JOL` | Information job openings | candidate-construction error; BLS preserved messages said "Series does not exist" | `JTS510000000000000JOL` | 197 monthly observations, 2010-M01 through 2026-M05 |

The original identifiers should not be treated as genuine provider exclusions. They were malformed/wrong industry-code constructions for the intended JOLTS industries. The corrected identifiers returned observations and were loaded inside TASK-208.

Authoritative metadata limitation: an attempted direct BLS time-series metadata file lookup was blocked by execution policy. The correction is therefore grounded in preserved BLS API evidence for the wrong identifiers plus successful BLS API acquisition/load of the corrected identifiers. TASK-208 should not be committed until raw artifact evidence is regenerated cleanly after the BLS daily request threshold resets.

## Corrected TASK-208 repository state

PostgreSQL run-scoped verification after correction:

```text
staging_rows|fact_rows|indicators|periods|lineage|quality|failed_quality|duplicate_canonical_key_groups
7116|7116|36|198|2|3|0|0
```

Corrected candidate accounting:

- Candidate series: 36.
- Compatible series: 36.
- Genuine provider exclusions: 0.
- Candidate-construction errors corrected: 2.
- Acquisition errors in corrected DB load: 0.
- Corrected observations loaded: 7,116.
- Corrected period coverage: 2010-M01 through 2026-M06 across the complete campaign; the corrected JOLTS industry series are present inside the 198 monthly-period run.

## Retry closeout result

After the BLS daily request threshold reset, TASK-208 cleanly regenerated active raw/processed/report/checksum artifacts from BLS public API v2 evidence. The corrected active artifact set now records 36 compatible series, 0 provider exclusions, 0 acquisition errors, 7,116 facts, 7,112 observed values, 4 explicit missing values, and 2010-M01 through 2026-M06 coverage.

The previous threshold-failed attempts remain preserved under attempt-specific raw directories as evidence and no longer overwrite active complete artifacts.

## Regression coverage added

`tests/test_task208_bls_us_labor_breadth_monthly_phase2_campaign.py` now covers:

- TASK-207 and TASK-208 reuse canonical `BLS_PUBLIC_API_V2` source identity.
- Corrected JOLTS identifiers are present and wrong original identifiers are absent.
- Acquisition errors block load SQL construction.
- Existing monthly-scalar/source-specific boundaries remain intact.

Focused verification completed:

```text
python3 -m py_compile tools/task207_bls_us_labor_monthly_phase2_campaign.py tools/task208_bls_us_labor_breadth_monthly_phase2_campaign.py tests/test_task208_bls_us_labor_breadth_monthly_phase2_campaign.py
PYTHONPATH=src:. uvx pytest -q tests/test_task208_bls_us_labor_breadth_monthly_phase2_campaign.py
# 7 passed, 1 skipped in 0.12s
```

## Revised prediction-quality verdict

Mixed.

The broad capability, architecture compatibility, and approximate scale were directionally right, but the original treatment of the two failed JOLTS identifiers as provider exclusions was wrong. They were candidate-construction errors and corrected identifiers loaded successfully.

## Architecture verdict

No architecture redesign is justified. The defect was implementation/candidate selection and source-identity hygiene, not a repository-class contradiction. Existing BLS monthly-scalar acquisition, normalization, lineage, quality, idempotence, and canonical duplicate checks remain sufficient once canonical source reuse and corrected JOLTS IDs are applied.
