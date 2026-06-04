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
SCHEMA_DOC = PROJECT_ROOT / "db" / "schema" / "v0_schema_foundation.md"
HEALTH_QUERY = PROJECT_ROOT / "db" / "queries" / "schema_health_check.sql"

REQUIRED_SCHEMAS = ["meta", "staging", "curated"]
REQUIRED_TABLES = [
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

    for table_name in REQUIRED_TABLES:
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
        subprocess.run(
            ["psql", "-v", "ON_ERROR_STOP=1", "-d", db_name, "-f", str(MIGRATION)],
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
