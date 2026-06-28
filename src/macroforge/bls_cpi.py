from __future__ import annotations

from typing import Any

from macroforge.observed_ingestion import (
    ObservedIngestionPackage,
    ObservedObservation,
    canonical_attribute_hash,
)

SERIES_ID = "CUUR0000SA0"
SERIES_LABEL = "CPI-U, U.S. city average, all items"
PROVIDER_DATASET_CODE = "BLS_PUBLIC_API_V2_TIMESERIES"
SOURCE_CODE = "BLS_CPI"
SOURCE_NAME = "U.S. Bureau of Labor Statistics CPI bounded monthly evidence slice"
SOURCE_HOME_URL = "https://www.bls.gov/cpi/"
TERRITORY_CODE = "USA"
TERRITORY_LABEL = "United States"
UNIT_CODE = "INDEX_1982_84_100"
UNIT_LABEL = "Index 1982-84=100"


def normalize_bls_cpi_fixture(
    raw: dict[str, Any],
    *,
    raw_artifact_path: str,
    raw_sha256: str,
    source_url: str,
) -> dict[str, Any]:
    """Normalize the bounded TASK-051 BLS CPI fixture without generalizing BLS support."""

    if raw.get("status") != "REQUEST_SUCCEEDED":
        raise ValueError("BLS fixture status must be REQUEST_SUCCEEDED")

    series = raw.get("Results", {}).get("series", [])
    if len(series) != 1 or series[0].get("seriesID") != SERIES_ID:
        raise ValueError("TASK-051 BLS fixture must contain exactly CUUR0000SA0")

    rows = [_normalize_observation(row) for row in series[0].get("data", [])]
    rows.sort(key=lambda row: (row["period_year"], row["period_month"]))
    period_range = f"{rows[0]['provider_period_code']}-{rows[-1]['provider_period_code']}" if rows else "unknown"

    return {
        "source_url": source_url,
        "raw_artifact_path": raw_artifact_path,
        "raw_sha256": raw_sha256,
        "provider_dataset_code": PROVIDER_DATASET_CODE,
        "series_id": SERIES_ID,
        "series_label": SERIES_LABEL,
        "territory_code": TERRITORY_CODE,
        "territory_label": TERRITORY_LABEL,
        "frequency": "M",
        "period_range": period_range,
        "row_count": len(rows),
        "rows": rows,
    }


def build_bls_cpi_observed_package(normalized: dict[str, Any]) -> ObservedIngestionPackage:
    observations = []
    for row in normalized["rows"]:
        attributes = dict(row["attributes"])
        observations.append(
            ObservedObservation(
                provider_indicator_code=row["series_id"],
                provider_indicator_label=row["series_label"],
                provider_territory_code=row["territory_code"],
                provider_territory_label=row["territory_label"],
                provider_period_code=row["provider_period_code"],
                frequency=row["frequency"],
                period_year=row["period_year"],
                period_month=row["period_month"],
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

    row_count = int(normalized.get("row_count", len(observations)))
    return ObservedIngestionPackage(
        source_code=SOURCE_CODE,
        source_name=SOURCE_NAME,
        source_home_url=SOURCE_HOME_URL,
        provider_dataset_code=normalized["provider_dataset_code"],
        release_key=_release_key(normalized),
        raw_evidence={
            "source_url": normalized["source_url"],
            "raw_artifact_path": normalized["raw_artifact_path"],
            "raw_sha256": normalized["raw_sha256"],
        },
        input_filters={
            "series_id": normalized["series_id"],
            "startyear": "2023",
            "endyear": "2023",
            "scope": "bounded TASK-051 architectural experiment",
        },
        row_count=row_count,
        expected_row_count=row_count,
        observations=tuple(observations),
    )


def _normalize_observation(row: dict[str, Any]) -> dict[str, Any]:
    year = int(row["year"])
    month = _month_number(row["period"])
    attributes = {"footnotes": _footnotes(row), "period_name": row.get("periodName")}
    return {
        "series_id": SERIES_ID,
        "series_label": SERIES_LABEL,
        "territory_code": TERRITORY_CODE,
        "territory_label": TERRITORY_LABEL,
        "provider_period_code": f"{year}-M{month:02d}",
        "frequency": "M",
        "period_year": year,
        "period_month": month,
        "unit_code": UNIT_CODE,
        "unit_label": UNIT_LABEL,
        "value": float(row["value"]),
        "observation_status": "missing" if row.get("value") in {None, ""} else "observed",
        "decimal_precision": _decimal_precision(row.get("value")),
        "attributes": attributes,
        "source_payload": dict(row),
    }


def _release_key(normalized: dict[str, Any]) -> str:
    raw_sha = normalized.get("raw_sha256", "unknown")
    return f"BLS_CPI:{normalized['series_id']}:{normalized['period_range']}:{raw_sha[:12]}"


def _month_number(period: str) -> int:
    if len(period) != 3 or not period.startswith("M"):
        raise ValueError(f"unsupported BLS monthly period: {period}")
    month = int(period[1:])
    if month < 1 or month > 12:
        raise ValueError(f"unsupported BLS monthly period: {period}")
    return month


def _decimal_precision(value: Any) -> int | None:
    if value is None or "." not in str(value):
        return None
    return len(str(value).split(".", 1)[1])


def _footnotes(row: dict[str, Any]) -> list[dict[str, Any]]:
    return [footnote for footnote in row.get("footnotes", []) if footnote]
