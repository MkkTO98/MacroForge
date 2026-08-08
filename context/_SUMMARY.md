# Folder Summary: context

## Purpose
Curated project context, context policy, latest handoff, and compact source-of-truth material. Stale generated context bundles are archived rather than used as startup context.

## Contains
<!-- PROJECTFORGE:BEGIN-CONTAINS -->
- `PROJECT_CONTEXT.md`
- `active_context.md`
- `archive/`
- `context_audit.json`
- `context_audit.md`
- `context_manifest.json`
- `context_policy.yaml`
- `imports/`
- `latest_handoff.md`
- `reconstruction/`
<!-- PROJECTFORGE:END-CONTAINS -->

## Active Work
- `latest_handoff.md` records the bounded reconciliation of the unauthorized `TASK-PF-20260801` publication: the exact 15-path successor and unrelated-state preservation were proven, publication nonetheless exceeded the latest user authorization, rollback is not required, and the technically closed workstream activates no successor. Corporate Reporting remains paused pending normal baseline reauthentication.
- Generated context bundles are task/model-target artifacts and should be regenerated when needed, not treated as mandatory startup context.

## Needs Attention
- Keep raw exports and large generated bundles out of normal startup context.
- Fresh work should start from bounded recovery: read `CONSTITUTION.md`, compact state files, and `context/latest_handoff.md`; expand only into relevant task/report/domain/artifact files.
- A later explicitly authorized Corporate Reporting continuation may resume the already-frozen implementation task only after reauthenticating repository-state-dependent assumptions against the reconciliation-containing HEAD.
