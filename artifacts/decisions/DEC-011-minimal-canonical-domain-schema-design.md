# DEC-011 — Minimal canonical-domain schema design

Status: accepted
Date: 2026-06-04
Related task: TASK-021
Governing decision: DEC-010
Design note: `docs/architecture/minimal-canonical-domain-schema-design.md`

## Decision

Accept the bounded minimal canonical-domain schema design for the next implementation step.

The next schema evolution should add only:

1. structured canonical periods for annual, quarterly, monthly, and daily-ready frequencies;
2. territory typing that preserves ISO3 country identity and optionally supports explicitly seeded non-country aggregates/economic areas;
3. provider period mappings;
4. provider territory mappings;
5. minimal provider code-list/code dictionary tables where needed for mapping, labels, and audit.

The fact table should not be widened with provider-specific columns.

## Accepted table direction

`curated.dim_period` should be evolved from annual-only `(frequency, period_year)` identity toward canonical interval identity:

- `frequency`
- `period_year`
- `period_quarter`
- `period_month`
- `period_date`
- `period_start_date`
- `period_end_date`
- `period_label`

`curated.dim_territory` should preserve countries as ISO3-identified canonical entities and add limited non-country support:

- `territory_type` in `country`, `economic_area`, `aggregate`
- `iso3_code` required for countries and null for non-countries
- `canonical_territory_code`
- `territory_name`
- optional validity/metadata fields

Provider mappings should live in `meta`:

- `meta.provider_period_mapping`
- `meta.provider_territory_mapping`
- `meta.provider_code_list`
- `meta.provider_code`

## Rationale

This is the smallest design that addresses the Eurostat spike and DEC-010 without turning provider representations into canonical identities.

It supports:

- World Bank annual observations;
- OECD annual observations;
- Eurostat quarterly observations;
- future FRED quarterly/monthly/daily observations at the schema level;
- explicit provider mappings for audit and reconciliation.

It avoids:

- generalized ingestion frameworks;
- provider-shaped facts;
- broad geography modeling;
- premature aggregate membership history;
- full indicator ontology;
- unit conversion framework;
- Eurostat or FRED production onboarding.

## Required now

- Design and later implement structured period rows.
- Design and later implement canonical country rows with ISO3 preserved.
- Design and later implement optional aggregate/economic-area rows only for explicitly needed codes.
- Design and later implement provider period/territory mappings.
- Design and later implement minimal provider code dictionaries where needed by source evidence.
- Keep source-specific staging tables as source-specific.
- Keep fact observation grain source-agnostic.

## Deferred

- Aggregate membership tables and versioned region membership.
- Fiscal calendars.
- Weekly/semiannual frequencies.
- Canonical indicator ontology.
- Unit conversion and transformation framework.
- FRED loader.
- Eurostat PostgreSQL promotion.
- Generic ingestion/source framework.
- Research/mart layer.

## Consequences

The next implementation task should create a new migration rather than editing `001_v0_schema_foundation.sql`.

Existing WDI/OECD loaders and tests will need compatibility updates so annual rows use the expanded period and territory dimensions.

Eurostat remains architecture-spike evidence only until a separate accepted task promotes it.

## Non-goals

This decision does not approve:

- executable migration in TASK-021;
- live `macro` database writes;
- Eurostat PostgreSQL promotion;
- FRED onboarding;
- generalized ingestion framework;
- provider-specific fact columns;
- research/mart implementation.
