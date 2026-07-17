from __future__ import annotations

from dataclasses import dataclass

from macroforge.contract_drift import ContractDriftReport, validate_observed_package_contract
from macroforge.observed_ingestion import (
    ObservedIngestionPackage,
    ObservedPackageComparison,
    compare_observed_packages,
)


@dataclass(frozen=True)
class LoadedObservedPackageContractVerification:
    """Deterministic verification evidence for one expected and reconstructed package."""

    expected_contract_report: ContractDriftReport
    loaded_contract_report: ContractDriftReport
    comparison: ObservedPackageComparison


def verify_loaded_observed_package(
    expected_package: ObservedIngestionPackage,
    loaded_package: ObservedIngestionPackage,
) -> ObservedPackageComparison:
    """Compare an expected observed package with a source-reconstructed loaded package."""

    return compare_observed_packages(expected_package, loaded_package)


def verify_loaded_observed_package_contracts(
    expected_package: ObservedIngestionPackage,
    loaded_package: ObservedIngestionPackage,
) -> LoadedObservedPackageContractVerification:
    """Validate expected and source-reconstructed packages, then compare them deterministically."""

    return LoadedObservedPackageContractVerification(
        expected_contract_report=validate_observed_package_contract(expected_package),
        loaded_contract_report=validate_observed_package_contract(loaded_package),
        comparison=compare_observed_packages(expected_package, loaded_package),
    )
