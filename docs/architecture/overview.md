# MacroForge Architecture Overview

## Current architecture

MacroForge is a ProjectForge-managed data/research project with a local-execution / cloud-governance operating model. Its governing purpose is to progressively reduce the recurring effort required to build, maintain, validate, canonicalize, and use trusted macroeconomic data for investment-relevant research.

Trusted macroeconomic databases and datasets are outputs of MacroForge. The project itself is the effort-reduction machine. The current implementation is intentionally small, raw-SQL/PostgreSQL-based, and source-specific while the project learns from real source pressure and extracts only mechanics that reduce recurring effort without weakening trust.

The current state is maintained in `state/active_goal.md`, `state/project_state.md`, `state/architecture.md`, `context/latest_handoff.md`, and active task/decision artifacts. This overview is a stable architecture map, not the live task ledger.

## Layers

1. Project operating system: ProjectForge-generated state, decisions, tasks, handoffs, policies, summaries, dry-runs, and lightweight audit tooling.
2. Evidence layer: recorded raw source payloads, checksums, normalized metadata, source reports, and source-contract evidence.
3. Database layer: PostgreSQL schemas for `meta`, `staging`, and `curated`; `mart` remains deferred.
4. Source-specific pipeline layer: bounded loaders and smoke/report commands for WDI, OECD/SDMX, and Eurostat NAMQ GDP evidence.
5. Canonical-domain layer: structured periods, canonical territories, provider period/territory/code mappings, and source-agnostic curated facts.
6. Validation/reporting layer: isolated database smokes, schema health checks, combined-source validation, quality/lineage checks, and deterministic canonical report artifacts.
7. Research layer: first minimal GDP snapshot report exists; broader research automation remains deferred until canonicalization/comparability design is accepted.

## Implemented source paths

- WDI: raw evidence, normalized metadata, source-specific staging, curated fact load, validation report, and rerunnable isolated smoke.
- OECD/SDMX: bounded no-key evidence, source-specific normalization, codelist/label metadata, `staging.oecd_sdmx_observation`, source-specific loader, and isolated load report.
- Eurostat NAMQ GDP: bounded recorded JSON-stat evidence, `staging.eurostat_namq_observation`, source-specific loader, provider mapping/code dictionaries, and isolated load report.

## Database migrations

- `001_v0_schema_foundation.sql`: base `meta`, WDI `staging`, and `curated` dimensions/facts.
- `002_oecd_sdmx_staging.sql`: bounded OECD/SDMX source-specific staging table.
- `003_canonical_domain_dimensions.sql`: structured periods, territory typing, provider period/territory mappings, and provider code dictionaries.
- `004_eurostat_namq_staging.sql`: bounded Eurostat NAMQ GDP source-specific staging table.

## Current boundary decisions

- MacroForge evaluates future components by the recurring effort they reduce: source onboarding, source maintenance, validation, canonical mapping, schema evolution, downstream analysis, or future agent recovery/context effort.
- Trust requires source evidence, reproducibility evidence such as checksums, source-preserving transforms, lineage, quality checks, canonical mapping status, validation, replay/rerun paths, and human review for high-impact economic meaning; PostgreSQL alone is not proof of truth.
- DEC-005 keeps raw SQL, PostgreSQL, psql/Python loaders, CLI runbooks, and tests; Alembic, SQLAlchemy, orchestration, Docker, and broad source frameworks remain deferred.
- DEC-006 accepts OECD/SDMX PostgreSQL promotion only as a narrow source-specific extension.
- DEC-007 keeps source-specific architecture after the second source and accepts only tiny shared mechanical helpers.
- DEC-011 accepts canonical-domain schema evolution: structured periods, territory typing, provider mappings, and no provider-specific fact columns.
- DEC-012 accepts bounded Eurostat promotion only for the recorded `namq_10_gdp` fixture.
- DEC-013 keeps source-specific loaders after three source paths and chooses combined-source validation rather than a generalized ingestion framework.
- DEC-014 selects the first minimal research-facing canonical GDP snapshot report.
- DEC-015/DEC-016 select and refine TASK-030: design an AI-assisted auditable canonicalization/comparability layer before further implementation.

## Governance and audit posture

The primary project audit trail is file-backed:

- task artifacts;
- decision artifacts;
- handoff artifacts;
- state artifacts;
- report artifacts where detailed evidence belongs.

Governance exists to reduce future uncertainty and agent recovery cost. A report, decision, manifest, registry, or artifact is justified only if it improves trust, reproducibility, recovery, maintainability, semantic correctness, or future effort reduction. Avoid governance theater.

Operational logs are optional debugging artifacts and are not the source of truth for normal governance.

Architecture-to-Reality Audits should be run every 5-10 completed tasks, before major architecture changes, and before major governance reviews. The lightweight tool `tools/architecture_reality_audit.py` complements `tools/check_coherence.py` and `tools/context_health.py`; it does not replace human or cloud governance review.

## Active next architecture work

No TASK-038 has been created, selected, opened, or started. The current recommendation-only next technical/design candidate is bounded, file-backed review-to-accepted/provisional canonicalization lifecycle validation using existing TASK-034/TASK-037 evidence.

Frame that candidate as a test of whether MacroForge can reduce future manual canonicalization effort while preserving trust, provenance, and review-gated semantic correctness. Do not treat it as merely another governance artifact.

Do not implement migrations, schema changes, source onboarding, report expansion, unit conversion, generalized ingestion/framework work, live source fetches, live/default `macro` writes, orchestration, or git push without a new accepted decision and dry-run.
