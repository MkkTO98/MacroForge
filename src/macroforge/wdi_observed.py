from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from macroforge.observed_ingestion import (
    EMPTY_ATTRIBUTE_HASH,
    UNKNOWN_UNIT_CODE,
    ObservedIngestionPackage,
    ObservedObservation,
    observed_package_fingerprint,
)


def validated_wdi_raw_provenance(
    raw: dict[str, Any],
    *,
    raw_artifact_path: str | Path,
    raw_payload: str | bytes,
) -> tuple[str, str, int]:
    """Validate provenance and return the artifact path, SHA-256, and byte count."""

    artifact_path = str(raw_artifact_path).strip()
    if not artifact_path:
        raise ValueError("raw_artifact_path is required")
    payload_bytes = raw_payload.encode("utf-8") if isinstance(raw_payload, str) else raw_payload
    if not isinstance(payload_bytes, bytes) or not payload_bytes:
        raise ValueError("non-empty raw_payload bytes are required")
    try:
        represented = json.loads(payload_bytes)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("raw_payload must be valid JSON bytes") from exc
    if represented != raw:
        raise ValueError("raw_payload bytes do not represent the supplied parsed WDI input")
    return artifact_path, hashlib.sha256(payload_bytes).hexdigest(), len(payload_bytes)


def _wdi_release_key(normalized: dict[str, Any]) -> str:
    last_updated = None
    if normalized.get("raw_artifacts"):
        last_updated = normalized["raw_artifacts"][0].get("source_metadata", {}).get("lastupdated")
    return f"WDI:{last_updated or 'unknown'}:{normalized.get('date_range', 'unknown')}"


def build_wdi_observed_package(normalized: dict[str, Any]) -> ObservedIngestionPackage:
    release_key = _wdi_release_key(normalized)
    raw_artifacts = normalized.get("raw_artifacts", [])
    observations = []
    for row in normalized["rows"]:
        unit_code = row.get("unit") or UNKNOWN_UNIT_CODE
        observation_status = "missing" if row.get("value") is None else "observed"
        observations.append(
            ObservedObservation(
                provider_indicator_code=row["indicator_id"],
                provider_indicator_label=row.get("indicator_name"),
                provider_territory_code=row["countryiso3code"],
                provider_territory_label=row.get("country_name"),
                provider_period_code=str(row["date"]),
                frequency="A",
                period_year=int(row["date"]),
                unit_code=unit_code,
                unit_label=None,
                value=row.get("value"),
                observation_status=observation_status,
                decimal_precision=row.get("decimal"),
                attributes={},
                source_payload=dict(row),
                attribute_hash=EMPTY_ATTRIBUTE_HASH,
            )
        )
    row_count = int(normalized.get("row_count", len(observations)))
    return ObservedIngestionPackage(
        source_code="WDI",
        source_name="World Bank World Development Indicators",
        source_home_url="https://data.worldbank.org/",
        provider_dataset_code="WDI",
        release_key=release_key,
        raw_evidence={
            "source_url": "; ".join(a["url"] for a in raw_artifacts),
            "raw_artifact_path": normalized.get("raw_fixture_path", normalized.get("support_bundle")),
            "raw_sha256": normalized.get("raw_sha256") or ";".join(a["sha256"] for a in raw_artifacts),
            "raw_artifacts": raw_artifacts,
        },
        input_filters={
            "countries": normalized.get("countries"),
            "indicators": normalized.get("indicators"),
            "date_range": normalized.get("date_range"),
        },
        row_count=row_count,
        expected_row_count=int(normalized.get("expected_row_count", row_count)),
        observations=tuple(observations),
    )

# TASK-129 Operational Capability Maturation: bounded WDI macro indicators
SOURCE_CODE = "WDI"
SOURCE_NAME = "World Bank World Development Indicators"
TASK_ID = "TASK-129"
CAPABILITY = "WDI macro indicators"
RAW_FIXTURE_PATH = "data/raw/wdi_macro_indicators/wdi-macro-indicators-6c-3i-2019-2023.json"
RAW_SHA256 = "c3695cae253eafa0436942c48e50dcb262d80a0b5f5f8933cdd4acff6f3cba5f"
DEFAULT_NORMALIZED_PATH = "data/metadata/wdi_macro_indicators/wdi-macro-indicators-normalized.json"
DEFAULT_REFRESH_MANIFEST_PATH = "data/operational/wdi_macro_indicators/wdi-macro-indicators-refresh-manifest.json"
COUNTRIES = ["USA", "DNK", "DEU", "JPN", "CHN", "IND"]
INDICATORS = ["NY.GDP.MKTP.CD", "SP.POP.TOTL", "FP.CPI.TOTL.ZG"]
DATE_RANGE = "2019:2023"
YEARS = ["2019", "2020", "2021", "2022", "2023"]
EXPECTED_OBSERVATION_COUNT = len(COUNTRIES) * len(INDICATORS) * len(YEARS)
DEFAULT_RUN_KEY = "task-129-wdi-macro-indicators-operational-v1"


def normalize_wdi_macro_indicators_fixture(
    raw: dict[str, Any],
    *,
    raw_artifact_path: str | Path,
    raw_payload: str | bytes,
) -> dict[str, Any]:
    """Normalize the bounded TASK-129 operational WDI fixture."""

    actual_path, actual_sha256, actual_bytes = validated_wdi_raw_provenance(
        raw, raw_artifact_path=raw_artifact_path, raw_payload=raw_payload
    )
    scope = raw.get("scope", {})
    if scope.get("task") != TASK_ID:
        raise ValueError(f"unexpected task scope: {scope.get('task')}")
    if scope.get("mode") != "Operational Capability Maturation":
        raise ValueError(f"unexpected operational mode: {scope.get('mode')}")
    if scope.get("countries") != COUNTRIES:
        raise ValueError(f"unexpected country scope: {scope.get('countries')}")
    if scope.get("indicators") != INDICATORS:
        raise ValueError(f"unexpected indicator scope: {scope.get('indicators')}")
    if scope.get("date_range") != DATE_RANGE:
        raise ValueError(f"unexpected date range: {scope.get('date_range')}")

    rows: list[dict[str, Any]] = []
    raw_artifacts: list[dict[str, Any]] = []
    requests = raw.get("requests", [])
    if [request.get("indicator_code") for request in requests] != INDICATORS:
        raise ValueError("WDI macro fixture request order must match bounded indicator scope")

    for request in requests:
        indicator_code = request["indicator_code"]
        response = request.get("response")
        if not isinstance(response, list) or len(response) != 2:
            raise ValueError(f"unexpected WDI response shape for {indicator_code}")
        metadata, observations = response
        if metadata.get("lastupdated") is None:
            raise ValueError(f"missing WDI lastupdated metadata for {indicator_code}")
        if len(observations) != len(COUNTRIES) * len(YEARS):
            raise ValueError(f"unexpected WDI observation count for {indicator_code}: {len(observations)}")
        raw_response_bytes = json.dumps(response, sort_keys=True).encode("utf-8")
        raw_artifacts.append(
            {
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
            }
        )
        for item in observations:
            indicator = item.get("indicator") or {}
            country = item.get("country") or {}
            row = {
                "source": SOURCE_NAME,
                "indicator_id": indicator.get("id"),
                "indicator_name": indicator.get("value"),
                "country_id": country.get("id"),
                "country_name": country.get("value"),
                "countryiso3code": item.get("countryiso3code"),
                "date": item.get("date"),
                "value": item.get("value"),
                "unit": item.get("unit") or None,
                "obs_status": item.get("obs_status") or None,
                "decimal": item.get("decimal"),
                "operational_capability": CAPABILITY,
                "operational_track": "Track B",
                "coverage_level": "bounded_operational_v1",
            }
            if row["indicator_id"] != indicator_code:
                raise ValueError(f"unexpected indicator in response: {row['indicator_id']} != {indicator_code}")
            if row["countryiso3code"] not in COUNTRIES:
                raise ValueError(f"unexpected country in response: {row['countryiso3code']}")
            if row["date"] not in YEARS:
                raise ValueError(f"unexpected year in response: {row['date']}")
            rows.append(row)

    rows.sort(key=lambda row: (INDICATORS.index(row["indicator_id"]), COUNTRIES.index(row["countryiso3code"]), int(row["date"])))
    if len(rows) != EXPECTED_OBSERVATION_COUNT:
        raise ValueError(f"expected {EXPECTED_OBSERVATION_COUNT} WDI macro rows, got {len(rows)}")

    return {
        "source": SOURCE_NAME,
        "support_bundle": actual_path,
        "created_at_utc": None,
        "countries": COUNTRIES,
        "indicators": INDICATORS,
        "date_range": DATE_RANGE,
        "expected_row_count": EXPECTED_OBSERVATION_COUNT,
        "row_count": len(rows),
        "rows": rows,
        "raw_artifacts": raw_artifacts,
        "raw_fixture_path": actual_path,
        "raw_sha256": actual_sha256,
        "operational_scope": {
            "task": TASK_ID,
            "maturation_track": "Track B",
            "capability": CAPABILITY,
            "coverage_level": "bounded_operational_v1",
            "countries": COUNTRIES,
            "indicators": INDICATORS,
            "date_range": DATE_RANGE,
            "refresh_procedure": "bounded_manual_refresh_with_deterministic_manifest",
            "non_goals": [
                "all_country_bulk_ingestion",
                "all_indicator_bulk_ingestion",
                "scheduled_production_refresh",
                "KnowledgeForge_query_api",
                "Controlled_Expansion_project_wide",
            ],
        },
    }


def build_wdi_macro_indicators_observed_package(
    raw: dict[str, Any], *, raw_artifact_path: str | Path, raw_payload: str | bytes
) -> ObservedIngestionPackage:
    return build_wdi_observed_package(
        normalize_wdi_macro_indicators_fixture(
            raw, raw_artifact_path=raw_artifact_path, raw_payload=raw_payload
        )
    )


def write_wdi_macro_indicators_normalized_artifact(
    raw: dict[str, Any],
    path: str | Path = DEFAULT_NORMALIZED_PATH,
    *,
    raw_artifact_path: str | Path,
    raw_payload: str | bytes,
) -> dict[str, Any]:
    normalized = normalize_wdi_macro_indicators_fixture(
        raw, raw_artifact_path=raw_artifact_path, raw_payload=raw_payload
    )
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(normalized, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return normalized


def write_wdi_macro_indicators_refresh_manifest(
    raw: dict[str, Any],
    path: str | Path = DEFAULT_REFRESH_MANIFEST_PATH,
    *,
    raw_artifact_path: str | Path,
    raw_payload: str | bytes,
    normalized_path: str | Path = DEFAULT_NORMALIZED_PATH,
    load_counts: dict[str, int] | None = None,
) -> dict[str, Any]:
    package = build_wdi_macro_indicators_observed_package(
        raw, raw_artifact_path=raw_artifact_path, raw_payload=raw_payload
    )
    normalized = normalize_wdi_macro_indicators_fixture(
        raw, raw_artifact_path=raw_artifact_path, raw_payload=raw_payload
    )
    payload = {
        "task": TASK_ID,
        "status": "succeeded",
        "capability": CAPABILITY,
        "maturation_track": "Track B",
        "refresh_procedure": "bounded_manual_refresh_with_deterministic_manifest",
        "raw_fixture_path": normalized["raw_fixture_path"],
        "raw_sha256": normalized["raw_sha256"],
        "normalized_path": str(normalized_path),
        "source_urls": [request["url"] for request in raw["requests"]],
        "countries": COUNTRIES,
        "indicators": INDICATORS,
        "date_range": DATE_RANGE,
        "row_count": normalized["row_count"],
        "expected_row_count": EXPECTED_OBSERVATION_COUNT,
        "package_fingerprint": observed_package_fingerprint(package),
        "load_counts": load_counts,
        "non_goals": normalized["operational_scope"]["non_goals"],
    }
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return payload


def _wdi_macro_refresh_key(row: dict[str, Any]) -> tuple[str, str, str]:
    return (str(row["indicator_id"]), str(row["countryiso3code"]), str(row["date"]))


def _wdi_macro_key_payload(key: tuple[str, str, str]) -> dict[str, str]:
    indicator_id, countryiso3code, date = key
    return {
        "indicator_id": indicator_id,
        "countryiso3code": countryiso3code,
        "date": date,
    }


def _wdi_macro_row_hash(row: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(row, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def _wdi_macro_normalized_fingerprint(normalized: dict[str, Any]) -> str:
    payload = {
        "countries": normalized.get("countries"),
        "date_range": normalized.get("date_range"),
        "indicators": normalized.get("indicators"),
        "row_count": normalized.get("row_count"),
        "rows": sorted(normalized.get("rows", []), key=_wdi_macro_refresh_key),
    }
    return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def refresh_delta_report_fingerprint(report: dict[str, Any]) -> str:
    """Return a stable fingerprint for a WDI macro refresh-delta report."""

    return hashlib.sha256(json.dumps(report, sort_keys=True, separators=(",", ":")).encode("utf-8")).hexdigest()


def build_wdi_macro_indicators_refresh_delta_report(previous: dict[str, Any], current: dict[str, Any]) -> dict[str, Any]:
    """Build a deterministic bounded pre-load refresh-delta report for TASK-130."""

    previous_rows = {_wdi_macro_refresh_key(row): row for row in previous.get("rows", [])}
    current_rows = {_wdi_macro_refresh_key(row): row for row in current.get("rows", [])}
    if len(previous_rows) != len(previous.get("rows", [])):
        raise ValueError("previous WDI macro normalized payload contains duplicate observation keys")
    if len(current_rows) != len(current.get("rows", [])):
        raise ValueError("current WDI macro normalized payload contains duplicate observation keys")

    previous_keys = set(previous_rows)
    current_keys = set(current_rows)
    added = sorted(current_keys - previous_keys)
    removed = sorted(previous_keys - current_keys)
    common = sorted(previous_keys & current_keys)
    updated = [key for key in common if _wdi_macro_row_hash(previous_rows[key]) != _wdi_macro_row_hash(current_rows[key])]
    updated_set = set(updated)
    unchanged = [key for key in common if key not in updated_set]

    report = {
        "task": "TASK-130",
        "status": "verified",
        "capability": CAPABILITY,
        "portfolio_category": "Operational Capability Maturation",
        "refresh_verification": "bounded_pre_load_delta_check",
        "previous_row_count": int(previous.get("row_count", len(previous_rows))),
        "current_row_count": int(current.get("row_count", len(current_rows))),
        "previous_fingerprint": _wdi_macro_normalized_fingerprint(previous),
        "current_fingerprint": _wdi_macro_normalized_fingerprint(current),
        "unchanged_count": len(unchanged),
        "updated_count": len(updated),
        "added_count": len(added),
        "removed_count": len(removed),
        "changed_count": len(updated) + len(added) + len(removed),
        "updated_keys": [_wdi_macro_key_payload(key) for key in updated],
        "added_keys": [_wdi_macro_key_payload(key) for key in added],
        "removed_keys": [_wdi_macro_key_payload(key) for key in removed],
        "non_goals": [
            "all_country_bulk_ingestion",
            "all_indicator_bulk_ingestion",
            "scheduled_production_refresh",
            "KnowledgeForge_query_api",
            "Controlled_Expansion_project_wide",
        ],
    }
    report["refresh_delta_fingerprint"] = refresh_delta_report_fingerprint(report)
    return report


def write_wdi_macro_indicators_refresh_delta_report(
    previous: dict[str, Any],
    current: dict[str, Any],
    path: str | Path = "data/operational/wdi_macro_indicators/wdi-macro-indicators-refresh-delta-report.json",
) -> dict[str, Any]:
    report = build_wdi_macro_indicators_refresh_delta_report(previous, current)
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


# TASK-132 Operational Capability Expansion: WDI Phase 1
PHASE1_TASK_ID = "TASK-132"
PHASE1_CAPABILITY = "WDI Phase 1 operational macro indicators"
PHASE1_MODE = "Operational Capability Expansion"
PHASE1_RAW_FIXTURE_PATH = "data/raw/wdi_operational_phase1/wdi-phase1-all-countries-3i-2000-2023.json"
PHASE1_RAW_SHA256 = "068aa33496e762e94447f60f62a046d4cdb11f98eca92e916005292b1194bed0"
PHASE1_DEFAULT_NORMALIZED_PATH = "data/metadata/wdi_operational_phase1/wdi-phase1-normalized.json"
PHASE1_DEFAULT_REFRESH_MANIFEST_PATH = "data/operational/wdi_operational_phase1/wdi-phase1-refresh-manifest.json"
PHASE1_DEFAULT_REFRESH_DELTA_PATH = "data/operational/wdi_operational_phase1/wdi-phase1-refresh-delta-report.json"
PHASE1_INDICATORS = ["NY.GDP.MKTP.CD", "SP.POP.TOTL", "FP.CPI.TOTL.ZG"]
PHASE1_DATE_RANGE = "2000:2023"
PHASE1_YEARS = [str(year) for year in range(2000, 2024)]
PHASE1_COUNTRY_COUNT = 217
PHASE1_EXPECTED_OBSERVATION_COUNT = PHASE1_COUNTRY_COUNT * len(PHASE1_INDICATORS) * len(PHASE1_YEARS)
PHASE1_DEFAULT_RUN_KEY = "task-132-wdi-phase1-operational-expansion"


def _phase1_countries(raw: dict[str, Any]) -> list[str]:
    countries = raw.get("scope", {}).get("countries", [])
    if len(countries) != PHASE1_COUNTRY_COUNT:
        raise ValueError(f"expected {PHASE1_COUNTRY_COUNT} WDI Phase 1 countries, got {len(countries)}")
    if len(set(countries)) != len(countries):
        raise ValueError("WDI Phase 1 country scope contains duplicate country ids")
    return countries


def _phase1_country_catalog(raw: dict[str, Any]) -> dict[str, dict[str, Any]]:
    catalog_rows = raw.get("country_catalog", {}).get("countries", [])
    catalog = {row.get("id"): row for row in catalog_rows}
    countries = _phase1_countries(raw)
    if set(catalog) != set(countries):
        raise ValueError("WDI Phase 1 country catalog does not match scoped countries")
    if any(row.get("region", {}).get("id") == "NA" for row in catalog.values()):
        raise ValueError("WDI Phase 1 country catalog includes aggregate rows")
    return catalog


def normalize_wdi_operational_phase1_fixture(
    raw: dict[str, Any],
    *,
    raw_artifact_path: str | Path,
    raw_payload: str | bytes,
) -> dict[str, Any]:
    """Normalize the bounded TASK-132 WDI Phase 1 fixture into existing WDI loader shape."""

    actual_path, actual_sha256, actual_bytes = validated_wdi_raw_provenance(
        raw, raw_artifact_path=raw_artifact_path, raw_payload=raw_payload
    )
    scope = raw.get("scope", {})
    if scope.get("task") != PHASE1_TASK_ID:
        raise ValueError(f"unexpected task scope: {scope.get('task')}")
    if scope.get("mode") != PHASE1_MODE:
        raise ValueError(f"unexpected operational mode: {scope.get('mode')}")
    if scope.get("phase") != "WDI Phase 1":
        raise ValueError(f"unexpected phase: {scope.get('phase')}")
    if scope.get("indicators") != PHASE1_INDICATORS:
        raise ValueError(f"unexpected indicator scope: {scope.get('indicators')}")
    if scope.get("date_range") != PHASE1_DATE_RANGE:
        raise ValueError(f"unexpected date range: {scope.get('date_range')}")
    if scope.get("expected_observation_count") != PHASE1_EXPECTED_OBSERVATION_COUNT:
        raise ValueError("WDI Phase 1 expected observation count changed")

    countries = _phase1_countries(raw)
    country_catalog = _phase1_country_catalog(raw)
    requests = raw.get("requests", [])
    if [request.get("indicator_code") for request in requests] != PHASE1_INDICATORS:
        raise ValueError("WDI Phase 1 request order must match validated macro indicator scope")

    rows: list[dict[str, Any]] = []
    raw_artifacts: list[dict[str, Any]] = []
    expected_rows_per_indicator = len(countries) * len(PHASE1_YEARS)
    for request in requests:
        indicator_code = request["indicator_code"]
        response = request.get("response")
        if not isinstance(response, list) or len(response) != 2:
            raise ValueError(f"unexpected WDI response shape for {indicator_code}")
        metadata, observations = response
        if metadata.get("lastupdated") is None:
            raise ValueError(f"missing WDI lastupdated metadata for {indicator_code}")
        if len(observations) != expected_rows_per_indicator:
            raise ValueError(f"unexpected WDI Phase 1 observation count for {indicator_code}: {len(observations)}")
        raw_response_bytes = json.dumps(response, sort_keys=True).encode("utf-8")
        raw_artifacts.append(
            {
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
            }
        )
        for item in observations:
            indicator = item.get("indicator") or {}
            country = item.get("country") or {}
            country_code = item.get("countryiso3code")
            row = {
                "source": SOURCE_NAME,
                "indicator_id": indicator.get("id"),
                "indicator_name": indicator.get("value"),
                "country_id": country.get("id"),
                "country_name": country.get("value"),
                "countryiso3code": country_code,
                "date": item.get("date"),
                "value": item.get("value"),
                "unit": item.get("unit") or None,
                "obs_status": item.get("obs_status") or None,
                "decimal": item.get("decimal"),
                "operational_capability": PHASE1_CAPABILITY,
                "operational_mode": PHASE1_MODE,
                "coverage_level": "wdi_phase1_operational_expansion",
                "region_id": country_catalog[country_code]["region"]["id"],
                "region_label": country_catalog[country_code]["region"]["value"],
                "income_level_id": country_catalog[country_code]["incomeLevel"]["id"],
                "income_level_label": country_catalog[country_code]["incomeLevel"]["value"],
            }
            if row["indicator_id"] != indicator_code:
                raise ValueError(f"unexpected indicator in response: {row['indicator_id']} != {indicator_code}")
            if row["countryiso3code"] not in countries:
                raise ValueError(f"unexpected country in response: {row['countryiso3code']}")
            if row["date"] not in PHASE1_YEARS:
                raise ValueError(f"unexpected year in response: {row['date']}")
            rows.append(row)

    rows.sort(key=lambda row: (PHASE1_INDICATORS.index(row["indicator_id"]), countries.index(row["countryiso3code"]), int(row["date"])))
    if len(rows) != PHASE1_EXPECTED_OBSERVATION_COUNT:
        raise ValueError(f"expected {PHASE1_EXPECTED_OBSERVATION_COUNT} WDI Phase 1 rows, got {len(rows)}")

    return {
        "source": SOURCE_NAME,
        "support_bundle": actual_path,
        "created_at_utc": None,
        "countries": countries,
        "indicators": PHASE1_INDICATORS,
        "date_range": PHASE1_DATE_RANGE,
        "expected_row_count": PHASE1_EXPECTED_OBSERVATION_COUNT,
        "row_count": len(rows),
        "rows": rows,
        "raw_artifacts": raw_artifacts,
        "raw_fixture_path": actual_path,
        "raw_sha256": actual_sha256,
        "operational_scope": {
            "task": PHASE1_TASK_ID,
            "mode": PHASE1_MODE,
            "phase": "WDI Phase 1",
            "capability": PHASE1_CAPABILITY,
            "expansion_level": "all_non_aggregate_countries_validated_macro_set_2000_2023",
            "country_count": len(countries),
            "countries": countries,
            "indicators": PHASE1_INDICATORS,
            "date_range": PHASE1_DATE_RANGE,
            "refresh_procedure": "bounded_phase1_manual_refresh_with_deterministic_manifest_and_delta_report",
            "non_goals": scope.get("non_goals", []),
        },
    }


def build_wdi_operational_phase1_observed_package(
    raw: dict[str, Any], *, raw_artifact_path: str | Path, raw_payload: str | bytes
) -> ObservedIngestionPackage:
    return build_wdi_observed_package(
        normalize_wdi_operational_phase1_fixture(
            raw, raw_artifact_path=raw_artifact_path, raw_payload=raw_payload
        )
    )


def write_wdi_operational_phase1_normalized_artifact(
    raw: dict[str, Any],
    path: str | Path = PHASE1_DEFAULT_NORMALIZED_PATH,
    *,
    raw_artifact_path: str | Path,
    raw_payload: str | bytes,
) -> dict[str, Any]:
    normalized = normalize_wdi_operational_phase1_fixture(
        raw, raw_artifact_path=raw_artifact_path, raw_payload=raw_payload
    )
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(normalized, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return normalized


def write_wdi_operational_phase1_refresh_manifest(
    raw: dict[str, Any],
    path: str | Path = PHASE1_DEFAULT_REFRESH_MANIFEST_PATH,
    *,
    raw_artifact_path: str | Path,
    raw_payload: str | bytes,
    normalized_path: str | Path = PHASE1_DEFAULT_NORMALIZED_PATH,
    load_counts: dict[str, int] | None = None,
) -> dict[str, Any]:
    package = build_wdi_operational_phase1_observed_package(
        raw, raw_artifact_path=raw_artifact_path, raw_payload=raw_payload
    )
    normalized = normalize_wdi_operational_phase1_fixture(
        raw, raw_artifact_path=raw_artifact_path, raw_payload=raw_payload
    )
    payload = {
        "task": PHASE1_TASK_ID,
        "status": "succeeded",
        "mode": PHASE1_MODE,
        "phase": "WDI Phase 1",
        "capability": PHASE1_CAPABILITY,
        "refresh_procedure": "bounded_phase1_manual_refresh_with_deterministic_manifest_and_delta_report",
        "raw_fixture_path": normalized["raw_fixture_path"],
        "raw_sha256": normalized["raw_sha256"],
        "normalized_path": str(normalized_path),
        "source_urls": [request["url"] for request in raw["requests"]],
        "country_count": len(normalized["countries"]),
        "countries_sample": normalized["countries"][:5] + normalized["countries"][-5:],
        "indicators": PHASE1_INDICATORS,
        "date_range": PHASE1_DATE_RANGE,
        "row_count": normalized["row_count"],
        "expected_row_count": PHASE1_EXPECTED_OBSERVATION_COUNT,
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


def build_wdi_operational_phase1_refresh_delta_report(previous: dict[str, Any], current: dict[str, Any]) -> dict[str, Any]:
    report = build_wdi_macro_indicators_refresh_delta_report(previous, current)
    report["task"] = PHASE1_TASK_ID
    report["capability"] = PHASE1_CAPABILITY
    report["portfolio_category"] = PHASE1_MODE
    report["phase"] = "WDI Phase 1"
    report["refresh_verification"] = "bounded_phase1_pre_load_delta_check"
    report["non_goals"] = [
        "full_WDI_catalog_ingestion",
        "all_indicator_ingestion",
        "Controlled_Expansion",
        "production_scheduling",
        "KnowledgeForge_implementation",
        "loader_redesign",
        "architecture_redesign",
    ]
    report.pop("refresh_delta_fingerprint", None)
    report["refresh_delta_fingerprint"] = refresh_delta_report_fingerprint(report)
    return report


def write_wdi_operational_phase1_refresh_delta_report(
    previous: dict[str, Any],
    current: dict[str, Any],
    path: str | Path = PHASE1_DEFAULT_REFRESH_DELTA_PATH,
) -> dict[str, Any]:
    report = build_wdi_operational_phase1_refresh_delta_report(previous, current)
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report
