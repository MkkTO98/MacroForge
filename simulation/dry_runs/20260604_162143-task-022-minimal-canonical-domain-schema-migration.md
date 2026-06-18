# Dry Run Report

```json
{
  "timestamp": "20260604_162143",
  "proposal": "Implement TASK-022 as a bounded minimal canonical-domain schema migration with TDD: add migration 003 for structured periods, territory typing, provider period/territory mappings, provider code dictionaries, update isolated schema/loader tests and WDI/OECD loader SQL compatibility only as needed.",
  "risk": "high",
  "mode": "balanced",
  "dry_run_depth": "full_dry_run",
  "files": [
    "db/migrations/003_canonical_domain_dimensions.sql",
    "db/queries/schema_health_check.sql",
    "db/schema/v0_schema_foundation.md",
    "docs/data/v0-data-model.md",
    "docs/data/source-contract.md",
    "tests/test_schema_foundation.py",
    "tests/test_wdi_loader.py",
    "tests/test_oecd_sdmx_loader.py",
    "src/macroforge/wdi_loader.py",
    "src/macroforge/oecd_sdmx_loader.py",
    "artifacts/tasks/TASK-022-implement-minimal-canonical-domain-schema-migration.md",
    "artifacts/tasks/backlog.md",
    "state/active_goal.md",
    "state/project_state.md",
    "state/architecture.md",
    "context/latest_handoff.md",
    "affected _SUMMARY.md files"
  ],
  "commands": [
    "PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests/test_schema_foundation.py::<targeted new tests> -q",
    "PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests/test_wdi_loader.py tests/test_oecd_sdmx_loader.py -q",
    "PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests -q",
    "python3 tools/check_coherence.py --project . --json",
    "python3 tools/update_context_summaries.py --project ."
  ],
  "validation_plan": [
    "Write RED schema tests before migration implementation for new 003 migration presence, table/constraint shape, isolated PostgreSQL period/territory/mapping constraints, and fact table non-widening.",
    "Run targeted schema tests and verify failure for missing migration/schema.",
    "Implement migration 003 and minimal docs/health-query updates.",
    "Update WDI/OECD loader SQL and isolated loader tests so annual smoke remains idempotent after 003 is applied.",
    "Run targeted schema and loader tests against isolated temporary PostgreSQL databases only.",
    "Run full test suite and ProjectForge coherence after governance/state/summary updates."
  ],
  "rollback_plan": [
    "Revert migration 003, test edits, loader SQL edits, docs/state/task/handoff/summary changes from git/worktree if validation fails.",
    "No live macro database writes are allowed, so rollback is file-only plus automatic temporary database drops."
  ],
  "approval_required": true,
  "context_used": [
    "CONSTITUTION.md",
    "instructions/GENERAL_INSTRUCTIONS.md",
    "context/context_policy.yaml",
    "state/active_goal.md",
    "state/project_state.md",
    "state/architecture.md",
    "context/latest_handoff.md",
    "artifacts/tasks/TASK-022-implement-minimal-canonical-domain-schema-migration.md",
    "docs/architecture/minimal-canonical-domain-schema-design.md",
    "db/migrations/001_v0_schema_foundation.sql",
    "db/migrations/002_oecd_sdmx_staging.sql",
    "tests/test_schema_foundation.py",
    "tests/test_wdi_loader.py",
    "tests/test_oecd_sdmx_loader.py",
    "src/macroforge/wdi_loader.py",
    "src/macroforge/oecd_sdmx_loader.py"
  ],
  "decision_artifacts_checked": [
    "DEC-011-minimal-canonical-domain-schema-design.md",
    "DEC-010-canonical-domain-schema-evolution.md",
    "DEC-007-post-second-source-architecture-and-next-scope.md",
    "DEC-005-post-vertical-slice-architecture-and-next-source-scope.md"
  ],
  "scope_boundaries": [
    "Do not edit 001_v0_schema_foundation.sql as the primary change path.",
    "Do not promote Eurostat to PostgreSQL.",
    "Do not add a FRED loader.",
    "Do not build a generalized ingestion/source framework.",
    "Do not widen curated.fact_observation with provider-specific columns.",
    "Do not add aggregate membership history, unit conversion, indicator ontology, research/mart scope, or live macro writes."
  ]
}
```
