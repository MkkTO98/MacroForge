from __future__ import annotations

import hashlib
import json
from pathlib import Path

from macroforge.contract_drift import validate_observed_package_contract
from macroforge.observed_ingestion import canonical_attribute_hash, compare_observed_packages, observed_package_fingerprint
from macroforge.treasury_fiscal_data import (
    build_treasury_avg_interest_observed_package,
    normalize_treasury_avg_interest_fixture,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_FIXTURE = (
    PROJECT_ROOT
    / "data"
    / "raw"
    / "treasury"
    / "treasury-avg-interest-rates-2026-05-31-raw.json"
)
SOURCE_URL = (
    "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v2/accounting/od/"
    "avg_interest_rates?fields=record_date,security_desc,avg_interest_rate_amt&"
    "filter=record_date:eq:2026-05-31&sort=security_desc&page[size]=20"
)


def _raw() -> dict:
    return json.loads(RAW_FIXTURE.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _normalized() -> dict:
    return normalize_treasury_avg_interest_fixture(
        _raw(),
        raw_artifact_path=str(RAW_FIXTURE.relative_to(PROJECT_ROOT)),
        raw_sha256=_sha256(RAW_FIXTURE),
        source_url=SOURCE_URL,
    )


def test_treasury_avg_interest_fixture_normalizes_row_oriented_api_metadata_without_framework():
    normalized = _normalized()

    assert normalized["source_code"] == "TREASURY_FISCAL_DATA"
    assert normalized["provider_dataset_code"] == "FISCAL_SERVICE:avg_interest_rates"
    assert normalized["endpoint"] == "avg_interest_rates"
    assert normalized["frequency"] == "M"
    assert normalized["period_range"] == "2026-M05-2026-M05"
    assert normalized["row_count"] == 16
    assert normalized["expected_row_count"] == 16
    assert normalized["input_filters"] == {
        "endpoint": "avg_interest_rates",
        "fields": "record_date,security_desc,avg_interest_rate_amt",
        "filter": "record_date:eq:2026-05-31",
        "sort": "security_desc",
        "page_size": 20,
        "scope": "bounded TASK-054 architectural experiment",
    }
    assert normalized["provider_metadata"] == {
        "count": 16,
        "total_count": 16,
        "total_pages": 1,
        "labels": {
            "record_date": "Record Date",
            "security_desc": "Security Description",
            "avg_interest_rate_amt": "Average Interest Rate Amount",
        },
        "data_types": {
            "record_date": "DATE",
            "security_desc": "STRING",
            "avg_interest_rate_amt": "PERCENTAGE",
        },
        "data_formats": {
            "record_date": "YYYY-MM-DD",
            "security_desc": "String",
            "avg_interest_rate_amt": "10.2%",
        },
        "pagination": {
            "self": "&page%5Bnumber%5D=1&page%5Bsize%5D=20",
            "first": "&page%5Bnumber%5D=1&page%5Bsize%5D=20",
            "prev": None,
            "next": None,
            "last": "&page%5Bnumber%5D=1&page%5Bsize%5D=20",
        },
    }

    first = normalized["rows"][0]
    assert first == {
        "endpoint": "avg_interest_rates",
        "provider_indicator_code": "AVG_INTEREST_RATE:DOMESTIC_SERIES",
        "provider_indicator_label": "Average Interest Rate Amount — Domestic Series",
        "security_desc": "Domestic Series",
        "territory_code": "USA",
        "territory_label": "United States",
        "provider_period_code": "2026-M05",
        "record_date": "2026-05-31",
        "frequency": "M",
        "period_year": 2026,
        "period_month": 5,
        "unit_code": "PERCENT",
        "unit_label": "Percent",
        "value": 7.577,
        "observation_status": "observed",
        "decimal_precision": 3,
        "attributes": {
            "endpoint": "avg_interest_rates",
            "record_date": "2026-05-31",
            "security_desc": "Domestic Series",
            "field_label": "Average Interest Rate Amount",
            "value_field": "avg_interest_rate_amt",
            "data_type": "PERCENTAGE",
            "data_format": "10.2%",
            "api_count": 16,
            "api_total_count": 16,
            "api_total_pages": 1,
        },
        "source_payload": {
            "record_date": "2026-05-31",
            "security_desc": "Domestic Series",
            "avg_interest_rate_amt": "7.577",
        },
    }


def test_treasury_avg_interest_observed_package_satisfies_existing_contract_without_contract_evolution():
    package = build_treasury_avg_interest_observed_package(_normalized())

    assert package.source_code == "TREASURY_FISCAL_DATA"
    assert package.source_name == "U.S. Treasury Fiscal Data bounded average interest rates evidence slice"
    assert package.source_home_url == "https://fiscaldata.treasury.gov/"
    assert package.provider_dataset_code == "FISCAL_SERVICE:avg_interest_rates"
    assert package.release_key.startswith("TREASURY_FISCAL_DATA:avg_interest_rates:2026-M05-2026-M05:")
    assert package.row_count == 16
    assert package.expected_row_count == 16
    assert package.input_filters == _normalized()["input_filters"]
    assert package.raw_evidence["source_url"] == SOURCE_URL
    assert package.raw_evidence["raw_artifact_path"] == "data/raw/treasury/treasury-avg-interest-rates-2026-05-31-raw.json"
    assert len(package.raw_evidence["raw_sha256"]) == 64
    assert package.raw_evidence["provider_metadata"] == _normalized()["provider_metadata"]

    observation = package.observations[0]
    assert observation.provider_indicator_code == "AVG_INTEREST_RATE:DOMESTIC_SERIES"
    assert observation.provider_indicator_label == "Average Interest Rate Amount — Domestic Series"
    assert observation.provider_territory_code == "USA"
    assert observation.provider_territory_label == "United States"
    assert observation.provider_period_code == "2026-M05"
    assert observation.frequency == "M"
    assert observation.period_year == 2026
    assert observation.period_quarter is None
    assert observation.period_month == 5
    assert observation.unit_code == "PERCENT"
    assert observation.unit_label == "Percent"
    assert observation.value == 7.577
    assert observation.observation_status == "observed"
    assert observation.decimal_precision == 3
    assert observation.attribute_hash == canonical_attribute_hash(observation.attributes)

    report = validate_observed_package_contract(package)
    assert report.valid is True
    assert report.issues == ()


def test_treasury_avg_interest_observed_package_replay_is_deterministic():
    package = build_treasury_avg_interest_observed_package(_normalized())
    replayed = build_treasury_avg_interest_observed_package(_normalized())

    comparison = compare_observed_packages(package, replayed)

    assert comparison.equivalent is True
    assert comparison.left_fingerprint == comparison.right_fingerprint
    assert comparison.row_count_match is True
    assert comparison.expected_row_count_match is True
    assert comparison.observation_count_match is True
    assert comparison.differing_observations == ()
    assert len(observed_package_fingerprint(package)) == 64


def test_treasury_module_remains_source_specific_not_generalized_acquisition_or_pagination_framework():
    source = (PROJECT_ROOT / "src" / "macroforge" / "treasury_fiscal_data.py").read_text(encoding="utf-8")

    forbidden = [
        "class BaseSource",
        "class SourcePlugin",
        "class PaginationFramework",
        "PluginRegistry",
        "requests.get",
        "urllib.request",
        "sqlalchemy",
        "CREATE TABLE",
        "INSERT INTO",
    ]
    for token in forbidden:
        assert token not in source
