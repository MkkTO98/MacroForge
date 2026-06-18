from __future__ import annotations

import json
import os
import shutil
import subprocess
import uuid
from pathlib import Path

from macroforge import eurostat_namq_loader

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BASE_MIGRATION = PROJECT_ROOT / "db" / "migrations" / "001_v0_schema_foundation.sql"
OECD_MIGRATION = PROJECT_ROOT / "db" / "migrations" / "002_oecd_sdmx_staging.sql"
CANONICAL_DOMAIN_MIGRATION = PROJECT_ROOT / "db" / "migrations" / "003_canonical_domain_dimensions.sql"
EUROSTAT_MIGRATION = PROJECT_ROOT / "db" / "migrations" / "004_eurostat_namq_staging.sql"
NORMALIZED = PROJECT_ROOT / "data" / "metadata" / "eurostat" / "eurostat-namq-10-gdp-architecture-spike-normalized.json"


def _postgres_available() -> bool:
    return all(shutil.which(cmd) for cmd in ["createdb", "dropdb", "psql"])


def _psql(db_name: str, sql: str) -> str:
    result = subprocess.run(
        ["psql", "-v", "ON_ERROR_STOP=1", "-d", db_name, "-At", "-c", sql],
        check=True,
        capture_output=True,
        text=True,
        env=os.environ.copy(),
    )
    return result.stdout.strip()


def test_eurostat_namq_loader_builds_source_specific_sql_without_network(tmp_path):
    normalized = json.loads(NORMALIZED.read_text(encoding="utf-8"))
    sql = eurostat_namq_loader.build_load_sql(normalized, run_key="task-024-sql-test", as_of_date="2026-06-04")

    assert "requests.get" not in sql
    assert "curl" not in sql
    assert "urllib" not in sql
    assert "INSERT INTO staging.eurostat_namq_observation" in sql
    assert "INSERT INTO curated.fact_observation" in sql
    assert "INSERT INTO meta.provider_period_mapping" in sql
    assert "INSERT INTO meta.provider_territory_mapping" in sql
    assert "INSERT INTO meta.provider_code_list" in sql
    assert "INSERT INTO meta.provider_code" in sql
    assert "EUROSTAT_NAMQ_GDP" in sql
    assert "namq_10_gdp" in sql
    assert "2023-Q1" in sql
    assert "2023-Q2" in sql
    assert "DEU" in sql
    assert "FRA" in sql
    assert "CP_MEUR" in sql
    assert "B1GQ" in sql
    assert "NSA" in sql
    assert "staging.eurostat " not in sql
    assert "CREATE TABLE" not in sql

    report_path = tmp_path / "eurostat-report.json"
    payload = eurostat_namq_loader.write_load_report(
        report_path,
        {
            "staging_rows": 4,
            "fact_rows": 4,
            "canonical_periods": ["2023 Q1", "2023 Q2"],
            "canonical_territories": ["DEU", "FRA"],
            "provider_code_dimensions": ["freq", "geo", "na_item", "s_adj", "time", "unit"],
        },
    )
    assert payload["task"] == "TASK-024"
    assert payload["status"] == "succeeded"
    assert json.loads(report_path.read_text(encoding="utf-8"))["fact_rows"] == 4


def test_eurostat_namq_loader_is_idempotent_against_isolated_postgres():
    if not _postgres_available():
        return

    db_name = f"macroforge_eurostat_loader_test_{uuid.uuid4().hex[:12]}"
    try:
        subprocess.run(["createdb", db_name], check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as exc:
        if "could not connect" in exc.stderr.lower() or "role" in exc.stderr.lower():
            return
        raise

    try:
        for migration in [BASE_MIGRATION, OECD_MIGRATION, CANONICAL_DOMAIN_MIGRATION, EUROSTAT_MIGRATION]:
            subprocess.run(
                ["psql", "-v", "ON_ERROR_STOP=1", "-d", db_name, "-f", str(migration)],
                check=True,
                capture_output=True,
                text=True,
            )

        first = eurostat_namq_loader.load_eurostat_namq_smoke_to_postgres(
            db_name, NORMALIZED, run_key="task-024-test", as_of_date="2026-06-04"
        )
        second = eurostat_namq_loader.load_eurostat_namq_smoke_to_postgres(
            db_name, NORMALIZED, run_key="task-024-test", as_of_date="2026-06-04"
        )

        assert first["staging_rows"] == 4
        assert first["fact_rows"] == 4
        assert second["staging_rows"] == 4
        assert second["fact_rows"] == 4
        assert second["canonical_periods"] == ["2023 Q1", "2023 Q2"]
        assert second["canonical_territories"] == ["DEU", "FRA"]
        assert second["provider_periods"] == ["2023-Q1", "2023-Q2"]
        assert second["provider_territories"] == ["DE", "FR"]
        assert second["provider_code_dimensions"] == ["freq", "geo", "na_item", "s_adj", "time", "unit"]
        assert second["lineage_events"] == 2
        assert second["quality_checks"] == 4

        counts_sql = """
        SELECT
          (SELECT count(*) FROM meta.source),
          (SELECT count(*) FROM meta.dataset_release),
          (SELECT count(*) FROM meta.pipeline_run),
          (SELECT count(*) FROM staging.eurostat_namq_observation),
          (SELECT count(*) FROM curated.dim_indicator),
          (SELECT count(*) FROM curated.dim_territory),
          (SELECT count(*) FROM curated.dim_period),
          (SELECT count(*) FROM curated.dim_unit),
          (SELECT count(*) FROM curated.dim_attribute_set),
          (SELECT count(*) FROM curated.fact_observation),
          (SELECT count(*) FROM meta.lineage_event),
          (SELECT count(*) FROM meta.quality_check),
          (SELECT count(*) FROM meta.provider_period_mapping),
          (SELECT count(*) FROM meta.provider_territory_mapping),
          (SELECT count(*) FROM meta.provider_code_list),
          (SELECT count(*) FROM meta.provider_code)
        """
        counts = [int(value) for value in _psql(db_name, counts_sql).split("|")]
        assert counts == [1, 1, 1, 4, 1, 2, 2, 1, 2, 4, 2, 4, 2, 2, 6, 8]

        canonical_shapes = _psql(
            db_name,
            """
            SELECT
              (SELECT string_agg(period_label || ':' || period_start_date || ':' || period_end_date, ',' ORDER BY period_label) FROM curated.dim_period),
              (SELECT string_agg(territory_type || ':' || iso3_code || ':' || canonical_territory_code, ',' ORDER BY iso3_code) FROM curated.dim_territory),
              (SELECT string_agg(provider_period_code, ',' ORDER BY provider_period_code) FROM meta.provider_period_mapping),
              (SELECT string_agg(provider_territory_code || '->' || t.canonical_territory_code, ',' ORDER BY provider_territory_code) FROM meta.provider_territory_mapping ptm JOIN curated.dim_territory t ON ptm.territory_id = t.territory_id),
              (SELECT string_agg(DISTINCT dimension_name, ',' ORDER BY dimension_name) FROM meta.provider_code_list)
            """,
        ).split("|")
        assert canonical_shapes == [
            "2023 Q1:2023-01-01:2023-03-31,2023 Q2:2023-04-01:2023-06-30",
            "country:DEU:DEU,country:FRA:FRA",
            "2023-Q1,2023-Q2",
            "DE->DEU,FR->FRA",
            "freq,geo,na_item,s_adj,time,unit",
        ]

        duplicate_grain_count = int(
            _psql(
                db_name,
                """
                SELECT count(*) FROM (
                  SELECT source_id, indicator_id, territory_id, period_id, unit_id, attribute_set_id, as_of_date, count(*)
                  FROM curated.fact_observation
                  GROUP BY source_id, indicator_id, territory_id, period_id, unit_id, attribute_set_id, as_of_date
                  HAVING count(*) > 1
                ) duplicates
                """,
            )
        )
        assert duplicate_grain_count == 0

        fact_columns = _psql(
            db_name,
            """
            SELECT string_agg(column_name, ',' ORDER BY ordinal_position)
            FROM information_schema.columns
            WHERE table_schema = 'curated' AND table_name = 'fact_observation';
            """,
        )
        assert fact_columns == (
            "fact_observation_id,source_id,dataset_release_id,pipeline_run_id,indicator_id,territory_id,"
            "period_id,unit_id,attribute_set_id,value,as_of_date,observation_status,created_at"
        )
    finally:
        subprocess.run(["dropdb", "--if-exists", db_name], capture_output=True, text=True)
