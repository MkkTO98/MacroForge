from __future__ import annotations

import json
from pathlib import Path

from macroforge import canonicalization_state

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SNAPSHOT_REPORT = PROJECT_ROOT / "artifacts" / "reports" / "canonical-gdp-snapshot-20260604.json"


def _snapshot_report() -> dict[str, object]:
    return json.loads(SNAPSHOT_REPORT.read_text(encoding="utf-8"))


def test_builds_provider_evidence_proposals_and_accepted_mapping_state_separately():
    state = canonicalization_state.build_seed_canonicalization_state(_snapshot_report())

    evidence_ids = {row["evidence_id"] for row in state["provider_indicator_evidence"]}
    proposal_ids = {row["proposal_id"] for row in state["mapping_proposals"]}
    accepted_ids = {row["accepted_mapping_id"] for row in state["accepted_mappings"]}

    assert evidence_ids == {
        "evidence:EUROSTAT_NAMQ_GDP:namq_10_gdp:B1GQ",
        "evidence:OECD_NAAG:OECD.SDD.NAD,DSD_NAAG@DF_NAAG_I:B1GQ",
        "evidence:WDI:WDI:NY.GDP.MKTP.CD",
    }
    assert proposal_ids == {
        "proposal:run:canonicalization-seed-20260605:EUROSTAT_NAMQ_GDP:B1GQ",
        "proposal:run:canonicalization-seed-20260605:OECD_NAAG:B1GQ",
        "proposal:run:canonicalization-seed-20260605:WDI:NY.GDP.MKTP.CD",
    }
    assert accepted_ids == {
        "mapping:v1:EUROSTAT_NAMQ_GDP:B1GQ:MACRO_GDP_OUTPUT",
        "mapping:v1:OECD_NAAG:B1GQ:MACRO_GDP_OUTPUT",
        "mapping:v1:WDI:NY.GDP.MKTP.CD:MACRO_GDP_OUTPUT",
    }

    assert all("accepted_mapping_id" not in proposal for proposal in state["mapping_proposals"])
    assert {mapping["accepted_from_proposal_id"] for mapping in state["accepted_mappings"]} == proposal_ids
    assert state["canonical_indicator_concepts"][0]["canonical_concept_id"] == "MACRO_GDP_OUTPUT"
    assert state["canonicalization_runs"][0]["method_type"] == "deterministic_fixture_rules"
    assert state["canonicalization_runs"][0]["model_version"] == "none"


def test_unknown_and_distinct_unit_profiles_block_direct_comparability_without_conversion():
    state = canonicalization_state.build_seed_canonicalization_state(_snapshot_report())
    profiles = {profile["unit_profile_id"]: profile for profile in state["unit_comparability_profiles"]}

    assert profiles["unit:WDI:unknown"]["metadata_quality"] == "unknown"
    assert profiles["unit:WDI:unknown"]["comparable_without_conversion"] is False
    assert profiles["unit:WDI:unknown"]["conversion_status"] == "deferred"
    assert profiles["unit:OECD_NAAG:USD_EXC"]["currency_basis"] == "exchange_rate"
    assert profiles["unit:OECD_NAAG:USD_PPP"]["currency_basis"] == "ppp"
    assert profiles["unit:EUROSTAT_NAMQ_GDP:CP_MEUR"]["scale_multiplier"] == 1000000

    wdi_mapping = next(mapping for mapping in state["accepted_mappings"] if mapping["source_code"] == "WDI")
    assert wdi_mapping["accepted_status"] == "provisional"
    assert wdi_mapping["review_state"] == "review_required"
    assert "unknown unit metadata" in " ".join(wdi_mapping["comparability_caveats"])


def test_annual_and_quarterly_applicability_are_explicit_and_not_aggregated():
    state = canonicalization_state.build_seed_canonicalization_state(_snapshot_report())

    assert state["period_policy"] == {
        "frequencies_observed": ["A", "Q"],
        "aggregation_policy": "no_frequency_aggregation",
        "conversion_policy": "no_unit_conversion",
    }

    applicability = {
        mapping["source_code"]: mapping["frequency_applicability"]
        for mapping in state["accepted_mappings"]
    }
    assert applicability == {
        "EUROSTAT_NAMQ_GDP": ["Q"],
        "OECD_NAAG": ["A"],
        "WDI": ["A"],
    }
    assert all(mapping["aggregation_policy"] == "no_frequency_aggregation" for mapping in state["accepted_mappings"])


def test_confidence_bands_route_high_impact_gdp_seed_mappings_to_review():
    state = canonicalization_state.build_seed_canonicalization_state(_snapshot_report())

    assert state["review_policy"]["high_impact_concepts"] == ["MACRO_GDP_OUTPUT"]
    assert {proposal["confidence_band"] for proposal in state["mapping_proposals"]} == {"review_required"}
    assert {proposal["review_reasons"][0] for proposal in state["mapping_proposals"]} == {"high_impact_concept"}
    assert all(proposal["confidence_score"] < 1 for proposal in state["mapping_proposals"])


def test_supersession_lineage_can_version_accepted_mapping_without_overwriting_history():
    state = canonicalization_state.build_seed_canonicalization_state(_snapshot_report())
    original = next(mapping for mapping in state["accepted_mappings"] if mapping["source_code"] == "WDI")

    replacement, supersession = canonicalization_state.supersede_accepted_mapping(
        original,
        new_mapping_version=2,
        new_status="accepted",
        reason="WDI unit evidence was enriched and reviewed",
        run_id="run:canonicalization-seed-20260605-r2",
    )

    assert original["mapping_version"] == 1
    assert original["superseded_by"] is None
    assert replacement["mapping_version"] == 2
    assert replacement["supersedes"] == original["accepted_mapping_id"]
    assert replacement["accepted_status"] == "accepted"
    assert supersession == {
        "superseded_mapping_id": original["accepted_mapping_id"],
        "superseded_by_mapping_id": replacement["accepted_mapping_id"],
        "reason": "WDI unit evidence was enriched and reviewed",
        "run_id": "run:canonicalization-seed-20260605-r2",
        "affected_scope": "bounded_fixture_reports_only",
    }


def test_audit_report_writer_is_deterministic_and_project_layout_safe(tmp_path):
    state = canonicalization_state.build_seed_canonicalization_state(_snapshot_report())
    json_path = tmp_path / "artifacts" / "reports" / "canonicalization-state-foundation-20260605.json"

    canonicalization_state.write_canonicalization_audit(json_path, state)
    first = json_path.read_text(encoding="utf-8")
    canonicalization_state.write_canonicalization_audit(json_path, state)

    assert json_path.read_text(encoding="utf-8") == first
    loaded = json.loads(first)
    assert loaded["task"] == "TASK-032"
    assert loaded["status"] == "succeeded"
    assert loaded["metadata"]["source_report"] == "artifacts/reports/canonical-gdp-snapshot-20260604.json"
    assert loaded["checks"] == {
        "proposal_state_separate_from_accepted_mapping_state": "pass",
        "unknown_units_block_direct_comparability": "pass",
        "annual_quarterly_non_aggregation": "pass",
        "high_impact_review_routing": "pass",
        "supersession_fields_present": "pass",
    }
