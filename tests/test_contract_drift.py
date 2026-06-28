from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

from macroforge.contract_drift import validate_observed_package_contract
from macroforge.observed_ingestion import (
    build_eurostat_observed_package,
    build_oecd_observed_package,
    build_wdi_observed_package,
    canonical_attribute_hash,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
WDI_NORMALIZED = PROJECT_ROOT / "data" / "metadata" / "wdi" / "wdi-smoke-normalized.json"
OECD_NORMALIZED = PROJECT_ROOT / "data" / "metadata" / "oecd_sdmx" / "oecd-sdmx-smoke-normalized.json"
EUROSTAT_NORMALIZED = PROJECT_ROOT / "data" / "metadata" / "eurostat" / "eurostat-namq-10-gdp-architecture-spike-normalized.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _supported_packages():
    return (
        build_wdi_observed_package(_load(WDI_NORMALIZED)),
        build_oecd_observed_package(_load(OECD_NORMALIZED)),
        build_eurostat_observed_package(_load(EUROSTAT_NORMALIZED)),
    )


def test_supported_observed_packages_satisfy_contract_invariants():
    reports = tuple(validate_observed_package_contract(package) for package in _supported_packages())

    assert {report.source_code for report in reports} == {"WDI", "OECD_NAAG", "EUROSTAT_NAMQ_GDP"}
    for report in reports:
        assert report.valid is True
        assert report.issues == ()
        assert report.fingerprint == report.recomputed_fingerprint
        assert len(report.fingerprint) == 64


def test_package_contract_drift_reports_deterministic_issue_codes_and_paths():
    package = build_wdi_observed_package(_load(WDI_NORMALIZED))
    drifted = replace(package, row_count=package.row_count + 1, release_key="")

    report = validate_observed_package_contract(drifted)

    assert report.valid is False
    assert [(issue.code, issue.path, issue.message) for issue in report.issues] == [
        ("missing_required_package_field", "package.release_key", "required package field is empty"),
        ("row_count_mismatch", "package.row_count", "row_count must equal observation count"),
    ]


def test_observation_contract_drift_reports_attribute_hash_and_period_invariants():
    package = build_eurostat_observed_package(_load(EUROSTAT_NORMALIZED))
    changed_observations = list(package.observations)
    changed_observations[0] = replace(
        changed_observations[0],
        provider_period_code="2023-Q0",
        period_quarter=0,
        attribute_hash=canonical_attribute_hash({"unexpected": "attributes"}),
    )
    drifted = replace(package, observations=tuple(changed_observations))

    report = validate_observed_package_contract(drifted)

    assert report.valid is False
    assert [(issue.code, issue.path, issue.message) for issue in report.issues] == [
        (
            "invalid_attribute_hash",
            "package.observations[0].attribute_hash",
            "attribute_hash must match canonical hash for observation attributes",
        ),
        ("invalid_quarter", "package.observations[0].period_quarter", "quarterly observations require quarter 1-4"),
    ]


def test_observation_contract_drift_reports_required_current_source_fields():
    package = build_oecd_observed_package(_load(OECD_NORMALIZED))
    changed_observations = list(package.observations)
    changed_observations[0] = replace(
        changed_observations[0],
        provider_indicator_code="",
        frequency="D",
        period_year=None,
    )
    drifted = replace(package, observations=tuple(changed_observations))

    report = validate_observed_package_contract(drifted)

    assert report.valid is False
    assert [(issue.code, issue.path, issue.message) for issue in report.issues] == [
        (
            "missing_required_observation_field",
            "package.observations[0].provider_indicator_code",
            "required observation field is empty",
        ),
        ("unsupported_frequency", "package.observations[0].frequency", "current contract supports only A, Q, or M frequency"),
        ("missing_period_year", "package.observations[0].period_year", "supported observations require period_year"),
    ]


def test_monthly_observation_contract_requires_month_between_one_and_twelve():
    package = build_eurostat_observed_package(_load(EUROSTAT_NORMALIZED))
    changed_observations = list(package.observations)
    changed_observations[0] = replace(
        changed_observations[0],
        frequency="M",
        provider_period_code="2023-M00",
        period_quarter=None,
        period_month=0,
    )
    drifted = replace(package, observations=tuple(changed_observations))

    report = validate_observed_package_contract(drifted)

    assert report.valid is False
    assert [(issue.code, issue.path, issue.message) for issue in report.issues] == [
        ("invalid_month", "package.observations[0].period_month", "monthly observations require month 1-12"),
    ]
