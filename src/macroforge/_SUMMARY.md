# Folder Summary: src/macroforge

## Purpose
This folder contains MacroForge implementation modules for source evidence, source-specific loaders, canonical/report workflows, deterministic canonicalization helpers, and shared mechanical helpers.

## Contains
<!-- PROJECTFORGE:BEGIN-CONTAINS -->
- `__init__.py`
- `alfred_gdp_vintage.py`
- `bea_nipa.py`
- `bis_cbpol.py`
- `bls_cpi.py`
- `canonical_gdp_snapshot.py`
- `canonicalization_state.py`
- `combined_source_smoke.py`
- `contract_drift.py`
- `db_helpers.py`
- `deterministic_change_verification.py`
- `ecb_sdw.py`
- `eurostat_energy_balance.py`
- `eurostat_input_output.py`
- `eurostat_namq_loader.py`
- `ilostat_unemployment.py`
- `imf_mfs_ir.py`
- `ingestion_feedback.py`
- `lineage_generation.py`
- `observed_ingestion.py`
- `oecd_sdmx.py`
- `oecd_sdmx_loader.py`
- `treasury_fiscal_data.py`
- `un_comtrade_trade.py`
- `wdi.py`
- `wdi_demographics.py`
- `wdi_loader.py`
- `wdi_smoke.py`
- `wdi_validation.py`
<!-- PROJECTFORGE:END-CONTAINS -->

## Active Work
- `fred_yield_curve.py` implements TASK-065's bounded FRED monthly U.S. Treasury yield-curve evidence slice: source-specific CSV fixture normalization, 2024-01/2024-02 observed-package construction across 1-month, 1-year, 10-year, and 30-year tenors, market curve/tenor metadata preservation, and deterministic replay evidence, with no broad FRED support, generic market-data infrastructure, yield-curve framework, canonical loading, interpolation, or derived curve analytics.
- `eurostat_energy_balance.py` implements TASK-064's bounded Eurostat complete energy balance evidence slice: source-specific JSON-stat fixture normalization, annual DE/FR production/import/export/final-consumption observed-package construction across total energy and renewables/biofuels, energy balance component/fuel/unit metadata preservation, and deterministic replay evidence, with no broad Eurostat Energy support, generic energy infrastructure, canonical loading, unit conversion, or derived energy analytics.
- `imf_bop_financial_account.py` implements TASK-063's bounded IMF BOP financial-account evidence slice: source-specific StructureSpecificData XML fixture normalization, annual USA/JPN asset/liability direct/portfolio investment observed-package construction, BOP accounting-entry/investment-category/unit/scale/methodology/access metadata preservation, and deterministic replay evidence, with no broad BOP support, financial-account framework, canonical loading, or generic SDMX extraction.
- `eurostat_input_output.py` implements TASK-062's bounded Eurostat input-output matrix evidence slice: source-specific JSON-stat fixture normalization, annual DE/FR product-by-product matrix-cell observed-package construction, stock-flow/product-role/CPA/flat-index metadata preservation, and deterministic replay evidence, with no broad Eurostat NAIO support, generic matrix or input-output framework, CPA hierarchy, canonical loading, or KnowledgeForge semantics.
- `wdi_demographics.py` implements TASK-061's bounded WDI demographic foundation slice: source-specific World Bank JSON fixture normalization, annual USA/JPN population/growth/age/fertility/life-expectancy/urbanization observed-package construction, demographic concept/unit metadata preservation, and deterministic replay evidence, with no broad demographic support, projection system, generic demographic framework, canonical loading, or KnowledgeForge semantics.
- `un_comtrade_trade.py` implements TASK-060's bounded UN Comtrade bilateral total-goods trade domain-expansion slice: source-specific JSON fixture normalization, annual USA/JPN import/export total-goods observed-package construction, reporter/partner/flow/product/value-basis metadata preservation, and deterministic replay evidence, with no broad UN Comtrade support, generic trade infrastructure, product classification framework, mirror trade, canonical loading, or KnowledgeForge semantics.
- `ilostat_unemployment.py` implements TASK-059's bounded ILOSTAT unemployment-rate domain-expansion slice: source-specific JSON fixture normalization, annual USA/JPN unemployment-rate observed-package construction, labor classification/status/source metadata preservation, and deterministic replay evidence, with no broad ILOSTAT support, generic labor infrastructure, classification framework, canonical loading, or KnowledgeForge semantics.
- `alfred_gdp_vintage.py` implements TASK-058's bounded ALFRED GDP revision-vintage evidence slice: source-specific CSV fixture normalization, two-vintage/two-period observed-package construction, changed/unchanged overlap analysis, and deterministic replay evidence, with no broad ALFRED/FRED support, API-key infrastructure, canonical loading, generic revision infrastructure, or framework extraction.
- `bis_cbpol.py` implements TASK-057's bounded BIS WS_CBPOL architectural evidence slice: source-specific central bank policy rate SDMX StructureSpecificData fixture normalization and `ObservedIngestionPackage` construction, with no broad BIS support, generic SDMX infrastructure, canonical loading, or framework extraction.
- `imf_mfs_ir.py` implements TASK-056's bounded IMF MFS_IR architectural evidence slice: source-specific StructureSpecificData fixture normalization plus dataflow/structure/codelist metadata preservation for USA/JPN monthly interest-rate observations, with no broad IMF support, canonical loading, generic SDMX layer, provider metadata framework, or substrate extraction.
- `ecb_sdw.py` implements TASK-055's bounded ECB SDW architectural experiment: source-specific EXR monthly EUR/USD SDMX GenericData fixture normalization and `ObservedIngestionPackage` construction, with no broad ECB support, canonical loading, SDMX Interpretation Layer, source framework, or substrate extraction.
- `treasury_fiscal_data.py` implements TASK-054's bounded U.S. Treasury Fiscal Data evidence slice: source-specific average-interest-rates JSON fixture normalization and `ObservedIngestionPackage` construction for one endpoint/date, with no broad Treasury support, canonical loading, generalized acquisition, pagination framework, or substrate extraction.
- `bea_nipa.py` implements TASK-053's bounded BEA NIPA evidence slice: source-specific iTableCore table normalization and `ObservedIngestionPackage` construction for NIPA Table 1.1.1, with no broad BEA support, canonical loading, or framework extraction.
- `contract_drift.py` implements TASK-049/TASK-050's narrow Contract Validation and Drift Detection capability: deterministic `ObservedIngestionPackage` v1 package/observation invariant checks, issue codes/paths/messages, and fingerprint reproducibility. It does not validate economic correctness or introduce a generalized validation framework.
- `deterministic_change_verification.py` reconstructs loaded WDI/OECD/Eurostat observed packages from isolated PostgreSQL canonical/staging outputs, compares them with expected `ObservedIngestionPackage` contracts, and now exposes `verify_loaded_observed_package_contracts` to validate expected/reconstructed package contracts inside the verification path.
- `ingestion_feedback.py` implements TASK-052's Deterministic Ingestion Feedback: deterministic explanatory surfaces from existing contract reports, package comparisons, lineage events, and qualitative source effort evidence. It is not a diagnostics platform, recovery automation, orchestration, runtime monitor, source framework, or report runner.
- `lineage_generation.py` implements TASK-048's Canonical Lineage Event Generation: deterministic two-event generation only, with loader-owned persistence retained.
- `observed_ingestion.py`
- `treasury_fiscal_data.py` implements TASK-046's `ObservedIngestionPackage` v1 equivalence extraction: immutable package/observation dataclasses, deterministic WDI/OECD/Eurostat adapters, canonical attribute hashing, deterministic package fingerprints, package equivalence diagnostics, WDI `unknown`/`empty` conventions, and no framework/plugin/runtime behavior.
- `wdi_loader.py`, `oecd_sdmx_loader.py`, and `eurostat_namq_loader.py` consume the extracted representation where it preserves existing semantics while retaining source-specific SQL, staging, provider mappings, lineage, quality checks, and canonical fact behavior.
- `canonicalization_state.py` implements deterministic fixture-backed canonicalization state/proposal/review mechanics; it remains file-backed and does not perform model canonicalization, conversion, aggregation, or PostgreSQL persistence.
- `canonical_gdp_snapshot.py` implements the first canonical-only GDP snapshot/audit report generator, using isolated temporary PostgreSQL, existing loaders/evidence, and core `curated.*` plus `meta.*` queries.

## Needs Attention
- Treat `ObservedIngestionPackage` changes as contract evolution requiring equivalence verification across WDI/OECD/Eurostat, not ordinary refactoring.
- Keep `contract_drift.py` limited to deterministic contract drift detection; do not let it absorb economic validation, provider-specific semantic rules, repair behavior, or generalized validation framework concerns.
- Keep WDI/OECD/Eurostat/ECB/IMF/BIS/ALFRED/ILOSTAT/UN Comtrade/WDI demographics/Eurostat input-output/IMF BOP financial-account/Eurostat energy-balance/FRED yield-curve work source-specific unless repeated implementation evidence justifies broader ingestion abstractions. Generalized frameworks/plugins, source registries, labor classification frameworks, trade infrastructure, demographic frameworks, input-output/matrix frameworks, financial-flow frameworks, energy frameworks, market-data/yield-curve frameworks, revision infrastructure, SDMX Interpretation Layers, conversion, aggregation, and model calls remain out of scope.
