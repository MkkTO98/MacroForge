# V0 Data Model

## PostgreSQL schemas

- `meta`: sources, releases, pipeline runs, lineage, quality checks.
- `staging`: normalized source-shaped observations.
- `curated`: canonical dimensions and facts.
- `mart`: future reporting/analysis layer; deferred from the first migration.

## Migration and health check

- Migration: `db/migrations/001_v0_schema_foundation.sql`
- Schema reference: `db/schema/v0_schema_foundation.md`
- Health check: `db/queries/schema_health_check.sql`

## Initial tables

### meta

- `meta.source`
- `meta.dataset_release`
- `meta.pipeline_run`
- `meta.lineage_event`
- `meta.quality_check`

### staging

- `staging.wdi_observation`

### curated

- `curated.dim_indicator`
- `curated.dim_territory`
- `curated.dim_period`
- `curated.dim_unit`
- `curated.dim_attribute_set`
- `curated.fact_observation`

## Fact grain

Initial candidate grain for `curated.fact_observation`:

`source_id + indicator_id + territory_id + period_id + unit_id + attribute_set_id + as_of_date`

## Modeling principles

- Preserve source differences instead of forcing premature merges.
- Do not overwrite historical vintages.
- Prefer natural keys plus `INSERT ... ON CONFLICT` for idempotency.
- Keep natural-key columns `NOT NULL` where uniqueness/idempotency depends on them.
- Avoid wide nullable fact tables.
- Use `attribute_set` for source-specific qualifiers.
- Add latest-vintage views later.
- Validate the model against WDI before generalizing to many providers.
