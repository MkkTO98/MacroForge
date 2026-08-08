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
- `latest_handoff.md` records the immutable review/correction chronology through the latest publication-transition BLOCK and routes live state conditionally. It does not assert one pending or sole next gate: exact-byte PASS permits bounded publication, BLOCK requires correction, local commit requires remote verification, and verified remote equality closes the workstream without activating a successor.
- Generated context bundles are task/model-target artifacts and should be regenerated when needed, not treated as mandatory startup context.

## Needs Attention
- Keep raw exports and large generated bundles out of normal startup context.
- Fresh work should start from bounded recovery: read `CONSTITUTION.md`, compact state files, and `context/latest_handoff.md`; expand only into relevant task/report/domain/artifact files.
- Do not reopen the published WDI correction. Route the bounded governance workstream from authenticated Git and exact-byte external evidence under the v3 transition contract; separate future work requires explicit prioritization.
