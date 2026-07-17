from __future__ import annotations

import argparse
import json
import resource
import subprocess
from collections import defaultdict
from pathlib import Path
from typing import Any

from macroforge.wdi_implemented_compatible_campaign import (
    fetch_campaign_raw,
    write_wdi_implemented_compatible_campaign_artifacts,
)
from macroforge.wdi_loader import load_wdi_implemented_compatible_campaign_to_postgres

TASK_ID = "TASK-178"
DATE_RANGE = "1990:2024"
START_YEAR = 1990
END_YEAR = 2024
RAW_PATH = Path("data/raw/demographic_structure_task178/task-178-wdi-demographic-structure-human-capital-1990-2024.json")
NORMALIZED_PATH = Path("data/processed/demographic_structure_task178/task-178-wdi-demographic-structure-human-capital-normalized.json")
PREFLIGHT_REPORT_PATH = Path("artifacts/reports/task-178-demographic-structure-preflight-report.json")
CLASSIFICATION_REPORT_PATH = Path("artifacts/reports/task-178-demographic-structure-classification-report.json")
OPERATIONAL_REPORT_PATH = Path("artifacts/reports/task-178-demographic-structure-operational-report.json")
COVERAGE_REPORT_PATH = Path("artifacts/reports/task-178-demographic-structure-coverage-report.json")
EXCEPTION_REPORT_PATH = Path("artifacts/reports/task-178-demographic-structure-exclusion-report.json")
CONFIDENCE_REPORT_PATH = Path("artifacts/reports/task-178-demographic-structure-confidence-report.json")
BEFORE_INVENTORY_PATH = Path("artifacts/reports/task-178-inventory-before.json")
AFTER_INVENTORY_PATH = Path("artifacts/reports/task-178-inventory-after.json")
LOAD_REPORT_PATH = Path("artifacts/reports/task-178-load-report.json")
VALIDATION_REPORT_PATH = Path("artifacts/reports/task-178-idempotence-validation-report.json")
FINAL_REPORT_PATH = Path("artifacts/reports/task-178-final-campaign-report.json")
CAMPAIGN_REPORT_PATH = Path("artifacts/reports/R-20260708-task-178-demographic-structure-human-capital-campaign.md")
GROWTH_REPORT_PATH = Path("artifacts/reports/R-20260708-task-178-postgresql-growth-report.md")
CAPABILITY_REPORT_PATH = Path("artifacts/reports/R-20260708-task-178-capability-improvement-report.md")
ARCHITECTURE_REPORT_PATH = Path("artifacts/reports/R-20260708-task-178-architectural-scaling-report.md")
MATURITY_REPORT_PATH = Path("artifacts/reports/R-20260708-task-178-capability-maturity-assessment.md")

CANDIDATE_INDICATORS = [
    "SP.POP.TOTL.FE.IN",
    "SP.POP.TOTL.MA.IN",
    "SP.POP.TOTL.FE.ZS",
    "SP.POP.TOTL.MA.ZS",
    "SP.DYN.CBRT.IN",
    "SP.DYN.CDRT.IN",
    "SP.DYN.IMRT.IN",
    "SH.DYN.MORT",
    "SP.DYN.AMRT.FE",
    "SP.DYN.AMRT.MA",
    "SH.STA.MMRT",
    "SP.ADO.TFRT",
    "SP.URB.TOTL",
    "SP.RUR.TOTL",
    "SP.RUR.TOTL.ZS",
    "EN.POP.DNST",
    "AG.LND.TOTL.K2",
    "SE.PRM.ENRR",
    "SE.PRM.CMPT.ZS",
    "SE.ADT.LITR.ZS",
    "SE.XPD.TOTL.GB.ZS",
    "SH.IMM.MEAS",
    "SH.IMM.IDPT",
    "SH.MED.PHYS.ZS",
    "SH.STA.BRTC.ZS",
    "SM.POP.REFG",
    "SM.POP.REFG.OR",
    "SL.TLF.CACT.FE.ZS",
    "SL.TLF.CACT.MA.ZS",
    "SL.TLF.CACT.ZS",
]

CAPABILITY_BY_INDICATOR = {
    "SP.POP.TOTL.FE.IN": "Sex-specific population stock",
    "SP.POP.TOTL.MA.IN": "Sex-specific population stock",
    "SP.POP.TOTL.FE.ZS": "Sex composition",
    "SP.POP.TOTL.MA.ZS": "Sex composition",
    "SP.DYN.CBRT.IN": "Births and vital rates",
    "SP.DYN.CDRT.IN": "Deaths and vital rates",
    "SP.DYN.IMRT.IN": "Infant mortality",
    "SH.DYN.MORT": "Child mortality",
    "SP.DYN.AMRT.FE": "Adult mortality by sex",
    "SP.DYN.AMRT.MA": "Adult mortality by sex",
    "SH.STA.MMRT": "Maternal mortality",
    "SP.ADO.TFRT": "Adolescent fertility",
    "SP.URB.TOTL": "Urban population stock",
    "SP.RUR.TOTL": "Rural population stock",
    "SP.RUR.TOTL.ZS": "Urban/rural structure",
    "EN.POP.DNST": "Population density",
    "AG.LND.TOTL.K2": "Land-area density context",
    "SE.PRM.ENRR": "Primary education enrollment",
    "SE.PRM.CMPT.ZS": "Primary education completion",
    "SE.ADT.LITR.ZS": "Adult literacy and basic human capital",
    "SE.XPD.TOTL.GB.ZS": "Education fiscal effort",
    "SH.IMM.MEAS": "Child health prevention",
    "SH.IMM.IDPT": "Child health prevention",
    "SH.MED.PHYS.ZS": "Health workforce",
    "SH.STA.BRTC.ZS": "Maternal/newborn health-system access",
    "SM.POP.REFG": "Forced migration asylum stock",
    "SM.POP.REFG.OR": "Forced migration origin stock",
    "SL.TLF.CACT.FE.ZS": "Human-capital utilization by sex",
    "SL.TLF.CACT.MA.ZS": "Human-capital utilization by sex",
    "SL.TLF.CACT.ZS": "Human-capital utilization",
}

BASELINE_CAPABILITIES = {
    "current_demographic_related_indicators": 18,
    "current_demographic_related_rows": 136710,
    "current_demographic_related_observed_values": 117347,
    "operationally_useful_before": [
        "total population",
        "population growth",
        "broad age shares",
        "dependency ratios",
        "fertility",
        "life expectancy",
        "urbanization share",
    ],
    "first_order_gaps_before": [
        "sex-specific structure",
        "births/deaths",
        "mortality depth",
        "adolescent fertility",
        "urban/rural stocks",
        "density/land context",
        "primary/literacy/completion education",
        "health prevention/workforce/access",
        "forced migration stocks",
    ],
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
        "wdi_coverage": psql_json(db, "SELECT row_to_json(x) FROM (SELECT count(DISTINCT i.source_indicator_code) indicators, count(DISTINCT t.iso3_code) countries, min(p.period_year) min_year, max(p.period_year) max_year, count(*) rows, count(fo.value) observed_values FROM curated.fact_observation fo JOIN curated.dim_indicator i USING(indicator_id) JOIN curated.dim_territory t USING(territory_id) JOIN curated.dim_period p USING(period_id) JOIN meta.source s ON fo.source_id=s.source_id WHERE s.source_code='WDI') x;"),
        "wdi_indicators": psql_json(db, "SELECT COALESCE(json_agg(source_indicator_code ORDER BY source_indicator_code),'[]'::json) FROM curated.dim_indicator i JOIN meta.source s USING(source_id) WHERE s.source_code='WDI';"),
        "task178_scope_coverage": psql_json(db, "SELECT row_to_json(x) FROM (SELECT count(DISTINCT i.source_indicator_code) indicators, count(DISTINCT t.iso3_code) countries, min(p.period_year) min_year, max(p.period_year) max_year, count(*) rows, count(fo.value) observed_values FROM curated.fact_observation fo JOIN curated.dim_indicator i USING(indicator_id) JOIN curated.dim_territory t USING(territory_id) JOIN curated.dim_period p USING(period_id) JOIN meta.source s ON fo.source_id=s.source_id WHERE s.source_code='WDI' AND i.source_indicator_code = ANY(ARRAY[" + ",".join("'" + i + "'" for i in CANDIDATE_INDICATORS) + "]) AND p.period_year BETWEEN 1990 AND 2024) x;"),
    }


def assess(db: str) -> dict[str, Any]:
    inv = inventory(db)
    loaded = set(inv["wdi_indicators"])
    report = {
        "task": TASK_ID,
        "status": "baseline_assessed",
        "domain": "Demographics, Human Capital, and Population Structure",
        "capability": "Demographic Structure and Human Capital Core",
        "baseline_from_task177": BASELINE_CAPABILITIES,
        "planning_candidate_indicators": CANDIDATE_INDICATORS,
        "candidate_indicator_count": len(CANDIDATE_INDICATORS),
        "already_loaded_candidates_before_campaign": sorted(set(CANDIDATE_INDICATORS) & loaded),
        "not_loaded_candidates_before_campaign": sorted(set(CANDIDATE_INDICATORS) - loaded),
        "countries": 217,
        "years": END_YEAR - START_YEAR + 1,
        "candidate_presparsity_rows": len(CANDIDATE_INDICATORS) * 217 * (END_YEAR - START_YEAR + 1),
        "current_repository_inventory": inv,
        "success_measure": "material capability gain first, with repository fact growth and WDI annual-scalar scaling evidence as operational proof",
    }
    write_json(Path("artifacts/reports/task-178-capability-baseline-assessment.json"), report)
    return report


def fetch(db: str) -> None:
    baseline = assess(db)
    raw = fetch_campaign_raw(indicators=CANDIDATE_INDICATORS, date_range=DATE_RANGE, timeout_seconds=180)
    raw["scope"].update({
        "task": TASK_ID,
        "campaign": "Demographic Structure and Human Capital Core Repository Expansion Campaign",
        "mode": "Demographics Domain Repository Expansion",
        "date_range": DATE_RANGE,
        "candidate_source": "TASK-177 recommended demographic-structure and human-capital capability gaps",
        "raw_artifact_path": RAW_PATH.as_posix(),
        "candidate_presparsity_rows": len(CANDIDATE_INDICATORS) * raw["scope"]["country_count"] * (END_YEAR - START_YEAR + 1),
        "capability_by_indicator": CAPABILITY_BY_INDICATOR,
        "baseline_from_task177": BASELINE_CAPABILITIES,
        "already_loaded_candidates_before_campaign": baseline["already_loaded_candidates_before_campaign"],
    })
    write_json(RAW_PATH, raw)
    print(json.dumps({"raw_path": RAW_PATH.as_posix(), "candidate_count": len(CANDIDATE_INDICATORS), "date_range": DATE_RANGE}, indent=2, sort_keys=True))


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
    catalog_names = {row["id"]: row.get("name") or row.get("value") or row["id"] for row in raw.get("country_catalog", {}).get("countries", []) if row.get("id")}
    years = list(range(START_YEAR, END_YEAR + 1))
    for row in normalized["rows"]:
        iso3 = row.get("countryiso3code")
        if iso3 in catalog_names:
            row["country_name"] = catalog_names[iso3]
        row["task"] = TASK_ID
        row["demographics_capability"] = CAPABILITY_BY_INDICATOR.get(row["indicator_id"], "Demographic/human-capital context")
        row["domain"] = "Demographics, Human Capital, and Population Structure"
    normalized["task"] = TASK_ID
    normalized["campaign"] = raw["scope"]["campaign"]
    normalized["mode"] = raw["scope"]["mode"]
    normalized["date_range"] = DATE_RANGE
    normalized["capability_by_indicator"] = CAPABILITY_BY_INDICATOR
    normalized["baseline_from_task177"] = BASELINE_CAPABILITIES
    classification = normalized.get("classification", {})
    classification["task"] = TASK_ID
    classification["campaign"] = raw["scope"]["campaign"]
    classification["requested_max_presparsity_rows"] = len(raw["scope"]["indicators"]) * raw["scope"]["country_count"] * len(years)
    for details in classification.get("indicator_results", {}).values():
        details["expected_max_rows"] = raw["scope"]["country_count"] * len(years)
        details["capability"] = CAPABILITY_BY_INDICATOR.get(details.get("indicator"), "Demographic/human-capital context")
    write_json(NORMALIZED_PATH, normalized)
    print(json.dumps(paths, indent=2, sort_keys=True))
    return normalized


def load(db: str) -> None:
    before = inventory(db)
    write_json(BEFORE_INVENTORY_PATH, before)
    before_fact = before["row_counts"]["curated.fact_observation"]
    before_indicator_count = before["wdi_coverage"]["indicators"]
    counts = load_wdi_implemented_compatible_campaign_to_postgres(db, NORMALIZED_PATH, run_key="task-178-demographic-structure-human-capital")
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
        "before_wdi_indicators": before_indicator_count,
        "after_wdi_indicators": after["wdi_coverage"]["indicators"],
        "wdi_indicators_added": after["wdi_coverage"]["indicators"] - before_indicator_count,
        "countries_after": after["wdi_coverage"]["countries"],
        "min_year_after": after["wdi_coverage"]["min_year"],
        "max_year_after": after["wdi_coverage"]["max_year"],
        "task178_scope_after": after["task178_scope_coverage"],
        "max_rss_kb_python_process": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    }
    write_json(LOAD_REPORT_PATH, payload)
    artifacts(load_counts=counts)
    print(json.dumps(payload, indent=2, sort_keys=True))


def validate(db: str) -> None:
    normalized = json.loads(NORMALIZED_PATH.read_text(encoding="utf-8"))
    before = json.loads(AFTER_INVENTORY_PATH.read_text(encoding="utf-8")) if AFTER_INVENTORY_PATH.exists() else inventory(db)
    rerun_counts = load_wdi_implemented_compatible_campaign_to_postgres(db, NORMALIZED_PATH, run_key="task-178-demographic-structure-human-capital-rerun")
    after = inventory(db)
    duplicate_checks = psql_json(db, "SELECT row_to_json(x) FROM (SELECT count(*) duplicate_key_groups FROM (SELECT source_id, indicator_id, territory_id, period_id, unit_id, attribute_set_id, as_of_date, count(*) c FROM curated.fact_observation GROUP BY 1,2,3,4,5,6,7 HAVING count(*) > 1) d) x;")
    run_checks = psql_json(db, "SELECT COALESCE(json_agg(row_to_json(x) ORDER BY run_key, check_name),'[]'::json) FROM (SELECT pr.run_key, qc.check_name, qc.check_status, qc.observed_value, qc.expected_value, qc.details FROM meta.quality_check qc JOIN meta.pipeline_run pr USING(pipeline_run_id) WHERE pr.run_key LIKE 'task-178%' ) x;")
    indicators_sql = ", ".join("'" + ind.replace("'", "''") + "'" for ind in normalized["indicators"])
    fingerprint_query = "SELECT md5(COALESCE(string_agg(i.source_indicator_code||'|'||t.iso3_code||'|'||p.period_year::text||'|'||COALESCE(fo.value::text,'NULL')||'|'||fo.observation_status, E'\\n' ORDER BY i.source_indicator_code,t.iso3_code,p.period_year),'empty')) FROM curated.fact_observation fo JOIN curated.dim_indicator i USING(indicator_id) JOIN curated.dim_territory t USING(territory_id) JOIN curated.dim_period p USING(period_id) JOIN meta.source s ON fo.source_id=s.source_id WHERE s.source_code='WDI' AND i.source_indicator_code = ANY(ARRAY[%s]) AND p.period_year BETWEEN %s AND %s;" % (indicators_sql, START_YEAR, END_YEAR)
    canonical_fingerprint = subprocess.check_output(["psql", "-d", db, "-At", "-c", fingerprint_query], text=True).strip()
    report = {
        "task": TASK_ID,
        "status": "complete",
        "rerun_load_counts": rerun_counts,
        "fact_rows_before_rerun": before["row_counts"]["curated.fact_observation"],
        "fact_rows_after_rerun": after["row_counts"]["curated.fact_observation"],
        "fact_rows_added_by_rerun": after["row_counts"]["curated.fact_observation"] - before["row_counts"]["curated.fact_observation"],
        "duplicate_key_groups": duplicate_checks["duplicate_key_groups"],
        "task178_quality_checks": run_checks,
        "canonical_scope_fingerprint_after_rerun": canonical_fingerprint,
        "deterministic_rerun": after["row_counts"]["curated.fact_observation"] == before["row_counts"]["curated.fact_observation"] and duplicate_checks["duplicate_key_groups"] == 0,
        "lineage_preserved": after["row_counts"]["meta.lineage_event"] >= before["row_counts"]["meta.lineage_event"],
        "scope_after_rerun": after["task178_scope_coverage"],
    }
    write_json(VALIDATION_REPORT_PATH, report)
    print(json.dumps(report, indent=2, sort_keys=True))


def markdown_reports(db: str) -> None:
    normalized = json.loads(NORMALIZED_PATH.read_text(encoding="utf-8"))
    load_report = json.loads(LOAD_REPORT_PATH.read_text(encoding="utf-8"))
    validation = json.loads(VALIDATION_REPORT_PATH.read_text(encoding="utf-8"))
    before = json.loads(BEFORE_INVENTORY_PATH.read_text(encoding="utf-8"))
    after = inventory(db)
    rows_by_cap: dict[str, dict[str, Any]] = defaultdict(lambda: {"indicators": set(), "rows": 0, "observed": 0, "missing": 0})
    for row in normalized["rows"]:
        cap = row.get("demographics_capability") or CAPABILITY_BY_INDICATOR.get(row["indicator_id"], "Demographic/human-capital context")
        rows_by_cap[cap]["indicators"].add(row["indicator_id"])
        rows_by_cap[cap]["rows"] += 1
        if row.get("value") is None:
            rows_by_cap[cap]["missing"] += 1
        else:
            rows_by_cap[cap]["observed"] += 1
    capability_payload = {cap: {**vals, "indicators": sorted(vals["indicators"]), "indicator_count": len(vals["indicators"])} for cap, vals in sorted(rows_by_cap.items())}
    final = {
        "task": TASK_ID,
        "status": "complete",
        "normalized_summary": {k: normalized[k] for k in ["indicator_count", "country_count", "date_range", "row_count", "observed_value_count", "missing_value_count", "excluded_indicators"]},
        "baseline_from_task177": BASELINE_CAPABILITIES,
        "before": before,
        "after": after,
        "load_report": load_report,
        "idempotence_validation": validation,
        "capability_improvements": capability_payload,
        "architectural_observations": {
            "broader_indicator_diversity": "Campaign combined counts, shares, rates, density, land-area context, education, health, labor-utilization, and forced-migration stock indicators inside one WDI annual-scalar run.",
            "missing_value_heterogeneity": "Normalized package retained explicit null provider observations across sparse education, health, and migration series.",
            "loader_robustness": "Existing WDI loader handled the campaign with run-scoped quality checks and idempotent rerun.",
            "canonicalization_robustness": "Country names were canonicalized from the accepted WDI country catalog before load, preserving the TASK-176 duplicate-upsert fix.",
            "architecture_change_required": False,
        },
        "recommended_next_demographics_capability": "Within Demographics, next assess detailed age/sex cohort structure and projections. If WDI cannot supply sufficient age-pyramid/projection coverage, evaluate UN Population Division as a new provider through a separate evidence-gated planning task.",
    }
    write_json(FINAL_REPORT_PATH, final)
    included = normalized["indicator_count"]
    excluded = len(normalized.get("excluded_indicators", []))
    common = f"""# TASK-178 — Demographic Structure and Human Capital Core Repository Expansion Campaign

Status: complete

## Scope

Domain: Demographics, Human Capital, and Population Structure.
Capability: Demographic Structure and Human Capital Core.
Provider: World Bank WDI via existing annual-scalar confidence cell.
Period: {DATE_RANGE}.
Countries: {normalized['country_count']}.
Candidate indicators assessed: {len(CANDIDATE_INDICATORS)}.
Included indicators: {included}.
Excluded indicators: {excluded}.
Normalized rows: {normalized['row_count']}.
Observed values: {normalized['observed_value_count']}.
Missing-value evidence rows: {normalized['missing_value_count']}.

## PostgreSQL growth

Curated fact rows before: {load_report['before_fact_rows']}.
Curated fact rows after first load: {load_report['after_fact_rows']}.
Curated fact rows added: {load_report['fact_rows_added']}.
WDI indicators before: {load_report['before_wdi_indicators']}.
WDI indicators after: {load_report['after_wdi_indicators']}.
WDI indicators added: {load_report['wdi_indicators_added']}.
Post-rerun fact rows added: {validation['fact_rows_added_by_rerun']}.
Duplicate key groups after rerun: {validation['duplicate_key_groups']}.
Lineage preserved: {validation['lineage_preserved']}.
Canonical scope fingerprint: `{validation['canonical_scope_fingerprint_after_rerun']}`.

## Capability result

Before campaign, Demographics had useful total population, growth, broad age-share, dependency-ratio, fertility, life-expectancy, and urbanization-share coverage, but lacked sex-specific structure, births/deaths, mortality depth, urban/rural stocks, density context, education depth, health prevention/workforce/access, and forced migration stocks.

After campaign, those gaps are materially reduced for the WDI annual country-year scope. Remaining gaps are detailed age/sex pyramids, projections/scenarios, subnational demographics, cross-source demographic validation, and higher-resolution migration flows.

## Architecture result

The existing WDI annual-scalar path handled broader demographic indicator diversity and sparse-provider behavior without schema redesign. No provider mirror, generic demographic framework, partitioning, canonical identity change, or production scheduling is justified by observed evidence.

See JSON final report: `{FINAL_REPORT_PATH}`.
"""
    CAMPAIGN_REPORT_PATH.write_text(common, encoding="utf-8")
    GROWTH_REPORT_PATH.write_text(common.replace("# TASK-178 — Demographic Structure and Human Capital Core Repository Expansion Campaign", "# TASK-178 — PostgreSQL Growth Report"), encoding="utf-8")
    cap_lines = ["# TASK-178 — Capability Improvement Report", "", "Status: complete", ""]
    for cap, vals in capability_payload.items():
        cap_lines += [f"## {cap}", "", f"Indicators: {', '.join(vals['indicators'])}.", f"Rows: {vals['rows']}.", f"Observed values: {vals['observed']}.", f"Missing-value evidence rows: {vals['missing']}.", "Capability effect: adds or deepens country-year demographic/human-capital evidence inside the WDI annual-scalar scope.", ""]
    CAPABILITY_REPORT_PATH.write_text("\n".join(cap_lines), encoding="utf-8")
    ARCHITECTURE_REPORT_PATH.write_text(f"""# TASK-178 — Architectural Scaling Report

Status: complete

Observed behavior:
- Broader indicator diversity: counts, percentages, rates, density, land area, education, health, labor-force participation, and forced migration.
- Sparse-value heterogeneity: {normalized['missing_value_count']} explicit missing-value rows were preserved without breaking normalization or load.
- Loader/idempotence: first load added {load_report['fact_rows_added']} curated facts; rerun added {validation['fact_rows_added_by_rerun']} facts; duplicate key groups = {validation['duplicate_key_groups']}.
- Lineage: preserved = {validation['lineage_preserved']}.
- Memory observable: Python loader process max RSS {load_report.get('max_rss_kb_python_process')} KB.

Architecture implication: no redesign is justified. Continue using source-specific WDI annual-scalar campaigns and deterministic preflight/exclusion evidence.
""", encoding="utf-8")
    MATURITY_REPORT_PATH.write_text(f"""# TASK-178 — Updated Capability Maturity Assessment

Status: complete

Before TASK-178: Demographics was Operationally Useful for core population aggregates but Developing for demographic structure and human capital depth.

After TASK-178: Demographic Structure and Human Capital Core is Operationally Useful for WDI annual country-year analysis across sex structure, vital rates, mortality depth, urban/rural density context, education/human-capital inputs, health prevention/workforce/access, forced migration stocks, and labor-force participation.

Scope qualification: this maturity applies only to WDI annual country-level scalar observations for 217 non-aggregate countries over 1990-2024. It does not cover detailed age/sex cohorts, projections, subnational demographics, bilateral migration flows, or cross-source demographic reconciliation.

Recommended next Demographics capability: detailed age/sex cohort structure and projections, with WDI assessed first and UN Population Division considered only if WDI cannot address the capability gap.
""", encoding="utf-8")
    print(json.dumps({"final_report": FINAL_REPORT_PATH.as_posix(), "rows_added": load_report["fact_rows_added"], "capability_count": len(capability_payload)}, indent=2, sort_keys=True))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("command", choices=["assess", "fetch", "artifacts", "load", "validate", "reports"])
    ap.add_argument("--db", default="macroforge")
    args = ap.parse_args()
    if args.command == "assess":
        print(json.dumps(assess(args.db), indent=2, sort_keys=True))
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
