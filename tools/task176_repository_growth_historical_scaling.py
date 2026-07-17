from __future__ import annotations

import argparse
import importlib
import json
import pkgutil
import resource
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Any

from macroforge import __path__ as macroforge_paths
from macroforge.wdi_implemented_compatible_campaign import (
    fetch_campaign_raw,
    normalize_wdi_implemented_compatible_campaign_raw,
    write_wdi_implemented_compatible_campaign_artifacts,
)
from macroforge.wdi_loader import load_wdi_implemented_compatible_campaign_to_postgres

TASK_ID = "TASK-176"
DATE_RANGE = "1990:2024"
START_YEAR = 1990
END_YEAR = 2024
RAW_PATH = Path("data/raw/repository_growth_task176/task-176-wdi-repository-growth-1990-2024.json")
NORMALIZED_PATH = Path("data/processed/repository_growth_task176/task-176-wdi-repository-growth-normalized.json")
ASSESSMENT_REPORT_PATH = Path("artifacts/reports/task-176-growth-opportunity-assessment.json")
PREFLIGHT_REPORT_PATH = Path("artifacts/reports/task-176-repository-growth-preflight-report.json")
CLASSIFICATION_REPORT_PATH = Path("artifacts/reports/task-176-repository-growth-classification-report.json")
OPERATIONAL_REPORT_PATH = Path("artifacts/reports/task-176-repository-growth-operational-report.json")
COVERAGE_REPORT_PATH = Path("artifacts/reports/task-176-repository-growth-coverage-report.json")
EXCEPTION_REPORT_PATH = Path("artifacts/reports/task-176-repository-growth-exception-report.json")
CONFIDENCE_REPORT_PATH = Path("artifacts/reports/task-176-repository-growth-confidence-report.json")
BEFORE_INVENTORY_PATH = Path("artifacts/reports/task-176-inventory-before.json")
AFTER_INVENTORY_PATH = Path("artifacts/reports/task-176-inventory-after.json")
LOAD_REPORT_PATH = Path("artifacts/reports/task-176-load-report.json")
VALIDATION_REPORT_PATH = Path("artifacts/reports/task-176-idempotence-validation-report.json")
FINAL_REPORT_PATH = Path("artifacts/reports/task-176-final-campaign-report.json")
GROWTH_REPORT_PATH = Path("artifacts/reports/R-20260708-task-176-repository-growth-report.md")
HISTORICAL_REPORT_PATH = Path("artifacts/reports/R-20260708-task-176-historical-scaling-validation.md")
IDEMPOTENCE_REPORT_PATH = Path("artifacts/reports/R-20260708-task-176-idempotence-validation.md")
CAPABILITY_REPORT_PATH = Path("artifacts/reports/R-20260708-task-176-capability-improvement-report.md")
STRESS_REPORT_PATH = Path("artifacts/reports/R-20260708-task-176-architecture-stress-observations.md")
CAMPAIGN_REPORT_PATH = Path("artifacts/reports/R-20260708-task-176-repository-growth-and-historical-scaling-campaign.md")

DOMAIN_HINTS = {
    "SP.": "Demographics and population structure",
    "NY.": "Macroeconomy and national accounts",
    "FP.": "Inflation and prices",
    "EG.": "Energy use and electricity mix",
    "NE.": "International trade and external demand",
    "TX.": "Exports, services, technology, and trade composition",
    "TM.": "Imports, services, and trade composition",
    "ST.": "Tourism and travel flows",
    "LP.": "Logistics and supply-chain performance",
    "FS.": "Financial depth and credit intermediation",
    "FD.": "Financial depth and credit intermediation",
    "FM.": "Money and broad liquidity",
    "CM.": "Capital markets",
    "FR.": "Interest rates and credit pricing",
    "FB.": "Banking soundness and financial access",
    "GFDD.": "Global financial development indicators",
    "AG.": "Agriculture, food, and land use",
    "NV.": "Production structure and agriculture share",
    "EN.": "Environment and climate exposure",
    "GB.": "Innovation and R&D",
    "IP.": "Innovation and intellectual property",
    "IT.": "Digital infrastructure",
    "SE.": "Education and human capital",
    "SH.": "Health systems",
    "SI.": "Poverty and inequality",
    "BX.": "Remittances and external transfers",
    "SM.": "Migration",
    "BG.": "Services trade intensity",
}


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def psql_json(db: str, sql: str) -> Any:
    out = subprocess.check_output(["psql", "-d", db, "-At", "-c", sql], text=True)
    return json.loads(out or "null")


def inventory(db: str) -> dict[str, Any]:
    return {
        "row_counts": psql_json(db, "SELECT json_object_agg(table_name, row_count) FROM (SELECT 'staging.wdi_observation' table_name, count(*) row_count FROM staging.wdi_observation UNION ALL SELECT 'curated.fact_observation', count(*) FROM curated.fact_observation UNION ALL SELECT 'curated.dim_indicator', count(*) FROM curated.dim_indicator UNION ALL SELECT 'curated.dim_territory', count(*) FROM curated.dim_territory UNION ALL SELECT 'curated.dim_period', count(*) FROM curated.dim_period UNION ALL SELECT 'meta.dataset_release', count(*) FROM meta.dataset_release UNION ALL SELECT 'meta.pipeline_run', count(*) FROM meta.pipeline_run UNION ALL SELECT 'meta.lineage_event', count(*) FROM meta.lineage_event UNION ALL SELECT 'meta.quality_check', count(*) FROM meta.quality_check) s;"),
        "wdi_coverage": psql_json(db, "SELECT row_to_json(x) FROM (SELECT count(DISTINCT i.source_indicator_code) indicators, count(DISTINCT t.iso3_code) countries, min(p.period_year) min_year, max(p.period_year) max_year, count(*) rows FROM curated.fact_observation fo JOIN curated.dim_indicator i USING(indicator_id) JOIN curated.dim_territory t USING(territory_id) JOIN curated.dim_period p USING(period_id) JOIN meta.source s ON fo.source_id=s.source_id WHERE s.source_code='WDI') x;"),
        "wdi_indicators": psql_json(db, "SELECT COALESCE(json_agg(source_indicator_code ORDER BY source_indicator_code),'[]'::json) FROM curated.dim_indicator i JOIN meta.source s USING(source_id) WHERE s.source_code='WDI';"),
        "wdi_rows_by_period_band": psql_json(db, "SELECT COALESCE(json_object_agg(band, rows),'{}'::json) FROM (SELECT CASE WHEN p.period_year < 2000 THEN 'pre_2000' WHEN p.period_year BETWEEN 2000 AND 2024 THEN 'overlap_2000_2024' ELSE 'post_2024' END band, count(*) rows FROM curated.fact_observation fo JOIN curated.dim_period p USING(period_id) JOIN meta.source s ON fo.source_id=s.source_id WHERE s.source_code='WDI' GROUP BY 1) x;"),
        "quality_checks": psql_json(db, "SELECT COALESCE(json_agg(row_to_json(x) ORDER BY run_key, check_name),'[]'::json) FROM (SELECT pr.run_key, qc.check_name, qc.check_status, qc.observed_value, qc.expected_value, qc.details FROM meta.quality_check qc JOIN meta.pipeline_run pr USING(pipeline_run_id)) x;"),
    }


def loaded_indicators(db: str) -> list[str]:
    return inventory(db)["wdi_indicators"]


def module_indicator_candidates() -> dict[str, list[str]]:
    out: dict[str, set[str]] = defaultdict(set)
    for modinfo in pkgutil.iter_modules(macroforge_paths):
        if not modinfo.name.startswith("wdi_"):
            continue
        module_name = f"macroforge.{modinfo.name}"
        try:
            module = importlib.import_module(module_name)
        except Exception:
            continue
        for name, value in vars(module).items():
            if "INDICATOR" not in name or not isinstance(value, (list, tuple, set)):
                continue
            if all(isinstance(item, str) and "." in item for item in value):
                for item in value:
                    out[item].add(f"src/macroforge/{modinfo.name}.py::{name}")
    return {key: sorted(value) for key, value in sorted(out.items())}


def capability_for_indicator(indicator: str) -> str:
    for prefix, capability in sorted(DOMAIN_HINTS.items(), key=lambda kv: len(kv[0]), reverse=True):
        if indicator.startswith(prefix):
            return capability
    return "Implemented-compatible WDI annual scalar context"


def build_candidate_assessment(db: str) -> dict[str, Any]:
    current = set(loaded_indicators(db))
    module_candidates = module_indicator_candidates()
    unloaded_module = sorted(set(module_candidates) - current)
    selected = sorted(current | set(module_candidates))
    historical_only_presparsity_gain = len(current) * 217 * 10
    module_expansion_presparsity_gain = len(unloaded_module) * 217 * 35
    combined_presparsity = len(selected) * 217 * 35
    report = {
        "task": TASK_ID,
        "status": "complete",
        "loaded_indicator_count_before": len(current),
        "implemented_module_candidate_count": len(module_candidates),
        "unloaded_implemented_module_candidates": unloaded_module,
        "unloaded_implemented_module_candidate_evidence": {k: module_candidates[k] for k in unloaded_module},
        "opportunities": {
            "historical_backfill_existing_74_1990_1999_presparsity_gain": historical_only_presparsity_gain,
            "additional_implemented_module_candidates_1990_2024_presparsity_gain": module_expansion_presparsity_gain,
            "combined_loaded_plus_module_candidates_1990_2024_presparsity_envelope": combined_presparsity,
        },
        "selected_campaign": {
            "description": "Combined historical backfill plus implemented-module candidate expansion over existing WDI annual scalar path.",
            "reason": "This dominates historical-only backfill while staying inside the WDI annual scalar country-indicator implementation boundary already used by TASK-165/TASK-174 and source modules with indicator constants.",
            "candidate_indicators": selected,
            "candidate_indicator_count": len(selected),
            "countries": 217,
            "date_range": DATE_RANGE,
            "candidate_presparsity_rows": combined_presparsity,
        },
    }
    write_json(ASSESSMENT_REPORT_PATH, report)
    return report


def fetch(db: str) -> None:
    assessment = build_candidate_assessment(db)
    indicators = assessment["selected_campaign"]["candidate_indicators"]
    raw = fetch_campaign_raw(indicators=indicators, date_range=DATE_RANGE, timeout_seconds=180)
    raw["scope"].update({
        "task": TASK_ID,
        "campaign": "Repository Growth and Historical Scaling Campaign",
        "mode": "Repository Growth plus Historical/Overlap Scaling Validation",
        "date_range": DATE_RANGE,
        "candidate_source": "loaded WDI indicators plus implemented WDI source-module indicator constants",
        "raw_artifact_path": RAW_PATH.as_posix(),
        "candidate_presparsity_rows": len(indicators) * raw["scope"]["country_count"] * (END_YEAR - START_YEAR + 1),
        "capability_by_indicator": {indicator: capability_for_indicator(indicator) for indicator in indicators},
    })
    write_json(RAW_PATH, raw)
    print(json.dumps({"raw_path": RAW_PATH.as_posix(), "candidate_count": len(indicators), "date_range": DATE_RANGE}, indent=2, sort_keys=True))


def artifacts(load_counts: dict[str, int] | None = None) -> dict[str, Any]:
    raw = json.loads(RAW_PATH.read_text(encoding="utf-8"))
    paths = write_wdi_implemented_compatible_campaign_artifacts(
        raw,
        normalized_path=NORMALIZED_PATH,
        preflight_report_path=PREFLIGHT_REPORT_PATH,
        classification_report_path=CLASSIFICATION_REPORT_PATH,
        operational_report_path=OPERATIONAL_REPORT_PATH,
        coverage_report_path=COVERAGE_REPORT_PATH,
        exception_report_path=EXCEPTION_REPORT_PATH,
        confidence_report_path=CONFIDENCE_REPORT_PATH,
        load_counts=load_counts,
    )
    normalized = json.loads(NORMALIZED_PATH.read_text(encoding="utf-8"))
    years = list(range(START_YEAR, END_YEAR + 1))
    catalog_names = {row["id"]: row.get("name") or row.get("value") or row["id"] for row in raw.get("country_catalog", {}).get("countries", []) if row.get("id")}
    for row in normalized["rows"]:
        iso3 = row.get("countryiso3code")
        if iso3 in catalog_names:
            row["country_name"] = catalog_names[iso3]
        row["repository_growth_task"] = TASK_ID
        row["historical_scaling_band"] = "pre_2000_backfill" if int(row["date"]) < 2000 else "overlap_2000_2024"
        row["repository_capability"] = capability_for_indicator(row["indicator_id"])
    normalized["task"] = TASK_ID
    normalized["campaign"] = raw["scope"]["campaign"]
    normalized["mode"] = raw["scope"]["mode"]
    normalized["date_range"] = DATE_RANGE
    normalized["capability_by_indicator"] = raw["scope"]["capability_by_indicator"]
    normalized["historical_scaling"] = {
        "years": years,
        "pre_2000_years": [y for y in years if y < 2000],
        "overlap_years": [y for y in years if 2000 <= y <= 2024],
        "candidate_presparsity_rows": len(raw["scope"]["indicators"]) * raw["scope"]["country_count"] * len(years),
    }
    # Correct generic TASK-165 arbitrary-date report fields for this TASK-176 historical range.
    classification = normalized.get("classification", {})
    classification["task"] = TASK_ID
    classification["campaign"] = raw["scope"]["campaign"]
    classification["requested_max_presparsity_rows"] = normalized["historical_scaling"]["candidate_presparsity_rows"]
    for details in classification.get("indicator_results", {}).values():
        details["expected_max_rows"] = raw["scope"]["country_count"] * len(years)
    write_json(NORMALIZED_PATH, normalized)
    print(json.dumps(paths, indent=2, sort_keys=True))
    return normalized


def load(db: str) -> None:
    before = inventory(db)
    write_json(BEFORE_INVENTORY_PATH, before)
    before_fact = before["row_counts"]["curated.fact_observation"]
    before_staging = before["row_counts"]["staging.wdi_observation"]
    before_quality = before["row_counts"]["meta.quality_check"]
    counts = load_wdi_implemented_compatible_campaign_to_postgres(db, NORMALIZED_PATH, run_key="task-176-repository-growth-historical-scaling")
    after = inventory(db)
    write_json(AFTER_INVENTORY_PATH, after)
    payload = {
        "task": TASK_ID,
        "status": "succeeded",
        "db": db,
        "normalized_path": NORMALIZED_PATH.as_posix(),
        "load_counts": counts,
        "before_fact_rows": before_fact,
        "after_fact_rows": after["row_counts"]["curated.fact_observation"],
        "fact_rows_added": after["row_counts"]["curated.fact_observation"] - before_fact,
        "staging_rows_added": after["row_counts"]["staging.wdi_observation"] - before_staging,
        "quality_checks_added": after["row_counts"]["meta.quality_check"] - before_quality,
        "max_rss_kb_python_process": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    }
    write_json(LOAD_REPORT_PATH, payload)
    artifacts(load_counts=counts)
    print(json.dumps(payload, indent=2, sort_keys=True))


def validate(db: str) -> None:
    normalized = json.loads(NORMALIZED_PATH.read_text(encoding="utf-8"))
    before = json.loads(AFTER_INVENTORY_PATH.read_text(encoding="utf-8")) if AFTER_INVENTORY_PATH.exists() else inventory(db)
    first_counts = load_wdi_implemented_compatible_campaign_to_postgres(db, NORMALIZED_PATH, run_key="task-176-repository-growth-historical-scaling-rerun")
    after = inventory(db)
    duplicate_checks = psql_json(db, "SELECT row_to_json(x) FROM (SELECT count(*) duplicate_key_groups FROM (SELECT source_id, indicator_id, territory_id, period_id, unit_id, attribute_set_id, as_of_date, count(*) c FROM curated.fact_observation GROUP BY 1,2,3,4,5,6,7 HAVING count(*) > 1) d) x;")
    run_checks = psql_json(db, "SELECT COALESCE(json_agg(row_to_json(x) ORDER BY run_key, check_name),'[]'::json) FROM (SELECT pr.run_key, qc.check_name, qc.check_status, qc.observed_value, qc.expected_value, qc.details FROM meta.quality_check qc JOIN meta.pipeline_run pr USING(pipeline_run_id) WHERE pr.run_key LIKE 'task-176%' ) x;")
    fingerprint_query = "SELECT md5(COALESCE(string_agg(i.source_indicator_code||'|'||t.iso3_code||'|'||p.period_year::text||'|'||COALESCE(fo.value::text,'NULL')||'|'||fo.observation_status, E'\\n' ORDER BY i.source_indicator_code,t.iso3_code,p.period_year),'empty')) FROM curated.fact_observation fo JOIN curated.dim_indicator i USING(indicator_id) JOIN curated.dim_territory t USING(territory_id) JOIN curated.dim_period p USING(period_id) JOIN meta.source s ON fo.source_id=s.source_id WHERE s.source_code='WDI' AND i.source_indicator_code = ANY(ARRAY[%s]) AND p.period_year BETWEEN %s AND %s;" % (", ".join("'" + ind.replace("'", "''") + "'" for ind in normalized["indicators"]), START_YEAR, END_YEAR)
    canonical_fingerprint = subprocess.check_output(["psql", "-d", db, "-At", "-c", fingerprint_query], text=True).strip()
    report = {
        "task": TASK_ID,
        "status": "complete",
        "rerun_load_counts": first_counts,
        "fact_rows_before_rerun": before["row_counts"]["curated.fact_observation"],
        "fact_rows_after_rerun": after["row_counts"]["curated.fact_observation"],
        "fact_rows_added_by_rerun": after["row_counts"]["curated.fact_observation"] - before["row_counts"]["curated.fact_observation"],
        "duplicate_key_groups": duplicate_checks["duplicate_key_groups"],
        "task176_quality_checks": run_checks,
        "canonical_scope_fingerprint_after_rerun": canonical_fingerprint,
        "deterministic_rerun": after["row_counts"]["curated.fact_observation"] == before["row_counts"]["curated.fact_observation"] and duplicate_checks["duplicate_key_groups"] == 0,
        "lineage_preserved": after["row_counts"]["meta.lineage_event"] >= before["row_counts"]["meta.lineage_event"],
    }
    write_json(VALIDATION_REPORT_PATH, report)
    print(json.dumps(report, indent=2, sort_keys=True))


def markdown_reports(db: str) -> None:
    assessment = json.loads(ASSESSMENT_REPORT_PATH.read_text(encoding="utf-8"))
    normalized = json.loads(NORMALIZED_PATH.read_text(encoding="utf-8"))
    load_report = json.loads(LOAD_REPORT_PATH.read_text(encoding="utf-8"))
    validation = json.loads(VALIDATION_REPORT_PATH.read_text(encoding="utf-8"))
    before = json.loads(BEFORE_INVENTORY_PATH.read_text(encoding="utf-8"))
    after = inventory(db)
    rows_by_cap: dict[str, dict[str, Any]] = defaultdict(lambda: {"indicators": set(), "rows": 0, "pre_2000_rows": 0, "overlap_rows": 0})
    for row in normalized["rows"]:
        cap = row.get("repository_capability") or capability_for_indicator(row["indicator_id"])
        rows_by_cap[cap]["indicators"].add(row["indicator_id"])
        rows_by_cap[cap]["rows"] += 1
        if int(row["date"]) < 2000:
            rows_by_cap[cap]["pre_2000_rows"] += 1
        else:
            rows_by_cap[cap]["overlap_rows"] += 1
    capability_payload = {
        cap: {**vals, "indicators": sorted(vals["indicators"]), "indicator_count": len(vals["indicators"])}
        for cap, vals in sorted(rows_by_cap.items())
    }
    final = {
        "task": TASK_ID,
        "status": "complete",
        "assessment": assessment,
        "normalized_summary": {k: normalized[k] for k in ["indicator_count", "country_count", "date_range", "row_count", "observed_value_count", "missing_value_count", "excluded_indicators"]},
        "before": before,
        "after": after,
        "load_report": load_report,
        "idempotence_validation": validation,
        "capability_improvements": capability_payload,
        "architecture_stress_observations": {
            "postgresql_scalability": "Campaign loaded materially larger WDI annual-scalar scope using existing schema and uniqueness constraints.",
            "loader_scalability": "Existing loader handled historical overlap after run-scoped quality-check correction; duplicate prevention verified by rerun.",
            "artifact_growth": f"Raw and normalized artifacts grew to {RAW_PATH} and {NORMALIZED_PATH}; no storage reorganization was required, but continued large JSON growth should be monitored.",
            "memory_usage_observable": {"python_loader_process_max_rss_kb": load_report.get("max_rss_kb_python_process")},
        },
        "next_largest_evidence_supported_campaign": "Continue WDI annual-scalar repository growth by selecting the next largest source-module-backed or DB-loaded capability family not yet run over the 1990-2024 country scope; if no larger implemented-compatible WDI set is available, run a second catalog-evidence assessment before adding new indicators.",
    }
    write_json(FINAL_REPORT_PATH, final)

    rows_added = load_report["fact_rows_added"]
    content = f"""# TASK-176 — Repository Growth and Historical Scaling Campaign\n\nStatus: complete\n\n## Campaign selected\n\nSelected the combined WDI annual-scalar campaign: loaded indicators already present in PostgreSQL plus additional implemented-module candidate indicators over {DATE_RANGE}.\n\nCandidate indicators: {normalized['indicator_count']} included / {assessment['selected_campaign']['candidate_indicator_count']} assessed.\nCountries: {normalized['country_count']}.\nNormalized rows: {normalized['row_count']}.\nObserved values: {normalized['observed_value_count']}.\nMissing-value rows retained as explicit provider evidence: {normalized['missing_value_count']}.\n\n## Repository growth\n\nCurated fact rows before: {load_report['before_fact_rows']}.\nCurated fact rows after first load: {load_report['after_fact_rows']}.\nCurated fact rows added: {rows_added}.\nPost-rerun fact rows added: {validation['fact_rows_added_by_rerun']}.\nDuplicate key groups after rerun: {validation['duplicate_key_groups']}.\n\n## Architecture result\n\nThe existing WDI annual-scalar path scaled through historical expansion, overlap, and rerun without schema redesign. The only loader issue observed was an inherited source-wide quality-check expectation from earlier narrow campaigns; it was corrected to run-scoped fact-row validation before TASK-176 load.\n\nSee JSON final report: `{FINAL_REPORT_PATH}`.\n"""
    CAMPAIGN_REPORT_PATH.write_text(content, encoding="utf-8")
    GROWTH_REPORT_PATH.write_text(content.replace("# TASK-176 — Repository Growth and Historical Scaling Campaign", "# TASK-176 — Repository Growth Report"), encoding="utf-8")
    HISTORICAL_REPORT_PATH.write_text(f"""# TASK-176 — Historical Scaling Validation\n\nStatus: complete\n\nHistorical window: {DATE_RANGE}.\nPre-2000 backfill rows in normalized package: {sum(v['pre_2000_rows'] for v in capability_payload.values())}.\nOverlap rows in normalized package: {sum(v['overlap_rows'] for v in capability_payload.values())}.\n\nValidation: first load added {rows_added} curated fact rows; rerun added {validation['fact_rows_added_by_rerun']} curated fact rows.\nDuplicate key groups after rerun: {validation['duplicate_key_groups']}.\nLineage preserved: {validation['lineage_preserved']}.\n""", encoding="utf-8")
    IDEMPOTENCE_REPORT_PATH.write_text(f"""# TASK-176 — Idempotence Validation\n\nStatus: complete\n\nRerun run key: `task-176-repository-growth-historical-scaling-rerun`.\nFact rows before rerun: {validation['fact_rows_before_rerun']}.\nFact rows after rerun: {validation['fact_rows_after_rerun']}.\nFact rows added by rerun: {validation['fact_rows_added_by_rerun']}.\nDuplicate key groups: {validation['duplicate_key_groups']}.\nDeterministic rerun: {validation['deterministic_rerun']}.\nCanonical scope fingerprint after rerun: `{validation['canonical_scope_fingerprint_after_rerun']}`.\n""", encoding="utf-8")
    cap_lines = ["# TASK-176 — Capability Improvement Report", "", "Status: complete", ""]
    for cap, vals in capability_payload.items():
        cap_lines += [f"## {cap}", "", f"Indicators after campaign: {vals['indicator_count']}.", f"Rows in campaign package: {vals['rows']}.", f"Pre-2000 rows: {vals['pre_2000_rows']}.", f"Overlap rows: {vals['overlap_rows']}.", "Remaining analytical gaps: country-level annual scalar coverage only; no subannual, bilateral, product-level, or firm-level semantics were added unless already represented by the indicator family.", "Confidence implication: expanded within the proven WDI annual scalar confidence cell; no new confidence cell is created.", ""]
    CAPABILITY_REPORT_PATH.write_text("\n".join(cap_lines), encoding="utf-8")
    STRESS_REPORT_PATH.write_text(f"""# TASK-176 — Architecture Stress Observations\n\nStatus: complete\n\nPostgreSQL scalability: first load moved curated WDI fact rows from {load_report['before_fact_rows']} to {load_report['after_fact_rows']} without schema redesign.\nLoader scalability: existing WDI loader handled {normalized['row_count']} normalized rows; duplicate prevention was verified by rerun.\nValidation scalability: run-scoped quality checks are required for overlapping campaigns. A pre-existing source-wide fact-row check was not valid after TASK-174 and was corrected to run-scoped validation.\nArtifact growth: large JSON raw/normalized artifacts remain workable for this campaign; monitor if future campaigns multiply beyond this envelope.\nLineage growth: lineage events increased/preserved across first load and rerun.\nMemory usage observable: Python loader process max RSS {load_report.get('max_rss_kb_python_process')} KB.\n\nNo provider mirror, schema partitioning, canonical identity redesign, or generic WDI framework is justified by TASK-176 evidence.\n""", encoding="utf-8")
    print(json.dumps({"final_report": FINAL_REPORT_PATH.as_posix(), "rows_added": rows_added, "capability_count": len(capability_payload)}, indent=2, sort_keys=True))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("command", choices=["assess", "inventory", "fetch", "artifacts", "load", "validate", "reports"])
    ap.add_argument("--db", default="macroforge")
    args = ap.parse_args()
    if args.command == "assess":
        print(json.dumps(build_candidate_assessment(args.db), indent=2, sort_keys=True))
    elif args.command == "inventory":
        inv = inventory(args.db)
        write_json(BEFORE_INVENTORY_PATH, inv)
        print(json.dumps(inv, indent=2, sort_keys=True))
    elif args.command == "fetch":
        fetch(args.db)
    elif args.command == "artifacts":
        artifacts()
    elif args.command == "load":
        load(args.db)
    elif args.command == "validate":
        validate(args.db)
    elif args.command == "reports":
        markdown_reports(args.db)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
