from __future__ import annotations

import hashlib
import json
from pathlib import Path

from macroforge.contract_drift import validate_observed_package_contract
from macroforge.eurostat_energy_balance import (
    build_eurostat_energy_balance_observed_package,
    normalize_eurostat_energy_balance_fixture,
)
from macroforge.observed_ingestion import canonical_attribute_hash, compare_observed_packages, observed_package_fingerprint

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_FIXTURE = PROJECT_ROOT / "data" / "raw" / "eurostat_energy_balance" / "eurostat-nrg-bal-c-de-fr-2022-2023-ktoe-pprd-imp-exp-fce-total-ra000.json"
CONTENT_TYPE = "application/json"
DATASET_CODE = "nrg_bal_c"
COUNTRIES = ("DE", "FR")
YEARS = ("2022", "2023")
BALANCE_COMPONENTS = ("PPRD", "IMP", "EXP", "FC_E")
FUELS = ("TOTAL", "RA000")

SAMPLE_VALUES = {
    ("PPRD", "TOTAL", "DE", "2022"): 88849.225,
    ("PPRD", "TOTAL", "DE", "2023"): 84382.374,
    ("PPRD", "TOTAL", "FR", "2022"): 135620.066,
    ("PPRD", "TOTAL", "FR", "2023"): 139010.242,
    ("PPRD", "RA000", "DE", "2022"): 38571.466,
    ("PPRD", "RA000", "DE", "2023"): 33820.848,
    ("PPRD", "RA000", "FR", "2022"): 31085.573,
    ("PPRD", "RA000", "FR", "2023"): 34009.456,
    ("IMP", "TOTAL", "DE", "2022"): 235165.251,
    ("IMP", "TOTAL", "DE", "2023"): 210619.587,
    ("IMP", "TOTAL", "FR", "2022"): 160101.484,
    ("IMP", "TOTAL", "FR", "2023"): 146824.783,
    ("IMP", "RA000", "DE", "2022"): 2778.398,
    ("IMP", "RA000", "DE", "2023"): 2673.524,
    ("IMP", "RA000", "FR", "2022"): 2484.012,
    ("IMP", "RA000", "FR", "2023"): 2660.307,
    ("EXP", "TOTAL", "DE", "2022"): 55998.418,
    ("EXP", "TOTAL", "DE", "2023"): 51044.422,
    ("EXP", "TOTAL", "FR", "2022"): 47718.274,
    ("EXP", "TOTAL", "FR", "2023"): 50098.604,
    ("EXP", "RA000", "DE", "2022"): 2858.466,
    ("EXP", "RA000", "DE", "2023"): 2875.192,
    ("EXP", "RA000", "FR", "2022"): 741.418,
    ("EXP", "RA000", "FR", "2023"): 650.991,
    ("FC_E", "TOTAL", "DE", "2022"): 189698.421,
    ("FC_E", "TOTAL", "DE", "2023"): 179048.225,
    ("FC_E", "TOTAL", "FR", "2022"): 134137.527,
    ("FC_E", "TOTAL", "FR", "2023"): 129009.684,
    ("FC_E", "RA000", "DE", "2022"): 18857.166,
    ("FC_E", "RA000", "DE", "2023"): 16936.822,
    ("FC_E", "RA000", "FR", "2022"): 16044.169,
    ("FC_E", "RA000", "FR", "2023"): 16775.314,
}


def _flat_index(*, nrg_bal: str, siec: str, geo: str, time: str) -> int:
    sizes = [1, 4, 2, 1, 2, 2]
    coords = [
        0,
        {code: index for index, code in enumerate(BALANCE_COMPONENTS)}[nrg_bal],
        {code: index for index, code in enumerate(FUELS)}[siec],
        0,
        {code: index for index, code in enumerate(COUNTRIES)}[geo],
        {code: index for index, code in enumerate(YEARS)}[time],
    ]
    index = 0
    for coord, size in zip(coords, sizes, strict=True):
        index = index * size + coord
    return index


def _sample_fixture_bytes() -> bytes:
    value = {
        str(_flat_index(nrg_bal=nrg_bal, siec=siec, geo=geo, time=time)): amount
        for (nrg_bal, siec, geo, time), amount in SAMPLE_VALUES.items()
    }
    payload = {
        "version": "2.0",
        "class": "dataset",
        "label": "Complete energy balances",
        "source": "ESTAT",
        "updated": "2026-06-02T23:00:00+0200",
        "id": ["freq", "nrg_bal", "siec", "unit", "geo", "time"],
        "size": [1, 4, 2, 1, 2, 2],
        "dimension": {
            "freq": {"category": {"index": {"A": 0}, "label": {"A": "Annual"}}},
            "nrg_bal": {
                "category": {
                    "index": {"PPRD": 0, "IMP": 1, "EXP": 2, "FC_E": 3},
                    "label": {
                        "PPRD": "Primary production",
                        "IMP": "Imports",
                        "EXP": "Exports",
                        "FC_E": "Final consumption - energy use",
                    },
                }
            },
            "siec": {"category": {"index": {"TOTAL": 0, "RA000": 1}, "label": {"TOTAL": "Total", "RA000": "Renewables and biofuels"}}},
            "unit": {"category": {"index": {"KTOE": 0}, "label": {"KTOE": "Thousand tonnes of oil equivalent"}}},
            "geo": {"category": {"index": {"DE": 0, "FR": 1}, "label": {"DE": "Germany", "FR": "France"}}},
            "time": {"category": {"index": {"2022": 0, "2023": 1}, "label": {"2022": "2022", "2023": "2023"}}},
        },
        "value": value,
    }
    wrapper = {
        "source": "Eurostat dissemination API",
        "scope": "bounded TASK-064 Eurostat energy balance evidence slice",
        "dataset_code": DATASET_CODE,
        "url": "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/nrg_bal_c?geo=DE&geo=FR&time=2022&time=2023&unit=KTOE&nrg_bal=PPRD&nrg_bal=IMP&nrg_bal=EXP&nrg_bal=FC_E&siec=TOTAL&siec=RA000&lang=en",
        "response": payload,
    }
    return json.dumps(wrapper, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _normalized_from_sample() -> dict:
    raw_payload = _sample_fixture_bytes()
    return normalize_eurostat_energy_balance_fixture(
        raw_payload,
        raw_artifact_path="data/raw/eurostat_energy_balance/eurostat-nrg-bal-c-de-fr-2022-2023-ktoe-pprd-imp-exp-fce-total-ra000.json",
        raw_sha256=hashlib.sha256(raw_payload).hexdigest(),
        content_type=CONTENT_TYPE,
    )


def test_eurostat_energy_balance_fixture_normalizes_bounded_energy_accounting_slice():
    normalized = _normalized_from_sample()

    assert normalized["source_code"] == "EUROSTAT_ENERGY_BALANCE"
    assert normalized["provider_dataset_code"] == DATASET_CODE
    assert normalized["dataset_label"] == "Complete energy balances"
    assert normalized["frequency"] == "A"
    assert normalized["period_range"] == "2022-2023"
    assert normalized["row_count"] == 32
    assert normalized["expected_row_count"] == 32
    assert normalized["energy_accounting_shape"] == {
        "balance_components": ["PPRD", "IMP", "EXP", "FC_E"],
        "energy_products": ["TOTAL", "RA000"],
        "geographies": ["DE", "FR"],
        "periods": ["2022", "2023"],
        "unit": "KTOE",
    }
    assert {
        (row["balance_component_code"], row["energy_product_code"], row["territory_code"], row["provider_period_code"])
        for row in normalized["rows"]
    } == set(SAMPLE_VALUES)

    row = next(
        row
        for row in normalized["rows"]
        if row["balance_component_code"] == "FC_E"
        and row["energy_product_code"] == "RA000"
        and row["territory_code"] == "FR"
        and row["provider_period_code"] == "2023"
    )
    assert row["value"] == 16775.314
    assert row["provider_indicator_code"] == "nrg_bal_c:FC_E:RA000"
    assert row["provider_indicator_label"] == "Final consumption - energy use — Renewables and biofuels"
    assert row["unit_code"] == "KTOE"
    assert row["unit_label"] == "Thousand tonnes of oil equivalent"
    assert row["energy_accounting_role"] == "energy_balance_component_by_product"
    assert row["attributes"]["balance_component_label"] == "Final consumption - energy use"
    assert row["attributes"]["energy_product_label"] == "Renewables and biofuels"
    assert row["attributes"]["jsonstat_flat_index"] == _flat_index(nrg_bal="FC_E", siec="RA000", geo="FR", time="2023")


def test_eurostat_energy_balance_observed_package_satisfies_existing_contract_without_contract_evolution():
    package = build_eurostat_energy_balance_observed_package(_normalized_from_sample())

    assert package.source_code == "EUROSTAT_ENERGY_BALANCE"
    assert package.source_name == "Eurostat bounded complete energy balance evidence slice"
    assert package.source_home_url == "https://ec.europa.eu/eurostat/"
    assert package.provider_dataset_code == DATASET_CODE
    assert package.release_key.startswith("EUROSTAT_ENERGY_BALANCE:nrg_bal_c:2022-2023:")
    assert package.row_count == 32
    assert package.expected_row_count == 32
    assert package.input_filters["scope"] == "bounded TASK-064 Eurostat energy balance evidence slice"
    assert package.input_filters["energy_products"] == ["TOTAL", "RA000"]

    observation = next(
        obs
        for obs in package.observations
        if obs.provider_indicator_code == "nrg_bal_c:IMP:TOTAL"
        and obs.provider_territory_code == "DE"
        and obs.provider_period_code == "2023"
    )
    assert observation.provider_indicator_label == "Imports — Total"
    assert observation.frequency == "A"
    assert observation.period_year == 2023
    assert observation.unit_code == "KTOE"
    assert observation.unit_label == "Thousand tonnes of oil equivalent"
    assert observation.value == 210619.587
    assert observation.observation_status == "observed"
    assert observation.decimal_precision == 3
    assert observation.attributes["energy_accounting_role"] == "energy_balance_component_by_product"
    assert observation.attributes["balance_component_code"] == "IMP"
    assert observation.attributes["energy_product_code"] == "TOTAL"
    assert observation.attribute_hash == canonical_attribute_hash(observation.attributes)

    report = validate_observed_package_contract(package)
    assert report.valid is True
    assert report.issues == ()


def test_eurostat_energy_balance_replay_and_fingerprint_are_deterministic():
    package = build_eurostat_energy_balance_observed_package(_normalized_from_sample())
    replayed = build_eurostat_energy_balance_observed_package(_normalized_from_sample())

    comparison = compare_observed_packages(package, replayed)

    assert comparison.equivalent is True
    assert comparison.left_fingerprint == comparison.right_fingerprint
    assert comparison.row_count_match is True
    assert comparison.expected_row_count_match is True
    assert comparison.observation_count_match is True
    assert comparison.differing_observations == ()
    assert len(observed_package_fingerprint(package)) == 64


def test_eurostat_energy_balance_module_remains_bounded_source_specific_not_energy_framework():
    source = (PROJECT_ROOT / "src" / "macroforge" / "eurostat_energy_balance.py").read_text(encoding="utf-8")

    forbidden = [
        "class EnergyFramework",
        "class EnergyBalanceFramework",
        "class FuelHierarchy",
        "canonical_energy",
        "KnowledgeForge",
        "CREATE TABLE",
        "postgres",
        "sqlalchemy",
    ]
    for token in forbidden:
        assert token not in source


def test_eurostat_energy_balance_recorded_fixture_replays_to_same_contract():
    assert RAW_FIXTURE.exists()
    raw_payload = RAW_FIXTURE.read_bytes()
    normalized = normalize_eurostat_energy_balance_fixture(
        raw_payload,
        raw_artifact_path="data/raw/eurostat_energy_balance/eurostat-nrg-bal-c-de-fr-2022-2023-ktoe-pprd-imp-exp-fce-total-ra000.json",
        raw_sha256=hashlib.sha256(raw_payload).hexdigest(),
        content_type=CONTENT_TYPE,
    )
    package = build_eurostat_energy_balance_observed_package(normalized)

    assert normalized["row_count"] == 32
    assert package.row_count == 32
    assert package.raw_evidence["raw_sha256"] == hashlib.sha256(raw_payload).hexdigest()
    assert validate_observed_package_contract(package).valid is True
