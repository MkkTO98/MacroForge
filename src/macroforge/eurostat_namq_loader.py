from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from macroforge.db_helpers import jsonb_literal, parse_pipe_counts, psql_scalar, run_psql_file, sql_literal, write_json_report
from macroforge.lineage_generation import canonical_lineage_events, lineage_values_sql
from macroforge.observed_ingestion import build_eurostat_observed_package, canonical_attribute_hash

SOURCE_CODE = "EUROSTAT_NAMQ_GDP"
SOURCE_NAME = "Eurostat quarterly national accounts GDP"
SOURCE_HOME_URL = "https://ec.europa.eu/eurostat/"
DEFAULT_PIPELINE_NAME = "eurostat_namq_smoke_slice"
DEFAULT_AS_OF_DATE = "2026-06-04"

GEO_TO_ISO3 = {
    "DE": "DEU",
    "FR": "FRA",
}


def json_literal(value: Any) -> str:
    return jsonb_literal(value)


def _release_key(normalized: dict[str, Any]) -> str:
    return build_eurostat_observed_package(normalized).release_key


def _quarter_start_month(quarter: int) -> int:
    return ((quarter - 1) * 3) + 1


def _quarter_end_month(quarter: int) -> int:
    return quarter * 3


def _quarter_end_day(quarter: int) -> int:
    return 31 if quarter in {1, 4} else 30


def _attribute_payload(normalized: dict[str, Any], row: dict[str, Any]) -> dict[str, Any]:
    status = row.get("source_payload", {}).get("status")
    attributes: dict[str, Any] = {
        "source": "Eurostat",
        "provider_dataset_code": normalized["provider_dataset_code"],
        "freq": row["frequency"],
        "s_adj": row["seasonal_adjustment"],
        "s_adj_label": row.get("seasonal_adjustment_name"),
        "observation_status": row.get("observation_status", "observed"),
    }
    if status is not None:
        attributes["jsonstat_status"] = status
    return attributes


def _row_values(normalized: dict[str, Any]) -> str:
    values = []
    for row in normalized["rows"]:
        payload = dict(row.get("source_payload") or {})
        dimensions = dict(payload.get("dimensions") or {})
        flat_index = payload.get("jsonstat_flat_index")
        jsonstat_flat_index = int(flat_index) if flat_index is not None else None
        attribute_payload = _attribute_payload(normalized, row)
        values.append(
            "(" + ", ".join(
                [
                    sql_literal(row["provider_dataset_code"]),
                    sql_literal(row["frequency"]),
                    sql_literal(row["unit"]),
                    sql_literal(row.get("unit_name")),
                    sql_literal(row["seasonal_adjustment"]),
                    sql_literal(row.get("seasonal_adjustment_name")),
                    sql_literal(row["indicator_code"]),
                    sql_literal(row.get("indicator_name")),
                    sql_literal(row["territory_code"]),
                    sql_literal(row.get("territory_name")),
                    sql_literal(GEO_TO_ISO3[row["territory_code"]]),
                    sql_literal(row["period"]),
                    sql_literal(int(row["period_year"])),
                    sql_literal(int(row["period_quarter"])),
                    sql_literal(_quarter_start_month(int(row["period_quarter"]))),
                    sql_literal(_quarter_end_month(int(row["period_quarter"]))),
                    sql_literal(_quarter_end_day(int(row["period_quarter"]))),
                    sql_literal(row.get("value")),
                    sql_literal(row.get("observation_status", "observed")),
                    sql_literal(row.get("decimal_precision")),
                    sql_literal(row.get("as_of_date")),
                    sql_literal(jsonstat_flat_index),
                    json_literal(dimensions),
                    json_literal(payload),
                    json_literal(attribute_payload),
                    sql_literal(canonical_attribute_hash(attribute_payload)),
                ]
            ) + ")"
        )
    return ",\n".join(values)


def _provider_code_values(normalized: dict[str, Any]) -> str:
    labels = normalized.get("dimensions", {}).get("labels", {})
    values = []
    code_systems = {
        "freq": "eurostat_freq",
        "unit": "eurostat_unit",
        "s_adj": "eurostat_s_adj",
        "na_item": "eurostat_na_item",
        "geo": "eurostat_geo",
        "time": "eurostat_time",
    }
    for dimension_name in normalized.get("dimensions", {}).get("id", []):
        for provider_code, provider_label in sorted(labels.get(dimension_name, {}).items()):
            values.append(
                "(" + ", ".join(
                    [
                        sql_literal(dimension_name),
                        sql_literal(code_systems[dimension_name]),
                        sql_literal(provider_code),
                        sql_literal(provider_label),
                    ]
                ) + ")"
            )
    return ",\n".join(values)


def build_load_sql(
    normalized: dict[str, Any],
    *,
    run_key: str = "eurostat-namq-smoke-20260604",
    as_of_date: str = DEFAULT_AS_OF_DATE,
) -> str:
    package = build_eurostat_observed_package(normalized)
    provider_dataset_code = package.provider_dataset_code
    release_key = package.release_key
    metadata = {
        "access_method": normalized.get("access_method"),
        "content_type": normalized.get("content_type"),
        "filters": normalized.get("filters"),
        "dimensions": normalized.get("dimensions"),
        "fetched_at_utc": normalized.get("fetched_at_utc"),
        "http_status": normalized.get("http_status"),
        "row_count": normalized.get("row_count"),
    }
    raw_metadata = {
        "raw_artifact_path": normalized.get("raw_artifact_path"),
        "raw_sha256": normalized.get("raw_sha256"),
        "raw_bytes": normalized.get("raw_bytes"),
    }
    row_values_sql = _row_values(normalized)
    code_values_sql = _provider_code_values(normalized)
    expected_rows = int(normalized.get("row_count", len(normalized.get("rows", []))))
    lineage_events = canonical_lineage_events(
        raw_artifact_path=normalized.get("raw_artifact_path"),
        raw_checksum_sha256=normalized.get("raw_sha256"),
        staging_artifact="staging.eurostat_namq_observation",
        staging_row_count_sql="(SELECT count(*)::bigint FROM staging.eurostat_namq_observation eno JOIN run_row rr ON eno.pipeline_run_id = rr.pipeline_run_id)",
        curated_row_count_sql="(SELECT count(*)::bigint FROM curated.fact_observation)",
        details={"task": "TASK-024"},
    )
    lineage_values = lineage_values_sql(lineage_events, include_checksum=True)

    return f"""
BEGIN;

CREATE TEMP TABLE _eurostat_namq_rows (
    provider_dataset_code text NOT NULL,
    frequency text NOT NULL,
    unit_code text NOT NULL,
    unit_name text,
    seasonal_adjustment_code text NOT NULL,
    seasonal_adjustment_name text,
    national_accounts_item_code text NOT NULL,
    national_accounts_item_name text,
    provider_geo_code text NOT NULL,
    provider_geo_name text,
    canonical_iso3_code text NOT NULL,
    provider_period_code text NOT NULL,
    period_year integer NOT NULL,
    period_quarter integer NOT NULL,
    quarter_start_month integer NOT NULL,
    quarter_end_month integer NOT NULL,
    quarter_end_day integer NOT NULL,
    observation_value numeric NOT NULL,
    observation_status text NOT NULL,
    decimal_precision integer,
    as_of_date date NOT NULL,
    jsonstat_flat_index integer,
    source_dimensions jsonb NOT NULL,
    source_payload jsonb NOT NULL,
    attributes jsonb NOT NULL,
    attribute_hash text NOT NULL
) ON COMMIT DROP;

INSERT INTO _eurostat_namq_rows (
    provider_dataset_code, frequency, unit_code, unit_name, seasonal_adjustment_code,
    seasonal_adjustment_name, national_accounts_item_code, national_accounts_item_name,
    provider_geo_code, provider_geo_name, canonical_iso3_code, provider_period_code,
    period_year, period_quarter, quarter_start_month, quarter_end_month, quarter_end_day,
    observation_value, observation_status, decimal_precision, as_of_date,
    jsonstat_flat_index, source_dimensions, source_payload, attributes, attribute_hash
) VALUES
{row_values_sql};

CREATE TEMP TABLE _eurostat_provider_codes (
    dimension_name text NOT NULL,
    code_system text NOT NULL,
    provider_code text NOT NULL,
    provider_label text
) ON COMMIT DROP;

INSERT INTO _eurostat_provider_codes (dimension_name, code_system, provider_code, provider_label) VALUES
{code_values_sql};

WITH upsert_source AS (
    INSERT INTO meta.source (source_code, source_name, source_home_url, license_note)
    VALUES ({sql_literal(SOURCE_CODE)}, {sql_literal(SOURCE_NAME)}, {sql_literal(SOURCE_HOME_URL)}, {sql_literal(normalized.get('license_note'))})
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
           {sql_literal(normalized.get('source_url'))}, {sql_literal(normalized.get('raw_artifact_path'))}, {sql_literal(normalized.get('raw_sha256'))}, {json_literal(metadata)}
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
           {json_literal({'row_count': expected_rows, 'raw_metadata': raw_metadata})}
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
INSERT INTO staging.eurostat_namq_observation (
    dataset_release_id, pipeline_run_id, provider_dataset_code, frequency,
    unit_code, unit_name, seasonal_adjustment_code, seasonal_adjustment_name,
    national_accounts_item_code, national_accounts_item_name, provider_geo_code,
    provider_geo_name, provider_period_code, period_year, period_quarter,
    observation_value, observation_status, decimal_precision, as_of_date,
    jsonstat_flat_index, source_payload
)
SELECT rel.dataset_release_id, run.pipeline_run_id, r.provider_dataset_code, r.frequency,
       r.unit_code, r.unit_name, r.seasonal_adjustment_code, r.seasonal_adjustment_name,
       r.national_accounts_item_code, r.national_accounts_item_name, r.provider_geo_code,
       r.provider_geo_name, r.provider_period_code, r.period_year, r.period_quarter,
       r.observation_value, r.observation_status, r.decimal_precision, r.as_of_date,
       r.jsonstat_flat_index, r.source_payload
FROM _eurostat_namq_rows r CROSS JOIN release_row rel CROSS JOIN run_row run
ON CONFLICT (pipeline_run_id, provider_dataset_code, frequency, unit_code, seasonal_adjustment_code, national_accounts_item_code, provider_geo_code, provider_period_code) DO UPDATE
  SET observation_value = EXCLUDED.observation_value,
      observation_status = EXCLUDED.observation_status,
      decimal_precision = EXCLUDED.decimal_precision,
      source_payload = EXCLUDED.source_payload;

WITH source_row AS (
    SELECT source_id FROM meta.source WHERE source_code = {sql_literal(SOURCE_CODE)}
), distinct_indicators AS (
    SELECT DISTINCT national_accounts_item_code, national_accounts_item_name FROM _eurostat_namq_rows
)
INSERT INTO curated.dim_indicator (source_id, source_indicator_code, indicator_name)
SELECT s.source_id, d.national_accounts_item_code, d.national_accounts_item_name
FROM source_row s CROSS JOIN distinct_indicators d
ON CONFLICT (source_id, source_indicator_code) DO UPDATE SET indicator_name = EXCLUDED.indicator_name;

WITH distinct_territories AS (
    SELECT DISTINCT canonical_iso3_code, provider_geo_name FROM _eurostat_namq_rows
)
INSERT INTO curated.dim_territory (territory_type, iso3_code, canonical_territory_code, territory_name)
SELECT 'country', d.canonical_iso3_code, d.canonical_iso3_code, d.provider_geo_name
FROM distinct_territories d
ON CONFLICT (canonical_territory_code) DO UPDATE
  SET territory_name = EXCLUDED.territory_name;

INSERT INTO curated.dim_period (frequency, period_year, period_quarter, period_start_date, period_end_date, period_label)
SELECT DISTINCT frequency, period_year, period_quarter,
       make_date(period_year, quarter_start_month, 1),
       make_date(period_year, quarter_end_month, quarter_end_day),
       period_year::text || ' Q' || period_quarter::text
FROM _eurostat_namq_rows
ON CONFLICT (frequency, period_start_date, period_end_date) DO UPDATE
  SET period_quarter = EXCLUDED.period_quarter,
      period_label = EXCLUDED.period_label;

WITH source_row AS (
    SELECT source_id FROM meta.source WHERE source_code = {sql_literal(SOURCE_CODE)}
), distinct_periods AS (
    SELECT DISTINCT provider_dataset_code, provider_period_code, frequency, period_year, period_quarter,
                    quarter_start_month, quarter_end_month, quarter_end_day
    FROM _eurostat_namq_rows
)
INSERT INTO meta.provider_period_mapping (source_id, provider_dataset_code, provider_period_code, period_id, provider_label)
SELECT s.source_id, d.provider_dataset_code, d.provider_period_code, p.period_id, d.provider_period_code
FROM source_row s
CROSS JOIN distinct_periods d
JOIN curated.dim_period p
  ON p.frequency = d.frequency
 AND p.period_start_date = make_date(d.period_year, d.quarter_start_month, 1)
 AND p.period_end_date = make_date(d.period_year, d.quarter_end_month, d.quarter_end_day)
ON CONFLICT (source_id, provider_dataset_code, provider_period_code) DO UPDATE
  SET period_id = EXCLUDED.period_id,
      provider_label = EXCLUDED.provider_label;

WITH source_row AS (
    SELECT source_id FROM meta.source WHERE source_code = {sql_literal(SOURCE_CODE)}
), distinct_territories AS (
    SELECT DISTINCT provider_dataset_code, provider_geo_code, provider_geo_name, canonical_iso3_code
    FROM _eurostat_namq_rows
)
INSERT INTO meta.provider_territory_mapping (source_id, provider_dataset_code, provider_territory_code, code_system, territory_id, provider_label)
SELECT s.source_id, d.provider_dataset_code, d.provider_geo_code, 'eurostat_geo', t.territory_id, d.provider_geo_name
FROM source_row s
CROSS JOIN distinct_territories d
JOIN curated.dim_territory t ON t.iso3_code = d.canonical_iso3_code
ON CONFLICT (source_id, provider_dataset_code, code_system, provider_territory_code) DO UPDATE
  SET territory_id = EXCLUDED.territory_id,
      provider_label = EXCLUDED.provider_label;

WITH source_row AS (
    SELECT source_id FROM meta.source WHERE source_code = {sql_literal(SOURCE_CODE)}
), release_row AS (
    SELECT dr.dataset_release_id
    FROM meta.dataset_release dr JOIN source_row s ON dr.source_id = s.source_id
    WHERE dr.provider_dataset_code = {sql_literal(provider_dataset_code)} AND dr.release_key = {sql_literal(release_key)}
), distinct_code_lists AS (
    SELECT DISTINCT dimension_name, code_system FROM _eurostat_provider_codes
)
INSERT INTO meta.provider_code_list (source_id, provider_dataset_code, dimension_name, code_system, dataset_release_id, metadata)
SELECT s.source_id, {sql_literal(provider_dataset_code)}, d.dimension_name, d.code_system, r.dataset_release_id,
       {json_literal({'scope': 'TASK-024 bounded Eurostat namq_10_gdp fixture'})}
FROM source_row s CROSS JOIN release_row r CROSS JOIN distinct_code_lists d
WHERE NOT EXISTS (
    SELECT 1 FROM meta.provider_code_list existing
    WHERE existing.source_id = s.source_id
      AND existing.provider_dataset_code = {sql_literal(provider_dataset_code)}
      AND existing.dimension_name = d.dimension_name
      AND existing.code_system = d.code_system
      AND existing.dataset_release_id = r.dataset_release_id
);

WITH source_row AS (
    SELECT source_id FROM meta.source WHERE source_code = {sql_literal(SOURCE_CODE)}
), release_row AS (
    SELECT dr.dataset_release_id
    FROM meta.dataset_release dr JOIN source_row s ON dr.source_id = s.source_id
    WHERE dr.provider_dataset_code = {sql_literal(provider_dataset_code)} AND dr.release_key = {sql_literal(release_key)}
)
INSERT INTO meta.provider_code (provider_code_list_id, provider_code, provider_label)
SELECT pcl.provider_code_list_id, c.provider_code, c.provider_label
FROM _eurostat_provider_codes c
CROSS JOIN source_row s
CROSS JOIN release_row r
JOIN meta.provider_code_list pcl
  ON pcl.source_id = s.source_id
 AND pcl.provider_dataset_code = {sql_literal(provider_dataset_code)}
 AND pcl.dimension_name = c.dimension_name
 AND pcl.code_system = c.code_system
 AND pcl.dataset_release_id = r.dataset_release_id
ON CONFLICT (provider_code_list_id, provider_code) DO UPDATE
  SET provider_label = EXCLUDED.provider_label;

INSERT INTO curated.dim_unit (unit_code, unit_name)
SELECT DISTINCT unit_code, unit_name
FROM _eurostat_namq_rows
ON CONFLICT (unit_code) DO UPDATE SET unit_name = EXCLUDED.unit_name;

INSERT INTO curated.dim_attribute_set (attribute_hash, attributes)
SELECT DISTINCT attribute_hash, attributes
FROM _eurostat_namq_rows
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
       p.period_id, u.unit_id, a.attribute_set_id, r.observation_value,
       r.as_of_date,
       r.observation_status
FROM _eurostat_namq_rows r
CROSS JOIN source_row s
CROSS JOIN release_row rel
CROSS JOIN run_row run
JOIN curated.dim_indicator i ON i.source_id = s.source_id AND i.source_indicator_code = r.national_accounts_item_code
JOIN curated.dim_territory t ON t.iso3_code = r.canonical_iso3_code
JOIN curated.dim_period p ON p.frequency = r.frequency
  AND p.period_start_date = make_date(r.period_year, r.quarter_start_month, 1)
  AND p.period_end_date = make_date(r.period_year, r.quarter_end_month, r.quarter_end_day)
JOIN curated.dim_unit u ON u.unit_code = r.unit_code
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
    {lineage_values}
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
      ('eurostat_namq_expected_staging_rows', CASE WHEN (SELECT count(*) FROM staging.eurostat_namq_observation eno JOIN run_row rr ON eno.pipeline_run_id = rr.pipeline_run_id) = {expected_rows} THEN 'pass' ELSE 'fail' END, 'error', (SELECT count(*)::numeric FROM staging.eurostat_namq_observation eno JOIN run_row rr ON eno.pipeline_run_id = rr.pipeline_run_id), {expected_rows}::numeric, {json_literal({'scope': 'staging'})}),
      ('eurostat_namq_expected_fact_rows', CASE WHEN (SELECT count(*) FROM curated.fact_observation fo JOIN source_row s ON fo.source_id = s.source_id) = {expected_rows} THEN 'pass' ELSE 'fail' END, 'error', (SELECT count(*)::numeric FROM curated.fact_observation fo JOIN source_row s ON fo.source_id = s.source_id), {expected_rows}::numeric, {json_literal({'scope': 'curated_source'})}),
      ('eurostat_namq_expected_quarterly_periods', CASE WHEN (SELECT count(*) FROM curated.dim_period WHERE frequency = 'Q') = 2 THEN 'pass' ELSE 'fail' END, 'error', (SELECT count(*)::numeric FROM curated.dim_period WHERE frequency = 'Q'), 2::numeric, {json_literal({'scope': 'periods'})}),
      ('eurostat_namq_expected_provider_mappings', CASE WHEN (SELECT count(*) FROM meta.provider_period_mapping ppm JOIN source_row s ON ppm.source_id = s.source_id) = 2 AND (SELECT count(*) FROM meta.provider_territory_mapping ptm JOIN source_row s ON ptm.source_id = s.source_id) = 2 THEN 'pass' ELSE 'fail' END, 'error', ((SELECT count(*) FROM meta.provider_period_mapping ppm JOIN source_row s ON ppm.source_id = s.source_id) + (SELECT count(*) FROM meta.provider_territory_mapping ptm JOIN source_row s ON ptm.source_id = s.source_id))::numeric, 4::numeric, {json_literal({'scope': 'provider_mappings_source'})})
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
      (SELECT count(*) FROM staging.eurostat_namq_observation),
      (SELECT count(*) FROM curated.fact_observation),
      (SELECT count(*) FROM meta.lineage_event),
      (SELECT count(*) FROM meta.quality_check),
      (SELECT string_agg(period_label, ',' ORDER BY period_label) FROM curated.dim_period),
      (SELECT string_agg(canonical_territory_code, ',' ORDER BY canonical_territory_code) FROM curated.dim_territory),
      (SELECT string_agg(provider_period_code, ',' ORDER BY provider_period_code) FROM meta.provider_period_mapping),
      (SELECT string_agg(provider_territory_code, ',' ORDER BY provider_territory_code) FROM meta.provider_territory_mapping),
      (SELECT string_agg(DISTINCT dimension_name, ',' ORDER BY dimension_name) FROM meta.provider_code_list)
    """
    return parse_pipe_counts(
        psql_scalar(db_name, sql),
        [
            ("staging_rows", int),
            ("fact_rows", int),
            ("lineage_events", int),
            ("quality_checks", int),
            ("canonical_periods", lambda value: value.split(",") if value else []),
            ("canonical_territories", lambda value: value.split(",") if value else []),
            ("provider_periods", lambda value: value.split(",") if value else []),
            ("provider_territories", lambda value: value.split(",") if value else []),
            ("provider_code_dimensions", lambda value: value.split(",") if value else []),
        ],
    )


def load_eurostat_namq_smoke_to_postgres(
    db_name: str,
    normalized_path: str | Path,
    *,
    run_key: str = "eurostat-namq-smoke-20260604",
    as_of_date: str = DEFAULT_AS_OF_DATE,
) -> dict[str, Any]:
    normalized = json.loads(Path(normalized_path).read_text(encoding="utf-8"))
    sql = build_load_sql(normalized, run_key=run_key, as_of_date=as_of_date)
    run_psql_file(db_name, sql)
    return _counts(db_name)


def write_load_report(path: str | Path, payload: dict[str, Any]) -> dict[str, Any]:
    return write_json_report(path, payload, default_task="TASK-024")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Load MacroForge Eurostat NAMQ GDP smoke rows to PostgreSQL")
    parser.add_argument("--db", required=True, help="PostgreSQL database name")
    parser.add_argument("--normalized", default="data/metadata/eurostat/eurostat-namq-10-gdp-architecture-spike-normalized.json")
    parser.add_argument("--run-key", default="eurostat-namq-smoke-20260604")
    parser.add_argument("--as-of-date", default=DEFAULT_AS_OF_DATE)
    parser.add_argument("--report", default="artifacts/reports/eurostat-namq-load-smoke-20260604.json")
    args = parser.parse_args(argv)

    result = load_eurostat_namq_smoke_to_postgres(args.db, args.normalized, run_key=args.run_key, as_of_date=args.as_of_date)
    write_load_report(args.report, result)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
