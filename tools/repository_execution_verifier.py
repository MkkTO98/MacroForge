#!/usr/bin/env python3
"""Repository execution verification helper.

This is deliberately an execution tool, not a planning framework. It packages the
repeated post-load checks observed across WDI repository campaigns into one
repeatable command:

- artifact existence and SHA-256 capture;
- normalized-campaign shape checks;
- provider exclusion classification presence;
- JSON report parse checks;
- optional PostgreSQL run-scoped staging/fact/lineage/quality checks;
- optional WDI duplicate canonical-key check.

The helper is intentionally narrow: it validates evidence and load consistency for
an already selected/executed campaign. It does not choose domains, providers, or
campaigns.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class CommandResult:
    command: list[str]
    stdout: str


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def parse_pipe_row(row: str) -> list[str]:
    row = row.strip()
    return [] if not row else row.split("|")


def run_psql(database: str, sql: str) -> CommandResult:
    command = ["psql", "-d", database, "-At", "-F", "|", "-c", sql]
    completed = subprocess.run(command, check=True, text=True, capture_output=True)
    return CommandResult(command=command, stdout=completed.stdout.strip())


def count_valid_json_reports(report_glob: str) -> dict[str, Any]:
    pattern_path = Path(report_glob)
    if pattern_path.is_absolute():
        paths = sorted(pattern_path.parent.glob(pattern_path.name))
    else:
        paths = sorted(Path().glob(report_glob))
    parsed: list[str] = []
    failures: list[dict[str, str]] = []
    for path in paths:
        try:
            load_json(path)
            parsed.append(str(path))
        except Exception as exc:  # pragma: no cover - exact parser exception not important
            failures.append({"path": str(path), "error": str(exc)})
    return {"glob": report_glob, "valid_count": len(parsed), "valid_paths": parsed, "failures": failures}


def summarize_normalized_campaign(normalized: dict[str, Any]) -> dict[str, Any]:
    evidence_manifest = normalized.get("evidence_manifest") or []
    excluded = normalized.get("excluded_indicators") or []
    unclassified_exclusions = []
    for entry in evidence_manifest:
        if not isinstance(entry, dict):
            continue
        classification = entry.get("classification")
        indicator = entry.get("indicator")
        if classification != "compatible" and not entry.get("provider_evidence_category"):
            unclassified_exclusions.append(indicator)

    return {
        "task": normalized.get("task"),
        "campaign": normalized.get("campaign"),
        "confidence_cell": (normalized.get("operational_scope") or {}).get("confidence_cell"),
        "candidate_count": (normalized.get("operational_scope") or {}).get("candidate_count"),
        "indicator_count": normalized.get("indicator_count"),
        "excluded_count": len(excluded),
        "row_count": normalized.get("row_count"),
        "observed_value_count": normalized.get("observed_value_count"),
        "missing_value_count": normalized.get("missing_value_count"),
        "country_count": normalized.get("country_count"),
        "date_range": normalized.get("date_range"),
        "support_bundle": normalized.get("support_bundle"),
        "evidence_manifest_count": len(evidence_manifest),
        "unclassified_exclusions": sorted(x for x in unclassified_exclusions if x),
    }


def postgres_repository_counts(database: str) -> dict[str, int]:
    sql = """
SELECT
  (SELECT count(*) FROM staging.wdi_observation),
  (SELECT count(*) FROM curated.fact_observation),
  (SELECT count(*) FROM curated.dim_indicator),
  (SELECT count(*) FROM curated.dim_territory),
  (SELECT count(*) FROM curated.dim_period),
  (SELECT count(*) FROM meta.pipeline_run),
  (SELECT count(*) FROM meta.lineage_event),
  (SELECT count(*) FROM meta.quality_check);
"""
    fields = parse_pipe_row(run_psql(database, sql).stdout)
    keys = [
        "staging_wdi_observation_rows",
        "curated_fact_observation_rows",
        "curated_dim_indicator_rows",
        "curated_dim_territory_rows",
        "curated_dim_period_rows",
        "meta_pipeline_run_rows",
        "meta_lineage_event_rows",
        "meta_quality_check_rows",
    ]
    return dict(zip(keys, [int(value) for value in fields], strict=True))


def postgres_run_scope(database: str, run_key: str) -> dict[str, Any]:
    sql = f"""
WITH run AS (SELECT pipeline_run_id FROM meta.pipeline_run WHERE run_key = '{run_key}')
SELECT
  (SELECT count(*) FROM staging.wdi_observation s JOIN run USING (pipeline_run_id)),
  (SELECT count(*) FROM curated.fact_observation f JOIN run USING (pipeline_run_id)),
  (SELECT count(DISTINCT indicator_id) FROM curated.fact_observation f JOIN run USING (pipeline_run_id)),
  (SELECT count(DISTINCT territory_id) FROM curated.fact_observation f JOIN run USING (pipeline_run_id)),
  (SELECT min(p.period_label)||':'||max(p.period_label)
     FROM curated.fact_observation f JOIN curated.dim_period p USING(period_id) JOIN run USING (pipeline_run_id)),
  (SELECT count(*) FROM meta.quality_check q JOIN run USING (pipeline_run_id) WHERE check_status='pass'),
  (SELECT count(*) FROM meta.lineage_event l JOIN run USING (pipeline_run_id));
"""
    fields = parse_pipe_row(run_psql(database, sql).stdout)
    keys = [
        "run_scoped_staging_rows",
        "run_scoped_curated_facts",
        "run_scoped_indicators",
        "run_scoped_territories",
        "run_scoped_period_range",
        "run_scoped_passing_quality_checks",
        "run_scoped_lineage_events",
    ]
    values: list[Any] = []
    for index, value in enumerate(fields):
        values.append(value if index == 4 else int(value))
    return dict(zip(keys, values, strict=True))


def postgres_wdi_duplicate_key_groups(database: str) -> int:
    sql = """
WITH src AS (SELECT source_id FROM meta.source WHERE source_code='WDI')
SELECT count(*) FROM (
  SELECT source_id, indicator_id, territory_id, period_id, unit_id, attribute_set_id, as_of_date, count(*)
  FROM curated.fact_observation
  WHERE source_id=(SELECT source_id FROM src)
  GROUP BY 1,2,3,4,5,6,7
  HAVING count(*) > 1
) d;
"""
    return int(run_psql(database, sql).stdout)


def verify(args: argparse.Namespace) -> dict[str, Any]:
    normalized_path = Path(args.normalized)
    raw_path = Path(args.raw) if args.raw else None
    task_path = Path(args.task_artifact) if args.task_artifact else None

    normalized = load_json(normalized_path)
    artifact_paths = [normalized_path]
    if raw_path:
        artifact_paths.append(raw_path)
    if task_path:
        artifact_paths.append(task_path)

    missing = [str(path) for path in artifact_paths if not path.exists()]
    if missing:
        raise FileNotFoundError(f"missing required artifacts: {missing}")

    result: dict[str, Any] = {
        "status": "pass",
        "task": args.task_id,
        "normalized_artifact": str(normalized_path),
        "raw_artifact": str(raw_path) if raw_path else None,
        "task_artifact": str(task_path) if task_path else None,
        "artifact_sha256": {str(path): sha256_file(path) for path in artifact_paths},
        "normalized_summary": summarize_normalized_campaign(normalized),
    }

    if args.report_glob:
        result["json_reports"] = count_valid_json_reports(args.report_glob)
        if result["json_reports"]["failures"]:
            result["status"] = "fail"

    if args.database:
        result["postgres_repository_counts"] = postgres_repository_counts(args.database)
        if args.run_key:
            result["postgres_run_scope"] = postgres_run_scope(args.database, args.run_key)
        if args.check_wdi_duplicates:
            result["wdi_duplicate_canonical_key_groups"] = postgres_wdi_duplicate_key_groups(args.database)
            if result["wdi_duplicate_canonical_key_groups"] != 0:
                result["status"] = "fail"

    unclassified = result["normalized_summary"].get("unclassified_exclusions") or []
    if unclassified:
        result["status"] = "fail"

    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Verify a completed repository execution campaign.")
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--normalized", required=True)
    parser.add_argument("--raw")
    parser.add_argument("--task-artifact")
    parser.add_argument("--report-glob")
    parser.add_argument("--database")
    parser.add_argument("--run-key")
    parser.add_argument("--check-wdi-duplicates", action="store_true")
    parser.add_argument("--output", help="Optional JSON output path.")
    return parser


def main() -> None:
    args = build_parser().parse_args()
    result = verify(args)
    output = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        Path(args.output).write_text(output + "\n", encoding="utf-8")
    print(output)
    if result["status"] != "pass":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
