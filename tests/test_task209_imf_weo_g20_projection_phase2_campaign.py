from __future__ import annotations

import json
from pathlib import Path

import pytest

import tools.task209_imf_weo_g20_projection_phase2_campaign as task209


def _redirect_outputs(monkeypatch, tmp_path):
    monkeypatch.setattr(task209, "RAW_PATH", tmp_path / "raw.json")
    monkeypatch.setattr(task209, "NORM_PATH", tmp_path / "norm.json")
    monkeypatch.setattr(task209, "MANIFEST_PATH", tmp_path / "manifest.json")
    monkeypatch.setattr(task209, "PROVIDER_REPORT", tmp_path / "provider.json")
    monkeypatch.setattr(task209, "EVAL_REPORT", tmp_path / "eval.json")
    monkeypatch.setattr(task209, "LOAD_REPORT", tmp_path / "load.json")
    monkeypatch.setattr(task209, "CHECKSUMS", tmp_path / "checksums.txt")


def _sample_raw():
    countries = {code: {"label": f"Country {code}"} for code in task209.COUNTRIES}
    indicators = {
        code: {
            "label": code,
            "description": f"Description {code}",
            "source": "World Economic Outlook (April 2026)",
            "unit": "Annual percent change" if code != "NGDPD" else "Billions of U.S. dollars",
            "dataset": "WEO",
            "last-modified": "2026-04-08 16:07:34",
        }
        for code in task209.INDICATORS
    }
    requests = []
    for indicator in task209.INDICATORS:
        requests.append(
            {
                "indicator_code": indicator,
                "url": f"https://example.test/{indicator}",
                "payload": {
                    "api": {"version": "1", "output-method": "json"},
                    "values": {
                        indicator: {
                            country: {year: 1.1 for year in task209.YEARS}
                            for country in task209.COUNTRIES
                        }
                    },
                },
            }
        )
    return {
        "task": "TASK-209",
        "scope": "Phase 2 IMF WEO G20 projection breadth campaign",
        "provider": "IMF DataMapper API",
        "accessed_at_utc": "2026-07-11T00:00:00+00:00",
        "countries": list(task209.COUNTRIES),
        "projection_years": list(task209.YEARS),
        "indicator_codes": list(task209.INDICATORS),
        "metadata": {"countries": countries, "indicators": indicators},
        "requests": requests,
        "acquisition_errors": [],
    }


def test_task209_scope_constants_are_bounded_and_non_bls():
    assert task209.TASK_ID == "TASK-209"
    assert task209.SOURCE_CODE == "IMF_WEO_DATAMAPPER_API_V1"
    assert "BLS" not in task209.SOURCE_CODE
    assert task209.EXPECTED_ROW_COUNT == 342
    assert len(task209.COUNTRIES) == 19
    assert len(task209.INDICATORS) == 6
    assert len(task209.YEARS) == 3


def test_task209_normalize_complete_fixture(tmp_path, monkeypatch):
    _redirect_outputs(monkeypatch, tmp_path)
    raw_path = task209.RAW_PATH
    task209.write_json(raw_path, _sample_raw())
    norm = task209.normalize(json.loads(raw_path.read_text()))
    assert norm["row_count"] == 342
    assert norm["expected_row_count"] == 342
    assert norm["indicator_count"] == 6
    assert norm["country_count"] == 19
    assert norm["period_count"] == 3
    assert norm["acquisition_errors"] == []
    assert norm["rows"][0]["attributes"]["api_surface"] == "IMF DataMapper API v1"


def test_task209_acquisition_error_blocks_completion(tmp_path, monkeypatch):
    raw = _sample_raw()
    raw["requests"][0]["payload"] = {"error": "boom"}
    _redirect_outputs(monkeypatch, tmp_path)
    raw_path = task209.RAW_PATH
    task209.write_json(raw_path, raw)
    with pytest.raises(RuntimeError, match="TASK-209 completion blocked"):
        task209.normalize(raw)


def test_task209_build_sql_contains_run_key_and_quality_checks(tmp_path, monkeypatch):
    _redirect_outputs(monkeypatch, tmp_path)
    raw_path = task209.RAW_PATH
    task209.write_json(raw_path, _sample_raw())
    norm = task209.normalize(json.loads(raw_path.read_text()))
    sql = task209.build_sql(norm)
    assert "task-209-imf-weo-g20-projection-phase2" in sql
    assert "staging.task209_imf_weo_g20_projection_observation" in sql
    assert "expected_row_count" in sql
    assert "expected_shape" in sql


def test_task209_release_identity_and_value_status_are_preserved(tmp_path, monkeypatch):
    _redirect_outputs(monkeypatch, tmp_path)
    task209.write_json(task209.RAW_PATH, _sample_raw())
    norm = task209.normalize(json.loads(task209.RAW_PATH.read_text()))
    assert norm["release_identity"]["provider_release_source"] == "World Economic Outlook (April 2026)"
    assert norm["release_identity"]["release_key"] == "world-economic-outlook-april-2026"
    assert norm["release_identity"]["api_identity"]["versions"] == ["1"]
    assert norm["release_identity"]["api_exposes_row_level_value_status"] is False
    assert {r["attributes"]["value_status"] for r in norm["rows"]} == {"provider_current_weo_value_status_unspecified"}
    assert norm["rows"][0]["attributes"]["provider_release_key"] == "world-economic-outlook-april-2026"
    assert "indicator_semantics" in norm["rows"][0]["attributes"]


def test_task209_simulated_later_release_gets_distinct_release_and_run_key(tmp_path, monkeypatch):
    _redirect_outputs(monkeypatch, tmp_path)
    raw = _sample_raw()
    for meta in raw["metadata"]["indicators"].values():
        meta["source"] = "World Economic Outlook (October 2026)"
        meta["last-modified"] = "2026-10-08 12:00:00"
    task209.write_json(task209.RAW_PATH, raw)
    norm = task209.normalize(raw)
    assert norm["release_identity"]["release_key"] == "world-economic-outlook-october-2026"
    assert norm["run_key"].endswith("world-economic-outlook-october-2026")
    sql = task209.build_sql(norm)
    assert "world-economic-outlook-october-2026" in sql
    assert "world-economic-outlook-april-2026" not in sql


def test_task209_indicator_semantics_keep_units_and_measure_types_distinct():
    assert task209.INDICATOR_SEMANTICS["NGDPD"]["measure_type"] == "currency_amount"
    assert task209.INDICATOR_SEMANTICS["NGDP_RPCH"]["measure_type"] == "percentage_change"
    assert task209.INDICATOR_SEMANTICS["GGXWDG_NGDP"]["scale"] == "percent_of_gdp"
