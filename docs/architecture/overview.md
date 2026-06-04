# MacroForge Architecture Overview

## Layers

1. Project operating system: ProjectForge-generated artifacts, policies, summaries, decisions, tasks, and logs.
2. Data evidence layer: immutable raw source payloads, checksums, source metadata, and run reports.
3. Database layer: PostgreSQL schemas for `meta`, `staging`, `curated`, and later `mart`.
4. Pipeline layer: source-specific extract/transform/load code beginning with WDI.
5. Validation layer: row counts, uniqueness, duplicate detection, null checks, sanity checks, and lineage checks.
6. Research layer: deferred until the data substrate is trustworthy.

## First vertical slice

World Bank WDI -> raw artifact/checksum -> staging observations -> curated dimensions/facts -> validation/report output.

## Boundary decisions

- Local execution, cloud governance.
- No autonomous deployment in v1.
- No paid/credentialed APIs in v1.
- Schema/WDI code is recreated cleanly from decisions and tests.
- DEC-005 keeps raw SQL/PostgreSQL/psql as the immediate framework and defers Alembic, SQLAlchemy, orchestration, Docker, and broad source abstractions.
- The next source/framework scope is WDI hardening, a minimal source contract, and a bounded no-key OECD/SDMX-style second-source spike.
