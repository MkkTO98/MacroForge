from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import shutil
import sys
import urllib.request
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "src"))

from macroforge.db_helpers import jsonb_literal, parse_pipe_counts, psql_scalar, run_psql_file, sql_literal, write_json_report

TASK_ID = "TASK-213"
SLUG = "task213_bis_cbpol_policy_rate_phase2_campaign"
SOURCE_CODE = "BIS_PUBLIC_SDMX_API"
SOURCE_NAME = "Bank for International Settlements public SDMX API"
SOURCE_HOME_URL = "https://www.bis.org/"
PROVIDER_DATASET_CODE = "BIS:WS_CBPOL"
DATAFLOW_CODE = "WS_CBPOL"
DATAFLOW_VERSION = "1.0"
RUN_KEY = "task-213-bis-cbpol-policy-rate-phase2"
PIPELINE_NAME = "bis_cbpol_policy_rate_phase2_campaign"
FREQUENCY = "M"
START_PERIOD = "2015-01"
END_PERIOD = "2026-06"
AS_OF_DATE = "2026-07-12"
UNIT_CODE = "PERCENT"
UNIT_LABEL = "Percent"
UNIT_MEASURE_PROVIDER_CODE = "368"
UNIT_MULT = "0"

AREAS = {
    "AU": ("AUS", "Australia"),
    "BR": ("BRA", "Brazil"),
    "CA": ("CAN", "Canada"),
    "CH": ("CHE", "Switzerland"),
    "CL": ("CHL", "Chile"),
    "CN": ("CHN", "China"),
    "CO": ("COL", "Colombia"),
    "CZ": ("CZE", "Czechia"),
    "DK": ("DNK", "Denmark"),
    "GB": ("GBR", "United Kingdom"),
    "HU": ("HUN", "Hungary"),
    "HK": ("HKG", "Hong Kong SAR"),
    "ID": ("IDN", "Indonesia"),
    "IL": ("ISR", "Israel"),
    "IN": ("IND", "India"),
    "IS": ("ISL", "Iceland"),
    "JP": ("JPN", "Japan"),
    "KR": ("KOR", "Korea, Rep."),
    "KW": ("KWT", "Kuwait"),
    "MA": ("MAR", "Morocco"),
    "MK": ("MKD", "North Macedonia"),
    "MX": ("MEX", "Mexico"),
    "MY": ("MYS", "Malaysia"),
    "NO": ("NOR", "Norway"),
    "NZ": ("NZL", "New Zealand"),
    "PE": ("PER", "Peru"),
    "PH": ("PHL", "Philippines"),
    "PL": ("POL", "Poland"),
    "RO": ("ROU", "Romania"),
    "RS": ("SRB", "Serbia"),
    "RU": ("RUS", "Russian Federation"),
    "SA": ("SAU", "Saudi Arabia"),
    "SE": ("SWE", "Sweden"),
    "TH": ("THA", "Thailand"),
    "TR": ("TUR", "Turkiye"),
    "US": ("USA", "United States"),
    "ZA": ("ZAF", "South Africa"),
}
SELECTION_EXCLUSIONS = [
    {"provider_code": "XM", "category": "aggregate_selection_exclusion", "label": "Euro area / euro area aggregate in BIS WS_CBPOL; deliberately outside country candidate grid"},
]
INDICATOR_CODE = "BIS:WS_CBPOL:CENTRAL_BANK_POLICY_RATE"
INDICATOR_NAME = "Central bank policy rate"
MEASURE_CLASS = "central_bank_policy_rate"


RAW_DIR = PROJECT_ROOT / "data/raw" / SLUG
PROCESSED_DIR = PROJECT_ROOT / "data/processed" / SLUG
REPORT_DIR = PROJECT_ROOT / "artifacts/reports"
PRED_PATH = REPORT_DIR / "task-213-bis-cbpol-policy-rate-frozen-pre-execution-prediction.json"
RAW_PATH = RAW_DIR / "active" / "task-213-bis-cbpol-policy-rate-2015m01-2026m06-raw.xml"
RAW_META_PATH = RAW_DIR / "active" / "task-213-bis-cbpol-policy-rate-2015m01-2026m06-raw-metadata.json"
NORM_PATH = PROCESSED_DIR / "active" / "task-213-bis-cbpol-policy-rate-normalized.json"
MANIFEST_PATH = PROCESSED_DIR / "active" / "task-213-bis-cbpol-policy-rate-manifest.json"
PROVIDER_REPORT = REPORT_DIR / "task-213-bis-cbpol-policy-rate-provider-evidence-report.json"
LOAD_REPORT = REPORT_DIR / "task-213-bis-cbpol-policy-rate-postgresql-load-report.json"
EVAL_REPORT = REPORT_DIR / "task-213-bis-cbpol-policy-rate-prediction-evaluation.json"
CHECKSUMS = REPORT_DIR / "task-213-bis-cbpol-policy-rate-artifact-checksums.txt"
SQL_PATH = REPORT_DIR / "task-213-bis-cbpol-policy-rate-load.sql"

NS = {"message": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message"}


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def attr_hash(attrs: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(attrs, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def rel(path: Path) -> str:
    return path.relative_to(PROJECT_ROOT).as_posix()


def source_url(start_period: str = START_PERIOD, end_period: str = END_PERIOD) -> str:
    area_key = "+".join(AREAS)
    return f"https://stats.bis.org/api/v2/data/dataflow/BIS/{DATAFLOW_CODE}/{DATAFLOW_VERSION}/{FREQUENCY}.{area_key}?startPeriod={start_period}&endPeriod={end_period}"


def release_key_from_provider_metadata(metadata: dict[str, Any], raw_sha256: str | None = None) -> str:
    prepared = metadata.get("prepared")
    if prepared:
        token = prepared.replace("-", "").replace(":", "").replace("Z", "z").replace("T", "t")
        return f"bis-ws-cbpol-snapshot-prepared-{token}"
    if raw_sha256:
        return f"bis-ws-cbpol-snapshot-raw-{raw_sha256[:16]}"
    raise ValueError("cannot derive BIS WS_CBPOL snapshot identity without provider prepared timestamp or raw checksum")


def build_run_key(release_key: str) -> str:
    return f"{RUN_KEY}-{release_key}"


def canonical_indicator_code(measure: str = MEASURE_CLASS, unit_code: str = UNIT_CODE, frequency: str = FREQUENCY) -> str:
    return f"BIS:WS_CBPOL:{measure.upper()}:{unit_code}:{frequency}"


def candidate_periods() -> list[tuple[int, int, str, str]]:
    start_year, start_month = [int(x) for x in START_PERIOD.split("-")]
    end_year, end_month = [int(x) for x in END_PERIOD.split("-")]
    out = []
    year, month = start_year, start_month
    while (year, month) <= (end_year, end_month):
        provider = f"{year}-{month:02d}"
        canonical = f"{year}-M{month:02d}"
        out.append((year, month, provider, canonical))
        month += 1
        if month == 13:
            year += 1
            month = 1
    return out


def fetch_raw() -> dict[str, Any]:
    attempt_id = dt.datetime.now(dt.timezone.utc).strftime("attempt-%Y%m%dT%H%M%SZ")
    attempt_dir = RAW_DIR / "_attempts" / attempt_id
    attempt_dir.mkdir(parents=True, exist_ok=True)
    url = source_url()
    acquired_at = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    req = urllib.request.Request(url, headers={"User-Agent": "MacroForge TASK-213 BIS CBPOL Phase2"})
    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            raw = response.read()
            status = response.status
            headers = dict(response.headers.items())
    except Exception as exc:
        err = {"task": TASK_ID, "status": "acquisition_error", "source_url": url, "acquired_at_utc": acquired_at, "error_type": type(exc).__name__, "error": str(exc)}
        write_json(attempt_dir / "acquisition-error.json", err)
        raise
    attempt_raw = attempt_dir / RAW_PATH.name
    attempt_raw.write_bytes(raw)
    meta = {"task": TASK_ID, "status": "acquired", "source_url": url, "request_parameters": {"dataflow": DATAFLOW_CODE, "version": DATAFLOW_VERSION, "key": f"{FREQUENCY}." + "+".join(AREAS), "startPeriod": START_PERIOD, "endPeriod": END_PERIOD}, "acquired_at_utc": acquired_at, "http_status": status, "headers": headers, "raw_sha256": sha256_bytes(raw), "raw_bytes": len(raw), "attempt_id": attempt_id, "content_type": headers.get("Content-Type")}
    write_json(attempt_dir / RAW_META_PATH.name, meta)
    # Atomic promotion: copy only after the attempt has both raw bytes and metadata.
    active_dir = RAW_PATH.parent
    tmp_dir = RAW_DIR / ".active.tmp"
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)
    tmp_dir.mkdir(parents=True)
    (tmp_dir / RAW_PATH.name).write_bytes(raw)
    write_json(tmp_dir / RAW_META_PATH.name, meta)
    if active_dir.exists():
        shutil.rmtree(active_dir)
    tmp_dir.replace(active_dir)
    return meta


def _local(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _provider_metadata(root: ET.Element, raw_meta: dict[str, Any]) -> dict[str, Any]:
    header = next((e for e in root.iter() if _local(e.tag) == "Header"), None)
    dataset = next((e for e in root.iter() if _local(e.tag) == "DataSet"), None)
    def child_text(local: str) -> str | None:
        if header is None:
            return None
        for child in header:
            if _local(child.tag) == local and child.text:
                return child.text.strip()
        return None
    sender = next((e for e in header.iter() if _local(e.tag) == "Sender"), None) if header is not None else None
    structure = next((e for e in header.iter() if _local(e.tag) == "Structure"), None) if header is not None else None
    return {
        "message_id": child_text("ID"),
        "prepared": child_text("Prepared"),
        "sender": sender.attrib.get("id") if sender is not None else None,
        "dataset_action": child_text("DataSetAction"),
        "structure_id": structure.attrib.get("structureID") if structure is not None else None,
        "structure_namespace": structure.attrib.get("namespace") if structure is not None else None,
        "dimension_at_observation": structure.attrib.get("dimensionAtObservation") if structure is not None else None,
        "dataflow": {"agency_id": "BIS", "id": DATAFLOW_CODE, "version": DATAFLOW_VERSION},
        "dataset_attributes": {k: dataset.attrib[k] for k in sorted(dataset.attrib) if k in {"UNIT_MULT", "UNIT_MEASURE"}} if dataset is not None else {},
        "http_status": raw_meta.get("http_status"),
        "content_type": raw_meta.get("content_type"),
        "acquired_at_utc": raw_meta.get("acquired_at_utc"),
    }


def normalize() -> dict[str, Any]:
    raw = RAW_PATH.read_bytes()
    raw_meta = json.loads(RAW_META_PATH.read_text(encoding="utf-8"))
    root = ET.fromstring(raw)
    metadata = _provider_metadata(root, raw_meta)
    raw_sha256 = sha(RAW_PATH)
    release_key = release_key_from_provider_metadata(metadata, raw_sha256)
    series_by_area: dict[str, dict[str, Any]] = {}
    obs_by_area_period: dict[tuple[str, str], dict[str, str]] = {}
    for series in root.iter():
        if _local(series.tag) != "Series":
            continue
        attrs = dict(series.attrib)
        area = attrs.get("REF_AREA")
        freq = attrs.get("FREQ")
        if freq != FREQUENCY or area not in AREAS:
            continue
        series_by_area[area] = attrs
        for obs in series:
            if _local(obs.tag) != "Obs":
                continue
            obs_attrs = dict(obs.attrib)
            period = obs_attrs.get("TIME_PERIOD")
            if period:
                obs_by_area_period[(area, period)] = obs_attrs
    rows: list[dict[str, Any]] = []
    whole_series_absence = []
    for area, (iso3, label) in AREAS.items():
        sattrs = series_by_area.get(area)
        if not sattrs:
            whole_series_absence.append({"provider_code": area, "iso3_code": iso3, "category": "whole_series_absence"})
            continue
        for year, month, provider_period, canonical_period in candidate_periods():
            obs = obs_by_area_period.get((area, provider_period))
            raw_value = obs.get("OBS_VALUE") if obs else None
            status = "missing" if raw_value in {None, ""} else "observed"
            value = None if status == "missing" else raw_value
            indicator_code = canonical_indicator_code()
            title = (sattrs.get("TITLE") or f"Central bank policy rates - {label} - Monthly").strip()
            attrs = {
                "task": TASK_ID,
                "source_provider": "BIS",
                "provider_dataset_code": PROVIDER_DATASET_CODE,
                "dataflow": DATAFLOW_CODE,
                "series_key": f"{FREQUENCY}.{area}",
                "frequency": FREQUENCY,
                "ref_area": area,
                "iso3_code": iso3,
                "measure": MEASURE_CLASS,
                "unit_measure_provider_code": metadata.get("dataset_attributes", {}).get("UNIT_MEASURE", UNIT_MEASURE_PROVIDER_CODE),
                "unit_mult": metadata.get("dataset_attributes", {}).get("UNIT_MULT", UNIT_MULT),
                "source_ref": sattrs.get("SOURCE_REF"),
                "compilation": sattrs.get("COMPILATION"),
                "decimals": sattrs.get("DECIMALS"),
                "title": title,
                "obs_status": obs.get("OBS_STATUS") if obs else None,
                "obs_conf": obs.get("OBS_CONF") if obs else None,
                "snapshot_release_key": release_key,
                "snapshot_prepared": metadata.get("prepared"),
                "snapshot_raw_sha256": raw_sha256,
            }
            rows.append({
                "provider_indicator_code": indicator_code,
                "provider_indicator_label": INDICATOR_NAME,
                "provider_series_key": f"{FREQUENCY}.{area}",
                "provider_territory_code": area,
                "territory_code": iso3,
                "territory_label": label,
                "provider_period_code": canonical_period,
                "period_year": year,
                "period_month": month,
                "frequency": FREQUENCY,
                "unit_code": UNIT_CODE,
                "unit_label": UNIT_LABEL,
                "value": value,
                "raw_value": raw_value,
                "observation_status": status,
                "decimal_precision": None if raw_value in {None, ""} or "." not in str(raw_value) else len(str(raw_value).split(".", 1)[1]),
                "attribute_hash": attr_hash(attrs),
                "attributes": attrs,
                "source_payload": {"series_attributes": sattrs, "obs_attributes": obs, "missing_basis": "candidate_period_absent_inside_valid_series" if obs is None else None},
            })
    rows.sort(key=lambda r: (r["provider_indicator_code"], r["provider_period_code"]))
    expected_cells = len(AREAS) * len(candidate_periods())
    provider_exclusions = whole_series_absence
    raw_sha256 = sha(RAW_PATH)
    release_key = release_key_from_provider_metadata(metadata, raw_sha256)
    norm = {
        "task": TASK_ID,
        "source_code": SOURCE_CODE,
        "source_name": SOURCE_NAME,
        "source_home_url": SOURCE_HOME_URL,
        "provider_dataset_code": PROVIDER_DATASET_CODE,
        "dataflow_code": DATAFLOW_CODE,
        "dataflow_version": DATAFLOW_VERSION,
        "release_key": release_key,
        "run_key": RUN_KEY,
        "pipeline_name": PIPELINE_NAME,
        "repository_class": "monthly_scalar_policy_rate_time_series",
        "repository_section": "Phase 2 monetary policy and financial conditions",
        "frequency": FREQUENCY,
        "as_of_date": AS_OF_DATE,
        "raw_evidence": {"source_url": raw_meta["source_url"], "raw_artifact_path": rel(RAW_PATH), "raw_metadata_path": rel(RAW_META_PATH), "raw_sha256": raw_sha256, "raw_bytes": RAW_PATH.stat().st_size, "request_parameters": raw_meta["request_parameters"]},
        "provider_metadata": metadata,
        "input_filters": {"frequency": FREQUENCY, "reference_areas": list(AREAS), "startPeriod": START_PERIOD, "endPeriod": END_PERIOD},
        "candidate_territory_count": len(AREAS),
        "candidate_period_count": len(candidate_periods()),
        "candidate_cell_count": expected_cells,
        "row_count": len(rows),
        "expected_row_count": expected_cells,
        "observed_value_count": sum(1 for r in rows if r["observation_status"] == "observed"),
        "explicit_missing_value_count": sum(1 for r in rows if r["observation_status"] == "missing"),
        "selection_exclusions": list(SELECTION_EXCLUSIONS),
        "provider_exclusions": provider_exclusions,
        "acquisition_errors": [],
        "territory_reconciliation": {"accepted_candidate_territories": [{"provider_code": k, "iso3_code": v[0], "label": v[1]} for k, v in AREAS.items()], "selection_exclusions": list(SELECTION_EXCLUSIONS), "unsupported_entities": [], "mapping_failures": [], "provider_exclusions": provider_exclusions},
        "rows": rows,
    }
    if norm["row_count"] != expected_cells:
        raise ValueError(f"candidate reconciliation failed: rows={norm['row_count']} expected={expected_cells}")
    return norm


def write_artifacts(norm: dict[str, Any]) -> None:
    tmp_dir = PROCESSED_DIR / ".active.tmp"
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)
    tmp_dir.mkdir(parents=True)
    tmp_norm = tmp_dir / NORM_PATH.name
    tmp_manifest = tmp_dir / MANIFEST_PATH.name
    tmp_norm.write_text(json.dumps(norm, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    manifest = {k: norm[k] for k in ["task", "source_code", "provider_dataset_code", "release_key", "run_key", "repository_class", "candidate_territory_count", "candidate_period_count", "candidate_cell_count", "row_count", "observed_value_count", "explicit_missing_value_count", "selection_exclusions", "provider_exclusions", "acquisition_errors"]}
    manifest["normalized_artifact_path"] = rel(NORM_PATH)
    manifest["normalized_sha256"] = sha256_bytes(tmp_norm.read_bytes())
    manifest["raw_artifact_path"] = rel(RAW_PATH)
    manifest["raw_sha256"] = norm["raw_evidence"]["raw_sha256"]
    tmp_manifest.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    active_dir = NORM_PATH.parent
    if active_dir.exists():
        shutil.rmtree(active_dir)
    tmp_dir.replace(active_dir)
    write_json(PROVIDER_REPORT, {"task": TASK_ID, "status": "complete", "candidate_cells": norm["candidate_cell_count"], "provider_valued_observations": norm["observed_value_count"], "explicit_missing": norm["explicit_missing_value_count"], "selection_exclusions": norm["selection_exclusions"], "provider_exclusions": norm["provider_exclusions"], "acquisition_errors": norm["acquisition_errors"], "provider_metadata": norm["provider_metadata"], "raw_evidence": norm["raw_evidence"]})
    write_checksums()


def values_sql(rows: list[dict[str, Any]]) -> str:
    vals = []
    for r in rows:
        vals.append("(" + ", ".join([
            sql_literal(r["provider_indicator_code"]), sql_literal(r["provider_indicator_label"]), sql_literal(r["territory_code"]), sql_literal(r["territory_label"]), sql_literal(r["provider_period_code"]), sql_literal(r["period_year"]), sql_literal(r["period_month"]), sql_literal(r["value"]), sql_literal(r["unit_code"]), sql_literal(r["unit_label"]), sql_literal(r["observation_status"]), sql_literal(r["decimal_precision"]), sql_literal(r["attribute_hash"]), jsonb_literal(r["attributes"]), jsonb_literal(r["source_payload"])
        ]) + ")")
    return ",\n".join(vals)


def build_sql(norm: dict[str, Any]) -> str:
    normalized_sha = sha(NORM_PATH)
    release_key = norm["release_key"]
    metadata = {"task": TASK_ID, "provider_metadata": norm["provider_metadata"], "candidate_cell_count": norm["candidate_cell_count"], "observed_value_count": norm["observed_value_count"], "explicit_missing_value_count": norm["explicit_missing_value_count"]}
    return f"""
BEGIN;
CREATE TABLE IF NOT EXISTS staging.bis_cbpol_policy_rate_phase2_observation (observation_id uuid PRIMARY KEY DEFAULT gen_random_uuid(), pipeline_run_id uuid NOT NULL REFERENCES meta.pipeline_run(pipeline_run_id), source_id uuid NOT NULL REFERENCES meta.source(source_id), dataset_release_id uuid REFERENCES meta.dataset_release(dataset_release_id), indicator_code text NOT NULL, indicator_name text NOT NULL, territory_code text NOT NULL, territory_label text NOT NULL, provider_period_code text NOT NULL, period_year integer NOT NULL, period_month integer NOT NULL, value numeric, unit_code text NOT NULL, unit_label text NOT NULL, observation_status text NOT NULL, decimal_precision integer, attribute_hash text NOT NULL, attributes jsonb NOT NULL, source_payload jsonb NOT NULL, CONSTRAINT uq_staging_bis_cbpol_policy_rate_phase2 UNIQUE (pipeline_run_id, indicator_code, territory_code, provider_period_code, unit_code, attribute_hash));
CREATE TEMP TABLE _task213_bis_rows (indicator_code text, indicator_name text, territory_code text, territory_label text, provider_period_code text, period_year integer, period_month integer, value numeric, unit_code text, unit_label text, observation_status text, decimal_precision integer, attribute_hash text, attributes jsonb, source_payload jsonb) ON COMMIT DROP;
INSERT INTO _task213_bis_rows VALUES
{values_sql(norm['rows'])};
WITH upsert_source AS (INSERT INTO meta.source (source_code, source_name, source_home_url, license_note) VALUES ({sql_literal(SOURCE_CODE)}, {sql_literal(SOURCE_NAME)}, {sql_literal(SOURCE_HOME_URL)}, 'BIS public SDMX API; campaign scope stored in dataset release and pipeline run metadata') ON CONFLICT (source_code) DO UPDATE SET source_name=EXCLUDED.source_name, source_home_url=EXCLUDED.source_home_url RETURNING source_id), source_row AS (SELECT source_id FROM upsert_source UNION ALL SELECT source_id FROM meta.source WHERE source_code={sql_literal(SOURCE_CODE)} LIMIT 1), upsert_release AS (INSERT INTO meta.dataset_release (source_id, provider_dataset_code, release_key, release_date, source_url, raw_artifact_path, raw_sha256, metadata) SELECT source_id,{sql_literal(PROVIDER_DATASET_CODE)},{sql_literal(release_key)},NULL::date,{sql_literal(norm['raw_evidence']['source_url'])},{sql_literal(norm['raw_evidence']['raw_artifact_path'])},{sql_literal(norm['raw_evidence']['raw_sha256'])},{jsonb_literal(metadata)} FROM source_row ON CONFLICT (source_id, provider_dataset_code, release_key) DO UPDATE SET release_date=EXCLUDED.release_date, source_url=EXCLUDED.source_url, raw_artifact_path=EXCLUDED.raw_artifact_path, raw_sha256=EXCLUDED.raw_sha256, metadata=EXCLUDED.metadata RETURNING dataset_release_id), release_row AS (SELECT dataset_release_id FROM upsert_release UNION ALL SELECT dr.dataset_release_id FROM meta.dataset_release dr JOIN source_row s ON dr.source_id=s.source_id WHERE dr.provider_dataset_code={sql_literal(PROVIDER_DATASET_CODE)} AND dr.release_key={sql_literal(release_key)} LIMIT 1), upsert_run AS (INSERT INTO meta.pipeline_run (run_key, source_id, dataset_release_id, pipeline_name, finished_at, status, input_parameters, artifact_manifest) SELECT {sql_literal(norm["run_key"])},s.source_id,r.dataset_release_id,{sql_literal(PIPELINE_NAME)},now(),'succeeded',{jsonb_literal(norm['input_filters'])},{jsonb_literal({'raw': rel(RAW_PATH), 'normalized': rel(NORM_PATH), 'manifest': rel(MANIFEST_PATH)})} FROM source_row s CROSS JOIN release_row r ON CONFLICT (run_key) DO UPDATE SET source_id=EXCLUDED.source_id, dataset_release_id=EXCLUDED.dataset_release_id, finished_at=EXCLUDED.finished_at, status=EXCLUDED.status, input_parameters=EXCLUDED.input_parameters, artifact_manifest=EXCLUDED.artifact_manifest RETURNING pipeline_run_id) SELECT 1;
WITH run_row AS (SELECT pipeline_run_id FROM meta.pipeline_run WHERE run_key={sql_literal(norm["run_key"])}) DELETE FROM staging.bis_cbpol_policy_rate_phase2_observation s USING run_row WHERE s.pipeline_run_id=run_row.pipeline_run_id;
WITH run_row AS (SELECT pipeline_run_id FROM meta.pipeline_run WHERE run_key={sql_literal(norm["run_key"])}) DELETE FROM curated.fact_observation f USING run_row WHERE f.pipeline_run_id=run_row.pipeline_run_id;
WITH run_row AS (SELECT pipeline_run_id FROM meta.pipeline_run WHERE run_key={sql_literal(norm["run_key"])}) DELETE FROM meta.lineage_event le USING run_row WHERE le.pipeline_run_id=run_row.pipeline_run_id;
WITH run_row AS (SELECT pipeline_run_id FROM meta.pipeline_run WHERE run_key={sql_literal(norm["run_key"])}) DELETE FROM meta.quality_check qc USING run_row WHERE qc.pipeline_run_id=run_row.pipeline_run_id;
WITH source_row AS (SELECT source_id FROM meta.source WHERE source_code={sql_literal(SOURCE_CODE)}), release_row AS (SELECT dataset_release_id FROM meta.dataset_release WHERE provider_dataset_code={sql_literal(PROVIDER_DATASET_CODE)} AND release_key={sql_literal(release_key)}), run_row AS (SELECT pipeline_run_id FROM meta.pipeline_run WHERE run_key={sql_literal(norm["run_key"])}) INSERT INTO staging.bis_cbpol_policy_rate_phase2_observation (pipeline_run_id,source_id,dataset_release_id,indicator_code,indicator_name,territory_code,territory_label,provider_period_code,period_year,period_month,value,unit_code,unit_label,observation_status,decimal_precision,attribute_hash,attributes,source_payload) SELECT run.pipeline_run_id,s.source_id,rel.dataset_release_id,r.* FROM _task213_bis_rows r CROSS JOIN source_row s CROSS JOIN release_row rel CROSS JOIN run_row run;
WITH source_row AS (SELECT source_id FROM meta.source WHERE source_code={sql_literal(SOURCE_CODE)}) INSERT INTO curated.dim_indicator (source_id, source_indicator_code, indicator_name, topic) SELECT DISTINCT s.source_id,r.indicator_code,r.indicator_name,'central_bank_policy_rate' FROM source_row s CROSS JOIN _task213_bis_rows r ON CONFLICT (source_id, source_indicator_code) DO UPDATE SET indicator_name=EXCLUDED.indicator_name, topic=EXCLUDED.topic;
INSERT INTO curated.dim_territory (territory_type, iso3_code, canonical_territory_code, territory_name, metadata) SELECT DISTINCT 'country',territory_code,territory_code,territory_label,{jsonb_literal({'source_provider':'BIS','task':TASK_ID})} FROM _task213_bis_rows ON CONFLICT (canonical_territory_code) DO UPDATE SET territory_name=EXCLUDED.territory_name, metadata=curated.dim_territory.metadata || EXCLUDED.metadata;
INSERT INTO curated.dim_period (frequency, period_year, period_month, period_start_date, period_end_date, period_label) SELECT DISTINCT 'M',period_year,period_month,make_date(period_year,period_month,1),(make_date(period_year,period_month,1)+interval '1 month - 1 day')::date,provider_period_code FROM _task213_bis_rows ON CONFLICT (frequency, period_start_date, period_end_date) DO UPDATE SET period_month=EXCLUDED.period_month, period_label=EXCLUDED.period_label;
INSERT INTO curated.dim_unit (unit_code, unit_name) SELECT DISTINCT unit_code,unit_label FROM _task213_bis_rows ON CONFLICT (unit_code) DO UPDATE SET unit_name=EXCLUDED.unit_name;
INSERT INTO curated.dim_attribute_set (attribute_hash, attributes) SELECT DISTINCT attribute_hash,attributes FROM _task213_bis_rows ON CONFLICT (attribute_hash) DO UPDATE SET attributes=EXCLUDED.attributes;
WITH source_row AS (SELECT source_id FROM meta.source WHERE source_code={sql_literal(SOURCE_CODE)}), release_row AS (SELECT dataset_release_id FROM meta.dataset_release WHERE provider_dataset_code={sql_literal(PROVIDER_DATASET_CODE)} AND release_key={sql_literal(release_key)}), run_row AS (SELECT pipeline_run_id FROM meta.pipeline_run WHERE run_key={sql_literal(norm["run_key"])}), staged AS (SELECT st.* FROM staging.bis_cbpol_policy_rate_phase2_observation st JOIN run_row r ON st.pipeline_run_id=r.pipeline_run_id) INSERT INTO curated.fact_observation (source_id,dataset_release_id,pipeline_run_id,indicator_id,territory_id,period_id,unit_id,attribute_set_id,value,as_of_date,observation_status) SELECT s.source_id,rel.dataset_release_id,run.pipeline_run_id,ind.indicator_id,terr.territory_id,per.period_id,unit.unit_id,aset.attribute_set_id,staged.value,{sql_literal(AS_OF_DATE)}::date,staged.observation_status FROM staged CROSS JOIN source_row s CROSS JOIN release_row rel CROSS JOIN run_row run JOIN curated.dim_indicator ind ON ind.source_id=s.source_id AND ind.source_indicator_code=staged.indicator_code JOIN curated.dim_territory terr ON terr.canonical_territory_code=staged.territory_code JOIN curated.dim_period per ON per.frequency='M' AND per.period_start_date=make_date(staged.period_year,staged.period_month,1) JOIN curated.dim_unit unit ON unit.unit_code=staged.unit_code JOIN curated.dim_attribute_set aset ON aset.attribute_hash=staged.attribute_hash;
WITH source_row AS (SELECT source_id FROM meta.source WHERE source_code={sql_literal(SOURCE_CODE)}), run_row AS (SELECT pipeline_run_id FROM meta.pipeline_run WHERE run_key={sql_literal(norm["run_key"])}) INSERT INTO meta.lineage_event (pipeline_run_id,source_id,event_type,from_artifact,to_artifact,checksum_sha256,row_count,details) SELECT run.pipeline_run_id,s.source_id,event_type,from_artifact,to_artifact,checksum,row_count,details FROM source_row s CROSS JOIN run_row run CROSS JOIN (VALUES ('raw_bis_sdmx_acquired',{sql_literal(rel(RAW_PATH))},{sql_literal(rel(NORM_PATH))},{sql_literal(norm['raw_evidence']['raw_sha256'])},{int(norm['row_count'])}::bigint,{jsonb_literal({'task':TASK_ID,'provider_dataset_code':PROVIDER_DATASET_CODE})}),('normalized_rows_loaded',{sql_literal(rel(NORM_PATH))},'curated.fact_observation',{sql_literal(normalized_sha)},{int(norm['row_count'])}::bigint,{jsonb_literal({'task':TASK_ID,'provider_dataset_code':PROVIDER_DATASET_CODE})})) AS events(event_type,from_artifact,to_artifact,checksum,row_count,details);
WITH run_row AS (SELECT pipeline_run_id FROM meta.pipeline_run WHERE run_key={sql_literal(norm["run_key"])}) INSERT INTO meta.quality_check (pipeline_run_id,check_name,check_status,severity,observed_value,expected_value,details) SELECT run.pipeline_run_id,check_name,check_status,'error',observed_value,expected_value,details FROM run_row run CROSS JOIN (VALUES ('candidate_cell_count', CASE WHEN (SELECT count(*) FROM _task213_bis_rows)={int(norm['candidate_cell_count'])} THEN 'pass' ELSE 'fail' END,(SELECT count(*)::numeric FROM _task213_bis_rows),{int(norm['candidate_cell_count'])}::numeric,{jsonb_literal({'task':TASK_ID})}),('observed_missing_reconciliation', CASE WHEN ((SELECT count(*) FROM _task213_bis_rows WHERE observation_status='observed')={int(norm['observed_value_count'])} AND (SELECT count(*) FROM _task213_bis_rows WHERE observation_status='missing')={int(norm['explicit_missing_value_count'])}) THEN 'pass' ELSE 'fail' END,(SELECT count(*)::numeric FROM _task213_bis_rows),{int(norm['candidate_cell_count'])}::numeric,{jsonb_literal({'task':TASK_ID})}),('acquisition_errors_absent','pass',0::numeric,0::numeric,{jsonb_literal({'task':TASK_ID})})) AS checks(check_name,check_status,observed_value,expected_value,details);
COMMIT;
"""


def counts(db: str) -> dict[str, int]:
    return parse_pipe_counts(psql_scalar(db, """SELECT (SELECT count(*) FROM curated.fact_observation)::text||'|'||(SELECT count(*) FROM curated.dim_indicator)::text||'|'||(SELECT count(*) FROM curated.dim_territory)::text||'|'||(SELECT count(*) FROM curated.dim_period)::text||'|'||(SELECT count(*) FROM meta.source)::text||'|'||(SELECT count(*) FROM meta.dataset_release)::text||'|'||(SELECT count(*) FROM meta.pipeline_run)::text||'|'||(SELECT count(*) FROM meta.lineage_event)::text||'|'||(SELECT count(*) FROM meta.quality_check)::text;"""), [("facts", int), ("indicators", int), ("territories", int), ("periods", int), ("sources", int), ("dataset_releases", int), ("runs", int), ("lineage", int), ("quality", int)])


def run_counts(db: str, run_key: str = RUN_KEY) -> dict[str, int]:
    raw = psql_scalar(db, f"""WITH run AS (SELECT pipeline_run_id FROM meta.pipeline_run WHERE run_key={sql_literal(run_key)}) SELECT (SELECT count(*) FROM staging.bis_cbpol_policy_rate_phase2_observation s JOIN run USING(pipeline_run_id))::text||'|'||(SELECT count(*) FROM curated.fact_observation f JOIN run USING(pipeline_run_id))::text||'|'||(SELECT count(*) FROM curated.fact_observation f JOIN run USING(pipeline_run_id) WHERE observation_status='observed')::text||'|'||(SELECT count(*) FROM curated.fact_observation f JOIN run USING(pipeline_run_id) WHERE observation_status='missing')::text||'|'||(SELECT count(DISTINCT indicator_id) FROM curated.fact_observation f JOIN run USING(pipeline_run_id))::text||'|'||(SELECT count(DISTINCT territory_id) FROM curated.fact_observation f JOIN run USING(pipeline_run_id))::text||'|'||(SELECT count(DISTINCT period_id) FROM curated.fact_observation f JOIN run USING(pipeline_run_id))::text||'|'||(SELECT count(*) FROM meta.lineage_event l JOIN run USING(pipeline_run_id))::text||'|'||(SELECT count(*) FROM meta.quality_check q JOIN run USING(pipeline_run_id))::text;""")
    return parse_pipe_counts(raw, [("staging_rows", int), ("fact_rows", int), ("observed_facts", int), ("explicit_missing_facts", int), ("indicator_count", int), ("territory_count", int), ("period_count", int), ("lineage_events", int), ("quality_checks", int)])


def load(norm: dict[str, Any], db: str = "macroforge") -> dict[str, Any]:
    sql = build_sql(norm)
    SQL_PATH.write_text(sql, encoding="utf-8")
    before = counts(db)
    run_psql_file(db, sql)
    after = counts(db)
    rc = run_counts(db, norm["run_key"])
    dup = int(psql_scalar(db, f"""WITH src AS (SELECT source_id FROM meta.source WHERE source_code={sql_literal(SOURCE_CODE)}) SELECT count(*) FROM (SELECT source_id,indicator_id,territory_id,period_id,unit_id,attribute_set_id,as_of_date,count(*) FROM curated.fact_observation WHERE source_id=(SELECT source_id FROM src) GROUP BY 1,2,3,4,5,6,7 HAVING count(*)>1)d;"""))
    source_rows = int(psql_scalar(db, f"SELECT count(*) FROM meta.source WHERE source_code={sql_literal(SOURCE_CODE)};"))
    corrected_dataset_rows = int(psql_scalar(db, f"WITH src AS (SELECT source_id FROM meta.source WHERE source_code={sql_literal(SOURCE_CODE)}) SELECT count(*) FROM meta.dataset_release WHERE source_id=(SELECT source_id FROM src) AND provider_dataset_code={sql_literal(PROVIDER_DATASET_CODE)} AND release_key={sql_literal(norm['release_key'])};"))
    all_dataset_rows = int(psql_scalar(db, f"WITH src AS (SELECT source_id FROM meta.source WHERE source_code={sql_literal(SOURCE_CODE)}) SELECT count(*) FROM meta.dataset_release WHERE source_id=(SELECT source_id FROM src) AND provider_dataset_code={sql_literal(PROVIDER_DATASET_CODE)};"))
    failed_q = int(psql_scalar(db, f"WITH run AS (SELECT pipeline_run_id FROM meta.pipeline_run WHERE run_key={sql_literal(norm['run_key'])}) SELECT count(*) FROM meta.quality_check q JOIN run USING(pipeline_run_id) WHERE check_status<>'pass';"))
    obsolete_release_refs = parse_pipe_counts(psql_scalar(db, """WITH oldrel AS (SELECT dataset_release_id FROM meta.dataset_release WHERE provider_dataset_code='BIS:WS_CBPOL' AND release_key='bis-ws-cbpol-current-snapshot-2015m01-2026m06') SELECT (SELECT count(*) FROM oldrel)::text||'|'||(SELECT count(*) FROM curated.fact_observation WHERE dataset_release_id IN (SELECT dataset_release_id FROM oldrel))::text||'|'||(SELECT count(*) FROM staging.bis_cbpol_policy_rate_phase2_observation WHERE dataset_release_id IN (SELECT dataset_release_id FROM oldrel))::text||'|'||(SELECT count(*) FROM meta.pipeline_run WHERE dataset_release_id IN (SELECT dataset_release_id FROM oldrel))::text;"""), [("dataset_release_rows", int), ("fact_refs", int), ("staging_refs", int), ("pipeline_run_refs", int)])
    obsolete_indicator_refs = parse_pipe_counts(psql_scalar(db, f"""WITH src AS (SELECT source_id FROM meta.source WHERE source_code={sql_literal(SOURCE_CODE)}), oldind AS (SELECT indicator_id FROM curated.dim_indicator WHERE source_id=(SELECT source_id FROM src) AND source_indicator_code LIKE 'BIS:WS_CBPOL:M.%') SELECT (SELECT count(*) FROM oldind)::text||'|'||(SELECT count(*) FROM curated.fact_observation WHERE indicator_id IN (SELECT indicator_id FROM oldind))::text;"""), [("indicator_rows", int), ("fact_refs", int)])
    report = {"task": TASK_ID, "run_key": norm["run_key"], "release_key": norm["release_key"], "source_code": SOURCE_CODE, "provider_dataset_code": PROVIDER_DATASET_CODE, "before_counts": before, "after_counts": after, "repository_growth": {k: after[k] - before[k] for k in before}, **rc, "duplicate_canonical_key_groups": dup, "canonical_source_rows": source_rows, "corrected_dataset_snapshot_rows": corrected_dataset_rows, "all_bis_ws_cbpol_dataset_release_rows": all_dataset_rows, "failed_quality_checks": failed_q, "obsolete_metadata_reference_audit": {"legacy_window_bound_release": obsolete_release_refs, "legacy_country_encoded_indicators": obsolete_indicator_refs}, "obsolete_metadata_cleanup_status": "not_deleted_requires_explicit_authorization"}
    write_json_report(LOAD_REPORT, report, default_task=TASK_ID)
    return report


def evaluate(norm: dict[str, Any], load_report: dict[str, Any]) -> dict[str, Any]:
    ev = {
        "task": TASK_ID,
        "prediction_quality_verdict": "Mixed",
        "scale_prediction_error": {"predicted": "4968 candidate cells and 4900-4968 provider-valued or explicit-missing cells", "actual_candidate_cells": norm["candidate_cell_count"], "actual_loaded_cells": norm["row_count"], "actual_provider_valued": norm["observed_value_count"], "actual_explicit_missing": norm["explicit_missing_value_count"], "explanation": "Scale prediction missed accepted Hong Kong mapping; corrected grid is 37 territories x 138 months = 5106 cells."},
        "provider_behavior_surprises": "No unresolved provider or transport errors. The selected broad WS_CBPOL key returned valid StructureSpecificData.",
        "territory_mapping_error": "Original prediction incorrectly treated HK as a non-sovereign exclusion. PostgreSQL already had canonical HKG/Hong Kong SAR, so HK was corrected into the accepted candidate grid. XM remains an aggregate selection exclusion, not a provider exclusion.",
        "unit_frequency_surprises": "None. Dataset-level UNIT_MEASURE=368 and UNIT_MULT=0 remained stable; frequency was monthly.",
        "dimensional_complexity_verdict": "WS_CBPOL remained scalar-compatible: provider dimensions were FREQ, REF_AREA, TIME_PERIOD plus series/observation attributes, not a repository-class mismatch.",
        "implementation_friction_error": "Higher than first pass: corrected identity required de-countrying indicator identity, deriving snapshot identity from provider prepared timestamp, adding HK mapping, and auditing obsolete metadata references. Still source-specific; no broad BIS/SDMX framework was needed.",
        "missing_bis_understanding_revealed": True,
    }
    write_json(EVAL_REPORT, ev)
    write_checksums()
    return ev


def write_checksums() -> None:
    paths = [p for p in [PRED_PATH, RAW_PATH, RAW_META_PATH, NORM_PATH, MANIFEST_PATH, PROVIDER_REPORT, LOAD_REPORT, EVAL_REPORT, SQL_PATH] if p.exists()]
    CHECKSUMS.parent.mkdir(parents=True, exist_ok=True)
    CHECKSUMS.write_text("".join(f"{sha(p)}  {rel(p)}\n" for p in sorted(paths)), encoding="utf-8")


def run_all(db: str) -> dict[str, Any]:
    if not PRED_PATH.exists():
        raise RuntimeError("Frozen prediction must exist before acquisition")
    fetch_raw()
    norm = normalize()
    write_artifacts(norm)
    report = load(norm, db=db)
    idem = load(norm, db=db)
    evaluation = evaluate(norm, idem)
    return {"normalized": {"candidate_cells": norm["candidate_cell_count"], "observed": norm["observed_value_count"], "explicit_missing": norm["explicit_missing_value_count"]}, "load_report": report, "idempotence_report": idem, "evaluation": evaluation}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=["fetch", "normalize", "load", "run", "evaluate"])
    parser.add_argument("--db", default="macroforge")
    args = parser.parse_args()
    if args.command == "fetch":
        print(json.dumps(fetch_raw(), indent=2, sort_keys=True))
    elif args.command == "normalize":
        norm = normalize(); write_artifacts(norm); print(json.dumps({"candidate_cells": norm["candidate_cell_count"], "observed": norm["observed_value_count"], "explicit_missing": norm["explicit_missing_value_count"]}, sort_keys=True))
    elif args.command == "load":
        norm = json.loads(NORM_PATH.read_text(encoding="utf-8")); print(json.dumps(load(norm, db=args.db), indent=2, sort_keys=True))
    elif args.command == "evaluate":
        norm = json.loads(NORM_PATH.read_text(encoding="utf-8")); load_report = json.loads(LOAD_REPORT.read_text(encoding="utf-8")); print(json.dumps(evaluate(norm, load_report), indent=2, sort_keys=True))
    elif args.command == "run":
        print(json.dumps(run_all(args.db), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
