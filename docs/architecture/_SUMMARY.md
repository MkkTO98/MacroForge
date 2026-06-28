# Folder Summary: docs/architecture

## Purpose
Architecture documentation for MacroForge data/research platform.

## Contains
<!-- PROJECTFORGE:BEGIN-CONTAINS -->
- `ai-assisted-canonicalization-governance-review.md`
- `bounded-eurostat-postgresql-promotion-design.md`
- `canonical-domain-schema-evolution.md`
- `canonicalization-next-scope-decision-analysis.md`
- `canonicalization-post-proposal-next-scope-decision-analysis.md`
- `capability-maturity-model.md`
- `historical-architecture-reconciliation.md`
- `metaharvest-trigger-gated-consultation.md`
- `minimal-ai-assisted-canonicalization-layer.md`
- `minimal-canonical-domain-schema-design.md`
- `observed-ingestion-representation.md`
- `overview.md`
<!-- PROJECTFORGE:END-CONTAINS -->

## Active Work
- `capability-maturity-model.md` is the active v1.1 implementation-planning model. It uses the lifecycle Discovered -> Specified -> Verified -> Adopted -> Shared -> Stable -> Mature, records lightweight Verified prerequisites for safe advancement, records Observed Boundary and Contract Stability plus Canonical Lineage Event Generation plus Contract Validation and Drift Detection plus Deterministic Ingestion Feedback as Verified, includes the standard foundational capability extraction checklist, and now records next-ten-source Evidence-Accumulating Source Expansion through completed TASK-054 Treasury Fiscal Data evidence.
- `observed-ingestion-representation.md` documents `ObservedIngestionPackage` v1 as a public internal architectural contract extracted from implemented WDI/OECD/Eurostat behavior. It records field purpose/ownership/status, invariants, boundaries, compatibility expectations, versioning policy, and explicit out-of-contract areas.
- `metaharvest-trigger-gated-consultation.md` documents the implemented Phase 1 helper at `tools/consult_metaharvest.py`: scoped task/governance preflight only, separate Consultation/Retrieval Contracts, versioned internal taxonomy, bounded advisory retrieval, non-blocking failure, and mandatory Authority note.
- `minimal-ai-assisted-canonicalization-layer.md` remains the accepted TASK-030 design for provider evidence, canonicalization runs, mapping/canonical-creation proposals, confidence/provenance/review state, accepted mappings, unit/comparability profiles, and re-canonicalization lineage.

## Needs Attention
- Treat `ObservedIngestionPackage` field/semantic changes as contract evolution, not routine implementation refactoring.
- The next source-expansion task should attempt to falsify the default substrate-stability assumption; do not design substrate features ahead of repeated implementation evidence.
- Preserve no unit conversion, report integration, database persistence, AI/model calls, generalized ingestion frameworks, plugin systems, or source registries unless explicitly changed by a new task/decision.
