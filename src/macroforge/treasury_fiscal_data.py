from __future__ import annotations

from typing import Any

from macroforge.observed_ingestion import ObservedIngestionPackage, ObservedObservation, canonical_attribute_hash

SOURCE_CODE = "TREASURY_FISCAL_DATA"
SOURCE_NAME = "U.S. Treasury Fiscal Data bounded average interest rates evidence slice"
SOURCE_HOME_URL = "https://fiscaldata.treasury.gov/"
PROVIDER_DATASET_CODE = "FISCAL_SERVICE:avg_interest_rates"
ENDPOINT = "avg_interest_rates"
TERRITORY_CODE = "USA"
TERRITORY_LABEL = "United States"
UNIT_CODE = "PERCENT"
UNIT_LABEL = "Percent"
VALUE_FIELD = "avg_interest_rate_amt"
RECORD_DATE = "2026-05-31"


def normalize_treasury_avg_interest_fixture(
    raw: dict[str, Any],
    *,
    raw_artifact_path: str,
    raw_sha256: str,
    source_url: str,
) -> dict[str, Any]:
    """Normalize the bounded TASK-054 Treasury Fiscal Data fixture without broad support."""

    meta = raw.get("meta", {})
    rows = [_normalize_row(row, meta) for row in raw.get("data", [])]
    rows.sort(key=lambda row: row["security_desc"])
    period_range = f"{rows[0]['provider_period_code']}-{rows[-1]['provider_period_code']}" if rows else "unknown"
    provider_metadata = _provider_metadata(raw)
    return {
        "source_code": SOURCE_CODE,
        "source_url": source_url,
        "raw_artifact_path": raw_artifact_path,
        "raw_sha256": raw_sha256,
        "provider_dataset_code": PROVIDER_DATASET_CODE,
        "endpoint": ENDPOINT,
        "frequency": "M",
        "period_range": period_range,
        "row_count": len(rows),
        "expected_row_count": int(meta.get("total-count", len(rows))),
        "input_filters": {
            "endpoint": ENDPOINT,
            "fields": "record_date,security_desc,avg_interest_rate_amt",
            "filter": "record_date:eq:2026-05-31",
            "sort": "security_desc",
            "page_size": 20,
            "scope": "bounded TASK-054 architectural experiment",
        },
        "provider_metadata": provider_metadata,
        "rows": rows,
    }


def build_treasury_avg_interest_observed_package(normalized: dict[str, Any]) -> ObservedIngestionPackage:
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
            "provider_metadata": dict(normalized["provider_metadata"]),
        },
        input_filters=dict(normalized["input_filters"]),
        row_count=int(normalized["row_count"]),
        expected_row_count=int(normalized["expected_row_count"]),
        observations=tuple(observations),
    )


def _normalize_row(row: dict[str, Any], meta: dict[str, Any]) -> dict[str, Any]:
    record_date = str(row["record_date"])
    if record_date != RECORD_DATE:
        raise ValueError("TASK-054 Treasury fixture must use bounded record_date 2026-05-31")
    period_year, period_month = _monthly_period(record_date)
    security_desc = str(row["security_desc"])
    value_text = row.get(VALUE_FIELD)
    labels = meta.get("labels", {})
    data_types = meta.get("dataTypes", {})
    data_formats = meta.get("dataFormats", {})
    attributes = {
        "endpoint": ENDPOINT,
        "record_date": record_date,
        "security_desc": security_desc,
        "field_label": labels.get(VALUE_FIELD),
        "value_field": VALUE_FIELD,
        "data_type": data_types.get(VALUE_FIELD),
        "data_format": data_formats.get(VALUE_FIELD),
        "api_count": int(meta.get("count", 0)),
        "api_total_count": int(meta.get("total-count", 0)),
        "api_total_pages": int(meta.get("total-pages", 0)),
    }
    return {
        "endpoint": ENDPOINT,
        "provider_indicator_code": f"AVG_INTEREST_RATE:{_indicator_suffix(security_desc)}",
        "provider_indicator_label": f"Average Interest Rate Amount — {security_desc}",
        "security_desc": security_desc,
        "territory_code": TERRITORY_CODE,
        "territory_label": TERRITORY_LABEL,
        "provider_period_code": f"{period_year}-M{period_month:02d}",
        "record_date": record_date,
        "frequency": "M",
        "period_year": period_year,
        "period_month": period_month,
        "unit_code": UNIT_CODE,
        "unit_label": UNIT_LABEL,
        "value": _parse_value(value_text),
        "observation_status": "missing" if value_text in {None, ""} else "observed",
        "decimal_precision": _decimal_precision(value_text),
        "attributes": attributes,
        "source_payload": dict(row),
    }


def _provider_metadata(raw: dict[str, Any]) -> dict[str, Any]:
    meta = raw.get("meta", {})
    links = raw.get("links", {})
    return {
        "count": int(meta.get("count", 0)),
        "total_count": int(meta.get("total-count", 0)),
        "total_pages": int(meta.get("total-pages", 0)),
        "labels": dict(meta.get("labels", {})),
        "data_types": dict(meta.get("dataTypes", {})),
        "data_formats": dict(meta.get("dataFormats", {})),
        "pagination": {
            "self": links.get("self"),
            "first": links.get("first"),
            "prev": links.get("prev"),
            "next": links.get("next"),
            "last": links.get("last"),
        },
    }


def _monthly_period(record_date: str) -> tuple[int, int]:
    year_text, month_text, day_text = record_date.split("-")
    if day_text not in {"28", "29", "30", "31"}:
        raise ValueError(f"unsupported Treasury monthly record date: {record_date}")
    month = int(month_text)
    if month not in set(range(1, 13)):
        raise ValueError(f"unsupported Treasury monthly record date: {record_date}")
    return int(year_text), month


def _indicator_suffix(value: str) -> str:
    chars = []
    for char in value.upper():
        if char.isalnum():
            chars.append(char)
        elif chars and chars[-1] != "_":
            chars.append("_")
    return "".join(chars).strip("_")


def _parse_value(value: Any) -> float | None:
    if value in {None, ""}:
        return None
    return float(str(value).replace(",", ""))


def _decimal_precision(value: Any) -> int | None:
    if value is None or "." not in str(value):
        return None
    return len(str(value).split(".", 1)[1])


def _release_key(normalized: dict[str, Any]) -> str:
    return f"TREASURY_FISCAL_DATA:{normalized['endpoint']}:{normalized['period_range']}:{normalized['raw_sha256'][:12]}"
