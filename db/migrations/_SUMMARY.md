# Folder Summary: db/migrations

## Purpose
Raw SQL migrations for PostgreSQL schema foundation.

## Contains
<!-- PROJECTFORGE:BEGIN-CONTAINS -->
- `001_v0_schema_foundation.sql`
- `002_oecd_sdmx_staging.sql`
<!-- PROJECTFORGE:END-CONTAINS -->

## Active Work
- `001_v0_schema_foundation.sql` creates `meta`, `staging`, and `curated` schemas for the WDI/PostgreSQL v1 vertical slice.
- `002_oecd_sdmx_staging.sql` adds the DEC-006 source-specific `staging.oecd_sdmx_observation` table for the bounded OECD/SDMX PostgreSQL loader.

## Needs Attention
- No folder-specific issues recorded.
