from __future__ import annotations

import hashlib
from pathlib import Path

from macroforge.contract_drift import validate_observed_package_contract
from macroforge.ilostat_unemployment import (
    build_ilostat_unemployment_observed_package,
    normalize_ilostat_unemployment_fixture,
)
from macroforge.observed_ingestion import canonical_attribute_hash, compare_observed_packages, observed_package_fingerprint

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_FIXTURE = PROJECT_ROOT / "data" / "raw" / "ilostat_unemployment" / "ilostat-unemployment-usa-jpn-total-age15plus-2023-2024.json"
SOURCE_URL = "https://rplumber.ilo.org/data/indicator/?id=UNE_2EAP_SEX_AGE_RT_A&ref_area=USA+JPN&sex=SEX_T&classif1=AGE_YTHADULT_YGE15&timefrom=2023&timeto=2024&format=json"
CONTENT_TYPE = "application/octet-stream"

SAMPLE_JSON = b'''[{"ref_area":"JPN","source":"XA:1843","indicator":"UNE_2EAP_SEX_AGE_RT","sex":"SEX_T","classif1":"AGE_YTHADULT_YGE15","time":"2024","obs_value":2.5,"obs_status":"R"},{"ref_area":"JPN","source":"XA:1843","indicator":"UNE_2EAP_SEX_AGE_RT","sex":"SEX_T","classif1":"AGE_YTHADULT_YGE15","time":"2023","obs_value":2.6,"obs_status":"R"},{"ref_area":"USA","source":"XA:2174","indicator":"UNE_2EAP_SEX_AGE_RT","sex":"SEX_T","classif1":"AGE_YTHADULT_YGE15","time":"2024","obs_value":4.022,"obs_status":"R"},{"ref_area":"USA","source":"XA:2174","indicator":"UNE_2EAP_SEX_AGE_RT","sex":"SEX_T","classif1":"AGE_YTHADULT_YGE15","time":"2023","obs_value":3.638,"obs_status":"R"}]'''


def _normalized_from_sample() -> dict:
    return normalize_ilostat_unemployment_fixture(
        SAMPLE_JSON,
        raw_artifact_path="data/raw/ilostat_unemployment/ilostat-unemployment-usa-jpn-total-age15plus-2023-2024.json",
        raw_sha256=hashlib.sha256(SAMPLE_JSON).hexdigest(),
        source_url=SOURCE_URL,
        content_type=CONTENT_TYPE,
    )


def test_ilostat_unemployment_fixture_normalizes_bounded_labor_slice():
    normalized = _normalized_from_sample()

    assert normalized["source_code"] == "ILOSTAT_UNEMPLOYMENT"
    assert normalized["provider_dataset_code"] == "ILOSTAT:UNE_2EAP_SEX_AGE_RT_A"
    assert normalized["indicator_id"] == "UNE_2EAP_SEX_AGE_RT"
    assert normalized["indicator_label"] == "Unemployment rate by sex and age"
    assert normalized["frequency"] == "A"
    assert normalized["period_range"] == "2023-2024"
    assert normalized["row_count"] == 4
    assert normalized["expected_row_count"] == 4
    assert normalized["input_filters"] == {
        "id": "UNE_2EAP_SEX_AGE_RT_A",
        "ref_area": ["USA", "JPN"],
        "sex": "SEX_T",
        "classif1": "AGE_YTHADULT_YGE15",
        "timefrom": "2023",
        "timeto": "2024",
        "format": "json",
        "scope": "bounded TASK-059 ILOSTAT unemployment-rate evidence slice",
    }
    assert {(row["territory_code"], row["provider_period_code"]): row["value"] for row in normalized["rows"]} == {
        ("JPN", "2023"): 2.6,
        ("JPN", "2024"): 2.5,
        ("USA", "2023"): 3.638,
        ("USA", "2024"): 4.022,
    }

    first = normalized["rows"][0]
    assert first["provider_indicator_code"] == "UNE_2EAP_SEX_AGE_RT"
    assert first["provider_indicator_label"] == "Unemployment rate by sex and age"
    assert first["territory_code"] == "JPN"
    assert first["territory_label"] == "Japan"
    assert first["unit_code"] == "PERCENT_OF_LABOR_FORCE"
    assert first["unit_label"] == "Percent of labor force"
    assert first["observation_status"] == "observed"
    assert first["decimal_precision"] == 1
    assert first["attributes"] == {
        "source_provider": "ILOSTAT",
        "source_code": "XA:1843",
        "sex": "SEX_T",
        "sex_label": "Total sex",
        "classif1": "AGE_YTHADULT_YGE15",
        "classif1_label": "Age 15+",
        "obs_status": "R",
    }
    assert first["source_payload"] == {
        "ref_area": "JPN",
        "source": "XA:1843",
        "indicator": "UNE_2EAP_SEX_AGE_RT",
        "sex": "SEX_T",
        "classif1": "AGE_YTHADULT_YGE15",
        "time": "2023",
        "obs_value": 2.6,
        "obs_status": "R",
    }


def test_ilostat_unemployment_observed_package_satisfies_existing_contract_without_contract_evolution():
    package = build_ilostat_unemployment_observed_package(_normalized_from_sample())

    assert package.source_code == "ILOSTAT_UNEMPLOYMENT"
    assert package.source_name == "ILOSTAT bounded unemployment-rate evidence slice"
    assert package.source_home_url == "https://ilostat.ilo.org/"
    assert package.provider_dataset_code == "ILOSTAT:UNE_2EAP_SEX_AGE_RT_A"
    assert package.release_key.startswith("ILOSTAT_UNEMPLOYMENT:UNE_2EAP_SEX_AGE_RT_A:2023-2024:")
    assert package.row_count == 4
    assert package.expected_row_count == 4
    assert package.input_filters == _normalized_from_sample()["input_filters"]
    assert package.raw_evidence["source_url"] == SOURCE_URL
    assert package.raw_evidence["raw_artifact_path"] == "data/raw/ilostat_unemployment/ilostat-unemployment-usa-jpn-total-age15plus-2023-2024.json"
    assert len(package.raw_evidence["raw_sha256"]) == 64

    observation = package.observations[0]
    assert observation.provider_indicator_code == "UNE_2EAP_SEX_AGE_RT"
    assert observation.provider_indicator_label == "Unemployment rate by sex and age"
    assert observation.provider_territory_code == "JPN"
    assert observation.provider_territory_label == "Japan"
    assert observation.provider_period_code == "2023"
    assert observation.frequency == "A"
    assert observation.period_year == 2023
    assert observation.period_quarter is None
    assert observation.period_month is None
    assert observation.unit_code == "PERCENT_OF_LABOR_FORCE"
    assert observation.unit_label == "Percent of labor force"
    assert observation.value == 2.6
    assert observation.observation_status == "observed"
    assert observation.decimal_precision == 1
    assert observation.attribute_hash == canonical_attribute_hash(observation.attributes)

    report = validate_observed_package_contract(package)
    assert report.valid is True
    assert report.issues == ()


def test_ilostat_unemployment_replay_and_fingerprint_are_deterministic():
    package = build_ilostat_unemployment_observed_package(_normalized_from_sample())
    replayed = build_ilostat_unemployment_observed_package(_normalized_from_sample())

    comparison = compare_observed_packages(package, replayed)

    assert comparison.equivalent is True
    assert comparison.left_fingerprint == comparison.right_fingerprint
    assert comparison.row_count_match is True
    assert comparison.expected_row_count_match is True
    assert comparison.observation_count_match is True
    assert comparison.differing_observations == ()
    assert len(observed_package_fingerprint(package)) == 64


def test_ilostat_unemployment_module_remains_bounded_source_specific_not_labor_or_provider_framework():
    source = (PROJECT_ROOT / "src" / "macroforge" / "ilostat_unemployment.py").read_text(encoding="utf-8")

    forbidden = [
        "class LaborFramework",
        "class ClassificationFramework",
        "class IlostatClient",
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


def test_project_ilostat_unemployment_fixture_preserves_live_bounded_evidence_when_present():
    if not RAW_FIXTURE.exists():
        return

    raw_payload = RAW_FIXTURE.read_bytes()
    normalized = normalize_ilostat_unemployment_fixture(
        raw_payload,
        raw_artifact_path=str(RAW_FIXTURE.relative_to(PROJECT_ROOT)),
        raw_sha256=hashlib.sha256(raw_payload).hexdigest(),
        source_url=SOURCE_URL,
        content_type=CONTENT_TYPE,
    )
    package = build_ilostat_unemployment_observed_package(normalized)

    assert normalized["row_count"] == 4
    assert normalized["period_range"] == "2023-2024"
    assert {(row["territory_code"], row["provider_period_code"]) for row in normalized["rows"]} == {
        ("JPN", "2023"),
        ("JPN", "2024"),
        ("USA", "2023"),
        ("USA", "2024"),
    }
    assert package.row_count == 4
    assert observed_package_fingerprint(package) == observed_package_fingerprint(build_ilostat_unemployment_observed_package(normalized))
