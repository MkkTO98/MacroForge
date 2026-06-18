# Bounded Eurostat PostgreSQL promotion design

Status: accepted design for TASK-023
Date: 2026-06-04
Governing decisions: DEC-009, DEC-010, DEC-011
Follow-on decision: DEC-012
Follow-on implementation task: TASK-024

## Purpose

This note designs the smallest source-specific PostgreSQL promotion path for the recorded Eurostat `namq_10_gdp` architecture-spike fixture.

The design uses the TASK-022 canonical-domain schema:

- structured quarterly periods in `curated.dim_period`;
- ISO3-preserved country territories in `curated.dim_territory`;
- Eurostat provider period and territory mappings in `meta`;
- Eurostat provider code dictionaries in `meta`;
- seasonal adjustment and JSON-stat status/source details in `curated.dim_attribute_set`;
- unchanged `curated.fact_observation` grain.

This is design-only. It does not implement the migration or loader.

## Accepted scope

Promote only the existing bounded evidence slice:

```text
Provider: Eurostat
Dataset: namq_10_gdp
Endpoint format: JSON-stat
Frequency: Q
Unit: CP_MEUR
National accounts item: B1GQ
Seasonal adjustment: NSA
Geographies: DE, FR
Periods: 2023-Q1, 2023-Q2
Rows: 4
Raw artifact: data/raw/eurostat/eurostat-namq-10-gdp-2023q1-2023q2-raw.json
Normalized artifact: data/metadata/eurostat/eurostat-namq-10-gdp-architecture-spike-normalized.json
```

The immediate implementation should load from the recorded normalized artifact, not from a live HTTP request.

## Non-goals

TASK-023 and TASK-024 do not approve:

- live `macro` database writes;
- live Eurostat fetching inside database tests;
- broad Eurostat production ingestion;
- generalized JSON-stat framework;
- generalized source framework;
- source/plugin registry;
- provider-specific columns on `curated.fact_observation`;
- Eurostat aggregate region membership history;
- FRED onboarding;
- research/mart layer;
- unit conversion framework;
- canonical indicator ontology.

## Design verdict

The recorded Eurostat fixture can be promoted with a narrow source-specific migration and loader.

The only new source-specific schema needed is a staging table:

```text
staging.eurostat_namq_observation
```

No curated schema change is required beyond TASK-022 migration 003.

## Required migrations for implementation

TASK-024 should apply migrations in this order in isolated PostgreSQL tests:

1. `db/migrations/001_v0_schema_foundation.sql`
2. `db/migrations/002_oecd_sdmx_staging.sql`
3. `db/migrations/003_canonical_domain_dimensions.sql`
4. new `db/migrations/004_eurostat_namq_staging.sql`

Migration 004 should add only the source-specific Eurostat staging table and indexes/constraints needed for the bounded fixture.

## Proposed source-specific staging table

```sql
CREATE TABLE staging.eurostat_namq_observation (
    staging_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    dataset_release_id uuid NOT NULL REFERENCES meta.dataset_release(dataset_release_id),
    pipeline_run_id uuid NOT NULL REFERENCES meta.pipeline_run(pipeline_run_id),

    provider_dataset_code text NOT NULL,
    frequency text NOT NULL,
    unit_code text NOT NULL,
    unit_name text,
    seasonal_adjustment_code text NOT NULL,
    seasonal_adjustment_name text,
    national_accounts_item_code text NOT NULL,
    national_accounts_item_name text,
    provider_geo_code text NOT NULL,
    provider_geo_name text,
    provider_period_code text NOT NULL,
    period_year integer NOT NULL,
    period_quarter integer NOT NULL,

    observation_value numeric NOT NULL,
    observation_status text,
    decimal_precision integer,
    as_of_date date,

    jsonstat_flat_index integer,
    source_payload jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now(),

    CONSTRAINT ck_staging_eurostat_namq_frequency
        CHECK (frequency = 'Q'),

    CONSTRAINT ck_staging_eurostat_namq_quarter
        CHECK (period_quarter BETWEEN 1 AND 4),

    CONSTRAINT uq_staging_eurostat_namq_observation
        UNIQUE (
            pipeline_run_id,
            provider_dataset_code,
            frequency,
            unit_code,
            seasonal_adjustment_code,
            national_accounts_item_code,
            provider_geo_code,
            provider_period_code
        )
);
```

Notes:

- The table is intentionally named for the dataset family, not for all Eurostat or JSON-stat.
- The staging table preserves provider-shaped values because staging is a source-specific layer.
- `source_payload` preserves the flattened JSON-stat dimensions and status details.
- The uniqueness constraint prevents duplicate staging rows inside one pipeline run.
- The table should not try to solve all Eurostat dimensions or future Eurostat datasets.

## Curated mapping rules

### Source and dataset release

Create or reuse `meta.source`:

| source_code | source_name | source_home_url |
| --- | --- | --- |
| EUROSTAT_NAMQ_GDP | Eurostat quarterly national accounts GDP | https://ec.europa.eu/eurostat/ |

Create a `meta.dataset_release` using the recorded endpoint/checksum metadata:

| field | value |
| --- | --- |
| provider_dataset_code | `namq_10_gdp` |
| source_url | recorded TASK-020 endpoint |
| raw_artifact_path | `data/raw/eurostat/eurostat-namq-10-gdp-2023q1-2023q2-raw.json` |
| raw_sha256 | `914888671969cf31253dc0e951aaa8bee66bbf8ec03d1ff193bc6b1feda1865a` |
| filters | `freq=Q`, `unit=CP_MEUR`, `na_item=B1GQ`, `s_adj=NSA`, `geo=DE,FR`, `time=2023-Q1,2023-Q2` |

### Periods

Insert/reuse canonical period rows:

| provider_period_code | frequency | period_year | period_quarter | period_start_date | period_end_date | period_label |
| --- | --- | ---: | ---: | --- | --- | --- |
| 2023-Q1 | Q | 2023 | 1 | 2023-01-01 | 2023-03-31 | 2023 Q1 |
| 2023-Q2 | Q | 2023 | 2 | 2023-04-01 | 2023-06-30 | 2023 Q2 |

Insert provider mappings:

| source_code | provider_dataset_code | provider_period_code | canonical period |
| --- | --- | --- | --- |
| EUROSTAT_NAMQ_GDP | namq_10_gdp | 2023-Q1 | Q / 2023-01-01..2023-03-31 |
| EUROSTAT_NAMQ_GDP | namq_10_gdp | 2023-Q2 | Q / 2023-04-01..2023-06-30 |

### Territories

Insert/reuse canonical country rows:

| provider_geo_code | provider_geo_name | canonical iso3_code | canonical_territory_code | territory_type |
| --- | --- | --- | --- | --- |
| DE | Germany | DEU | DEU | country |
| FR | France | FRA | FRA | country |

Insert provider mappings:

| source_code | provider_dataset_code | code_system | provider_territory_code | canonical territory |
| --- | --- | --- | --- | --- |
| EUROSTAT_NAMQ_GDP | namq_10_gdp | Eurostat geo | DE | DEU |
| EUROSTAT_NAMQ_GDP | namq_10_gdp | Eurostat geo | FR | FRA |

Do not store `DE` or `FR` as canonical ISO3 codes. They are provider geography codes mapped to canonical country territories.

### Provider code dictionaries

For the bounded fixture, load only the code lists present in the normalized artifact:

| dimension_name | code_system | codes |
| --- | --- | --- |
| freq | Eurostat freq | `Q` = Quarterly |
| unit | Eurostat unit | `CP_MEUR` = Current prices, million euro |
| s_adj | Eurostat s_adj | `NSA` = Unadjusted data |
| na_item | Eurostat na_item | `B1GQ` = Gross domestic product at market prices |
| geo | Eurostat geo | `DE`, `FR` |
| time | Eurostat time | `2023-Q1`, `2023-Q2` |

These are metadata/audit rows, not canonical identity definitions.

### Indicators

For the bounded implementation, create/reuse one source-specific indicator row:

| indicator_code | indicator_name | source/provider meaning |
| --- | --- | --- |
| B1GQ | Gross domestic product at market prices | Eurostat national accounts item |

This design does not create a cross-provider canonical GDP ontology. That remains deferred.

### Units

Create/reuse one unit row:

| unit_code | unit_name |
| --- | --- |
| CP_MEUR | Current prices, million euro |

This design does not perform unit conversion.

### Attribute set

Store provider qualifiers in `curated.dim_attribute_set`, for example:

```json
{
  "source": "Eurostat",
  "provider_dataset_code": "namq_10_gdp",
  "freq": "Q",
  "s_adj": "NSA",
  "s_adj_label": "Unadjusted data (i.e. neither seasonally adjusted nor calendar adjusted data)",
  "jsonstat_status": "p",
  "observation_status": "observed"
}
```

For rows where JSON-stat status is null, omit `jsonstat_status` or store it as null consistently. The implementation should be tested for the observed DE `p` and FR null cases.

### Facts

Insert four facts into `curated.fact_observation`:

| territory | period | value | unit | attribute |
| --- | --- | ---: | --- | --- |
| DEU | 2023 Q1 | 1043520.0 | CP_MEUR | NSA/status p |
| DEU | 2023 Q2 | 1031880.0 | CP_MEUR | NSA/status p |
| FRA | 2023 Q1 | 684762.7 | CP_MEUR | NSA/status null |
| FRA | 2023 Q2 | 706147.7 | CP_MEUR | NSA/status null |

The fact uniqueness/grain remains the existing curated grain. Provider-specific details remain in source lineage, staging, provider mappings, provider code dictionaries, and attribute sets.

## Loader shape for TASK-024

Add a source-specific module:

```text
src/macroforge/eurostat_namq_loader.py
```

Expected behavior:

1. Read `data/metadata/eurostat/eurostat-namq-10-gdp-architecture-spike-normalized.json`.
2. Generate or execute SQL against a supplied PostgreSQL URL.
3. Upsert/reuse source, dataset release, pipeline run, dimensions, mappings, provider dictionaries, staging rows, facts, lineage, and quality checks.
4. Refuse live/default `macro` targets unless an explicit unsafe flag already used by project conventions exists.
5. Write a small report, for example:

```text
artifacts/reports/eurostat-namq-load-smoke-20260604.json
```

No live Eurostat HTTP fetch should occur in the loader or tests.

## Test plan for TASK-024

Follow TDD:

1. RED: migration file/table-shape test expects `004_eurostat_namq_staging.sql` and `staging.eurostat_namq_observation`.
2. RED: loader module/API test expects SQL generation from the normalized artifact and verifies no network call surface.
3. GREEN: implement migration 004.
4. GREEN: implement the source-specific loader.
5. Isolated PostgreSQL idempotency test:
   - create temporary database;
   - apply migrations 001, 002, 003, 004;
   - run the Eurostat loader twice with the same run key;
   - verify staging row count = 4;
   - verify fact row count = 4;
   - verify canonical periods = `2023 Q1`, `2023 Q2` with quarterly intervals;
   - verify canonical territories = `DEU`, `FRA`;
   - verify provider territory mappings `DE -> DEU`, `FR -> FRA`;
   - verify provider period mappings `2023-Q1`, `2023-Q2`;
   - verify provider code-list/code rows for the bounded dimensions;
   - verify no duplicate facts at the curated grain;
   - verify lineage and quality checks are written.
6. Full suite plus coherence after governance/state/handoff updates.

## Migration and loader risks

| Risk | Mitigation |
| --- | --- |
| Provider `DE`/`FR` accidentally stored as canonical ISO3 | Tests must assert canonical territories are `DEU` and `FRA`, with provider mappings from `DE`/`FR`. |
| Quarterly periods collapse into annual 2023 | Tests must assert two distinct `Q` period rows for Q1 and Q2. |
| JSON-stat dimension metadata becomes fact columns | Keep provider dimensions in staging, code dictionaries, mappings, and attribute sets. |
| Loader becomes generalized JSON-stat framework | Name module and staging table for `eurostat_namq`; only parse the recorded normalized artifact. |
| Live/network behavior enters database tests | Tests must use local normalized artifact and inspect module surface for no fetch/curl/requests. |
| Aggregate territories are prematurely modeled | Do not add EU27/EA20 rows in TASK-024 unless the fixture includes them; they remain supported by schema but not seeded here. |
| Unit conversion/indicator ontology pressure | Store `CP_MEUR` and `B1GQ` source-specifically; defer canonical ontology/conversion. |

## Required now vs deferred

Required for TASK-024:

- migration 004 with source-specific Eurostat staging table;
- source-specific loader from recorded normalized fixture;
- quarterly period inserts/mappings;
- `DE`/`FR` to `DEU`/`FRA` territory mappings;
- bounded provider code dictionaries for fixture dimensions;
- four curated facts with unchanged fact shape;
- isolated PostgreSQL idempotency test;
- report artifact.

Deferred:

- live Eurostat fetch/hardening;
- any other Eurostat dataset;
- aggregate region rows unless a fixture requires them;
- generalized JSON-stat parsing framework;
- provider-neutral indicator ontology;
- unit conversion;
- mart/research outputs;
- scheduling/orchestration.

## Decision summary

Proceed to TASK-024 only as a bounded implementation of this design. The implementation should look more like the OECD/SDMX source-specific promotion than like a new framework.
