# Minimal canonical-domain schema design

Status: accepted design for TASK-021
Date: 2026-06-04
Governing decision: DEC-010
Follow-on decision: DEC-011
Follow-on implementation task: TASK-022

## Purpose

This note defines the minimal canonical-domain schema evolution needed before a third source such as Eurostat can be promoted into PostgreSQL.

The goal is deliberately bounded:

- structured period support for annual, quarterly, monthly, and daily-ready observations;
- territory typing that preserves ISO3 country identity while allowing a small number of optional non-country aggregates;
- explicit provider mappings for period codes, territory codes, and provider code dictionaries;
- no executable migration yet;
- no Eurostat PostgreSQL promotion yet;
- no generalized ingestion framework;
- no provider-specific columns added to curated facts.

MacroForge should keep source-specific ingestion boring while making curated observations domain-stable for investment research.

## Design principles

1. Curated dimensions model canonical analytical entities.
2. Provider strings and provider codes are metadata or mappings, not curated identity.
3. Tables should be explicit and boring.
4. Do not solve all geography, calendar, fiscal-year, or membership-version problems now.
5. Keep `curated.fact_observation` centered on existing canonical dimension IDs plus source/release/run lineage.
6. Implement as a new migration later, not by editing `001_v0_schema_foundation.sql`.

## Required now vs deferred

Required now:

- Extend `curated.dim_period` for annual, quarterly, monthly, and daily-ready canonical periods.
- Extend `curated.dim_territory` with `territory_type`, country ISO3 preservation, and optional aggregate codes.
- Add `meta.provider_period_mapping`.
- Add `meta.provider_territory_mapping`.
- Add minimal `meta.provider_code_list` and `meta.provider_code` tables for provider dictionaries where mapping/reporting needs them.
- Keep `curated.fact_observation` unchanged except for continuing to reference canonical `period_id` and `territory_id`.

Deferred:

- Aggregate membership tables, such as EU27 membership by date.
- Fiscal-calendar support.
- Weekly/semiannual periods.
- Multiple canonical calendars.
- Canonical indicator ontology across providers.
- Canonical unit conversion framework.
- Full provider registry/plugin framework.
- Eurostat production ingestion.
- Research/mart models.

## Proposed table definitions

These are design definitions, not an executable migration. TASK-022 should translate them into a tested migration.

### 1. `curated.dim_period`

Replace the annual-only natural key with structured canonical period identity.

```sql
CREATE TABLE curated.dim_period (
    period_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    frequency text NOT NULL,
    period_year integer NOT NULL,
    period_quarter integer,
    period_month integer,
    period_date date,
    period_start_date date NOT NULL,
    period_end_date date NOT NULL,
    period_label text NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),

    CONSTRAINT ck_curated_dim_period_frequency
        CHECK (frequency IN ('A', 'Q', 'M', 'D')),

    CONSTRAINT ck_curated_dim_period_order
        CHECK (period_start_date <= period_end_date),

    CONSTRAINT ck_curated_dim_period_annual
        CHECK (
            frequency <> 'A'
            OR (
                period_quarter IS NULL
                AND period_month IS NULL
                AND period_date IS NULL
            )
        ),

    CONSTRAINT ck_curated_dim_period_quarterly
        CHECK (
            frequency <> 'Q'
            OR (
                period_quarter BETWEEN 1 AND 4
                AND period_month IS NULL
                AND period_date IS NULL
            )
        ),

    CONSTRAINT ck_curated_dim_period_monthly
        CHECK (
            frequency <> 'M'
            OR (
                period_quarter IS NULL
                AND period_month BETWEEN 1 AND 12
                AND period_date IS NULL
            )
        ),

    CONSTRAINT ck_curated_dim_period_daily
        CHECK (
            frequency <> 'D'
            OR (
                period_quarter IS NULL
                AND period_month IS NULL
                AND period_date IS NOT NULL
                AND period_start_date = period_date
                AND period_end_date = period_date
            )
        ),

    CONSTRAINT uq_curated_dim_period_interval
        UNIQUE (frequency, period_start_date, period_end_date)
);
```

Notes:

- Canonical identity is the interval plus frequency, not a provider period string.
- `period_label` is display-only, e.g. `2023`, `2023 Q1`, `2023-01`, `2023-01-03`.
- Daily support is ready through `period_date`, but no daily source loader is required now.
- This design does not add fiscal-year variants. If a future source uses fiscal periods, add a decision rather than overloading this table.

### Example period rows

| frequency | period_year | period_quarter | period_month | period_date | period_start_date | period_end_date | period_label | Example source |
| --- | ---: | ---: | ---: | --- | --- | --- | --- | --- |
| A | 2021 | null | null | null | 2021-01-01 | 2021-12-31 | 2021 | World Bank WDI annual |
| Q | 2023 | 1 | null | null | 2023-01-01 | 2023-03-31 | 2023 Q1 | FRED quarterly / Eurostat quarterly |
| M | 2023 | null | 1 | null | 2023-01-01 | 2023-01-31 | 2023-01 | FRED monthly |
| D | 2023 | null | null | 2023-01-03 | 2023-01-03 | 2023-01-03 | 2023-01-03 | FRED daily-ready |

### 2. `curated.dim_territory`

Preserve ISO3 country identity while allowing a bounded set of non-country aggregate territories.

```sql
CREATE TABLE curated.dim_territory (
    territory_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    territory_type text NOT NULL,
    iso3_code text,
    canonical_territory_code text NOT NULL,
    territory_name text NOT NULL,
    region text,
    income_group text,
    valid_from date,
    valid_to date,
    metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now(),

    CONSTRAINT ck_curated_dim_territory_type
        CHECK (territory_type IN ('country', 'economic_area', 'aggregate')),

    CONSTRAINT ck_curated_dim_territory_country_iso3
        CHECK (
            (territory_type = 'country' AND iso3_code IS NOT NULL)
            OR (territory_type <> 'country' AND iso3_code IS NULL)
        ),

    CONSTRAINT uq_curated_dim_territory_iso3_country
        UNIQUE (iso3_code),

    CONSTRAINT uq_curated_dim_territory_canonical_code
        UNIQUE (canonical_territory_code)
);
```

Notes:

- Countries remain canonicalized by ISO3. Examples: `USA`, `DNK`, `DEU`, `FRA`.
- `canonical_territory_code` is MacroForge-owned. For country rows it can equal ISO3.
- Non-country aggregates are optional and explicit. Examples: `EU27_2020`, `EA20`.
- `source_id` should no longer be part of canonical territory identity. Provider-specific codes move to mappings.
- Only `country`, `economic_area`, and `aggregate` are required now. Do not add every possible geography type yet.
- `valid_from` / `valid_to` are minimal placeholders for aggregate definitions. Full membership tables are deferred.

### Example territory rows

| territory_type | iso3_code | canonical_territory_code | territory_name | Example source |
| --- | --- | --- | --- | --- |
| country | USA | USA | United States | WDI `USA`, FRED United States series |
| country | DNK | DNK | Denmark | WDI `DNK` |
| country | DEU | DEU | Germany | Eurostat `DE` |
| country | FRA | FRA | France | Eurostat `FR` |
| economic_area | null | EU27_2020 | European Union - 27 countries from 2020 | Eurostat `EU27_2020` |
| economic_area | null | EA20 | Euro area - 20 countries | Eurostat `EA20` |

### 3. `meta.provider_period_mapping`

Map provider period codes to canonical periods.

```sql
CREATE TABLE meta.provider_period_mapping (
    provider_period_mapping_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id uuid NOT NULL REFERENCES meta.source(source_id),
    provider_dataset_code text NOT NULL,
    provider_period_code text NOT NULL,
    period_id uuid NOT NULL REFERENCES curated.dim_period(period_id),
    provider_label text,
    metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now(),

    CONSTRAINT uq_meta_provider_period_mapping
        UNIQUE (source_id, provider_dataset_code, provider_period_code)
);
```

Examples:

| source | provider_dataset_code | provider_period_code | canonical period |
| --- | --- | --- | --- |
| WDI | WDI | 2021 | A / 2021-01-01..2021-12-31 |
| FRED | GDP | 2023-Q1 | Q / 2023-01-01..2023-03-31 |
| FRED | UNRATE | 2023-01 | M / 2023-01-01..2023-01-31 |
| FRED | DGS10 | 2023-01-03 | D / 2023-01-03..2023-01-03 |
| EUROSTAT_NAMQ_GDP | namq_10_gdp | 2023-Q1 | Q / 2023-01-01..2023-03-31 |

### 4. `meta.provider_territory_mapping`

Map provider geography codes to canonical territories.

```sql
CREATE TABLE meta.provider_territory_mapping (
    provider_territory_mapping_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id uuid NOT NULL REFERENCES meta.source(source_id),
    provider_dataset_code text NOT NULL,
    provider_territory_code text NOT NULL,
    code_system text NOT NULL,
    territory_id uuid NOT NULL REFERENCES curated.dim_territory(territory_id),
    provider_label text,
    metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now(),

    CONSTRAINT uq_meta_provider_territory_mapping
        UNIQUE (source_id, provider_dataset_code, code_system, provider_territory_code)
);
```

Examples:

| source | provider_dataset_code | code_system | provider_territory_code | canonical territory |
| --- | --- | --- | --- | --- |
| WDI | WDI | wdi_countryiso3code | USA | country / USA |
| WDI | WDI | wdi_countryiso3code | DNK | country / DNK |
| FRED | GDP | fred_series_scope | US | country / USA |
| EUROSTAT_NAMQ_GDP | namq_10_gdp | eurostat_geo | DE | country / DEU |
| EUROSTAT_NAMQ_GDP | namq_10_gdp | eurostat_geo | FR | country / FRA |
| EUROSTAT_NAMQ_GDP | namq_10_gdp | eurostat_geo | EU27_2020 | economic_area / EU27_2020 |
| EUROSTAT_NAMQ_GDP | namq_10_gdp | eurostat_geo | EA20 | economic_area / EA20 |

### 5. `meta.provider_code_list`

Store provider code dictionaries when needed for mapping, labels, or audit.

```sql
CREATE TABLE meta.provider_code_list (
    provider_code_list_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id uuid NOT NULL REFERENCES meta.source(source_id),
    provider_dataset_code text NOT NULL,
    dimension_name text NOT NULL,
    code_system text NOT NULL,
    dataset_release_id uuid REFERENCES meta.dataset_release(dataset_release_id),
    metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now(),

    CONSTRAINT uq_meta_provider_code_list
        UNIQUE (source_id, provider_dataset_code, dimension_name, code_system, dataset_release_id)
);
```

### 6. `meta.provider_code`

Store provider code values and labels.

```sql
CREATE TABLE meta.provider_code (
    provider_code_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    provider_code_list_id uuid NOT NULL REFERENCES meta.provider_code_list(provider_code_list_id),
    provider_code text NOT NULL,
    provider_label text,
    provider_parent_code text,
    metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now(),

    CONSTRAINT uq_meta_provider_code
        UNIQUE (provider_code_list_id, provider_code)
);
```

Examples:

| source | dataset | dimension_name | provider_code | provider_label |
| --- | --- | --- | --- | --- |
| OECD | SDD_NAD | REF_AREA | USA | United States |
| OECD | SDD_NAD | UNIT_MEASURE | USD_PPP | US dollars, PPP converted |
| EUROSTAT_NAMQ_GDP | namq_10_gdp | geo | DE | Germany |
| EUROSTAT_NAMQ_GDP | namq_10_gdp | unit | CP_MEUR | Current prices, million euro |
| EUROSTAT_NAMQ_GDP | namq_10_gdp | s_adj | NSA | Unadjusted data |

## Fact table impact

No provider-specific columns should be added to `curated.fact_observation`.

Current fact grain remains conceptually correct:

```text
source_id + indicator_id + territory_id + period_id + unit_id + attribute_set_id + as_of_date
```

The source/release/run lineage columns stay in the fact table:

- `source_id`
- `dataset_release_id`
- `pipeline_run_id`

This preserves provenance without leaking provider dimension codes into canonical facts.

## Example end-to-end rows

### World Bank annual

Canonical period:

| frequency | year | start | end | label |
| --- | ---: | --- | --- | --- |
| A | 2021 | 2021-01-01 | 2021-12-31 | 2021 |

Canonical territory:

| type | iso3 | canonical code | name |
| --- | --- | --- | --- |
| country | USA | USA | United States |

Provider mappings:

| mapping | provider code | canonical |
| --- | --- | --- |
| period | `2021` | A 2021 |
| territory | `USA` | country USA |

### FRED quarterly

Example series: `GDP`.

| mapping | provider code | canonical |
| --- | --- | --- |
| period | `2023-Q1` | Q 2023 Q1 |
| territory | `US` or series scope metadata | country USA |

### FRED monthly

Example series: `UNRATE`.

| mapping | provider code | canonical |
| --- | --- | --- |
| period | `2023-01` | M 2023-01 |
| territory | `US` or series scope metadata | country USA |

### FRED daily-ready

Example series: `DGS10`.

| mapping | provider code | canonical |
| --- | --- | --- |
| period | `2023-01-03` | D 2023-01-03 |
| territory | `US` or series scope metadata | country USA |

This is daily-ready only. TASK-022 should not add a FRED loader or daily ingestion.

### Eurostat quarterly

Example dataset: `namq_10_gdp`.

| mapping | provider code | canonical |
| --- | --- | --- |
| period | `2023-Q1` | Q 2023 Q1 |
| territory | `DE` | country DEU |
| territory | `FR` | country FRA |
| territory | `EU27_2020` | economic_area EU27_2020, if explicitly seeded |
| territory | `EA20` | economic_area EA20, if explicitly seeded |

## Migration-risk notes

1. `curated.dim_period` currently has unique `(frequency, period_year)` and existing WDI/OECD annual rows. A migration must backfill structured dates before tightening constraints.
2. Existing loaders use annual period assumptions. WDI and OECD loader tests must be updated to insert/use structured annual period rows.
3. `curated.dim_territory` currently includes `source_id` in its natural key. Removing source-scoped canonical territory identity requires deduplicating country rows across sources.
4. Existing WDI/OECD facts reference existing territory IDs. Migration must preserve or remap fact foreign keys safely.
5. Existing staging tables may remain source-specific and provider-shaped. They do not need to be rewritten immediately.
6. `meta.provider_code_list` uniqueness with nullable `dataset_release_id` needs careful PostgreSQL handling. TASK-022 may prefer an explicit sentinel release reference or use `NULLS NOT DISTINCT` if the project PostgreSQL version supports it.
7. Backfilling provider mappings should be deterministic from existing staging/source payloads for WDI and OECD; Eurostat mappings can be design/fixture-only until Eurostat promotion is separately accepted.
8. Aggregate territories should be seeded only for observed/needed codes such as `EU27_2020` and `EA20`; membership history is deferred.
9. Do not edit `001_v0_schema_foundation.sql`. Create a new migration, likely `003_canonical_domain_dimensions.sql`, to preserve migration history.

## Test implications

TASK-022 should be TDD and should include:

1. Schema tests:
   - annual, quarterly, monthly, daily period rows pass constraints;
   - invalid quarterly/monthly/daily combinations fail;
   - countries require ISO3;
   - non-country aggregates require null ISO3 and a canonical code;
   - provider period/territory mapping uniqueness is enforced;
   - provider code dictionaries enforce unique code-list/code pairs.

2. Loader compatibility tests:
   - WDI annual smoke still loads expected staging rows and facts;
   - OECD annual smoke still loads expected staging rows and facts;
   - fact grain remains unchanged except for new canonical `period_id`/`territory_id` rows.

3. Mapping tests:
   - WDI `2021` maps to canonical annual period 2021;
   - WDI `USA` maps to canonical country `USA`;
   - Eurostat fixture examples `2023-Q1`, `DE`, `FR`, optionally `EU27_2020` and `EA20`, map correctly without promoting Eurostat to PostgreSQL;
   - FRED example mapping fixtures for quarterly/monthly/daily periods can be pure schema/mapping tests, not source onboarding.

4. Negative tests:
   - provider period strings are not inserted as canonical period identity fields;
   - provider territory codes like `DE` are not stored as canonical ISO3 country codes;
   - `curated.fact_observation` is not widened with provider-specific columns.

## Next implementation task boundary

TASK-022 should implement only the accepted minimal schema migration and compatibility updates.

TASK-022 should not:

- promote Eurostat into PostgreSQL;
- add a FRED loader;
- add a generalized ingestion framework;
- add aggregate membership history;
- implement unit conversion;
- create research/mart tables;
- write to a live `macro` database.
