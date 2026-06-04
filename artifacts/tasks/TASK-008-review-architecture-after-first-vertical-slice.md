# TASK-008 — Review architecture after first vertical slice

Acceptance: decision record for next source/framework scope. Status: completed.

Completed: 2026-06-03
Decision: `artifacts/decisions/DEC-005-post-vertical-slice-architecture-and-next-source-scope.md`

## Outcome

The post-vertical-slice architecture review is recorded in DEC-005.

Summary:

- Keep the current minimal raw-SQL/PostgreSQL/psql-based architecture for immediate hardening.
- Do not introduce Alembic, SQLAlchemy, orchestration, Docker, or a broad ingestion framework yet.
- Harden the WDI vertical slice first.
- Define only a minimal source contract before the second-source spike.
- Use a no-key OECD/SDMX-style source as the first second-source spike candidate, with fallback allowed if live access or API friction blocks it.

## Follow-up tasks

- TASK-009 — Harden WDI vertical slice for rerunnable local operation.
- TASK-010 — Define minimal source contract for second-source spike.
- TASK-011 — Spike no-key OECD/SDMX-style second source.

## Notes

Follow ProjectForge startup context rules. Run relevant tests before marking complete. Record decisions for durable changes.
