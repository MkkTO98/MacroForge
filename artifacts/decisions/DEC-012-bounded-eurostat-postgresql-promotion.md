# DEC-012 — Bounded Eurostat PostgreSQL promotion design

Status: accepted
Date: 2026-06-04
Related task: TASK-023
Depends on: DEC-009, DEC-010, DEC-011, TASK-022
Design note: `docs/architecture/bounded-eurostat-postgresql-promotion-design.md`
Follow-on task: TASK-024

## Decision

Accept a bounded, source-specific PostgreSQL promotion path for the recorded Eurostat `namq_10_gdp` fixture.

The next implementation may add only:

1. a source-specific migration for `staging.eurostat_namq_observation`;
2. a source-specific loader module for the recorded normalized Eurostat fixture;
3. canonical quarterly periods for `2023-Q1` and `2023-Q2`;
4. canonical ISO3 country territories `DEU` and `FRA`;
5. provider mappings from Eurostat period/geography codes to canonical period/territory rows;
6. bounded provider code dictionaries for the fixture's Eurostat dimensions;
7. four curated source-agnostic fact rows;
8. isolated PostgreSQL idempotency tests and a small load report.

The existing `curated.fact_observation` table remains unchanged.

## Rationale

TASK-020 proved Eurostat is useful architecture pressure but exposed period and territory schema gaps. DEC-010 and DEC-011 resolved those gaps from a canonical-domain perspective. TASK-022 implemented the required canonical-domain schema foundation.

With migration 003 available, the recorded Eurostat fixture no longer requires a curated schema redesign. It needs only a narrow staging table and a source-specific loader.

This keeps MacroForge's architecture consistent with DEC-005, DEC-006, and DEC-007:

- raw SQL migrations;
- PostgreSQL;
- source-specific loaders;
- no generalized ingestion framework until repeated implemented-source pressure justifies one;
- no live/default database writes without approval.

## Accepted implementation boundaries

TASK-024 may:

- create `db/migrations/004_eurostat_namq_staging.sql`;
- create `src/macroforge/eurostat_namq_loader.py`;
- add fixture-backed and isolated PostgreSQL tests;
- load only `data/metadata/eurostat/eurostat-namq-10-gdp-architecture-spike-normalized.json`;
- write an isolated smoke report artifact;
- use existing tiny mechanical DB helpers where appropriate.

TASK-024 must apply migrations in order:

1. `001_v0_schema_foundation.sql`
2. `002_oecd_sdmx_staging.sql`
3. `003_canonical_domain_dimensions.sql`
4. `004_eurostat_namq_staging.sql`

## Explicit non-goals

This decision does not approve:

- live `macro` writes;
- live Eurostat HTTP fetching in database tests;
- generalized JSON-stat framework;
- generalized source/plugin framework;
- broad Eurostat production ingestion;
- any Eurostat dataset beyond the recorded bounded `namq_10_gdp` fixture;
- FRED onboarding;
- provider-specific columns on `curated.fact_observation`;
- aggregate territory membership history;
- unit conversion framework;
- canonical indicator ontology;
- mart/research layer;
- orchestration/scheduling.

## Mapping requirements

TASK-024 must prove:

- Eurostat `2023-Q1` maps to canonical `Q / 2023-01-01..2023-03-31`;
- Eurostat `2023-Q2` maps to canonical `Q / 2023-04-01..2023-06-30`;
- Eurostat `DE` maps to canonical country `DEU`;
- Eurostat `FR` maps to canonical country `FRA`;
- provider code dictionaries capture bounded fixture dimensions: `freq`, `unit`, `s_adj`, `na_item`, `geo`, and `time`;
- seasonal adjustment/status metadata remains in attribute sets or source payloads, not fact columns.

## Reconsideration triggers

Reopen this decision if:

- a live Eurostat endpoint changes shape materially from the recorded fixture;
- another Eurostat dataset requires incompatible staging structure;
- provider geography aggregates such as `EU27_2020` or `EA20` become part of the promotion fixture;
- multiple implemented JSON-stat sources expose duplicated parser mechanics worth extracting;
- quarterly period or provider mapping constraints fail under isolated PostgreSQL tests.

## Consequences

The next task is implementation, but still bounded. It should resemble the OECD/SDMX source-specific PostgreSQL promotion pattern rather than a framework build.

TASK-023 is complete once this decision, the design note, and TASK-024 are recorded and project state is updated.
