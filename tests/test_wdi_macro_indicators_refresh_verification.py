from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

from macroforge.wdi_observed import (
    EXPECTED_OBSERVATION_COUNT,
    normalize_wdi_macro_indicators_fixture,
    write_wdi_macro_indicators_normalized_artifact,
)
from macroforge.wdi_observed import (
    build_wdi_macro_indicators_refresh_delta_report,
    refresh_delta_report_fingerprint,
    write_wdi_macro_indicators_refresh_delta_report,
)
from synthetic_wdi import build_synthetic_wdi_fixture, synthetic_fixture_bytes, synthetic_fixture_provenance

PROJECT_ROOT = Path(__file__).resolve().parents[1]
EXPECTED_REFRESH_FINGERPRINT = "551c414d3b3e0c1eb19761de7c068f29eecbd601f92542ab3a827b80c65f3422"


def _normalized() -> dict:
    return normalize_wdi_macro_indicators_fixture(build_synthetic_wdi_fixture("macro_indicators"), **_provenance())


def _provenance() -> dict:
    return {
        "raw_artifact_path": synthetic_fixture_provenance("macro_indicators")["raw_artifact_path"],
        "raw_payload": synthetic_fixture_bytes("macro_indicators"),
    }


def _mutated_current(previous: dict) -> dict:
    current = copy.deepcopy(previous)
    updated_key = ("NY.GDP.MKTP.CD", "USA", "2023")
    removed_key = ("FP.CPI.TOTL.ZG", "IND", "2019")
    added_row = copy.deepcopy(current["rows"][0])
    added_row["indicator_id"] = "SP.POP.TOTL"
    added_row["indicator_name"] = "Population, total"
    added_row["countryiso3code"] = "USA"
    added_row["country_name"] = "United States"
    added_row["country_id"] = "US"
    added_row["date"] = "2024"
    added_row["value"] = 335000000
    rows = []
    for row in current["rows"]:
        key = (row["indicator_id"], row["countryiso3code"], row["date"])
        if key == removed_key:
            continue
        if key == updated_key:
            row = copy.deepcopy(row)
            row["value"] = row["value"] + 1
        rows.append(row)
    rows.append(added_row)
    current["rows"] = rows
    current["row_count"] = len(rows)
    current["expected_row_count"] = len(rows)
    current["date_range"] = "2019:2024"
    return current


def test_refresh_delta_report_classifies_row_level_changes() -> None:
    previous = _normalized()
    current = _mutated_current(previous)
    report = build_wdi_macro_indicators_refresh_delta_report(previous, current)
    assert report["task"] == "TASK-130"
    assert report["capability"] == "WDI macro indicators"
    assert report["previous_row_count"] == EXPECTED_OBSERVATION_COUNT
    assert report["current_row_count"] == EXPECTED_OBSERVATION_COUNT
    assert report["unchanged_count"] == EXPECTED_OBSERVATION_COUNT - 2
    assert report["updated_count"] == 1
    assert report["added_count"] == 1
    assert report["removed_count"] == 1
    assert report["changed_count"] == 3
    assert report["updated_keys"] == [{"indicator_id": "NY.GDP.MKTP.CD", "countryiso3code": "USA", "date": "2023"}]
    assert report["removed_keys"] == [{"indicator_id": "FP.CPI.TOTL.ZG", "countryiso3code": "IND", "date": "2019"}]
    assert report["added_keys"] == [{"indicator_id": "SP.POP.TOTL", "countryiso3code": "USA", "date": "2024"}]


def test_refresh_delta_report_is_deterministically_fingerprinted() -> None:
    previous = _normalized()
    current = _mutated_current(previous)
    left = build_wdi_macro_indicators_refresh_delta_report(previous, current)
    right = build_wdi_macro_indicators_refresh_delta_report(previous, current)
    assert left == right
    assert refresh_delta_report_fingerprint(left) == EXPECTED_REFRESH_FINGERPRINT


def test_refresh_delta_report_persists_operational_artifact(tmp_path: Path) -> None:
    previous = _normalized()
    current = _mutated_current(previous)
    path = tmp_path / "refresh-delta.json"
    report = write_wdi_macro_indicators_refresh_delta_report(previous, current, path)
    assert path.exists()
    assert json.loads(path.read_text(encoding="utf-8")) == report
    assert report["status"] == "verified"
    assert report["refresh_verification"] == "bounded_pre_load_delta_check"


def test_refresh_delta_report_handles_no_change_case() -> None:
    previous = _normalized()
    report = build_wdi_macro_indicators_refresh_delta_report(previous, copy.deepcopy(previous))
    assert report["unchanged_count"] == EXPECTED_OBSERVATION_COUNT
    assert report["changed_count"] == 0
    assert report["added_count"] == 0
    assert report["removed_count"] == 0
    assert report["updated_count"] == 0


def test_refresh_delta_report_uses_persisted_task129_normalized_artifact(tmp_path: Path) -> None:
    normalized_path = tmp_path / "normalized.json"
    normalized = write_wdi_macro_indicators_normalized_artifact(
        build_synthetic_wdi_fixture("macro_indicators"), normalized_path, **_provenance()
    )
    assert normalized["raw_fixture_path"] == _provenance()["raw_artifact_path"]
    assert normalized["raw_sha256"] == synthetic_fixture_provenance("macro_indicators")["raw_sha256"]
    assert hashlib.sha256(normalized_path.read_bytes()).hexdigest()
    report = build_wdi_macro_indicators_refresh_delta_report(normalized, normalized)
    assert report["previous_row_count"] == EXPECTED_OBSERVATION_COUNT
    assert report["current_row_count"] == EXPECTED_OBSERVATION_COUNT


def test_refresh_delta_report_does_not_create_forbidden_operational_scope() -> None:
    forbidden_paths = [PROJECT_ROOT / "src" / "macroforge" / name for name in ["wdi_bulk_ingestion.py", "wdi_all_indicators_loader.py", "wdi_refresh_daemon.py", "knowledgeforge_query_api.py", "controlled_expansion_pipeline.py", "provider_registry.py", "refresh_scheduler.py"]]
    assert not any(path.exists() for path in forbidden_paths)
