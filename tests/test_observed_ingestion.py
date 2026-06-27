from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from dataclasses import replace

from macroforge.observed_ingestion import (
    EMPTY_ATTRIBUTE_HASH,
    build_eurostat_observed_package,
    build_oecd_observed_package,
    build_wdi_observed_package,
    canonical_attribute_hash,
    compare_observed_packages,
    observed_package_fingerprint,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
WDI_NORMALIZED = PROJECT_ROOT / "data" / "metadata" / "wdi" / "wdi-smoke-normalized.json"
OECD_NORMALIZED = PROJECT_ROOT / "data" / "metadata" / "oecd_sdmx" / "oecd-sdmx-smoke-normalized.json"
EUROSTAT_NORMALIZED = PROJECT_ROOT / "data" / "metadata" / "eurostat" / "eurostat-namq-10-gdp-architecture-spike-normalized.json"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def test_wdi_observed_package_preserves_existing_loader_semantics():
    package = build_wdi_observed_package(_load(WDI_NORMALIZED))

    assert package.source_code == "WDI"
    assert package.source_name == "World Bank World Development Indicators"
    assert package.source_home_url == "https://data.worldbank.org/"
    assert package.provider_dataset_code == "WDI"
    assert package.release_key == "WDI:2026-04-08:2020:2021"
    assert package.row_count == 8
    assert package.expected_row_count == 8
    assert package.input_filters == {
        "countries": ["USA", "DNK"],
        "indicators": ["NY.GDP.MKTP.CD", "SP.POP.TOTL"],
        "date_range": "2020:2021",
    }
    assert package.raw_evidence["raw_sha256"] == ";".join(
        artifact["sha256"] for artifact in _load(WDI_NORMALIZED)["raw_artifacts"]
    )

    observation = package.observations[0]
    assert observation.provider_indicator_code == "NY.GDP.MKTP.CD"
    assert observation.provider_indicator_label == "GDP (current US$)"
    assert observation.provider_territory_code == "DNK"
    assert observation.provider_territory_label == "Denmark"
    assert observation.provider_period_code == "2021"
    assert observation.frequency == "A"
    assert observation.period_year == 2021
    assert observation.unit_code == "unknown"
    assert observation.value == 406110162088.054
    assert observation.observation_status == "observed"
    assert observation.decimal_precision == 0
    assert observation.attributes == {}
    assert observation.attribute_hash == EMPTY_ATTRIBUTE_HASH
    assert observation.source_payload == _load(WDI_NORMALIZED)["rows"][0]


def test_oecd_observed_package_preserves_existing_loader_semantics():
    package = build_oecd_observed_package(_load(OECD_NORMALIZED))

    assert package.source_code == "OECD_NAAG"
    assert package.source_name == "OECD annual national accounts / NAAG Chapter 1 GDP dataflow"
    assert package.source_home_url == "https://sdmx.oecd.org/"
    assert package.provider_dataset_code == "OECD.SDD.NAD,DSD_NAAG@DF_NAAG_I"
    assert package.release_key.startswith("OECD_NAAG:OECD.SDD.NAD,DSD_NAAG@DF_NAAG_I:2020-2021:")
    assert package.row_count == 8
    assert package.expected_row_count == 8
    assert package.input_filters == {
        "filters": _load(OECD_NORMALIZED)["filters"],
        "provider_dataset_code": "OECD.SDD.NAD,DSD_NAAG@DF_NAAG_I",
    }

    observations = package.observations
    assert {observation.unit_code for observation in observations} == {"USD_EXC", "USD_PPP"}
    assert {observation.frequency for observation in observations} == {"A"}
    assert {observation.attribute_hash for observation in observations} == {
        canonical_attribute_hash({"CONF_STATUS": "F", "DECIMALS": "2", "OBS_STATUS": "A"})
    }
    observation = observations[0]
    assert observation.provider_indicator_code == "B1GQ"
    assert observation.provider_indicator_label == "B1GQ"
    assert observation.provider_territory_code == "AUS"
    assert observation.provider_territory_label == "AUS"
    assert observation.provider_period_code == "2020"
    assert observation.period_year == 2020
    assert observation.observation_status == "observed"
    assert observation.decimal_precision == 2
    assert observation.attributes == {"CONF_STATUS": "F", "DECIMALS": "2", "OBS_STATUS": "A"}
    assert observation.source_payload == _load(OECD_NORMALIZED)["rows"][0]["source_payload"]


def test_eurostat_observed_package_preserves_existing_loader_semantics():
    package = build_eurostat_observed_package(_load(EUROSTAT_NORMALIZED))

    assert package.source_code == "EUROSTAT_NAMQ_GDP"
    assert package.source_name == "Eurostat quarterly national accounts GDP"
    assert package.source_home_url == "https://ec.europa.eu/eurostat/"
    assert package.provider_dataset_code == "namq_10_gdp"
    assert package.release_key.startswith("EUROSTAT_NAMQ_GDP:namq_10_gdp:2023-Q1-2023-Q2:")
    assert package.row_count == 4
    assert package.expected_row_count == 4
    assert package.input_filters == {
        "filters": _load(EUROSTAT_NORMALIZED)["filters"],
        "provider_dataset_code": "namq_10_gdp",
    }

    observation = package.observations[0]
    assert observation.provider_indicator_code == "B1GQ"
    assert observation.provider_indicator_label == "Gross domestic product at market prices"
    assert observation.provider_territory_code == "DE"
    assert observation.provider_territory_label == "Germany"
    assert observation.provider_period_code == "2023-Q1"
    assert observation.frequency == "Q"
    assert observation.period_year == 2023
    assert observation.period_quarter == 1
    assert observation.unit_code == "CP_MEUR"
    assert observation.unit_label == "Current prices, million euro"
    assert observation.value == 1043520.0
    assert observation.observation_status == "observed"
    assert observation.decimal_precision is None
    assert observation.attributes == {
        "source": "Eurostat",
        "provider_dataset_code": "namq_10_gdp",
        "freq": "Q",
        "s_adj": "NSA",
        "s_adj_label": "Unadjusted data (i.e. neither seasonally adjusted nor calendar adjusted data)",
        "observation_status": "observed",
        "jsonstat_status": "p",
    }
    assert observation.attribute_hash == canonical_attribute_hash(observation.attributes)
    assert observation.source_payload == _load(EUROSTAT_NORMALIZED)["rows"][0]["source_payload"]



def test_observed_package_fingerprint_is_deterministic_for_replayed_package():
    package = build_wdi_observed_package(_load(WDI_NORMALIZED))

    first = observed_package_fingerprint(package)
    second = observed_package_fingerprint(build_wdi_observed_package(_load(WDI_NORMALIZED)))

    assert first == second
    assert len(first) == 64
    assert all(character in "0123456789abcdef" for character in first)


def test_compare_observed_packages_reports_equivalent_replay():
    package = build_oecd_observed_package(_load(OECD_NORMALIZED))

    comparison = compare_observed_packages(package, build_oecd_observed_package(_load(OECD_NORMALIZED)))

    assert comparison.equivalent is True
    assert comparison.left_fingerprint == comparison.right_fingerprint
    assert comparison.row_count_match is True
    assert comparison.expected_row_count_match is True
    assert comparison.observation_count_match is True
    assert comparison.differing_observations == ()


def test_compare_observed_packages_reports_deterministic_observation_difference():
    package = build_eurostat_observed_package(_load(EUROSTAT_NORMALIZED))
    changed_observations = list(package.observations)
    changed_observations[0] = replace(changed_observations[0], value=changed_observations[0].value + 1)
    changed = replace(package, observations=tuple(changed_observations))

    comparison = compare_observed_packages(package, changed)

    assert comparison.equivalent is False
    assert comparison.left_fingerprint != comparison.right_fingerprint
    assert comparison.row_count_match is True
    assert comparison.expected_row_count_match is True
    assert comparison.observation_count_match is True
    assert comparison.differing_observations == (
        {
            "index": 0,
            "provider_indicator_code": "B1GQ",
            "provider_territory_code": "DE",
            "provider_period_code": "2023-Q1",
            "changed_fields": ("value",),
        },
    )


def test_observed_ingestion_module_is_not_a_generalized_framework():
    source = (PROJECT_ROOT / "src" / "macroforge" / "observed_ingestion.py").read_text(encoding="utf-8")

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
