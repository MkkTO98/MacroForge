# Project State

Project: MacroForge
Template: python_data_project
Canonical path: `/home/mkkto/srv/EIP/projects/MacroForge`
Last updated UTC: 2026-06-28T03:20:00Z

## Current state

MacroForge is governed by Strategic Constitution v1.1. Its strategic asset is reusable deterministic ingestion capability for transforming heterogeneous public economic evidence into canonical, auditable observations. PostgreSQL databases and datasets are outputs of that capability, not the source of truth by themselves.

TASK-004 through TASK-054 are complete. Current source evidence includes WDI, OECD_NAAG, EUROSTAT_NAMQ_GDP, bounded BLS_CPI monthly evidence, bounded BEA_NIPA table evidence, and bounded TREASURY_FISCAL_DATA row-oriented government JSON evidence.

MacroForge is now optimizing Evidence-Accumulating Source Expansion for making the next ten heterogeneous trustworthy source implementations progressively cheaper. New bounded source implementations should generate implementation evidence that attempts to falsify the default assumption that the current post-boundary architecture is correct. Architecture evolves only when repeated implementation evidence demonstrates insufficiency.

## Current capability summary

- `ObservedIngestionPackage` is the public internal handoff boundary after source-specific acquisition and normalization.
- Deterministic post-boundary mechanics include package fingerprinting/comparison, Deterministic Change Verification, Canonical Lineage Event Generation, Contract Validation and Drift Detection, and Deterministic Ingestion Feedback.
- WDI/OECD/Eurostat are canonical-loaded source paths. BLS_CPI, BEA_NIPA, and TREASURY_FISCAL_DATA are bounded architectural/evidence slices only; they are not broad provider support and do not have canonical PostgreSQL loaders.
- TASK-053 confirmed BEA NIPA table/line metadata fits the current observed-package contract without additive evolution.
- DEC-022 records the accepted next-ten-source optimization target, Implementation Lessons requirement, evidence-gated extraction rule, and future stability-review technical debt.
- TASK-054 confirmed Treasury Fiscal Data row-oriented API metadata fits the current observed-package contract without additive evolution.

## Capability maturity snapshot

Lifecycle: Discovered -> Specified -> Verified -> Adopted -> Shared -> Stable -> Mature.

- Observed Boundary and Contract Stability: Verified.
- Deterministic Change Verification: Verified.
- Canonical Lineage Event Generation: Verified.
- Contract Validation and Drift Detection: Verified.
- Deterministic Ingestion Feedback: Verified for current v1.1 scope.
- Shared Post-Boundary Infrastructure Extraction: Discovered.
- Canonicalization Governance and Mapping Advancement: Stable for file-backed lifecycle; targeted mapping advancement remains evidence-gated.
- Evidence-Accumulating Source Expansion: Specified through TASK-054.

## Current implementation result

TASK-053 implemented a bounded BEA NIPA evidence slice from a BEA iTableCore fixture for NIPA Table 1.1.1. It produced 252 quarterly observed observations and a valid `ObservedIngestionPackage`.

Prediction review: all five predictions were confirmed. Existing substrate components remained unchanged; no observed-package contract evolution was required; effort concentrated before the boundary; pre-boundary table/line-code and interactive-table patterns emerged as evidence only; no post-boundary capability emerged.

TASK-053 Implementation Lessons were recorded in `artifacts/reports/L-20260628-task-053-implementation-lessons.md`. Future heterogeneous source implementations should add the same short lessons artifact after verification.

TASK-054 implemented the bounded U.S. Treasury Fiscal Data average-interest-rates evidence slice selected for architectural learning per unit of implementation effort. It produced 16 monthly observed observations and confirmed the previous estimation model remains valid.

Detailed evidence:

- `artifacts/tasks/TASK-053-bounded-bea-nipa-evidence-slice.md`
- `artifacts/reports/R-20260627-bounded-bea-nipa-evidence-slice.md`
- `artifacts/reports/L-20260628-task-053-implementation-lessons.md`
- `artifacts/decisions/DEC-022-next-ten-source-expansion-optimization.md`
- `artifacts/reports/R-20260628-task-054-candidate-source-selection.md`
- `artifacts/tasks/TASK-054-bounded-us-treasury-fiscal-data-evidence-slice.md`
- `artifacts/reports/L-20260628-task-054-implementation-lessons.md`

## Current governance posture

- Optimize for decreasing marginal source implementation effort across the next ten heterogeneous trustworthy sources without sacrificing determinism, auditability, provenance, reproducibility, or canonical consistency.
- Every proposed implementation task must first answer whether it permanently reduces future engineering, human, or LLM effort for trustworthy economic datasets.
- Keep source-specific acquisition, parsing, provider metadata interpretation, staging/loading, and mapping decisions source-specific until repeated implementation evidence justifies extraction.
- Do not extract source frameworks, provider metadata frameworks, runtime orchestration, recovery automation, graph/catalog systems, semantic economic validation, conversion, aggregation, or broad provider support from intuition.
- Extract shared infrastructure only when multiple independent implementations demonstrate contract convergence, algorithm convergence, implementation convergence, deterministic verification, acceptable coupling, and measurable future effort reduction.
- Treat `ObservedIngestionPackage` field/semantic changes as contract evolution requiring deterministic verification.
- Do not push without explicit approval.

## Durable recovery anchors

- Constitution: `CONSTITUTION.md`
- Active goal: `state/active_goal.md`
- Architecture state: `state/architecture.md`
- Latest handoff: `context/latest_handoff.md`
- Backlog/task chronology: `artifacts/tasks/backlog.md`
- TASK-053: `artifacts/tasks/TASK-053-bounded-bea-nipa-evidence-slice.md`
- TASK-053 report: `artifacts/reports/R-20260627-bounded-bea-nipa-evidence-slice.md`
- DEC-022: `artifacts/decisions/DEC-022-next-ten-source-expansion-optimization.md`
- TASK-054: `artifacts/tasks/TASK-054-bounded-us-treasury-fiscal-data-evidence-slice.md`
- TASK-054 lessons: `artifacts/reports/L-20260628-task-054-implementation-lessons.md`
- Observed package contract: `docs/architecture/observed-ingestion-representation.md`
