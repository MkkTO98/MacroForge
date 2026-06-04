-- MacroForge v0 schema health check
-- Returns one row per required table with regclass existence status.

WITH required_tables(table_name, regclass_value) AS (
    VALUES
        ('meta.source', to_regclass('meta.source')),
        ('meta.dataset_release', to_regclass('meta.dataset_release')),
        ('meta.pipeline_run', to_regclass('meta.pipeline_run')),
        ('meta.lineage_event', to_regclass('meta.lineage_event')),
        ('meta.quality_check', to_regclass('meta.quality_check')),
        ('staging.wdi_observation', to_regclass('staging.wdi_observation')),
        ('curated.dim_indicator', to_regclass('curated.dim_indicator')),
        ('curated.dim_territory', to_regclass('curated.dim_territory')),
        ('curated.dim_period', to_regclass('curated.dim_period')),
        ('curated.dim_unit', to_regclass('curated.dim_unit')),
        ('curated.dim_attribute_set', to_regclass('curated.dim_attribute_set')),
        ('curated.fact_observation', to_regclass('curated.fact_observation'))
)
SELECT
    table_name,
    regclass_value IS NOT NULL AS exists
FROM required_tables
ORDER BY table_name;
