# Future Work — Trigger-Matched MetaHarvest Retrieval During MacroForge Preflight

Date: 2026-06-19
Status: future-work note only
Type: workflow recommendation artifact, not implementation

## Statement

Trigger-matched task classification should activate compact MetaHarvest retrieval during MacroForge preflight/governance classification.

This is not an implementation task and does not modify MacroForge workflow. It records the result of a practical consultation trial using TASK-042 GDP eligibility classification / comparability semantics as the test case.

## Rationale

A read-only MetaHarvest consultation trial found that compact retrieval can surface useful external pattern evidence for MacroForge tasks matching existing consultation triggers, especially canonicalization lifecycle/comparability semantics and lineage/check-contract changes.

The trial topic matched existing MacroForge MetaHarvest triggers:

- `canonicalization_architecture_changes`
- `lineage_or_validation_registry_changes`

The natural MacroForge gate is the pre-execution task/governance classification stage, after active/proposed task scope is known and before design/governance work proceeds.

## Evidence from consultation trial

Compact retrieval attempts:

1. `python3 tools/query_knowledge.py --problem canonicalization_lifecycle_comparability_eligibility_check_gates`
   - Result: no matching records.
   - Cost: about 0.36 seconds, 457 bytes.

2. `python3 tools/query_knowledge.py --keyword canonicalization`
   - Result: relevant synthesis, contradiction, adoption, and candidate records.
   - Cost: about 0.36 seconds, 2,790 bytes.

3. `python3 tools/query_knowledge.py --problem metadata_catalog_lineage_governance`
   - Result: OpenMetadata component-card evidence for schema-first entity models and lineage resources.
   - Cost: about 0.37 seconds, 871 bytes.

4. `python3 tools/query_knowledge.py --problem transformation_lineage_asset_orchestration`
   - Result: dbt and Dagster component-card evidence for manifests, contracts/tests, asset checks, metadata/schema versioning, external/source assets, and orchestration boundaries.
   - Cost: about 0.38 seconds, 1,105 bytes.

Relevant MetaHarvest records inspected after compact retrieval:

- `synthesis/data_contract_check_gate.yaml`
- `synthesis/provider_evidence_not_canonical_truth.yaml`
- `synthesis/typed_canonical_manifest.yaml`
- `synthesis/asset_key_lineage_graph.yaml`
- `synthesis/metadata_first_lineage_evidence.yaml`
- `synthesis/schema_evolution_policy_surface.yaml`
- `contradictions/contracts_vs_flexible_exploration.yaml`
- `contradictions/lineage_completeness_vs_context_bloat.yaml`
- `component_cards/dbt-contracts-tests.yaml`
- `component_cards/dagster-asset-checks-validation.yaml`
- `component_cards/openmetadata-lineage-resource.yaml`
- `component_cards/openmetadata-schema-first-entity-model.yaml`

Useful evidence surfaced:

- Accepted canonicalization and schema evolution should pass explicit checks before downstream reports treat mappings as accepted.
- Provider indicators, units, period/geography codes should remain evidence/mappings; accepted canonical state is the gate to curated/report use.
- Source evidence, canonical concepts, mappings, tables, reports, and checks can be represented as compact typed definitions before execution.
- Stable asset keys and explicit dependency edges are useful for raw -> staging -> curated -> report/canonicalization artifacts.
- Metadata/provenance/lineage should be inspectable artifacts, not only logs or run side effects.
- Strict checks fit accepted canonical state; lighter evidence reports fit exploratory source spikes.
- Full lineage should live in artifacts while normal context should load compact summaries/pointers.
- OpenMetadata contributes vocabulary for schema-first metadata entities, entity references, lineage edge details, source type, SQL/query details, pipeline references, column lineage, and authorized lineage mutation.

## Expected scope if later implemented

A later implementation, if approved, should be narrow:

- During task/preflight/governance classification, compare the active/proposed task against `architecture/architectureharvest/relevance_map.yaml` consultation triggers.
- If a material trigger matches, run compact MetaHarvest retrieval first.
- Use problem-first retrieval where a known problem catalog term exists.
- Use keyword retrieval as fallback when problem-first retrieval returns no matches.
- Inspect deeper MetaHarvest artifacts only when compact retrieval shows relevance and compact records are insufficient.
- Treat MetaHarvest output as advisory evidence only.
- Leave relevance evaluation, adoption, rejection, task creation, and implementation authority inside MacroForge.

## Explicit non-goals

- No startup-wide retrieval.
- No mandatory retrieval for all tasks.
- No MetaHarvest authority over MacroForge.
- No automatic adoption of MetaHarvest findings.
- No automatic task creation.
- No automatic workflow mutation.
- No dbt, Dagster, OpenMetadata, orchestration, catalog, or generalized ingestion runtime adoption.
- No replacement of MacroForge decisions, task artifacts, review gates, or human authority.

## Trial conclusion

The TASK-042 consultation produced enough value to justify documenting future trigger-gated MetaHarvest retrieval as a candidate workflow improvement.

The value was not mainly new doctrine: most core principles were already present inside MacroForge. The value was external confirmation, sharper vocabulary, and concrete reusable pattern names/interfaces for future canonicalization, eligibility, lineage, and check-contract work.

The consultation also exposed one retrieval-interface weakness: the most natural problem query for TASK-042 returned no results, while keyword and adjacent problem queries returned useful records. A future workflow should therefore support fallback retrieval rather than assuming exact problem-query coverage.
