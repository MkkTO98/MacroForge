-- MacroForge Eurostat NAMQ source-specific staging migration
-- TASK-024 / DEC-012
-- Bounded scope: recorded Eurostat namq_10_gdp fixture only.
-- This is intentionally not a generalized Eurostat or JSON-stat framework.

CREATE TABLE IF NOT EXISTS staging.eurostat_namq_observation (
    eurostat_namq_observation_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
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
    observation_status text NOT NULL DEFAULT 'observed',
    decimal_precision integer,
    as_of_date date NOT NULL,
    jsonstat_flat_index integer,
    source_payload jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT ck_staging_eurostat_namq_frequency CHECK (frequency = 'Q'),
    CONSTRAINT ck_staging_eurostat_namq_quarter CHECK (period_quarter BETWEEN 1 AND 4),
    CONSTRAINT uq_staging_eurostat_namq_observation UNIQUE (
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

CREATE INDEX IF NOT EXISTS ix_staging_eurostat_namq_release
ON staging.eurostat_namq_observation (dataset_release_id);

CREATE INDEX IF NOT EXISTS ix_staging_eurostat_namq_period_geo
ON staging.eurostat_namq_observation (provider_period_code, provider_geo_code);
