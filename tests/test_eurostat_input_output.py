from __future__ import annotations

import hashlib
import json
from pathlib import Path

from macroforge.contract_drift import validate_observed_package_contract
from macroforge.observed_ingestion import canonical_attribute_hash, compare_observed_packages, observed_package_fingerprint
from macroforge.eurostat_input_output import (
    build_eurostat_input_output_observed_package,
    normalize_eurostat_input_output_fixture,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_FIXTURE = PROJECT_ROOT / "data" / "raw" / "eurostat_input_output" / "eurostat-naio-10-cp1700-de-fr-2020-dom-imp-cpa-a01-cpa-c10-12.json"
CONTENT_TYPE = "application/json"
DATASET_CODE = "naio_10_cp1700"
COUNTRIES = ("DE", "FR")
YEAR = "2020"
STOCK_FLOWS = ("IMP", "DOM")
PRODUCTS = ("CPA_A01", "CPA_C10-12")

SAMPLE_VALUES = {
    ("IMP", "CPA_A01", "CPA_A01", "DE"): 583,
    ("IMP", "CPA_A01", "CPA_A01", "FR"): 1130.11,
    ("IMP", "CPA_A01", "CPA_C10-12", "DE"): 344,
    ("IMP", "CPA_A01", "CPA_C10-12", "FR"): 563.63,
    ("IMP", "CPA_C10-12", "CPA_A01", "DE"): 15473,
    ("IMP", "CPA_C10-12", "CPA_A01", "FR"): 3562.59,
    ("IMP", "CPA_C10-12", "CPA_C10-12", "DE"): 7651,
    ("IMP", "CPA_C10-12", "CPA_C10-12", "FR"): 6292.46,
    ("DOM", "CPA_A01", "CPA_A01", "DE"): 1813,
    ("DOM", "CPA_A01", "CPA_A01", "FR"): 10570.82,
    ("DOM", "CPA_A01", "CPA_C10-12", "DE"): 1870,
    ("DOM", "CPA_A01", "CPA_C10-12", "FR"): 4925.46,
    ("DOM", "CPA_C10-12", "CPA_A01", "DE"): 29088,
    ("DOM", "CPA_C10-12", "CPA_A01", "FR"): 33323.72,
    ("DOM", "CPA_C10-12", "CPA_C10-12", "DE"): 22011,
    ("DOM", "CPA_C10-12", "CPA_C10-12", "FR"): 21175.38,
}


def _flat_index(*, stk_flow: str, prd_use: str, prd_ava: str, geo: str) -> int:
    sizes = [1, 1, 2, 2, 2, 2, 1]
    coords = [
        0,
        0,
        {code: index for index, code in enumerate(STOCK_FLOWS)}[stk_flow],
        {code: index for index, code in enumerate(PRODUCTS)}[prd_use],
        {code: index for index, code in enumerate(PRODUCTS)}[prd_ava],
        {code: index for index, code in enumerate(COUNTRIES)}[geo],
        0,
    ]
    index = 0
    for coord, size in zip(coords, sizes, strict=True):
        index = index * size + coord
    return index


def _sample_fixture_bytes() -> bytes:
    value = {
        str(_flat_index(stk_flow=flow, prd_use=prd_use, prd_ava=prd_ava, geo=geo)): amount
        for (flow, prd_use, prd_ava, geo), amount in SAMPLE_VALUES.items()
    }
    payload = {
        "version": "2.0",
        "class": "dataset",
        "label": "Symmetric input-output table at basic prices (product by product)",
        "source": "ESTAT",
        "updated": "2026-04-30T23:00:00+0200",
        "id": ["freq", "unit", "stk_flow", "prd_use", "prd_ava", "geo", "time"],
        "size": [1, 1, 2, 2, 2, 2, 1],
        "dimension": {
            "freq": {"category": {"index": {"A": 0}, "label": {"A": "Annual"}}},
            "unit": {"category": {"index": {"MIO_EUR": 0}, "label": {"MIO_EUR": "Million euro"}}},
            "stk_flow": {"category": {"index": {"IMP": 0, "DOM": 1}, "label": {"IMP": "Imports", "DOM": "Domestic uses"}}},
            "prd_use": {
                "category": {
                    "index": {"CPA_A01": 0, "CPA_C10-12": 1},
                    "label": {
                        "CPA_A01": "Products of agriculture, hunting and related services",
                        "CPA_C10-12": "Food, beverages and tobacco products",
                    },
                }
            },
            "prd_ava": {
                "category": {
                    "index": {"CPA_A01": 0, "CPA_C10-12": 1},
                    "label": {
                        "CPA_A01": "Products of agriculture, hunting and related services",
                        "CPA_C10-12": "Food, beverages and tobacco products",
                    },
                }
            },
            "geo": {"category": {"index": {"DE": 0, "FR": 1}, "label": {"DE": "Germany", "FR": "France"}}},
            "time": {"category": {"index": {"2020": 0}, "label": {"2020": "2020"}}},
        },
        "value": value,
    }
    wrapper = {
        "source": "Eurostat dissemination API",
        "scope": "bounded TASK-062 Eurostat input-output matrix evidence slice",
        "dataset_code": DATASET_CODE,
        "url": "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/naio_10_cp1700?geo=DE&geo=FR&time=2020&unit=MIO_EUR&stk_flow=DOM&stk_flow=IMP&prd_use=CPA_A01&prd_use=CPA_C10-12&prd_ava=CPA_A01&prd_ava=CPA_C10-12&lang=en",
        "response": payload,
    }
    return json.dumps(wrapper, sort_keys=True, separators=(",", ":")).encode("utf-8")


def _normalized_from_sample() -> dict:
    raw_payload = _sample_fixture_bytes()
    return normalize_eurostat_input_output_fixture(
        raw_payload,
        raw_artifact_path="data/raw/eurostat_input_output/eurostat-naio-10-cp1700-de-fr-2020-dom-imp-cpa-a01-cpa-c10-12.json",
        raw_sha256=hashlib.sha256(raw_payload).hexdigest(),
        content_type=CONTENT_TYPE,
    )


def test_eurostat_input_output_fixture_normalizes_bounded_matrix_slice():
    normalized = _normalized_from_sample()

    assert normalized["source_code"] == "EUROSTAT_INPUT_OUTPUT"
    assert normalized["provider_dataset_code"] == DATASET_CODE
    assert normalized["dataset_label"] == "Symmetric input-output table at basic prices (product by product)"
    assert normalized["frequency"] == "A"
    assert normalized["period_range"] == "2020-2020"
    assert normalized["row_count"] == 16
    assert normalized["expected_row_count"] == 16
    assert normalized["matrix_shape"] == {
        "stock_flows": ["IMP", "DOM"],
        "products_used": ["CPA_A01", "CPA_C10-12"],
        "products_available": ["CPA_A01", "CPA_C10-12"],
        "geographies": ["DE", "FR"],
        "periods": ["2020"],
    }

    assert {
        (row["stock_flow_code"], row["product_used_code"], row["product_available_code"], row["territory_code"])
        for row in normalized["rows"]
    } == set(SAMPLE_VALUES)

    cell = next(
        row
        for row in normalized["rows"]
        if row["stock_flow_code"] == "DOM"
        and row["product_used_code"] == "CPA_C10-12"
        and row["product_available_code"] == "CPA_A01"
        and row["territory_code"] == "FR"
    )
    assert cell["value"] == 33323.72
    assert cell["provider_indicator_code"] == "naio_10_cp1700:DOM:CPA_A01->CPA_C10-12"
    assert cell["provider_indicator_label"] == "Domestic uses: Products of agriculture, hunting and related services available to Food, beverages and tobacco products"
    assert cell["unit_code"] == "MIO_EUR"
    assert cell["unit_label"] == "Million euro"
    assert cell["matrix_role"] == "product_by_product_input_output_cell"
    assert cell["attributes"]["stock_flow_label"] == "Domestic uses"
    assert cell["attributes"]["product_available_label"] == "Products of agriculture, hunting and related services"
    assert cell["attributes"]["product_used_label"] == "Food, beverages and tobacco products"


def test_eurostat_input_output_observed_package_satisfies_existing_contract_without_contract_evolution():
    package = build_eurostat_input_output_observed_package(_normalized_from_sample())

    assert package.source_code == "EUROSTAT_INPUT_OUTPUT"
    assert package.source_name == "Eurostat bounded symmetric input-output matrix evidence slice"
    assert package.source_home_url == "https://ec.europa.eu/eurostat/"
    assert package.provider_dataset_code == DATASET_CODE
    assert package.release_key.startswith("EUROSTAT_INPUT_OUTPUT:naio_10_cp1700:2020-2020:")
    assert package.row_count == 16
    assert package.expected_row_count == 16
    assert package.raw_evidence["raw_artifact_path"] == "data/raw/eurostat_input_output/eurostat-naio-10-cp1700-de-fr-2020-dom-imp-cpa-a01-cpa-c10-12.json"
    assert len(package.raw_evidence["raw_sha256"]) == 64
    assert package.input_filters["matrix_shape"] == "product_by_product"

    observation = next(
        obs
        for obs in package.observations
        if obs.provider_indicator_code == "naio_10_cp1700:IMP:CPA_A01->CPA_C10-12"
        and obs.provider_territory_code == "DE"
    )
    assert observation.provider_indicator_label == "Imports: Products of agriculture, hunting and related services available to Food, beverages and tobacco products"
    assert observation.provider_period_code == "2020"
    assert observation.frequency == "A"
    assert observation.period_year == 2020
    assert observation.unit_code == "MIO_EUR"
    assert observation.unit_label == "Million euro"
    assert observation.value == 15473
    assert observation.observation_status == "observed"
    assert observation.decimal_precision == 0
    assert observation.attributes["matrix_role"] == "product_by_product_input_output_cell"
    assert observation.attributes["product_available_code"] == "CPA_A01"
    assert observation.attributes["product_used_code"] == "CPA_C10-12"
    assert observation.attribute_hash == canonical_attribute_hash(observation.attributes)

    report = validate_observed_package_contract(package)
    assert report.valid is True
    assert report.issues == ()


def test_eurostat_input_output_replay_and_fingerprint_are_deterministic():
    package = build_eurostat_input_output_observed_package(_normalized_from_sample())
    replayed = build_eurostat_input_output_observed_package(_normalized_from_sample())

    comparison = compare_observed_packages(package, replayed)

    assert comparison.equivalent is True
    assert comparison.left_fingerprint == comparison.right_fingerprint
    assert comparison.row_count_match is True
    assert comparison.expected_row_count_match is True
    assert comparison.observation_count_match is True
    assert comparison.differing_observations == ()
    assert len(observed_package_fingerprint(package)) == 64


def test_eurostat_input_output_module_remains_bounded_source_specific_not_matrix_or_io_framework():
    source = (PROJECT_ROOT / "src" / "macroforge" / "eurostat_input_output.py").read_text(encoding="utf-8")

    forbidden = [
        "class MatrixFramework",
        "class InputOutputFramework",
        "class SupplyUseFramework",
        "class CpaClassificationFramework",
        "class EurostatClient",
        "Leontief",
        "multiplier",
        "canonical loading",
        "KnowledgeForge",
    ]
    for text in forbidden:
        assert text not in source


def test_eurostat_input_output_recorded_fixture_matches_expected_shape_when_present():
    if not RAW_FIXTURE.exists():
        return

    raw_payload = RAW_FIXTURE.read_bytes()
    normalized = normalize_eurostat_input_output_fixture(
        raw_payload,
        raw_artifact_path="data/raw/eurostat_input_output/eurostat-naio-10-cp1700-de-fr-2020-dom-imp-cpa-a01-cpa-c10-12.json",
        raw_sha256=hashlib.sha256(raw_payload).hexdigest(),
        content_type=CONTENT_TYPE,
    )
    package = build_eurostat_input_output_observed_package(normalized)

    assert normalized["row_count"] == 16
    assert package.row_count == 16
    assert validate_observed_package_contract(package).valid is True
    assert normalized["matrix_shape"] == {
        "stock_flows": ["IMP", "DOM"],
        "products_used": ["CPA_A01", "CPA_C10-12"],
        "products_available": ["CPA_A01", "CPA_C10-12"],
        "geographies": ["DE", "FR"],
        "periods": ["2020"],
    }
