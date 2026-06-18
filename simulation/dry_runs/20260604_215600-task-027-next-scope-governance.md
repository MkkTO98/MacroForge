# Dry Run Report

```json
{
  "timestamp": "20260604_215600",
  "proposal": "Complete TASK-027 as governance-only: accept the user's preferred next scope, record DEC-014 selecting the first minimal research-facing canonical report, and open TASK-028 for implementation without implementing it now.",
  "risk": "low",
  "mode": "governance_only",
  "depth": "bounded_next_scope_decision",
  "dry_run_depth": "bounded_next_scope_decision",
  "files": [
    "artifacts/decisions/DEC-014-first-minimal-research-facing-canonical-output.md",
    "artifacts/tasks/TASK-028-implement-first-canonical-gdp-snapshot-report.md",
    "artifacts/tasks/TASK-027-decide-next-scope-after-combined-source-canonical-validation-smoke.md",
    "artifacts/tasks/backlog.md",
    "state/active_goal.md",
    "state/project_state.md",
    "state/architecture.md",
    "docs/roadmap.md",
    "context/latest_handoff.md",
    "affected _SUMMARY.md files"
  ],
  "commands": [
    "python3 tools/build_context.py --project . --model-target cloud --context-mode governance ...",
    "python3 tools/build_context.py --project . --model-target cloud --context-mode project_wide_review ...",
    "python3 tools/validate_dry_run.py simulation/dry_runs/20260604_215600-task-027-next-scope-governance.md",
    "python3 tools/update_context_summaries.py --project .",
    "PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests -q && python3 tools/check_coherence.py --project . --json",
    "python3 tools/check_coherence.py --project . --json && git status --short"
  ],
  "validation_plan": [
    "Validate this dry-run before governance edits.",
    "Record DEC-014 as accepted with explicit reasons and rejected alternatives.",
    "Open exactly one follow-on task, TASK-028, for implementation of a small canonical GDP snapshot/audit report.",
    "Do not implement report code or generate the report in TASK-027.",
    "Update state, backlog, architecture, roadmap, handoff, and summaries.",
    "Run full tests plus ProjectForge coherence after closeout edits."
  ],
  "rollback_plan": [
    "Remove DEC-014 and TASK-028 if the governance decision must be reverted.",
    "Restore TASK-027 status to open and revert state/backlog/handoff/summary changes from this dry-run."
  ],
  "approval_required": false,
  "context_used": [
    "User's explicit preferred next scope message",
    "CONSTITUTION.md",
    "instructions/GENERAL_INSTRUCTIONS.md",
    "context/context_policy.yaml",
    "state/active_goal.md",
    "state/project_state.md",
    "state/architecture.md",
    "context/latest_handoff.md",
    "artifacts/tasks/TASK-027-decide-next-scope-after-combined-source-canonical-validation-smoke.md",
    "artifacts/tasks/TASK-026-implement-combined-source-canonical-validation-smoke.md",
    "artifacts/decisions/DEC-013-post-third-source-architecture-and-next-scope.md",
    "artifacts/reports/combined-source-canonical-smoke-20260604.json",
    "context/context_audit.md"
  ],
  "decisions_checked": [
    "DEC-005",
    "DEC-007",
    "DEC-011",
    "DEC-013"
  ],
  "decision_artifacts_checked": [
    "artifacts/decisions/DEC-005-post-vertical-slice-architecture-and-next-source-scope.md",
    "artifacts/decisions/DEC-007-post-second-source-architecture-and-next-scope.md",
    "artifacts/decisions/DEC-011-minimal-canonical-domain-schema-design.md",
    "artifacts/decisions/DEC-013-post-third-source-architecture-and-next-scope.md"
  ],
  "expected_decision": "Select first minimal research-facing canonical output: a small deterministic GDP snapshot/audit report from canonical tables plus lineage/source metadata, using no staging tables except optional audit/debug sections, no new sources, no framework extraction, and no broad schema refactor."
}
```
