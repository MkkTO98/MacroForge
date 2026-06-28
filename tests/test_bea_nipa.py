from __future__ import annotations

import json
from pathlib import Path

from macroforge.bea_nipa import build_bea_nipa_observed_package, normalize_bea_nipa_itable_fixture
from macroforge.contract_drift import validate_observed_package_contract
from macroforge.observed_ingestion import canonical_attribute_hash, compare_observed_packages, observed_package_fingerprint

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_FIXTURE = PROJECT_ROOT / "data" / "raw" / "bea" / "bea-nipa-t10101-itablecore-20260625-raw.json"
RAW_SHA256 = "99f5d0ebc9cd31cc93426c7d9ee4dc742e708ce102f843bb989de3ac6366d689"
SOURCE_URL = "https://apps.bea.gov/iTablecore/data/app/GetSteps"


def _raw() -> dict:
    return json.loads(RAW_FIXTURE.read_text(encoding="utf-8"))


def _normalized() -> dict:
    return normalize_bea_nipa_itable_fixture(
        _raw(),
        raw_artifact_path=str(RAW_FIXTURE.relative_to(PROJECT_ROOT)),
        raw_sha256=RAW_SHA256,
        source_url=SOURCE_URL,
    )


def test_bea_nipa_fixture_normalization_preserves_table_line_and_period_evidence():
    normalized = _normalized()

    assert normalized["source_code"] == "BEA_NIPA"
    assert normalized["provider_dataset_code"] == "NIPA:T10101"
    assert normalized["table_id"] == "T10101"
    assert normalized["table_title"] == "Table 1.1.1. Percent Change From Preceding Period in Real Gross Domestic Product"
    assert normalized["release_description"] == "Last Revised on: June 25, 2026 - Next Release Date July 30, 2026"
    assert normalized["frequency"] == "Q"
    assert normalized["period_range"] == "2024-Q1-2026-Q1"
    assert normalized["row_count"] == 252
    assert normalized["expected_row_count"] == 252
    assert normalized["input_filters"] == {
        "appid": 19,
        "category": "Survey",
        "table_key": "1",
        "table_id": "T10101",
        "series": "Q",
        "scope": "bounded TASK-053 architectural experiment",
    }

    first = normalized["rows"][0]
    assert first == {
        "table_id": "T10101",
        "table_title": "Table 1.1.1. Percent Change From Preceding Period in Real Gross Domestic Product",
        "line_number": "1",
        "line_description": "Gross domestic product",
        "indicator_code": "T10101:L1",
        "territory_code": "USA",
        "territory_label": "United States",
        "provider_period_code": "2024-Q1",
        "frequency": "Q",
        "period_year": 2024,
        "period_quarter": 1,
        "unit_code": "PERCENT_SAAR",
        "unit_label": "Percent, seasonally adjusted at annual rates",
        "value": 0.8,
        "observation_status": "observed",
        "decimal_precision": 1,
        "attributes": {
            "bea_table_id": "T10101",
            "bea_table_key": "1",
            "bea_line_number": "1",
            "bea_line_description": "Gross domestic product",
            "cell_style": "NormalStyle_bold",
            "indent_level": "0",
            "release_description": "Last Revised on: June 25, 2026 - Next Release Date July 30, 2026",
            "section_name": "Section 1 - Domestic Product and Income",
            "sub_title": "[Percent] Seasonally adjusted at annual rates",
        },
        "source_payload": {
            "line_cell": {"CS": "NormalStyle", "CV": "1", "IL": "0"},
            "stub_cell": {"CS": "BoldStubStyle", "CV": "Gross domestic product", "IL": "4"},
            "year_cell": {"CS": "ColumnHeaderStyle", "CV": "2024", "IL": "0"},
            "quarter_cell": {"CS": "ColumnHeaderStyle", "CV": "Q1", "IL": "0"},
            "value_cell": {"CS": "NormalStyle_bold", "CV": "0.8", "IL": "0"},
        },
    }


def test_bea_nipa_observed_package_satisfies_existing_contract_without_contract_evolution():
    package = build_bea_nipa_observed_package(_normalized())

    assert package.source_code == "BEA_NIPA"
    assert package.source_name == "U.S. Bureau of Economic Analysis NIPA bounded table evidence slice"
    assert package.source_home_url == "https://www.bea.gov/data/gdp/gross-domestic-product"
    assert package.provider_dataset_code == "NIPA:T10101"
    assert package.release_key == "BEA_NIPA:T10101:2024-Q1-2026-Q1:99f5d0ebc9cd"
    assert package.row_count == 252
    assert package.expected_row_count == 252
    assert package.raw_evidence == {
        "source_url": SOURCE_URL,
        "raw_artifact_path": "data/raw/bea/bea-nipa-t10101-itablecore-20260625-raw.json",
        "raw_sha256": RAW_SHA256,
        "release_description": "Last Revised on: June 25, 2026 - Next Release Date July 30, 2026",
    }

    observation = package.observations[0]
    assert observation.provider_indicator_code == "T10101:L1"
    assert observation.provider_indicator_label == "Gross domestic product"
    assert observation.provider_territory_code == "USA"
    assert observation.provider_territory_label == "United States"
    assert observation.provider_period_code == "2024-Q1"
    assert observation.frequency == "Q"
    assert observation.period_year == 2024
    assert observation.period_quarter == 1
    assert observation.period_month is None
    assert observation.unit_code == "PERCENT_SAAR"
    assert observation.unit_label == "Percent, seasonally adjusted at annual rates"
    assert observation.value == 0.8
    assert observation.observation_status == "observed"
    assert observation.decimal_precision == 1
    assert observation.attribute_hash == canonical_attribute_hash(observation.attributes)

    report = validate_observed_package_contract(package)
    assert report.valid is True
    assert report.issues == ()


def test_bea_nipa_observed_package_replay_is_deterministic():
    package = build_bea_nipa_observed_package(_normalized())
    replayed = build_bea_nipa_observed_package(_normalized())

    comparison = compare_observed_packages(package, replayed)

    assert comparison.equivalent is True
    assert comparison.left_fingerprint == comparison.right_fingerprint
    assert comparison.row_count_match is True
    assert comparison.expected_row_count_match is True
    assert comparison.observation_count_match is True
    assert comparison.differing_observations == ()
    assert len(observed_package_fingerprint(package)) == 64


def test_bea_nipa_module_is_not_a_generalized_framework():
    source = (PROJECT_ROOT / "src" / "macroforge" / "bea_nipa.py").read_text(encoding="utf-8")

    forbidden = [
        "class BaseLoader",
        "class SourcePlugin",
        "PluginRegistry",
        "framework",
        "sqlalchemy",
        "requests.get",
        "urllib.request",
    ]
    for token in forbidden:
        assert token not in source
