# V0 Schema Foundation

TASK-004 creates the first PostgreSQL schema foundation for MacroForge. It is intentionally raw SQL, small, and WDI-oriented so the first vertical slice can prove provenance, grain, idempotency, and validation before adding migration-framework complexity.

## Default database

Use database name `macro` unless live verification proves otherwise.

## First source

World Bank WDI is the first v1 source.

## Migration

- `db/migrations/001_v0_schema_foundation.sql`

## Health check

- `db/queries/schema_health_check.sql`

## Schemas and tables

### meta

- `meta.source`: source/provider identity keyed by `source_code`.
- `meta.dataset_release`: provider dataset/release/raw artifact/checksum metadata keyed by `source_id`, `provider_dataset_code`, and `release_key`.
- `meta.pipeline_run`: pipeline run status and artifact manifest keyed by `run_key`.
- `meta.lineage_event`: raw/staging/curated lineage and checksum events.
- `meta.quality_check`: validation outcomes tied to a pipeline run.

### staging

- `staging.wdi_observation`: normalized source-shaped World Bank WDI observations keyed by `pipeline_run_id`, `country_code`, `indicator_code`, and `period_year`.

### curated

- `curated.dim_indicator`: source-scoped indicator dimension keyed by `source_id` and `source_indicator_code`.
- `curated.dim_territory`: source-scoped territory dimension keyed by `source_id` and `iso3_code`.
- `curated.dim_period`: frequency/year period dimension keyed by `frequency` and `period_year`.
- `curated.dim_unit`: unit dimension keyed by `unit_code`.
- `curated.dim_attribute_set`: JSONB qualifier/attribute dimension keyed by `attribute_hash`.
- `curated.fact_observation`: canonical observation fact keyed by `source_id`, `indicator_id`, `territory_id`, `period_id`, `unit_id`, `attribute_set_id`, and `as_of_date`.

## Idempotency and revision principles

- Natural keys are explicit unique constraints.
- Columns participating in uniqueness are `NOT NULL` where idempotency depends on them.
- `as_of_date` is `NOT NULL` for facts so historical/revision context is not overwritten.
- `attribute_set` keeps source-specific qualifiers out of wide nullable fact columns.
- Loader implementation should use `INSERT ... ON CONFLICT` patterns; the migration includes a WDI source upsert example as a reminder.

## Deferred hardening

- Composite constraints to enforce source consistency between facts and source-scoped dimensions may be added after WDI proves the model.
- `mart` schema/views are deferred until validated analytical queries exist.
- Alembic or another migration framework is deferred until manual raw SQL migrations become painful.
