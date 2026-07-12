# TASK-211 WEO dataset-release cleanup diagnostic

Status: read-only diagnosis complete; no deletion executed in this step.

## Cause

The cleanup script created a temporary table named `_target_dataset_release` containing the two approved obsolete release ids, then discovered every `dataset_release_id` column through `information_schema.columns` excluding only `pg_catalog` and `information_schema`.

PostgreSQL exposes temporary tables through a `pg_temp_*` schema. Because the script did not exclude temporary schemas or its own helper tables, the dynamic reference loop counted `_target_dataset_release.dataset_release_id` joined against itself. That produces exactly 2 references: one for each approved target row.

The explicit pre-delete audits did not include the cleanup script's own temporary target table, so after loader reruns they correctly reported zero external references.

Classification: self-reference counting bug in cleanup script, not genuine external references, not stale audit state, not transaction/snapshot drift.

## Complete discovered dataset_release_id relation inventory

| schema | table | column | FK to meta.dataset_release |
|---|---|---|---|
| curated | fact_observation | dataset_release_id | fact_observation_dataset_release_id_fkey |
| meta | dataset_release | dataset_release_id | primary key / self row, not FK |
| meta | pipeline_run | dataset_release_id | pipeline_run_dataset_release_id_fkey |
| meta | provider_code_list | dataset_release_id | provider_code_list_dataset_release_id_fkey |
| staging | bls_us_labor_breadth_monthly_phase2_observation | dataset_release_id | bls_us_labor_breadth_monthly_phase2_obs_dataset_release_id_fkey |
| staging | bls_us_labor_monthly_phase2_observation | dataset_release_id | bls_us_labor_monthly_phase2_observation_dataset_release_id_fkey |
| staging | task209_imf_weo_g20_projection_observation | dataset_release_id | task209_imf_weo_g20_projection_observat_dataset_release_id_fkey |
| staging | task211_imf_weo_broad_macro_observation | dataset_release_id | task211_imf_weo_broad_macro_observation_dataset_release_id_fkey |
| staging | wdi_observation | dataset_release_id | wdi_observation_dataset_release_id_fkey |

## Counts for obsolete target ids

Target ids:

- IMF:WEO:DATAMAPPER:BROAD_MACRO_ANNUAL | world-economic-outlook-april-2026 | be368384-0d63-4f92-82ec-d469c0967f03
- IMF:WEO:DATAMAPPER:PROJECTIONS | world-economic-outlook-april-2026 | b3d29966-8c4c-4f3f-b337-d2422cdf5d96

| schema | table | BROAD_MACRO_ANNUAL | PROJECTIONS |
|---|---:|---:|---:|
| curated | fact_observation | 0 | 0 |
| meta | dataset_release | 1 | 1 |
| meta | pipeline_run | 0 | 0 |
| meta | provider_code_list | 0 | 0 |
| staging | bls_us_labor_breadth_monthly_phase2_observation | 0 | 0 |
| staging | bls_us_labor_monthly_phase2_observation | 0 | 0 |
| staging | task209_imf_weo_g20_projection_observation | 0 | 0 |
| staging | task211_imf_weo_broad_macro_observation | 0 | 0 |
| staging | wdi_observation | 0 | 0 |

External references excluding the target rows themselves: 0.

## Script correction

Patched `artifacts/reports/task-211-weo-dataset-release-cleanup.sql` so its dynamic discovery excludes:

- `pg_temp_%` schemas;
- `pg_toast_temp_%` schemas;
- helper tables `_target_dataset_release`, `_dataset_release_reference_audit`, `_deleted_dataset_release`.

Added static regression tests in `tests/test_task211_weo_dataset_release_cleanup_script.py`.

Verification:

- `PYTHONPATH=src:. uvx pytest -q tests/test_task211_weo_dataset_release_cleanup_script.py tests/test_imf_weo_datamapper_substrate.py`
- Result: `8 passed in 0.06s`

## Safety verdict

Deletion is now demonstrably safe by external-reference evidence, but deletion was not executed during this diagnostic step per instruction.
