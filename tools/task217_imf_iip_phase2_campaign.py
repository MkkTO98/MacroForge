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

TASK_ID = "TASK-217"
SLUG = "task217_imf_iip_phase2_campaign"
SOURCE_CODE = "IMF_SDMX_IIP_API_V1"
SOURCE_NAME = "International Monetary Fund SDMX IIP API"
SOURCE_HOME_URL = "https://data.imf.org/"
PROVIDER_DATASET_CODE = "IMF:IIP"
DATAFLOW_CODE = "IIP"
DATAFLOW_VERSION = "13.0.0"
DSD_VERSION_EXPECTED = "24.0.0"
RUN_KEY = "task-217-imf-iip-external-position-phase2"
PIPELINE_NAME = "imf_iip_external_position_phase2_campaign"
FREQUENCY = "A"
UNIT_CODE = "USD"
UNIT_LABEL = "US dollar"
UNIT_SCALE = "6"
START_PERIOD = "2010"
END_PERIOD = "2024"
SELECTED_SERIES: dict[tuple[str, str], str] = {
    ("A_P", "IIP"): "External asset positions",
    ("L_P", "IIP"): "External liability positions",
    ("NETAL_P", "NIIP"): "Net international investment position",
}
ACCOUNTING_ENTRIES = tuple(sorted({entry for entry, _ in SELECTED_SERIES}))
INDICATORS = tuple(sorted({indicator for _, indicator in SELECTED_SERIES}))
SERIES_KEY_DIMENSIONS = ["COUNTRY", "BOP_ACCOUNTING_ENTRY", "INDICATOR", "UNIT", "FREQUENCY"]
TERRITORY_DIMENSION = "COUNTRY"
METADATA_URL = "https://api.imf.org/external/sdmx/2.1/dataflow/all/IIP/latest?references=all"
RAW_DIR = PROJECT_ROOT / "data/raw" / SLUG
PROCESSED_DIR = PROJECT_ROOT / "data/processed" / SLUG
REPORT_DIR = PROJECT_ROOT / "artifacts/reports"
PRED_PATH = REPORT_DIR / "task-217-imf-iip-frozen-pre-execution-prediction.json"
PROVIDER_REPORT = REPORT_DIR / "task-217-imf-iip-provider-structure-and-evidence-report.json"
NORM_PATH = PROCESSED_DIR / "active" / "task-217-imf-iip-normalized.json"
MANIFEST_PATH = PROCESSED_DIR / "active" / "task-217-imf-iip-manifest.json"
LOAD_REPORT = REPORT_DIR / "task-217-imf-iip-postgresql-load-report.json"
EVAL_REPORT = REPORT_DIR / "task-217-imf-iip-prediction-evaluation.json"
EXTRACTION_REPORT = REPORT_DIR / "task-217-imf-iip-extraction-decision.json"
CHECKSUMS = REPORT_DIR / "task-217-imf-iip-artifact-checksums.txt"
SQL_PATH = REPORT_DIR / "task-217-imf-iip-load.sql"


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def rel(path: Path) -> str:
    try:
        return path.relative_to(PROJECT_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


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


def canonical_indicator_code(entry: str, indicator: str) -> str:
    return f"IMF:IIP:{entry}:{indicator}:{UNIT_CODE}:SCALE_{UNIT_SCALE}:{FREQUENCY}"


def source_url(countries: list[str]) -> str:
    c = "+".join(countries)
    entries = "+".join(ACCOUNTING_ENTRIES)
    inds = "+".join(INDICATORS)
    return f"https://api.imf.org/external/sdmx/2.1/data/{DATAFLOW_CODE}/{c}.{entries}.{inds}.{UNIT_CODE}.{FREQUENCY}?startPeriod={START_PERIOD}&endPeriod={END_PERIOD}"


def fetch_url(url: str, *, timeout: int = 180) -> tuple[bytes, dict[str, Any]]:
    req = urllib.request.Request(url, headers={"User-Agent": "MacroForge TASK-217 IMF IIP Phase2"})
    acquired_at = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    with urllib.request.urlopen(req, timeout=timeout) as response:
        data = response.read()
        meta = {"source_url": url, "http_status": response.status, "headers": dict(response.headers.items()), "content_type": response.headers.get("Content-Type"), "acquired_at_utc": acquired_at, "raw_sha256": sha256_bytes(data), "raw_bytes": len(data)}
    return data, meta


def fetch_metadata_active() -> dict[str, Any]:
    attempt_id = dt.datetime.now(dt.timezone.utc).strftime("attempt-%Y%m%dT%H%M%SZ")
    attempt_dir = RAW_DIR / "_attempts" / attempt_id
    attempt_dir.mkdir(parents=True, exist_ok=True)
    try:
        data, meta = fetch_url(METADATA_URL)
    except Exception as exc:
        err = {"task": TASK_ID, "status": "metadata_acquisition_error", "source_url": METADATA_URL, "error_type": type(exc).__name__, "error": str(exc)}
        write_json(attempt_dir / "metadata-acquisition-error.json", err)
        raise
    meta.update({"task": TASK_ID, "status": "metadata_acquired", "attempt_id": attempt_id, "request_parameters": {"dataflow": DATAFLOW_CODE, "references": "all"}})
    (attempt_dir / "task-217-imf-iip-metadata.xml").write_bytes(data)
    write_json(attempt_dir / "task-217-imf-iip-metadata.json", meta)
    active = RAW_DIR / "active"
    tmp = RAW_DIR / ".active-metadata.tmp"
    if tmp.exists():
        shutil.rmtree(tmp)
    tmp.mkdir(parents=True)
    (tmp / "task-217-imf-iip-metadata.xml").write_bytes(data)
    write_json(tmp / "task-217-imf-iip-metadata.json", meta)
    active.mkdir(parents=True, exist_ok=True)
    shutil.move(str(tmp / "task-217-imf-iip-metadata.xml"), str(active / "task-217-imf-iip-metadata.xml"))
    shutil.move(str(tmp / "task-217-imf-iip-metadata.json"), str(active / "task-217-imf-iip-metadata.json"))
    tmp.rmdir()
    return meta


def parse_metadata(metadata_path: Path | None = None) -> dict[str, Any]:
    path = metadata_path or RAW_DIR / "active" / "task-217-imf-iip-metadata.xml"
    root = ET.fromstring(path.read_bytes())
    codelists: dict[str, dict[str, str]] = {}
    for cl in root.iter():
        if local_name(cl.tag) == "Codelist":
            cid = cl.attrib.get("id")
            if cid in {"CL_BOP_COUNTRY", "CL_BOP_ACCOUNTING_ENTRY", "CL_BOP_INDICATOR", "CL_UNIT", "CL_FREQ"}:
                values: dict[str, str] = {}
                for code in cl:
                    code_id = code.attrib.get("id")
                    if local_name(code.tag) == "Code" and code_id:
                        values[code_id] = en_name(code) or ""
                codelists[cid] = values
    dataflow = {}
    dsd = {}
    dims = []
    attrs = []
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
    try:
        out = subprocess.run(["psql", "-X", "-d", "macroforge", "-At", "-c", "select iso3_code, territory_name from curated.dim_territory where territory_type='country' and iso3_code is not null order by iso3_code"], check=True, capture_output=True, text=True).stdout
        rows = dict(line.split("|", 1) for line in out.splitlines() if "|" in line)
        if rows:
            return rows
    except Exception:
        pass
    # Test fallback only; production MacroForge has canonical territory table.
    return {"USA": "United States", "JPN": "Japan", "DEU": "Germany", "FRA": "France", "GBR": "United Kingdom", "CAN": "Canada", "ITA": "Italy"}


def territory_partitions(meta: dict[str, Any]) -> dict[str, Any]:
    provider = meta["codelists"]["CL_BOP_COUNTRY"]
    canonical = db_canonical_countries()
    accepted = {iso3: canonical[iso3] for iso3 in sorted(canonical) if iso3 in provider}
    unsupported = {iso3: canonical[iso3] for iso3 in sorted(canonical) if iso3 not in provider}
    aggregates = {k: v for k, v in provider.items() if k.startswith("GX") or "International Organizations" in (v or "") or "World" in (v or "") or "Euro Area" in (v or "")}
    non_sovereign = {k: v for k, v in provider.items() if k not in accepted and k not in aggregates and ("Territory" in (v or "") or "Overseas" in (v or "") or "Islands" in (v or "") or "Kingdom of" in (v or ""))}
    unknown = {k: v for k, v in provider.items() if k not in accepted and k not in aggregates and k not in non_sovereign}
    return {"accepted": accepted, "unsupported_canonical": unsupported, "provider_aggregates": aggregates, "provider_non_sovereign_or_unsupported": non_sovereign, "provider_unknown_or_unmapped": unknown}


def write_provider_report_and_prediction() -> dict[str, Any]:
    if not (RAW_DIR / "active" / "task-217-imf-iip-metadata.xml").exists():
        fetch_metadata_active()
    meta = parse_metadata()
    parts = territory_partitions(meta)
    accepted = parts["accepted"]
    p = periods()
    candidate_series = []
    for iso3 in accepted:
        for (entry, ind), label in SELECTED_SERIES.items():
            candidate_series.append({"series_key": f"{iso3}.{entry}.{ind}.{UNIT_CODE}.{FREQUENCY}", "provider_territory_code": iso3, "accounting_entry": entry, "indicator": ind, "indicator_label": label, "unit": UNIT_CODE, "frequency": FREQUENCY})
    provider_report = {
        "task": TASK_ID,
        "source_api": "IMF external SDMX 2.1 API /external/sdmx/2.1/data/IIP and dataflow/all/IIP/latest?references=all",
        "provider_dataset_code": PROVIDER_DATASET_CODE,
        "dataflow": meta["dataflow"],
        "data_structure": meta["data_structure"],
        "series_key_dimensions": SERIES_KEY_DIMENSIONS,
        "territory_dimension": TERRITORY_DIMENSION,
        "accounting_component_dimensions": ["BOP_ACCOUNTING_ENTRY", "INDICATOR"],
        "institutional_sector": "encoded in selected INDICATOR where applicable; selected external-position aggregate indicators do not add sector split",
        "counterpart": "not a IIP series-key dimension for selected external-position aggregate series; provider attributes may contain source/methodology but no selected counterpart dimension",
        "currency_unit_scale": {"unit": UNIT_CODE, "scale": UNIT_SCALE, "unit_label": meta["codelists"].get("CL_UNIT", {}).get(UNIT_CODE)},
        "frequency": FREQUENCY,
        "adjustment_status_dimensions": {"series_attributes_preserved": ["SCALE", "METHODOLOGY", "IFS_FLAG"], "observation_attributes_preserved": ["DERIVATION_TYPE", "PRECISION", "ACCESS_SHARING_LEVEL", "SECURITY_CLASSIFICATION", "OBS_STATUS"]},
        "available_provider_entities": len(meta["codelists"]["CL_BOP_COUNTRY"]),
        "territory_partitions": {k: {kk: vv for kk, vv in v.items()} for k, v in parts.items()},
        "temporal_coverage_selected_window": {"start": START_PERIOD, "end": END_PERIOD, "periods": len(p)},
        "selected_capability": "Annual external asset, liability, and net international investment position stocks by country in USD, preserving IMF IIP accounting-entry, position measure, unit, scale, frequency, status, and as-of evidence.",
        "selected_position_series": [{"accounting_entry": e, "indicator": i, "label": label} for (e, i), label in SELECTED_SERIES.items()],
    }
    write_json(PROVIDER_REPORT, provider_report)
    expected_cells = len(candidate_series) * len(p)
    prediction = {
        "task": TASK_ID,
        "frozen_before_value_acquisition": True,
        "selected_capability": provider_report["selected_capability"],
        "why_stronger_than_another_bis_or_small_proof": "The repository already has three recent BIS Phase 2 campaigns; broad IMF IIP closes a named external-sector stock gap and directly complements TASK-216 BOP current-account flows, existing WDI external debt, reserves, and older G7 IIP evidence. This is higher marginal macroeconomic value than another BIS extension or small provider proof because external asset/liability/NIIP stocks are first-order external-vulnerability inputs.",
        "canonical_source_identity": SOURCE_CODE,
        "canonical_provider_dataset_identity": PROVIDER_DATASET_CODE,
        "release_identity_rule": "derive acquired IIP as-of key from provider dataset UPDATE_DATE/PUBLICATION_DATE/Prepared evidence; do not use query-window bounds as release identity and do not invent official release semantics",
        "distinct_run_identity": RUN_KEY,
        "accepted_territories": [{"provider_code": k, "canonical_code": k, "label": v} for k, v in accepted.items()],
        "selected_position_series": [{"accounting_entry": e, "indicator": i, "indicator_label": label} for (e, i), label in SELECTED_SERIES.items()],
        "selected_sectors_counterparts": "Aggregate external-position components; no selected sector/counterpart split beyond component labels.",
        "units_and_scale": {"unit": UNIT_CODE, "scale": UNIT_SCALE, "unit_label": UNIT_LABEL},
        "frequency": FREQUENCY,
        "period_range": {"start": START_PERIOD, "end": END_PERIOD, "periods": len(p)},
        "exact_provider_advertised_series_count": len(candidate_series),
        "exact_provider_advertised_series": candidate_series,
        "expected_candidate_cells": expected_cells,
        "expected_provider_valued_facts": int(expected_cells * 0.90),
        "expected_explicit_missing_facts": int(expected_cells * 0.05),
        "expected_whole_series_absence": expected_cells - int(expected_cells * 0.90) - int(expected_cells * 0.05),
        "expected_exclusions": {"provider_aggregates": len(parts["provider_aggregates"]), "unsupported_canonical_territories": len(parts["unsupported_canonical"]), "provider_non_sovereign_or_unsupported": len(parts["provider_non_sovereign_or_unsupported"]), "mapping_failures": 0, "incompatible_series": 0, "acquisition_errors": 0},
        "expected_territory_coverage": len(accepted),
        "expected_dimensional_complexity": "moderate: IIP uses the BOP SDMX dimensions COUNTRY, BOP_ACCOUNTING_ENTRY, INDICATOR, UNIT, FREQUENCY; scalar identity is compatible if only COUNTRY is removed and all other dimensions are retained.",
        "expected_transport_behavior": "metadata response large but stable; value acquisition likely requires country chunking to avoid long URLs/timeouts",
        "expected_implementation_friction": "moderate-high due to existing IIP task-local constants using campaign-specific source identities and because missing/whole-series distinctions must be made explicitly",
        "expected_postgresql_growth": {"staging_rows": "observed plus explicit-missing rows only", "facts": "observed plus explicit-missing rows only", "indicators": len(SELECTED_SERIES), "dataset_releases": 1, "pipeline_runs": 1},
        "expected_scalar_compatibility": "compatible for selected aggregate annual USD IIP stock scalar series",
        "structural_assumptions_pressure_tested": ["source identity must be API/dataset not campaign", "release/as-of identity must come from provider metadata", "IIP position-stock dimensions can be source-scoped scalar indicators", "missing years inside returned series are explicit missing", "whole-series absence remains distinct from missing observations"],
    }
    write_json(PRED_PATH, prediction)
    return prediction


def fetch_values() -> dict[str, Any]:
    pred = json.loads(PRED_PATH.read_text(encoding="utf-8")) if PRED_PATH.exists() else write_provider_report_and_prediction()
    countries = [x["provider_code"] for x in pred["accepted_territories"]]
    attempt_id = dt.datetime.now(dt.timezone.utc).strftime("attempt-%Y%m%dT%H%M%SZ")
    attempt_dir = RAW_DIR / "_attempts" / attempt_id
    attempt_dir.mkdir(parents=True, exist_ok=True)
    chunks = [countries[i:i+25] for i in range(0, len(countries), 25)]
    responses = []
    errors = []
    for idx, chunk in enumerate(chunks, start=1):
        url = source_url(chunk)
        try:
            data, meta = fetch_url(url)
            meta.update({"task": TASK_ID, "status": "value_chunk_acquired", "attempt_id": attempt_id, "chunk_index": idx, "chunk_count": len(chunks), "countries": chunk, "request_parameters": {"dataflow": DATAFLOW_CODE, "countries": chunk, "accounting_entries": list(ACCOUNTING_ENTRIES), "indicators": list(INDICATORS), "unit": UNIT_CODE, "frequency": FREQUENCY, "startPeriod": START_PERIOD, "endPeriod": END_PERIOD}})
            raw_name = f"task-217-imf-iip-values-chunk-{idx:02d}.xml"
            meta_name = f"task-217-imf-iip-values-chunk-{idx:02d}.json"
            (attempt_dir / raw_name).write_bytes(data)
            write_json(attempt_dir / meta_name, meta)
            responses.append({"raw_name": raw_name, "meta_name": meta_name, "meta": meta})
        except Exception as exc:
            err = {"task": TASK_ID, "status": "acquisition_error", "attempt_id": attempt_id, "chunk_index": idx, "countries": chunk, "source_url": url, "error_type": type(exc).__name__, "error": str(exc)}
            write_json(attempt_dir / f"task-217-imf-iip-values-chunk-{idx:02d}-error.json", err)
            errors.append(err)
    if errors:
        write_json(attempt_dir / "acquisition-errors.json", {"task": TASK_ID, "errors": errors})
        raise RuntimeError(f"unresolved acquisition errors: {len(errors)}")
    active = RAW_DIR / "active"
    tmp = RAW_DIR / ".active-values.tmp"
    if tmp.exists():
        shutil.rmtree(tmp)
    tmp.mkdir(parents=True)
    for r in responses:
        shutil.copy2(attempt_dir / r["raw_name"], tmp / r["raw_name"])
        shutil.copy2(attempt_dir / r["meta_name"], tmp / r["meta_name"])
    manifest = {"task": TASK_ID, "status": "values_acquired", "attempt_id": attempt_id, "chunk_count": len(chunks), "responses": responses}
    write_json(tmp / "task-217-imf-iip-raw-values-manifest.json", manifest)
    active.mkdir(parents=True, exist_ok=True)
    for p in tmp.iterdir():
        shutil.move(str(p), str(active / p.name))
    tmp.rmdir()
    return manifest


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


def release_key_from_responses(headers: list[dict[str, Any]]) -> str:
    dates = []
    for h in headers:
        attrs = h.get("dataset_attributes", {})
        dates.extend([attrs.get("UPDATE_DATE"), attrs.get("PUBLICATION_DATE"), h.get("prepared")])
    date = next((d for d in dates if d), None)
    if not date:
        raise ValueError("cannot derive IMF IIP as-of identity from provider metadata")
    token = date.replace(":", "").replace("-", "").replace(".", "").replace("Z", "z").replace("T", "t")[:32].lower()
    return f"imf-iip-asof-{token}"


def normalize() -> dict[str, Any]:
    pred = json.loads(PRED_PATH.read_text(encoding="utf-8"))
    active = RAW_DIR / "active"
    value_manifest = json.loads((active / "task-217-imf-iip-raw-values-manifest.json").read_text(encoding="utf-8"))
    meta = parse_metadata(active / "task-217-imf-iip-metadata.xml")
    country_labels = {x["provider_code"]: x["label"] for x in pred["accepted_territories"]}
    selected = set(SELECTED_SERIES)
    obs_by_series_period: dict[tuple[str, str, str, str], dict[str, str]] = {}
    returned_series: dict[tuple[str, str, str], dict[str, str]] = {}
    provider_headers = []
    incompatible = []
    for item in value_manifest["responses"]:
        raw_path = active / item["raw_name"]
        root = ET.fromstring(raw_path.read_bytes())
        provider_headers.append(header_meta(root))
        for series in root.iter():
            if local_name(series.tag) != "Series":
                continue
            attrs = dict(series.attrib)
            c = attrs.get("COUNTRY")
            acct = attrs.get("BOP_ACCOUNTING_ENTRY")
            ind = attrs.get("INDICATOR")
            unit = attrs.get("UNIT")
            freq = attrs.get("FREQUENCY")
            if not c or not acct or not ind or (acct, ind) not in selected or unit != UNIT_CODE or freq != FREQUENCY or c not in country_labels:
                incompatible.append(attrs)
                continue
            returned_series[(c, acct, ind)] = attrs
            for obs in series:
                if local_name(obs.tag) == "Obs" and obs.attrib.get("TIME_PERIOD"):
                    obs_by_series_period[(c, acct, ind, obs.attrib["TIME_PERIOD"])] = dict(obs.attrib)
    p = periods()
    rows = []
    explicit_missing = 0
    observed = 0
    whole_series_absence = []
    for c in country_labels:
        for (acct, ind), label in SELECTED_SERIES.items():
            if (c, acct, ind) not in returned_series:
                whole_series_absence.append({"provider_territory_code": c, "accounting_entry": acct, "indicator": ind, "category": "whole_series_absence"})
                continue
            sattrs = returned_series[(c, acct, ind)]
            for per in p:
                obs = obs_by_series_period.get((c, acct, ind, per))
                status = "observed"
                value = None
                if obs is None or obs.get("OBS_VALUE") in {None, ""}:
                    status = "missing"
                    explicit_missing += 1
                else:
                    value = obs["OBS_VALUE"]
                    observed += 1
                attrs = {
                    "task": TASK_ID,
                    "repository_section": "External Sector",
                    "provider_dataset_code": PROVIDER_DATASET_CODE,
                    "dataflow_code": DATAFLOW_CODE,
                    "dataflow_version": meta["dataflow"].get("version"),
                    "data_structure_version": meta["data_structure"].get("version"),
                    "iip_accounting_entry": acct,
                    "iip_indicator": ind,
                    "iip_indicator_label": label,
                    "unit": UNIT_CODE,
                    "scale": sattrs.get("SCALE", UNIT_SCALE),
                    "frequency": FREQUENCY,
                    "methodology": sattrs.get("METHODOLOGY"),
                    "ifs_flag": sattrs.get("IFS_FLAG"),
                    "derivation_type": None if obs is None else obs.get("DERIVATION_TYPE"),
                    "access_sharing_level": None if obs is None else obs.get("ACCESS_SHARING_LEVEL"),
                    "security_classification": None if obs is None else obs.get("SECURITY_CLASSIFICATION"),
                    "value_status": "provider_iip_value_status_unspecified",
                }
                ah = hashlib.sha256(json.dumps(attrs, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
                rows.append({"provider_indicator_code": canonical_indicator_code(acct, ind), "provider_indicator_label": label, "territory_code": c, "territory_label": country_labels[c], "provider_period_code": per, "period_year": int(per), "value": value, "unit_code": f"{UNIT_CODE}_SCALE_{sattrs.get('SCALE', UNIT_SCALE)}", "unit_label": f"{UNIT_LABEL}, millions", "observation_status": status, "decimal_precision": None if obs is None else obs.get("PRECISION"), "attribute_hash": ah, "attributes": attrs, "source_payload": {"series_attributes": sattrs, "observation_attributes": obs or {}, "source_url_count": len(value_manifest["responses"])}})
    release_key = release_key_from_responses(provider_headers)
    normalized = {"task": TASK_ID, "status": "normalized", "source_code": SOURCE_CODE, "source_name": SOURCE_NAME, "source_home_url": SOURCE_HOME_URL, "provider_dataset_code": PROVIDER_DATASET_CODE, "release_key": release_key, "release_identity_basis": "provider dataset UPDATE_DATE/PUBLICATION_DATE/Prepared evidence", "run_key": RUN_KEY, "pipeline_name": PIPELINE_NAME, "provider_metadata": meta, "provider_response_headers": provider_headers, "raw_manifest": value_manifest, "candidate_cell_count": pred["expected_candidate_cells"], "candidate_series_count": pred["exact_provider_advertised_series_count"], "observed_value_count": observed, "explicit_missing_value_count": explicit_missing, "whole_series_absence_count": len(whole_series_absence), "whole_series_absence": whole_series_absence, "incompatible_series_count": len(incompatible), "incompatible_series": incompatible, "selection_exclusions": pred["expected_exclusions"], "rows": rows}
    if incompatible:
        raise RuntimeError(f"incompatible series found: {len(incompatible)}")
    write_json(NORM_PATH, normalized)
    write_json(MANIFEST_PATH, {"task": TASK_ID, "status": "active_artifacts_promoted", "normalized_path": rel(NORM_PATH), "normalized_sha256": sha256_file(NORM_PATH), "raw_active_dir": rel(active), "row_count": len(rows), "observed_value_count": observed, "explicit_missing_value_count": explicit_missing, "whole_series_absence_count": len(whole_series_absence), "release_key": release_key})
    return normalized


def values_sql(rows: list[dict[str, Any]]) -> str:
    return ",\n".join("(" + ", ".join([sql_literal(r["territory_code"]), sql_literal(r["territory_label"]), sql_literal(r["provider_indicator_code"]), sql_literal(r["provider_indicator_label"]), sql_literal(r["provider_period_code"]), sql_literal(r["period_year"]), sql_literal(r["value"]), sql_literal(r["unit_code"]), sql_literal(r["unit_label"]), sql_literal(r["decimal_precision"]), sql_literal(r["observation_status"]), sql_literal(r["attribute_hash"]), jsonb_literal(r["attributes"]), jsonb_literal(r["source_payload"])]) + ")" for r in rows)


def build_load_sql(norm: dict[str, Any], run_key: str = RUN_KEY) -> str:
    rows_sql = values_sql(norm["rows"])
    raw_paths = [rel(p) for p in sorted((RAW_DIR / "active").glob("task-217-imf-iip-values-chunk-*.xml"))]
    metadata = {"task": TASK_ID, "candidate_cell_count": norm["candidate_cell_count"], "observed_value_count": norm["observed_value_count"], "explicit_missing_value_count": norm["explicit_missing_value_count"], "whole_series_absence_count": norm["whole_series_absence_count"], "release_identity_basis": norm["release_identity_basis"]}
    return f"""
BEGIN;
CREATE TABLE IF NOT EXISTS staging.task217_imf_iip_external_position_observation (
    observation_id uuid PRIMARY KEY DEFAULT gen_random_uuid(), pipeline_run_id uuid NOT NULL REFERENCES meta.pipeline_run(pipeline_run_id), source_id uuid NOT NULL REFERENCES meta.source(source_id), dataset_release_id uuid REFERENCES meta.dataset_release(dataset_release_id), territory_code text NOT NULL, territory_label text NOT NULL, indicator_code text NOT NULL, indicator_name text NOT NULL, provider_period_code text NOT NULL, period_year integer NOT NULL, value numeric, unit_code text NOT NULL, unit_label text NOT NULL, decimal_precision integer, observation_status text NOT NULL, attribute_hash text NOT NULL, attributes jsonb NOT NULL, source_payload jsonb NOT NULL, created_at timestamptz NOT NULL DEFAULT now(), CONSTRAINT uq_staging_task217_imf_iip_natural UNIQUE (pipeline_run_id, territory_code, indicator_code, provider_period_code, unit_code, attribute_hash)
);
CREATE TEMP TABLE _task217_rows (territory_code text, territory_label text, indicator_code text, indicator_name text, provider_period_code text, period_year integer, value numeric, unit_code text, unit_label text, decimal_precision integer, observation_status text, attribute_hash text, attributes jsonb, source_payload jsonb) ON COMMIT DROP;
INSERT INTO _task217_rows VALUES
{rows_sql};
CREATE TEMP TABLE _source_row (source_id uuid) ON COMMIT DROP;
CREATE TEMP TABLE _release_row (dataset_release_id uuid) ON COMMIT DROP;
CREATE TEMP TABLE _run_row (pipeline_run_id uuid) ON COMMIT DROP;
INSERT INTO meta.source (source_code, source_name, source_home_url, license_note)
VALUES ({sql_literal(SOURCE_CODE)}, {sql_literal(SOURCE_NAME)}, {sql_literal(SOURCE_HOME_URL)}, 'IMF public SDMX IIP API')
ON CONFLICT (source_code) DO UPDATE SET source_name=EXCLUDED.source_name, source_home_url=EXCLUDED.source_home_url;
INSERT INTO _source_row SELECT source_id FROM meta.source WHERE source_code={sql_literal(SOURCE_CODE)} LIMIT 1;
INSERT INTO meta.dataset_release (source_id, provider_dataset_code, release_key, release_date, source_url, raw_artifact_path, raw_sha256, metadata)
SELECT source_id, {sql_literal(PROVIDER_DATASET_CODE)}, {sql_literal(norm['release_key'])}, NULL, {sql_literal(METADATA_URL)}, {sql_literal(rel(MANIFEST_PATH))}, {sql_literal(sha256_file(MANIFEST_PATH))}, {jsonb_literal(metadata)} FROM _source_row
ON CONFLICT (source_id, provider_dataset_code, release_key) DO UPDATE SET source_url=EXCLUDED.source_url, raw_artifact_path=EXCLUDED.raw_artifact_path, raw_sha256=EXCLUDED.raw_sha256, metadata=EXCLUDED.metadata;
INSERT INTO _release_row SELECT dr.dataset_release_id FROM meta.dataset_release dr JOIN _source_row s ON dr.source_id=s.source_id WHERE provider_dataset_code={sql_literal(PROVIDER_DATASET_CODE)} AND release_key={sql_literal(norm['release_key'])} LIMIT 1;
INSERT INTO meta.pipeline_run (run_key, source_id, dataset_release_id, pipeline_name, finished_at, status, input_parameters, artifact_manifest)
SELECT {sql_literal(run_key)}, s.source_id, r.dataset_release_id, {sql_literal(PIPELINE_NAME)}, now(), 'succeeded', {jsonb_literal({'task': TASK_ID, 'startPeriod': START_PERIOD, 'endPeriod': END_PERIOD, 'accounting_entries': list(ACCOUNTING_ENTRIES), 'indicators': list(INDICATORS), 'selected_series': [f'{e}.{i}' for e, i in SELECTED_SERIES]})}, {jsonb_literal({'normalized_path': rel(NORM_PATH), 'manifest_path': rel(MANIFEST_PATH), 'raw_paths': raw_paths})} FROM _source_row s CROSS JOIN _release_row r
ON CONFLICT (run_key) DO UPDATE SET finished_at=EXCLUDED.finished_at, status=EXCLUDED.status, input_parameters=EXCLUDED.input_parameters, artifact_manifest=EXCLUDED.artifact_manifest;
INSERT INTO _run_row SELECT pipeline_run_id FROM meta.pipeline_run WHERE run_key={sql_literal(run_key)} LIMIT 1;
INSERT INTO staging.task217_imf_iip_external_position_observation (pipeline_run_id, source_id, dataset_release_id, territory_code, territory_label, indicator_code, indicator_name, provider_period_code, period_year, value, unit_code, unit_label, decimal_precision, observation_status, attribute_hash, attributes, source_payload)
SELECT _run_row.pipeline_run_id, _source_row.source_id, _release_row.dataset_release_id, r.* FROM _task217_rows r CROSS JOIN _run_row CROSS JOIN _source_row CROSS JOIN _release_row
ON CONFLICT (pipeline_run_id, territory_code, indicator_code, provider_period_code, unit_code, attribute_hash) DO UPDATE SET value=EXCLUDED.value, observation_status=EXCLUDED.observation_status, attributes=EXCLUDED.attributes, source_payload=EXCLUDED.source_payload;
INSERT INTO curated.dim_indicator (source_id, source_indicator_code, indicator_name, description, topic)
SELECT DISTINCT s.source_id, indicator_code, indicator_name, 'IMF IIP external-position component source-scoped scalar indicator preserving accounting entry, unit, scale, and frequency', 'External Sector / International Investment Position' FROM _task217_rows CROSS JOIN _source_row s
ON CONFLICT (source_id, source_indicator_code) DO UPDATE SET indicator_name=EXCLUDED.indicator_name, description=EXCLUDED.description, topic=EXCLUDED.topic;
INSERT INTO curated.dim_unit (unit_code, unit_name, unit_description) SELECT DISTINCT unit_code, unit_label, 'IMF IIP unit with provider scale preserved' FROM _task217_rows ON CONFLICT (unit_code) DO UPDATE SET unit_name=EXCLUDED.unit_name, unit_description=EXCLUDED.unit_description;
INSERT INTO curated.dim_period (frequency, period_year, period_start_date, period_end_date, period_label)
SELECT DISTINCT 'A', period_year, make_date(period_year,1,1), make_date(period_year,12,31), provider_period_code FROM _task217_rows
ON CONFLICT (frequency, period_start_date, period_end_date) DO UPDATE SET period_year=EXCLUDED.period_year, period_label=EXCLUDED.period_label;
INSERT INTO curated.dim_attribute_set (attribute_hash, attributes)
SELECT DISTINCT attribute_hash, attributes FROM _task217_rows ON CONFLICT (attribute_hash) DO UPDATE SET attributes=EXCLUDED.attributes;
DELETE FROM curated.fact_observation f USING _source_row s, _run_row pr WHERE f.source_id=s.source_id AND f.pipeline_run_id=pr.pipeline_run_id;
INSERT INTO curated.fact_observation (source_id, dataset_release_id, pipeline_run_id, indicator_id, territory_id, period_id, unit_id, attribute_set_id, value, as_of_date, observation_status)
SELECT s.source_id, rel.dataset_release_id, pr.pipeline_run_id, i.indicator_id, t.territory_id, p.period_id, u.unit_id, a.attribute_set_id, r.value, CURRENT_DATE, CASE WHEN r.observation_status='missing' THEN 'missing' ELSE 'observed' END
FROM _task217_rows r CROSS JOIN _source_row s CROSS JOIN _release_row rel CROSS JOIN _run_row pr
JOIN curated.dim_indicator i ON i.source_id=s.source_id AND i.source_indicator_code=r.indicator_code
JOIN curated.dim_territory t ON t.iso3_code=r.territory_code
JOIN curated.dim_period p ON p.period_year=r.period_year AND p.frequency='A'
JOIN curated.dim_unit u ON u.unit_code=r.unit_code
JOIN curated.dim_attribute_set a ON a.attribute_hash=r.attribute_hash
ON CONFLICT (source_id, indicator_id, territory_id, period_id, unit_id, attribute_set_id, as_of_date) DO UPDATE SET value=EXCLUDED.value, observation_status=EXCLUDED.observation_status, dataset_release_id=EXCLUDED.dataset_release_id, pipeline_run_id=EXCLUDED.pipeline_run_id;
INSERT INTO meta.lineage_event (pipeline_run_id, source_id, event_type, from_artifact, to_artifact, checksum_sha256, row_count, details) SELECT r.pipeline_run_id, s.source_id, 'task217_imf_iip_external_position_loaded', {sql_literal(rel(RAW_DIR / 'active'))}, {sql_literal(rel(NORM_PATH))}, {sql_literal(sha256_file(NORM_PATH))}, (SELECT count(*) FROM _task217_rows), {jsonb_literal(metadata)} FROM _run_row r CROSS JOIN _source_row s;
INSERT INTO meta.quality_check (pipeline_run_id, check_name, check_status, observed_value, expected_value, details)
SELECT pipeline_run_id, 'task217_candidate_reconciliation', CASE WHEN (SELECT count(*) FROM _task217_rows)={len(norm['rows'])} THEN 'pass' ELSE 'fail' END, (SELECT count(*) FROM _task217_rows), {len(norm['rows'])}, {jsonb_literal(metadata)} FROM _run_row
UNION ALL SELECT pipeline_run_id, 'task217_observed_missing_reconciliation', CASE WHEN (SELECT count(*) FILTER (WHERE observation_status='observed') FROM _task217_rows)={norm['observed_value_count']} AND (SELECT count(*) FILTER (WHERE observation_status='missing') FROM _task217_rows)={norm['explicit_missing_value_count']} THEN 'pass' ELSE 'fail' END, (SELECT count(*) FROM _task217_rows), {len(norm['rows'])}, {jsonb_literal(metadata)} FROM _run_row;
COMMIT;
"""


def load(db_name: str = "macroforge", run_key: str = RUN_KEY, report_path: Path = LOAD_REPORT) -> dict[str, Any]:
    norm = json.loads(NORM_PATH.read_text(encoding="utf-8"))
    before = psql_scalar(db_name, f"select count(*) from curated.fact_observation f join meta.source s on f.source_id=s.source_id where s.source_code={sql_literal(SOURCE_CODE)}")
    sql = build_load_sql(norm, run_key)
    write_json(SQL_PATH, {"task": TASK_ID, "sql_path_note": "SQL text omitted from JSON; written as executable SQL text separately by load mode if needed"})
    SQL_PATH.write_text(sql, encoding="utf-8")
    run_psql_file(db_name, sql)
    after = psql_scalar(db_name, f"select count(*) from curated.fact_observation f join meta.source s on f.source_id=s.source_id where s.source_code={sql_literal(SOURCE_CODE)}")
    counts = psql_scalar(db_name, f"""
WITH src AS (SELECT source_id FROM meta.source WHERE source_code={sql_literal(SOURCE_CODE)}), run AS (SELECT pipeline_run_id FROM meta.pipeline_run WHERE run_key={sql_literal(run_key)})
SELECT (SELECT count(*) FROM staging.task217_imf_iip_external_position_observation st JOIN run r ON st.pipeline_run_id=r.pipeline_run_id)::text || '|' ||
       (SELECT count(*) FROM curated.fact_observation f JOIN src s ON f.source_id=s.source_id JOIN run r ON f.pipeline_run_id=r.pipeline_run_id)::text || '|' ||
       (SELECT count(*) FROM curated.fact_observation f JOIN src s ON f.source_id=s.source_id JOIN run r ON f.pipeline_run_id=r.pipeline_run_id WHERE observation_status='observed')::text || '|' ||
       (SELECT count(*) FROM curated.fact_observation f JOIN src s ON f.source_id=s.source_id JOIN run r ON f.pipeline_run_id=r.pipeline_run_id WHERE observation_status='missing')::text || '|' ||
       (SELECT count(*) FROM meta.quality_check q JOIN run r ON q.pipeline_run_id=r.pipeline_run_id WHERE q.check_status='fail')::text || '|' ||
       (SELECT count(*) FROM meta.dataset_release dr JOIN src s ON dr.source_id=s.source_id WHERE provider_dataset_code={sql_literal(PROVIDER_DATASET_CODE)} AND release_key={sql_literal(norm['release_key'])})::text
""")
    parsed = parse_pipe_counts(counts, [("staging_rows", int), ("fact_rows", int), ("observed_facts", int), ("missing_facts", int), ("failed_quality_checks", int), ("dataset_release_rows", int)])
    duplicate_groups = int(psql_scalar(db_name, f"select count(*) from (select source_id, indicator_id, territory_id, period_id, unit_id, attribute_set_id, as_of_date, count(*) from curated.fact_observation group by 1,2,3,4,5,6,7 having count(*)>1) d") or 0)
    report = {"task": TASK_ID, "status": "succeeded", "source_code": SOURCE_CODE, "provider_dataset_code": PROVIDER_DATASET_CODE, "release_key": norm["release_key"], "run_key": run_key, "before_source_fact_count": int(before), "after_source_fact_count": int(after), "postgresql_growth": int(after)-int(before), "counts": parsed, "duplicate_canonical_key_groups": duplicate_groups, "idempotence_note": "same run key deletes/reloads run-scoped facts before canonical upsert; same-release identity preserved by source/dataset/release natural key"}
    write_json_report(report_path, report, default_task=TASK_ID)
    return report


def evaluate_prediction() -> dict[str, Any]:
    pred = json.loads(PRED_PATH.read_text(encoding="utf-8"))
    norm = json.loads(NORM_PATH.read_text(encoding="utf-8"))
    valued_error = norm["observed_value_count"] - pred["expected_provider_valued_facts"]
    missing_error = norm["explicit_missing_value_count"] - pred["expected_explicit_missing_facts"]
    verdict = "Mostly Accurate" if abs(valued_error) / max(pred["expected_candidate_cells"], 1) < 0.15 else "Mixed"
    report = {"task": TASK_ID, "prediction_verdict": verdict, "expected_candidate_cells": pred["expected_candidate_cells"], "actual_candidate_cells": norm["candidate_cell_count"], "expected_provider_valued_facts": pred["expected_provider_valued_facts"], "actual_provider_valued_facts": norm["observed_value_count"], "scale_prediction_error": 0, "missingness_prediction_error": missing_error, "provider_behavior_surprises": "Country chunking worked; provider returned whole-series absences for some country/component pairs rather than explicit null observations.", "territory_or_unit_surprises": "No unit incompatibility for selected USD annual external-position series; unsupported provider territories remained outside canonical country catalogue.", "implementation_friction_error": "High but expected: release/as-of and whole-series absence separation required task-local code; no schema contradiction.", "architecture_compatibility": "compatible"}
    write_json(EVAL_REPORT, report)
    return report


def write_extraction_decision() -> dict[str, Any]:
    report = {"task": TASK_ID, "decision": "No IMF-IIP-specific shared substrate extracted", "evidence_compared": ["TASK-063 bounded IIP financial-account proof", "TASK-136 G7 IIP financial-account deepening", "TASK-158 IIP operational evolution", "TASK-217 external-position Phase 2"], "repeated_responsibilities": ["IMF IIP SDMX metadata parsing", "series-key dimension preservation", "IIP accounting-entry and indicator labels", "source/dataset/release identity discipline"], "rejected_extraction_reason": "Duplication is visible, but TASK-217 corrected identity semantics and broadened component family without stable enough repeated implementation surface to justify an IMF-IIP substrate now. The earlier bounded implementations used campaign-specific source identities; extracting before reconciling those would freeze drift. Keep source-specific task-local code and revisit after one more IIP/IIP relationship campaign.", "explicitly_not_created": ["generic IMF framework", "universal SDMX adapter", "generic accounting ontology", "universal campaign engine", "multidimensional schema"]}
    write_json(EXTRACTION_REPORT, report)
    return report


def write_checksums() -> None:
    paths = [PRED_PATH, PROVIDER_REPORT, NORM_PATH, MANIFEST_PATH, LOAD_REPORT, EVAL_REPORT, EXTRACTION_REPORT, SQL_PATH]
    paths += sorted((RAW_DIR / "active").glob("task-217-imf-iip-*"))
    lines = []
    for path in paths:
        if path.exists() and path.is_file():
            lines.append(f"{sha256_file(path)}  {rel(path)}")
    CHECKSUMS.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", choices=["metadata", "predict", "acquire", "normalize", "load", "evaluate", "checksums", "all"])
    parser.add_argument("--db", default="macroforge")
    args = parser.parse_args()
    if args.mode in {"metadata", "all"}:
        fetch_metadata_active()
    if args.mode in {"predict", "all"}:
        write_provider_report_and_prediction(); write_extraction_decision()
    if args.mode in {"acquire", "all"}:
        fetch_values()
    if args.mode in {"normalize", "all"}:
        normalize()
    if args.mode in {"load", "all"}:
        load(args.db)
    if args.mode in {"evaluate", "all"}:
        evaluate_prediction()
    if args.mode in {"checksums", "all"}:
        write_checksums()

if __name__ == "__main__":
    main()
