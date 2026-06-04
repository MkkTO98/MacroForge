# DEC-004 — V0 PostgreSQL Schema Foundation

Status: Accepted for implementation planning
Date: 2026-06-02

## Decision

The v0 PostgreSQL foundation will be recreated cleanly using raw SQL migrations and tests. It will start with `meta`, `staging`, and `curated` schemas, with `mart` documented for later analytical/reporting use.

## Initial model

- `meta.source`
- `meta.dataset_release`
- `meta.pipeline_run`
- `meta.lineage_event`
- `meta.quality_check`
- `staging.wdi_observation`
- `curated.dim_indicator`
- `curated.dim_territory`
- `curated.dim_period`
- `curated.dim_unit`
- `curated.dim_attribute_set`
- `curated.fact_observation`

## Fact grain candidate

`source_id + indicator_id + territory_id + period_id + unit_id + attribute_set_id + as_of_date`

## Implementation constraints

- Recreate from this decision and tests, not old deleted files.
- Use idempotent SQL patterns such as natural keys and `INSERT ... ON CONFLICT`.
- Preserve vintage/as-of context; do not overwrite historical revisions.
- Verify with migration/schema tests before loading real data.
