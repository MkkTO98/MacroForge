# TASK-015 — Implement OECD/SDMX PostgreSQL loader

Status: completed
Created: 2026-06-03
Completed: 2026-06-03
Preceded by: TASK-014
Decision: DEC-006
Dry-run/preflight: completed in `simulation/dry_runs/20260603_220913-implement-task-015-oecd-sdmx-postgresql-loader.md`

## Goal

Implement the narrow OECD/SDMX PostgreSQL promotion accepted by DEC-006: add a source-specific OECD/SDMX staging table and a source-specific loader that loads the recorded normalized OECD smoke evidence into staging and curated PostgreSQL tables in an isolated rerunnable smoke database.

This task is implementation, not architecture expansion. It must remain source-specific and boring.

## Scope

In scope:

- Add a second raw SQL migration for `staging.oecd_sdmx_observation`.
- Add migration/schema tests for the new staging table and natural key.
- Add `src/macroforge/oecd_sdmx_loader.py` or equivalent source-specific loader.
- Load from `data/metadata/oecd_sdmx/oecd-sdmx-smoke-normalized.json`; do not fetch live OECD data in the database loader/test path.
- Upsert:
  - `meta.source`
  - `meta.dataset_release`
  - `meta.pipeline_run`
  - `staging.oecd_sdmx_observation`
  - curated dimensions and facts
  - lineage events
  - quality checks
- Map `UNIT_MEASURE` to `curated.dim_unit` so `USD_EXC` and `USD_PPP` remain distinct facts.
- Map observed SDMX attributes such as `CONF_STATUS`, `DECIMALS`, and `OBS_STATUS` into `curated.dim_attribute_set`.
- Verify idempotent reruns against an isolated temporary PostgreSQL database.
- Add a small JSON smoke report under `artifacts/reports/` if the loader succeeds.
- Update runbook/state/handoff/summaries with exact verification output.

Out of scope:

- Live `macro` database writes.
- Live OECD fetch inside database loader tests.
- Generalized SDMX framework/plugin architecture.
- Codelist label enrichment beyond code preservation.
- Curated schema changes beyond using existing dimensions/facts.
- `mart` schema/reporting work.
- Alembic, SQLAlchemy, orchestration, Docker, scheduling, or CI automation.
- Paid, credentialed, or production API use.
- Git push.

## Required implementation boundaries

- Do not modify `db/migrations/001_v0_schema_foundation.sql`; add a new migration file instead.
- The loader must target an explicit database name and should be tested only against isolated temp databases.
- The loader must not default to writing a live `macro` database without an explicit approval-gated workflow.
- The loader should be patterned after `wdi_loader.py`, but do not extract a generalized loader abstraction unless a failing test proves the need.

## Expected files

Suggested files, subject to TDD refinement:

- `db/migrations/002_oecd_sdmx_staging.sql`
- `src/macroforge/oecd_sdmx_loader.py`
- `tests/test_oecd_sdmx_loader.py`
- `tests/test_schema_foundation.py` or a focused migration test update
- `artifacts/reports/oecd-sdmx-load-smoke-20260603.json`
- `docs/runbooks/` update only if command surface is non-obvious

## Acceptance criteria

- New migration creates `staging.oecd_sdmx_observation` with the minimum DEC-006 columns and natural key.
- Tests prove schema/migration behavior for the OECD staging table.
- Loader builds SQL from recorded normalized OECD evidence without network access.
- Isolated PostgreSQL smoke load succeeds.
- Rerunning the loader with the same run key is idempotent.
- Staging row count is 8.
- Curated fact row count is 8.
- There are no duplicate curated facts for:
  - source
  - indicator
  - territory
  - period
  - unit
  - attribute set
  - as-of date
- `curated.dim_unit` contains both `USD_EXC` and `USD_PPP`.
- `curated.dim_attribute_set` preserves observed SDMX attributes.
- Lineage and quality checks are recorded.
- Full test suite passes.
- Generated-project coherence passes.
- No live `macro` database write occurs.

## Verification plan

Run after implementation:

```bash
PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests/test_oecd_sdmx_loader.py -q
PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests -q
python3 tools/check_coherence.py --project . --json
```

If a CLI smoke command is added, run it only against an isolated temporary PostgreSQL database and record exact output.

## Notes

DEC-006 accepts a narrow source-specific staging migration plus source-specific loader. It does not approve a generalized SDMX framework or curated schema changes.

## Outcome

TASK-015 implemented the DEC-006 bounded OECD/SDMX PostgreSQL promotion:

- Added `db/migrations/002_oecd_sdmx_staging.sql` with source-specific `staging.oecd_sdmx_observation` and a natural key over `pipeline_run_id + provider_dataset_code + measure_code + ref_area_code + period_year + unit_measure_code`.
- Added `src/macroforge/oecd_sdmx_loader.py`, a source-specific loader patterned after the WDI loader without extracting a generalized SDMX framework.
- Added `tests/test_oecd_sdmx_loader.py` and extended `tests/test_schema_foundation.py` with RED/GREEN coverage for the migration, SQL builder, report writer, isolated PostgreSQL idempotency, unit preservation, attribute preservation, lineage, and quality checks.
- Generated isolated smoke evidence at `artifacts/reports/oecd-sdmx-load-smoke-20260603.json`.

Observed isolated smoke output after two reruns against a temporary PostgreSQL database:

```json
{
  "attribute_sets": 1,
  "fact_rows": 8,
  "lineage_events": 2,
  "quality_checks": 4,
  "staging_rows": 8,
  "unit_codes": [
    "USD_EXC",
    "USD_PPP"
  ]
}
```

Additional database truth inspected during the smoke:

```text
staging.oecd_sdmx_observation rows: 8
curated.fact_observation rows: 8
curated.dim_unit: USD_EXC,USD_PPP
curated.dim_attribute_set.attributes: {"DECIMALS": "2", "OBS_STATUS": "A", "CONF_STATUS": "F"}
```

No live `macro` database write, live OECD fetch inside database tests, curated schema change, generalized SDMX framework, paid/credentialed API use, or git push was performed.
