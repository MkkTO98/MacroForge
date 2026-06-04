# TASK-009 — Harden WDI vertical slice for rerunnable local operation

Status: completed
Created: 2026-06-03
Completed: 2026-06-03
Decision: DEC-005

## Goal

Make the existing WDI vertical slice easier and safer for future agents to rerun locally without relying on chat history or accidental environment assumptions.

## Scope

- Keep raw SQL/PostgreSQL/psql architecture from DEC-005.
- Do not load into a live `macro` database without explicit user approval and a fresh dry-run.
- Continue using the existing support bundle as live API evidence unless network permission is explicitly available.

## Acceptance criteria

- A single documented local command or script can run the isolated WDI smoke path end-to-end.
- The command/script creates an isolated database, applies migration, loads WDI rows twice, validates output, and cleans up.
- Tests cover the command/script or its core behavior.
- Existing test suite passes.
- Generated-project coherence passes.
- Handoff/state files are updated with exact verification output.

## Outcome

Implemented `src/macroforge/wdi_smoke.py` and documented this single-command rerun:

```bash
PYTHONPATH=src python3 -m macroforge.wdi_smoke --project-root .
```

The script creates a unique isolated `macroforge_wdi_smoke_*` database, applies the v0 schema migration, loads WDI rows twice with one run key, validates output, writes a smoke rerun report, and drops the isolated database in cleanup. It refuses `--db macro` to prevent accidental live database writes.

## Verification evidence

TDD RED:

```text
ImportError: cannot import name 'wdi_smoke' from 'macroforge'
```

Targeted tests after implementation:

```text
...                                                                      [100%]
3 passed in 0.01s
```

Live isolated smoke command:

```text
"status": "succeeded"
"loader_runs": 2
"cleanup": "dropdb --if-exists executed"
```

Full-suite/coherence evidence is recorded in `context/latest_handoff.md` after all current tasks.

## Notes

This task hardens the proven vertical slice; it must not introduce orchestration frameworks or broad source abstractions.
