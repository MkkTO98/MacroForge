from __future__ import annotations

from typing import Any

from macroforge.observed_ingestion import ObservedIngestionPackage, ObservedObservation, canonical_attribute_hash


def _oecd_release_key(normalized: dict[str, Any]) -> str:
    provider_dataset_code = normalized["provider_dataset_code"]
    periods = sorted({str(row["period"]) for row in normalized["rows"]})
    period_range = f"{periods[0]}-{periods[-1]}" if periods else "unknown"
    raw_sha = normalized.get("raw_metadata", {}).get("sha256", "unknown")
    return f"OECD_NAAG:{provider_dataset_code}:{period_range}:{raw_sha[:12]}"


def _oecd_observation_status(attributes: dict[str, Any], value: Any) -> str:
    if value is None:
        return "missing"
    obs_status = str(attributes.get("OBS_STATUS", "A"))
    if obs_status in {"M", "L", "N"}:
        return "missing"
    if obs_status in {"S", "C"}:
        return "suppressed"
    return "observed"


def _oecd_decimal_precision(attributes: dict[str, Any]) -> int | None:
    decimals = attributes.get("DECIMALS")
    if decimals is None or decimals == "":
        return None
    return int(decimals)


def build_oecd_observed_package(normalized: dict[str, Any]) -> ObservedIngestionPackage:
    raw_metadata = normalized.get("raw_metadata", {})
    observations = []
    for row in normalized["rows"]:
        attributes = dict(row.get("attributes") or {})
        observations.append(
            ObservedObservation(
                provider_indicator_code=row["indicator_code"],
                provider_indicator_label=row["indicator_code"],
                provider_territory_code=row["territory_code"],
                provider_territory_label=row["territory_code"],
                provider_period_code=str(row["period"]),
                frequency=row["frequency"],
                period_year=int(row["period"]),
                unit_code=row["unit"],
                unit_label=None,
                value=row.get("value"),
                observation_status=_oecd_observation_status(attributes, row.get("value")),
                decimal_precision=_oecd_decimal_precision(attributes),
                attributes=attributes,
                source_payload=dict(row.get("source_payload", {})),
                attribute_hash=canonical_attribute_hash(attributes),
            )
        )
    row_count = int(normalized.get("row_count", len(observations)))
    provider_dataset_code = normalized["provider_dataset_code"]
    return ObservedIngestionPackage(
        source_code="OECD_NAAG",
        source_name="OECD annual national accounts / NAAG Chapter 1 GDP dataflow",
        source_home_url="https://sdmx.oecd.org/",
        provider_dataset_code=provider_dataset_code,
        release_key=_oecd_release_key(normalized),
        raw_evidence={
            "source_url": raw_metadata.get("endpoint"),
            "raw_artifact_path": raw_metadata.get("raw_artifact_path"),
            "raw_sha256": raw_metadata.get("sha256"),
            "raw_metadata": raw_metadata,
        },
        input_filters={"filters": normalized.get("filters"), "provider_dataset_code": provider_dataset_code},
        row_count=row_count,
        expected_row_count=row_count,
        observations=tuple(observations),
    )
