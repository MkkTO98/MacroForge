# TASK-023 — Design bounded Eurostat PostgreSQL promotion against canonical-domain schema

Status: complete
Created: 2026-06-04
Completed: 2026-06-04
Depends on: TASK-022
Governing decisions: DEC-009, DEC-010, DEC-011
Outcome decision: DEC-012
Design note: `docs/architecture/bounded-eurostat-postgresql-promotion-design.md`
Follow-on task: TASK-024

## Objective

Design, but do not yet implement, the smallest source-specific Eurostat PostgreSQL promotion path that uses the TASK-022 canonical-domain schema migration.

The design should answer whether the recorded Eurostat `namq_10_gdp` fixture can be promoted using:

- a source-specific `staging.eurostat_namq_observation` table,
- structured canonical quarterly periods in `curated.dim_period`,
- ISO3 country territories for DE/FR via provider territory mappings,
- provider period and territory mappings,
- provider code dictionaries for the bounded Eurostat dimensions needed by the fixture,
- `curated.dim_attribute_set` for seasonal adjustment and other provider qualifiers,
- unchanged `curated.fact_observation` grain.

## Explicit boundaries

- Do not implement the Eurostat migration yet.
- Do not write to live `macro`.
- Do not build a generalized JSON-stat/Eurostat ingestion framework.
- Do not broaden beyond the existing bounded `namq_10_gdp` fixture unless a blocking schema issue requires a tiny example.
- Do not add mart/research UI scope.

## Expected output

- architecture/design note,
- proposed source-specific staging table shape,
- provider mapping rows required for the fixture,
- validation/test plan,
- migration and loader risks,
- implementation task if the design is accepted.

## Outcome

TASK-023 accepted DEC-012: the recorded Eurostat `namq_10_gdp` fixture can be promoted through a narrow source-specific PostgreSQL path after TASK-022.

The design requires only:

- a future source-specific `staging.eurostat_namq_observation` migration;
- a future source-specific loader from the recorded normalized fixture;
- canonical quarterly periods for `2023-Q1` and `2023-Q2`;
- canonical country territories `DEU` and `FRA`;
- provider period/territory mappings;
- bounded provider code dictionaries;
- unchanged `curated.fact_observation`.

No migration or loader was implemented in TASK-023.

## Verification

```text
python3 tools/build_context.py --project . --model-target cloud --context-mode governance --task-type architecture_decision --task "TASK-023 bounded Eurostat PostgreSQL promotion design: design source-specific namq_10_gdp staging/load path against TASK-022 canonical-domain schema; no migration/loader implementation" --task-file artifacts/tasks/TASK-023-design-bounded-eurostat-postgresql-promotion.md --decisions DEC-009,DEC-010,DEC-011 --model-selected gpt-5.5 --model-reason "User approved next recommended bounded governance design step for Eurostat promotion"

{
  "context": "/home/mkkto/srv/projectforge/workspace/projects/macroforge/context/active_context.md",
  "audit": "/home/mkkto/srv/projectforge/workspace/projects/macroforge/context/context_audit.json",
  "estimated_tokens": 7942,
  "budget_tokens": 10000,
  "within_budget": true,
  "context_mode": "governance"
}

python3 tools/validate_dry_run.py simulation/dry_runs/20260604_165504-task-023-bounded-eurostat-postgresql-promotion-design.md

valid: simulation/dry_runs/20260604_165504-task-023-bounded-eurostat-postgresql-promotion-design.md
```
