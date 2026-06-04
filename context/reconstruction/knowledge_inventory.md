# MacroForge Knowledge Inventory

## High-confidence goals

MacroForge is an AI-first internal platform for macroeconomic and later equity/investing research. It starts as a PostgreSQL-backed macroeconomic data warehouse and expands only after data reliability is proven.

## Database and data model

Recommended v0 architecture:

- `meta`: source identity, dataset releases, pipeline runs, lineage, quality checks.
- `staging`: source-shaped normalized incoming observations.
- `curated`: canonical dimensions and revision-safe facts.
- `mart`: later analytical/reporting layer, not required in the first migration unless explicitly accepted.

Recommended v0 tables:

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

Candidate fact grain:

`source_id + indicator_id + territory_id + period_id + unit_id + attribute_set_id + as_of_date`

## First pipeline

World Bank WDI is the first v1 source because it is public, no-key, broad enough to exercise the data model, and lower-friction than UNPD/WPP endpoints that may require a token.

Initial smoke slice target: USA/DNK, GDP/population, years 2020-2021.

## Agent/governance model

Agents may inspect, plan, edit docs/code for accepted tasks, run tests, and produce evidence. They must pause for secrets, destructive actions, schema/architecture policy changes not covered by decisions, production data, billing, deployment, git push, or unresolved blocking questions.
