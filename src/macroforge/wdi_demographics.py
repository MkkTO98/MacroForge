from __future__ import annotations

import json
from decimal import Decimal
from pathlib import Path
from typing import Any
import hashlib

from macroforge.observed_ingestion import ObservedIngestionPackage, ObservedObservation, canonical_attribute_hash
from macroforge.wdi_observed import (
    build_wdi_macro_indicators_refresh_delta_report,
    build_wdi_observed_package,
    observed_package_fingerprint,
    refresh_delta_report_fingerprint,
)

SOURCE_CODE = "WDI_DEMOGRAPHICS"
SOURCE_NAME = "World Bank WDI bounded demographic foundation evidence slice"
SOURCE_HOME_URL = "https://data.worldbank.org/"
PROVIDER_DATASET_CODE = "WDI:DEMOGRAPHIC_FOUNDATION"
FREQUENCY = "A"
SCOPE = "bounded TASK-061 WDI demographic foundation evidence slice"
EXPECTED_COUNTRIES = ("USA", "JPN")
EXPECTED_PERIODS = ("2022", "2023")
EXPECTED_INDICATORS = (
    "SP.POP.TOTL",
    "SP.POP.GROW",
    "SP.POP.0014.TO.ZS",
    "SP.POP.1564.TO.ZS",
    "SP.POP.65UP.TO.ZS",
    "SP.DYN.TFRT.IN",
    "SP.DYN.LE00.IN",
    "SP.URB.TOTL.IN.ZS",
)
EXPECTED_ROW_COUNT = len(EXPECTED_COUNTRIES) * len(EXPECTED_PERIODS) * len(EXPECTED_INDICATORS)

INDICATOR_METADATA = {
    "SP.POP.TOTL": {
        "concept": "population_total",
        "unit_code": "PERSONS",
        "unit_label": "persons",
        "foundation_group": "population",
    },
    "SP.POP.GROW": {
        "concept": "population_growth",
        "unit_code": "ANNUAL_PERCENT",
        "unit_label": "annual percent",
        "foundation_group": "population_growth",
    },
    "SP.POP.0014.TO.ZS": {
        "concept": "age_structure_0_14",
        "unit_code": "PERCENT_OF_TOTAL_POPULATION",
        "unit_label": "percent of total population",
        "foundation_group": "age_structure",
    },
    "SP.POP.1564.TO.ZS": {
        "concept": "age_structure_15_64",
        "unit_code": "PERCENT_OF_TOTAL_POPULATION",
        "unit_label": "percent of total population",
        "foundation_group": "age_structure",
    },
    "SP.POP.65UP.TO.ZS": {
        "concept": "age_structure_65_plus",
        "unit_code": "PERCENT_OF_TOTAL_POPULATION",
        "unit_label": "percent of total population",
        "foundation_group": "age_structure",
    },
    "SP.DYN.TFRT.IN": {
        "concept": "fertility",
        "unit_code": "BIRTHS_PER_WOMAN",
        "unit_label": "births per woman",
        "foundation_group": "fertility",
    },
    "SP.DYN.LE00.IN": {
        "concept": "life_expectancy",
        "unit_code": "YEARS",
        "unit_label": "years",
        "foundation_group": "life_expectancy",
    },
    "SP.URB.TOTL.IN.ZS": {
        "concept": "urbanization",
        "unit_code": "PERCENT_OF_TOTAL_POPULATION",
        "unit_label": "percent of total population",
        "foundation_group": "urbanization",
    },
}


def normalize_wdi_demographic_foundation_fixture(
    raw_payload: str | bytes,
    *,
    raw_artifact_path: str,
    raw_sha256: str,
    content_type: str,
) -> dict[str, Any]:
    """Normalize only the bounded TASK-061 WDI demographic foundation fixture."""

    payload = json.loads(_coerce_payload(raw_payload))
    if not isinstance(payload, dict):
        raise ValueError("TASK-061 WDI demographic fixture must be a JSON object")
    requests = payload.get("requests")
    if not isinstance(requests, list):
        raise ValueError("TASK-061 WDI demographic fixture must contain a requests array")

    rows: list[dict[str, Any]] = []
    source_urls: list[str] = []
    request_metadata: dict[str, Any] = {}
    for request in requests:
        if not isinstance(request, dict):
            raise ValueError("TASK-061 WDI demographic request entries must be JSON objects")
        indicator_code = str(request.get("indicator_code"))
        _validate_indicator_code(indicator_code)
        source_urls.append(str(request.get("url")))
        response = request.get("response")
        if not (isinstance(response, list) and len(response) == 2):
            raise ValueError(f"WDI response for {indicator_code} must be [metadata, rows]")
        metadata, data_rows = response
        if not isinstance(metadata, dict) or not isinstance(data_rows, list):
            raise ValueError(f"WDI response for {indicator_code} has invalid metadata or rows")
        request_metadata[indicator_code] = {
            "page": metadata.get("page"),
            "pages": metadata.get("pages"),
            "per_page": metadata.get("per_page"),
            "total": metadata.get("total"),
            "sourceid": metadata.get("sourceid"),
            "lastupdated": metadata.get("lastupdated"),
        }
        rows.extend(_normalize_record(record, indicator_code=indicator_code, request_metadata=request_metadata[indicator_code]) for record in data_rows)

    rows.sort(key=lambda row: (_indicator_order(row["provider_indicator_code"]), row["territory_code"], row["provider_period_code"]))
    periods = sorted({row["provider_period_code"] for row in rows})
    period_range = f"{periods[0]}-{periods[-1]}" if periods else "unknown"
    return {
        "source_code": SOURCE_CODE,
        "source_urls": source_urls,
        "content_type": content_type,
        "raw_artifact_path": raw_artifact_path,
        "raw_sha256": raw_sha256,
        "provider_dataset_code": PROVIDER_DATASET_CODE,
        "frequency": FREQUENCY,
        "period_range": period_range,
        "row_count": len(rows),
        "expected_row_count": EXPECTED_ROW_COUNT,
        "input_filters": {
            "countries": list(EXPECTED_COUNTRIES),
            "periods": list(EXPECTED_PERIODS),
            "indicators": list(EXPECTED_INDICATORS),
            "scope": SCOPE,
        },
        "provider_metadata": {
            "provider": "World Bank",
            "provider_name": "World Bank World Development Indicators",
            "api_surface": "World Bank API v2",
            "indicator_count": len(EXPECTED_INDICATORS),
            "country_count": len(EXPECTED_COUNTRIES),
            "period_count": len(EXPECTED_PERIODS),
            "request_metadata": request_metadata,
        },
        "rows": rows,
    }


def build_wdi_demographic_foundation_observed_package(normalized: dict[str, Any]) -> ObservedIngestionPackage:
    observations = []
    for row in normalized["rows"]:
        attributes = dict(row["attributes"])
        observations.append(
            ObservedObservation(
                provider_indicator_code=row["provider_indicator_code"],
                provider_indicator_label=row["provider_indicator_label"],
                provider_territory_code=row["territory_code"],
                provider_territory_label=row["territory_label"],
                provider_period_code=row["provider_period_code"],
                frequency=row["frequency"],
                period_year=row["period_year"],
                unit_code=row["unit_code"],
                unit_label=row["unit_label"],
                value=row["value"],
                observation_status=row["observation_status"],
                decimal_precision=row["decimal_precision"],
                attributes=attributes,
                source_payload=dict(row["source_payload"]),
                attribute_hash=canonical_attribute_hash(attributes),
            )
        )

    return ObservedIngestionPackage(
        source_code=SOURCE_CODE,
        source_name=SOURCE_NAME,
        source_home_url=SOURCE_HOME_URL,
        provider_dataset_code=normalized["provider_dataset_code"],
        release_key=_release_key(normalized),
        raw_evidence={
            "source_urls": list(normalized["source_urls"]),
            "content_type": normalized["content_type"],
            "raw_artifact_path": normalized["raw_artifact_path"],
            "raw_sha256": normalized["raw_sha256"],
            "provider_metadata": dict(normalized["provider_metadata"]),
        },
        input_filters=dict(normalized["input_filters"]),
        row_count=len(observations),
        expected_row_count=normalized["expected_row_count"],
        observations=tuple(observations),
    )


def _coerce_payload(raw_payload: str | bytes) -> str:
    if isinstance(raw_payload, bytes):
        return raw_payload.decode("utf-8-sig")
    return raw_payload.lstrip("\ufeff")


def _normalize_record(record: dict[str, Any], *, indicator_code: str, request_metadata: dict[str, Any]) -> dict[str, Any]:
    _validate_record_scope(record, indicator_code)
    indicator = record["indicator"]
    country = record["country"]
    meta = INDICATOR_METADATA[indicator_code]
    value = record.get("value")
    attributes = {
        "source_provider": "World Bank WDI",
        "demographic_concept": meta["concept"],
        "foundation_group": meta["foundation_group"],
        "indicator_id": indicator_code,
        "indicator_label": str(indicator["value"]),
        "country_id": str(country["id"]),
        "countryiso3code": str(record["countryiso3code"]),
        "country_name": str(country["value"]),
        "world_bank_unit": str(record.get("unit", "")),
        "world_bank_obs_status": str(record.get("obs_status", "")),
        "world_bank_decimal": record.get("decimal"),
        "world_bank_sourceid": request_metadata.get("sourceid"),
        "world_bank_lastupdated": request_metadata.get("lastupdated"),
    }
    return {
        "provider_indicator_code": indicator_code,
        "provider_indicator_label": str(indicator["value"]),
        "territory_code": str(record["countryiso3code"]),
        "territory_label": str(country["value"]),
        "provider_period_code": str(record["date"]),
        "frequency": FREQUENCY,
        "period_year": int(record["date"]),
        "unit_code": meta["unit_code"],
        "unit_label": meta["unit_label"],
        "value": value,
        "observation_status": "missing" if value is None else "observed",
        "decimal_precision": _decimal_precision(value),
        "demographic_concept": meta["concept"],
        "attributes": attributes,
        "source_payload": dict(record),
    }


def _validate_record_scope(record: dict[str, Any], indicator_code: str) -> None:
    required = {"indicator", "country", "countryiso3code", "date", "value", "unit", "obs_status", "decimal"}
    missing = required - set(record)
    if missing:
        raise ValueError(f"WDI demographic record missing required fields: {sorted(missing)}")
    indicator = record["indicator"]
    country = record["country"]
    if not isinstance(indicator, dict) or not isinstance(country, dict):
        raise ValueError("WDI demographic record indicator and country fields must be objects")
    if str(indicator.get("id")) != indicator_code:
        raise ValueError(f"WDI demographic record indicator mismatch: {indicator.get('id')} != {indicator_code}")
    _validate_indicator_code(indicator_code)
    country_iso = str(record["countryiso3code"])
    if country_iso not in EXPECTED_COUNTRIES:
        raise ValueError(f"Unexpected WDI demographic country: {country_iso}")
    period = str(record["date"])
    if period not in EXPECTED_PERIODS:
        raise ValueError(f"Unexpected WDI demographic period: {period}")


def _validate_indicator_code(indicator_code: str) -> None:
    if indicator_code not in EXPECTED_INDICATORS:
        raise ValueError(f"Unexpected WDI demographic indicator: {indicator_code}")


def _indicator_order(indicator_code: str) -> int:
    return EXPECTED_INDICATORS.index(indicator_code)


def _decimal_precision(value: Any) -> int:
    if value is None:
        return 0
    decimal = Decimal(str(value)).normalize()
    if decimal == decimal.to_integral():
        return 0
    exponent = decimal.as_tuple().exponent
    if not isinstance(exponent, int):
        return 0
    return max(0, -exponent)


def _release_key(normalized: dict[str, Any]) -> str:
    return f"{SOURCE_CODE}:USA-JPN:{normalized['period_range']}:{normalized['raw_sha256'][:12]}"

# TASK-133 Knowledge Leverage / Operational Capability Expansion: WDI Demographics Phase 1
DEMOGRAPHICS_PHASE1_TASK_ID = "TASK-133"
DEMOGRAPHICS_PHASE1_MODE = "Operational Capability Expansion"
DEMOGRAPHICS_PHASE1_PHASE = "WDI Demographics Phase 1"
DEMOGRAPHICS_PHASE1_CAPABILITY = "WDI demographics operational foundation"
DEMOGRAPHICS_PHASE1_KNOWLEDGE_LEVERAGE = "demographic_foundation"
DEMOGRAPHICS_PHASE1_RAW_FIXTURE_PATH = "data/raw/wdi_demographics_phase1/wdi-demographics-phase1-all-countries-8i-2000-2023.json"
DEMOGRAPHICS_PHASE1_RAW_SHA256 = "81e113754293e66fbfd089e74548852772e182889a5a5a226425c642b43d5281"
DEMOGRAPHICS_PHASE1_DEFAULT_NORMALIZED_PATH = "data/metadata/wdi_demographics_phase1/wdi-demographics-phase1-normalized.json"
DEMOGRAPHICS_PHASE1_DEFAULT_REFRESH_MANIFEST_PATH = "data/operational/wdi_demographics_phase1/wdi-demographics-phase1-refresh-manifest.json"
DEMOGRAPHICS_PHASE1_DEFAULT_REFRESH_DELTA_PATH = "data/operational/wdi_demographics_phase1/wdi-demographics-phase1-refresh-delta-report.json"
DEMOGRAPHICS_PHASE1_INDICATORS = list(EXPECTED_INDICATORS)
DEMOGRAPHICS_PHASE1_DATE_RANGE = "2000:2023"
DEMOGRAPHICS_PHASE1_YEARS = [str(year) for year in range(2000, 2024)]
DEMOGRAPHICS_PHASE1_COUNTRY_COUNT = 217
DEMOGRAPHICS_PHASE1_EXPECTED_OBSERVATION_COUNT = DEMOGRAPHICS_PHASE1_COUNTRY_COUNT * len(DEMOGRAPHICS_PHASE1_INDICATORS) * len(DEMOGRAPHICS_PHASE1_YEARS)
DEMOGRAPHICS_PHASE1_DEFAULT_RUN_KEY = "task-133-wdi-demographics-phase1-knowledge-leverage"


def _phase1_countries(raw: dict[str, Any]) -> list[str]:
    countries = raw.get("scope", {}).get("countries", [])
    if len(countries) != DEMOGRAPHICS_PHASE1_COUNTRY_COUNT:
        raise ValueError(f"expected {DEMOGRAPHICS_PHASE1_COUNTRY_COUNT} countries, got {len(countries)}")
    if len(set(countries)) != len(countries):
        raise ValueError("WDI demographics Phase 1 country scope contains duplicate country ids")
    return countries


def _phase1_country_catalog(raw: dict[str, Any]) -> dict[str, dict[str, Any]]:
    catalog_rows = raw.get("country_catalog", {}).get("countries", [])
    catalog = {row.get("id"): row for row in catalog_rows}
    countries = _phase1_countries(raw)
    if set(catalog) != set(countries):
        raise ValueError("WDI demographics Phase 1 country catalog does not match scoped countries")
    if any(row.get("region", {}).get("id") == "NA" for row in catalog.values()):
        raise ValueError("WDI demographics Phase 1 includes aggregate rows")
    return catalog


def normalize_wdi_demographics_phase1_fixture(raw: dict[str, Any]) -> dict[str, Any]:
    """Normalize TASK-133 WDI Demographics Phase 1 into existing WDI loader-compatible shape."""

    scope = raw.get("scope", {})
    if scope.get("task") != DEMOGRAPHICS_PHASE1_TASK_ID:
        raise ValueError(f"unexpected task scope: {scope.get('task')}")
    if scope.get("mode") != DEMOGRAPHICS_PHASE1_MODE:
        raise ValueError(f"unexpected mode: {scope.get('mode')}")
    if scope.get("phase") != DEMOGRAPHICS_PHASE1_PHASE:
        raise ValueError(f"unexpected phase: {scope.get('phase')}")
    if scope.get("indicators") != DEMOGRAPHICS_PHASE1_INDICATORS:
        raise ValueError(f"unexpected indicator scope: {scope.get('indicators')}")
    if scope.get("date_range") != DEMOGRAPHICS_PHASE1_DATE_RANGE:
        raise ValueError(f"unexpected date range: {scope.get('date_range')}")
    if scope.get("expected_observation_count") != DEMOGRAPHICS_PHASE1_EXPECTED_OBSERVATION_COUNT:
        raise ValueError("WDI demographics Phase 1 expected observation count changed")

    countries = _phase1_countries(raw)
    country_catalog = _phase1_country_catalog(raw)
    requests = raw.get("requests", [])
    if [request.get("indicator_code") for request in requests] != DEMOGRAPHICS_PHASE1_INDICATORS:
        raise ValueError("WDI demographics Phase 1 request order must match validated indicator scope")

    rows: list[dict[str, Any]] = []
    raw_artifacts: list[dict[str, Any]] = []
    expected_rows_per_indicator = len(countries) * len(DEMOGRAPHICS_PHASE1_YEARS)
    for request in requests:
        indicator_code = request["indicator_code"]
        response = request.get("response")
        if not isinstance(response, list) or len(response) != 2:
            raise ValueError(f"unexpected WDI response shape for {indicator_code}")
        metadata, observations = response
        if metadata.get("lastupdated") is None:
            raise ValueError(f"missing WDI lastupdated metadata for {indicator_code}")
        if len(observations) != expected_rows_per_indicator:
            raise ValueError(f"unexpected WDI demographics observation count for {indicator_code}: {len(observations)}")
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
            "raw_file": DEMOGRAPHICS_PHASE1_RAW_FIXTURE_PATH.rsplit("/", 1)[-1],
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
                "demographic_concept": meta["concept"],
                "demographic_group": meta["foundation_group"],
                "operational_capability": DEMOGRAPHICS_PHASE1_CAPABILITY,
                "operational_mode": DEMOGRAPHICS_PHASE1_MODE,
                "knowledge_leverage": DEMOGRAPHICS_PHASE1_KNOWLEDGE_LEVERAGE,
                "coverage_level": "wdi_demographics_phase1_operational_expansion",
                "region_id": country_catalog[country_code]["region"]["id"],
                "region_label": country_catalog[country_code]["region"]["value"],
                "income_level_id": country_catalog[country_code]["incomeLevel"]["id"],
                "income_level_label": country_catalog[country_code]["incomeLevel"]["value"],
            }
            if row["indicator_id"] != indicator_code:
                raise ValueError(f"unexpected indicator in response: {row['indicator_id']} != {indicator_code}")
            if row["countryiso3code"] not in countries:
                raise ValueError(f"unexpected country in response: {row['countryiso3code']}")
            if row["date"] not in DEMOGRAPHICS_PHASE1_YEARS:
                raise ValueError(f"unexpected year in response: {row['date']}")
            rows.append(row)

    rows.sort(key=lambda row: (DEMOGRAPHICS_PHASE1_INDICATORS.index(row["indicator_id"]), countries.index(row["countryiso3code"]), int(row["date"])))
    if len(rows) != DEMOGRAPHICS_PHASE1_EXPECTED_OBSERVATION_COUNT:
        raise ValueError(f"expected {DEMOGRAPHICS_PHASE1_EXPECTED_OBSERVATION_COUNT} rows, got {len(rows)}")

    return {
        "source": "World Bank World Development Indicators",
        "support_bundle": DEMOGRAPHICS_PHASE1_RAW_FIXTURE_PATH,
        "created_at_utc": None,
        "countries": countries,
        "indicators": DEMOGRAPHICS_PHASE1_INDICATORS,
        "date_range": DEMOGRAPHICS_PHASE1_DATE_RANGE,
        "expected_row_count": DEMOGRAPHICS_PHASE1_EXPECTED_OBSERVATION_COUNT,
        "row_count": len(rows),
        "rows": rows,
        "raw_artifacts": raw_artifacts,
        "raw_fixture_path": DEMOGRAPHICS_PHASE1_RAW_FIXTURE_PATH,
        "raw_sha256": DEMOGRAPHICS_PHASE1_RAW_SHA256,
        "operational_scope": {
            "task": DEMOGRAPHICS_PHASE1_TASK_ID,
            "mode": DEMOGRAPHICS_PHASE1_MODE,
            "phase": DEMOGRAPHICS_PHASE1_PHASE,
            "capability": DEMOGRAPHICS_PHASE1_CAPABILITY,
            "knowledge_leverage": DEMOGRAPHICS_PHASE1_KNOWLEDGE_LEVERAGE,
            "expansion_level": "all_non_aggregate_countries_demographic_foundation_2000_2023",
            "country_count": len(countries),
            "countries": countries,
            "indicators": DEMOGRAPHICS_PHASE1_INDICATORS,
            "date_range": DEMOGRAPHICS_PHASE1_DATE_RANGE,
            "non_goals": scope.get("non_goals", []),
        },
    }


def build_wdi_demographics_phase1_observed_package(raw: dict[str, Any]) -> ObservedIngestionPackage:
    return build_wdi_observed_package(normalize_wdi_demographics_phase1_fixture(raw))


def write_wdi_demographics_phase1_normalized_artifact(raw: dict[str, Any], path: str | Path = DEMOGRAPHICS_PHASE1_DEFAULT_NORMALIZED_PATH) -> dict[str, Any]:
    normalized = normalize_wdi_demographics_phase1_fixture(raw)
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(normalized, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return normalized


def write_wdi_demographics_phase1_refresh_manifest(raw: dict[str, Any], path: str | Path = DEMOGRAPHICS_PHASE1_DEFAULT_REFRESH_MANIFEST_PATH, *, normalized_path: str | Path = DEMOGRAPHICS_PHASE1_DEFAULT_NORMALIZED_PATH, load_counts: dict[str, int] | None = None) -> dict[str, Any]:
    package = build_wdi_demographics_phase1_observed_package(raw)
    normalized = normalize_wdi_demographics_phase1_fixture(raw)
    payload = {
        "task": DEMOGRAPHICS_PHASE1_TASK_ID,
        "status": "succeeded",
        "mode": DEMOGRAPHICS_PHASE1_MODE,
        "phase": DEMOGRAPHICS_PHASE1_PHASE,
        "capability": DEMOGRAPHICS_PHASE1_CAPABILITY,
        "knowledge_leverage": DEMOGRAPHICS_PHASE1_KNOWLEDGE_LEVERAGE,
        "raw_fixture_path": DEMOGRAPHICS_PHASE1_RAW_FIXTURE_PATH,
        "raw_sha256": DEMOGRAPHICS_PHASE1_RAW_SHA256,
        "normalized_path": str(normalized_path),
        "source_urls": [request["url"] for request in raw["requests"]],
        "country_count": len(normalized["countries"]),
        "indicators": DEMOGRAPHICS_PHASE1_INDICATORS,
        "date_range": DEMOGRAPHICS_PHASE1_DATE_RANGE,
        "row_count": normalized["row_count"],
        "expected_row_count": DEMOGRAPHICS_PHASE1_EXPECTED_OBSERVATION_COUNT,
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


def build_wdi_demographics_phase1_refresh_delta_report(previous: dict[str, Any], current: dict[str, Any]) -> dict[str, Any]:
    report = build_wdi_macro_indicators_refresh_delta_report(previous, current)
    report["task"] = DEMOGRAPHICS_PHASE1_TASK_ID
    report["capability"] = DEMOGRAPHICS_PHASE1_CAPABILITY
    report["portfolio_category"] = DEMOGRAPHICS_PHASE1_MODE
    report["phase"] = DEMOGRAPHICS_PHASE1_PHASE
    report["knowledge_leverage"] = DEMOGRAPHICS_PHASE1_KNOWLEDGE_LEVERAGE
    report["refresh_verification"] = "bounded_demographics_phase1_pre_load_delta_check"
    report.pop("refresh_delta_fingerprint", None)
    report["refresh_delta_fingerprint"] = refresh_delta_report_fingerprint(report)
    return report


def write_wdi_demographics_phase1_refresh_delta_report(previous: dict[str, Any], current: dict[str, Any], path: str | Path = DEMOGRAPHICS_PHASE1_DEFAULT_REFRESH_DELTA_PATH) -> dict[str, Any]:
    report = build_wdi_demographics_phase1_refresh_delta_report(previous, current)
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report
