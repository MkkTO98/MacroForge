from __future__ import annotations

from typing import Any
from xml.etree import ElementTree as ET

from macroforge.observed_ingestion import ObservedIngestionPackage, ObservedObservation, canonical_attribute_hash

SOURCE_CODE = "IMF_BOP_FINANCIAL_ACCOUNT"
SOURCE_NAME = "International Monetary Fund bounded BOP financial-account evidence slice"
SOURCE_HOME_URL = "https://www.imf.org/"
PROVIDER_DATASET_CODE = "BOP"
DATAFLOW_CODE = "BOP"
DATAFLOW_VERSION = "21.0.0"
FREQUENCY = "A"
COUNTRIES = ("USA", "JPN")
ACCOUNTING_ENTRIES = ("A_NFA_T", "L_NIL_T")
INDICATORS = ("D_F", "P_F")
UNIT_CODE = "USD"
START_PERIOD = "2022"
END_PERIOD = "2023"
EXPECTED_ROW_COUNT = len(COUNTRIES) * len(ACCOUNTING_ENTRIES) * len(INDICATORS) * 2

NS = {
    "message": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message",
    "common": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/common",
}


def normalize_imf_bop_financial_account_fixture(
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
    """Normalize only the bounded TASK-063 IMF BOP financial-account fixture."""

    root = ET.fromstring(_coerce_payload(raw_payload))
    metadata_root = ET.fromstring(_coerce_payload(metadata_payload))
    provider_metadata = _provider_metadata(root, metadata_root)
    rows: list[dict[str, Any]] = []
    for series in _children_by_local_name(root, "Series"):
        series_attributes = dict(series.attrib)
        _validate_bounded_series(series_attributes)
        for obs in _children_by_local_name(series, "Obs"):
            rows.append(_normalize_observation(series_attributes, dict(obs.attrib), provider_metadata))

    rows.sort(
        key=lambda row: (
            row["territory_code"],
            row["accounting_entry_code"],
            row["investment_category_code"],
            row["provider_period_code"],
        )
    )
    periods = sorted({row["provider_period_code"] for row in rows})
    period_range = f"{periods[0]}-{periods[-1]}" if periods else "unknown"
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
        "expected_row_count": EXPECTED_ROW_COUNT,
        "input_filters": {
            "dataflow": DATAFLOW_CODE,
            "countries": list(COUNTRIES),
            "accounting_entries": list(ACCOUNTING_ENTRIES),
            "indicators": list(INDICATORS),
            "unit": UNIT_CODE,
            "frequency": FREQUENCY,
            "startPeriod": START_PERIOD,
            "endPeriod": END_PERIOD,
            "scope": "bounded TASK-063 IMF BOP financial-account evidence slice",
        },
        "provider_metadata": provider_metadata,
        "rows": rows,
    }


def build_imf_bop_financial_account_observed_package(normalized: dict[str, Any]) -> ObservedIngestionPackage:
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
    return {
        "message_id": _text(header, "message:ID"),
        "prepared": _text(header, "message:Prepared"),
        "sender": sender.attrib.get("id") if sender is not None else None,
        "structure_id": structure.attrib.get("structureID") if structure is not None else None,
        "dataset_action": _text(header, "message:DataSetAction") or (dataset.attrib.get("action") if dataset is not None else None),
        "dataset_attributes": _dataset_attributes(dataset),
        "dimension_at_observation": structure.attrib.get("dimensionAtObservation", "TIME_PERIOD") if structure is not None else "TIME_PERIOD",
        "dataflow": _metadata_dataflow(metadata_root),
        "data_structure": _metadata_data_structure(metadata_root),
        "dimension_order": _dimension_order(metadata_root),
        "codelists": _relevant_codelists(metadata_root),
    }


def _dataset_attributes(dataset: ET.Element | None) -> dict[str, str]:
    if dataset is None:
        return {}
    allowed = [
        "LANGUAGE",
        "PUBLISHER",
        "UPDATE_DATE",
        "PUBLICATION_DATE",
        "CONTACT_POINT",
        "DEPARTMENT",
        "TOPIC_DATASET",
        "SHORT_SOURCE_CITATION",
        "SUGGESTED_CITATION",
    ]
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


def _dimension_order(metadata_root: ET.Element) -> list[str]:
    ordered: list[tuple[int, str]] = []
    time_dimension: str | None = None
    for dimension in metadata_root.iter():
        name = _local_name(dimension.tag)
        if name == "Dimension" and dimension.attrib.get("id"):
            position = dimension.attrib.get("position")
            if position is not None:
                ordered.append((int(position), dimension.attrib["id"]))
        elif name == "TimeDimension":
            time_dimension = dimension.attrib.get("id", "TIME_PERIOD")
    dimensions = [dimension_id for _, dimension_id in sorted(ordered)]
    if time_dimension:
        dimensions.append(time_dimension)
    return dimensions


def _relevant_codelists(metadata_root: ET.Element) -> dict[str, dict[str, str]]:
    desired_codes = {
        "CL_BOP_COUNTRY": set(COUNTRIES),
        "CL_BOP_ACCOUNTING_ENTRY": set(ACCOUNTING_ENTRIES),
        "CL_BOP_INDICATOR": set(INDICATORS),
        "CL_UNIT": {UNIT_CODE},
        "CL_FREQ": {FREQUENCY},
    }
    codelists: dict[str, dict[str, str]] = {codelist_id: {} for codelist_id in desired_codes}
    for codelist in metadata_root.iter():
        if _local_name(codelist.tag) != "Codelist":
            continue
        codelist_id = codelist.attrib.get("id")
        if codelist_id not in desired_codes:
            continue
        labels: dict[str, str] = {}
        for code in codelist:
            if _local_name(code.tag) != "Code":
                continue
            code_id = code.attrib.get("id")
            if code_id is not None and code_id in desired_codes[codelist_id]:
                labels[code_id] = _first_child_name(code) or code_id
        codelists[codelist_id] = labels
    return codelists


def _first_child_name(element: ET.Element) -> str | None:
    for child in element:
        if _local_name(child.tag) == "Name" and child.text:
            return child.text.strip()
    return None


def _validate_bounded_series(series_attributes: dict[str, str]) -> None:
    expected = {
        "COUNTRY": COUNTRIES,
        "BOP_ACCOUNTING_ENTRY": ACCOUNTING_ENTRIES,
        "INDICATOR": INDICATORS,
        "UNIT": (UNIT_CODE,),
        "FREQUENCY": (FREQUENCY,),
    }
    for field, allowed_values in expected.items():
        value = series_attributes.get(field)
        if value not in allowed_values:
            raise ValueError(f"unexpected IMF BOP {field}: {value}")


def _normalize_observation(
    series_attributes: dict[str, str],
    obs_attributes: dict[str, str],
    provider_metadata: dict[str, Any],
) -> dict[str, Any]:
    territory_code = series_attributes["COUNTRY"]
    accounting_entry_code = series_attributes["BOP_ACCOUNTING_ENTRY"]
    investment_category_code = series_attributes["INDICATOR"]
    unit_code = series_attributes["UNIT"]
    period = obs_attributes["TIME_PERIOD"]
    value_text = obs_attributes["OBS_VALUE"]
    accounting_entry_label = _label(provider_metadata, "CL_BOP_ACCOUNTING_ENTRY", accounting_entry_code)
    investment_category_label = _label(provider_metadata, "CL_BOP_INDICATOR", investment_category_code)
    attributes = {
        "dataflow_code": DATAFLOW_CODE,
        "bop_scope": "financial_account_transactions",
        "accounting_entry_code": accounting_entry_code,
        "accounting_entry_label": accounting_entry_label,
        "investment_category_code": investment_category_code,
        "investment_category_label": investment_category_label,
        "financial_account_side": _financial_account_side(accounting_entry_code),
        "unit_code": unit_code,
        "methodology": series_attributes.get("METHODOLOGY"),
        "scale": series_attributes.get("SCALE"),
        "precision": obs_attributes.get("PRECISION"),
        "derivation_type": obs_attributes.get("DERIVATION_TYPE"),
        "access_sharing_level": obs_attributes.get("ACCESS_SHARING_LEVEL"),
        "security_classification": obs_attributes.get("SECURITY_CLASSIFICATION"),
        "series_key": f"{territory_code}.{accounting_entry_code}.{investment_category_code}.{unit_code}.{FREQUENCY}",
    }
    if "IFS_FLAG" in series_attributes:
        attributes["ifs_flag"] = series_attributes["IFS_FLAG"]
    return {
        "provider_indicator_code": f"{DATAFLOW_CODE}:{accounting_entry_code}:{investment_category_code}",
        "provider_indicator_label": f"{accounting_entry_label} — {investment_category_label}",
        "territory_code": territory_code,
        "territory_label": _label(provider_metadata, "CL_BOP_COUNTRY", territory_code),
        "provider_period_code": period,
        "frequency": FREQUENCY,
        "period_year": int(period),
        "unit_code": unit_code,
        "unit_label": _label(provider_metadata, "CL_UNIT", unit_code),
        "value": float(value_text),
        "observation_status": _observation_status(obs_attributes),
        "decimal_precision": _decimal_precision(value_text),
        "accounting_entry_code": accounting_entry_code,
        "investment_category_code": investment_category_code,
        "attributes": attributes,
        "source_payload": {
            "series_attributes": dict(series_attributes),
            "obs_attributes": dict(obs_attributes),
        },
    }


def _label(provider_metadata: dict[str, Any], codelist_id: str, code: str) -> str:
    return provider_metadata.get("codelists", {}).get(codelist_id, {}).get(code, code)


def _financial_account_side(accounting_entry_code: str) -> str:
    if accounting_entry_code == "A_NFA_T":
        return "asset"
    if accounting_entry_code == "L_NIL_T":
        return "liability"
    return "unknown"


def _observation_status(obs_attributes: dict[str, str]) -> str:
    security = obs_attributes.get("SECURITY_CLASSIFICATION")
    access = obs_attributes.get("ACCESS_SHARING_LEVEL")
    if security == "PUB" and access == "PUBLIC_OPEN":
        return "observed"
    return obs_attributes.get("OBS_STATUS", "observed")


def _decimal_precision(value_text: str) -> int:
    if "." not in value_text:
        return 0
    return len(value_text.rstrip("0").split(".", 1)[1])


def _release_key(normalized: dict[str, Any]) -> str:
    return ":".join(
        [
            SOURCE_CODE,
            normalized["provider_dataset_code"],
            normalized["period_range"],
            normalized["raw_sha256"][:16],
            normalized["metadata_sha256"][:16],
        ]
    )
