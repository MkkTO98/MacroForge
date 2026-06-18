-- MacroForge minimal canonical-domain dimension migration
-- TASK-022 / DEC-011
-- Bounded scope: structured periods, territory typing, provider mappings, provider code dictionaries.
-- This does not promote Eurostat/FRED, widen curated facts, or introduce a generalized ingestion framework.

CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- -----------------------------------------------------------------------------
-- Structured canonical periods
-- -----------------------------------------------------------------------------

ALTER TABLE curated.dim_period
    ADD COLUMN IF NOT EXISTS period_quarter integer,
    ADD COLUMN IF NOT EXISTS period_month integer,
    ADD COLUMN IF NOT EXISTS period_date date,
    ADD COLUMN IF NOT EXISTS period_label text;

UPDATE curated.dim_period
SET period_start_date = COALESCE(period_start_date, make_date(period_year, 1, 1)),
    period_end_date = COALESCE(period_end_date, make_date(period_year, 12, 31)),
    period_label = COALESCE(period_label, period_year::text)
WHERE frequency = 'A';

ALTER TABLE curated.dim_period
    ALTER COLUMN period_start_date SET NOT NULL,
    ALTER COLUMN period_end_date SET NOT NULL,
    ALTER COLUMN period_label SET NOT NULL;

ALTER TABLE curated.dim_period
    DROP CONSTRAINT IF EXISTS uq_curated_dim_period_natural;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'ck_curated_dim_period_frequency'
    ) THEN
        ALTER TABLE curated.dim_period
            ADD CONSTRAINT ck_curated_dim_period_frequency
            CHECK (frequency IN ('A', 'Q', 'M', 'D'));
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'ck_curated_dim_period_order'
    ) THEN
        ALTER TABLE curated.dim_period
            ADD CONSTRAINT ck_curated_dim_period_order
            CHECK (period_start_date <= period_end_date);
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'ck_curated_dim_period_annual'
    ) THEN
        ALTER TABLE curated.dim_period
            ADD CONSTRAINT ck_curated_dim_period_annual
            CHECK (
                frequency <> 'A'
                OR (
                    period_quarter IS NULL
                    AND period_month IS NULL
                    AND period_date IS NULL
                )
            );
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'ck_curated_dim_period_quarterly'
    ) THEN
        ALTER TABLE curated.dim_period
            ADD CONSTRAINT ck_curated_dim_period_quarterly
            CHECK (
                frequency <> 'Q'
                OR (
                    period_quarter BETWEEN 1 AND 4
                    AND period_month IS NULL
                    AND period_date IS NULL
                )
            );
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'ck_curated_dim_period_monthly'
    ) THEN
        ALTER TABLE curated.dim_period
            ADD CONSTRAINT ck_curated_dim_period_monthly
            CHECK (
                frequency <> 'M'
                OR (
                    period_quarter IS NULL
                    AND period_month BETWEEN 1 AND 12
                    AND period_date IS NULL
                )
            );
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'ck_curated_dim_period_daily'
    ) THEN
        ALTER TABLE curated.dim_period
            ADD CONSTRAINT ck_curated_dim_period_daily
            CHECK (
                frequency <> 'D'
                OR (
                    period_quarter IS NULL
                    AND period_month IS NULL
                    AND period_date IS NOT NULL
                    AND period_start_date = period_date
                    AND period_end_date = period_date
                )
            );
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'uq_curated_dim_period_interval'
    ) THEN
        ALTER TABLE curated.dim_period
            ADD CONSTRAINT uq_curated_dim_period_interval
            UNIQUE (frequency, period_start_date, period_end_date);
    END IF;
END $$;

-- -----------------------------------------------------------------------------
-- Canonical territory typing
-- -----------------------------------------------------------------------------

ALTER TABLE curated.dim_territory
    ADD COLUMN IF NOT EXISTS territory_type text,
    ADD COLUMN IF NOT EXISTS canonical_territory_code text,
    ADD COLUMN IF NOT EXISTS valid_from date,
    ADD COLUMN IF NOT EXISTS valid_to date,
    ADD COLUMN IF NOT EXISTS metadata jsonb NOT NULL DEFAULT '{}'::jsonb;

UPDATE curated.dim_territory
SET territory_type = COALESCE(territory_type, 'country'),
    canonical_territory_code = COALESCE(canonical_territory_code, iso3_code),
    metadata = COALESCE(metadata, '{}'::jsonb)
WHERE iso3_code IS NOT NULL;

-- If older source-scoped country rows already exist, remap facts to one canonical
-- country row per ISO3 before adding canonical uniqueness constraints.
WITH ranked AS (
    SELECT
        territory_id,
        iso3_code,
        (first_value(territory_id::text) OVER (PARTITION BY iso3_code ORDER BY created_at, territory_id::text))::uuid AS survivor_id
    FROM curated.dim_territory
    WHERE iso3_code IS NOT NULL
), duplicates AS (
    SELECT territory_id, survivor_id
    FROM ranked
    WHERE territory_id <> survivor_id
)
UPDATE curated.fact_observation fact
SET territory_id = duplicates.survivor_id
FROM duplicates
WHERE fact.territory_id = duplicates.territory_id;

WITH ranked AS (
    SELECT
        territory_id,
        (first_value(territory_id::text) OVER (PARTITION BY iso3_code ORDER BY created_at, territory_id::text))::uuid AS survivor_id
    FROM curated.dim_territory
    WHERE iso3_code IS NOT NULL
)
DELETE FROM curated.dim_territory territory
USING ranked
WHERE territory.territory_id = ranked.territory_id
  AND ranked.territory_id <> ranked.survivor_id;

ALTER TABLE curated.dim_territory
    ALTER COLUMN source_id DROP NOT NULL,
    ALTER COLUMN iso3_code DROP NOT NULL,
    ALTER COLUMN territory_type SET NOT NULL,
    ALTER COLUMN canonical_territory_code SET NOT NULL,
    ALTER COLUMN metadata SET NOT NULL;

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'ck_curated_dim_territory_type'
    ) THEN
        ALTER TABLE curated.dim_territory
            ADD CONSTRAINT ck_curated_dim_territory_type
            CHECK (territory_type IN ('country', 'economic_area', 'aggregate'));
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'ck_curated_dim_territory_country_iso3'
    ) THEN
        ALTER TABLE curated.dim_territory
            ADD CONSTRAINT ck_curated_dim_territory_country_iso3
            CHECK (
                (territory_type = 'country' AND iso3_code IS NOT NULL)
                OR (territory_type <> 'country' AND iso3_code IS NULL)
            );
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'uq_curated_dim_territory_iso3_country'
    ) THEN
        ALTER TABLE curated.dim_territory
            ADD CONSTRAINT uq_curated_dim_territory_iso3_country
            UNIQUE (iso3_code);
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_constraint WHERE conname = 'uq_curated_dim_territory_canonical_code'
    ) THEN
        ALTER TABLE curated.dim_territory
            ADD CONSTRAINT uq_curated_dim_territory_canonical_code
            UNIQUE (canonical_territory_code);
    END IF;
END $$;

-- -----------------------------------------------------------------------------
-- Provider mappings and bounded provider code dictionaries
-- -----------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS meta.provider_period_mapping (
    provider_period_mapping_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id uuid NOT NULL REFERENCES meta.source(source_id),
    provider_dataset_code text NOT NULL,
    provider_period_code text NOT NULL,
    period_id uuid NOT NULL REFERENCES curated.dim_period(period_id),
    provider_label text,
    metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT uq_meta_provider_period_mapping UNIQUE (source_id, provider_dataset_code, provider_period_code)
);

CREATE TABLE IF NOT EXISTS meta.provider_territory_mapping (
    provider_territory_mapping_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id uuid NOT NULL REFERENCES meta.source(source_id),
    provider_dataset_code text NOT NULL,
    provider_territory_code text NOT NULL,
    code_system text NOT NULL,
    territory_id uuid NOT NULL REFERENCES curated.dim_territory(territory_id),
    provider_label text,
    metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT uq_meta_provider_territory_mapping UNIQUE (source_id, provider_dataset_code, code_system, provider_territory_code)
);

CREATE TABLE IF NOT EXISTS meta.provider_code_list (
    provider_code_list_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    source_id uuid NOT NULL REFERENCES meta.source(source_id),
    provider_dataset_code text NOT NULL,
    dimension_name text NOT NULL,
    code_system text NOT NULL,
    dataset_release_id uuid REFERENCES meta.dataset_release(dataset_release_id),
    metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_meta_provider_code_list
ON meta.provider_code_list (
    source_id,
    provider_dataset_code,
    dimension_name,
    code_system,
    COALESCE(dataset_release_id, '00000000-0000-0000-0000-000000000000'::uuid)
);

CREATE TABLE IF NOT EXISTS meta.provider_code (
    provider_code_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    provider_code_list_id uuid NOT NULL REFERENCES meta.provider_code_list(provider_code_list_id),
    provider_code text NOT NULL,
    provider_label text,
    provider_parent_code text,
    metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now(),
    CONSTRAINT uq_meta_provider_code UNIQUE (provider_code_list_id, provider_code)
);
