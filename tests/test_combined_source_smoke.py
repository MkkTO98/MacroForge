from __future__ import annotations

import json
import os
import shutil
import subprocess
import uuid
from pathlib import Path

from macroforge import combined_source_smoke

PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = PROJECT_ROOT / "artifacts" / "reports" / "combined-source-canonical-smoke-20260604.json"


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


def _psql(db_name: str, sql: str) -> str:
    result = subprocess.run(
        ["psql", "-v", "ON_ERROR_STOP=1", "-d", db_name, "-At", "-c", sql],
        check=True,
        capture_output=True,
        text=True,
        env=os.environ.copy(),
    )
    return result.stdout.strip()


def test_combined_source_smoke_plan_is_isolated_and_uses_existing_migrations_and_evidence(tmp_path):
    plan = combined_source_smoke.build_combined_smoke_plan(
        project_root=tmp_path,
        db_name="macroforge_combined_source_smoke_test",
    )

    assert plan.db_name == "macroforge_combined_source_smoke_test"
    assert plan.db_name != "macro"
    assert [path.name for path in plan.migration_paths] == [
        "001_v0_schema_foundation.sql",
        "002_oecd_sdmx_staging.sql",
        "003_canonical_domain_dimensions.sql",
        "004_eurostat_namq_staging.sql",
    ]
    assert plan.wdi_normalized_path == tmp_path / "data" / "metadata" / "wdi" / "wdi-smoke-normalized.json"
    assert plan.oecd_normalized_path == tmp_path / "data" / "metadata" / "oecd_sdmx" / "oecd-sdmx-smoke-normalized.json"
    assert plan.eurostat_normalized_path == tmp_path / "data" / "metadata" / "eurostat" / "eurostat-namq-10-gdp-architecture-spike-normalized.json"
    assert plan.run_key_prefix.startswith("combined-source-smoke-")


def test_combined_source_smoke_refuses_live_macro_database(tmp_path):
    runner = FakeRunner()

    try:
        combined_source_smoke.run_combined_source_smoke(project_root=tmp_path, db_name="macro", runner=runner)
    except ValueError as exc:
        assert "live `macro` database" in str(exc)
    else:
        raise AssertionError("expected live database refusal")

    assert runner.commands == []
    assert runner.dropped == []


def test_combined_source_smoke_runner_executes_create_migrations_loads_checks_report_and_cleanup(tmp_path):
    runner = FakeRunner()

    result = combined_source_smoke.run_combined_source_smoke(
        project_root=tmp_path,
        db_name="macroforge_combined_source_smoke_test",
        runner=runner,
        write_report=False,
    )

    command_text = [" ".join(command) for command in runner.commands]
    assert command_text[0] == "createdb macroforge_combined_source_smoke_test"
    assert sum("psql -v ON_ERROR_STOP=1 -d macroforge_combined_source_smoke_test -f" in text for text in command_text) == 4
    assert runner.dropped == ["macroforge_combined_source_smoke_test"]
    assert result["status"] == "succeeded"
    assert result["database"] == "macroforge_combined_source_smoke_test"
    assert result["sources"] == ["EUROSTAT_NAMQ_GDP", "OECD_NAAG", "WDI"]
    assert result["checks"]["no_duplicate_fact_grain"] == "pass"
    assert result["checks"]["source_specific_loaders_remain_separate"] == "pass"


def test_combined_source_smoke_module_does_not_introduce_framework_surface():
    source = (PROJECT_ROOT / "src" / "macroforge" / "combined_source_smoke.py").read_text(encoding="utf-8")

    forbidden = [
        "class BaseLoader",
        "class SourcePlugin",
        "PluginRegistry",
        "jsonstat framework",
        "sqlalchemy",
        "requests.get",
        "urllib.request",
    ]
    for token in forbidden:
        assert token not in source


def test_combined_source_smoke_writes_project_layout_report(tmp_path):
    payload = {
        "status": "succeeded",
        "sources": ["EUROSTAT_NAMQ_GDP", "OECD_NAAG", "WDI"],
        "source_count": 3,
        "fact_rows_by_source": {"EUROSTAT_NAMQ_GDP": 4, "OECD_NAAG": 8, "WDI": 8},
        "checks": {"no_duplicate_fact_grain": "pass"},
    }

    report = combined_source_smoke.write_combined_report(tmp_path / "combined.json", payload)

    assert report["task"] == "TASK-026"
    assert report["status"] == "succeeded"
    assert json.loads((tmp_path / "combined.json").read_text(encoding="utf-8"))["source_count"] == 3


def test_combined_source_smoke_runs_against_isolated_postgres_and_combines_all_sources():
    if not _postgres_available():
        return

    db_name = f"macroforge_combined_source_test_{uuid.uuid4().hex[:12]}"
    try:
        subprocess.run(["createdb", db_name], check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as exc:
        if "could not connect" in exc.stderr.lower() or "role" in exc.stderr.lower():
            return
        raise
    else:
        subprocess.run(["dropdb", "--if-exists", db_name], capture_output=True, text=True)

    report = combined_source_smoke.run_combined_source_smoke(
        project_root=PROJECT_ROOT,
        db_name=db_name,
        run_key_prefix="task-026-test",
        report_path=REPORT_PATH,
    )

    assert report["status"] == "succeeded"
    assert report["source_count"] == 3
    assert report["dataset_release_count"] == 3
    assert report["staging_rows_by_table"] == {
        "staging.eurostat_namq_observation": 4,
        "staging.oecd_sdmx_observation": 8,
        "staging.wdi_observation": 8,
    }
    assert report["fact_rows_by_source"] == {"EUROSTAT_NAMQ_GDP": 4, "OECD_NAAG": 8, "WDI": 8}
    assert report["fact_rows_total"] == 20
    assert report["duplicate_fact_grain_count"] == 0
    assert report["canonical_frequencies"] == ["A", "Q"]
    assert set(report["canonical_territories"]) >= {"AUS", "DEU", "DNK", "FRA", "USA"}
    assert report["provider_period_mapping_count_by_source"] == {"EUROSTAT_NAMQ_GDP": 2, "OECD_NAAG": 2, "WDI": 2}
    assert report["provider_territory_mapping_count_by_source"] == {"EUROSTAT_NAMQ_GDP": 2, "OECD_NAAG": 2, "WDI": 2}
    assert report["lineage_events_by_source"] == {"EUROSTAT_NAMQ_GDP": 2, "OECD_NAAG": 2, "WDI": 2}
    assert report["quality_checks_by_source"] == {"EUROSTAT_NAMQ_GDP": 4, "OECD_NAAG": 4, "WDI": 2}
    assert report["failing_quality_checks"] == 0
    assert all(status == "pass" for status in report["checks"].values())
    assert json.loads(REPORT_PATH.read_text(encoding="utf-8"))["fact_rows_total"] == 20
