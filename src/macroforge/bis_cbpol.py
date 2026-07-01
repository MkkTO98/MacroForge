from __future__ import annotations

from typing import Any
from xml.etree import ElementTree as ET

from macroforge.observed_ingestion import ObservedIngestionPackage, ObservedObservation, canonical_attribute_hash

SOURCE_CODE = "BIS_CBPOL"
SOURCE_NAME = "Bank for International Settlements bounded central bank policy rates SDMX evidence slice"
SOURCE_HOME_URL = "https://www.bis.org/"
PROVIDER_DATASET_CODE = "BIS:WS_CBPOL"
DATAFLOW_CODE = "WS_CBPOL"
DATAFLOW_VERSION = "1.0"
FREQUENCY = "M"
REFERENCE_AREAS = ("US", "JP")
START_PERIOD = "2024-01"
END_PERIOD = "2024-03"
UNIT_CODE = "PERCENT"
UNIT_LABEL = "Percent"
INDICATOR_CODE = "WS_CBPOL:POLICY_RATE"
INDICATOR_LABEL = "Central bank policy rates"
TERRITORY_LABELS = {"US": "United States", "JP": "Japan"}

NS = {
    "message": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message",
    "common": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/common",
}


def normalize_bis_cbpol_fixture(
    raw_payload: str | bytes,
    *,
    raw_artifact_path: str,
    raw_sha256: str,
    source_url: str,
    content_type: str,
) -> dict[str, Any]:
    """Normalize the bounded TASK-057 BIS CBPOL fixture without broad BIS or SDMX support."""

    root = ET.fromstring(_coerce_payload(raw_payload))
    provider_metadata = _provider_metadata(root)
    rows: list[dict[str, Any]] = []
    for series in _children_by_local_name(root, "Series"):
        series_attributes = dict(series.attrib)
        _validate_bounded_series(series_attributes)
        for obs in _children_by_local_name(series, "Obs"):
            rows.append(_normalize_observation(series_attributes, dict(obs.attrib)))

    rows.sort(key=lambda row: (row["territory_code"], row["provider_period_code"], row["provider_indicator_code"]))
    period_range = f"{rows[0]['provider_period_code']}-{rows[-1]['provider_period_code']}" if rows else "unknown"
    return {
        "source_code": SOURCE_CODE,
        "source_url": source_url,
        "content_type": content_type,
        "raw_artifact_path": raw_artifact_path,
        "raw_sha256": raw_sha256,
        "provider_dataset_code": PROVIDER_DATASET_CODE,
        "dataflow_code": DATAFLOW_CODE,
        "dataflow_version": provider_metadata["dataflow"]["version"],
        "frequency": FREQUENCY,
        "period_range": period_range,
        "row_count": len(rows),
        "expected_row_count": len(rows),
        "input_filters": {
            "dataflow": DATAFLOW_CODE,
            "reference_areas": list(REFERENCE_AREAS),
            "frequency": FREQUENCY,
            "startPeriod": START_PERIOD,
            "endPeriod": END_PERIOD,
            "scope": "bounded TASK-057 BIS WS_CBPOL architectural evidence slice",
        },
        "provider_metadata": provider_metadata,
        "rows": rows,
    }


def build_bis_cbpol_observed_package(normalized: dict[str, Any]) -> ObservedIngestionPackage:
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
            "content_type": normalized["content_type"],
            "raw_artifact_path": normalized["raw_artifact_path"],
            "raw_sha256": normalized["raw_sha256"],
            "provider_metadata": dict(normalized["provider_metadata"]),
        },
        input_filters=dict(normalized["input_filters"]),
        row_count=int(normalized["row_count"]),
        expected_row_count=int(normalized["expected_row_count"]),
        observations=tuple(observations),
    )


def _coerce_payload(raw_payload: str | bytes) -> bytes:
    if isinstance(raw_payload, bytes):
        return raw_payload
    return raw_payload.encode("utf-8")


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _children_by_local_name(element: ET.Element, local_name: str) -> list[ET.Element]:
    return [descendant for descendant in element.iter() if _local_name(descendant.tag) == local_name]


def _text(element: ET.Element | None, path: str) -> str | None:
    if element is None:
        return None
    child = element.find(path, NS)
    if child is None or child.text is None:
        return None
    text = child.text.strip()
    return text or None


def _provider_metadata(root: ET.Element) -> dict[str, Any]:
    header = root.find("message:Header", NS)
    structure = header.find("message:Structure", NS) if header is not None else None
    sender = header.find("message:Sender", NS) if header is not None else None
    dataset = root.find("message:DataSet", NS)
    return {
        "message_id": _text(header, "message:ID"),
        "prepared": _text(header, "message:Prepared"),
        "sender": sender.attrib.get("id") if sender is not None else None,
        "structure_id": structure.attrib.get("structureID") if structure is not None else None,
        "structure_namespace": structure.attrib.get("namespace") if structure is not None else None,
        "dataset_action": _text(header, "message:DataSetAction"),
        "dataset_attributes": _dataset_attributes(dataset),
        "dimension_at_observation": structure.attrib.get("dimensionAtObservation", "TIME_PERIOD") if structure is not None else "TIME_PERIOD",
        "dataflow": _dataflow_ref(structure),
    }


def _dataset_attributes(dataset: ET.Element | None) -> dict[str, str]:
    if dataset is None:
        return {}
    allowed = ["UNIT_MULT", "UNIT_MEASURE"]
    return {key: dataset.attrib[key] for key in allowed if key in dataset.attrib}


def _dataflow_ref(structure: ET.Element | None) -> dict[str, str | None]:
    if structure is not None:
        for descendant in structure.iter():
            if _local_name(descendant.tag) == "Ref" and descendant.attrib.get("id") == DATAFLOW_CODE:
                return {
                    "agency_id": descendant.attrib.get("agencyID"),
                    "id": descendant.attrib.get("id"),
                    "version": descendant.attrib.get("version"),
                }
    return {"agency_id": "BIS", "id": DATAFLOW_CODE, "version": DATAFLOW_VERSION}


def _validate_bounded_series(series_attributes: dict[str, str]) -> None:
    if series_attributes.get("FREQ") != FREQUENCY:
        raise ValueError("TASK-057 BIS fixture must use monthly frequency")
    if series_attributes.get("REF_AREA") not in REFERENCE_AREAS:
        raise ValueError("TASK-057 BIS fixture must use bounded US/JP reference areas")


def _normalize_observation(series_attributes: dict[str, str], obs_attributes: dict[str, str]) -> dict[str, Any]:
    period = obs_attributes["TIME_PERIOD"]
    if period < START_PERIOD or period > END_PERIOD:
        raise ValueError("TASK-057 BIS fixture contains period outside bounded range")
    period_year, period_month = _monthly_period(period)
    value_text = obs_attributes.get("OBS_VALUE")
    ref_area = series_attributes["REF_AREA"]
    attributes = {
        "dataflow": DATAFLOW_CODE,
        "series_key": f"{series_attributes['FREQ']}.{ref_area}",
        "source_ref": series_attributes.get("SOURCE_REF"),
        "compilation": series_attributes.get("COMPILATION"),
        "title": _clean_title(series_attributes.get("TITLE")),
        "obs_status": obs_attributes.get("OBS_STATUS"),
        "obs_conf": obs_attributes.get("OBS_CONF"),
    }
    return {
        "provider_indicator_code": INDICATOR_CODE,
        "provider_indicator_label": INDICATOR_LABEL,
        "territory_code": ref_area,
        "territory_label": TERRITORY_LABELS[ref_area],
        "provider_period_code": f"{period_year}-M{period_month:02d}",
        "frequency": FREQUENCY,
        "period_year": period_year,
        "period_month": period_month,
        "unit_code": UNIT_CODE,
        "unit_label": UNIT_LABEL,
        "value": _parse_value(value_text),
        "observation_status": "missing" if value_text in {None, ""} else "observed",
        "decimal_precision": _decimal_precision(value_text),
        "attributes": attributes,
        "source_payload": {
            "series_attributes": dict(series_attributes),
            "obs_attributes": dict(obs_attributes),
        },
    }


def _monthly_period(period: str) -> tuple[int, int]:
    year_text, month_text = period.split("-", 1)
    month = int(month_text)
    if month not in range(1, 13):
        raise ValueError(f"unsupported BIS monthly period: {period}")
    return int(year_text), month


def _parse_value(value: str | None) -> float | None:
    if value is None or value == "":
        return None
    return float(value)


def _decimal_precision(value: str | None) -> int | None:
    if value is None or "." not in value:
        return None
    return len(value.split(".", 1)[1])


def _clean_title(value: str | None) -> str | None:
    if value is None:
        return None
    return value.strip()


def _release_key(normalized: dict[str, Any]) -> str:
    return f"BIS_CBPOL:{DATAFLOW_CODE}:{normalized['period_range']}:{normalized['raw_sha256'][:12]}"
