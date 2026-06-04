# DEC-007 — Post-Second-Source Architecture and Next Scope

Status: Accepted
Date: 2026-06-03
Task: TASK-016
Preceded by: TASK-015
Governing context: DEC-002, DEC-005, DEC-006, TASK-016 governance context bundle

## Decision

MacroForge will keep the current source-specific, raw-SQL/PostgreSQL/psql-based architecture for the next bounded step, but the second database-backed source now justifies one narrow hardening/refactor task: extract tiny shared execution/reporting helpers and standardize validation/report shape across the WDI and OECD/SDMX smoke loaders.

Do not build a generalized source framework, generalized SDMX framework, plugin registry, ORM layer, migration framework, orchestration platform, Docker dependency, scheduler, or mart/research layer yet.

The immediate follow-on task is:

- TASK-017 — Harden shared validation and loader reporting.

TASK-017 is allowed to reduce proven duplication in local helper/reporting code, but it must not change source semantics, staging schemas, curated schema, loader outputs, live data behavior, or database target policy.

## Answers to TASK-016 required questions

### 1. Do WDI + OECD/SDMX justify extracting a tiny shared loader helper now?

Yes, but only a tiny helper layer is justified.

Observed duplication is concrete and mechanical:

- both loaders define `sql_literal` and `json_literal`;
- both loaders write generated SQL to a temporary file and run `psql -v ON_ERROR_STOP=1`;
- both loaders query scalar/count summaries with `psql -At`;
- both loaders write JSON reports with task/status/count payloads;
- both loader test suites verify no-network SQL construction and isolated PostgreSQL idempotency.

This justifies extracting small local utilities such as SQL literal rendering, JSONB literal rendering, temp-file psql execution, scalar psql calls, and report writing. It does not justify a source abstraction, base class, registry, common loader template, or generalized ingestion engine. WDI and OECD/SDMX still have different raw evidence formats, staging shapes, release-key rules, unit handling, attribute handling, and operational commands.

### 2. Does having two source-specific staging tables justify migration-tooling changes?

No. Keep raw SQL migrations for now.

The project has two ordered SQL migrations:

- `001_v0_schema_foundation.sql`
- `002_oecd_sdmx_staging.sql`

That is enough to require clearer migration application discipline in tests/runbooks, but not enough to introduce Alembic or another migration framework. Raw SQL remains more legible for future agents and keeps PostgreSQL semantics explicit.

Migration tooling should be reconsidered only if one of these triggers occurs:

- a third nontrivial schema migration is needed after `002`;
- persistent databases need repeatable upgrade/rollback procedures across environments;
- migration ordering or partial-application state becomes hard to audit with plain SQL;
- multiple agents begin editing schema concurrently;
- rollback/downgrade policy becomes a real operational need.

### 3. Should validation/reporting be hardened next, and should it be source-specific or shared?

Yes. Validation/reporting is the best next hardening target.

WDI currently has a separate validation module and isolated smoke wrapper. OECD/SDMX has strong loader tests and quality checks, but its validation/reporting shape is less standardized. The second source exposes a useful pattern: keep source-specific checks where source semantics differ, while sharing report envelope, psql execution helpers, duplicate-grain checks, quality-check status checks, and idempotency smoke reporting conventions.

TASK-017 should therefore produce a small shared validation/reporting surface, not a shared loader framework.

### 4. Should the next source task be a third-source spike, codelist enrichment, runbook hardening, or research-layer work?

Not yet. Do validation/reporting hardening first.

A third-source spike would create more variation, but current evidence already shows enough operational duplication and reporting inconsistency to harden before broadening. Codelist/label enrichment is valuable but should follow once report/validation shape is consistent. Research-layer work remains premature until the data substrate has reliable rerun/validation conventions for at least two sources.

Recommended sequencing:

1. TASK-017 — shared validation/reporting helper hardening.
2. Then either codelist/label enrichment for OECD/SDMX or a bounded third-source spike, decided after TASK-017 evidence.
3. Research/mart layer only after data reliability, source metadata, and validation conventions are stronger.

### 5. What exact triggers would justify a generalized source/SDMX framework later?

A generalized framework may be reconsidered only if at least two of the following are true:

- three or more database-backed sources have passed through raw evidence, normalized metadata, staging, curated load, validation, and idempotent smoke tests;
- two independent SDMX providers/dataflows require the same parser/codelist/release behavior;
- source-specific loaders duplicate more than mechanical helpers and share a stable operation sequence that remains unchanged across sources;
- adding a source requires copying more than about 150 lines of non-source-semantic boilerplate;
- source codelists/labels/attribute semantics become necessary for real analysis across sources;
- manual runbooks become the bottleneck after two or more reliable isolated smoke commands exist;
- schema evolution requires multiple ordered revisions across persistent environments.

Until these triggers are met, prefer source-specific modules with tiny shared utilities.

### 6. What remains out of scope for the next task?

TASK-017 must not include:

- source/framework implementation beyond tiny helper extraction;
- generalized SDMX/source framework creation;
- new source onboarding;
- schema changes or migration rewrites;
- live data fetches;
- live `macro` database writes;
- Alembic, SQLAlchemy, Airflow, Dagster, Prefect, Docker, scheduling, or mart work;
- paid, credentialed, or production API use;
- git push.

## Evidence reviewed

Context bundle:

- `context/active_context.md`
- `context/context_audit.md`
- `context/context_audit.json`

The context audit reported:

- context mode: governance;
- estimated tokens: 8062;
- budget tokens: 10000;
- within budget: True;
- raw logs excluded: True;
- summaries used: True.

Implementation evidence inspected:

- `src/macroforge/wdi_loader.py`
- `src/macroforge/wdi_validation.py`
- `src/macroforge/wdi_smoke.py`
- `src/macroforge/oecd_sdmx.py`
- `src/macroforge/oecd_sdmx_loader.py`
- `db/migrations/001_v0_schema_foundation.sql`
- `db/migrations/002_oecd_sdmx_staging.sql`
- `tests/test_wdi_loader.py`
- `tests/test_wdi_smoke.py`
- `tests/test_oecd_sdmx.py`
- `tests/test_oecd_sdmx_loader.py`
- `docs/data/source-contract.md`
- `artifacts/reports/wdi-isolated-smoke-rerun-20260603.json`
- `artifacts/reports/oecd-sdmx-live-smoke-20260603.md`
- `artifacts/reports/oecd-sdmx-load-smoke-20260603.json`

## Non-goals

- No broad ingestion framework.
- No generalized SDMX framework.
- No plugin registry or source base class.
- No curated schema change.
- No source-specific staging schema change.
- No migration framework yet.
- No orchestration platform or scheduler.
- No mart/research/reporting layer yet.
- No live `macro` database write.
- No live data fetch.
- No paid or credentialed APIs.
- No git push.

## Risks

- Tiny shared helpers can accidentally grow into a hidden framework; TASK-017 must keep the helper API narrow and mechanical.
- Shared validation/reporting can overfit to 8-row smoke fixtures; tests should preserve source-specific expectations.
- Keeping raw SQL migrations remains acceptable now, but the next schema revision should reopen the migration-tooling trigger discussion.
- Deferring third-source work slows source breadth but improves reliability of the two proven pipelines.

## Follow-on task

Open TASK-017:

`artifacts/tasks/TASK-017-harden-shared-validation-and-loader-reporting.md`

TASK-017 should start with its own implementation dry-run and TDD. It may edit code/tests, but only within the bounded helper/reporting/validation scope accepted here.

## Verification / evidence used

Context used:

- `projectforge` skill
- `projectforge` reference `generated-project-post-vertical-slice-architecture-review.md`
- `CONSTITUTION.md`
- `instructions/GENERAL_INSTRUCTIONS.md`
- `context/context_policy.yaml`
- `simulation/dry_run_policy.yaml`
- `context/active_context.md`
- `context/context_audit.md`
- `state/active_goal.md`
- `state/project_state.md`
- `state/architecture.md`
- `context/latest_handoff.md`
- `artifacts/tasks/TASK-016-review-architecture-after-second-source.md`
- `artifacts/decisions/DEC-002-v1-scope-wdi-postgres-vertical-slice.md`
- `artifacts/decisions/DEC-005-post-vertical-slice-architecture-and-next-source-scope.md`
- `artifacts/decisions/DEC-006-oecd-sdmx-postgresql-promotion.md`
- implementation evidence listed above

Final tests and coherence are recorded in TASK-016, `state/project_state.md`, and `context/latest_handoff.md` after governance updates.
