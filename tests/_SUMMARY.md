# Folder Summary: tests

## Purpose
Tests for MacroForge source evidence, loaders, database schema, canonical-domain behavior, canonicalization helpers, reports, fixture persistence, and ProjectForge integration.

## Contains
<!-- PROJECTFORGE:BEGIN-CONTAINS -->
- `fixtures/`
- `invariants/`
- `test_alfred_gdp_vintage.py`
- `test_architectureharvest_integration.py`
- `test_bea_nipa.py`
- `test_bis_cbpol.py`
- `test_bls_cpi.py`
- `test_canonical_gdp_snapshot.py`
- `test_canonicalization_proposal_workflow.py`
- `test_canonicalization_state.py`
- `test_combined_source_smoke.py`
- `test_consult_metaharvest.py`
- `test_contract_drift.py`
- `test_db_helpers.py`
- `test_ecb_sdw.py`
- `test_eurostat_energy_balance.py`
- `test_eurostat_input_output.py`
- `test_deterministic_change_verification.py`
- `test_eurostat_namq_loader.py`
- `test_fixture_persistence.py`
- `test_ilostat_unemployment.py`
- `test_imf_mfs_ir.py`
- `test_ingestion_feedback.py`
- `test_lineage_generation.py`
- `test_observed_ingestion.py`
- `test_oecd_sdmx.py`
- `test_oecd_sdmx_codelists.py`
- `test_oecd_sdmx_loader.py`
- `test_placeholder.py`
- `test_treasury_fiscal_data.py`
- `test_un_comtrade_trade.py`
- `test_schema_foundation.py`
- `test_wdi.py`
- `test_wdi_demographics.py`
- `test_wdi_loader.py`
- `test_wdi_smoke.py`
- `test_wdi_validation.py`
<!-- PROJECTFORGE:END-CONTAINS -->

## Active Work
- `test_fred_yield_curve.py` verifies TASK-065 bounded FRED yield-curve fixture normalization, same-period tenor curve metadata preservation, observed-package contract validity, deterministic replay, fixture persistence, and anti-framework boundaries.
- `test_eurostat_energy_balance.py` verifies TASK-064 bounded Eurostat energy balance fixture normalization, energy balance component and fuel/product metadata preservation, observed-package contract validity, deterministic replay, fixture persistence, and anti-framework boundaries.
- `test_imf_bop_financial_account.py` verifies TASK-063 bounded IMF BOP financial-account fixture normalization, asset/liability accounting-entry and direct/portfolio investment-category metadata preservation, observed-package contract validity, deterministic replay, fixture persistence, and anti-framework boundaries.
- `test_eurostat_input_output.py` verifies TASK-062 bounded Eurostat input-output matrix fixture normalization, product-by-product matrix-cell shape, stock-flow/product-role/CPA metadata preservation, observed-package contract validity, deterministic replay, fixture persistence, and anti-framework boundaries.
- `test_wdi_demographics.py` verifies TASK-061 bounded WDI demographic foundation fixture normalization, required foundation concepts, unit/concept metadata preservation, observed-package contract validity, deterministic replay, fixture persistence, and anti-framework boundaries.
- `test_un_comtrade_trade.py` verifies TASK-060 bounded UN Comtrade bilateral total-goods trade fixture normalization, reporter/partner/flow/product/value-basis metadata preservation, observed-package contract validity, deterministic replay, fixture persistence, and anti-framework boundaries.
- `test_ilostat_unemployment.py` verifies TASK-059 bounded ILOSTAT unemployment-rate fixture normalization, labor classification/status/source metadata preservation, observed-package contract validity, deterministic replay, fixture persistence, and anti-framework boundaries.
- `test_alfred_gdp_vintage.py` verifies TASK-058 bounded ALFRED GDP revision-vintage fixture normalization, provider-backed vintage identity, changed and unchanged overlapping values, observed-package contract validity, deterministic replay, and anti-framework boundaries.
- `test_bis_cbpol.py` verifies TASK-057 bounded BIS WS_CBPOL fixture normalization, BIS policy-rate metadata preservation, observed-package contract validity, deterministic replay, and anti-framework boundaries.
- `test_imf_mfs_ir.py` verifies TASK-056 bounded IMF MFS_IR fixture normalization, IMF dataflow/DSD/dimension/codelist/attribute metadata preservation, observed-package contract validity, deterministic replay, and anti-framework boundaries.
- `test_ecb_sdw.py` verifies TASK-055 bounded ECB SDW fixture normalization, ECB metadata/provenance preservation, observed-package contract validity, deterministic replay, and anti-framework boundaries.
- `test_treasury_fiscal_data.py` verifies TASK-054 bounded Treasury Fiscal Data fixture normalization, query/endpoint/pagination metadata preservation, observed-package contract validity, deterministic replay, and anti-framework boundaries.
- `test_bea_nipa.py` verifies TASK-053 bounded BEA NIPA fixture normalization, observed-package contract validity, deterministic replay, and anti-framework boundaries.
- `test_ingestion_feedback.py` verifies TASK-052 Deterministic Ingestion Feedback: contract-failure explanations, package-comparison changed-observation explanations, lineage event explanations, and qualitative engineering-effort profiles for WDI/OECD/Eurostat/BLS.
- `test_contract_drift.py` covers TASK-049's specified contract drift model: all supported packages satisfy invariant checks, and package/observation drift emits deterministic issue codes, paths, and messages.
- `test_observed_ingestion.py` covers `ObservedIngestionPackage` v1 WDI/OECD/Eurostat semantics plus deterministic package fingerprinting, equivalent package comparison, changed-observation diagnostics, and anti-framework constraints.
- `test_deterministic_change_verification.py` proves the Specified -> Verified transition by loading WDI/OECD/Eurostat into isolated PostgreSQL, reconstructing observed packages from staging/canonical outputs, validating expected/reconstructed package contract reports, and comparing them with expected fixture-backed packages.
- WDI/OECD/Eurostat loader tests preserve source-specific SQL/staging/provider mapping/lineage/quality behavior while loaders consume the extracted representation.
- `test_combined_source_smoke.py` verifies combined isolated PostgreSQL behavior for all supported sources.
- `test_fixture_persistence.py` covers TASK-045's clean-clone fixture-persistence guard.
- `test_consult_metaharvest.py` covers trigger-gated MetaHarvest consultation, including the v2 `foundational_capability_extraction` trigger and diagnostic-only replay non-trigger behavior.
- Canonicalization tests cover deterministic file-backed proposal/review mechanics and remain separate from ingestion runtime.

## Needs Attention
- Any future `ObservedIngestionPackage` contract evolution must run `test_contract_drift.py`, `test_observed_ingestion.py`, relevant source evidence tests, relevant loader tests, combined-source smoke tests, and full pytest.
- Preserve fixture-backed and isolated-PostgreSQL coverage if OECD/SDMX, ECB SDW, Eurostat, combined-source validation, canonical report generation, canonicalization state mechanics, proposal workflow mechanics, or WDI metadata enrichment are later broadened.
