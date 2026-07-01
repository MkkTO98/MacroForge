from __future__ import annotations

import csv
import io
from typing import Any

from macroforge.observed_ingestion import ObservedIngestionPackage, ObservedObservation, canonical_attribute_hash

SOURCE_CODE = "ALFRED_GDP_VINTAGE"
SOURCE_NAME = "ALFRED bounded GDP release-vintage evidence slice"
SOURCE_HOME_URL = "https://alfred.stlouisfed.org/"
PROVIDER_DATASET_CODE = "ALFRED:GDP"
SERIES_ID = "GDP"
SERIES_TITLE = "Gross Domestic Product"
FREQUENCY = "Q"
TERRITORY_CODE = "USA"
TERRITORY_LABEL = "United States"
UNIT_CODE = "BILLIONS_USD_SAAR"
UNIT_LABEL = "Billions of Dollars, Seasonally Adjusted Annual Rate"
SCOPE = "bounded TASK-058 ALFRED revision-vintage architectural evidence slice"


def normalize_alfred_gdp_vintage_fixture(
    raw_payload: str | bytes,
    *,
    raw_artifact_path: str,
    raw_sha256: str,
    source_url: str,
    content_type: str,
) -> dict[str, Any]:
    """Normalize the bounded TASK-058 ALFRED GDP vintage CSV without broad ALFRED support."""

    text = _coerce_payload(raw_payload)
    reader = csv.DictReader(io.StringIO(text))
    if reader.fieldnames is None or "observation_date" not in reader.fieldnames:
        raise ValueError("TASK-058 ALFRED fixture must include observation_date")

    vintage_columns = [field for field in reader.fieldnames if field.startswith(f"{SERIES_ID}_")]
    if len(vintage_columns) != 2:
        raise ValueError("TASK-058 ALFRED fixture must include exactly two GDP vintage columns")
    vintage_dates = [_vintage_date_from_column(column) for column in vintage_columns]

    rows: list[dict[str, Any]] = []
    source_rows = list(reader)
    for source_row in source_rows:
        observation_date = source_row["observation_date"]
        provider_period_code, period_year, period_quarter = _quarterly_period(observation_date)
        for column, vintage_date in zip(vintage_columns, vintage_dates, strict=True):
            raw_value = source_row[column]
            rows.append(
                _normalize_observation(
                    observation_date=observation_date,
                    provider_period_code=provider_period_code,
                    period_year=period_year,
                    period_quarter=period_quarter,
                    vintage_column=column,
                    vintage_date=vintage_date,
                    raw_value=raw_value,
                )
            )

    rows.sort(key=lambda row: (row["vintage_date"], row["provider_period_code"]))
    periods = sorted({row["provider_period_code"] for row in rows})
    period_range = f"{periods[0]}-{periods[-1]}" if periods else "unknown"
    revision_summary = _revision_summary(rows)
    return {
        "source_code": SOURCE_CODE,
        "source_url": source_url,
        "content_type": content_type,
        "raw_artifact_path": raw_artifact_path,
        "raw_sha256": raw_sha256,
        "provider_dataset_code": PROVIDER_DATASET_CODE,
        "series_id": SERIES_ID,
        "series_title": SERIES_TITLE,
        "frequency": FREQUENCY,
        "period_range": period_range,
        "vintage_dates": vintage_dates,
        "row_count": len(rows),
        "expected_row_count": len(rows),
        "input_filters": {
            "series_id": SERIES_ID,
            "vintage_dates": vintage_dates,
            "observation_start": source_rows[0]["observation_date"] if source_rows else None,
            "observation_end": source_rows[-1]["observation_date"] if source_rows else None,
            "scope": SCOPE,
        },
        "provider_metadata": {
            "provider": "ALFRED",
            "provider_name": "ArchivaL Federal Reserve Economic Data",
            "source_agency": "Federal Reserve Bank of St. Louis",
            "series_id": SERIES_ID,
            "series_title": SERIES_TITLE,
            "release": "Gross Domestic Product",
            "source": "U.S. Bureau of Economic Analysis",
            "frequency": "Quarterly",
            "units": UNIT_LABEL,
        },
        "revision_summary": revision_summary,
        "rows": rows,
    }


def build_alfred_gdp_revision_observed_package(normalized: dict[str, Any]) -> ObservedIngestionPackage:
    return _build_package(normalized, list(normalized["rows"]), release_key=_combined_release_key(normalized))


def build_alfred_gdp_vintage_packages(normalized: dict[str, Any]) -> dict[str, ObservedIngestionPackage]:
    packages: dict[str, ObservedIngestionPackage] = {}
    for vintage_date in normalized["vintage_dates"]:
        vintage_rows = [row for row in normalized["rows"] if row["vintage_date"] == vintage_date]
        packages[vintage_date] = _build_package(
            normalized,
            vintage_rows,
            release_key=_vintage_release_key(normalized, vintage_date),
            vintage_date=vintage_date,
        )
    return packages


def _build_package(
    normalized: dict[str, Any],
    rows: list[dict[str, Any]],
    *,
    release_key: str,
    vintage_date: str | None = None,
) -> ObservedIngestionPackage:
    observations = []
    for row in rows:
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
                period_quarter=row["period_quarter"],
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

    raw_evidence: dict[str, Any] = {
        "source_url": normalized["source_url"],
        "content_type": normalized["content_type"],
        "raw_artifact_path": normalized["raw_artifact_path"],
        "raw_sha256": normalized["raw_sha256"],
        "provider_metadata": dict(normalized["provider_metadata"]),
        "revision_summary": dict(normalized["revision_summary"]),
    }
    input_filters = dict(normalized["input_filters"])
    if vintage_date is not None:
        raw_evidence["vintage_date"] = vintage_date
        input_filters["vintage_date"] = vintage_date

    return ObservedIngestionPackage(
        source_code=SOURCE_CODE,
        source_name=SOURCE_NAME,
        source_home_url=SOURCE_HOME_URL,
        provider_dataset_code=normalized["provider_dataset_code"],
        release_key=release_key,
        raw_evidence=raw_evidence,
        input_filters=input_filters,
        row_count=len(observations),
        expected_row_count=len(observations),
        observations=tuple(observations),
    )


def _coerce_payload(raw_payload: str | bytes) -> str:
    if isinstance(raw_payload, bytes):
        return raw_payload.decode("utf-8")
    return raw_payload


def _vintage_date_from_column(column: str) -> str:
    raw_date = column.removeprefix(f"{SERIES_ID}_")
    if len(raw_date) != 8 or not raw_date.isdigit():
        raise ValueError("TASK-058 ALFRED vintage columns must use GDP_YYYYMMDD format")
    return f"{raw_date[:4]}-{raw_date[4:6]}-{raw_date[6:]}"


def _quarterly_period(observation_date: str) -> tuple[str, int, int]:
    year_text, month_text, _day_text = observation_date.split("-", 2)
    year = int(year_text)
    month = int(month_text)
    if month not in {1, 4, 7, 10}:
        raise ValueError("TASK-058 ALFRED GDP fixture must use quarter-start observation dates")
    quarter = ((month - 1) // 3) + 1
    return f"{year}-Q{quarter}", year, quarter


def _normalize_observation(
    *,
    observation_date: str,
    provider_period_code: str,
    period_year: int,
    period_quarter: int,
    vintage_column: str,
    vintage_date: str,
    raw_value: str,
) -> dict[str, Any]:
    attributes = {
        "series_id": SERIES_ID,
        "vintage_date": vintage_date,
        "release_identity": f"ALFRED:{SERIES_ID}:{vintage_date}",
        "observation_date": observation_date,
        "source_provider": "ALFRED",
    }
    return {
        "provider_indicator_code": SERIES_ID,
        "provider_indicator_label": SERIES_TITLE,
        "territory_code": TERRITORY_CODE,
        "territory_label": TERRITORY_LABEL,
        "provider_period_code": provider_period_code,
        "frequency": FREQUENCY,
        "period_year": period_year,
        "period_quarter": period_quarter,
        "unit_code": UNIT_CODE,
        "unit_label": UNIT_LABEL,
        "value": _parse_value(raw_value),
        "observation_status": "missing" if raw_value in {"", "."} else "observed",
        "decimal_precision": _decimal_precision(raw_value),
        "vintage_date": vintage_date,
        "attributes": attributes,
        "source_payload": {
            "observation_date": observation_date,
            "vintage_column": vintage_column,
            "vintage_date": vintage_date,
            "raw_value": raw_value,
        },
    }


def _parse_value(raw_value: str) -> float | None:
    if raw_value in {"", "."}:
        return None
    return float(raw_value)


def _decimal_precision(raw_value: str) -> int | None:
    if "." not in raw_value:
        return 0 if raw_value else None
    return len(raw_value.rsplit(".", 1)[1])


def _revision_summary(rows: list[dict[str, Any]]) -> dict[str, list[str]]:
    by_period: dict[str, list[Any]] = {}
    for row in rows:
        by_period.setdefault(row["provider_period_code"], []).append(row["value"])
    overlapping_periods = sorted(period for period, values in by_period.items() if len(values) > 1)
    changed_periods = sorted(period for period, values in by_period.items() if len(values) > 1 and len(set(values)) > 1)
    unchanged_control_periods = sorted(period for period, values in by_period.items() if len(values) > 1 and len(set(values)) == 1)
    if not changed_periods:
        raise ValueError("TASK-058 ALFRED fixture must include at least one revised overlapping value")
    if not unchanged_control_periods:
        raise ValueError("TASK-058 ALFRED fixture must include at least one unchanged overlapping control value")
    return {
        "overlapping_periods": overlapping_periods,
        "changed_periods": changed_periods,
        "unchanged_control_periods": unchanged_control_periods,
    }


def _combined_release_key(normalized: dict[str, Any]) -> str:
    vintage_part = "+".join(normalized["vintage_dates"])
    raw_sha = normalized.get("raw_sha256", "unknown")
    return f"{SOURCE_CODE}:{SERIES_ID}:{vintage_part}:{normalized['period_range']}:{raw_sha[:12]}"


def _vintage_release_key(normalized: dict[str, Any], vintage_date: str) -> str:
    raw_sha = normalized.get("raw_sha256", "unknown")
    return f"{SOURCE_CODE}:{SERIES_ID}:{vintage_date}:{normalized['period_range']}:{raw_sha[:12]}"
