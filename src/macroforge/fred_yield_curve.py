from __future__ import annotations

import csv
from io import StringIO
from typing import Any

from macroforge.observed_ingestion import ObservedIngestionPackage, ObservedObservation, canonical_attribute_hash

SOURCE_CODE = "FRED_YIELD_CURVE"
SOURCE_NAME = "FRED bounded monthly U.S. Treasury yield curve evidence slice"
SOURCE_HOME_URL = "https://fred.stlouisfed.org/"
PROVIDER_DATASET_CODE = "FRED:GS1M_GS1_GS10_GS30"
TERRITORY_CODE = "USA"
TERRITORY_LABEL = "United States"
UNIT_CODE = "PERCENT"
UNIT_LABEL = "Percent"
CURVE_NAME = "Monthly U.S. Treasury constant maturity yield curve"

TENOR_METADATA: dict[str, dict[str, int | str | None]] = {
    "GS1M": {"label": "1 month constant maturity", "months": 1, "years": None},
    "GS1": {"label": "1 year constant maturity", "months": 12, "years": 1},
    "GS10": {"label": "10 year constant maturity", "months": 120, "years": 10},
    "GS30": {"label": "30 year constant maturity", "months": 360, "years": 30},
}


def normalize_fred_yield_curve_fixture(
    raw_csv: str,
    *,
    raw_artifact_path: str,
    raw_sha256: str,
    source_url: str,
    selected_periods: tuple[str, ...] | list[str],
    selected_tenors: tuple[str, ...] | list[str],
) -> dict[str, Any]:
    """Normalize the bounded TASK-065 FRED yield-curve fixture without broad support."""

    selected_period_list = list(selected_periods)
    selected_tenor_list = list(selected_tenors)
    _validate_selected_tenors(selected_tenor_list)
    csv_rows = list(csv.DictReader(StringIO(raw_csv)))
    rows: list[dict[str, Any]] = []
    for csv_row in csv_rows:
        provider_period_code = _monthly_period_code(csv_row["observation_date"])
        if provider_period_code.replace("-M", "-") not in selected_period_list:
            continue
        for tenor_code in selected_tenor_list:
            rows.append(_normalize_curve_point(csv_row, provider_period_code, tenor_code))

    rows.sort(key=lambda row: (row["provider_period_code"], _tenor_sort_key(row["tenor_code"])))
    return {
        "source_code": SOURCE_CODE,
        "source_url": source_url,
        "raw_artifact_path": raw_artifact_path,
        "raw_sha256": raw_sha256,
        "provider_dataset_code": PROVIDER_DATASET_CODE,
        "observation_family": "financial_market_curve",
        "territory_code": TERRITORY_CODE,
        "territory_label": TERRITORY_LABEL,
        "frequency": "M",
        "selected_periods": selected_period_list,
        "selected_tenors": selected_tenor_list,
        "row_count": len(rows),
        "expected_row_count": len(selected_period_list) * len(selected_tenor_list),
        "input_filters": {
            "series_ids": selected_tenor_list,
            "selected_periods": selected_period_list,
            "selected_tenors": selected_tenor_list,
            "scope": "bounded TASK-065 yield-curve evidence slice",
        },
        "provider_metadata": {
            "csv_row_count": len(csv_rows),
            "csv_columns": list(csv_rows[0].keys()) if csv_rows else [],
        },
        "rows": rows,
    }


def build_fred_yield_curve_observed_package(normalized: dict[str, Any]) -> ObservedIngestionPackage:
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


def _normalize_curve_point(csv_row: dict[str, str], provider_period_code: str, tenor_code: str) -> dict[str, Any]:
    raw_value = csv_row.get(tenor_code)
    tenor = TENOR_METADATA[tenor_code]
    year, month = _year_month(provider_period_code)
    attributes = {
        "observation_family": "financial_market_curve",
        "curve_name": CURVE_NAME,
        "curve_point_role": "tenor",
        "provider_series_id": tenor_code,
        "observation_date": csv_row["observation_date"],
        "tenor_code": tenor_code,
        "tenor_label": tenor["label"],
        "tenor_months": tenor["months"],
        "tenor_years": tenor["years"],
        "source_frequency": "monthly",
    }
    return {
        "provider_indicator_code": f"FRED_YIELD:{tenor_code}",
        "provider_indicator_label": f"Market Yield on U.S. Treasury Securities — {tenor['label']}",
        "territory_code": TERRITORY_CODE,
        "territory_label": TERRITORY_LABEL,
        "provider_period_code": provider_period_code,
        "observation_date": csv_row["observation_date"],
        "frequency": "M",
        "period_year": year,
        "period_month": month,
        "unit_code": UNIT_CODE,
        "unit_label": UNIT_LABEL,
        "value": _parse_value(raw_value),
        "observation_status": "missing" if raw_value in {None, ""} else "observed",
        "decimal_precision": _decimal_precision(raw_value),
        "tenor_code": tenor_code,
        "tenor_label": tenor["label"],
        "tenor_months": tenor["months"],
        "tenor_years": tenor["years"],
        "attributes": attributes,
        "source_payload": {
            "observation_date": csv_row["observation_date"],
            tenor_code: raw_value,
        },
    }


def _monthly_period_code(observation_date: str) -> str:
    year, month, day = observation_date.split("-")
    if day != "01":
        raise ValueError(f"expected FRED monthly first-day observation date, got {observation_date}")
    return f"{year}-M{month}"


def _year_month(provider_period_code: str) -> tuple[int, int]:
    year_text, month_text = provider_period_code.split("-M", 1)
    return int(year_text), int(month_text)


def _parse_value(value: Any) -> float | None:
    if value in {None, "", "."}:
        return None
    return float(str(value).replace(",", ""))


def _decimal_precision(value: Any) -> int | None:
    if value is None or "." not in str(value):
        return None
    return len(str(value).split(".", 1)[1])


def _validate_selected_tenors(selected_tenors: list[str]) -> None:
    unknown = [tenor for tenor in selected_tenors if tenor not in TENOR_METADATA]
    if unknown:
        raise ValueError(f"unsupported FRED yield-curve tenor(s): {unknown}")


def _tenor_sort_key(tenor_code: str) -> int:
    months = TENOR_METADATA[tenor_code]["months"]
    if not isinstance(months, int):
        raise ValueError(f"invalid tenor month metadata for {tenor_code}")
    return months


def _release_key(normalized: dict[str, Any]) -> str:
    periods = "_".join(period.replace("-", "-M") if "-M" not in period else period for period in normalized["selected_periods"])
    return f"FRED_YIELD_CURVE:{periods}:{normalized['raw_sha256'][:12]}"
