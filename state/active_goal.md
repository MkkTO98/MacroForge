# Active Goal

Project: MacroForge

## Current milestone

Milestone 3 — second-source PostgreSQL promotion, post-second-source architecture review, shared validation/reporting hardening, post-hardening next-scope governance, bounded OECD/SDMX codelist/label enrichment, and a bounded third-source architecture spike are complete.

## Purpose

MacroForge is an AI-first macroeconomic and investing research platform that begins as a reproducible PostgreSQL-backed macro data warehouse.

## Current objective

TASK-020 is complete and DEC-010 has reoriented the schema response toward canonical-domain identity. The active design task is TASK-021: design canonical period, territory, and provider mapping schema evolution before any executable migration or third-source PostgreSQL promotion.

## V1 success

MacroForge v1 succeeds when one World Bank WDI vertical slice proves raw evidence, checksum, staging transform, idempotent PostgreSQL load, metadata, lineage, quality checks, validation, and an inspectable report.

## Current defaults

- Recreate schema/WDI/OECD cleanly from decisions, tasks, and tests.
- Use isolated temporary PostgreSQL databases for smoke verification unless a fresh dry-run and explicit approval allow otherwise.
- Keep WDI and OECD/SDMX source-specific until accepted decision triggers justify broader abstractions.
- Treat OECD/SDMX labels/descriptions as filesystem metadata/report evidence first; do not load labels into PostgreSQL or change schemas without a new accepted decision.
- Treat Eurostat TASK-020 evidence as architecture-spike evidence only; do not promote Eurostat to PostgreSQL until period, territory, and provider metadata schema changes are accepted.
- Preserve canonical-domain identities: structured periods, ISO3 country identity, explicit territory types for aggregates, and provider period/territory codes as mappings/metadata rather than curated identities.
