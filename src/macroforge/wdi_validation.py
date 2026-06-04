from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from macroforge.db_helpers import psql_int


def _int_scalar(db_name: str, sql: str) -> int:
    return psql_int(db_name, sql)


def validate_wdi_smoke(db_name: str, *, expected_rows: int = 8) -> dict[str, Any]:
    staging_rows = _int_scalar(db_name, "SELECT count(*) FROM staging.wdi_observation")
    fact_rows = _int_scalar(db_name, "SELECT count(*) FROM curated.fact_observation")
    duplicate_fact_grains = _int_scalar(
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
    failing_quality_checks = _int_scalar(db_name, "SELECT count(*) FROM meta.quality_check WHERE check_status <> 'pass'")
    lineage_events = _int_scalar(db_name, "SELECT count(*) FROM meta.lineage_event")
    required_tables_missing = _int_scalar(
        db_name,
        """
        WITH required(table_name, regclass_value) AS (
          VALUES
            ('meta.source', to_regclass('meta.source')),
            ('meta.dataset_release', to_regclass('meta.dataset_release')),
            ('meta.pipeline_run', to_regclass('meta.pipeline_run')),
            ('meta.lineage_event', to_regclass('meta.lineage_event')),
            ('meta.quality_check', to_regclass('meta.quality_check')),
            ('staging.wdi_observation', to_regclass('staging.wdi_observation')),
            ('curated.dim_indicator', to_regclass('curated.dim_indicator')),
            ('curated.dim_territory', to_regclass('curated.dim_territory')),
            ('curated.dim_period', to_regclass('curated.dim_period')),
            ('curated.dim_unit', to_regclass('curated.dim_unit')),
            ('curated.dim_attribute_set', to_regclass('curated.dim_attribute_set')),
            ('curated.fact_observation', to_regclass('curated.fact_observation'))
        )
        SELECT count(*) FROM required WHERE regclass_value IS NULL
        """,
    )

    checks = [
        {
            "name": "required_tables_exist",
            "status": "pass" if required_tables_missing == 0 else "fail",
            "observed": required_tables_missing,
            "expected": 0,
        },
        {
            "name": "staging_expected_rows",
            "status": "pass" if staging_rows == expected_rows else "fail",
            "observed": staging_rows,
            "expected": expected_rows,
        },
        {
            "name": "fact_expected_rows",
            "status": "pass" if fact_rows == expected_rows else "fail",
            "observed": fact_rows,
            "expected": expected_rows,
        },
        {
            "name": "no_duplicate_fact_grain",
            "status": "pass" if duplicate_fact_grains == 0 else "fail",
            "observed": duplicate_fact_grains,
            "expected": 0,
        },
        {
            "name": "quality_checks_pass",
            "status": "pass" if failing_quality_checks == 0 else "fail",
            "observed": failing_quality_checks,
            "expected": 0,
        },
        {
            "name": "lineage_events_present",
            "status": "pass" if lineage_events >= 2 else "fail",
            "observed": lineage_events,
            "expected": ">=2",
        },
    ]
    return {
        "task": "TASK-007",
        "database": db_name,
        "expected_rows": expected_rows,
        "status": "pass" if all(check["status"] == "pass" for check in checks) else "fail",
        "checks": checks,
    }


def render_markdown(report: dict[str, Any]) -> str:
    rows = "\n".join(
        f"| {check['name']} | {check['status']} | {check['observed']} | {check['expected']} |"
        for check in report["checks"]
    )
    return f"""# WDI validation report

- Task: {report['task']}
- Database: `{report['database']}`
- Overall status: {report['status']}
- Expected rows: {report['expected_rows']}

| check | status | observed | expected |
| --- | --- | ---: | ---: |
{rows}
"""


def write_validation_reports(db_name: str, json_path: str | Path, markdown_path: str | Path, *, expected_rows: int = 8) -> dict[str, Any]:
    report = validate_wdi_smoke(db_name, expected_rows=expected_rows)
    json_output = Path(json_path)
    markdown_output = Path(markdown_path)
    json_output.parent.mkdir(parents=True, exist_ok=True)
    markdown_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_output.write_text(render_markdown(report), encoding="utf-8")
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate MacroForge WDI smoke database state")
    parser.add_argument("--db", required=True)
    parser.add_argument("--expected-rows", type=int, default=8)
    parser.add_argument("--json-report", default="artifacts/reports/wdi-validation-smoke-20260602.json")
    parser.add_argument("--markdown-report", default="artifacts/reports/wdi-validation-smoke-20260602.md")
    args = parser.parse_args(argv)

    report = write_validation_reports(args.db, args.json_report, args.markdown_report, expected_rows=args.expected_rows)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
