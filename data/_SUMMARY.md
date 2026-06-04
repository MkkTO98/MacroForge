# Folder Summary: data

## Purpose
Local data artifact directories. Keep large raw data and DB dumps out of git unless a later policy explicitly allows fixtures.

## Contains
<!-- PROJECTFORGE:BEGIN-CONTAINS -->
- `curated/`
- `metadata/`
- `raw/`
- `staging/`
<!-- PROJECTFORGE:END-CONTAINS -->

## Active Work
- TASK-005 generated WDI smoke raw payload copies and metadata under `data/raw/wdi` and `data/metadata/wdi`.
- TASK-012 generated fixture-backed OECD/SDMX raw XML and normalized metadata under `data/raw/oecd_sdmx` and `data/metadata/oecd_sdmx`.

## Needs Attention
- Raw data and metadata are ignored by default; decide deliberately before versioning or promoting fixture evidence.
