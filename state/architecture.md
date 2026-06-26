# Architecture State

## Current architecture

MacroForge is a ProjectForge-managed data/research project whose governing purpose is to reduce recurring effort in trusted macroeconomic data work for investment-relevant research. The project OS is file-backed and summary-first. Domain implementation currently combines source-specific WDI/OECD/Eurostat evidence paths, a canonical-domain PostgreSQL substrate, deterministic file-backed canonicalization state/proposal mechanics, bounded review-lifecycle artifacts, and OECD unit-basis/status review evidence.

Trusted databases and datasets are outputs of MacroForge, not the whole project. Trust requires source evidence, reproducibility evidence, lineage, quality checks, canonical mapping status, validation, replay/rerun paths, and human review for high-impact economic meaning.

## Target v1 flow

WDI source payload -> immutable raw artifact + checksum -> staging observation rows -> curated dimensions/facts -> lineage/quality checks -> query/report output.

## Database schemas

TASK-004 created the first raw SQL migration for:

- `meta`
- `staging`
- `curated`

`mart` remains documented for later analytical/reporting use.

## Current implementation state

MacroForge implementation is currently capability-complete through TASK-045 OECD/Eurostat fixture-persistence hardening. No open implementation task is active.

### Source-specific substrate

- WDI has raw evidence, loading, validation, isolated smoke checks repaired for the current canonical-domain schema state, and first vertical-slice proof.
- OECD/SDMX has recorded/live-smoke evidence, codelist/label metadata, staging observation support, loader behavior, bounded comparability artifacts, and unignored bounded fixture files for clean-clone reconstruction.
- Eurostat `namq_10_gdp` has recorded fixture evidence, staging observation support, loader behavior, provider mappings/dictionaries, isolated load smoke evidence, and unignored bounded fixture files for clean-clone reconstruction.
- Source-specific-first remains the governing posture; generalized ingestion/source frameworks remain deferred until repeated proven duplication justifies them.

### Canonical-domain substrate

- Canonical periods are structured rather than provider-string identities.
- Country/territory identity preserves ISO3 and explicit territory types.
- Provider period/territory/code representations live in mappings/metadata rather than becoming curated identities.
- Source-agnostic curated facts exist, and combined-source canonical validation plus the first canonical GDP snapshot report are complete.
- PostgreSQL is the accepted analytical store, but database persistence alone is not treated as truth without evidence, lineage, checks, replayability, and review status.

### Canonicalization lifecycle

- DEC-018 accepts a minimal AI-assisted canonicalization/comparability design: provider indicators are evidence, automated output is proposal state, accepted/provisional mapping state gates curated/report use, and confidence is review-routing metadata rather than truth.
- Implemented lifecycle mechanics remain deterministic and file-backed. They cover provider evidence, proposal state, unit/comparability profiles, review routing, supersession, no-auto-apply mapping proposals, WDI unit metadata enrichment, and bounded proposal -> review -> accepted/provisional validation.
- The canonical asset manifest exists as a narrow file-backed pointer registry in `artifacts/manifests/canonical_assets.json`.

### Current governance helper

- TASK-043 added `tools/consult_metaharvest.py` as a bounded preflight helper for scoped governance/design tasks. It classifies task text with `task_classification_version: 1`, applies the existing `architecture/architectureharvest/relevance_map.yaml` through a Consultation Contract, and only then runs a separate Retrieval Contract for compact advisory MetaHarvest context.
- The helper is advisory-only: no startup consultation, no routine-task retrieval, no automatic adoption, no task creation, no MetaHarvest authority, no runtime/orchestration adoption, and non-blocking failure if MetaHarvest is unavailable.

### Current review status

- WDI GDP evidence has a governed provisional lifecycle outcome from bounded review evidence.
- OECD and Eurostat GDP mappings remain deferred unless future review decisions explicitly advance them.
- OECD `B1GQ` evidence is now split into `USD_EXC` exchange-rate and `USD_PPP` PPP basis candidates, but the bounded mapping-status review keeps both deferred and not report-eligible from that review alone.
- Future OECD advancement starts from `artifacts/reports/canonicalization-oecd-mapping-status-review-20260618.json` plus `artifacts/reports/canonicalization-oecd-unit-basis-comparability-20260618.json`.
- Future Eurostat advancement starts from `artifacts/reports/canonicalization-deferred-mapping-advancement-requirements-20260618.json`.
- TASK-041 found MacroForge partially research-ready: same-source descriptive and boundary findings were supported, while trustworthy cross-source GDP research remained blocked by missing deterministic eligibility/comparability classification and absent conversion/aggregation policy.
- TASK-042 created `artifacts/reports/gdp-eligibility-classification-20260619.json`, the compact deterministic eligibility contract for current GDP evidence. WDI is eligible only for bounded WDI-only descriptive findings with governed provisional caveats; OECD `USD_EXC`/`USD_PPP` remain deferred and profile-specific; Eurostat `CP_MEUR` remains deferred/profile-specific with cross-source annual/current-USD use blocked by missing frequency/currency/scale policy.

## Current architecture decisions

DEC-005 keeps the immediate architecture intentionally minimal: raw SQL migrations, PostgreSQL, psql/Python loaders, CLI runbooks, and tests. Alembic, SQLAlchemy, orchestration platforms, Docker, and broad source frameworks remain deferred until real schema evolution, multiple manual source pipelines, or repeated non-semantic duplication prove that abstraction would reduce recurring effort without weakening trust.

DEC-006 through DEC-021 remain as recorded. DEC-018 governs canonicalization/comparability design; DEC-019 selected the tiny deterministic proposal workflow; DEC-020 accepted the narrow canonical asset manifest registry; DEC-021 selected bounded WDI unit metadata enrichment. TASK-042 provides a file-backed eligibility classification artifact but does not accept production canonicalization persistence, model use, report integration, direct base-state mutation, direct manifest mutation, conversion, aggregation, or OECD mapping advancement.

## Deferred areas

The following remain deferred unless a new accepted decision changes scope:

- production PostgreSQL persistence for canonicalization state;
- AI/model calls for canonicalization proposals;
- report integration of lifecycle-derived mappings;
- unit/currency conversion or frequency aggregation;
- generalized ingestion, metadata, source, orchestration, dbt/Dagster, Alembic, SQLAlchemy, Docker, or mart-layer expansion;
- direct mutation of accepted/base mapping state or canonical manifests without explicit review artifact approval.

## Next architecture work

No next architecture task is open. MacroForge should stop expanding after TASK-042 unless a downstream consumer produces a concrete evidence-backed blocker. Any future architecture or canonicalization task should start from current recovery anchors rather than re-reading full task chronology: `state/active_goal.md`, `artifacts/reports/_SUMMARY.md`, `artifacts/tasks/backlog.md`, the GDP eligibility classification artifact, and the latest OECD/Eurostat canonicalization reports named above.
