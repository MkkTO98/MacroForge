# Dry Run Report

```json
{
  "timestamp": "20260603_214803",
  "proposal": "Open TASK-014 as a focused OECD/SDMX PostgreSQL promotion design task before any loader, schema, live database, or generalized SDMX framework work.",
  "risk": "low",
  "mode": "balanced",
  "dry_run_depth": "micro_preflight",
  "files": [
    "simulation/dry_runs/20260603_214803-open-task-014-oecd-postgresql-promotion-design.md",
    "artifacts/tasks/TASK-014-design-oecd-sdmx-postgresql-promotion.md",
    "artifacts/tasks/backlog.md",
    "state/active_goal.md",
    "state/project_state.md",
    "state/architecture.md",
    "docs/roadmap.md",
    "context/latest_handoff.md",
    "affected _SUMMARY.md files"
  ],
  "commands": [
    "python3 tools/validate_dry_run.py simulation/dry_runs/20260603_214803-open-task-014-oecd-postgresql-promotion-design.md",
    "python3 tools/update_context_summaries.py --project .",
    "PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests -q",
    "python3 tools/check_coherence.py --project . --json"
  ],
  "validation_plan": "Validate the dry-run report, refresh affected summaries, run the full test suite, and run generated-project coherence. This task-opening step does not modify source code, schema, or database contents.",
  "rollback_plan": "Delete the TASK-014 artifact and this dry-run report, then restore backlog, state, architecture, roadmap, handoff, and affected summaries to their prior TASK-013-complete state.",
  "approval_required": false,
  "context_used": [
    "CONSTITUTION.md",
    "instructions/GENERAL_INSTRUCTIONS.md",
    "context/context_policy.yaml",
    "context/latest_handoff.md",
    "state/active_goal.md",
    "state/project_state.md",
    "state/architecture.md",
    "artifacts/tasks/backlog.md",
    "artifacts/tasks/TASK-013-harden-oecd-sdmx-live-rerunnable-smoke-command.md",
    "artifacts/decisions/DEC-005-post-vertical-slice-architecture-and-next-source-scope.md",
    "docs/data/source-contract.md",
    "docs/roadmap.md",
    "artifacts/reports/oecd-sdmx-live-smoke-20260603.md",
    "simulation/dry_run_policy.yaml"
  ],
  "decision_artifacts_checked": [
    "DEC-005 keeps the immediate architecture minimal and requires a decision before altering schema when second-source grain does not fit the current curated observation model.",
    "TASK-013 outcome explicitly recommends this design task before loader/schema work."
  ]
}
```
