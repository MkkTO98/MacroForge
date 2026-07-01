from __future__ import annotations

import hashlib
import json
from pathlib import Path

from macroforge.contract_drift import validate_observed_package_contract
from macroforge.observed_ingestion import canonical_attribute_hash, compare_observed_packages, observed_package_fingerprint
from macroforge.wdi_demographics import (
    build_wdi_demographic_foundation_observed_package,
    normalize_wdi_demographic_foundation_fixture,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_FIXTURE = PROJECT_ROOT / "data" / "raw" / "wdi_demographics" / "wdi-demographic-foundation-usa-jpn-2022-2023.json"
CONTENT_TYPE = "application/json"
COUNTRIES = ("USA", "JPN")
YEARS = ("2022", "2023")
INDICATORS = (
    "SP.POP.TOTL",
    "SP.POP.GROW",
    "SP.POP.0014.TO.ZS",
    "SP.POP.1564.TO.ZS",
    "SP.POP.65UP.TO.ZS",
    "SP.DYN.TFRT.IN",
    "SP.DYN.LE00.IN",
    "SP.URB.TOTL.IN.ZS",
)

SAMPLE_VALUES = {
    ("SP.POP.TOTL", "JPN", "2023"): 124516650,
    ("SP.POP.TOTL", "JPN", "2022"): 125124989,
    ("SP.POP.TOTL", "USA", "2023"): 336755052,
    ("SP.POP.TOTL", "USA", "2022"): 333996304,
    ("SP.POP.GROW", "JPN", "2023"): -0.487370782049143,
    ("SP.POP.GROW", "JPN", "2022"): -0.443851919148528,
    ("SP.POP.GROW", "USA", "2023"): 0.822589035790284,
    ("SP.POP.GROW", "USA", "2022"): 0.569329881519084,
    ("SP.POP.0014.TO.ZS", "JPN", "2023"): 11.6492906162775,
    ("SP.POP.0014.TO.ZS", "JPN", "2022"): 11.8589361787474,
    ("SP.POP.0014.TO.ZS", "USA", "2023"): 17.5946376490897,
    ("SP.POP.0014.TO.ZS", "USA", "2022"): 17.8818251956671,
    ("SP.POP.1564.TO.ZS", "JPN", "2023"): 58.7888993029413,
    ("SP.POP.1564.TO.ZS", "JPN", "2022"): 58.7384165155584,
    ("SP.POP.1564.TO.ZS", "USA", "2023"): 64.9735428685564,
    ("SP.POP.1564.TO.ZS", "USA", "2022"): 65.1985544146872,
    ("SP.POP.65UP.TO.ZS", "JPN", "2023"): 29.5618100807812,
    ("SP.POP.65UP.TO.ZS", "JPN", "2022"): 29.4026473056942,
    ("SP.POP.65UP.TO.ZS", "USA", "2023"): 17.4318194823539,
    ("SP.POP.65UP.TO.ZS", "USA", "2022"): 16.9196203896458,
    ("SP.DYN.TFRT.IN", "JPN", "2023"): 1.2,
    ("SP.DYN.TFRT.IN", "JPN", "2022"): 1.26,
    ("SP.DYN.TFRT.IN", "USA", "2023"): 1.6165,
    ("SP.DYN.TFRT.IN", "USA", "2022"): 1.6565,
    ("SP.DYN.LE00.IN", "JPN", "2023"): 84.0412195121951,
    ("SP.DYN.LE00.IN", "JPN", "2022"): 83.9963414634146,
    ("SP.DYN.LE00.IN", "USA", "2023"): 78.3853658536585,
    ("SP.DYN.LE00.IN", "USA", "2022"): 77.4341463414634,
    ("SP.URB.TOTL.IN.ZS", "JPN", "2023"): 92.0826903891473,
    ("SP.URB.TOTL.IN.ZS", "JPN", "2022"): 91.9776532428406,
    ("SP.URB.TOTL.IN.ZS", "USA", "2023"): 80.071561119178,
    ("SP.URB.TOTL.IN.ZS", "USA", "2022"): 80.0324978239707,
}

INDICATOR_LABELS = {
    "SP.POP.TOTL": "Population, total",
    "SP.POP.GROW": "Population growth (annual %)",
    "SP.POP.0014.TO.ZS": "Population ages 0-14 (% of total population)",
    "SP.POP.1564.TO.ZS": "Population ages 15-64 (% of total population)",
    "SP.POP.65UP.TO.ZS": "Population ages 65 and above (% of total population)",
    "SP.DYN.TFRT.IN": "Fertility rate, total (births per woman)",
    "SP.DYN.LE00.IN": "Life expectancy at birth, total (years)",
    "SP.URB.TOTL.IN.ZS": "Urban population (% of total population)",
}


def _sample_fixture_bytes() -> bytes:
    requests = []
    for indicator in INDICATORS:
        rows = []
        for iso, country_name in (("JPN", "Japan"), ("USA", "United States")):
            for year in ("2023", "2022"):
                rows.append(
                    {
                        "indicator": {"id": indicator, "value": INDICATOR_LABELS[indicator]},
                        "country": {"id": "JP" if iso == "JPN" else "US", "value": country_name},
                        "countryiso3code": iso,
                        "date": year,
                        "value": SAMPLE_VALUES[(indicator, iso, year)],
                        "unit": "",
                        "obs_status": "",
                        "decimal": 0,
                    }
                )
        requests.append(
            {
                "indicator_code": indicator,
                "url": f"https://api.worldbank.org/v2/country/USA;JPN/indicator/{indicator}?format=json&date=2022:2023&per_page=1000",
                "response": [
                    {
                        "page": 1,
                        "pages": 1,
                        "per_page": "1000",
                        "total": 4,
                        "sourceid": "2",
                        "lastupdated": "2025-10-07",
                    },
                    rows,
                ],
            }
        )
    payload = {
        "source": "World Bank World Development Indicators API",
        "scope": "bounded TASK-061 WDI demographic foundation evidence slice",
        "countries": ["USA", "JPN"],
        "date_range": "2022:2023",
        "requests": requests,
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _normalized_from_sample() -> dict:
    raw_payload = _sample_fixture_bytes()
    return normalize_wdi_demographic_foundation_fixture(
        raw_payload,
        raw_artifact_path="data/raw/wdi_demographics/wdi-demographic-foundation-usa-jpn-2022-2023.json",
        raw_sha256=hashlib.sha256(raw_payload).hexdigest(),
        content_type=CONTENT_TYPE,
    )


def test_wdi_demographic_foundation_fixture_normalizes_required_foundation_slice():
    normalized = _normalized_from_sample()

    assert normalized["source_code"] == "WDI_DEMOGRAPHICS"
    assert normalized["provider_dataset_code"] == "WDI:DEMOGRAPHIC_FOUNDATION"
    assert normalized["frequency"] == "A"
    assert normalized["period_range"] == "2022-2023"
    assert normalized["row_count"] == 32
    assert normalized["expected_row_count"] == 32
    assert normalized["input_filters"] == {
        "countries": ["USA", "JPN"],
        "periods": ["2022", "2023"],
        "indicators": list(INDICATORS),
        "scope": "bounded TASK-061 WDI demographic foundation evidence slice",
    }
    assert {row["demographic_concept"] for row in normalized["rows"]} == {
        "population_total",
        "population_growth",
        "age_structure_0_14",
        "age_structure_15_64",
        "age_structure_65_plus",
        "fertility",
        "life_expectancy",
        "urbanization",
    }
    assert {(row["territory_code"], row["provider_period_code"]) for row in normalized["rows"]} == {
        (country, year) for country in COUNTRIES for year in YEARS
    }

    population = next(
        row
        for row in normalized["rows"]
        if row["provider_indicator_code"] == "SP.POP.TOTL" and row["territory_code"] == "JPN" and row["provider_period_code"] == "2023"
    )
    assert population["provider_indicator_label"] == "Population, total"
    assert population["territory_label"] == "Japan"
    assert population["unit_code"] == "PERSONS"
    assert population["unit_label"] == "persons"
    assert population["value"] == 124516650
    assert population["attributes"]["demographic_concept"] == "population_total"
    assert population["attributes"]["world_bank_sourceid"] == "2"

    fertility = next(
        row
        for row in normalized["rows"]
        if row["provider_indicator_code"] == "SP.DYN.TFRT.IN" and row["territory_code"] == "USA" and row["provider_period_code"] == "2023"
    )
    assert fertility["unit_code"] == "BIRTHS_PER_WOMAN"
    assert fertility["unit_label"] == "births per woman"
    assert fertility["value"] == 1.6165


def test_wdi_demographic_foundation_observed_package_satisfies_existing_contract_without_contract_evolution():
    package = build_wdi_demographic_foundation_observed_package(_normalized_from_sample())

    assert package.source_code == "WDI_DEMOGRAPHICS"
    assert package.source_name == "World Bank WDI bounded demographic foundation evidence slice"
    assert package.source_home_url == "https://data.worldbank.org/"
    assert package.provider_dataset_code == "WDI:DEMOGRAPHIC_FOUNDATION"
    assert package.release_key.startswith("WDI_DEMOGRAPHICS:USA-JPN:2022-2023:")
    assert package.row_count == 32
    assert package.expected_row_count == 32
    assert package.raw_evidence["raw_artifact_path"] == "data/raw/wdi_demographics/wdi-demographic-foundation-usa-jpn-2022-2023.json"
    assert len(package.raw_evidence["raw_sha256"]) == 64
    assert len(package.raw_evidence["source_urls"]) == 8

    observation = next(
        obs
        for obs in package.observations
        if obs.provider_indicator_code == "SP.URB.TOTL.IN.ZS" and obs.provider_territory_code == "JPN" and obs.provider_period_code == "2023"
    )
    assert observation.provider_indicator_label == "Urban population (% of total population)"
    assert observation.provider_territory_label == "Japan"
    assert observation.frequency == "A"
    assert observation.period_year == 2023
    assert observation.unit_code == "PERCENT_OF_TOTAL_POPULATION"
    assert observation.unit_label == "percent of total population"
    assert observation.value == 92.0826903891473
    assert observation.observation_status == "observed"
    assert observation.decimal_precision == 13
    assert observation.attribute_hash == canonical_attribute_hash(observation.attributes)

    report = validate_observed_package_contract(package)
    assert report.valid is True
    assert report.issues == ()


def test_wdi_demographic_foundation_replay_and_fingerprint_are_deterministic():
    package = build_wdi_demographic_foundation_observed_package(_normalized_from_sample())
    replayed = build_wdi_demographic_foundation_observed_package(_normalized_from_sample())

    comparison = compare_observed_packages(package, replayed)

    assert comparison.equivalent is True
    assert comparison.left_fingerprint == comparison.right_fingerprint
    assert comparison.row_count_match is True
    assert comparison.expected_row_count_match is True
    assert comparison.observation_count_match is True
    assert comparison.differing_observations == ()
    assert len(observed_package_fingerprint(package)) == 64


def test_wdi_demographic_foundation_module_remains_bounded_source_specific_not_demographic_or_provider_framework():
    source = (PROJECT_ROOT / "src" / "macroforge" / "wdi_demographics.py").read_text(encoding="utf-8")

    forbidden = [
        "class DemographicFramework",
        "class PopulationProjection",
        "class WdiClient",
        "class BaseSource",
        "class SourcePlugin",
        "PluginRegistry",
        "CREATE TABLE",
        "INSERT INTO",
        "requests.get",
        "urllib.request",
        "sqlalchemy",
        "forecast",
        "projection_scenario",
        "migration_system",
        "canonical_load",
    ]
    for token in forbidden:
        assert token not in source


def test_project_wdi_demographic_foundation_fixture_preserves_live_bounded_evidence_when_present():
    if not RAW_FIXTURE.exists():
        return

    raw_payload = RAW_FIXTURE.read_bytes()
    normalized = normalize_wdi_demographic_foundation_fixture(
        raw_payload,
        raw_artifact_path=str(RAW_FIXTURE.relative_to(PROJECT_ROOT)),
        raw_sha256=hashlib.sha256(raw_payload).hexdigest(),
        content_type=CONTENT_TYPE,
    )
    package = build_wdi_demographic_foundation_observed_package(normalized)

    assert normalized["row_count"] == 32
    assert normalized["expected_row_count"] == 32
    assert len({row["provider_indicator_code"] for row in normalized["rows"]}) == 8
    assert len({row["territory_code"] for row in normalized["rows"]}) == 2
    assert len({row["provider_period_code"] for row in normalized["rows"]}) == 2
    assert next(
        row["value"]
        for row in normalized["rows"]
        if row["provider_indicator_code"] == "SP.POP.TOTL" and row["territory_code"] == "USA" and row["provider_period_code"] == "2023"
    ) == 336755052
    assert package.row_count == 32
    assert observed_package_fingerprint(package) == observed_package_fingerprint(
        build_wdi_demographic_foundation_observed_package(normalized)
    )
