from __future__ import annotations

import hashlib
from pathlib import Path

from macroforge.contract_drift import validate_observed_package_contract
from macroforge.fred_yield_curve import build_fred_yield_curve_observed_package, normalize_fred_yield_curve_fixture
from macroforge.observed_ingestion import canonical_attribute_hash, compare_observed_packages, observed_package_fingerprint

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_FIXTURE = PROJECT_ROOT / "data" / "raw" / "fred_yield_curve" / "fred-monthly-yield-curve-gs1m-gs1-gs10-gs30.csv"
SOURCE_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=GS1M,GS1,GS10,GS30"
SELECTED_PERIODS = ("2024-01", "2024-02")
SELECTED_TENORS = ("GS1M", "GS1", "GS10", "GS30")
EXPECTED_FINGERPRINT = "d7646c4ce18dfacf430fe66cfe170694d18a9aa2af97fcd13251e47276778633"


def _raw_text() -> str:
    return RAW_FIXTURE.read_text(encoding="utf-8")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _normalized() -> dict:
    return normalize_fred_yield_curve_fixture(
        _raw_text(),
        raw_artifact_path=str(RAW_FIXTURE.relative_to(PROJECT_ROOT)),
        raw_sha256=_sha256(RAW_FIXTURE),
        source_url=SOURCE_URL,
        selected_periods=SELECTED_PERIODS,
        selected_tenors=SELECTED_TENORS,
    )


def test_fred_yield_curve_fixture_normalizes_curve_surface_without_market_framework():
    normalized = _normalized()

    assert normalized["source_code"] == "FRED_YIELD_CURVE"
    assert normalized["provider_dataset_code"] == "FRED:GS1M_GS1_GS10_GS30"
    assert normalized["observation_family"] == "financial_market_curve"
    assert normalized["territory_code"] == "USA"
    assert normalized["territory_label"] == "United States"
    assert normalized["frequency"] == "M"
    assert normalized["selected_periods"] == ["2024-01", "2024-02"]
    assert normalized["selected_tenors"] == ["GS1M", "GS1", "GS10", "GS30"]
    assert normalized["row_count"] == 8
    assert normalized["expected_row_count"] == 8
    assert normalized["provider_metadata"]["csv_row_count"] == 878
    assert normalized["provider_metadata"]["csv_columns"] == ["observation_date", "GS1M", "GS1", "GS10", "GS30"]
    assert normalized["input_filters"] == {
        "series_ids": ["GS1M", "GS1", "GS10", "GS30"],
        "selected_periods": ["2024-01", "2024-02"],
        "selected_tenors": ["GS1M", "GS1", "GS10", "GS30"],
        "scope": "bounded TASK-065 yield-curve evidence slice",
    }

    assert normalized["rows"][0] == {
        "provider_indicator_code": "FRED_YIELD:GS1M",
        "provider_indicator_label": "Market Yield on U.S. Treasury Securities — 1 month constant maturity",
        "territory_code": "USA",
        "territory_label": "United States",
        "provider_period_code": "2024-M01",
        "observation_date": "2024-01-01",
        "frequency": "M",
        "period_year": 2024,
        "period_month": 1,
        "unit_code": "PERCENT",
        "unit_label": "Percent",
        "value": 5.54,
        "observation_status": "observed",
        "decimal_precision": 2,
        "tenor_code": "GS1M",
        "tenor_label": "1 month constant maturity",
        "tenor_months": 1,
        "tenor_years": None,
        "attributes": {
            "observation_family": "financial_market_curve",
            "curve_name": "Monthly U.S. Treasury constant maturity yield curve",
            "curve_point_role": "tenor",
            "provider_series_id": "GS1M",
            "observation_date": "2024-01-01",
            "tenor_code": "GS1M",
            "tenor_label": "1 month constant maturity",
            "tenor_months": 1,
            "tenor_years": None,
            "source_frequency": "monthly",
        },
        "source_payload": {
            "observation_date": "2024-01-01",
            "GS1M": "5.54",
        },
    }

    assert normalized["rows"][-1]["provider_indicator_code"] == "FRED_YIELD:GS30"
    assert normalized["rows"][-1]["provider_period_code"] == "2024-M02"
    assert normalized["rows"][-1]["value"] == 4.38
    assert normalized["rows"][-1]["tenor_years"] == 30


def test_fred_yield_curve_observed_package_satisfies_existing_contract_without_contract_evolution():
    package = build_fred_yield_curve_observed_package(_normalized())

    assert package.source_code == "FRED_YIELD_CURVE"
    assert package.source_name == "FRED bounded monthly U.S. Treasury yield curve evidence slice"
    assert package.source_home_url == "https://fred.stlouisfed.org/"
    assert package.provider_dataset_code == "FRED:GS1M_GS1_GS10_GS30"
    assert package.release_key.startswith("FRED_YIELD_CURVE:2024-M01_2024-M02:")
    assert package.row_count == 8
    assert package.expected_row_count == 8
    assert package.input_filters == _normalized()["input_filters"]
    assert package.raw_evidence["source_url"] == SOURCE_URL
    assert package.raw_evidence["raw_artifact_path"] == "data/raw/fred_yield_curve/fred-monthly-yield-curve-gs1m-gs1-gs10-gs30.csv"
    assert len(package.raw_evidence["raw_sha256"]) == 64
    assert package.raw_evidence["provider_metadata"] == _normalized()["provider_metadata"]

    observation = package.observations[3]
    assert observation.provider_indicator_code == "FRED_YIELD:GS30"
    assert observation.provider_indicator_label == "Market Yield on U.S. Treasury Securities — 30 year constant maturity"
    assert observation.provider_territory_code == "USA"
    assert observation.provider_territory_label == "United States"
    assert observation.provider_period_code == "2024-M01"
    assert observation.frequency == "M"
    assert observation.period_year == 2024
    assert observation.period_quarter is None
    assert observation.period_month == 1
    assert observation.unit_code == "PERCENT"
    assert observation.unit_label == "Percent"
    assert observation.value == 4.26
    assert observation.observation_status == "observed"
    assert observation.decimal_precision == 2
    assert observation.attribute_hash == canonical_attribute_hash(observation.attributes)
    assert observation.attributes["observation_family"] == "financial_market_curve"
    assert observation.attributes["tenor_years"] == 30

    report = validate_observed_package_contract(package)
    assert report.valid is True
    assert report.issues == ()


def test_fred_yield_curve_observed_package_replay_is_deterministic():
    package = build_fred_yield_curve_observed_package(_normalized())
    replayed = build_fred_yield_curve_observed_package(_normalized())

    comparison = compare_observed_packages(package, replayed)

    assert comparison.equivalent is True
    assert comparison.left_fingerprint == comparison.right_fingerprint
    assert comparison.row_count_match is True
    assert comparison.expected_row_count_match is True
    assert comparison.observation_count_match is True
    assert comparison.differing_observations == ()
    assert observed_package_fingerprint(package) == EXPECTED_FINGERPRINT


def test_fred_yield_curve_fixture_is_persisted_for_clean_clone_replay():
    assert RAW_FIXTURE.exists()
    assert _sha256(RAW_FIXTURE) == "0870977a6dc92d4eb841235ed1335c32ad88914387fe7588ffeeb851e3411a2f"


def test_fred_yield_curve_module_remains_source_specific_not_generalized_market_or_fred_framework():
    source = (PROJECT_ROOT / "src" / "macroforge" / "fred_yield_curve.py").read_text(encoding="utf-8")

    forbidden = [
        "class BaseSource",
        "class SourcePlugin",
        "class FredClient",
        "class MarketDataFramework",
        "class YieldCurveFramework",
        "PluginRegistry",
        "requests.get",
        "urllib.request",
        "sqlalchemy",
        "CREATE TABLE",
        "INSERT INTO",
        "interpolate",
        "yield_spread",
        "curve_slope",
    ]
    for token in forbidden:
        assert token not in source
