from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass
from typing import Any

EMPTY_ATTRIBUTE_HASH = "empty"
UNKNOWN_UNIT_CODE = "unknown"


@dataclass(frozen=True)
class ObservedObservation:
    """Canonical-load-ready observation values extracted from existing source rows."""

    provider_indicator_code: str
    provider_indicator_label: str | None
    provider_territory_code: str
    provider_territory_label: str | None
    provider_period_code: str
    frequency: str
    unit_code: str
    value: Any
    observation_status: str
    attributes: dict[str, Any]
    source_payload: dict[str, Any]
    attribute_hash: str
    period_year: int | None = None
    period_quarter: int | None = None
    unit_label: str | None = None
    decimal_precision: int | None = None


@dataclass(frozen=True)
class ObservedIngestionPackage:
    """Shared source-normalized handoff observed in current WDI/OECD/Eurostat loaders."""

    source_code: str
    source_name: str
    source_home_url: str | None
    provider_dataset_code: str
    release_key: str
    raw_evidence: dict[str, Any]
    input_filters: dict[str, Any]
    row_count: int
    expected_row_count: int
    observations: tuple[ObservedObservation, ...]


@dataclass(frozen=True)
class ObservedPackageComparison:
    """Deterministic replay/equivalence diagnostic for two observed packages."""

    equivalent: bool
    left_fingerprint: str
    right_fingerprint: str
    row_count_match: bool
    expected_row_count_match: bool
    observation_count_match: bool
    differing_observations: tuple[dict[str, Any], ...]


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def observed_package_fingerprint(package: ObservedIngestionPackage) -> str:
    """Return a deterministic SHA-256 fingerprint for replaying an observed package."""

    return hashlib.sha256(_canonical_json(asdict(package)).encode("utf-8")).hexdigest()


def _observation_identity(observation: ObservedObservation) -> dict[str, Any]:
    return {
        "provider_indicator_code": observation.provider_indicator_code,
        "provider_territory_code": observation.provider_territory_code,
        "provider_period_code": observation.provider_period_code,
    }


def _changed_observation_fields(left: ObservedObservation, right: ObservedObservation) -> tuple[str, ...]:
    return tuple(
        field
        for field, value in asdict(left).items()
        if value != asdict(right)[field]
    )


def compare_observed_packages(
    left: ObservedIngestionPackage,
    right: ObservedIngestionPackage,
) -> ObservedPackageComparison:
    """Compare replayed observed packages without changing source-specific ingestion behavior."""

    differing_observations = []
    for index, (left_observation, right_observation) in enumerate(zip(left.observations, right.observations, strict=False)):
        changed_fields = _changed_observation_fields(left_observation, right_observation)
        if changed_fields:
            differing_observations.append(
                {
                    "index": index,
                    **_observation_identity(left_observation),
                    "changed_fields": changed_fields,
                }
            )

    left_fingerprint = observed_package_fingerprint(left)
    right_fingerprint = observed_package_fingerprint(right)
    observation_count_match = len(left.observations) == len(right.observations)
    return ObservedPackageComparison(
        equivalent=left_fingerprint == right_fingerprint,
        left_fingerprint=left_fingerprint,
        right_fingerprint=right_fingerprint,
        row_count_match=left.row_count == right.row_count,
        expected_row_count_match=left.expected_row_count == right.expected_row_count,
        observation_count_match=observation_count_match,
        differing_observations=tuple(differing_observations),
    )


def canonical_attribute_hash(attributes: dict[str, Any]) -> str:
    canonical = json.dumps(attributes, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _wdi_release_key(normalized: dict[str, Any]) -> str:
    last_updated = None
    if normalized.get("raw_artifacts"):
        last_updated = normalized["raw_artifacts"][0].get("source_metadata", {}).get("lastupdated")
    return f"WDI:{last_updated or 'unknown'}:{normalized.get('date_range', 'unknown')}"


def _oecd_release_key(normalized: dict[str, Any]) -> str:
    provider_dataset_code = normalized["provider_dataset_code"]
    periods = sorted({str(row["period"]) for row in normalized["rows"]})
    period_range = f"{periods[0]}-{periods[-1]}" if periods else "unknown"
    raw_sha = normalized.get("raw_metadata", {}).get("sha256", "unknown")
    return f"OECD_NAAG:{provider_dataset_code}:{period_range}:{raw_sha[:12]}"


def _eurostat_release_key(normalized: dict[str, Any]) -> str:
    raw_sha = normalized.get("raw_sha256", "unknown")
    periods = sorted({str(row["period"]) for row in normalized["rows"]})
    period_range = f"{periods[0]}-{periods[-1]}" if periods else "unknown"
    return f"EUROSTAT_NAMQ_GDP:{normalized['provider_dataset_code']}:{period_range}:{raw_sha[:12]}"


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


def build_wdi_observed_package(normalized: dict[str, Any]) -> ObservedIngestionPackage:
    release_key = _wdi_release_key(normalized)
    raw_artifacts = normalized.get("raw_artifacts", [])
    observations = []
    for row in normalized["rows"]:
        unit_code = row.get("unit") or UNKNOWN_UNIT_CODE
        observation_status = "missing" if row.get("value") is None else "observed"
        observations.append(
            ObservedObservation(
                provider_indicator_code=row["indicator_id"],
                provider_indicator_label=row.get("indicator_name"),
                provider_territory_code=row["countryiso3code"],
                provider_territory_label=row.get("country_name"),
                provider_period_code=str(row["date"]),
                frequency="A",
                period_year=int(row["date"]),
                unit_code=unit_code,
                unit_label=None,
                value=row.get("value"),
                observation_status=observation_status,
                decimal_precision=row.get("decimal"),
                attributes={},
                source_payload=dict(row),
                attribute_hash=EMPTY_ATTRIBUTE_HASH,
            )
        )
    row_count = int(normalized.get("row_count", len(observations)))
    return ObservedIngestionPackage(
        source_code="WDI",
        source_name="World Bank World Development Indicators",
        source_home_url="https://data.worldbank.org/",
        provider_dataset_code="WDI",
        release_key=release_key,
        raw_evidence={
            "source_url": "; ".join(a["url"] for a in raw_artifacts),
            "raw_artifact_path": normalized.get("support_bundle"),
            "raw_sha256": ";".join(a["sha256"] for a in raw_artifacts),
            "raw_artifacts": raw_artifacts,
        },
        input_filters={
            "countries": normalized.get("countries"),
            "indicators": normalized.get("indicators"),
            "date_range": normalized.get("date_range"),
        },
        row_count=row_count,
        expected_row_count=int(normalized.get("expected_row_count", row_count)),
        observations=tuple(observations),
    )


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
