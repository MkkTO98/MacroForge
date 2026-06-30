from __future__ import annotations

from typing import Any
from xml.etree import ElementTree as ET

from macroforge.observed_ingestion import ObservedIngestionPackage, ObservedObservation, canonical_attribute_hash

SOURCE_CODE = "ECB_SDW"
SOURCE_NAME = "European Central Bank Statistical Data Warehouse bounded exchange-rate evidence slice"
SOURCE_HOME_URL = "https://data.ecb.europa.eu/"
PROVIDER_DATASET_CODE = "EXR:M.USD.EUR.SP00.A"
DATAFLOW_CODE = "EXR"
SERIES_KEY = "M.USD.EUR.SP00.A"
TERRITORY_CODE = "ECB_AREA"
TERRITORY_LABEL = "European Central Bank statistical area"

NS = {
    "message": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message",
    "common": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/common",
    "generic": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic",
}


def normalize_ecb_exr_fixture(
    raw_payload: str | bytes,
    *,
    raw_artifact_path: str,
    raw_sha256: str,
    source_url: str,
    content_type: str,
) -> dict[str, Any]:
    """Normalize the bounded TASK-055 ECB EXR SDW fixture without broad ECB or SDMX support."""

    root = ET.fromstring(_coerce_payload(raw_payload))
    provider_metadata = _provider_metadata(root)
    rows = []
    for series in root.findall(".//generic:Series", NS):
        series_dimensions = _values_by_id(series.find("generic:SeriesKey", NS))
        _validate_bounded_series(series_dimensions)
        series_attributes = _values_by_id(series.find("generic:Attributes", NS))
        for obs in series.findall("generic:Obs", NS):
            obs_dimension = _observation_dimension(obs, provider_metadata["dimension_at_observation"])
            obs_value = _obs_value(obs)
            obs_attributes = _values_by_id(obs.find("generic:Attributes", NS))
            rows.append(
                _normalize_observation(
                    series_dimensions,
                    series_attributes,
                    obs_dimension,
                    obs_value,
                    obs_attributes,
                    provider_metadata["dimension_at_observation"],
                )
            )

    rows.sort(key=lambda row: (row["provider_period_code"], row["provider_indicator_code"]))
    period_range = f"{rows[0]['provider_period_code']}-{rows[-1]['provider_period_code']}" if rows else "unknown"
    return {
        "source_code": SOURCE_CODE,
        "source_url": source_url,
        "content_type": content_type,
        "raw_artifact_path": raw_artifact_path,
        "raw_sha256": raw_sha256,
        "provider_dataset_code": PROVIDER_DATASET_CODE,
        "dataflow_code": DATAFLOW_CODE,
        "series_key": SERIES_KEY,
        "frequency": "M",
        "period_range": period_range,
        "row_count": len(rows),
        "expected_row_count": len(rows),
        "input_filters": {
            "dataflow": DATAFLOW_CODE,
            "series_key": SERIES_KEY,
            "startPeriod": "2026-05",
            "endPeriod": "2026-05",
            "scope": "bounded TASK-055 architectural experiment",
        },
        "provider_metadata": provider_metadata,
        "rows": rows,
    }


def build_ecb_exr_observed_package(normalized: dict[str, Any]) -> ObservedIngestionPackage:
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


def _text(element: ET.Element | None, path: str) -> str | None:
    if element is None:
        return None
    child = element.find(path, NS)
    if child is None or child.text is None:
        return None
    text = child.text.strip()
    return text or None


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _first_descendant_text(element: ET.Element | None, local_name: str) -> str | None:
    if element is None:
        return None
    for descendant in element.iter():
        if _local_name(descendant.tag) == local_name and descendant.text is not None:
            text = descendant.text.strip()
            return text or None
    return None


def _provider_metadata(root: ET.Element) -> dict[str, Any]:
    header = root.find("message:Header", NS)
    structure = header.find("message:Structure", NS) if header is not None else None
    dataset = root.find("message:DataSet", NS)
    sender = header.find("message:Sender", NS) if header is not None else None
    return {
        "message_id": _text(header, "message:ID"),
        "prepared": _text(header, "message:Prepared"),
        "sender": sender.attrib.get("id") if sender is not None else None,
        "structure_id": structure.attrib.get("structureID") if structure is not None else None,
        "structure_urn": _first_descendant_text(structure, "URN"),
        "dataset_action": dataset.attrib.get("action") if dataset is not None else None,
        "valid_from_date": dataset.attrib.get("validFromDate") if dataset is not None else None,
        "dimension_at_observation": structure.attrib.get("dimensionAtObservation", "TIME_PERIOD") if structure is not None else "TIME_PERIOD",
    }


def _values_by_id(parent: ET.Element | None) -> dict[str, str]:
    values: dict[str, str] = {}
    if parent is None:
        return values
    for value in parent.findall("generic:Value", NS):
        identifier = value.attrib.get("id")
        raw_value = value.attrib.get("value")
        if identifier is not None and raw_value is not None:
            values[identifier] = raw_value
    return values


def _validate_bounded_series(dimensions: dict[str, str]) -> None:
    expected = {
        "FREQ": "M",
        "CURRENCY": "USD",
        "CURRENCY_DENOM": "EUR",
        "EXR_TYPE": "SP00",
        "EXR_SUFFIX": "A",
    }
    if dimensions != expected:
        raise ValueError("TASK-055 ECB fixture must use bounded EXR M.USD.EUR.SP00.A series")


def _observation_dimension(obs: ET.Element, dimension_at_observation: str) -> dict[str, str]:
    node = obs.find("generic:ObsDimension", NS)
    if node is None:
        return {}
    dimension_id = node.attrib.get("id") or dimension_at_observation
    value = node.attrib.get("value")
    return {dimension_id: value} if value is not None else {}


def _obs_value(obs: ET.Element) -> str | None:
    node = obs.find("generic:ObsValue", NS)
    return node.attrib.get("value") if node is not None else None


def _normalize_observation(
    series_dimensions: dict[str, str],
    series_attributes: dict[str, str],
    obs_dimension: dict[str, str],
    obs_value: str | None,
    obs_attributes: dict[str, str],
    dimension_at_observation: str,
) -> dict[str, Any]:
    period_text = obs_dimension.get("TIME_PERIOD")
    if period_text is None:
        raise ValueError("TASK-055 ECB fixture must include TIME_PERIOD observation dimension")
    period_year, period_month = _monthly_period(period_text)
    currency = series_dimensions["CURRENCY"]
    currency_denom = series_dimensions["CURRENCY_DENOM"]
    exr_type = series_dimensions["EXR_TYPE"]
    exr_suffix = series_dimensions["EXR_SUFFIX"]
    title = series_attributes.get("TITLE")
    attributes = {
        "dataflow_code": DATAFLOW_CODE,
        "series_key": SERIES_KEY,
        "frequency": series_dimensions["FREQ"],
        "currency": currency,
        "currency_denom": currency_denom,
        "exr_type": exr_type,
        "exr_suffix": exr_suffix,
        "decimals": series_attributes.get("DECIMALS"),
        "title_compl": series_attributes.get("TITLE_COMPL"),
        "unit_mult": series_attributes.get("UNIT_MULT"),
        "title": title,
        "source_agency": series_attributes.get("SOURCE_AGENCY"),
        "unit": series_attributes.get("UNIT"),
        "time_format": series_attributes.get("TIME_FORMAT"),
        "collection": series_attributes.get("COLLECTION"),
        "unit_index_base": series_attributes.get("UNIT_INDEX_BASE"),
        "obs_status": obs_attributes.get("OBS_STATUS"),
        "obs_conf": obs_attributes.get("OBS_CONF"),
        "dimension_at_observation": dimension_at_observation,
    }
    return {
        "dataflow_code": DATAFLOW_CODE,
        "series_key": SERIES_KEY,
        "provider_indicator_code": f"EXR:{currency}_{currency_denom}:{exr_type}:{exr_suffix}",
        "provider_indicator_label": title,
        "currency": currency,
        "currency_denom": currency_denom,
        "exr_type": exr_type,
        "exr_suffix": exr_suffix,
        "territory_code": TERRITORY_CODE,
        "territory_label": TERRITORY_LABEL,
        "provider_period_code": f"{period_year}-M{period_month:02d}",
        "frequency": series_dimensions["FREQ"],
        "period_year": period_year,
        "period_month": period_month,
        "unit_code": f"{currency}_PER_{currency_denom}",
        "unit_label": f"{_currency_label(currency)} per {_currency_label(currency_denom).lower()}",
        "value": _float_or_none(obs_value),
        "observation_status": _observation_status(obs_attributes, obs_value),
        "decimal_precision": _decimal_precision(obs_value),
        "attributes": attributes,
        "source_payload": {
            "series_dimensions": dict(series_dimensions),
            "series_attributes": dict(series_attributes),
            "obs_dimension": dict(obs_dimension),
            "obs_value": obs_value,
            "obs_attributes": dict(obs_attributes),
        },
    }


def _monthly_period(period: str) -> tuple[int, int]:
    year_text, month_text = period.split("-", 1)
    month = int(month_text)
    if month not in set(range(1, 13)):
        raise ValueError(f"unsupported ECB monthly period: {period}")
    return int(year_text), month


def _currency_label(currency: str) -> str:
    labels = {"USD": "US dollar", "EUR": "euro"}
    return labels.get(currency, currency)


def _float_or_none(value: str | None) -> float | None:
    if value is None or value == "":
        return None
    return float(value)


def _observation_status(obs_attributes: dict[str, str], value: str | None) -> str:
    if value in {None, ""}:
        return "missing"
    status = obs_attributes.get("OBS_STATUS", "A")
    if status in {"M", "L", "N"}:
        return "missing"
    if status in {"C", "S"}:
        return "suppressed"
    return "observed"


def _decimal_precision(value: str | None) -> int | None:
    if value is None or "." not in value:
        return None
    return len(value.split(".", 1)[1])


def _release_key(normalized: dict[str, Any]) -> str:
    return f"ECB_SDW:{normalized['provider_dataset_code']}:{normalized['period_range']}:{normalized['raw_sha256'][:12]}"
