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
    validated_wdi_raw_provenance,
)

TRADE_CORE_TASK_ID = "TASK-142"
TRADE_CORE_MODE = "Operational Repository Construction"
TRADE_CORE_SECTION = "Trade"
TRADE_CORE_SECTION_STATUS_TARGET = "Developing"
TRADE_CORE_PHASE = "WDI Trade Core Operational Dataset"
TRADE_CORE_CAPABILITY = "WDI trade core operational repository section"
TRADE_CORE_RAW_FIXTURE_PATH = "data/raw/wdi_trade_core_operational/wdi-trade-core-all-countries-4i-2000-2023.json"
TRADE_CORE_RAW_SHA256 = "d537645e66831fab3d75238ca5205d3790699dd7357ebdc909c0f158aa8bd262"
TRADE_CORE_DEFAULT_NORMALIZED_PATH = "data/metadata/wdi_trade_core_operational/wdi-trade-core-normalized.json"
TRADE_CORE_DEFAULT_REFRESH_MANIFEST_PATH = "data/operational/wdi_trade_core_operational/wdi-trade-core-refresh-manifest.json"
TRADE_CORE_DEFAULT_REFRESH_DELTA_PATH = "data/operational/wdi_trade_core_operational/wdi-trade-core-refresh-delta-report.json"
TRADE_CORE_INDICATORS = [
    "NE.EXP.GNFS.CD",
    "NE.IMP.GNFS.CD",
    "NE.EXP.GNFS.ZS",
    "NE.IMP.GNFS.ZS",
]
TRADE_CORE_DATE_RANGE = "2000:2023"
TRADE_CORE_YEARS = [str(year) for year in range(2000, 2024)]
TRADE_CORE_COUNTRY_COUNT = 217
TRADE_CORE_EXPECTED_OBSERVATION_COUNT = TRADE_CORE_COUNTRY_COUNT * len(TRADE_CORE_INDICATORS) * len(TRADE_CORE_YEARS)
TRADE_CORE_DEFAULT_RUN_KEY = "task-142-wdi-trade-core-operational-repository"

INDICATOR_METADATA = {
    "NE.EXP.GNFS.CD": {
        "concept": "exports_goods_services_current_usd",
        "flow": "exports",
        "unit_code": "CURRENT_USD",
        "unit_label": "current US dollars",
        "measure_basis": "current_value",
    },
    "NE.IMP.GNFS.CD": {
        "concept": "imports_goods_services_current_usd",
        "flow": "imports",
        "unit_code": "CURRENT_USD",
        "unit_label": "current US dollars",
        "measure_basis": "current_value",
    },
    "NE.EXP.GNFS.ZS": {
        "concept": "exports_goods_services_percent_gdp",
        "flow": "exports",
        "unit_code": "PERCENT_OF_GDP",
        "unit_label": "percent of GDP",
        "measure_basis": "share_of_gdp",
    },
    "NE.IMP.GNFS.ZS": {
        "concept": "imports_goods_services_percent_gdp",
        "flow": "imports",
        "unit_code": "PERCENT_OF_GDP",
        "unit_label": "percent of GDP",
        "measure_basis": "share_of_gdp",
    },
}


def _trade_core_countries(raw: dict[str, Any]) -> list[str]:
    countries = raw.get("scope", {}).get("countries", [])
    if len(countries) != TRADE_CORE_COUNTRY_COUNT:
        raise ValueError(f"expected {TRADE_CORE_COUNTRY_COUNT} countries, got {len(countries)}")
    if len(set(countries)) != len(countries):
        raise ValueError("WDI trade core country scope contains duplicate country ids")
    return countries


def _trade_core_country_catalog(raw: dict[str, Any]) -> dict[str, dict[str, Any]]:
    catalog_rows = raw.get("country_catalog", {}).get("countries", [])
    catalog = {row.get("id"): row for row in catalog_rows}
    countries = _trade_core_countries(raw)
    if set(catalog) != set(countries):
        raise ValueError("WDI trade core country catalog does not match scoped countries")
    if any(row.get("region", {}).get("id") == "NA" for row in catalog.values()):
        raise ValueError("WDI trade core includes aggregate rows")
    return catalog


def normalize_wdi_trade_core_fixture(
    raw: dict[str, Any], *, raw_artifact_path: str | Path, raw_payload: str | bytes
) -> dict[str, Any]:
    """Normalize TASK-142 WDI Trade Core into existing WDI loader-compatible shape."""

    actual_path, actual_sha256, actual_bytes = validated_wdi_raw_provenance(
        raw, raw_artifact_path=raw_artifact_path, raw_payload=raw_payload
    )
    scope = raw.get("scope", {})
    if scope.get("task") != TRADE_CORE_TASK_ID:
        raise ValueError(f"unexpected task scope: {scope.get('task')}")
    if scope.get("mode") != TRADE_CORE_MODE:
        raise ValueError(f"unexpected mode: {scope.get('mode')}")
    if scope.get("section") != TRADE_CORE_SECTION:
        raise ValueError(f"unexpected repository section: {scope.get('section')}")
    if scope.get("section_status_target") != TRADE_CORE_SECTION_STATUS_TARGET:
        raise ValueError(f"unexpected section status target: {scope.get('section_status_target')}")
    if scope.get("phase") != TRADE_CORE_PHASE:
        raise ValueError(f"unexpected phase: {scope.get('phase')}")
    if scope.get("indicators") != TRADE_CORE_INDICATORS:
        raise ValueError(f"unexpected indicator scope: {scope.get('indicators')}")
    if scope.get("date_range") != TRADE_CORE_DATE_RANGE:
        raise ValueError(f"unexpected date range: {scope.get('date_range')}")
    if scope.get("expected_observation_count") != TRADE_CORE_EXPECTED_OBSERVATION_COUNT:
        raise ValueError("WDI trade core expected observation count changed")

    countries = _trade_core_countries(raw)
    country_catalog = _trade_core_country_catalog(raw)
    requests = raw.get("requests", [])
    if [request.get("indicator_code") for request in requests] != TRADE_CORE_INDICATORS:
        raise ValueError("WDI trade core request order must match validated indicator scope")

    rows: list[dict[str, Any]] = []
    raw_artifacts: list[dict[str, Any]] = []
    expected_rows_per_indicator = len(countries) * len(TRADE_CORE_YEARS)
    for request in requests:
        indicator_code = request["indicator_code"]
        response = request.get("response")
        if not isinstance(response, list) or len(response) != 2:
            raise ValueError(f"unexpected WDI response shape for {indicator_code}")
        metadata, observations = response
        if metadata.get("lastupdated") is None:
            raise ValueError(f"missing WDI lastupdated metadata for {indicator_code}")
        if len(observations) != expected_rows_per_indicator:
            raise ValueError(f"unexpected WDI trade observation count for {indicator_code}: {len(observations)}")
        raw_response_bytes = json.dumps(response, sort_keys=True).encode("utf-8")
        raw_artifacts.append({
            "indicator": indicator_code,
            "url": request["url"],
            "status": "ok",
            "content_type": "application/json",
            "bytes": actual_bytes,
            "sha256": actual_sha256,
            "response_bytes": len(raw_response_bytes),
            "response_sha256": hashlib.sha256(raw_response_bytes).hexdigest(),
            "row_count": len(observations),
            "source_metadata": metadata,
            "raw_file": actual_path,
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
                "trade_concept": meta["concept"],
                "trade_flow": meta["flow"],
                "trade_measure_basis": meta["measure_basis"],
                "repository_section": TRADE_CORE_SECTION,
                "section_status_target": TRADE_CORE_SECTION_STATUS_TARGET,
                "operational_capability": TRADE_CORE_CAPABILITY,
                "operational_mode": TRADE_CORE_MODE,
                "coverage_level": "wdi_trade_core_operational_repository",
                "region_id": country_catalog[country_code]["region"]["id"],
                "region_label": country_catalog[country_code]["region"]["value"],
                "income_level_id": country_catalog[country_code]["incomeLevel"]["id"],
                "income_level_label": country_catalog[country_code]["incomeLevel"]["value"],
            }
            if row["indicator_id"] != indicator_code:
                raise ValueError(f"unexpected indicator in response: {row['indicator_id']} != {indicator_code}")
            if row["countryiso3code"] not in countries:
                raise ValueError(f"unexpected country in response: {row['countryiso3code']}")
            if row["date"] not in TRADE_CORE_YEARS:
                raise ValueError(f"unexpected year in response: {row['date']}")
            rows.append(row)

    rows.sort(key=lambda row: (TRADE_CORE_INDICATORS.index(row["indicator_id"]), countries.index(row["countryiso3code"]), int(row["date"])))
    if len(rows) != TRADE_CORE_EXPECTED_OBSERVATION_COUNT:
        raise ValueError(f"expected {TRADE_CORE_EXPECTED_OBSERVATION_COUNT} rows, got {len(rows)}")

    return {
        "source": "World Bank World Development Indicators",
        "support_bundle": actual_path,
        "created_at_utc": None,
        "countries": countries,
        "indicators": TRADE_CORE_INDICATORS,
        "date_range": TRADE_CORE_DATE_RANGE,
        "expected_row_count": TRADE_CORE_EXPECTED_OBSERVATION_COUNT,
        "row_count": len(rows),
        "rows": rows,
        "raw_artifacts": raw_artifacts,
        "raw_fixture_path": actual_path,
        "raw_sha256": actual_sha256,
        "operational_scope": {
            "task": TRADE_CORE_TASK_ID,
            "mode": TRADE_CORE_MODE,
            "repository_section": TRADE_CORE_SECTION,
            "section_status_target": TRADE_CORE_SECTION_STATUS_TARGET,
            "phase": TRADE_CORE_PHASE,
            "capability": TRADE_CORE_CAPABILITY,
            "expansion_level": "all_non_aggregate_countries_trade_core_2000_2023",
            "country_count": len(countries),
            "countries": countries,
            "indicators": TRADE_CORE_INDICATORS,
            "date_range": TRADE_CORE_DATE_RANGE,
            "non_goals": scope.get("non_goals", []),
        },
    }


def build_wdi_trade_core_observed_package(raw: dict[str, Any], *, raw_artifact_path: str | Path, raw_payload: str | bytes) -> ObservedIngestionPackage:
    return build_wdi_observed_package(normalize_wdi_trade_core_fixture(raw, raw_artifact_path=raw_artifact_path, raw_payload=raw_payload))


def write_wdi_trade_core_normalized_artifact(raw: dict[str, Any], path: str | Path = TRADE_CORE_DEFAULT_NORMALIZED_PATH, *, raw_artifact_path: str | Path, raw_payload: str | bytes) -> dict[str, Any]:
    normalized = normalize_wdi_trade_core_fixture(raw, raw_artifact_path=raw_artifact_path, raw_payload=raw_payload)
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(normalized, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return normalized


def write_wdi_trade_core_refresh_manifest(raw: dict[str, Any], path: str | Path = TRADE_CORE_DEFAULT_REFRESH_MANIFEST_PATH, *, raw_artifact_path: str | Path, raw_payload: str | bytes, normalized_path: str | Path = TRADE_CORE_DEFAULT_NORMALIZED_PATH, load_counts: dict[str, int] | None = None) -> dict[str, Any]:
    package = build_wdi_trade_core_observed_package(raw, raw_artifact_path=raw_artifact_path, raw_payload=raw_payload)
    normalized = normalize_wdi_trade_core_fixture(raw, raw_artifact_path=raw_artifact_path, raw_payload=raw_payload)
    payload = {
        "task": TRADE_CORE_TASK_ID,
        "status": "succeeded",
        "mode": TRADE_CORE_MODE,
        "repository_section": TRADE_CORE_SECTION,
        "section_status_target": TRADE_CORE_SECTION_STATUS_TARGET,
        "phase": TRADE_CORE_PHASE,
        "capability": TRADE_CORE_CAPABILITY,
        "raw_fixture_path": normalized["raw_fixture_path"],
        "raw_sha256": normalized["raw_sha256"],
        "normalized_path": str(normalized_path),
        "source_urls": [request["url"] for request in raw["requests"]],
        "country_count": len(normalized["countries"]),
        "indicators": TRADE_CORE_INDICATORS,
        "date_range": TRADE_CORE_DATE_RANGE,
        "row_count": normalized["row_count"],
        "expected_row_count": TRADE_CORE_EXPECTED_OBSERVATION_COUNT,
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


def build_wdi_trade_core_refresh_delta_report(previous: dict[str, Any], current: dict[str, Any]) -> dict[str, Any]:
    report = build_wdi_macro_indicators_refresh_delta_report(previous, current)
    report["task"] = TRADE_CORE_TASK_ID
    report["capability"] = TRADE_CORE_CAPABILITY
    report["mode"] = TRADE_CORE_MODE
    report["repository_section"] = TRADE_CORE_SECTION
    report["section_status_target"] = TRADE_CORE_SECTION_STATUS_TARGET
    report["phase"] = TRADE_CORE_PHASE
    report["refresh_verification"] = "bounded_wdi_trade_core_pre_load_delta_check"
    report.pop("refresh_delta_fingerprint", None)
    report["refresh_delta_fingerprint"] = refresh_delta_report_fingerprint(report)
    return report


def write_wdi_trade_core_refresh_delta_report(previous: dict[str, Any], current: dict[str, Any], path: str | Path = TRADE_CORE_DEFAULT_REFRESH_DELTA_PATH) -> dict[str, Any]:
    report = build_wdi_trade_core_refresh_delta_report(previous, current)
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report
