# Folder Summary: src/macroforge

## Purpose
This folder is part of the ProjectForge file-backed operating system for `src/macroforge`.

## Contains
<!-- PROJECTFORGE:BEGIN-CONTAINS -->
- `__init__.py`
- `db_helpers.py`
- `oecd_sdmx.py`
- `oecd_sdmx_loader.py`
- `wdi.py`
- `wdi_loader.py`
- `wdi_smoke.py`
- `wdi_validation.py`
<!-- PROJECTFORGE:END-CONTAINS -->

## Active Work
- `db_helpers.py` contains TASK-017 tiny mechanical helpers for SQL/JSONB literals, psql execution/scalar/count parsing, and JSON report writing.
- WDI and OECD/SDMX modules remain source-specific; loaders use shared helpers only for mechanical operations.

## Needs Attention
- Keep OECD/SDMX source-specific until a future decision justifies broader ingestion abstractions.
