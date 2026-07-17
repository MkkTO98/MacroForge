from __future__ import annotations

import importlib.util
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = PROJECT_ROOT / "tools/task204_wdi_gender_equality_chunked_expansion.py"


def _load_task204_module():
    spec = importlib.util.spec_from_file_location("task204_wdi_gender_equality_chunked_expansion", SCRIPT_PATH)
    assert spec is not None
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_task204_classify_does_not_convert_acquisition_error_placeholder_to_zero_observation() -> None:
    task204 = _load_task204_module()
    raw = {
        "scope": {
            "countries": ["USA"],
            "indicators": ["SE.ADT.1524.LT.FE.ZS"],
        },
        "requests": [
            {
                "indicator_code": "SE.ADT.1524.LT.FE.ZS",
                "url": "https://api.worldbank.org/v2/country/all/indicator/SE.ADT.1524.LT.FE.ZS?format=json&date=1990:2024&per_page=20000",
                "metadata_url": "https://api.worldbank.org/v2/indicator/SE.ADT.1524.LT.FE.ZS?format=json",
                "response": [
                    {"error": "TimeoutError", "message": "The read operation timed out", "lastupdated": None},
                    [],
                ],
                "metadata_response": [{"page": 1, "pages": 1, "per_page": "50", "total": 1}, [{"id": "SE.ADT.1524.LT.FE.ZS"}]],
            }
        ],
    }

    result = task204.classify(raw)
    ev = result["indicator_results"]["SE.ADT.1524.LT.FE.ZS"]

    assert ev["classification"] == "provider_unavailable"
    assert ev["provider_evidence_category"] == "acquisition_error"
    assert ev["provider_evidence_category"] != "zero_observations_within_requested_scope"
    assert "TimeoutError" in ev["exclusion_evidence"]


def test_task204_unresolved_acquisition_errors_block_completion_claims() -> None:
    task204 = _load_task204_module()
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

    completion = task204.completion_semantics(manifest)

    assert completion["unresolved_acquisition_error_count"] == 1
    assert completion["can_claim_successful_completion"] is False
    assert completion["can_claim_candidate_set_exhaustion"] is False
    assert completion["can_claim_capability_closure"] is False
    assert completion["status"] == "blocked_unresolved_acquisition_errors"


def test_task204_completion_claims_allowed_when_no_acquisition_errors_remain() -> None:
    task204 = _load_task204_module()
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

    completion = task204.completion_semantics(manifest)

    assert completion["unresolved_acquisition_error_count"] == 0
    assert completion["can_claim_successful_completion"] is True
    assert completion["can_claim_candidate_set_exhaustion"] is True
    assert completion["can_claim_capability_closure"] is True
    assert completion["status"] == "complete"
