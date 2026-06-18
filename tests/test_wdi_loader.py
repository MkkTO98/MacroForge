from __future__ import annotations

import json
import os
import shutil
import subprocess
import uuid
from pathlib import Path

from macroforge import wdi_loader

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MIGRATION = PROJECT_ROOT / "db" / "migrations" / "001_v0_schema_foundation.sql"
CANONICAL_DOMAIN_MIGRATION = PROJECT_ROOT / "db" / "migrations" / "003_canonical_domain_dimensions.sql"
NORMALIZED = PROJECT_ROOT / "data" / "metadata" / "wdi" / "wdi-smoke-normalized.json"


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


def test_wdi_loader_is_idempotent_against_isolated_postgres(tmp_path):
    if not _postgres_available():
        return

    db_name = f"macroforge_loader_test_{uuid.uuid4().hex[:12]}"
    try:
        subprocess.run(["createdb", db_name], check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as exc:
        if "could not connect" in exc.stderr.lower() or "role" in exc.stderr.lower():
            return
        raise

    try:
        for migration in [MIGRATION, CANONICAL_DOMAIN_MIGRATION]:
            subprocess.run(
                ["psql", "-v", "ON_ERROR_STOP=1", "-d", db_name, "-f", str(migration)],
                check=True,
                capture_output=True,
                text=True,
            )

        first = wdi_loader.load_wdi_smoke_to_postgres(db_name, NORMALIZED, run_key="task-006-test")
        second = wdi_loader.load_wdi_smoke_to_postgres(db_name, NORMALIZED, run_key="task-006-test")

        assert first["staging_rows"] == 8
        assert first["fact_rows"] == 8
        assert second["staging_rows"] == 8
        assert second["fact_rows"] == 8

        counts_sql = """
        SELECT
          (SELECT count(*) FROM meta.source),
          (SELECT count(*) FROM meta.dataset_release),
          (SELECT count(*) FROM meta.pipeline_run),
          (SELECT count(*) FROM staging.wdi_observation),
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
        assert counts == [1, 1, 1, 8, 2, 2, 2, 1, 1, 8, 2, 2, 2, 2]

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
        assert canonical_shapes == ["2020,2021", "country:DNK:DNK,country:USA:USA", "2020,2021", "DNK,USA"]

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
    finally:
        subprocess.run(["dropdb", "--if-exists", db_name], capture_output=True, text=True)


def test_wdi_loader_cli_writes_load_report_sql_without_network(tmp_path):
    report = tmp_path / "load-report.json"
    sql = wdi_loader.build_load_sql(json.loads(NORMALIZED.read_text(encoding="utf-8")), run_key="task-006-sql-test")

    assert "INSERT INTO staging.wdi_observation" in sql
    assert "INSERT INTO curated.fact_observation" in sql
    assert "INSERT INTO meta.provider_period_mapping" in sql
    assert "INSERT INTO meta.provider_territory_mapping" in sql
    assert "ON CONFLICT" in sql
    assert "task-006-sql-test" in sql

    payload = wdi_loader.write_load_report(report, {"staging_rows": 8, "fact_rows": 8})
    assert payload["staging_rows"] == 8
    assert json.loads(report.read_text(encoding="utf-8"))["fact_rows"] == 8
