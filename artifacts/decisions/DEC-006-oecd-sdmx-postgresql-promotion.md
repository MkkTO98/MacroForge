# DEC-006 — OECD/SDMX PostgreSQL Promotion

Status: Accepted
Date: 2026-06-03
Task: TASK-014
Preceded by: TASK-013
Governing context: DEC-004, DEC-005, TASK-010 source contract, TASK-012/TASK-013 OECD/SDMX evidence

## Decision

Promote the bounded OECD/SDMX source-specific evidence slice toward PostgreSQL, but only after a narrow schema migration adds an OECD/SDMX staging table.

The existing curated observation model can represent the bounded OECD/SDMX facts without curated schema changes because its fact grain already includes `unit_id` and `attribute_set_id`:

`source_id + indicator_id + territory_id + period_id + unit_id + attribute_set_id + as_of_date`

However, the current permanent staging table is `staging.wdi_observation`, and its natural key is WDI-specific:

`pipeline_run_id + country_code + indicator_code + period_year`

That staging shape cannot safely represent the live OECD/SDMX bounded slice because TASK-013 evidence contains two rows for the same indicator/territory/period when `UNIT_MEASURE` differs (`USD_EXC` and `USD_PPP`). Therefore, the smallest justified schema change is a source-specific staging table for OECD/SDMX observations. No curated schema change is accepted by this decision.

## Required schema direction

Create a narrow second migration in the follow-on implementation task. Do not rewrite `db/migrations/001_v0_schema_foundation.sql`.

Expected new staging table:

`staging.oecd_sdmx_observation`

Minimum columns should include:

- `oecd_sdmx_observation_id uuid primary key default gen_random_uuid()`
- `pipeline_run_id uuid not null references meta.pipeline_run(pipeline_run_id)`
- `source_id uuid not null references meta.source(source_id)`
- `dataset_release_id uuid references meta.dataset_release(dataset_release_id)`
- `provider_dataset_code text not null`
- `measure_code text not null`
- `ref_area_code text not null`
- `period_year integer not null`
- `frequency text not null`
- `unit_measure_code text not null`
- `value numeric`
- `observation_status text not null default 'observed'`
- `decimal_precision integer`
- `attributes jsonb not null default '{}'::jsonb`
- `series_dimensions jsonb not null default '{}'::jsonb`
- `source_payload jsonb not null default '{}'::jsonb`
- `as_of_date date not null`
- `created_at timestamptz not null default now()`

Minimum natural key:

`pipeline_run_id + provider_dataset_code + measure_code + ref_area_code + period_year + unit_measure_code`

This is intentionally source-specific. It is not a generic SDMX staging framework.

## Required loader direction

The follow-on loader should be source-specific and patterned after `src/macroforge/wdi_loader.py` only where that keeps the workflow boring and auditable:

- build SQL from the existing normalized OECD JSON evidence,
- upsert `meta.source` with `source_code = 'OECD_NAAG'`,
- upsert `meta.dataset_release` using the provider dataset code and a deterministic release key,
- upsert one `meta.pipeline_run`,
- load `staging.oecd_sdmx_observation`,
- upsert curated dimensions and facts,
- record lineage and quality checks,
- verify idempotent rerun behavior in an isolated temporary database.

The loader must not fetch live data itself for the database smoke. It should load from `data/metadata/oecd_sdmx/oecd-sdmx-smoke-normalized.json` so database tests remain no-network and reproducible. Live fetching remains the job of `src/macroforge/oecd_sdmx.py` from TASK-013.

## Answers to TASK-014 required questions

### 1. Does the current curated fact grain fit OECD/SDMX observations?

Yes for the bounded slice. The current curated fact grain includes `unit_id` and `attribute_set_id`, which are enough to distinguish the observed OECD/SDMX rows.

The live evidence contains 8 rows because `UNIT_MEASURE` has both `USD_EXC` and `USD_PPP` for the same `MEASURE`, `REF_AREA`, and `TIME_PERIOD`. Those should become distinct curated facts through different `unit_id` values.

No curated schema change is required for the bounded promotion.

### 2. Is `MEASURE=B1GQ` the right `indicator_code`, and should `UNIT_MEASURE` map to `curated.dim_unit`?

Yes.

- `MEASURE` maps to `curated.dim_indicator.source_indicator_code`.
- `B1GQ` is the correct source indicator code for the bounded slice.
- `UNIT_MEASURE` maps to `curated.dim_unit.unit_code`.
- `USD_EXC` and `USD_PPP` are separate units and must not be collapsed.

For now, `unit_name` may equal the unit code until a later codelist-label task justifies enrichment.

### 3. What should happen to SDMX dimensions not present in WDI?

At current maturity:

- `REF_AREA` maps to `curated.dim_territory.iso3_code` and staging `ref_area_code`.
- `MEASURE` maps to `curated.dim_indicator.source_indicator_code` and staging `measure_code`.
- `FREQ` maps to `curated.dim_period.frequency` and staging `frequency`.
- `UNIT_MEASURE` maps to `curated.dim_unit.unit_code` and staging `unit_measure_code`.
- Other series dimensions such as `CHAPTER` remain in staging `series_dimensions` and fact `source_payload`; they do not become first-class curated dimensions yet.
- Dimensions that are absent from the current smoke but may appear in future OECD slices, such as `ADJUSTMENT`, should be preserved in JSON first. They become schema candidates only if they are required to prevent duplicate facts or support a concrete query/report.

### 4. Which SDMX attributes should map into `curated.dim_attribute_set`?

For v1 scope, map the observed SDMX observation attributes into `curated.dim_attribute_set.attributes`:

- `CONF_STATUS`
- `DECIMALS`
- `OBS_STATUS`

The attribute hash should be computed from a canonical JSON representation of the attributes.

`OBS_STATUS` should also drive `curated.fact_observation.observation_status` with this minimal mapping:

- observed/non-empty ordinary values, including current `OBS_STATUS = 'A'`, map to `observed`
- source values indicating missing/suppressed data should map to `missing` or `suppressed` when encountered
- unknown codes should remain preserved in `dim_attribute_set.attributes` even if the fact status defaults conservatively

### 5. How should release/as-of behavior be derived?

For the bounded promotion, use a deterministic source-specific release key derived from the raw evidence metadata rather than pretending the endpoint exposes a semantic release timestamp.

Recommended release key shape:

`OECD_NAAG:<provider_dataset_code>:<start_period>-<end_period>:<raw_sha256_prefix>`

Recommended `as_of_date`:

- use the UTC date of the evidence/run when available in artifact metadata, or
- use the date embedded in the smoke artifact/report filename for this bounded slice, currently `2026-06-03`.

The full raw SHA-256, endpoint, byte count, content type, filters, row count, and units should be stored in `meta.dataset_release.metadata` and `meta.pipeline_run.artifact_manifest`.

### 6. Should PostgreSQL promotion use a source-specific loader patterned after `wdi_loader.py`?

Yes, but source-specific only.

Use the WDI loader as a boring implementation pattern, not as a generalized abstraction. A future refactor can extract common helper functions only after the OECD loader has passed isolated database tests and real duplication is visible.

Do not create a plugin registry, abstract source base class, generalized SDMX loader, orchestration framework, ORM layer, or migration framework in the follow-on task.

### 7. If schema change is justified, what is the smallest explicit schema decision needed?

A new source-specific staging table is justified:

`staging.oecd_sdmx_observation`

No curated schema change is justified. No `mart` schema work is justified. No generalized staging table is justified yet.

## Follow-on task

Open TASK-015 to implement the narrow migration and source-specific loader:

`artifacts/tasks/TASK-015-implement-oecd-sdmx-postgresql-loader.md`

TASK-015 must use an isolated temporary PostgreSQL database for verification and must refuse or avoid live `macro` database writes.

## Non-goals

- No live `macro` database write.
- No generalized SDMX ingestion framework.
- No plugin registry or source abstraction layer.
- No Alembic, SQLAlchemy, Dagster, Airflow, Prefect, Docker, or scheduling.
- No codelist-label enrichment beyond preserving codes and JSON attributes.
- No research/mart/reporting layer.
- No paid or credentialed APIs.
- No git push.

## Risks

- OECD release/as-of semantics remain approximate until a source-specific release metadata endpoint or codelist strategy is added.
- Code-only units/attributes are sufficient for current storage but weak for human-facing analysis.
- A source-specific staging table creates some duplication with WDI loader patterns; this is accepted until two database-backed sources prove which pieces are genuinely common.
- The raw live OECD payload checksum may change between upstream responses. The database smoke should load from recorded normalized evidence unless a separate live-rerun task is explicitly opened.

## Verification / evidence used

Context used:

- `CONSTITUTION.md`
- `instructions/GENERAL_INSTRUCTIONS.md`
- `context/context_policy.yaml`
- `context/latest_handoff.md`
- `state/active_goal.md`
- `state/project_state.md`
- `state/architecture.md`
- `artifacts/tasks/TASK-014-design-oecd-sdmx-postgresql-promotion.md`
- `artifacts/tasks/TASK-013-harden-oecd-sdmx-live-rerunnable-smoke-command.md`
- `artifacts/decisions/DEC-004-v0-postgresql-schema-foundation.md`
- `artifacts/decisions/DEC-005-post-vertical-slice-architecture-and-next-source-scope.md`
- `docs/data/source-contract.md`
- `db/migrations/001_v0_schema_foundation.sql`
- `src/macroforge/wdi_loader.py`
- `tests/test_wdi_loader.py`
- `src/macroforge/oecd_sdmx.py`
- `data/metadata/oecd_sdmx/oecd-sdmx-smoke-normalized.json`
- `artifacts/reports/oecd-sdmx-smoke-20260603.md`
- `artifacts/reports/oecd-sdmx-live-smoke-20260603.md`

Final project verification is recorded in TASK-014, `state/project_state.md`, and `context/latest_handoff.md` after governance updates.
