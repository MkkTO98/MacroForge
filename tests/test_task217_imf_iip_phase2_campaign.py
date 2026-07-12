from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
from pathlib import Path

import pytest

from tools import task217_imf_iip_phase2_campaign as task217


def _load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_task217_prediction_candidate_universe_is_frozen() -> None:
    prediction = _load_json(task217.PRED_PATH)
    assert prediction["task"] == "TASK-217"
    assert prediction["frozen_before_value_acquisition"] is True
    assert prediction["canonical_source_identity"] == "IMF_SDMX_IIP_API_V1"
    assert prediction["canonical_provider_dataset_identity"] == "IMF:IIP"
    assert prediction["distinct_run_identity"] == "task-217-imf-iip-external-position-phase2"
    assert prediction["expected_territory_coverage"] == 214
    assert prediction["exact_provider_advertised_series_count"] == 642
    assert prediction["expected_candidate_cells"] == 9630
    selected = {(row["accounting_entry"], row["indicator"]) for row in prediction["exact_provider_advertised_series"]}
    assert selected == set(task217.SELECTED_SERIES)


def test_task217_normalized_reconciliation_and_identity() -> None:
    normalized = _load_json(task217.NORM_PATH)
    assert normalized["task"] == "TASK-217"
    assert normalized["source_code"] == "IMF_SDMX_IIP_API_V1"
    assert normalized["provider_dataset_code"] == "IMF:IIP"
    assert normalized["release_key"] == "imf-iip-asof-20260711t233032958933600z"
    assert normalized["release_identity_basis"] == "provider dataset UPDATE_DATE/PUBLICATION_DATE/Prepared evidence"
    assert normalized["run_key"] == task217.RUN_KEY
    assert normalized["candidate_cell_count"] == 9630
    assert normalized["observed_value_count"] == 6969
    assert normalized["explicit_missing_value_count"] == 726
    assert normalized["whole_series_absence_count"] == 129
    assert normalized["incompatible_series_count"] == 0
    assert len(normalized["rows"]) == 7695
    assert normalized["observed_value_count"] + normalized["explicit_missing_value_count"] + normalized["whole_series_absence_count"] * 15 == normalized["candidate_cell_count"]
    assert {row["provider_indicator_code"] for row in normalized["rows"]} == {
        "IMF:IIP:A_P:IIP:USD:SCALE_6:A",
        "IMF:IIP:L_P:IIP:USD:SCALE_6:A",
        "IMF:IIP:NETAL_P:NIIP:USD:SCALE_6:A",
    }


def test_task217_raw_and_processed_checksums_match_manifest() -> None:
    checksum_path = task217.CHECKSUMS
    assert checksum_path.exists()
    entries = []
    for line in checksum_path.read_text(encoding="utf-8").splitlines():
        digest, rel_path = line.split("  ", 1)
        entries.append((digest, Path(rel_path)))
    assert len(entries) == 29
    mismatches = []
    for digest, path in entries:
        assert path.exists(), path
        actual = hashlib.sha256(path.read_bytes()).hexdigest()
        if actual != digest:
            mismatches.append(path.as_posix())
    assert mismatches == []
    raw_files = sorted((task217.RAW_DIR / "active").glob("task-217-imf-iip-*"))
    assert len(raw_files) == 21
    assert not list((task217.RAW_DIR / "_attempts").glob("**/*-error.json"))


def test_task217_load_report_and_prediction_evaluation() -> None:
    load = _load_json(task217.LOAD_REPORT)
    assert load["status"] == "succeeded"
    assert load["source_code"] == "IMF_SDMX_IIP_API_V1"
    assert load["provider_dataset_code"] == "IMF:IIP"
    assert load["release_key"] == "imf-iip-asof-20260711t233032958933600z"
    assert load["counts"] == {
        "dataset_release_rows": 1,
        "fact_rows": 7695,
        "failed_quality_checks": 0,
        "missing_facts": 726,
        "observed_facts": 6969,
        "staging_rows": 7695,
    }
    assert load["duplicate_canonical_key_groups"] == 0
    idempotence = _load_json(Path("artifacts/reports/task-217-imf-iip-postgresql-idempotence-report.json"))
    assert idempotence["counts"]["fact_rows"] == 7695
    evaluation = _load_json(task217.EVAL_REPORT)
    assert evaluation["prediction_verdict"] in {"Mostly Accurate", "Mixed"}
    assert evaluation["actual_candidate_cells"] == 9630


@pytest.mark.skipif(shutil.which("psql") is None, reason="psql unavailable")
def test_task217_postgresql_run_scope_verification() -> None:
    sql = """
WITH src AS (SELECT source_id FROM meta.source WHERE source_code='IMF_SDMX_IIP_API_V1'),
run AS (SELECT pipeline_run_id FROM meta.pipeline_run WHERE run_key='task-217-imf-iip-external-position-phase2')
SELECT
  (SELECT count(*) FROM meta.source WHERE source_code='IMF_SDMX_IIP_API_V1')::text || '|' ||
  (SELECT count(*) FROM meta.dataset_release dr JOIN src s ON dr.source_id=s.source_id WHERE provider_dataset_code='IMF:IIP' AND release_key='imf-iip-asof-20260711t233032958933600z')::text || '|' ||
  (SELECT count(*) FROM staging.task217_imf_iip_external_position_observation st JOIN run r ON st.pipeline_run_id=r.pipeline_run_id)::text || '|' ||
  (SELECT count(*) FROM curated.fact_observation f JOIN src s ON f.source_id=s.source_id JOIN run r ON f.pipeline_run_id=r.pipeline_run_id)::text || '|' ||
  (SELECT count(*) FROM curated.fact_observation f JOIN src s ON f.source_id=s.source_id JOIN run r ON f.pipeline_run_id=r.pipeline_run_id WHERE observation_status='observed')::text || '|' ||
  (SELECT count(*) FROM curated.fact_observation f JOIN src s ON f.source_id=s.source_id JOIN run r ON f.pipeline_run_id=r.pipeline_run_id WHERE observation_status='missing')::text || '|' ||
  (SELECT count(DISTINCT indicator_id) FROM curated.fact_observation f JOIN src s ON f.source_id=s.source_id JOIN run r ON f.pipeline_run_id=r.pipeline_run_id)::text || '|' ||
  (SELECT count(DISTINCT territory_id) FROM curated.fact_observation f JOIN src s ON f.source_id=s.source_id JOIN run r ON f.pipeline_run_id=r.pipeline_run_id)::text || '|' ||
  (SELECT count(DISTINCT period_id) FROM curated.fact_observation f JOIN src s ON f.source_id=s.source_id JOIN run r ON f.pipeline_run_id=r.pipeline_run_id)::text || '|' ||
  (SELECT count(*) FROM meta.quality_check q JOIN run r ON q.pipeline_run_id=r.pipeline_run_id WHERE q.check_status='fail')::text || '|' ||
  (SELECT count(*) FROM (SELECT source_id, indicator_id, territory_id, period_id, unit_id, attribute_set_id, as_of_date, count(*) FROM curated.fact_observation GROUP BY 1,2,3,4,5,6,7 HAVING count(*)>1) d)::text;
"""
    out = subprocess.run(["psql", "-d", "macroforge", "-At", "-c", sql], check=True, capture_output=True, text=True).stdout.strip()
    assert out == "1|1|7695|7695|6969|726|3|171|15|0|0"
