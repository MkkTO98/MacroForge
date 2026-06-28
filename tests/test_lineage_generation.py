from __future__ import annotations

from macroforge.lineage_generation import canonical_lineage_events, lineage_values_sql


def test_canonical_lineage_events_generate_current_two_step_semantics_without_checksum():
    events = canonical_lineage_events(
        raw_artifact_path="data/metadata/wdi/raw.json",
        staging_artifact="staging.wdi_observation",
        staging_row_count_sql="(SELECT count(*)::bigint FROM staging.wdi_observation)",
        curated_row_count_sql="(SELECT count(*)::bigint FROM curated.fact_observation)",
        details={"task": "TASK-006"},
    )

    assert [event.event_type for event in events] == ["raw_to_staging", "staging_to_curated"]
    assert events[0].from_artifact == "data/metadata/wdi/raw.json"
    assert events[0].to_artifact == "staging.wdi_observation"
    assert events[0].checksum_sha256 is None
    assert events[0].row_count_sql == "(SELECT count(*)::bigint FROM staging.wdi_observation)"
    assert events[1].from_artifact == "staging.wdi_observation"
    assert events[1].to_artifact == "curated.fact_observation"
    assert events[1].checksum_sha256 is None
    assert events[1].row_count_sql == "(SELECT count(*)::bigint FROM curated.fact_observation)"
    assert all(event.details == {"task": "TASK-006"} for event in events)


def test_canonical_lineage_values_preserve_existing_loader_sql_shape_with_checksum():
    events = canonical_lineage_events(
        raw_artifact_path="data/metadata/oecd/raw.json",
        raw_checksum_sha256="abc123",
        staging_artifact="staging.oecd_sdmx_observation",
        staging_row_count_sql="(SELECT count(*)::bigint FROM staging.oecd_sdmx_observation swo JOIN run_row rr ON swo.pipeline_run_id = rr.pipeline_run_id)",
        curated_row_count_sql="(SELECT count(*)::bigint FROM curated.fact_observation)",
        details={"task": "TASK-015"},
    )

    assert lineage_values_sql(events, include_checksum=True) == """VALUES
      ('raw_to_staging', 'data/metadata/oecd/raw.json', 'staging.oecd_sdmx_observation', 'abc123', (SELECT count(*)::bigint FROM staging.oecd_sdmx_observation swo JOIN run_row rr ON swo.pipeline_run_id = rr.pipeline_run_id), '{\"task\": \"TASK-015\"}'::jsonb),
      ('staging_to_curated', 'staging.oecd_sdmx_observation', 'curated.fact_observation', NULL, (SELECT count(*)::bigint FROM curated.fact_observation), '{\"task\": \"TASK-015\"}'::jsonb)"""


def test_canonical_lineage_values_preserve_existing_loader_sql_shape_without_checksum_column():
    events = canonical_lineage_events(
        raw_artifact_path="data/metadata/wdi/raw.json",
        staging_artifact="staging.wdi_observation",
        staging_row_count_sql="(SELECT count(*)::bigint FROM staging.wdi_observation swo JOIN run_row rr ON swo.pipeline_run_id = rr.pipeline_run_id)",
        curated_row_count_sql="(SELECT count(*)::bigint FROM curated.fact_observation)",
        details={"task": "TASK-006"},
    )

    assert lineage_values_sql(events, include_checksum=False) == """VALUES
      ('raw_to_staging', 'data/metadata/wdi/raw.json', 'staging.wdi_observation', (SELECT count(*)::bigint FROM staging.wdi_observation swo JOIN run_row rr ON swo.pipeline_run_id = rr.pipeline_run_id), '{\"task\": \"TASK-006\"}'::jsonb),
      ('staging_to_curated', 'staging.wdi_observation', 'curated.fact_observation', (SELECT count(*)::bigint FROM curated.fact_observation), '{\"task\": \"TASK-006\"}'::jsonb)"""
