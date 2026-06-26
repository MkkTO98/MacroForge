from __future__ import annotations

from pathlib import Path
import sys

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tools.consult_metaharvest import (
    AdvisoryBuilder,
    ConsultationContract,
    ConsultationDecision,
    RetrievalContract,
    TaskClassification,
    classify_task_text,
    load_relevance_map,
)


RELEVANCE_MAP = {
    "consult_required_during": [
        "canonicalization_architecture_changes",
        "source_contract_design_changes",
        "lineage_or_validation_registry_changes",
        "orchestration_or_runtime_adoption_decisions",
        "generalized_ingestion_framework_decisions",
    ]
}


def test_routine_work_does_not_consult_metaharvest():
    classification = classify_task_text("Run existing tests and regenerate the existing fixture report without changing semantics.")

    decision = ConsultationContract().evaluate(classification, RELEVANCE_MAP)

    assert classification.task_classification_version == 1
    assert classification.primary_category == "routine_operation"
    assert decision.action == "do_not_consult"
    assert decision.matched_triggers == []


def test_valid_canonicalization_trigger_requests_consultation():
    classification = classify_task_text(
        "Revise canonicalization lifecycle semantics and report eligibility governance for accepted/provisional mappings."
    )

    decision = ConsultationContract().evaluate(classification, RELEVANCE_MAP)

    assert decision.action == "consult"
    assert "canonicalization_architecture_changes" in decision.matched_triggers


def test_consultation_contract_never_performs_retrieval():
    class ExplodingRetriever:
        def retrieve(self, *_args, **_kwargs):
            raise AssertionError("consultation contract must not perform retrieval")

    classification = classify_task_text("Change lineage validation registry semantics.")

    decision = ConsultationContract(retriever=ExplodingRetriever()).evaluate(classification, RELEVANCE_MAP)

    assert decision.action == "consult"


def test_retrieval_contract_cannot_execute_without_consult_decision(tmp_path: Path):
    retrieval = RetrievalContract(metaharvest_root=tmp_path)
    classification = classify_task_text("Change canonicalization lifecycle semantics.")
    decision = ConsultationDecision(action="do_not_consult", matched_triggers=[], rationale="routine")

    with pytest.raises(ValueError, match="requires a consult decision"):
        retrieval.retrieve(decision, classification)


def test_keyword_fallback_runs_when_primary_returns_no_records(tmp_path: Path):
    calls: list[list[str]] = []

    def runner(args: list[str], cwd: Path):
        calls.append(args)
        if "--problem" in args and args[-1] == "canonicalization_lifecycle_comparability_eligibility_check_gates":
            return 0, ""
        return 0, "records/relevant.md\nKeyword result"

    (tmp_path / "tools").mkdir()
    (tmp_path / "tools" / "query_knowledge.py").write_text("# fixture", encoding="utf-8")
    classification = classify_task_text("Change canonicalization lifecycle semantics.")
    decision = ConsultationContract().evaluate(classification, RELEVANCE_MAP)

    result = RetrievalContract(metaharvest_root=tmp_path, command_runner=runner).retrieve(decision, classification)

    assert ["--keyword", "canonicalization"] in calls
    assert result.failure is None
    assert "records/relevant.md" in result.records


def test_adjacent_fallback_runs_within_limit_when_keyword_is_empty(tmp_path: Path):
    calls: list[list[str]] = []

    def runner(args: list[str], cwd: Path):
        calls.append(args)
        if "--problem" in args and args[-1] == "transformation_lineage_asset_orchestration":
            return 0, "records/adjacent.md\nAdjacent result"
        return 0, ""

    (tmp_path / "tools").mkdir()
    (tmp_path / "tools" / "query_knowledge.py").write_text("# fixture", encoding="utf-8")
    classification = classify_task_text("Change canonicalization lifecycle semantics.")
    decision = ConsultationContract().evaluate(classification, RELEVANCE_MAP)

    result = RetrievalContract(metaharvest_root=tmp_path, command_runner=runner).retrieve(decision, classification)

    adjacent_calls = [args for args in calls if args[:1] == ["--problem"] and args[-1] != "canonicalization_lifecycle_comparability_eligibility_check_gates"]
    assert len(adjacent_calls) <= 2
    assert ["--problem", "transformation_lineage_asset_orchestration"] in calls
    assert result.records == ["records/adjacent.md"]


def test_retrieval_budgets_are_enforced_for_queries_and_deeper_reads(tmp_path: Path):
    calls: list[list[str]] = []
    for idx in range(6):
        record = tmp_path / "records" / f"r{idx}.md"
        record.parent.mkdir(exist_ok=True)
        record.write_text(f"record {idx}", encoding="utf-8")

    def runner(args: list[str], cwd: Path):
        calls.append(args)
        records = "\n".join(f"records/r{idx}.md" for idx in range(6))
        return 0, records

    (tmp_path / "tools").mkdir()
    (tmp_path / "tools" / "query_knowledge.py").write_text("# fixture", encoding="utf-8")
    classification = classify_task_text("Change validation registry semantics and check-contract governance.")
    decision = ConsultationContract().evaluate(classification, RELEVANCE_MAP)

    result = RetrievalContract(metaharvest_root=tmp_path, command_runner=runner).retrieve(decision, classification)

    assert len(calls) == 1
    assert len(result.records) == 3
    assert len(result.deeper_records) == 3


def test_absolute_deeper_read_cap_for_governance_reports_is_five(tmp_path: Path):
    for idx in range(8):
        record = tmp_path / "records" / f"r{idx}.md"
        record.parent.mkdir(exist_ok=True)
        record.write_text(f"record {idx}", encoding="utf-8")

    def runner(args: list[str], cwd: Path):
        records = "\n".join(f"records/r{idx}.md" for idx in range(8))
        return 0, records

    (tmp_path / "tools").mkdir()
    (tmp_path / "tools" / "query_knowledge.py").write_text("# fixture", encoding="utf-8")
    classification = classify_task_text("Write a governance design report changing canonicalization lifecycle semantics.")
    decision = ConsultationContract().evaluate(classification, RELEVANCE_MAP)

    result = RetrievalContract(metaharvest_root=tmp_path, command_runner=runner).retrieve(
        decision, classification, allow_governance_deeper_cap=True
    )

    assert len(result.records) == 5
    assert len(result.deeper_records) == 5


def test_retrieval_failure_is_non_blocking(tmp_path: Path):
    classification = classify_task_text("Change canonicalization lifecycle semantics.")
    decision = ConsultationContract().evaluate(classification, RELEVANCE_MAP)

    result = RetrievalContract(metaharvest_root=tmp_path).retrieve(decision, classification)

    assert result.failure == "MetaHarvest unavailable; consultation skipped."
    assert result.records == []


def test_advisory_template_is_complete_and_authority_note_is_always_present(tmp_path: Path):
    classification = TaskClassification(
        task_classification_version=1,
        primary_category="data_model_evolution",
        secondary_categories=["governance_decision"],
        durable_semantic_change=True,
        routine_execution_only=False,
        proposed_trigger_matches=["canonicalization_architecture_changes"],
        rationale="Changes canonicalization lifecycle semantics.",
    )
    decision = ConsultationDecision(
        action="consult",
        matched_triggers=["canonicalization_architecture_changes"],
        rationale="Material trigger match.",
    )
    advisory = AdvisoryBuilder().build(
        classification=classification,
        decision=decision,
        records=["records/relevant.md"],
        confidence="High",
        relevant_prior_decisions=["DEC-018"],
        recommended_considerations=["Keep MetaHarvest advisory-only."],
        ignored_because=["Runtime adoption: exceeds approved scope."],
    )

    for section in [
        "MetaHarvest Advisory",
        "Reason triggered:",
        "Retrieved records:",
        "Confidence:",
        "Relevant prior decisions:",
        "Recommended considerations:",
        "Ignored because:",
        "Authority note:",
        "task_classification_version: 1",
    ]:
        assert section in advisory
    assert "MetaHarvest provides historical architectural context only" in advisory
    assert "MacroForge retains full ownership of design decisions" in advisory
    assert "advisory rather than authoritative" in advisory


def test_confidence_semantics_accept_only_documented_values():
    builder = AdvisoryBuilder()

    assert builder.normalize_confidence("High") == "High"
    assert builder.normalize_confidence("Medium") == "Medium"
    assert builder.normalize_confidence("Low") == "Low"
    with pytest.raises(ValueError, match="Confidence must be one of"):
        builder.normalize_confidence("Certain")


def test_no_trigger_preserves_existing_macroforge_behavior_without_retrieval(tmp_path: Path):
    retrieval_called = False

    def runner(args: list[str], cwd: Path):
        nonlocal retrieval_called
        retrieval_called = True
        return 0, "unexpected"

    classification = classify_task_text("Inspect git status and run existing smoke tests.")
    decision = ConsultationContract().evaluate(classification, RELEVANCE_MAP)
    if decision.action == "consult":
        RetrievalContract(metaharvest_root=tmp_path, command_runner=runner).retrieve(decision, classification)

    assert decision.action == "do_not_consult"
    assert retrieval_called is False


def test_load_relevance_map_reads_consultation_triggers(tmp_path: Path):
    path = tmp_path / "relevance_map.yaml"
    path.write_text(
        "schema_version: 1\nconsult_required_during:\n  - canonicalization_architecture_changes\n",
        encoding="utf-8",
    )

    loaded = load_relevance_map(path)

    assert loaded["consult_required_during"] == ["canonicalization_architecture_changes"]
