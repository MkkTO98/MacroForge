from __future__ import annotations

import json

import pytest

from synthetic_wdi import build_synthetic_wdi_fixture, synthetic_fixture_json


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
