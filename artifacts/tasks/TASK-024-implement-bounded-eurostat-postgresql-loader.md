# TASK-024 — Implement bounded Eurostat PostgreSQL loader

Status: complete
Created: 2026-06-04
Completed: 2026-06-04
Depends on: TASK-023
Governing decision: DEC-012
Design note: `docs/architecture/bounded-eurostat-postgresql-promotion-design.md`

## Objective

Implement the bounded Eurostat `namq_10_gdp` PostgreSQL promotion accepted by DEC-012.

The implementation should load only the recorded normalized fixture:

```text
data/metadata/eurostat/eurostat-namq-10-gdp-architecture-spike-normalized.json
```

It should use the TASK-022 canonical-domain schema and should not broaden into live Eurostat ingestion or a generalized JSON-stat/source framework.

## Required scope

- Create `db/migrations/004_eurostat_namq_staging.sql`.
- Add `staging.eurostat_namq_observation` for the bounded fixture.
- Create `src/macroforge/eurostat_namq_loader.py`.
- Load from the recorded normalized fixture only.
- Insert/reuse:
  - `meta.source` for `EUROSTAT_NAMQ_GDP`;
  - `meta.dataset_release` with endpoint/checksum/filter metadata;
  - `meta.pipeline_run`;
  - canonical quarterly periods for `2023-Q1` and `2023-Q2`;
  - canonical country territories `DEU` and `FRA`;
  - provider period mappings;
  - provider territory mappings `DE -> DEU` and `FR -> FRA`;
  - bounded provider code-list/code dictionaries for `freq`, `unit`, `s_adj`, `na_item`, `geo`, `time`;
  - source-specific indicator/unit rows;
  - attribute sets for seasonal adjustment and JSON-stat status/source details;
  - four `curated.fact_observation` rows;
  - lineage and quality checks.
- Write a small load report artifact.

## Acceptance criteria

- [x] Fresh implementation dry-run is created and validated before code/test edits.
- [x] RED tests fail for missing migration/loader behavior before implementation.
- [x] Migration 004 is tested for expected table/constraint shape.
- [x] Loader tests verify no live network call surface and local normalized fixture input.
- [x] Isolated PostgreSQL smoke applies migrations 001, 002, 003, and 004 in order.
- [x] Running the loader twice with the same run key is idempotent.
- [x] Staging row count is 4.
- [x] Curated fact row count is 4.
- [x] Quarterly periods remain distinct: `2023 Q1` and `2023 Q2`.
- [x] Canonical territories are `DEU` and `FRA`, not provider codes `DE` and `FR`.
- [x] Provider mappings exist for Eurostat periods and territories.
- [x] Provider code dictionaries exist for bounded fixture dimensions.
- [x] `curated.fact_observation` is not widened with provider-specific columns.
- [x] Full tests and ProjectForge coherence pass after governance/handoff updates.

## Explicit boundaries

Do not:

- write to live/default `macro`;
- live-fetch Eurostat inside loader tests;
- build a generalized JSON-stat framework;
- build a generalized source/plugin framework;
- broaden beyond the recorded bounded `namq_10_gdp` fixture;
- onboard FRED;
- add provider-specific fact columns;
- add aggregate membership history;
- implement unit conversion or canonical indicator ontology;
- add mart/research outputs;
- push to git.

## Notes

Use the OECD/SDMX source-specific PostgreSQL promotion as the implementation pattern, but adapt it to the TASK-022 canonical-domain period/territory/provider mapping schema.

## Outcome

TASK-024 implemented DEC-012 as a bounded source-specific Eurostat PostgreSQL loader.

Created:

- `db/migrations/004_eurostat_namq_staging.sql`
- `src/macroforge/eurostat_namq_loader.py`
- `tests/test_eurostat_namq_loader.py`
- `artifacts/reports/eurostat-namq-load-smoke-20260604.json`
- `simulation/dry_runs/20260604_170659-task-024-bounded-eurostat-loader-implementation.md`

Updated schema tests/docs/health checks to include the bounded Eurostat NAMQ staging table.

No live `macro` write, live Eurostat test fetch, generalized JSON-stat/source framework, FRED onboarding, provider-specific fact columns, aggregate membership history, or mart/research scope was introduced.

## Verification

```text
python3 tools/validate_dry_run.py simulation/dry_runs/20260604_170659-task-024-bounded-eurostat-loader-implementation.md

valid: simulation/dry_runs/20260604_170659-task-024-bounded-eurostat-loader-implementation.md

PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests/test_schema_foundation.py::test_eurostat_namq_staging_migration_exists_and_has_required_shape -q; PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests/test_eurostat_namq_loader.py::test_eurostat_namq_loader_builds_source_specific_sql_without_network -q

FAILED tests/test_schema_foundation.py::test_eurostat_namq_staging_migration_exists_and_has_required_shape
ImportError: cannot import name 'eurostat_namq_loader' from 'macroforge'

PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests/test_schema_foundation.py tests/test_eurostat_namq_loader.py -q

..........                                                               [100%]
10 passed in 1.41s

PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests -q

......................................                                   [100%]
38 passed in 3.25s
```
