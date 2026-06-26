# TASK-043 — Implement trigger-gated MetaHarvest consultation helper

Status: complete
Date: 2026-06-26

## Objective

Implement the approved Phase 1 trigger-gated MetaHarvest consultation feature from `artifacts/reports/R-20260626-metaharvest-trigger-gated-consultation-implementation-design.md` without introducing runtime frameworks, orchestration, startup retrieval, automatic adoption, task creation, or additional cross-project authority.

## Implementation summary

Created `tools/consult_metaharvest.py`, a minimal preflight helper for the existing task-scope/governance-classification stage.

Implemented:

- versioned structured task classification with `task_classification_version: 1`;
- internal MacroForge task taxonomy, not user-configurable;
- relevance-map loading from `architecture/architectureharvest/relevance_map.yaml`;
- `ConsultationContract`, which only decides `consult` or `do_not_consult`;
- `RetrievalContract`, which only runs after a `consult` decision;
- bounded primary, keyword, and adjacent problem retrieval against MetaHarvest `tools/query_knowledge.py`;
- default deeper-read cap of 3 records and explicit governance/design cap of 5 records;
- non-blocking retrieval failure behavior;
- standardized `MetaHarvest Advisory` output with mandatory Authority note;
- confidence normalization limited to `High`, `Medium`, and `Low`;
- unit tests for contracts, trigger/no-trigger behavior, budgets, fallbacks, failures, and advisory shape;
- minimal documentation at `docs/architecture/metaharvest-trigger-gated-consultation.md`.

## Preserved boundaries

- No startup consultation.
- No eager or unconditional MetaHarvest access.
- No automatic task creation.
- No automatic adoption of retrieved findings.
- No MetaHarvest authority over MacroForge decisions.
- No runtime framework, orchestration layer, database/schema change, source onboarding, canonical evidence mutation, or report-generation system.
- No MetaHarvest state mutation.
- Existing MacroForge behavior remains unchanged when no trigger matches; routine work returns `do_not_consult` and performs no retrieval.

## Tests and verification

Targeted TDD RED result before implementation:

```text
ModuleNotFoundError: No module named 'tools.consult_metaharvest'
```

Targeted tests after implementation:

```text
uvx --from pytest --with pyyaml pytest tests/test_consult_metaharvest.py -q
13 passed in 0.04s
```

Manual CLI smoke checks:

```text
python3 tools/consult_metaharvest.py --task-summary 'Run existing tests and inspect git status.'
```

Returned `routine_operation`, `no trigger`, no retrieved records, and mandatory Authority note.

```text
python3 tools/consult_metaharvest.py --metaharvest-root /tmp/nonexistent-metaharvest --task-summary 'Revise canonicalization lifecycle semantics and report eligibility governance.'
```

Returned a triggered advisory with non-blocking retrieval failure recorded.

```text
python3 tools/consult_metaharvest.py --task-summary 'Revise canonicalization lifecycle semantics and report eligibility governance.'
```

Returned a triggered advisory using bounded primary/keyword retrieval against local MetaHarvest and selected 3 records.

Final verification is recorded in `context/latest_handoff.md` after closeout.

## Outcome

TASK-043 is complete. The Phase 1 feature is implemented as a bounded, advisory-only preflight helper. No deviations from the approved design are known.
