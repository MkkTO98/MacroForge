# TASK-017 — Harden shared validation and loader reporting

Status: complete
Created: 2026-06-03
Preceded by: TASK-016
Governing decision: DEC-007

## Goal

Harden the two proven database-backed smoke paths by extracting tiny shared mechanical helpers and standardizing validation/reporting conventions across WDI and OECD/SDMX.

This is a bounded implementation hardening task. It is not a source framework task.

## Why now

TASK-016/DEC-007 found that WDI and OECD/SDMX now prove real, concrete duplication in local helper/reporting mechanics:

- SQL literal and JSONB literal rendering;
- temporary SQL-file execution through `psql -v ON_ERROR_STOP=1`;
- scalar/count queries through `psql -At`;
- JSON report writing with task/status/count payloads;
- isolated PostgreSQL idempotency smoke reporting;
- duplicate curated-grain and quality-check validation patterns.

The duplication is mechanical enough to harden, but source semantics are still different enough to keep WDI and OECD/SDMX source-specific.

## Required first step

Begin with a fresh implementation dry-run before changing code:

- classify risk as medium;
- list exact source/test/report files to modify;
- confirm no schema changes, live fetches, live `macro` writes, or generalized framework work;
- validate the dry-run with `python3 tools/validate_dry_run.py <path>`.

## Scope

In scope:

- Add a tiny shared utility module if useful, for example under `src/macroforge/`.
- Move only mechanical helpers such as:
  - SQL literal rendering;
  - JSONB literal rendering;
  - temporary SQL-file `psql` execution;
  - scalar/count `psql` calls;
  - JSON report writing with stable task/status fields.
- Standardize validation/report envelopes where source semantics allow it.
- Add or update tests before refactoring implementation.
- Preserve WDI and OECD/SDMX current loader behavior and report counts.
- Preserve isolated PostgreSQL smoke/idempotency checks.

Out of scope:

- New source onboarding.
- Generalized source framework.
- Generalized SDMX framework.
- Plugin registry or source base class.
- Loader orchestration framework.
- Alembic, SQLAlchemy, Airflow, Dagster, Prefect, Docker, or scheduling.
- Schema changes or migration rewrites.
- Live data fetches.
- Live `macro` database writes.
- Mart/research layer work.
- Paid, credentialed, or production API use.
- Git push.

## Acceptance criteria

- Fresh implementation dry-run is created and validated.
- Tests are added/updated before behavior-preserving refactor work.
- Shared helper surface stays mechanical and small.
- WDI loader/report behavior remains compatible with current reports/tests.
- OECD/SDMX loader/report behavior remains compatible with current reports/tests.
- Isolated PostgreSQL idempotency tests still pass for both sources when PostgreSQL is available.
- No source/schema/framework behavior changes are introduced.
- Full test suite passes.
- Generated-project coherence passes.
- Task/state/handoff/summaries are updated on completion per `context/context_policy.yaml`.

## Verification plan

Run after implementation and governance updates:

```bash
PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests -q
python3 tools/check_coherence.py --project . --json
```

If recording verification output changes state/handoff, run a final coherence-only check:

```bash
python3 tools/check_coherence.py --project . --json
```

## Notes

Keep helper extraction boring. If the code starts needing source registration, inheritance, plugin lookup, generated SQL templates per source type, or generic SDMX concepts, stop and open a new design decision instead of expanding TASK-017.

## Outcome

Completed 2026-06-04.

Implemented a bounded, behavior-preserving hardening pass:

- Created and validated the fresh medium-risk implementation dry-run at `simulation/dry_runs/20260604_073353-implement-task-017-shared-validation-loader-reporting.md`.
- Added `src/macroforge/db_helpers.py` as a tiny mechanical helper module only.
- Added `tests/test_db_helpers.py` before production-code implementation and verified RED first because `macroforge.db_helpers` did not exist.
- Extracted SQL literal rendering, JSONB literal rendering, temporary `psql -v ON_ERROR_STOP=1 -f` execution, scalar `psql -At` calls, integer/count parsing, pipe-delimited count parsing, and JSON report writing.
- Updated `wdi_loader.py`, `oecd_sdmx_loader.py`, and `wdi_validation.py` to use the shared helpers while preserving source-specific SQL generation, loader entrypoints, report defaults, counts, schemas, and tests.
- Opened TASK-018 as a governance follow-up to decide the next bounded source/data-reliability scope after TASK-017 evidence.

No schema changes, migration rewrites, live fetches, live `macro` writes, generalized source/SDMX framework, plugin registry, source base class, ORM, orchestration, dependency install, or git push were introduced.

## Verification evidence

Dry-run validation:

```text
python3 tools/validate_dry_run.py simulation/dry_runs/20260604_073353-implement-task-017-shared-validation-loader-reporting.md

valid: simulation/dry_runs/20260604_073353-implement-task-017-shared-validation-loader-reporting.md
```

RED check before implementation:

```text
PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests/test_db_helpers.py -q

ImportError: cannot import name 'db_helpers' from 'macroforge'
```

Targeted GREEN check after helper implementation and loader/validation refactor:

```text
PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests/test_db_helpers.py tests/test_wdi_loader.py tests/test_oecd_sdmx_loader.py tests/test_wdi_validation.py -q

.........                                                                [100%]
9 passed in 1.75s
```

Full test suite after implementation:

```text
PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests -q

.............................                                            [100%]
29 passed in 2.09s
```

Generated-project coherence after implementation:

```text
python3 tools/check_coherence.py --project . --json

{
  "mode": "generated",
  "blocks": [],
  "warnings": []
}
```
