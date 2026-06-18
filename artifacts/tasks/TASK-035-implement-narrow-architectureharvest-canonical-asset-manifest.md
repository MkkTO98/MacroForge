# TASK-035 — Implement narrow ArchitectureHarvest canonical asset manifest

Status: completed
Date: 2026-06-08
Decision: `artifacts/decisions/DEC-020-architectureharvest-canonical-asset-manifest-registry.md`
Dry run: `simulation/dry_runs/20260608_164056-dry-run.md`

## Goal

Retrofit MacroForge with missing ProjectForge-generated ArchitectureHarvest placeholder files and implement `MF-AH-REV-001` narrowly as a file-backed canonical asset/manifest registry.

## Implementation

Created generated-project ArchitectureHarvest placeholders:

- `architecture/architecture_state.md`
- `architecture/architectureharvest/relevance_map.yaml`
- `architecture/architectureharvest/adoption_candidates.md`
- `architecture/architectureharvest/rejected_candidates.md`
- `architecture/architectureharvest/review_history.md`

Created manifest:

- `artifacts/manifests/canonical_assets.json`

Added tests:

- `tests/test_architectureharvest_integration.py`

Recorded central ArchitectureHarvest outcome:

- `/home/mkkto/srv/projectforge/ArchitectureHarvest/adoption_log/O-20260608-macroforge-canonical-asset-manifest-registry.yaml`

## Boundaries preserved

No dbt, Dagster, orchestration runtime, generalized ingestion framework, database migration, raw loader change, automatic materialization, scheduling, or live/default database write was introduced.

## Verification

See final assistant report for exact command outputs.
