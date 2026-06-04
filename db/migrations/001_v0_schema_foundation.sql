-- MacroForge v0 PostgreSQL schema foundation
-- TASK-004 / DEC-004
-- Recreated cleanly from reconstruction decisions; not restored from deleted files.

CREATE EXTENSION IF NOT EXISTS pgcrypto;

CREATE SCHEMA IF NOT EXISTS meta;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS curated;

CREATE TABLE IF NOT EXISTS meta.source (
    source_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    source_code text NOT NULL,
    source_name text NOT NULL,
    source_home_url text,
    license_note text,
    created_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT uq_meta_source_source_code UNIQUE (source_code)
);

CREATE TABLE IF NOT EXISTS meta.dataset_release (
    dataset_release_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id uuid NOT NULL REFERENCES meta.source(source_id),
    provider_dataset_code text NOT NULL,
    release_key text NOT NULL,
    release_date date,
    source_url text,
    raw_artifact_path text,
    raw_sha256 text,
    metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT uq_meta_dataset_release_natural UNIQUE (source_id, provider_dataset_code, release_key)
);

CREATE TABLE IF NOT EXISTS meta.pipeline_run (
    pipeline_run_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    run_key text NOT NULL,
    source_id uuid NOT NULL REFERENCES meta.source(source_id),
    dataset_release_id uuid REFERENCES meta.dataset_release(dataset_release_id),
    pipeline_name text NOT NULL,
    started_at timestamptz NOT NULL DEFAULT now(),
    finished_at timestamptz,
    status text NOT NULL DEFAULT 'started',
    input_parameters jsonb NOT NULL DEFAULT '{}'::jsonb,
    artifact_manifest jsonb NOT NULL DEFAULT '{}'::jsonb,
    CONSTRAINT ck_meta_pipeline_run_status CHECK (status IN ('started', 'succeeded', 'failed')),
    CONSTRAINT uq_meta_pipeline_run_run_key UNIQUE (run_key)
);

CREATE TABLE IF NOT EXISTS meta.lineage_event (
    lineage_event_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    pipeline_run_id uuid NOT NULL REFERENCES meta.pipeline_run(pipeline_run_id),
    source_id uuid NOT NULL REFERENCES meta.source(source_id),
    event_type text NOT NULL,
    from_artifact text,
    to_artifact text,
    checksum_sha256 text,
    row_count bigint,
    details jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS meta.quality_check (
    quality_check_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    pipeline_run_id uuid NOT NULL REFERENCES meta.pipeline_run(pipeline_run_id),
    check_name text NOT NULL,
    check_status text NOT NULL,
    severity text NOT NULL DEFAULT 'error',
    observed_value numeric,
    expected_value numeric,
    details jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT ck_meta_quality_check_status CHECK (check_status IN ('pass', 'warn', 'fail')),
    CONSTRAINT ck_meta_quality_check_severity CHECK (severity IN ('info', 'warning', 'error'))
);

CREATE TABLE IF NOT EXISTS staging.wdi_observation (
    wdi_observation_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    pipeline_run_id uuid NOT NULL REFERENCES meta.pipeline_run(pipeline_run_id),
    source_id uuid NOT NULL REFERENCES meta.source(source_id),
    dataset_release_id uuid REFERENCES meta.dataset_release(dataset_release_id),
    country_code text NOT NULL,
    country_name text,
    indicator_code text NOT NULL,
    indicator_name text,
    period_year integer NOT NULL,
    value numeric,
    unit_code text NOT NULL DEFAULT 'unknown',
    decimal_precision integer,
    as_of_date date NOT NULL,
    source_payload jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT uq_staging_wdi_observation_natural UNIQUE (pipeline_run_id, country_code, indicator_code, period_year)
);

CREATE TABLE IF NOT EXISTS curated.dim_indicator (
    indicator_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id uuid NOT NULL REFERENCES meta.source(source_id),
    source_indicator_code text NOT NULL,
    indicator_name text NOT NULL,
    description text,
    topic text,
    created_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT uq_curated_dim_indicator_natural UNIQUE (source_id, source_indicator_code)
);

CREATE TABLE IF NOT EXISTS curated.dim_territory (
    territory_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id uuid NOT NULL REFERENCES meta.source(source_id),
    iso3_code text NOT NULL,
    territory_name text NOT NULL,
    region text,
    income_group text,
    created_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT uq_curated_dim_territory_natural UNIQUE (source_id, iso3_code)
);

CREATE TABLE IF NOT EXISTS curated.dim_period (
    period_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    frequency text NOT NULL,
    period_year integer NOT NULL,
    period_start_date date,
    period_end_date date,
    created_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT uq_curated_dim_period_natural UNIQUE (frequency, period_year)
);

CREATE TABLE IF NOT EXISTS curated.dim_unit (
    unit_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    unit_code text NOT NULL,
    unit_name text NOT NULL,
    unit_description text,
    created_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT uq_curated_dim_unit_natural UNIQUE (unit_code)
);

CREATE TABLE IF NOT EXISTS curated.dim_attribute_set (
    attribute_set_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    attribute_hash text NOT NULL,
    attributes jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT uq_curated_dim_attribute_set_natural UNIQUE (attribute_hash)
);

CREATE TABLE IF NOT EXISTS curated.fact_observation (
    fact_observation_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id uuid NOT NULL REFERENCES meta.source(source_id),
    dataset_release_id uuid REFERENCES meta.dataset_release(dataset_release_id),
    pipeline_run_id uuid NOT NULL REFERENCES meta.pipeline_run(pipeline_run_id),
    indicator_id uuid NOT NULL REFERENCES curated.dim_indicator(indicator_id),
    territory_id uuid NOT NULL REFERENCES curated.dim_territory(territory_id),
    period_id uuid NOT NULL REFERENCES curated.dim_period(period_id),
    unit_id uuid NOT NULL REFERENCES curated.dim_unit(unit_id),
    attribute_set_id uuid NOT NULL REFERENCES curated.dim_attribute_set(attribute_set_id),
    value numeric,
    as_of_date date NOT NULL,
    observation_status text NOT NULL DEFAULT 'observed',
    created_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT ck_curated_fact_observation_status CHECK (observation_status IN ('observed', 'missing', 'suppressed')),
    CONSTRAINT uq_curated_fact_observation_grain UNIQUE (source_id, indicator_id, territory_id, period_id, unit_id, attribute_set_id, as_of_date)
);

-- Idempotent loader pattern for later TASK-006:
-- INSERT INTO meta.source (source_code, source_name)
-- VALUES ('WDI', 'World Bank World Development Indicators')
-- ON CONFLICT (source_code) DO UPDATE SET source_name = EXCLUDED.source_name;
