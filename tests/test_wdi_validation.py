from __future__ import annotations

import json
import shutil
import subprocess
import uuid
from pathlib import Path

from macroforge import wdi_loader, wdi_validation

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MIGRATION = PROJECT_ROOT / "db" / "migrations" / "001_v0_schema_foundation.sql"
NORMALIZED = PROJECT_ROOT / "data" / "metadata" / "wdi" / "wdi-smoke-normalized.json"


def _postgres_available() -> bool:
    return all(shutil.which(cmd) for cmd in ["createdb", "dropdb", "psql"])


def test_wdi_validation_report_passes_after_loader_rerun(tmp_path):
    if not _postgres_available():
        return

    db_name = f"macroforge_validation_test_{uuid.uuid4().hex[:12]}"
    try:
        subprocess.run(["createdb", db_name], check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as exc:
        if "could not connect" in exc.stderr.lower() or "role" in exc.stderr.lower():
            return
        raise

    try:
        subprocess.run(
            ["psql", "-v", "ON_ERROR_STOP=1", "-d", db_name, "-f", str(MIGRATION)],
            check=True,
            capture_output=True,
            text=True,
        )
        wdi_loader.load_wdi_smoke_to_postgres(db_name, NORMALIZED, run_key="task-007-validation-test")
        wdi_loader.load_wdi_smoke_to_postgres(db_name, NORMALIZED, run_key="task-007-validation-test")

        json_report = tmp_path / "wdi-validation.json"
        md_report = tmp_path / "wdi-validation.md"
        report = wdi_validation.write_validation_reports(db_name, json_report, md_report, expected_rows=8)

        assert report["status"] == "pass"
        assert all(check["status"] == "pass" for check in report["checks"])
        assert {check["name"] for check in report["checks"]} >= {
            "staging_expected_rows",
            "fact_expected_rows",
            "no_duplicate_fact_grain",
            "quality_checks_pass",
            "lineage_events_present",
        }
        assert json.loads(json_report.read_text(encoding="utf-8"))["status"] == "pass"
        assert "WDI validation report" in md_report.read_text(encoding="utf-8")
    finally:
        subprocess.run(["dropdb", "--if-exists", db_name], capture_output=True, text=True)
