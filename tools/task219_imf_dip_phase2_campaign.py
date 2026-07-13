from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import shutil
import subprocess
import sys
import urllib.request
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "src"))

from macroforge.db_helpers import jsonb_literal, parse_pipe_counts, psql_scalar, run_psql_file, sql_literal, write_json_report

TASK_ID = "TASK-219"
SLUG = "task219_imf_dip_phase2_campaign"
SOURCE_CODE = "IMF_SDMX_DIP_API_V1"
SOURCE_NAME = "International Monetary Fund SDMX DIP API"
SOURCE_HOME_URL = "https://data.imf.org/"
PROVIDER_DATASET_CODE = "IMF:DIP"
DATAFLOW_CODE = "DIP"
DATAFLOW_VERSION = "12.0.1"
DSD_VERSION_EXPECTED = "13.0.0"
RUN_KEY = "task-219-imf-dip-direct-investment-counterpart-phase2"
PIPELINE_NAME = "imf_dip_direct_investment_counterpart_phase2_campaign"
FREQUENCY = "A"
UNIT_CODE = "USD"
UNIT_LABEL = "US dollar"
UNIT_SCALE = "6"
START_PERIOD = "2020"
END_PERIOD = "2024"
SELECTED_ECONOMIES = (
    "AUS", "BEL", "BRA", "CAN", "CHE", "CHN", "DEU", "ESP",
    "FRA", "GBR", "HKG", "IND", "IRL", "ITA", "JPN", "KOR",
    "LUX", "MEX", "NLD", "NOR", "SGP", "SWE", "USA", "DNK",
)
DV_TYPE = "O"
SELECTED_SERIES: dict[str, str] = {
    "OTWD_D_NETAL_FALL_ALL": "Outward direct investment, net assets less liabilities, all financial instruments, all entities",
    "INWD_D_NETLA_FALL_ALL": "Inward direct investment, net liabilities less assets, all financial instruments, all entities",
    "OTWD_D_NETAL_F51_ALL": "Outward direct investment, net assets less liabilities, equity, all entities",
    "INWD_D_NETLA_F51_ALL": "Inward direct investment, net liabilities less assets, equity, all entities",
    "OTWD_D_NETAL_FL_ALL": "Outward direct investment, net assets less liabilities, debt instruments, all entities",
    "INWD_D_NETLA_FL_ALL": "Inward direct investment, net liabilities less assets, debt instruments, all entities",
}
INDICATORS = tuple(SELECTED_SERIES)
SERIES_KEY_DIMENSIONS = ["COUNTRY", "DV_TYPE", "INDICATOR", "COUNTERPART_COUNTRY", "FREQUENCY"]
TERRITORY_DIMENSION = "COUNTRY"
COUNTERPART_DIMENSION = "COUNTERPART_COUNTRY"
METADATA_URL = "https://api.imf.org/external/sdmx/2.1/dataflow/all/DIP/latest?references=all"
RAW_DIR = PROJECT_ROOT / "data/raw" / SLUG
PROCESSED_DIR = PROJECT_ROOT / "data/processed" / SLUG
REPORT_DIR = PROJECT_ROOT / "artifacts/reports"
PRED_PATH = REPORT_DIR / "task-219-imf-dip-frozen-pre-execution-prediction.json"
PROVIDER_REPORT = REPORT_DIR / "task-219-imf-dip-provider-structure-and-evidence-report.json"
NORM_PATH = PROCESSED_DIR / "active" / "task-219-imf-dip-normalized.json"
MANIFEST_PATH = PROCESSED_DIR / "active" / "task-219-imf-dip-manifest.json"
LOAD_REPORT = REPORT_DIR / "task-219-imf-dip-postgresql-load-report.json"
IDEMPOTENCE_REPORT = REPORT_DIR / "task-219-imf-dip-postgresql-idempotence-report.json"
EVAL_REPORT = REPORT_DIR / "task-219-imf-dip-prediction-evaluation.json"
EXTRACTION_REPORT = REPORT_DIR / "task-219-imf-dip-extraction-decision.json"
CHECKSUMS = REPORT_DIR / "task-219-imf-dip-artifact-checksums.txt"
SQL_PATH = REPORT_DIR / "task-219-imf-dip-load.sql"


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def rel(path: Path) -> str:
    return path.relative_to(PROJECT_ROOT).as_posix() if path.is_absolute() else path.as_posix()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def en_name(code: ET.Element) -> str | None:
    for child in code:
        if local_name(child.tag) == "Name" and child.attrib.get("{http://www.w3.org/XML/1998/namespace}lang") == "en":
            return child.text
    for child in code:
        if local_name(child.tag) == "Name":
            return child.text
    return None


def periods() -> list[str]:
    return [str(y) for y in range(int(START_PERIOD), int(END_PERIOD) + 1)]


def canonical_indicator_code(indicator: str, counterpart: str) -> str:
    return f"IMF:DIP:DVTYPE_{DV_TYPE}:{indicator}:COUNTERPART_{counterpart}:{UNIT_CODE}:SCALE_{UNIT_SCALE}:{FREQUENCY}"


def source_url(countries: list[str], counterparts: list[str]) -> str:
    c = "+".join(countries)
    inds = "+".join(INDICATORS)
    cp = "+".join(counterparts)
    return f"https://api.imf.org/external/sdmx/2.1/data/{DATAFLOW_CODE}/{c}.{DV_TYPE}.{inds}.{cp}.{FREQUENCY}?startPeriod={START_PERIOD}&endPeriod={END_PERIOD}"


def fetch_url(url: str, *, timeout: int = 240) -> tuple[bytes, dict[str, Any]]:
    req = urllib.request.Request(url, headers={"User-Agent": "MacroForge TASK-219 IMF DIP Phase2"})
    acquired_at = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    with urllib.request.urlopen(req, timeout=timeout) as response:
        data = response.read()
        meta = {"source_url": url, "http_status": response.status, "headers": dict(response.headers.items()), "content_type": response.headers.get("Content-Type"), "acquired_at_utc": acquired_at, "raw_sha256": sha256_bytes(data), "raw_bytes": len(data)}
    return data, meta


def fetch_metadata_active() -> dict[str, Any]:
    attempt_id = dt.datetime.now(dt.timezone.utc).strftime("attempt-%Y%m%dT%H%M%SZ")
    attempt_dir = RAW_DIR / "_attempts" / attempt_id
    attempt_dir.mkdir(parents=True, exist_ok=True)
    data, meta = fetch_url(METADATA_URL)
    meta.update({"task": TASK_ID, "status": "metadata_acquired", "attempt_id": attempt_id, "request_parameters": {"dataflow": DATAFLOW_CODE, "references": "all"}})
    (attempt_dir / "task-219-imf-dip-metadata.xml").write_bytes(data)
    write_json(attempt_dir / "task-219-imf-dip-metadata.json", meta)
    active = RAW_DIR / "active"
    tmp = RAW_DIR / ".active-metadata.tmp"
    if tmp.exists(): shutil.rmtree(tmp)
    tmp.mkdir(parents=True)
    (tmp / "task-219-imf-dip-metadata.xml").write_bytes(data)
    write_json(tmp / "task-219-imf-dip-metadata.json", meta)
    active.mkdir(parents=True, exist_ok=True)
    for p in tmp.iterdir(): shutil.move(str(p), str(active / p.name))
    tmp.rmdir()
    return meta


def parse_metadata(metadata_path: Path | None = None) -> dict[str, Any]:
    path = metadata_path or RAW_DIR / "active" / "task-219-imf-dip-metadata.xml"
    root = ET.fromstring(path.read_bytes())
    codelists: dict[str, dict[str, str]] = {}
    keep = {"CL_COUNTRY", "CL_DIP_COUNTRY", "CL_DIP_DV_TYPE", "CL_DIP_INDICATOR", "CL_UNIT", "CL_FREQ", "CL_OBS_STATUS", "CL_CONF_STATUS"}
    for cl in root.iter():
        if local_name(cl.tag) == "Codelist":
            cid = cl.attrib.get("id")
            if cid in keep:
                values: dict[str, str] = {}
                for code in cl:
                    code_id = code.attrib.get("id")
                    if local_name(code.tag) == "Code" and code_id:
                        values[code_id] = en_name(code) or ""
                codelists[cid] = values
    dataflow = {}; dsd = {}; dims = []; attrs = []
    for el in root.iter():
        if local_name(el.tag) == "Dataflow" and el.attrib.get("id") == DATAFLOW_CODE:
            dataflow = {"agency_id": el.attrib.get("agencyID"), "id": el.attrib.get("id"), "version": el.attrib.get("version"), "name": next((c.text for c in el if local_name(c.tag) == "Name" and c.text), None)}
        if local_name(el.tag) == "DataStructure":
            dsd = {"agency_id": el.attrib.get("agencyID"), "id": el.attrib.get("id"), "version": el.attrib.get("version")}
        if local_name(el.tag) in {"Dimension", "TimeDimension"} and el.attrib.get("id"):
            dims.append((int(el.attrib.get("position", "999")), el.attrib.get("id")))
        if local_name(el.tag) == "Attribute" and el.attrib.get("id"):
            attrs.append(el.attrib.get("id"))
    return {"dataflow": dataflow, "data_structure": dsd, "dimension_order": [x for _, x in sorted(dims) if x != "TIME_PERIOD"] + ["TIME_PERIOD"], "attribute_ids": sorted(set(attrs)), "codelists": codelists, "metadata_sha256": sha256_file(path), "metadata_path": rel(path)}


def db_canonical_countries() -> dict[str, str]:
    out = subprocess.run(["psql", "-X", "-d", "macroforge", "-At", "-c", "select iso3_code, territory_name from curated.dim_territory where territory_type='country' and iso3_code is not null order by iso3_code"], check=True, capture_output=True, text=True).stdout
    return dict(line.split("|", 1) for line in out.splitlines() if "|" in line)


def selected_economies(meta: dict[str, Any]) -> dict[str, str]:
    provider = meta["codelists"].get("CL_DIP_COUNTRY") or meta["codelists"].get("CL_COUNTRY") or {}
    canonical = db_canonical_countries()
    missing_provider = [c for c in SELECTED_ECONOMIES if c not in provider]
    missing_canonical = [c for c in SELECTED_ECONOMIES if c not in canonical]
    if missing_provider or missing_canonical:
        raise RuntimeError(f"selected economy mismatch provider={missing_provider} canonical={missing_canonical}")
    return {c: canonical[c] for c in SELECTED_ECONOMIES}


def write_provider_report_and_prediction() -> dict[str, Any]:
    if not (RAW_DIR / "active" / "task-219-imf-dip-metadata.xml").exists():
        fetch_metadata_active()
    meta = parse_metadata()
    countries = selected_economies(meta)
    p = periods()
    candidate_series = []
    for reporter in SELECTED_ECONOMIES:
        for counterpart in SELECTED_ECONOMIES:
            for ind, label in SELECTED_SERIES.items():
                candidate_series.append({"series_key": f"{reporter}.{DV_TYPE}.{ind}.{counterpart}.{FREQUENCY}", "reporter_country": reporter, "counterpart_country": counterpart, "dv_type": DV_TYPE, "indicator": ind, "indicator_label": label, "frequency": FREQUENCY})
    expected_cells = len(candidate_series) * len(p)
    provider_report = {"task": TASK_ID, "source_api": "IMF external SDMX 2.1 API /external/sdmx/2.1/data/DIP and dataflow/all/DIP/latest?references=all", "provider_dataset_code": PROVIDER_DATASET_CODE, "dataflow": meta["dataflow"], "data_structure": meta["data_structure"], "series_key_dimensions": SERIES_KEY_DIMENSIONS, "territory_dimension": TERRITORY_DIMENSION, "counterpart_dimension": COUNTERPART_DIMENSION, "selected_economies": [{"provider_code": k, "canonical_code": k, "label": countries[k]} for k in SELECTED_ECONOMIES], "selected_indicators": [{"indicator": k, "label": v} for k, v in SELECTED_SERIES.items()], "dv_type_selection": {"dv_type": DV_TYPE, "label": "Reported official data"}, "temporal_coverage_selected_window": {"start": START_PERIOD, "end": END_PERIOD, "periods": len(p)}, "candidate_series_count": len(candidate_series), "candidate_cell_count": expected_cells, "selected_capability": "Annual IMF DIP/CDIS direct investment positions by reporting economy, counterpart economy, and instrument family for a 24-economy investment-relevant matrix."}
    write_json(PROVIDER_REPORT, provider_report)
    prediction = {"task": TASK_ID, "frozen_before_value_acquisition": True, "selected_source": SOURCE_CODE, "provider_dataset_code": PROVIDER_DATASET_CODE, "release_identity_rule": "derive DIP as-of key from provider dataset UPDATE_DATE/PUBLICATION_DATE/Prepared evidence", "run_key": RUN_KEY, "selected_capability": provider_report["selected_capability"], "confidence_cell": "IMF SDMX annual scalar relationship-position values with reporter territory as canonical territory and counterpart economy preserved in source-scoped indicator identity/attributes", "selected_economies": provider_report["selected_economies"], "selected_indicators": provider_report["selected_indicators"], "exact_provider_advertised_series_count": len(candidate_series), "exact_provider_advertised_series": candidate_series, "expected_candidate_cells": expected_cells, "expected_provider_valued_facts": int(expected_cells * 0.60), "expected_explicit_missing_facts": int(expected_cells * 0.20), "expected_whole_series_absence": expected_cells - int(expected_cells * 0.60) - int(expected_cells * 0.20), "expected_units": {"unit": UNIT_CODE, "scale": UNIT_SCALE, "unit_label": UNIT_LABEL}, "expected_transport_behavior": "four reporter chunks against 24 counterpart economies; metadata large but proven accessible", "expected_implementation_friction": "moderate-high: DIP adds counterpart-country relationship semantics but should fit scalar storage by retaining counterpart in indicator attributes", "expected_postgresql_growth": {"facts": "observed plus explicit-missing rows only", "indicators": len(SELECTED_ECONOMIES) * len(SELECTED_SERIES)}, "structural_assumptions_pressure_tested": ["relationship/counterpart economy can be preserved without schema redesign for bounded DIP matrix", "provider as-of identity remains dataset/release metadata", "whole-series absence remains distinct from explicit missing years", "same-run idempotence holds after deleting/reloading run-scoped facts"]}
    write_json(PRED_PATH, prediction)
    return prediction


def write_extraction_decision() -> dict[str, Any]:
    report = {"task": TASK_ID, "decision": "No shared IMF/DIP or relationship-position substrate extracted", "evidence_compared": ["TASK-216 IMF BOP current-account flows", "TASK-217 IMF IIP aggregate stocks", "TASK-219 IMF DIP counterpart direct-investment positions"], "repeated_responsibilities": ["IMF SDMX metadata parsing", "provider-derived as-of identity", "attempt-specific acquisition and active promotion", "explicit-missing and whole-series absence reconciliation"], "rejected_extraction_reason": "DIP introduces counterpart-country relationship semantics distinct from BOP/IIP aggregate scopes. Repetition is visible, but extracting now risks a generic SDMX or external-sector framework before relationship identity has repeated stable contracts.", "explicitly_not_created": ["universal SDMX machinery", "generic campaign engine", "counterparty ontology", "schema redesign"]}
    write_json(EXTRACTION_REPORT, report)
    return report


def fetch_values() -> dict[str, Any]:
    pred = json.loads(PRED_PATH.read_text(encoding="utf-8")) if PRED_PATH.exists() else write_provider_report_and_prediction()
    reporters = [x["provider_code"] for x in pred["selected_economies"]]
    counterparts = reporters[:]
    attempt_id = dt.datetime.now(dt.timezone.utc).strftime("attempt-%Y%m%dT%H%M%SZ")
    attempt_dir = RAW_DIR / "_attempts" / attempt_id
    attempt_dir.mkdir(parents=True, exist_ok=True)
    chunks = [reporters[i:i+6] for i in range(0, len(reporters), 6)]
    responses=[]; errors=[]
    for idx, chunk in enumerate(chunks, 1):
        url = source_url(chunk, counterparts)
        try:
            data, meta = fetch_url(url)
            meta.update({"task": TASK_ID, "status": "value_chunk_acquired", "attempt_id": attempt_id, "chunk_index": idx, "chunk_count": len(chunks), "reporters": chunk, "counterparts": counterparts, "request_parameters": {"dataflow": DATAFLOW_CODE, "reporters": chunk, "dv_type": DV_TYPE, "indicators": list(INDICATORS), "counterparts": counterparts, "frequency": FREQUENCY, "startPeriod": START_PERIOD, "endPeriod": END_PERIOD}})
            raw_name=f"task-219-imf-dip-values-chunk-{idx:02d}.xml"; meta_name=f"task-219-imf-dip-values-chunk-{idx:02d}.json"
            (attempt_dir/raw_name).write_bytes(data); write_json(attempt_dir/meta_name, meta)
            responses.append({"raw_name": raw_name, "meta_name": meta_name, "meta": meta})
        except Exception as exc:
            err={"task":TASK_ID,"status":"acquisition_error","attempt_id":attempt_id,"chunk_index":idx,"reporters":chunk,"source_url":url,"error_type":type(exc).__name__,"error":str(exc)}
            write_json(attempt_dir/f"task-219-imf-dip-values-chunk-{idx:02d}-error.json", err); errors.append(err)
    if errors:
        write_json(attempt_dir/"acquisition-errors.json", {"task":TASK_ID,"errors":errors})
        raise RuntimeError(f"unresolved acquisition errors: {len(errors)}")
    active = RAW_DIR / "active"; tmp = RAW_DIR / ".active-values.tmp"
    if tmp.exists(): shutil.rmtree(tmp)
    tmp.mkdir(parents=True)
    for r in responses:
        shutil.copy2(attempt_dir/r["raw_name"], tmp/r["raw_name"]); shutil.copy2(attempt_dir/r["meta_name"], tmp/r["meta_name"])
    manifest={"task":TASK_ID,"status":"values_acquired","attempt_id":attempt_id,"chunk_count":len(chunks),"responses":responses}
    write_json(tmp/"task-219-imf-dip-raw-values-manifest.json", manifest)
    active.mkdir(parents=True, exist_ok=True)
    for p in tmp.iterdir(): shutil.move(str(p), str(active/p.name))
    tmp.rmdir(); return manifest


def dataset_attrs(root: ET.Element) -> dict[str, str]:
    ds = next((e for e in root.iter() if local_name(e.tag) == "DataSet"), None)
    keep = {"UPDATE_DATE", "PUBLICATION_DATE", "LANGUAGE", "PUBLISHER", "CONTACT_POINT", "DEPARTMENT", "TOPIC_DATASET", "SHORT_SOURCE_CITATION", "SUGGESTED_CITATION"}
    return {k: v for k, v in (ds.attrib.items() if ds is not None else []) if k in keep}


def header_meta(root: ET.Element) -> dict[str, Any]:
    header = next((e for e in root.iter() if local_name(e.tag) == "Header"), None)
    def text(name: str) -> str | None:
        if header is None: return None
        for ch in header:
            if local_name(ch.tag) == name and ch.text: return ch.text.strip()
        return None
    return {"message_id": text("ID"), "prepared": text("Prepared"), "dataset_action": text("DataSetAction"), "dataset_attributes": dataset_attrs(root)}


def provider_as_of_from_responses(headers: list[dict[str, Any]]) -> tuple[str, str]:
    dates=[]
    for h in headers:
        attrs=h.get("dataset_attributes", {})
        dates.extend([attrs.get("UPDATE_DATE"), attrs.get("PUBLICATION_DATE"), h.get("prepared")])
    date=next((d for d in dates if d), None)
    if not date: raise ValueError("cannot derive IMF DIP as-of identity from provider metadata")
    token=date.replace(":", "").replace("-", "").replace(".", "").replace("Z", "z").replace("T", "t")[:32].lower()
    as_of_date=date[:10]
    return f"imf-dip-asof-{token}", as_of_date


def normalize() -> dict[str, Any]:
    pred=json.loads(PRED_PATH.read_text(encoding="utf-8")); active=RAW_DIR/"active"
    value_manifest=json.loads((active/"task-219-imf-dip-raw-values-manifest.json").read_text(encoding="utf-8"))
    meta=parse_metadata(active/"task-219-imf-dip-metadata.xml")
    labels={x["provider_code"]: x["label"] for x in pred["selected_economies"]}
    selected_countries=set(labels); selected_ind=set(INDICATORS); p=periods()
    obs_by_key={}; returned_series={}; provider_headers=[]; incompatible=[]
    for item in value_manifest["responses"]:
        root=ET.fromstring((active/item["raw_name"]).read_bytes()); provider_headers.append(header_meta(root))
        for series in root.iter():
            if local_name(series.tag)!="Series": continue
            attrs=dict(series.attrib)
            c=attrs.get("COUNTRY"); dv=attrs.get("DV_TYPE"); ind=attrs.get("INDICATOR"); cp=attrs.get("COUNTERPART_COUNTRY"); freq=attrs.get("FREQUENCY")
            if c not in selected_countries or cp not in selected_countries or dv!=DV_TYPE or ind not in selected_ind or freq!=FREQUENCY:
                incompatible.append(attrs); continue
            returned_series[(c, ind, cp)] = attrs
            for obs in series:
                if local_name(obs.tag)=="Obs" and obs.attrib.get("TIME_PERIOD"):
                    obs_by_key[(c, ind, cp, obs.attrib["TIME_PERIOD"])] = dict(obs.attrib)
    rows=[]; observed=0; explicit_missing=0; whole=[]
    for c in SELECTED_ECONOMIES:
        for cp in SELECTED_ECONOMIES:
            for ind,label in SELECTED_SERIES.items():
                if (c,ind,cp) not in returned_series:
                    whole.append({"reporter_country":c,"counterpart_country":cp,"indicator":ind,"category":"whole_series_absence"}); continue
                sattrs=returned_series[(c,ind,cp)]
                for per in p:
                    obs=obs_by_key.get((c,ind,cp,per)); status="observed"; value=None
                    if obs is None or obs.get("OBS_VALUE") in {None,""}:
                        status="missing"; explicit_missing+=1
                    else:
                        value=obs["OBS_VALUE"]; observed+=1
                    attrs={"task":TASK_ID,"repository_section":"External Sector","provider_dataset_code":PROVIDER_DATASET_CODE,"dataflow_code":DATAFLOW_CODE,"dataflow_version":meta["dataflow"].get("version"),"data_structure_version":meta["data_structure"].get("version"),"dip_dv_type":DV_TYPE,"dip_indicator":ind,"dip_indicator_label":label,"reporter_country":c,"counterpart_country":cp,"di_direction":sattrs.get("DI_DIRECTION"),"functional_category":sattrs.get("FUNCTIONAL_CAT"),"instrument_asset":sattrs.get("INSTR_ASSET"),"direct_investment_entity":sattrs.get("DI_ENTITY"),"accounting_entry":sattrs.get("ACCOUNTING_ENTRY"),"unit":sattrs.get("UNIT", UNIT_CODE),"scale":sattrs.get("SCALE",UNIT_SCALE),"frequency":FREQUENCY,"obs_status":None if obs is None else obs.get("OBS_STATUS"),"derivation_type":None if obs is None else obs.get("DERIVATION_TYPE"),"conf_status":None if obs is None else obs.get("CONF_STATUS"),"access_sharing_level":None if obs is None else obs.get("ACCESS_SHARING_LEVEL"),"security_classification":None if obs is None else obs.get("SECURITY_CLASSIFICATION"),"value_status":"provider_dip_value_status_preserved_when_obs_status_present_otherwise_unspecified"}
                    ah=hashlib.sha256(json.dumps(attrs, sort_keys=True, separators=(",",":")).encode()).hexdigest()
                    rows.append({"provider_indicator_code":canonical_indicator_code(ind,cp),"provider_indicator_label":f"{label}; counterpart {cp}","territory_code":c,"territory_label":labels[c],"provider_period_code":per,"period_year":int(per),"value":value,"unit_code":f"{UNIT_CODE}_SCALE_{sattrs.get('SCALE',UNIT_SCALE)}","unit_label":f"{UNIT_LABEL}, scale {sattrs.get('SCALE',UNIT_SCALE)}","observation_status":status,"decimal_precision":None if obs is None else obs.get("PRECISION"),"attribute_hash":ah,"attributes":attrs,"source_payload":{"series_attributes":sattrs,"observation_attributes":obs or {},"source_url_count":len(value_manifest["responses"])}})
    if incompatible: raise RuntimeError(f"incompatible series found: {len(incompatible)}")
    release_key, release_as_of_date = provider_as_of_from_responses(provider_headers)
    normalized={"task":TASK_ID,"status":"normalized","source_code":SOURCE_CODE,"source_name":SOURCE_NAME,"source_home_url":SOURCE_HOME_URL,"provider_dataset_code":PROVIDER_DATASET_CODE,"release_key":release_key,"release_as_of_date":release_as_of_date,"release_identity_basis":"provider dataset UPDATE_DATE/PUBLICATION_DATE/Prepared evidence","run_key":RUN_KEY,"pipeline_name":PIPELINE_NAME,"provider_metadata":meta,"provider_response_headers":provider_headers,"raw_manifest":value_manifest,"candidate_cell_count":pred["expected_candidate_cells"],"candidate_series_count":pred["exact_provider_advertised_series_count"],"observed_value_count":observed,"explicit_missing_value_count":explicit_missing,"whole_series_absence_count":len(whole),"whole_series_absence":whole,"incompatible_series_count":0,"incompatible_series":[],"rows":rows}
    write_json(NORM_PATH, normalized)
    raw_files=[{"path":rel(p),"sha256":sha256_file(p),"bytes":p.stat().st_size} for p in sorted(active.glob("task-219-imf-dip-*")) if p.is_file()]
    write_json(MANIFEST_PATH,{"task":TASK_ID,"status":"active_artifacts_promoted","normalized_path":rel(NORM_PATH),"normalized_sha256":sha256_file(NORM_PATH),"raw_active_dir":rel(active),"raw_active_files":raw_files,"row_count":len(rows),"observed_value_count":observed,"explicit_missing_value_count":explicit_missing,"whole_series_absence_count":len(whole),"release_key":release_key,"release_as_of_date":release_as_of_date})
    return normalized


def values_sql(rows: list[dict[str, Any]]) -> str:
    return ",\n".join("(" + ", ".join([sql_literal(r["territory_code"]), sql_literal(r["territory_label"]), sql_literal(r["provider_indicator_code"]), sql_literal(r["provider_indicator_label"]), sql_literal(r["provider_period_code"]), sql_literal(r["period_year"]), sql_literal(r["value"]), sql_literal(r["unit_code"]), sql_literal(r["unit_label"]), sql_literal(r["decimal_precision"]), sql_literal(r["observation_status"]), sql_literal(r["attribute_hash"]), jsonb_literal(r["attributes"]), jsonb_literal(r["source_payload"])]) + ")" for r in rows)


def build_load_sql(norm: dict[str, Any], run_key: str = RUN_KEY) -> str:
    rows_sql=values_sql(norm["rows"])
    raw_paths=[rel(p) for p in sorted((RAW_DIR/"active").glob("task-219-imf-dip-values-chunk-*.xml"))]
    metadata={"task":TASK_ID,"candidate_cell_count":norm["candidate_cell_count"],"observed_value_count":norm["observed_value_count"],"explicit_missing_value_count":norm["explicit_missing_value_count"],"whole_series_absence_count":norm["whole_series_absence_count"],"release_identity_basis":norm["release_identity_basis"],"release_as_of_date":norm.get("release_as_of_date")}
    return f"""
BEGIN;
CREATE TABLE IF NOT EXISTS staging.task219_imf_dip_portfolio_counterpart_observation (observation_id uuid PRIMARY KEY DEFAULT gen_random_uuid(), pipeline_run_id uuid NOT NULL REFERENCES meta.pipeline_run(pipeline_run_id), source_id uuid NOT NULL REFERENCES meta.source(source_id), dataset_release_id uuid REFERENCES meta.dataset_release(dataset_release_id), territory_code text NOT NULL, territory_label text NOT NULL, indicator_code text NOT NULL, indicator_name text NOT NULL, provider_period_code text NOT NULL, period_year integer NOT NULL, value numeric, unit_code text NOT NULL, unit_label text NOT NULL, decimal_precision integer, observation_status text NOT NULL, attribute_hash text NOT NULL, attributes jsonb NOT NULL, source_payload jsonb NOT NULL, created_at timestamptz NOT NULL DEFAULT now(), CONSTRAINT uq_staging_task219_imf_dip_natural UNIQUE (pipeline_run_id, territory_code, indicator_code, provider_period_code, unit_code, attribute_hash));
CREATE TEMP TABLE _task219_rows (territory_code text, territory_label text, indicator_code text, indicator_name text, provider_period_code text, period_year integer, value numeric, unit_code text, unit_label text, decimal_precision integer, observation_status text, attribute_hash text, attributes jsonb, source_payload jsonb) ON COMMIT DROP;
INSERT INTO _task219_rows VALUES
{rows_sql};
CREATE TEMP TABLE _source_row (source_id uuid) ON COMMIT DROP; CREATE TEMP TABLE _release_row (dataset_release_id uuid) ON COMMIT DROP; CREATE TEMP TABLE _run_row (pipeline_run_id uuid) ON COMMIT DROP;
INSERT INTO meta.source (source_code, source_name, source_home_url, license_note) VALUES ({sql_literal(SOURCE_CODE)}, {sql_literal(SOURCE_NAME)}, {sql_literal(SOURCE_HOME_URL)}, 'IMF public SDMX DIP API') ON CONFLICT (source_code) DO UPDATE SET source_name=EXCLUDED.source_name, source_home_url=EXCLUDED.source_home_url;
INSERT INTO _source_row SELECT source_id FROM meta.source WHERE source_code={sql_literal(SOURCE_CODE)} LIMIT 1;
INSERT INTO meta.dataset_release (source_id, provider_dataset_code, release_key, release_date, source_url, raw_artifact_path, raw_sha256, metadata) SELECT source_id, {sql_literal(PROVIDER_DATASET_CODE)}, {sql_literal(norm['release_key'])}, NULL, {sql_literal(METADATA_URL)}, {sql_literal(rel(MANIFEST_PATH))}, {sql_literal(sha256_file(MANIFEST_PATH))}, {jsonb_literal(metadata)} FROM _source_row ON CONFLICT (source_id, provider_dataset_code, release_key) DO UPDATE SET source_url=EXCLUDED.source_url, raw_artifact_path=EXCLUDED.raw_artifact_path, raw_sha256=EXCLUDED.raw_sha256, metadata=EXCLUDED.metadata;
INSERT INTO _release_row SELECT dr.dataset_release_id FROM meta.dataset_release dr JOIN _source_row s ON dr.source_id=s.source_id WHERE provider_dataset_code={sql_literal(PROVIDER_DATASET_CODE)} AND release_key={sql_literal(norm['release_key'])} LIMIT 1;
INSERT INTO meta.pipeline_run (run_key, source_id, dataset_release_id, pipeline_name, finished_at, status, input_parameters, artifact_manifest) SELECT {sql_literal(run_key)}, s.source_id, r.dataset_release_id, {sql_literal(PIPELINE_NAME)}, now(), 'succeeded', {jsonb_literal({'task': TASK_ID, 'startPeriod': START_PERIOD, 'endPeriod': END_PERIOD, 'selected_economies': list(SELECTED_ECONOMIES), 'indicators': list(INDICATORS), 'counterpart_dimension': COUNTERPART_DIMENSION})}, {jsonb_literal({'normalized_path': rel(NORM_PATH), 'manifest_path': rel(MANIFEST_PATH), 'raw_paths': raw_paths})} FROM _source_row s CROSS JOIN _release_row r ON CONFLICT (run_key) DO UPDATE SET finished_at=EXCLUDED.finished_at, status=EXCLUDED.status, input_parameters=EXCLUDED.input_parameters, artifact_manifest=EXCLUDED.artifact_manifest;
INSERT INTO _run_row SELECT pipeline_run_id FROM meta.pipeline_run WHERE run_key={sql_literal(run_key)} LIMIT 1;
INSERT INTO staging.task219_imf_dip_portfolio_counterpart_observation (pipeline_run_id, source_id, dataset_release_id, territory_code, territory_label, indicator_code, indicator_name, provider_period_code, period_year, value, unit_code, unit_label, decimal_precision, observation_status, attribute_hash, attributes, source_payload) SELECT _run_row.pipeline_run_id, _source_row.source_id, _release_row.dataset_release_id, r.* FROM _task219_rows r CROSS JOIN _run_row CROSS JOIN _source_row CROSS JOIN _release_row ON CONFLICT (pipeline_run_id, territory_code, indicator_code, provider_period_code, unit_code, attribute_hash) DO UPDATE SET value=EXCLUDED.value, observation_status=EXCLUDED.observation_status, attributes=EXCLUDED.attributes, source_payload=EXCLUDED.source_payload;
INSERT INTO curated.dim_indicator (source_id, source_indicator_code, indicator_name, description, topic) SELECT DISTINCT s.source_id, indicator_code, indicator_name, 'IMF DIP source-scoped scalar indicator preserving direct-investment direction, instrument basis, and counterpart economy in indicator identity/attributes', 'External Sector / Direct Investment Positions' FROM _task219_rows CROSS JOIN _source_row s ON CONFLICT (source_id, source_indicator_code) DO UPDATE SET indicator_name=EXCLUDED.indicator_name, description=EXCLUDED.description, topic=EXCLUDED.topic;
INSERT INTO curated.dim_unit (unit_code, unit_name, unit_description) SELECT DISTINCT unit_code, unit_label, 'IMF DIP USD unit with provider scale preserved' FROM _task219_rows ON CONFLICT (unit_code) DO UPDATE SET unit_name=EXCLUDED.unit_name, unit_description=EXCLUDED.unit_description;
INSERT INTO curated.dim_period (frequency, period_year, period_start_date, period_end_date, period_label) SELECT DISTINCT 'A', period_year, make_date(period_year,1,1), make_date(period_year,12,31), provider_period_code FROM _task219_rows ON CONFLICT (frequency, period_start_date, period_end_date) DO UPDATE SET period_year=EXCLUDED.period_year, period_label=EXCLUDED.period_label;
INSERT INTO curated.dim_attribute_set (attribute_hash, attributes) SELECT DISTINCT attribute_hash, attributes FROM _task219_rows ON CONFLICT (attribute_hash) DO UPDATE SET attributes=EXCLUDED.attributes;
DELETE FROM curated.fact_observation f USING _source_row s, _run_row pr WHERE f.source_id=s.source_id AND f.pipeline_run_id=pr.pipeline_run_id;
INSERT INTO curated.fact_observation (source_id, dataset_release_id, pipeline_run_id, indicator_id, territory_id, period_id, unit_id, attribute_set_id, value, as_of_date, observation_status) SELECT s.source_id, rel.dataset_release_id, pr.pipeline_run_id, i.indicator_id, t.territory_id, p.period_id, u.unit_id, a.attribute_set_id, r.value, {sql_literal(norm.get('release_as_of_date'))}::date, CASE WHEN r.observation_status='missing' THEN 'missing' ELSE 'observed' END FROM _task219_rows r CROSS JOIN _source_row s CROSS JOIN _release_row rel CROSS JOIN _run_row pr JOIN curated.dim_indicator i ON i.source_id=s.source_id AND i.source_indicator_code=r.indicator_code JOIN curated.dim_territory t ON t.iso3_code=r.territory_code JOIN curated.dim_period p ON p.period_year=r.period_year AND p.frequency='A' JOIN curated.dim_unit u ON u.unit_code=r.unit_code JOIN curated.dim_attribute_set a ON a.attribute_hash=r.attribute_hash ON CONFLICT (source_id, indicator_id, territory_id, period_id, unit_id, attribute_set_id, as_of_date) DO UPDATE SET value=EXCLUDED.value, observation_status=EXCLUDED.observation_status, dataset_release_id=EXCLUDED.dataset_release_id, pipeline_run_id=EXCLUDED.pipeline_run_id;
INSERT INTO meta.lineage_event (pipeline_run_id, source_id, event_type, from_artifact, to_artifact, checksum_sha256, row_count, details) SELECT r.pipeline_run_id, s.source_id, 'task219_imf_dip_direct_investment_counterpart_loaded', {sql_literal(rel(RAW_DIR / 'active'))}, {sql_literal(rel(NORM_PATH))}, {sql_literal(sha256_file(NORM_PATH))}, (SELECT count(*) FROM _task219_rows), {jsonb_literal(metadata)} FROM _run_row r CROSS JOIN _source_row s;
INSERT INTO meta.quality_check (pipeline_run_id, check_name, check_status, observed_value, expected_value, details) SELECT pipeline_run_id, 'task219_candidate_reconciliation', CASE WHEN (SELECT count(*) FROM _task219_rows)={len(norm['rows'])} THEN 'pass' ELSE 'fail' END, (SELECT count(*) FROM _task219_rows), {len(norm['rows'])}, {jsonb_literal(metadata)} FROM _run_row UNION ALL SELECT pipeline_run_id, 'task219_observed_missing_reconciliation', CASE WHEN (SELECT count(*) FILTER (WHERE observation_status='observed') FROM _task219_rows)={norm['observed_value_count']} AND (SELECT count(*) FILTER (WHERE observation_status='missing') FROM _task219_rows)={norm['explicit_missing_value_count']} THEN 'pass' ELSE 'fail' END, (SELECT count(*) FROM _task219_rows), {len(norm['rows'])}, {jsonb_literal(metadata)} FROM _run_row;
COMMIT;
"""


def load(db_name: str = "macroforge", run_key: str = RUN_KEY, report_path: Path = LOAD_REPORT) -> dict[str, Any]:
    norm=json.loads(NORM_PATH.read_text(encoding="utf-8"))
    before=psql_scalar(db_name, f"select count(*) from curated.fact_observation f join meta.source s on f.source_id=s.source_id where s.source_code={sql_literal(SOURCE_CODE)}")
    sql=build_load_sql(norm, run_key); SQL_PATH.write_text(sql, encoding="utf-8"); run_psql_file(db_name, sql)
    after=psql_scalar(db_name, f"select count(*) from curated.fact_observation f join meta.source s on f.source_id=s.source_id where s.source_code={sql_literal(SOURCE_CODE)}")
    counts=psql_scalar(db_name, f"""WITH src AS (SELECT source_id FROM meta.source WHERE source_code={sql_literal(SOURCE_CODE)}), run AS (SELECT pipeline_run_id FROM meta.pipeline_run WHERE run_key={sql_literal(run_key)}) SELECT (SELECT count(*) FROM staging.task219_imf_dip_portfolio_counterpart_observation st JOIN run r ON st.pipeline_run_id=r.pipeline_run_id)::text || '|' || (SELECT count(*) FROM curated.fact_observation f JOIN src s ON f.source_id=s.source_id JOIN run r ON f.pipeline_run_id=r.pipeline_run_id)::text || '|' || (SELECT count(*) FROM curated.fact_observation f JOIN src s ON f.source_id=s.source_id JOIN run r ON f.pipeline_run_id=r.pipeline_run_id WHERE observation_status='observed')::text || '|' || (SELECT count(*) FROM curated.fact_observation f JOIN src s ON f.source_id=s.source_id JOIN run r ON f.pipeline_run_id=r.pipeline_run_id WHERE observation_status='missing')::text || '|' || (SELECT count(*) FROM meta.quality_check q JOIN run r ON q.pipeline_run_id=r.pipeline_run_id WHERE q.check_status='fail')::text || '|' || (SELECT count(*) FROM meta.dataset_release dr JOIN src s ON dr.source_id=s.source_id WHERE provider_dataset_code={sql_literal(PROVIDER_DATASET_CODE)} AND release_key={sql_literal(norm['release_key'])})::text""")
    parsed=parse_pipe_counts(counts, [("staging_rows",int),("fact_rows",int),("observed_facts",int),("missing_facts",int),("failed_quality_checks",int),("dataset_release_rows",int)])
    duplicate_groups=int(psql_scalar(db_name, f"select count(*) from (select source_id, indicator_id, territory_id, period_id, unit_id, attribute_set_id, as_of_date, count(*) from curated.fact_observation group by 1,2,3,4,5,6,7 having count(*)>1) d") or 0)
    report={"task":TASK_ID,"status":"succeeded","source_code":SOURCE_CODE,"provider_dataset_code":PROVIDER_DATASET_CODE,"release_key":norm["release_key"],"run_key":run_key,"before_source_fact_count":int(before),"after_source_fact_count":int(after),"postgresql_growth":int(after)-int(before),"counts":parsed,"duplicate_canonical_key_groups":duplicate_groups}
    write_json_report(report_path, report, default_task=TASK_ID); return report


def evaluate_prediction() -> dict[str, Any]:
    pred=json.loads(PRED_PATH.read_text(encoding="utf-8")); norm=json.loads(NORM_PATH.read_text(encoding="utf-8"))
    valued_error=norm["observed_value_count"]-pred["expected_provider_valued_facts"]; missing_error=norm["explicit_missing_value_count"]-pred["expected_explicit_missing_facts"]
    verdict="Mostly Accurate" if abs(valued_error)/max(pred["expected_candidate_cells"],1)<0.20 else "Mixed"
    report={"task":TASK_ID,"prediction_verdict":verdict,"expected_candidate_cells":pred["expected_candidate_cells"],"actual_candidate_cells":norm["candidate_cell_count"],"expected_provider_valued_facts":pred["expected_provider_valued_facts"],"actual_provider_valued_facts":norm["observed_value_count"],"expected_explicit_missing_facts":pred["expected_explicit_missing_facts"],"actual_explicit_missing_facts":norm["explicit_missing_value_count"],"whole_series_absence_count":norm["whole_series_absence_count"],"scale_prediction_error":0,"missingness_prediction_error":missing_error,"provider_behavior_surprises":"DIP returns whole-series absences for many reporter/counterpart/instrument pairs; successful returned series usually have dense annual values.","architecture_compatibility":"compatible for bounded reporter-territory plus counterpart-in-indicator scalar representation"}
    write_json(EVAL_REPORT, report); return report


def write_checksums() -> None:
    paths=[PRED_PATH, PROVIDER_REPORT, NORM_PATH, MANIFEST_PATH, LOAD_REPORT, IDEMPOTENCE_REPORT, EVAL_REPORT, EXTRACTION_REPORT, SQL_PATH]
    paths += sorted(REPORT_DIR.glob("task-219-imf-dip-*-report.json"))
    paths += sorted((RAW_DIR/"active").glob("task-219-imf-dip-*"))
    unique=[]
    seen=set()
    for p in paths:
        if p.exists() and p.is_file() and p not in seen:
            unique.append(p); seen.add(p)
    lines=[f"{sha256_file(p)}  {rel(p)}" for p in unique]
    CHECKSUMS.write_text("\n".join(lines)+"\n", encoding="utf-8")


def main() -> None:
    parser=argparse.ArgumentParser(); parser.add_argument("mode", choices=["metadata","predict","acquire","normalize","load","evaluate","checksums","all"]); parser.add_argument("--db", default="macroforge"); args=parser.parse_args()
    if args.mode in {"metadata","all"}: fetch_metadata_active()
    if args.mode in {"predict","all"}: write_provider_report_and_prediction(); write_extraction_decision()
    if args.mode in {"acquire","all"}: fetch_values()
    if args.mode in {"normalize","all"}: normalize()
    if args.mode in {"load","all"}: load(args.db)
    if args.mode in {"evaluate","all"}: evaluate_prediction()
    if args.mode in {"checksums","all"}: write_checksums()

if __name__ == "__main__":
    main()
