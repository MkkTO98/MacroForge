# Folder Summary: context

## Purpose
Curated project context, context policy, latest handoff, and compact source-of-truth material. Stale generated context bundles are archived rather than used as startup context.

## Contains
<!-- PROJECTFORGE:BEGIN-CONTAINS -->
- `.gitkeep`
- `PROJECT_CONTEXT.md`
- `archive/`
- `context_policy.yaml`
- `imports/`
- `latest_handoff.md`
- `reconstruction/`
<!-- PROJECTFORGE:END-CONTAINS -->

## Active Work
- `latest_handoff.md` records the completed 2026-07-01 bounded context-health and audit maintenance pass: primary state files compressed, architecture-reality audit report recorded, and all known continuity/audit warnings resolved.
- `context_policy.yaml` remains the context discipline policy; `CONSTITUTION.md` carries the governing optimization objective.
- Generated context bundles are task/model-target artifacts and should be regenerated when needed, not treated as mandatory startup context.

## Needs Attention
- Keep raw exports and large generated bundles out of normal startup context.
- Fresh work should start from bounded recovery: read `CONSTITUTION.md`, compact state files, and `context/latest_handoff.md`; expand only into relevant task/report/domain artifacts.
- MacroForge is safe to continue Domain Expansion Mode. No implementation task is currently active.
