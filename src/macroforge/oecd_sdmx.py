from __future__ import annotations

import argparse
import hashlib
import json
import urllib.request
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

SOURCE_CODE = "OECD_NAAG"
SOURCE_NAME = "OECD annual national accounts / NAAG Chapter 1 GDP dataflow"
SOURCE_HOME_URL = "https://sdmx.oecd.org/"
PROVIDER_DATASET_CODE = "OECD.SDD.NAD,DSD_NAAG@DF_NAAG_I"
DEFAULT_ENDPOINT = "https://sdmx.oecd.org/public/rest/v1/data/OECD.SDD.NAD,DSD_NAAG@DF_NAAG_I/.?startPeriod=2020&endPeriod=2021"
DEFAULT_CONTENT_TYPE = "application/vnd.sdmx.genericdata+xml; version=2.1; charset=utf-8"
DEFAULT_RAW_FILENAME = "oecd_sdmx_naag_2020_2021_raw.xml"
DEFAULT_NORMALIZED_FILENAME = "oecd-sdmx-smoke-normalized.json"
DEFAULT_REPORT_FILENAME = "oecd-sdmx-smoke-20260603.md"
DEFAULT_STRUCTURE_ENDPOINT = "https://sdmx.oecd.org/public/rest/v1/dataflow/OECD.SDD.NAD/all/latest"
DEFAULT_STRUCTURE_CONTENT_TYPE = "application/vnd.sdmx.structure+xml; version=2.1; charset=utf-8"
DEFAULT_STRUCTURE_RAW_FILENAME = "oecd_sdmx_naag_structure_20260604.xml"
DEFAULT_CODELIST_LABELS_FILENAME = "oecd-sdmx-codelist-labels-20260604.json"
DEFAULT_CODELIST_REPORT_FILENAME = "oecd-sdmx-codelist-labels-20260604.md"
DEFAULT_TERRITORY_CODES: tuple[str, ...] = ("AUS", "USA")
DEFAULT_MEASURE_CODES: tuple[str, ...] = ("B1GQ",)
DEFAULT_UNIT_CODES: tuple[str, ...] = ("USD_EXC", "USD_PPP")
DEFAULT_ATTRIBUTE_CODES: dict[str, tuple[str, ...]] = {
    "CONF_STATUS": ("F",),
    "OBS_STATUS": ("A",),
    "DECIMALS": ("2",),
}
DEFAULT_USER_AGENT = "MacroForge/0.1 (+https://localhost)"

NS = {
    "generic": "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic",
}

DEFAULT_CODELIST_TARGETS: dict[str, dict[str, Any]] = {
    "MEASURE": {"codelist_id": "CL_MEASURE", "codes": DEFAULT_MEASURE_CODES},
    "REF_AREA": {"codelist_id": "CL_REF_AREA", "codes": DEFAULT_TERRITORY_CODES},
    "UNIT_MEASURE": {"codelist_id": "CL_UNIT_MEASURE", "codes": DEFAULT_UNIT_CODES},
    "CONF_STATUS": {"codelist_id": "CL_CONF_STATUS", "codes": DEFAULT_ATTRIBUTE_CODES["CONF_STATUS"]},
    "OBS_STATUS": {"codelist_id": "CL_OBS_STATUS", "codes": DEFAULT_ATTRIBUTE_CODES["OBS_STATUS"]},
    "DECIMALS": {"codelist_id": "CL_DECIMALS", "codes": DEFAULT_ATTRIBUTE_CODES["DECIMALS"]},
}


def _coerce_payload(raw_payload: str | bytes) -> bytes:
    if isinstance(raw_payload, bytes):
        return raw_payload
    return raw_payload.encode("utf-8")


def _path_string(path: str | Path | None) -> str | None:
    if path is None:
        return None
    return str(Path(path))


def build_raw_metadata(
    raw_payload: str | bytes,
    *,
    endpoint: str = DEFAULT_ENDPOINT,
    content_type: str = DEFAULT_CONTENT_TYPE,
    artifact_path: str | Path | None = None,
) -> dict[str, Any]:
    """Build raw evidence metadata for an OECD SDMX XML payload."""
    payload = _coerce_payload(raw_payload)
    metadata: dict[str, Any] = {
        "endpoint": endpoint,
        "content_type": content_type,
        "bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
    }
    if artifact_path is not None:
        metadata["raw_artifact_path"] = _path_string(artifact_path)
    return metadata


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _first_child_text(element: ET.Element, child_name: str) -> str | None:
    for child in element:
        if _local_name(child.tag) == child_name and child.text is not None:
            text = child.text.strip()
            return text or None
    return None


def _codelists_by_id(root: ET.Element) -> dict[str, ET.Element]:
    codelists: dict[str, ET.Element] = {}
    for element in root.iter():
        if _local_name(element.tag) == "Codelist":
            codelist_id = element.attrib.get("id")
            if codelist_id:
                codelists[codelist_id] = element
    return codelists


def parse_codelist_labels(
    raw_payload: str | bytes,
    *,
    endpoint: str = DEFAULT_STRUCTURE_ENDPOINT,
    content_type: str = DEFAULT_STRUCTURE_CONTENT_TYPE,
    artifact_path: str | Path | None = None,
    targets: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Parse bounded OECD/SDMX codelist labels for the current smoke slice.

    This is source-specific and bounded to codes already present in OECD_NAAG
    smoke evidence. It is not a generalized SDMX metadata framework.
    """
    target_map = targets or DEFAULT_CODELIST_TARGETS
    payload = _coerce_payload(raw_payload)
    root = ET.fromstring(payload)
    codelists = _codelists_by_id(root)

    extracted: dict[str, Any] = {}
    for concept, spec in target_map.items():
        codelist_id = spec.get("codelist_id")
        wanted_codes = tuple(spec.get("codes", ()))
        codelist = codelists.get(codelist_id) if codelist_id else None
        concept_entry: dict[str, Any] = {
            "codelist_id": codelist_id if codelist is not None else None,
            "codelist_name": _first_child_text(codelist, "Name") if codelist is not None else None,
            "codes": {},
        }
        code_nodes: dict[str, ET.Element] = {}
        if codelist is not None:
            for child in codelist:
                if _local_name(child.tag) == "Code" and child.attrib.get("id"):
                    code_nodes[child.attrib["id"]] = child
        for code in wanted_codes:
            code_node = code_nodes.get(code)
            if code_node is None:
                concept_entry["codes"][code] = {
                    "label": None,
                    "description": "No codelist label found in bounded structure fixture.",
                }
            else:
                concept_entry["codes"][code] = {
                    "label": _first_child_text(code_node, "Name"),
                    "description": _first_child_text(code_node, "Description"),
                }
        extracted[concept] = concept_entry

    return {
        "source_code": SOURCE_CODE,
        "source_name": SOURCE_NAME,
        "source_home_url": SOURCE_HOME_URL,
        "provider_dataset_code": PROVIDER_DATASET_CODE,
        "raw_metadata": build_raw_metadata(
            payload,
            endpoint=endpoint,
            content_type=content_type,
            artifact_path=artifact_path,
        ),
        "codelists": extracted,
        "limitations": [
            "Bounded to currently observed OECD/SDMX smoke-slice codes; not a broad codelist harvest.",
            "DECIMALS is preserved as an observed attribute value when no codelist entry is present.",
            "No PostgreSQL schema change or live macro write is implied by this metadata evidence.",
        ],
    }


def _values_by_id(parent: ET.Element) -> dict[str, str]:
    values: dict[str, str] = {}
    for value in parent.findall("generic:Value", NS):
        identifier = value.attrib.get("id")
        raw_value = value.attrib.get("value")
        if identifier is not None and raw_value is not None:
            values[identifier] = raw_value
    return values


def parse_genericdata_observations(raw_payload: str | bytes) -> list[dict[str, Any]]:
    """Parse SDMX GenericData XML into source-shaped observation evidence.

    This is source-specific for TASK-012. It preserves codes and XML-derived
    dimensions; it does not perform codelist label enrichment or generalized
    SDMX dataflow handling.
    """
    root = ET.fromstring(_coerce_payload(raw_payload))
    observations: list[dict[str, Any]] = []

    for series in root.findall(".//generic:Series", NS):
        series_key = series.find("generic:SeriesKey", NS)
        series_dimensions = _values_by_id(series_key) if series_key is not None else {}

        for obs in series.findall("generic:Obs", NS):
            obs_dimension: dict[str, str] = {}
            dimension = obs.find("generic:ObsDimension", NS)
            if dimension is not None:
                dim_id = dimension.attrib.get("id")
                dim_value = dimension.attrib.get("value")
                if dim_id is not None and dim_value is not None:
                    obs_dimension[dim_id] = dim_value

            value_node = obs.find("generic:ObsValue", NS)
            obs_value = value_node.attrib.get("value") if value_node is not None else None

            attributes_node = obs.find("generic:Attributes", NS)
            attributes = _values_by_id(attributes_node) if attributes_node is not None else {}

            observations.append(
                {
                    "series_dimensions": series_dimensions,
                    "obs_dimension": obs_dimension,
                    "obs_value": obs_value,
                    "attributes": attributes,
                }
            )

    return observations


def _float_or_none(value: str | None) -> float | None:
    if value is None or value == "":
        return None
    return float(value)


def _sorted_filter(values: set[str] | list[str] | tuple[str, ...] | None) -> list[str] | None:
    if values is None:
        return None
    return sorted(values)


def normalize_sdmx_payload(
    raw_payload: str | bytes,
    *,
    endpoint: str = DEFAULT_ENDPOINT,
    content_type: str = DEFAULT_CONTENT_TYPE,
    territory_codes: set[str] | list[str] | tuple[str, ...] | None = None,
    measure_codes: set[str] | list[str] | tuple[str, ...] | None = None,
    artifact_path: str | Path | None = None,
) -> dict[str, Any]:
    territory_filter = set(territory_codes) if territory_codes is not None else None
    measure_filter = set(measure_codes) if measure_codes is not None else None

    rows: list[dict[str, Any]] = []
    for observation in parse_genericdata_observations(raw_payload):
        dimensions = observation["series_dimensions"]
        territory = dimensions.get("REF_AREA")
        measure = dimensions.get("MEASURE")
        if territory_filter is not None and territory not in territory_filter:
            continue
        if measure_filter is not None and measure not in measure_filter:
            continue

        rows.append(
            {
                "source_code": SOURCE_CODE,
                "provider_dataset_code": PROVIDER_DATASET_CODE,
                "indicator_code": measure,
                "territory_code": territory,
                "period": observation["obs_dimension"].get("TIME_PERIOD"),
                "frequency": dimensions.get("FREQ"),
                "value": _float_or_none(observation.get("obs_value")),
                "unit": dimensions.get("UNIT_MEASURE"),
                "attributes": observation["attributes"],
                "source_payload": {
                    "series_dimensions": dimensions,
                    "obs_dimension": observation["obs_dimension"],
                    "obs_value": observation.get("obs_value"),
                },
            }
        )

    return {
        "source_code": SOURCE_CODE,
        "source_name": SOURCE_NAME,
        "source_home_url": SOURCE_HOME_URL,
        "provider_dataset_code": PROVIDER_DATASET_CODE,
        "raw_metadata": build_raw_metadata(
            raw_payload,
            endpoint=endpoint,
            content_type=content_type,
            artifact_path=artifact_path,
        ),
        "filters": {
            "territory_codes": _sorted_filter(territory_codes),
            "measure_codes": _sorted_filter(measure_codes),
        },
        "row_count": len(rows),
        "rows": rows,
    }


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def render_markdown_report(result: dict[str, Any]) -> str:
    metadata = result["raw_metadata"]
    row_lines = "\n".join(
        f"| {row['indicator_code']} | {row['territory_code']} | {row['period']} | {row['frequency']} | {row['unit']} | {row['value']} |"
        for row in result["rows"]
    )
    if not row_lines:
        row_lines = "| _none_ | _none_ | _none_ | _none_ | _none_ | _none_ |"

    return f"""# OECD/SDMX smoke evidence slice

## Result

- Source: {result['source_code']} — {result['source_name']}
- Provider dataset code: `{result['provider_dataset_code']}`
- Endpoint: `{metadata['endpoint']}`
- Content type: `{metadata['content_type']}`
- Raw bytes: {metadata['bytes']}
- Raw SHA-256: `{metadata['sha256']}`
- Observations: {result['row_count']} observations
- Scope boundary: No PostgreSQL schema change and no live `macro` database write.

## Source contract mapping

- `source_code`: `{result['source_code']}`
- `provider_dataset_code`: `{result['provider_dataset_code']}`
- `indicator_code`: SDMX `MEASURE`
- `territory_code`: SDMX `REF_AREA`
- `period`: SDMX observation `TIME_PERIOD`
- `frequency`: SDMX `FREQ`
- `value`: SDMX `ObsValue.value`
- `unit`: SDMX `UNIT_MEASURE`
- `attributes`: SDMX observation attributes such as `CONF_STATUS`, `DECIMALS`, and `OBS_STATUS`
- `source_payload`: preserved series dimensions, observation dimension, and original observation value

## Normalized rows

| indicator | territory | period | frequency | unit | value |
| --- | --- | --- | --- | --- | ---: |
{row_lines}

## Schema pressure

No immediate schema change is required for this smoke evidence slice. Future PostgreSQL promotion should revisit codelist labels/descriptions and richer attribute-set handling before changing migrations.
"""


def write_smoke_artifacts(
    raw_payload: str | bytes,
    *,
    output_root: str | Path,
    endpoint: str = DEFAULT_ENDPOINT,
    content_type: str = DEFAULT_CONTENT_TYPE,
    territory_codes: set[str] | list[str] | tuple[str, ...] | None = None,
    measure_codes: set[str] | list[str] | tuple[str, ...] | None = None,
) -> dict[str, str]:
    output = Path(output_root)
    raw_dir = output / "raw" / "oecd_sdmx"
    metadata_dir = output / "metadata" / "oecd_sdmx"
    reports_dir = output / "reports"
    raw_path = raw_dir / DEFAULT_RAW_FILENAME
    normalized_path = metadata_dir / DEFAULT_NORMALIZED_FILENAME
    report_path = reports_dir / DEFAULT_REPORT_FILENAME

    raw_dir.mkdir(parents=True, exist_ok=True)
    metadata_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    raw_bytes = _coerce_payload(raw_payload)
    raw_path.write_bytes(raw_bytes)
    result = normalize_sdmx_payload(
        raw_bytes,
        endpoint=endpoint,
        content_type=content_type,
        territory_codes=territory_codes,
        measure_codes=measure_codes,
        artifact_path=raw_path,
    )
    _write_json(normalized_path, result)
    report_path.write_text(render_markdown_report(result), encoding="utf-8")

    return {
        "raw_artifact": str(raw_path),
        "normalized": str(normalized_path),
        "report": str(report_path),
    }


def write_project_smoke_artifacts(
    raw_payload: str | bytes,
    *,
    project_root: str | Path,
    endpoint: str = DEFAULT_ENDPOINT,
    content_type: str = DEFAULT_CONTENT_TYPE,
    territory_codes: set[str] | list[str] | tuple[str, ...] | None = None,
    measure_codes: set[str] | list[str] | tuple[str, ...] | None = None,
) -> dict[str, str]:
    project = Path(project_root)
    raw_path = project / "data" / "raw" / "oecd_sdmx" / DEFAULT_RAW_FILENAME
    normalized_path = project / "data" / "metadata" / "oecd_sdmx" / DEFAULT_NORMALIZED_FILENAME
    report_path = project / "artifacts" / "reports" / DEFAULT_REPORT_FILENAME

    raw_path.parent.mkdir(parents=True, exist_ok=True)
    normalized_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    raw_bytes = _coerce_payload(raw_payload)
    raw_path.write_bytes(raw_bytes)
    result = normalize_sdmx_payload(
        raw_bytes,
        endpoint=endpoint,
        content_type=content_type,
        territory_codes=territory_codes,
        measure_codes=measure_codes,
        artifact_path=raw_path,
    )
    _write_json(normalized_path, result)
    report_path.write_text(render_markdown_report(result), encoding="utf-8")

    return {
        "raw_artifact": str(raw_path),
        "normalized": str(normalized_path),
        "report": str(report_path),
    }


def _markdown_cell(value: Any) -> str:
    return "" if value is None else str(value)


def render_codelist_markdown_report(result: dict[str, Any]) -> str:
    metadata = result["raw_metadata"]
    rows: list[str] = []
    for concept, entry in result["codelists"].items():
        for code, code_info in entry["codes"].items():
            rows.append(
                f"| {concept} | {code} | {_markdown_cell(code_info['label'])} | {_markdown_cell(code_info['description'])} |"
            )
    if not rows:
        rows.append("| _none_ | _none_ | _none_ | _none_ |")
    limitations = "\n".join(f"- {item}" for item in result["limitations"])
    row_lines = "\n".join(rows)
    return f"""# OECD/SDMX codelist and label enrichment

## Result

- Source: {result['source_code']} — {result['source_name']}
- Provider dataset code: `{result['provider_dataset_code']}`
- Endpoint: `{metadata['endpoint']}`
- Content type: `{metadata['content_type']}`
- Raw bytes: {metadata['bytes']}
- Raw SHA-256: `{metadata['sha256']}`
- Scope boundary: No PostgreSQL schema change, no live `macro` database write, and not a generalized SDMX/source framework.

## Bounded labels

| concept | code | label | description |
| --- | --- | --- | --- |
{row_lines}

## Limitations

{limitations}
"""


def write_project_codelist_artifacts(
    raw_payload: str | bytes,
    *,
    project_root: str | Path,
    endpoint: str = DEFAULT_STRUCTURE_ENDPOINT,
    content_type: str = DEFAULT_STRUCTURE_CONTENT_TYPE,
) -> dict[str, str]:
    project = Path(project_root)
    raw_path = project / "data" / "raw" / "oecd_sdmx" / DEFAULT_STRUCTURE_RAW_FILENAME
    normalized_path = project / "data" / "metadata" / "oecd_sdmx" / DEFAULT_CODELIST_LABELS_FILENAME
    report_path = project / "artifacts" / "reports" / DEFAULT_CODELIST_REPORT_FILENAME

    raw_path.parent.mkdir(parents=True, exist_ok=True)
    normalized_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    raw_bytes = _coerce_payload(raw_payload)
    raw_path.write_bytes(raw_bytes)
    result = parse_codelist_labels(
        raw_bytes,
        endpoint=endpoint,
        content_type=content_type,
        artifact_path=raw_path,
    )
    _write_json(normalized_path, result)
    report_path.write_text(render_codelist_markdown_report(result), encoding="utf-8")
    return {
        "raw_structure_artifact": str(raw_path),
        "normalized_labels": str(normalized_path),
        "report": str(report_path),
    }


def fetch_payload(endpoint: str = DEFAULT_ENDPOINT, *, timeout: float = 30.0) -> tuple[bytes, str]:
    """Fetch public OECD SDMX XML without credentials.

    Kept separate so tests can exercise parsing without network access.
    """
    request = urllib.request.Request(
        endpoint,
        headers={
            "Accept": DEFAULT_CONTENT_TYPE,
            "User-Agent": DEFAULT_USER_AGENT,
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        content_type = response.headers.get("content-type", DEFAULT_CONTENT_TYPE)
        return response.read(), content_type


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="MacroForge OECD/SDMX smoke evidence utilities")
    parser.add_argument("--input-xml", help="read observation XML from an existing fixture/artifact instead of fetching")
    parser.add_argument("--input-structure-xml", help="read SDMX structure/codelist XML from an existing fixture/artifact")
    parser.add_argument("--output-root", default=".", help="write generic raw/metadata/reports directories under this root")
    parser.add_argument("--project-root", help="write MacroForge project-layout data/raw, data/metadata, and artifacts/reports outputs")
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    parser.add_argument("--structure-endpoint", default=DEFAULT_STRUCTURE_ENDPOINT)
    parser.add_argument("--territory", action="append", dest="territories", help="REF_AREA code to keep; repeatable")
    parser.add_argument("--measure", action="append", dest="measures", help="MEASURE code to keep; repeatable")
    parser.add_argument("--fetch", action="store_true", help="fetch the public no-key OECD observation endpoint")
    parser.add_argument("--write-codelist-labels", action="store_true", help="write bounded codelist label artifacts from --input-structure-xml")
    args = parser.parse_args(argv)

    if args.write_codelist_labels:
        if not args.input_structure_xml:
            parser.error("provide --input-structure-xml with --write-codelist-labels")
        if not args.project_root:
            parser.error("provide --project-root with --write-codelist-labels")
        payload = Path(args.input_structure_xml).read_bytes()
        paths = write_project_codelist_artifacts(
            payload,
            project_root=args.project_root,
            endpoint=args.structure_endpoint,
        )
        print(json.dumps(paths, indent=2, sort_keys=True))
        return 0

    if args.input_xml:
        payload = Path(args.input_xml).read_bytes()
        content_type = DEFAULT_CONTENT_TYPE
    elif args.fetch:
        payload, content_type = fetch_payload(args.endpoint)
    else:
        parser.error("provide --input-xml, --fetch, or --write-codelist-labels")

    territory_codes: list[str] = args.territories or list(DEFAULT_TERRITORY_CODES)
    measure_codes: list[str] = args.measures or list(DEFAULT_MEASURE_CODES)

    if args.project_root:
        paths = write_project_smoke_artifacts(
            payload,
            project_root=args.project_root,
            endpoint=args.endpoint,
            content_type=content_type,
            territory_codes=territory_codes,
            measure_codes=measure_codes,
        )
    else:
        paths = write_smoke_artifacts(
            payload,
            output_root=args.output_root,
            endpoint=args.endpoint,
            content_type=content_type,
            territory_codes=territory_codes,
            measure_codes=measure_codes,
        )
    print(json.dumps(paths, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
