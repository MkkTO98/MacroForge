from __future__ import annotations

import importlib.util
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = PROJECT_ROOT / "tools/task206_wdi_social_protection_all_programs_chunked_expansion.py"


def _load_task206_module():
    spec = importlib.util.spec_from_file_location("task206_wdi_social_protection_all_programs_chunked_expansion", SCRIPT_PATH)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def _metadata(indicator: str):
    return [{"page": 1, "pages": 1, "per_page": "50", "total": 1}, [{"id": indicator}]]


def _row(indicator: str, *, iso: str, country_id: str, value: float | None = 1.0, date: str = "2020"):
    return {
        "indicator": {"id": indicator, "value": "Synthetic indicator"},
        "country": {"id": country_id, "value": country_id},
        "countryiso3code": iso,
        "date": date,
        "value": value,
        "unit": "",
        "obs_status": "",
        "decimal": 1,
    }


def _raw(indicator: str, rows: list[dict], countries: list[str] | None = None):
    countries = countries or ["USA", "DNK"]
    return {
        "scope": {
            "countries": countries,
            "indicators": [indicator],
            "periods": ["2020"],
            "raw_evidence_policy": "test",
        },
        "country_catalog": {
            "countries": [
                {"id": "USA", "name": "United States", "region": {"id": "NAC", "value": "North America"}, "incomeLevel": {"id": "HIC", "value": "High income"}},
                {"id": "DNK", "name": "Denmark", "region": {"id": "ECS", "value": "Europe & Central Asia"}, "incomeLevel": {"id": "HIC", "value": "High income"}},
            ]
        },
        "requests": [
            {
                "indicator_code": indicator,
                "url": f"https://api.worldbank.org/v2/country/all/indicator/{indicator}?format=json&date=1990:2024&per_page=20000",
                "metadata_url": f"https://api.worldbank.org/v2/indicator/{indicator}?format=json",
                "response": [{"lastupdated": "2025-08-25", "page": 1, "pages": 1, "per_page": 20000, "total": len(rows), "total_before_non_aggregate_filter": len(rows)}, rows],
                "metadata_response": _metadata(indicator),
            }
        ],
    }


def test_task206_classify_does_not_convert_acquisition_error_placeholder_to_zero_observation() -> None:
    task206 = _load_task206_module()
    raw = {
        "scope": {
            "countries": ["USA"],
            "indicators": ["per_allsp.cov_q1_tot"],
        },
        "requests": [
            {
                "indicator_code": "per_allsp.cov_q1_tot",
                "url": "https://api.worldbank.org/v2/country/all/indicator/per_allsp.cov_q1_tot?format=json&date=1990:2024&per_page=20000",
                "metadata_url": "https://api.worldbank.org/v2/indicator/per_allsp.cov_q1_tot?format=json",
                "response": [
                    {"error": "TimeoutError", "message": "The read operation timed out", "lastupdated": None},
                    [],
                ],
                "metadata_response": _metadata("per_allsp.cov_q1_tot"),
            }
        ],
    }

    result = task206.classify(raw)
    ev = result["indicator_results"]["per_allsp.cov_q1_tot"]

    assert ev["classification"] == "provider_unavailable"
    assert ev["provider_evidence_category"] == "acquisition_error"
    assert ev["provider_evidence_category"] != "zero_observations_within_requested_scope"
    assert "TimeoutError" in ev["exclusion_evidence"]


def test_task206_countryiso3code_remains_authoritative_when_valid() -> None:
    task206 = _load_task206_module()
    assert task206._row_country_code({"countryiso3code": "USA", "country": {"id": "DNK"}}, {"USA", "DNK"}) == "USA"


def test_task206_blank_countryiso3code_falls_back_to_valid_non_aggregate_country_id() -> None:
    task206 = _load_task206_module()
    indicator = "per_allsp.synthetic"
    raw = _raw(indicator, [_row(indicator, iso="", country_id="DNK", value=2.0)])

    classified = task206.classify(raw)
    ev = classified["indicator_results"][indicator]
    normalized = task206.normalize(raw)

    assert ev["provider_evidence_category"] == "compatible_annual_scalar_observations"
    assert ev["countries_with_rows"] == 1
    assert normalized["rows"][0]["countryiso3code"] == "DNK"
    assert normalized["rows"][0]["provider_countryiso3code"] == ""
    assert normalized["rows"][0]["country_id"] == "DNK"


def test_task206_aggregate_country_id_is_rejected_when_iso3_blank() -> None:
    task206 = _load_task206_module()
    indicator = "per_allsp.synthetic"
    raw = _raw(indicator, [_row(indicator, iso="", country_id="WLD", value=1.0)])

    ev = task206.classify(raw)["indicator_results"][indicator]

    assert ev["provider_evidence_category"] == "outside_non_aggregate_country_scope"
    assert "WLD" in ev["exclusion_evidence"]


def test_task206_unknown_country_id_is_rejected_when_iso3_blank() -> None:
    task206 = _load_task206_module()
    indicator = "per_allsp.synthetic"
    raw = _raw(indicator, [_row(indicator, iso="", country_id="ZZZ", value=1.0)])

    ev = task206.classify(raw)["indicator_results"][indicator]

    assert ev["provider_evidence_category"] == "outside_non_aggregate_country_scope"
    assert "ZZZ" in ev["exclusion_evidence"]


def test_task206_fallback_normalization_does_not_create_duplicate_canonical_keys() -> None:
    task206 = _load_task206_module()
    indicator = "per_allsp.synthetic"
    raw = _raw(
        indicator,
        [
            _row(indicator, iso="", country_id="DNK", value=2.0, date="2020"),
            _row(indicator, iso="USA", country_id="USA", value=3.0, date="2020"),
        ],
        countries=["DNK", "USA"],
    )

    normalized = task206.normalize(raw)
    keys = [(r["indicator_id"], r["countryiso3code"], r["date"]) for r in normalized["rows"]]

    assert keys == [(indicator, "DNK", "2020"), (indicator, "USA", "2020")]
    assert len(keys) == len(set(keys))


def test_task206_unresolved_acquisition_errors_block_completion_claims() -> None:
    task206 = _load_task206_module()
    manifest = {
        "candidate_count": 2,
        "included_indicator_count": 1,
        "excluded_indicator_count": 1,
        "classification": {
            "indicator_results": {
                "GOOD.IND": {
                    "classification": "compatible",
                    "provider_evidence_category": "compatible_annual_scalar_observations",
                },
                "TIMEOUT.IND": {
                    "classification": "provider_unavailable",
                    "provider_evidence_category": "acquisition_error",
                },
            }
        },
    }

    completion = task206.completion_semantics(manifest)

    assert completion["unresolved_acquisition_error_count"] == 1
    assert completion["can_claim_successful_completion"] is False
    assert completion["can_claim_candidate_set_exhaustion"] is False
    assert completion["can_claim_capability_closure"] is False
    assert completion["status"] == "blocked_unresolved_acquisition_errors"


def test_task206_completion_claims_allowed_when_no_acquisition_errors_remain() -> None:
    task206 = _load_task206_module()
    manifest = {
        "candidate_count": 2,
        "included_indicator_count": 1,
        "excluded_indicator_count": 1,
        "classification": {
            "indicator_results": {
                "GOOD.IND": {
                    "classification": "compatible",
                    "provider_evidence_category": "compatible_annual_scalar_observations",
                },
                "ZERO.IND": {
                    "classification": "provider_unavailable",
                    "provider_evidence_category": "zero_observations_within_requested_scope",
                },
            }
        },
    }

    completion = task206.completion_semantics(manifest)

    assert completion["unresolved_acquisition_error_count"] == 0
    assert completion["can_claim_successful_completion"] is True
    assert completion["can_claim_candidate_set_exhaustion"] is True
    assert completion["can_claim_capability_closure"] is True
    assert completion["status"] == "complete"
