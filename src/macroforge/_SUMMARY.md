# Folder Summary: src/macroforge

## Purpose
This folder contains MacroForge implementation modules for source evidence, source-specific loaders, canonical/report workflows, deterministic canonicalization helpers, and shared mechanical helpers.

## Contains
<!-- PROJECTFORGE:BEGIN-CONTAINS -->
- `__init__.py`
- `canonical_gdp_snapshot.py`
- `canonicalization_state.py`
- `combined_source_smoke.py`
- `db_helpers.py`
- `deterministic_change_verification.py`
- `eurostat_namq_loader.py`
- `observed_ingestion.py`
- `oecd_sdmx.py`
- `oecd_sdmx_loader.py`
- `wdi.py`
- `wdi_loader.py`
- `wdi_smoke.py`
- `wdi_validation.py`
<!-- PROJECTFORGE:END-CONTAINS -->

## Active Work
- `deterministic_change_verification.py` reconstructs loaded WDI/OECD/Eurostat observed packages from isolated PostgreSQL canonical/staging outputs and compares them with expected `ObservedIngestionPackage` contracts.
- `observed_ingestion.py` implements TASK-046's `ObservedIngestionPackage` v1 equivalence extraction: immutable package/observation dataclasses, deterministic WDI/OECD/Eurostat adapters, canonical attribute hashing, deterministic package fingerprints, package equivalence diagnostics, WDI `unknown`/`empty` conventions, and no framework/plugin/runtime behavior.
- `wdi_loader.py`, `oecd_sdmx_loader.py`, and `eurostat_namq_loader.py` consume the extracted representation where it preserves existing semantics while retaining source-specific SQL, staging, provider mappings, lineage, quality checks, and canonical fact behavior.
- `canonicalization_state.py` implements deterministic fixture-backed canonicalization state/proposal/review mechanics; it remains file-backed and does not perform model canonicalization, conversion, aggregation, or PostgreSQL persistence.
- `canonical_gdp_snapshot.py` implements the first canonical-only GDP snapshot/audit report generator, using isolated temporary PostgreSQL, existing loaders/evidence, and core `curated.*` plus `meta.*` queries.

## Needs Attention
- Treat `ObservedIngestionPackage` changes as contract evolution requiring equivalence verification across WDI/OECD/Eurostat, not ordinary refactoring.
- Keep WDI/OECD/Eurostat work source-specific unless a future decision justifies broader ingestion abstractions. Generalized frameworks/plugins, source registries, conversion, aggregation, and model calls remain out of scope.
