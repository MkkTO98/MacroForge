from __future__ import annotations

import json
from decimal import Decimal
from typing import Any

from macroforge.observed_ingestion import ObservedIngestionPackage, ObservedObservation, canonical_attribute_hash

SOURCE_CODE = "ILOSTAT_UNEMPLOYMENT"
SOURCE_NAME = "ILOSTAT bounded unemployment-rate evidence slice"
SOURCE_HOME_URL = "https://ilostat.ilo.org/"
PROVIDER_DATASET_CODE = "ILOSTAT:UNE_2EAP_SEX_AGE_RT_A"
API_INDICATOR_ID = "UNE_2EAP_SEX_AGE_RT_A"
OBSERVED_INDICATOR_ID = "UNE_2EAP_SEX_AGE_RT"
INDICATOR_LABEL = "Unemployment rate by sex and age"
FREQUENCY = "A"
UNIT_CODE = "PERCENT_OF_LABOR_FORCE"
UNIT_LABEL = "Percent of labor force"
SCOPE = "bounded TASK-059 ILOSTAT unemployment-rate evidence slice"
EXPECTED_REF_AREAS = ("USA", "JPN")
EXPECTED_SEX = "SEX_T"
EXPECTED_CLASSIF1 = "AGE_YTHADULT_YGE15"
EXPECTED_TIMEFROM = "2023"
EXPECTED_TIMETO = "2024"
TERRITORY_LABELS = {
    "JPN": "Japan",
    "USA": "United States",
}
SEX_LABELS = {
    "SEX_T": "Total sex",
}
CLASSIF1_LABELS = {
    "AGE_YTHADULT_YGE15": "Age 15+",
}


def normalize_ilostat_unemployment_fixture(
    raw_payload: str | bytes,
    *,
    raw_artifact_path: str,
    raw_sha256: str,
    source_url: str,
    content_type: str,
) -> dict[str, Any]:
    """Normalize the bounded TASK-059 ILOSTAT unemployment fixture only."""

    records = json.loads(_coerce_payload(raw_payload))
    if not isinstance(records, list):
        raise ValueError("TASK-059 ILOSTAT fixture must be a JSON array")

    rows = [_normalize_record(record) for record in records]
    rows.sort(key=lambda row: (row["territory_code"], row["provider_period_code"]))
    periods = sorted({row["provider_period_code"] for row in rows})
    period_range = f"{periods[0]}-{periods[-1]}" if periods else "unknown"
    return {
        "source_code": SOURCE_CODE,
        "source_url": source_url,
        "content_type": content_type,
        "raw_artifact_path": raw_artifact_path,
        "raw_sha256": raw_sha256,
        "provider_dataset_code": PROVIDER_DATASET_CODE,
        "indicator_id": OBSERVED_INDICATOR_ID,
        "indicator_label": INDICATOR_LABEL,
        "frequency": FREQUENCY,
        "period_range": period_range,
        "row_count": len(rows),
        "expected_row_count": 4,
        "input_filters": {
            "id": API_INDICATOR_ID,
            "ref_area": list(EXPECTED_REF_AREAS),
            "sex": EXPECTED_SEX,
            "classif1": EXPECTED_CLASSIF1,
            "timefrom": EXPECTED_TIMEFROM,
            "timeto": EXPECTED_TIMETO,
            "format": "json",
            "scope": SCOPE,
        },
        "provider_metadata": {
            "provider": "ILOSTAT",
            "provider_name": "International Labour Organization ILOSTAT",
            "api_indicator_id": API_INDICATOR_ID,
            "indicator_id": OBSERVED_INDICATOR_ID,
            "indicator_label": INDICATOR_LABEL,
            "frequency": "Annual",
            "unit": UNIT_LABEL,
            "sex": EXPECTED_SEX,
            "sex_label": SEX_LABELS[EXPECTED_SEX],
            "classif1": EXPECTED_CLASSIF1,
            "classif1_label": CLASSIF1_LABELS[EXPECTED_CLASSIF1],
        },
        "rows": rows,
    }


def build_ilostat_unemployment_observed_package(normalized: dict[str, Any]) -> ObservedIngestionPackage:
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
    territory_code = str(record["ref_area"])
    period = str(record["time"])
    value = record.get("obs_value")
    obs_status = str(record.get("obs_status", ""))
    attributes = {
        "source_provider": "ILOSTAT",
        "source_code": str(record["source"]),
        "sex": str(record["sex"]),
        "sex_label": SEX_LABELS.get(str(record["sex"])),
        "classif1": str(record["classif1"]),
        "classif1_label": CLASSIF1_LABELS.get(str(record["classif1"])),
        "obs_status": obs_status,
    }
    return {
        "provider_indicator_code": OBSERVED_INDICATOR_ID,
        "provider_indicator_label": INDICATOR_LABEL,
        "territory_code": territory_code,
        "territory_label": TERRITORY_LABELS.get(territory_code),
        "provider_period_code": period,
        "frequency": FREQUENCY,
        "period_year": int(period),
        "unit_code": UNIT_CODE,
        "unit_label": UNIT_LABEL,
        "value": value,
        "observation_status": _observation_status(obs_status, value),
        "decimal_precision": _decimal_precision(value),
        "attributes": attributes,
        "source_payload": dict(record),
    }


def _validate_record_scope(record: dict[str, Any]) -> None:
    required = {"ref_area", "source", "indicator", "sex", "classif1", "time", "obs_value", "obs_status"}
    missing = sorted(required.difference(record))
    if missing:
        raise ValueError(f"TASK-059 ILOSTAT record is missing required fields: {missing}")
    if record["ref_area"] not in EXPECTED_REF_AREAS:
        raise ValueError("TASK-059 ILOSTAT fixture contains an out-of-scope ref_area")
    if record["indicator"] != OBSERVED_INDICATOR_ID:
        raise ValueError("TASK-059 ILOSTAT fixture contains an out-of-scope indicator")
    if record["sex"] != EXPECTED_SEX:
        raise ValueError("TASK-059 ILOSTAT fixture contains an out-of-scope sex classification")
    if record["classif1"] != EXPECTED_CLASSIF1:
        raise ValueError("TASK-059 ILOSTAT fixture contains an out-of-scope age classification")
    year = int(str(record["time"]))
    if year < int(EXPECTED_TIMEFROM) or year > int(EXPECTED_TIMETO):
        raise ValueError("TASK-059 ILOSTAT fixture contains an out-of-scope year")


def _observation_status(obs_status: str, value: Any) -> str:
    if value is None:
        return "missing"
    if obs_status in {"", "R"}:
        return "observed"
    return "observed"


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
    return f"{SOURCE_CODE}:{API_INDICATOR_ID}:{normalized['period_range']}:{raw_sha[:12]}"
