from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

from macroforge.bls_cpi import build_bls_cpi_observed_package, normalize_bls_cpi_fixture
from macroforge.contract_drift import validate_observed_package_contract
from macroforge.ingestion_feedback import (
    SourceEngineeringEffortProfile,
    deterministic_feedback_from_contract_report,
    deterministic_feedback_from_lineage_events,
    deterministic_feedback_from_package_comparison,
    source_engineering_effort_profiles,
)
from macroforge.lineage_generation import canonical_lineage_events
from macroforge.observed_ingestion import build_eurostat_observed_package, build_wdi_observed_package, compare_observed_packages

PROJECT_ROOT = Path(__file__).resolve().parents[1]
WDI_NORMALIZED = PROJECT_ROOT / "data" / "metadata" / "wdi" / "wdi-smoke-normalized.json"
EUROSTAT_NORMALIZED = PROJECT_ROOT / "data" / "metadata" / "eurostat" / "eurostat-namq-10-gdp-architecture-spike-normalized.json"
BLS_RAW = PROJECT_ROOT / "data" / "raw" / "bls" / "bls-cpi-cuur0000sa0-2023-raw.json"


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _bls_package():
    normalized = normalize_bls_cpi_fixture(
        _load(BLS_RAW),
        raw_artifact_path=str(BLS_RAW.relative_to(PROJECT_ROOT)),
        raw_sha256="55bd2b4ae23fd31f274754d36f4ce8c7e00433b109174a3d8544fa2ff392cdc3",
        source_url="https://api.bls.gov/publicAPI/v2/timeseries/data/CUUR0000SA0?startyear=2023&endyear=2023",
    )
    return build_bls_cpi_observed_package(normalized)


def test_contract_feedback_explains_failed_contract_path_and_inspection_location():
    package = _bls_package()
    observations = list(package.observations)
    observations[0] = replace(observations[0], period_month=13)
    drifted = replace(package, observations=tuple(observations))

    feedback = deterministic_feedback_from_contract_report(validate_observed_package_contract(drifted))

    assert feedback.source_code == "BLS_CPI"
    assert feedback.status == "failed"
    assert feedback.summary == "BLS_CPI observed package violates 1 deterministic contract invariant."
    assert feedback.deterministic_guarantee == "ObservedIngestionPackage contract invariants"
    assert feedback.inspection_hint == "Inspect package.observations[0].period_month."
    assert feedback.items == (
        {
            "question": "Which contract failed?",
            "code": "invalid_month",
            "where": "package.observations[0].period_month",
            "what_changed": "monthly observations require month 1-12",
            "deterministic_guarantee": "ObservedIngestionPackage contract invariants",
            "likely_inspection_location": "package.observations[0]",
        },
    )


def test_package_comparison_feedback_explains_changed_observation_and_fingerprint_drift():
    package = build_eurostat_observed_package(_load(EUROSTAT_NORMALIZED))
    observations = list(package.observations)
    observations[1] = replace(observations[1], value=999999)
    drifted = replace(package, observations=tuple(observations))

    feedback = deterministic_feedback_from_package_comparison(
        "EUROSTAT_NAMQ_GDP",
        compare_observed_packages(package, drifted),
    )

    assert feedback.status == "failed"
    assert feedback.summary == "EUROSTAT_NAMQ_GDP observed package comparison found non-equivalent fingerprints."
    assert feedback.deterministic_guarantee == "Observed package fingerprint equivalence"
    assert feedback.inspection_hint == "Inspect observation identity at index 1: B1GQ/DE/2023-Q2."
    assert feedback.items == (
        {
            "question": "Which observation differs?",
            "index": 1,
            "provider_indicator_code": "B1GQ",
            "provider_territory_code": "DE",
            "provider_period_code": "2023-Q2",
            "changed_fields": ("value",),
            "what_changed": "observation fields differ: value",
            "deterministic_guarantee": "Observed package fingerprint equivalence",
            "likely_inspection_location": "package.observations[1]",
        },
    )


def test_package_comparison_feedback_reports_success_from_existing_evidence():
    package = build_wdi_observed_package(_load(WDI_NORMALIZED))

    feedback = deterministic_feedback_from_package_comparison("WDI", compare_observed_packages(package, package))

    assert feedback.status == "passed"
    assert feedback.summary == "WDI observed package comparison is deterministic-equivalent."
    assert feedback.items == ()
    assert feedback.inspection_hint == "No inspection required."


def test_lineage_feedback_explains_existing_two_step_lineage_guarantee():
    events = canonical_lineage_events(
        raw_artifact_path="data/raw/bls/bls-cpi-cuur0000sa0-2023-raw.json",
        raw_checksum_sha256="55bd2b4ae23fd31f274754d36f4ce8c7e00433b109174a3d8544fa2ff392cdc3",
        staging_artifact="staging.bls_cpi_observation",
        staging_row_count_sql="(SELECT count(*)::bigint FROM staging.bls_cpi_observation)",
        curated_row_count_sql="(SELECT count(*)::bigint FROM curated.fact_observation)",
        details={"task": "TASK-052", "source_code": "BLS_CPI"},
    )

    feedback = deterministic_feedback_from_lineage_events("BLS_CPI", events)

    assert feedback.status == "passed"
    assert feedback.summary == "BLS_CPI lineage evidence has deterministic raw_to_staging -> staging_to_curated event order."
    assert feedback.deterministic_guarantee == "Canonical two-step lineage event semantics"
    assert feedback.inspection_hint == "Inspect lineage events raw_to_staging and staging_to_curated."
    assert feedback.items == (
        {
            "question": "Where did it change?",
            "event_type": "raw_to_staging",
            "from_artifact": "data/raw/bls/bls-cpi-cuur0000sa0-2023-raw.json",
            "to_artifact": "staging.bls_cpi_observation",
            "deterministic_guarantee": "Canonical two-step lineage event semantics",
            "likely_inspection_location": "lineage_events[0]",
        },
        {
            "question": "Where did it change?",
            "event_type": "staging_to_curated",
            "from_artifact": "staging.bls_cpi_observation",
            "to_artifact": "curated.fact_observation",
            "deterministic_guarantee": "Canonical two-step lineage event semantics",
            "likely_inspection_location": "lineage_events[1]",
        },
    )


def test_source_engineering_effort_profiles_record_qualitative_substrate_effort_ratio():
    profiles = source_engineering_effort_profiles()

    assert set(profiles) == {"WDI", "OECD_NAAG", "EUROSTAT_NAMQ_GDP", "BLS_CPI"}
    assert profiles["BLS_CPI"] == SourceEngineeringEffortProfile(
        source_code="BLS_CPI",
        acquisition="Low",
        provider_interpretation="Medium",
        normalization="Medium",
        observed_package_construction="Low",
        deterministic_substrate="Very Low",
        canonical_loading="None",
        deterministic_verification="Low",
        testing="Medium",
        substrate_effort_ratio="Very Low",
        evidence_note="TASK-051 bounded monthly CPI slice required only optional period_month and A/Q/M contract validation after the observed boundary; no canonical loader was added.",
    )
    assert all(profile.substrate_effort_ratio in {"High", "Medium", "Low", "Very Low"} for profile in profiles.values())
    assert profiles["WDI"].substrate_effort_ratio == "Low"
    assert profiles["OECD_NAAG"].substrate_effort_ratio == "Low"
    assert profiles["EUROSTAT_NAMQ_GDP"].substrate_effort_ratio == "Low"
