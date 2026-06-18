from __future__ import annotations

import json
import os
import shutil
import subprocess
import uuid
from pathlib import Path

from macroforge import canonical_gdp_snapshot

PROJECT_ROOT = Path(__file__).resolve().parents[1]
JSON_REPORT = PROJECT_ROOT / "artifacts" / "reports" / "canonical-gdp-snapshot-20260604.json"
MD_REPORT = PROJECT_ROOT / "artifacts" / "reports" / "canonical-gdp-snapshot-20260604.md"


class FakeRunner:
    def __init__(self):
        self.commands: list[list[str]] = []
        self.dropped: list[str] = []

    def run(self, command, **kwargs):
        self.commands.append(list(command))

    def dropdb(self, db_name: str) -> None:
        self.dropped.append(db_name)


def _postgres_available() -> bool:
    return all(shutil.which(cmd) for cmd in ["createdb", "dropdb", "psql"])


def test_snapshot_plan_is_isolated_and_points_to_deterministic_project_reports(tmp_path):
    plan = canonical_gdp_snapshot.build_snapshot_plan(
        project_root=tmp_path,
        db_name="macroforge_canonical_gdp_snapshot_test",
    )

    assert plan.db_name == "macroforge_canonical_gdp_snapshot_test"
    assert plan.db_name != "macro"
    assert plan.json_report_path == tmp_path / "artifacts" / "reports" / "canonical-gdp-snapshot-20260604.json"
    assert plan.markdown_report_path == tmp_path / "artifacts" / "reports" / "canonical-gdp-snapshot-20260604.md"
    assert plan.generated_at == "2026-06-04T00:00:00Z"
    assert plan.combined_run_key_prefix.startswith("canonical-gdp-snapshot-")


def test_snapshot_refuses_live_macro_database(tmp_path):
    runner = FakeRunner()

    try:
        canonical_gdp_snapshot.run_canonical_gdp_snapshot(project_root=tmp_path, db_name="macro", runner=runner)
    except ValueError as exc:
        assert "live `macro` database" in str(exc)
    else:
        raise AssertionError("expected live database refusal")

    assert runner.commands == []
    assert runner.dropped == []


def test_core_report_sql_uses_only_curated_and_meta_tables():
    sql_text = "\n".join(canonical_gdp_snapshot.CORE_REPORT_SQL.values()).lower()

    assert "curated." in sql_text
    assert "meta." in sql_text
    assert "staging." not in sql_text
    assert " from wdi" not in sql_text
    assert "oecd_sdmx_observation" not in sql_text
    assert "eurostat_namq_observation" not in sql_text


def test_snapshot_runner_uses_isolated_combined_database_and_writes_reports_with_fake_runner(tmp_path):
    runner = FakeRunner()

    report = canonical_gdp_snapshot.run_canonical_gdp_snapshot(
        project_root=tmp_path,
        db_name="macroforge_canonical_gdp_snapshot_test",
        runner=runner,
    )

    command_text = [" ".join(command) for command in runner.commands]
    assert command_text[0] == "createdb macroforge_canonical_gdp_snapshot_test"
    assert sum("psql -v ON_ERROR_STOP=1 -d macroforge_canonical_gdp_snapshot_test -f" in text for text in command_text) == 4
    assert runner.dropped == ["macroforge_canonical_gdp_snapshot_test"]

    assert report["task"] == "TASK-028"
    assert report["status"] == "succeeded"
    assert report["metadata"]["database_safety"] == "isolated_temporary_database"
    assert report["coverage"]["fact_rows_by_source"] == {"EUROSTAT_NAMQ_GDP": 4, "OECD_NAAG": 8, "WDI": 8}
    assert report["data_quality"]["duplicate_fact_grain_count"] == 0
    assert report["data_quality"]["failing_quality_checks"] == 0
    assert (tmp_path / "artifacts" / "reports" / "canonical-gdp-snapshot-20260604.json").exists()
    assert (tmp_path / "artifacts" / "reports" / "canonical-gdp-snapshot-20260604.md").exists()


def test_report_writer_is_deterministic_and_includes_required_sections(tmp_path):
    report = canonical_gdp_snapshot.fake_snapshot_report("macroforge_canonical_gdp_snapshot_test")

    json_path = tmp_path / "snapshot.json"
    md_path = tmp_path / "snapshot.md"
    canonical_gdp_snapshot.write_snapshot_reports(json_path, md_path, report)
    first_json = json_path.read_text(encoding="utf-8")
    first_md = md_path.read_text(encoding="utf-8")
    canonical_gdp_snapshot.write_snapshot_reports(json_path, md_path, report)

    assert json_path.read_text(encoding="utf-8") == first_json
    assert md_path.read_text(encoding="utf-8") == first_md
    loaded = json.loads(first_json)
    assert loaded["metadata"]["report_name"] == "canonical_gdp_snapshot"
    assert loaded["coverage"]["sources"] == ["EUROSTAT_NAMQ_GDP", "OECD_NAAG", "WDI"]
    assert "missingness" in loaded
    assert "source_lineage" in loaded
    assert "gdp_snapshot" in loaded
    assert "duplicate_fact_grain_count" in loaded["data_quality"]
    assert "# Canonical GDP Snapshot" in first_md
    assert "No unit conversion or frequency aggregation is performed." in first_md


def test_snapshot_runs_against_isolated_postgres_and_generates_canonical_only_report():
    if not _postgres_available():
        return

    db_name = f"macroforge_canonical_gdp_snapshot_test_{uuid.uuid4().hex[:12]}"
    try:
        subprocess.run(["createdb", db_name], check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as exc:
        if "could not connect" in exc.stderr.lower() or "role" in exc.stderr.lower():
            return
        raise
    else:
        subprocess.run(["dropdb", "--if-exists", db_name], capture_output=True, text=True)

    report = canonical_gdp_snapshot.run_canonical_gdp_snapshot(
        project_root=PROJECT_ROOT,
        db_name=db_name,
        run_key_prefix="task-028-test",
        json_report_path=JSON_REPORT,
        markdown_report_path=MD_REPORT,
    )

    assert report["status"] == "succeeded"
    assert report["coverage"]["fact_rows_total"] == 20
    assert report["coverage"]["fact_rows_by_source"] == {"EUROSTAT_NAMQ_GDP": 4, "OECD_NAAG": 8, "WDI": 8}
    assert report["coverage"]["frequencies"] == ["A", "Q"]
    assert set(report["coverage"]["territories"]) >= {"AUS", "DEU", "DNK", "FRA", "USA"}
    assert report["data_quality"]["duplicate_fact_grain_count"] == 0
    assert report["data_quality"]["failing_quality_checks"] == 0
    assert report["data_quality"]["core_query_boundary"] == "curated_and_meta_only"
    assert report["missingness"]["missing_observation_count"] == 0
    assert len(report["gdp_snapshot"]["observations"]) == 16
    assert "SP.POP.TOTL" not in {row["indicator_code"] for row in report["gdp_snapshot"]["observations"]}
    assert {row["frequency"] for row in report["gdp_snapshot"]["observations"]} == {"A", "Q"}
    assert json.loads(JSON_REPORT.read_text(encoding="utf-8"))["status"] == "succeeded"
    assert "# Canonical GDP Snapshot" in MD_REPORT.read_text(encoding="utf-8")
