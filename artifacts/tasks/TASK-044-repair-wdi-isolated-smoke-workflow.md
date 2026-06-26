# TASK-044 — Repair WDI isolated smoke workflow

Status: complete
Date: 2026-06-26

## Objective

Resolve the first operational pre-freeze blocker from `artifacts/reports/R-20260619-operational-capability-validation.md`: the WDI-only isolated smoke workflow was stale because it applied only migration `001_v0_schema_foundation.sql` while the current WDI loader requires canonical-domain columns introduced by `003_canonical_domain_dimensions.sql`.

## Scope

Minimal operational hardening only:

- keep the WDI source-specific isolated smoke workflow;
- keep isolated temporary PostgreSQL execution and live `macro` refusal;
- do not change WDI loader semantics;
- do not add sources, schemas, migrations, frameworks, conversion, aggregation, report integration, model calls, or live/default database writes.

## Implementation summary

Updated `src/macroforge/wdi_smoke.py` so the isolated WDI smoke plan applies the current WDI-required migrations in order:

1. `db/migrations/001_v0_schema_foundation.sql`
2. `db/migrations/003_canonical_domain_dimensions.sql`

Updated `tests/test_wdi_smoke.py` to cover the ordered migration list and execution order.

Updated `docs/runbooks/wdi-v1-runbook.md` so the documented single-command and manual WDI smoke procedure match the repaired workflow.

## Verification

TDD RED before implementation:

```text
AttributeError: 'SmokePlan' object has no attribute 'migration_paths'
```

Targeted tests:

```text
uvx --from pytest --with pyyaml pytest tests/test_wdi_smoke.py -q
3 passed in 0.02s
```

Compile check:

```text
python3 -m py_compile src/macroforge/wdi_smoke.py
<no output; exit 0>
```

Operational WDI isolated smoke:

```text
PYTHONPATH=src python3 -m macroforge.wdi_smoke --project-root . --report /tmp/macroforge-task044-wdi-isolated-smoke.json
```

Observed result:

```text
status: succeeded
loader_runs: 2
expected_rows: 8
validation status: pass
staging_rows: 8
fact_rows: 8
lineage_events: 2
quality_checks: 2
cleanup: dropdb --if-exists executed
```

## Outcome

TASK-044 is complete. The WDI-only isolated smoke workflow no longer fails on missing canonical-domain columns and now applies the current required WDI schema state before loading/validation.

The second operational pre-freeze blocker remains open: OECD/Eurostat bounded source fixture persistence must be made clean-clone safe.
