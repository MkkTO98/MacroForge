# Project State

Project: MacroForge
Template: python_data_project
Canonical path: `/home/mkkto/srv/EIP/projects/MacroForge`
Last updated UTC: 2026-06-28T03:20:00Z

## Current state

MacroForge is governed by Strategic Constitution v1.1. Its strategic asset is reusable deterministic ingestion capability for transforming heterogeneous public economic evidence into canonical, auditable observations. PostgreSQL databases and datasets are outputs of that capability, not the source of truth by themselves.

TASK-004 through TASK-055 are complete. Current source evidence includes WDI, OECD_NAAG, EUROSTAT_NAMQ_GDP, bounded BLS_CPI monthly evidence, bounded BEA_NIPA table evidence, bounded TREASURY_FISCAL_DATA row-oriented government JSON evidence, and bounded ECB_SDW monthly exchange-rate SDMX evidence.

MacroForge is now optimizing Evidence-Accumulating Source Expansion for building a progressively broader corpus of trustworthy economic data while continuously reducing marginal engineering, human, and LLM reasoning effort. New bounded source implementations should generate implementation evidence that attempts to falsify the default assumption that the current post-boundary architecture is correct. Architecture evolves only when repeated implementation pain and evidence demonstrate insufficiency. The implementation methodology is now frozen and treated as stable infrastructure; methodology changes require extraction-grade repeated implementation evidence and measurable improvement, not organizational elegance, consistency, or theoretical appeal.

## Current capability summary

- `ObservedIngestionPackage` is the public internal handoff boundary after source-specific acquisition and normalization.
- Deterministic post-boundary mechanics include package fingerprinting/comparison, Deterministic Change Verification, Canonical Lineage Event Generation, Contract Validation and Drift Detection, and Deterministic Ingestion Feedback.
- WDI/OECD/Eurostat are canonical-loaded source paths. BLS_CPI, BEA_NIPA, TREASURY_FISCAL_DATA, and ECB_SDW are bounded architectural/evidence slices only; they are not broad provider support and do not have canonical PostgreSQL loaders.
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
- Evidence-Accumulating Source Expansion: Specified through TASK-055.

## Current implementation result

TASK-053 implemented a bounded BEA NIPA evidence slice from a BEA iTableCore fixture for NIPA Table 1.1.1. It produced 252 quarterly observed observations and a valid `ObservedIngestionPackage`.

Prediction review: all five predictions were confirmed. Existing substrate components remained unchanged; no observed-package contract evolution was required; effort concentrated before the boundary; pre-boundary table/line-code and interactive-table patterns emerged as evidence only; no post-boundary capability emerged.

TASK-053 Implementation Lessons were recorded in `artifacts/reports/L-20260628-task-053-implementation-lessons.md`. Future heterogeneous source implementations should add the same short lessons artifact after verification.

TASK-054 implemented the bounded U.S. Treasury Fiscal Data average-interest-rates evidence slice selected for architectural learning per unit of implementation effort. It produced 16 monthly observed observations and confirmed the previous estimation model remains valid.

TASK-055 implemented the bounded ECB SDW monthly EUR/USD exchange-rate evidence slice. It produced one monthly observed observation from SDMX GenericData XML and confirmed the existing observed boundary and deterministic post-boundary substrate still require no evolution. It recorded future SDMX extraction evidence around repeated GenericData mechanics, but no SDMX Interpretation Layer is justified by TASK-055 alone.

Detailed evidence:

- `artifacts/tasks/TASK-053-bounded-bea-nipa-evidence-slice.md`
- `artifacts/reports/R-20260627-bounded-bea-nipa-evidence-slice.md`
- `artifacts/reports/L-20260628-task-053-implementation-lessons.md`
- `artifacts/decisions/DEC-022-next-ten-source-expansion-optimization.md`
- `artifacts/reports/R-20260628-task-054-candidate-source-selection.md`
- `artifacts/reports/R-20260629-task-055-source-selection-review.md`
- `artifacts/tasks/TASK-055-bounded-ecb-sdw-architectural-experiment.md`
- `artifacts/reports/L-20260629-task-055-implementation-lessons.md`
- `docs/architecture/architectural-confidence-ledger.md`
- `docs/architecture/architectural-surprise-log.md`
- `docs/architecture/marginal-source-cost-index.md`
- `docs/architecture/recurring-implementation-pain.md`
- `artifacts/tasks/TASK-054-bounded-us-treasury-fiscal-data-evidence-slice.md`
- `artifacts/reports/L-20260628-task-054-implementation-lessons.md`

## Current governance posture

- TASK-055 is implemented and verified in the current worktree; it strengthened the source-specific-first and no-SDMX-Interpretation-Layer posture.
- Implementation methodology is frozen as stable infrastructure. Changes require extraction-grade repeated implementation evidence and measurable improvement, not elegance, consistency, or theory.
- Standard heterogeneous-source loop: prediction ledger, implementation, verification, lessons, surprise log, confidence calibration with Prediction Quality, cost-index update, and recurring-pain update.
- Five-source Retrospective Review is a decision gate only: continue unchanged or recommend exactly one evidence-justified extraction.
- Primary methodology artifacts: `docs/architecture/architectural-confidence-ledger.md`, `docs/architecture/architectural-surprise-log.md`, `docs/architecture/marginal-source-cost-index.md`, and `docs/architecture/recurring-implementation-pain.md`.
- Optimize for broader trustworthy economic data while reducing marginal engineering, human, and LLM effort without sacrificing determinism, auditability, provenance, reproducibility, or canonical consistency.
- Keep source-specific acquisition/parsing/provider interpretation/staging/mapping source-specific until repeated implementation evidence justifies extraction.
- Do not extract frameworks, orchestration, provider metadata systems, semantic validation, conversion/aggregation, broad provider support, or shared infrastructure from intuition.
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
