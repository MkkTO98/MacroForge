from __future__ import annotations

import json
from decimal import Decimal
from itertools import product
from typing import Any

from macroforge.observed_ingestion import ObservedIngestionPackage, ObservedObservation, canonical_attribute_hash

SOURCE_CODE = "EUROSTAT_ENERGY_BALANCE"
SOURCE_NAME = "Eurostat bounded complete energy balance evidence slice"
SOURCE_HOME_URL = "https://ec.europa.eu/eurostat/"
PROVIDER_DATASET_CODE = "nrg_bal_c"
FREQUENCY = "A"
SCOPE = "bounded TASK-064 Eurostat energy balance evidence slice"
EXPECTED_GEOS = ("DE", "FR")
EXPECTED_PERIODS = ("2022", "2023")
EXPECTED_UNIT = "KTOE"
EXPECTED_BALANCE_COMPONENTS = ("PPRD", "IMP", "EXP", "FC_E")
EXPECTED_ENERGY_PRODUCTS = ("TOTAL", "RA000")
EXPECTED_DIMENSION_ORDER = ("freq", "nrg_bal", "siec", "unit", "geo", "time")
EXPECTED_ROW_COUNT = len(EXPECTED_GEOS) * len(EXPECTED_PERIODS) * len(EXPECTED_BALANCE_COMPONENTS) * len(EXPECTED_ENERGY_PRODUCTS)


def normalize_eurostat_energy_balance_fixture(
    raw_payload: str | bytes,
    *,
    raw_artifact_path: str,
    raw_sha256: str,
    content_type: str,
) -> dict[str, Any]:
    """Normalize only the bounded TASK-064 Eurostat complete-energy-balance fixture."""

    wrapper = json.loads(_coerce_payload(raw_payload))
    if not isinstance(wrapper, dict):
        raise ValueError("TASK-064 Eurostat energy balance fixture must be a JSON object")
    dataset_code = str(wrapper.get("dataset_code"))
    if dataset_code != PROVIDER_DATASET_CODE:
        raise ValueError(f"unexpected Eurostat energy balance dataset: {dataset_code}")
    response = wrapper.get("response")
    if not isinstance(response, dict):
        raise ValueError("TASK-064 Eurostat energy balance fixture must contain response object")

    ids = tuple(response.get("id", ()))
    sizes = tuple(response.get("size", ()))
    if ids != EXPECTED_DIMENSION_ORDER:
        raise ValueError(f"unexpected Eurostat energy balance dimension order: {ids}")
    if len(sizes) != len(ids):
        raise ValueError("Eurostat energy balance size vector must match dimension id vector")

    categories = {dimension_id: _dimension_categories(response, dimension_id) for dimension_id in ids}
    _validate_scope(categories)

    value_by_index = response.get("value")
    if not isinstance(value_by_index, dict):
        raise ValueError("Eurostat energy balance response must contain JSON-stat value object")

    rows = []
    for balance_component, energy_product, geo, period in product(
        EXPECTED_BALANCE_COMPONENTS,
        EXPECTED_ENERGY_PRODUCTS,
        EXPECTED_GEOS,
        EXPECTED_PERIODS,
    ):
        coords = {
            "freq": FREQUENCY,
            "nrg_bal": balance_component,
            "siec": energy_product,
            "unit": EXPECTED_UNIT,
            "geo": geo,
            "time": period,
        }
        flat_index = _flat_index(ids=ids, sizes=sizes, categories=categories, coords=coords)
        raw_value = value_by_index.get(str(flat_index))
        rows.append(_normalize_cell(response, coords=coords, flat_index=flat_index, raw_value=raw_value, categories=categories))

    rows.sort(key=lambda row: (row["provider_period_code"], row["balance_component_code"], row["energy_product_code"], row["territory_code"]))
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
        "energy_accounting_shape": {
            "balance_components": list(EXPECTED_BALANCE_COMPONENTS),
            "energy_products": list(EXPECTED_ENERGY_PRODUCTS),
            "geographies": list(EXPECTED_GEOS),
            "periods": list(EXPECTED_PERIODS),
            "unit": EXPECTED_UNIT,
        },
        "input_filters": {
            "dataset_code": PROVIDER_DATASET_CODE,
            "freq": FREQUENCY,
            "unit": EXPECTED_UNIT,
            "balance_components": list(EXPECTED_BALANCE_COMPONENTS),
            "energy_products": list(EXPECTED_ENERGY_PRODUCTS),
            "geo": list(EXPECTED_GEOS),
            "time": list(EXPECTED_PERIODS),
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


def build_eurostat_energy_balance_observed_package(normalized: dict[str, Any]) -> ObservedIngestionPackage:
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
        raise ValueError(f"missing Eurostat energy balance dimension {dimension_id}")
    category = dimension.get("category")
    if not isinstance(category, dict):
        raise ValueError(f"missing Eurostat energy balance category metadata for {dimension_id}")
    indexes = category.get("index")
    labels = category.get("label", {})
    if not isinstance(indexes, dict):
        raise ValueError(f"missing Eurostat energy balance category indexes for {dimension_id}")
    if not isinstance(labels, dict):
        labels = {}
    return {"index": indexes, "label": labels}


def _validate_scope(categories: dict[str, dict[str, Any]]) -> None:
    expected = {
        "freq": (FREQUENCY,),
        "nrg_bal": EXPECTED_BALANCE_COMPONENTS,
        "siec": EXPECTED_ENERGY_PRODUCTS,
        "unit": (EXPECTED_UNIT,),
        "geo": EXPECTED_GEOS,
        "time": EXPECTED_PERIODS,
    }
    for dimension_id, expected_codes in expected.items():
        actual_codes = tuple(sorted(categories[dimension_id]["index"], key=lambda code: categories[dimension_id]["index"][code]))
        if actual_codes != expected_codes:
            raise ValueError(f"unexpected Eurostat energy balance {dimension_id} scope: {actual_codes}")


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
    balance_component_code = coords["nrg_bal"]
    energy_product_code = coords["siec"]
    unit_code = coords["unit"]
    territory_code = coords["geo"]
    period = coords["time"]
    balance_component_label = _label(categories, "nrg_bal", balance_component_code)
    energy_product_label = _label(categories, "siec", energy_product_code)
    unit_label = _label(categories, "unit", unit_code)
    territory_label = _label(categories, "geo", territory_code)
    value = _number_value(raw_value)
    attributes = {
        "source_provider": "Eurostat",
        "dataset_code": PROVIDER_DATASET_CODE,
        "dataset_label": str(response.get("label")),
        "energy_accounting_role": "energy_balance_component_by_product",
        "balance_component_code": balance_component_code,
        "balance_component_label": balance_component_label,
        "energy_product_code": energy_product_code,
        "energy_product_label": energy_product_label,
        "jsonstat_flat_index": flat_index,
        "jsonstat_dimension_order": list(EXPECTED_DIMENSION_ORDER),
    }
    provider_indicator_code = f"{PROVIDER_DATASET_CODE}:{balance_component_code}:{energy_product_code}"
    provider_indicator_label = f"{balance_component_label} — {energy_product_label}"
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
        "balance_component_code": balance_component_code,
        "energy_product_code": energy_product_code,
        "energy_accounting_role": "energy_balance_component_by_product",
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
        raise ValueError("Eurostat energy balance values must be numeric, not boolean")
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
