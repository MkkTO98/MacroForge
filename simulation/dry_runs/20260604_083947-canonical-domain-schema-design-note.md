# Dry Run Report

```json
{
  "timestamp": "20260604_083947",
  "proposal": "Produce a canonical-domain schema design note comparing provider-centric schema evolution with canonical-domain schema evolution after TASK-020, reflecting the user's correction that provider representations must not become canonical identities.",
  "risk": "medium",
  "dry_run_depth": "standard_dry_run",
  "mode": "balanced",
  "files": {
    "create": [
      "docs/architecture/canonical-domain-schema-evolution.md",
      "artifacts/decisions/DEC-010-canonical-domain-schema-evolution.md",
      "artifacts/tasks/TASK-021-decide-canonical-period-territory-provider-metadata-schema.md"
    ],
    "update": [
      "state/active_goal.md",
      "state/project_state.md",
      "state/architecture.md",
      "artifacts/tasks/backlog.md",
      "docs/architecture/_SUMMARY.md",
      "artifacts/decisions/_SUMMARY.md",
      "artifacts/tasks/_SUMMARY.md",
      "docs/_SUMMARY.md",
      "state/_SUMMARY.md",
      "context/latest_handoff.md"
    ]
  },
  "commands": [
    "python3 tools/build_context.py --project . --model-target cloud --context-mode governance ...",
    "python3 tools/update_context_summaries.py --project .",
    "python3 tools/check_coherence.py --project . --json"
  ],
  "validation_plan": [
    "Validate this dry-run with tools/validate_dry_run.py.",
    "Write the design note as a durable architecture document, not an executable migration.",
    "Record DEC-010 so future schema work preserves source-agnostic canonical identities.",
    "Open TASK-021 for later schema decision/implementation planning; do not implement schema changes now.",
    "Refresh/inspect affected summaries and run coherence after governance edits."
  ],
  "rollback_plan": [
    "Remove created DEC/TASK/design-note files if the design note direction is rejected.",
    "Revert state/backlog/summary/handoff patches to prior TASK-020-only next-step wording."
  ],
  "context_used": [
    "CONSTITUTION.md",
    "instructions/GENERAL_INSTRUCTIONS.md",
    "context/context_policy.yaml",
    "context/active_context.md",
    "context/context_audit.md",
    "state/active_goal.md",
    "state/project_state.md",
    "state/architecture.md",
    "context/latest_handoff.md",
    "db/migrations/001_v0_schema_foundation.sql",
    "docs/data/v0-data-model.md",
    "artifacts/reports/eurostat-third-source-architecture-spike-20260604.md",
    "artifacts/decisions/DEC-009-third-source-spike-scope.md"
  ],
  "decision_artifacts_checked": [
    "DEC-004",
    "DEC-005",
    "DEC-007",
    "DEC-009"
  ],
  "approval_required": false
}
```
