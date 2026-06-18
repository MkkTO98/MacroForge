# Folder Summary: src/macroforge

## Purpose
This folder is part of the ProjectForge file-backed operating system for `src/macroforge`.

## Contains
<!-- PROJECTFORGE:BEGIN-CONTAINS -->
- `__init__.py`
- `canonical_gdp_snapshot.py`
- `canonicalization_state.py`
- `combined_source_smoke.py`
- `db_helpers.py`
- `eurostat_namq_loader.py`
- `oecd_sdmx.py`
- `oecd_sdmx_loader.py`
- `wdi.py`
- `wdi_loader.py`
- `wdi_smoke.py`
- `wdi_validation.py`
<!-- PROJECTFORGE:END-CONTAINS -->

## Active Work
- `canonicalization_state.py` implements TASK-032's deterministic fixture-backed canonicalization state foundation, TASK-034's deterministic proposal workflow, and TASK-037's bounded WDI GDP unit metadata enrichment: provider evidence, canonicalization runs, mapping proposals, unit profiles, provisional accepted mappings, review routing, supersession helpers, workflow proposals, no-auto-apply mapping update proposals, WDI metadata evidence enrichment, and deterministic audit writers.
- `canonical_gdp_snapshot.py` implements TASK-028's first canonical-only GDP snapshot/audit report generator, using isolated temporary PostgreSQL, existing loaders/evidence, and core `curated.*` plus `meta.*` queries.

## Needs Attention
- Keep WDI/OECD/Eurostat work source-specific until a future decision justifies broader ingestion abstractions; canonicalization state/proposal/WDI-enrichment workflow remains deterministic/file-backed and is not PostgreSQL schema persistence, model canonicalization, unit conversion, aggregation, or a broad ontology/framework.
