from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from macroforge.observed_ingestion import ObservedIngestionPackage
from macroforge.wdi_observed import (
    build_wdi_macro_indicators_refresh_delta_report,
    build_wdi_observed_package,
    observed_package_fingerprint,
    refresh_delta_report_fingerprint,
)

FINANCIAL_ACCOUNTS_CORE_TASK_ID = "TASK-143"
FINANCIAL_ACCOUNTS_CORE_MODE = "Operational Repository Construction"
FINANCIAL_ACCOUNTS_CORE_SECTION = "Financial Accounts"
FINANCIAL_ACCOUNTS_CORE_SECTION_STATUS_TARGET = "Developing"
FINANCIAL_ACCOUNTS_CORE_PHASE = "WDI Financial Accounts Core Operational Dataset"
FINANCIAL_ACCOUNTS_CORE_CAPABILITY = "WDI financial accounts core operational repository section"
FINANCIAL_ACCOUNTS_CORE_RAW_FIXTURE_PATH = "data/raw/wdi_financial_accounts_core_operational/wdi-financial-accounts-core-all-countries-4i-2000-2023.json"
FINANCIAL_ACCOUNTS_CORE_RAW_SHA256 = "b959b323b0e99373e4e0e1131160d44dda807d60c83836f983434e28a5a33aa0"
FINANCIAL_ACCOUNTS_CORE_DEFAULT_NORMALIZED_PATH = "data/metadata/wdi_financial_accounts_core_operational/wdi-financial-accounts-core-normalized.json"
FINANCIAL_ACCOUNTS_CORE_DEFAULT_REFRESH_MANIFEST_PATH = "data/operational/wdi_financial_accounts_core_operational/wdi-financial-accounts-core-refresh-manifest.json"
FINANCIAL_ACCOUNTS_CORE_DEFAULT_REFRESH_DELTA_PATH = "data/operational/wdi_financial_accounts_core_operational/wdi-financial-accounts-core-refresh-delta-report.json"
FINANCIAL_ACCOUNTS_CORE_INDICATORS = [
    "FS.AST.PRVT.GD.ZS",
    "FM.LBL.BMNY.GD.ZS",
    "CM.MKT.LCAP.GD.ZS",
    "CM.MKT.LDOM.NO",
]
FINANCIAL_ACCOUNTS_CORE_DATE_RANGE = "2000:2023"
FINANCIAL_ACCOUNTS_CORE_YEARS = [str(year) for year in range(2000, 2024)]
FINANCIAL_ACCOUNTS_CORE_COUNTRY_COUNT = 217
FINANCIAL_ACCOUNTS_CORE_EXPECTED_OBSERVATION_COUNT = FINANCIAL_ACCOUNTS_CORE_COUNTRY_COUNT * len(FINANCIAL_ACCOUNTS_CORE_INDICATORS) * len(FINANCIAL_ACCOUNTS_CORE_YEARS)
FINANCIAL_ACCOUNTS_CORE_DEFAULT_RUN_KEY = "task-143-wdi-financial-accounts-core-operational-repository"

INDICATOR_METADATA = {
    "FS.AST.PRVT.GD.ZS": {
        "concept": "domestic_credit_private_sector_percent_gdp",
        "financial_role": "domestic_credit_private_sector",
        "unit_code": "PERCENT_OF_GDP",
        "unit_label": "percent of GDP",
        "measure_basis": "share_of_gdp",
    },
    "FM.LBL.BMNY.GD.ZS": {
        "concept": "broad_money_percent_gdp",
        "financial_role": "broad_money",
        "unit_code": "PERCENT_OF_GDP",
        "unit_label": "percent of GDP",
        "measure_basis": "share_of_gdp",
    },
    "CM.MKT.LCAP.GD.ZS": {
        "concept": "listed_domestic_market_cap_percent_gdp",
        "financial_role": "listed_equity_market_capitalization",
        "unit_code": "PERCENT_OF_GDP",
        "unit_label": "percent of GDP",
        "measure_basis": "share_of_gdp",
    },
    "CM.MKT.LDOM.NO": {
        "concept": "listed_domestic_companies_count",
        "financial_role": "listed_company_count",
        "unit_code": "COUNT",
        "unit_label": "count",
        "measure_basis": "entity_count",
    },
}


def _financial_accounts_core_countries(raw: dict[str, Any]) -> list[str]:
    countries = raw.get("scope", {}).get("countries", [])
    if len(countries) != FINANCIAL_ACCOUNTS_CORE_COUNTRY_COUNT:
        raise ValueError(f"expected {FINANCIAL_ACCOUNTS_CORE_COUNTRY_COUNT} countries, got {len(countries)}")
    if len(set(countries)) != len(countries):
        raise ValueError("WDI financial accounts core country scope contains duplicate country ids")
    return countries


def _financial_accounts_core_country_catalog(raw: dict[str, Any]) -> dict[str, dict[str, Any]]:
    catalog_rows = raw.get("country_catalog", {}).get("countries", [])
    catalog = {row.get("id"): row for row in catalog_rows}
    countries = _financial_accounts_core_countries(raw)
    if set(catalog) != set(countries):
        raise ValueError("WDI financial accounts core country catalog does not match scoped countries")
    if any(row.get("region", {}).get("id") == "NA" for row in catalog.values()):
        raise ValueError("WDI financial accounts core includes aggregate rows")
    return catalog


def normalize_wdi_financial_accounts_core_fixture(raw: dict[str, Any]) -> dict[str, Any]:
    """Normalize TASK-143 WDI Financial Accounts Core into existing WDI loader-compatible shape."""

    scope = raw.get("scope", {})
    if scope.get("task") != FINANCIAL_ACCOUNTS_CORE_TASK_ID:
        raise ValueError(f"unexpected task scope: {scope.get('task')}")
    if scope.get("mode") != FINANCIAL_ACCOUNTS_CORE_MODE:
        raise ValueError(f"unexpected mode: {scope.get('mode')}")
    if scope.get("section") != FINANCIAL_ACCOUNTS_CORE_SECTION:
        raise ValueError(f"unexpected repository section: {scope.get('section')}")
    if scope.get("section_status_target") != FINANCIAL_ACCOUNTS_CORE_SECTION_STATUS_TARGET:
        raise ValueError(f"unexpected section status target: {scope.get('section_status_target')}")
    if scope.get("phase") != FINANCIAL_ACCOUNTS_CORE_PHASE:
        raise ValueError(f"unexpected phase: {scope.get('phase')}")
    if scope.get("indicators") != FINANCIAL_ACCOUNTS_CORE_INDICATORS:
        raise ValueError(f"unexpected indicator scope: {scope.get('indicators')}")
    if scope.get("date_range") != FINANCIAL_ACCOUNTS_CORE_DATE_RANGE:
        raise ValueError(f"unexpected date range: {scope.get('date_range')}")
    if scope.get("expected_observation_count") != FINANCIAL_ACCOUNTS_CORE_EXPECTED_OBSERVATION_COUNT:
        raise ValueError("WDI financial accounts core expected observation count changed")

    countries = _financial_accounts_core_countries(raw)
    country_catalog = _financial_accounts_core_country_catalog(raw)
    requests = raw.get("requests", [])
    if [request.get("indicator_code") for request in requests] != FINANCIAL_ACCOUNTS_CORE_INDICATORS:
        raise ValueError("WDI financial accounts core request order must match validated indicator scope")

    rows: list[dict[str, Any]] = []
    raw_artifacts: list[dict[str, Any]] = []
    expected_rows_per_indicator = len(countries) * len(FINANCIAL_ACCOUNTS_CORE_YEARS)
    for request in requests:
        indicator_code = request["indicator_code"]
        response = request.get("response")
        if not isinstance(response, list) or len(response) != 2:
            raise ValueError(f"unexpected WDI response shape for {indicator_code}")
        metadata, observations = response
        if metadata.get("lastupdated") is None:
            raise ValueError(f"missing WDI lastupdated metadata for {indicator_code}")
        if len(observations) != expected_rows_per_indicator:
            raise ValueError(f"unexpected WDI financial_accounts observation count for {indicator_code}: {len(observations)}")
        raw_response_json = json.dumps(response, sort_keys=True)
        raw_artifacts.append({
            "indicator": indicator_code,
            "url": request["url"],
            "status": "ok",
            "content_type": "application/json",
            "bytes": len(raw_response_json.encode("utf-8")),
            "sha256": hashlib.sha256(raw_response_json.encode("utf-8")).hexdigest(),
            "row_count": len(observations),
            "source_metadata": metadata,
            "raw_file": FINANCIAL_ACCOUNTS_CORE_RAW_FIXTURE_PATH.rsplit("/", 1)[-1],
        })
        meta = INDICATOR_METADATA[indicator_code]
        for item in observations:
            indicator = item.get("indicator") or {}
            country = item.get("country") or {}
            country_code = item.get("countryiso3code")
            row = {
                "source": "World Bank World Development Indicators",
                "indicator_id": indicator.get("id"),
                "indicator_name": indicator.get("value"),
                "country_id": country.get("id"),
                "country_name": country.get("value"),
                "countryiso3code": country_code,
                "date": item.get("date"),
                "value": item.get("value"),
                "unit": meta["unit_code"],
                "unit_label": meta["unit_label"],
                "obs_status": item.get("obs_status") or None,
                "decimal": item.get("decimal"),
                "financial_accounts_concept": meta["concept"],
                "financial_accounts_role": meta["financial_role"],
                "financial_accounts_measure_basis": meta["measure_basis"],
                "repository_section": FINANCIAL_ACCOUNTS_CORE_SECTION,
                "section_status_target": FINANCIAL_ACCOUNTS_CORE_SECTION_STATUS_TARGET,
                "operational_capability": FINANCIAL_ACCOUNTS_CORE_CAPABILITY,
                "operational_mode": FINANCIAL_ACCOUNTS_CORE_MODE,
                "coverage_level": "wdi_financial_accounts_core_operational_repository",
                "region_id": country_catalog[country_code]["region"]["id"],
                "region_label": country_catalog[country_code]["region"]["value"],
                "income_level_id": country_catalog[country_code]["incomeLevel"]["id"],
                "income_level_label": country_catalog[country_code]["incomeLevel"]["value"],
            }
            if row["indicator_id"] != indicator_code:
                raise ValueError(f"unexpected indicator in response: {row['indicator_id']} != {indicator_code}")
            if row["countryiso3code"] not in countries:
                raise ValueError(f"unexpected country in response: {row['countryiso3code']}")
            if row["date"] not in FINANCIAL_ACCOUNTS_CORE_YEARS:
                raise ValueError(f"unexpected year in response: {row['date']}")
            rows.append(row)

    rows.sort(key=lambda row: (FINANCIAL_ACCOUNTS_CORE_INDICATORS.index(row["indicator_id"]), countries.index(row["countryiso3code"]), int(row["date"])))
    if len(rows) != FINANCIAL_ACCOUNTS_CORE_EXPECTED_OBSERVATION_COUNT:
        raise ValueError(f"expected {FINANCIAL_ACCOUNTS_CORE_EXPECTED_OBSERVATION_COUNT} rows, got {len(rows)}")

    return {
        "source": "World Bank World Development Indicators",
        "support_bundle": FINANCIAL_ACCOUNTS_CORE_RAW_FIXTURE_PATH,
        "created_at_utc": None,
        "countries": countries,
        "indicators": FINANCIAL_ACCOUNTS_CORE_INDICATORS,
        "date_range": FINANCIAL_ACCOUNTS_CORE_DATE_RANGE,
        "expected_row_count": FINANCIAL_ACCOUNTS_CORE_EXPECTED_OBSERVATION_COUNT,
        "row_count": len(rows),
        "rows": rows,
        "raw_artifacts": raw_artifacts,
        "raw_fixture_path": FINANCIAL_ACCOUNTS_CORE_RAW_FIXTURE_PATH,
        "raw_sha256": FINANCIAL_ACCOUNTS_CORE_RAW_SHA256,
        "operational_scope": {
            "task": FINANCIAL_ACCOUNTS_CORE_TASK_ID,
            "mode": FINANCIAL_ACCOUNTS_CORE_MODE,
            "repository_section": FINANCIAL_ACCOUNTS_CORE_SECTION,
            "section_status_target": FINANCIAL_ACCOUNTS_CORE_SECTION_STATUS_TARGET,
            "phase": FINANCIAL_ACCOUNTS_CORE_PHASE,
            "capability": FINANCIAL_ACCOUNTS_CORE_CAPABILITY,
            "expansion_level": "all_non_aggregate_countries_financial_accounts_core_2000_2023",
            "country_count": len(countries),
            "countries": countries,
            "indicators": FINANCIAL_ACCOUNTS_CORE_INDICATORS,
            "date_range": FINANCIAL_ACCOUNTS_CORE_DATE_RANGE,
            "non_goals": scope.get("non_goals", []),
        },
    }


def build_wdi_financial_accounts_core_observed_package(raw: dict[str, Any]) -> ObservedIngestionPackage:
    return build_wdi_observed_package(normalize_wdi_financial_accounts_core_fixture(raw))


def write_wdi_financial_accounts_core_normalized_artifact(raw: dict[str, Any], path: str | Path = FINANCIAL_ACCOUNTS_CORE_DEFAULT_NORMALIZED_PATH) -> dict[str, Any]:
    normalized = normalize_wdi_financial_accounts_core_fixture(raw)
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(normalized, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return normalized


def write_wdi_financial_accounts_core_refresh_manifest(raw: dict[str, Any], path: str | Path = FINANCIAL_ACCOUNTS_CORE_DEFAULT_REFRESH_MANIFEST_PATH, *, normalized_path: str | Path = FINANCIAL_ACCOUNTS_CORE_DEFAULT_NORMALIZED_PATH, load_counts: dict[str, int] | None = None) -> dict[str, Any]:
    package = build_wdi_financial_accounts_core_observed_package(raw)
    normalized = normalize_wdi_financial_accounts_core_fixture(raw)
    payload = {
        "task": FINANCIAL_ACCOUNTS_CORE_TASK_ID,
        "status": "succeeded",
        "mode": FINANCIAL_ACCOUNTS_CORE_MODE,
        "repository_section": FINANCIAL_ACCOUNTS_CORE_SECTION,
        "section_status_target": FINANCIAL_ACCOUNTS_CORE_SECTION_STATUS_TARGET,
        "phase": FINANCIAL_ACCOUNTS_CORE_PHASE,
        "capability": FINANCIAL_ACCOUNTS_CORE_CAPABILITY,
        "raw_fixture_path": FINANCIAL_ACCOUNTS_CORE_RAW_FIXTURE_PATH,
        "raw_sha256": FINANCIAL_ACCOUNTS_CORE_RAW_SHA256,
        "normalized_path": str(normalized_path),
        "source_urls": [request["url"] for request in raw["requests"]],
        "country_count": len(normalized["countries"]),
        "indicators": FINANCIAL_ACCOUNTS_CORE_INDICATORS,
        "date_range": FINANCIAL_ACCOUNTS_CORE_DATE_RANGE,
        "row_count": normalized["row_count"],
        "expected_row_count": FINANCIAL_ACCOUNTS_CORE_EXPECTED_OBSERVATION_COUNT,
        "observed_value_count": sum(1 for row in normalized["rows"] if row["value"] is not None),
        "missing_value_count": sum(1 for row in normalized["rows"] if row["value"] is None),
        "package_fingerprint": observed_package_fingerprint(package),
        "load_counts": load_counts,
        "non_goals": normalized["operational_scope"]["non_goals"],
    }
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def build_wdi_financial_accounts_core_refresh_delta_report(previous: dict[str, Any], current: dict[str, Any]) -> dict[str, Any]:
    report = build_wdi_macro_indicators_refresh_delta_report(previous, current)
    report["task"] = FINANCIAL_ACCOUNTS_CORE_TASK_ID
    report["capability"] = FINANCIAL_ACCOUNTS_CORE_CAPABILITY
    report["mode"] = FINANCIAL_ACCOUNTS_CORE_MODE
    report["repository_section"] = FINANCIAL_ACCOUNTS_CORE_SECTION
    report["section_status_target"] = FINANCIAL_ACCOUNTS_CORE_SECTION_STATUS_TARGET
    report["phase"] = FINANCIAL_ACCOUNTS_CORE_PHASE
    report["refresh_verification"] = "bounded_wdi_financial_accounts_core_pre_load_delta_check"
    report.pop("refresh_delta_fingerprint", None)
    report["refresh_delta_fingerprint"] = refresh_delta_report_fingerprint(report)
    return report


def write_wdi_financial_accounts_core_refresh_delta_report(previous: dict[str, Any], current: dict[str, Any], path: str | Path = FINANCIAL_ACCOUNTS_CORE_DEFAULT_REFRESH_DELTA_PATH) -> dict[str, Any]:
    report = build_wdi_financial_accounts_core_refresh_delta_report(previous, current)
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report
