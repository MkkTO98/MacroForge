from __future__ import annotations

from dataclasses import dataclass

from macroforge.observed_ingestion import (
    EMPTY_ATTRIBUTE_HASH,
    ObservedIngestionPackage,
    ObservedObservation,
    canonical_attribute_hash,
    observed_package_fingerprint,
)


@dataclass(frozen=True)
class ContractDriftIssue:
    """Deterministic issue describing divergence from ObservedIngestionPackage v1."""

    code: str
    path: str
    message: str


@dataclass(frozen=True)
class ContractDriftReport:
    """Deterministic contract-drift report for one observed package."""

    source_code: str
    valid: bool
    fingerprint: str
    recomputed_fingerprint: str
    issues: tuple[ContractDriftIssue, ...]


def validate_observed_package_contract(package: ObservedIngestionPackage) -> ContractDriftReport:
    """Detect drift from the verified ObservedIngestionPackage v1 contract.

    This is a narrow invariant specification for current WDI/OECD/Eurostat
    package behavior. It does not validate economic correctness and does not
    repair drift.
    """

    issues: list[ContractDriftIssue] = []
    issues.extend(_package_issues(package))
    for index, observation in enumerate(package.observations):
        issues.extend(_observation_issues(index, observation))

    fingerprint = observed_package_fingerprint(package)
    recomputed_fingerprint = observed_package_fingerprint(package)
    if fingerprint != recomputed_fingerprint:
        issues.append(
            ContractDriftIssue(
                code="non_reproducible_fingerprint",
                path="package.fingerprint",
                message="observed package fingerprint must be reproducible",
            )
        )

    return ContractDriftReport(
        source_code=package.source_code,
        valid=not issues,
        fingerprint=fingerprint,
        recomputed_fingerprint=recomputed_fingerprint,
        issues=tuple(issues),
    )


def _package_issues(package: ObservedIngestionPackage) -> tuple[ContractDriftIssue, ...]:
    issues: list[ContractDriftIssue] = []
    for field_name in ["source_code", "source_name", "provider_dataset_code", "release_key"]:
        if _is_empty_string(getattr(package, field_name)):
            issues.append(
                ContractDriftIssue(
                    code="missing_required_package_field",
                    path=f"package.{field_name}",
                    message="required package field is empty",
                )
            )

    if not isinstance(package.raw_evidence, dict):
        issues.append(
            ContractDriftIssue(
                code="invalid_raw_evidence",
                path="package.raw_evidence",
                message="raw_evidence must be a source-specific dictionary",
            )
        )
    if not isinstance(package.input_filters, dict):
        issues.append(
            ContractDriftIssue(
                code="invalid_input_filters",
                path="package.input_filters",
                message="input_filters must be a source-specific dictionary",
            )
        )
    if package.row_count != len(package.observations):
        issues.append(
            ContractDriftIssue(
                code="row_count_mismatch",
                path="package.row_count",
                message="row_count must equal observation count",
            )
        )
    if package.expected_row_count < 0:
        issues.append(
            ContractDriftIssue(
                code="invalid_expected_row_count",
                path="package.expected_row_count",
                message="expected_row_count must be non-negative",
            )
        )
    return tuple(issues)


def _observation_issues(index: int, observation: ObservedObservation) -> tuple[ContractDriftIssue, ...]:
    issues: list[ContractDriftIssue] = []
    base_path = f"package.observations[{index}]"
    for field_name in [
        "provider_indicator_code",
        "provider_territory_code",
        "provider_period_code",
        "frequency",
        "unit_code",
        "observation_status",
        "attribute_hash",
    ]:
        if _is_empty_string(getattr(observation, field_name)):
            issues.append(
                ContractDriftIssue(
                    code="missing_required_observation_field",
                    path=f"{base_path}.{field_name}",
                    message="required observation field is empty",
                )
            )

    if observation.frequency not in {"A", "Q", "M"}:
        issues.append(
            ContractDriftIssue(
                code="unsupported_frequency",
                path=f"{base_path}.frequency",
                message="current contract supports only A, Q, or M frequency",
            )
        )
    if observation.period_year is None:
        issues.append(
            ContractDriftIssue(
                code="missing_period_year",
                path=f"{base_path}.period_year",
                message="supported observations require period_year",
            )
        )
    if not isinstance(observation.attributes, dict):
        issues.append(
            ContractDriftIssue(
                code="invalid_attributes",
                path=f"{base_path}.attributes",
                message="attributes must be a dictionary",
            )
        )
    elif observation.attribute_hash != _expected_attribute_hash(observation.attributes):
        issues.append(
            ContractDriftIssue(
                code="invalid_attribute_hash",
                path=f"{base_path}.attribute_hash",
                message="attribute_hash must match canonical hash for observation attributes",
            )
        )
    if not isinstance(observation.source_payload, dict):
        issues.append(
            ContractDriftIssue(
                code="invalid_source_payload",
                path=f"{base_path}.source_payload",
                message="source_payload must be a source-specific dictionary",
            )
        )
    if observation.frequency == "A" and observation.period_quarter is not None:
        issues.append(
            ContractDriftIssue(
                code="unexpected_quarter",
                path=f"{base_path}.period_quarter",
                message="annual observations must not set period_quarter",
            )
        )
    if observation.frequency == "A" and observation.period_month is not None:
        issues.append(
            ContractDriftIssue(
                code="unexpected_month",
                path=f"{base_path}.period_month",
                message="annual observations must not set period_month",
            )
        )
    if observation.frequency == "Q" and observation.period_quarter not in {1, 2, 3, 4}:
        issues.append(
            ContractDriftIssue(
                code="invalid_quarter",
                path=f"{base_path}.period_quarter",
                message="quarterly observations require quarter 1-4",
            )
        )
    if observation.frequency == "Q" and observation.period_month is not None:
        issues.append(
            ContractDriftIssue(
                code="unexpected_month",
                path=f"{base_path}.period_month",
                message="quarterly observations must not set period_month",
            )
        )
    if observation.frequency == "M" and observation.period_quarter is not None:
        issues.append(
            ContractDriftIssue(
                code="unexpected_quarter",
                path=f"{base_path}.period_quarter",
                message="monthly observations must not set period_quarter",
            )
        )
    if observation.frequency == "M" and observation.period_month not in set(range(1, 13)):
        issues.append(
            ContractDriftIssue(
                code="invalid_month",
                path=f"{base_path}.period_month",
                message="monthly observations require month 1-12",
            )
        )
    return tuple(issues)


def _expected_attribute_hash(attributes: dict) -> str:
    if attributes == {}:
        return EMPTY_ATTRIBUTE_HASH
    return canonical_attribute_hash(attributes)


def _is_empty_string(value: object) -> bool:
    return not isinstance(value, str) or value.strip() == ""
