from __future__ import annotations

import json
import os
import shutil
import subprocess
import uuid
from pathlib import Path

from macroforge import wdi_loader
from synthetic_wdi import build_synthetic_wdi_fixture, write_synthetic_wdi_fixture

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MIGRATION = PROJECT_ROOT / "db" / "migrations" / "001_v0_schema_foundation.sql"
CANONICAL_DOMAIN_MIGRATION = PROJECT_ROOT / "db" / "migrations" / "003_canonical_domain_dimensions.sql"



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

        normalized_path = write_synthetic_wdi_fixture(
            tmp_path / "wdi-smoke-normalized.json", "normalized_smoke"
        )
        first = wdi_loader.load_wdi_smoke_to_postgres(db_name, normalized_path, run_key="task-006-test")
        second = wdi_loader.load_wdi_smoke_to_postgres(db_name, normalized_path, run_key="task-006-test")

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


def _write_variant(path: Path, *, lastupdated: str, drop_last_row: bool = False) -> Path:
    normalized = build_synthetic_wdi_fixture("normalized_smoke")
    for artifact in normalized["raw_artifacts"]:
        artifact["source_metadata"]["lastupdated"] = lastupdated
    if drop_last_row:
        normalized["rows"] = normalized["rows"][:-1]
        normalized["row_count"] = len(normalized["rows"])
        normalized["expected_row_count"] = len(normalized["rows"])
    path.write_text(json.dumps(normalized, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return path


def test_wdi_loader_corrected_same_run_reload_is_scoped_and_idempotent(tmp_path):
    if not _postgres_available():
        return

    db_name = f"macroforge_loader_scope_test_{uuid.uuid4().hex[:12]}"
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

        original = _write_variant(tmp_path / "original.json", lastupdated="2026-04-08")
        unrelated = _write_variant(tmp_path / "unrelated.json", lastupdated="2027-01-01")
        corrected = _write_variant(tmp_path / "corrected.json", lastupdated="2028-01-01", drop_last_row=True)

        wdi_loader.load_wdi_smoke_to_postgres(db_name, original, run_key="same-run")
        wdi_loader.load_wdi_smoke_to_postgres(db_name, unrelated, run_key="unrelated-run")
        first_corrected = wdi_loader.load_wdi_smoke_to_postgres(db_name, corrected, run_key="same-run")
        second_corrected = wdi_loader.load_wdi_smoke_to_postgres(db_name, corrected, run_key="same-run")

        assert first_corrected == second_corrected
        assert second_corrected["staging_rows"] == 15
        assert second_corrected["fact_rows"] == 15
        assert second_corrected["lineage_events"] == 4
        assert second_corrected["quality_checks"] == 4

        scoped_counts = [int(value) for value in _psql(
            db_name,
            """
            SELECT
              (SELECT count(*) FROM staging.wdi_observation swo JOIN meta.pipeline_run pr ON swo.pipeline_run_id = pr.pipeline_run_id WHERE pr.run_key = 'same-run'),
              (SELECT count(*) FROM curated.fact_observation fo JOIN meta.pipeline_run pr ON fo.pipeline_run_id = pr.pipeline_run_id WHERE pr.run_key = 'same-run'),
              (SELECT count(*) FROM staging.wdi_observation swo JOIN meta.pipeline_run pr ON swo.pipeline_run_id = pr.pipeline_run_id WHERE pr.run_key = 'unrelated-run'),
              (SELECT count(*) FROM curated.fact_observation fo JOIN meta.pipeline_run pr ON fo.pipeline_run_id = pr.pipeline_run_id WHERE pr.run_key = 'unrelated-run'),
              (SELECT count(*) FROM meta.lineage_event le JOIN meta.pipeline_run pr ON le.pipeline_run_id = pr.pipeline_run_id WHERE pr.run_key = 'same-run'),
              (SELECT count(*) FROM meta.quality_check qc JOIN meta.pipeline_run pr ON qc.pipeline_run_id = pr.pipeline_run_id WHERE pr.run_key = 'same-run')
            """,
        ).split("|")]
        assert scoped_counts == [7, 7, 8, 8, 2, 2]

        as_of_dates = _psql(
            db_name,
            """
            SELECT pr.run_key || ':' || string_agg(DISTINCT swo.as_of_date::text, ',' ORDER BY swo.as_of_date::text)
            FROM staging.wdi_observation swo
            JOIN meta.pipeline_run pr ON swo.pipeline_run_id = pr.pipeline_run_id
            GROUP BY pr.run_key
            ORDER BY pr.run_key
            """,
        ).splitlines()
        assert as_of_dates == ["same-run:2028-01-01", "unrelated-run:2027-01-01"]

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


def test_wdi_loader_sql_uses_transaction_and_run_scoped_replacement() -> None:
    sql = wdi_loader.build_load_sql(
        build_synthetic_wdi_fixture("normalized_smoke"), run_key="task-006-sql-safety-test"
    )

    assert "BEGIN;" in sql
    assert "COMMIT;" in sql
    assert "DELETE FROM curated.fact_observation fo\nUSING run_row run\nWHERE fo.pipeline_run_id = run.pipeline_run_id" in sql
    assert "DELETE FROM meta.lineage_event le\nUSING run_row run\nWHERE le.pipeline_run_id = run.pipeline_run_id" in sql
    assert "DELETE FROM meta.quality_check qc\nUSING run_row run\nWHERE qc.pipeline_run_id = run.pipeline_run_id" in sql
    assert "ON CONFLICT (source_id, indicator_id, territory_id, period_id, unit_id, attribute_set_id, as_of_date) DO UPDATE" in sql


def test_wdi_loader_cli_writes_load_report_sql_without_network(tmp_path):
    report = tmp_path / "load-report.json"
    sql = wdi_loader.build_load_sql(
        build_synthetic_wdi_fixture("normalized_smoke"), run_key="task-006-sql-test"
    )

    assert "INSERT INTO staging.wdi_observation" in sql
    assert "INSERT INTO curated.fact_observation" in sql
    assert "INSERT INTO meta.provider_period_mapping" in sql
    assert "INSERT INTO meta.provider_territory_mapping" in sql
    assert "ON CONFLICT" in sql
    assert "task-006-sql-test" in sql

    payload = wdi_loader.write_load_report(report, {"staging_rows": 8, "fact_rows": 8})
    assert payload["staging_rows"] == 8
    assert json.loads(report.read_text(encoding="utf-8"))["fact_rows"] == 8
