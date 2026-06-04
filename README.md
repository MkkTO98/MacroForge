# MacroForge

MacroForge is a ProjectForge-managed, AI-first macroeconomic and investing research platform.

Its v1 goal is deliberately narrow: build a trustworthy PostgreSQL-backed macroeconomic data warehouse vertical slice before producing AI research briefs or broad multi-source automation.

## Current phase

Milestone 0: reconstruction and initialization.

The project has been freshly generated from the current ProjectForge `python_data_project` template at:

`/home/mkkto/srv/projectforge/workspace/projects/macroforge`

The deleted prior MacroForge project is historical evidence only. Schema and WDI work must be recreated cleanly from current decisions and reconstruction documents, not blindly restored from old files.

## V1 success

V1 succeeds when MacroForge can run one real macro data vertical slice and prove:

- where raw data came from;
- what checksum was stored;
- how rows map to staging;
- how rows load into canonical PostgreSQL tables;
- what dimensions/facts changed;
- whether validation passed;
- what report/query output was produced;
- what task/decision/run evidence exists;
- how to rerun safely.

## V1 source and database defaults

- First v1 source: World Bank WDI.
- Default database name: `macro`, unless live verification proves otherwise.
- No secrets, paid APIs, deployment, Docker/cloud dependency, or GitHub push in v1 without a separate decision and human approval.

## Important project docs

- `context/PROJECT_CONTEXT.md` — compact current source of truth.
- `context/reconstruction/` — curated reconstruction evidence.
- `docs/roadmap.md` — milestone roadmap.
- `docs/architecture/overview.md` — architecture summary.
- `docs/data/v0-data-model.md` — reconstructed schema direction.
- `artifacts/decisions/DEC-001-import-precedence-and-reconstruction.md` through `DEC-004-v0-postgresql-schema-foundation.md` — current durable decisions.
- `artifacts/tasks/` — current backlog and acceptance criteria.

## Agent operating rules

Agents must read `AGENTS.md`, `CONSTITUTION.md`, state files, relevant decisions/tasks, and folder summaries before nontrivial work. Raw chat exports and deleted-project files are evidence, not canonical truth, until curated into this project.

Before reporting code or schema changes, run the relevant tests/checks and report exact output.
