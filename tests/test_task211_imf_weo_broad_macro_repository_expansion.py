from __future__ import annotations

import json
from pathlib import Path

import pytest

import tools.task211_imf_weo_broad_macro_repository_expansion as task211


def test_task211_scope_preserves_task209_and_uses_canonical_imf_source():
    assert task211.TASK_ID == "TASK-211"
    assert task211.USER_REQUESTED_TASK_ID == "TASK-210"
    assert task211.SOURCE_CODE == "IMF_WEO_DATAMAPPER_API_V1"
    assert task211.PROVIDER_DATASET_CODE == "IMF:WEO:DATAMAPPER"
    assert len(task211.INDICATORS) == 12
    assert task211.YEARS[0] == "2015"
    assert task211.YEARS[-1] == "2028"
    assert task211.is_task209_overlap("USA", "NGDPD", "2026") is True
    assert task211.is_task209_overlap("USA", "NGDPDPC", "2026") is False


def _sample_raw():
    indicators = {
        code: {
            "label": code,
            "description": f"Description {code}",
            "source": "World Economic Outlook (April 2026)",
            "unit": "Percent of GDP" if code.endswith("_NGDP") or code.endswith("_NGDPD") or code == "NI_GDP" else "Annual percent change",
            "dataset": "WEO",
            "last-modified": "2026-04-08 16:07:34",
        }
        for code in task211.INDICATORS
    }
    countries = {"USA": {"label": "United States"}, "DNK": {"label": "Denmark"}}
    requests = []
    for ind in task211.INDICATORS:
        requests.append({"indicator_code": ind, "url": f"https://example.test/{ind}", "payload": {"api": {"version": "1"}, "values": {ind: {"USA": {year: 1.0 for year in task211.YEARS}, "DNK": {year: 2.0 for year in task211.YEARS}}}}})
    return {"task": "TASK-211", "attempt_id": "attempt-test", "accessed_at_utc": "2026-07-11T00:00:00+00:00", "countries": ["DNK", "USA"], "years": list(task211.YEARS), "indicator_codes": list(task211.INDICATORS), "candidate_cells": len([1 for c in ["DNK", "USA"] for i in task211.INDICATORS for y in task211.YEARS if not task211.is_task209_overlap(c, i, y)]), "task209_overlap_excluded_cells": len([1 for c in ["DNK", "USA"] for i in task211.INDICATORS for y in task211.YEARS if task211.is_task209_overlap(c, i, y)]), "provider_aggregate_entities": ["ATI", "ATL"], "unsupported_entities": ["TWN"], "metadata": {"countries": countries, "indicators": indicators, "api": {"countries": {"version": "1"}, "indicators": {"version": "1"}}}, "requests": requests, "acquisition_errors": []}


def test_task211_normalization_excludes_exact_task209_overlap(tmp_path, monkeypatch):
    raw_path = tmp_path / "raw.json"
    raw = _sample_raw()
    raw_path.write_text(json.dumps(raw, sort_keys=True))
    monkeypatch.setattr(task211, "RAW_ACTIVE_PATH", raw_path)
    norm = task211.normalize(raw, raw_path)
    assert norm["release_identity"]["release_key"] == "world-economic-outlook-april-2026"
    assert norm["row_count"] == raw["candidate_cells"]
    assert norm["task209_overlap_excluded_cells"] == 18
    assert not any(r for r in norm["rows"] if r["territory_code"] == "USA" and r["indicator_code"] in task211.TASK209_INDICATORS and r["provider_period_code"] in task211.TASK209_YEARS)
    assert {r["attributes"]["value_status"] for r in norm["rows"]} == {"provider_current_weo_value_status_unspecified"}


def test_task211_explicit_missing_is_candidate_cell_not_acquisition_error(tmp_path, monkeypatch):
    raw = _sample_raw()
    del raw["requests"][0]["payload"]["values"][task211.INDICATORS[0]]["DNK"]["2028"]
    raw_path = tmp_path / "raw.json"
    raw_path.write_text(json.dumps(raw, sort_keys=True))
    monkeypatch.setattr(task211, "RAW_ACTIVE_PATH", raw_path)
    norm = task211.normalize(raw, raw_path)
    missing = [r for r in norm["rows"] if r["indicator_code"] == task211.INDICATORS[0] and r["territory_code"] == "DNK" and r["provider_period_code"] == "2028"]
    assert len(missing) == 1
    assert missing[0]["observation_status"] == "missing"
    assert missing[0]["attributes"]["missing_reason"] == "year_key_absent_from_otherwise_valid_country_indicator_series"
    assert norm["acquisition_errors"] == []


def test_task211_acquisition_errors_block_completion(tmp_path, monkeypatch):
    raw = _sample_raw()
    raw["requests"][0]["payload"] = {"error": "boom"}
    raw["acquisition_errors"] = [{"indicator_code": task211.INDICATORS[0], "error": "boom"}]
    raw_path = tmp_path / "raw.json"
    raw_path.write_text(json.dumps(raw, sort_keys=True))
    monkeypatch.setattr(task211, "RAW_ACTIVE_PATH", raw_path)
    with pytest.raises(RuntimeError, match="completion blocked"):
        task211.normalize(raw, raw_path)


def test_task211_later_release_coexists_by_release_specific_run_key(tmp_path, monkeypatch):
    raw = _sample_raw()
    for meta in raw["metadata"]["indicators"].values():
        meta["source"] = "World Economic Outlook (October 2026)"
    raw_path = tmp_path / "raw.json"
    raw_path.write_text(json.dumps(raw, sort_keys=True))
    monkeypatch.setattr(task211, "RAW_ACTIVE_PATH", raw_path)
    norm = task211.normalize(raw, raw_path)
    assert norm["release_identity"]["release_key"] == "world-economic-outlook-october-2026"
    assert norm["run_key"].endswith("world-economic-outlook-october-2026")
    sql = task211.build_sql(norm)
    assert "world-economic-outlook-october-2026" in sql
    assert task211.TASK209_RUN_KEY not in sql


def test_task211_indicator_units_keep_semantics_distinct():
    assert task211.INDICATOR_SEMANTICS["NGDPD"]["measure_type"] == "currency_amount"
    assert task211.INDICATOR_SEMANTICS["NGDP_RPCH"]["measure_type"] == "percentage_change"
    assert task211.INDICATOR_SEMANTICS["NGDPDPC"]["measure_type"] == "currency_per_capita"
    assert task211.INDICATOR_SEMANTICS["BCA_NGDPD"]["scale"] == "percent_of_gdp"
