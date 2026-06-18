# Architecture State

Status: active

This lightweight generated-project architecture state file connects MacroForge to the current MetaHarvest advisory integration contract while preserving the local compatibility folder name `architecture/architectureharvest/`.

Authoritative current architecture remains summarized in `state/architecture.md`.

## Current MetaHarvest compatibility integration

- First MacroForge MetaHarvest compatibility review: `/home/mkkto/srv/EIP/projects/MetaHarvest/reviews/R-20260608-macroforge-first-architectureharvest-review.md`
- Implemented narrow recommendation: `MF-AH-REV-001`
- Local manifest registry: `artifacts/manifests/canonical_assets.json`

## Boundary

MacroForge keeps the implementation file-backed and minimal. This does not adopt dbt, Dagster, an orchestration runtime, a generalized ingestion framework, or new database migrations.
