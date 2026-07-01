from __future__ import annotations

import json
from decimal import Decimal
from itertools import product
from typing import Any

from macroforge.observed_ingestion import ObservedIngestionPackage, ObservedObservation, canonical_attribute_hash

SOURCE_CODE = "EUROSTAT_INPUT_OUTPUT"
SOURCE_NAME = "Eurostat bounded symmetric input-output matrix evidence slice"
SOURCE_HOME_URL = "https://ec.europa.eu/eurostat/"
PROVIDER_DATASET_CODE = "naio_10_cp1700"
FREQUENCY = "A"
SCOPE = "bounded TASK-062 Eurostat input-output matrix evidence slice"
EXPECTED_GEOS = ("DE", "FR")
EXPECTED_PERIODS = ("2020",)
EXPECTED_UNIT = "MIO_EUR"
EXPECTED_STOCK_FLOWS = ("IMP", "DOM")
EXPECTED_PRODUCTS = ("CPA_A01", "CPA_C10-12")
EXPECTED_DIMENSION_ORDER = ("freq", "unit", "stk_flow", "prd_use", "prd_ava", "geo", "time")
EXPECTED_ROW_COUNT = len(EXPECTED_GEOS) * len(EXPECTED_PERIODS) * len(EXPECTED_STOCK_FLOWS) * len(EXPECTED_PRODUCTS) * len(EXPECTED_PRODUCTS)


def normalize_eurostat_input_output_fixture(
    raw_payload: str | bytes,
    *,
    raw_artifact_path: str,
    raw_sha256: str,
    content_type: str,
) -> dict[str, Any]:
    """Normalize only the bounded TASK-062 Eurostat input-output matrix fixture."""

    wrapper = json.loads(_coerce_payload(raw_payload))
    if not isinstance(wrapper, dict):
        raise ValueError("TASK-062 Eurostat input-output fixture must be a JSON object")
    dataset_code = str(wrapper.get("dataset_code"))
    if dataset_code != PROVIDER_DATASET_CODE:
        raise ValueError(f"unexpected Eurostat input-output dataset: {dataset_code}")
    response = wrapper.get("response")
    if not isinstance(response, dict):
        raise ValueError("TASK-062 Eurostat input-output fixture must contain response object")

    ids = tuple(response.get("id", ()))
    sizes = tuple(response.get("size", ()))
    if ids != EXPECTED_DIMENSION_ORDER:
        raise ValueError(f"unexpected Eurostat input-output dimension order: {ids}")
    if len(sizes) != len(ids):
        raise ValueError("Eurostat input-output size vector must match dimension id vector")

    categories = {dimension_id: _dimension_categories(response, dimension_id) for dimension_id in ids}
    _validate_scope(categories)

    value_by_index = response.get("value")
    if not isinstance(value_by_index, dict):
        raise ValueError("Eurostat input-output response must contain JSON-stat value object")

    rows = []
    for stk_flow, prd_use, prd_ava, geo, period in product(
        EXPECTED_STOCK_FLOWS,
        EXPECTED_PRODUCTS,
        EXPECTED_PRODUCTS,
        EXPECTED_GEOS,
        EXPECTED_PERIODS,
    ):
        coords = {
            "freq": FREQUENCY,
            "unit": EXPECTED_UNIT,
            "stk_flow": stk_flow,
            "prd_use": prd_use,
            "prd_ava": prd_ava,
            "geo": geo,
            "time": period,
        }
        flat_index = _flat_index(ids=ids, sizes=sizes, categories=categories, coords=coords)
        raw_value = value_by_index.get(str(flat_index))
        rows.append(_normalize_cell(response, coords=coords, flat_index=flat_index, raw_value=raw_value, categories=categories))

    rows.sort(key=lambda row: (row["provider_period_code"], row["stock_flow_code"], row["product_used_code"], row["product_available_code"], row["territory_code"]))
    periods = sorted({row["provider_period_code"] for row in rows})
    period_range = f"{periods[0]}-{periods[-1]}" if periods else "unknown"
    return {
        "source_code": SOURCE_CODE,
        "source_url": str(wrapper.get("url")),
        "content_type": content_type,
        "raw_artifact_path": raw_artifact_path,
        "raw_sha256": raw_sha256,
        "provider_dataset_code": PROVIDER_DATASET_CODE,
        "dataset_label": str(response.get("label")),
        "frequency": FREQUENCY,
        "period_range": period_range,
        "row_count": len(rows),
        "expected_row_count": EXPECTED_ROW_COUNT,
        "matrix_shape": {
            "stock_flows": list(EXPECTED_STOCK_FLOWS),
            "products_used": list(EXPECTED_PRODUCTS),
            "products_available": list(EXPECTED_PRODUCTS),
            "geographies": list(EXPECTED_GEOS),
            "periods": list(EXPECTED_PERIODS),
        },
        "input_filters": {
            "dataset_code": PROVIDER_DATASET_CODE,
            "freq": FREQUENCY,
            "unit": EXPECTED_UNIT,
            "stk_flow": list(EXPECTED_STOCK_FLOWS),
            "prd_use": list(EXPECTED_PRODUCTS),
            "prd_ava": list(EXPECTED_PRODUCTS),
            "geo": list(EXPECTED_GEOS),
            "time": list(EXPECTED_PERIODS),
            "matrix_shape": "product_by_product",
            "scope": SCOPE,
        },
        "provider_metadata": {
            "provider": "Eurostat",
            "api_surface": "Eurostat dissemination statistics API JSON-stat",
            "source": response.get("source"),
            "updated": response.get("updated"),
            "dimension_order": list(ids),
            "dimension_sizes": list(sizes),
            "dataset_label": response.get("label"),
        },
        "rows": rows,
    }


def build_eurostat_input_output_observed_package(normalized: dict[str, Any]) -> ObservedIngestionPackage:
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


def _dimension_categories(response: dict[str, Any], dimension_id: str) -> dict[str, Any]:
    dimension = response.get("dimension", {}).get(dimension_id)
    if not isinstance(dimension, dict):
        raise ValueError(f"missing Eurostat dimension {dimension_id}")
    category = dimension.get("category")
    if not isinstance(category, dict):
        raise ValueError(f"missing Eurostat category metadata for {dimension_id}")
    indexes = category.get("index")
    labels = category.get("label", {})
    if not isinstance(indexes, dict):
        raise ValueError(f"missing Eurostat category indexes for {dimension_id}")
    if not isinstance(labels, dict):
        labels = {}
    return {"index": indexes, "label": labels}


def _validate_scope(categories: dict[str, dict[str, Any]]) -> None:
    expected = {
        "freq": (FREQUENCY,),
        "unit": (EXPECTED_UNIT,),
        "stk_flow": EXPECTED_STOCK_FLOWS,
        "prd_use": EXPECTED_PRODUCTS,
        "prd_ava": EXPECTED_PRODUCTS,
        "geo": EXPECTED_GEOS,
        "time": EXPECTED_PERIODS,
    }
    for dimension_id, expected_codes in expected.items():
        actual_codes = tuple(sorted(categories[dimension_id]["index"], key=lambda code: categories[dimension_id]["index"][code]))
        if actual_codes != expected_codes:
            raise ValueError(f"unexpected Eurostat {dimension_id} scope: {actual_codes}")


def _flat_index(*, ids: tuple[str, ...], sizes: tuple[int, ...], categories: dict[str, dict[str, Any]], coords: dict[str, str]) -> int:
    index = 0
    for dimension_id, size in zip(ids, sizes, strict=True):
        coord = categories[dimension_id]["index"][coords[dimension_id]]
        index = index * int(size) + int(coord)
    return index


def _normalize_cell(
    response: dict[str, Any],
    *,
    coords: dict[str, str],
    flat_index: int,
    raw_value: Any,
    categories: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    unit_code = coords["unit"]
    stock_flow_code = coords["stk_flow"]
    product_used_code = coords["prd_use"]
    product_available_code = coords["prd_ava"]
    territory_code = coords["geo"]
    period = coords["time"]
    unit_label = _label(categories, "unit", unit_code)
    stock_flow_label = _label(categories, "stk_flow", stock_flow_code)
    product_used_label = _label(categories, "prd_use", product_used_code)
    product_available_label = _label(categories, "prd_ava", product_available_code)
    territory_label = _label(categories, "geo", territory_code)
    value = _number_value(raw_value)
    attributes = {
        "source_provider": "Eurostat",
        "dataset_code": PROVIDER_DATASET_CODE,
        "dataset_label": str(response.get("label")),
        "matrix_role": "product_by_product_input_output_cell",
        "stock_flow_code": stock_flow_code,
        "stock_flow_label": stock_flow_label,
        "product_available_code": product_available_code,
        "product_available_label": product_available_label,
        "product_used_code": product_used_code,
        "product_used_label": product_used_label,
        "jsonstat_flat_index": flat_index,
        "jsonstat_dimension_order": list(EXPECTED_DIMENSION_ORDER),
    }
    provider_indicator_code = f"{PROVIDER_DATASET_CODE}:{stock_flow_code}:{product_available_code}->{product_used_code}"
    provider_indicator_label = f"{stock_flow_label}: {product_available_label} available to {product_used_label}"
    return {
        "provider_indicator_code": provider_indicator_code,
        "provider_indicator_label": provider_indicator_label,
        "territory_code": territory_code,
        "territory_label": territory_label,
        "provider_period_code": period,
        "frequency": FREQUENCY,
        "period_year": int(period),
        "unit_code": unit_code,
        "unit_label": unit_label,
        "value": value,
        "observation_status": "missing" if value is None else "observed",
        "decimal_precision": _decimal_precision(value),
        "stock_flow_code": stock_flow_code,
        "product_used_code": product_used_code,
        "product_available_code": product_available_code,
        "matrix_role": "product_by_product_input_output_cell",
        "attributes": attributes,
        "source_payload": {
            "flat_index": flat_index,
            "dimensions": dict(coords),
            "raw_value": raw_value,
        },
    }


def _label(categories: dict[str, dict[str, Any]], dimension_id: str, code: str) -> str:
    return str(categories[dimension_id]["label"].get(code, code))


def _number_value(value: Any) -> int | float | None:
    if value is None:
        return None
    if isinstance(value, bool):
        raise ValueError("Eurostat input-output values must be numeric, not boolean")
    if isinstance(value, int):
        return value
    if isinstance(value, float):
        return value
    decimal = Decimal(str(value))
    if decimal == decimal.to_integral_value():
        return int(decimal)
    return float(decimal)


def _decimal_precision(value: int | float | None) -> int | None:
    if value is None:
        return None
    decimal = Decimal(str(value))
    exponent = decimal.as_tuple().exponent
    if not isinstance(exponent, int):
        return 0
    return max(0, -exponent)


def _release_key(normalized: dict[str, Any]) -> str:
    return f"{SOURCE_CODE}:{normalized['provider_dataset_code']}:{normalized['period_range']}:{normalized['raw_sha256'][:12]}"
