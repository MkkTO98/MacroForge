from __future__ import annotations

from pathlib import Path


SCRIPT = Path("artifacts/reports/task-211-weo-dataset-release-cleanup.sql")


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
