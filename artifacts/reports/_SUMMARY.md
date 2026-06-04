# Folder Summary: artifacts/reports

## Purpose
This folder is part of the ProjectForge file-backed operating system for `artifacts/reports`.

## Contains
<!-- PROJECTFORGE:BEGIN-CONTAINS -->
- `.gitkeep`
- `eurostat-third-source-architecture-spike-20260604.md`
- `oecd-sdmx-codelist-labels-20260604.md`
- `oecd-sdmx-live-smoke-20260603.md`
- `oecd-sdmx-load-smoke-20260603.json`
- `oecd-sdmx-second-source-spike-20260603.md`
- `oecd-sdmx-smoke-20260603.md`
- `wdi-isolated-smoke-rerun-20260603.json`
- `wdi-load-smoke-20260602.json`
- `wdi-smoke-20260602.md`
- `wdi-validation-smoke-20260602.json`
- `wdi-validation-smoke-20260602.md`
<!-- PROJECTFORGE:END-CONTAINS -->

## Active Work
- TASK-012 produced `oecd-sdmx-smoke-20260603.md`, mapping SDMX XML fields to the minimal source contract.
- TASK-015 produced `oecd-sdmx-load-smoke-20260603.json`, recording isolated PostgreSQL loader counts for the bounded OECD/SDMX slice.
- TASK-019 produced `oecd-sdmx-codelist-labels-20260604.md`, recording bounded label/description evidence for smoke-slice OECD/SDMX codes.
- TASK-020 produced `eurostat-third-source-architecture-spike-20260604.md`, recording Eurostat architecture-fit findings. DEC-010 refines its schema recommendations toward canonical-domain identities.

## Needs Attention
- Do not treat the OECD/SDMX load report as a live `macro` database write; it came from an isolated temporary PostgreSQL smoke database. Do not treat TASK-019/TASK-020 reports as schema/database implementation; they are filesystem evidence only until a new decision accepts changes.
