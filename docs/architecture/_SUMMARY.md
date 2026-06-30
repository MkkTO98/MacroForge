# Folder Summary: docs/architecture

## Purpose
Architecture documentation for MacroForge data/research platform.

## Contains
<!-- PROJECTFORGE:BEGIN-CONTAINS -->
- `ai-assisted-canonicalization-governance-review.md`
- `architectural-confidence-ledger.md`
- `architectural-surprise-log.md`
- `bounded-eurostat-postgresql-promotion-design.md`
- `canonical-domain-schema-evolution.md`
- `canonicalization-next-scope-decision-analysis.md`
- `canonicalization-post-proposal-next-scope-decision-analysis.md`
- `capability-maturity-model.md`
- `historical-architecture-reconciliation.md`
- `marginal-source-cost-index.md`
- `recurring-implementation-pain.md`
- `metaharvest-trigger-gated-consultation.md`
- `minimal-ai-assisted-canonicalization-layer.md`
- `minimal-canonical-domain-schema-design.md`
- `observed-ingestion-representation.md`
- `overview.md`
<!-- PROJECTFORGE:END-CONTAINS -->

## Active Work
- `architectural-confidence-ledger.md` records lightweight confidence estimates for current MacroForge architectural assumptions, includes TASK-055 post-implementation calibration, and requires calibration after every heterogeneous source implementation: confidence before, confidence after, direction, evidence for every tracked assumption, and a lightweight Prediction Quality value: Accurate, Mostly Accurate, Mixed, or Poor.
- `architectural-surprise-log.md` records only material prediction mismatches from heterogeneous source implementations; TASK-055 recorded no material architectural surprise, and summaries belong in implementation lessons, not the surprise log.
- `marginal-source-cost-index.md` records approximate engineering, human, LLM reasoning, and architectural-confidence estimates after heterogeneous implementations for trend detection, not precision.
- `recurring-implementation-pain.md` records recurring implementation difficulties; repeated pain, not repeated code, is the primary evidence for future extraction candidates.
- `capability-maturity-model.md` is the active v1.1 implementation-planning model. It uses the lifecycle Discovered -> Specified -> Verified -> Adopted -> Shared -> Stable -> Mature, records lightweight Verified prerequisites for safe advancement, records Observed Boundary and Contract Stability plus Canonical Lineage Event Generation plus Contract Validation and Drift Detection plus Deterministic Ingestion Feedback as Verified, includes the standard foundational capability extraction checklist, and now records next-ten-source Evidence-Accumulating Source Expansion through completed TASK-054 Treasury Fiscal Data evidence.
- `observed-ingestion-representation.md` documents `ObservedIngestionPackage` v1 as a public internal architectural contract extracted from implemented WDI/OECD/Eurostat behavior. It records field purpose/ownership/status, invariants, boundaries, compatibility expectations, versioning policy, and explicit out-of-contract areas.
- `metaharvest-trigger-gated-consultation.md` documents the implemented Phase 1 helper at `tools/consult_metaharvest.py`: scoped task/governance preflight only, separate Consultation/Retrieval Contracts, versioned internal taxonomy, bounded advisory retrieval, non-blocking failure, and mandatory Authority note.
- `minimal-ai-assisted-canonicalization-layer.md` remains the accepted TASK-030 design for provider evidence, canonicalization runs, mapping/canonical-creation proposals, confidence/provenance/review state, accepted mappings, unit/comparability profiles, and re-canonicalization lineage.

## Needs Attention
- Treat `ObservedIngestionPackage` field/semantic changes as contract evolution, not routine implementation refactoring.
- TASK-055 showed SDMX GenericData mechanics repeating across OECD and ECB, but did not justify an SDMX Interpretation Layer. Continue source-specific-first implementation until repeated evidence satisfies the extraction gate.
- Outside the five-source Retrospective Review decision gate, follow the frozen execution loop: select source, predict, implement, verify, lessons, surprise log, confidence calibration including Prediction Quality, cost-index update, pain update, then continue. Methodology changes now require extraction-grade repeated implementation evidence; elegance, consistency, or theoretical appeal are insufficient.
- Preserve no unit conversion, report integration, database persistence, AI/model calls, generalized ingestion frameworks, plugin systems, or source registries unless explicitly changed by a new task/decision.
