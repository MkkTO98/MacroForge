# DEC-020 — Narrow ArchitectureHarvest canonical asset manifest registry

Status: accepted
Date: 2026-06-08
Related review: `/home/mkkto/srv/EIP/projects/MetaHarvest/reviews/R-20260608-macroforge-first-architectureharvest-review.md`
Related recommendation: `MF-AH-REV-001`

## Decision

Adopt `MF-AH-REV-001` in a modified, narrow MacroForge-native form: a tiny file-backed canonical asset/manifest registry at `artifacts/manifests/canonical_assets.json`.

## Scope

The registry records only the currently needed fields:

- stable asset key;
- role: `raw`, `staging`, `canonical`, `report`, `mapping`, `validation`;
- status: `proposed`, `provisional`, `accepted`, `rejected`, `retired`;
- owner or review authority;
- source/provider evidence pointers;
- related artifact paths;
- canonical concept or mapping pointer where applicable;
- version/supersession pointer where applicable;
- notes/caveats.

## Boundaries

This decision does not adopt dbt, Dagster, orchestration runtime behavior, generalized ingestion framework behavior, database migrations, raw-loader changes, automatic materialization, scheduling, or live/default database writes.

Provider/source identities remain evidence and mapping metadata. They are not canonical truth.

## Rationale

The first MacroForge ArchitectureHarvest review found the highest positive benefit-to-effort opportunity in a static asset/manifest vocabulary. This captures the useful dbt/Dagster evidence while preserving MacroForge's current file-backed, source-specific, governance-gated architecture.

## Consequences

- MacroForge now has the ProjectForge-generated ArchitectureHarvest placeholder files required by coherence.
- MacroForge has a small manifest seeded only from existing canonicalization/source-contract/schema/report artifacts.
- Future lineage/check/schema-evolution registries remain deferred until local pressure appears.
- The manifest is reversible: deleting it and the test returns the project to its previous runtime behavior.
