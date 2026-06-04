from __future__ import annotations

import json
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Callable, Iterable, TypeVar

T = TypeVar("T")


def sql_literal(value: Any) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    if isinstance(value, (int, float)):
        return str(value)
    text = str(value).replace("'", "''")
    return f"'{text}'"


def jsonb_literal(value: Any) -> str:
    return sql_literal(json.dumps(value, sort_keys=True)) + "::jsonb"


def run_psql_file(db_name: str, sql: str) -> None:
    with tempfile.NamedTemporaryFile("w", suffix=".sql", encoding="utf-8", delete=False) as handle:
        handle.write(sql)
        temp_path = Path(handle.name)
    try:
        subprocess.run(
            ["psql", "-v", "ON_ERROR_STOP=1", "-d", db_name, "-f", str(temp_path)],
            check=True,
            capture_output=True,
            text=True,
        )
    finally:
        temp_path.unlink(missing_ok=True)


def psql_scalar(db_name: str, sql: str) -> str:
    result = subprocess.run(
        ["psql", "-v", "ON_ERROR_STOP=1", "-d", db_name, "-At", "-c", sql],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def psql_int(db_name: str, sql: str) -> int:
    return int(psql_scalar(db_name, sql) or "0")


def parse_pipe_counts(output: str, fields: Iterable[tuple[str, Callable[[str], T]]]) -> dict[str, Any]:
    values = output.split("|")
    field_list = list(fields)
    if len(values) != len(field_list):
        raise ValueError(f"Expected {len(field_list)} pipe-delimited values, got {len(values)}")
    return {name: parser(value) for value, (name, parser) in zip(values, field_list)}


def write_json_report(
    path: str | Path,
    payload: dict[str, Any],
    *,
    default_task: str,
    default_status: str = "succeeded",
) -> dict[str, Any]:
    report = dict(payload)
    report.setdefault("task", default_task)
    report.setdefault("status", default_status)
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report
