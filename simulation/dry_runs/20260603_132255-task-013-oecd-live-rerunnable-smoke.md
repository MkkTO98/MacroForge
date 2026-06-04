# Dry Run Report

```json
{
  "timestamp": "20260603_132255",
  "proposal": "Open and implement TASK-013 to harden the existing OECD/SDMX source-specific evidence slice into a live no-key rerunnable smoke command. The command should fetch the public OECD endpoint, write only project-layout raw/metadata/report artifacts, remain source-specific, and avoid PostgreSQL/schema/live macro database effects.",
  "risk": "medium",
  "mode": "balanced",
  "dry_run_depth": "standard_dry_run",
  "files": [
    "artifacts/tasks/TASK-013-harden-oecd-sdmx-live-rerunnable-smoke-command.md",
    "src/macroforge/oecd_sdmx.py",
    "tests/test_oecd_sdmx.py",
    "artifacts/reports/oecd-sdmx-live-smoke-20260603.md",
    "data/raw/oecd_sdmx/oecd_sdmx_naag_2020_2021_raw.xml",
    "data/metadata/oecd_sdmx/oecd-sdmx-smoke-normalized.json",
    "artifacts/reports/oecd-sdmx-smoke-20260603.md",
    "docs/roadmap.md",
    "artifacts/tasks/backlog.md",
    "state/active_goal.md",
    "state/project_state.md",
    "state/architecture.md",
    "context/latest_handoff.md",
    "affected _SUMMARY.md files"
  ],
  "commands": [
    "PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests/test_oecd_sdmx.py::<new_test> -q",
    "PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests/test_oecd_sdmx.py -q",
    "PYTHONPATH=src python3 -m macroforge.oecd_sdmx --project-root . --fetch --territory AUS --territory USA --measure B1GQ",
    "PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests -q",
    "python3 tools/update_context_summaries.py --project .",
    "python3 tools/check_coherence.py --project . --json"
  ],
  "validation_plan": "Write a failing fixture-backed test that CLI/main can write project-layout artifacts instead of generic raw/metadata/reports directories. Implement minimal --project-root support/default bounded filters, run targeted tests, run live no-key OECD command once if network/upstream access succeeds, confirm no root-level raw/metadata/reports directories, then update governance/handoff/summaries and rerun full tests/coherence.",
  "rollback_plan": "Revert edits to src/macroforge/oecd_sdmx.py and tests/test_oecd_sdmx.py if tests cannot be made green. Remove only corrupt TASK-013-generated OECD project-layout artifacts if needed. Do not touch PostgreSQL schema, live macro database, credentials, or git remotes.",
  "approval_required": false,
  "context_used": [
    "ProjectForge generated-project instructions from AGENTS.md",
    "projectforge skill",
    "test-driven-development skill",
    "CONSTITUTION.md",
    "state/active_goal.md",
    "state/project_state.md",
    "state/architecture.md",
    "context/latest_handoff.md",
    "artifacts/tasks/backlog.md",
    "docs/roadmap.md",
    "simulation/dry_run_policy.yaml",
    "TASK-012 code/tests/artifacts"
  ],
  "decision_artifacts_checked": [
    "artifacts/decisions/DEC-005-post-vertical-slice-architecture-and-next-source-scope.md"
  ]
}
```
