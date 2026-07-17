from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import time
import urllib.request
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TASK_ID = "TASK-200"
CAMPAIGN_NAME = "WDI Poverty and Inequality Chunked Expansion Campaign"
CAMPAIGN_MODE = "Large Campaign Execution Optimization"
SOURCE_NAME = "World Bank World Development Indicators poverty and inequality indicators"
COUNTRY_CATALOG_FIXTURE = PROJECT_ROOT / "data/raw/wdi_operational_phase1/wdi-phase1-all-countries-3i-2000-2023.json"
BASE_RAW_DIR = PROJECT_ROOT / "data/raw/task200_wdi_poverty_inequality_chunked_expansion"
BASE_PROCESSED_DIR = PROJECT_ROOT / "data/processed/task200_wdi_poverty_inequality_chunked_expansion"
CHECKPOINT_DIR = BASE_RAW_DIR / "checkpoints"
RAW_CHUNK_DIR = BASE_RAW_DIR / "chunks"
NORM_CHUNK_DIR = BASE_PROCESSED_DIR / "chunks"
MANIFEST_PATH = BASE_PROCESSED_DIR / "task-200-wdi-poverty-inequality-chunked-manifest.json"
DATE_RANGE = "1990:2024"
PERIODS = [str(y) for y in range(1990, 2025)]
CHUNK_SIZE = 80
CANDIDATE_INDICATORS = [
    "1.0.HCount.1.90usd",
    "1.0.HCount.2.5usd",
    "1.0.HCount.Mid10to50",
    "1.0.HCount.Ofcl",
    "1.0.HCount.Poor4uds",
    "1.0.HCount.Vul4to10",
    "1.0.PGap.1.90usd",
    "1.0.PGap.2.5usd",
    "1.0.PGap.Poor4uds",
    "1.0.PSev.1.90usd",
    "1.0.PSev.2.5usd",
    "1.0.PSev.Poor4uds",
    "1.1.HCount.1.90usd",
    "1.1.HCount.2.5usd",
    "1.1.HCount.Mid10to50",
    "1.1.HCount.Ofcl",
    "1.1.HCount.Poor4uds",
    "1.1.HCount.Vul4to10",
    "1.1.PGap.1.90usd",
    "1.1.PGap.2.5usd",
    "1.1.PGap.Poor4uds",
    "1.1.PSev.1.90usd",
    "1.1.PSev.2.5usd",
    "1.1.PSev.Poor4uds",
    "1.2.HCount.1.90usd",
    "1.2.HCount.2.5usd",
    "1.2.HCount.Mid10to50",
    "1.2.HCount.Ofcl",
    "1.2.HCount.Poor4uds",
    "1.2.HCount.Vul4to10",
    "1.2.PGap.1.90usd",
    "1.2.PGap.2.5usd",
    "1.2.PGap.Poor4uds",
    "1.2.PSev.1.90usd",
    "1.2.PSev.2.5usd",
    "1.2.PSev.Poor4uds",
    "2.0.cov.Cel",
    "2.0.cov.Ele",
    "2.0.cov.Int",
    "2.0.cov.Math.pl_2.all",
    "2.0.cov.Math.pl_2.prv",
    "2.0.cov.Math.pl_2.pub",
    "2.0.cov.Math.pl_3.all",
    "2.0.cov.Math.pl_3.prv",
    "2.0.cov.Math.pl_3.pub",
    "2.0.cov.Read.pl_2.all",
    "2.0.cov.Read.pl_2.prv",
    "2.0.cov.Read.pl_2.pub",
    "2.0.cov.Read.pl_3.all",
    "2.0.cov.Read.pl_3.prv",
    "2.0.cov.Read.pl_3.pub",
    "2.0.cov.San",
    "2.0.cov.Sch",
    "2.0.cov.Scie.pl_2.all",
    "2.0.cov.Scie.pl_2.prv",
    "2.0.cov.Scie.pl_2.pub",
    "2.0.cov.Scie.pl_3.all",
    "2.0.cov.Scie.pl_3.prv",
    "2.0.cov.Scie.pl_3.pub",
    "2.0.cov.Wat",
    "2.0.hoi.Cel",
    "2.0.hoi.Ele",
    "2.0.hoi.Int",
    "2.0.hoi.Math.pl_2.all",
    "2.0.hoi.Math.pl_2.prv",
    "2.0.hoi.Math.pl_2.pub",
    "2.0.hoi.Math.pl_3.all",
    "2.0.hoi.Math.pl_3.prv",
    "2.0.hoi.Math.pl_3.pub",
    "2.0.hoi.Read.pl_2.all",
    "2.0.hoi.Read.pl_2.prv",
    "2.0.hoi.Read.pl_2.pub",
    "2.0.hoi.Read.pl_3.all",
    "2.0.hoi.Read.pl_3.prv",
    "2.0.hoi.Read.pl_3.pub",
    "2.0.hoi.San",
    "2.0.hoi.Sch",
    "2.0.hoi.Scie.pl_2.all",
    "2.0.hoi.Scie.pl_2.prv",
    "2.0.hoi.Scie.pl_2.pub",
    "2.0.hoi.Scie.pl_3.all",
    "2.0.hoi.Scie.pl_3.prv",
    "2.0.hoi.Scie.pl_3.pub",
    "2.0.hoi.Wat",
    "3.0.Atkin.0.5",
    "3.0.Atkin.1",
    "3.0.Atkin.2",
    "3.0.GenEnt-1",
    "3.0.GenEnt2",
    "3.0.Gini",
    "3.0.Gini_nozero",
    "3.0.IncShr.q1",
    "3.0.IncShr.q2",
    "3.0.IncShr.q3",
    "3.0.IncShr.q4",
    "3.0.IncShr.q5",
    "3.0.MLongDev0",
    "3.0.Rate75-25",
    "3.0.Rate90-10",
    "3.0.TheilInd1",
    "3.1.Gini",
    "3.1.MLongDev0",
    "3.1.TheilInd1",
    "3.2.Gini",
    "3.2.MLongDev0",
    "3.2.TheilInd1",
    "8.0.LIPI",
    "SI.DST.02ND.20",
    "SI.DST.03RD.20",
    "SI.DST.04TH.20",
    "SI.DST.05TH.20",
    "SI.DST.10TH.10",
    "SI.DST.50MD",
    "SI.DST.FRST.10",
    "SI.DST.FRST.20",
    "SI.POV.2DAY",
    "SI.POV.GAP2",
    "SI.POV.GAPS",
    "SI.POV.LMIC",
    "SI.POV.LMIC.GP",
    "SI.POV.MDIM",
    "SI.POV.MDIM.17",
    "SI.POV.MDIM.17.XQ",
    "SI.POV.MDIM.FE",
    "SI.POV.MDIM.HH",
    "SI.POV.MDIM.IT",
    "SI.POV.MDIM.MA",
    "SI.POV.MDIM.XQ",
    "SI.POV.NAGP",
    "SI.POV.NAHC",
    "SI.POV.RUGP",
    "SI.POV.RUHC",
    "SI.POV.UMIC",
    "SI.POV.UMIC.GP",
    "SI.POV.URGP",
    "SI.POV.URHC",
    "SI.SPR.PC40",
    "SI.SPR.PC40.05",
    "SI.SPR.PC40.ZG",
    "SI.SPR.PCAP",
    "SI.SPR.PCAP.05",
    "SI.SPR.PCAP.ZG"
]
NON_GOALS = ["architecture_redesign", "generic_WDI_framework_extraction", "provider_mirror", "source_registry", "production_live_ingestion", "raw_evidence_cleanup"]


def _read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256_blob(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _file_sha(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for b in iter(lambda:f.read(1024*1024), b''):
            h.update(b)
    return h.hexdigest()


def _load_countries() -> tuple[list[str], list[dict[str, Any]]]:
    raw = _read_json(COUNTRY_CATALOG_FIXTURE)
    countries = list(raw["scope"]["countries"])
    catalog = list(raw["country_catalog"]["countries"])
    by_id = {r["id"]: r for r in catalog}
    countries = [c for c in countries if c in by_id]
    aggregates = [r["id"] for r in catalog if r.get("region", {}).get("id") == "NA" and r["id"] in countries]
    if aggregates:
        raise ValueError(f"country catalog includes aggregate rows: {aggregates[:5]}")
    return countries, [by_id[c] for c in countries]


def _worldbank_url(indicator: str) -> str:
    return f"https://api.worldbank.org/v2/country/all/indicator/{indicator}?format=json&date={DATE_RANGE}&per_page=20000"


def _indicator_metadata_url(indicator: str) -> str:
    return f"https://api.worldbank.org/v2/indicator/{indicator}?format=json"


def _get_json(url: str, timeout_seconds: int) -> Any:
    req = urllib.request.Request(url, headers={"User-Agent": "MacroForge TASK-200 WDI poverty and inequality chunked expansion"})
    with urllib.request.urlopen(req, timeout=timeout_seconds) as response:
        return json.loads(response.read().decode("utf-8"))


def _checkpoint_path(indicator: str) -> Path:
    safe = indicator.replace("/", "_").replace(":", "_")
    return CHECKPOINT_DIR / f"{safe}.json"


def _chunks(values: list[str], size: int) -> list[list[str]]:
    return [values[i:i+size] for i in range(0, len(values), size)]


def fetch_one(indicator: str, allowed: set[str], timeout_seconds: int) -> dict[str, Any]:
    cp = _checkpoint_path(indicator)
    if cp.exists():
        cached = _read_json(cp)
        cached["checkpoint_status"] = "resumed_from_checkpoint"
        return cached
    data_url = _worldbank_url(indicator)
    meta_url = _indicator_metadata_url(indicator)
    payload = None; metadata_payload = None; data_error = None; metadata_error = None
    start = time.monotonic()
    for _ in range(3):
        try:
            payload = _get_json(data_url, timeout_seconds)
            if isinstance(payload, list) and len(payload) == 2 and isinstance(payload[1], list):
                before_total = len(payload[1])
                payload = [dict(payload[0]), [r for r in payload[1] if r.get("countryiso3code") in allowed]]
                payload[0]["total_before_non_aggregate_filter"] = payload[0].get("total")
                payload[0]["rows_before_non_aggregate_filter"] = before_total
                payload[0]["total"] = len(payload[1])
            data_error = None; break
        except Exception as exc:
            data_error = {"type": type(exc).__name__, "message": str(exc)}
    for _ in range(3):
        try:
            metadata_payload = _get_json(meta_url, timeout_seconds)
            metadata_error = None; break
        except Exception as exc:
            metadata_error = {"type": type(exc).__name__, "message": str(exc)}
    if data_error is not None:
        payload = [{"error": data_error["type"], "message": data_error["message"], "lastupdated": None}, []]
    if metadata_error is not None:
        metadata_payload = [{"error": metadata_error["type"], "message": metadata_error["message"]}]
    result = {"indicator_code": indicator, "url": data_url, "metadata_url": meta_url, "response": payload, "metadata_response": metadata_payload, "checkpoint_status": "fetched_and_checkpointed", "elapsed_seconds": round(time.monotonic()-start, 3)}
    cp.parent.mkdir(parents=True, exist_ok=True)
    tmp=cp.with_suffix('.tmp')
    tmp.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp.replace(cp)
    return result


def base_scope(indicators: list[str], chunk_index: int | None = None) -> dict[str, Any]:
    countries, _ = _load_countries()
    return {"task": TASK_ID, "campaign": CAMPAIGN_NAME, "mode": CAMPAIGN_MODE,
        "strategic_objective": "construct the canonical macroeconomic repository while improving large campaign execution",
        "domain": "Poverty, inequality, and distributional welfare", "analytical_capability": "Poverty headcount/gap/severity, inequality, income distribution, shared prosperity, and distributional welfare monitoring",
        "confidence_cell": "WDI public API v2 annual scalar country-indicator observations for poverty and inequality indicators",
        "country_scope": "all_non_aggregate_wdi_countries", "countries": countries, "country_count": len(countries),
        "date_range": DATE_RANGE, "periods": PERIODS, "indicators": indicators, "candidate_count": len(indicators),
        "max_presparsity_rows": len(countries) * len(PERIODS) * len(indicators), "chunk_index": chunk_index,
        "chunk_size": CHUNK_SIZE, "raw_evidence_policy": "preserve per-indicator checkpoints and per-chunk raw/normalized artifacts by default",
        "execution_improvements": ["per_indicator_atomic_checkpoints", "deterministic_candidate_chunks", "per_chunk_raw_artifacts", "per_chunk_normalized_artifacts", "partial_completion_manifest", "chunked_postgresql_loads"],
        "non_goals": NON_GOALS}


def fetch_raw(timeout_seconds: int = 45, max_workers: int = 16) -> dict[str, Any]:
    countries, catalog = _load_countries(); allowed=set(countries)
    CHECKPOINT_DIR.mkdir(parents=True, exist_ok=True); RAW_CHUNK_DIR.mkdir(parents=True, exist_ok=True)
    chunk_records=[]; t0=time.monotonic()
    for idx, indicators in enumerate(_chunks(CANDIDATE_INDICATORS, CHUNK_SIZE), start=1):
        start=time.monotonic()
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as pool:
            by_indicator = {req["indicator_code"]: req for req in pool.map(lambda ind: fetch_one(ind, allowed, timeout_seconds), indicators)}
        requests=[by_indicator[i] for i in indicators]
        raw={"scope": base_scope(indicators, idx), "country_catalog": {"source_fixture": str(COUNTRY_CATALOG_FIXTURE.relative_to(PROJECT_ROOT)), "countries": catalog}, "requests": requests}
        raw_path=RAW_CHUNK_DIR / f"task-200-wdi-poverty-inequality-raw-chunk-{idx:02d}.json"
        raw_path.write_text(json.dumps(raw, indent=2, sort_keys=True)+"\n", encoding='utf-8')
        resumed=sum(1 for r in requests if r.get('checkpoint_status')=='resumed_from_checkpoint')
        fetched=sum(1 for r in requests if r.get('checkpoint_status')=='fetched_and_checkpointed')
        rec={"chunk_index": idx, "indicator_count": len(indicators), "raw_path": str(raw_path.relative_to(PROJECT_ROOT)), "raw_sha256": _file_sha(raw_path), "resumed_from_checkpoint": resumed, "fetched_this_run": fetched, "elapsed_seconds": round(time.monotonic()-start,3)}
        chunk_records.append(rec)
    return {"scope": base_scope(CANDIDATE_INDICATORS, None) | {"chunk_count": len(chunk_records), "chunk_records": chunk_records, "elapsed_seconds": round(time.monotonic()-t0,3)}, "country_catalog": {"source_fixture": str(COUNTRY_CATALOG_FIXTURE.relative_to(PROJECT_ROOT)), "countries": catalog}, "requests": []}


def _parts(req: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    resp=req.get('response')
    if not isinstance(resp, list): raise ValueError('unsupported response structure: response is not a JSON list')
    if len(resp)==1 and isinstance(resp[0], dict) and 'message' in resp[0]: raise ValueError('provider_error_message')
    if len(resp)!=2 or not isinstance(resp[0], dict) or not isinstance(resp[1], list): raise ValueError('unsupported response structure: expected [metadata, observations]')
    return resp[0], resp[1]


def _metadata_known(req: dict[str, Any]) -> bool | None:
    meta=req.get('metadata_response')
    if isinstance(meta, list) and len(meta)==2 and isinstance(meta[1], list): return len(meta[1])>0
    if isinstance(meta, list) and len(meta)==1 and isinstance(meta[0], dict) and 'message' in meta[0]: return False
    return None


def _provider_message(req: dict[str, Any]) -> str | None:
    resp=req.get('response')
    if isinstance(resp, list) and len(resp)==1 and isinstance(resp[0], dict) and 'message' in resp[0]: return json.dumps(resp[0].get('message'), sort_keys=True)
    return None


def classify(raw: dict[str, Any], min_non_null_observations: int=1) -> dict[str, Any]:
    countries=list(raw['scope']['countries']); country_set=set(countries)
    results={}; included=[]; excluded=[]; arch=[]; outside=[]
    for req in raw['requests']:
        indicator=req['indicator_code']; ev={"indicator": indicator, "classification": "compatible", "provider_evidence_category": "compatible_annual_scalar_observations", "exclusion_evidence": None, "provider_label": None, "provider_lastupdated": None, "provider_total": None, "provider_total_before_non_aggregate_filter": None, "returned_row_count":0, "expected_max_rows": len(countries)*len(PERIODS), "countries_with_rows":0, "countries_with_observations":0, "periods": [], "period_count":0, "non_null_observation_count":0, "missing_observation_count":0, "non_null_density":0.0, "response_sha256": _sha256_blob(req.get('response')), "metadata_sha256": _sha256_blob(req.get('metadata_response')), "metadata_known_indicator": _metadata_known(req), "data_url": req.get('url'), "metadata_url": req.get('metadata_url')}
        try:
            meta, obs = _parts(req)
        except ValueError as exc:
            ev['classification']='provider_unavailable'; ev['provider_evidence_category']='provider_unavailable_invalid_indicator' if _metadata_known(req) is False else 'unsupported_response_structure'; ev['exclusion_evidence']=_provider_message(req) or str(exc)
            outside.append(indicator); excluded.append(indicator); results[indicator]=ev; continue
        ev['provider_lastupdated']=meta.get('lastupdated'); ev['provider_total']=meta.get('total'); ev['provider_total_before_non_aggregate_filter']=meta.get('total_before_non_aggregate_filter'); ev['returned_row_count']=len(obs)
        row_c=set(); val_c=set(); periods=set(); non_null=0; bad=None; wrong=None; out=set(); nonannual=set(); label=None
        for row in obs:
            ind=row.get('indicator') or {}; c=row.get('country') or {}; iso=row.get('countryiso3code'); per=str(row.get('date')); label=label or ind.get('value')
            if not ind.get('id') or not iso or not per or not c: bad='missing required WDI scalar observation fields'; break
            if ind.get('id') != indicator: wrong=ind.get('id'); break
            if iso not in country_set: out.add(str(iso))
            if not per.isdigit() or len(per)!=4: nonannual.add(per)
            periods.add(per); row_c.add(str(iso))
            if row.get('value') is not None: non_null += 1; val_c.add(str(iso))
        ev.update({"provider_label": label, "countries_with_rows": len(row_c), "countries_with_observations": len(val_c), "periods": sorted(periods), "period_count": len(periods), "non_null_observation_count": non_null, "missing_observation_count": len(obs)-non_null, "non_null_density": round(non_null/len(obs),6) if obs else 0.0})
        if bad:
            ev['classification']='incompatible_representation'; ev['provider_evidence_category']='unsupported_response_structure'; ev['exclusion_evidence']=bad; arch.append(indicator); excluded.append(indicator)
        elif wrong:
            ev['classification']='changed_provider_semantics'; ev['provider_evidence_category']='changed_provider_semantics'; ev['exclusion_evidence']=f'response contained unexpected indicator {wrong}'; outside.append(indicator); excluded.append(indicator)
        elif out:
            ev['classification']='incompatible_representation'; ev['provider_evidence_category']='outside_non_aggregate_country_scope'; ev['exclusion_evidence']=f'response contained countries outside non-aggregate scope: {sorted(out)[:10]}'; outside.append(indicator); excluded.append(indicator)
        elif nonannual:
            ev['classification']='incompatible_representation'; ev['provider_evidence_category']='non_annual_periods'; ev['exclusion_evidence']=f'response contained non-annual periods: {sorted(nonannual)[:10]}'; arch.append(indicator); excluded.append(indicator)
        elif len(obs)==0:
            ev['classification']='provider_unavailable'; ev['provider_evidence_category']='zero_observations_within_requested_scope'; ev['exclusion_evidence']='provider returned zero non-aggregate rows for requested countries/date range'; outside.append(indicator); excluded.append(indicator)
        elif non_null < min_non_null_observations:
            ev['classification']='provider_unavailable'; ev['provider_evidence_category']='zero_non_null_observations_within_requested_scope'; ev['exclusion_evidence']='provider returned rows but zero non-null observations'; outside.append(indicator); excluded.append(indicator)
        else: included.append(indicator)
        results[indicator]=ev
    return {"task": TASK_ID, "campaign": CAMPAIGN_NAME, "candidate_count": len(raw['scope']['indicators']), "included_indicators": sorted(included), "included_indicator_count": len(included), "excluded_indicators": sorted(set(excluded)), "excluded_indicator_count": len(set(excluded)), "requested_country_count": len(countries), "requested_date_range": DATE_RANGE, "requested_max_presparsity_rows": len(countries)*len(PERIODS)*len(raw['scope']['indicators']), "partition": {"immediately_ingestible": sorted(included), "requires_architectural_investigation": sorted(set(arch)), "provider_or_scope_exclusion": sorted(set(outside))}, "indicator_results": {k:results[k] for k in sorted(results)}}


def normalize(raw: dict[str, Any]) -> dict[str, Any]:
    classification=classify(raw); included=set(classification['included_indicators']); catalog={r['id']: r for r in raw['country_catalog']['countries']}; countries=list(raw['scope']['countries'])
    rows=[]; raw_artifacts=[]; evidence_manifest=[]
    for req in raw['requests']:
        indicator=req['indicator_code']; ev=classification['indicator_results'][indicator]; response_bytes=len(json.dumps(req.get('response'), sort_keys=True).encode())
        manifest={"indicator": indicator, "url": req.get('url'), "metadata_url": req.get('metadata_url'), "sha256": _sha256_blob(req.get('response')), "response_sha256": _sha256_blob(req.get('response')), "metadata_sha256": _sha256_blob(req.get('metadata_response')), "bytes": response_bytes, "classification": ev['classification'], "provider_evidence_category": ev['provider_evidence_category'], "preservation_status": "preserved_in_per_indicator_checkpoint_and_raw_chunk"}
        evidence_manifest.append(manifest)
        if indicator not in included: continue
        meta, obs = _parts(req); raw_artifacts.append({**manifest, "status": "ok", "content_type": "application/json", "row_count": len(obs), "non_null_observation_count": ev['non_null_observation_count'], "source_metadata": meta})
        for item in obs:
            ind=item.get('indicator') or {}; country=item.get('country') or {}; iso=item.get('countryiso3code'); cat=catalog.get(iso,{})
            rows.append({"source": SOURCE_NAME, "indicator_id": ind.get('id'), "indicator_name": ind.get('value'), "country_id": country.get('id'), "country_name": (cat.get('name') or cat.get('value') or country.get('value')), "countryiso3code": iso, "date": str(item.get('date')), "value": item.get('value'), "unit": item.get('unit') or None, "obs_status": item.get('obs_status') or None, "decimal": item.get('decimal'), "repository_section": "poverty_inequality_chunked", "operational_capability": "Poverty headcount/gap/severity, inequality, income distribution, shared prosperity, and distributional welfare monitoring", "operational_mode": CAMPAIGN_MODE, "coverage_level": "implemented_compatible_wdi_economy_growth_chunked_annual_scalar_campaign", "region_id": (cat.get('region') or {}).get('id'), "region_label": (cat.get('region') or {}).get('value'), "income_level_id": (cat.get('incomeLevel') or {}).get('id'), "income_level_label": (cat.get('incomeLevel') or {}).get('value')})
    c_order={c:i for i,c in enumerate(countries)}; i_order={ind:i for i,ind in enumerate(classification['included_indicators'])}
    rows.sort(key=lambda r: (i_order[r['indicator_id']], c_order.get(r['countryiso3code'],9999), int(r['date'])))
    observed=sum(1 for r in rows if r['value'] is not None)
    raw_artifact_path = raw['scope'].get('raw_chunk_path') or raw['scope'].get('raw_manifest_path') or str(BASE_RAW_DIR.relative_to(PROJECT_ROOT))
    normalized_artifact_path = raw['scope'].get('normalized_chunk_path') or str(NORM_CHUNK_DIR.relative_to(PROJECT_ROOT))
    normalized={"task": TASK_ID, "campaign": CAMPAIGN_NAME, "mode": CAMPAIGN_MODE, "source": SOURCE_NAME, "support_bundle": raw_artifact_path, "raw_evidence_preservation": {"policy": raw['scope']['raw_evidence_policy'], "raw_artifact": raw_artifact_path, "normalized_artifact": normalized_artifact_path, "raw_artifact_sha256": _sha256_blob(raw), "deletion_performed": False, "cleanup_proposed": False}, "countries": countries, "country_count": len(countries), "indicators": classification['included_indicators'], "indicator_count": classification['included_indicator_count'], "excluded_indicators": classification['excluded_indicators'], "date_range": DATE_RANGE, "expected_row_count": len(rows), "row_count": len(rows), "observed_value_count": observed, "missing_value_count": len(rows)-observed, "rows": rows, "raw_artifacts": raw_artifacts, "evidence_manifest": evidence_manifest, "classification": classification, "operational_scope": raw['scope']}
    normalized['normalized_artifact_sha256']=_sha256_blob({k:v for k,v in normalized.items() if k!='normalized_artifact_sha256'})
    return normalized


def write_artifacts(raw_all: dict[str, Any]) -> dict[str, Any]:
    BASE_RAW_DIR.mkdir(parents=True, exist_ok=True); BASE_PROCESSED_DIR.mkdir(parents=True, exist_ok=True); RAW_CHUNK_DIR.mkdir(parents=True, exist_ok=True); NORM_CHUNK_DIR.mkdir(parents=True, exist_ok=True)
    chunk_man=[]; all_class={}; total_rows=0; total_obs=0; total_missing=0; included=[]; excluded=[]
    requests_by={r['indicator_code']: r for r in raw_all.get('requests', [])}
    _, catalog = _load_countries()
    for idx, indicators in enumerate(_chunks(CANDIDATE_INDICATORS, CHUNK_SIZE), start=1):
        raw_path=RAW_CHUNK_DIR / f"task-200-wdi-poverty-inequality-raw-chunk-{idx:02d}.json"
        if raw_path.exists(): raw=_read_json(raw_path)
        else:
            raw={"scope": base_scope(indicators, idx), "country_catalog": {"source_fixture": str(COUNTRY_CATALOG_FIXTURE.relative_to(PROJECT_ROOT)), "countries": catalog}, "requests": [requests_by[i] for i in indicators]}
        raw['scope']['raw_chunk_path']=str(raw_path.relative_to(PROJECT_ROOT))
        norm_path=NORM_CHUNK_DIR / f"task-200-wdi-poverty-inequality-normalized-chunk-{idx:02d}.json"
        raw['scope']['normalized_chunk_path']=str(norm_path.relative_to(PROJECT_ROOT))
        raw_path.write_text(json.dumps(raw, indent=2, sort_keys=True)+"\n", encoding='utf-8')
        norm=normalize(raw)
        norm_path.write_text(json.dumps(norm, indent=2, sort_keys=True)+"\n", encoding='utf-8')
        all_class.update(norm['classification']['indicator_results']); total_rows += norm['row_count']; total_obs += norm['observed_value_count']; total_missing += norm['missing_value_count']; included.extend(norm['indicators']); excluded.extend(norm['excluded_indicators'])
        chunk_man.append({"chunk_index": idx, "candidate_count": len(indicators), "included_indicator_count": norm['indicator_count'], "excluded_indicator_count": len(norm['excluded_indicators']), "row_count": norm['row_count'], "observed_value_count": norm['observed_value_count'], "raw_path": str(raw_path.relative_to(PROJECT_ROOT)), "raw_sha256": _file_sha(raw_path), "normalized_path": str(norm_path.relative_to(PROJECT_ROOT)), "normalized_sha256": _file_sha(norm_path)})
    manifest={"task": TASK_ID, "campaign": CAMPAIGN_NAME, "mode": CAMPAIGN_MODE, "candidate_count": len(CANDIDATE_INDICATORS), "chunk_size": CHUNK_SIZE, "chunk_count": len(chunk_man), "included_indicators": sorted(set(included)), "included_indicator_count": len(set(included)), "excluded_indicators": sorted(set(excluded)), "excluded_indicator_count": len(set(excluded)), "row_count": total_rows, "observed_value_count": total_obs, "missing_value_count": total_missing, "country_count": len(raw_all['scope']['countries']), "date_range": DATE_RANGE, "chunks": chunk_man, "classification": {"indicator_results": {k: all_class[k] for k in sorted(all_class)}}, "execution_improvements": raw_all['scope']['execution_improvements'], "operational_scope": raw_all['scope']}
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2, sort_keys=True)+"\n", encoding='utf-8')
    return manifest


def main(argv: list[str] | None=None) -> int:
    p=argparse.ArgumentParser()
    p.add_argument('command', choices=['fetch','manifest'])
    p.add_argument('--timeout-seconds', type=int, default=45)
    p.add_argument('--max-workers', type=int, default=16)
    args=p.parse_args(argv)
    if args.command=='fetch':
        raw=fetch_raw(args.timeout_seconds, args.max_workers)
        manifest=write_artifacts(raw)
        print(json.dumps({"status":"complete", "candidate_count": manifest['candidate_count'], "chunk_count": manifest['chunk_count'], "included_indicator_count": manifest['included_indicator_count'], "excluded_indicator_count": manifest['excluded_indicator_count'], "row_count": manifest['row_count'], "elapsed_seconds": raw['scope'].get('elapsed_seconds')}, sort_keys=True))
    elif args.command=='manifest':
        raw={"scope": base_scope(CANDIDATE_INDICATORS, None), "country_catalog": {"source_fixture": str(COUNTRY_CATALOG_FIXTURE.relative_to(PROJECT_ROOT)), "countries": _load_countries()[1]}, "requests": [_read_json(_checkpoint_path(i)) for i in CANDIDATE_INDICATORS]}
        manifest=write_artifacts(raw); print(json.dumps({"status":"complete", "row_count": manifest['row_count']}, sort_keys=True))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
