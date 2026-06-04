from __future__ import annotations

import json
from pathlib import Path

from macroforge import db_helpers


def test_sql_and_jsonb_literals_preserve_current_loader_rendering():
    assert db_helpers.sql_literal(None) == "NULL"
    assert db_helpers.sql_literal(True) == "TRUE"
    assert db_helpers.sql_literal(False) == "FALSE"
    assert db_helpers.sql_literal(42) == "42"
    assert db_helpers.sql_literal(3.5) == "3.5"
    assert db_helpers.sql_literal("O'Brien") == "'O''Brien'"
    assert db_helpers.jsonb_literal({"b": 2, "a": "O'Brien"}) == "'{\"a\": \"O''Brien\", \"b\": 2}'::jsonb"


def test_write_json_report_adds_stable_defaults_and_sorted_pretty_file(tmp_path):
    report_path = tmp_path / "nested" / "report.json"

    report = db_helpers.write_json_report(
        report_path,
        {"fact_rows": 8, "staging_rows": 8},
        default_task="TASK-017",
        default_status="succeeded",
    )

    assert report == {
        "fact_rows": 8,
        "staging_rows": 8,
        "status": "succeeded",
        "task": "TASK-017",
    }
    assert json.loads(report_path.read_text(encoding="utf-8")) == report
    assert report_path.read_text(encoding="utf-8").endswith("\n")


def test_parse_pipe_counts_supports_source_specific_count_reports():
    parsed = db_helpers.parse_pipe_counts(
        "8|8|2|4|1|USD_EXC,USD_PPP",
        [
            ("staging_rows", int),
            ("fact_rows", int),
            ("lineage_events", int),
            ("quality_checks", int),
            ("attribute_sets", int),
            ("unit_codes", lambda value: value.split(",") if value else []),
        ],
    )

    assert parsed == {
        "staging_rows": 8,
        "fact_rows": 8,
        "lineage_events": 2,
        "quality_checks": 4,
        "attribute_sets": 1,
        "unit_codes": ["USD_EXC", "USD_PPP"],
    }


def test_psql_helpers_use_on_error_stop_and_scalar_output(monkeypatch, tmp_path):
    calls = []

    def fake_run(command, check, capture_output, text):
        calls.append(command)
        if "-At" in command:
            class Result:
                stdout = "7\n"

            return Result()

        sql_path = Path(command[-1])
        assert sql_path.read_text(encoding="utf-8") == "SELECT 1;"

        class Result:
            stdout = ""

        return Result()

    monkeypatch.setattr(db_helpers.subprocess, "run", fake_run)

    db_helpers.run_psql_file("scratch_db", "SELECT 1;")
    scalar = db_helpers.psql_scalar("scratch_db", "SELECT 7")
    integer = db_helpers.psql_int("scratch_db", "SELECT 7")

    assert scalar == "7"
    assert integer == 7
    assert calls[0][:6] == ["psql", "-v", "ON_ERROR_STOP=1", "-d", "scratch_db", "-f"]
    assert calls[1] == ["psql", "-v", "ON_ERROR_STOP=1", "-d", "scratch_db", "-At", "-c", "SELECT 7"]
    assert calls[2] == ["psql", "-v", "ON_ERROR_STOP=1", "-d", "scratch_db", "-At", "-c", "SELECT 7"]
    assert not Path(calls[0][-1]).exists()
