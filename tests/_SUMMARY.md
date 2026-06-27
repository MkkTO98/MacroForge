# Folder Summary: tests

## Purpose
Tests for MacroForge source evidence, loaders, database schema, canonical-domain behavior, canonicalization helpers, reports, fixture persistence, and ProjectForge integration.

## Contains
<!-- PROJECTFORGE:BEGIN-CONTAINS -->
- `fixtures/`
- `invariants/`
- `test_architectureharvest_integration.py`
- `test_canonical_gdp_snapshot.py`
- `test_canonicalization_proposal_workflow.py`
- `test_canonicalization_state.py`
- `test_combined_source_smoke.py`
- `test_consult_metaharvest.py`
- `test_db_helpers.py`
- `test_deterministic_change_verification.py`
- `test_eurostat_namq_loader.py`
- `test_fixture_persistence.py`
- `test_observed_ingestion.py`
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
- `test_observed_ingestion.py` covers `ObservedIngestionPackage` v1 WDI/OECD/Eurostat semantics plus deterministic package fingerprinting, equivalent package comparison, changed-observation diagnostics, and anti-framework constraints.
- `test_deterministic_change_verification.py` proves the Specified -> Verified transition by loading WDI/OECD/Eurostat into isolated PostgreSQL, reconstructing observed packages from staging/canonical outputs, and comparing them with expected fixture-backed packages.
- WDI/OECD/Eurostat loader tests preserve source-specific SQL/staging/provider mapping/lineage/quality behavior while loaders consume the extracted representation.
- `test_combined_source_smoke.py` verifies combined isolated PostgreSQL behavior for all supported sources.
- `test_fixture_persistence.py` covers TASK-045's clean-clone fixture-persistence guard.
- `test_consult_metaharvest.py` covers trigger-gated MetaHarvest consultation, including the v2 `foundational_capability_extraction` trigger and diagnostic-only replay non-trigger behavior.
- Canonicalization tests cover deterministic file-backed proposal/review mechanics and remain separate from ingestion runtime.

## Needs Attention
- Any future `ObservedIngestionPackage` contract evolution must run `test_observed_ingestion.py`, relevant loader tests, combined-source smoke tests, and full pytest.
- Preserve fixture-backed and isolated-PostgreSQL coverage if OECD/SDMX, Eurostat, combined-source validation, canonical report generation, canonicalization state mechanics, proposal workflow mechanics, or WDI metadata enrichment are later broadened.
