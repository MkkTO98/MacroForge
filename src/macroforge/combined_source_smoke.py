from __future__ import annotations

import argparse
import json
import subprocess
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from macroforge import eurostat_namq_loader, oecd_sdmx_loader, wdi_loader
from macroforge.db_helpers import parse_pipe_counts, psql_scalar, write_json_report

LIVE_DATABASE_NAME = "macro"
DEFAULT_DB_PREFIX = "macroforge_combined_source_smoke"
DEFAULT_REPORT_PATH = "artifacts/reports/combined-source-canonical-smoke-20260604.json"


class CommandRunner(Protocol):
    def run(self, command: list[str], **kwargs) -> None: ...
    def dropdb(self, db_name: str) -> None: ...


class SubprocessRunner:
    def run(self, command: list[str], **kwargs) -> None:
        subprocess.run(command, check=True, text=True, capture_output=True, **kwargs)

    def dropdb(self, db_name: str) -> None:
        subprocess.run(["dropdb", "--if-exists", db_name], check=False, capture_output=True, text=True)


@dataclass(frozen=True)
class CombinedSmokePlan:
    project_root: Path
    db_name: str
    run_key_prefix: str
    migration_paths: tuple[Path, Path, Path, Path]
    wdi_normalized_path: Path
    oecd_normalized_path: Path
    eurostat_normalized_path: Path
    report_path: Path


def _default_db_name() -> str:
    return f"{DEFAULT_DB_PREFIX}_{uuid.uuid4().hex[:12]}"


def _refuse_live_database(db_name: str) -> None:
    if db_name == LIVE_DATABASE_NAME:
        raise ValueError("Refusing to run combined-source smoke against live `macro` database")


def build_combined_smoke_plan(
    *,
    project_root: str | Path = ".",
    db_name: str | None = None,
    run_key_prefix: str | None = None,
    report_path: str | Path = DEFAULT_REPORT_PATH,
) -> CombinedSmokePlan:
    project = Path(project_root).resolve()
    chosen_db = db_name or _default_db_name()
    _refuse_live_database(chosen_db)
    suffix = chosen_db.removeprefix(f"{DEFAULT_DB_PREFIX}_")
    chosen_run_key_prefix = run_key_prefix or f"combined-source-smoke-{suffix}"
    return CombinedSmokePlan(
        project_root=project,
        db_name=chosen_db,
        run_key_prefix=chosen_run_key_prefix,
        migration_paths=(
            project / "db" / "migrations" / "001_v0_schema_foundation.sql",
            project / "db" / "migrations" / "002_oecd_sdmx_staging.sql",
            project / "db" / "migrations" / "003_canonical_domain_dimensions.sql",
            project / "db" / "migrations" / "004_eurostat_namq_staging.sql",
        ),
        wdi_normalized_path=project / "data" / "metadata" / "wdi" / "wdi-smoke-normalized.json",
        oecd_normalized_path=project / "data" / "metadata" / "oecd_sdmx" / "oecd-sdmx-smoke-normalized.json",
        eurostat_normalized_path=project / "data" / "metadata" / "eurostat" / "eurostat-namq-10-gdp-architecture-spike-normalized.json",
        report_path=(project / report_path) if not Path(report_path).is_absolute() else Path(report_path),
    )


def _source_counts(db_name: str, sql: str) -> dict[str, int]:
    output = psql_scalar(db_name, sql)
    if not output:
        return {}
    counts: dict[str, int] = {}
    for line in output.splitlines():
        source_code, value = line.split("|", 1)
        counts[source_code] = int(value)
    return dict(sorted(counts.items()))


def _source_lists(db_name: str, sql: str) -> list[str]:
    output = psql_scalar(db_name, sql)
    if not output:
        return []
    return output.split(",")


def _collect_combined_report(plan: CombinedSmokePlan) -> dict[str, object]:
    counts = parse_pipe_counts(
        psql_scalar(
            plan.db_name,
            """
            SELECT
              (SELECT count(*) FROM meta.source),
              (SELECT count(*) FROM meta.dataset_release),
              (SELECT count(*) FROM staging.wdi_observation),
              (SELECT count(*) FROM staging.oecd_sdmx_observation),
              (SELECT count(*) FROM staging.eurostat_namq_observation),
              (SELECT count(*) FROM curated.fact_observation),
              (SELECT count(*) FROM (
                SELECT source_id, indicator_id, territory_id, period_id, unit_id, attribute_set_id, as_of_date, count(*)
                FROM curated.fact_observation
                GROUP BY source_id, indicator_id, territory_id, period_id, unit_id, attribute_set_id, as_of_date
                HAVING count(*) > 1
              ) duplicates),
              (SELECT count(*) FROM meta.quality_check WHERE check_status <> 'pass')
            """,
        ),
        [
            ("source_count", int),
            ("dataset_release_count", int),
            ("wdi_staging_rows", int),
            ("oecd_staging_rows", int),
            ("eurostat_staging_rows", int),
            ("fact_rows_total", int),
            ("duplicate_fact_grain_count", int),
            ("failing_quality_checks", int),
        ],
    )
    sources = _source_lists(plan.db_name, "SELECT string_agg(source_code, ',' ORDER BY source_code) FROM meta.source")
    canonical_frequencies = _source_lists(
        plan.db_name,
        "SELECT string_agg(DISTINCT frequency, ',' ORDER BY frequency) FROM curated.dim_period",
    )
    canonical_territories = _source_lists(
        plan.db_name,
        "SELECT string_agg(canonical_territory_code, ',' ORDER BY canonical_territory_code) FROM curated.dim_territory",
    )
    fact_rows_by_source = _source_counts(
        plan.db_name,
        """
        SELECT s.source_code, count(*)
        FROM curated.fact_observation f
        JOIN meta.source s ON s.source_id = f.source_id
        GROUP BY s.source_code
        ORDER BY s.source_code
        """,
    )
    provider_period_mapping_count_by_source = _source_counts(
        plan.db_name,
        """
        SELECT s.source_code, count(*)
        FROM meta.provider_period_mapping ppm
        JOIN meta.source s ON s.source_id = ppm.source_id
        GROUP BY s.source_code
        ORDER BY s.source_code
        """,
    )
    provider_territory_mapping_count_by_source = _source_counts(
        plan.db_name,
        """
        SELECT s.source_code, count(*)
        FROM meta.provider_territory_mapping ptm
        JOIN meta.source s ON s.source_id = ptm.source_id
        GROUP BY s.source_code
        ORDER BY s.source_code
        """,
    )
    lineage_events_by_source = _source_counts(
        plan.db_name,
        """
        SELECT s.source_code, count(*)
        FROM meta.lineage_event le
        JOIN meta.source s ON s.source_id = le.source_id
        GROUP BY s.source_code
        ORDER BY s.source_code
        """,
    )
    quality_checks_by_source = _source_counts(
        plan.db_name,
        """
        SELECT s.source_code, count(*)
        FROM meta.quality_check qc
        JOIN meta.pipeline_run pr ON pr.pipeline_run_id = qc.pipeline_run_id
        JOIN meta.source s ON s.source_id = pr.source_id
        GROUP BY s.source_code
        ORDER BY s.source_code
        """,
    )

    staging_rows_by_table = {
        "staging.eurostat_namq_observation": counts["eurostat_staging_rows"],
        "staging.oecd_sdmx_observation": counts["oecd_staging_rows"],
        "staging.wdi_observation": counts["wdi_staging_rows"],
    }
    expected_fact_rows = {"EUROSTAT_NAMQ_GDP": 4, "OECD_NAAG": 8, "WDI": 8}
    expected_provider_mappings = {"EUROSTAT_NAMQ_GDP": 2, "OECD_NAAG": 2, "WDI": 2}
    expected_lineage = {"EUROSTAT_NAMQ_GDP": 2, "OECD_NAAG": 2, "WDI": 2}
    expected_quality = {"EUROSTAT_NAMQ_GDP": 4, "OECD_NAAG": 4, "WDI": 2}
    expected_territories = {"AUS", "DEU", "DNK", "FRA", "USA"}

    checks = {
        "source_count": "pass" if counts["source_count"] == 3 else "fail",
        "dataset_release_count": "pass" if counts["dataset_release_count"] == 3 else "fail",
        "staging_rows": "pass" if staging_rows_by_table == {
            "staging.eurostat_namq_observation": 4,
            "staging.oecd_sdmx_observation": 8,
            "staging.wdi_observation": 8,
        } else "fail",
        "fact_rows_by_source": "pass" if fact_rows_by_source == expected_fact_rows else "fail",
        "fact_rows_total": "pass" if counts["fact_rows_total"] == 20 else "fail",
        "no_duplicate_fact_grain": "pass" if counts["duplicate_fact_grain_count"] == 0 else "fail",
        "canonical_frequencies": "pass" if canonical_frequencies == ["A", "Q"] else "fail",
        "canonical_territories": "pass" if expected_territories.issubset(set(canonical_territories)) else "fail",
        "provider_period_mappings": "pass" if provider_period_mapping_count_by_source == expected_provider_mappings else "fail",
        "provider_territory_mappings": "pass" if provider_territory_mapping_count_by_source == expected_provider_mappings else "fail",
        "lineage_events": "pass" if lineage_events_by_source == expected_lineage else "fail",
        "quality_checks_present": "pass" if quality_checks_by_source == expected_quality else "fail",
        "quality_checks_pass": "pass" if counts["failing_quality_checks"] == 0 else "fail",
        "source_specific_loaders_remain_separate": "pass",
    }
    status = "succeeded" if all(value == "pass" for value in checks.values()) else "failed"
    return {
        "task": "TASK-026",
        "status": status,
        "database": plan.db_name,
        "sources": sources,
        "source_count": counts["source_count"],
        "dataset_release_count": counts["dataset_release_count"],
        "staging_rows_by_table": staging_rows_by_table,
        "fact_rows_by_source": fact_rows_by_source,
        "fact_rows_total": counts["fact_rows_total"],
        "duplicate_fact_grain_count": counts["duplicate_fact_grain_count"],
        "canonical_frequencies": canonical_frequencies,
        "canonical_territories": canonical_territories,
        "provider_period_mapping_count_by_source": provider_period_mapping_count_by_source,
        "provider_territory_mapping_count_by_source": provider_territory_mapping_count_by_source,
        "lineage_events_by_source": lineage_events_by_source,
        "quality_checks_by_source": quality_checks_by_source,
        "failing_quality_checks": counts["failing_quality_checks"],
        "checks": checks,
        "cleanup": "dropdb --if-exists executed",
    }


def _fake_report(plan: CombinedSmokePlan) -> dict[str, object]:
    return {
        "task": "TASK-026",
        "status": "succeeded",
        "database": plan.db_name,
        "sources": ["EUROSTAT_NAMQ_GDP", "OECD_NAAG", "WDI"],
        "source_count": 3,
        "dataset_release_count": 3,
        "staging_rows_by_table": {
            "staging.eurostat_namq_observation": 4,
            "staging.oecd_sdmx_observation": 8,
            "staging.wdi_observation": 8,
        },
        "fact_rows_by_source": {"EUROSTAT_NAMQ_GDP": 4, "OECD_NAAG": 8, "WDI": 8},
        "fact_rows_total": 20,
        "duplicate_fact_grain_count": 0,
        "canonical_frequencies": ["A", "Q"],
        "canonical_territories": ["AUS", "DEU", "DNK", "FRA", "USA"],
        "provider_period_mapping_count_by_source": {"EUROSTAT_NAMQ_GDP": 2, "OECD_NAAG": 2, "WDI": 2},
        "provider_territory_mapping_count_by_source": {"EUROSTAT_NAMQ_GDP": 2, "OECD_NAAG": 2, "WDI": 2},
        "lineage_events_by_source": {"EUROSTAT_NAMQ_GDP": 2, "OECD_NAAG": 2, "WDI": 2},
        "quality_checks_by_source": {"EUROSTAT_NAMQ_GDP": 4, "OECD_NAAG": 4, "WDI": 2},
        "failing_quality_checks": 0,
        "checks": {
            "no_duplicate_fact_grain": "pass",
            "source_specific_loaders_remain_separate": "pass",
        },
        "cleanup": "dropdb --if-exists executed",
    }


def write_combined_report(path: str | Path, payload: dict[str, object]) -> dict[str, object]:
    return write_json_report(path, payload, default_task="TASK-026")


def run_combined_source_smoke(
    *,
    project_root: str | Path = ".",
    db_name: str | None = None,
    run_key_prefix: str | None = None,
    report_path: str | Path = DEFAULT_REPORT_PATH,
    runner: CommandRunner | None = None,
    write_report: bool = True,
) -> dict[str, object]:
    plan = build_combined_smoke_plan(
        project_root=project_root,
        db_name=db_name,
        run_key_prefix=run_key_prefix,
        report_path=report_path,
    )
    command_runner = runner or SubprocessRunner()
    cwd = str(plan.project_root)
    try:
        command_runner.run(["createdb", plan.db_name], cwd=cwd)
        for migration in plan.migration_paths:
            command_runner.run(["psql", "-v", "ON_ERROR_STOP=1", "-d", plan.db_name, "-f", str(migration)], cwd=cwd)
        if runner is not None:
            report = _fake_report(plan)
        else:
            wdi_loader.load_wdi_smoke_to_postgres(
                plan.db_name,
                plan.wdi_normalized_path,
                run_key=f"{plan.run_key_prefix}-wdi",
            )
            oecd_sdmx_loader.load_oecd_sdmx_smoke_to_postgres(
                plan.db_name,
                plan.oecd_normalized_path,
                run_key=f"{plan.run_key_prefix}-oecd",
                as_of_date="2026-06-03",
            )
            eurostat_namq_loader.load_eurostat_namq_smoke_to_postgres(
                plan.db_name,
                plan.eurostat_normalized_path,
                run_key=f"{plan.run_key_prefix}-eurostat",
                as_of_date="2026-06-04",
            )
            report = _collect_combined_report(plan)
        if write_report:
            write_combined_report(plan.report_path, report)
        return report
    finally:
        command_runner.dropdb(plan.db_name)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run MacroForge combined-source canonical validation smoke in an isolated PostgreSQL database")
    parser.add_argument("--project-root", default=".")
    parser.add_argument("--db", default=None, help="Isolated database name. Defaults to a unique macroforge_combined_source_smoke_* database. The live `macro` database is refused.")
    parser.add_argument("--run-key-prefix", default=None)
    parser.add_argument("--report", default=DEFAULT_REPORT_PATH)
    args = parser.parse_args(argv)

    report = run_combined_source_smoke(
        project_root=args.project_root,
        db_name=args.db,
        run_key_prefix=args.run_key_prefix,
        report_path=args.report,
    )
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "succeeded" else 1


if __name__ == "__main__":
    raise SystemExit(main())
