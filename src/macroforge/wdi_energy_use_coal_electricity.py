from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from macroforge.observed_ingestion import ObservedIngestionPackage, ObservedObservation, canonical_attribute_hash
from macroforge.wdi_observed import (
    build_wdi_macro_indicators_refresh_delta_report,
    build_wdi_observed_package,
    observed_package_fingerprint,
    refresh_delta_report_fingerprint,
    validated_wdi_raw_provenance,
)

SOURCE_CODE = "WDI_ENERGY_USE_COAL_ELECTRICITY"
SOURCE_NAME = "World Bank WDI bounded energy use and coal-electricity evidence slice"
SOURCE_HOME_URL = "https://data.worldbank.org/"
PROVIDER_DATASET_CODE = "WDI:ENERGY_USE_COAL_ELECTRICITY"
FREQUENCY = "A"
SCOPE = "bounded TASK-096 WDI energy use and coal-electricity evidence slice"
EXPECTED_COUNTRIES = ("USA", "CHN")
EXPECTED_PERIODS = ("2020", "2021")
EXPECTED_INDICATORS = ("EG.USE.PCAP.KG.OE", "EG.ELC.COAL.ZS")
EXPECTED_ROW_COUNT = len(EXPECTED_COUNTRIES) * len(EXPECTED_PERIODS) * len(EXPECTED_INDICATORS)

INDICATOR_METADATA = {
    "EG.USE.PCAP.KG.OE": {
        "energy_concept": "energy_use_per_capita",
        "energy_group": "energy_intensity",
        "unit_code": "KG_OIL_EQUIVALENT_PER_CAPITA",
        "unit_label": "kg of oil equivalent per capita",
    },
    "EG.ELC.COAL.ZS": {
        "energy_concept": "coal_electricity_share",
        "energy_group": "electricity_mix",
        "unit_code": "PERCENT_OF_TOTAL",
        "unit_label": "percent of total electricity production",
    },
}


def normalize_wdi_energy_use_coal_electricity_fixture(
    raw_payload: str | bytes,
    *,
    raw_artifact_path: str,
    raw_sha256: str,
    content_type: str,
) -> dict[str, Any]:
    payload = json.loads(_coerce_payload(raw_payload))
    if not isinstance(payload, dict):
        raise ValueError("TASK-096 WDI energy fixture must be a JSON object")
    if payload.get("scope") != SCOPE:
        raise ValueError(f"unexpected TASK-096 scope: {payload.get('scope')}")
    requests = payload.get("requests")
    if not isinstance(requests, list):
        raise ValueError("TASK-096 WDI energy fixture must contain a requests array")

    rows: list[dict[str, Any]] = []
    source_urls: list[str] = []
    request_metadata: dict[str, Any] = {}
    for request in requests:
        if not isinstance(request, dict):
            raise ValueError("TASK-096 WDI energy request entries must be JSON objects")
        indicator_code = str(request.get("indicator_code"))
        _validate_indicator_code(indicator_code)
        source_url = str(request.get("url"))
        source_urls.append(source_url)
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
            "source_url": source_url,
        }
        for record in data_rows:
            if _record_in_scope(record, indicator_code):
                rows.append(
                    _normalize_record(
                        record,
                        indicator_code=indicator_code,
                        request_metadata=request_metadata[indicator_code],
                        raw_artifact_path=raw_artifact_path,
                        raw_sha256=raw_sha256,
                    )
                )

    rows.sort(key=lambda row: (_indicator_order(row["provider_indicator_code"]), row["territory_code"], row["provider_period_code"]))
    periods = sorted({row["provider_period_code"] for row in rows})
    return {
        "source_code": SOURCE_CODE,
        "source_urls": source_urls,
        "content_type": content_type,
        "raw_artifact_path": raw_artifact_path,
        "raw_sha256": raw_sha256,
        "provider_dataset_code": PROVIDER_DATASET_CODE,
        "frequency": FREQUENCY,
        "period_range": f"{periods[0]}-{periods[-1]}" if periods else "unknown",
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


def build_wdi_energy_use_coal_electricity_observed_package(normalized: dict[str, Any]) -> ObservedIngestionPackage:
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


def _normalize_record(
    record: dict[str, Any],
    *,
    indicator_code: str,
    request_metadata: dict[str, Any],
    raw_artifact_path: str,
    raw_sha256: str,
) -> dict[str, Any]:
    indicator = record["indicator"]
    country = record["country"]
    meta = INDICATOR_METADATA[indicator_code]
    value = record.get("value")
    value_text = _value_text(value)
    attributes = {
        "source_provider": "World Bank WDI",
        "observation_family": "energy_intensity_and_electricity_mix",
        "energy_concept": meta["energy_concept"],
        "energy_group": meta["energy_group"],
        "indicator_id": indicator_code,
        "indicator_label": str(indicator["value"]),
        "country_id": str(country["id"]),
        "countryiso3code": str(record["countryiso3code"]),
        "country_name": str(country["value"]),
        "unit_code": meta["unit_code"],
        "unit_label": meta["unit_label"],
        "frequency": FREQUENCY,
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
        "value": value_text,
        "energy_concept": meta["energy_concept"],
        "observation_status": "observed",
        "decimal_precision": _decimal_precision(value_text),
        "attributes": attributes,
        "source_payload": {
            "raw_artifact_path": raw_artifact_path,
            "raw_sha256": raw_sha256,
            "request_metadata": dict(request_metadata),
            "source_record": record,
        },
    }


def _record_in_scope(record: Any, indicator_code: str) -> bool:
    if not isinstance(record, dict):
        return False
    if str(record.get("countryiso3code")) not in EXPECTED_COUNTRIES:
        return False
    if str(record.get("date")) not in EXPECTED_PERIODS:
        return False
    if record.get("value") is None:
        return False
    indicator = record.get("indicator")
    return isinstance(indicator, dict) and str(indicator.get("id")) == indicator_code


def _validate_indicator_code(indicator_code: str) -> None:
    if indicator_code not in INDICATOR_METADATA:
        raise ValueError(f"unsupported TASK-096 WDI energy indicator: {indicator_code}")


def _indicator_order(indicator_code: str) -> int:
    return {code: index for index, code in enumerate(EXPECTED_INDICATORS)}[indicator_code]


def _value_text(value: Any) -> str:
    return str(value)


def _decimal_precision(value: str) -> int | None:
    if "." not in value:
        return None
    return len(value.split(".", 1)[1])


def _release_key(normalized: dict[str, Any]) -> str:
    return f"{SOURCE_CODE}:{normalized['period_range']}:{normalized['raw_sha256'][:12]}"

# TASK-134 Knowledge Leverage / Operational Capability Expansion: WDI Energy Phase 1
ENERGY_PHASE1_TASK_ID = "TASK-134"
ENERGY_PHASE1_MODE = "Operational Capability Expansion"
ENERGY_PHASE1_PHASE = "WDI Energy Phase 1"
ENERGY_PHASE1_CAPABILITY = "WDI energy operational foundation"
ENERGY_PHASE1_KNOWLEDGE_LEVERAGE = "energy_security_foundation"
ENERGY_PHASE1_RAW_FIXTURE_PATH = "data/raw/wdi_energy_phase1/wdi-energy-phase1-all-countries-2i-2000-2023.json"
ENERGY_PHASE1_RAW_SHA256 = "8a040af7908f687b3e92cdb5ea16f9a39d4e140a234a175f50476ae10b9a968b"
ENERGY_PHASE1_DEFAULT_NORMALIZED_PATH = "data/metadata/wdi_energy_phase1/wdi-energy-phase1-normalized.json"
ENERGY_PHASE1_DEFAULT_REFRESH_MANIFEST_PATH = "data/operational/wdi_energy_phase1/wdi-energy-phase1-refresh-manifest.json"
ENERGY_PHASE1_DEFAULT_REFRESH_DELTA_PATH = "data/operational/wdi_energy_phase1/wdi-energy-phase1-refresh-delta-report.json"
ENERGY_PHASE1_INDICATORS = list(EXPECTED_INDICATORS)
ENERGY_PHASE1_DATE_RANGE = "2000:2023"
ENERGY_PHASE1_YEARS = [str(year) for year in range(2000, 2024)]
ENERGY_PHASE1_COUNTRY_COUNT = 217
ENERGY_PHASE1_EXPECTED_OBSERVATION_COUNT = ENERGY_PHASE1_COUNTRY_COUNT * len(ENERGY_PHASE1_INDICATORS) * len(ENERGY_PHASE1_YEARS)
ENERGY_PHASE1_DEFAULT_RUN_KEY = "task-134-wdi-energy-phase1-knowledge-leverage"


def _energy_phase1_countries(raw: dict[str, Any]) -> list[str]:
    countries = raw.get("scope", {}).get("countries", [])
    if len(countries) != ENERGY_PHASE1_COUNTRY_COUNT:
        raise ValueError(f"expected {ENERGY_PHASE1_COUNTRY_COUNT} countries, got {len(countries)}")
    if len(set(countries)) != len(countries):
        raise ValueError("WDI energy Phase 1 country scope contains duplicate country ids")
    return countries


def _energy_phase1_country_catalog(raw: dict[str, Any]) -> dict[str, dict[str, Any]]:
    catalog_rows = raw.get("country_catalog", {}).get("countries", [])
    catalog = {row.get("id"): row for row in catalog_rows}
    countries = _energy_phase1_countries(raw)
    if set(catalog) != set(countries):
        raise ValueError("WDI energy Phase 1 country catalog does not match scoped countries")
    if any(row.get("region", {}).get("id") == "NA" for row in catalog.values()):
        raise ValueError("WDI energy Phase 1 includes aggregate rows")
    return catalog


def normalize_wdi_energy_phase1_fixture(
    raw: dict[str, Any], *, raw_artifact_path: str | Path, raw_payload: str | bytes
) -> dict[str, Any]:
    """Normalize TASK-134 WDI Energy Phase 1 into existing WDI loader-compatible shape."""

    actual_path, actual_sha256, actual_bytes = validated_wdi_raw_provenance(
        raw, raw_artifact_path=raw_artifact_path, raw_payload=raw_payload
    )
    scope = raw.get("scope", {})
    if scope.get("task") != ENERGY_PHASE1_TASK_ID:
        raise ValueError(f"unexpected task scope: {scope.get('task')}")
    if scope.get("mode") != ENERGY_PHASE1_MODE:
        raise ValueError(f"unexpected mode: {scope.get('mode')}")
    if scope.get("phase") != ENERGY_PHASE1_PHASE:
        raise ValueError(f"unexpected phase: {scope.get('phase')}")
    if scope.get("indicators") != ENERGY_PHASE1_INDICATORS:
        raise ValueError(f"unexpected indicator scope: {scope.get('indicators')}")
    if scope.get("date_range") != ENERGY_PHASE1_DATE_RANGE:
        raise ValueError(f"unexpected date range: {scope.get('date_range')}")
    if scope.get("expected_observation_count") != ENERGY_PHASE1_EXPECTED_OBSERVATION_COUNT:
        raise ValueError("WDI energy Phase 1 expected observation count changed")

    countries = _energy_phase1_countries(raw)
    country_catalog = _energy_phase1_country_catalog(raw)
    requests = raw.get("requests", [])
    if [request.get("indicator_code") for request in requests] != ENERGY_PHASE1_INDICATORS:
        raise ValueError("WDI energy Phase 1 request order must match validated indicator scope")

    rows: list[dict[str, Any]] = []
    raw_artifacts: list[dict[str, Any]] = []
    expected_rows_per_indicator = len(countries) * len(ENERGY_PHASE1_YEARS)
    for request in requests:
        indicator_code = request["indicator_code"]
        response = request.get("response")
        if not isinstance(response, list) or len(response) != 2:
            raise ValueError(f"unexpected WDI response shape for {indicator_code}")
        metadata, observations = response
        if metadata.get("lastupdated") is None:
            raise ValueError(f"missing WDI lastupdated metadata for {indicator_code}")
        if len(observations) != expected_rows_per_indicator:
            raise ValueError(f"unexpected WDI energy observation count for {indicator_code}: {len(observations)}")
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
                "energy_concept": meta["energy_concept"],
                "energy_group": meta["energy_group"],
                "operational_capability": ENERGY_PHASE1_CAPABILITY,
                "operational_mode": ENERGY_PHASE1_MODE,
                "knowledge_leverage": ENERGY_PHASE1_KNOWLEDGE_LEVERAGE,
                "coverage_level": "wdi_energy_phase1_operational_expansion",
                "region_id": country_catalog[country_code]["region"]["id"],
                "region_label": country_catalog[country_code]["region"]["value"],
                "income_level_id": country_catalog[country_code]["incomeLevel"]["id"],
                "income_level_label": country_catalog[country_code]["incomeLevel"]["value"],
            }
            if row["indicator_id"] != indicator_code:
                raise ValueError(f"unexpected indicator in response: {row['indicator_id']} != {indicator_code}")
            if row["countryiso3code"] not in countries:
                raise ValueError(f"unexpected country in response: {row['countryiso3code']}")
            if row["date"] not in ENERGY_PHASE1_YEARS:
                raise ValueError(f"unexpected year in response: {row['date']}")
            rows.append(row)

    rows.sort(key=lambda row: (ENERGY_PHASE1_INDICATORS.index(row["indicator_id"]), countries.index(row["countryiso3code"]), int(row["date"])))
    if len(rows) != ENERGY_PHASE1_EXPECTED_OBSERVATION_COUNT:
        raise ValueError(f"expected {ENERGY_PHASE1_EXPECTED_OBSERVATION_COUNT} rows, got {len(rows)}")

    return {
        "source": "World Bank World Development Indicators",
        "support_bundle": actual_path,
        "created_at_utc": None,
        "countries": countries,
        "indicators": ENERGY_PHASE1_INDICATORS,
        "date_range": ENERGY_PHASE1_DATE_RANGE,
        "expected_row_count": ENERGY_PHASE1_EXPECTED_OBSERVATION_COUNT,
        "row_count": len(rows),
        "rows": rows,
        "raw_artifacts": raw_artifacts,
        "raw_fixture_path": actual_path,
        "raw_sha256": actual_sha256,
        "operational_scope": {
            "task": ENERGY_PHASE1_TASK_ID,
            "mode": ENERGY_PHASE1_MODE,
            "phase": ENERGY_PHASE1_PHASE,
            "capability": ENERGY_PHASE1_CAPABILITY,
            "knowledge_leverage": ENERGY_PHASE1_KNOWLEDGE_LEVERAGE,
            "expansion_level": "all_non_aggregate_countries_energy_foundation_2000_2023",
            "country_count": len(countries),
            "countries": countries,
            "indicators": ENERGY_PHASE1_INDICATORS,
            "date_range": ENERGY_PHASE1_DATE_RANGE,
            "non_goals": scope.get("non_goals", []),
        },
    }


def build_wdi_energy_phase1_observed_package(raw: dict[str, Any], *, raw_artifact_path: str | Path, raw_payload: str | bytes) -> ObservedIngestionPackage:
    return build_wdi_observed_package(normalize_wdi_energy_phase1_fixture(raw, raw_artifact_path=raw_artifact_path, raw_payload=raw_payload))


def write_wdi_energy_phase1_normalized_artifact(raw: dict[str, Any], path: str | Path = ENERGY_PHASE1_DEFAULT_NORMALIZED_PATH, *, raw_artifact_path: str | Path, raw_payload: str | bytes) -> dict[str, Any]:
    normalized = normalize_wdi_energy_phase1_fixture(raw, raw_artifact_path=raw_artifact_path, raw_payload=raw_payload)
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(normalized, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return normalized


def write_wdi_energy_phase1_refresh_manifest(raw: dict[str, Any], path: str | Path = ENERGY_PHASE1_DEFAULT_REFRESH_MANIFEST_PATH, *, raw_artifact_path: str | Path, raw_payload: str | bytes, normalized_path: str | Path = ENERGY_PHASE1_DEFAULT_NORMALIZED_PATH, load_counts: dict[str, int] | None = None) -> dict[str, Any]:
    package = build_wdi_energy_phase1_observed_package(raw, raw_artifact_path=raw_artifact_path, raw_payload=raw_payload)
    normalized = normalize_wdi_energy_phase1_fixture(raw, raw_artifact_path=raw_artifact_path, raw_payload=raw_payload)
    payload = {
        "task": ENERGY_PHASE1_TASK_ID,
        "status": "succeeded",
        "mode": ENERGY_PHASE1_MODE,
        "phase": ENERGY_PHASE1_PHASE,
        "capability": ENERGY_PHASE1_CAPABILITY,
        "knowledge_leverage": ENERGY_PHASE1_KNOWLEDGE_LEVERAGE,
        "raw_fixture_path": normalized["raw_fixture_path"],
        "raw_sha256": normalized["raw_sha256"],
        "normalized_path": str(normalized_path),
        "source_urls": [request["url"] for request in raw["requests"]],
        "country_count": len(normalized["countries"]),
        "indicators": ENERGY_PHASE1_INDICATORS,
        "date_range": ENERGY_PHASE1_DATE_RANGE,
        "row_count": normalized["row_count"],
        "expected_row_count": ENERGY_PHASE1_EXPECTED_OBSERVATION_COUNT,
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


def build_wdi_energy_phase1_refresh_delta_report(previous: dict[str, Any], current: dict[str, Any]) -> dict[str, Any]:
    report = build_wdi_macro_indicators_refresh_delta_report(previous, current)
    report["task"] = ENERGY_PHASE1_TASK_ID
    report["capability"] = ENERGY_PHASE1_CAPABILITY
    report["portfolio_category"] = ENERGY_PHASE1_MODE
    report["phase"] = ENERGY_PHASE1_PHASE
    report["knowledge_leverage"] = ENERGY_PHASE1_KNOWLEDGE_LEVERAGE
    report["refresh_verification"] = "bounded_energy_phase1_pre_load_delta_check"
    report.pop("refresh_delta_fingerprint", None)
    report["refresh_delta_fingerprint"] = refresh_delta_report_fingerprint(report)
    return report


def write_wdi_energy_phase1_refresh_delta_report(previous: dict[str, Any], current: dict[str, Any], path: str | Path = ENERGY_PHASE1_DEFAULT_REFRESH_DELTA_PATH) -> dict[str, Any]:
    report = build_wdi_energy_phase1_refresh_delta_report(previous, current)
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report
