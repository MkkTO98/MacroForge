# Folder Summary: db/migrations

## Purpose
Raw SQL migrations for PostgreSQL schema foundation.

## Contains
<!-- PROJECTFORGE:BEGIN-CONTAINS -->
- `001_v0_schema_foundation.sql`
- `002_oecd_sdmx_staging.sql`
- `003_canonical_domain_dimensions.sql`
- `004_eurostat_namq_staging.sql`
- `005_corporate_reporting_foundation.sql`
- `006_corporate_reporting_source_native_candidate.sql`
<!-- PROJECTFORGE:END-CONTAINS -->

## Active Work
- `001_v0_schema_foundation.sql` creates `meta`, `staging`, and `curated` schemas for the WDI/PostgreSQL v1 vertical slice.
- `002_oecd_sdmx_staging.sql` adds the DEC-006 source-specific `staging.oecd_sdmx_observation` table for the bounded OECD/SDMX PostgreSQL loader.
- `003_canonical_domain_dimensions.sql` implements DEC-011/TASK-022 structured periods, territory typing, provider mappings, and provider code dictionaries.
- `004_eurostat_namq_staging.sql` adds the DEC-012/TASK-024 source-specific `staging.eurostat_namq_observation` table for the bounded Eurostat NAMQ PostgreSQL loader.
- `005_corporate_reporting_foundation.sql` owns Corporate Reporting source evidence plus governed authority/release structures.
- `006_corporate_reporting_source_native_candidate.sql` adds append-only, non-governed private-analysis candidate persistence with immutable header/member/document rows and no mapping, rights, eligibility, release, or publication conferral.

## Needs Attention
- No folder-specific issues recorded.
