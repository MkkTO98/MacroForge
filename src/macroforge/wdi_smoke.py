from __future__ import annotations

import argparse
import json
import subprocess
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

LIVE_DATABASE_NAME = "macro"
DEFAULT_DB_PREFIX = "macroforge_wdi_smoke"
DEFAULT_EXPECTED_ROWS = 8


class CommandRunner(Protocol):
    def run(self, command: list[str], **kwargs) -> None: ...
    def dropdb(self, db_name: str) -> None: ...


class SubprocessRunner:
    def run(self, command: list[str], **kwargs) -> None:
        subprocess.run(command, check=True, text=True, **kwargs)

    def dropdb(self, db_name: str) -> None:
        subprocess.run(["dropdb", "--if-exists", db_name], check=False, capture_output=True, text=True)


@dataclass(frozen=True)
class SmokePlan:
    project_root: Path
    db_name: str
    run_key: str
    migration_path: Path
    normalized_path: Path
    load_report_path: Path
    validation_json_path: Path
    validation_markdown_path: Path
    expected_rows: int = DEFAULT_EXPECTED_ROWS


def _default_db_name() -> str:
    return f"{DEFAULT_DB_PREFIX}_{uuid.uuid4().hex[:12]}"


def _refuse_live_database(db_name: str) -> None:
    if db_name == LIVE_DATABASE_NAME:
        raise ValueError("Refusing to run isolated WDI smoke against live `macro` database")


def build_smoke_plan(
    *,
    project_root: str | Path = ".",
    db_name: str | None = None,
    run_key: str | None = None,
    expected_rows: int = DEFAULT_EXPECTED_ROWS,
) -> SmokePlan:
    project = Path(project_root).resolve()
    chosen_db = db_name or _default_db_name()
    _refuse_live_database(chosen_db)
    suffix = chosen_db.removeprefix(f"{DEFAULT_DB_PREFIX}_")
    chosen_run_key = run_key or f"wdi-smoke-rerun-{suffix}"
    return SmokePlan(
        project_root=project,
        db_name=chosen_db,
        run_key=chosen_run_key,
        migration_path=project / "db" / "migrations" / "001_v0_schema_foundation.sql",
        normalized_path=project / "data" / "metadata" / "wdi" / "wdi-smoke-normalized.json",
        load_report_path=project / "artifacts" / "reports" / "wdi-load-smoke-20260602.json",
        validation_json_path=project / "artifacts" / "reports" / "wdi-validation-smoke-20260602.json",
        validation_markdown_path=project / "artifacts" / "reports" / "wdi-validation-smoke-20260602.md",
        expected_rows=expected_rows,
    )


def _python_module_command(module: str, *args: str) -> list[str]:
    return ["python3", "-m", module, *args]


def run_isolated_smoke(
    *,
    project_root: str | Path = ".",
    db_name: str | None = None,
    run_key: str | None = None,
    expected_rows: int = DEFAULT_EXPECTED_ROWS,
    runner: CommandRunner | None = None,
) -> dict[str, object]:
    plan = build_smoke_plan(project_root=project_root, db_name=db_name, run_key=run_key, expected_rows=expected_rows)
    command_runner = runner or SubprocessRunner()
    cwd = str(plan.project_root)
    loader_command = _python_module_command(
        "macroforge.wdi_loader",
        "--db",
        plan.db_name,
        "--normalized",
        str(plan.normalized_path),
        "--run-key",
        plan.run_key,
        "--report",
        str(plan.load_report_path),
    )
    validation_command = _python_module_command(
        "macroforge.wdi_validation",
        "--db",
        plan.db_name,
        "--expected-rows",
        str(plan.expected_rows),
        "--json-report",
        str(plan.validation_json_path),
        "--markdown-report",
        str(plan.validation_markdown_path),
    )

    try:
        command_runner.run(["createdb", plan.db_name], cwd=cwd)
        command_runner.run(["psql", "-v", "ON_ERROR_STOP=1", "-d", plan.db_name, "-f", str(plan.migration_path)], cwd=cwd)
        command_runner.run(loader_command, cwd=cwd)
        command_runner.run(loader_command, cwd=cwd)
        command_runner.run(validation_command, cwd=cwd)
    finally:
        command_runner.dropdb(plan.db_name)

    return {
        "status": "succeeded",
        "database": plan.db_name,
        "run_key": plan.run_key,
        "loader_runs": 2,
        "expected_rows": plan.expected_rows,
        "validation_report": str(plan.validation_json_path),
        "cleanup": "dropdb --if-exists executed",
    }


def write_smoke_run_report(path: str | Path, report: dict[str, object]) -> None:
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run MacroForge WDI smoke path in an isolated PostgreSQL database")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--db", default=None, help="Isolated database name. Defaults to a unique macroforge_wdi_smoke_* database. The live `macro` database is refused.")
    parser.add_argument("--run-key", default=None)
    parser.add_argument("--expected-rows", type=int, default=DEFAULT_EXPECTED_ROWS)
    parser.add_argument("--report", default="artifacts/reports/wdi-isolated-smoke-rerun-20260603.json")
    args = parser.parse_args(argv)

    report = run_isolated_smoke(
        project_root=args.project_root,
        db_name=args.db,
        run_key=args.run_key,
        expected_rows=args.expected_rows,
    )
    write_smoke_run_report(Path(args.project_root) / args.report, report)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
