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
- `historical-architecture-reconciliation.md`
- `minimal-ai-assisted-canonicalization-layer.md`
- `minimal-canonical-domain-schema-design.md`
- `metaharvest-trigger-gated-consultation.md`
- `overview.md`
<!-- PROJECTFORGE:END-CONTAINS -->

## Active Work
- `metaharvest-trigger-gated-consultation.md` documents the implemented Phase 1 helper at `tools/consult_metaharvest.py`: scoped task/governance preflight only, separate Consultation/Retrieval Contracts, versioned internal taxonomy, bounded advisory retrieval, non-blocking failure, and mandatory Authority note.
- `overview.md` now records the doctrine-aligned architecture purpose: MacroForge is the system for reducing recurring effort to build, maintain, validate, canonicalize, and use trusted macroeconomic data; trusted databases/datasets are outputs.
- `minimal-ai-assisted-canonicalization-layer.md` remains the accepted TASK-030 design for provider evidence, canonicalization runs, mapping/canonical-creation proposals, confidence/provenance/review state, accepted mappings, unit/comparability profiles, and re-canonicalization lineage.
- Historical decision-analysis notes remain evidence for the bounded sequencing through TASK-037.

## Needs Attention
- TASK-037 is complete. The next recommended architecture validation candidate is a bounded, file-backed proposal review-to-accepted/provisional state lifecycle simulation, but no TASK-038 has been created or approved.
- Frame that candidate as testing whether MacroForge can reduce future manual canonicalization effort while preserving trust, provenance, and review-gated semantic correctness. Preserve no unit conversion, report integration, database persistence, AI/model calls, new sources, or generalized metadata framework boundaries unless explicitly changed by a new task/decision.
