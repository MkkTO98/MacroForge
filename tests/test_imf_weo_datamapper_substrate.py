from __future__ import annotations

import json
from pathlib import Path

from macroforge import imf_weo_datamapper as weo
import tools.task209_imf_weo_g20_projection_phase2_campaign as task209
import tools.task211_imf_weo_broad_macro_repository_expansion as task211


def test_shared_weo_identity_is_not_campaign_scoped():
    assert weo.SOURCE_CODE == "IMF_WEO_DATAMAPPER_API_V1"
    assert weo.PROVIDER_DATASET_CODE == "IMF:WEO:DATAMAPPER"
    assert task209.PROVIDER_DATASET_CODE == weo.PROVIDER_DATASET_CODE
    assert task211.PROVIDER_DATASET_CODE == weo.PROVIDER_DATASET_CODE
    assert task209.RUN_KEY_PREFIX != task211.RUN_KEY_PREFIX


def test_release_key_and_later_release_contract():
    meta = {"NGDPD": {"source": "World Economic Outlook (April 2026)", "last-modified": "2026-04-08"}}
    release = weo.release_evidence_from_indicator_meta(meta, "2026-07-11T00:00:00+00:00", [{"version": "1"}])
    assert release["release_key"] == "world-economic-outlook-april-2026"
    assert weo.run_key_for_release("task-x", release["release_key"]) == "task-x-world-economic-outlook-april-2026"
    meta["NGDPD"]["source"] = "World Economic Outlook (October 2026)"
    assert weo.release_evidence_from_indicator_meta(meta, None, [])["release_key"] == "world-economic-outlook-october-2026"


def test_missingness_value_status_and_indicator_contracts():
    assert weo.VALUE_STATUS_UNSPECIFIED == "provider_current_weo_value_status_unspecified"
    assert weo.explicit_missing_reason(False, None) == "year_key_absent_from_otherwise_valid_country_indicator_series"
    assert weo.explicit_missing_reason(True, None) == "explicit_null_or_missing_value_in_country_indicator_series"
    assert weo.explicit_missing_reason(True, "1.0") is None
    assert weo.canonical_indicator_id("NGDPD") == "IMF_WEO:NGDPD"


def test_indicator_partition_manifest_reconciles_and_detects_checksums(tmp_path):
    rows = [
        {"indicator_code": "A", "territory_code": "USA", "provider_period_code": "2026", "observation_status": "observed"},
        {"indicator_code": "A", "territory_code": "USA", "provider_period_code": "2027", "observation_status": "missing"},
        {"indicator_code": "B", "territory_code": "DNK", "provider_period_code": "2026", "observation_status": "observed"},
    ]
    norm = {"task": "T", "row_count": 3, "observed_provider_value_count": 2, "explicit_missing_fact_count": 1, "rows": rows}
    manifest = weo.partition_rows_by_indicator(norm, output_dir=tmp_path / "partitions", project_root=tmp_path)
    assert manifest["partition_count"] == 2
    assert manifest["partition_totals"] == {"row_count": 3, "observed_provider_value_count": 2, "explicit_missing_fact_count": 1}
    loaded = weo.load_partitioned_rows(manifest, project_root=tmp_path)
    assert [(r["indicator_code"], r["territory_code"], r["provider_period_code"]) for r in loaded] == [("A", "USA", "2026"), ("A", "USA", "2027"), ("B", "DNK", "2026")]
    first_path = tmp_path / manifest["partitions"][0]["path"]
    first_path.write_text(first_path.read_text() + "\n")
    try:
        weo.load_partitioned_rows(manifest, project_root=tmp_path)
    except ValueError as exc:
        assert "checksum mismatch" in str(exc)
    else:
        raise AssertionError("checksum mismatch was not detected")


def test_task211_uses_25_country_transport_default():
    assert weo.CONSERVATIVE_COUNTRY_CHUNK_SIZE == 25
    assert "country_chunk_size = weo.CONSERVATIVE_COUNTRY_CHUNK_SIZE" in Path(task211.__file__).read_text()


def test_staging_upsert_refreshes_mutable_provenance_fields_transactionally():
    for module in (task209, task211):
        assert module.__file__ is not None
        text = Path(module.__file__).read_text()
        assert "BEGIN;" in text and "COMMIT;" in text
        assert "ON CONFLICT (pipeline_run_id, territory_code, indicator_code, provider_period_code) DO UPDATE SET" in text
        conflict = text.split("ON CONFLICT (pipeline_run_id, territory_code, indicator_code, provider_period_code) DO UPDATE SET", 1)[1].split(";", 1)[0]
        # Existing staging rows from obsolete campaign-specific releases must be corrected by a normal loader rerun.
        assert "source_id=EXCLUDED.source_id" in conflict
        assert "dataset_release_id=EXCLUDED.dataset_release_id" in conflict
        # Other mutable provenance/normalization fields are refreshed consistently, while identity columns remain the conflict key.
        for field in ["territory_label", "indicator_name", "period_year", "unit_code", "unit_label", "observation_status", "attribute_hash", "attributes", "source_payload"]:
            assert f"{field}=EXCLUDED.{field}" in conflict
        assert module.PROVIDER_DATASET_CODE == "IMF:WEO:DATAMAPPER"
