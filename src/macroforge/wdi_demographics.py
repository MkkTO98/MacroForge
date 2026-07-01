from __future__ import annotations

import json
from decimal import Decimal
from typing import Any

from macroforge.observed_ingestion import ObservedIngestionPackage, ObservedObservation, canonical_attribute_hash

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
