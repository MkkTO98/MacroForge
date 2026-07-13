import hashlib
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def read_json(path: str):
    return json.loads((PROJECT_ROOT / path).read_text(encoding="utf-8"))


def test_task219_normalized_shape_and_identities():
    norm = read_json("data/processed/task219_imf_dip_phase2_campaign/active/task-219-imf-dip-normalized.json")
    assert norm["task"] == "TASK-219"
    assert norm["source_code"] == "IMF_SDMX_DIP_API_V1"
    assert norm["provider_dataset_code"] == "IMF:DIP"
    assert norm["release_key"] == "imf-dip-asof-20251210t162520656782100z"
    assert norm["release_as_of_date"] == "2025-12-10"
    assert norm["run_key"] == "task-219-imf-dip-direct-investment-counterpart-phase2"
    assert norm["candidate_cell_count"] == 17280
    assert norm["candidate_series_count"] == 3456
    assert len(norm["rows"]) == 16215
    assert norm["observed_value_count"] == 14755
    assert norm["explicit_missing_value_count"] == 1460
    assert norm["whole_series_absence_count"] == 213
    assert norm["incompatible_series_count"] == 0


def test_task219_counterpart_and_direct_investment_semantics_preserved():
    norm = read_json("data/processed/task219_imf_dip_phase2_campaign/active/task-219-imf-dip-normalized.json")
    rows = norm["rows"]
    assert rows
    selected = {"AUS", "BEL", "BRA", "CAN", "CHE", "CHN", "DEU", "DNK", "ESP", "FRA", "GBR", "HKG", "IND", "IRL", "ITA", "JPN", "KOR", "LUX", "MEX", "NLD", "NOR", "SGP", "SWE", "USA"}
    sample = rows[0]
    attrs = sample["attributes"]
    assert attrs["reporter_country"] == sample["territory_code"]
    assert attrs["counterpart_country"] in selected
    assert f"COUNTERPART_{attrs['counterpart_country']}" in sample["provider_indicator_code"]
    assert attrs["dip_dv_type"] == "O"
    assert "_D_" in attrs["dip_indicator"]
    assert attrs["direct_investment_entity"] in {"ALL", None}
    assert attrs["unit"] == "USD"
    assert attrs["scale"] == "6"
    assert attrs["value_status"] == "provider_dip_value_status_preserved_when_obs_status_present_otherwise_unspecified"


def test_task219_manifest_reports_and_database_counts_reconcile():
    manifest = read_json("data/processed/task219_imf_dip_phase2_campaign/active/task-219-imf-dip-manifest.json")
    load = read_json("artifacts/reports/task-219-imf-dip-postgresql-load-report.json")
    idem = read_json("artifacts/reports/task-219-imf-dip-postgresql-idempotence-report.json")
    coexist = read_json("artifacts/reports/task-219-imf-dip-later-asof-coexistence-report.json")
    assert manifest["row_count"] == 16215
    assert manifest["observed_value_count"] == 14755
    assert manifest["explicit_missing_value_count"] == 1460
    assert len(manifest["raw_active_files"]) == 11
    assert load["counts"]["fact_rows"] == 16215
    assert load["counts"]["observed_facts"] == 14755
    assert load["counts"]["missing_facts"] == 1460
    assert load["counts"]["failed_quality_checks"] == 0
    assert load["duplicate_canonical_key_groups"] == 0
    assert idem["total_growth"] == 0
    assert idem["source_growth"] == 0
    assert coexist["status"] == "succeeded"
    assert coexist["transaction_output"] == "simulated_later_rows|1|1"
    assert coexist["post_rollback_simulated_release_rows"] == 0


def test_task219_relationship_proliferation_verdict():
    report = read_json("artifacts/reports/task-219-imf-dip-relationship-proliferation-report.json")
    assert report["representation_verdict"] == "B"
    assert report["reporters"] == 24
    assert report["counterparts"] == 24
    assert report["instrument_concept_combinations"] == 6
    assert report["theoretical_series_count"] == 3456
    assert report["canonical_indicators_created"] == 144
    assert report["canonical_key_collapse_detected"] is False
    assert report["comparison_with_task218"]["task218_canonical_indicators"] == 72


def test_task219_checksum_file_matches_artifacts():
    checksum_path = PROJECT_ROOT / "artifacts/reports/task-219-imf-dip-artifact-checksums.txt"
    assert checksum_path.exists()
    lines = [line for line in checksum_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    assert len(lines) == 22
    for line in lines:
        digest, relpath = line.split("  ", 1)
        target = PROJECT_ROOT / relpath
        assert target.exists(), relpath
        actual = hashlib.sha256(target.read_bytes()).hexdigest()
        assert actual == digest, relpath


def test_task219_prediction_evaluation_classifies_actuals():
    pred = read_json("artifacts/reports/task-219-imf-dip-frozen-pre-execution-prediction.json")
    evaluation = read_json("artifacts/reports/task-219-imf-dip-prediction-evaluation.json")
    assert pred["expected_candidate_cells"] == 17280
    assert pred["expected_provider_valued_facts"] == 10368
    assert pred["expected_explicit_missing_facts"] == 3456
    assert evaluation["actual_candidate_cells"] == 17280
    assert evaluation["actual_provider_valued_facts"] == 14755
    assert evaluation["actual_explicit_missing_facts"] == 1460
    assert evaluation["prediction_verdict"] == "Mixed"
