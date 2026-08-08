# Folder Summary: state

## Purpose
Current project state files: active goal, architecture posture, project state, issues, lessons, and recent changes.

## Contains
<!-- PROJECTFORGE:BEGIN-CONTAINS -->
- `active_goal.md`
- `architecture.md`
- `known_issues.md`
- `lessons.md`
- `project_state.md`
- `recent_changes.md`
<!-- PROJECTFORGE:END-CONTAINS -->

## Active Work
- `active_goal.md` and `project_state.md` record `TASK-PF-20260801` as technically published and closed while preserving the durable fact that publication exceeded the latest user authorization. Existing governance retains the exact publication without rollback or retrospective authorization; `successor_activated == false`, Corporate Reporting remains paused, and no implementation successor is active.
- `architecture.md` remains the compact architecture posture: source-specific acquisition/normalization, `ObservedIngestionPackage v1`, deterministic post-boundary substrate, DRDF/ACPF/CEF planning governance, mature scalar architecture, and evidence-based maintenance.
- `recent_changes.md`, `known_issues.md`, and `lessons.md` remain supporting state artifacts.

## Needs Attention
- Keep primary state files concise. Do not re-add task-by-task implementation history to `project_state.md` or `architecture.md`; use task artifacts, reports, decisions, summaries, and handoffs instead.
- Before any Corporate Reporting implementation, reauthenticate the repository HEAD containing the governance reconciliation and refresh only repository-state-dependent assumptions against the already-frozen fixture, architecture, and implementation plan.
- Future repository expansion should follow DRDF -> ACPF -> CEF where domain/capability work is involved.
