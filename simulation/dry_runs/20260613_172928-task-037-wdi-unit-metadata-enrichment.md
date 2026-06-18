# Dry Run Report

```json
{
  "timestamp": "20260613_172928",
  "proposal": "Implement TASK-037 bounded WDI unit metadata enrichment for canonicalization evidence: add RED tests first, add the smallest fixture-backed WDI-specific metadata enrichment path for existing GDP evidence, preserve proposal-vs-accepted-state separation and no-unit-conversion policy, generate/read back a bounded audit artifact, then update task/state/handoff/summaries.",
  "risk": "medium",
  "mode": "balanced",
  "dry_run_depth": "standard_dry_run",
  "files": [
    "src/macroforge/canonicalization_state.py",
    "tests/test_canonicalization_proposal_workflow.py",
    "tests/test_canonicalization_state.py (only if existing state tests need fixture alignment)",
    "artifacts/reports/canonicalization-wdi-unit-metadata-enrichment-20260613.json",
    "artifacts/tasks/TASK-037-implement-bounded-wdi-unit-metadata-enrichment-for-canonicalization-evidence.md",
    "artifacts/tasks/backlog.md",
    "state/active_goal.md",
    "state/project_state.md",
    "state/architecture.md",
    "context/latest_handoff.md",
    "affected _SUMMARY.md files"
  ],
  "commands": [
    "python3 tools/validate_dry_run.py simulation/dry_runs/20260613_172928-task-037-wdi-unit-metadata-enrichment.md",
    "uvx --from pytest --with pyyaml pytest tests/test_canonicalization_proposal_workflow.py -q (RED before implementation)",
    "uvx --from pytest --with pyyaml pytest tests/test_canonicalization_proposal_workflow.py tests/test_canonicalization_state.py -q",
    "uvx --from pytest --with pyyaml pytest tests -q",
    "python3 tools/check_coherence.py --project . --json",
    "python3 tools/architecture_reality_audit.py --project . --write-report"
  ],
  "validation_plan": "Validate dry-run before edits. Observe a failing RED test for WDI unit metadata enrichment. Implement the smallest source-specific fixture-backed WDI GDP unit metadata path. Verify targeted tests, full tests, deterministic audit artifact read-back, generated-project coherence, architecture-to-reality audit, and final coherence after task/state/handoff/summary closeout.",
  "rollback_plan": "Revert the WDI-specific metadata fixture/enrichment code, tests, bounded audit artifact, and TASK-037 closeout/state/handoff/summary updates. No database schema, live database, live fetch, model, unit conversion, accepted mapping mutation, or report integration changes are planned.",
  "approval_required": false,
  "context_used": [
    "CONSTITUTION.md",
    "state/active_goal.md",
    "state/project_state.md",
    "state/architecture.md",
    "context/latest_handoff.md",
    "context/context_policy.yaml",
    "artifacts/decisions/DEC-021-next-scope-after-deterministic-canonicalization-proposal-workflow.md",
    "artifacts/tasks/TASK-037-implement-bounded-wdi-unit-metadata-enrichment-for-canonicalization-evidence.md",
    "artifacts/tasks/TASK-034-implement-tiny-deterministic-canonicalization-proposal-workflow.md",
    "artifacts/reports/canonicalization-proposal-workflow-20260613.json",
    "src/macroforge/canonicalization_state.py",
    "tests/test_canonicalization_proposal_workflow.py"
  ],
  "decision_artifacts_checked": [
    "DEC-021",
    "DEC-018",
    "DEC-016",
    "DEC-015"
  ],
  "explicit_non_goals": [
    "No AI/model proposal generation",
    "No live fetch without explicit approval",
    "No database migrations or live/default macro writes",
    "No unit or currency conversion",
    "No accepted/provisional mapping auto-apply or mutation",
    "No generalized metadata/source framework",
    "No new sources",
    "No unrelated report or deterministic-output churn"
  ]
}
```
