# Dry Run Report

```json
{
  "timestamp": "20260604_073353",
  "proposal": "Implement TASK-017 as a bounded behavior-preserving hardening pass: add tests first for tiny shared mechanical helpers, extract SQL/JSON literal rendering, psql execution/scalar helpers, integer/count parsing, and JSON report writing into a small non-framework utility module, update WDI and OECD/SDMX loaders/validation to use those helpers, then verify all source-specific SQL, reports, isolated PostgreSQL tests, and project coherence still pass.",
  "risk": "medium",
  "mode": "balanced",
  "dry_run_depth": "standard_dry_run",
  "files": [
    "simulation/dry_runs/20260604_073353-implement-task-017-shared-validation-loader-reporting.md",
    "src/macroforge/db_helpers.py",
    "src/macroforge/wdi_loader.py",
    "src/macroforge/oecd_sdmx_loader.py",
    "src/macroforge/wdi_validation.py",
    "tests/test_db_helpers.py",
    "tests/test_wdi_loader.py",
    "tests/test_oecd_sdmx_loader.py",
    "tests/test_wdi_validation.py",
    "artifacts/tasks/TASK-017-harden-shared-validation-and-loader-reporting.md",
    "artifacts/tasks/backlog.md",
    "state/active_goal.md",
    "state/project_state.md",
    "state/architecture.md",
    "context/latest_handoff.md",
    "affected _SUMMARY.md files"
  ],
  "commands": [
    "python3 tools/validate_dry_run.py simulation/dry_runs/20260604_073353-implement-task-017-shared-validation-loader-reporting.md",
    "PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests/test_db_helpers.py -q",
    "PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests/test_wdi_loader.py tests/test_oecd_sdmx_loader.py tests/test_wdi_validation.py -q",
    "PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests -q",
    "python3 tools/check_coherence.py --project . --json",
    "python3 tools/update_context_summaries.py --project .",
    "python3 tools/check_coherence.py --project . --json"
  ],
  "validation_plan": "Use strict TDD. First add tests for the wished-for shared helper API and confirm RED because src/macroforge/db_helpers.py does not exist. Implement only the smallest helper surface required for GREEN: sql_literal, jsonb_literal, run_psql_file, psql_scalar, psql_int, parse_pipe_counts, and write_json_report. Update WDI/OECD loader and WDI validation code after the helper tests are green, preserving public functions and report payload compatibility. Run targeted tests, full tests, generated-project coherence, refresh affected summaries, inspect curated summary sections, and rerun final verification after governance/summary edits.",
  "rollback_plan": "Remove src/macroforge/db_helpers.py and tests/test_db_helpers.py, revert edits to WDI/OECD loader and validation modules, remove this dry-run report, and restore TASK-017/backlog/state/architecture/handoff/summary edits to the TASK-017-open state. No schema changes, live fetches, live macro writes, dependency installs, git pushes, or production data changes are planned.",
  "approval_required": false,
  "context_used": [
    "projectforge skill",
    "test-driven-development skill",
    "CONSTITUTION.md",
    "instructions/GENERAL_INSTRUCTIONS.md",
    "context/context_policy.yaml",
    "simulation/dry_run_policy.yaml",
    "state/active_goal.md",
    "state/project_state.md",
    "state/architecture.md",
    "context/latest_handoff.md",
    "artifacts/tasks/TASK-017-harden-shared-validation-and-loader-reporting.md",
    "artifacts/decisions/DEC-007-post-second-source-architecture-and-next-scope.md",
    "src/macroforge/_SUMMARY.md",
    "tests/_SUMMARY.md",
    "artifacts/tasks/_SUMMARY.md",
    "artifacts/decisions/_SUMMARY.md",
    "artifacts/reports/_SUMMARY.md",
    "src/macroforge/wdi_loader.py",
    "src/macroforge/oecd_sdmx_loader.py",
    "src/macroforge/wdi_validation.py",
    "src/macroforge/wdi_smoke.py",
    "tests/test_wdi_loader.py",
    "tests/test_oecd_sdmx_loader.py",
    "tests/test_wdi_validation.py",
    "tests/test_wdi_smoke.py"
  ],
  "decision_artifacts_checked": [
    "DEC-007 accepts only tiny shared mechanical helper plus validation/reporting hardening across WDI and OECD/SDMX.",
    "DEC-007 rejects generalized source/SDMX frameworks, plugin registries, source base classes, ORM/migration/orchestration tooling, schema changes, live fetches, and live macro writes.",
    "TASK-017 requires a medium-risk fresh implementation dry-run, tests before refactoring, preservation of source-specific loader behavior/report counts, full tests, generated-project coherence, and task/state/handoff/summary updates."
  ]
}
```
