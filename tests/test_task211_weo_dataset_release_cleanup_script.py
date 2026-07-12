from __future__ import annotations

import json
from pathlib import Path


SCRIPT = Path("artifacts/reports/task-211-weo-dataset-release-cleanup.sql")
CORRECTED_JSON_ARTIFACTS = [
    Path("artifacts/reports/task-211-weo-dataset-release-cleanup-audit.json"),
    Path("artifacts/reports/task-211-weo-dataset-release-cleanup-audit-after-loader.json"),
    Path("artifacts/reports/task-211-weo-dataset-release-cleanup-execution-audit.json"),
]
PRESERVED_TRANSCRIPTS = [path.with_suffix(".original-psql-transcript.log") for path in CORRECTED_JSON_ARTIFACTS]


def test_cleanup_script_excludes_its_own_temp_target_from_reference_count():
    text = SCRIPT.read_text()
    assert "CREATE TEMP TABLE _target_dataset_release" in text
    assert "table_schema NOT LIKE 'pg_temp_%'" in text
    assert "table_schema NOT LIKE 'pg_toast_temp_%'" in text
    assert "_target_dataset_release" in text
    assert "_deleted_dataset_release" in text
    assert "IF NOT (tbl.table_schema = 'meta' AND tbl.table_name = 'dataset_release')" in text


def test_cleanup_script_remains_bounded_to_approved_weo_releases():
    text = SCRIPT.read_text()
    assert "s.source_code = 'IMF_WEO_DATAMAPPER_API_V1'" in text
    assert "dr.release_key = 'world-economic-outlook-april-2026'" in text
    assert "IMF:WEO:DATAMAPPER:BROAD_MACRO_ANNUAL" in text
    assert "IMF:WEO:DATAMAPPER:PROJECTIONS" in text
    assert "DELETE FROM meta.dataset_release" in text
    assert "RETURNING t.source_code, t.provider_dataset_code, t.release_key" in text


def test_corrected_cleanup_audit_json_artifacts_parse_and_preserve_transcripts():
    for path, transcript in zip(CORRECTED_JSON_ARTIFACTS, PRESERVED_TRANSCRIPTS):
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert payload["task"] == "TASK-211"
        assert payload["canonical_source"] == "IMF_WEO_DATAMAPPER_API_V1"
        assert payload["canonical_dataset"] == "IMF:WEO:DATAMAPPER"
        assert payload["canonical_release"] == "world-economic-outlook-april-2026"
        assert transcript.exists()
        assert payload["provenance_links"]["preserved_transcript"] == str(transcript)
        assert payload["current_read_only_verification_evidence"]["canonical_release_rows"] == 1
        assert payload["current_read_only_verification_evidence"]["obsolete_rows"] == 0


def test_execution_summary_points_raw_psql_evidence_to_preserved_log():
    summary = json.loads(Path("artifacts/reports/task-211-weo-dataset-release-cleanup-execution-summary.json").read_text(encoding="utf-8"))
    assert summary["raw_psql_audit"].endswith(".original-psql-transcript.log")
    assert summary["corrected_structured_audit"].endswith("task-211-weo-dataset-release-cleanup-execution-audit.json")
    assert len(summary["artifact_format_correction"]["transcript_paths"]) == 3
