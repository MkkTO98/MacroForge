from __future__ import annotations

from typing import Any
from xml.etree import ElementTree as ET

from macroforge.observed_ingestion import ObservedIngestionPackage, ObservedObservation, canonical_attribute_hash

SOURCE_CODE = "IMF_MFS_IR"
SOURCE_NAME = "International Monetary Fund bounded MFS_IR interest-rate SDMX evidence slice"
SOURCE_HOME_URL = "https://www.imf.org/"
PROVIDER_DATASET_CODE = "MFS_IR"
DATAFLOW_CODE = "MFS_IR"
DATAFLOW_VERSION = "9.0.0"
INDICATOR_CODE = "MFS166_RT_PT_A_PT"
FREQUENCY = "M"
COUNTRIES = ("USA", "JPN")
START_PERIOD = "2024-01"
END_PERIOD = "2024-03"
UNIT_CODE = "PERCENT"
UNIT_LABEL = "Percent"

NS = {
    "message": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message",
    "common": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/common",
    "structure": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/structure",
}


def normalize_imf_mfs_ir_fixture(
    raw_payload: str | bytes,
    *,
    metadata_payload: str | bytes,
    raw_artifact_path: str,
    raw_sha256: str,
    metadata_artifact_path: str,
    metadata_sha256: str,
    source_urls: tuple[str, ...] | list[str],
    metadata_url: str,
    content_type: str,
) -> dict[str, Any]:
    """Normalize the bounded TASK-056 IMF MFS_IR fixture without broad IMF or SDMX support."""

    root = ET.fromstring(_coerce_payload(raw_payload))
    metadata_root = ET.fromstring(_coerce_payload(metadata_payload))
    provider_metadata = _provider_metadata(root, metadata_root)
    rows: list[dict[str, Any]] = []
    for series in _children_by_local_name(root, "Series"):
        series_attributes = dict(series.attrib)
        _validate_bounded_series(series_attributes)
        for obs in _children_by_local_name(series, "Obs"):
            rows.append(_normalize_observation(series_attributes, dict(obs.attrib), provider_metadata))

    rows.sort(key=lambda row: (row["territory_code"], row["provider_period_code"], row["provider_indicator_code"]))
    period_range = f"{rows[0]['provider_period_code']}-{rows[-1]['provider_period_code']}" if rows else "unknown"
    return {
        "source_code": SOURCE_CODE,
        "source_urls": list(source_urls),
        "metadata_url": metadata_url,
        "content_type": content_type,
        "raw_artifact_path": raw_artifact_path,
        "raw_sha256": raw_sha256,
        "metadata_artifact_path": metadata_artifact_path,
        "metadata_sha256": metadata_sha256,
        "provider_dataset_code": PROVIDER_DATASET_CODE,
        "dataflow_code": DATAFLOW_CODE,
        "dataflow_version": provider_metadata["dataflow"]["version"],
        "frequency": FREQUENCY,
        "period_range": period_range,
        "row_count": len(rows),
        "expected_row_count": len(rows),
        "input_filters": {
            "dataflow": DATAFLOW_CODE,
            "countries": list(COUNTRIES),
            "indicator": INDICATOR_CODE,
            "frequency": FREQUENCY,
            "startPeriod": START_PERIOD,
            "endPeriod": END_PERIOD,
            "scope": "bounded TASK-056 IMF MFS_IR architectural evidence slice",
        },
        "provider_metadata": provider_metadata,
        "rows": rows,
    }


def build_imf_mfs_ir_observed_package(normalized: dict[str, Any]) -> ObservedIngestionPackage:
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
            "source_urls": list(normalized["source_urls"]),
            "metadata_url": normalized["metadata_url"],
            "content_type": normalized["content_type"],
            "raw_artifact_path": normalized["raw_artifact_path"],
            "raw_sha256": normalized["raw_sha256"],
            "metadata_artifact_path": normalized["metadata_artifact_path"],
            "metadata_sha256": normalized["metadata_sha256"],
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


def _provider_metadata(root: ET.Element, metadata_root: ET.Element) -> dict[str, Any]:
    header = root.find("message:Header", NS)
    structure = header.find("message:Structure", NS) if header is not None else None
    sender = header.find("message:Sender", NS) if header is not None else None
    dataset = root.find("message:DataSet", NS)
    dataflow = _metadata_dataflow(metadata_root)
    data_structure = _metadata_data_structure(metadata_root)
    return {
        "message_id": _text(header, "message:ID"),
        "prepared": _text(header, "message:Prepared"),
        "sender": sender.attrib.get("id") if sender is not None else None,
        "structure_id": structure.attrib.get("structureID") if structure is not None else None,
        "dataset_action": _text(header, "message:DataSetAction") or (dataset.attrib.get("action") if dataset is not None else None),
        "dataset_attributes": _dataset_attributes(dataset),
        "dimension_at_observation": structure.attrib.get("dimensionAtObservation", "TIME_PERIOD") if structure is not None else "TIME_PERIOD",
        "dataflow": dataflow,
        "data_structure": data_structure,
        "dimension_order": _dimension_order(metadata_root),
        "codelists": _relevant_codelists(metadata_root),
    }


def _dataset_attributes(dataset: ET.Element | None) -> dict[str, str]:
    if dataset is None:
        return {}
    allowed = ["LANGUAGE", "PUBLISHER", "UPDATE_DATE", "PUBLICATION_DATE", "CONTACT_POINT", "DEPARTMENT", "TOPIC_DATASET"]
    return {key: dataset.attrib[key] for key in allowed if key in dataset.attrib}


def _metadata_dataflow(metadata_root: ET.Element) -> dict[str, str | None]:
    for dataflow in metadata_root.iter():
        if _local_name(dataflow.tag) == "Dataflow" and dataflow.attrib.get("id") == DATAFLOW_CODE:
            return {
                "agency_id": dataflow.attrib.get("agencyID"),
                "id": dataflow.attrib.get("id"),
                "version": dataflow.attrib.get("version"),
                "name": _first_child_name(dataflow),
            }
    return {"agency_id": None, "id": DATAFLOW_CODE, "version": DATAFLOW_VERSION, "name": None}


def _metadata_data_structure(metadata_root: ET.Element) -> dict[str, str | None]:
    for data_structure in metadata_root.iter():
        if _local_name(data_structure.tag) == "DataStructure":
            return {
                "agency_id": data_structure.attrib.get("agencyID"),
                "id": data_structure.attrib.get("id"),
                "version": data_structure.attrib.get("version"),
            }
    return {"agency_id": None, "id": None, "version": None}


def _first_child_name(element: ET.Element) -> str | None:
    for child in element:
        if _local_name(child.tag) == "Name" and child.text:
            return child.text.strip()
    return None


def _dimension_order(metadata_root: ET.Element) -> list[str]:
    ordered: list[tuple[int, str]] = []
    time_dimension: str | None = None
    for dimension in metadata_root.iter():
        name = _local_name(dimension.tag)
        if name == "Dimension" and "id" in dimension.attrib:
            position = int(dimension.attrib.get("position", len(ordered)))
            ordered.append((position, dimension.attrib["id"]))
        elif name == "TimeDimension" and "id" in dimension.attrib:
            time_dimension = dimension.attrib["id"]
    result = [identifier for _, identifier in sorted(ordered)]
    if time_dimension is not None:
        result.append(time_dimension)
    return result


def _relevant_codelists(metadata_root: ET.Element) -> dict[str, dict[str, str | None]]:
    wanted = {
        "CL_MFS_COUNTRY": set(COUNTRIES),
        "CL_MFS_IR_INDICATOR": {INDICATOR_CODE},
        "CL_FREQ": {FREQUENCY},
    }
    codelists: dict[str, dict[str, str | None]] = {}
    for codelist in metadata_root.iter():
        if _local_name(codelist.tag) != "Codelist":
            continue
        codelist_id = codelist.attrib.get("id")
        if codelist_id not in wanted:
            continue
        codes: dict[str, str | None] = {}
        for child in codelist:
            if _local_name(child.tag) == "Code" and child.attrib.get("id") in wanted[codelist_id]:
                codes[child.attrib["id"]] = _first_child_name(child)
        codelists[codelist_id] = codes
    return codelists


def _validate_bounded_series(series_attributes: dict[str, str]) -> None:
    country = series_attributes.get("COUNTRY")
    if country not in COUNTRIES:
        raise ValueError("TASK-056 IMF fixture must use bounded USA/JPN countries")
    if series_attributes.get("INDICATOR") != INDICATOR_CODE:
        raise ValueError("TASK-056 IMF fixture must use bounded MFS166_RT_PT_A_PT indicator")
    if series_attributes.get("FREQUENCY") != FREQUENCY:
        raise ValueError("TASK-056 IMF fixture must use monthly frequency")


def _normalize_observation(
    series_attributes: dict[str, str],
    obs_attributes: dict[str, str],
    provider_metadata: dict[str, Any],
) -> dict[str, Any]:
    period_text = obs_attributes.get("TIME_PERIOD")
    if period_text is None:
        raise ValueError("TASK-056 IMF fixture must include TIME_PERIOD")
    period_year, period_month = _monthly_period(period_text)
    value_text = obs_attributes.get("OBS_VALUE")
    country = series_attributes["COUNTRY"]
    indicator = series_attributes["INDICATOR"]
    frequency = series_attributes["FREQUENCY"]
    codelists = provider_metadata.get("codelists", {})
    territory_label = codelists.get("CL_MFS_COUNTRY", {}).get(country) or country
    indicator_label = codelists.get("CL_MFS_IR_INDICATOR", {}).get(indicator) or indicator
    attributes = {
        "dataflow_code": DATAFLOW_CODE,
        "dataflow_version": provider_metadata["dataflow"].get("version"),
        "data_structure_id": provider_metadata["data_structure"].get("id"),
        "data_structure_version": provider_metadata["data_structure"].get("version"),
        "series_key": f"{country}.{indicator}.{frequency}",
        "country": country,
        "indicator": indicator,
        "frequency": frequency,
        "ifs_flag": series_attributes.get("IFS_FLAG"),
        "overlap": series_attributes.get("OVERLAP"),
        "scale": series_attributes.get("SCALE"),
        "access_sharing_level": series_attributes.get("ACCESS_SHARING_LEVEL"),
        "security_classification": series_attributes.get("SECURITY_CLASSIFICATION"),
        "derivation_type": obs_attributes.get("DERIVATION_TYPE"),
        "dimension_at_observation": provider_metadata.get("dimension_at_observation"),
    }
    return {
        "dataflow_code": DATAFLOW_CODE,
        "series_key": f"{country}.{indicator}.{frequency}",
        "provider_indicator_code": indicator,
        "provider_indicator_label": indicator_label,
        "territory_code": country,
        "territory_label": territory_label,
        "provider_period_code": f"{period_year}-M{period_month:02d}",
        "frequency": frequency,
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


def _monthly_period(period_text: str) -> tuple[int, int]:
    if "-M" in period_text:
        year_text, month_text = period_text.split("-M", 1)
    else:
        year_text, month_text = period_text.split("-", 1)
    month = int(month_text)
    if month not in set(range(1, 13)):
        raise ValueError(f"unsupported IMF monthly period: {period_text}")
    return int(year_text), month


def _parse_value(value: str | None) -> float | None:
    if value is None or value == "":
        return None
    return float(value)


def _decimal_precision(value: str | None) -> int | None:
    if value is None or "." not in value:
        return None
    return len(value.split(".", 1)[1])


def _release_key(normalized: dict[str, Any]) -> str:
    return f"IMF_MFS_IR:{normalized['provider_dataset_code']}:{normalized['period_range']}:{normalized['raw_sha256'][:12]}"
