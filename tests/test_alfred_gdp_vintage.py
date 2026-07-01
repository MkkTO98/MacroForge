from __future__ import annotations

import hashlib
from pathlib import Path

from macroforge.alfred_gdp_vintage import (
    build_alfred_gdp_revision_observed_package,
    build_alfred_gdp_vintage_packages,
    normalize_alfred_gdp_vintage_fixture,
)
from macroforge.contract_drift import validate_observed_package_contract
from macroforge.observed_ingestion import canonical_attribute_hash, compare_observed_packages, observed_package_fingerprint

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_FIXTURE = PROJECT_ROOT / "data" / "raw" / "alfred_gdp_vintage" / "alfred-gdp-20260528-20260625-2025q4-2026q1.csv"
SOURCE_URL = "https://alfred.stlouisfed.org/graph/alfredgraph.csv?id=GDP,GDP&cosd=2025-10-03,2025-10-03&coed=2026-01-01,2026-01-01&vintage_date=2026-05-28,2026-06-25"
CONTENT_TYPE = "application/csv"

SAMPLE_CSV = b'''observation_date,GDP_20260528,GDP_20260625
2025-10-01,31422.526,31422.526
2026-01-01,31819.464,31865.721
'''


def _normalized_from_sample() -> dict:
    return normalize_alfred_gdp_vintage_fixture(
        SAMPLE_CSV,
        raw_artifact_path="data/raw/alfred_gdp_vintage/alfred-gdp-20260528-20260625-2025q4-2026q1.csv",
        raw_sha256=hashlib.sha256(SAMPLE_CSV).hexdigest(),
        source_url=SOURCE_URL,
        content_type=CONTENT_TYPE,
    )


def test_alfred_gdp_revision_fixture_normalizes_two_vintages_with_changed_and_unchanged_overlap():
    normalized = _normalized_from_sample()

    assert normalized["source_code"] == "ALFRED_GDP_VINTAGE"
    assert normalized["provider_dataset_code"] == "ALFRED:GDP"
    assert normalized["series_id"] == "GDP"
    assert normalized["series_title"] == "Gross Domestic Product"
    assert normalized["frequency"] == "Q"
    assert normalized["period_range"] == "2025-Q4-2026-Q1"
    assert normalized["vintage_dates"] == ["2026-05-28", "2026-06-25"]
    assert normalized["row_count"] == 4
    assert normalized["expected_row_count"] == 4
    assert normalized["revision_summary"] == {
        "overlapping_periods": ["2025-Q4", "2026-Q1"],
        "changed_periods": ["2026-Q1"],
        "unchanged_control_periods": ["2025-Q4"],
    }
    assert normalized["input_filters"] == {
        "series_id": "GDP",
        "vintage_dates": ["2026-05-28", "2026-06-25"],
        "observation_start": "2025-10-01",
        "observation_end": "2026-01-01",
        "scope": "bounded TASK-058 ALFRED revision-vintage architectural evidence slice",
    }
    assert {(row["vintage_date"], row["provider_period_code"]): row["value"] for row in normalized["rows"]} == {
        ("2026-05-28", "2025-Q4"): 31422.526,
        ("2026-05-28", "2026-Q1"): 31819.464,
        ("2026-06-25", "2025-Q4"): 31422.526,
        ("2026-06-25", "2026-Q1"): 31865.721,
    }

    first = normalized["rows"][0]
    assert first["provider_indicator_code"] == "GDP"
    assert first["provider_indicator_label"] == "Gross Domestic Product"
    assert first["territory_code"] == "USA"
    assert first["territory_label"] == "United States"
    assert first["unit_code"] == "BILLIONS_USD_SAAR"
    assert first["unit_label"] == "Billions of Dollars, Seasonally Adjusted Annual Rate"
    assert first["attributes"]["vintage_date"] == "2026-05-28"
    assert first["attributes"]["release_identity"] == "ALFRED:GDP:2026-05-28"
    assert first["source_payload"] == {
        "observation_date": "2025-10-01",
        "vintage_column": "GDP_20260528",
        "vintage_date": "2026-05-28",
        "raw_value": "31422.526",
    }


def test_alfred_gdp_revision_observed_package_satisfies_existing_contract_without_contract_evolution():
    package = build_alfred_gdp_revision_observed_package(_normalized_from_sample())

    assert package.source_code == "ALFRED_GDP_VINTAGE"
    assert package.source_name == "ALFRED bounded GDP release-vintage evidence slice"
    assert package.source_home_url == "https://alfred.stlouisfed.org/"
    assert package.provider_dataset_code == "ALFRED:GDP"
    assert package.release_key.startswith("ALFRED_GDP_VINTAGE:GDP:2026-05-28+2026-06-25:2025-Q4-2026-Q1:")
    assert package.row_count == 4
    assert package.expected_row_count == 4
    assert package.input_filters == _normalized_from_sample()["input_filters"]
    assert package.raw_evidence["source_url"] == SOURCE_URL
    assert package.raw_evidence["raw_artifact_path"] == "data/raw/alfred_gdp_vintage/alfred-gdp-20260528-20260625-2025q4-2026q1.csv"
    assert len(package.raw_evidence["raw_sha256"]) == 64
    assert package.raw_evidence["revision_summary"] == _normalized_from_sample()["revision_summary"]

    observation = package.observations[0]
    assert observation.provider_indicator_code == "GDP"
    assert observation.provider_indicator_label == "Gross Domestic Product"
    assert observation.provider_territory_code == "USA"
    assert observation.provider_territory_label == "United States"
    assert observation.provider_period_code == "2025-Q4"
    assert observation.frequency == "Q"
    assert observation.period_year == 2025
    assert observation.period_quarter == 4
    assert observation.period_month is None
    assert observation.unit_code == "BILLIONS_USD_SAAR"
    assert observation.value == 31422.526
    assert observation.observation_status == "observed"
    assert observation.decimal_precision == 3
    assert observation.attribute_hash == canonical_attribute_hash(observation.attributes)

    report = validate_observed_package_contract(package)
    assert report.valid is True
    assert report.issues == ()


def test_alfred_gdp_revision_package_preserves_multiple_source_backed_values_for_same_economic_period():
    package = build_alfred_gdp_revision_observed_package(_normalized_from_sample())

    values_by_vintage = {
        observation.attributes["vintage_date"]: observation.value
        for observation in package.observations
        if observation.provider_period_code == "2026-Q1"
    }
    unchanged_values_by_vintage = {
        observation.attributes["vintage_date"]: observation.value
        for observation in package.observations
        if observation.provider_period_code == "2025-Q4"
    }

    assert values_by_vintage == {"2026-05-28": 31819.464, "2026-06-25": 31865.721}
    assert unchanged_values_by_vintage == {"2026-05-28": 31422.526, "2026-06-25": 31422.526}
    assert {observation.provider_indicator_code for observation in package.observations} == {"GDP"}
    assert {observation.provider_territory_code for observation in package.observations} == {"USA"}


def test_alfred_gdp_revision_replay_and_per_vintage_fingerprints_are_deterministic():
    package = build_alfred_gdp_revision_observed_package(_normalized_from_sample())
    replayed = build_alfred_gdp_revision_observed_package(_normalized_from_sample())

    comparison = compare_observed_packages(package, replayed)

    assert comparison.equivalent is True
    assert comparison.left_fingerprint == comparison.right_fingerprint
    assert comparison.row_count_match is True
    assert comparison.expected_row_count_match is True
    assert comparison.observation_count_match is True
    assert comparison.differing_observations == ()
    assert len(observed_package_fingerprint(package)) == 64

    vintage_packages = build_alfred_gdp_vintage_packages(_normalized_from_sample())
    first = vintage_packages["2026-05-28"]
    second = vintage_packages["2026-06-25"]
    vintage_comparison = compare_observed_packages(first, second)

    assert vintage_comparison.equivalent is False
    assert vintage_comparison.row_count_match is True
    assert vintage_comparison.observation_count_match is True
    assert vintage_comparison.differing_observations == (
        {
            "index": 0,
            "provider_indicator_code": "GDP",
            "provider_territory_code": "USA",
            "provider_period_code": "2025-Q4",
            "changed_fields": ("attributes", "source_payload", "attribute_hash"),
        },
        {
            "index": 1,
            "provider_indicator_code": "GDP",
            "provider_territory_code": "USA",
            "provider_period_code": "2026-Q1",
            "changed_fields": ("value", "attributes", "source_payload", "attribute_hash"),
        },
    )
    assert observed_package_fingerprint(first) == observed_package_fingerprint(build_alfred_gdp_vintage_packages(_normalized_from_sample())["2026-05-28"])


def test_alfred_gdp_module_remains_bounded_source_specific_not_revision_or_provider_framework():
    source = (PROJECT_ROOT / "src" / "macroforge" / "alfred_gdp_vintage.py").read_text(encoding="utf-8")

    forbidden = [
        "class RevisionFramework",
        "class VintageEngine",
        "class FredClient",
        "class AlfredClient",
        "class BaseSource",
        "class SourcePlugin",
        "PluginRegistry",
        "CREATE TABLE",
        "INSERT INTO",
        "requests.get",
        "urllib.request",
        "sqlalchemy",
        "api_key",
    ]
    for token in forbidden:
        assert token not in source


def test_project_alfred_gdp_revision_fixture_preserves_live_bounded_evidence_when_present():
    if not RAW_FIXTURE.exists():
        return

    raw_payload = RAW_FIXTURE.read_bytes()
    normalized = normalize_alfred_gdp_vintage_fixture(
        raw_payload,
        raw_artifact_path=str(RAW_FIXTURE.relative_to(PROJECT_ROOT)),
        raw_sha256=hashlib.sha256(raw_payload).hexdigest(),
        source_url=SOURCE_URL,
        content_type=CONTENT_TYPE,
    )
    package = build_alfred_gdp_revision_observed_package(normalized)

    assert normalized["row_count"] == 4
    assert normalized["revision_summary"]["changed_periods"] == ["2026-Q1"]
    assert normalized["revision_summary"]["unchanged_control_periods"] == ["2025-Q4"]
    assert package.row_count == 4
    assert package.observations[0].attributes["vintage_date"] == "2026-05-28"
    assert package.observations[-1].attributes["vintage_date"] == "2026-06-25"
    assert observed_package_fingerprint(package) == observed_package_fingerprint(build_alfred_gdp_revision_observed_package(normalized))
