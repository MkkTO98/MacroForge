# Dry Run Report

```json
{
  "timestamp": "20260604_075457",
  "proposal": "Implement TASK-019 as a bounded source-specific OECD/SDMX codelist and label enrichment spike. Use TDD to add fixture-backed structure/codelist parsing tests, then project-layout metadata/report writer tests, then minimal source-specific implementation in macroforge.oecd_sdmx. Generate bounded metadata/report artifacts from recorded fixture/local evidence only; do not perform live fetches, schema changes, database writes, or framework extraction.",
  "risk": "medium",
  "mode": "balanced",
  "dry_run_depth": "standard_dry_run",
  "files": [
    "simulation/dry_runs/20260604_075457-implement-task-019-oecd-sdmx-codelist-label-enrichment.md",
    "tests/test_oecd_sdmx_codelists.py",
    "tests/fixtures/oecd_sdmx_naag_structure_sample.xml",
    "src/macroforge/oecd_sdmx.py",
    "data/raw/oecd_sdmx/oecd_sdmx_naag_structure_20260604.xml",
    "data/metadata/oecd_sdmx/oecd-sdmx-codelist-labels-20260604.json",
    "artifacts/reports/oecd-sdmx-codelist-labels-20260604.md",
    "docs/data/source-contract.md",
    "artifacts/tasks/TASK-019-spike-oecd-sdmx-codelist-label-enrichment.md",
    "artifacts/tasks/backlog.md",
    "state/active_goal.md",
    "state/project_state.md",
    "state/architecture.md",
    "docs/roadmap.md",
    "context/latest_handoff.md",
    "affected _SUMMARY.md files"
  ],
  "commands": [
    "python3 tools/validate_dry_run.py simulation/dry_runs/20260604_075457-implement-task-019-oecd-sdmx-codelist-label-enrichment.md",
    "PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests/test_oecd_sdmx_codelists.py -q",
    "PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests/test_oecd_sdmx.py tests/test_oecd_sdmx_codelists.py -q",
    "PYTHONPATH=src python3 -m macroforge.oecd_sdmx --input-structure-xml tests/fixtures/oecd_sdmx_naag_structure_sample.xml --project-root . --write-codelist-labels",
    "PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests -q",
    "python3 tools/check_coherence.py --project . --json",
    "python3 tools/update_context_summaries.py --project .",
    "python3 tools/check_coherence.py --project . --json"
  ],
  "validation_plan": "Use strict TDD. First add tests/test_oecd_sdmx_codelists.py and a tiny structure/codelist XML fixture, then run the targeted test and confirm RED because macroforge.oecd_sdmx lacks the requested codelist parsing/enrichment API. Implement only source-specific parsing for bounded concepts/codes and verify GREEN. Add writer/report tests before generating real project-layout artifacts. Generate artifacts only from recorded fixture/local XML, not live HTTP. Run targeted tests, full tests, coherence, refresh/inspect affected summaries, update task/state/handoff, and rerun final verification after governance edits.",
  "rollback_plan": "Remove tests/test_oecd_sdmx_codelists.py, tests/fixtures/oecd_sdmx_naag_structure_sample.xml, generated codelist raw/metadata/report artifacts, and the dry-run report; revert edits to src/macroforge/oecd_sdmx.py, docs/data/source-contract.md, TASK-019/backlog/state/architecture/roadmap/handoff/summaries. No schema changes, live macro writes, dependency installs, live fetches, git pushes, or production data changes are planned.",
  "approval_required": false,
  "context_used": [
    "projectforge skill",
    "projectforge reference generated-project-task-implementation-tdd.md",
    "test-driven-development skill",
    "CONSTITUTION.md",
    "instructions/GENERAL_INSTRUCTIONS.md",
    "context/context_policy.yaml",
    "simulation/dry_run_policy.yaml",
    "state/active_goal.md",
    "state/project_state.md",
    "state/architecture.md",
    "context/latest_handoff.md",
    "artifacts/tasks/TASK-019-spike-oecd-sdmx-codelist-label-enrichment.md",
    "artifacts/decisions/DEC-008-next-scope-after-shared-validation-reporting.md",
    "src/macroforge/oecd_sdmx.py",
    "tests/test_oecd_sdmx.py",
    "tests/fixtures/oecd_sdmx_naag_sample.xml"
  ],
  "decision_artifacts_checked": [
    "DEC-008 accepts bounded source-specific OECD/SDMX codelist and label enrichment before a third-source spike.",
    "DEC-008 rejects generalized SDMX/source framework work, schema changes, live macro writes, broad codelist harvesting, third-source onboarding, and research/mart implementation in TASK-019.",
    "TASK-019 requires fresh implementation dry-run, TDD, recorded fixture evidence before live no-key commands, metadata/report artifacts with endpoint/checksum/bytes/labels/limitations, full tests, coherence, and task/state/handoff/summary updates."
  ]
}
```
