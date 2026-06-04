# TASK-014 — Design OECD/SDMX PostgreSQL promotion

Status: completed
Created: 2026-06-03
Completed: 2026-06-03
Preceded by: TASK-013
Decision context: DEC-005, TASK-010 source contract, TASK-012/TASK-013 OECD/SDMX evidence
Dry-run/preflight: `simulation/dry_runs/20260603_214803-open-task-014-oecd-postgresql-promotion-design.md`

## Goal

Decide whether and how the bounded OECD/SDMX evidence slice should be promoted from filesystem evidence/rerun smoke into PostgreSQL staging and curated modeling.

This is a design/governance task. It must produce an explicit decision before any loader implementation, schema migration, live `macro` database write, or generalized SDMX framework work begins.

## Background

TASK-012 proved MacroForge can parse and normalize a source-specific SDMX GenericData XML slice into the minimal source contract.

TASK-013 proved the same slice can be rerun against the live no-key OECD endpoint and written to stable MacroForge project-layout evidence paths.

Live bounded evidence currently returns 8 rows for:

- `REF_AREA in {AUS, USA}`
- `MEASURE = B1GQ`
- periods 2020-2021

The 8-row count is caused by multiple `UNIT_MEASURE` values, currently observed as:

- `USD_EXC`
- `USD_PPP`

That makes canonical grain and unit handling the immediate design pressure before database promotion.

## Scope

In scope:

- Inspect current v0 PostgreSQL schema, WDI loader behavior, source contract, and OECD/SDMX normalized metadata/report evidence.
- Decide whether the existing curated observation model can represent the OECD/SDMX slice without schema changes.
- Decide canonical grain for OECD/SDMX rows, especially whether `UNIT_MEASURE` participates through the existing `curated.dim_unit` / `unit_id` grain or requires source-specific treatment.
- Decide how SDMX codelist codes and observation attributes should be represented at the current maturity level.
- Decide whether a narrow source-specific OECD loader task is justified next, and if so define its boundaries and acceptance criteria.
- Produce a decision artifact, expected next task artifact(s), and updated state/handoff/roadmap/backlog pointers.

Out of scope:

- Writing OECD/SDMX loader code.
- Changing `db/migrations/001_v0_schema_foundation.sql` or adding a new migration.
- Writing to a live `macro` database.
- Creating generalized SDMX plugin/framework abstractions.
- Adding codelist label enrichment unless the design concludes it is required for safe PostgreSQL promotion.
- Adding orchestration, Docker, Alembic, SQLAlchemy, Dagster/Airflow/Prefect, or scheduling.
- Paid, credentialed, or production API use.
- Git push.

## Required questions to answer

1. Does the current curated fact grain from DEC-004/TASK-006 fit OECD/SDMX observations?
   - Current conceptual grain: source + indicator + territory + period + unit + attribute set + as-of/release.
2. Is `MEASURE=B1GQ` the right `indicator_code`, and should `UNIT_MEASURE` map directly to `curated.dim_unit`?
3. What should happen to SDMX dimensions not present in WDI, including `UNIT_MEASURE`, `ADJUSTMENT`, `REF_AREA`, and any dataset/series dimensions preserved in source payload?
4. Which SDMX attributes should map into `curated.dim_attribute_set` or equivalent source payload fields at v1 scope?
   - Consider `CONF_STATUS`, `DECIMALS`, `OBS_STATUS`, and any other observed attributes.
5. How should OECD/SDMX release/as-of behavior be derived if the live endpoint does not expose a clean release timestamp in the normalized smoke output?
6. Should PostgreSQL promotion use a source-specific loader patterned after `wdi_loader.py`, or should the project stop at filesystem evidence until a second design input is available?
7. If schema change is justified, what is the smallest explicit schema decision needed before implementation?

## Expected deliverables

- New decision artifact, expected name:
  - `artifacts/decisions/DEC-006-oecd-sdmx-postgresql-promotion.md`
- If promotion is accepted, a new implementation task, expected name:
  - `artifacts/tasks/TASK-015-implement-oecd-sdmx-postgresql-loader.md`
- If promotion is deferred/rejected, a task or note that clearly states what evidence would change the decision.
- Updated backlog, active goal, project state, architecture state, roadmap, latest handoff, and affected folder summaries.

## Acceptance criteria

- Decision artifact explicitly answers all required questions above.
- Decision states one of:
  - promote OECD/SDMX with the current schema,
  - promote OECD/SDMX only after a schema change decision,
  - defer PostgreSQL promotion and keep OECD/SDMX as evidence/rerun smoke.
- If promotion is accepted, the follow-on task includes precise boundaries: source-specific loader only, isolated smoke database only, no live `macro` writes without explicit approval, no generalized framework.
- If schema change is proposed, the decision identifies the exact schema pressure and forbids implementation until a migration task exists.
- No code, schema, database, or live-source artifact changes are made by this design task except optional read-only inspection/rerun evidence if explicitly needed and safe.
- Full test suite passes.
- Generated-project coherence passes.

## Verification plan

Run after completing the design artifacts and state updates:

```bash
PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests -q
python3 tools/check_coherence.py --project . --json
```

If summaries are refreshed after state edits, run final verification after the summary updates.

## Notes

Keep the design boring and source-specific. DEC-005 still forbids broad ingestion abstractions until evidence from multiple sources proves they are necessary.

## Outcome

Completed the OECD/SDMX PostgreSQL promotion design.

Decision artifact:

- `artifacts/decisions/DEC-006-oecd-sdmx-postgresql-promotion.md`

DEC-006 accepts PostgreSQL promotion only after a narrow source-specific staging schema migration. The existing curated observation model can represent the bounded OECD/SDMX facts because `unit_id` and `attribute_set_id` are already part of the fact grain, but the current permanent staging table is WDI-specific and cannot safely represent duplicate indicator/territory/period rows that differ by `UNIT_MEASURE`.

Smallest accepted schema change:

- add `staging.oecd_sdmx_observation` in a new migration;
- do not rewrite `db/migrations/001_v0_schema_foundation.sql`;
- do not change curated tables.

Follow-on task opened:

- `artifacts/tasks/TASK-015-implement-oecd-sdmx-postgresql-loader.md`

TASK-015 is bounded to a source-specific migration and loader that loads recorded normalized OECD evidence into an isolated PostgreSQL smoke database. It must not write to live `macro`, fetch live OECD data inside database tests, or create a generalized SDMX framework.

## Decision summary

- Promote OECD/SDMX toward PostgreSQL, but only with a narrow source-specific staging migration first.
- `MEASURE=B1GQ` maps to curated indicator code.
- `UNIT_MEASURE` maps to curated unit code; `USD_EXC` and `USD_PPP` remain distinct facts.
- Observed attributes (`CONF_STATUS`, `DECIMALS`, `OBS_STATUS`) map into `curated.dim_attribute_set` and remain preserved as JSON.
- Existing curated fact grain fits the bounded source slice.
- Release/as-of semantics use deterministic recorded evidence metadata for now; do not invent a semantic OECD release timestamp.

## Final verification evidence

```text
PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests -q
python3 tools/check_coherence.py --project . --json

......................                                                   [100%]
22 passed in 1.40s
{
  "mode": "generated",
  "blocks": [],
  "warnings": []
}
```
