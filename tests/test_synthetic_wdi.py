from __future__ import annotations

import hashlib
import json

import pytest

from macroforge.wdi_demographics import normalize_wdi_demographics_phase1_fixture
from macroforge.wdi_energy_use_coal_electricity import normalize_wdi_energy_phase1_fixture
from macroforge.wdi_financial_accounts_core import normalize_wdi_financial_accounts_core_fixture
from macroforge.wdi_observed import (
    normalize_wdi_macro_indicators_fixture,
    normalize_wdi_operational_phase1_fixture,
)
from macroforge.wdi_trade_core import normalize_wdi_trade_core_fixture
from synthetic_wdi import (
    build_synthetic_wdi_fixture,
    synthetic_fixture_bytes,
    synthetic_fixture_json,
    synthetic_fixture_provenance,
)


FAMILY_SHAPES = {
    "normalized_smoke": (8, 2, 2),
    "macro_indicators": (90, 6, 3),
    "operational_phase1": (15_624, 217, 3),
    "demographics_phase1": (41_664, 217, 8),
    "energy_phase1": (10_416, 217, 2),
    "energy_bounded": (8, 2, 2),
    "trade_core": (20_832, 217, 4),
    "financial_accounts_core": (20_832, 217, 4),
}


@pytest.mark.parametrize(("family", "shape"), FAMILY_SHAPES.items())
def test_synthetic_fixture_is_deterministic_and_has_required_shape(
    family: str, shape: tuple[int, int, int]
) -> None:
    left = build_synthetic_wdi_fixture(family)
    right = build_synthetic_wdi_fixture(family)

    assert left == right
    expected_rows, expected_countries, expected_indicators = shape
    if family == "normalized_smoke":
        assert left["row_count"] == expected_rows
        assert len({row["countryiso3code"] for row in left["rows"]}) == expected_countries
        assert len({row["indicator_id"] for row in left["rows"]}) == expected_indicators
    else:
        observations = [row for request in left["requests"] for row in request["response"][1]]
        assert len(observations) == expected_rows
        assert len({row["countryiso3code"] for row in observations}) == expected_countries
        assert len(left["requests"]) == expected_indicators


def test_synthetic_fixture_contains_only_authored_test_provenance() -> None:
    text = "\n".join(synthetic_fixture_json(family) for family in FAMILY_SHAPES)
    lowered = text.lower()

    assert "example.invalid" in lowered
    assert "synthetic territory" in lowered
    assert "api.worldbank.org" not in lowered
    assert "data.worldbank.org" not in lowered
    assert "united states" not in lowered
    assert "china" not in lowered
    assert "denmark" not in lowered
    assert "japan" not in lowered


def test_synthetic_fixture_serialization_is_canonical() -> None:
    text = synthetic_fixture_json("normalized_smoke")
    assert text.endswith("\n")
    assert json.loads(text) == build_synthetic_wdi_fixture("normalized_smoke")


@pytest.mark.parametrize("family", FAMILY_SHAPES)
def test_synthetic_fixture_provenance_is_byte_for_byte_deterministic(family: str) -> None:
    left_bytes = synthetic_fixture_bytes(family)
    right_bytes = synthetic_fixture_bytes(family)
    left = synthetic_fixture_provenance(family)
    right = synthetic_fixture_provenance(family)

    assert left_bytes == right_bytes
    assert left == right
    assert left["raw_artifact_path"] == f"tests/synthetic_wdi.py#{family}"
    assert left["raw_sha256"] == hashlib.sha256(left_bytes).hexdigest()


@pytest.mark.parametrize(
    ("family", "normalizer"),
    [
        ("macro_indicators", normalize_wdi_macro_indicators_fixture),
        ("operational_phase1", normalize_wdi_operational_phase1_fixture),
        ("demographics_phase1", normalize_wdi_demographics_phase1_fixture),
        ("energy_phase1", normalize_wdi_energy_phase1_fixture),
        ("trade_core", normalize_wdi_trade_core_fixture),
        ("financial_accounts_core", normalize_wdi_financial_accounts_core_fixture),
    ],
)
def test_affected_normalizers_fail_closed_on_missing_or_contradictory_provenance(
    family: str, normalizer
) -> None:
    raw = build_synthetic_wdi_fixture(family)
    with pytest.raises(TypeError):
        normalizer(raw)
    with pytest.raises(ValueError, match="do not represent the supplied parsed WDI input"):
        normalizer(
            raw,
            raw_artifact_path=f"tests/synthetic_wdi.py#{family}",
            raw_payload=b"{}",
        )


@pytest.mark.parametrize(
    ("family", "normalizer"),
    [
        ("macro_indicators", normalize_wdi_macro_indicators_fixture),
        ("operational_phase1", normalize_wdi_operational_phase1_fixture),
        ("demographics_phase1", normalize_wdi_demographics_phase1_fixture),
        ("energy_phase1", normalize_wdi_energy_phase1_fixture),
        ("trade_core", normalize_wdi_trade_core_fixture),
        ("financial_accounts_core", normalize_wdi_financial_accounts_core_fixture),
    ],
)
def test_nested_raw_artifacts_distinguish_bundle_from_canonical_responses(
    family: str, normalizer
) -> None:
    raw = build_synthetic_wdi_fixture(family)
    raw_payload = synthetic_fixture_bytes(family)
    provenance = synthetic_fixture_provenance(family)
    normalized = normalizer(
        raw,
        raw_artifact_path=provenance["raw_artifact_path"],
        raw_payload=raw_payload,
    )

    assert len(normalized["raw_artifacts"]) == len(raw["requests"])
    for artifact, request in zip(normalized["raw_artifacts"], raw["requests"], strict=True):
        response_bytes = json.dumps(request["response"], sort_keys=True).encode("utf-8")
        assert artifact["raw_file"] == provenance["raw_artifact_path"]
        assert artifact["bytes"] == len(raw_payload)
        assert artifact["sha256"] == provenance["raw_sha256"]
        assert artifact["response_bytes"] == len(response_bytes)
        assert artifact["response_sha256"] == hashlib.sha256(response_bytes).hexdigest()
