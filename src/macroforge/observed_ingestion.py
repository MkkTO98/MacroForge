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
    period_month: int | None = None
    unit_label: str | None = None
    decimal_precision: int | None = None


@dataclass(frozen=True)
class ObservedIngestionPackage:
    """Shared source-normalized handoff after source-specific acquisition and normalization."""

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
    right_fields = asdict(right)
    return tuple(field for field, value in asdict(left).items() if value != right_fields[field])


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


def build_wdi_observed_package(normalized: dict[str, Any]) -> ObservedIngestionPackage:
    """Compatibility wrapper; WDI-specific construction lives in macroforge.wdi_observed."""

    from macroforge.wdi_observed import build_wdi_observed_package as source_builder

    return source_builder(normalized)


def build_oecd_observed_package(normalized: dict[str, Any]) -> ObservedIngestionPackage:
    """Compatibility wrapper; OECD-specific construction lives in macroforge.oecd_sdmx_observed."""

    from macroforge.oecd_sdmx_observed import build_oecd_observed_package as source_builder

    return source_builder(normalized)


def build_eurostat_observed_package(normalized: dict[str, Any]) -> ObservedIngestionPackage:
    """Compatibility wrapper; Eurostat-specific construction lives in macroforge.eurostat_namq_observed."""

    from macroforge.eurostat_namq_observed import build_eurostat_observed_package as source_builder

    return source_builder(normalized)
