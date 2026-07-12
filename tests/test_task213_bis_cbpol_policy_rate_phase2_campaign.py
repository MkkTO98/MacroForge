from __future__ import annotations

import hashlib
import json
from pathlib import Path

from tools import task213_bis_cbpol_policy_rate_phase2_campaign as campaign

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _load_normalized() -> dict:
    path = PROJECT_ROOT / "data/processed/task213_bis_cbpol_policy_rate_phase2_campaign/active/task-213-bis-cbpol-policy-rate-normalized.json"
    assert path.exists()
    return json.loads(path.read_text(encoding="utf-8"))


def test_task213_candidate_reconciliation_and_counts():
    norm = _load_normalized()
    assert norm["task"] == "TASK-213"
    assert norm["source_code"] == "BIS_PUBLIC_SDMX_API"
    assert norm["provider_dataset_code"] == "BIS:WS_CBPOL"
    assert norm["candidate_territory_count"] == 37
    assert norm["candidate_period_count"] == 138
    assert norm["candidate_cell_count"] == 5106
    assert norm["row_count"] == 5106
    assert norm["observed_value_count"] == 5082
    assert norm["explicit_missing_value_count"] == 24
    assert norm["acquisition_errors"] == []
    assert norm["provider_exclusions"] == []
    assert norm["observed_value_count"] + norm["explicit_missing_value_count"] == norm["candidate_cell_count"]


def test_task213_bis_identity_separation_and_entity_classification():
    norm = _load_normalized()
    assert norm["source_code"] != norm["provider_dataset_code"]
    assert norm["source_code"] == "BIS_PUBLIC_SDMX_API"
    assert norm["provider_dataset_code"] == "BIS:WS_CBPOL"
    assert norm["run_key"] == "task-213-bis-cbpol-policy-rate-phase2"
    exclusions = {(e["provider_code"], e["category"]) for e in norm["selection_exclusions"]}
    assert ("XM", "aggregate_selection_exclusion") in exclusions
    accepted = {e["provider_code"] for e in norm["territory_reconciliation"]["accepted_candidate_territories"]}
    assert "XM" not in accepted
    assert "HK" in accepted
    assert {"US", "JP", "GB", "CN", "BR", "ZA", "HK"}.issubset(accepted)
    assert norm["territory_reconciliation"]["unsupported_entities"] == []
    assert norm["territory_reconciliation"]["mapping_failures"] == []


def test_task213_preserves_bis_dimensions_and_units_without_semantic_flattening():
    norm = _load_normalized()
    row = next(r for r in norm["rows"] if r["provider_territory_code"] == "US" and r["provider_period_code"] == "2024-M01")
    assert row["provider_indicator_code"] == "BIS:WS_CBPOL:CENTRAL_BANK_POLICY_RATE:PERCENT:M"
    assert row["provider_series_key"] == "M.US"
    assert row["unit_code"] == "PERCENT"
    assert row["frequency"] == "M"
    attrs = row["attributes"]
    assert attrs["dataflow"] == "WS_CBPOL"
    assert attrs["series_key"] == "M.US"
    assert attrs["ref_area"] == "US"
    assert attrs["unit_measure_provider_code"] == "368"
    assert attrs["measure"] == "central_bank_policy_rate"
    assert "source_ref" in attrs
    assert "compilation" in attrs
    assert "snapshot_release_key" in attrs
    assert row["attribute_hash"] == campaign.attr_hash(attrs)


def test_task213_indicator_identity_is_measure_unit_frequency_not_territory():
    norm = _load_normalized()
    indicator_codes = {r["provider_indicator_code"] for r in norm["rows"]}
    assert indicator_codes == {"BIS:WS_CBPOL:CENTRAL_BANK_POLICY_RATE:PERCENT:M"}
    by_territory = {r["provider_territory_code"]: r["provider_indicator_code"] for r in norm["rows"]}
    assert by_territory["US"] == by_territory["DK"] == by_territory["HK"]
    assert campaign.canonical_indicator_code("central_bank_policy_rate", "PERCENT", "M") == "BIS:WS_CBPOL:CENTRAL_BANK_POLICY_RATE:PERCENT:M"
    assert campaign.canonical_indicator_code("central_bank_policy_rate", "INDEX", "M") != campaign.canonical_indicator_code("central_bank_policy_rate", "PERCENT", "M")
    assert campaign.canonical_indicator_code("central_bank_policy_rate", "PERCENT", "Q") != campaign.canonical_indicator_code("central_bank_policy_rate", "PERCENT", "M")
    assert campaign.canonical_indicator_code("policy_rate_change", "PERCENT", "M") != campaign.canonical_indicator_code("central_bank_policy_rate", "PERCENT", "M")


def test_task213_cross_country_retrieval_uses_one_indicator_plus_territory():
    norm = _load_normalized()
    rows_2024 = [r for r in norm["rows"] if r["provider_period_code"] == "2024-M01" and r["provider_territory_code"] in {"US", "DK", "HK"}]
    assert len(rows_2024) == 3
    assert {r["provider_indicator_code"] for r in rows_2024} == {"BIS:WS_CBPOL:CENTRAL_BANK_POLICY_RATE:PERCENT:M"}
    assert {r["territory_code"] for r in rows_2024} == {"USA", "DNK", "HKG"}


def test_task213_snapshot_release_identity_is_provider_snapshot_not_query_window():
    metadata = {"prepared": "2026-07-12T11:45:54Z"}
    same_a = campaign.release_key_from_provider_metadata(metadata, "a" * 64)
    same_b = campaign.release_key_from_provider_metadata(metadata, "b" * 64)
    assert same_a == same_b == "bis-ws-cbpol-snapshot-prepared-20260712t114554z"
    later = campaign.release_key_from_provider_metadata({"prepared": "2026-07-13T00:00:00Z"}, "a" * 64)
    assert later != same_a
    assert campaign.source_url("2015-01", "2026-06") != campaign.source_url("2020-01", "2024-12")
    assert campaign.release_key_from_provider_metadata(metadata, "a" * 64) == same_a
    assert campaign.build_run_key(same_a) != campaign.build_run_key(later)


def test_task213_explicit_missing_is_candidate_grid_absence_inside_valid_series():
    norm = _load_normalized()
    missing = [r for r in norm["rows"] if r["observation_status"] == "missing"]
    assert len(missing) == 24
    assert {r["provider_territory_code"] for r in missing} == {"ID", "IN", "JP", "MA"}
    assert all(r["value"] is None for r in missing)
    assert all(r["source_payload"]["missing_basis"] == "candidate_period_absent_inside_valid_series" for r in missing)
    hk = [r for r in norm["rows"] if r["provider_territory_code"] == "HK"]
    assert len(hk) == 138
    assert all(r["observation_status"] == "observed" for r in hk)


def test_task213_manifest_checksums_and_prediction_are_parseable():
    report_dir = PROJECT_ROOT / "artifacts/reports"
    processed = PROJECT_ROOT / "data/processed/task213_bis_cbpol_policy_rate_phase2_campaign/active"
    for path in [
        report_dir / "task-213-bis-cbpol-policy-rate-frozen-pre-execution-prediction.json",
        report_dir / "task-213-bis-cbpol-policy-rate-provider-evidence-report.json",
        report_dir / "task-213-bis-cbpol-policy-rate-postgresql-load-report.json",
        report_dir / "task-213-bis-cbpol-policy-rate-prediction-evaluation.json",
        processed / "task-213-bis-cbpol-policy-rate-manifest.json",
    ]:
        assert path.exists()
        json.loads(path.read_text(encoding="utf-8"))
    checksum_path = report_dir / "task-213-bis-cbpol-policy-rate-artifact-checksums.txt"
    lines = checksum_path.read_text(encoding="utf-8").strip().splitlines()
    assert lines
    for line in lines:
        digest, rel_path = line.split("  ", 1)
        assert len(digest) == 64
        target = PROJECT_ROOT / rel_path
        assert target.exists()
        assert hashlib.sha256(target.read_bytes()).hexdigest() == digest


def test_task213_load_report_records_obsolete_metadata_audit_without_cleanup():
    report = json.loads((PROJECT_ROOT / "artifacts/reports/task-213-bis-cbpol-policy-rate-postgresql-load-report.json").read_text(encoding="utf-8"))
    assert report["corrected_dataset_snapshot_rows"] == 1
    assert report["all_bis_ws_cbpol_dataset_release_rows"] >= 1
    audit = report["obsolete_metadata_reference_audit"]
    assert audit["legacy_country_encoded_indicators"]["indicator_rows"] == 36
    assert audit["legacy_country_encoded_indicators"]["fact_refs"] == 0
    assert audit["legacy_window_bound_release"]["dataset_release_rows"] == 1
    assert audit["legacy_window_bound_release"]["fact_refs"] == 0
    assert report["obsolete_metadata_cleanup_status"] == "not_deleted_requires_explicit_authorization"


def test_task213_prediction_evaluation_reclassified_after_identity_correction():
    evaluation = json.loads((PROJECT_ROOT / "artifacts/reports/task-213-bis-cbpol-policy-rate-prediction-evaluation.json").read_text(encoding="utf-8"))
    assert evaluation["prediction_quality_verdict"] == "Mixed"
    assert evaluation["missing_bis_understanding_revealed"] is True
    assert evaluation["scale_prediction_error"]["actual_candidate_cells"] == 5106


def test_task213_script_remains_bis_specific_not_generic_provider_framework():
    source = (PROJECT_ROOT / "tools/task213_bis_cbpol_policy_rate_phase2_campaign.py").read_text(encoding="utf-8")
    forbidden = [
        "class GenericSdmxAdapter",
        "class UniversalCampaignEngine",
        "class ProviderFramework",
        "class FinancialDataOntology",
        "class BisClient",
        "PluginRegistry",
        "BaseSource",
    ]
    for token in forbidden:
        assert token not in source
