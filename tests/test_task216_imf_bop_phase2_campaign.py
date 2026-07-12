from __future__ import annotations

import json
from pathlib import Path

import tools.task216_imf_bop_phase2_campaign as task216


def test_task216_identity_and_indicator_code_preserve_non_territory_dimensions():
    assert task216.TASK_ID == "TASK-216"
    assert task216.SOURCE_CODE == "IMF_SDMX_BOP_API_V1"
    assert task216.PROVIDER_DATASET_CODE == "IMF:BOP"
    code = task216.canonical_indicator_code("CAB")
    assert code == "IMF:BOP:NETCD_T:CAB:USD:SCALE_6:A"
    assert "USA" not in code
    assert "NETCD_T" in code
    assert "USD" in code
    assert code.endswith(":A")


def test_task216_frozen_prediction_counts_and_scope():
    pred = task216.write_provider_report_and_prediction()
    assert pred["task"] == "TASK-216"
    assert pred["frozen_before_value_acquisition"] is True
    assert pred["canonical_source_identity"] == "IMF_SDMX_BOP_API_V1"
    assert pred["canonical_provider_dataset_identity"] == "IMF:BOP"
    assert pred["period_range"] == {"start": "2010", "end": "2024", "periods": 15}
    assert pred["exact_provider_advertised_series_count"] == len(pred["accepted_territories"]) * 5
    assert pred["expected_candidate_cells"] == pred["exact_provider_advertised_series_count"] * 15
    assert "query-window bounds" in pred["release_identity_rule"]
    assert "BIS" in pred["why_stronger_than_another_bis_or_small_proof"]


def test_task216_provider_report_records_full_bop_key_dimensions():
    report = json.loads(task216.PROVIDER_REPORT.read_text(encoding="utf-8")) if task216.PROVIDER_REPORT.exists() else task216.write_provider_report_and_prediction()
    if "provider_dataset_code" not in report:
        report = json.loads(task216.PROVIDER_REPORT.read_text(encoding="utf-8"))
    assert report["series_key_dimensions"] == ["COUNTRY", "BOP_ACCOUNTING_ENTRY", "INDICATOR", "UNIT", "FREQUENCY"]
    assert report["territory_dimension"] == "COUNTRY"
    assert report["accounting_component_dimensions"] == ["BOP_ACCOUNTING_ENTRY", "INDICATOR"]
    assert report["currency_unit_scale"]["unit"] == "USD"
    assert report["currency_unit_scale"]["scale"] == "6"


def test_task216_normalized_active_artifact_reconciles_observed_missing_and_absence_when_present():
    if not task216.NORM_PATH.exists():
        return
    norm = json.loads(task216.NORM_PATH.read_text(encoding="utf-8"))
    assert norm["candidate_cell_count"] == 16050
    assert norm["observed_value_count"] == 13600
    assert norm["explicit_missing_value_count"] == 875
    assert norm["whole_series_absence_count"] == 105
    assert norm["incompatible_series_count"] == 0
    assert len(norm["rows"]) == norm["observed_value_count"] + norm["explicit_missing_value_count"]
    first = norm["rows"][0]
    assert first["attributes"]["bop_accounting_entry"] == "NETCD_T"
    assert first["attributes"]["frequency"] == "A"
    assert first["unit_code"] == "USD_SCALE_6"


def test_task216_asof_identity_prefers_provider_update_date_over_acquisition_prepared():
    headers = [
        {
            "dataset_attributes": {
                "UPDATE_DATE": "2026-07-11T23:14:24.302015100Z",
                "PUBLICATION_DATE": "2026-07-11T23:14:24.269092200Z",
            },
            "prepared": "2026-07-12T18:44:36Z",
        }
    ]
    assert task216.release_key_from_responses(headers) == "imf-bop-asof-20260711t231424302015100z"


def test_task216_active_artifact_uses_one_provider_dataset_update_asof_for_all_chunks():
    if not task216.NORM_PATH.exists():
        return
    norm = json.loads(task216.NORM_PATH.read_text(encoding="utf-8"))
    assert norm["release_key"] == "imf-bop-asof-20260711t231424302015100z"
    updates = {
        h["dataset_attributes"].get("UPDATE_DATE")
        for h in norm["provider_response_headers"]
    }
    publications = {
        h["dataset_attributes"].get("PUBLICATION_DATE")
        for h in norm["provider_response_headers"]
    }
    prepared = {h.get("prepared") for h in norm["provider_response_headers"]}
    assert updates == {"2026-07-11T23:14:24.302015100Z"}
    assert publications == {"2026-07-11T23:14:24.269092200Z"}
    assert len(prepared) == 9
    assert all(p.startswith("2026-07-12T18:44:") for p in prepared)


def test_task216_active_artifact_reconciles_whole_series_absence_distribution():
    if not task216.NORM_PATH.exists():
        return
    norm = json.loads(task216.NORM_PATH.read_text(encoding="utf-8"))
    by_territory = {}
    for absence in norm["whole_series_absence"]:
        by_territory.setdefault(absence["provider_territory_code"], []).append(absence["indicator"])
    assert len(norm["whole_series_absence"]) == 105
    assert sorted(by_territory) == [
        "ASM", "CAF", "CUB", "ERI", "GIB", "GNQ", "GRL", "GUM", "IMN", "IRN", "LIE", "MAF", "MCO", "MNP", "PRI", "PRK", "SOM", "TCD", "TKM", "VGB", "VIR",
    ]
    assert all(sorted(v) == ["CAB", "G", "IN1", "IN2", "S"] for v in by_territory.values())
    assert norm["observed_value_count"] + norm["explicit_missing_value_count"] + len(norm["whole_series_absence"]) * 15 == norm["candidate_cell_count"]


def test_task216_values_sql_preserves_missing_status_and_unit():
    row = {
        "territory_code": "USA",
        "territory_label": "United States",
        "provider_indicator_code": task216.canonical_indicator_code("CAB"),
        "provider_indicator_label": "Current account balance",
        "provider_period_code": "2024",
        "period_year": 2024,
        "value": None,
        "unit_code": "USD_SCALE_6",
        "unit_label": "US dollar, millions",
        "decimal_precision": None,
        "observation_status": "missing",
        "attribute_hash": "abc",
        "attributes": {"bop_indicator": "CAB"},
        "source_payload": {},
    }
    sql = task216.values_sql([row])
    assert "missing" in sql
    assert "USD_SCALE_6" in sql
    assert "IMF:BOP:NETCD_T:CAB:USD:SCALE_6:A" in sql
