from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from macroforge.db_helpers import jsonb_literal, parse_pipe_counts, psql_scalar, run_psql_file, sql_literal, write_json_report

SOURCE_CODE = "WDI"
SOURCE_NAME = "World Bank World Development Indicators"
DEFAULT_PROVIDER_DATASET = "WDI"
DEFAULT_PIPELINE_NAME = "wdi_smoke_slice"
UNKNOWN_UNIT_CODE = "unknown"
UNKNOWN_UNIT_NAME = "Unknown / source unspecified"
EMPTY_ATTRIBUTE_HASH = "empty"


def json_literal(value: Any) -> str:
    return jsonb_literal(value)


def _release_key(normalized: dict[str, Any]) -> str:
    last_updated = None
    if normalized.get("raw_artifacts"):
        last_updated = normalized["raw_artifacts"][0].get("source_metadata", {}).get("lastupdated")
    return f"WDI:{last_updated or 'unknown'}:{normalized.get('date_range', 'unknown')}"


def build_load_sql(normalized: dict[str, Any], *, run_key: str = "wdi-smoke-20260602") -> str:
    rows = normalized["rows"]
    release_key = _release_key(normalized)
    source_url = "; ".join(a["url"] for a in normalized.get("raw_artifacts", []))
    raw_sha256 = ";".join(a["sha256"] for a in normalized.get("raw_artifacts", []))
    raw_artifact_path = normalized.get("support_bundle")
    metadata = {
        "countries": normalized.get("countries"),
        "indicators": normalized.get("indicators"),
        "date_range": normalized.get("date_range"),
        "raw_artifacts": normalized.get("raw_artifacts", []),
    }

    values = []
    for row in rows:
        unit_code = row.get("unit") or UNKNOWN_UNIT_CODE
        observation_status = "missing" if row.get("value") is None else "observed"
        values.append(
            "(" + ", ".join(
                [
                    sql_literal(row["countryiso3code"]),
                    sql_literal(row.get("country_name")),
                    sql_literal(row["indicator_id"]),
                    sql_literal(row.get("indicator_name")),
                    sql_literal(int(row["date"])),
                    sql_literal(row.get("value")),
                    sql_literal(unit_code),
                    sql_literal(row.get("decimal")),
                    json_literal(row),
                    sql_literal(observation_status),
                ]
            ) + ")"
        )

    values_sql = ",\n".join(values)
    as_of_date = release_key.split(":")[1] if ":" in release_key else "2026-04-08"

    return f"""
BEGIN;

CREATE TEMP TABLE _wdi_rows (
    country_code text NOT NULL,
    country_name text,
    indicator_code text NOT NULL,
    indicator_name text,
    period_year integer NOT NULL,
    value numeric,
    unit_code text NOT NULL,
    decimal_precision integer,
    source_payload jsonb NOT NULL,
    observation_status text NOT NULL
) ON COMMIT DROP;

INSERT INTO _wdi_rows (
    country_code, country_name, indicator_code, indicator_name, period_year,
    value, unit_code, decimal_precision, source_payload, observation_status
) VALUES
{values_sql};

WITH upsert_source AS (
    INSERT INTO meta.source (source_code, source_name, source_home_url, license_note)
    VALUES ({sql_literal(SOURCE_CODE)}, {sql_literal(SOURCE_NAME)}, 'https://data.worldbank.org/', 'World Bank WDI no-key public API smoke slice')
    ON CONFLICT (source_code) DO UPDATE SET source_name = EXCLUDED.source_name
    RETURNING source_id
), source_row AS (
    SELECT source_id FROM upsert_source
    UNION ALL
    SELECT source_id FROM meta.source WHERE source_code = {sql_literal(SOURCE_CODE)}
    LIMIT 1
), upsert_release AS (
    INSERT INTO meta.dataset_release (source_id, provider_dataset_code, release_key, release_date, source_url, raw_artifact_path, raw_sha256, metadata)
    SELECT source_id, {sql_literal(DEFAULT_PROVIDER_DATASET)}, {sql_literal(release_key)}, NULL, {sql_literal(source_url)}, {sql_literal(raw_artifact_path)}, {sql_literal(raw_sha256)}, {json_literal(metadata)}
    FROM source_row
    ON CONFLICT (source_id, provider_dataset_code, release_key) DO UPDATE
      SET source_url = EXCLUDED.source_url,
          raw_artifact_path = EXCLUDED.raw_artifact_path,
          raw_sha256 = EXCLUDED.raw_sha256,
          metadata = EXCLUDED.metadata
    RETURNING dataset_release_id
), release_row AS (
    SELECT dataset_release_id FROM upsert_release
    UNION ALL
    SELECT dr.dataset_release_id
    FROM meta.dataset_release dr
    JOIN source_row s ON dr.source_id = s.source_id
    WHERE dr.provider_dataset_code = {sql_literal(DEFAULT_PROVIDER_DATASET)} AND dr.release_key = {sql_literal(release_key)}
    LIMIT 1
), upsert_run AS (
    INSERT INTO meta.pipeline_run (run_key, source_id, dataset_release_id, pipeline_name, finished_at, status, input_parameters, artifact_manifest)
    SELECT {sql_literal(run_key)}, s.source_id, r.dataset_release_id, {sql_literal(DEFAULT_PIPELINE_NAME)}, now(), 'succeeded',
           {json_literal({'countries': normalized.get('countries'), 'indicators': normalized.get('indicators'), 'date_range': normalized.get('date_range')})},
           {json_literal({'row_count': normalized.get('row_count'), 'raw_artifacts': normalized.get('raw_artifacts')})}
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
INSERT INTO staging.wdi_observation (
    pipeline_run_id, source_id, dataset_release_id, country_code, country_name,
    indicator_code, indicator_name, period_year, value, unit_code,
    decimal_precision, as_of_date, source_payload
)
SELECT run.pipeline_run_id, s.source_id, rel.dataset_release_id, w.country_code, w.country_name,
       w.indicator_code, w.indicator_name, w.period_year, w.value, w.unit_code,
       w.decimal_precision, {sql_literal(as_of_date)}::date, w.source_payload
FROM _wdi_rows w CROSS JOIN source_row s CROSS JOIN release_row rel CROSS JOIN run_row run
ON CONFLICT (pipeline_run_id, country_code, indicator_code, period_year) DO UPDATE
  SET value = EXCLUDED.value,
      unit_code = EXCLUDED.unit_code,
      source_payload = EXCLUDED.source_payload;

WITH source_row AS (
    SELECT source_id FROM meta.source WHERE source_code = {sql_literal(SOURCE_CODE)}
), distinct_indicators AS (
    SELECT DISTINCT indicator_code, indicator_name FROM _wdi_rows
)
INSERT INTO curated.dim_indicator (source_id, source_indicator_code, indicator_name)
SELECT s.source_id, d.indicator_code, d.indicator_name
FROM source_row s CROSS JOIN distinct_indicators d
ON CONFLICT (source_id, source_indicator_code) DO UPDATE SET indicator_name = EXCLUDED.indicator_name;

WITH source_row AS (
    SELECT source_id FROM meta.source WHERE source_code = {sql_literal(SOURCE_CODE)}
), distinct_territories AS (
    SELECT DISTINCT country_code, country_name FROM _wdi_rows
)
INSERT INTO curated.dim_territory (source_id, iso3_code, territory_name)
SELECT s.source_id, d.country_code, d.country_name
FROM source_row s CROSS JOIN distinct_territories d
ON CONFLICT (source_id, iso3_code) DO UPDATE SET territory_name = EXCLUDED.territory_name;

INSERT INTO curated.dim_period (frequency, period_year, period_start_date, period_end_date)
SELECT DISTINCT 'A', period_year, make_date(period_year, 1, 1), make_date(period_year, 12, 31)
FROM _wdi_rows
ON CONFLICT (frequency, period_year) DO NOTHING;

INSERT INTO curated.dim_unit (unit_code, unit_name)
SELECT DISTINCT unit_code, CASE WHEN unit_code = {sql_literal(UNKNOWN_UNIT_CODE)} THEN {sql_literal(UNKNOWN_UNIT_NAME)} ELSE unit_code END
FROM _wdi_rows
ON CONFLICT (unit_code) DO UPDATE SET unit_name = EXCLUDED.unit_name;

INSERT INTO curated.dim_attribute_set (attribute_hash, attributes)
VALUES ({sql_literal(EMPTY_ATTRIBUTE_HASH)}, '{{}}'::jsonb)
ON CONFLICT (attribute_hash) DO NOTHING;

WITH source_row AS (
    SELECT source_id FROM meta.source WHERE source_code = {sql_literal(SOURCE_CODE)}
), release_row AS (
    SELECT dr.dataset_release_id FROM meta.dataset_release dr JOIN source_row s ON dr.source_id = s.source_id
    WHERE dr.provider_dataset_code = {sql_literal(DEFAULT_PROVIDER_DATASET)} AND dr.release_key = {sql_literal(release_key)}
), run_row AS (
    SELECT pipeline_run_id FROM meta.pipeline_run WHERE run_key = {sql_literal(run_key)}
)
INSERT INTO curated.fact_observation (
    source_id, dataset_release_id, pipeline_run_id, indicator_id, territory_id,
    period_id, unit_id, attribute_set_id, value, as_of_date, observation_status
)
SELECT s.source_id, rel.dataset_release_id, run.pipeline_run_id, i.indicator_id, t.territory_id,
       p.period_id, u.unit_id, a.attribute_set_id, w.value,
       {sql_literal(as_of_date)}::date,
       w.observation_status
FROM _wdi_rows w
CROSS JOIN source_row s
CROSS JOIN release_row rel
CROSS JOIN run_row run
JOIN curated.dim_indicator i ON i.source_id = s.source_id AND i.source_indicator_code = w.indicator_code
JOIN curated.dim_territory t ON t.source_id = s.source_id AND t.iso3_code = w.country_code
JOIN curated.dim_period p ON p.frequency = 'A' AND p.period_year = w.period_year
JOIN curated.dim_unit u ON u.unit_code = w.unit_code
JOIN curated.dim_attribute_set a ON a.attribute_hash = {sql_literal(EMPTY_ATTRIBUTE_HASH)}
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
INSERT INTO meta.lineage_event (pipeline_run_id, source_id, event_type, from_artifact, to_artifact, row_count, details)
SELECT run.pipeline_run_id, s.source_id, event_type, from_artifact, to_artifact, row_count, details
FROM source_row s CROSS JOIN run_row run CROSS JOIN (
    VALUES
      ('raw_to_staging', {sql_literal(raw_artifact_path)}, 'staging.wdi_observation', (SELECT count(*)::bigint FROM staging.wdi_observation swo JOIN run_row rr ON swo.pipeline_run_id = rr.pipeline_run_id), {json_literal({'task': 'TASK-006'})}),
      ('staging_to_curated', 'staging.wdi_observation', 'curated.fact_observation', (SELECT count(*)::bigint FROM curated.fact_observation), {json_literal({'task': 'TASK-006'})})
) AS v(event_type, from_artifact, to_artifact, row_count, details)
WHERE NOT EXISTS (
    SELECT 1 FROM meta.lineage_event le
    WHERE le.pipeline_run_id = run.pipeline_run_id AND le.event_type = v.event_type
);

WITH run_row AS (
    SELECT pipeline_run_id FROM meta.pipeline_run WHERE run_key = {sql_literal(run_key)}
)
INSERT INTO meta.quality_check (pipeline_run_id, check_name, check_status, severity, observed_value, expected_value, details)
SELECT run.pipeline_run_id, check_name, check_status, severity, observed_value, expected_value, details
FROM run_row run CROSS JOIN (
    VALUES
      ('wdi_smoke_expected_rows', CASE WHEN (SELECT count(*) FROM staging.wdi_observation swo JOIN run_row rr ON swo.pipeline_run_id = rr.pipeline_run_id) = {normalized.get('expected_row_count', 8)} THEN 'pass' ELSE 'fail' END, 'error', (SELECT count(*)::numeric FROM staging.wdi_observation swo JOIN run_row rr ON swo.pipeline_run_id = rr.pipeline_run_id), {normalized.get('expected_row_count', 8)}::numeric, {json_literal({'scope': 'staging'})}),
      ('wdi_smoke_fact_rows', CASE WHEN (SELECT count(*) FROM curated.fact_observation) = {normalized.get('expected_row_count', 8)} THEN 'pass' ELSE 'fail' END, 'error', (SELECT count(*)::numeric FROM curated.fact_observation), {normalized.get('expected_row_count', 8)}::numeric, {json_literal({'scope': 'curated'})})
) AS v(check_name, check_status, severity, observed_value, expected_value, details)
WHERE NOT EXISTS (
    SELECT 1 FROM meta.quality_check qc
    WHERE qc.pipeline_run_id = run.pipeline_run_id AND qc.check_name = v.check_name
);

COMMIT;
"""


def _counts(db_name: str) -> dict[str, int]:
    sql = """
    SELECT
      (SELECT count(*) FROM staging.wdi_observation),
      (SELECT count(*) FROM curated.fact_observation),
      (SELECT count(*) FROM meta.lineage_event),
      (SELECT count(*) FROM meta.quality_check)
    """
    return parse_pipe_counts(
        psql_scalar(db_name, sql),
        [
            ("staging_rows", int),
            ("fact_rows", int),
            ("lineage_events", int),
            ("quality_checks", int),
        ],
    )


def load_wdi_smoke_to_postgres(db_name: str, normalized_path: str | Path, *, run_key: str = "wdi-smoke-20260602") -> dict[str, int]:
    normalized = json.loads(Path(normalized_path).read_text(encoding="utf-8"))
    sql = build_load_sql(normalized, run_key=run_key)
    run_psql_file(db_name, sql)
    return _counts(db_name)


def write_load_report(path: str | Path, payload: dict[str, Any]) -> dict[str, Any]:
    return write_json_report(path, payload, default_task="TASK-006")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Load MacroForge WDI smoke rows to PostgreSQL")
    parser.add_argument("--db", required=True, help="PostgreSQL database name")
    parser.add_argument("--normalized", default="data/metadata/wdi/wdi-smoke-normalized.json")
    parser.add_argument("--run-key", default="wdi-smoke-20260602")
    parser.add_argument("--report", default="artifacts/reports/wdi-load-smoke-20260602.json")
    args = parser.parse_args(argv)

    result = load_wdi_smoke_to_postgres(args.db, args.normalized, run_key=args.run_key)
    write_load_report(args.report, result)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
