from __future__ import annotations

import hashlib
from pathlib import Path

from macroforge.contract_drift import validate_observed_package_contract
from macroforge.observed_ingestion import (
    canonical_attribute_hash,
    compare_observed_packages,
    observed_package_fingerprint,
)
from macroforge.wdi_energy_use_coal_electricity import (
    build_wdi_energy_use_coal_electricity_observed_package,
    normalize_wdi_energy_use_coal_electricity_fixture,
)
from synthetic_wdi import synthetic_fixture_json

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONTENT_TYPE = "application/json"


def _normalized_from_sample():
    raw = synthetic_fixture_json("energy_bounded")
    return normalize_wdi_energy_use_coal_electricity_fixture(
        raw,
        raw_artifact_path="tests/synthetic_wdi.py#energy_bounded",
        raw_sha256=hashlib.sha256(raw.encode("utf-8")).hexdigest(),
        content_type=CONTENT_TYPE,
    )


def test_wdi_energy_use_coal_electricity_fixture_is_persisted_with_expected_hash() -> None:
    raw = synthetic_fixture_json("energy_bounded")

    assert '"scope": "bounded TASK-096 WDI energy use and coal-electricity evidence slice"' in raw
    assert '"EG.USE.PCAP.KG.OE"' in raw
    assert '"EG.ELC.COAL.ZS"' in raw
    assert '"countryiso3code": "USA"' in raw
    assert '"countryiso3code": "CHN"' in raw
    assert "example.invalid" in raw
    assert "api.worldbank.org" not in raw


def test_wdi_energy_use_coal_electricity_normalizes_bounded_rows() -> None:
    normalized = _normalized_from_sample()

    assert normalized["source_code"] == "WDI_ENERGY_USE_COAL_ELECTRICITY"
    assert normalized["provider_dataset_code"] == "WDI:ENERGY_USE_COAL_ELECTRICITY"
    assert normalized["content_type"] == CONTENT_TYPE
    assert normalized["row_count"] == 8
    assert normalized["expected_row_count"] == 8
    assert normalized["input_filters"] == {
        "countries": ["USA", "CHN"],
        "periods": ["2020", "2021"],
        "indicators": ["EG.USE.PCAP.KG.OE", "EG.ELC.COAL.ZS"],
        "scope": "bounded TASK-096 WDI energy use and coal-electricity evidence slice",
    }

    first = normalized["rows"][0]
    assert first["provider_indicator_code"] == "EG.USE.PCAP.KG.OE"
    assert first["territory_code"] == "CHN"
    assert first["provider_period_code"] == "2020"
    assert first["value"] == "100.25"
    assert first["energy_concept"] == "energy_use_per_capita"

    coal = [row for row in normalized["rows"] if row["provider_indicator_code"] == "EG.ELC.COAL.ZS" and row["territory_code"] == "USA" and row["provider_period_code"] == "2021"][0]
    assert coal["value"] == "1000001.25"
    assert coal["energy_concept"] == "coal_electricity_share"


def test_wdi_energy_use_coal_electricity_builds_observed_package_with_metadata() -> None:
    package = build_wdi_energy_use_coal_electricity_observed_package(_normalized_from_sample())

    assert package.source_code == "WDI_ENERGY_USE_COAL_ELECTRICITY"
    assert package.source_name == "World Bank WDI bounded energy use and coal-electricity evidence slice"
    assert package.source_home_url == "https://data.worldbank.org/"
    assert package.provider_dataset_code == "WDI:ENERGY_USE_COAL_ELECTRICITY"
    assert package.release_key.startswith("WDI_ENERGY_USE_COAL_ELECTRICITY:2020-2021:")
    assert package.raw_evidence["raw_sha256"] == hashlib.sha256(
        synthetic_fixture_json("energy_bounded").encode("utf-8")
    ).hexdigest()
    assert package.raw_evidence["content_type"] == CONTENT_TYPE
    assert package.row_count == 8
    assert package.expected_row_count == 8

    first = package.observations[0]
    assert first.provider_indicator_code == "EG.USE.PCAP.KG.OE"
    assert first.provider_indicator_label == "Synthetic Indicator 1"
    assert first.provider_territory_code == "CHN"
    assert first.provider_territory_label == "Synthetic Territory CHN"
    assert first.provider_period_code == "2020"
    assert first.frequency == "A"
    assert first.period_year == 2020
    assert first.value == "100.25"
    assert first.unit_code == "KG_OIL_EQUIVALENT_PER_CAPITA"
    assert first.unit_label == "kg of oil equivalent per capita"
    assert first.observation_status == "observed"
    assert first.attributes == {
        "source_provider": "World Bank WDI",
        "observation_family": "energy_intensity_and_electricity_mix",
        "energy_concept": "energy_use_per_capita",
        "energy_group": "energy_intensity",
        "indicator_id": "EG.USE.PCAP.KG.OE",
        "indicator_label": "Synthetic Indicator 1",
        "country_id": "CN",
        "countryiso3code": "CHN",
        "country_name": "Synthetic Territory CHN",
        "unit_code": "KG_OIL_EQUIVALENT_PER_CAPITA",
        "unit_label": "kg of oil equivalent per capita",
        "frequency": "A",
    }
    assert first.attribute_hash == canonical_attribute_hash(first.attributes)
    assert first.source_payload["raw_artifact_path"] == "tests/synthetic_wdi.py#energy_bounded"
    assert first.source_payload["request_metadata"]["lastupdated"]

    coal = [obs for obs in package.observations if obs.provider_indicator_code == "EG.ELC.COAL.ZS" and obs.provider_territory_code == "USA" and obs.provider_period_code == "2021"][0]
    assert coal.attributes["energy_concept"] == "coal_electricity_share"
    assert coal.unit_code == "PERCENT_OF_TOTAL"
    assert validate_observed_package_contract(package).valid is True


def test_wdi_energy_use_coal_electricity_replay_is_deterministic() -> None:
    package = build_wdi_energy_use_coal_electricity_observed_package(_normalized_from_sample())
    replayed = build_wdi_energy_use_coal_electricity_observed_package(_normalized_from_sample())

    assert compare_observed_packages(package, replayed).equivalent is True
    assert observed_package_fingerprint(package) == observed_package_fingerprint(replayed)
    assert observed_package_fingerprint(package) == "8a27589ba82af790514471611087fe82c03f13ad453888d95c7a7fba18a15d58"


def test_wdi_energy_use_coal_electricity_does_not_introduce_forbidden_frameworks() -> None:
    forbidden_paths = [
        PROJECT_ROOT / "src" / "macroforge" / "wdi_client.py",
        PROJECT_ROOT / "src" / "macroforge" / "energy_framework.py",
        PROJECT_ROOT / "src" / "macroforge" / "climate_transition_framework.py",
        PROJECT_ROOT / "src" / "macroforge" / "electricity_mix_ontology.py",
        PROJECT_ROOT / "src" / "macroforge" / "wdi_energy_use_coal_electricity_loader.py",
        PROJECT_ROOT / "src" / "macroforge" / "knowledgeforge_energy_semantics.py",
    ]

    assert not any(path.exists() for path in forbidden_paths)
