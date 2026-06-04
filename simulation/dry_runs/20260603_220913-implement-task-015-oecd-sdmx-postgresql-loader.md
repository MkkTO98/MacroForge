# Dry Run Report

```json
{
  "timestamp": "20260603_220913",
  "proposal": "Implement TASK-015 as a narrow DEC-006 OECD/SDMX PostgreSQL promotion: add a source-specific staging migration, write failing tests first, implement a source-specific loader from recorded normalized evidence, verify isolated PostgreSQL idempotency, generate a small smoke report, then update task/state/handoff/summaries.",
  "risk": "medium",
  "mode": "balanced",
  "dry_run_depth": "standard_dry_run",
  "files": [
    "simulation/dry_runs/20260603_220913-implement-task-015-oecd-sdmx-postgresql-loader.md",
    "db/migrations/002_oecd_sdmx_staging.sql",
    "src/macroforge/oecd_sdmx_loader.py",
    "tests/test_oecd_sdmx_loader.py",
    "tests/test_schema_foundation.py",
    "artifacts/reports/oecd-sdmx-load-smoke-20260603.json",
    "artifacts/tasks/TASK-015-implement-oecd-sdmx-postgresql-loader.md",
    "artifacts/tasks/backlog.md",
    "state/active_goal.md",
    "state/project_state.md",
    "state/architecture.md",
    "docs/roadmap.md",
    "context/latest_handoff.md",
    "affected _SUMMARY.md files"
  ],
  "commands": [
    "python3 tools/validate_dry_run.py simulation/dry_runs/20260603_220913-implement-task-015-oecd-sdmx-postgresql-loader.md",
    "PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests/test_schema_foundation.py::test_oecd_sdmx_staging_migration_exists_and_has_required_shape -q",
    "PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests/test_oecd_sdmx_loader.py -q",
    "PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests -q",
    "python3 tools/check_coherence.py --project . --json",
    "python3 tools/update_context_summaries.py --project ."
  ],
  "validation_plan": "Use strict TDD. First add failing schema and loader tests, confirm RED, then add the minimal migration/loader for GREEN. Database verification must create/use an isolated temporary PostgreSQL database and must not target the live macro database. After implementation and smoke report generation, run targeted tests, full tests, generated-project coherence, refresh affected summaries, inspect stale curated sections, and rerun final verification.",
  "rollback_plan": "Remove the new migration, loader, loader tests, smoke report, this dry-run report, and TASK-015 state/handoff/summary edits; restore any edited schema tests/backlog/state/architecture/roadmap/handoff/summaries to the previous TASK-015-open state. No live database writes are planned, so database rollback is limited to dropping isolated temporary smoke databases if any remain.",
  "approval_required": false,
  "context_used": [
    "projectforge skill",
    "test-driven-development skill",
    "projectforge references/generated-project-task-implementation-tdd.md",
    "CONSTITUTION.md",
    "instructions/GENERAL_INSTRUCTIONS.md",
    "context/context_policy.yaml",
    "simulation/dry_run_policy.yaml",
    "state/active_goal.md",
    "state/project_state.md",
    "state/architecture.md",
    "context/latest_handoff.md",
    "artifacts/tasks/TASK-015-implement-oecd-sdmx-postgresql-loader.md",
    "artifacts/decisions/DEC-006-oecd-sdmx-postgresql-promotion.md",
    "affected folder _SUMMARY.md files"
  ],
  "decision_artifacts_checked": [
    "DEC-006 accepts only a narrow source-specific OECD/SDMX staging migration and source-specific loader.",
    "TASK-015 forbids live macro writes, live OECD fetches inside database tests, curated schema changes, and generalized SDMX framework work.",
    "The ProjectForge dry-run policy requires a dry run for schema changes before implementation."
  ]
}
```
