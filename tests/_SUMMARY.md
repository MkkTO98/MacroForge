# Folder Summary: tests

## Purpose
This folder is part of the ProjectForge file-backed operating system for `tests`.

## Contains
<!-- PROJECTFORGE:BEGIN-CONTAINS -->
- `fixtures/`
- `invariants/`
- `test_architectureharvest_integration.py`
- `test_canonical_gdp_snapshot.py`
- `test_canonicalization_proposal_workflow.py`
- `test_canonicalization_state.py`
- `test_combined_source_smoke.py`
- `test_db_helpers.py`
- `test_eurostat_namq_loader.py`
- `test_oecd_sdmx.py`
- `test_oecd_sdmx_codelists.py`
- `test_oecd_sdmx_loader.py`
- `test_placeholder.py`
- `test_schema_foundation.py`
- `test_wdi.py`
- `test_wdi_loader.py`
- `test_wdi_smoke.py`
- `test_wdi_validation.py`
<!-- PROJECTFORGE:END-CONTAINS -->

## Active Work
- `test_canonicalization_proposal_workflow.py` covers TASK-034's deterministic proposal workflow and TASK-037's WDI unit metadata enrichment: provider-evidence-derived proposal generation, proposal/accepted-state separation, review routing, WDI unknown-unit caveat reduction through fixture metadata evidence, non-WDI unchanged behavior, annual/quarterly non-aggregation, no unit conversion, no-auto-apply mapping update proposals, and deterministic audit writing.
- `test_architectureharvest_integration.py` covers TASK-035's ArchitectureHarvest placeholder retrofit and canonical asset manifest registry shape/path/provider-truth boundaries.
- `test_canonicalization_state.py` covers TASK-032's deterministic canonicalization state foundation: proposal-vs-accepted-state separation, unit comparability caveats, annual/quarterly non-aggregation, high-impact review routing, supersession lineage, and deterministic audit writing.
- `test_canonical_gdp_snapshot.py` covers TASK-028 isolated canonical report generation, canonical/meta-only SQL boundary, deterministic JSON/Markdown writers, and real PostgreSQL report output.

## Needs Attention
- Preserve fixture-backed and isolated-PostgreSQL TDD coverage if OECD/SDMX, Eurostat, combined-source validation, canonical report generation, canonicalization state mechanics, proposal workflow mechanics, or WDI metadata enrichment are later broadened.
