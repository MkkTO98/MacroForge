# Folder Summary: tests

## Purpose
This folder is part of the ProjectForge file-backed operating system for `tests`.

## Contains
<!-- PROJECTFORGE:BEGIN-CONTAINS -->
- `fixtures/`
- `invariants/`
- `test_db_helpers.py`
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
- `test_db_helpers.py` covers TASK-017 shared mechanical helper behavior.
- WDI and OECD/SDMX loader/validation tests preserve source-specific SQL, report, and isolated PostgreSQL behavior after helper extraction.

## Needs Attention
- Preserve fixture-backed and isolated-PostgreSQL TDD coverage if OECD/SDMX is later broadened.
