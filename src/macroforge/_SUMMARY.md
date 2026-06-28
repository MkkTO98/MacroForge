# Folder Summary: src/macroforge

## Purpose
This folder contains MacroForge implementation modules for source evidence, source-specific loaders, canonical/report workflows, deterministic canonicalization helpers, and shared mechanical helpers.

## Contains
<!-- PROJECTFORGE:BEGIN-CONTAINS -->
- `__init__.py`
- `bea_nipa.py`
- `bls_cpi.py`
- `canonical_gdp_snapshot.py`
- `canonicalization_state.py`
- `combined_source_smoke.py`
- `contract_drift.py`
- `db_helpers.py`
- `deterministic_change_verification.py`
- `eurostat_namq_loader.py`
- `ingestion_feedback.py`
- `lineage_generation.py`
- `observed_ingestion.py`
- `treasury_fiscal_data.py`
- `oecd_sdmx.py`
- `oecd_sdmx_loader.py`
- `wdi.py`
- `wdi_loader.py`
- `wdi_smoke.py`
- `wdi_validation.py`
<!-- PROJECTFORGE:END-CONTAINS -->

## Active Work
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
- Keep WDI/OECD/Eurostat work source-specific unless a future decision justifies broader ingestion abstractions. Generalized frameworks/plugins, source registries, conversion, aggregation, and model calls remain out of scope.
