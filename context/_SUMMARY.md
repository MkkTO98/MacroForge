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
- `latest_handoff.md` records TASK-221's exact published implementation identity, commit `3be04c379409067e728ff851e7b98d3c08d8d864`, completed verification, fresh 23-question independent PASS, preserved chronology and limitations, fail-closed Corporate Reporting data-release authority, and no active successor.
- Generated context bundles are task/model-target artifacts and should be regenerated when needed, not treated as mandatory startup context.

## Needs Attention
- TASK-221 is Git-published and technically closed. Any future Corporate Reporting work requires separate task selection and authority; reviewed implementation/test bytes must not change absent that authority.
- Mapping, eligible-revision, Corporate Reporting data-release, redistribution-rights, quality-authority, and remote-delivery gates remain fail-closed, and the provenance/metadata limitations remain explicit.
- Keep raw exports and large generated bundles out of normal startup context.
- Fresh work should start from bounded recovery: read `CONSTITUTION.md`, compact state files, and `context/latest_handoff.md`; expand only into relevant task/report/domain/artifact files.
