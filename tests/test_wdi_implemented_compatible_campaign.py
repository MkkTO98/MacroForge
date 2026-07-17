from __future__ import annotations

import json
import shutil
import subprocess
import uuid
from pathlib import Path

import pytest

from macroforge.observed_ingestion import compare_observed_packages
from macroforge.wdi_implemented_compatible_campaign import (
    CAMPAIGN_CANDIDATE_INDICATORS,
    CAMPAIGN_MAX_PRESPARSITY_ROWS,
    CAMPAIGN_PERIODS,
    CAMPAIGN_PRESPARSITY_COUNTRY_COUNT,
    build_wdi_implemented_compatible_campaign_observed_package,
    classify_campaign_raw,
    normalize_wdi_implemented_compatible_campaign_raw,
    write_wdi_implemented_compatible_campaign_artifacts,
)
from macroforge.wdi_loader import load_wdi_implemented_compatible_campaign_to_postgres

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BASE_MIGRATION = PROJECT_ROOT / "db/migrations/001_v0_schema_foundation.sql"
CANONICAL_DOMAIN_MIGRATION = PROJECT_ROOT / "db/migrations/003_canonical_domain_dimensions.sql"


def _fixture_response(indicator: str, label: str, *, values: list[float | None]) -> dict:
    countries = ["USA", "JPN"]
    years = ["2000", "2001"]
    rows = []
    index = 0
    for country, country_label, wb_id in [("USA", "United States", "US"), ("JPN", "Japan", "JP")]:
        for year in years:
            rows.append(
                {
                    "indicator": {"id": indicator, "value": label},
                    "country": {"id": wb_id, "value": country_label},
                    "countryiso3code": country,
                    "date": year,
                    "value": values[index],
                    "unit": "",
                    "obs_status": "",
                    "decimal": 0,
                }
            )
            index += 1
    return {
        "indicator_code": indicator,
        "url": f"https://api.worldbank.org/v2/country/USA;JPN/indicator/{indicator}?format=json&date=2000:2001",
        "response": [
            {"page": 1, "pages": 1, "per_page": 20000, "total": len(rows), "sourceid": "2", "lastupdated": "2026-07-01"},
            rows,
        ],
    }


def _sample_raw() -> dict:
    return {
        "scope": {
            "task": "TASK-165",
            "mode": "Operational Repository Expansion Campaign",
            "countries": ["JPN", "USA"],
            "country_count": 2,
            "date_range": "2000:2001",
            "indicators": ["SP.POP.DPND", "IT.NET.BBND.P2", "LP.LPI.OVRL.XQ"],
        },
        "country_catalog": {
            "url": "fixture://countries",
            "countries": [
                {"id": "JPN", "iso2Code": "JP", "name": "Japan", "region": {"id": "EAS", "value": "East Asia & Pacific"}, "incomeLevel": {"id": "HIC", "value": "High income"}},
                {"id": "USA", "iso2Code": "US", "name": "United States", "region": {"id": "NAC", "value": "North America"}, "incomeLevel": {"id": "HIC", "value": "High income"}},
            ],
        },
        "requests": [
            _fixture_response("SP.POP.DPND", "Age dependency ratio (% of working-age population)", values=[54.1, 54.2, 51.0, 51.3]),
            _fixture_response("IT.NET.BBND.P2", "Fixed broadband subscriptions (per 100 people)", values=[None, 10.5, None, 20.2]),
            _fixture_response("LP.LPI.OVRL.XQ", "Logistics performance index: Overall", values=[None, None, None, None]),
        ],
    }


def _postgres_available() -> bool:
    return all(shutil.which(command) for command in ("createdb", "dropdb", "psql"))


def _psql(db_name: str, sql: str) -> str:
    return subprocess.run(
        ["psql", "-v", "ON_ERROR_STOP=1", "-d", db_name, "-At", "-c", sql],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def test_campaign_candidate_universe_matches_task_165a_scope() -> None:
    assert len(CAMPAIGN_CANDIDATE_INDICATORS) == 27
    assert CAMPAIGN_PRESPARSITY_COUNTRY_COUNT == 217
    assert len(CAMPAIGN_PERIODS) == 24
    assert CAMPAIGN_MAX_PRESPARSITY_ROWS == 140_616
    assert "SP.POP.DPND" in CAMPAIGN_CANDIDATE_INDICATORS
    assert "TX.VAL.TECH.MF.ZS" in CAMPAIGN_CANDIDATE_INDICATORS
    assert "NY.GDP.MKTP.CD" not in CAMPAIGN_CANDIDATE_INDICATORS


def test_campaign_preflight_classifies_compatible_and_operationally_unsuitable_indicators() -> None:
    classification = classify_campaign_raw(_sample_raw(), min_non_null_observations=1)
    assert classification["candidate_count"] == 3
    assert classification["included_indicators"] == ["IT.NET.BBND.P2", "SP.POP.DPND"]
    assert classification["excluded_indicators"] == ["LP.LPI.OVRL.XQ"]
    lpi = classification["indicator_results"]["LP.LPI.OVRL.XQ"]
    assert lpi["classification"] == "operationally_unsuitable"
    assert lpi["exclusion_evidence"] == "zero non-null observations in requested provider period window"
    assert classification["partition"]["immediately_ingestible"] == ["IT.NET.BBND.P2", "SP.POP.DPND"]
    assert classification["partition"]["requires_architectural_investigation"] == []
    assert classification["partition"]["permanently_outside_confidence_cell"] == ["LP.LPI.OVRL.XQ"]


def test_campaign_normalization_builds_one_campaign_package_and_artifacts(tmp_path: Path) -> None:
    raw = _sample_raw()
    normalized = normalize_wdi_implemented_compatible_campaign_raw(raw, min_non_null_observations=1)
    assert normalized["task"] == "TASK-165"
    assert normalized["campaign"] == "WDI Implemented-Compatible Annual Scalar Expansion Campaign"
    assert normalized["indicators"] == ["IT.NET.BBND.P2", "SP.POP.DPND"]
    assert normalized["excluded_indicators"] == ["LP.LPI.OVRL.XQ"]
    assert normalized["row_count"] == 8
    assert normalized["observed_value_count"] == 6
    assert normalized["missing_value_count"] == 2

    package = build_wdi_implemented_compatible_campaign_observed_package(raw, min_non_null_observations=1)
    assert package.row_count == 8
    assert package.expected_row_count == 8
    assert compare_observed_packages(package, package).equivalent is True

    outputs = write_wdi_implemented_compatible_campaign_artifacts(
        raw,
        normalized_path=tmp_path / "normalized.json",
        preflight_report_path=tmp_path / "preflight.json",
        classification_report_path=tmp_path / "classification.json",
        operational_report_path=tmp_path / "operational.json",
        coverage_report_path=tmp_path / "coverage.json",
        confidence_report_path=tmp_path / "confidence.json",
        min_non_null_observations=1,
    )
    for path in outputs.values():
        assert Path(path).exists()
    assert json.loads((tmp_path / "coverage.json").read_text())["repository_growth"]["observations_added"] == 8


def test_campaign_loads_as_single_postgres_operation_when_available(tmp_path: Path) -> None:
    if not _postgres_available():
        pytest.skip("PostgreSQL CLI tools unavailable")

    raw = _sample_raw()
    normalized_path = tmp_path / "normalized.json"
    write_wdi_implemented_compatible_campaign_artifacts(raw, normalized_path=normalized_path, min_non_null_observations=1)
    db_name = f"macroforge_task165_campaign_{uuid.uuid4().hex[:12]}"
    try:
        subprocess.run(["createdb", db_name], check=True, capture_output=True, text=True)
        for migration in (BASE_MIGRATION, CANONICAL_DOMAIN_MIGRATION):
            subprocess.run(["psql", "-v", "ON_ERROR_STOP=1", "-d", db_name, "-f", str(migration)], check=True, capture_output=True, text=True)
        first = load_wdi_implemented_compatible_campaign_to_postgres(db_name, normalized_path, run_key="task-165-test")
        second = load_wdi_implemented_compatible_campaign_to_postgres(db_name, normalized_path, run_key="task-165-test")
        assert first == second
        assert first["staging_rows"] == 8
        assert first["fact_rows"] == 8
        counts = _psql(
            db_name,
            """
            SELECT
              (SELECT count(DISTINCT source_indicator_code) FROM curated.dim_indicator),
              (SELECT count(DISTINCT canonical_territory_code) FROM curated.dim_territory),
              (SELECT count(DISTINCT period_year) FROM curated.dim_period),
              (SELECT count(DISTINCT run_key) FROM meta.pipeline_run);
            """,
        )
        indicators, territories, periods, runs = [int(value) for value in counts.split("|")]
        assert indicators == 2
        assert territories == 2
        assert periods == 2
        assert runs == 1
    finally:
        subprocess.run(["dropdb", "--if-exists", db_name], capture_output=True, text=True)
