from __future__ import annotations

from typing import Any

from macroforge.observed_ingestion import ObservedIngestionPackage, ObservedObservation, canonical_attribute_hash

SOURCE_CODE = "BEA_NIPA"
SOURCE_NAME = "U.S. Bureau of Economic Analysis NIPA bounded table evidence slice"
SOURCE_HOME_URL = "https://www.bea.gov/data/gdp/gross-domestic-product"
PROVIDER_DATASET_CODE = "NIPA:T10101"
TABLE_ID = "T10101"
TABLE_KEY = "1"
TABLE_TITLE = "Table 1.1.1. Percent Change From Preceding Period in Real Gross Domestic Product"
TERRITORY_CODE = "USA"
TERRITORY_LABEL = "United States"
UNIT_CODE = "PERCENT_SAAR"
UNIT_LABEL = "Percent, seasonally adjusted at annual rates"


def normalize_bea_nipa_itable_fixture(
    raw: dict[str, Any],
    *,
    raw_artifact_path: str,
    raw_sha256: str,
    source_url: str,
) -> dict[str, Any]:
    """Normalize the bounded TASK-053 BEA NIPA iTable fixture without broad BEA support."""

    table_prompt = _table_prompt(raw)
    prompt_data = table_prompt["PromtData"]
    table = _decode_table(prompt_data)
    _validate_bounded_table(table)

    header_years = table["Data_Rows"][0]
    header_quarters = table["Data_Rows"][1]
    rows = []
    for source_row in table["Data_Rows"][2:]:
        line_cell = source_row[0]
        stub_cell = source_row[1]
        line_number = str(line_cell["CV"])
        line_description = str(stub_cell["CV"])
        for column_index, value_cell in enumerate(source_row[2:], start=2):
            period_year = int(header_years[column_index]["CV"])
            quarter = _quarter_number(str(header_quarters[column_index]["CV"]))
            period = f"{period_year}-Q{quarter}"
            value = _parse_value(value_cell.get("CV"))
            attributes = {
                "bea_table_id": TABLE_ID,
                "bea_table_key": TABLE_KEY,
                "bea_line_number": line_number,
                "bea_line_description": line_description,
                "cell_style": value_cell.get("CS"),
                "indent_level": line_cell.get("IL"),
                "release_description": table["Description"],
                "section_name": _section_name(raw),
                "sub_title": table["Sub_Title"],
            }
            rows.append(
                {
                    "table_id": TABLE_ID,
                    "table_title": table["Title"],
                    "line_number": line_number,
                    "line_description": line_description,
                    "indicator_code": f"{TABLE_ID}:L{line_number}",
                    "territory_code": TERRITORY_CODE,
                    "territory_label": TERRITORY_LABEL,
                    "provider_period_code": period,
                    "frequency": "Q",
                    "period_year": period_year,
                    "period_quarter": quarter,
                    "unit_code": UNIT_CODE,
                    "unit_label": UNIT_LABEL,
                    "value": value,
                    "observation_status": "missing" if value is None else "observed",
                    "decimal_precision": _decimal_precision(value_cell.get("CV")),
                    "attributes": attributes,
                    "source_payload": {
                        "line_cell": dict(line_cell),
                        "stub_cell": dict(stub_cell),
                        "year_cell": dict(header_years[column_index]),
                        "quarter_cell": dict(header_quarters[column_index]),
                        "value_cell": dict(value_cell),
                    },
                }
            )

    period_range = f"{rows[0]['provider_period_code']}-{rows[-1]['provider_period_code']}" if rows else "unknown"
    input_filters = {
        "appid": 19,
        "category": "Survey",
        "table_key": TABLE_KEY,
        "table_id": TABLE_ID,
        "series": "Q",
        "scope": "bounded TASK-053 architectural experiment",
    }
    return {
        "source_code": SOURCE_CODE,
        "source_url": source_url,
        "raw_artifact_path": raw_artifact_path,
        "raw_sha256": raw_sha256,
        "provider_dataset_code": PROVIDER_DATASET_CODE,
        "table_id": TABLE_ID,
        "table_key": TABLE_KEY,
        "table_title": table["Title"],
        "release_description": table["Description"],
        "frequency": "Q",
        "period_range": period_range,
        "row_count": len(rows),
        "expected_row_count": len(rows),
        "input_filters": input_filters,
        "rows": rows,
    }


def build_bea_nipa_observed_package(normalized: dict[str, Any]) -> ObservedIngestionPackage:
    observations = []
    for row in normalized["rows"]:
        attributes = dict(row["attributes"])
        observations.append(
            ObservedObservation(
                provider_indicator_code=row["indicator_code"],
                provider_indicator_label=row["line_description"],
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
            "release_description": normalized["release_description"],
        },
        input_filters=dict(normalized["input_filters"]),
        row_count=int(normalized["row_count"]),
        expected_row_count=int(normalized["expected_row_count"]),
        observations=tuple(observations),
    )


def _table_prompt(raw: dict[str, Any]) -> dict[str, Any]:
    steps = raw.get("Steps", [])
    if len(steps) < 3 or steps[2].get("Name") != "Interactive Data":
        raise ValueError("TASK-053 BEA fixture must include Interactive Data step")
    prompts = steps[2].get("Prompts", [])
    for prompt in prompts:
        if prompt.get("Name") == "TheTable" and prompt.get("UIControl") == "Table":
            return prompt
    raise ValueError("TASK-053 BEA fixture must include TheTable prompt")


def _decode_table(prompt_data: str) -> dict[str, Any]:
    import json

    decoded = json.loads(prompt_data)
    return json.loads(decoded["Table"])


def _validate_bounded_table(table: dict[str, Any]) -> None:
    if table.get("iTable_DescriptorKey") != TABLE_KEY:
        raise ValueError("TASK-053 BEA fixture must use NIPA table key 1")
    if table.get("Title") != TABLE_TITLE:
        raise ValueError("TASK-053 BEA fixture must use BEA NIPA T10101")
    if table.get("Sub_Title") != "[Percent] Seasonally adjusted at annual rates":
        raise ValueError("TASK-053 BEA fixture must use percent SAAR subtitle")
    rows = table.get("Data_Rows", [])
    if len(rows) < 3:
        raise ValueError("TASK-053 BEA fixture must include header and data rows")


def _section_name(raw: dict[str, Any]) -> str:
    table_list_prompt = raw["Steps"][1]["Prompts"][0]
    table_rows = __import__("json").loads(table_list_prompt["PromtData"])["Table"]
    for row in table_rows:
        if str(row.get("TableKey")) == TABLE_KEY:
            return str(row["SectionName"])
    return "unknown"


def _quarter_number(value: str) -> int:
    if len(value) != 2 or not value.startswith("Q"):
        raise ValueError(f"unsupported BEA quarterly period: {value}")
    quarter = int(value[1:])
    if quarter not in {1, 2, 3, 4}:
        raise ValueError(f"unsupported BEA quarterly period: {value}")
    return quarter


def _parse_value(value: Any) -> float | None:
    text = str(value).strip()
    if text in {"", "---"}:
        return None
    return float(text.replace(",", ""))


def _decimal_precision(value: Any) -> int | None:
    text = str(value).strip()
    if text in {"", "---"} or "." not in text:
        return None
    return len(text.split(".", 1)[1])


def _release_key(normalized: dict[str, Any]) -> str:
    return f"BEA_NIPA:{normalized['table_id']}:{normalized['period_range']}:{normalized['raw_sha256'][:12]}"
