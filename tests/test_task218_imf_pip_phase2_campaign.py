import hashlib
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def read_json(path: str):
    return json.loads((PROJECT_ROOT / path).read_text(encoding="utf-8"))


def test_task218_normalized_shape_and_identities():
    norm = read_json("data/processed/task218_imf_pip_phase2_campaign/active/task-218-imf-pip-normalized.json")
    assert norm["task"] == "TASK-218"
    assert norm["source_code"] == "IMF_SDMX_PIP_API_V1"
    assert norm["provider_dataset_code"] == "IMF:PIP"
    assert norm["release_key"] == "imf-pip-asof-20260311t004734566029300z"
    assert norm["release_as_of_date"] == "2026-03-11"
    assert norm["run_key"] == "task-218-imf-pip-portfolio-counterpart-phase2"
    assert norm["candidate_cell_count"] == 8640
    assert norm["candidate_series_count"] == 1728
    assert len(norm["rows"]) == 8275
    assert norm["observed_value_count"] == 8000
    assert norm["explicit_missing_value_count"] == 275
    assert norm["whole_series_absence_count"] == 73
    assert norm["incompatible_series_count"] == 0


def test_task218_counterpart_semantics_preserved_in_indicator_and_attributes():
    norm = read_json("data/processed/task218_imf_pip_phase2_campaign/active/task-218-imf-pip-normalized.json")
    rows = norm["rows"]
    assert rows
    sample = rows[0]
    attrs = sample["attributes"]
    assert attrs["reporter_country"] == sample["territory_code"]
    assert attrs["counterpart_country"] in {"AUS", "BEL", "BRA", "CAN", "CHE", "CHN", "DEU", "DNK", "ESP", "FRA", "GBR", "HKG", "IND", "IRL", "ITA", "JPN", "KOR", "LUX", "MEX", "NLD", "NOR", "SGP", "SWE", "USA"}
    assert f"COUNTERPART_{attrs['counterpart_country']}" in sample["provider_indicator_code"]
    assert attrs["sector"] == "S1"
    assert attrs["counterpart_sector"] == "S1"
    assert attrs["value_status"] == "provider_pip_value_status_unspecified"


def test_task218_manifest_and_reports_reconcile_counts():
    manifest = read_json("data/processed/task218_imf_pip_phase2_campaign/active/task-218-imf-pip-manifest.json")
    load = read_json("artifacts/reports/task-218-imf-pip-postgresql-load-report.json")
    idem = read_json("artifacts/reports/task-218-imf-pip-postgresql-idempotence-report.json")
    coexist = read_json("artifacts/reports/task-218-imf-pip-later-asof-coexistence-report.json")
    assert manifest["row_count"] == 8275
    assert manifest["observed_value_count"] == 8000
    assert manifest["explicit_missing_value_count"] == 275
    assert load["counts"]["fact_rows"] == 8275
    assert load["counts"]["observed_facts"] == 8000
    assert load["counts"]["missing_facts"] == 275
    assert load["counts"]["failed_quality_checks"] == 0
    assert load["duplicate_canonical_key_groups"] == 0
    assert idem["same_run_idempotence"]["postgresql_growth"] == 0
    assert coexist["status"] == "passed_rolled_back_sample"
    assert coexist["after_rollback"] == {"simulated_run_facts": 0, "simulated_run_rows": 0}


def test_task218_checksum_file_matches_artifacts():
    checksum_path = PROJECT_ROOT / "artifacts/reports/task-218-imf-pip-artifact-checksums.txt"
    assert checksum_path.exists()
    lines = [line for line in checksum_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(lines) >= 10
    for line in lines:
        digest, relpath = line.split("  ", 1)
        target = PROJECT_ROOT / relpath
        assert target.exists(), relpath
        actual = hashlib.sha256(target.read_bytes()).hexdigest()
        assert actual == digest, relpath


def test_task218_prediction_evaluation_classifies_actuals():
    pred = read_json("artifacts/reports/task-218-imf-pip-frozen-pre-execution-prediction.json")
    evaluation = read_json("artifacts/reports/task-218-imf-pip-prediction-evaluation.json")
    assert pred["expected_candidate_cells"] == 8640
    assert pred["expected_provider_valued_facts"] == 6048
    assert evaluation["actual_candidate_cells"] == 8640
    assert evaluation["actual_provider_valued_facts"] == 8000
    assert evaluation["actual_explicit_missing_facts"] == 275
    assert evaluation["prediction_verdict"] in {"Mostly Accurate", "Mixed"}
