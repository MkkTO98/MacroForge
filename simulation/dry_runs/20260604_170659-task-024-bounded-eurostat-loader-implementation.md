# Dry Run Report

```json
{
  "timestamp": "20260604_170659",
  "proposal": "Implement TASK-024 as a bounded source-specific Eurostat namq_10_gdp PostgreSQL loader: add migration 004, add RED/GREEN tests, create src/macroforge/eurostat_namq_loader.py, load only the recorded normalized fixture into isolated PostgreSQL, write a small load report, and update governance artifacts after verification.",
  "risk": "high",
  "mode": "implementation_tdd",
  "dry_run_depth": "bounded",
  "approval_required": true,
  "files": {
    "create": [
      "db/migrations/004_eurostat_namq_staging.sql",
      "src/macroforge/eurostat_namq_loader.py",
      "tests/test_eurostat_namq_loader.py",
      "artifacts/reports/eurostat-namq-load-smoke-20260604.json"
    ],
    "modify": [
      "tests/test_schema_foundation.py",
      "db/schema/v0_schema_foundation.md",
      "db/queries/schema_health_check.sql",
      "artifacts/tasks/TASK-024-implement-bounded-eurostat-postgresql-loader.md",
      "artifacts/tasks/backlog.md",
      "state/active_goal.md",
      "state/project_state.md",
      "state/architecture.md",
      "docs/roadmap.md",
      "docs/data/source-contract.md",
      "context/latest_handoff.md",
      "affected _SUMMARY.md files"
    ]
  },
  "commands": [
    "PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests/test_schema_foundation.py::test_eurostat_namq_staging_migration_exists_and_has_required_shape -q",
    "PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests/test_eurostat_namq_loader.py -q",
    "PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests -q",
    "python3 tools/check_coherence.py --project . --json"
  ],
  "validation_plan": [
    "Observe RED for missing migration 004 and missing eurostat loader module/API before implementation.",
    "Add migration 004 with only staging.eurostat_namq_observation and bounded constraints/indexes.",
    "Add source-specific loader from recorded normalized fixture only; verify generated SQL has no requests/curl/fetch surface and targets staging/curated/provider mapping tables.",
    "Apply migrations 001, 002, 003, 004 to isolated PostgreSQL, run loader twice with same run key, and assert idempotent row counts.",
    "Verify staging rows=4, fact rows=4, quarterly periods 2023 Q1/Q2, canonical territories DEU/FRA, provider mappings for DE/FR and 2023-Q1/Q2, provider dictionaries for freq/unit/s_adj/na_item/geo/time, lineage/quality checks, and unchanged fact table columns.",
    "Run full tests and ProjectForge coherence after task/state/handoff/summary updates."
  ],
  "rollback_plan": [
    "Delete new migration/module/test/report files if implementation fails before acceptance.",
    "Revert task/state/docs/handoff/summary edits to TASK-024 open state.",
    "Drop only isolated temporary PostgreSQL databases created by tests; never touch live/default macro."
  ],
  "context_used": [
    "CONSTITUTION.md",
    "instructions/GENERAL_INSTRUCTIONS.md",
    "context/context_policy.yaml",
    "state/active_goal.md",
    "state/project_state.md",
    "state/architecture.md",
    "context/latest_handoff.md",
    "artifacts/tasks/TASK-024-implement-bounded-eurostat-postgresql-loader.md",
    "artifacts/decisions/DEC-012-bounded-eurostat-postgresql-promotion.md",
    "docs/architecture/bounded-eurostat-postgresql-promotion-design.md",
    "data/metadata/eurostat/eurostat-namq-10-gdp-architecture-spike-normalized.json",
    "db/migrations/001_v0_schema_foundation.sql",
    "db/migrations/002_oecd_sdmx_staging.sql",
    "db/migrations/003_canonical_domain_dimensions.sql",
    "src/macroforge/oecd_sdmx_loader.py",
    "src/macroforge/wdi_loader.py",
    "src/macroforge/db_helpers.py",
    "tests/test_oecd_sdmx_loader.py",
    "tests/test_schema_foundation.py"
  ],
  "decision_artifacts_checked": [
    "DEC-012-bounded-eurostat-postgresql-promotion.md",
    "DEC-011-minimal-canonical-domain-schema-design.md",
    "DEC-010-canonical-domain-schema-evolution.md",
    "DEC-009-third-source-spike-scope.md"
  ],
  "boundaries": [
    "No live/default macro writes.",
    "No live Eurostat HTTP fetch in tests.",
    "No generalized JSON-stat/source/plugin framework.",
    "No broader Eurostat datasets or production ingestion.",
    "No FRED onboarding.",
    "No provider-specific fact columns.",
    "No aggregate membership, unit conversion, canonical indicator ontology, or mart/research scope.",
    "No git push."
  ]
}
```
