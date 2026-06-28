from __future__ import annotations

import hashlib
import json
from pathlib import Path

from macroforge.bls_cpi import build_bls_cpi_observed_package, normalize_bls_cpi_fixture
from macroforge.contract_drift import validate_observed_package_contract
from macroforge.observed_ingestion import EMPTY_ATTRIBUTE_HASH, observed_package_fingerprint

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BLS_RAW = PROJECT_ROOT / "data" / "raw" / "bls" / "bls-cpi-cuur0000sa0-2023-raw.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_bounded_bls_cpi_fixture_normalizes_one_monthly_series_without_framework():
    normalized = normalize_bls_cpi_fixture(
        _load(BLS_RAW),
        raw_artifact_path=str(BLS_RAW.relative_to(PROJECT_ROOT)),
        raw_sha256=_sha256(BLS_RAW),
        source_url="https://api.bls.gov/publicAPI/v2/timeseries/data/CUUR0000SA0?startyear=2023&endyear=2023",
    )

    assert normalized["provider_dataset_code"] == "BLS_PUBLIC_API_V2_TIMESERIES"
    assert normalized["series_id"] == "CUUR0000SA0"
    assert normalized["series_label"] == "CPI-U, U.S. city average, all items"
    assert normalized["territory_code"] == "USA"
    assert normalized["territory_label"] == "United States"
    assert normalized["frequency"] == "M"
    assert normalized["period_range"] == "2023-M01-2023-M12"
    assert normalized["row_count"] == 12
    assert [row["provider_period_code"] for row in normalized["rows"][:3]] == ["2023-M01", "2023-M02", "2023-M03"]
    first = normalized["rows"][0]
    assert first == {
        "series_id": "CUUR0000SA0",
        "series_label": "CPI-U, U.S. city average, all items",
        "territory_code": "USA",
        "territory_label": "United States",
        "provider_period_code": "2023-M01",
        "frequency": "M",
        "period_year": 2023,
        "period_month": 1,
        "unit_code": "INDEX_1982_84_100",
        "unit_label": "Index 1982-84=100",
        "value": 299.17,
        "observation_status": "observed",
        "decimal_precision": 3,
        "attributes": {"footnotes": [], "period_name": "January"},
        "source_payload": {
            "year": "2023",
            "period": "M01",
            "periodName": "January",
            "value": "299.170",
            "footnotes": [{}],
        },
    }


def test_bounded_bls_cpi_observed_package_requires_only_minimal_monthly_contract_evolution():
    normalized = normalize_bls_cpi_fixture(
        _load(BLS_RAW),
        raw_artifact_path=str(BLS_RAW.relative_to(PROJECT_ROOT)),
        raw_sha256=_sha256(BLS_RAW),
        source_url="https://api.bls.gov/publicAPI/v2/timeseries/data/CUUR0000SA0?startyear=2023&endyear=2023",
    )

    package = build_bls_cpi_observed_package(normalized)
    report = validate_observed_package_contract(package)

    assert package.source_code == "BLS_CPI"
    assert package.source_name == "U.S. Bureau of Labor Statistics CPI bounded monthly evidence slice"
    assert package.provider_dataset_code == "BLS_PUBLIC_API_V2_TIMESERIES"
    assert package.release_key == "BLS_CPI:CUUR0000SA0:2023-M01-2023-M12:55bd2b4ae23f"
    assert package.row_count == 12
    assert package.expected_row_count == 12
    assert package.input_filters == {
        "series_id": "CUUR0000SA0",
        "startyear": "2023",
        "endyear": "2023",
        "scope": "bounded TASK-051 architectural experiment",
    }
    assert report.valid is True
    assert report.issues == ()
    assert len(observed_package_fingerprint(package)) == 64

    first = package.observations[0]
    assert first.provider_indicator_code == "CUUR0000SA0"
    assert first.provider_indicator_label == "CPI-U, U.S. city average, all items"
    assert first.provider_territory_code == "USA"
    assert first.provider_territory_label == "United States"
    assert first.provider_period_code == "2023-M01"
    assert first.frequency == "M"
    assert first.period_year == 2023
    assert first.period_quarter is None
    assert first.period_month == 1
    assert first.unit_code == "INDEX_1982_84_100"
    assert first.unit_label == "Index 1982-84=100"
    assert first.value == 299.17
    assert first.observation_status == "observed"
    assert first.decimal_precision == 3
    assert first.attributes == {"footnotes": [], "period_name": "January"}
    assert first.attribute_hash != EMPTY_ATTRIBUTE_HASH
    assert first.source_payload == normalized["rows"][0]["source_payload"]


def test_bls_cpi_module_remains_source_specific_not_a_generalized_series_framework():
    source = (PROJECT_ROOT / "src" / "macroforge" / "bls_cpi.py").read_text(encoding="utf-8")

    forbidden = [
        "class BaseSource",
        "class SeriesFramework",
        "PluginRegistry",
        "requests.get",
        "urllib.request",
        "sqlalchemy",
        "CREATE TABLE",
        "INSERT INTO",
    ]
    for token in forbidden:
        assert token not in source
