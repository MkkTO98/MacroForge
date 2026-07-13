# Folder Summary: architecture/metaharvest

## Purpose
This folder records MacroForge-local MetaHarvest advisory compatibility state. It is a consumer-local contract for advisory retrieval and architecture-governance context, not ownership of MetaHarvest itself and not runtime coupling.

## Contains
<!-- PROJECTFORGE:BEGIN-CONTAINS -->
- `adoption_candidates.md`
- `rejected_candidates.md`
- `relevance_map.yaml`
- `review_history.md`
<!-- PROJECTFORGE:END-CONTAINS -->

## Active Work
- MF-AH-REV-001 is recorded as adopted in modified/narrow form; local manifest lives at `artifacts/manifests/canonical_assets.json`.
- `relevance_map.yaml` includes the v1.1 `foundational_capability_extraction` trigger for proposed implementation expected to become a reusable dependency of multiple future capabilities.

## Needs Attention
- Do not treat deferred dbt/Dagster runtime or generalized ingestion candidates as approved.
- Preserve historical ArchitectureHarvest terminology in historical reports, decisions, and completed tasks.
