# V0 Schema Foundation

TASK-004 creates the first PostgreSQL schema foundation for MacroForge. It is intentionally raw SQL, small, and WDI-oriented so the first vertical slice can prove provenance, grain, idempotency, and validation before adding migration-framework complexity.

## Default database

Use database name `macro` unless live verification proves otherwise.

## First source

World Bank WDI is the first v1 source.

## Migration

- `db/migrations/001_v0_schema_foundation.sql`
- `db/migrations/002_oecd_sdmx_staging.sql` adds the bounded DEC-006/TASK-015 source-specific OECD/SDMX staging table.
- `db/migrations/003_canonical_domain_dimensions.sql` extends the v0 foundation with the bounded DEC-011 canonical-domain dimension changes.
- `db/migrations/004_eurostat_namq_staging.sql` adds only the bounded DEC-012 source-specific Eurostat `namq_10_gdp` staging table.

## Health check

- `db/queries/schema_health_check.sql`

## Schemas and tables

### meta

- `meta.source`: source/provider identity keyed by `source_code`.
- `meta.dataset_release`: provider dataset/release/raw artifact/checksum metadata keyed by `source_id`, `provider_dataset_code`, and `release_key`.
- `meta.pipeline_run`: pipeline run status and artifact manifest keyed by `run_key`.
- `meta.lineage_event`: raw/staging/curated lineage and checksum events.
- `meta.quality_check`: validation outcomes tied to a pipeline run.
- `meta.provider_period_mapping`: provider period-code to canonical `curated.dim_period` mapping.
- `meta.provider_territory_mapping`: provider territory-code to canonical `curated.dim_territory` mapping.
- `meta.provider_code_list`: minimal provider code dictionary/list metadata.
- `meta.provider_code`: provider code values and labels for bounded mapping/audit needs.

### staging

- `staging.wdi_observation`: normalized source-shaped World Bank WDI observations keyed by `pipeline_run_id`, `country_code`, `indicator_code`, and `period_year`.
- `staging.oecd_sdmx_observation`: bounded source-specific OECD/SDMX observations keyed by pipeline run plus provider dataset, measure, reference area, annual period, and unit measure codes.
- `staging.eurostat_namq_observation`: bounded source-specific Eurostat `namq_10_gdp` observations keyed by pipeline run plus provider dataset/frequency/unit/seasonal adjustment/national accounts item/geography/period codes.

### curated

- `curated.dim_indicator`: source-scoped indicator dimension keyed by `source_id` and `source_indicator_code`.
- `curated.dim_territory`: canonical territory dimension. TASK-022 evolves it to preserve ISO3 for `country` rows and add bounded `territory_type` support for optional `economic_area` / `aggregate` rows.
- `curated.dim_period`: canonical period dimension. TASK-022 evolves it from annual frequency/year rows to structured annual, quarterly, monthly, and daily-ready interval rows.
- `curated.dim_unit`: unit dimension keyed by `unit_code`.
- `curated.dim_attribute_set`: JSONB qualifier/attribute dimension keyed by `attribute_hash`.
- `curated.fact_observation`: canonical observation fact keyed by `source_id`, `indicator_id`, `territory_id`, `period_id`, `unit_id`, `attribute_set_id`, and `as_of_date`.

## Idempotency and revision principles

- Natural keys are explicit unique constraints.
- Columns participating in uniqueness are `NOT NULL` where idempotency depends on them.
- `as_of_date` is `NOT NULL` for facts so historical/revision context is not overwritten.
- `attribute_set` keeps source-specific qualifiers out of wide nullable fact columns.
- Provider period/territory/code values live in `meta` mapping/dictionary tables, not as canonical dimension identities.
- `curated.fact_observation` remains source-agnostic; TASK-022 does not add provider-specific fact columns.
- TASK-024 promotes only the recorded Eurostat `namq_10_gdp` fixture through a source-specific staging table and provider mappings; it does not broaden into a JSON-stat/source framework.
- Loader implementation should use `INSERT ... ON CONFLICT` patterns; the migration includes a WDI source upsert example as a reminder.

## Deferred hardening

- Composite constraints to enforce source consistency between facts and source-scoped dimensions may be added after WDI proves the model.
- `mart` schema/views are deferred until validated analytical queries exist.
- Alembic or another migration framework is deferred until manual raw SQL migrations become painful.
