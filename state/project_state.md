# Project State

Project: MacroForge
Template: python_data_project
Canonical path: `/home/mkkto/srv/EIP/projects/MacroForge`
Last updated UTC: 2026-06-18T08:45:52Z

## Current state

MacroForge is a ProjectForge-generated autonomous EIP project and AI-first macroeconomic and investing research platform. Its governing purpose is to progressively reduce the recurring effort required to build, maintain, validate, canonicalize, and use trusted macroeconomic data for investment-relevant research. Trusted macroeconomic databases and datasets are outputs; the effort-reduction system is the project. Previous deleted MacroForge files and Desktop/ChatGPT exports are historical evidence only unless explicitly curated into current artifacts.

TASK-004 through TASK-039 are complete. TASK-031 was an Architecture-to-Reality remediation hygiene interruption and did not supersede the domain sequence. TASK-035 retrofitted ProjectForge-generated MetaHarvest compatibility placeholders and implemented `MF-AH-REV-001` narrowly as a file-backed canonical asset manifest registry. TASK-034 implemented the deterministic canonicalization proposal workflow. TASK-036 completed DEC-021 and selected TASK-037. TASK-037 completed bounded WDI unit metadata enrichment for canonicalization evidence. TASK-038 validated the proposal -> review -> accepted/provisional lifecycle in bounded file-backed form, demonstrating one governed provisional WDI outcome and deferred OECD/Eurostat outcomes with explicit decisions, gates, deltas, lineage, and replay evidence. TASK-039 persisted the deferred OECD/Eurostat mapping advancement requirements as compact JSON/Markdown recovery artifacts.

ProjectForge continuity/recovery adoption is complete via `artifacts/tasks/TASK-PF-20260614-continuity-recovery-adoption.md`. Fresh MacroForge sessions can run `python3 tools/recover_session.py --project . --json` to recover state, active/recent task, recent decisions, blockers, next actions, and resume procedure without broad repository scanning.

## Implemented domain substrate

- Raw SQL/PostgreSQL foundation with schemas `meta`, `staging`, and `curated`; `mart` remains deferred.
- Migrations:
  - `001_v0_schema_foundation.sql`
  - `002_oecd_sdmx_staging.sql`
  - `003_canonical_domain_dimensions.sql`
  - `004_eurostat_namq_staging.sql`
- Source-specific bounded paths:
  - WDI raw evidence, loader, validation, and isolated smoke.
  - OECD/SDMX evidence, codelist/label metadata, `staging.oecd_sdmx_observation`, loader, and isolated load smoke.
  - Eurostat `namq_10_gdp` recorded fixture, `staging.eurostat_namq_observation`, loader, provider mappings/dictionaries, and isolated load smoke.
- Canonical-domain foundation:
  - structured canonical periods;
  - ISO3-preserved country territories and territory types;
  - provider period/territory mappings;
  - provider code lists/codes;
  - source-agnostic curated facts.
- Combined-source canonical validation smoke and first canonical GDP snapshot report are complete.
- Minimal AI-assisted canonicalization/comparability design is accepted in DEC-018.
- TASK-032 implemented a fixture-backed canonicalization state foundation with provider evidence, deterministic run/proposal state, unit/comparability profiles, provisional accepted mappings, review routing, and supersession mechanics.
- TASK-033 completed DEC-019, selecting a tiny deterministic proposal-generation workflow as the next uncertainty-reduction step.
- TASK-035 implemented DEC-020: `artifacts/manifests/canonical_assets.json`, a tiny file-backed canonical asset/manifest registry seeded only from existing artifacts.
- TASK-034 implemented a tiny deterministic proposal workflow over existing TASK-032 WDI/OECD/Eurostat GDP fixture state, producing review-required workflow proposals, no-auto-apply mapping update proposals, and `artifacts/reports/canonicalization-proposal-workflow-20260613.json`.
- TASK-036 completed DEC-021 and selected bounded WDI unit metadata enrichment as the next uncertainty-reduction step.
- TASK-037 implemented bounded WDI-specific fixture metadata enrichment for existing `NY.GDP.MKTP.CD` canonicalization evidence. It reduced WDI `unknown_unit_metadata` in proposal evidence to explicit current-USD metadata evidence while preserving no-unit-conversion, high-impact review routing, proposal/accepted-state separation, no auto-apply, and non-WDI source behavior.
- TASK-038 produced `artifacts/reports/canonicalization-review-lifecycle-20260614.json` and `.md`, validating a bounded proposal -> review -> accepted/provisional lifecycle over existing WDI/OECD/Eurostat GDP evidence. It records explicit review decisions, check gates, state deltas, manifest deltas, lineage edges, and replay inputs. WDI moved to governed provisional; OECD and Eurostat remained deferred.

## Active objective

No open implementation task after TASK-039 closeout. Future OECD/Eurostat GDP mapping advancement work should start from `artifacts/reports/canonicalization-deferred-mapping-advancement-requirements-20260618.json` and satisfy its minimum advancement conditions before changing mapping status, accepted/base state, manifest state, or report behavior.

## Current governance posture

- Use Hermes tools directly for normal agent work; `tools/run.py` is for manual/non-Hermes audited command execution when useful.
- Evaluate future work by asking which recurring effort it reduces: source onboarding, source maintenance, validation, canonical mapping, schema evolution, downstream analysis, or future agent recovery/context effort.
- The primary audit trail is task, decision, handoff, state, and report artifacts.
- Governance exists to reduce future uncertainty and agent recovery cost; artifacts that do not improve trust, reproducibility, maintainability, semantic correctness, or recurring effort reduction should be deferred, pruned, or consolidated.
- Operational logs are optional debugging artifacts, not the source of truth for normal governance.
- Primary state artifacts should remain concise current-state pointers. Historical verification detail belongs in task/report/handoff artifacts.
- Run Architecture-to-Reality Audits every 5-10 completed tasks and before major architecture/governance reviews.

## Boundaries for next work

Until a new task/decision explicitly changes scope, future canonicalization lifecycle work must not call AI/models for canonicalization, configure prompts/providers, onboard new sources, live-fetch without separate approval, write to live/default `macro`, add PostgreSQL migrations, implement unit/currency conversion, aggregate quarterly to annual, integrate canonicalization state into GDP reports, extract generalized metadata/source frameworks, add provider-specific fact columns, auto-apply accepted mappings, directly mutate lifecycle-derived accepted state without explicit review artifact approval, or push to git.

## Durable pointers

- Active goal: `state/active_goal.md`
- Architecture state: `state/architecture.md`
- Generated-project architecture state: `architecture/architecture_state.md`
- MetaHarvest compatibility review history: `architecture/architectureharvest/review_history.md`
- Latest handoff: `context/latest_handoff.md`
- Backlog: `artifacts/tasks/backlog.md`
- Pre-TASK-038 canonicalization evidence: TASK-032/TASK-034/TASK-037 artifacts listed in `artifacts/tasks/backlog.md` and `artifacts/reports/_SUMMARY.md`
- Completed TASK-038: `artifacts/tasks/TASK-038-simulate-bounded-canonicalization-review-lifecycle.md`
- TASK-038 lifecycle artifact: `artifacts/reports/canonicalization-review-lifecycle-20260614.json`
- TASK-038 lifecycle report: `artifacts/reports/canonicalization-review-lifecycle-20260614.md`
- Completed TASK-039: `artifacts/tasks/TASK-039-persist-deferred-mapping-advancement-requirements.md`
- TASK-039 requirements artifact: `artifacts/reports/canonicalization-deferred-mapping-advancement-requirements-20260618.json`
- TASK-039 requirements report: `artifacts/reports/canonicalization-deferred-mapping-advancement-requirements-20260618.md`
- Canonicalization implementation: `src/macroforge/canonicalization_state.py`
- Accepted canonicalization design: `docs/architecture/minimal-ai-assisted-canonicalization-layer.md`
- Completed TASK-035: `artifacts/tasks/TASK-035-implement-narrow-architectureharvest-canonical-asset-manifest.md`
- DEC-020: `artifacts/decisions/DEC-020-architectureharvest-canonical-asset-manifest-registry.md`
- Canonical asset manifest: `artifacts/manifests/canonical_assets.json`
