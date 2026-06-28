# Folder Summary: data/raw

## Purpose
Immutable raw source artifacts and checksums from pipeline runs.

## Contains
<!-- PROJECTFORGE:BEGIN-CONTAINS -->
- `bea/`
- `bls/`
- `eurostat/`
- `oecd_sdmx/`
- `treasury/`
- `wdi/`
<!-- PROJECTFORGE:END-CONTAINS -->

## Active Work
- Contains TASK-005 WDI raw payload copies from the live support bundle.
- Contains TASK-012 fixture-backed OECD/SDMX raw XML evidence at `oecd_sdmx/oecd_sdmx_naag_2020_2021_raw.xml`.
- Contains TASK-019 bounded OECD/SDMX structure/codelist XML evidence at `oecd_sdmx/oecd_sdmx_naag_structure_20260604.xml`.
- Contains TASK-020 Eurostat raw JSON architecture-spike evidence at `eurostat/eurostat-namq-10-gdp-2023q1-2023q2-raw.json`.
- Contains TASK-051 bounded BLS monthly CPI architectural experiment evidence under `bls/`.
- Contains TASK-053 bounded BEA NIPA iTableCore evidence under `bea/`.
- Contains TASK-054 bounded U.S. Treasury Fiscal Data average-interest-rates evidence under `treasury/`.

## Needs Attention
- Raw files remain ignored by git by default, except the bounded OECD/Eurostat/BLS/BEA/Treasury fixture evidence explicitly unignored for clean-clone reconstruction.
