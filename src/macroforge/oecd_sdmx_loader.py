from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from macroforge.db_helpers import jsonb_literal, parse_pipe_counts, psql_scalar, run_psql_file, sql_literal, write_json_report
from macroforge.observed_ingestion import build_oecd_observed_package, canonical_attribute_hash

SOURCE_CODE = "OECD_NAAG"
SOURCE_NAME = "OECD annual national accounts / NAAG Chapter 1 GDP dataflow"
SOURCE_HOME_URL = "https://sdmx.oecd.org/"
DEFAULT_PIPELINE_NAME = "oecd_sdmx_smoke_slice"
DEFAULT_AS_OF_DATE = "2026-06-03"


def json_literal(value: Any) -> str:
    return jsonb_literal(value)


def _release_key(normalized: dict[str, Any]) -> str:
    return build_oecd_observed_package(normalized).release_key


def _observation_status(attributes: dict[str, Any], value: Any) -> str:
    if value is None:
        return "missing"
    obs_status = str(attributes.get("OBS_STATUS", "A"))
    if obs_status in {"M", "L", "N"}:
        return "missing"
    if obs_status in {"S", "C"}:
        return "suppressed"
    return "observed"


def _decimal_precision(attributes: dict[str, Any]) -> int | None:
    decimals = attributes.get("DECIMALS")
    if decimals is None or decimals == "":
        return None
    return int(decimals)


def build_load_sql(
    normalized: dict[str, Any],
    *,
    run_key: str = "oecd-sdmx-smoke-20260603",
    as_of_date: str = DEFAULT_AS_OF_DATE,
) -> str:
    package = build_oecd_observed_package(normalized)
    rows = normalized["rows"]
    release_key = package.release_key
    provider_dataset_code = package.provider_dataset_code
    raw_metadata = normalized.get("raw_metadata", {})
    source_url = package.raw_evidence["source_url"]
    raw_artifact_path = package.raw_evidence["raw_artifact_path"]
    raw_sha256 = package.raw_evidence["raw_sha256"]
    metadata = {
        "filters": normalized.get("filters"),
        "raw_metadata": raw_metadata,
        "row_count": normalized.get("row_count"),
        "units": sorted({row.get("unit") for row in rows}),
    }

    values = []
    for observation in package.observations:
        series_dimensions = dict(observation.source_payload.get("series_dimensions") or {})
        values.append(
            "(" + ", ".join(
                [
                    sql_literal(provider_dataset_code),
                    sql_literal(observation.provider_indicator_code),
                    sql_literal(observation.provider_territory_code),
                    sql_literal(observation.period_year),
                    sql_literal(observation.frequency),
                    sql_literal(observation.unit_code),
                    sql_literal(observation.value),
                    sql_literal(observation.observation_status),
                    sql_literal(observation.decimal_precision),
                    json_literal(observation.attributes),
                    json_literal(series_dimensions),
                    json_literal(observation.source_payload),
                    sql_literal(observation.attribute_hash),
                ]
            ) + ")"
        )
    values_sql = ",\n".join(values)

    return f"""
BEGIN;

CREATE TEMP TABLE _oecd_sdmx_rows (
    provider_dataset_code text NOT NULL,
    measure_code text NOT NULL,
    ref_area_code text NOT NULL,
    period_year integer NOT NULL,
    frequency text NOT NULL,
    unit_measure_code text NOT NULL,
    value numeric,
    observation_status text NOT NULL,
    decimal_precision integer,
    attributes jsonb NOT NULL,
    series_dimensions jsonb NOT NULL,
    source_payload jsonb NOT NULL,
    attribute_hash text NOT NULL
) ON COMMIT DROP;

INSERT INTO _oecd_sdmx_rows (
    provider_dataset_code, measure_code, ref_area_code, period_year, frequency,
    unit_measure_code, value, observation_status, decimal_precision, attributes,
    series_dimensions, source_payload, attribute_hash
) VALUES
{values_sql};

WITH upsert_source AS (
    INSERT INTO meta.source (source_code, source_name, source_home_url, license_note)
    VALUES ({sql_literal(SOURCE_CODE)}, {sql_literal(SOURCE_NAME)}, {sql_literal(SOURCE_HOME_URL)}, 'OECD no-key public SDMX smoke slice')
    ON CONFLICT (source_code) DO UPDATE
      SET source_name = EXCLUDED.source_name,
          source_home_url = EXCLUDED.source_home_url,
          license_note = EXCLUDED.license_note
    RETURNING source_id
), source_row AS (
    SELECT source_id FROM upsert_source
    UNION ALL
    SELECT source_id FROM meta.source WHERE source_code = {sql_literal(SOURCE_CODE)}
    LIMIT 1
), upsert_release AS (
    INSERT INTO meta.dataset_release (source_id, provider_dataset_code, release_key, release_date, source_url, raw_artifact_path, raw_sha256, metadata)
    SELECT source_id, {sql_literal(provider_dataset_code)}, {sql_literal(release_key)}, {sql_literal(as_of_date)}::date,
           {sql_literal(source_url)}, {sql_literal(raw_artifact_path)}, {sql_literal(raw_sha256)}, {json_literal(metadata)}
    FROM source_row
    ON CONFLICT (source_id, provider_dataset_code, release_key) DO UPDATE
      SET release_date = EXCLUDED.release_date,
          source_url = EXCLUDED.source_url,
          raw_artifact_path = EXCLUDED.raw_artifact_path,
          raw_sha256 = EXCLUDED.raw_sha256,
          metadata = EXCLUDED.metadata
    RETURNING dataset_release_id
), release_row AS (
    SELECT dataset_release_id FROM upsert_release
    UNION ALL
    SELECT dr.dataset_release_id
    FROM meta.dataset_release dr JOIN source_row s ON dr.source_id = s.source_id
    WHERE dr.provider_dataset_code = {sql_literal(provider_dataset_code)} AND dr.release_key = {sql_literal(release_key)}
    LIMIT 1
), upsert_run AS (
    INSERT INTO meta.pipeline_run (run_key, source_id, dataset_release_id, pipeline_name, finished_at, status, input_parameters, artifact_manifest)
    SELECT {sql_literal(run_key)}, s.source_id, r.dataset_release_id, {sql_literal(DEFAULT_PIPELINE_NAME)}, now(), 'succeeded',
           {json_literal({'filters': normalized.get('filters'), 'provider_dataset_code': provider_dataset_code})},
           {json_literal({'row_count': normalized.get('row_count'), 'raw_metadata': raw_metadata})}
    FROM source_row s CROSS JOIN release_row r
    ON CONFLICT (run_key) DO UPDATE
      SET finished_at = EXCLUDED.finished_at,
          status = EXCLUDED.status,
          input_parameters = EXCLUDED.input_parameters,
          artifact_manifest = EXCLUDED.artifact_manifest
    RETURNING pipeline_run_id
), run_row AS (
    SELECT pipeline_run_id FROM upsert_run
    UNION ALL
    SELECT pipeline_run_id FROM meta.pipeline_run WHERE run_key = {sql_literal(run_key)}
    LIMIT 1
)
INSERT INTO staging.oecd_sdmx_observation (
    pipeline_run_id, source_id, dataset_release_id, provider_dataset_code, measure_code,
    ref_area_code, period_year, frequency, unit_measure_code, value,
    observation_status, decimal_precision, attributes, series_dimensions, source_payload, as_of_date
)
SELECT run.pipeline_run_id, s.source_id, rel.dataset_release_id, r.provider_dataset_code, r.measure_code,
       r.ref_area_code, r.period_year, r.frequency, r.unit_measure_code, r.value,
       r.observation_status, r.decimal_precision, r.attributes, r.series_dimensions, r.source_payload,
       {sql_literal(as_of_date)}::date
FROM _oecd_sdmx_rows r CROSS JOIN source_row s CROSS JOIN release_row rel CROSS JOIN run_row run
ON CONFLICT (pipeline_run_id, provider_dataset_code, measure_code, ref_area_code, period_year, unit_measure_code) DO UPDATE
  SET value = EXCLUDED.value,
      observation_status = EXCLUDED.observation_status,
      decimal_precision = EXCLUDED.decimal_precision,
      attributes = EXCLUDED.attributes,
      series_dimensions = EXCLUDED.series_dimensions,
      source_payload = EXCLUDED.source_payload;

WITH source_row AS (
    SELECT source_id FROM meta.source WHERE source_code = {sql_literal(SOURCE_CODE)}
), distinct_indicators AS (
    SELECT DISTINCT measure_code FROM _oecd_sdmx_rows
)
INSERT INTO curated.dim_indicator (source_id, source_indicator_code, indicator_name)
SELECT s.source_id, d.measure_code, d.measure_code
FROM source_row s CROSS JOIN distinct_indicators d
ON CONFLICT (source_id, source_indicator_code) DO UPDATE SET indicator_name = EXCLUDED.indicator_name;

WITH distinct_territories AS (
    SELECT DISTINCT ref_area_code FROM _oecd_sdmx_rows
)
INSERT INTO curated.dim_territory (territory_type, iso3_code, canonical_territory_code, territory_name)
SELECT 'country', d.ref_area_code, d.ref_area_code, d.ref_area_code
FROM distinct_territories d
ON CONFLICT (canonical_territory_code) DO UPDATE
  SET territory_name = EXCLUDED.territory_name;

INSERT INTO curated.dim_period (frequency, period_year, period_start_date, period_end_date, period_label)
SELECT DISTINCT frequency, period_year, make_date(period_year, 1, 1), make_date(period_year, 12, 31), period_year::text
FROM _oecd_sdmx_rows
ON CONFLICT (frequency, period_start_date, period_end_date) DO UPDATE
  SET period_label = EXCLUDED.period_label;

WITH source_row AS (
    SELECT source_id FROM meta.source WHERE source_code = {sql_literal(SOURCE_CODE)}
), distinct_periods AS (
    SELECT DISTINCT provider_dataset_code, frequency, period_year FROM _oecd_sdmx_rows
)
INSERT INTO meta.provider_period_mapping (source_id, provider_dataset_code, provider_period_code, period_id, provider_label)
SELECT s.source_id, d.provider_dataset_code, d.period_year::text, p.period_id, d.period_year::text
FROM source_row s
CROSS JOIN distinct_periods d
JOIN curated.dim_period p
  ON p.frequency = d.frequency
 AND p.period_start_date = make_date(d.period_year, 1, 1)
 AND p.period_end_date = make_date(d.period_year, 12, 31)
ON CONFLICT (source_id, provider_dataset_code, provider_period_code) DO UPDATE
  SET period_id = EXCLUDED.period_id,
      provider_label = EXCLUDED.provider_label;

WITH source_row AS (
    SELECT source_id FROM meta.source WHERE source_code = {sql_literal(SOURCE_CODE)}
), distinct_territories AS (
    SELECT DISTINCT provider_dataset_code, ref_area_code FROM _oecd_sdmx_rows
)
INSERT INTO meta.provider_territory_mapping (source_id, provider_dataset_code, provider_territory_code, code_system, territory_id, provider_label)
SELECT s.source_id, d.provider_dataset_code, d.ref_area_code, 'oecd_ref_area', t.territory_id, d.ref_area_code
FROM source_row s
CROSS JOIN distinct_territories d
JOIN curated.dim_territory t ON t.iso3_code = d.ref_area_code
ON CONFLICT (source_id, provider_dataset_code, code_system, provider_territory_code) DO UPDATE
  SET territory_id = EXCLUDED.territory_id,
      provider_label = EXCLUDED.provider_label;

INSERT INTO curated.dim_unit (unit_code, unit_name)
SELECT DISTINCT unit_measure_code, unit_measure_code
FROM _oecd_sdmx_rows
ON CONFLICT (unit_code) DO UPDATE SET unit_name = EXCLUDED.unit_name;

INSERT INTO curated.dim_attribute_set (attribute_hash, attributes)
SELECT DISTINCT attribute_hash, attributes
FROM _oecd_sdmx_rows
ON CONFLICT (attribute_hash) DO UPDATE SET attributes = EXCLUDED.attributes;

WITH source_row AS (
    SELECT source_id FROM meta.source WHERE source_code = {sql_literal(SOURCE_CODE)}
), release_row AS (
    SELECT dr.dataset_release_id FROM meta.dataset_release dr JOIN source_row s ON dr.source_id = s.source_id
    WHERE dr.provider_dataset_code = {sql_literal(provider_dataset_code)} AND dr.release_key = {sql_literal(release_key)}
), run_row AS (
    SELECT pipeline_run_id FROM meta.pipeline_run WHERE run_key = {sql_literal(run_key)}
)
INSERT INTO curated.fact_observation (
    source_id, dataset_release_id, pipeline_run_id, indicator_id, territory_id,
    period_id, unit_id, attribute_set_id, value, as_of_date, observation_status
)
SELECT s.source_id, rel.dataset_release_id, run.pipeline_run_id, i.indicator_id, t.territory_id,
       p.period_id, u.unit_id, a.attribute_set_id, r.value,
       {sql_literal(as_of_date)}::date,
       r.observation_status
FROM _oecd_sdmx_rows r
CROSS JOIN source_row s
CROSS JOIN release_row rel
CROSS JOIN run_row run
JOIN curated.dim_indicator i ON i.source_id = s.source_id AND i.source_indicator_code = r.measure_code
JOIN curated.dim_territory t ON t.iso3_code = r.ref_area_code
JOIN curated.dim_period p ON p.frequency = r.frequency AND p.period_start_date = make_date(r.period_year, 1, 1) AND p.period_end_date = make_date(r.period_year, 12, 31)
JOIN curated.dim_unit u ON u.unit_code = r.unit_measure_code
JOIN curated.dim_attribute_set a ON a.attribute_hash = r.attribute_hash
ON CONFLICT (source_id, indicator_id, territory_id, period_id, unit_id, attribute_set_id, as_of_date) DO UPDATE
  SET value = EXCLUDED.value,
      pipeline_run_id = EXCLUDED.pipeline_run_id,
      dataset_release_id = EXCLUDED.dataset_release_id,
      observation_status = EXCLUDED.observation_status;

WITH source_row AS (
    SELECT source_id FROM meta.source WHERE source_code = {sql_literal(SOURCE_CODE)}
), run_row AS (
    SELECT pipeline_run_id FROM meta.pipeline_run WHERE run_key = {sql_literal(run_key)}
)
INSERT INTO meta.lineage_event (pipeline_run_id, source_id, event_type, from_artifact, to_artifact, checksum_sha256, row_count, details)
SELECT run.pipeline_run_id, s.source_id, event_type, from_artifact, to_artifact, checksum_sha256, row_count, details
FROM source_row s CROSS JOIN run_row run CROSS JOIN (
    VALUES
      ('raw_to_staging', {sql_literal(raw_artifact_path)}, 'staging.oecd_sdmx_observation', {sql_literal(raw_sha256)}, (SELECT count(*)::bigint FROM staging.oecd_sdmx_observation swo JOIN run_row rr ON swo.pipeline_run_id = rr.pipeline_run_id), {json_literal({'task': 'TASK-015'})}),
      ('staging_to_curated', 'staging.oecd_sdmx_observation', 'curated.fact_observation', NULL, (SELECT count(*)::bigint FROM curated.fact_observation), {json_literal({'task': 'TASK-015'})})
) AS v(event_type, from_artifact, to_artifact, checksum_sha256, row_count, details)
WHERE NOT EXISTS (
    SELECT 1 FROM meta.lineage_event le
    WHERE le.pipeline_run_id = run.pipeline_run_id AND le.event_type = v.event_type
);

WITH source_row AS (
    SELECT source_id FROM meta.source WHERE source_code = {sql_literal(SOURCE_CODE)}
), run_row AS (
    SELECT pipeline_run_id FROM meta.pipeline_run WHERE run_key = {sql_literal(run_key)}
)
INSERT INTO meta.quality_check (pipeline_run_id, check_name, check_status, severity, observed_value, expected_value, details)
SELECT run.pipeline_run_id, check_name, check_status, severity, observed_value, expected_value, details
FROM run_row run CROSS JOIN (
    VALUES
      ('oecd_sdmx_expected_staging_rows', CASE WHEN (SELECT count(*) FROM staging.oecd_sdmx_observation swo JOIN run_row rr ON swo.pipeline_run_id = rr.pipeline_run_id) = {normalized.get('row_count', 8)} THEN 'pass' ELSE 'fail' END, 'error', (SELECT count(*)::numeric FROM staging.oecd_sdmx_observation swo JOIN run_row rr ON swo.pipeline_run_id = rr.pipeline_run_id), {normalized.get('row_count', 8)}::numeric, {json_literal({'scope': 'staging'})}),
      ('oecd_sdmx_expected_fact_rows', CASE WHEN (SELECT count(*) FROM curated.fact_observation fo JOIN source_row s ON fo.source_id = s.source_id) = {normalized.get('row_count', 8)} THEN 'pass' ELSE 'fail' END, 'error', (SELECT count(*)::numeric FROM curated.fact_observation fo JOIN source_row s ON fo.source_id = s.source_id), {normalized.get('row_count', 8)}::numeric, {json_literal({'scope': 'curated_source'})}),
      ('oecd_sdmx_expected_units', CASE WHEN (SELECT count(DISTINCT unit_code) FROM curated.dim_unit WHERE unit_code IN ('USD_EXC', 'USD_PPP')) = 2 THEN 'pass' ELSE 'fail' END, 'error', (SELECT count(DISTINCT unit_code)::numeric FROM curated.dim_unit WHERE unit_code IN ('USD_EXC', 'USD_PPP')), 2::numeric, {json_literal({'scope': 'units'})}),
      ('oecd_sdmx_expected_attribute_sets', CASE WHEN (SELECT count(DISTINCT fo.attribute_set_id) FROM curated.fact_observation fo JOIN source_row s ON fo.source_id = s.source_id) = 1 THEN 'pass' ELSE 'fail' END, 'error', (SELECT count(DISTINCT fo.attribute_set_id)::numeric FROM curated.fact_observation fo JOIN source_row s ON fo.source_id = s.source_id), 1::numeric, {json_literal({'scope': 'attributes_source'})})
) AS v(check_name, check_status, severity, observed_value, expected_value, details)
WHERE NOT EXISTS (
    SELECT 1 FROM meta.quality_check qc
    WHERE qc.pipeline_run_id = run.pipeline_run_id AND qc.check_name = v.check_name
);

COMMIT;
"""


def _counts(db_name: str) -> dict[str, Any]:
    sql = """
    SELECT
      (SELECT count(*) FROM staging.oecd_sdmx_observation),
      (SELECT count(*) FROM curated.fact_observation),
      (SELECT count(*) FROM meta.lineage_event),
      (SELECT count(*) FROM meta.quality_check),
      (SELECT count(*) FROM curated.dim_attribute_set),
      (SELECT string_agg(unit_code, ',' ORDER BY unit_code) FROM curated.dim_unit)
    """
    return parse_pipe_counts(
        psql_scalar(db_name, sql),
        [
            ("staging_rows", int),
            ("fact_rows", int),
            ("lineage_events", int),
            ("quality_checks", int),
            ("attribute_sets", int),
            ("unit_codes", lambda value: value.split(",") if value else []),
        ],
    )


def load_oecd_sdmx_smoke_to_postgres(
    db_name: str,
    normalized_path: str | Path,
    *,
    run_key: str = "oecd-sdmx-smoke-20260603",
    as_of_date: str = DEFAULT_AS_OF_DATE,
) -> dict[str, Any]:
    normalized = json.loads(Path(normalized_path).read_text(encoding="utf-8"))
    sql = build_load_sql(normalized, run_key=run_key, as_of_date=as_of_date)
    run_psql_file(db_name, sql)
    return _counts(db_name)


def write_load_report(path: str | Path, payload: dict[str, Any]) -> dict[str, Any]:
    return write_json_report(path, payload, default_task="TASK-015")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Load MacroForge OECD/SDMX smoke rows to PostgreSQL")
    parser.add_argument("--db", required=True, help="PostgreSQL database name")
    parser.add_argument("--normalized", default="data/metadata/oecd_sdmx/oecd-sdmx-smoke-normalized.json")
    parser.add_argument("--run-key", default="oecd-sdmx-smoke-20260603")
    parser.add_argument("--as-of-date", default=DEFAULT_AS_OF_DATE)
    parser.add_argument("--report", default="artifacts/reports/oecd-sdmx-load-smoke-20260603.json")
    args = parser.parse_args(argv)

    result = load_oecd_sdmx_smoke_to_postgres(args.db, args.normalized, run_key=args.run_key, as_of_date=args.as_of_date)
    write_load_report(args.report, result)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
