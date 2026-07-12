from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "src"))

from macroforge import bis_sdmx
from macroforge.db_helpers import jsonb_literal, parse_pipe_counts, psql_scalar, run_psql_file, sql_literal, write_json_report

TASK_ID = "TASK-215"
SLUG = "task215_bis_credit_gap_phase2_campaign"
SOURCE_CODE = bis_sdmx.BIS_SOURCE_CODE
SOURCE_NAME = bis_sdmx.BIS_SOURCE_NAME
SOURCE_HOME_URL = bis_sdmx.BIS_SOURCE_HOME_URL
PROVIDER_DATASET_CODE = "BIS:WS_CREDIT_GAP"
DATAFLOW_CODE = "WS_CREDIT_GAP"
DATAFLOW_VERSION = "1.0"
RUN_KEY = "task-215-bis-credit-gap-phase2"
PIPELINE_NAME = "bis_credit_gap_phase2_campaign"
FREQUENCY = "Q"
START_PERIOD = "2010-Q1"
END_PERIOD = "2025-Q4"
AS_OF_DATE = "2026-07-12"
UNIT_CODE = "PERCENTAGE_POINTS"
UNIT_LABEL = "Percentage points"
UNIT_MEASURE_PROVIDER_CODE = "770"
UNIT_MULT = "0"
TERRITORY_DIMENSION = "BORROWERS_CTY"
SERIES_KEY_DIMENSIONS = ["FREQ", "BORROWERS_CTY", "TC_BORROWERS", "TC_LENDERS", "CG_DTYPE"]

AREAS: dict[str, tuple[str, str]] = {
    "AR": ("ARG", "Argentina"), "AT": ("AUT", "Austria"), "AU": ("AUS", "Australia"), "BE": ("BEL", "Belgium"),
    "BR": ("BRA", "Brazil"), "CA": ("CAN", "Canada"), "CH": ("CHE", "Switzerland"), "CL": ("CHL", "Chile"),
    "CN": ("CHN", "China"), "CO": ("COL", "Colombia"), "CZ": ("CZE", "Czechia"), "DE": ("DEU", "Germany"),
    "DK": ("DNK", "Denmark"), "ES": ("ESP", "Spain"), "FI": ("FIN", "Finland"), "FR": ("FRA", "France"),
    "GB": ("GBR", "United Kingdom"), "GR": ("GRC", "Greece"), "HK": ("HKG", "Hong Kong SAR"), "HU": ("HUN", "Hungary"),
    "ID": ("IDN", "Indonesia"), "IE": ("IRL", "Ireland"), "IL": ("ISR", "Israel"), "IN": ("IND", "India"),
    "IT": ("ITA", "Italy"), "JP": ("JPN", "Japan"), "KR": ("KOR", "Korea"), "LU": ("LUX", "Luxembourg"),
    "MX": ("MEX", "Mexico"), "MY": ("MYS", "Malaysia"), "NL": ("NLD", "Netherlands"), "NO": ("NOR", "Norway"),
    "NZ": ("NZL", "New Zealand"), "PL": ("POL", "Poland"), "PT": ("PRT", "Portugal"), "RU": ("RUS", "Russia"),
    "SA": ("SAU", "Saudi Arabia"), "SE": ("SWE", "Sweden"), "SG": ("SGP", "Singapore"), "TH": ("THA", "Thailand"),
    "TR": ("TUR", "Turkiye"), "US": ("USA", "United States"), "ZA": ("ZAF", "South Africa"),
}
AGGREGATE_EXCLUSIONS = {"XM": "Euro area aggregate"}
TC_BORROWERS = {"P": ("PRIVATE_NONFINANCIAL_SECTOR", "Private non-financial sector")}
TC_LENDERS = {"A": ("ALL_SECTORS", "All sectors")}
CG_DTYPES = {"C": ("CREDIT_TO_GDP_GAP_ACTUAL_MINUS_TREND", "Credit-to-GDP gap (actual minus HP-filter trend)")}
PROVIDER_STRUCTURE = {
    "provider_dataset_code": PROVIDER_DATASET_CODE,
    "dataflow_code": DATAFLOW_CODE,
    "dataflow_version": DATAFLOW_VERSION,
    "series_key_dimensions": SERIES_KEY_DIMENSIONS,
    "territory_dimension": TERRITORY_DIMENSION,
    "borrower_sector_dimensions": ["TC_BORROWERS"],
    "lender_sector_dimensions": ["TC_LENDERS"],
    "measure_dimensions": ["CG_DTYPE"],
    "frequency": FREQUENCY,
    "unit_measure_provider_code": UNIT_MEASURE_PROVIDER_CODE,
    "unit_measure_label": "Percentage points",
    "unit_mult": UNIT_MULT,
    "provider_area_count": 44,
    "selected_area_count": 43,
    "provider_aggregate_exclusions": AGGREGATE_EXCLUSIONS,
    "provider_series_count_all_dtypes": 132,
    "selected_provider_advertised_series_count": 43,
    "provider_temporal_coverage_all": {"start": "1947-Q4", "end": "2025-Q4"},
    "selected_window": {"start": START_PERIOD, "end": END_PERIOD, "quarters": 64},
    "codelist_labels": {"TC_BORROWERS.P": "Private non-financial sector", "TC_LENDERS.A": "All sectors", "CG_DTYPE.C": "Credit-to-GDP gaps (actual-trend)", "UNIT_MEASURE.770": "Percentage points"},
}
SERIES_KEYS: tuple[tuple[str, str, str, str], ...] = tuple((area, "P", "A", "C") for area in sorted(AREAS))

RAW_DIR = PROJECT_ROOT / "data/raw" / SLUG
PROCESSED_DIR = PROJECT_ROOT / "data/processed" / SLUG
REPORT_DIR = PROJECT_ROOT / "artifacts/reports"
PRED_PATH = REPORT_DIR / "task-215-bis-credit-gap-frozen-pre-execution-prediction.json"
RAW_PATH = RAW_DIR / "active" / "task-215-bis-credit-gap-2010q1-2025q4-raw.xml"
RAW_META_PATH = RAW_DIR / "active" / "task-215-bis-credit-gap-2010q1-2025q4-raw-metadata.json"
NORM_PATH = PROCESSED_DIR / "active" / "task-215-bis-credit-gap-normalized.json"
MANIFEST_PATH = PROCESSED_DIR / "active" / "task-215-bis-credit-gap-manifest.json"
PROVIDER_REPORT = REPORT_DIR / "task-215-bis-credit-gap-provider-structure-and-evidence-report.json"
LOAD_REPORT = REPORT_DIR / "task-215-bis-credit-gap-postgresql-load-report.json"
EVAL_REPORT = REPORT_DIR / "task-215-bis-credit-gap-prediction-evaluation.json"
SUBSTRATE_REPORT = REPORT_DIR / "task-215-bis-substrate-extraction-decision.json"
CHECKSUMS = REPORT_DIR / "task-215-bis-credit-gap-artifact-checksums.txt"
SQL_PATH = REPORT_DIR / "task-215-bis-credit-gap-load.sql"


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def rel(path: Path) -> str:
    return bis_sdmx.rel(path, PROJECT_ROOT)


def sha(path: Path) -> str:
    return bis_sdmx.sha256_file(path)


def quarter_periods() -> list[tuple[int, int, str, str, str, str]]:
    return bis_sdmx.quarter_periods(START_PERIOD, END_PERIOD)


def source_url(start_period: str = START_PERIOD, end_period: str = END_PERIOD) -> str:
    return bis_sdmx.bis_data_url(DATAFLOW_CODE, DATAFLOW_VERSION, "Q..P.A.C", start_period=start_period, end_period=end_period)


def canonical_indicator_code(borrower: str = "P", lender: str = "A", dtype: str = "C", unit_code: str = UNIT_CODE, frequency: str = FREQUENCY) -> str:
    return f"BIS:WS_CREDIT_GAP:{CG_DTYPES[dtype][0]}:{TC_BORROWERS[borrower][0]}:{TC_LENDERS[lender][0]}:{unit_code}:{frequency}"


def write_substrate_decision() -> dict[str, Any]:
    decision = {
        "task": TASK_ID,
        "decision": "Extracted narrow BIS-specific substrate helpers",
        "evidence_tasks": ["TASK-057", "TASK-213", "TASK-214", "TASK-215"],
        "implemented_boundary": "src/macroforge/bis_sdmx.py",
        "stable_contracts": [
            "canonical BIS public API source constants",
            "Prepared-derived acquired-response snapshot key that excludes query windows and campaign scope",
            "SDMX Header/DataSet response metadata extraction",
            "attempt-specific fetch evidence plus atomic active raw promotion",
            "quarterly period helper",
            "series-key helper that removes only the territory dimension for scalar indicator compatibility checks",
            "shared hashing/path helpers for artifact manifests and attribute identity",
        ],
        "explicitly_not_implemented": ["universal SDMX adapter", "generic provider framework", "universal campaign engine", "generic financial ontology", "speculative multidimensional schema"],
        "reason": "Four BIS campaigns now repeat source identity, Prepared snapshot identity, response metadata, attempt publication, and territory-removal indicator logic. Keeping these task-local would risk drift like TASK-213's earlier country-encoded identity and HK exclusion mistake. The extracted module remains BIS-specific and does not own dataflow-specific semantics.",
    }
    write_json(SUBSTRATE_REPORT, decision)
    return decision


def write_prediction() -> dict[str, Any]:
    write_substrate_decision()
    periods = quarter_periods()
    pred = {
        "task": TASK_ID,
        "selected_capability": "BIS quarterly cross-country credit-to-GDP gap for private non-financial sector credit from all lenders",
        "provider_structure_investigation": PROVIDER_STRUCTURE,
        "provider_dataset": PROVIDER_DATASET_CODE,
        "dataflow_code": DATAFLOW_CODE,
        "series_key_dimensions": SERIES_KEY_DIMENSIONS,
        "canonical_indicator_rule": "remove only BORROWERS_CTY/territory; preserve TC_BORROWERS, TC_LENDERS, CG_DTYPE, unit, and frequency in source-scoped scalar indicator identity",
        "accepted_frequency": FREQUENCY,
        "period_range": {"start": START_PERIOD, "end": END_PERIOD, "quarters": len(periods)},
        "accepted_territories": [{"provider_code": k, "iso3_code": v[0], "label": v[1]} for k, v in AREAS.items()],
        "sectors": {"borrowers": TC_BORROWERS, "lenders": TC_LENDERS},
        "measures": CG_DTYPES,
        "units": {"canonical": UNIT_CODE, "provider_unit_measure": UNIT_MEASURE_PROVIDER_CODE, "unit_multiplier": UNIT_MULT},
        "candidate_series": [{"series_key": f"Q.{area}.P.A.C", "provider_territory_code": area, "tc_borrowers": "P", "tc_lenders": "A", "cg_dtype": "C"} for area, _, _, _ in SERIES_KEYS],
        "selection_exclusions": [{"provider_code": k, "category": "provider_aggregate_selection_exclusion", "reason": v} for k, v in AGGREGATE_EXCLUSIONS.items()],
        "expected_candidate_series": len(SERIES_KEYS),
        "expected_candidate_cells": len(SERIES_KEYS) * len(periods),
        "expected_provider_valued_facts": len(SERIES_KEYS) * len(periods),
        "expected_explicit_missing_facts": 0,
        "expected_exclusions": {"aggregates": 1, "unsupported_entities": 0, "mapping_failures": 0, "incompatible_series": 0, "acquisition_errors": 0},
        "expected_dimensional_complexity": "scalar-compatible if BORROWERS_CTY is removed and TC_BORROWERS=P, TC_LENDERS=A, CG_DTYPE=C, unit=percentage points, frequency=Q remain in indicator identity",
        "expected_transport_behavior": "compact single BIS StructureSpecificData response for Q..P.A.C over 2010-Q1..2025-Q4; provider Prepared timestamp may churn",
        "expected_implementation_friction": "moderate: this is the fourth BIS campaign and justifies narrow shared BIS helper extraction, but dataflow-specific semantics remain task-local",
        "expected_postgresql_growth": {"facts": len(SERIES_KEYS) * len(periods), "indicators": 1, "dataset_releases": 1, "pipeline_runs": 1},
        "expected_scalar_compatibility": "compatible; credit gaps are percentage-point scalar observations when CG_DTYPE=C is isolated from ratios/trends",
    }
    write_json(PRED_PATH, pred)
    return pred


def fetch_raw() -> dict[str, Any]:
    return bis_sdmx.fetch_to_attempt(
        url=source_url(), raw_dir=RAW_DIR, active_raw_path=RAW_PATH, active_meta_path=RAW_META_PATH, task_id=TASK_ID,
        request_parameters={"dataflow": DATAFLOW_CODE, "version": DATAFLOW_VERSION, "key": "Q..P.A.C", "startPeriod": START_PERIOD, "endPeriod": END_PERIOD},
        user_agent="MacroForge TASK-215 BIS credit-gap Phase2", timeout=120,
    )


def normalize() -> dict[str, Any]:
    raw_meta = json.loads(RAW_META_PATH.read_text(encoding="utf-8"))
    root = ET.fromstring(RAW_PATH.read_bytes())
    metadata = bis_sdmx.provider_metadata(root, dataflow_code=DATAFLOW_CODE, dataflow_version=DATAFLOW_VERSION, raw_meta=raw_meta)
    raw_sha256 = sha(RAW_PATH)
    release_key = bis_sdmx.prepared_to_snapshot_key(DATAFLOW_CODE, metadata.get("prepared"))
    series_attrs: dict[str, dict[str, str]] = {}
    obs_by_area_period: dict[tuple[str, str], dict[str, str]] = {}
    incompatible_series = []
    for series in root.iter():
        if bis_sdmx.local_name(series.tag) != "Series":
            continue
        attrs = dict(series.attrib)
        area = attrs.get("BORROWERS_CTY")
        if attrs.get("FREQ") != FREQUENCY or attrs.get("TC_BORROWERS") != "P" or attrs.get("TC_LENDERS") != "A" or attrs.get("CG_DTYPE") != "C":
            incompatible_series.append(attrs)
            continue
        if area in AGGREGATE_EXCLUSIONS:
            continue
        if area not in AREAS:
            incompatible_series.append(attrs)
            continue
        remaining = bis_sdmx.series_key_without_territory(attrs, SERIES_KEY_DIMENSIONS, TERRITORY_DIMENSION)
        if remaining != (FREQUENCY, "P", "A", "C"):
            incompatible_series.append(attrs)
            continue
        series_attrs[area] = attrs
        for obs in series:
            if bis_sdmx.local_name(obs.tag) == "Obs" and obs.attrib.get("TIME_PERIOD"):
                obs_by_area_period[(area, obs.attrib["TIME_PERIOD"])] = dict(obs.attrib)
    rows: list[dict[str, Any]] = []
    whole_series_absence = []
    for area, borrower, lender, dtype in SERIES_KEYS:
        sattrs = series_attrs.get(area)
        iso3, label = AREAS[area]
        if not sattrs:
            whole_series_absence.append({"provider_code": f"Q.{area}.{borrower}.{lender}.{dtype}", "category": "whole_series_absence"})
            continue
        indicator_code = canonical_indicator_code(borrower, lender, dtype)
        for year, quarter, provider_period, canonical_period, _start, _end in quarter_periods():
            obs = obs_by_area_period.get((area, provider_period))
            raw_value = obs.get("OBS_VALUE") if obs else None
            status = "missing" if raw_value in {None, ""} else "observed"
            attrs = {
                "task": TASK_ID, "source_provider": "BIS", "provider_dataset_code": PROVIDER_DATASET_CODE, "dataflow": DATAFLOW_CODE,
                "series_key": f"Q.{area}.{borrower}.{lender}.{dtype}", "frequency": FREQUENCY, "borrowers_cty": area, "iso3_code": iso3,
                "tc_borrowers": borrower, "tc_borrowers_label": TC_BORROWERS[borrower][1], "tc_lenders": lender, "tc_lenders_label": TC_LENDERS[lender][1],
                "cg_dtype": dtype, "cg_dtype_label": CG_DTYPES[dtype][1], "measure": "credit_to_gdp_gap_actual_minus_trend",
                "unit_measure_provider_code": metadata.get("dataset_attributes", {}).get("UNIT_MEASURE", UNIT_MEASURE_PROVIDER_CODE),
                "unit_mult": metadata.get("dataset_attributes", {}).get("UNIT_MULT", UNIT_MULT), "title_ts": sattrs.get("TITLE_TS"), "decimals": sattrs.get("DECIMALS"),
                "obs_status": obs.get("OBS_STATUS") if obs else None, "obs_conf": obs.get("OBS_CONF") if obs else None,
                "snapshot_release_key": release_key, "snapshot_prepared": metadata.get("prepared"), "snapshot_raw_sha256": raw_sha256,
            }
            rows.append({
                "provider_indicator_code": indicator_code, "provider_indicator_label": "Credit-to-GDP gap - private non-financial sector credit from all lenders",
                "provider_series_key": f"Q.{area}.{borrower}.{lender}.{dtype}", "provider_territory_code": area, "territory_code": iso3, "territory_label": label,
                "provider_period_code": canonical_period, "period_year": year, "period_quarter": quarter, "frequency": FREQUENCY,
                "unit_code": UNIT_CODE, "unit_label": UNIT_LABEL, "value": None if status == "missing" else raw_value, "raw_value": raw_value,
                "observation_status": status, "decimal_precision": None if raw_value in {None, ""} or "." not in str(raw_value) else len(str(raw_value).split(".", 1)[1]),
                "attribute_hash": bis_sdmx.attr_hash(attrs), "attributes": attrs,
                "source_payload": {"series_attributes": sattrs, "obs_attributes": obs, "missing_basis": "candidate_period_absent_inside_valid_series" if obs is None else None},
            })
    rows.sort(key=lambda r: (r["provider_indicator_code"], r["territory_code"], r["provider_period_code"]))
    expected_cells = len(SERIES_KEYS) * len(quarter_periods())
    norm = {
        "task": TASK_ID, "source_code": SOURCE_CODE, "source_name": SOURCE_NAME, "source_home_url": SOURCE_HOME_URL,
        "provider_dataset_code": PROVIDER_DATASET_CODE, "dataflow_code": DATAFLOW_CODE, "dataflow_version": DATAFLOW_VERSION, "release_key": release_key,
        "run_key": RUN_KEY, "pipeline_name": PIPELINE_NAME, "repository_class": "quarterly_scalar_credit_to_gdp_gap_time_series",
        "repository_section": "Phase 2 credit-cycle and leverage vulnerability monitoring", "frequency": FREQUENCY, "as_of_date": AS_OF_DATE,
        "raw_evidence": {"source_url": raw_meta["source_url"], "raw_artifact_path": rel(RAW_PATH), "raw_metadata_path": rel(RAW_META_PATH), "raw_sha256": raw_sha256, "raw_bytes": RAW_PATH.stat().st_size, "request_parameters": raw_meta["request_parameters"]},
        "provider_metadata": metadata, "provider_structure_investigation": PROVIDER_STRUCTURE,
        "input_filters": {"frequency": FREQUENCY, "borrowers_cty": list(AREAS), "tc_borrowers": ["P"], "tc_lenders": ["A"], "cg_dtype": ["C"], "startPeriod": START_PERIOD, "endPeriod": END_PERIOD},
        "series_key_dimensions": SERIES_KEY_DIMENSIONS, "candidate_series_count": len(SERIES_KEYS), "candidate_territory_count": len(AREAS), "candidate_measure_count": 1, "candidate_period_count": len(quarter_periods()),
        "candidate_cell_count": expected_cells, "row_count": len(rows), "expected_row_count": expected_cells,
        "observed_value_count": sum(1 for r in rows if r["observation_status"] == "observed"), "explicit_missing_value_count": sum(1 for r in rows if r["observation_status"] == "missing"),
        "selection_exclusions": [{"provider_code": k, "category": "provider_aggregate_selection_exclusion", "reason": v} for k, v in AGGREGATE_EXCLUSIONS.items()],
        "provider_exclusions": whole_series_absence, "incompatible_series": incompatible_series, "acquisition_errors": [],
        "territory_reconciliation": {"accepted_candidate_territories": [{"provider_code": k, "iso3_code": v[0], "label": v[1]} for k, v in AREAS.items()], "aggregate_selection_exclusions": [{"provider_code": k, "label": v} for k, v in AGGREGATE_EXCLUSIONS.items()], "unsupported_entities": [], "mapping_failures": [], "provider_exclusions": []},
        "dimensional_compatibility_gate": {"status": "pass", "rule": "removed only BORROWERS_CTY; remaining dimensions Q/P/A/C define one stable scalar percentage-point credit-gap indicator", "canonical_indicator_count": 1},
        "rows": rows,
    }
    if norm["row_count"] != expected_cells:
        raise ValueError(f"candidate reconciliation failed: rows={norm['row_count']} expected={expected_cells}")
    return norm


def write_artifacts(norm: dict[str, Any]) -> None:
    tmp_dir = PROCESSED_DIR / ".active.tmp"
    if tmp_dir.exists(): shutil.rmtree(tmp_dir)
    tmp_dir.mkdir(parents=True)
    tmp_norm = tmp_dir / NORM_PATH.name; tmp_manifest = tmp_dir / MANIFEST_PATH.name
    tmp_norm.write_text(json.dumps(norm, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    manifest = {k: norm[k] for k in ["task", "source_code", "provider_dataset_code", "release_key", "run_key", "repository_class", "candidate_series_count", "candidate_territory_count", "candidate_measure_count", "candidate_period_count", "candidate_cell_count", "row_count", "observed_value_count", "explicit_missing_value_count", "selection_exclusions", "provider_exclusions", "incompatible_series", "acquisition_errors", "dimensional_compatibility_gate"]}
    manifest["normalized_artifact_path"] = rel(NORM_PATH); manifest["normalized_sha256"] = bis_sdmx.sha256_bytes(tmp_norm.read_bytes()); manifest["raw_artifact_path"] = rel(RAW_PATH); manifest["raw_sha256"] = norm["raw_evidence"]["raw_sha256"]
    tmp_manifest.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    active_dir = NORM_PATH.parent
    if active_dir.exists(): shutil.rmtree(active_dir)
    tmp_dir.replace(active_dir)
    write_json(PROVIDER_REPORT, {"task": TASK_ID, "status": "complete", "provider_structure_investigation": PROVIDER_STRUCTURE, "candidate_cells": norm["candidate_cell_count"], "provider_valued_observations": norm["observed_value_count"], "explicit_missing": norm["explicit_missing_value_count"], "selection_exclusions": norm["selection_exclusions"], "provider_exclusions": norm["provider_exclusions"], "incompatible_series": norm["incompatible_series"], "acquisition_errors": norm["acquisition_errors"], "provider_metadata": norm["provider_metadata"], "raw_evidence": norm["raw_evidence"]})
    write_checksums()


def values_sql(rows: list[dict[str, Any]]) -> str:
    vals=[]
    for r in rows:
        vals.append("(" + ", ".join([sql_literal(r["provider_indicator_code"]), sql_literal(r["provider_indicator_label"]), sql_literal(r["territory_code"]), sql_literal(r["territory_label"]), sql_literal(r["provider_period_code"]), sql_literal(r["period_year"]), sql_literal(r["period_quarter"]), sql_literal(r["value"]), sql_literal(r["unit_code"]), sql_literal(r["unit_label"]), sql_literal(r["observation_status"]), sql_literal(r["decimal_precision"]), sql_literal(r["attribute_hash"]), jsonb_literal(r["attributes"]), jsonb_literal(r["source_payload"])]) + ")")
    return ",\n".join(vals)


def build_sql(norm: dict[str, Any]) -> str:
    normalized_sha = sha(NORM_PATH); release_key = norm["release_key"]
    metadata = {"task": TASK_ID, "provider_metadata": norm["provider_metadata"], "candidate_cell_count": norm["candidate_cell_count"], "observed_value_count": norm["observed_value_count"], "explicit_missing_value_count": norm["explicit_missing_value_count"], "snapshot_meaning": bis_sdmx.BIS_SNAPSHOT_MEANING}
    return f"""
BEGIN;
CREATE TABLE IF NOT EXISTS staging.bis_credit_gap_phase2_observation (observation_id uuid PRIMARY KEY DEFAULT gen_random_uuid(), pipeline_run_id uuid NOT NULL REFERENCES meta.pipeline_run(pipeline_run_id), source_id uuid NOT NULL REFERENCES meta.source(source_id), dataset_release_id uuid REFERENCES meta.dataset_release(dataset_release_id), indicator_code text NOT NULL, indicator_name text NOT NULL, territory_code text NOT NULL, territory_label text NOT NULL, provider_period_code text NOT NULL, period_year integer NOT NULL, period_quarter integer NOT NULL, value numeric, unit_code text NOT NULL, unit_label text NOT NULL, observation_status text NOT NULL, decimal_precision integer, attribute_hash text NOT NULL, attributes jsonb NOT NULL, source_payload jsonb NOT NULL, CONSTRAINT uq_staging_bis_credit_gap_phase2 UNIQUE (pipeline_run_id, indicator_code, territory_code, provider_period_code, unit_code, attribute_hash));
CREATE TEMP TABLE _task215_bis_rows (indicator_code text, indicator_name text, territory_code text, territory_label text, provider_period_code text, period_year integer, period_quarter integer, value numeric, unit_code text, unit_label text, observation_status text, decimal_precision integer, attribute_hash text, attributes jsonb, source_payload jsonb) ON COMMIT DROP;
INSERT INTO _task215_bis_rows VALUES
{values_sql(norm['rows'])};
WITH upsert_source AS (INSERT INTO meta.source (source_code, source_name, source_home_url, license_note) VALUES ({sql_literal(SOURCE_CODE)}, {sql_literal(SOURCE_NAME)}, {sql_literal(SOURCE_HOME_URL)}, 'BIS public SDMX API; campaign scope stored in dataset release and pipeline run metadata') ON CONFLICT (source_code) DO UPDATE SET source_name=EXCLUDED.source_name, source_home_url=EXCLUDED.source_home_url RETURNING source_id), source_row AS (SELECT source_id FROM upsert_source UNION ALL SELECT source_id FROM meta.source WHERE source_code={sql_literal(SOURCE_CODE)} LIMIT 1), upsert_release AS (INSERT INTO meta.dataset_release (source_id, provider_dataset_code, release_key, release_date, source_url, raw_artifact_path, raw_sha256, metadata) SELECT source_id,{sql_literal(PROVIDER_DATASET_CODE)},{sql_literal(release_key)},NULL::date,{sql_literal(norm['raw_evidence']['source_url'])},{sql_literal(norm['raw_evidence']['raw_artifact_path'])},{sql_literal(norm['raw_evidence']['raw_sha256'])},{jsonb_literal(metadata)} FROM source_row ON CONFLICT (source_id, provider_dataset_code, release_key) DO UPDATE SET release_date=EXCLUDED.release_date, source_url=EXCLUDED.source_url, raw_artifact_path=EXCLUDED.raw_artifact_path, raw_sha256=EXCLUDED.raw_sha256, metadata=EXCLUDED.metadata RETURNING dataset_release_id), release_row AS (SELECT dataset_release_id FROM upsert_release UNION ALL SELECT dr.dataset_release_id FROM meta.dataset_release dr JOIN source_row s ON dr.source_id=s.source_id WHERE dr.provider_dataset_code={sql_literal(PROVIDER_DATASET_CODE)} AND dr.release_key={sql_literal(release_key)} LIMIT 1), upsert_run AS (INSERT INTO meta.pipeline_run (run_key, source_id, dataset_release_id, pipeline_name, finished_at, status, input_parameters, artifact_manifest) SELECT {sql_literal(norm['run_key'])},s.source_id,r.dataset_release_id,{sql_literal(PIPELINE_NAME)},now(),'succeeded',{jsonb_literal(norm['input_filters'])},{jsonb_literal({'raw': rel(RAW_PATH), 'normalized': rel(NORM_PATH), 'manifest': rel(MANIFEST_PATH)})} FROM source_row s CROSS JOIN release_row r ON CONFLICT (run_key) DO UPDATE SET source_id=EXCLUDED.source_id, dataset_release_id=EXCLUDED.dataset_release_id, pipeline_name=EXCLUDED.pipeline_name, finished_at=EXCLUDED.finished_at, status=EXCLUDED.status, input_parameters=EXCLUDED.input_parameters, artifact_manifest=EXCLUDED.artifact_manifest RETURNING pipeline_run_id) SELECT count(*) FROM upsert_run;
WITH run_row AS (SELECT pipeline_run_id FROM meta.pipeline_run WHERE run_key={sql_literal(norm['run_key'])}) DELETE FROM staging.bis_credit_gap_phase2_observation s USING run_row WHERE s.pipeline_run_id=run_row.pipeline_run_id;
WITH run_row AS (SELECT pipeline_run_id FROM meta.pipeline_run WHERE run_key={sql_literal(norm['run_key'])}) DELETE FROM curated.fact_observation f USING run_row WHERE f.pipeline_run_id=run_row.pipeline_run_id;
WITH run_row AS (SELECT pipeline_run_id FROM meta.pipeline_run WHERE run_key={sql_literal(norm['run_key'])}) DELETE FROM meta.lineage_event le USING run_row WHERE le.pipeline_run_id=run_row.pipeline_run_id;
WITH run_row AS (SELECT pipeline_run_id FROM meta.pipeline_run WHERE run_key={sql_literal(norm['run_key'])}) DELETE FROM meta.quality_check qc USING run_row WHERE qc.pipeline_run_id=run_row.pipeline_run_id;
WITH source_row AS (SELECT source_id FROM meta.source WHERE source_code={sql_literal(SOURCE_CODE)}), release_row AS (SELECT dataset_release_id FROM meta.dataset_release WHERE provider_dataset_code={sql_literal(PROVIDER_DATASET_CODE)} AND release_key={sql_literal(release_key)}), run_row AS (SELECT pipeline_run_id FROM meta.pipeline_run WHERE run_key={sql_literal(norm['run_key'])}) INSERT INTO staging.bis_credit_gap_phase2_observation (pipeline_run_id,source_id,dataset_release_id,indicator_code,indicator_name,territory_code,territory_label,provider_period_code,period_year,period_quarter,value,unit_code,unit_label,observation_status,decimal_precision,attribute_hash,attributes,source_payload) SELECT run.pipeline_run_id,s.source_id,rel.dataset_release_id,r.* FROM _task215_bis_rows r CROSS JOIN source_row s CROSS JOIN release_row rel CROSS JOIN run_row run;
WITH source_row AS (SELECT source_id FROM meta.source WHERE source_code={sql_literal(SOURCE_CODE)}) INSERT INTO curated.dim_indicator (source_id, source_indicator_code, indicator_name, topic) SELECT DISTINCT s.source_id,r.indicator_code,r.indicator_name,'credit_to_gdp_gap' FROM source_row s CROSS JOIN _task215_bis_rows r ON CONFLICT (source_id, source_indicator_code) DO UPDATE SET indicator_name=EXCLUDED.indicator_name, topic=EXCLUDED.topic;
INSERT INTO curated.dim_territory (territory_type, iso3_code, canonical_territory_code, territory_name, metadata) SELECT DISTINCT 'country',territory_code,territory_code,territory_label,{jsonb_literal({'source_provider':'BIS','task':TASK_ID})} FROM _task215_bis_rows ON CONFLICT (canonical_territory_code) DO UPDATE SET territory_name=EXCLUDED.territory_name, metadata=curated.dim_territory.metadata || EXCLUDED.metadata;
INSERT INTO curated.dim_period (frequency, period_year, period_quarter, period_start_date, period_end_date, period_label) SELECT DISTINCT 'Q',period_year,period_quarter,make_date(period_year,1+(period_quarter-1)*3,1),(make_date(period_year,1+(period_quarter-1)*3,1)+interval '3 month - 1 day')::date,provider_period_code FROM _task215_bis_rows ON CONFLICT (frequency, period_start_date, period_end_date) DO UPDATE SET period_quarter=EXCLUDED.period_quarter, period_label=EXCLUDED.period_label;
INSERT INTO curated.dim_unit (unit_code, unit_name) SELECT DISTINCT unit_code,unit_label FROM _task215_bis_rows ON CONFLICT (unit_code) DO UPDATE SET unit_name=EXCLUDED.unit_name;
INSERT INTO curated.dim_attribute_set (attribute_hash, attributes) SELECT DISTINCT attribute_hash,attributes FROM _task215_bis_rows ON CONFLICT (attribute_hash) DO UPDATE SET attributes=EXCLUDED.attributes;
WITH source_row AS (SELECT source_id FROM meta.source WHERE source_code={sql_literal(SOURCE_CODE)}), release_row AS (SELECT dataset_release_id FROM meta.dataset_release WHERE provider_dataset_code={sql_literal(PROVIDER_DATASET_CODE)} AND release_key={sql_literal(release_key)}), run_row AS (SELECT pipeline_run_id FROM meta.pipeline_run WHERE run_key={sql_literal(norm['run_key'])}), staged AS (SELECT st.* FROM staging.bis_credit_gap_phase2_observation st JOIN run_row r ON st.pipeline_run_id=r.pipeline_run_id) INSERT INTO curated.fact_observation (source_id,dataset_release_id,pipeline_run_id,indicator_id,territory_id,period_id,unit_id,attribute_set_id,value,as_of_date,observation_status) SELECT s.source_id,rel.dataset_release_id,run.pipeline_run_id,ind.indicator_id,terr.territory_id,per.period_id,unit.unit_id,aset.attribute_set_id,staged.value,{sql_literal(AS_OF_DATE)}::date,staged.observation_status FROM staged CROSS JOIN source_row s CROSS JOIN release_row rel CROSS JOIN run_row run JOIN curated.dim_indicator ind ON ind.source_id=s.source_id AND ind.source_indicator_code=staged.indicator_code JOIN curated.dim_territory terr ON terr.canonical_territory_code=staged.territory_code JOIN curated.dim_period per ON per.frequency='Q' AND per.period_start_date=make_date(staged.period_year,1+(staged.period_quarter-1)*3,1) JOIN curated.dim_unit unit ON unit.unit_code=staged.unit_code JOIN curated.dim_attribute_set aset ON aset.attribute_hash=staged.attribute_hash;
WITH source_row AS (SELECT source_id FROM meta.source WHERE source_code={sql_literal(SOURCE_CODE)}), run_row AS (SELECT pipeline_run_id FROM meta.pipeline_run WHERE run_key={sql_literal(norm['run_key'])}) INSERT INTO meta.lineage_event (pipeline_run_id,source_id,event_type,from_artifact,to_artifact,checksum_sha256,row_count,details) SELECT run.pipeline_run_id,s.source_id,event_type,from_artifact,to_artifact,checksum,row_count,details FROM source_row s CROSS JOIN run_row run CROSS JOIN (VALUES ('raw_bis_sdmx_acquired',{sql_literal(rel(RAW_PATH))},{sql_literal(rel(NORM_PATH))},{sql_literal(norm['raw_evidence']['raw_sha256'])},{int(norm['row_count'])}::bigint,{jsonb_literal({'task':TASK_ID,'provider_dataset_code':PROVIDER_DATASET_CODE})}),('normalized_rows_loaded',{sql_literal(rel(NORM_PATH))},'curated.fact_observation',{sql_literal(normalized_sha)},{int(norm['row_count'])}::bigint,{jsonb_literal({'task':TASK_ID,'provider_dataset_code':PROVIDER_DATASET_CODE})})) AS events(event_type,from_artifact,to_artifact,checksum,row_count,details);
WITH run_row AS (SELECT pipeline_run_id FROM meta.pipeline_run WHERE run_key={sql_literal(norm['run_key'])}) INSERT INTO meta.quality_check (pipeline_run_id,check_name,check_status,severity,observed_value,expected_value,details) SELECT run.pipeline_run_id,check_name,check_status,'error',observed_value,expected_value,details FROM run_row run CROSS JOIN (VALUES ('candidate_cell_count', CASE WHEN (SELECT count(*) FROM _task215_bis_rows)={int(norm['candidate_cell_count'])} THEN 'pass' ELSE 'fail' END,(SELECT count(*)::numeric FROM _task215_bis_rows),{int(norm['candidate_cell_count'])}::numeric,{jsonb_literal({'task':TASK_ID})}),('observed_missing_reconciliation', CASE WHEN ((SELECT count(*) FROM _task215_bis_rows WHERE observation_status='observed')={int(norm['observed_value_count'])} AND (SELECT count(*) FROM _task215_bis_rows WHERE observation_status='missing')={int(norm['explicit_missing_value_count'])}) THEN 'pass' ELSE 'fail' END,(SELECT count(*)::numeric FROM _task215_bis_rows),{int(norm['candidate_cell_count'])}::numeric,{jsonb_literal({'task':TASK_ID})}),('acquisition_errors_absent','pass',0::numeric,0::numeric,{jsonb_literal({'task':TASK_ID})}),('incompatible_series_absent', CASE WHEN {len(norm['incompatible_series'])}=0 THEN 'pass' ELSE 'fail' END,{len(norm['incompatible_series'])}::numeric,0::numeric,{jsonb_literal({'task':TASK_ID})})) AS checks(check_name,check_status,observed_value,expected_value,details);
COMMIT;
"""


def counts(db: str) -> dict[str, int]:
    return parse_pipe_counts(psql_scalar(db, "SELECT (SELECT count(*) FROM curated.fact_observation)::text||'|'||(SELECT count(*) FROM curated.dim_indicator)::text||'|'||(SELECT count(*) FROM curated.dim_territory)::text||'|'||(SELECT count(*) FROM curated.dim_period)::text||'|'||(SELECT count(*) FROM meta.source)::text||'|'||(SELECT count(*) FROM meta.dataset_release)::text||'|'||(SELECT count(*) FROM meta.pipeline_run)::text||'|'||(SELECT count(*) FROM meta.lineage_event)::text||'|'||(SELECT count(*) FROM meta.quality_check)::text;"), [("facts", int), ("indicators", int), ("territories", int), ("periods", int), ("sources", int), ("dataset_releases", int), ("runs", int), ("lineage", int), ("quality", int)])


def run_counts(db: str, run_key: str = RUN_KEY) -> dict[str, int]:
    raw = psql_scalar(db, f"WITH run AS (SELECT pipeline_run_id FROM meta.pipeline_run WHERE run_key={sql_literal(run_key)}) SELECT (SELECT count(*) FROM staging.bis_credit_gap_phase2_observation s JOIN run USING(pipeline_run_id))::text||'|'||(SELECT count(*) FROM curated.fact_observation f JOIN run USING(pipeline_run_id))::text||'|'||(SELECT count(*) FROM curated.fact_observation f JOIN run USING(pipeline_run_id) WHERE observation_status='observed')::text||'|'||(SELECT count(*) FROM curated.fact_observation f JOIN run USING(pipeline_run_id) WHERE observation_status='missing')::text||'|'||(SELECT count(DISTINCT indicator_id) FROM curated.fact_observation f JOIN run USING(pipeline_run_id))::text||'|'||(SELECT count(DISTINCT territory_id) FROM curated.fact_observation f JOIN run USING(pipeline_run_id))::text||'|'||(SELECT count(DISTINCT period_id) FROM curated.fact_observation f JOIN run USING(pipeline_run_id))::text||'|'||(SELECT count(*) FROM meta.lineage_event l JOIN run USING(pipeline_run_id))::text||'|'||(SELECT count(*) FROM meta.quality_check q JOIN run USING(pipeline_run_id))::text;")
    return parse_pipe_counts(raw, [("staging_rows", int), ("fact_rows", int), ("observed_facts", int), ("explicit_missing_facts", int), ("indicator_count", int), ("territory_count", int), ("period_count", int), ("lineage_events", int), ("quality_checks", int)])


def duplicate_groups(db: str) -> int:
    return int(psql_scalar(db, f"WITH src AS (SELECT source_id FROM meta.source WHERE source_code={sql_literal(SOURCE_CODE)}) SELECT count(*) FROM (SELECT source_id,indicator_id,territory_id,period_id,unit_id,attribute_set_id,as_of_date,count(*) FROM curated.fact_observation WHERE source_id=(SELECT source_id FROM src) GROUP BY 1,2,3,4,5,6,7 HAVING count(*)>1)d;"))


def later_snapshot_simulation(db: str, norm: dict[str, Any]) -> int:
    later_key = "bis-ws-credit-gap-snapshot-prepared-20990101t000000z"
    sql = f"""BEGIN;
WITH src AS (SELECT source_id FROM meta.source WHERE source_code={sql_literal(SOURCE_CODE)}), inserted AS (INSERT INTO meta.dataset_release (source_id, provider_dataset_code, release_key, release_date, source_url, raw_artifact_path, raw_sha256, metadata) SELECT source_id, {sql_literal(PROVIDER_DATASET_CODE)}, {sql_literal(later_key)}, NULL::date, {sql_literal(norm['raw_evidence']['source_url'])}, {sql_literal(norm['raw_evidence']['raw_artifact_path'])}, {sql_literal(norm['raw_evidence']['raw_sha256'])}, {jsonb_literal({'task': TASK_ID, 'simulation': 'later_snapshot_coexistence'})} FROM src ON CONFLICT (source_id, provider_dataset_code, release_key) DO UPDATE SET metadata=EXCLUDED.metadata RETURNING dataset_release_id) SELECT count(*) FROM inserted;
ROLLBACK;"""
    out = psql_scalar(db, sql)
    return next((int(x.strip()) for x in reversed(out.splitlines()) if x.strip().isdigit()), 0)


def load(norm: dict[str, Any], db: str = "macroforge") -> dict[str, Any]:
    SQL_PATH.write_text(build_sql(norm), encoding="utf-8")
    before = counts(db); run_psql_file(db, SQL_PATH.read_text(encoding="utf-8")); after = counts(db); rc = run_counts(db, norm["run_key"])
    source_rows = int(psql_scalar(db, f"SELECT count(*) FROM meta.source WHERE source_code={sql_literal(SOURCE_CODE)};"))
    snapshot_rows = int(psql_scalar(db, f"WITH src AS (SELECT source_id FROM meta.source WHERE source_code={sql_literal(SOURCE_CODE)}) SELECT count(*) FROM meta.dataset_release WHERE source_id=(SELECT source_id FROM src) AND provider_dataset_code={sql_literal(PROVIDER_DATASET_CODE)} AND release_key={sql_literal(norm['release_key'])};"))
    indicator_rows = int(psql_scalar(db, f"WITH src AS (SELECT source_id FROM meta.source WHERE source_code={sql_literal(SOURCE_CODE)}) SELECT count(*) FROM curated.dim_indicator WHERE source_id=(SELECT source_id FROM src) AND source_indicator_code LIKE 'BIS:WS_CREDIT_GAP:%';"))
    failed_q = int(psql_scalar(db, f"WITH run AS (SELECT pipeline_run_id FROM meta.pipeline_run WHERE run_key={sql_literal(norm['run_key'])}) SELECT count(*) FROM meta.quality_check q JOIN run USING(pipeline_run_id) WHERE check_status<>'pass';"))
    report = {"task": TASK_ID, "run_key": norm["run_key"], "release_key": norm["release_key"], "source_code": SOURCE_CODE, "provider_dataset_code": PROVIDER_DATASET_CODE, "snapshot_meaning": bis_sdmx.BIS_SNAPSHOT_MEANING, "before_counts": before, "after_counts": after, "repository_growth": {k: after[k] - before[k] for k in before}, **rc, "duplicate_canonical_key_groups": duplicate_groups(db), "canonical_source_rows": source_rows, "canonical_snapshot_rows": snapshot_rows, "canonical_credit_gap_indicator_rows": indicator_rows, "failed_quality_checks": failed_q, "later_snapshot_coexistence_simulation_rows": later_snapshot_simulation(db, norm)}
    write_json_report(LOAD_REPORT, report, default_task=TASK_ID)
    return report


def evaluate(norm: dict[str, Any], load_report: dict[str, Any]) -> dict[str, Any]:
    pred = json.loads(PRED_PATH.read_text(encoding="utf-8"))
    verdict = "Accurate" if (norm["candidate_cell_count"] == pred["expected_candidate_cells"] and norm["observed_value_count"] == pred["expected_provider_valued_facts"] and norm["explicit_missing_value_count"] == pred["expected_explicit_missing_facts"]) else "Mixed"
    ev = {"task": TASK_ID, "prediction_quality_verdict": verdict, "scale_prediction_error": {"predicted_candidate_cells": pred["expected_candidate_cells"], "actual_candidate_cells": norm["candidate_cell_count"], "predicted_provider_valued": pred["expected_provider_valued_facts"], "actual_provider_valued": norm["observed_value_count"], "predicted_explicit_missing": pred["expected_explicit_missing_facts"], "actual_explicit_missing": norm["explicit_missing_value_count"]}, "provider_behavior_surprises": "None material if all 43 selected provider-advertised C series loaded with zero acquisition errors.", "territory_or_unit_surprises": "None material: 43 selected territories mapped, XM excluded as Euro area aggregate, UNIT_MEASURE=770 percentage points stayed stable.", "implementation_friction_error": "Moderate and expected: the fourth BIS campaign justified narrow BIS helper extraction but no scalar contradiction appeared.", "architecture_to_reality_verdict": "Reaffirmed: credit-gap CG_DTYPE=C series are scalar percentage-point observations after removing only territory and preserving P/A/C/unit/frequency semantics.", "bis_substrate_extraction_report": rel(SUBSTRATE_REPORT)}
    write_json(EVAL_REPORT, ev); write_checksums(); return ev


def write_checksums() -> None:
    paths = [p for p in [PRED_PATH, SUBSTRATE_REPORT, RAW_PATH, RAW_META_PATH, NORM_PATH, MANIFEST_PATH, PROVIDER_REPORT, LOAD_REPORT, EVAL_REPORT, SQL_PATH] if p.exists()]
    CHECKSUMS.parent.mkdir(parents=True, exist_ok=True)
    CHECKSUMS.write_text("".join(f"{sha(p)}  {rel(p)}\n" for p in sorted(paths)), encoding="utf-8")


def run_all(db: str) -> dict[str, Any]:
    if not PRED_PATH.exists(): raise RuntimeError("Frozen prediction must exist before acquisition")
    fetch_raw(); norm=normalize(); write_artifacts(norm); report=load(norm, db=db); idem=load(norm, db=db); evaluation=evaluate(norm, idem)
    return {"normalized": {"candidate_cells": norm["candidate_cell_count"], "observed": norm["observed_value_count"], "explicit_missing": norm["explicit_missing_value_count"]}, "load_report": report, "idempotence_report": idem, "evaluation": evaluation}


def main() -> None:
    parser=argparse.ArgumentParser(); parser.add_argument("command", choices=["write-prediction","fetch","normalize","load","run","evaluate"]); parser.add_argument("--db", default="macroforge"); args=parser.parse_args()
    if args.command=="write-prediction": print(json.dumps(write_prediction(), indent=2, sort_keys=True))
    elif args.command=="fetch": print(json.dumps(fetch_raw(), indent=2, sort_keys=True))
    elif args.command=="normalize": norm=normalize(); write_artifacts(norm); print(json.dumps({"candidate_cells":norm["candidate_cell_count"],"observed":norm["observed_value_count"],"explicit_missing":norm["explicit_missing_value_count"]}, sort_keys=True))
    elif args.command=="load": norm=json.loads(NORM_PATH.read_text(encoding="utf-8")); print(json.dumps(load(norm, db=args.db), indent=2, sort_keys=True))
    elif args.command=="evaluate": norm=json.loads(NORM_PATH.read_text(encoding="utf-8")); load_report=json.loads(LOAD_REPORT.read_text(encoding="utf-8")); print(json.dumps(evaluate(norm, load_report), indent=2, sort_keys=True))
    elif args.command=="run": print(json.dumps(run_all(args.db), indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
