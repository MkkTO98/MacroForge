# Dry Run Report

```json
{
  "timestamp": "2026-06-18T12:00:00Z",
  "proposal": "Open and implement TASK-040: deterministic OECD unit-basis comparability split for existing GDP canonicalization evidence, using TASK-039 advancement requirements as input.",
  "risk": "medium",
  "mode": "implementation",
  "dry_run_depth": "bounded",
  "files": {
    "create": [
      "artifacts/tasks/TASK-040-implement-oecd-unit-basis-comparability-split.md",
      "artifacts/reports/canonicalization-oecd-unit-basis-comparability-20260618.json",
      "artifacts/reports/canonicalization-oecd-unit-basis-comparability-20260618.md"
    ],
    "modify": [
      "src/macroforge/canonicalization_state.py",
      "tests/test_canonicalization_proposal_workflow.py",
      "artifacts/tasks/backlog.md",
      "state/active_goal.md",
      "state/project_state.md",
      "state/architecture.md",
      "state/recent_changes.md",
      "context/latest_handoff.md",
      "artifacts/reports/_SUMMARY.md",
      "artifacts/tasks/_SUMMARY.md"
    ],
    "forbidden": [
      "db/migrations/*",
      "artifacts/manifests/canonical_assets.json",
      "live/default macro database",
      "new source onboarding",
      "accepted/base mapping state mutation"
    ]
  },
  "commands": [
    "uvx --from pytest --with pyyaml pytest tests/test_canonicalization_proposal_workflow.py -q",
    "PYTHONPATH=src python3 - <<'PY' ... write_oecd_unit_basis_comparability_audit_from_state() ... PY",
    "uvx --from pytest --with pyyaml pytest tests -q",
    "python3 tools/check_coherence.py --project . --json",
    "python3 tools/context_health.py --project . --json"
  ],
  "validation_plan": [
    "Confirm RED test fails because the OECD unit-basis split helper does not exist yet.",
    "Implement deterministic basis-aware classifier/writer with no model calls, no conversion, no aggregation, and no accepted-state mutation.",
    "Generate and read back JSON/Markdown artifacts.",
    "Run targeted and full tests plus coherence/context-health after closeout edits."
  ],
  "rollback_plan": [
    "Revert source/test/task/report/state/handoff edits with git checkout before commit if validation fails.",
    "Do not touch live databases or remote git state."
  ],
  "approval_required": false,
  "context_used": [
    "CONSTITUTION.md",
    "state/active_goal.md",
    "state/project_state.md",
    "state/architecture.md",
    "context/latest_handoff.md",
    "artifacts/tasks/TASK-038-simulate-bounded-canonicalization-review-lifecycle.md",
    "artifacts/tasks/TASK-039-persist-deferred-mapping-advancement-requirements.md",
    "artifacts/reports/canonicalization-deferred-mapping-advancement-requirements-20260618.json",
    "artifacts/decisions/DEC-018-minimal-ai-assisted-canonicalization-layer.md",
    "artifacts/decisions/DEC-021-next-scope-after-deterministic-canonicalization-proposal-workflow.md"
  ],
  "decisions_checked": [
    "DEC-018",
    "DEC-021",
    "TASK-038 outcome boundaries",
    "TASK-039 advancement requirements"
  ],
  "decision_artifacts_checked": [
    "artifacts/decisions/DEC-018-minimal-ai-assisted-canonicalization-layer.md",
    "artifacts/decisions/DEC-021-next-scope-after-deterministic-canonicalization-proposal-workflow.md",
    "artifacts/tasks/TASK-038-simulate-bounded-canonicalization-review-lifecycle.md",
    "artifacts/tasks/TASK-039-persist-deferred-mapping-advancement-requirements.md",
    "artifacts/reports/canonicalization-deferred-mapping-advancement-requirements-20260618.json"
  ]
}
```
