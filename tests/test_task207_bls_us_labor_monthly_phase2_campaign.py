from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import tools.task207_bls_us_labor_monthly_phase2_campaign as task207


def test_prediction_artifact_records_required_frozen_fields(tmp_path):
    original = task207.PRED_PATH
    try:
        task207.PRED_PATH = tmp_path / "prediction.json"
        prediction = task207.write_prediction()
        loaded = json.loads(task207.PRED_PATH.read_text())
    finally:
        task207.PRED_PATH = original

    assert prediction == loaded
    assert loaded["task"] == "TASK-207"
    assert loaded["selected_source"] == "BLS public API v2"
    assert "monthly labor-market" in loaded["selected_domain"]
    assert loaded["expected_repository_class"] == "source-specific monthly scalar time-series observations in existing curated fact substrate"
    assert loaded["existing_architecture_predicted_to_suffice"] is True


def test_normalize_preserves_monthly_provider_semantics_and_blocks_non_monthly():
    raw = {
        "task": "TASK-207",
        "status": "acquired",
        "acquired_at_utc": "2026-07-10T00:00:00+00:00",
        "request_series": list(task207.SERIES),
        "chunks": [
            {
                "startyear": 2010,
                "endyear": 2010,
                "raw_artifact_path": "data/raw/example.json",
                "raw_sha256": "0" * 64,
                "payload": {
                    "status": "REQUEST_SUCCEEDED",
                    "message": ["warning retained"],
                    "Results": {
                        "series": [
                            {
                                "seriesID": "LNS14000000",
                                "data": [
                                    {"year": "2010", "period": "M01", "periodName": "January", "value": "9.8", "footnotes": []},
                                    {"year": "2010", "period": "M13", "periodName": "Annual", "value": "9.7", "footnotes": []},
                                    {"year": "2010", "period": "M02", "periodName": "February", "value": "-", "footnotes": []},
                                ],
                            }
                        ]
                    },
                },
            }
        ],
    }
    normalized = task207.normalize(raw)

    assert normalized["row_count"] == 2
    assert normalized["observed_value_count"] == 1
    assert normalized["explicit_missing_value_count"] == 1
    assert normalized["provider_exclusions"] == [{"category": "non_monthly_period", "period": "M13", "series_id": "LNS14000000"}]
    assert normalized["acquisition_errors"]
    row = normalized["rows"][0]
    assert row["frequency"] == "M"
    assert row["provider_period_code"] == "2010-M01"
    assert row["unit_code"] == "PERCENT"
    assert row["attributes"]["seasonal_adjustment"] == "SA"


def test_load_sql_stays_source_specific_and_uses_monthly_periods(tmp_path):
    raw_path = task207.PROJECT_ROOT / "data/raw/task207_bls_us_labor_monthly_phase2_campaign/task-207-bls-us-labor-monthly-2010-2026.json"
    norm_path = task207.PROJECT_ROOT / "data/processed/task207_bls_us_labor_monthly_phase2_campaign/task-207-bls-us-labor-monthly-normalized.json"
    original_raw, original_norm = task207.RAW_PATH, task207.NORM_PATH
    try:
        task207.RAW_PATH = raw_path
        task207.NORM_PATH = norm_path
        row_attrs = {
            "task": "TASK-207",
            "source_provider": "BLS",
            "series_id": "LNS14000000",
            "series_name": "Unemployment rate, civilian labor force, seasonally adjusted",
            "domain": "labor_unemployment",
            "seasonal_adjustment": "SA",
            "frequency": "M",
            "provider_dataset_code": task207.PROVIDER_DATASET_CODE,
            "footnotes": [],
        }
        norm = {
            "task": "TASK-207",
            "repository_section": "Phase 2 U.S. labor-market enrichment",
            "repository_class": "monthly_scalar_time_series",
            "row_count": 1,
            "observed_value_count": 1,
            "period_count": 1,
            "period_range": "2010-M01:2010-M01",
            "raw_evidence": {"raw_sha256": "0" * 64, "source_url": "https://api.bls.gov/publicAPI/v2/timeseries/data/", "raw_artifact_path": "raw.json"},
            "input_filters": {"series": ["LNS14000000"]},
            "acquisition_errors": [],
            "expected_row_count": 1,
            "compatible_series_count": 1,
            "rows": [
                {
                    "series_id": "LNS14000000",
                    "series_name": "Unemployment rate, civilian labor force, seasonally adjusted",
                    "provider_period_code": "2010-M01",
                    "period_year": 2010,
                    "period_month": 1,
                    "value": "9.8",
                    "unit_code": "PERCENT",
                    "unit_label": "Percent",
                    "observation_status": "observed",
                    "decimal_precision": 1,
                    "attribute_hash": task207.attr_hash(row_attrs),
                    "attributes": row_attrs,
                    "source_payload": {"value": "9.8"},
                }
            ],
        }
        sql = task207.build_sql(norm)
    finally:
        task207.RAW_PATH, task207.NORM_PATH = original_raw, original_norm

    assert "staging.bls_us_labor_monthly_phase2_observation" in sql
    assert "BLS_PUBLIC_API_V2" in sql
    assert "BLS_US_LABOR_MONTHLY_PHASE2" not in sql
    assert "frequency='M'" in sql or "frequency = 'M'" in sql
    assert "make_date(staged.period_year,staged.period_month,1)" in sql
    assert "trade" not in sql.lower()
    assert "company" not in sql.lower()


def test_live_artifacts_are_valid_after_campaign_execution():
    manifest = json.loads(task207.MANIFEST_PATH.read_text())
    provider = json.loads(task207.PROVIDER_REPORT.read_text())
    load = json.loads(task207.LOAD_REPORT.read_text())
    evaluation = json.loads(task207.EVAL_REPORT.read_text())

    assert manifest["task"] == "TASK-207"
    assert manifest["row_count"] == 2374
    assert manifest["compatible_series_count"] == 12
    assert manifest["period_range"] == "2010-M01:2026-M06"
    assert provider["acquisition_errors"] == []
    assert load["fact_rows"] == 2374
    assert load["duplicate_canonical_key_groups"] == 0
    assert load["failed_quality_checks"] == 0
    assert load["idempotence"]["idempotent"] is True
    assert evaluation["prediction_quality_verdict"] == "Mostly Accurate"


def test_script_py_compiles():
    result = subprocess.run(
        [sys.executable, "-m", "py_compile", "tools/task207_bls_us_labor_monthly_phase2_campaign.py"],
        cwd=Path(__file__).resolve().parents[1],
        text=True,
        capture_output=True,
    )
    assert result.returncode == 0, result.stderr
