# MacroForge Reconstruction Report

Generated: 2026-06-02
Scope: reconstruct MacroForge from exported ChatGPT conversations, scaffold archives/context documents, ProjectForge answers, and the compact deletion manifest before any new implementation.

## Source precedence

1. User's current instruction in this session.
2. Existing exported ChatGPT conversations and context documents as primary historical evidence.
3. ProjectForge setup answers and deletion manifest as compact reconstruction evidence.
4. Prior deleted MacroForge implementation artifacts as historical design evidence only, not current live files.
5. Raw chat/export material remains evidence, not automatic canonical truth, until promoted into project docs/decisions.

## Phase 1 — Discovery

### Relevant files and artifacts found

High-confidence MacroForge sources:

- `/home/mkkto/Desktop/ChatGPT_chats/ChatGPT_exports.zip`
  - Export archive containing historical ChatGPT conversations.
- `/home/mkkto/Desktop/ChatGPT_chats/ChatGPT_exports./conversations.json`
  - Extracted structured conversation export.
- `/home/mkkto/Desktop/ChatGPT_chats/ChatGPT_exports./chat.html`
  - Rendered export companion.
- `/home/mkkto/Desktop/ChatGPT_chats/MacroForge_unified_scaffold.zip`
  - Prior unified scaffold archive referenced in exported chats.
- `/home/mkkto/Desktop/ChatGPT_chats/merger_1/MacroForge_Context_and_Scaffold.zip`
  - Prior context + scaffold archive.
- `/home/mkkto/Desktop/ChatGPT_chats/merger_1/MacroForge_Context_and_Scaffold/MacroForge_Context.md`
  - Compact authoritative MacroForge context snapshot.
- `/home/mkkto/Desktop/ChatGPT_chats/merger_1/MacroForge_Context_and_Scaffold/macroforge_repo.zip`
  - Prior scaffold repository archive.
- `/home/mkkto/Desktop/ChatGPT_chats/merger_1/ai_project_architecture_context.md`
  - AI-integrated project architecture and operating model.
- `/home/mkkto/Desktop/ChatGPT_chats/merger_1/continuation_summary.txt`
  - Home server / SSH / Tailscale / PostgreSQL continuation summary.
- `/home/mkkto/Desktop/ChatGPT_chats/merger_1/home_server.txt`
  - Similar home-server continuation summary, with DB name corrected to `macro`.
- `/home/mkkto/Desktop/ChatGPT_chats/merger_1/ai_framework/AI_Usage_Framework.md`
  - Reusable AI interaction framework.
- `/home/mkkto/Desktop/ChatGPT_chats/merger_1/ai_framework/domain_overlays/system_design.txt`
- `/home/mkkto/Desktop/ChatGPT_chats/merger_1/ai_framework/domain_overlays/investment_research.txt`
- `/home/mkkto/Desktop/ChatGPT_chats/merger_1/ai_framework/modes/research_strict.txt`
- `/home/mkkto/Desktop/ChatGPT_chats/merger_1/ai_framework/modes/builder_high_fidelity.txt`
- `/home/mkkto/Desktop/ChatGPT_chats/merger_1/ai_framework/modes/teacher_first_principles.txt`
- `/home/mkkto/Desktop/ChatGPT_chats/merger_1/ai_framework/modes/default_high_rigor.txt`

ProjectForge / deleted-project evidence:

- `/home/mkkto/srv/projectforge/context/project_creation_answers_macroforge.json`
  - Current ProjectForge answers for MacroForge rebuild.
- `/home/mkkto/srv/projectforge/workspace/macroforge-deletion-manifest-20260602T204545Z.md`
  - Compact manifest of the deleted ProjectForge-generated MacroForge project.
- `/home/mkkto/srv/projectforge/workspace/projects_registry.yaml`
  - Stale registry still listing MacroForge at the now-deleted canonical path.

### Knowledge inventory by category

#### Project goals

MacroForge is a long-lived, AI-first internal platform for macroeconomic and later investment/equity research. Its immediate goal is to become a reliable PostgreSQL-backed macroeconomic data warehouse before expanding into AI-assisted research products.

Evidence:
- `MacroForge_Context.md`: MacroForge is an AI-first internal platform for a long-lived macroeconomic and later equity-focused data/research system.
- `project_creation_answers_macroforge.json`: data platform first, research/analysis second; PostgreSQL-backed macroeconomic data warehouse first.

Confidence: Very high.

#### Business goals

MacroForge supports the user's ambition to build serious macro/investing skill: understand economies, markets, commodities/energy, equities, and future market positioning through reproducible data and evidence-backed analysis.

Evidence:
- Chat export snippets about macro-oriented investing, stock analysis, market modeling, commodities/energy, and building independent investment skill.
- ProjectForge answers mention investing research, equities, filings, fundamentals, stocks, and investment analysis.

Confidence: Medium-high. Business motivation is clear; exact commercial use is not defined.

#### Architecture

Architecture should separate docs, decisions, tasks, state, logs, agents, tools, data, database, code, tests, and infrastructure. ProjectForge becomes the outer project operating system; MacroForge is a generated/managed project inside it.

Evidence:
- `ai_project_architecture_context.md`: separation of instructions/state/logs/evidence; high-level structure with docs, ai/agents, ai/tasks, ai/state, ai/logs, src, tests, data, infra.
- ProjectForge v6 docs: generated projects use context/state/decisions/tasks/logs/summaries/coherence.

Confidence: High.

#### Database design

PostgreSQL is the authoritative analytical store. The intended v0 database architecture is schema-separated:

- `meta`: sources, dataset releases, pipeline runs, lineage, quality checks.
- `staging`: source-shaped or normalized-but-not-curated incoming observations.
- `curated`: canonical dimensions and facts.
- `mart`: later analytical/reporting layer.

Canonical macro model:

- dimensions: time/period, geography/territory, indicator, unit, attribute/qualifier set.
- fact table: revision-safe `fact_observation`.
- candidate grain: source + indicator + geography/territory + period + unit + frequency/attribute set + vintage/as-of date.

Evidence:
- `MacroForge_Context.md`: schemas `meta`, `staging`, `curated`, later `mart`; core tables source, dataset_release, run, lineage, quality_check; dimensions time/geo/indicator/unit/fact_observation revision-safe.
- Deletion manifest: prior DEC-004 and v0 schema design used `meta.source`, `meta.dataset_release`, `meta.pipeline_run`, `meta.lineage_event`, `meta.quality_check`, `staging.wdi_observation`, `curated.dim_indicator`, `dim_territory`, `dim_period`, `dim_unit`, `dim_attribute_set`, `fact_observation`.

Confidence: Very high.

#### Ingestion pipelines

The first implementation milestone should be one real macro dataset end-to-end. World Bank WDI is the best first source because it is public/no-key and broad enough to test indicator/geography/time/unit modeling. UN WPP/UNPD remains historically discussed but may require a token for data endpoints.

Pipeline pattern:

1. Extract source payload.
2. Preserve immutable raw evidence.
3. Store checksum and source metadata.
4. Transform into staging-shaped observations.
5. Load idempotently into PostgreSQL.
6. Upsert dimensions and curated facts.
7. Record run/lineage/quality evidence.
8. Validate row counts, uniqueness, duplicates, nulls, and sanity checks.
9. Produce inspectable output/report.

Evidence:
- ProjectForge answers: v1 success is extract one public dataset, raw evidence/checksum, staging transform, idempotent PostgreSQL load, metadata, validation, inspectable report.
- Chat export: WDI recommended over UNPD as lowest-friction first real macro pipeline; UNPD data endpoint may require `UNPD_API_TOKEN`.
- Deletion manifest: previous work implemented WDI extraction smoke for USA/DNK, GDP/population, years 2020-2021, 8 records.

Confidence: High.

#### AI integration

AI is central, but constrained. Agents are accelerators, not authorities. Model runtime and agent runtime must be separated:

- Model runtime: passive service with minimal access.
- Agent runtime: side-effect-capable orchestrator, constrained by wrappers, task contracts, permissions, and logs.

Evidence:
- `MacroForge_Context.md`: model runtime passive; agent runtime orchestrates tools and is constrained.
- `ai_project_architecture_context.md`: agents may propose/implement/document but architecture ownership remains human-controlled.
- ProjectForge answers: local autonomy balanced-to-aggressive within strict boundaries.

Confidence: Very high.

#### Agent workflows

Agent work should use explicit task contracts, bounded context, permission tiers, run evidence, and review. Historical wrapper names:

- `mf_task.sh`
- `mf_db.sh`
- `mf_git.sh`
- `mf_test.sh`
- possibly `mf_deploy.sh` as human-only or highly restricted.

Roles:

- operator/context-manager
- planner
- builder/coder
- reviewer
- researcher/analyst
- data steward
- auditor
- incident responder/ops
- teacher/explainer

Evidence:
- `MacroForge_Context.md`: wrappers and role-based permissions.
- `ai_project_architecture_context.md`: permission tiers and task package model.
- ProjectForge answers: specialized local roles and bounded context bundles.

Confidence: Very high.

#### Infrastructure

V1 infrastructure is local/home-server first:

- Ubuntu/Linux host.
- PostgreSQL service.
- Tailscale for remote access without router control/port forwarding.
- SSH key-only access.
- PostgreSQL listens on localhost + Tailscale IP, not public LAN/0.0.0.0.
- CI via GitHub only; server executes pinned commits manually or via conservative systemd timers.
- Docker/cloud/public exposure deferred.

Evidence:
- `continuation_summary.txt` and `home_server.txt`.
- `MacroForge_Context.md`: no autonomous deployment; containers deferred to v2; GitHub CI only.

Confidence: High.

#### Deployment

Deployment is intentionally conservative. No autonomous deployment in v1. GitHub may run CI, but the server executes pinned commits manually or via controlled timers after the data loop is stable. No remote push without human approval.

Evidence:
- `MacroForge_Context.md`: GitHub CI only; server executes pinned commits manually or via systemd timers; no self-updating early instability.
- ProjectForge answers: Docker/cloud/public deferred; git remote/push human-approved.

Confidence: High.

#### Unresolved decisions

High-confidence unresolved areas:

- Exact v0 PostgreSQL schema should be reconstructed/accepted again before implementation because previous files were deleted.
- Whether to use WDI first is strongly recommended, but source choice can still be explicitly overridden.
- Whether to restore prior deleted schema/WDI code from git/backup/archive or recreate from design.
- Registry staleness: ProjectForge registry still lists deleted MacroForge path.
- Exact GitHub/branch/remote policy.
- Exact wrappers and enforcement details for agent commands.
- Whether logs need filesystem immutability or just append-only convention.
- Containerization timing and whether OS-level users are enough for v1.
- Database name inconsistency in historical notes: `macro` vs `macrodata`; `home_server.txt` uses `macro`, `continuation_summary.txt` had `macrodata` in one test command.

Confidence: High.

## Phase 2 — Reconstruction

### Purpose

MacroForge is a personal/internal, AI-first macroeconomic and investing research platform. It begins as a reproducible PostgreSQL macro data warehouse with raw/staging/curated separation, provenance, lineage, quality checks, and run evidence. It later expands into AI-assisted macro research, equities/firm-level data, filings/fundamentals, dashboards/reports, and eventually structured investment workflows.

Confidence: Very high.

### Scope

V1 scope:

- ProjectForge-managed project operating system for MacroForge.
- Current-source reconstruction from historical chats/context.
- One public macro dataset vertical slice.
- PostgreSQL schema foundation.
- Raw evidence + checksums.
- Staging transform.
- Idempotent PostgreSQL load.
- Metadata, lineage, quality checks.
- Query/report output.
- Tests and verification.

Expansion scope:

- More macro sources: FRED, OECD, IMF, Eurostat, UN WPP/UNPD, national sources.
- Equity/firm data: filings, fundamentals, stocks.
- Research workflows and briefs only after data reliability is proven.
- Dataset catalog UI and macro briefs later.

Confidence: High.

### Success criteria

V1 succeeds when a future agent/human can run one source pipeline and prove:

- where raw data came from;
- what checksum was stored;
- how rows map to staging;
- how rows load into canonical PostgreSQL tables;
- what dimensions/facts were changed;
- whether validation passed;
- what report/query output was produced;
- what task/decision/run evidence exists;
- how to rerun safely.

Confidence: Very high.

### Non-goals

- No AI-generated research briefs as first milestone.
- No many-provider ingestion spree before schema/grain/idempotency/logging/validation stabilize.
- No Airflow/Dagster/Prefect initially.
- No Docker/cloud/public deployment initially.
- No paid/credentialed APIs in v1 without separate decision and secrets policy.
- No raw shell/secrets/deployment/billing authority for agents.
- No raw ChatGPT export as canonical truth without curation.
- No broad universal framework before seeing real source variation.

Confidence: Very high.

### Architecture

Recommended reconstructed architecture:

```text
/home/mkkto/srv/projectforge/workspace/projects/macroforge/
  AGENTS.md
  CONSTITUTION.md
  README.md
  project.yaml
  context/
    PROJECT_CONTEXT.md
    reconstruction/
      reconstruction_report.md
      knowledge_inventory.md
      architecture_assessment.md
      missing_information.md
      source_index.md
    imports/
      chatgpt_export_recovery/
        README.md
        conversation_index.md
        recovery_summary.md
  state/
    active_goal.md
    project_state.md
    architecture.md
    known_issues.md
    lessons.md
  instructions/
    GENERAL_INSTRUCTIONS.md
    CONTEXT_POLICY.md
  artifacts/
    decisions/
    tasks/
    reports/
    handoffs/
    reviews/
  docs/
    architecture/
    data/
    runbooks/
    glossary.md
    roadmap.md
  db/
    migrations/
    schema/
    queries/
  src/
    macroforge/
      __init__.py
      wdi.py
      db.py
      loaders.py
      validation.py
  tests/
  data/
    raw/
    staging/
    curated/
    metadata/
  pipelines/
    wdi/
  agents/
  permissions/
  logs/
  metrics/
  models/
  tools/
```

This should be generated with ProjectForge's current `python_data_project` template, then enriched with MacroForge-specific reconstruction docs/decisions/tasks.

Confidence: High.

### Data model

Recommended v0 model:

- `meta.source`
  - provider/source identity.
- `meta.dataset_release`
  - provider dataset/version/release details.
- `meta.pipeline_run`
  - run_id, source, timing, inputs, status, artifact paths.
- `meta.lineage_event`
  - raw -> staging -> curated lineage and checksums.
- `meta.quality_check`
  - validation outcomes.
- `staging.wdi_observation`
  - source-shaped normalized WDI observations and run reference.
- `curated.dim_indicator`
- `curated.dim_territory`
- `curated.dim_period`
- `curated.dim_unit`
- `curated.dim_attribute_set`
- `curated.fact_observation`
  - canonical observation fact.

Recommended fact grain:

`source_id + indicator_id + territory_id + period_id + unit_id + attribute_set_id + as_of_date`

Important modeling principles:

- Preserve source differences instead of forcing premature merges.
- Do not overwrite historical vintages.
- Add latest-vintage views later.
- Avoid wide nullable fact tables.
- Use natural keys plus `INSERT ... ON CONFLICT` for idempotency.

Confidence: High.

### Technology stack

- Python 3.12+
- PostgreSQL
- SQL migrations, initially raw SQL rather than Alembic
- Markdown/YAML/JSON/JSONL for project OS artifacts
- ProjectForge v6 for governance/scaffolding/context discipline
- pytest for Python tests
- SQL validation queries for schema/data checks
- Tailscale + SSH key-only for home-server access
- Git/GitHub CI later, remote push human-approved

Confidence: High.

### Development roadmap

Milestone 0 — Reconstruction and scaffold:

- Recreate MacroForge inside ProjectForge with current template.
- Import compact recovered context, not raw full exports.
- Create reconstruction report, architecture assessment, missing-info report, decisions, tasks, summaries.
- Fix stale registry.

Milestone 1 — PostgreSQL/WDI vertical slice:

- Recreate/accept v0 schema decision.
- Implement migration and schema verification tests.
- Implement WDI extract/raw/checksum writer.
- Implement staging/curated PostgreSQL loader.
- Implement validation queries and run report.
- Run a tiny smoke slice: USA/DNK, GDP/population, 2020-2021.

Milestone 2 — Hardening:

- Idempotent reruns.
- Better failure handling.
- Source catalog documentation.
- Data quality checks and reports.
- Runbook for WDI pipeline.
- Backup/restore and DB environment documentation.

Milestone 3 — Second source:

- Add one source with different shape/friction to test abstraction.
- Candidate: FRED if API key policy is accepted; or another no-key public source if available.

Milestone 4 — Research layer:

- Query notebooks/reports.
- Macro brief generation backed by canonical facts and citations.
- Analyst workflows and AI-assisted research roles.

Milestone 5 — Broader automation:

- Scheduling after manual reliability.
- CI/data validation automation.
- Optional Docker/containerized agents.
- Dataset catalog UI.

Confidence: High.

### Contradictions found

1. Database name: `macro` vs `macrodata`.
   - `home_server.txt` says test with `-d macro`; `continuation_summary.txt` says `-d macrodata` in one line.
   - Recommendation: use `macro` unless the live DB proves otherwise.

2. First source: UN WPP/UNPD vs World Bank WDI.
   - Early conversations used UN demographic/WPP as first pipeline; later setup favored WDI because UNPD data endpoint may require a token.
   - Recommendation: WDI first for v1 unless user explicitly switches.

3. AI folder naming: historical `ai/` layout vs ProjectForge `agents/`, `state/`, `artifacts/`, `logs/` layout.
   - Recommendation: use ProjectForge-native layout and preserve historical `ai/` intent through `agents/`, `permissions/`, `artifacts/tasks/`, and run logs rather than duplicating both systems.

4. Containers deferred vs prior scaffold may include `infra/docker-compose.yml`.
   - Recommendation: Docker may exist as optional/dev reference only; no v1 dependency without decision.

5. Prior tasks marked complete but project deleted.
   - Recommendation: treat as historical evidence; recreate and re-verify before marking current tasks complete.

### Missing information

High-impact:

- Is the live PostgreSQL database name `macro` and is it available from the ProjectForge host?
- Should the rebuild restore prior deleted WDI/schema work from backup/archive/git if possible, or recreate cleanly from the report?
- Should the old scaffold zips be unpacked into a curated import directory, or only summarized/indexed?

Medium-impact:

- Exact remote/GitHub repository policy.
- Whether brother collaboration remains in scope for v1.
- Whether OS-level agent users/wrappers should be implemented before or after WDI vertical slice.
- Whether FRED API key is acceptable in milestone 3.

Low-impact:

- Exact names for agent roles/profiles.
- Whether `mart` schema appears in v0 or is documented only.
- Exact report format for first output.

### Assumptions that should not be made

- Do not assume raw exports are safe to commit.
- Do not assume prior deleted code exists.
- Do not assume PostgreSQL credentials or secrets.
- Do not assume remote GitHub push is authorized.
- Do not assume Docker/cloud/public deployment.
- Do not assume live DB availability until verified.
- Do not assume UNPD data endpoints are public.
- Do not assume AI agents can use raw shell or privileged commands.

## Confidence score by reconstructed area

- Purpose: 0.95
- V1 success criteria: 0.95
- Non-goals: 0.95
- ProjectForge location/rebuild model: 0.90
- Data model direction: 0.90
- WDI-first recommendation: 0.85
- PostgreSQL/home-server infrastructure: 0.80
- Agent/AI governance: 0.95
- Deployment model: 0.85
- Git/remote workflow: 0.60
- Exact current DB name/connectivity: 0.55
- Business/career goals: 0.75
- Exact old zip contents: 0.65 until zips are listed/extracted safely.

## Phase 3 — Architecture assessment

### Internal consistency

Overall consistent if ProjectForge becomes the project OS and MacroForge avoids duplicating an older `ai/` system. The strongest coherent path is:

- ProjectForge handles context/state/decisions/tasks/logs/agents.
- MacroForge domain code focuses on data ingestion, database schema, validation, and research workflows.
- Historical AI architecture concepts are mapped into ProjectForge's existing structure.

Risk: duplicating both ProjectForge governance and old `ai/` folder conventions would increase tokens and confusion.

Assessment: Good with simplification.

### Scalability

Database scalability is directionally sound:

- normalized dimensions + fact grain;
- source/release/run/lineage metadata;
- revision-safe facts;
- raw/staging/curated separation.

Risks:

- canonical fact grain can become overcomplicated too early;
- source-specific qualifiers may explode unless `attribute_set` is designed carefully;
- many providers will stress mapping/validation conventions.

Assessment: Good if v1 stays narrow and generalization waits for at least two real sources.

### Maintainability

Strengths:

- durable decisions/tasks/reports;
- tests before summaries;
- small vertical slice;
- raw evidence and checksums;
- ProjectForge folder summaries for token discipline.

Risks:

- excessive artifacts can consume tokens if raw imports are copied into project context;
- wrappers/agent permission system may be overbuilt before implementation proves recurring needs.

Assessment: Good if curated summaries are primary and raw imports stay external/untracked.

### AI-assisted development suitability

Very strong if implemented through ProjectForge discipline:

- bounded tasks;
- summaries;
- explicit acceptance criteria;
- permission tiers;
- run evidence;
- decisions for architecture changes.

Risk: agents must not treat historical chat as direct instructions. They need a clear source hierarchy.

Assessment: Excellent with import-precedence decision.

### Suitability for long-term macro/investment research

Strong foundational design. Macro/investment research needs provenance, comparable series, vintage awareness, and evidence-backed claims. MacroForge's planned database and lineage model support that.

Risks:

- real investment research later needs entity/security master, filings/fundamentals model, calendars, currency/unit conversion, portfolio/watchlist context, and citation discipline.
- those should not be forced into v1.

Assessment: Strong foundation; research layer should wait until data reliability is proven.

### Bottlenecks and technical debt risks

- Context/token bloat from importing too much raw chat/scaffold content.
- Premature framework design before second source.
- Under-specified DB connection/secrets/run environment.
- Ambiguous database name and live DB availability.
- Registry stale after deleting old MacroForge.
- Prior completed tasks may be confused with current live state.
- Agent-wrapper enforcement could become ceremonial unless tied to actual recurring commands.

### Opportunities for simplification

- Use ProjectForge-native folders instead of recreating old `ai/` folder hierarchy.
- Keep WDI as first source, avoid UNPD token complexity.
- Raw SQL migrations for v0; defer Alembic.
- Local/manual pipeline runs first; defer scheduler/orchestrator.
- One smoke dataset; no broad source catalog implementation until Milestone 2.
- Compact recovery summary, not full raw export import.

## Phase 4 — Clarification questions

Only high-leverage questions are needed now:

1. For the rebuild, should I recreate schema/WDI work cleanly from the reconstruction, or first try to recover exact prior files from available zips/git/backup if possible?

2. Should MacroForge v1 use database name `macro` as the default, unless live verification proves otherwise?

3. Are you comfortable with WDI as the first v1 source, given the evidence that it avoids API-key friction, or do you want UN WPP/UNPD despite token/friction risk?

These are not needed to produce the report, but they affect the first implementation tasks after initialization.

## Phase 5 — Proposed project initialization

Recommended process:

1. Generate fresh ProjectForge project at:
   `/home/mkkto/srv/projectforge/workspace/projects/macroforge`

2. Use template:
   `python_data_project`

3. Use answers file:
   `/home/mkkto/srv/projectforge/context/project_creation_answers_macroforge.json`

4. Fix or refresh the stale ProjectForge registry entry.

5. Add curated reconstruction docs under:
   `context/reconstruction/`

6. Add import-precedence decision:
   `artifacts/decisions/DEC-001-import-precedence-and-reconstruction.md`

7. Add scope/v1 decision:
   `artifacts/decisions/DEC-002-v1-scope-wdi-postgres-vertical-slice.md`

8. Add agent operating decision:
   `artifacts/decisions/DEC-003-ai-agent-operating-model.md`

9. Add database architecture decision:
   `artifacts/decisions/DEC-004-v0-postgresql-schema-foundation.md`

10. Add initial task backlog.

11. Run generated-project coherence and tests.

## Implementation roadmap

### Backlog

TASK-001 — Rebuild MacroForge scaffold with current ProjectForge
- Generate project with `python_data_project` template.
- Register canonical path.
- Verify coherence.
- Acceptance: project exists, registry is correct, coherence passes.

TASK-002 — Import curated reconstruction context
- Add reconstruction report, knowledge inventory, architecture assessment, missing-info report, source index.
- Do not import full raw chats into git.
- Acceptance: future agent can read compact docs and understand MacroForge without raw exports.

TASK-003 — Establish source-of-truth/precedence decisions
- Record historical export precedence, WDI-first default, ProjectForge-native layout decision.
- Acceptance: contradictions are documented and current truth is clear.

TASK-004 — Recreate v0 PostgreSQL schema foundation
- Raw SQL migration.
- Schema documentation.
- Verification query.
- Tests.
- Acceptance: migration and schema checks pass against isolated/local PostgreSQL where available, or dry-run/test fallback is documented.

TASK-005 — Recreate narrow WDI extract/raw evidence slice
- WDI client.
- Raw artifact writer.
- Checksums and source metadata.
- Tests for URL/run_id/overwrite/normalization.
- Acceptance: 8-row USA/DNK GDP/pop 2020-2021 smoke result with report.

TASK-006 — Implement PostgreSQL loader for WDI staging/curated facts
- Insert source/release/run metadata.
- Insert staging observations.
- Upsert dimensions.
- Upsert fact observations.
- Write lineage and quality checks.
- Acceptance: idempotent rerun and no duplicate canonical grain.

TASK-007 — Add runbook and validation reporting
- Document safe run command, expected output, failure modes, rerun behavior.
- Acceptance: a future agent can rerun and verify the pipeline.

TASK-008 — Review architecture after first vertical slice
- Evaluate schema abstraction against real WDI data.
- Decide second source and whether to generalize framework.
- Acceptance: decision record for next source/framework scope.

## Recommended first milestone

Recommended first milestone:

"Fresh ProjectForge-managed MacroForge scaffold plus one WDI-to-PostgreSQL vertical slice with raw evidence, checksums, metadata, idempotent load, lineage, validation, and an inspectable report."

Why this milestone:

- It matches the historical MacroForge concept.
- It avoids API-key friction.
- It tests the real hard parts: grain, provenance, idempotency, validation, and agent-operable evidence.
- It keeps AI research output deferred until the data substrate is trustworthy.

## Current blockers / operational note

The old MacroForge directory was deleted while it was the active Hermes process working directory. Terminal execution in this session now fails before command execution because the deleted cwd cannot be resolved. File/search/write tools still work. To run ProjectForge's `tools/new_project.py`, coherence checks, or tests, a fresh Hermes session should start from `/home/mkkto/srv/projectforge`, or the tool environment must be reset to a surviving cwd.
