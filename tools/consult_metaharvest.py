#!/usr/bin/env python3
"""Trigger-gated MetaHarvest consultation helper for MacroForge.

This helper is intentionally narrow. It is meant to be called after MacroForge
recovery has identified a proposed or active task and before governance/design
reasoning proceeds. It must not be run during startup unconditionally.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Callable, Literal

try:
    import yaml
except ModuleNotFoundError:  # pragma: no cover - fallback for minimal stdlib use
    yaml = None

CLASSIFICATION_VERSION = 2
DEFAULT_METAHARVEST_ROOT = Path("/home/mkkto/srv/EIP/projects/MetaHarvest")
RELEVANCE_MAP_RELATIVE = Path("architecture/architectureharvest/relevance_map.yaml")
AUTHORITY_NOTE = (
    "Mandatory. MetaHarvest provides historical architectural context only. "
    "MacroForge retains full ownership of design decisions. Consultation is "
    "advisory rather than authoritative."
)
CONFIDENCE_VALUES = {"High", "Medium", "Low"}
MEANINGFUL_CATEGORIES = {
    "architecture_modification",
    "governance_decision",
    "data_model_evolution",
    "runtime_orchestration_adoption",
    "cross_project_boundary_change",
}


@dataclass(frozen=True)
class TaskClassification:
    task_classification_version: int
    primary_category: str
    secondary_categories: list[str]
    durable_semantic_change: bool
    routine_execution_only: bool
    proposed_trigger_matches: list[str]
    rationale: str


@dataclass(frozen=True)
class ConsultationDecision:
    action: Literal["consult", "do_not_consult"]
    matched_triggers: list[str]
    rationale: str


@dataclass(frozen=True)
class RetrievalResult:
    records: list[str]
    deeper_records: dict[str, str]
    commands_run: list[str]
    failure: str | None = None
    raw_summaries: list[str] | None = None


CommandRunner = Callable[[list[str], Path], tuple[int, str]]


def _basic_yaml_load(text: str) -> dict[str, Any]:
    """Parse the tiny relevance-map shape if PyYAML is unavailable."""
    result: dict[str, Any] = {}
    current_list_key: str | None = None
    for raw_line in text.splitlines():
        line = raw_line.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        if not line.startswith(" ") and ":" in line:
            key, value = line.split(":", 1)
            key = key.strip()
            value = value.strip()
            if value:
                result[key] = value.strip('"\'')
                current_list_key = None
            else:
                result[key] = []
                current_list_key = key
            continue
        if current_list_key and line.lstrip().startswith("- "):
            result.setdefault(current_list_key, []).append(line.lstrip()[2:].strip())
    return result


def load_relevance_map(path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    if yaml is not None:
        data = yaml.safe_load(text)
    else:
        data = _basic_yaml_load(text)
    if not isinstance(data, dict):
        raise ValueError(f"relevance map did not parse as a mapping: {path}")
    triggers = data.get("consult_required_during")
    if not isinstance(triggers, list):
        raise ValueError("relevance map missing consult_required_during list")
    return data


def classify_task_text(text: str) -> TaskClassification:
    lowered = text.lower()
    triggers: list[str] = []
    categories: list[str] = []

    routine_terms = [
        "run existing",
        "existing tests",
        "git status",
        "closeout",
        "recover state",
        "regenerate existing",
        "fixture refresh",
        "report regeneration",
        "status inspection",
    ]
    semantic_terms = [
        "semantics",
        "governance",
        "architecture",
        "lifecycle",
        "contract",
        "registry",
        "eligibility",
        "authority",
        "schema",
        "model evolution",
        "adoption",
        "capability extraction",
        "reusable dependency",
        "shared infrastructure",
    ]
    negated_semantic_change = any(
        phrase in lowered
        for phrase in ("without changing semantics", "no semantic change", "no durable semantic", "without durable semantics")
    )
    routine_execution_only = any(term in lowered for term in routine_terms) and (
        negated_semantic_change or not any(term in lowered for term in semantic_terms)
    )

    def add_category(category: str) -> None:
        if category not in categories:
            categories.append(category)

    def add_trigger(trigger: str) -> None:
        if trigger not in triggers:
            triggers.append(trigger)

    canonical_terms = [
        "canonicalization",
        "accepted/provisional",
        "accepted mapping",
        "provisional mapping",
        "mapping state",
        "comparability",
        "eligibility",
        "canonical asset",
    ]
    source_contract_terms = ["source contract", "provider metadata", "territory", "period", "unit", "frequency"]
    lineage_terms = ["lineage", "validation registry", "check-contract", "check contract", "replay evidence"]
    runtime_terms = ["dagster", "dbt", "airflow", "prefect", "openmetadata", "orchestration", "runtime", "scheduler"]
    framework_terms = ["generalized ingestion", "plugin system", "shared source abstraction", "ingestion framework"]
    foundational_capability_terms = [
        "foundational capability extraction",
        "capability extraction",
        "reusable dependency of multiple future capabilities",
        "reusable dependency for multiple future capabilities",
        "reusable dependency across capabilities",
        "shared deterministic infrastructure",
        "foundational shared infrastructure",
        "shared validation infrastructure",
        "shared replay infrastructure",
        "deterministic replay infrastructure",
        "shared diagnostics infrastructure",
        "shared canonical loading infrastructure",
        "canonical load helper extraction",
        "canonical upsert helper extraction",
        "shared lineage infrastructure",
        "shared quality-check infrastructure",
        "extracted from multiple implementations",
        "post-observed-boundary shared infrastructure",
    ]
    governance_terms = ["governance", "decision", "authority", "policy", "review lifecycle"]
    architecture_terms = ["architecture", "subsystem boundary", "operating model", "design report"]
    cross_project_terms = ["metaharvest", "projectforge", "cross-project", "project boundary"]

    if any(term in lowered for term in canonical_terms):
        add_category("data_model_evolution")
        add_trigger("canonicalization_architecture_changes")
    if any(term in lowered for term in source_contract_terms):
        add_category("data_model_evolution")
        add_trigger("source_contract_design_changes")
    if any(term in lowered for term in lineage_terms):
        add_category("data_model_evolution")
        add_trigger("lineage_or_validation_registry_changes")
    if any(term in lowered for term in runtime_terms):
        add_category("runtime_orchestration_adoption")
        add_trigger("orchestration_or_runtime_adoption_decisions")
    if any(term in lowered for term in framework_terms):
        add_category("architecture_modification")
        add_trigger("generalized_ingestion_framework_decisions")
    if any(term in lowered for term in foundational_capability_terms):
        add_category("architecture_modification")
        add_trigger("foundational_capability_extraction")
    if any(term in lowered for term in governance_terms):
        add_category("governance_decision")
    if any(term in lowered for term in architecture_terms):
        add_category("architecture_modification")
    if any(term in lowered for term in cross_project_terms):
        add_category("cross_project_boundary_change")

    durable_semantic_change = any(term in lowered for term in semantic_terms) or bool(triggers)
    if routine_execution_only or not categories:
        primary = "routine_operation" if routine_execution_only else "feature_implementation"
    else:
        priority = [
            "data_model_evolution",
            "governance_decision",
            "architecture_modification",
            "runtime_orchestration_adoption",
            "cross_project_boundary_change",
        ]
        primary = next((category for category in priority if category in categories), categories[0])

    secondary = [category for category in categories if category != primary]
    rationale = (
        "Routine execution under existing behavior; no durable semantic or governance change detected."
        if primary == "routine_operation"
        else "Task text indicates durable governance, architecture, data-model, runtime, or cross-project significance."
    )
    return TaskClassification(
        task_classification_version=CLASSIFICATION_VERSION,
        primary_category=primary,
        secondary_categories=secondary,
        durable_semantic_change=durable_semantic_change and not routine_execution_only,
        routine_execution_only=routine_execution_only,
        proposed_trigger_matches=triggers,
        rationale=rationale,
    )


class ConsultationContract:
    """Decides whether consultation should occur; never retrieves records."""

    def __init__(self, retriever: object | None = None) -> None:
        self._retriever = retriever  # retained only to prove it is not used

    def evaluate(self, classification: TaskClassification, relevance_map: dict[str, Any]) -> ConsultationDecision:
        configured = relevance_map.get("consult_required_during", [])
        if not isinstance(configured, list):
            configured = []
        configured_set = {str(item) for item in configured}
        matched = [trigger for trigger in classification.proposed_trigger_matches if trigger in configured_set]
        significant = (
            classification.primary_category in MEANINGFUL_CATEGORIES
            or bool(set(classification.secondary_categories) & MEANINGFUL_CATEGORIES)
        )
        if classification.routine_execution_only or not classification.durable_semantic_change:
            return ConsultationDecision(
                action="do_not_consult",
                matched_triggers=[],
                rationale="Routine execution or no durable semantic/governance change detected.",
            )
        if significant and matched:
            return ConsultationDecision(
                action="consult",
                matched_triggers=matched,
                rationale="Structured task classification materially matches active MetaHarvest consultation trigger(s).",
            )
        return ConsultationDecision(
            action="do_not_consult",
            matched_triggers=[],
            rationale="No material active consultation trigger matched the structured task classification.",
        )


QUERY_MAPPING: list[tuple[set[str], str, str, list[str]]] = [
    (
        {"data_model_evolution", "governance_decision", "canonicalization_architecture_changes"},
        "canonicalization_lifecycle_comparability_eligibility_check_gates",
        "canonicalization",
        ["transformation_lineage_asset_orchestration", "metadata_catalog_lineage_governance"],
    ),
    (
        {"data_model_evolution", "source_contract_design_changes"},
        "source_contract_metadata_governance",
        "source contract",
        ["metadata_catalog_lineage_governance"],
    ),
    (
        {"data_model_evolution", "governance_decision", "lineage_or_validation_registry_changes"},
        "transformation_lineage_asset_orchestration",
        "lineage",
        ["metadata_catalog_lineage_governance"],
    ),
    (
        {"runtime_orchestration_adoption", "orchestration_or_runtime_adoption_decisions"},
        "transformation_lineage_asset_orchestration",
        "orchestration",
        ["metadata_catalog_lineage_governance"],
    ),
    (
        {"architecture_modification", "foundational_capability_extraction"},
        "transformation_lineage_asset_orchestration",
        "shared deterministic infrastructure",
        ["metadata_catalog_lineage_governance", "canonicalization_lifecycle_comparability_eligibility_check_gates"],
    ),
    (
        {"architecture_modification", "generalized_ingestion_framework_decisions"},
        "generalized_ingestion_framework_decisions",
        "framework",
        ["transformation_lineage_asset_orchestration"],
    ),
]


def _query_plan(classification: TaskClassification, decision: ConsultationDecision) -> tuple[str, str, list[str]]:
    labels = {classification.primary_category, *classification.secondary_categories, *decision.matched_triggers}
    for required, problem, keyword, adjacent in QUERY_MAPPING:
        has_trigger = any(
            label.endswith("_changes") or label.endswith("_decisions") or label.endswith("_extraction")
            for label in required & labels
        )
        has_category = any(label in MEANINGFUL_CATEGORIES for label in required & labels)
        if has_trigger and has_category and (required & labels):
            return problem, keyword, adjacent[:2]
    first_trigger = decision.matched_triggers[0] if decision.matched_triggers else "canonicalization_architecture_changes"
    return first_trigger, first_trigger.replace("_", " "), []


def _default_command_runner(args: list[str], cwd: Path) -> tuple[int, str]:
    command = [sys.executable, "tools/query_knowledge.py", *args]
    completed = subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)
    output = completed.stdout
    if completed.stderr:
        output = (output + "\n" + completed.stderr).strip()
    return completed.returncode, output


def _extract_records(output: str) -> list[str]:
    records: list[str] = []
    for raw_line in output.splitlines():
        line = raw_line.strip().strip("`")
        line = re.sub(r"^[-*]\s+", "", line)
        match = re.search(r"([A-Za-z0-9_./-]+\.(?:md|json|yaml|yml))", line)
        if match:
            record = match.group(1)
            if record not in records:
                records.append(record)
    return records


class RetrievalContract:
    """Retrieves compact advisory information only after consultation is requested."""

    def __init__(self, metaharvest_root: Path = DEFAULT_METAHARVEST_ROOT, command_runner: CommandRunner | None = None) -> None:
        self.metaharvest_root = Path(metaharvest_root)
        self.command_runner = command_runner or _default_command_runner

    def retrieve(
        self,
        decision: ConsultationDecision,
        classification: TaskClassification,
        *,
        allow_governance_deeper_cap: bool = False,
    ) -> RetrievalResult:
        if decision.action != "consult":
            raise ValueError("Retrieval Contract requires a consult decision from the Consultation Contract.")
        query_tool = self.metaharvest_root / "tools" / "query_knowledge.py"
        if not self.metaharvest_root.exists() or not query_tool.exists():
            return RetrievalResult(
                records=[],
                deeper_records={},
                commands_run=[],
                failure="MetaHarvest unavailable; consultation skipped.",
                raw_summaries=[],
            )

        problem, keyword, adjacent = _query_plan(classification, decision)
        commands: list[list[str]] = [["--problem", problem], ["--keyword", keyword]]
        commands.extend([ ["--problem", item] for item in adjacent[:2] ])
        commands_run: list[str] = []
        raw_summaries: list[str] = []
        records: list[str] = []
        failure: str | None = None

        for idx, args in enumerate(commands):
            if idx > 0 and records:
                break
            commands_run.append("python3 tools/query_knowledge.py " + " ".join(args))
            code, output = self.command_runner(args, self.metaharvest_root)
            raw_summaries.append(output.strip())
            if code != 0:
                failure = f"MetaHarvest retrieval command failed with exit code {code}."
                break
            records = _extract_records(output)

        cap = 5 if allow_governance_deeper_cap else 3
        selected_records = records[:cap]
        deeper_records: dict[str, str] = {}
        for record in selected_records:
            candidate = (self.metaharvest_root / record).resolve()
            try:
                candidate.relative_to(self.metaharvest_root.resolve())
            except ValueError:
                continue
            if candidate.exists() and candidate.is_file():
                deeper_records[record] = candidate.read_text(encoding="utf-8", errors="replace")[:4000]
        return RetrievalResult(
            records=selected_records,
            deeper_records=deeper_records,
            commands_run=commands_run,
            failure=failure,
            raw_summaries=raw_summaries,
        )


class AdvisoryBuilder:
    def normalize_confidence(self, value: str) -> str:
        normalized = value.strip().capitalize()
        if normalized not in CONFIDENCE_VALUES:
            allowed = ", ".join(sorted(CONFIDENCE_VALUES))
            raise ValueError(f"Confidence must be one of: {allowed}")
        return normalized

    def infer_confidence(self, records: list[str], decision: ConsultationDecision, failure: str | None = None) -> str:
        if failure or not records:
            return "Low"
        if any(trigger in decision.matched_triggers for trigger in ("canonicalization_architecture_changes", "source_contract_design_changes")):
            return "Medium"
        return "Low"

    def build(
        self,
        *,
        classification: TaskClassification,
        decision: ConsultationDecision,
        records: list[str],
        confidence: str,
        relevant_prior_decisions: list[str] | None = None,
        recommended_considerations: list[str] | None = None,
        ignored_because: list[str] | None = None,
        failure: str | None = None,
        commands_run: list[str] | None = None,
    ) -> str:
        confidence = self.normalize_confidence(confidence)
        relevant_prior_decisions = relevant_prior_decisions or [
            "MacroForge CONSTITUTION.md and current state artifacts remain authoritative.",
            "Existing MacroForge decisions/tasks/reports retain local authority over applicability.",
        ]
        recommended_considerations = recommended_considerations or [
            "Use retrieved MetaHarvest context only as historical architectural evidence.",
            "Adopt no finding without a MacroForge-owned task, decision, or review artifact.",
            "Preserve current no-runtime-framework and source-specific-first boundaries unless separately approved.",
        ]
        ignored_because = ignored_because or [
            "Automatic adoption/task creation/runtime integration: outside Phase 1 scope and intentionally discarded."
        ]
        if failure:
            ignored_because = [*ignored_because, f"Retrieval failure: {failure}"]

        lines: list[str] = [
            "MetaHarvest Advisory",
            "Reason triggered:",
            f"- task_classification_version: {classification.task_classification_version}",
            f"- {classification.primary_category} + {', '.join(decision.matched_triggers) or 'no trigger'}: {decision.rationale}",
            "",
            "Retrieved records:",
        ]
        lines.extend(f"- {record}" for record in records) if records else lines.append("- none")
        if commands_run:
            lines.extend(["", "Commands run:"])
            lines.extend(f"- {command}" for command in commands_run)
        lines.extend(["", "Confidence:", f"- {confidence}"])
        lines.extend(["", "Relevant prior decisions:"])
        lines.extend(f"- {item}" for item in relevant_prior_decisions)
        lines.extend(["", "Recommended considerations:"])
        lines.extend(f"- {item}" for item in recommended_considerations)
        lines.extend(["", "Ignored because:"])
        lines.extend(f"- {item}" for item in ignored_because)
        lines.extend(["", "Authority note:", f"- {AUTHORITY_NOTE}"])
        return "\n".join(lines) + "\n"


def run_consultation(
    *,
    project_root: Path,
    task_text: str,
    metaharvest_root: Path = DEFAULT_METAHARVEST_ROOT,
    allow_governance_deeper_cap: bool = False,
) -> tuple[TaskClassification, ConsultationDecision, RetrievalResult | None, str]:
    relevance_map = load_relevance_map(project_root / RELEVANCE_MAP_RELATIVE)
    classification = classify_task_text(task_text)
    decision = ConsultationContract().evaluate(classification, relevance_map)
    if decision.action == "do_not_consult":
        advisory = AdvisoryBuilder().build(
            classification=classification,
            decision=decision,
            records=[],
            confidence="Low",
            recommended_considerations=["No MetaHarvest retrieval was performed; continue normal MacroForge execution."],
            ignored_because=["No active consultation trigger matched the structured task classification."],
        )
        return classification, decision, None, advisory
    retrieval = RetrievalContract(metaharvest_root=metaharvest_root).retrieve(
        decision, classification, allow_governance_deeper_cap=allow_governance_deeper_cap
    )
    builder = AdvisoryBuilder()
    advisory = builder.build(
        classification=classification,
        decision=decision,
        records=retrieval.records,
        confidence=builder.infer_confidence(retrieval.records, decision, retrieval.failure),
        failure=retrieval.failure,
        commands_run=retrieval.commands_run,
    )
    return classification, decision, retrieval, advisory


def _read_task_text(args: argparse.Namespace) -> str:
    if args.task_file:
        return Path(args.task_file).read_text(encoding="utf-8")
    if args.task_summary:
        return args.task_summary
    raise SystemExit("Provide --task-summary or --task-file. Do not run consultation during startup without task scope.")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run trigger-gated MetaHarvest consultation for a scoped MacroForge task.")
    parser.add_argument("--project-root", type=Path, default=Path.cwd())
    parser.add_argument("--metaharvest-root", type=Path, default=DEFAULT_METAHARVEST_ROOT)
    parser.add_argument("--task-summary")
    parser.add_argument("--task-file")
    parser.add_argument("--allow-governance-deeper-cap", action="store_true")
    parser.add_argument("--json", action="store_true", help="Emit classification/decision/retrieval metadata as JSON.")
    args = parser.parse_args(argv)

    task_text = _read_task_text(args)
    classification, decision, retrieval, advisory = run_consultation(
        project_root=args.project_root,
        task_text=task_text,
        metaharvest_root=args.metaharvest_root,
        allow_governance_deeper_cap=args.allow_governance_deeper_cap,
    )
    if args.json:
        print(
            json.dumps(
                {
                    "task_classification": asdict(classification),
                    "consultation_decision": asdict(decision),
                    "retrieval": asdict(retrieval) if retrieval is not None else None,
                    "advisory": advisory,
                },
                indent=2,
                sort_keys=True,
            )
        )
    else:
        print(advisory, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
