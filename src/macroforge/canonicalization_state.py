from __future__ import annotations

import json
from collections import defaultdict
from copy import deepcopy
from pathlib import Path
from typing import Any

DETERMINISTIC_GENERATED_AT = "2026-06-05T00:00:00Z"
DEFAULT_AUDIT_PATH = "artifacts/reports/canonicalization-state-foundation-20260605.json"
SOURCE_REPORT_PATH = "artifacts/reports/canonical-gdp-snapshot-20260604.json"
DEFAULT_PROPOSAL_WORKFLOW_AUDIT_PATH = "artifacts/reports/canonicalization-proposal-workflow-20260613.json"
DEFAULT_WDI_UNIT_METADATA_ENRICHMENT_AUDIT_PATH = "artifacts/reports/canonicalization-wdi-unit-metadata-enrichment-20260613.json"
SOURCE_STATE_REPORT_PATH = "artifacts/reports/canonicalization-state-foundation-20260605.json"
RUN_ID = "run:canonicalization-seed-20260605"
PROPOSAL_WORKFLOW_RUN_ID = "run:canonicalization-proposal-workflow-20260613"
WDI_UNIT_METADATA_ENRICHMENT_RUN_ID = "run:wdi-unit-metadata-enrichment-20260613"
CANONICAL_GDP_CONCEPT_ID = "MACRO_GDP_OUTPUT"
WDI_GDP_METADATA_FIXTURE = {
    "source_code": "WDI",
    "provider_dataset_code": "WDI",
    "provider_indicator_code": "NY.GDP.MKTP.CD",
    "unit_profile_id": "unit:WDI:unknown",
    "profile": {
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
    },
}


def _source_sort_key(row: dict[str, Any]) -> tuple[str, str, str]:
    return (row["source_code"], row["provider_dataset_code"], row["indicator_code"])


def _group_seed_observations(snapshot_report: dict[str, Any]) -> list[dict[str, Any]]:
    grouped: dict[tuple[str, str, str], dict[str, Any]] = {}
    for observation in snapshot_report["gdp_snapshot"]["observations"]:
        key = (
            observation["source_code"],
            observation["provider_dataset_code"],
            observation["indicator_code"],
        )
        if key not in grouped:
            grouped[key] = {
                "source_code": observation["source_code"],
                "provider_dataset_code": observation["provider_dataset_code"],
                "indicator_code": observation["indicator_code"],
                "indicator_name": observation.get("indicator_name") or observation["indicator_code"],
                "release_keys": set(),
                "frequencies": set(),
                "territories": set(),
                "unit_codes": set(),
                "period_labels": set(),
                "observation_count": 0,
            }
        group = grouped[key]
        group["release_keys"].add(observation.get("release_key"))
        group["frequencies"].add(observation["frequency"])
        group["territories"].add(observation["territory_code"])
        group["unit_codes"].add(observation["unit_code"])
        group["period_labels"].add(observation["period_label"])
        group["observation_count"] += 1

    rows: list[dict[str, Any]] = []
    for group in grouped.values():
        rows.append(
            {
                **{key: value for key, value in group.items() if not isinstance(value, set)},
                "release_keys": sorted(value for value in group["release_keys"] if value),
                "frequencies": sorted(group["frequencies"]),
                "territories": sorted(group["territories"]),
                "unit_codes": sorted(group["unit_codes"]),
                "period_labels": sorted(group["period_labels"]),
            }
        )
    return sorted(rows, key=_source_sort_key)


def _evidence_id(row: dict[str, Any]) -> str:
    return f"evidence:{row['source_code']}:{row['provider_dataset_code']}:{row['indicator_code']}"


def _proposal_id(row: dict[str, Any]) -> str:
    return f"proposal:{RUN_ID}:{row['source_code']}:{row['indicator_code']}"


def _mapping_id(row: dict[str, Any], version: int = 1) -> str:
    return f"mapping:v{version}:{row['source_code']}:{row['indicator_code']}:{CANONICAL_GDP_CONCEPT_ID}"


def _unit_profile(source_code: str, unit_code: str) -> dict[str, Any]:
    known_profiles: dict[tuple[str, str], dict[str, Any]] = {
        ("EUROSTAT_NAMQ_GDP", "CP_MEUR"): {
            "unit_family": "currency",
            "currency": "EUR",
            "scale_multiplier": 1000000,
            "price_basis": "current",
            "currency_basis": "domestic_currency",
            "metadata_quality": "partial",
            "comparability_group": "current_price_eur_millions",
            "comparable_without_conversion": False,
            "conversion_status": "deferred",
            "caveats": ["Current-price million euro values are not directly comparable to USD_EXC, USD_PPP, or unknown units without conversion policy."],
        },
        ("OECD_NAAG", "USD_EXC"): {
            "unit_family": "currency",
            "currency": "USD",
            "scale_multiplier": None,
            "price_basis": "current",
            "currency_basis": "exchange_rate",
            "metadata_quality": "partial",
            "comparability_group": "current_usd_exchange_rate_basis",
            "comparable_without_conversion": False,
            "conversion_status": "deferred",
            "caveats": ["Exchange-rate USD and PPP USD are separate comparability profiles."],
        },
        ("OECD_NAAG", "USD_PPP"): {
            "unit_family": "currency",
            "currency": "USD",
            "scale_multiplier": None,
            "price_basis": "current",
            "currency_basis": "ppp",
            "metadata_quality": "partial",
            "comparability_group": "current_usd_ppp_basis",
            "comparable_without_conversion": False,
            "conversion_status": "deferred",
            "caveats": ["PPP-basis USD and exchange-rate USD are separate comparability profiles."],
        },
        ("WDI", "unknown"): {
            "unit_family": "unknown",
            "currency": None,
            "scale_multiplier": None,
            "price_basis": "unknown",
            "currency_basis": "unknown",
            "metadata_quality": "unknown",
            "comparability_group": "unknown_unit_metadata",
            "comparable_without_conversion": False,
            "conversion_status": "deferred",
            "caveats": ["unknown unit metadata blocks direct comparability until WDI unit evidence is enriched."],
        },
    }
    profile = dict(known_profiles.get((source_code, unit_code), {}))
    if not profile:
        profile = {
            "unit_family": "unknown",
            "currency": None,
            "scale_multiplier": None,
            "price_basis": "unknown",
            "currency_basis": "unknown",
            "metadata_quality": "unknown",
            "comparability_group": "unknown_unit_metadata",
            "comparable_without_conversion": False,
            "conversion_status": "deferred",
            "caveats": ["Unit metadata is not yet sufficient for direct comparability."],
        }
    return {
        "unit_profile_id": f"unit:{source_code}:{unit_code}",
        "source_code": source_code,
        "provider_unit_code": unit_code,
        **profile,
    }


def _confidence_score(row: dict[str, Any]) -> float:
    if row["source_code"] == "WDI":
        return 0.82
    if row["source_code"] == "EUROSTAT_NAMQ_GDP":
        return 0.88
    return 0.86


def _review_reasons(row: dict[str, Any], profiles: list[dict[str, Any]]) -> list[str]:
    reasons = ["high_impact_concept"]
    if any(profile["metadata_quality"] == "unknown" for profile in profiles):
        reasons.append("unknown unit metadata")
    if row["frequencies"] == ["Q"]:
        reasons.append("quarterly_frequency_must_not_be_aggregated")
    if len(profiles) > 1:
        reasons.append("multiple_unit_profiles")
    return reasons


def build_seed_canonicalization_state(snapshot_report: dict[str, Any]) -> dict[str, Any]:
    grouped = _group_seed_observations(snapshot_report)
    unit_profiles_by_id: dict[str, dict[str, Any]] = {}
    provider_evidence: list[dict[str, Any]] = []
    proposals: list[dict[str, Any]] = []
    accepted_mappings: list[dict[str, Any]] = []

    for row in grouped:
        evidence_id = _evidence_id(row)
        row_profiles = [_unit_profile(row["source_code"], unit_code) for unit_code in row["unit_codes"]]
        for profile in row_profiles:
            unit_profiles_by_id[profile["unit_profile_id"]] = profile
        provider_evidence.append(
            {
                "evidence_id": evidence_id,
                "source_code": row["source_code"],
                "provider_dataset_code": row["provider_dataset_code"],
                "provider_indicator_code": row["indicator_code"],
                "provider_indicator_name": row["indicator_name"],
                "provider_description": None,
                "release_keys": row["release_keys"],
                "frequency_hints": row["frequencies"],
                "territory_hints": row["territories"],
                "unit_profile_ids": [profile["unit_profile_id"] for profile in row_profiles],
                "period_labels": row["period_labels"],
                "observation_count": row["observation_count"],
                "raw_artifact_references": [SOURCE_REPORT_PATH],
                "evidence_version": "seed-snapshot-20260604",
            }
        )
        reasons = _review_reasons(row, row_profiles)
        proposal_id = _proposal_id(row)
        proposals.append(
            {
                "proposal_id": proposal_id,
                "canonicalization_run_id": RUN_ID,
                "provider_indicator_evidence_id": evidence_id,
                "proposed_canonical_concept_id": CANONICAL_GDP_CONCEPT_ID,
                "relationship_type": "close",
                "confidence_score": _confidence_score(row),
                "confidence_band": "review_required",
                "reasoning_summary": "Bounded fixture evidence identifies GDP-like provider indicators, but high-impact GDP mappings require review and unit/frequency caveats.",
                "evidence_references": [SOURCE_REPORT_PATH],
                "unit_profile_ids": [profile["unit_profile_id"] for profile in row_profiles],
                "frequency_treatment": "explicit_no_aggregation",
                "status": "review_required",
                "created_at": DETERMINISTIC_GENERATED_AT,
                "review_reasons": reasons,
                "supersedes": None,
                "superseded_by": None,
            }
        )
        caveats = [caveat for profile in row_profiles for caveat in profile["caveats"]]
        accepted_mappings.append(
            {
                "accepted_mapping_id": _mapping_id(row),
                "mapping_version": 1,
                "source_code": row["source_code"],
                "provider_dataset_code": row["provider_dataset_code"],
                "provider_indicator_code": row["indicator_code"],
                "provider_indicator_evidence_id": evidence_id,
                "canonical_concept_id": CANONICAL_GDP_CONCEPT_ID,
                "canonical_concept_version": 1,
                "relationship_type": "close",
                "unit_profile_ids": [profile["unit_profile_id"] for profile in row_profiles],
                "frequency_applicability": row["frequencies"],
                "aggregation_policy": "no_frequency_aggregation",
                "accepted_status": "provisional",
                "acceptance_source": "deterministic_fixture_policy",
                "accepted_from_proposal_id": proposal_id,
                "accepted_at": DETERMINISTIC_GENERATED_AT,
                "review_state": "review_required",
                "review_reasons": reasons,
                "comparability_caveats": caveats,
                "supersedes": None,
                "superseded_by": None,
                "affected_scope": "bounded_fixture_reports_only",
            }
        )

    return {
        "task": "TASK-032",
        "status": "succeeded",
        "metadata": {
            "generated_at": DETERMINISTIC_GENERATED_AT,
            "source_report": SOURCE_REPORT_PATH,
            "scope": "fixture_backed_wdi_oecd_eurostat_gdp_seed",
            "model_calls": "none",
            "live_fetches": "none",
            "unit_conversion": "not_implemented",
            "frequency_aggregation": "not_implemented",
        },
        "canonicalization_runs": [
            {
                "run_id": RUN_ID,
                "timestamp": DETERMINISTIC_GENERATED_AT,
                "method_type": "deterministic_fixture_rules",
                "ruleset_version": "canonicalization_seed_rules_v1",
                "model_version": "none",
                "prompt_version": "none",
                "input_evidence_versions": ["seed-snapshot-20260604"],
                "thresholds": {"auto_accept_min": 0.95, "review_required_below": 0.95},
                "policy_version": "DEC-018",
            }
        ],
        "canonical_indicator_concepts": [
            {
                "canonical_concept_id": CANONICAL_GDP_CONCEPT_ID,
                "version": 1,
                "label": "Gross domestic product output",
                "definition": "Source-agnostic GDP/output concept candidate for bounded fixture evidence; exact national-accounting scope remains review-gated.",
                "domain": "macroeconomics",
                "measure_type": "flow",
                "lifecycle_status": "proposed_active_seed",
                "default_comparability_caveats": ["Units, price basis, currency basis, and frequency must be checked before comparison."],
                "supersedes": None,
                "superseded_by": None,
            }
        ],
        "provider_indicator_evidence": provider_evidence,
        "unit_comparability_profiles": [unit_profiles_by_id[key] for key in sorted(unit_profiles_by_id)],
        "mapping_proposals": proposals,
        "canonical_creation_proposals": [],
        "accepted_mappings": accepted_mappings,
        "period_policy": {
            "frequencies_observed": sorted(snapshot_report["coverage"]["frequencies"]),
            "aggregation_policy": "no_frequency_aggregation",
            "conversion_policy": "no_unit_conversion",
        },
        "review_policy": {
            "high_impact_concepts": [CANONICAL_GDP_CONCEPT_ID],
            "confidence_score_is_routing_metadata_not_truth": True,
            "auto_accept_deferred_until_calibrated": True,
        },
        "supersession_lineage": [],
    }


def supersede_accepted_mapping(
    accepted_mapping: dict[str, Any],
    *,
    new_mapping_version: int,
    new_status: str,
    reason: str,
    run_id: str,
) -> tuple[dict[str, Any], dict[str, Any]]:
    replacement = deepcopy(accepted_mapping)
    replacement["mapping_version"] = new_mapping_version
    replacement["accepted_mapping_id"] = accepted_mapping["accepted_mapping_id"].replace(":v1:", f":v{new_mapping_version}:")
    replacement["accepted_status"] = new_status
    replacement["supersedes"] = accepted_mapping["accepted_mapping_id"]
    replacement["superseded_by"] = None
    supersession = {
        "superseded_mapping_id": accepted_mapping["accepted_mapping_id"],
        "superseded_by_mapping_id": replacement["accepted_mapping_id"],
        "reason": reason,
        "run_id": run_id,
        "affected_scope": accepted_mapping.get("affected_scope", "bounded_fixture_reports_only"),
    }
    return replacement, supersession


def _audit_checks(state: dict[str, Any]) -> dict[str, str]:
    proposals = state["mapping_proposals"]
    accepted = state["accepted_mappings"]
    profiles = state["unit_comparability_profiles"]
    return {
        "proposal_state_separate_from_accepted_mapping_state": "pass"
        if proposals and accepted and all("accepted_mapping_id" not in proposal for proposal in proposals)
        else "fail",
        "unknown_units_block_direct_comparability": "pass"
        if any(profile["metadata_quality"] == "unknown" and profile["comparable_without_conversion"] is False for profile in profiles)
        else "fail",
        "annual_quarterly_non_aggregation": "pass"
        if state["period_policy"]["frequencies_observed"] == ["A", "Q"] and state["period_policy"]["aggregation_policy"] == "no_frequency_aggregation"
        else "fail",
        "high_impact_review_routing": "pass"
        if all(proposal["confidence_band"] == "review_required" and proposal["review_reasons"][0] == "high_impact_concept" for proposal in proposals)
        else "fail",
        "supersession_fields_present": "pass"
        if all("supersedes" in mapping and "superseded_by" in mapping for mapping in accepted)
        else "fail",
    }


def write_canonicalization_audit(path: str | Path, state: dict[str, Any]) -> dict[str, Any]:
    report = deepcopy(state)
    report["checks"] = _audit_checks(report)
    report["status"] = "succeeded" if all(value == "pass" for value in report["checks"].values()) else "failed"
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def write_seed_audit_from_snapshot(
    snapshot_report_path: str | Path = SOURCE_REPORT_PATH,
    audit_path: str | Path = DEFAULT_AUDIT_PATH,
) -> dict[str, Any]:
    snapshot = json.loads(Path(snapshot_report_path).read_text(encoding="utf-8"))
    state = build_seed_canonicalization_state(snapshot)
    return write_canonicalization_audit(audit_path, state)


def _proposal_workflow_checks(workflow: dict[str, Any]) -> dict[str, str]:
    proposals = workflow["generated_mapping_proposals"]
    updates = workflow["mapping_update_proposals"]
    return {
        "generated_from_provider_evidence": "pass"
        if proposals and all(proposal["generated_from_provider_evidence_id"].startswith("evidence:") for proposal in proposals)
        else "fail",
        "proposal_state_separate_from_accepted_mapping_state": "pass"
        if proposals and updates and all("accepted_mapping_id" not in proposal for proposal in proposals)
        else "fail",
        "high_impact_review_routing": "pass"
        if all(proposal["review_state"] == "review_required" and proposal["review_reasons"][0] == "high_impact_concept" for proposal in proposals)
        else "fail",
        "unknown_unit_caveat_propagated": "pass"
        if any("unknown_unit_metadata" in proposal["comparability_blockers"] for proposal in proposals)
        or workflow["metadata"].get("wdi_unit_metadata_enrichment") == "fixture_backed_source_specific"
        else "fail",
        "annual_quarterly_non_aggregation": "pass"
        if workflow["period_policy"] == {
            "frequencies_observed": ["A", "Q"],
            "aggregation_policy": "no_frequency_aggregation",
            "conversion_policy": "no_unit_conversion",
        }
        and all(proposal["frequency_treatment"] == "explicit_no_aggregation" for proposal in proposals)
        else "fail",
        "no_auto_apply_mapping_updates": "pass" if updates and all(update["auto_apply"] is False for update in updates) else "fail",
    }


def _workflow_proposal_id(evidence: dict[str, Any]) -> str:
    return f"workflow-proposal:{PROPOSAL_WORKFLOW_RUN_ID}:{evidence['source_code']}:{evidence['provider_indicator_code']}"


def _unit_profiles_by_id(state: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {profile["unit_profile_id"]: profile for profile in state["unit_comparability_profiles"]}


def build_deterministic_proposal_workflow(seed_state: dict[str, Any]) -> dict[str, Any]:
    """Generate TASK-034 deterministic workflow proposals from existing TASK-032 state.

    This intentionally treats the existing accepted/provisional mappings as input
    state and emits separate update proposals. It does not mutate or auto-apply
    accepted mapping state.
    """
    profiles_by_id = _unit_profiles_by_id(seed_state)
    accepted_by_evidence_id = {
        mapping["provider_indicator_evidence_id"]: mapping for mapping in seed_state["accepted_mappings"]
    }
    generated_proposals: list[dict[str, Any]] = []
    mapping_updates: list[dict[str, Any]] = []

    for evidence in sorted(
        seed_state["provider_indicator_evidence"],
        key=lambda row: (row["source_code"], row["provider_dataset_code"], row["provider_indicator_code"]),
    ):
        row_profiles = [profiles_by_id[profile_id] for profile_id in evidence["unit_profile_ids"]]
        existing_mapping = accepted_by_evidence_id[evidence["evidence_id"]]
        unit_caveats = [caveat for profile in row_profiles for caveat in profile["caveats"]]
        comparability_blockers = sorted(
            {
                profile["comparability_group"]
                for profile in row_profiles
                if profile["comparable_without_conversion"] is False
            }
        )
        review_reasons = list(existing_mapping["review_reasons"])
        workflow_proposal_id = _workflow_proposal_id(evidence)
        generated_proposals.append(
            {
                "workflow_proposal_id": workflow_proposal_id,
                "proposal_generation_run_id": PROPOSAL_WORKFLOW_RUN_ID,
                "generated_from_provider_evidence_id": evidence["evidence_id"],
                "source_code": evidence["source_code"],
                "provider_dataset_code": evidence["provider_dataset_code"],
                "provider_indicator_code": evidence["provider_indicator_code"],
                "proposed_canonical_concept_id": existing_mapping["canonical_concept_id"],
                "relationship_type": existing_mapping["relationship_type"],
                "frequency_applicability": existing_mapping["frequency_applicability"],
                "frequency_treatment": "explicit_no_aggregation",
                "unit_profile_ids": evidence["unit_profile_ids"],
                "unit_caveats": unit_caveats,
                "comparability_blockers": comparability_blockers,
                "review_state": "review_required",
                "review_reasons": review_reasons,
                "confidence_band": "review_required",
                "confidence_score": next(
                    proposal["confidence_score"]
                    for proposal in seed_state["mapping_proposals"]
                    if proposal["provider_indicator_evidence_id"] == evidence["evidence_id"]
                ),
                "reasoning_summary": "Deterministic TASK-034 workflow proposal generated from existing provider evidence and TASK-032 canonicalization state; high-impact GDP and unit/frequency caveats remain review-gated.",
                "created_at": DETERMINISTIC_GENERATED_AT,
            }
        )
        mapping_updates.append(
            {
                "mapping_update_proposal_id": f"mapping-update:{workflow_proposal_id}",
                "workflow_proposal_id": workflow_proposal_id,
                "target_existing_mapping_id": existing_mapping["accepted_mapping_id"],
                "target_existing_mapping_version": existing_mapping["mapping_version"],
                "proposed_update_status": "provisional_review_required",
                "proposed_review_state": "review_required",
                "auto_apply": False,
                "proposed_changes": {
                    "preserve_accepted_mapping_id": True,
                    "preserve_accepted_status": existing_mapping["accepted_status"],
                    "preserve_frequency_applicability": existing_mapping["frequency_applicability"],
                    "preserve_aggregation_policy": existing_mapping["aggregation_policy"],
                    "propagate_comparability_caveats": unit_caveats,
                },
            }
        )

    workflow = {
        "task": "TASK-034",
        "status": "succeeded",
        "metadata": {
            "generated_at": DETERMINISTIC_GENERATED_AT,
            "source_state_report": SOURCE_STATE_REPORT_PATH,
            "scope": seed_state["metadata"].get("scope", "fixture_backed_wdi_oecd_eurostat_gdp_proposal_workflow"),
            "model_calls": "none",
            "live_fetches": "none",
            "database_writes": "none",
            "unit_conversion": "not_implemented",
            "frequency_aggregation": "not_implemented",
            **{
                key: value
                for key, value in seed_state["metadata"].items()
                if key.startswith("wdi_unit_metadata_")
            },
        },
        "proposal_generation_run": {
            "run_id": PROPOSAL_WORKFLOW_RUN_ID,
            "method_type": "deterministic_fixture_rules",
            "ruleset_version": "proposal_workflow_rules_v1",
            "model_version": "none",
            "prompt_version": "none",
            "input_state_versions": sorted(
                {evidence["evidence_version"] for evidence in seed_state["provider_indicator_evidence"]}
            ),
            "decision_policy": "DEC-019",
        },
        "generated_mapping_proposals": generated_proposals,
        "mapping_update_proposals": mapping_updates,
        "period_policy": deepcopy(seed_state["period_policy"]),
        "review_policy": deepcopy(seed_state["review_policy"]),
        "accepted_mapping_state_mutated": False,
    }
    workflow["checks"] = _proposal_workflow_checks(workflow)
    workflow["status"] = "succeeded" if all(value == "pass" for value in workflow["checks"].values()) else "failed"
    return workflow


def _is_wdi_gdp_evidence(evidence: dict[str, Any]) -> bool:
    return (
        evidence["source_code"] == WDI_GDP_METADATA_FIXTURE["source_code"]
        and evidence["provider_dataset_code"] == WDI_GDP_METADATA_FIXTURE["provider_dataset_code"]
        and evidence["provider_indicator_code"] == WDI_GDP_METADATA_FIXTURE["provider_indicator_code"]
    )


def enrich_wdi_gdp_unit_metadata(seed_state: dict[str, Any]) -> dict[str, Any]:
    """Add bounded fixture-backed unit metadata evidence for WDI GDP only.

    The existing fixture state stores WDI GDP with provider unit code ``unknown``.
    TASK-037 intentionally leaves the provider unit profile identity unchanged and
    enriches only its metadata evidence. It does not convert units, mutate
    accepted mappings, or generalize metadata extraction beyond WDI
    ``NY.GDP.MKTP.CD``.
    """
    enriched = deepcopy(seed_state)
    wdi_evidence = [evidence for evidence in enriched["provider_indicator_evidence"] if _is_wdi_gdp_evidence(evidence)]
    if not wdi_evidence:
        return enriched

    target_profile_id = WDI_GDP_METADATA_FIXTURE["unit_profile_id"]
    if target_profile_id not in wdi_evidence[0]["unit_profile_ids"]:
        return enriched

    for profile in enriched["unit_comparability_profiles"]:
        if profile["unit_profile_id"] == target_profile_id and profile["source_code"] == "WDI":
            profile.update(deepcopy(WDI_GDP_METADATA_FIXTURE["profile"]))

    enriched["metadata"] = {
        **enriched["metadata"],
        "scope": "fixture_backed_wdi_gdp_unit_metadata_enrichment",
        "wdi_unit_metadata_enrichment": "fixture_backed_source_specific",
        "wdi_unit_metadata_evidence_role": "metadata_evidence_not_canonical_truth",
        "wdi_unit_metadata_fixture": WDI_GDP_METADATA_FIXTURE["profile"]["metadata_source"],
        "model_calls": "none",
        "live_fetches": "none",
        "unit_conversion": "not_implemented",
        "frequency_aggregation": "not_implemented",
    }
    return enriched


def _wdi_unit_metadata_enrichment_checks(
    seed_state: dict[str, Any], enriched_state: dict[str, Any], workflow: dict[str, Any]
) -> dict[str, str]:
    seed_profiles = _unit_profiles_by_id(seed_state)
    enriched_profiles = _unit_profiles_by_id(enriched_state)
    wdi_profile = enriched_profiles[WDI_GDP_METADATA_FIXTURE["unit_profile_id"]]
    proposals = {proposal["source_code"]: proposal for proposal in workflow["generated_mapping_proposals"]}
    return {
        "wdi_unknown_unit_metadata_reduced": "pass"
        if seed_profiles["unit:WDI:unknown"]["comparability_group"] == "unknown_unit_metadata"
        and wdi_profile["comparability_group"] != "unknown_unit_metadata"
        and "unknown_unit_metadata" not in proposals["WDI"]["comparability_blockers"]
        else "fail",
        "non_wdi_sources_unchanged": "pass"
        if all(
            enriched_profiles[profile_id] == profile
            for profile_id, profile in seed_profiles.items()
            if not profile_id.startswith("unit:WDI:")
        )
        else "fail",
        "metadata_evidence_not_canonical_truth": "pass"
        if wdi_profile.get("metadata_evidence_role") == "source_metadata_not_canonical_truth"
        else "fail",
        "no_unit_conversion": "pass"
        if workflow["period_policy"]["conversion_policy"] == "no_unit_conversion"
        and workflow["metadata"]["unit_conversion"] == "not_implemented"
        and wdi_profile["conversion_status"] == "deferred"
        and wdi_profile["comparable_without_conversion"] is False
        else "fail",
        "proposal_state_separate_from_accepted_mapping_state": "pass"
        if workflow["checks"]["proposal_state_separate_from_accepted_mapping_state"] == "pass"
        and seed_state["accepted_mappings"] == enriched_state["accepted_mappings"]
        else "fail",
        "high_impact_review_routing_preserved": "pass"
        if all(proposal["review_state"] == "review_required" for proposal in workflow["generated_mapping_proposals"])
        and all(proposal["review_reasons"][0] == "high_impact_concept" for proposal in workflow["generated_mapping_proposals"])
        else "fail",
        "no_auto_apply_mapping_updates": "pass"
        if workflow["checks"]["no_auto_apply_mapping_updates"] == "pass"
        else "fail",
    }


def write_proposal_workflow_audit(path: str | Path, seed_state: dict[str, Any]) -> dict[str, Any]:
    report = build_deterministic_proposal_workflow(seed_state)
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def write_wdi_unit_metadata_enrichment_audit(path: str | Path, seed_state: dict[str, Any]) -> dict[str, Any]:
    enriched_state = enrich_wdi_gdp_unit_metadata(seed_state)
    workflow = build_deterministic_proposal_workflow(enriched_state)
    checks = _wdi_unit_metadata_enrichment_checks(seed_state, enriched_state, workflow)
    report = {
        "task": "TASK-037",
        "status": "succeeded" if all(value == "pass" for value in checks.values()) else "failed",
        "metadata": {
            "generated_at": DETERMINISTIC_GENERATED_AT,
            "run_id": WDI_UNIT_METADATA_ENRICHMENT_RUN_ID,
            "source_state_report": SOURCE_STATE_REPORT_PATH,
            "scope": "fixture_backed_wdi_gdp_unit_metadata_enrichment",
            "model_calls": "none",
            "live_fetches": "none",
            "database_writes": "none",
            "unit_conversion": "not_implemented",
            "frequency_aggregation": "not_implemented",
        },
        "checks": checks,
        "enriched_state": enriched_state,
        "workflow": workflow,
    }
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return report


def write_proposal_workflow_audit_from_state(
    state_report_path: str | Path = SOURCE_STATE_REPORT_PATH,
    audit_path: str | Path = DEFAULT_PROPOSAL_WORKFLOW_AUDIT_PATH,
) -> dict[str, Any]:
    seed_state = json.loads(Path(state_report_path).read_text(encoding="utf-8"))
    return write_proposal_workflow_audit(audit_path, seed_state)


if __name__ == "__main__":
    write_seed_audit_from_snapshot()
