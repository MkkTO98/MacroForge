# MacroForge Minimal Source Contract

Status: accepted for second-source spike
Created: 2026-06-03
Decision: `artifacts/decisions/DEC-005-post-vertical-slice-architecture-and-next-source-scope.md`
Task: TASK-010

## Purpose

This contract is the smallest shared shape needed to compare World Bank WDI with a second macro data source without building a broad ingestion framework prematurely.

It is a specification for source spikes and future source-specific loaders. It is not a plugin registry, ORM model, scheduler, or generalized ingestion framework.

## Contract fields

A candidate source spike or implementation should document these fields before curated loading is accepted.

### 1. Source identity

- `source_code`: stable short code used in `meta.source.source_code`.
- `source_name`: human-readable source name.
- `source_home_url`: canonical source landing page.
- `provider_dataset_code`: provider dataset or collection identifier.
- `license_note`: no-key/public/usage note sufficient for internal research use.

### 2. Access and raw evidence

- `access_method`: HTTP API, downloaded file, support bundle, or local fixture.
- `credentials_required`: must be `false` for the current v1/v2 no-key scope unless a new decision changes policy.
- `source_url`: exact endpoint or artifact source.
- `raw_artifact_path`: filesystem path to immutable raw payload evidence.
- `raw_sha256`: SHA-256 checksum of the raw payload.
- `raw_bytes`: byte count.
- `source_metadata`: provider metadata such as last updated date, pagination, dimensions, or response headers.

### 3. Normalized observation rows

A source-specific normalizer should be able to produce observation rows with these conceptual fields, even if field names differ by source:

- `source`
- `indicator_id`
- `indicator_name`
- `territory_code`
- `territory_name`
- `period`
- `frequency`
- `value`
- `unit`
- `observation_status`
- `decimal_precision` or source-specific precision note
- `as_of_date` or source release/vintage value
- `source_payload`

### 4. Grain and vintage behavior

Each source must state:

- observation grain, for example indicator + territory + annual period + unit + attribute set + as-of date
- frequency values expected in the smoke slice
- whether data is revised, versioned, or only available as latest values
- how `as_of_date` / release key is derived
- what missing/suppressed values look like

### 5. Staging and curated load assumptions

Before curated load, the source must state whether it can reuse the current curated observation model:

- `curated.dim_indicator`
- `curated.dim_territory`
- `curated.dim_period`
- `curated.dim_unit`
- `curated.dim_attribute_set`
- `curated.fact_observation`

If a source does not fit indicator/territory/period/value shape, create a decision record before changing schema.

### 6. Required validation checks

Minimum checks for a smoke slice:

- required raw artifact exists
- raw checksum matches manifest
- normalized row count equals expected row count
- required staging/curated tables exist before load
- staging row count equals expected row count
- fact row count equals expected row count
- no duplicate curated fact grain
- quality checks pass
- lineage events exist for raw-to-staging and staging-to-curated

## WDI mapping

### Source identity

- `source_code`: `WDI`
- `source_name`: `World Bank World Development Indicators`
- `source_home_url`: `https://data.worldbank.org/`
- `provider_dataset_code`: `WDI`
- `license_note`: World Bank WDI no-key public API smoke slice; internal research use.

### Access and raw evidence

- `access_method`: support bundle from prior live no-key HTTP fetch.
- `credentials_required`: `false`
- `source_url`: World Bank v2 indicator endpoints recorded per raw artifact in `data/metadata/wdi/wdi-smoke-manifest.json`.
- `raw_artifact_path`: `data/raw/wdi/`
- `raw_sha256`:
  - `NY.GDP.MKTP.CD`: `fe79eb846324a5d69df9518844e08b41add5377ac4f968208bd1152898d91167`
  - `SP.POP.TOTL`: `bfda0ac8ed98a9a68ceb6af210f893f2a57e1313b829c1fd9cb73c70b04d5c0b`
- `source_metadata`: World Bank payload metadata copied into `data/metadata/wdi/wdi-smoke-normalized.json`.

### Normalized observation row mapping

- `source`: `World Bank WDI`
- `indicator_id`: World Bank indicator id, for example `NY.GDP.MKTP.CD`
- `indicator_name`: World Bank indicator display name
- `territory_code`: `countryiso3code`
- `territory_name`: `country.value`
- `period`: `date`
- `frequency`: annual, derived from WDI yearly observations
- `value`: `value`
- `unit`: WDI `unit`, normalized to `unknown` when blank for curated load
- `observation_status`: `missing` when value is null, else `observed`
- `decimal_precision`: `decimal`
- `as_of_date`: derived from World Bank metadata `lastupdated` when available
- `source_payload`: full normalized source row JSON

### Grain and vintage behavior

Current WDI smoke fact grain follows DEC-004:

`source_id + indicator_id + territory_id + period_id + unit_id + attribute_set_id + as_of_date`

WDI revisions are represented by `dataset_release.release_key` and curated `as_of_date`. The current smoke slice uses annual frequency and two indicators for USA/DNK over 2020-2021.

### Validation checks

WDI currently satisfies the minimum checks through:

- `src/macroforge/wdi.py`
- `src/macroforge/wdi_loader.py`
- `src/macroforge/wdi_validation.py`
- `src/macroforge/wdi_smoke.py`
- `tests/test_wdi.py`
- `tests/test_wdi_loader.py`
- `tests/test_wdi_validation.py`
- `tests/test_wdi_smoke.py`

## Intentionally not generalized yet

Do not generalize these until a second source produces evidence:

- no plugin registry
- no abstract base class for all sources
- no orchestration framework
- no ORM/SQLAlchemy model layer
- no Alembic migration framework
- no automatic source discovery
- no generalized SDMX parser
- no `mart` schema/reporting model
- no paid/credentialed source workflow

## How TASK-011 should use this contract

The OECD/SDMX-style second-source spike should fill a short evidence report against the same sections:

1. Source identity.
2. Access and raw evidence.
3. Response shape and normalized observation row feasibility.
4. Grain/frequency/as-of behavior.
5. Whether the current curated observation model fits.
6. Required validation checks and smallest possible implementation task.

The spike may conclude that OECD/SDMX is not viable yet. That is acceptable if the report records evidence and recommends the next no-key candidate.

## OECD/SDMX bounded codelist enrichment evidence

Status: accepted as bounded filesystem metadata/report evidence for TASK-019.

TASK-019 adds source-specific label/description evidence for the existing OECD/SDMX smoke slice without changing schemas or introducing a generalized SDMX framework.

Evidence artifacts:

- raw structure fixture/evidence: `data/raw/oecd_sdmx/oecd_sdmx_naag_structure_20260604.xml`
- normalized labels: `data/metadata/oecd_sdmx/oecd-sdmx-codelist-labels-20260604.json`
- report: `artifacts/reports/oecd-sdmx-codelist-labels-20260604.md`

Bounded labels/descriptions currently covered:

- `MEASURE` / `B1GQ`: Gross domestic product; GDP, expenditure approach, current prices.
- `REF_AREA` / `AUS`: Australia.
- `REF_AREA` / `USA`: United States.
- `UNIT_MEASURE` / `USD_EXC`: US dollars, exchange rate converted.
- `UNIT_MEASURE` / `USD_PPP`: US dollars, PPP converted.
- `CONF_STATUS` / `F`: Free for publication.
- `OBS_STATUS` / `A`: Normal value.
- `DECIMALS` / `2`: preserved as an observed attribute value when no codelist label is present in bounded fixture evidence.

Limits:

- This is not broad codelist harvesting.
- This is not a generalized SDMX/source framework.
- This does not load labels into PostgreSQL.
- This does not change curated/staging schemas.
- Future database/schema promotion of labels requires a new accepted decision.

## Eurostat third-source architecture spike evidence

Status: accepted as bounded architecture-spike evidence for TASK-020.

TASK-020 validates the current canonical model, ingestion posture, metadata architecture, and fact table design against one additional public no-key source: Eurostat quarterly national accounts GDP (`namq_10_gdp`). It is not a production-grade Eurostat ingestion implementation.

Evidence artifacts:

- raw public no-key JSON: `data/raw/eurostat/eurostat-namq-10-gdp-2023q1-2023q2-raw.json`
- normalized architecture evidence: `data/metadata/eurostat/eurostat-namq-10-gdp-architecture-spike-normalized.json`
- findings report: `artifacts/reports/eurostat-third-source-architecture-spike-20260604.md`

Bounded source identity:

- `source_code`: `EUROSTAT_NAMQ_GDP`
- `source_name`: Eurostat quarterly national accounts GDP
- `source_home_url`: `https://ec.europa.eu/eurostat/`
- `provider_dataset_code`: `namq_10_gdp`
- `credentials_required`: `false`
- `access_method`: HTTP JSON-stat API

Bounded smoke slice:

- countries/provider geographies: `DE`, `FR`
- indicator: `B1GQ` / Gross domestic product at market prices
- frequency: quarterly (`Q`)
- periods: `2023-Q1`, `2023-Q2`
- unit: `CP_MEUR` / Current prices, million euro
- seasonal adjustment: `NSA` / unadjusted data
- normalized rows: 4

Architecture verdict: PARTIAL.

Findings:

- The broad canonical observation concept still fits: indicator, territory, period, unit, value, attributes, source payload.
- The current concrete `curated.dim_period` design is too annual because `(frequency, period_year)` would collapse quarterly observations such as `2023-Q1` and `2023-Q2`.
- The current concrete territory design is too narrow for provider geography codes and regional aggregates, but ISO3 should remain the canonical country identifier.
- Provider dimension/code dictionaries are becoming recurring metadata across OECD and Eurostat; metadata architecture should grow either first-class provider codelist tables or stricter dataset-release metadata conventions before many more sources are promoted.

DEC-010 refinement:

The TASK-020 schema recommendations are interpreted from a canonical-domain perspective, not a provider-centric one.

1. Extend `curated.dim_period` with structured canonical period fields for annual, quarterly, monthly, and eventually daily observations. Provider period strings such as `2023-Q1` belong in metadata/mapping, not canonical period identity.
2. Preserve ISO3 as the canonical country identifier. Add `territory_type` and aggregate/economic-area support for non-country territories rather than replacing ISO3 semantics with provider codes.
3. Add provider period/territory/code mappings and provider code-list metadata before broad source promotion.
4. If Eurostat is promoted later, use source-specific `staging.eurostat_namq_observation`; do not build a generalized ingestion framework yet.
5. Preserve seasonal adjustment in `curated.dim_attribute_set` initially.

Limits:

- No PostgreSQL write occurred.
- No executable schema migration was created.
- No production-grade Eurostat ingestion was implemented.
- No generalized ingestion/source framework was introduced.
- Future schema implementation requires a new accepted decision/task.
