# MetaHarvest Compatibility Adoption Candidates

Status: active

This lightweight placeholder lists MacroForge-local MetaHarvest compatibility candidates currently relevant to architecture coherence.

## Adopted narrowly

- `MF-AH-REV-001` — Create a tiny file-backed canonical asset/manifest registry for accepted/provisional canonicalization artifacts.
  - Local artifact: `artifacts/manifests/canonical_assets.json`
  - Outcome: modified/adopted narrowly as file-backed metadata only.
  - Boundary: no dbt, Dagster, orchestration runtime, generalized ingestion framework, database migration, or raw-loader changes.

## Deferred

- `MF-AH-REV-002` lineage edge artifacts — valuable after manifest pressure is proven.
- `MF-AH-REV-003` reusable contract/check artifacts — valuable for accepted canonical state after the first registry has local use.
- `MF-AH-REV-004` replacement of ad hoc validation/lineage shapes — requires more local repetition evidence.
- `MF-AH-REV-005` schema/mapping version and staleness model — only minimal version/supersession pointers are included now.
