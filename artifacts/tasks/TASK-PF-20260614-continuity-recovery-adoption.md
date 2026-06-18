# Task: Adopt ProjectForge Continuity and Recovery Framework

Date: 2026-06-14
Status: Complete
Type: ProjectForge framework adoption / project-local operating-system update

## Why this task exists

ProjectForge added a small continuity and recovery framework for fast bounded session recovery and near-quota shutdown hygiene. MacroForge was explicitly named as an existing project that should adopt the capability.

This task is not TASK-038 and does not start the next MacroForge domain task. The existing recommendation-only next candidate remains unchanged: a bounded review-to-accepted/provisional canonicalization lifecycle validation task if the user approves it later.

## Existing MacroForge mechanisms extended

- Priority startup files: `state/active_goal.md`, `state/project_state.md`, `state/architecture.md`, and `context/latest_handoff.md`.
- Task/decision artifacts under `artifacts/`.
- `tools/build_context.py`, `tools/context_health.py`, and `tools/check_coherence.py`.
- `context/context_policy.yaml` task completion and context loading policy.
- `AGENTS.md` startup and completion instructions.

## Changes adopted

- Added `tools/recover_session.py`.
- Added `recovery/continuity_framework.md`.
- Updated `AGENTS.md` with the bounded recovery command, standard closeout sufficiency, and near-quota continuity priority.
- Updated `context/context_policy.yaml` with `continuity_recovery` policy, including `standard_closeout_command` and `standard_closeout_order`.
- Updated `tools/check_coherence.py` so continuity framework files and standard closeout/recovery command contracts are part of the generated-project coherence contract.
- Hardened `tools/recover_session.py` so referenced `artifacts/tasks/_SUMMARY.md` files are not treated as active tasks.

## Verification

Initial adoption smoke checks run from MacroForge:

```text
python3 tools/recover_session.py --project . --json
```

Result: command returned 0 and reported `raw_logs_read: false`, `repository_wide_scan: false`, current project state, TASK-037 as active/recent task, recent decisions, blockers, next recommended action, and resume procedure.

```text
python3 tools/check_coherence.py --project . --mode generated --json
{
  "mode": "generated",
  "blocks": [],
  "warnings": []
}
```

Final verification is recorded in `context/latest_handoff.md` after ProjectForge-level closeout.

## Boundaries

- No MacroForge domain implementation was started.
- No TASK-038 was created.
- No source ingestion, schema change, database migration, live write, AI/model call, or git push was performed.
