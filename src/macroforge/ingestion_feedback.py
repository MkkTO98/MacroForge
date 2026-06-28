from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from macroforge.contract_drift import ContractDriftReport
from macroforge.lineage_generation import CanonicalLineageEvent
from macroforge.observed_ingestion import ObservedPackageComparison


@dataclass(frozen=True)
class DeterministicIngestionFeedback:
    """Human-readable deterministic feedback derived from existing verification evidence."""

    source_code: str
    status: str
    summary: str
    deterministic_guarantee: str
    inspection_hint: str
    items: tuple[dict[str, Any], ...]


@dataclass(frozen=True)
class SourceEngineeringEffortProfile:
    """Qualitative implementation-effort evidence for one implemented source."""

    source_code: str
    acquisition: str
    provider_interpretation: str
    normalization: str
    observed_package_construction: str
    deterministic_substrate: str
    canonical_loading: str
    deterministic_verification: str
    testing: str
    substrate_effort_ratio: str
    evidence_note: str


def deterministic_feedback_from_contract_report(report: ContractDriftReport) -> DeterministicIngestionFeedback:
    """Explain contract validation evidence without adding recovery automation."""

    guarantee = "ObservedIngestionPackage contract invariants"
    if report.valid:
        return DeterministicIngestionFeedback(
            source_code=report.source_code,
            status="passed",
            summary=f"{report.source_code} observed package satisfies deterministic contract invariants.",
            deterministic_guarantee=guarantee,
            inspection_hint="No inspection required.",
            items=(),
        )

    items = tuple(
        {
            "question": "Which contract failed?",
            "code": issue.code,
            "where": issue.path,
            "what_changed": issue.message,
            "deterministic_guarantee": guarantee,
            "likely_inspection_location": _contract_inspection_location(issue.path),
        }
        for issue in report.issues
    )
    issue_count = len(report.issues)
    plural = "invariant" if issue_count == 1 else "invariants"
    return DeterministicIngestionFeedback(
        source_code=report.source_code,
        status="failed",
        summary=f"{report.source_code} observed package violates {issue_count} deterministic contract {plural}.",
        deterministic_guarantee=guarantee,
        inspection_hint=f"Inspect {report.issues[0].path}.",
        items=items,
    )


def deterministic_feedback_from_package_comparison(
    source_code: str,
    comparison: ObservedPackageComparison,
) -> DeterministicIngestionFeedback:
    """Explain observed-package comparison evidence for developers and agents."""

    guarantee = "Observed package fingerprint equivalence"
    if comparison.equivalent:
        return DeterministicIngestionFeedback(
            source_code=source_code,
            status="passed",
            summary=f"{source_code} observed package comparison is deterministic-equivalent.",
            deterministic_guarantee=guarantee,
            inspection_hint="No inspection required.",
            items=(),
        )

    items: list[dict[str, Any]] = []
    if not comparison.row_count_match:
        items.append(
            {
                "question": "What changed?",
                "what_changed": "row_count differs",
                "deterministic_guarantee": guarantee,
                "likely_inspection_location": "package.row_count",
            }
        )
    if not comparison.expected_row_count_match:
        items.append(
            {
                "question": "What changed?",
                "what_changed": "expected_row_count differs",
                "deterministic_guarantee": guarantee,
                "likely_inspection_location": "package.expected_row_count",
            }
        )
    if not comparison.observation_count_match:
        items.append(
            {
                "question": "What changed?",
                "what_changed": "observation count differs",
                "deterministic_guarantee": guarantee,
                "likely_inspection_location": "package.observations",
            }
        )
    for difference in comparison.differing_observations:
        changed_fields = tuple(difference["changed_fields"])
        index = difference["index"]
        items.append(
            {
                "question": "Which observation differs?",
                "index": index,
                "provider_indicator_code": difference["provider_indicator_code"],
                "provider_territory_code": difference["provider_territory_code"],
                "provider_period_code": difference["provider_period_code"],
                "changed_fields": changed_fields,
                "what_changed": f"observation fields differ: {', '.join(changed_fields)}",
                "deterministic_guarantee": guarantee,
                "likely_inspection_location": f"package.observations[{index}]",
            }
        )

    return DeterministicIngestionFeedback(
        source_code=source_code,
        status="failed",
        summary=f"{source_code} observed package comparison found non-equivalent fingerprints.",
        deterministic_guarantee=guarantee,
        inspection_hint=_comparison_inspection_hint(comparison),
        items=tuple(items),
    )


def deterministic_feedback_from_lineage_events(
    source_code: str,
    events: tuple[CanonicalLineageEvent, ...],
) -> DeterministicIngestionFeedback:
    """Explain existing canonical lineage event evidence deterministically."""

    guarantee = "Canonical two-step lineage event semantics"
    event_order = tuple(event.event_type for event in events)
    expected_order = ("raw_to_staging", "staging_to_curated")
    status = "passed" if event_order == expected_order else "failed"
    if status == "passed":
        summary = f"{source_code} lineage evidence has deterministic raw_to_staging -> staging_to_curated event order."
        inspection_hint = "Inspect lineage events raw_to_staging and staging_to_curated."
    else:
        summary = f"{source_code} lineage evidence violates deterministic two-step event order."
        inspection_hint = "Inspect lineage event order."

    return DeterministicIngestionFeedback(
        source_code=source_code,
        status=status,
        summary=summary,
        deterministic_guarantee=guarantee,
        inspection_hint=inspection_hint,
        items=tuple(
            {
                "question": "Where did it change?",
                "event_type": event.event_type,
                "from_artifact": event.from_artifact,
                "to_artifact": event.to_artifact,
                "deterministic_guarantee": guarantee,
                "likely_inspection_location": f"lineage_events[{index}]",
            }
            for index, event in enumerate(events)
        ),
    )


def source_engineering_effort_profiles() -> dict[str, SourceEngineeringEffortProfile]:
    """Return qualitative source implementation effort evidence gathered so far.

    This is a lightweight implementation metric only. It is not a scheduler,
    scorecard, governance subsystem, numerical measurement framework, or source
    registry.
    """

    return {
        "WDI": SourceEngineeringEffortProfile(
            source_code="WDI",
            acquisition="Medium",
            provider_interpretation="Medium",
            normalization="Medium",
            observed_package_construction="Low",
            deterministic_substrate="Low",
            canonical_loading="Medium",
            deterministic_verification="Medium",
            testing="Medium",
            substrate_effort_ratio="Low",
            evidence_note="Initial annual WDI vertical slice required source-specific support-bundle interpretation and loader work; later observed-package substrate mechanics reduced post-boundary effort.",
        ),
        "OECD_NAAG": SourceEngineeringEffortProfile(
            source_code="OECD_NAAG",
            acquisition="Medium",
            provider_interpretation="High",
            normalization="High",
            observed_package_construction="Low",
            deterministic_substrate="Low",
            canonical_loading="High",
            deterministic_verification="Medium",
            testing="High",
            substrate_effort_ratio="Low",
            evidence_note="OECD/SDMX required substantial provider dimension, codelist, status, staging, and loader interpretation; post-boundary package comparison and contract mechanics remained reusable.",
        ),
        "EUROSTAT_NAMQ_GDP": SourceEngineeringEffortProfile(
            source_code="EUROSTAT_NAMQ_GDP",
            acquisition="Medium",
            provider_interpretation="High",
            normalization="High",
            observed_package_construction="Low",
            deterministic_substrate="Low",
            canonical_loading="High",
            deterministic_verification="Medium",
            testing="High",
            substrate_effort_ratio="Low",
            evidence_note="Eurostat JSON-stat quarterly evidence required source-specific provider metadata, period mapping, staging, and canonical loader work; observed package and contract evidence reused existing substrate patterns.",
        ),
        "BLS_CPI": SourceEngineeringEffortProfile(
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
        ),
    }


def _contract_inspection_location(path: str) -> str:
    if path.startswith("package.observations["):
        return path.split("].", maxsplit=1)[0] + "]"
    return path.rsplit(".", maxsplit=1)[0] if "." in path else path


def _comparison_inspection_hint(comparison: ObservedPackageComparison) -> str:
    if comparison.differing_observations:
        first = comparison.differing_observations[0]
        identity = "/".join(
            [
                str(first["provider_indicator_code"]),
                str(first["provider_territory_code"]),
                str(first["provider_period_code"]),
            ]
        )
        return f"Inspect observation identity at index {first['index']}: {identity}."
    if not comparison.row_count_match:
        return "Inspect package.row_count."
    if not comparison.expected_row_count_match:
        return "Inspect package.expected_row_count."
    if not comparison.observation_count_match:
        return "Inspect package.observations."
    return "Inspect package fingerprints and package-level metadata."
