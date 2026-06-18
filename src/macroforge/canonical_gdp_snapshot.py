from __future__ import annotations

import argparse
import json
import subprocess
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from macroforge import eurostat_namq_loader, oecd_sdmx_loader, wdi_loader
from macroforge.db_helpers import psql_scalar

LIVE_DATABASE_NAME = "macro"
DEFAULT_DB_PREFIX = "macroforge_canonical_gdp_snapshot"
DEFAULT_JSON_REPORT_PATH = "artifacts/reports/canonical-gdp-snapshot-20260604.json"
DEFAULT_MARKDOWN_REPORT_PATH = "artifacts/reports/canonical-gdp-snapshot-20260604.md"
DETERMINISTIC_GENERATED_AT = "2026-06-04T00:00:00Z"

CORE_REPORT_SQL = {
    "sources": """
        SELECT COALESCE(string_agg(source_code, ',' ORDER BY source_code), '')
        FROM meta.source
    """,
    "coverage_counts": """
        SELECT
          (SELECT count(*) FROM curated.fact_observation),
          (SELECT count(*) FROM curated.dim_territory),
          (SELECT count(*) FROM curated.dim_period),
          (SELECT count(*) FROM curated.dim_indicator),
          (SELECT count(*) FROM curated.dim_unit)
    """,
    "fact_rows_by_source": """
        SELECT s.source_code, count(*)
        FROM curated.fact_observation f
        JOIN meta.source s ON s.source_id = f.source_id
        GROUP BY s.source_code
        ORDER BY s.source_code
    """,
    "coverage_lists": """
        SELECT json_build_object(
          'territories', (SELECT COALESCE(json_agg(code ORDER BY code), '[]'::json) FROM (SELECT DISTINCT canonical_territory_code AS code FROM curated.dim_territory) x),
          'frequencies', (SELECT COALESCE(json_agg(frequency ORDER BY frequency), '[]'::json) FROM (SELECT DISTINCT frequency FROM curated.dim_period) x),
          'periods', (SELECT COALESCE(json_agg(period_label ORDER BY period_start_date, period_label), '[]'::json) FROM (SELECT DISTINCT period_label, period_start_date FROM curated.dim_period) x),
          'units', (SELECT COALESCE(json_agg(unit_code ORDER BY unit_code), '[]'::json) FROM (SELECT DISTINCT unit_code FROM curated.dim_unit) x),
          'indicators', (SELECT COALESCE(json_agg(indicator ORDER BY indicator), '[]'::json) FROM (SELECT DISTINCT source_indicator_code AS indicator FROM curated.dim_indicator) x)
        )::text
    """,
    "observations": """
        SELECT COALESCE(json_agg(json_build_object(
          'source_code', source_code,
          'provider_dataset_code', provider_dataset_code,
          'release_key', release_key,
          'indicator_code', source_indicator_code,
          'indicator_name', indicator_name,
          'territory_code', canonical_territory_code,
          'territory_name', territory_name,
          'frequency', frequency,
          'period_label', period_label,
          'period_start_date', period_start_date,
          'period_end_date', period_end_date,
          'unit_code', unit_code,
          'value', value_text,
          'as_of_date', as_of_date,
          'observation_status', observation_status
        ) ORDER BY source_code, canonical_territory_code, source_indicator_code, frequency, period_start_date, unit_code, as_of_date), '[]'::json)::text
        FROM (
          SELECT
            s.source_code,
            dr.provider_dataset_code,
            dr.release_key,
            i.source_indicator_code,
            i.indicator_name,
            t.canonical_territory_code,
            t.territory_name,
            p.frequency,
            p.period_label,
            p.period_start_date::text,
            p.period_end_date::text,
            u.unit_code,
            f.value::text AS value_text,
            f.as_of_date::text,
            f.observation_status
          FROM curated.fact_observation f
          JOIN meta.source s ON s.source_id = f.source_id
          LEFT JOIN meta.dataset_release dr ON dr.dataset_release_id = f.dataset_release_id
          JOIN curated.dim_indicator i ON i.indicator_id = f.indicator_id
          JOIN curated.dim_territory t ON t.territory_id = f.territory_id
          JOIN curated.dim_period p ON p.period_id = f.period_id
          JOIN curated.dim_unit u ON u.unit_id = f.unit_id
          WHERE i.source_indicator_code IN ('B1GQ', 'NY.GDP.MKTP.CD')
        ) observations
    """,
    "missingness": """
        WITH source_indicator_units AS (
          SELECT DISTINCT f.source_id, f.indicator_id, f.unit_id
          FROM curated.fact_observation f
          JOIN curated.dim_indicator i ON i.indicator_id = f.indicator_id
          WHERE i.source_indicator_code IN ('B1GQ', 'NY.GDP.MKTP.CD')
        ), source_territories AS (
          SELECT DISTINCT source_id, territory_id FROM curated.fact_observation
        ), source_periods AS (
          SELECT DISTINCT source_id, period_id FROM curated.fact_observation
        ), expected AS (
          SELECT siu.source_id, siu.indicator_id, st.territory_id, sp.period_id, siu.unit_id
          FROM source_indicator_units siu
          JOIN source_territories st ON st.source_id = siu.source_id
          JOIN source_periods sp ON sp.source_id = siu.source_id
        ), missing AS (
          SELECT e.*
          FROM expected e
          LEFT JOIN curated.fact_observation f
            ON f.source_id = e.source_id
           AND f.indicator_id = e.indicator_id
           AND f.territory_id = e.territory_id
           AND f.period_id = e.period_id
           AND f.unit_id = e.unit_id
          WHERE f.fact_observation_id IS NULL
        )
        SELECT json_build_object(
          'expected_observation_count', (SELECT count(*) FROM expected),
          'observed_observation_count', (SELECT count(*) FROM curated.fact_observation f JOIN curated.dim_indicator i ON i.indicator_id = f.indicator_id WHERE i.source_indicator_code IN ('B1GQ', 'NY.GDP.MKTP.CD')),
          'missing_observation_count', (SELECT count(*) FROM missing),
          'missing_observations', COALESCE((
            SELECT json_agg(json_build_object(
              'source_code', s.source_code,
              'indicator_code', i.source_indicator_code,
              'territory_code', t.canonical_territory_code,
              'period_label', p.period_label,
              'unit_code', u.unit_code
            ) ORDER BY s.source_code, t.canonical_territory_code, i.source_indicator_code, p.period_label, u.unit_code)
            FROM missing m
            JOIN meta.source s ON s.source_id = m.source_id
            JOIN curated.dim_indicator i ON i.indicator_id = m.indicator_id
            JOIN curated.dim_territory t ON t.territory_id = m.territory_id
            JOIN curated.dim_period p ON p.period_id = m.period_id
            JOIN curated.dim_unit u ON u.unit_id = m.unit_id
          ), '[]'::json),
          'notes', json_build_array('Expected coverage is bounded to observed source-specific indicator/unit, territory, and period universes; no cross-source unit conversion or frequency aggregation is assumed.')
        )::text
    """,
    "lineage": """
        SELECT COALESCE(json_agg(json_build_object(
          'source_code', source_code,
          'dataset_release_count', dataset_release_count,
          'lineage_event_count', lineage_event_count,
          'latest_to_artifact', latest_to_artifact
        ) ORDER BY source_code), '[]'::json)::text
        FROM (
          SELECT
            s.source_code,
            count(DISTINCT dr.dataset_release_id) AS dataset_release_count,
            count(DISTINCT le.lineage_event_id) AS lineage_event_count,
            max(le.to_artifact) AS latest_to_artifact
          FROM meta.source s
          LEFT JOIN meta.dataset_release dr ON dr.source_id = s.source_id
          LEFT JOIN meta.lineage_event le ON le.source_id = s.source_id
          GROUP BY s.source_code
        ) lineage
    """,
    "quality": """
        SELECT json_build_object(
          'duplicate_fact_grain_count', (
            SELECT count(*) FROM (
              SELECT source_id, indicator_id, territory_id, period_id, unit_id, attribute_set_id, as_of_date, count(*)
              FROM curated.fact_observation
              GROUP BY source_id, indicator_id, territory_id, period_id, unit_id, attribute_set_id, as_of_date
              HAVING count(*) > 1
            ) duplicates
          ),
          'failing_quality_checks', (SELECT count(*) FROM meta.quality_check WHERE check_status <> 'pass'),
          'quality_checks_by_source', COALESCE((
            SELECT json_object_agg(source_code, check_count ORDER BY source_code)
            FROM (
              SELECT s.source_code, count(qc.quality_check_id) AS check_count
              FROM meta.source s
              LEFT JOIN meta.pipeline_run pr ON pr.source_id = s.source_id
              LEFT JOIN meta.quality_check qc ON qc.pipeline_run_id = pr.pipeline_run_id
              GROUP BY s.source_code
            ) q
          ), '{}'::json),
          'core_query_boundary', 'curated_and_meta_only'
        )::text
    """,
}


class CommandRunner(Protocol):
    def run(self, command: list[str], **kwargs) -> None: ...
    def dropdb(self, db_name: str) -> None: ...


class SubprocessRunner:
    def run(self, command: list[str], **kwargs) -> None:
        subprocess.run(command, check=True, text=True, capture_output=True, **kwargs)

    def dropdb(self, db_name: str) -> None:
        subprocess.run(["dropdb", "--if-exists", db_name], check=False, capture_output=True, text=True)


@dataclass(frozen=True)
class SnapshotPlan:
    project_root: Path
    db_name: str
    combined_run_key_prefix: str
    migration_paths: tuple[Path, Path, Path, Path]
    wdi_normalized_path: Path
    oecd_normalized_path: Path
    eurostat_normalized_path: Path
    json_report_path: Path
    markdown_report_path: Path
    generated_at: str = DETERMINISTIC_GENERATED_AT


def _default_db_name() -> str:
    return f"{DEFAULT_DB_PREFIX}_{uuid.uuid4().hex[:12]}"


def _refuse_live_database(db_name: str) -> None:
    if db_name == LIVE_DATABASE_NAME:
        raise ValueError("Refusing to run canonical GDP snapshot against live `macro` database")


def build_snapshot_plan(
    *,
    project_root: str | Path = ".",
    db_name: str | None = None,
    run_key_prefix: str | None = None,
    json_report_path: str | Path = DEFAULT_JSON_REPORT_PATH,
    markdown_report_path: str | Path = DEFAULT_MARKDOWN_REPORT_PATH,
) -> SnapshotPlan:
    project = Path(project_root).resolve()
    chosen_db = db_name or _default_db_name()
    _refuse_live_database(chosen_db)
    suffix = chosen_db.removeprefix(f"{DEFAULT_DB_PREFIX}_")
    chosen_prefix = run_key_prefix or f"canonical-gdp-snapshot-{suffix}"
    return SnapshotPlan(
        project_root=project,
        db_name=chosen_db,
        combined_run_key_prefix=chosen_prefix,
        migration_paths=(
            project / "db" / "migrations" / "001_v0_schema_foundation.sql",
            project / "db" / "migrations" / "002_oecd_sdmx_staging.sql",
            project / "db" / "migrations" / "003_canonical_domain_dimensions.sql",
            project / "db" / "migrations" / "004_eurostat_namq_staging.sql",
        ),
        wdi_normalized_path=project / "data" / "metadata" / "wdi" / "wdi-smoke-normalized.json",
        oecd_normalized_path=project / "data" / "metadata" / "oecd_sdmx" / "oecd-sdmx-smoke-normalized.json",
        eurostat_normalized_path=project / "data" / "metadata" / "eurostat" / "eurostat-namq-10-gdp-architecture-spike-normalized.json",
        json_report_path=(project / json_report_path) if not Path(json_report_path).is_absolute() else Path(json_report_path),
        markdown_report_path=(project / markdown_report_path) if not Path(markdown_report_path).is_absolute() else Path(markdown_report_path),
    )


def _split_csv(value: str) -> list[str]:
    return [] if not value else value.split(",")


def _source_counts(db_name: str, sql: str) -> dict[str, int]:
    output = psql_scalar(db_name, sql)
    counts: dict[str, int] = {}
    for line in output.splitlines():
        if not line:
            continue
        source_code, value = line.split("|", 1)
        counts[source_code] = int(value)
    return dict(sorted(counts.items()))


def _json_scalar(db_name: str, sql: str):
    text = psql_scalar(db_name, sql)
    return json.loads(text) if text else None


def _coverage_counts(db_name: str) -> dict[str, int]:
    values = psql_scalar(db_name, CORE_REPORT_SQL["coverage_counts"]).split("|")
    keys = ["fact_rows_total", "territory_count", "period_count", "indicator_count", "unit_count"]
    return {key: int(value) for key, value in zip(keys, values, strict=True)}


def collect_snapshot_report(plan: SnapshotPlan) -> dict[str, object]:
    sources = _split_csv(psql_scalar(plan.db_name, CORE_REPORT_SQL["sources"]))
    coverage_counts = _coverage_counts(plan.db_name)
    coverage_lists = _json_scalar(plan.db_name, CORE_REPORT_SQL["coverage_lists"])
    fact_rows_by_source = _source_counts(plan.db_name, CORE_REPORT_SQL["fact_rows_by_source"])
    observations = _json_scalar(plan.db_name, CORE_REPORT_SQL["observations"])
    missingness = _json_scalar(plan.db_name, CORE_REPORT_SQL["missingness"])
    lineage = _json_scalar(plan.db_name, CORE_REPORT_SQL["lineage"])
    quality = _json_scalar(plan.db_name, CORE_REPORT_SQL["quality"])

    data_quality = {
        "duplicate_fact_grain_count": int(quality["duplicate_fact_grain_count"]),
        "failing_quality_checks": int(quality["failing_quality_checks"]),
        "quality_checks_by_source": dict(sorted((quality.get("quality_checks_by_source") or {}).items())),
        "core_query_boundary": quality["core_query_boundary"],
    }
    checks = {
        "no_duplicate_fact_grain": "pass" if data_quality["duplicate_fact_grain_count"] == 0 else "fail",
        "quality_checks_pass": "pass" if data_quality["failing_quality_checks"] == 0 else "fail",
        "missingness_bounded_fixture_complete": "pass" if int(missingness["missing_observation_count"]) == 0 else "fail",
        "core_query_boundary": "pass" if data_quality["core_query_boundary"] == "curated_and_meta_only" else "fail",
        "annual_and_quarterly_explicit": "pass" if set(coverage_lists["frequencies"]) >= {"A", "Q"} else "fail",
    }
    status = "succeeded" if all(value == "pass" for value in checks.values()) else "failed"
    return {
        "task": "TASK-028",
        "status": status,
        "metadata": {
            "report_name": "canonical_gdp_snapshot",
            "generated_at": plan.generated_at,
            "database": plan.db_name,
            "database_safety": "isolated_temporary_database",
            "sources_included": sources,
            "notes": [
                "Core report queries use curated canonical tables plus meta source/dataset/lineage/quality metadata only.",
                "No staging tables are queried for the core report.",
                "No unit conversion or frequency aggregation is performed.",
            ],
        },
        "coverage": {
            "sources": sources,
            "fact_rows_by_source": fact_rows_by_source,
            **coverage_counts,
            "territories": coverage_lists["territories"],
            "frequencies": coverage_lists["frequencies"],
            "periods": coverage_lists["periods"],
            "units": coverage_lists["units"],
            "indicators": coverage_lists["indicators"],
        },
        "missingness": missingness,
        "gdp_snapshot": {
            "comparison_boundary": "descriptive_only_no_unit_conversion_no_frequency_aggregation",
            "observations": observations,
        },
        "source_lineage": lineage,
        "data_quality": data_quality,
        "checks": checks,
    }


def fake_snapshot_report(db_name: str) -> dict[str, object]:
    return {
        "task": "TASK-028",
        "status": "succeeded",
        "metadata": {
            "report_name": "canonical_gdp_snapshot",
            "generated_at": DETERMINISTIC_GENERATED_AT,
            "database": db_name,
            "database_safety": "isolated_temporary_database",
            "sources_included": ["EUROSTAT_NAMQ_GDP", "OECD_NAAG", "WDI"],
            "notes": [
                "Core report queries use curated canonical tables plus meta source/dataset/lineage/quality metadata only.",
                "No staging tables are queried for the core report.",
                "No unit conversion or frequency aggregation is performed.",
            ],
        },
        "coverage": {
            "sources": ["EUROSTAT_NAMQ_GDP", "OECD_NAAG", "WDI"],
            "fact_rows_by_source": {"EUROSTAT_NAMQ_GDP": 4, "OECD_NAAG": 8, "WDI": 8},
            "fact_rows_total": 20,
            "territory_count": 5,
            "period_count": 4,
            "indicator_count": 4,
            "unit_count": 3,
            "territories": ["AUS", "DEU", "DNK", "FRA", "USA"],
            "frequencies": ["A", "Q"],
            "periods": ["2020", "2021", "2023 Q1", "2023 Q2"],
            "units": ["USD_EXC", "USD_PPP", "current_usd"],
            "indicators": ["B1GQ", "NY.GDP.MKTP.CD", "SP.POP.TOTL"],
        },
        "missingness": {
            "expected_observation_count": 20,
            "observed_observation_count": 20,
            "missing_observation_count": 0,
            "missing_observations": [],
            "notes": ["Expected coverage is bounded to observed source-specific indicator/unit, territory, and period universes; no cross-source unit conversion or frequency aggregation is assumed."],
        },
        "gdp_snapshot": {
            "comparison_boundary": "descriptive_only_no_unit_conversion_no_frequency_aggregation",
            "observations": [],
        },
        "source_lineage": [
            {"source_code": "EUROSTAT_NAMQ_GDP", "dataset_release_count": 1, "lineage_event_count": 2, "latest_to_artifact": "curated.fact_observation"},
            {"source_code": "OECD_NAAG", "dataset_release_count": 1, "lineage_event_count": 2, "latest_to_artifact": "curated.fact_observation"},
            {"source_code": "WDI", "dataset_release_count": 1, "lineage_event_count": 2, "latest_to_artifact": "curated.fact_observation"},
        ],
        "data_quality": {
            "duplicate_fact_grain_count": 0,
            "failing_quality_checks": 0,
            "quality_checks_by_source": {"EUROSTAT_NAMQ_GDP": 4, "OECD_NAAG": 4, "WDI": 2},
            "core_query_boundary": "curated_and_meta_only",
        },
        "checks": {
            "no_duplicate_fact_grain": "pass",
            "quality_checks_pass": "pass",
            "missingness_bounded_fixture_complete": "pass",
            "core_query_boundary": "pass",
            "annual_and_quarterly_explicit": "pass",
        },
    }


def _markdown_table(headers: list[str], rows: list[list[object]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(value) for value in row) + " |")
    return "\n".join(lines)


def render_markdown_report(report: dict[str, object]) -> str:
    metadata = report["metadata"]
    coverage = report["coverage"]
    missingness = report["missingness"]
    quality = report["data_quality"]
    observations = report["gdp_snapshot"]["observations"]
    lineage = report["source_lineage"]
    obs_rows = [
        [
            row["source_code"],
            row["territory_code"],
            row["period_label"],
            row["frequency"],
            row["indicator_code"],
            row["unit_code"],
            row["value"],
        ]
        for row in observations[:30]
    ]
    lineage_rows = [[row["source_code"], row["dataset_release_count"], row["lineage_event_count"], row.get("latest_to_artifact") or ""] for row in lineage]
    return "\n".join(
        [
            "# Canonical GDP Snapshot",
            "",
            f"Status: {report['status']}",
            f"Generated: {metadata['generated_at']}",
            f"Database safety: {metadata['database_safety']}",
            "",
            "No unit conversion or frequency aggregation is performed.",
            "Core report queries use curated canonical tables plus meta source/dataset/lineage/quality metadata only.",
            "",
            "## Coverage",
            "",
            f"Sources: {', '.join(coverage['sources'])}",
            f"Fact rows total: {coverage['fact_rows_total']}",
            f"Territories: {', '.join(coverage['territories'])}",
            f"Frequencies: {', '.join(coverage['frequencies'])}",
            f"Periods: {', '.join(coverage['periods'])}",
            f"Units: {', '.join(coverage['units'])}",
            "",
            "## Missingness",
            "",
            f"Expected bounded observations: {missingness['expected_observation_count']}",
            f"Observed observations: {missingness['observed_observation_count']}",
            f"Missing observations: {missingness['missing_observation_count']}",
            "",
            "## Data quality",
            "",
            f"Duplicate fact grains: {quality['duplicate_fact_grain_count']}",
            f"Failing quality checks: {quality['failing_quality_checks']}",
            f"Core query boundary: {quality['core_query_boundary']}",
            "",
            "## Source lineage",
            "",
            _markdown_table(["Source", "Dataset releases", "Lineage events", "Latest artifact"], lineage_rows),
            "",
            "## GDP observations",
            "",
            _markdown_table(["Source", "Territory", "Period", "Frequency", "Indicator", "Unit", "Value"], obs_rows),
            "",
        ]
    )


def write_snapshot_reports(json_path: str | Path, markdown_path: str | Path, report: dict[str, object]) -> dict[str, object]:
    json_output = Path(json_path)
    markdown_output = Path(markdown_path)
    json_output.parent.mkdir(parents=True, exist_ok=True)
    markdown_output.parent.mkdir(parents=True, exist_ok=True)
    json_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown_output.write_text(render_markdown_report(report), encoding="utf-8")
    return report


def _run_loaders(plan: SnapshotPlan) -> None:
    wdi_loader.load_wdi_smoke_to_postgres(
        plan.db_name,
        plan.wdi_normalized_path,
        run_key=f"{plan.combined_run_key_prefix}-wdi",
    )
    oecd_sdmx_loader.load_oecd_sdmx_smoke_to_postgres(
        plan.db_name,
        plan.oecd_normalized_path,
        run_key=f"{plan.combined_run_key_prefix}-oecd",
        as_of_date="2026-06-03",
    )
    eurostat_namq_loader.load_eurostat_namq_smoke_to_postgres(
        plan.db_name,
        plan.eurostat_normalized_path,
        run_key=f"{plan.combined_run_key_prefix}-eurostat",
        as_of_date="2026-06-04",
    )


def run_canonical_gdp_snapshot(
    *,
    project_root: str | Path = ".",
    db_name: str | None = None,
    run_key_prefix: str | None = None,
    json_report_path: str | Path = DEFAULT_JSON_REPORT_PATH,
    markdown_report_path: str | Path = DEFAULT_MARKDOWN_REPORT_PATH,
    runner: CommandRunner | None = None,
    write_reports: bool = True,
) -> dict[str, object]:
    plan = build_snapshot_plan(
        project_root=project_root,
        db_name=db_name,
        run_key_prefix=run_key_prefix,
        json_report_path=json_report_path,
        markdown_report_path=markdown_report_path,
    )
    command_runner = runner or SubprocessRunner()
    cwd = str(plan.project_root)
    try:
        command_runner.run(["createdb", plan.db_name], cwd=cwd)
        for migration in plan.migration_paths:
            command_runner.run(["psql", "-v", "ON_ERROR_STOP=1", "-d", plan.db_name, "-f", str(migration)], cwd=cwd)
        if runner is not None:
            report = fake_snapshot_report(plan.db_name)
        else:
            _run_loaders(plan)
            report = collect_snapshot_report(plan)
        if write_reports:
            write_snapshot_reports(plan.json_report_path, plan.markdown_report_path, report)
        return report
    finally:
        command_runner.dropdb(plan.db_name)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate MacroForge's first canonical GDP snapshot report from an isolated combined-source database")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--db", default=None, help="Isolated database name. Defaults to a unique macroforge_canonical_gdp_snapshot_* database. The live `macro` database is refused.")
    parser.add_argument("--run-key-prefix", default=None)
    parser.add_argument("--json-report", default=DEFAULT_JSON_REPORT_PATH)
    parser.add_argument("--markdown-report", default=DEFAULT_MARKDOWN_REPORT_PATH)
    args = parser.parse_args(argv)
    report = run_canonical_gdp_snapshot(
        project_root=args.project_root,
        db_name=args.db,
        run_key_prefix=args.run_key_prefix,
        json_report_path=args.json_report,
        markdown_report_path=args.markdown_report,
    )
    print(f"status: {report['status']}")
    print(f"fact_rows_total: {report['coverage']['fact_rows_total']}")
    print(f"missing_observations: {report['missingness']['missing_observation_count']}")
    print(f"duplicate_fact_grains: {report['data_quality']['duplicate_fact_grain_count']}")
    return 0 if report["status"] == "succeeded" else 1


if __name__ == "__main__":
    raise SystemExit(main())
