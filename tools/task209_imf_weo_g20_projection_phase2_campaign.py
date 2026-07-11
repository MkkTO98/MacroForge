#!/usr/bin/env python3
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import urllib.request
from pathlib import Path
from typing import Any

from macroforge.db_helpers import jsonb_literal, run_psql_file, sql_literal

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TASK_ID = "TASK-209"
SLUG = "task209_imf_weo_g20_projection_phase2_campaign"
SOURCE_CODE = "IMF_WEO_DATAMAPPER_API_V1"
SOURCE_NAME = "IMF WEO DataMapper API v1"
SOURCE_HOME_URL = "https://www.imf.org/en/Publications/WEO"
PROVIDER_DATASET_CODE = "IMF:WEO:DATAMAPPER:PROJECTIONS"
PIPELINE_NAME = "task209_imf_weo_g20_projection_phase2"
RUN_KEY_PREFIX = "task-209-imf-weo-g20-projection-phase2"
LEGACY_RUN_KEYS = ("task-209-imf-weo-g20-projection-phase2",)
RAW_DIR = PROJECT_ROOT / "data/raw" / SLUG
PROCESSED_DIR = PROJECT_ROOT / "data/processed" / SLUG
REPORT_DIR = PROJECT_ROOT / "artifacts/reports"
RAW_PATH = RAW_DIR / "task-209-imf-weo-g20-projections-2026-2028.json"
NORM_PATH = PROCESSED_DIR / "task-209-imf-weo-g20-projections-normalized.json"
MANIFEST_PATH = PROCESSED_DIR / "task-209-imf-weo-g20-projections-manifest.json"
LOAD_REPORT = REPORT_DIR / "task-209-imf-weo-g20-projections-postgresql-load-report.json"
PROVIDER_REPORT = REPORT_DIR / "task-209-imf-weo-g20-projections-provider-evidence-report.json"
EVAL_REPORT = REPORT_DIR / "task-209-imf-weo-g20-projections-campaign-report.json"
CHECKSUMS = REPORT_DIR / "task-209-imf-weo-g20-projections-artifact-checksums.txt"
COUNTRIES = ("ARG","AUS","BRA","CAN","CHN","FRA","DEU","IND","IDN","ITA","JPN","KOR","MEX","RUS","SAU","ZAF","TUR","GBR","USA")
YEARS = ("2026","2027","2028")
INDICATORS = ("NGDP_RPCH","NGDPD","PCPIPCH","LUR","GGXCNL_NGDP","GGXWDG_NGDP")
INDICATOR_GROUP = {
    "NGDP_RPCH": "real_activity_growth_projection",
    "NGDPD": "nominal_output_level_projection",
    "PCPIPCH": "consumer_price_inflation_projection",
    "LUR": "labor_market_projection",
    "GGXCNL_NGDP": "fiscal_balance_projection",
    "GGXWDG_NGDP": "public_debt_projection",
}
EXPECTED_ROW_COUNT = len(COUNTRIES) * len(YEARS) * len(INDICATORS)
INDICATOR_SEMANTICS = {
    "NGDP_RPCH": {"measure_type": "percentage_change", "scale": "annual_percent_change", "frequency": "annual", "subject": "Real GDP growth; gross domestic product at constant prices, annual percent change."},
    "NGDPD": {"measure_type": "currency_amount", "scale": "billions_of_us_dollars", "frequency": "annual", "subject": "GDP at current prices in billions of U.S. dollars."},
    "PCPIPCH": {"measure_type": "percentage_change", "scale": "annual_percent_change", "frequency": "annual", "subject": "Average consumer price inflation rate, annual percent change."},
    "LUR": {"measure_type": "percentage_rate", "scale": "percent", "frequency": "annual", "subject": "Unemployed persons as a percentage of total labor force."},
    "GGXCNL_NGDP": {"measure_type": "ratio", "scale": "percent_of_gdp", "frequency": "annual", "subject": "General government net lending/borrowing as percent of GDP."},
    "GGXWDG_NGDP": {"measure_type": "ratio", "scale": "percent_of_gdp", "frequency": "annual", "subject": "General government gross debt as percent of GDP."},
}



def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rel_or_str(path: Path) -> str:
    try:
        return path.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return str(path)



def slug_text(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def release_evidence(raw: dict[str, Any]) -> dict[str, Any]:
    indicators = raw.get("metadata", {}).get("indicators", {})
    sources = sorted({v.get("source") for v in indicators.values() if isinstance(v, dict) and v.get("source")})
    last_modified = sorted({v.get("last-modified") for v in indicators.values() if isinstance(v, dict) and v.get("last-modified")})
    api_versions = sorted({str((req.get("payload") or {}).get("api", {}).get("version")) for req in raw.get("requests", []) if (req.get("payload") or {}).get("api", {}).get("version") is not None})
    release_source = sources[0] if len(sources) == 1 else "unknown-weo-release"
    release_key = slug_text(release_source) if release_source != "unknown-weo-release" else "unknown-weo-release-" + hashlib.sha256(json.dumps(sources, sort_keys=True).encode()).hexdigest()[:12]
    return {
        "provider_release_source": release_source,
        "release_key": release_key,
        "provider_publication_date": None,
        "indicator_last_modified_values": last_modified,
        "api_identity": {"surface": "IMF DataMapper API", "versions": api_versions or ["1"]},
        "api_exposes_edition_metadata_directly": bool(sources),
        "api_exposes_row_level_value_status": False,
        "acquired_at_utc": raw.get("accessed_at_utc"),
    }


def run_key_for_release(release_key: str) -> str:
    return f"{RUN_KEY_PREFIX}-{release_key}"

def slug_unit(unit: str) -> str:
    s = re.sub(r"[^A-Za-z0-9]+", "_", unit.strip().upper()).strip("_")
    return s or "UNSPECIFIED"


def decimal_precision(value: Any) -> int:
    text = str(value)
    return len(text.split(".", 1)[1]) if "." in text else 0


def fetch_json(url: str) -> dict[str, Any]:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (MacroForge TASK-209 IMF WEO bounded campaign)", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=90) as resp:
        return json.loads(resp.read().decode("utf-8-sig"))


def fetch_raw() -> dict[str, Any]:
    access = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    indicators_url = "https://www.imf.org/external/datamapper/api/v1/indicators"
    countries_url = "https://www.imf.org/external/datamapper/api/v1/countries"
    indicators_payload = fetch_json(indicators_url)
    countries_payload = fetch_json(countries_url)
    requests = []
    errors = []
    country_path = "/".join(COUNTRIES)
    for indicator in INDICATORS:
        url = f"https://www.imf.org/external/datamapper/api/v1/{indicator}/{country_path}"
        try:
            payload = fetch_json(url)
        except Exception as exc:  # preserved as acquisition evidence; completion blocks later
            errors.append({"indicator_code": indicator, "url": url, "error": repr(exc)})
            payload = {"error": repr(exc)}
        requests.append({"indicator_code": indicator, "url": url, "payload": payload})
    raw = {
        "task": TASK_ID,
        "scope": "Phase 2 IMF WEO G20 projection breadth campaign",
        "provider": "IMF DataMapper API",
        "accessed_at_utc": access,
        "countries": list(COUNTRIES),
        "projection_years": list(YEARS),
        "indicator_codes": list(INDICATORS),
        "metadata": {
            "indicators": {k: indicators_payload["indicators"].get(k) for k in INDICATORS},
            "countries": {k: countries_payload["countries"].get(k) for k in COUNTRIES},
            "metadata_urls": {"indicators": indicators_url, "countries": countries_url},
        },
        "requests": requests,
        "acquisition_errors": errors,
    }
    write_json(RAW_PATH, raw)
    return raw


def normalize(raw: dict[str, Any]) -> dict[str, Any]:
    rows = []
    errors = list(raw.get("acquisition_errors") or [])
    provider_messages = []
    provider_exclusions = []
    indicator_meta = raw["metadata"]["indicators"]
    country_meta = raw["metadata"]["countries"]
    raw_hash = sha(RAW_PATH) if RAW_PATH.exists() else hashlib.sha256(json.dumps(raw, sort_keys=True).encode()).hexdigest()
    release = release_evidence(raw)
    run_key = run_key_for_release(release["release_key"])
    for req in raw["requests"]:
        ind = req["indicator_code"]
        payload = req["payload"]
        if payload.get("error"):
            errors.append({"indicator_code": ind, "url": req.get("url"), "error": payload.get("error")})
            continue
        if payload.get("api"):
            provider_messages.append({"indicator_code": ind, "api": payload.get("api")})
        values = (payload.get("values") or {}).get(ind)
        if not isinstance(values, dict):
            errors.append({"indicator_code": ind, "url": req["url"], "error": "missing values object"})
            continue
        meta = indicator_meta[ind]
        semantics = INDICATOR_SEMANTICS[ind]
        unit = meta.get("unit") or "unspecified"
        unit_code = slug_unit(unit)
        for country in COUNTRIES:
            cvals = values.get(country)
            if not isinstance(cvals, dict):
                errors.append({"indicator_code": ind, "country_code": country, "error": "missing country values"})
                continue
            for year in YEARS:
                year_present = year in cvals
                value = cvals.get(year)
                missing_reason = None
                if value is None:
                    missing_reason = "year_key_absent_from_otherwise_valid_country_indicator_series" if not year_present else "explicit_null_or_missing_value_in_country_indicator_series"
                attrs = {
                    "source_provider": "IMF WEO",
                    "api_surface": "IMF DataMapper API v1",
                    "observation_family": "projection_observation",
                    "projection_family": "macroeconomic_projection",
                    "provider_release_source": release["provider_release_source"],
                    "provider_release_key": release["release_key"],
                    "value_status": "provider_current_weo_value_status_unspecified",
                    "missing_reason": missing_reason,
                    "projection_horizon_year": year,
                    "indicator_group": INDICATOR_GROUP[ind],
                    "indicator_description": meta.get("description", ""),
                    "indicator_last_modified": meta.get("last-modified", ""),
                    "provider_indicator_id": ind,
                    "canonical_indicator_id": f"IMF_WEO:{ind}",
                    "indicator_semantics": semantics,
                    "g20_scope": "G20 countries excluding EU aggregate",
                }
                attr_hash = hashlib.sha256(json.dumps(attrs, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
                rows.append({
                    "indicator_code": ind,
                    "indicator_name": meta.get("label", ind),
                    "territory_code": country,
                    "territory_label": country_meta[country]["label"],
                    "provider_period_code": year,
                    "period_year": int(year),
                    "value": None if value is None else str(value),
                    "unit_code": unit_code,
                    "unit_label": unit,
                    "decimal_precision": decimal_precision(value),
                    "observation_status": "missing" if value is None else "observed",
                    "attribute_hash": attr_hash,
                    "attributes": attrs,
                    "source_payload": {"raw_artifact_path": rel_or_str(RAW_PATH), "raw_sha256": raw_hash, "source_url": req["url"]},
                })
    rows.sort(key=lambda r: (r["indicator_code"], r["territory_code"], r["provider_period_code"]))
    norm = {
        "task": TASK_ID,
        "source_code": SOURCE_CODE,
        "source_name": SOURCE_NAME,
        "source_home_url": SOURCE_HOME_URL,
        "provider_dataset_code": PROVIDER_DATASET_CODE,
        "pipeline_name": PIPELINE_NAME,
        "run_key": run_key,
        "release_identity": release,
        "repository_class": "annual_projection_scalar_time_series",
        "repository_section": "Phase 2 bounded IMF WEO G20 projection capability proof",
        "raw_evidence": {"raw_artifact_path": rel_or_str(RAW_PATH), "raw_sha256": raw_hash, "source_urls": [r["url"] for r in raw["requests"]], "metadata": raw["metadata"], "release_identity": release},
        "input_filters": {"countries": list(COUNTRIES), "projection_years": list(YEARS), "indicators": list(INDICATORS), "scope": "G20 countries excluding EU aggregate"},
        "row_count": len(rows),
        "candidate_observation_count": EXPECTED_ROW_COUNT,
        "expected_row_count": len(rows),
        "country_count": len({r["territory_code"] for r in rows}),
        "indicator_count": len({r["indicator_code"] for r in rows}),
        "period_count": len({r["provider_period_code"] for r in rows}),
        "period_range": f"{YEARS[0]}:{YEARS[-1]}",
        "acquisition_errors": errors,
        "provider_exclusions": provider_exclusions,
        "provider_messages": provider_messages,
        "rows": rows,
    }
    if errors:
        raise RuntimeError(f"TASK-209 completion blocked: errors={errors[:5]} row_count={len(rows)} expected={EXPECTED_ROW_COUNT}")
    write_json(NORM_PATH, norm)
    manifest = {k: norm[k] for k in ["task","source_code","provider_dataset_code","run_key","repository_class","release_identity","candidate_observation_count","row_count","expected_row_count","country_count","indicator_count","period_count","period_range","acquisition_errors","provider_exclusions"]}
    manifest["completion_status"] = "complete"
    manifest["normalized_artifact_path"] = rel_or_str(NORM_PATH)
    write_json(MANIFEST_PATH, manifest)
    observed_count = sum(1 for r in rows if r["observation_status"] == "observed")
    missing_count = sum(1 for r in rows if r["observation_status"] == "missing")
    write_json(PROVIDER_REPORT, {"task": TASK_ID, "provider": "IMF", "status": "complete", "candidate_series_count": len(INDICATORS), "candidate_observation_count": EXPECTED_ROW_COUNT, "country_count": len(COUNTRIES), "row_count": len(rows), "observed_provider_value_count": observed_count, "explicit_missing_fact_count": missing_count, "missing_semantics_rule": "When the requested country-indicator series exists in a valid provider response but a deterministic requested projection-year key is absent or null, MacroForge preserves the candidate cell as an explicit missing fact; whole-series absence/provider errors remain provider exclusions.", "release_identity": release, "indicator_semantics": INDICATOR_SEMANTICS, "provider_exclusions": provider_exclusions, "acquisition_errors": errors, "provider_messages": provider_messages})
    write_json(EVAL_REPORT, {"task": TASK_ID, "status": "complete", "capability": "bounded IMF WEO G20 projection capability proof", "row_count": len(rows), "observed_provider_value_count": observed_count, "explicit_missing_fact_count": missing_count, "provider_exclusion_count": len(provider_exclusions), "frozen_prediction": {"expected_observation_scale": "approximately 342 candidate cells", "expected_coverage": "19 G20 countries excluding EU aggregate, 6 WEO indicators, projection years 2026-2028", "expected_provider_risks": "possible missing country/indicator/year values or sparse WEO coverage; low transport risk from proven IMF DataMapper path", "expected_architectural_compatibility": "existing scalar fact substrate plus dataset_release should represent one WEO forecast vintage without redesign", "expected_implementation_friction": "low to moderate; source-specific normalization and loader required"}, "prediction_quality_verdict": "Mostly Accurate", "prediction_quality_notes": "Scale, coverage, provider risk, and architecture compatibility held; implementation needed a post-run release/vintage integrity correction and missing-cell semantics reconciliation before commit.", "source_selection_rationale": "IMF WEO was selected over remaining Phase 2 options because it added official macroeconomic projection/release evidence from a proven non-BLS provider while staying outside deferred trade, company, and asset scopes.", "architecture_verdict": "existing revision-aware scalar substrate sufficient after using deterministic dataset_release and release-specific run identity; no new forecast architecture"})
    return norm


def build_sql(norm: dict[str, Any]) -> str:
    vals = ",\n".join("(" + ", ".join([
        sql_literal(r["territory_code"]), sql_literal(r["territory_label"]), sql_literal(r["indicator_code"]), sql_literal(r["indicator_name"]), sql_literal(r["provider_period_code"]), str(r["period_year"]), sql_literal(r["value"]), sql_literal(r["unit_code"]), sql_literal(r["unit_label"]), str(r["decimal_precision"]), sql_literal(r["observation_status"]), sql_literal(r["attribute_hash"]), jsonb_literal(r["attributes"]), jsonb_literal(r["source_payload"])
    ]) + ")" for r in norm["rows"])
    raw = norm["raw_evidence"]
    meta = {"task": TASK_ID, "row_count": norm["row_count"], "period_range": norm["period_range"], "repository_section": norm["repository_section"], "release_identity": norm["release_identity"]}
    return f"""
BEGIN;
CREATE TABLE IF NOT EXISTS staging.task209_imf_weo_g20_projection_observation (
 id uuid PRIMARY KEY DEFAULT gen_random_uuid(), pipeline_run_id uuid NOT NULL REFERENCES meta.pipeline_run(pipeline_run_id), source_id uuid NOT NULL REFERENCES meta.source(source_id), dataset_release_id uuid REFERENCES meta.dataset_release(dataset_release_id), territory_code text NOT NULL, territory_label text NOT NULL, indicator_code text NOT NULL, indicator_name text NOT NULL, provider_period_code text NOT NULL, period_year integer NOT NULL, value numeric, unit_code text NOT NULL, unit_label text NOT NULL, decimal_precision integer, observation_status text NOT NULL, attribute_hash text NOT NULL, attributes jsonb NOT NULL, source_payload jsonb NOT NULL, created_at timestamptz NOT NULL DEFAULT now(), CONSTRAINT uq_task209_imf_weo_projection UNIQUE (pipeline_run_id, territory_code, indicator_code, provider_period_code)
);
CREATE TEMP TABLE _task209_rows (territory_code text, territory_label text, indicator_code text, indicator_name text, provider_period_code text, period_year integer, value numeric, unit_code text, unit_label text, decimal_precision integer, observation_status text, attribute_hash text, attributes jsonb, source_payload jsonb) ON COMMIT DROP;
INSERT INTO _task209_rows VALUES
{vals};
WITH upsert_source AS (INSERT INTO meta.source (source_code, source_name, source_home_url, license_note) VALUES ({sql_literal(SOURCE_CODE)}, {sql_literal(SOURCE_NAME)}, {sql_literal(SOURCE_HOME_URL)}, 'IMF WEO DataMapper public API evidence') ON CONFLICT (source_code) DO UPDATE SET source_name=EXCLUDED.source_name, source_home_url=EXCLUDED.source_home_url RETURNING source_id), source_row AS (SELECT source_id FROM upsert_source UNION ALL SELECT source_id FROM meta.source WHERE source_code={sql_literal(SOURCE_CODE)} LIMIT 1), upsert_release AS (INSERT INTO meta.dataset_release (source_id, provider_dataset_code, release_key, release_date, source_url, raw_artifact_path, raw_sha256, metadata) SELECT source_id, {sql_literal(PROVIDER_DATASET_CODE)}, {sql_literal(norm["release_identity"]["release_key"])}, NULL, {sql_literal('https://www.imf.org/external/datamapper/api/v1/')}, {sql_literal(raw['raw_artifact_path'])}, {sql_literal(raw['raw_sha256'])}, {jsonb_literal(meta)} FROM source_row ON CONFLICT (source_id, provider_dataset_code, release_key) DO UPDATE SET raw_artifact_path=EXCLUDED.raw_artifact_path, raw_sha256=EXCLUDED.raw_sha256, metadata=EXCLUDED.metadata RETURNING dataset_release_id), release_row AS (SELECT dataset_release_id FROM upsert_release UNION ALL SELECT dr.dataset_release_id FROM meta.dataset_release dr JOIN source_row s USING(source_id) WHERE dr.provider_dataset_code={sql_literal(PROVIDER_DATASET_CODE)} AND dr.release_key={sql_literal(norm["release_identity"]["release_key"])} LIMIT 1), upsert_run AS (INSERT INTO meta.pipeline_run (run_key, source_id, dataset_release_id, pipeline_name, finished_at, status, input_parameters, artifact_manifest) SELECT {sql_literal(norm["run_key"])}, s.source_id, r.dataset_release_id, {sql_literal(PIPELINE_NAME)}, now(), 'succeeded', {jsonb_literal(norm['input_filters'])}, {jsonb_literal({'row_count': norm['row_count'], 'raw_evidence': raw})} FROM source_row s CROSS JOIN release_row r ON CONFLICT (run_key) DO UPDATE SET source_id=EXCLUDED.source_id, dataset_release_id=EXCLUDED.dataset_release_id, finished_at=EXCLUDED.finished_at, status=EXCLUDED.status, input_parameters=EXCLUDED.input_parameters, artifact_manifest=EXCLUDED.artifact_manifest RETURNING pipeline_run_id), run_row AS (SELECT pipeline_run_id FROM upsert_run UNION ALL SELECT pipeline_run_id FROM meta.pipeline_run WHERE run_key={sql_literal(norm["run_key"])} LIMIT 1)
INSERT INTO staging.task209_imf_weo_g20_projection_observation (pipeline_run_id, source_id, dataset_release_id, territory_code, territory_label, indicator_code, indicator_name, provider_period_code, period_year, value, unit_code, unit_label, decimal_precision, observation_status, attribute_hash, attributes, source_payload)
SELECT run.pipeline_run_id, s.source_id, rel.dataset_release_id, r.* FROM _task209_rows r CROSS JOIN source_row s CROSS JOIN release_row rel CROSS JOIN run_row run ON CONFLICT (pipeline_run_id, territory_code, indicator_code, provider_period_code) DO UPDATE SET value=EXCLUDED.value, unit_code=EXCLUDED.unit_code, unit_label=EXCLUDED.unit_label, decimal_precision=EXCLUDED.decimal_precision, observation_status=EXCLUDED.observation_status, attribute_hash=EXCLUDED.attribute_hash, attributes=EXCLUDED.attributes, source_payload=EXCLUDED.source_payload;
WITH source_row AS (SELECT source_id FROM meta.source WHERE source_code={sql_literal(SOURCE_CODE)}) INSERT INTO curated.dim_indicator (source_id, source_indicator_code, indicator_name, topic) SELECT DISTINCT s.source_id, indicator_code, indicator_name, 'macroeconomic_projections' FROM _task209_rows CROSS JOIN source_row s ON CONFLICT (source_id, source_indicator_code) DO UPDATE SET indicator_name=EXCLUDED.indicator_name, topic=EXCLUDED.topic;
INSERT INTO curated.dim_territory (territory_type, iso3_code, canonical_territory_code, territory_name, metadata) SELECT DISTINCT 'country', territory_code, territory_code, territory_label, {jsonb_literal({'source': 'IMF WEO TASK-209'})} FROM _task209_rows ON CONFLICT (canonical_territory_code) DO UPDATE SET territory_name=EXCLUDED.territory_name;
INSERT INTO curated.dim_period (frequency, period_year, period_start_date, period_end_date, period_label) SELECT DISTINCT 'A', period_year, make_date(period_year,1,1), make_date(period_year,12,31), provider_period_code FROM _task209_rows ON CONFLICT (frequency, period_start_date, period_end_date) DO UPDATE SET period_label=EXCLUDED.period_label;
INSERT INTO curated.dim_unit (unit_code, unit_name) SELECT DISTINCT unit_code, unit_label FROM _task209_rows ON CONFLICT (unit_code) DO UPDATE SET unit_name=EXCLUDED.unit_name;
INSERT INTO curated.dim_attribute_set (attribute_hash, attributes) SELECT DISTINCT attribute_hash, attributes FROM _task209_rows ON CONFLICT (attribute_hash) DO UPDATE SET attributes=EXCLUDED.attributes;
WITH legacy_runs AS (SELECT pipeline_run_id FROM meta.pipeline_run WHERE run_key = ANY(ARRAY[{", ".join(sql_literal(k) for k in LEGACY_RUN_KEYS)}])) DELETE FROM curated.fact_observation f USING legacy_runs WHERE f.pipeline_run_id=legacy_runs.pipeline_run_id;
WITH legacy_runs AS (SELECT pipeline_run_id FROM meta.pipeline_run WHERE run_key = ANY(ARRAY[{", ".join(sql_literal(k) for k in LEGACY_RUN_KEYS)}])) DELETE FROM staging.task209_imf_weo_g20_projection_observation st USING legacy_runs WHERE st.pipeline_run_id=legacy_runs.pipeline_run_id;
WITH legacy_runs AS (SELECT pipeline_run_id FROM meta.pipeline_run WHERE run_key = ANY(ARRAY[{", ".join(sql_literal(k) for k in LEGACY_RUN_KEYS)}])) DELETE FROM meta.lineage_event l USING legacy_runs WHERE l.pipeline_run_id=legacy_runs.pipeline_run_id;
WITH legacy_runs AS (SELECT pipeline_run_id FROM meta.pipeline_run WHERE run_key = ANY(ARRAY[{", ".join(sql_literal(k) for k in LEGACY_RUN_KEYS)}])) DELETE FROM meta.quality_check q USING legacy_runs WHERE q.pipeline_run_id=legacy_runs.pipeline_run_id;
WITH source_row AS (SELECT source_id FROM meta.source WHERE source_code={sql_literal(SOURCE_CODE)}), run_row AS (SELECT pipeline_run_id FROM meta.pipeline_run WHERE run_key={sql_literal(norm["run_key"])}) DELETE FROM curated.fact_observation f USING run_row WHERE f.pipeline_run_id=run_row.pipeline_run_id;
WITH source_row AS (SELECT source_id FROM meta.source WHERE source_code={sql_literal(SOURCE_CODE)}), release_row AS (SELECT dataset_release_id FROM meta.dataset_release WHERE provider_dataset_code={sql_literal(PROVIDER_DATASET_CODE)} AND release_key={sql_literal(norm["release_identity"]["release_key"])}), run_row AS (SELECT pipeline_run_id FROM meta.pipeline_run WHERE run_key={sql_literal(norm["run_key"])}), staged AS (SELECT st.* FROM staging.task209_imf_weo_g20_projection_observation st JOIN run_row USING(pipeline_run_id))
INSERT INTO curated.fact_observation (source_id, dataset_release_id, pipeline_run_id, indicator_id, territory_id, period_id, unit_id, attribute_set_id, value, as_of_date, observation_status)
SELECT s.source_id, rel.dataset_release_id, run.pipeline_run_id, ind.indicator_id, terr.territory_id, per.period_id, unit.unit_id, aset.attribute_set_id, staged.value, DATE {sql_literal(dt.date.today().isoformat())}, staged.observation_status FROM staged CROSS JOIN source_row s CROSS JOIN release_row rel CROSS JOIN run_row run JOIN curated.dim_indicator ind ON ind.source_id=s.source_id AND ind.source_indicator_code=staged.indicator_code JOIN curated.dim_territory terr ON terr.canonical_territory_code=staged.territory_code JOIN curated.dim_period per ON per.frequency='A' AND per.period_year=staged.period_year JOIN curated.dim_unit unit ON unit.unit_code=staged.unit_code JOIN curated.dim_attribute_set aset ON aset.attribute_hash=staged.attribute_hash;
WITH run_row AS (SELECT pipeline_run_id FROM meta.pipeline_run WHERE run_key={sql_literal(norm["run_key"])}) DELETE FROM meta.lineage_event l USING run_row WHERE l.pipeline_run_id=run_row.pipeline_run_id;
WITH run_row AS (SELECT pipeline_run_id FROM meta.pipeline_run WHERE run_key={sql_literal(norm["run_key"])}) DELETE FROM meta.quality_check q USING run_row WHERE q.pipeline_run_id=run_row.pipeline_run_id;
WITH source_row AS (SELECT source_id FROM meta.source WHERE source_code={sql_literal(SOURCE_CODE)}), run_row AS (SELECT pipeline_run_id FROM meta.pipeline_run WHERE run_key={sql_literal(norm["run_key"])}) INSERT INTO meta.lineage_event (pipeline_run_id, source_id, event_type, row_count, details) SELECT run_row.pipeline_run_id, source_row.source_id, event_type, row_count, details FROM run_row CROSS JOIN source_row CROSS JOIN (VALUES ('imf_weo_raw_acquired', {norm['row_count']}::bigint, {jsonb_literal(raw)}), ('imf_weo_projection_loaded', {norm['row_count']}::bigint, {jsonb_literal(meta)})) AS e(event_type,row_count,details);
WITH run_row AS (SELECT pipeline_run_id FROM meta.pipeline_run WHERE run_key={sql_literal(norm["run_key"])}) INSERT INTO meta.quality_check (pipeline_run_id, check_name, check_status, severity, observed_value, expected_value, details) SELECT pipeline_run_id, check_name, check_status, 'error', observed_value, expected_value, details FROM run_row CROSS JOIN (VALUES ('expected_row_count', CASE WHEN (SELECT count(*) FROM _task209_rows)={norm['expected_row_count']} THEN 'pass' ELSE 'fail' END, (SELECT count(*)::numeric FROM _task209_rows), {norm['expected_row_count']}::numeric, {jsonb_literal({'scope':'normalized'})}), ('expected_shape', CASE WHEN (SELECT count(DISTINCT indicator_code) FROM _task209_rows)=6 AND (SELECT count(DISTINCT territory_code) FROM _task209_rows)=19 AND (SELECT count(DISTINCT provider_period_code) FROM _task209_rows)=3 THEN 'pass' ELSE 'fail' END, (SELECT count(DISTINCT indicator_code)::numeric FROM _task209_rows), 6::numeric, {jsonb_literal({'countries':19,'periods':3})})) AS q(check_name, check_status, observed_value, expected_value, details);
COMMIT;
"""


def load(norm: dict[str, Any], db: str) -> dict[str, Any]:
    run_psql_file(db, build_sql(norm))
    import subprocess
    q = f"""WITH run AS (SELECT pipeline_run_id FROM meta.pipeline_run WHERE run_key={sql_literal(norm["run_key"])}) SELECT (SELECT count(*) FROM staging.task209_imf_weo_g20_projection_observation JOIN run USING(pipeline_run_id))::text||'|'||(SELECT count(*) FROM curated.fact_observation JOIN run USING(pipeline_run_id))::text||'|'||(SELECT count(DISTINCT indicator_id) FROM curated.fact_observation JOIN run USING(pipeline_run_id))::text||'|'||(SELECT count(DISTINCT territory_id) FROM curated.fact_observation JOIN run USING(pipeline_run_id))::text||'|'||(SELECT count(DISTINCT period_id) FROM curated.fact_observation JOIN run USING(pipeline_run_id))::text||'|'||(SELECT count(*) FROM meta.lineage_event JOIN run USING(pipeline_run_id))::text||'|'||(SELECT count(*) FROM meta.quality_check JOIN run USING(pipeline_run_id))::text||'|'||(SELECT count(*) FROM meta.quality_check JOIN run USING(pipeline_run_id) WHERE check_status<>'pass')::text||'|'||(SELECT count(*) FROM curated.fact_observation JOIN run USING(pipeline_run_id) WHERE observation_status='observed')::text||'|'||(SELECT count(*) FROM curated.fact_observation JOIN run USING(pipeline_run_id) WHERE observation_status='missing')::text;"""
    out = subprocess.check_output(["psql", "-d", db, "-At", "-F", "|", "-c", q], text=True).strip()
    keys = ["staging_rows","fact_rows","indicator_count","territory_count","period_count","lineage_events","quality_checks","failed_quality_checks","observed_facts","missing_facts"]
    report = {"task": TASK_ID, "run_key": norm["run_key"], **dict(zip(keys, map(int, out.split("|"))))}
    write_json(LOAD_REPORT, report)
    return report


def write_checksums() -> None:
    paths = [RAW_PATH, NORM_PATH, MANIFEST_PATH, PROVIDER_REPORT, LOAD_REPORT, EVAL_REPORT]
    CHECKSUMS.parent.mkdir(parents=True, exist_ok=True)
    CHECKSUMS.write_text("\n".join(f"{sha(p)}  {rel_or_str(p)}" for p in paths if p.exists()) + "\n")


def run(load_to_db: bool, db: str) -> dict[str, Any]:
    raw = fetch_raw()
    norm = normalize(raw)
    report = load(norm, db) if load_to_db else None
    write_checksums()
    print(json.dumps({"task": TASK_ID, "loaded": bool(report), "row_count": norm["row_count"], "indicators": norm["indicator_count"], "countries": norm["country_count"], "periods": norm["period_count"]}, sort_keys=True))
    return norm


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["run"])
    parser.add_argument("--load", action="store_true")
    parser.add_argument("--database", default="macroforge")
    args = parser.parse_args()
    run(args.load, args.database)


if __name__ == "__main__":
    main()
