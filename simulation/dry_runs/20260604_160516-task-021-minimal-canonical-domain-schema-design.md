# Dry Run Report

```json
{
  "timestamp": "20260604_160516",
  "proposal": "Complete TASK-021 as a bounded design-only schema task: write a minimal canonical-domain architecture note, proposed table definitions, migration-risk notes, test implications, DEC-011, and TASK-022 implementation follow-up. No migrations or loader changes will be implemented.",
  "risk": "medium",
  "mode": "standard_dry_run",
  "dry_run_depth": "bounded governance/design",
  "files": {
    "create": [
      "docs/architecture/minimal-canonical-domain-schema-design.md",
      "artifacts/decisions/DEC-011-minimal-canonical-domain-schema-design.md",
      "artifacts/tasks/TASK-022-implement-minimal-canonical-domain-schema-migration.md"
    ],
    "modify": [
      "artifacts/tasks/TASK-021-design-canonical-period-territory-provider-mapping-schema-evolution.md",
      "artifacts/tasks/backlog.md",
      "state/active_goal.md",
      "state/project_state.md",
      "state/architecture.md",
      "docs/roadmap.md",
      "docs/data/source-contract.md",
      "affected _SUMMARY.md files",
      "context/latest_handoff.md"
    ],
    "not_modify": [
      "db/migrations/*.sql",
      "src/macroforge/*.py",
      "tests/*.py"
    ]
  },
  "commands": [
    "python3 tools/build_context.py --project . --model-target cloud --context-mode governance --task-type architecture_decision ...",
    "python3 tools/validate_dry_run.py simulation/dry_runs/20260604_160516-task-021-minimal-canonical-domain-schema-design.md",
    "python3 tools/update_context_summaries.py --project .",
    "PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests -q && python3 tools/check_coherence.py --project . --json",
    "python3 tools/check_coherence.py --project . --json"
  ],
  "validation_plan": [
    "Validate this dry-run report before durable design writes.",
    "Read back the architecture note, DEC, TASK, and affected summaries for stale provider-centric wording.",
    "Run full tests even though this is docs/governance-only, because ProjectForge completion policy requires final verification.",
    "Run coherence after state/handoff/summary edits and again after replacing verification placeholders."
  ],
  "rollback_plan": [
    "Remove newly created DEC-011/TASK-022/design note if the design is rejected before implementation.",
    "Revert TASK-021 status/backlog/state/handoff summary edits using file diffs or prior content.",
    "No database migration, PostgreSQL write, or source promotion rollback is needed because none will be performed."
  ],
  "context_used": [
    "CONSTITUTION.md",
    "context/context_policy.yaml",
    "state/active_goal.md",
    "state/project_state.md",
    "state/architecture.md",
    "context/latest_handoff.md",
    "artifacts/tasks/TASK-021-design-canonical-period-territory-provider-mapping-schema-evolution.md",
    "docs/architecture/canonical-domain-schema-evolution.md",
    "db/migrations/001_v0_schema_foundation.sql",
    "db/migrations/002_oecd_sdmx_staging.sql",
    "docs/data/source-contract.md",
    "artifacts/decisions/DEC-010-canonical-domain-schema-evolution.md",
    "context/context_audit.md",
    "context/active_context.md"
  ],
  "decision_artifacts_checked": [
    "DEC-010-canonical-domain-schema-evolution",
    "DEC-009-third-source-spike-scope",
    "DEC-006-oecd-sdmx-postgresql-promotion",
    "DEC-004-v0-postgresql-schema-foundation"
  ],
  "approval_required": false,
  "explicit_boundaries": [
    "Do not implement migrations yet.",
    "Do not promote Eurostat to PostgreSQL yet.",
    "Do not build a generalized ingestion framework.",
    "Do not widen curated facts with provider-specific columns.",
    "Prefer explicit, boring tables over clever abstractions."
  ]
}
```
