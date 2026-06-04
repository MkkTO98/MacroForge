-- MacroForge OECD/SDMX source-specific staging migration
-- TASK-015 / DEC-006
-- This is intentionally not a generalized SDMX staging framework.

CREATE TABLE IF NOT EXISTS staging.oecd_sdmx_observation (
    oecd_sdmx_observation_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    pipeline_run_id uuid NOT NULL REFERENCES meta.pipeline_run(pipeline_run_id),
    source_id uuid NOT NULL REFERENCES meta.source(source_id),
    dataset_release_id uuid REFERENCES meta.dataset_release(dataset_release_id),
    provider_dataset_code text NOT NULL,
    measure_code text NOT NULL,
    ref_area_code text NOT NULL,
    period_year integer NOT NULL,
    frequency text NOT NULL,
    unit_measure_code text NOT NULL,
    value numeric,
    observation_status text NOT NULL DEFAULT 'observed',
    decimal_precision integer,
    attributes jsonb NOT NULL DEFAULT '{}'::jsonb,
    series_dimensions jsonb NOT NULL DEFAULT '{}'::jsonb,
    source_payload jsonb NOT NULL DEFAULT '{}'::jsonb,
    as_of_date date NOT NULL,
    created_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT uq_staging_oecd_sdmx_observation_natural UNIQUE (
        pipeline_run_id,
        provider_dataset_code,
        measure_code,
        ref_area_code,
        period_year,
        unit_measure_code
    )
);
