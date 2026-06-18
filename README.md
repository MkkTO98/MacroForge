# MacroForge

MacroForge is a ProjectForge-managed, AI-first macroeconomic and investing research platform.

MacroForge exists to progressively reduce the recurring effort required to build, maintain, validate, canonicalize, and use trusted macroeconomic data for investment-relevant research. Trusted macroeconomic databases and datasets are outputs of MacroForge; the project itself is the effort-reduction machine that makes such data increasingly cheaper, safer, clearer, and more reproducible to produce and use.

The current implementation is a reproducible PostgreSQL-backed macro data substrate, not yet a broad research automation system. The project has progressed beyond initial reconstruction: WDI, OECD/SDMX, and a bounded Eurostat NAMQ GDP fixture now coexist through source-specific PostgreSQL paths, canonical-domain period/territory/provider mapping support, combined-source validation, a first deterministic canonical GDP snapshot report, and bounded file-backed canonicalization proposal evidence.

## Current phase

MacroForge is in Milestone 3. TASK-004 through TASK-039 are complete. TASK-038 validated the bounded proposal -> review -> accepted/provisional canonicalization lifecycle. TASK-039 persisted the deferred OECD/Eurostat mapping advancement requirements so future work can resume from explicit blockers and minimum advancement conditions instead of reinterpreting the full lifecycle artifact.

For live project status, read these file-backed state artifacts first:

- `state/active_goal.md`
- `state/project_state.md`
- `state/architecture.md`
- `context/latest_handoff.md`
- the active task under `artifacts/tasks/`

## Implemented substrate

- Raw SQL PostgreSQL migrations 001-004.
- Schemas: `meta`, `staging`, and `curated`; `mart` remains deferred.
- Source-specific loaders for:
  - World Bank WDI;
  - OECD/SDMX recorded/bounded evidence;
  - Eurostat `namq_10_gdp` recorded/bounded evidence.
- Canonical-domain foundation:
  - structured annual/quarterly/monthly/daily-ready periods;
  - ISO3-preserved country territories plus explicit territory types;
  - provider period/territory/code mapping metadata;
  - source-agnostic curated facts.
- Combined-source canonical validation smoke.
- Canonical GDP snapshot/audit report over `curated.*` plus `meta.*` only.

## Current architecture posture

MacroForge intentionally remains boring, bounded, and effort-reduction oriented:

- use raw SQL migrations, PostgreSQL, psql, and source-specific Python loaders;
- use isolated temporary databases for smoke/report verification by default;
- keep provider representations in staging/source payloads/metadata/mapping layers, not as curated identities;
- preserve source-specific-first discipline and extract shared mechanics only after repeated non-semantic duplication appears;
- treat PostgreSQL as the accepted analytical store, not proof of truth by itself;
- keep operational logs optional and debugging-oriented; task, decision, state, and handoff artifacts are the primary audit trail.

Do not introduce a generalized ingestion framework, ORM/Alembic layer, orchestration system, new source, new dataset, live/default `macro` write, or canonicalization implementation without a fresh accepted decision and dry-run that explains which recurring effort the change reduces while preserving trust.

## V1 success

V1 succeeds when MacroForge can run one real macro data vertical slice and prove:

- where raw data came from;
- what checksum was stored;
- how rows map to staging;
- how rows load into canonical PostgreSQL tables;
- what dimensions/facts changed;
- whether validation passed;
- what report/query output was produced;
- what task/decision/handoff evidence exists;
- how to rerun safely.

## Important project docs

- `AGENTS.md` — project-local agent operating rules.
- `context/context_policy.yaml` — summary-first context, task completion, context-health, and Architecture-to-Reality audit policy.
- `docs/architecture/overview.md` — current architecture summary.
- `docs/architecture/historical-architecture-reconciliation.md` — classification of historical Desktop architecture concepts against current decisions.
- `docs/data/v0-data-model.md` — current schema/data-model reference.
- `db/schema/v0_schema_foundation.md` — migration/table reference.
- `artifacts/decisions/` — durable decisions through the current project state.
- `artifacts/tasks/` — backlog, completed tasks, active task, and acceptance criteria.

## Agent operating rules

Agents must read `AGENTS.md`, `CONSTITUTION.md`, state files, relevant decisions/tasks, and folder summaries before nontrivial work. Raw chat exports, Desktop exports, PDFs, and deleted-project files are historical evidence, not canonical truth, until curated into this project.

Before reporting code, schema, governance, or state changes, run the relevant tests/checks and report exact output.
