# Architecture State

## Current architecture

MacroForge is a ProjectForge-managed data/research project. The project OS is file-backed and summary-first. The domain platform begins with a WDI-to-PostgreSQL vertical slice.

## Target v1 flow

WDI source payload -> immutable raw artifact + checksum -> staging observation rows -> curated dimensions/facts -> lineage/quality checks -> query/report output.

## Database schemas

TASK-004 created the first raw SQL migration for:

- `meta`
- `staging`
- `curated`

`mart` remains documented for later analytical/reporting use.

## Current implementation status

Schema foundation, WDI raw evidence normalization, PostgreSQL load, validation reporting, isolated rerun hardening, minimal source contract, OECD/SDMX second-source spike, fixture-backed OECD/SDMX raw-evidence normalization, a live no-key OECD/SDMX rerunnable smoke command, the OECD/SDMX PostgreSQL promotion decision, the narrow TASK-015 OECD/SDMX PostgreSQL loader, the post-second-source architecture review, TASK-017 shared mechanical helper hardening, TASK-018 next-scope governance decision, TASK-019 bounded OECD/SDMX codelist/label enrichment, and TASK-020 Eurostat third-source architecture spike are implemented/recorded. The project now has two database-backed source-specific slices plus third-source architecture evidence and a tiny non-framework helper surface for SQL/JSONB literals, psql execution/scalar/count parsing, and JSON report writing.

## Current architecture decision

DEC-005 keeps the immediate architecture intentionally minimal: raw SQL migrations, PostgreSQL, psql/Python loaders, CLI runbooks, and tests. Alembic, SQLAlchemy, orchestration platforms, Docker, and broad source frameworks are deferred until real schema evolution or multiple manual source pipelines justify them.

DEC-006 accepted OECD/SDMX PostgreSQL promotion only as a narrow source-specific extension: add `staging.oecd_sdmx_observation`, keep the existing curated fact model, and avoid generalized SDMX/source framework work. TASK-015 implemented that decision without curated schema changes.

DEC-007 keeps the post-second-source architecture source-specific and raw-SQL/psql-based. It rejects generalized source/SDMX/framework work for now, keeps raw SQL migrations, and accepted only tiny shared mechanical helper plus validation/reporting hardening in TASK-017. TASK-017 completed that accepted hardening without schema, source-semantic, live-fetch, live-write, or framework changes.

DEC-008 chose bounded source-specific OECD/SDMX codelist and label enrichment before a third-source spike. TASK-019 completed that enrichment as filesystem metadata/report evidence and rejected generalized SDMX/source framework work, schema changes, live `macro` writes, third-source onboarding, and research/mart implementation.

DEC-009 accepted a bounded third no-key source spike using Eurostat `namq_10_gdp`. TASK-020 completed that spike and found the broad canonical observation model still valid but the concrete period and territory dimensions insufficient for quarterly/provider-code source data.

DEC-010 refines the TASK-020 schema response: MacroForge should prefer canonical-domain schema evolution over provider-centric identities. Periods should use structured canonical fields rather than provider period strings. ISO3 remains the canonical country identifier; aggregate regions should use `territory_type` and provider mappings rather than replacing ISO3 semantics. Provider codes belong in raw/staging/source payload/metadata/mapping layers.

## Next architecture work

The active design task is TASK-021: design concrete canonical-domain schema evolution for structured periods, territory typing/aggregate support, and provider mappings before any executable migration or third-source PostgreSQL promotion. Do not introduce a generalized source framework, orchestration, ORM, migration framework, mart layer, third-source PostgreSQL promotion, or live `macro` write without a new accepted decision artifact and, for implementation, a fresh dry-run.
