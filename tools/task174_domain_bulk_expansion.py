from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any

from macroforge.wdi_implemented_compatible_campaign import (
    fetch_campaign_raw,
    normalize_wdi_implemented_compatible_campaign_raw,
    write_wdi_implemented_compatible_campaign_artifacts,
)
from macroforge.wdi_loader import load_wdi_implemented_compatible_campaign_to_postgres

TASK_ID = "TASK-174"
RAW_PATH = Path("data/raw/domain_bulk_expansion_task174/task-174-wdi-trade-finance-bulk-2000-2024.json")
NORMALIZED_PATH = Path("data/processed/domain_bulk_expansion_task174/task-174-wdi-trade-finance-bulk-normalized.json")
PREFLIGHT_REPORT_PATH = Path("artifacts/reports/task-174-domain-bulk-preflight-report.json")
CLASSIFICATION_REPORT_PATH = Path("artifacts/reports/task-174-domain-bulk-classification-report.json")
OPERATIONAL_REPORT_PATH = Path("artifacts/reports/task-174-domain-bulk-operational-expansion-report.json")
COVERAGE_REPORT_PATH = Path("artifacts/reports/task-174-domain-bulk-coverage-report.json")
EXCEPTION_REPORT_PATH = Path("artifacts/reports/task-174-domain-bulk-exclusion-report.json")
CONFIDENCE_REPORT_PATH = Path("artifacts/reports/task-174-domain-bulk-confidence-report.json")
LOAD_REPORT_PATH = Path("artifacts/reports/task-174-domain-bulk-load-report.json")
INVENTORY_REPORT_PATH = Path("artifacts/reports/task-174-domain-bulk-inventory-before.json")
FINAL_REPORT_PATH = Path("artifacts/reports/task-174-domain-bulk-final-report.json")
DATE_RANGE = "2000:2024"

TRADE_TOURISM_SUPPLY_CHAIN_INDICATORS = [
    "NE.EXP.GNFS.CD", "NE.IMP.GNFS.CD", "NE.EXP.GNFS.ZS", "NE.IMP.GNFS.ZS",
    "NE.TRD.GNFS.ZS", "TX.VAL.MRCH.CD.WT", "TM.VAL.MRCH.CD.WT",
    "TX.VAL.SERV.CD.WT", "TM.VAL.SERV.CD.WT", "TX.VAL.TRAN.ZS.WT", "TM.VAL.TRAN.ZS.WT",
    "TX.VAL.INSF.ZS.WT", "TM.VAL.INSF.ZS.WT", "TX.VAL.ICTG.ZS.UN", "TM.VAL.ICTG.ZS.UN",
    "ST.INT.ARVL", "ST.INT.RCPT.CD", "ST.INT.XPND.CD", "ST.INT.RCPT.XP.ZS", "ST.INT.XPND.MP.ZS",
    "LP.LPI.OVRL.XQ", "LP.LPI.INFR.XQ", "LP.LPI.LOGS.XQ", "LP.LPI.CUST.XQ", "LP.LPI.TIME.XQ", "LP.LPI.TRAC.XQ", "LP.LPI.ITRN.XQ",
]

MONETARY_BANKING_CREDIT_INDICATORS = [
    "FS.AST.PRVT.GD.ZS", "FD.AST.PRVT.GD.ZS", "FS.AST.DOMS.GD.ZS", "FM.LBL.BMNY.GD.ZS",
    "FM.LBL.BMNY.CN", "FM.LBL.BMNY.ZG", "CM.MKT.LCAP.GD.ZS", "CM.MKT.LDOM.NO", "CM.MKT.TRAD.GD.ZS",
    "FR.INR.DPST", "FR.INR.LEND", "FR.INR.LNDP", "FR.INR.RINR", "FR.INR.RISK",
    "FB.AST.NPER.ZS", "FB.BNK.CAPA.ZS", "FB.BNK.CAR.ZS", "FB.BNK.LQRS.ZS", "FB.BNK.ZSCORE",
    "FB.CBK.BRCH.P5", "FB.ATM.TOTL.P5", "FB.CBK.DPTR.P3", "FB.CBK.BRWR.P3",
    "GFDD.DI.01", "GFDD.DI.02", "GFDD.DI.05", "GFDD.EI.02", "GFDD.OI.02",
]

INDICATOR_DOMAIN = {code: "International Trade, Tourism, and Supply Chains" for code in TRADE_TOURISM_SUPPLY_CHAIN_INDICATORS}
INDICATOR_DOMAIN.update({code: "Monetary, Banking, Credit, and Financial Intermediation" for code in MONETARY_BANKING_CREDIT_INDICATORS})
CANDIDATE_INDICATORS = sorted(INDICATOR_DOMAIN)


def psql_json(db: str, sql: str) -> Any:
    out = subprocess.check_output(["psql", "-d", db, "-At", "-c", sql], text=True)
    return json.loads(out or "null")


def inventory(db: str) -> dict[str, Any]:
    return {
        "tables": psql_json(db, "SELECT COALESCE(json_agg(schemaname||'.'||tablename ORDER BY schemaname, tablename),'[]'::json) FROM pg_tables WHERE schemaname IN ('staging','curated','meta');"),
        "row_counts": psql_json(db, "SELECT json_object_agg(table_name, row_count) FROM (SELECT 'staging.wdi_observation' table_name, count(*) row_count FROM staging.wdi_observation UNION ALL SELECT 'curated.fact_observation', count(*) FROM curated.fact_observation UNION ALL SELECT 'curated.dim_indicator', count(*) FROM curated.dim_indicator UNION ALL SELECT 'curated.dim_territory', count(*) FROM curated.dim_territory UNION ALL SELECT 'curated.dim_period', count(*) FROM curated.dim_period UNION ALL SELECT 'meta.source', count(*) FROM meta.source UNION ALL SELECT 'meta.dataset_release', count(*) FROM meta.dataset_release UNION ALL SELECT 'meta.pipeline_run', count(*) FROM meta.pipeline_run UNION ALL SELECT 'meta.lineage_event', count(*) FROM meta.lineage_event UNION ALL SELECT 'meta.quality_check', count(*) FROM meta.quality_check) s;"),
        "sources": psql_json(db, "SELECT COALESCE(json_agg(row_to_json(x) ORDER BY source_code),'[]'::json) FROM (SELECT s.source_code, s.source_name, count(DISTINCT dr.provider_dataset_code) dataset_count, count(DISTINCT pr.pipeline_run_id) run_count FROM meta.source s LEFT JOIN meta.dataset_release dr USING(source_id) LEFT JOIN meta.pipeline_run pr USING(source_id) GROUP BY 1,2) x;"),
        "wdi_coverage": psql_json(db, "SELECT row_to_json(x) FROM (SELECT count(DISTINCT indicator_code) indicators, count(DISTINCT country_code) countries, min(period_year) min_year, max(period_year) max_year, count(*) rows FROM staging.wdi_observation) x;"),
        "wdi_indicators": psql_json(db, "SELECT COALESCE(json_agg(indicator_code ORDER BY indicator_code),'[]'::json) FROM (SELECT DISTINCT indicator_code FROM staging.wdi_observation) x;"),
    }


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")


def fetch() -> None:
    raw = fetch_campaign_raw(indicators=CANDIDATE_INDICATORS, date_range=DATE_RANGE, timeout_seconds=120)
    raw["scope"].update({
        "task": TASK_ID,
        "campaign": "Domain Bulk Expansion Mandate — WDI trade/tourism/supply-chain plus monetary/banking/credit annual scalar campaign",
        "mode": "Domain Bulk Expansion",
        "date_range": DATE_RANGE,
        "candidate_source": "implemented-compatible WDI annual scalar country-indicator loader path plus existing WDI domain modules",
        "domain_bias": "maximal within current WDI annual scalar compatibility evidence; exclude only with deterministic evidence",
        "target_domains": sorted(set(INDICATOR_DOMAIN.values())),
        "indicator_domains": INDICATOR_DOMAIN,
        "raw_artifact_path": RAW_PATH.as_posix(),
    })
    write_json(RAW_PATH, raw)
    print(json.dumps({"raw_path": RAW_PATH.as_posix(), "candidate_count": len(CANDIDATE_INDICATORS), "date_range": DATE_RANGE}, indent=2, sort_keys=True))


def artifacts(load_counts: dict[str, int] | None = None) -> None:
    raw = json.loads(RAW_PATH.read_text())
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
    normalized = json.loads(NORMALIZED_PATH.read_text())
    catalog_names = {
        row["id"]: row.get("name") or row.get("value") or row["id"]
        for row in raw.get("country_catalog", {}).get("countries", [])
        if row.get("id")
    }
    # WDI responses can spell the same territory differently across indicators
    # (observed: CUW "Curacao" vs "Curaçao"). The existing loader upserts
    # distinct country_code/country_name pairs into a unique canonical territory
    # key, so bulk campaigns must canonicalize display names inside the
    # already-validated country catalog before PostgreSQL load.
    for row in normalized["rows"]:
        iso3 = row.get("countryiso3code")
        if iso3 in catalog_names:
            row["country_name"] = catalog_names[iso3]
    normalized["task"] = TASK_ID
    normalized["campaign"] = raw["scope"]["campaign"]
    normalized["mode"] = raw["scope"]["mode"]
    normalized["domain_bulk_expansion"] = {"target_domains": raw["scope"]["target_domains"], "indicator_domains": INDICATOR_DOMAIN}
    write_json(NORMALIZED_PATH, normalized)
    print(json.dumps(paths, indent=2, sort_keys=True))


def load(db: str) -> None:
    counts = load_wdi_implemented_compatible_campaign_to_postgres(db, NORMALIZED_PATH, run_key="task-174-domain-bulk-expansion-wdi-trade-finance")
    write_json(LOAD_REPORT_PATH, {"task": TASK_ID, "status": "succeeded", "db": db, "load_counts": counts, "normalized_path": NORMALIZED_PATH.as_posix()})
    artifacts(load_counts=counts)
    print(json.dumps(counts, indent=2, sort_keys=True))


def final_report(db: str, before_path: Path = INVENTORY_REPORT_PATH) -> None:
    before = json.loads(before_path.read_text()) if before_path.exists() else None
    after = inventory(db)
    raw = json.loads(RAW_PATH.read_text())
    normalized = json.loads(NORMALIZED_PATH.read_text())
    classification = normalized["classification"]
    domains = {}
    for indicator in normalized["indicators"]:
        domain = INDICATOR_DOMAIN.get(indicator, "Other implemented-compatible WDI annual scalar")
        domains.setdefault(domain, {"indicators": [], "rows": 0})
        domains[domain]["indicators"].append(indicator)
    rows_by_indicator = {}
    for row in normalized["rows"]:
        rows_by_indicator[row["indicator_id"]] = rows_by_indicator.get(row["indicator_id"], 0) + 1
    for domain in domains.values():
        domain["rows"] = sum(rows_by_indicator.get(i, 0) for i in domain["indicators"])
        domain["indicator_count"] = len(domain["indicators"])
    before_fact = before["row_counts"]["curated.fact_observation"] if before else None
    after_fact = after["row_counts"]["curated.fact_observation"]
    report = {
        "task": TASK_ID,
        "status": "succeeded",
        "before": before,
        "after": after,
        "rows_added": None if before_fact is None else after_fact - before_fact,
        "largest_candidate_universe_considered": {
            "provider_path": "World Bank WDI public API v2 through existing WDI annual scalar observed-package and PostgreSQL loader path",
            "countries": raw["scope"]["country_count"],
            "date_range": DATE_RANGE,
            "candidate_indicators": len(CANDIDATE_INDICATORS),
            "candidate_presparsity_rows": raw["scope"]["country_count"] * len(CANDIDATE_INDICATORS) * 25,
            "target_domains": raw["scope"]["target_domains"],
        },
        "preflight_classification": classification,
        "included_domains": domains,
        "exclusions": {indicator: classification["indicator_results"][indicator] for indicator in classification["excluded_indicators"]},
        "next_largest_safe_campaign": "Expand the same implemented-compatible WDI annual scalar path to additional Trade and Monetary/Financial WDI indicators not yet loaded, then separately evaluate UN Comtrade only after its current hard-coded USA-Japan product normalizer is generalized by evidence or a source-specific bulk normalizer is added.",
    }
    write_json(FINAL_REPORT_PATH, report)
    print(json.dumps({"final_report": FINAL_REPORT_PATH.as_posix(), "rows_added": report["rows_added"], "after_fact_rows": after_fact}, indent=2, sort_keys=True))


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("command", choices=["inventory", "fetch", "artifacts", "load", "final-report"])
    ap.add_argument("--db", default="macroforge")
    args = ap.parse_args()
    if args.command == "inventory":
        inv = inventory(args.db)
        write_json(INVENTORY_REPORT_PATH, inv)
        print(json.dumps(inv, indent=2, sort_keys=True))
    elif args.command == "fetch":
        fetch()
    elif args.command == "artifacts":
        artifacts()
    elif args.command == "load":
        load(args.db)
    elif args.command == "final-report":
        final_report(args.db)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
