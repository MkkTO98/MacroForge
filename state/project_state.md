# Project State

Project: MacroForge
Template: python_data_project
Canonical path: `/home/mkkto/srv/EIP/projects/MacroForge`
Last updated UTC: 2026-06-27T01:50:21Z

## Current state

MacroForge is governed by Strategic Constitution v1.1. It exists to transform heterogeneous public economic evidence into deterministic, canonical, auditable observations suitable for long-term analytical use. Its strategic asset is increasingly reusable, trustworthy, deterministic ingestion capability; data and PostgreSQL outputs are products of that capability.

TASK-004 through TASK-046 are complete. MacroForge has source-specific WDI/OECD/Eurostat GDP evidence paths, a canonical-domain PostgreSQL foundation, deterministic file-backed canonicalization/proposal/review evidence, GDP eligibility classification, trigger-gated advisory-only MetaHarvest consultation, repaired WDI isolated smoke, clean-clone-safe OECD/Eurostat fixture persistence, a narrow `ObservedIngestionPackage` v1 contract extracted from current WDI/OECD/Eurostat behavior, deterministic package fingerprint/equivalence diagnostics, and end-to-end isolated PostgreSQL proof that deterministic change verification works for all supported sources.

The current strategic reassessment is recorded in `artifacts/reports/R-20260626-strategic-constitution-v11-backlog-reassessment.md`. The final governance alignment assessment is recorded in `artifacts/reports/R-20260627-governance-alignment-after-strategic-constitution-v11.md`. The final v1.1 governance refinement/freeze is recorded in `artifacts/reports/R-20260627-final-governance-refinement-and-freeze.md`.

## Current capability summary

- Raw SQL/PostgreSQL foundation exists with `meta`, `staging`, and `curated` schemas; `mart` remains deferred.
- Source-specific bounded paths exist for WDI, OECD/SDMX, and Eurostat GDP evidence/loading/validation.
- `ObservedIngestionPackage` v1 exists as the public internal handoff contract between source-specific normalization and existing source-specific canonical load SQL.
- Canonical-domain substrate exists for structured periods, ISO3-preserved territories, provider mappings/codes, units/attribute sets, and source-agnostic curated facts.
- Combined-source canonical validation and the first canonical GDP snapshot report are complete.
- Implemented canonicalization remains deterministic and file-backed; DEC-018 accepts the AI-assisted canonicalization design only conceptually.
- Strategic Constitution v1.1 reprioritizes the roadmap around compounding deterministic ingestion capability and reducing future engineering/human/LLM effort.

## Capability maturity snapshot

Lifecycle: Discovered -> Specified -> Verified -> Adopted -> Shared -> Stable -> Mature.

- Observed Boundary and Contract Stability: Specified. Target: Adopted, then Stable. Next transition: Specified -> Verified.
- Deterministic Change Verification: Verified. Target: Stable. Next transition: Verified -> Adopted.
- Contract Validation and Drift Detection: Discovered. Target: Verified. Next transition: Discovered -> Specified.
- Ingestion Diagnostics and Recovery Evidence: Discovered. Target: Verified. Next transition: Discovered -> Specified.
- Shared Post-Boundary Infrastructure Extraction: Discovered. Target: Verified readiness, not immediate Shared. Next transition: Discovered -> Specified after change-verification evidence and consultation.
- Canonicalization Governance and Mapping Advancement: Stable for file-backed lifecycle; Discovered/Specified for OECD/Eurostat advancement. Target: preserve Stable lifecycle; verify targeted advancement only when needed.
- Knowledge-Accumulating Source Expansion: Discovered. Target: Specified only after verification/diagnostics capabilities mature.

## Active objective

MacroForge has entered implementation-driven development.

Default cycle:

```text
Implement capability transition
    ↓
Verify deterministically
    ↓
Update capability maturity
    ↓
Select next capability transition
    ↓
Implement
```

Architectural reports should only be created when implementation exposes uncertainty that cannot be resolved from the existing Constitution, contracts, capability model, dependency graph, or deterministic verification evidence.

Current capability: Deterministic Change Verification.

Completed transition: Specified -> Verified through isolated PostgreSQL end-to-end proof for WDI, OECD, and Eurostat.

Next transition: Verified -> Adopted, only after MacroForge makes this verified path the required change-verification path for relevant ingestion/package changes.

## Current governance posture

- Optimize for decreasing marginal data acquisition/update/validation/maintenance cost without sacrificing determinism, auditability, provenance, or canonical consistency.
- Extract shared infrastructure only from evidence: converged contract, converged algorithm, and converged implementation.
- Generic shared infrastructure must not contain source-specific conditionals; source-specific behavior belongs in adapters.
- Increase ArchitectureHarvest consultation intensity before foundational capability extraction: proposed implementation expected to become a reusable dependency of multiple future capabilities triggers `foundational_capability_extraction`. Routine work keeps bounded consultation policy.
- Primary audit trail: constitution, task, decision, handoff, state, and report artifacts. Operational logs are optional debugging artifacts.
- Treat `ObservedIngestionPackage` field/semantic changes as contract evolution requiring equivalence verification across WDI/OECD/Eurostat.

## Boundaries for next work

Until a new task/decision explicitly changes scope, future work must not:

- call AI/models for canonicalization or configure prompt/provider behavior;
- onboard new sources, deepen datasets, live-fetch data, write to live/default `macro`, or add PostgreSQL migrations;
- mutate mapping status, accepted/base state, canonical manifests, or reports without explicit review artifact approval;
- implement unit/currency conversion, frequency aggregation, generalized ingestion/source frameworks, plugin systems, provider-specific fact columns, or auto-apply mappings;
- push to git.

## Durable recovery anchors

- Constitution: `CONSTITUTION.md`
- Active goal: `state/active_goal.md`
- Architecture state: `state/architecture.md`
- Latest handoff: `context/latest_handoff.md`
- Backlog/task chronology: `artifacts/tasks/backlog.md`
- Reports summary: `artifacts/reports/_SUMMARY.md`
- Strategic reassessment: `artifacts/reports/R-20260626-strategic-constitution-v11-backlog-reassessment.md`
- TASK-046: `artifacts/tasks/TASK-046-extract-observed-common-ingestion-representation.md`
- ObservedIngestionPackage contract: `docs/architecture/observed-ingestion-representation.md`
