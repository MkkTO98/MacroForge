from __future__ import annotations

import os
import re
import shutil
import subprocess
import uuid
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MIGRATION = PROJECT_ROOT / "db" / "migrations" / "001_v0_schema_foundation.sql"
OECD_SDMX_MIGRATION = PROJECT_ROOT / "db" / "migrations" / "002_oecd_sdmx_staging.sql"
CANONICAL_DOMAIN_MIGRATION = PROJECT_ROOT / "db" / "migrations" / "003_canonical_domain_dimensions.sql"
EUROSTAT_NAMQ_MIGRATION = PROJECT_ROOT / "db" / "migrations" / "004_eurostat_namq_staging.sql"
SCHEMA_DOC = PROJECT_ROOT / "db" / "schema" / "v0_schema_foundation.md"
HEALTH_QUERY = PROJECT_ROOT / "db" / "queries" / "schema_health_check.sql"

REQUIRED_SCHEMAS = ["meta", "staging", "curated"]
BASE_REQUIRED_TABLES = [
    "meta.source",
    "meta.dataset_release",
    "meta.pipeline_run",
    "meta.lineage_event",
    "meta.quality_check",
    "staging.wdi_observation",
    "curated.dim_indicator",
    "curated.dim_territory",
    "curated.dim_period",
    "curated.dim_unit",
    "curated.dim_attribute_set",
    "curated.fact_observation",
]
REQUIRED_TABLES = [
    *BASE_REQUIRED_TABLES,
    "meta.provider_period_mapping",
    "meta.provider_territory_mapping",
    "meta.provider_code_list",
    "meta.provider_code",
    "staging.oecd_sdmx_observation",
    "staging.eurostat_namq_observation",
]


def _sql() -> str:
    return MIGRATION.read_text(encoding="utf-8")


def _normalised_sql() -> str:
    return re.sub(r"\s+", " ", _sql().lower())


def test_v0_schema_foundation_files_exist_and_document_scope():
    assert MIGRATION.exists(), "raw SQL migration is required for TASK-004"
    assert SCHEMA_DOC.exists(), "schema reference doc is required for future agents"
    assert HEALTH_QUERY.exists(), "schema health-check SQL query is required"

    schema_doc = SCHEMA_DOC.read_text(encoding="utf-8")
    for table_name in REQUIRED_TABLES:
        assert table_name in schema_doc

    assert "World Bank WDI" in schema_doc
    assert "macro" in schema_doc


def test_migration_declares_required_schemas_tables_and_idempotency_constraints():
    sql = _normalised_sql()

    for schema_name in REQUIRED_SCHEMAS:
        assert f"create schema if not exists {schema_name}" in sql

    for table_name in BASE_REQUIRED_TABLES:
        schema_name, table = table_name.split(".")
        assert f"create table if not exists {schema_name}.{table}" in sql

    required_natural_keys = [
        "source_code",
        "source_id, provider_dataset_code, release_key",
        "run_key",
        "pipeline_run_id, country_code, indicator_code, period_year",
        "source_id, source_indicator_code",
        "source_id, iso3_code",
        "frequency, period_year",
        "unit_code",
        "attribute_hash",
        "source_id, indicator_id, territory_id, period_id, unit_id, attribute_set_id, as_of_date",
    ]
    for key in required_natural_keys:
        assert key in sql

    assert "pipeline_run_id uuid not null" in sql
    assert "as_of_date date not null" in sql
    assert "on conflict" in sql, "migration should document idempotent insert/upsert examples"


def test_oecd_sdmx_staging_migration_exists_and_has_required_shape():
    assert OECD_SDMX_MIGRATION.exists(), "TASK-015 must add a second raw SQL migration"
    sql = re.sub(r"\s+", " ", OECD_SDMX_MIGRATION.read_text(encoding="utf-8").lower())

    assert "create table if not exists staging.oecd_sdmx_observation" in sql
    for required_column in [
        "pipeline_run_id uuid not null references meta.pipeline_run",
        "source_id uuid not null references meta.source",
        "dataset_release_id uuid references meta.dataset_release",
        "provider_dataset_code text not null",
        "measure_code text not null",
        "ref_area_code text not null",
        "period_year integer not null",
        "frequency text not null",
        "unit_measure_code text not null",
        "attributes jsonb not null default '{}'::jsonb",
        "series_dimensions jsonb not null default '{}'::jsonb",
        "source_payload jsonb not null default '{}'::jsonb",
        "as_of_date date not null",
    ]:
        assert required_column in sql

    assert "pipeline_run_id, provider_dataset_code, measure_code, ref_area_code, period_year, unit_measure_code" in sql
    assert "create table if not exists staging.sdmx" not in sql



def test_canonical_domain_migration_declares_minimal_schema_evolution():
    assert CANONICAL_DOMAIN_MIGRATION.exists(), "TASK-022 must add a third migration, not edit 001 as primary path"
    sql = re.sub(r"\s+", " ", CANONICAL_DOMAIN_MIGRATION.read_text(encoding="utf-8").lower())

    for required in [
        "alter table curated.dim_period",
        "period_quarter integer",
        "period_month integer",
        "period_date date",
        "period_label text",
        "ck_curated_dim_period_frequency",
        "ck_curated_dim_period_quarterly",
        "ck_curated_dim_period_monthly",
        "ck_curated_dim_period_daily",
        "uq_curated_dim_period_interval",
        "alter table curated.dim_territory",
        "territory_type text",
        "canonical_territory_code text",
        "ck_curated_dim_territory_type",
        "ck_curated_dim_territory_country_iso3",
        "uq_curated_dim_territory_canonical_code",
        "create table if not exists meta.provider_period_mapping",
        "create table if not exists meta.provider_territory_mapping",
        "create table if not exists meta.provider_code_list",
        "create table if not exists meta.provider_code",
    ]:
        assert required in sql

    assert "alter table curated.fact_observation add column provider" not in sql
    assert "create table if not exists staging.eurostat" not in sql
    assert "create table if not exists staging.fred" not in sql


def test_eurostat_namq_staging_migration_exists_and_has_required_shape():
    assert EUROSTAT_NAMQ_MIGRATION.exists(), "TASK-024 must add a source-specific Eurostat staging migration"
    sql = re.sub(r"\s+", " ", EUROSTAT_NAMQ_MIGRATION.read_text(encoding="utf-8").lower())

    assert "create table if not exists staging.eurostat_namq_observation" in sql
    for required_column in [
        "pipeline_run_id uuid not null references meta.pipeline_run",
        "dataset_release_id uuid not null references meta.dataset_release",
        "provider_dataset_code text not null",
        "frequency text not null",
        "unit_code text not null",
        "seasonal_adjustment_code text not null",
        "national_accounts_item_code text not null",
        "provider_geo_code text not null",
        "provider_period_code text not null",
        "period_year integer not null",
        "period_quarter integer not null",
        "observation_value numeric not null",
        "observation_status text not null",
        "source_payload jsonb not null default '{}'::jsonb",
    ]:
        assert required_column in sql

    for required_constraint in [
        "ck_staging_eurostat_namq_frequency",
        "check (frequency = 'q')",
        "ck_staging_eurostat_namq_quarter",
        "check (period_quarter between 1 and 4)",
        "uq_staging_eurostat_namq_observation",
        "pipeline_run_id, provider_dataset_code, frequency, unit_code, seasonal_adjustment_code, national_accounts_item_code, provider_geo_code, provider_period_code",
    ]:
        assert required_constraint in sql

    assert "create table if not exists staging.eurostat " not in sql
    assert "jsonstat framework" not in sql


def test_canonical_domain_migration_constraints_against_isolated_postgres_when_available():
    if shutil.which("psql") is None or shutil.which("createdb") is None or shutil.which("dropdb") is None:
        return

    db_name = f"macroforge_canonical_schema_test_{uuid.uuid4().hex[:12]}"
    env = os.environ.copy()
    try:
        subprocess.run(["createdb", db_name], check=True, env=env, capture_output=True, text=True)
    except subprocess.CalledProcessError as exc:
        if "could not connect" in exc.stderr.lower() or "role" in exc.stderr.lower():
            return
        raise

    def psql(sql: str) -> str:
        result = subprocess.run(
            ["psql", "-v", "ON_ERROR_STOP=1", "-d", db_name, "-At", "-c", sql],
            check=True,
            env=env,
            capture_output=True,
            text=True,
        )
        return result.stdout.strip()

    def psql_fails(sql: str) -> str:
        result = subprocess.run(
            ["psql", "-v", "ON_ERROR_STOP=1", "-d", db_name, "-At", "-c", sql],
            env=env,
            capture_output=True,
            text=True,
        )
        assert result.returncode != 0
        return result.stderr

    try:
        for migration in [MIGRATION, OECD_SDMX_MIGRATION, CANONICAL_DOMAIN_MIGRATION]:
            subprocess.run(
                ["psql", "-v", "ON_ERROR_STOP=1", "-d", db_name, "-f", str(migration)],
                check=True,
                env=env,
                capture_output=True,
                text=True,
            )

        psql(
            """
            INSERT INTO curated.dim_period (frequency, period_year, period_start_date, period_end_date, period_label)
            VALUES ('A', 2021, '2021-01-01', '2021-12-31', '2021');
            INSERT INTO curated.dim_period (frequency, period_year, period_quarter, period_start_date, period_end_date, period_label)
            VALUES ('Q', 2023, 1, '2023-01-01', '2023-03-31', '2023 Q1');
            INSERT INTO curated.dim_period (frequency, period_year, period_month, period_start_date, period_end_date, period_label)
            VALUES ('M', 2023, 1, '2023-01-01', '2023-01-31', '2023-01');
            INSERT INTO curated.dim_period (frequency, period_year, period_date, period_start_date, period_end_date, period_label)
            VALUES ('D', 2023, '2023-01-03', '2023-01-03', '2023-01-03', '2023-01-03');
            """
        )
        psql_fails(
            """
            INSERT INTO curated.dim_period (frequency, period_year, period_month, period_start_date, period_end_date, period_label)
            VALUES ('Q', 2024, 1, '2024-01-01', '2024-03-31', 'bad quarter');
            """
        )
        psql_fails(
            """
            INSERT INTO curated.dim_period (frequency, period_year, period_date, period_start_date, period_end_date, period_label)
            VALUES ('D', 2024, '2024-01-03', '2024-01-01', '2024-01-03', 'bad day');
            """
        )

        psql(
            """
            INSERT INTO meta.source (source_code, source_name) VALUES ('WDI', 'World Bank WDI');
            INSERT INTO meta.source (source_code, source_name) VALUES ('EUROSTAT_NAMQ_GDP', 'Eurostat NAMQ GDP');
            INSERT INTO curated.dim_territory (territory_type, iso3_code, canonical_territory_code, territory_name)
            VALUES ('country', 'USA', 'USA', 'United States');
            INSERT INTO curated.dim_territory (territory_type, iso3_code, canonical_territory_code, territory_name)
            VALUES ('country', 'DEU', 'DEU', 'Germany');
            INSERT INTO curated.dim_territory (territory_type, canonical_territory_code, territory_name)
            VALUES ('economic_area', 'EU27_2020', 'European Union - 27 countries from 2020');
            """
        )
        psql_fails(
            """
            INSERT INTO curated.dim_territory (territory_type, canonical_territory_code, territory_name)
            VALUES ('country', 'BAD', 'Bad country without ISO3');
            """
        )
        psql_fails(
            """
            INSERT INTO curated.dim_territory (territory_type, iso3_code, canonical_territory_code, territory_name)
            VALUES ('economic_area', 'EUR', 'EA20', 'Bad aggregate with ISO3');
            """
        )

        psql(
            """
            INSERT INTO meta.provider_period_mapping (source_id, provider_dataset_code, provider_period_code, period_id, provider_label)
            SELECT s.source_id, 'WDI', '2021', p.period_id, '2021'
            FROM meta.source s CROSS JOIN curated.dim_period p
            WHERE s.source_code = 'WDI' AND p.frequency = 'A' AND p.period_year = 2021;
            INSERT INTO meta.provider_territory_mapping (source_id, provider_dataset_code, provider_territory_code, code_system, territory_id, provider_label)
            SELECT s.source_id, 'namq_10_gdp', 'DE', 'eurostat_geo', t.territory_id, 'Germany'
            FROM meta.source s CROSS JOIN curated.dim_territory t
            WHERE s.source_code = 'EUROSTAT_NAMQ_GDP' AND t.iso3_code = 'DEU';
            INSERT INTO meta.provider_code_list (source_id, provider_dataset_code, dimension_name, code_system)
            SELECT source_id, 'namq_10_gdp', 'geo', 'eurostat_geo'
            FROM meta.source WHERE source_code = 'EUROSTAT_NAMQ_GDP';
            INSERT INTO meta.provider_code (provider_code_list_id, provider_code, provider_label)
            SELECT provider_code_list_id, 'DE', 'Germany' FROM meta.provider_code_list;
            """
        )
        psql_fails(
            """
            INSERT INTO meta.provider_code (provider_code_list_id, provider_code, provider_label)
            SELECT provider_code_list_id, 'DE', 'Duplicate Germany' FROM meta.provider_code_list;
            """
        )

        fact_columns = psql(
            """
            SELECT string_agg(column_name, ',' ORDER BY ordinal_position)
            FROM information_schema.columns
            WHERE table_schema = 'curated' AND table_name = 'fact_observation';
            """
        )
        assert fact_columns == (
            "fact_observation_id,source_id,dataset_release_id,pipeline_run_id,indicator_id,territory_id,"
            "period_id,unit_id,attribute_set_id,value,as_of_date,observation_status,created_at"
        )
    finally:
        subprocess.run(["dropdb", "--if-exists", db_name], env=env, capture_output=True, text=True)


def test_schema_health_query_checks_all_required_tables():
    query = HEALTH_QUERY.read_text(encoding="utf-8").lower()
    for table_name in REQUIRED_TABLES:
        assert f"to_regclass('{table_name}')" in query


def test_migration_applies_to_isolated_postgres_when_available():
    if shutil.which("psql") is None or shutil.which("createdb") is None or shutil.which("dropdb") is None:
        return

    db_name = f"macroforge_schema_test_{uuid.uuid4().hex[:12]}"
    env = os.environ.copy()
    try:
        subprocess.run(["createdb", db_name], check=True, env=env, capture_output=True, text=True)
    except subprocess.CalledProcessError as exc:
        if "could not connect" in exc.stderr.lower() or "role" in exc.stderr.lower():
            return
        raise

    try:
        for migration in [MIGRATION, OECD_SDMX_MIGRATION, CANONICAL_DOMAIN_MIGRATION, EUROSTAT_NAMQ_MIGRATION]:
            subprocess.run(
                ["psql", "-v", "ON_ERROR_STOP=1", "-d", db_name, "-f", str(migration)],
                check=True,
                env=env,
                capture_output=True,
                text=True,
            )
        subprocess.run(
            ["psql", "-v", "ON_ERROR_STOP=1", "-d", db_name, "-f", str(HEALTH_QUERY)],
            check=True,
            env=env,
            capture_output=True,
            text=True,
        )
    finally:
        subprocess.run(["dropdb", "--if-exists", db_name], env=env, capture_output=True, text=True)
