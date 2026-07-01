from __future__ import annotations

import json
from decimal import Decimal
from typing import Any

from macroforge.observed_ingestion import ObservedIngestionPackage, ObservedObservation, canonical_attribute_hash

SOURCE_CODE = "UN_COMTRADE_TRADE"
SOURCE_NAME = "UN Comtrade bounded bilateral total-goods trade evidence slice"
SOURCE_HOME_URL = "https://comtradeplus.un.org/"
PROVIDER_DATASET_CODE = "UN_COMTRADE:PUBLIC_PREVIEW:C:A:HS"
FREQUENCY = "A"
UNIT_CODE = "CURRENT_USD"
UNIT_LABEL = "Current US dollars"
SCOPE = "bounded TASK-060 UN Comtrade bilateral total-goods trade evidence slice"
EXPECTED_TYPE_CODE = "C"
EXPECTED_FREQ_CODE = "A"
EXPECTED_CLASSIFICATION = "HS"
EXPECTED_CLASSIFICATION_CODE = "H6"
EXPECTED_REPORTER_CODE = 842
EXPECTED_REPORTER_ISO = "USA"
EXPECTED_PARTNER_CODE = 392
EXPECTED_PARTNER_ISO = "JPN"
EXPECTED_FLOW_CODES = ("M", "X")
EXPECTED_CMD_CODE = "TOTAL"
EXPECTED_PERIOD = "2023"
FLOW_LABELS = {
    "M": "Import",
    "X": "Export",
}
INDICATOR_LABELS = {
    "M": "Import trade value, total goods",
    "X": "Export trade value, total goods",
}
VALUE_BASIS = {
    "M": "cifvalue",
    "X": "fobvalue",
}


def normalize_un_comtrade_trade_fixture(
    raw_payload: str | bytes,
    *,
    raw_artifact_path: str,
    raw_sha256: str,
    source_url: str,
    content_type: str,
) -> dict[str, Any]:
    """Normalize only the bounded TASK-060 UN Comtrade bilateral trade fixture."""

    payload = json.loads(_coerce_payload(raw_payload))
    if not isinstance(payload, dict):
        raise ValueError("TASK-060 UN Comtrade fixture must be a JSON object")
    records = payload.get("data")
    if not isinstance(records, list):
        raise ValueError("TASK-060 UN Comtrade fixture must contain a data array")

    rows = [_normalize_record(record) for record in records]
    rows.sort(key=lambda row: row["trade_direction_code"])
    periods = sorted({row["provider_period_code"] for row in rows})
    period_range = f"{periods[0]}-{periods[-1]}" if periods else "unknown"
    return {
        "source_code": SOURCE_CODE,
        "source_url": source_url,
        "content_type": content_type,
        "raw_artifact_path": raw_artifact_path,
        "raw_sha256": raw_sha256,
        "provider_dataset_code": PROVIDER_DATASET_CODE,
        "frequency": FREQUENCY,
        "period_range": period_range,
        "row_count": len(rows),
        "expected_row_count": 2,
        "input_filters": {
            "typeCode": EXPECTED_TYPE_CODE,
            "freqCode": EXPECTED_FREQ_CODE,
            "classification": EXPECTED_CLASSIFICATION,
            "reporterCode": EXPECTED_REPORTER_CODE,
            "reporterISO": EXPECTED_REPORTER_ISO,
            "partnerCode": EXPECTED_PARTNER_CODE,
            "partnerISO": EXPECTED_PARTNER_ISO,
            "flowCode": list(EXPECTED_FLOW_CODES),
            "cmdCode": EXPECTED_CMD_CODE,
            "period": EXPECTED_PERIOD,
            "includeDesc": True,
            "scope": SCOPE,
        },
        "provider_metadata": {
            "provider": "UN Comtrade",
            "provider_name": "United Nations Comtrade",
            "api_surface": "public preview",
            "typeCode": EXPECTED_TYPE_CODE,
            "freqCode": EXPECTED_FREQ_CODE,
            "classification": EXPECTED_CLASSIFICATION,
            "classificationCode": EXPECTED_CLASSIFICATION_CODE,
            "cmdCode": EXPECTED_CMD_CODE,
            "cmdDesc": "All Commodities",
            "unit": UNIT_LABEL,
            "response_count": payload.get("count"),
            "response_error": payload.get("error"),
        },
        "rows": rows,
    }


def build_un_comtrade_trade_observed_package(normalized: dict[str, Any]) -> ObservedIngestionPackage:
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
            "source_url": normalized["source_url"],
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


def _normalize_record(record: dict[str, Any]) -> dict[str, Any]:
    _validate_record_scope(record)
    flow_code = str(record["flowCode"])
    value = record.get("primaryValue")
    value_basis = VALUE_BASIS[flow_code]
    attributes = {
        "source_provider": "UN Comtrade",
        "reporterCode": record["reporterCode"],
        "reporterISO": str(record["reporterISO"]),
        "reporterDesc": str(record["reporterDesc"]),
        "partnerCode": record["partnerCode"],
        "partnerISO": str(record["partnerISO"]),
        "partnerDesc": str(record["partnerDesc"]),
        "flowCode": flow_code,
        "flowDesc": str(record["flowDesc"]),
        "cmdCode": str(record["cmdCode"]),
        "cmdDesc": str(record["cmdDesc"]),
        "classificationCode": str(record["classificationCode"]),
        "classificationSearchCode": str(record["classificationSearchCode"]),
        "aggrLevel": record["aggrLevel"],
        "isAggregate": record["isAggregate"],
        "isOriginalClassification": record["isOriginalClassification"],
        "value_basis": value_basis,
        "fobvalue": record.get("fobvalue"),
        "cifvalue": record.get("cifvalue"),
        "qtyUnitCode": record.get("qtyUnitCode"),
        "qtyUnitAbbr": record.get("qtyUnitAbbr"),
        "qty": record.get("qty"),
        "netWgt": record.get("netWgt"),
        "grossWgt": record.get("grossWgt"),
        "isReported": record.get("isReported"),
        "legacyEstimationFlag": record.get("legacyEstimationFlag"),
    }
    return {
        "provider_indicator_code": f"TRADE_VALUE_TOTAL_GOODS_{flow_code}",
        "provider_indicator_label": INDICATOR_LABELS[flow_code],
        "territory_code": str(record["reporterISO"]),
        "territory_label": str(record["reporterDesc"]),
        "provider_period_code": str(record["period"]),
        "frequency": FREQUENCY,
        "period_year": int(record["period"]),
        "unit_code": UNIT_CODE,
        "unit_label": UNIT_LABEL,
        "value": value,
        "observation_status": "missing" if value is None else "observed",
        "decimal_precision": _decimal_precision(value),
        "trade_direction_code": flow_code,
        "attributes": attributes,
        "source_payload": dict(record),
    }


def _validate_record_scope(record: dict[str, Any]) -> None:
    required = {
        "typeCode",
        "freqCode",
        "period",
        "reporterCode",
        "reporterISO",
        "reporterDesc",
        "flowCode",
        "flowDesc",
        "partnerCode",
        "partnerISO",
        "partnerDesc",
        "classificationCode",
        "classificationSearchCode",
        "isOriginalClassification",
        "cmdCode",
        "cmdDesc",
        "aggrLevel",
        "isAggregate",
        "primaryValue",
    }
    missing = sorted(required.difference(record))
    if missing:
        raise ValueError(f"TASK-060 UN Comtrade record is missing required fields: {missing}")
    if record["typeCode"] != EXPECTED_TYPE_CODE:
        raise ValueError("TASK-060 UN Comtrade fixture contains an out-of-scope typeCode")
    if record["freqCode"] != EXPECTED_FREQ_CODE:
        raise ValueError("TASK-060 UN Comtrade fixture contains an out-of-scope freqCode")
    if record["reporterCode"] != EXPECTED_REPORTER_CODE or record["reporterISO"] != EXPECTED_REPORTER_ISO:
        raise ValueError("TASK-060 UN Comtrade fixture contains an out-of-scope reporter")
    if record["partnerCode"] != EXPECTED_PARTNER_CODE or record["partnerISO"] != EXPECTED_PARTNER_ISO:
        raise ValueError("TASK-060 UN Comtrade fixture contains an out-of-scope partner")
    if record["flowCode"] not in EXPECTED_FLOW_CODES:
        raise ValueError("TASK-060 UN Comtrade fixture contains an out-of-scope trade direction")
    if record["cmdCode"] != EXPECTED_CMD_CODE:
        raise ValueError("TASK-060 UN Comtrade fixture contains an out-of-scope commodity code")
    if record["period"] != EXPECTED_PERIOD:
        raise ValueError("TASK-060 UN Comtrade fixture contains an out-of-scope period")
    if record["classificationSearchCode"] != EXPECTED_CLASSIFICATION:
        raise ValueError("TASK-060 UN Comtrade fixture contains an out-of-scope classification search code")


def _decimal_precision(value: Any) -> int | None:
    if value is None:
        return None
    decimal = Decimal(str(value))
    exponent = int(decimal.as_tuple().exponent)
    if exponent >= 0:
        return 0
    return abs(exponent)


def _release_key(normalized: dict[str, Any]) -> str:
    raw_sha = normalized.get("raw_sha256", "unknown")
    filters = normalized["input_filters"]
    return (
        f"{SOURCE_CODE}:{filters['cmdCode']}:{filters['reporterISO']}:{filters['partnerISO']}:"
        f"{normalized['period_range']}:{raw_sha[:12]}"
    )
