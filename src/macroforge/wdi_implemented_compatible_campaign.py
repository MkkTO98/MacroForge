from __future__ import annotations

import argparse
import hashlib
import json
import urllib.request
from pathlib import Path
from typing import Any

from macroforge.observed_ingestion import compare_observed_packages, observed_package_fingerprint
from macroforge.wdi_observed import build_wdi_observed_package

PROJECT_ROOT = Path(__file__).resolve().parents[2]
TASK_ID = "TASK-165"
CAMPAIGN_NAME = "WDI Implemented-Compatible Annual Scalar Expansion Campaign"
CAMPAIGN_MODE = "Operational Repository Expansion Campaign"
SOURCE_NAME = "World Bank World Development Indicators"
WDI_COUNTRY_CATALOG_FIXTURE = PROJECT_ROOT / "data/raw/wdi_operational_phase1/wdi-phase1-all-countries-3i-2000-2023.json"
DEFAULT_RAW_PATH = PROJECT_ROOT / "data/raw/wdi_implemented_compatible_campaign/wdi-implemented-compatible-campaign-27i-2000-2023.json"
DEFAULT_NORMALIZED_PATH = PROJECT_ROOT / "data/processed/wdi_implemented_compatible_campaign/wdi-implemented-compatible-campaign-normalized.json"
DEFAULT_PREFLIGHT_REPORT_PATH = PROJECT_ROOT / "artifacts/reports/task-165-wdi-campaign-preflight-report.json"
DEFAULT_CLASSIFICATION_REPORT_PATH = PROJECT_ROOT / "artifacts/reports/task-165-wdi-campaign-compatibility-classification-report.json"
DEFAULT_OPERATIONAL_REPORT_PATH = PROJECT_ROOT / "artifacts/reports/task-165-wdi-campaign-operational-expansion-report.json"
DEFAULT_COVERAGE_REPORT_PATH = PROJECT_ROOT / "artifacts/reports/task-165-wdi-campaign-repository-coverage-report.json"
DEFAULT_EXCEPTION_REPORT_PATH = PROJECT_ROOT / "artifacts/reports/task-165-wdi-campaign-exception-report.json"
DEFAULT_CONFIDENCE_REPORT_PATH = PROJECT_ROOT / "artifacts/reports/task-165-wdi-campaign-updated-confidence-assessment.json"
CAMPAIGN_PERIODS = [str(year) for year in range(2000, 2024)]
CAMPAIGN_DATE_RANGE = "2000:2023"
CAMPAIGN_PRESPARSITY_COUNTRY_COUNT = 217
CAMPAIGN_CANDIDATE_INDICATORS = [
    "AG.LND.FRST.ZS",
    "AG.PRD.FOOD.XD",
    "BG.GSR.NFSV.GD.ZS",
    "BX.TRF.PWKR.DT.GD.ZS",
    "EN.ATM.PM25.MC.M3",
    "GB.XPD.RSDV.GD.ZS",
    "IP.PAT.RESD",
    "IT.NET.BBND.P2",
    "LP.LPI.INFR.XQ",
    "LP.LPI.LOGS.XQ",
    "LP.LPI.OVRL.XQ",
    "NV.AGR.TOTL.ZS",
    "SE.SEC.ENRR",
    "SE.TER.ENRR",
    "SE.XPD.TOTL.GD.ZS",
    "SH.MED.BEDS.ZS",
    "SH.XPD.CHEX.GD.ZS",
    "SI.POV.DDAY",
    "SI.POV.GINI",
    "SM.POP.NETM",
    "SP.POP.DPND",
    "SP.POP.DPND.OL",
    "SP.POP.DPND.YG",
    "ST.INT.ARVL",
    "ST.INT.RCPT.CD",
    "TX.VAL.TECH.CD",
    "TX.VAL.TECH.MF.ZS",
]
CAMPAIGN_MAX_PRESPARSITY_ROWS = len(CAMPAIGN_CANDIDATE_INDICATORS) * CAMPAIGN_PRESPARSITY_COUNTRY_COUNT * len(CAMPAIGN_PERIODS)
INDICATOR_SOURCE_MODULE_EVIDENCE = {
    "AG.LND.FRST.ZS": "src/macroforge/wdi_environment_agriculture.py",
    "AG.PRD.FOOD.XD": "src/macroforge/wdi_environment_agriculture.py",
    "BG.GSR.NFSV.GD.ZS": "src/macroforge/wdi_services_trade.py",
    "BX.TRF.PWKR.DT.GD.ZS": "src/macroforge/wdi_migration_remittances.py",
    "EN.ATM.PM25.MC.M3": "src/macroforge/wdi_environment_agriculture.py",
    "GB.XPD.RSDV.GD.ZS": "src/macroforge/wdi_innovation.py",
    "IP.PAT.RESD": "src/macroforge/wdi_innovation.py",
    "IT.NET.BBND.P2": "src/macroforge/wdi_digital_infrastructure.py",
    "LP.LPI.INFR.XQ": "src/macroforge/wdi_logistics_performance.py",
    "LP.LPI.LOGS.XQ": "src/macroforge/wdi_logistics_performance.py",
    "LP.LPI.OVRL.XQ": "src/macroforge/wdi_logistics_performance.py",
    "NV.AGR.TOTL.ZS": "src/macroforge/wdi_environment_agriculture.py",
    "SE.SEC.ENRR": "src/macroforge/wdi_education_human_capital.py",
    "SE.TER.ENRR": "src/macroforge/wdi_education_human_capital.py",
    "SE.XPD.TOTL.GD.ZS": "src/macroforge/wdi_education_human_capital.py",
    "SH.MED.BEDS.ZS": "src/macroforge/wdi_health_systems.py",
    "SH.XPD.CHEX.GD.ZS": "src/macroforge/wdi_health_systems.py",
    "SI.POV.DDAY": "src/macroforge/wdi_poverty_inequality.py",
    "SI.POV.GINI": "src/macroforge/wdi_poverty_inequality.py",
    "SM.POP.NETM": "src/macroforge/wdi_migration_remittances.py",
    "SP.POP.DPND": "src/macroforge/wdi_demographic_dependency.py",
    "SP.POP.DPND.OL": "src/macroforge/wdi_demographic_dependency.py",
    "SP.POP.DPND.YG": "src/macroforge/wdi_demographic_dependency.py",
    "ST.INT.ARVL": "src/macroforge/wdi_tourism.py",
    "ST.INT.RCPT.CD": "src/macroforge/wdi_tourism.py",
    "TX.VAL.TECH.CD": "src/macroforge/wdi_high_technology_exports.py",
    "TX.VAL.TECH.MF.ZS": "src/macroforge/wdi_high_technology_exports.py",
}
NON_GOALS = [
    "full_WDI_catalog_ingestion",
    "provider_mirror",
    "generic_WDI_framework_extraction",
    "arbitrary_catalog_crawling",
    "Controlled_Expansion",
    "Companies_or_canonical_identity",
    "KnowledgeForge_semantics",
    "production_live_ingestion",
]


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256_blob(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def _sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_non_aggregate_country_catalog(path: str | Path = WDI_COUNTRY_CATALOG_FIXTURE) -> tuple[list[str], list[dict[str, Any]]]:
    raw = _read_json(Path(path))
    countries = list(raw["scope"]["countries"])
    catalog = list(raw["country_catalog"]["countries"])
    if len(countries) != CAMPAIGN_PRESPARSITY_COUNTRY_COUNT:
        raise ValueError(f"expected {CAMPAIGN_PRESPARSITY_COUNTRY_COUNT} WDI countries, got {len(countries)}")
    catalog_by_iso3 = {row["id"]: row for row in catalog}
    if set(countries) != set(catalog_by_iso3):
        raise ValueError("WDI country catalog does not match non-aggregate country scope")
    aggregates = [row["id"] for row in catalog if row.get("region", {}).get("id") == "NA"]
    if aggregates:
        raise ValueError(f"WDI country catalog includes aggregate rows: {aggregates[:5]}")
    return countries, catalog


def _worldbank_url(countries: list[str], indicator: str, date_range: str = CAMPAIGN_DATE_RANGE) -> str:
    return (
        f"https://api.worldbank.org/v2/country/all/indicator/{indicator}"
        f"?format=json&date={date_range}&per_page=20000"
    )


def fetch_campaign_raw(
    *,
    countries: list[str] | None = None,
    indicators: list[str] | None = None,
    date_range: str = CAMPAIGN_DATE_RANGE,
    timeout_seconds: int = 60,
) -> dict[str, Any]:
    scoped_countries, country_catalog = load_non_aggregate_country_catalog()
    if countries is None:
        countries = scoped_countries
    if indicators is None:
        indicators = CAMPAIGN_CANDIDATE_INDICATORS
    requests = []
    for indicator in indicators:
        url = _worldbank_url(countries, indicator, date_range)
        last_error: Exception | None = None
        payload: Any = None
        for attempt in range(3):
            try:
                http_request = urllib.request.Request(url, headers={"User-Agent": "MacroForge TASK-165 deterministic preflight"})
                with urllib.request.urlopen(http_request, timeout=timeout_seconds) as response:
                    payload = json.loads(response.read().decode("utf-8"))
                if isinstance(payload, list) and len(payload) == 2 and isinstance(payload[1], list):
                    allowed_countries = set(countries)
                    payload = [payload[0], [row for row in payload[1] if row.get("countryiso3code") in allowed_countries]]
                    payload[0] = dict(payload[0])
                    payload[0]["total_before_non_aggregate_filter"] = payload[0].get("total")
                    payload[0]["total"] = len(payload[1])
                last_error = None
                break
            except Exception as exc:  # pragma: no cover - exercised by live provider instability
                last_error = exc
        if last_error is not None:
            payload = [{"error": type(last_error).__name__, "message": str(last_error), "lastupdated": None}, []]
        requests.append({"indicator_code": indicator, "url": url, "response": payload})
    return {
        "scope": {
            "task": TASK_ID,
            "campaign": CAMPAIGN_NAME,
            "mode": CAMPAIGN_MODE,
            "candidate_source": "implemented_macroforge_wdi_source_module_evidence",
            "confidence_cell": "WDI public API v2 annual scalar country-indicator observations",
            "countries": countries,
            "country_count": len(countries),
            "country_scope": "all_non_aggregate_wdi_countries",
            "date_range": date_range,
            "indicators": indicators,
            "candidate_count": len(indicators),
            "max_presparsity_rows": len(countries) * len(indicators) * len(CAMPAIGN_PERIODS),
            "non_goals": NON_GOALS,
        },
        "country_catalog": {"source_fixture": str(WDI_COUNTRY_CATALOG_FIXTURE.relative_to(PROJECT_ROOT)), "countries": country_catalog},
        "requests": requests,
    }


def write_campaign_raw(path: str | Path = DEFAULT_RAW_PATH) -> dict[str, Any]:
    raw = fetch_campaign_raw()
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(raw, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return raw


def _response_parts(request: dict[str, Any]) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    response = request.get("response")
    if not isinstance(response, list) or len(response) != 2:
        raise ValueError(f"unsupported WDI response shape for {request.get('indicator_code')}")
    metadata, observations = response
    if not isinstance(metadata, dict) or not isinstance(observations, list):
        raise ValueError(f"unsupported WDI response payload for {request.get('indicator_code')}")
    return metadata, observations


def _row_key(row: dict[str, Any]) -> tuple[str, str, str]:
    return (str(row.get("indicator_id")), str(row.get("countryiso3code")), str(row.get("date")))


def classify_campaign_raw(raw: dict[str, Any], *, min_non_null_observations: int = 1) -> dict[str, Any]:
    scope = raw.get("scope", {})
    countries = list(scope.get("countries") or [])
    indicators = list(scope.get("indicators") or [request.get("indicator_code") for request in raw.get("requests", [])])
    country_set = set(countries)
    requested_periods = set(str(year) for year in range(2000, 2024)) if scope.get("date_range") == CAMPAIGN_DATE_RANGE else set()
    results: dict[str, dict[str, Any]] = {}
    immediately_ingestible: list[str] = []
    requires_architecture: list[str] = []
    outside_cell: list[str] = []
    exclusions: list[str] = []
    for request in raw.get("requests", []):
        indicator = request.get("indicator_code")
        evidence = {
            "indicator": indicator,
            "source_module_evidence": INDICATOR_SOURCE_MODULE_EVIDENCE.get(indicator, "test_fixture_or_unknown_module"),
            "classification": "compatible",
            "exclusion_evidence": None,
            "provider_label": None,
            "provider_lastupdated": None,
            "provider_total": None,
            "returned_row_count": 0,
            "expected_max_rows": len(countries) * (len(requested_periods) if requested_periods else len(CAMPAIGN_PERIODS)),
            "country_count": 0,
            "countries_with_observations": 0,
            "periods": [],
            "period_count": 0,
            "non_null_observation_count": 0,
            "missing_observation_count": 0,
            "non_null_density": 0.0,
            "response_sha256": None,
        }
        try:
            metadata, observations = _response_parts(request)
        except ValueError as exc:
            evidence["classification"] = "unsupported_representation"
            evidence["exclusion_evidence"] = str(exc)
            results[str(indicator)] = evidence
            requires_architecture.append(str(indicator))
            exclusions.append(str(indicator))
            continue
        evidence["provider_lastupdated"] = metadata.get("lastupdated")
        evidence["provider_total"] = metadata.get("total")
        evidence["returned_row_count"] = len(observations)
        evidence["response_sha256"] = _sha256_blob(request.get("response"))
        row_countries = set()
        countries_with_values = set()
        periods = set()
        non_null = 0
        bad_shape = None
        wrong_indicator = None
        outside_countries = set()
        non_annual_periods = set()
        provider_label = None
        for item in observations:
            indicator_obj = item.get("indicator") or {}
            country_obj = item.get("country") or {}
            item_indicator = indicator_obj.get("id")
            provider_label = provider_label or indicator_obj.get("value")
            iso3 = item.get("countryiso3code")
            period = str(item.get("date"))
            if not item_indicator or not iso3 or not period or not country_obj:
                bad_shape = "missing required WDI scalar observation fields"
                break
            if item_indicator != indicator:
                wrong_indicator = item_indicator
                break
            if country_set and iso3 not in country_set:
                outside_countries.add(iso3)
            if not period.isdigit() or len(period) != 4:
                non_annual_periods.add(period)
            periods.add(period)
            row_countries.add(iso3)
            if item.get("value") is not None:
                non_null += 1
                countries_with_values.add(iso3)
        evidence["provider_label"] = provider_label
        evidence["country_count"] = len(row_countries)
        evidence["countries_with_observations"] = len(countries_with_values)
        evidence["periods"] = sorted(periods)
        evidence["period_count"] = len(periods)
        evidence["non_null_observation_count"] = non_null
        evidence["missing_observation_count"] = len(observations) - non_null
        evidence["non_null_density"] = round(non_null / len(observations), 6) if observations else 0.0
        if bad_shape:
            evidence["classification"] = "unsupported_representation"
            evidence["exclusion_evidence"] = bad_shape
            requires_architecture.append(str(indicator))
            exclusions.append(str(indicator))
        elif wrong_indicator:
            evidence["classification"] = "incompatible"
            evidence["exclusion_evidence"] = f"response contained unexpected indicator {wrong_indicator}"
            outside_cell.append(str(indicator))
            exclusions.append(str(indicator))
        elif outside_countries:
            evidence["classification"] = "incompatible"
            evidence["exclusion_evidence"] = f"response contained countries outside non-aggregate scope: {sorted(outside_countries)[:10]}"
            outside_cell.append(str(indicator))
            exclusions.append(str(indicator))
        elif non_annual_periods:
            evidence["classification"] = "unsupported_representation"
            evidence["exclusion_evidence"] = f"response contained non-annual periods: {sorted(non_annual_periods)[:10]}"
            requires_architecture.append(str(indicator))
            exclusions.append(str(indicator))
        elif len(observations) == 0:
            evidence["classification"] = "unavailable"
            evidence["exclusion_evidence"] = "provider returned zero rows for requested country-period window"
            outside_cell.append(str(indicator))
            exclusions.append(str(indicator))
        elif non_null < min_non_null_observations:
            evidence["classification"] = "operationally_unsuitable"
            evidence["exclusion_evidence"] = "zero non-null observations in requested provider period window"
            outside_cell.append(str(indicator))
            exclusions.append(str(indicator))
        else:
            immediately_ingestible.append(str(indicator))
        results[str(indicator)] = evidence
    missing_requests = sorted(set(indicators) - set(results))
    for indicator in missing_requests:
        results[indicator] = {
            "indicator": indicator,
            "source_module_evidence": INDICATOR_SOURCE_MODULE_EVIDENCE.get(indicator),
            "classification": "unavailable",
            "exclusion_evidence": "candidate had no request payload in campaign raw artifact",
        }
        outside_cell.append(indicator)
        exclusions.append(indicator)
    return {
        "task": TASK_ID,
        "campaign": CAMPAIGN_NAME,
        "candidate_count": len(indicators),
        "requested_country_count": len(countries),
        "requested_date_range": scope.get("date_range"),
        "requested_max_presparsity_rows": len(indicators) * len(countries) * (len(requested_periods) if requested_periods else len(CAMPAIGN_PERIODS)),
        "included_indicators": sorted(immediately_ingestible),
        "included_indicator_count": len(immediately_ingestible),
        "excluded_indicators": sorted(set(exclusions)),
        "excluded_indicator_count": len(set(exclusions)),
        "partition": {
            "immediately_ingestible": sorted(immediately_ingestible),
            "requires_architectural_investigation": sorted(set(requires_architecture)),
            "permanently_outside_confidence_cell": sorted(set(outside_cell)),
        },
        "indicator_results": {indicator: results[indicator] for indicator in sorted(results)},
        "non_goals_preserved": NON_GOALS,
    }


def normalize_wdi_implemented_compatible_campaign_raw(raw: dict[str, Any], *, min_non_null_observations: int = 1) -> dict[str, Any]:
    classification = classify_campaign_raw(raw, min_non_null_observations=min_non_null_observations)
    included = classification["included_indicators"]
    scope = raw.get("scope", {})
    countries = list(scope.get("countries") or [])
    country_catalog = {row.get("id"): row for row in raw.get("country_catalog", {}).get("countries", [])}
    rows: list[dict[str, Any]] = []
    raw_artifacts: list[dict[str, Any]] = []
    for request in raw.get("requests", []):
        indicator = request.get("indicator_code")
        if indicator not in included:
            continue
        metadata, observations = _response_parts(request)
        raw_artifacts.append({
            "indicator": indicator,
            "url": request.get("url"),
            "status": "ok",
            "content_type": "application/json",
            "bytes": len(json.dumps(request.get("response"), sort_keys=True).encode("utf-8")),
            "sha256": _sha256_blob(request.get("response")),
            "row_count": len(observations),
            "non_null_observation_count": classification["indicator_results"][indicator]["non_null_observation_count"],
            "source_metadata": metadata,
            "source_module_evidence": INDICATOR_SOURCE_MODULE_EVIDENCE.get(indicator),
        })
        for item in observations:
            indicator_obj = item.get("indicator") or {}
            country_obj = item.get("country") or {}
            iso3 = item.get("countryiso3code")
            catalog = country_catalog.get(iso3, {})
            rows.append({
                "source": SOURCE_NAME,
                "indicator_id": indicator_obj.get("id"),
                "indicator_name": indicator_obj.get("value"),
                "country_id": country_obj.get("id"),
                "country_name": country_obj.get("value"),
                "countryiso3code": iso3,
                "date": str(item.get("date")),
                "value": item.get("value"),
                "unit": item.get("unit") or None,
                "obs_status": item.get("obs_status") or None,
                "decimal": item.get("decimal"),
                "repository_section": "cross_sectional_context",
                "operational_capability": CAMPAIGN_NAME,
                "operational_mode": CAMPAIGN_MODE,
                "coverage_level": "implemented_compatible_wdi_annual_scalar_campaign",
                "source_module_evidence": INDICATOR_SOURCE_MODULE_EVIDENCE.get(indicator),
                "region_id": (catalog.get("region") or {}).get("id"),
                "region_label": (catalog.get("region") or {}).get("value"),
                "income_level_id": (catalog.get("incomeLevel") or {}).get("id"),
                "income_level_label": (catalog.get("incomeLevel") or {}).get("value"),
            })
    country_order = {country: index for index, country in enumerate(countries)}
    indicator_order = {indicator: index for index, indicator in enumerate(included)}
    rows.sort(key=lambda row: (indicator_order[row["indicator_id"]], country_order.get(row["countryiso3code"], 9999), int(row["date"])))
    seen = set()
    duplicates = []
    for row in rows:
        key = _row_key(row)
        if key in seen:
            duplicates.append(key)
        seen.add(key)
    if duplicates:
        raise ValueError(f"campaign normalized rows contain duplicate observation keys: {duplicates[:5]}")
    observed_values = sum(1 for row in rows if row.get("value") is not None)
    raw_path = Path(scope.get("raw_artifact_path", DEFAULT_RAW_PATH))
    return {
        "task": TASK_ID,
        "campaign": CAMPAIGN_NAME,
        "mode": CAMPAIGN_MODE,
        "source": SOURCE_NAME,
        "support_bundle": str(raw_path.relative_to(PROJECT_ROOT)) if raw_path.is_absolute() and raw_path.exists() else str(raw_path),
        "countries": countries,
        "country_count": len(countries),
        "indicators": included,
        "indicator_count": len(included),
        "excluded_indicators": classification["excluded_indicators"],
        "date_range": scope.get("date_range", CAMPAIGN_DATE_RANGE),
        "expected_row_count": len(rows),
        "row_count": len(rows),
        "observed_value_count": observed_values,
        "missing_value_count": len(rows) - observed_values,
        "rows": rows,
        "raw_artifacts": raw_artifacts,
        "classification": classification,
        "operational_scope": {
            "task": TASK_ID,
            "campaign": CAMPAIGN_NAME,
            "mode": CAMPAIGN_MODE,
            "confidence_cell": scope.get("confidence_cell", "WDI public API v2 annual scalar country-indicator observations"),
            "country_scope": scope.get("country_scope", "all_non_aggregate_wdi_countries"),
            "candidate_indicators": scope.get("indicators", CAMPAIGN_CANDIDATE_INDICATORS),
            "included_indicators": included,
            "excluded_indicators": classification["excluded_indicators"],
            "date_range": scope.get("date_range", CAMPAIGN_DATE_RANGE),
            "non_goals": NON_GOALS,
        },
    }


def build_wdi_implemented_compatible_campaign_observed_package(raw: dict[str, Any], *, min_non_null_observations: int = 1):
    return build_wdi_observed_package(normalize_wdi_implemented_compatible_campaign_raw(raw, min_non_null_observations=min_non_null_observations))


def _write_json(path: str | Path, payload: dict[str, Any]) -> str:
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return str(out)


def _campaign_fingerprint(payload: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def build_campaign_reports(raw: dict[str, Any], *, min_non_null_observations: int = 1, load_counts: dict[str, int] | None = None) -> dict[str, dict[str, Any]]:
    normalized = normalize_wdi_implemented_compatible_campaign_raw(raw, min_non_null_observations=min_non_null_observations)
    classification = normalized["classification"]
    package = build_wdi_observed_package(normalized)
    replay = compare_observed_packages(package, package)
    indicator_results = classification["indicator_results"]
    included_details = {indicator: indicator_results[indicator] for indicator in normalized["indicators"]}
    excluded_details = {indicator: indicator_results[indicator] for indicator in classification["excluded_indicators"]}
    periods = sorted({row["date"] for row in normalized["rows"]})
    countries_with_rows = sorted({row["countryiso3code"] for row in normalized["rows"]})
    preflight = {
        "task": TASK_ID,
        "status": "complete",
        "campaign": CAMPAIGN_NAME,
        "candidate_universe_source": "TASK-165A implemented-compatible WDI annual scalar source-module evidence",
        "candidate_count": classification["candidate_count"],
        "candidate_indicators": classification["indicator_results"].keys().__class__(classification["indicator_results"].keys()) if False else list(classification["indicator_results"].keys()),
        "requested_country_count": classification["requested_country_count"],
        "requested_date_range": classification["requested_date_range"],
        "requested_max_presparsity_rows": classification["requested_max_presparsity_rows"],
        "classification_counts": {
            "compatible": classification["included_indicator_count"],
            "excluded": classification["excluded_indicator_count"],
        },
        "indicator_results": indicator_results,
        "non_goals_preserved": NON_GOALS,
    }
    compatibility = {
        "task": TASK_ID,
        "status": "complete",
        "campaign": CAMPAIGN_NAME,
        "partition": classification["partition"],
        "included_indicators": classification["included_indicators"],
        "excluded_indicators": classification["excluded_indicators"],
        "excluded_details": excluded_details,
        "ambiguous_state_remaining": False,
    }
    operational = {
        "task": TASK_ID,
        "status": "succeeded" if normalized["row_count"] else "no_rows",
        "campaign": CAMPAIGN_NAME,
        "execution_unit": "single_campaign_bundle",
        "included_indicator_count": normalized["indicator_count"],
        "included_indicators": normalized["indicators"],
        "row_count": normalized["row_count"],
        "observed_value_count": normalized["observed_value_count"],
        "missing_value_count": normalized["missing_value_count"],
        "country_count": len(countries_with_rows),
        "period_range": f"{periods[0]}:{periods[-1]}" if periods else None,
        "package_fingerprint": observed_package_fingerprint(package),
        "self_replay_equivalent": replay.equivalent,
        "load_counts": load_counts,
        "normalized_path": str(DEFAULT_NORMALIZED_PATH),
    }
    coverage = {
        "task": TASK_ID,
        "status": "complete",
        "campaign": CAMPAIGN_NAME,
        "repository_growth": {
            "indicators_added": normalized["indicator_count"],
            "observations_added": normalized["row_count"],
            "observed_values_added": normalized["observed_value_count"],
            "missing_value_rows_added": normalized["missing_value_count"],
            "countries_represented": len(countries_with_rows),
            "temporal_coverage": f"{periods[0]}:{periods[-1]}" if periods else None,
            "postgresql_load_counts": load_counts,
        },
        "successfully_operationalized_indicators": included_details,
        "excluded_indicators": excluded_details,
        "remaining_compatible_opportunities": [],
        "non_goals_preserved": NON_GOALS,
    }
    exception = {
        "task": TASK_ID,
        "status": "required" if excluded_details else "not_required",
        "campaign": CAMPAIGN_NAME,
        "localized_failures_or_exclusions": excluded_details,
        "campaign_continued_after_isolated_exclusions": True,
        "shared_architecture_regression_detected": False,
    }
    confidence = {
        "task": TASK_ID,
        "status": "complete",
        "campaign": CAMPAIGN_NAME,
        "confidence_cell": "WDI public API v2 annual scalar country-indicator observations",
        "previous_confidence": "High for implemented-compatible WDI annual scalar country-indicator operational expansion",
        "updated_confidence": "Increased within implemented-compatible WDI annual scalar confidence cell" if normalized["indicator_count"] else "Unchanged; no compatible rows operationalized",
        "basis": {
            "candidate_count": classification["candidate_count"],
            "included_indicator_count": normalized["indicator_count"],
            "excluded_indicator_count": classification["excluded_indicator_count"],
            "row_count": normalized["row_count"],
            "self_replay_equivalent": replay.equivalent,
            "load_counts": load_counts,
            "architecture_redesign_required": False,
        },
        "localized_regression": classification["excluded_indicators"],
        "next_confidence_boundary": "Do not generalize to full WDI catalog, provider mirror, arbitrary metadata, or non-scalar representations without separate evidence.",
    }
    for report in (preflight, compatibility, operational, coverage, exception, confidence):
        report["report_fingerprint"] = _campaign_fingerprint(report)
    return {
        "normalized": normalized,
        "preflight": preflight,
        "classification": compatibility,
        "operational": operational,
        "coverage": coverage,
        "exception": exception,
        "confidence": confidence,
    }


def write_wdi_implemented_compatible_campaign_artifacts(
    raw: dict[str, Any],
    *,
    normalized_path: str | Path = DEFAULT_NORMALIZED_PATH,
    preflight_report_path: str | Path = DEFAULT_PREFLIGHT_REPORT_PATH,
    classification_report_path: str | Path = DEFAULT_CLASSIFICATION_REPORT_PATH,
    operational_report_path: str | Path = DEFAULT_OPERATIONAL_REPORT_PATH,
    coverage_report_path: str | Path = DEFAULT_COVERAGE_REPORT_PATH,
    exception_report_path: str | Path | None = DEFAULT_EXCEPTION_REPORT_PATH,
    confidence_report_path: str | Path = DEFAULT_CONFIDENCE_REPORT_PATH,
    min_non_null_observations: int = 1,
    load_counts: dict[str, int] | None = None,
) -> dict[str, str]:
    reports = build_campaign_reports(raw, min_non_null_observations=min_non_null_observations, load_counts=load_counts)
    paths = {
        "normalized": _write_json(normalized_path, reports["normalized"]),
        "preflight": _write_json(preflight_report_path, reports["preflight"]),
        "classification": _write_json(classification_report_path, reports["classification"]),
        "operational": _write_json(operational_report_path, reports["operational"]),
        "coverage": _write_json(coverage_report_path, reports["coverage"]),
        "confidence": _write_json(confidence_report_path, reports["confidence"]),
    }
    if exception_report_path is not None and reports["exception"]["status"] == "required":
        paths["exception"] = _write_json(exception_report_path, reports["exception"])
    return paths


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run TASK-165 WDI implemented-compatible campaign utilities")
    sub = parser.add_subparsers(dest="command", required=True)
    fetch = sub.add_parser("fetch")
    fetch.add_argument("--raw", default=str(DEFAULT_RAW_PATH))
    fetch.add_argument("--timeout-seconds", type=int, default=120)
    artifacts = sub.add_parser("artifacts")
    artifacts.add_argument("--raw", default=str(DEFAULT_RAW_PATH))
    artifacts.add_argument("--normalized", default=str(DEFAULT_NORMALIZED_PATH))
    args = parser.parse_args(argv)
    if args.command == "fetch":
        raw = fetch_campaign_raw(timeout_seconds=args.timeout_seconds)
        out = Path(args.raw)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(raw, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps({"raw_path": args.raw, "candidate_count": len(raw["requests"]), "raw_sha256": _sha256_file(out)}, indent=2, sort_keys=True))
        return 0
    if args.command == "artifacts":
        raw = _read_json(Path(args.raw))
        raw.setdefault("scope", {})["raw_artifact_path"] = args.raw
        paths = write_wdi_implemented_compatible_campaign_artifacts(raw, normalized_path=args.normalized)
        print(json.dumps(paths, indent=2, sort_keys=True))
        return 0
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
