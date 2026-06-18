from __future__ import annotations

import json
import os
import shutil
import subprocess
import uuid
from pathlib import Path

from macroforge import oecd_sdmx_loader

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BASE_MIGRATION = PROJECT_ROOT / "db" / "migrations" / "001_v0_schema_foundation.sql"
OECD_MIGRATION = PROJECT_ROOT / "db" / "migrations" / "002_oecd_sdmx_staging.sql"
CANONICAL_DOMAIN_MIGRATION = PROJECT_ROOT / "db" / "migrations" / "003_canonical_domain_dimensions.sql"
NORMALIZED = PROJECT_ROOT / "data" / "metadata" / "oecd_sdmx" / "oecd-sdmx-smoke-normalized.json"


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


def test_oecd_sdmx_loader_builds_source_specific_sql_without_network(tmp_path):
    normalized = json.loads(NORMALIZED.read_text(encoding="utf-8"))
    sql = oecd_sdmx_loader.build_load_sql(normalized, run_key="task-015-sql-test", as_of_date="2026-06-03")

    assert "requests.get" not in sql
    assert "curl" not in sql
    assert "INSERT INTO staging.oecd_sdmx_observation" in sql
    assert "INSERT INTO curated.fact_observation" in sql
    assert "INSERT INTO meta.provider_period_mapping" in sql
    assert "INSERT INTO meta.provider_territory_mapping" in sql
    assert "OECD_NAAG" in sql
    assert "USD_EXC" in sql
    assert "USD_PPP" in sql
    assert "CONF_STATUS" in sql
    assert "DECIMALS" in sql
    assert "OBS_STATUS" in sql
    assert "staging.sdmx" not in sql

    report_path = tmp_path / "oecd-report.json"
    payload = oecd_sdmx_loader.write_load_report(
        report_path,
        {
            "staging_rows": 8,
            "fact_rows": 8,
            "unit_codes": ["USD_EXC", "USD_PPP"],
            "attribute_sets": 1,
        },
    )
    assert payload["task"] == "TASK-015"
    assert payload["status"] == "succeeded"
    assert json.loads(report_path.read_text(encoding="utf-8"))["fact_rows"] == 8


def test_oecd_sdmx_loader_is_idempotent_against_isolated_postgres():
    if not _postgres_available():
        return

    db_name = f"macroforge_oecd_loader_test_{uuid.uuid4().hex[:12]}"
    try:
        subprocess.run(["createdb", db_name], check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as exc:
        if "could not connect" in exc.stderr.lower() or "role" in exc.stderr.lower():
            return
        raise

    try:
        for migration in [BASE_MIGRATION, OECD_MIGRATION, CANONICAL_DOMAIN_MIGRATION]:
            subprocess.run(
                ["psql", "-v", "ON_ERROR_STOP=1", "-d", db_name, "-f", str(migration)],
                check=True,
                capture_output=True,
                text=True,
            )

        first = oecd_sdmx_loader.load_oecd_sdmx_smoke_to_postgres(
            db_name, NORMALIZED, run_key="task-015-test", as_of_date="2026-06-03"
        )
        second = oecd_sdmx_loader.load_oecd_sdmx_smoke_to_postgres(
            db_name, NORMALIZED, run_key="task-015-test", as_of_date="2026-06-03"
        )

        assert first["staging_rows"] == 8
        assert first["fact_rows"] == 8
        assert second["staging_rows"] == 8
        assert second["fact_rows"] == 8
        assert second["unit_codes"] == ["USD_EXC", "USD_PPP"]
        assert second["attribute_sets"] == 1
        assert second["lineage_events"] == 2
        assert second["quality_checks"] == 4

        counts_sql = """
        SELECT
          (SELECT count(*) FROM meta.source),
          (SELECT count(*) FROM meta.dataset_release),
          (SELECT count(*) FROM meta.pipeline_run),
          (SELECT count(*) FROM staging.oecd_sdmx_observation),
          (SELECT count(*) FROM curated.dim_indicator),
          (SELECT count(*) FROM curated.dim_territory),
          (SELECT count(*) FROM curated.dim_period),
          (SELECT count(*) FROM curated.dim_unit),
          (SELECT count(*) FROM curated.dim_attribute_set),
          (SELECT count(*) FROM curated.fact_observation),
          (SELECT count(*) FROM meta.lineage_event),
          (SELECT count(*) FROM meta.quality_check),
          (SELECT count(*) FROM meta.provider_period_mapping),
          (SELECT count(*) FROM meta.provider_territory_mapping)
        """
        counts = [int(value) for value in _psql(db_name, counts_sql).split("|")]
        assert counts == [1, 1, 1, 8, 1, 2, 2, 2, 1, 8, 2, 4, 2, 2]

        canonical_shapes = _psql(
            db_name,
            """
            SELECT
              (SELECT string_agg(period_label, ',' ORDER BY period_label) FROM curated.dim_period),
              (SELECT string_agg(territory_type || ':' || iso3_code || ':' || canonical_territory_code, ',' ORDER BY iso3_code) FROM curated.dim_territory),
              (SELECT string_agg(provider_period_code, ',' ORDER BY provider_period_code) FROM meta.provider_period_mapping),
              (SELECT string_agg(provider_territory_code, ',' ORDER BY provider_territory_code) FROM meta.provider_territory_mapping)
            """,
        ).split("|")
        assert canonical_shapes == ["2020,2021", "country:AUS:AUS,country:USA:USA", "2020,2021", "AUS,USA"]

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

        attributes = json.loads(
            _psql(
                db_name,
                "SELECT attributes::text FROM curated.dim_attribute_set",
            )
        )
        assert attributes == {"CONF_STATUS": "F", "DECIMALS": "2", "OBS_STATUS": "A"}
    finally:
        subprocess.run(["dropdb", "--if-exists", db_name], capture_output=True, text=True)
