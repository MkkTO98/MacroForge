# DEC-005 — Post-Vertical-Slice Architecture and Next Source Scope

Status: Accepted
Date: 2026-06-03
Task: TASK-008

## Decision

MacroForge will keep the current minimal raw-SQL/PostgreSQL/psql-based architecture for the immediate post-WDI hardening phase. Do not introduce Alembic, SQLAlchemy, Airflow, Dagster, Prefect, Docker, or a broad ingestion framework yet.

The next source/framework scope is:

1. Harden the existing WDI vertical slice first.
2. Add a small source-contract layer only where it removes duplication already proven by WDI.
3. Spike one no-key public second source with a different API/data shape before committing to broader source abstractions.
4. Treat OECD SDMX-style public data as the first second-source candidate because it should stress different source-shape concerns than World Bank WDI without requiring paid credentials. If live access or API friction blocks it, record evidence and choose another no-key candidate before implementation.

## Why

The first WDI vertical slice has proven the core data path:

- raw evidence artifacts and checksums
- normalized source rows
- PostgreSQL schema foundation
- idempotent staging and curated load
- lineage and quality checks
- validation reporting and runbook evidence

That is enough evidence to review architecture, but not enough evidence to design a universal ingestion framework. The current design is intentionally boring and inspectable. Introducing migration frameworks, ORM layers, or orchestration now would add abstraction before the project has observed a second source's real variation.

## Architectural choices

### Migration/tooling

Keep raw SQL migrations for now.

Rationale:

- The current schema is small and readable.
- Tests already verify schema invariants.
- Raw SQL keeps PostgreSQL semantics explicit for future agents.
- Migration tooling becomes more valuable once schema evolution requires ordered revisions, rollback policy, or multiple environments.

Deferred trigger for Alembic or another migration tool:

- more than one nontrivial schema revision after v0, or
- a need to apply ordered migrations repeatedly across multiple persistent databases, or
- rollback/upgrade workflow becomes harder to audit with plain SQL.

### Loader/interface

Keep the current psql/Python loader pattern for WDI, but extract a minimal source contract before implementing the second source.

The source contract should describe:

- source code and source name
- provider dataset code
- raw artifact metadata and checksum shape
- normalized observation row fields
- expected grain/frequency/as-of behavior
- validation checks required before curated load

Do not build a plugin registry or generalized orchestration layer until two sources have passed through the contract.

### Database model

Keep `meta`, `staging`, and `curated` as the authoritative foundation. Continue treating `mart` as deferred until there is a concrete report/query need.

For the next source, prefer reusing the existing curated observation model if the source is indicator/territory/period/value shaped. If the source's grain does not fit, create a decision record before altering the schema.

### Orchestration

Manual CLI + tests + runbooks remain the operating model. Scheduling and workflow orchestration are deferred until at least two manual source pipelines are reliable and rerunnable.

## Next tasks created by this decision

- TASK-009 — Harden WDI vertical slice for rerunnable local operation.
- TASK-010 — Define minimal source contract for second-source spike.
- TASK-011 — Spike no-key OECD/SDMX-style second source and decide whether to implement it.

## Non-goals

- No broad source framework yet.
- No paid or credentialed source in the next source spike.
- No live `macro` database load without explicit approval and a fresh dry-run.
- No orchestration platform until manual workflows are proven.
- No research brief layer until data substrate hardening is complete.

## Risks

- Staying with raw SQL may become cumbersome once schema evolution accelerates.
- A second source may expose grain or metadata needs not covered by the WDI-derived model.
- OECD/SDMX-style access may be more complex than expected; the spike must be allowed to fail and produce evidence rather than forcing implementation.

## Verification / evidence used

Context used:

- `CONSTITUTION.md`
- `instructions/GENERAL_INSTRUCTIONS.md`
- `context/context_policy.yaml`
- `context/active_context.md`
- `context/context_audit.md`
- `context/latest_handoff.md`
- `state/active_goal.md`
- `state/project_state.md`
- `state/architecture.md`
- `artifacts/tasks/TASK-008-review-architecture-after-first-vertical-slice.md`
- `artifacts/decisions/DEC-002-v1-scope-wdi-postgres-vertical-slice.md`
- `artifacts/decisions/DEC-004-v0-postgresql-schema-foundation.md`
- `docs/architecture/overview.md`
- `docs/roadmap.md`
- WDI implementation files: `src/macroforge/wdi.py`, `src/macroforge/wdi_loader.py`, `src/macroforge/wdi_validation.py`
- v0 schema: `db/migrations/001_v0_schema_foundation.sql`
- runbook/tests for the WDI vertical slice

The decision should be considered complete only after TASK-008 is marked complete and the project tests/coherence checks pass.
