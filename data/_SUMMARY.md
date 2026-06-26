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
- TASK-012/TASK-019 generated bounded OECD/SDMX raw XML, codelist XML, normalized metadata, and labels under `data/raw/oecd_sdmx` and `data/metadata/oecd_sdmx`.
- TASK-020 generated bounded Eurostat raw JSON and normalized metadata under `data/raw/eurostat` and `data/metadata/eurostat`.
- TASK-045 made only the bounded OECD/Eurostat fixture evidence and folder summaries unignored/commit-eligible for clean-clone reconstruction.

## Needs Attention
- Raw data and metadata remain ignored by default except explicitly unignored bounded fixture evidence; decide deliberately before versioning or promoting any additional fixture evidence.
