# TASK-034 — Implement tiny deterministic canonicalization proposal workflow

Status: complete
Created: 2026-06-05
Completed: 2026-06-13
Depends on: TASK-033
Governing decisions: DEC-019, DEC-018, DEC-016, DEC-015
Decision analysis: `docs/architecture/canonicalization-next-scope-decision-analysis.md`

## Objective

Implement the smallest deterministic proposal-generation workflow that validates the TASK-032 canonicalization state foundation before introducing AI/model dependence or broader architecture.

The task should prove this loop over the existing bounded WDI/OECD/Eurostat GDP fixture evidence:

```text
provider evidence
-> deterministic proposal generation
-> review routing
-> accepted/provisional mapping update proposal
-> audit report
```

## Scope allowed

TASK-034 may create or modify:

- a fresh implementation dry-run;
- tests written before implementation;
- a small deterministic proposal-generation helper or extension to `src/macroforge/canonicalization_state.py`;
- a deterministic audit artifact for generated proposal workflow output;
- bounded documentation/state/handoff/summary updates for closeout.

## Required properties

- Use only existing TASK-032 fixture evidence and generated state.
- Generate proposals deterministically from provider evidence rather than hard-coding static proposals as final output.
- Preserve proposal state separately from accepted/provisional mapping state.
- Preserve canonicalization run provenance with method/ruleset/model/prompt fields; model and prompt values must remain `none`.
- Route GDP-like high-impact mappings to review-required.
- Propagate unit/comparability caveats, especially WDI unknown unit metadata.
- Keep annual and quarterly frequency applicability explicit and non-aggregated.
- Do not auto-accept mappings beyond existing fixture/provisional policy.
- Produce deterministic audit output that can be diffed across runs.

## Acceptance criteria

- Fresh dry-run is created and reviewed before edits.
- TDD red check is observed before implementation.
- Tests cover deterministic generation from provider evidence.
- Tests cover proposal/accepted-state separation.
- Tests cover high-impact review routing.
- Tests cover WDI unknown unit caveat propagation.
- Tests cover annual/quarterly no-aggregation behavior.
- Tests cover deterministic audit output.
- Full tests pass.
- `python3 tools/check_coherence.py --project . --json` reports no blocks or warnings.
- Task/backlog/state/architecture/roadmap/handoff/summaries are updated after implementation.

## Explicit non-goals

Do not:

- call an LLM/model for canonicalization;
- configure prompts/model providers/embeddings;
- onboard a new source;
- live-fetch sources;
- write to live/default `macro`;
- implement PostgreSQL migrations for canonicalization state;
- implement unit conversion;
- aggregate quarterly to annual;
- create mart/dashboard/report scope beyond bounded audit output;
- expand the ontology or state surface unless directly required by the deterministic workflow;
- extract a generalized ingestion/source framework;
- add provider-specific fact columns;
- push to git.

## Outcome

Completed. TASK-034 added a tiny deterministic proposal workflow over the existing TASK-032 WDI/OECD/Eurostat GDP fixture state.

Implementation:

- Added `tests/test_canonicalization_proposal_workflow.py` with RED/GREEN coverage for provider-evidence-derived proposal generation, proposal/accepted-state separation, high-impact review routing, WDI unknown-unit caveat propagation, annual/quarterly no-aggregation behavior, no-auto-apply mapping update proposals, and deterministic audit writing.
- Extended `src/macroforge/canonicalization_state.py` with `build_deterministic_proposal_workflow`, `write_proposal_workflow_audit`, and `write_proposal_workflow_audit_from_state`.
- Wrote `artifacts/reports/canonicalization-proposal-workflow-20260613.json`.

The output contains 3 generated workflow proposals and 3 mapping update proposals, all review-required and `auto_apply: false`. Existing accepted/provisional mapping state is treated as input and is not mutated.

## Verification

Implementation verification before closeout:

```text
uvx --from pytest --with pyyaml pytest tests/test_canonicalization_proposal_workflow.py -q
....                                                                     [100%]
4 passed in 0.02s

PYTHONPATH=src python3 - <<'PY'
from macroforge.canonicalization_state import write_proposal_workflow_audit_from_state
report = write_proposal_workflow_audit_from_state()
print(report['status'])
print(report['checks'])
print(len(report['generated_mapping_proposals']), len(report['mapping_update_proposals']))
PY
succeeded
{'generated_from_provider_evidence': 'pass', 'proposal_state_separate_from_accepted_mapping_state': 'pass', 'high_impact_review_routing': 'pass', 'unknown_unit_caveat_propagated': 'pass', 'annual_quarterly_non_aggregation': 'pass', 'no_auto_apply_mapping_updates': 'pass'}
3 3

uvx --from pytest --with pyyaml pytest tests -q
................................................................         [100%]
64 passed in 6.20s
```

Post-closeout final verification is recorded in `context/latest_handoff.md`.
