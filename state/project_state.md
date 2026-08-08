# Project State

## Current governance condition

`TASK-PF-20260801` is technically published and closed under `macroforge-ignored-artifact-governance-lifecycle-v3`. Its canonical task history records that publication of commit `0e1ac2abc9b3371daabcfb74bab9c1007c943d0a` exceeded the latest user authorization.

The publication was unauthorized at execution time, was subsequently verified technically exact, and is retained because no technical or governance evidence requires rollback. This reconciliation does not retrospectively authorize the publication.

## Stable technical facts

- Parent baseline: `37cbbbd076926a1dfcecaab11a4c03305d123284`.
- Accepted technical implementation commit: `0e1ac2abc9b3371daabcfb74bab9c1007c943d0a`.
- Publication boundary: exactly the code-owned canonical 15-path tuple.
- Missing, extra, blob-drifted, or Git-mode-drifted paths: `0`.
- Outside-candidate population/projection: `1100` / `bab4d058d3e73a247bea02912cc3bb1ab49a5572823f1b9802896f34d89c54d1`.
- Ignored population/projection: `5423` / `fc3b28cc7770a4967161331c8abad15c4dc5ed5cee7e74e0635f176295ff0e09`.
- Publication transition: technically closed.
- `successor_activated == false`.

The repository baseline for later work is the authenticated HEAD containing this reconciliation. Future agents must reauthenticate it rather than infer a live hash from this pre-commit record.

## Governance treatment

- Existing task/state/handoff/summary mechanisms own the reconciliation; no new incident subsystem or lifecycle was created.
- No reset, revert, amend, force-push, or history rewrite is required.
- Corporate Reporting remained paused and no implementation successor was activated.
- The already-frozen Corporate Reporting fixture, architecture, and implementation plan remain semantically controlling.
- Repository-state-dependent Corporate Reporting assumptions require normal reauthentication before implementation resumes under separate authorization.

## Constraints

This state does not authorize Corporate Reporting implementation, Gatos evidence mutation, PostgreSQL work, OIP work, WDI work, territory work, historical SEC experimental mutation, unrelated cleanup, rollback, or any implicit successor.
