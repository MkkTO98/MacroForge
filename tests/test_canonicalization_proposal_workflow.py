from __future__ import annotations

import json
from pathlib import Path

from macroforge import canonicalization_state

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SEED_STATE_REPORT = PROJECT_ROOT / "artifacts" / "reports" / "canonicalization-state-foundation-20260605.json"


def _seed_state() -> dict[str, object]:
    return json.loads(SEED_STATE_REPORT.read_text(encoding="utf-8"))


def test_workflow_generates_review_routed_proposals_from_existing_provider_evidence():
    workflow = canonicalization_state.build_deterministic_proposal_workflow(_seed_state())

    assert workflow["task"] == "TASK-034"
    assert workflow["metadata"]["source_state_report"] == "artifacts/reports/canonicalization-state-foundation-20260605.json"
    assert workflow["metadata"]["model_calls"] == "none"
    assert workflow["proposal_generation_run"] == {
        "run_id": "run:canonicalization-proposal-workflow-20260613",
        "method_type": "deterministic_fixture_rules",
        "ruleset_version": "proposal_workflow_rules_v1",
        "model_version": "none",
        "prompt_version": "none",
        "input_state_versions": ["seed-snapshot-20260604"],
        "decision_policy": "DEC-019",
    }

    source_codes = {proposal["source_code"] for proposal in workflow["generated_mapping_proposals"]}
    assert source_codes == {"WDI", "OECD_NAAG", "EUROSTAT_NAMQ_GDP"}
    assert all(proposal["generated_from_provider_evidence_id"].startswith("evidence:") for proposal in workflow["generated_mapping_proposals"])
    assert {proposal["review_state"] for proposal in workflow["generated_mapping_proposals"]} == {"review_required"}
    assert all(proposal["review_reasons"][0] == "high_impact_concept" for proposal in workflow["generated_mapping_proposals"])


def test_workflow_keeps_generated_proposals_separate_from_existing_accepted_mapping_state():
    seed = _seed_state()
    workflow = canonicalization_state.build_deterministic_proposal_workflow(seed)

    existing_accepted_ids = {mapping["accepted_mapping_id"] for mapping in seed["accepted_mappings"]}
    workflow_proposal_ids = {proposal["workflow_proposal_id"] for proposal in workflow["generated_mapping_proposals"]}
    update_targets = {update["target_existing_mapping_id"] for update in workflow["mapping_update_proposals"]}

    assert workflow_proposal_ids == {
        "workflow-proposal:run:canonicalization-proposal-workflow-20260613:EUROSTAT_NAMQ_GDP:B1GQ",
        "workflow-proposal:run:canonicalization-proposal-workflow-20260613:OECD_NAAG:B1GQ",
        "workflow-proposal:run:canonicalization-proposal-workflow-20260613:WDI:NY.GDP.MKTP.CD",
    }
    assert update_targets == existing_accepted_ids
    assert all("accepted_mapping_id" not in proposal for proposal in workflow["generated_mapping_proposals"])
    assert seed["accepted_mappings"] == _seed_state()["accepted_mappings"]
    assert all(update["proposed_update_status"] == "provisional_review_required" for update in workflow["mapping_update_proposals"])
    assert all(update["auto_apply"] is False for update in workflow["mapping_update_proposals"])


def test_workflow_propagates_unit_caveats_and_explicit_frequency_non_aggregation():
    workflow = canonicalization_state.build_deterministic_proposal_workflow(_seed_state())

    by_source = {proposal["source_code"]: proposal for proposal in workflow["generated_mapping_proposals"]}

    assert by_source["WDI"]["unit_caveats"] == [
        "unknown unit metadata blocks direct comparability until WDI unit evidence is enriched."
    ]
    assert "unknown_unit_metadata" in by_source["WDI"]["comparability_blockers"]
    assert by_source["EUROSTAT_NAMQ_GDP"]["frequency_applicability"] == ["Q"]
    assert by_source["EUROSTAT_NAMQ_GDP"]["frequency_treatment"] == "explicit_no_aggregation"
    assert by_source["OECD_NAAG"]["frequency_applicability"] == ["A"]
    assert workflow["period_policy"] == {
        "frequencies_observed": ["A", "Q"],
        "aggregation_policy": "no_frequency_aggregation",
        "conversion_policy": "no_unit_conversion",
    }


def test_workflow_audit_writer_is_deterministic_and_reports_checks(tmp_path):
    seed = _seed_state()
    json_path = tmp_path / "artifacts" / "reports" / "canonicalization-proposal-workflow-20260613.json"

    canonicalization_state.write_proposal_workflow_audit(json_path, seed)
    first = json_path.read_text(encoding="utf-8")
    report = canonicalization_state.write_proposal_workflow_audit(json_path, seed)

    assert json_path.read_text(encoding="utf-8") == first
    assert report["status"] == "succeeded"
    assert report["checks"] == {
        "generated_from_provider_evidence": "pass",
        "proposal_state_separate_from_accepted_mapping_state": "pass",
        "high_impact_review_routing": "pass",
        "unknown_unit_caveat_propagated": "pass",
        "annual_quarterly_non_aggregation": "pass",
        "no_auto_apply_mapping_updates": "pass",
    }
    loaded = json.loads(first)
    assert loaded["metadata"]["live_fetches"] == "none"
    assert loaded["metadata"]["database_writes"] == "none"
    assert loaded["status"] == "succeeded"


def test_wdi_unit_metadata_enrichment_is_deterministic_and_source_specific():
    seed = _seed_state()
    enriched = canonicalization_state.enrich_wdi_gdp_unit_metadata(seed)

    seed_profiles = {profile["unit_profile_id"]: profile for profile in seed["unit_comparability_profiles"]}
    enriched_profiles = {profile["unit_profile_id"]: profile for profile in enriched["unit_comparability_profiles"]}

    assert enriched is not seed
    assert seed_profiles["unit:WDI:unknown"]["metadata_quality"] == "unknown"
    assert enriched_profiles["unit:WDI:unknown"] == {
        "unit_profile_id": "unit:WDI:unknown",
        "source_code": "WDI",
        "provider_unit_code": "unknown",
        "unit_family": "currency",
        "currency": "USD",
        "scale_multiplier": 1,
        "price_basis": "current",
        "currency_basis": "exchange_rate",
        "metadata_quality": "metadata_evidence",
        "metadata_evidence_role": "source_metadata_not_canonical_truth",
        "metadata_source": "fixture:wdi:NY.GDP.MKTP.CD:unit_metadata",
        "comparability_group": "current_usd_exchange_rate_basis",
        "comparable_without_conversion": False,
        "conversion_status": "deferred",
        "caveats": [
            "WDI fixture metadata identifies NY.GDP.MKTP.CD as current US dollars, but this is metadata evidence only and does not perform currency/unit conversion or prove canonical comparability."
        ],
    }
    assert enriched["metadata"]["wdi_unit_metadata_enrichment"] == "fixture_backed_source_specific"
    assert enriched["metadata"]["unit_conversion"] == "not_implemented"

    for profile_id, profile in seed_profiles.items():
        if profile_id != "unit:WDI:unknown":
            assert enriched_profiles[profile_id] == profile


def test_wdi_enrichment_reduces_unknown_only_for_existing_wdi_gdp_evidence_and_preserves_review_routing():
    seed = _seed_state()
    enriched = canonicalization_state.enrich_wdi_gdp_unit_metadata(seed)
    workflow = canonicalization_state.build_deterministic_proposal_workflow(enriched)
    proposals = {proposal["source_code"]: proposal for proposal in workflow["generated_mapping_proposals"]}

    assert "unknown_unit_metadata" not in proposals["WDI"]["comparability_blockers"]
    assert proposals["WDI"]["comparability_blockers"] == ["current_usd_exchange_rate_basis"]
    assert proposals["WDI"]["unit_caveats"] == [
        "WDI fixture metadata identifies NY.GDP.MKTP.CD as current US dollars, but this is metadata evidence only and does not perform currency/unit conversion or prove canonical comparability."
    ]
    assert proposals["WDI"]["review_state"] == "review_required"
    assert proposals["WDI"]["review_reasons"][0] == "high_impact_concept"
    assert proposals["WDI"]["confidence_band"] == "review_required"

    assert proposals["OECD_NAAG"]["comparability_blockers"] == [
        "current_usd_exchange_rate_basis",
        "current_usd_ppp_basis",
    ]
    assert proposals["EUROSTAT_NAMQ_GDP"]["comparability_blockers"] == ["current_price_eur_millions"]


def test_wdi_enrichment_does_not_convert_units_or_auto_accept_mappings():
    seed = _seed_state()
    enriched = canonicalization_state.enrich_wdi_gdp_unit_metadata(seed)
    workflow = canonicalization_state.build_deterministic_proposal_workflow(enriched)

    assert workflow["metadata"]["unit_conversion"] == "not_implemented"
    assert workflow["period_policy"] == {
        "frequencies_observed": ["A", "Q"],
        "aggregation_policy": "no_frequency_aggregation",
        "conversion_policy": "no_unit_conversion",
    }
    assert workflow["accepted_mapping_state_mutated"] is False
    assert all(update["auto_apply"] is False for update in workflow["mapping_update_proposals"])
    assert seed["accepted_mappings"] == _seed_state()["accepted_mappings"]
    assert enriched["accepted_mappings"] == seed["accepted_mappings"]


def test_wdi_enrichment_audit_writer_is_deterministic_and_reads_back_metadata_evidence(tmp_path):
    seed = _seed_state()
    json_path = tmp_path / "artifacts" / "reports" / "canonicalization-wdi-unit-metadata-enrichment-20260613.json"

    report = canonicalization_state.write_wdi_unit_metadata_enrichment_audit(json_path, seed)
    first = json_path.read_text(encoding="utf-8")
    canonicalization_state.write_wdi_unit_metadata_enrichment_audit(json_path, seed)

    assert json_path.read_text(encoding="utf-8") == first
    assert report["task"] == "TASK-037"
    assert report["status"] == "succeeded"
    assert report["checks"] == {
        "wdi_unknown_unit_metadata_reduced": "pass",
        "non_wdi_sources_unchanged": "pass",
        "metadata_evidence_not_canonical_truth": "pass",
        "no_unit_conversion": "pass",
        "proposal_state_separate_from_accepted_mapping_state": "pass",
        "high_impact_review_routing_preserved": "pass",
        "no_auto_apply_mapping_updates": "pass",
    }

    loaded = json.loads(first)
    wdi_profile = next(profile for profile in loaded["enriched_state"]["unit_comparability_profiles"] if profile["source_code"] == "WDI")
    assert wdi_profile["metadata_evidence_role"] == "source_metadata_not_canonical_truth"
    assert loaded["workflow"]["metadata"]["model_calls"] == "none"
    assert loaded["workflow"]["metadata"]["live_fetches"] == "none"
    assert loaded["workflow"]["metadata"]["database_writes"] == "none"
