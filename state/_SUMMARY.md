# Folder Summary: state

## Purpose
This folder is part of the ProjectForge file-backed operating system for `state`.

## Contains
<!-- PROJECTFORGE:BEGIN-CONTAINS -->
- `.gitkeep`
- `active_goal.md`
- `architecture.md`
- `known_issues.md`
- `lessons.md`
- `project_state.md`
- `recent_changes.md`
<!-- PROJECTFORGE:END-CONTAINS -->

## Active Work
- Doctrine alignment is complete: MacroForge exists to progressively reduce recurring effort required to build, maintain, validate, canonicalize, and use trusted macroeconomic data for investment-relevant research.
- TASK-038 is complete. State now points to the recommended next bounded task: persist deferred mapping advancement requirements from TASK-038.
- `TASK-PF-20260614-continuity-recovery-adoption.md` records ProjectForge continuity/recovery adoption; fresh sessions can run `python3 tools/recover_session.py --project . --json` for bounded recovery.

## Needs Attention
- Await user approval before creating or starting the next bounded task.
- Recommended next task should persist TASK-038 deferred mapping rationale, missing evidence, semantic blockers, minimum advancement conditions, and evidence/replay pointers; do not enrich metadata, redesign lifecycle, add models, conversion/aggregation, report integration, or canonicalization logic without separate approval.
