from __future__ import annotations

from typing import Any

from macroforge.observed_ingestion import ObservedIngestionPackage, ObservedObservation, canonical_attribute_hash


def _eurostat_release_key(normalized: dict[str, Any]) -> str:
    raw_sha = normalized.get("raw_sha256", "unknown")
    periods = sorted({str(row["period"]) for row in normalized["rows"]})
    period_range = f"{periods[0]}-{periods[-1]}" if periods else "unknown"
    return f"EUROSTAT_NAMQ_GDP:{normalized['provider_dataset_code']}:{period_range}:{raw_sha[:12]}"


def _eurostat_attribute_payload(normalized: dict[str, Any], row: dict[str, Any]) -> dict[str, Any]:
    status = row.get("source_payload", {}).get("status")
    attributes: dict[str, Any] = {
        "source": "Eurostat",
        "provider_dataset_code": normalized["provider_dataset_code"],
        "freq": row["frequency"],
        "s_adj": row["seasonal_adjustment"],
        "s_adj_label": row.get("seasonal_adjustment_name"),
        "observation_status": row.get("observation_status", "observed"),
    }
    if status is not None:
        attributes["jsonstat_status"] = status
    return attributes


def build_eurostat_observed_package(normalized: dict[str, Any]) -> ObservedIngestionPackage:
    observations = []
    for row in normalized["rows"]:
        attributes = _eurostat_attribute_payload(normalized, row)
        observations.append(
            ObservedObservation(
                provider_indicator_code=row["indicator_code"],
                provider_indicator_label=row.get("indicator_name"),
                provider_territory_code=row["territory_code"],
                provider_territory_label=row.get("territory_name"),
                provider_period_code=row["period"],
                frequency=row["frequency"],
                period_year=int(row["period_year"]),
                period_quarter=int(row["period_quarter"]),
                unit_code=row["unit"],
                unit_label=row.get("unit_name"),
                value=row.get("value"),
                observation_status=row.get("observation_status", "observed"),
                decimal_precision=row.get("decimal_precision"),
                attributes=attributes,
                source_payload=dict(row.get("source_payload") or {}),
                attribute_hash=canonical_attribute_hash(attributes),
            )
        )
    row_count = int(normalized.get("row_count", len(observations)))
    provider_dataset_code = normalized["provider_dataset_code"]
    return ObservedIngestionPackage(
        source_code="EUROSTAT_NAMQ_GDP",
        source_name="Eurostat quarterly national accounts GDP",
        source_home_url="https://ec.europa.eu/eurostat/",
        provider_dataset_code=provider_dataset_code,
        release_key=_eurostat_release_key(normalized),
        raw_evidence={
            "source_url": normalized.get("source_url"),
            "raw_artifact_path": normalized.get("raw_artifact_path"),
            "raw_sha256": normalized.get("raw_sha256"),
            "raw_bytes": normalized.get("raw_bytes"),
        },
        input_filters={"filters": normalized.get("filters"), "provider_dataset_code": provider_dataset_code},
        row_count=row_count,
        expected_row_count=row_count,
        observations=tuple(observations),
    )
