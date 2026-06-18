# Dry Run Report

```json
{
  "timestamp": "20260604_223659",
  "proposal": "Implement TASK-028: first minimal research-facing canonical GDP snapshot/audit report from existing canonical facts and meta lineage/source metadata, reusing an isolated combined-source database path.",
  "risk": "medium",
  "mode": "implementation_tdd",
  "depth": "bounded_report_artifact_generation",
  "dry_run_depth": "bounded_report_artifact_generation",
  "files": [
    "tests/test_canonical_gdp_snapshot.py",
    "src/macroforge/canonical_gdp_snapshot.py",
    "artifacts/reports/canonical-gdp-snapshot-20260604.json",
    "artifacts/reports/canonical-gdp-snapshot-20260604.md",
    "artifacts/tasks/TASK-028-implement-first-canonical-gdp-snapshot-report.md",
    "artifacts/tasks/backlog.md",
    "state/active_goal.md",
    "state/project_state.md",
    "state/architecture.md",
    "docs/roadmap.md",
    "context/latest_handoff.md",
    "affected _SUMMARY.md files"
  ],
  "commands": [
    "python3 tools/validate_dry_run.py simulation/dry_runs/20260604_223659-task-028-first-canonical-gdp-snapshot-report.md",
    "PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests/test_canonical_gdp_snapshot.py -q",
    "PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests/test_canonical_gdp_snapshot.py -q",
    "PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests -q",
    "PYTHONPATH=src python3 -m macroforge.canonical_gdp_snapshot --project-root . --json-report artifacts/reports/canonical-gdp-snapshot-20260604.json --markdown-report artifacts/reports/canonical-gdp-snapshot-20260604.md",
    "python3 tools/update_context_summaries.py --project .",
    "PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests -q && python3 tools/check_coherence.py --project . --json",
    "python3 tools/check_coherence.py --project . --json && git status --short"
  ],
  "validation_plan": [
    "Validate this dry-run before writing tests/source.",
    "Write RED tests proving the missing report generator, isolated safe database planning, canonical/meta-only SQL boundary, deterministic JSON/Markdown writers, and generated report shape.",
    "Implement the minimal report generator to pass tests.",
    "Generate real deterministic report artifacts only after writer tests pass.",
    "Run targeted tests, full tests, real report command, and ProjectForge coherence.",
    "Read back generated report artifacts and update task/state/handoff/summaries after verification."
  ],
  "rollback_plan": [
    "Remove tests/test_canonical_gdp_snapshot.py and src/macroforge/canonical_gdp_snapshot.py if implementation is abandoned before closeout.",
    "Remove generated canonical GDP snapshot report artifacts if report generation fails acceptance criteria.",
    "Restore TASK-028/backlog/state/handoff/summaries to open pre-implementation state if closeout is reverted."
  ],
  "approval_required": false,
  "context_used": [
    "CONSTITUTION.md",
    "state/active_goal.md",
    "state/project_state.md",
    "state/architecture.md",
    "context/latest_handoff.md",
    "context/context_policy.yaml",
    "artifacts/tasks/TASK-028-implement-first-canonical-gdp-snapshot-report.md",
    "artifacts/decisions/DEC-014-first-minimal-research-facing-canonical-output.md",
    "src/macroforge/combined_source_smoke.py",
    "tests/test_combined_source_smoke.py",
    "src/macroforge/db_helpers.py",
    "db/schema/v0_schema_foundation.md",
    "db/migrations/001_v0_schema_foundation.sql",
    "db/migrations/003_canonical_domain_dimensions.sql"
  ],
  "decisions_checked": [
    "DEC-014"
  ],
  "decision_artifacts_checked": [
    "artifacts/decisions/DEC-014-first-minimal-research-facing-canonical-output.md"
  ],
  "non_goals_enforced": [
    "no new source",
    "no live source fetch",
    "no live/default macro database write",
    "no migration",
    "no broad schema refactor",
    "no provider-specific fact columns",
    "no unit conversion",
    "no canonical indicator ontology",
    "no quarterly-to-annual aggregation",
    "no mart schema",
    "no dashboard/UI/notebook",
    "no generalized ingestion framework",
    "no orchestration/scheduling",
    "no git push"
  ]
}
```
