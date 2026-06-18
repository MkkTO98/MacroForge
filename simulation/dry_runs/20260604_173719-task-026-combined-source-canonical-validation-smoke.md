# Dry Run Report

```json
{
  "timestamp": "20260604_173719",
  "proposal": "Implement TASK-026 as a bounded combined-source canonical validation smoke: add RED/GREEN tests, add a small source-agnostic smoke module that creates an isolated temporary PostgreSQL database, applies existing migrations, runs existing WDI/OECD/Eurostat loaders against recorded evidence, runs combined canonical substrate checks, writes a JSON report, and closes out task/state/handoff/summaries.",
  "risk": "medium",
  "mode": "implementation_tdd",
  "dry_run_depth": "bounded",
  "approval_required": false,
  "context_used": [
    "CONSTITUTION.md",
    "instructions/GENERAL_INSTRUCTIONS.md",
    "context/context_policy.yaml",
    "state/active_goal.md",
    "state/project_state.md",
    "state/architecture.md",
    "context/latest_handoff.md",
    "artifacts/tasks/TASK-026-implement-combined-source-canonical-validation-smoke.md",
    "artifacts/decisions/DEC-013-post-third-source-architecture-and-next-scope.md",
    "source-specific loader modules and tests for WDI, OECD/SDMX, and Eurostat"
  ],
  "decision_artifacts_checked": [
    "DEC-013",
    "DEC-012",
    "DEC-011",
    "DEC-007"
  ],
  "files": [
    "tests/test_combined_source_smoke.py",
    "src/macroforge/combined_source_smoke.py",
    "artifacts/reports/combined-source-canonical-smoke-20260604.json"
  ],
  "files_to_update": [
    "src/macroforge/wdi_loader.py",
    "src/macroforge/oecd_sdmx_loader.py",
    "src/macroforge/eurostat_namq_loader.py",
    "artifacts/tasks/TASK-026-implement-combined-source-canonical-validation-smoke.md",
    "artifacts/tasks/backlog.md",
    "state/active_goal.md",
    "state/project_state.md",
    "state/architecture.md",
    "docs/roadmap.md",
    "context/latest_handoff.md",
    "affected _SUMMARY.md files"
  ],
  "commands": [
    "python3 tools/validate_dry_run.py simulation/dry_runs/20260604_173719-task-026-combined-source-canonical-validation-smoke.md",
    "PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests/test_combined_source_smoke.py -q",
    "PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests -q",
    "PYTHONPATH=src python3 -m macroforge.combined_source_smoke --project-root . --report artifacts/reports/combined-source-canonical-smoke-20260604.json",
    "python3 tools/update_context_summaries.py --project .",
    "PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests -q && python3 tools/check_coherence.py --project . --json"
  ],
  "validation_plan": [
    "Validate this implementation dry-run before writing tests/source.",
    "Write RED tests for plan shape, live macro refusal, source-specific/no-framework boundaries, combined report checks, and isolated PostgreSQL behavior.",
    "Implement the minimal combined smoke module and any source-scoped quality-count fixes needed for loaders to compose in one database.",
    "Run targeted tests and full test suite.",
    "Run an isolated combined smoke and read back the generated report artifact.",
    "Update task/state/handoff/summaries and run final full tests plus ProjectForge coherence."
  ],
  "rollback_plan": [
    "Remove the new combined smoke module/test/report if implementation fails before closeout.",
    "Revert source-loader quality-count patches if they change isolated behavior unexpectedly.",
    "Revert task/state/handoff/summary edits if final verification fails.",
    "No live database, live network fetch, destructive operation, or git push is planned."
  ],
  "boundaries": [
    "No new loaders, sources, migrations, schemas, or provider-specific fact columns.",
    "No live/default macro database writes; combined smoke must use isolated temporary databases and refuse macro.",
    "No live World Bank/OECD/Eurostat fetches.",
    "No generalized source/plugin/JSON-stat/SDMX framework, registry, base class, ORM, migration framework, scheduler, or mart/research output.",
    "No FRED onboarding.",
    "No git push."
  ]
}
```
