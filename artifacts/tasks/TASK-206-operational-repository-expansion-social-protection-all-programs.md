# TASK-206 — Corrected Operational Repository Expansion for Social Protection All-Programs

Status: complete after correction rerun
Date: 2026-07-10
Type: repository expansion / WDI chunked campaign / provider-empty audit correction / Phase 1 transition gate

## Objective

Select and execute the strongest remaining first-order macroeconomic WDI annual-scalar expansion while explicitly testing whether bulk WDI Phase 1 is approaching diminishing returns. A follow-up provider-empty audit invalidated the original zero-observation classifications; this artifact records the corrected TASK-206 result.

## Correction root cause

Original TASK-206 classified many ASPIRE/WDI source 29 responses as `zero_observations_within_requested_scope` because acquisition filtered solely on `countryiso3code`. ASPIRE responses can leave `countryiso3code` blank while providing the usable WDI territory identifier in `row["country"]["id"]`.

Corrected bounded rule:
- use `countryiso3code` when populated and present in the accepted non-aggregate WDI territory catalogue;
- otherwise use `row["country"]["id"]` only when present in the same accepted non-aggregate catalogue;
- reject aggregate/unknown territory identifiers;
- preserve original provider `countryiso3code` as `provider_countryiso3code` and retain provider `country.id` as source evidence.

Invalid original generated evidence was preserved non-destructively under:
`data/raw/task206_wdi_social_protection_all_programs_chunked_expansion/audit_archives/task-206-correction-20260710T211050Z/`

Archive manifest:
`data/raw/task206_wdi_social_protection_all_programs_chunked_expansion/audit_archives/task-206-correction-20260710T211050Z/archive-manifest.json`

## Selected domain and capability

Selected domain: Social protection, labor-market protection, and household-transfer systems.

Selected capability: aggregate all-program social protection/labor reach, adequacy, benefit incidence, benefit distribution, and poverty/inequality reduction monitoring.

Confidence cell: WDI public API v2 annual scalar country-indicator observations for aggregate All Social Protection and Labor indicators.

Candidate population: unloaded WDI topic 10 Social Protection & Labor indicators with code prefix `per_allsp.` or `per_allsp_`.

## Corrected results

- Candidate indicators: 135
- Included compatible indicators: 4 — `per_allsp.adq_pop_tot`, `per_allsp.avt_pop_preT_tot`, `per_allsp.ben_q1_tot`, `per_allsp.cov_pop_tot`
- Provider/representation exclusions: 131
- Exclusion categories: `non_annual_periods`: 131; `compatible_annual_scalar_observations`: 4
- Zero-observation exclusions after correction: 0
- Unresolved acquisition errors: 0
- Provider rows before territory filtering: 560,049
- Accepted non-aggregate rows after territory fallback: 514,556
- Aggregate rows excluded by live WDI country catalogue: 44,863
- Unknown/unusable territory rows: 630
- Canonical facts loaded: 30,380
- Observed values: 2,099
- Explicit missing values: 28,281
- Territories: 217
- Period range: 1990:2024

The 131 excluded candidates are not provider-empty. They have accepted non-aggregate rows but include non-annual provider period labels such as `2011-21S`/`2011-21W`, which are outside the mature WDI annual-scalar confidence cell.

## Candidate-partition integrity

- Unique candidates: 135 / 135
- Missing candidates: none
- Duplicate candidates: none
- Included/excluded overlap: none
- Accounted candidates: 135 / 135
- Candidate-set exhaustion claim: yes, but only for the exact aggregate all-program WDI annual-scalar candidate population named above.
- Domain capability closure: not claimed for broad Social Protection & Labor.

## PostgreSQL evidence

Original invalid TASK-206 loaded state before correction: 10,545,804 curated facts / 1,410 indicators / 12,341,870 WDI staging rows.

Corrected state after same-run replacement:
- `curated.fact_observation`: 10,553,399
- `curated.dim_indicator`: 1,411
- `staging.wdi_observation`: 12,349,465
- `meta.pipeline_run`: 38
- `meta.lineage_event`: 76
- `meta.quality_check`: 76

Corrected TASK-206 run scope:
- 30,380 curated facts
- 30,380 staging rows
- 4 indicators
- 217 territories
- 1990:2024
- 4 lineage events
- 4 quality checks
- 0 non-passing quality checks
- 0 WDI duplicate canonical-key groups

Idempotence: corrected same-run rerun produced zero net repository growth.

## Wider ASPIRE/source-29 impact

No previously implemented ASPIRE/source-29 `per_allsp.` / `per_allsp_` WDI indicators outside TASK-206 were found in `curated.dim_indicator`. Active processed `per_allsp` artifacts are TASK-206 only. Other WDI campaign scripts may still use countryiso3code-only filtering, but this task found no evidence that prior loaded campaigns used ASPIRE/source-29 rows affected by the blank-`countryiso3code` behavior. No unrelated campaigns were repaired or redesigned.

## Revised Phase 1 finding

The original provider-empty diminishing-returns verdict is withdrawn. Corrected TASK-206 still supports a Phase 1 transition gate, but for a different reason: the strongest coherent residual WDI target produced 4 annual-scalar compatible indicators / 30,380 facts, while 131 coherent candidates were excluded because their accepted non-aggregate provider rows contain non-annual period labels outside the mature annual-scalar path. Bulk WDI Phase 1 has reached diminishing marginal returns for this exact annual-scalar confidence cell; remaining Social Protection/Labor value likely requires non-annual/survey-period handling or diverse-source Phase 2 enrichment, not another automatic bulk WDI annual-scalar campaign.

## Key artifacts

- `tools/task206_wdi_social_protection_all_programs_chunked_expansion.py`
- `tests/test_task206_acquisition_completion_semantics.py`
- `data/raw/task206_wdi_social_protection_all_programs_chunked_expansion/`
- `data/processed/task206_wdi_social_protection_all_programs_chunked_expansion/`
- `artifacts/reports/task-206-corrected-provider-evidence-classification-report.json`
- `artifacts/reports/task-206-corrected-postgresql-load-report.json`
- `artifacts/reports/task-206-corrected-phase-1-transition-gate-report.json`
- `artifacts/reports/task-206-aspire-source29-wider-impact-assessment.json`
- `artifacts/reports/task-206-artifact-checksums.txt`

## Architecture verdict

Frozen/evidence-maintained architecture remains valid. The correction was source-specific normalization inside the existing WDI annual-scalar path. No schema change, provider mirror, generic source framework, taxonomy, new prioritization layer, trade/company/financial-asset construction, or production scheduling was introduced.
