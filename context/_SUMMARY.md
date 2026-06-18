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
- `latest_handoff.md` records the latest durable handoff; current execution should start from relocated project path `/home/mkkto/srv/EIP/projects/MacroForge`.
- `context_policy.yaml` includes concise MacroForge doctrine for recurring effort reduction and deferring components that do not improve trust, reproducibility, maintainability, semantic correctness, or future effort reduction.
- Generated context bundles are task/model-target artifacts and should be regenerated when needed, not treated as mandatory startup context.

## Needs Attention
- Keep raw exports out of normal context.
- Fresh work should start from bounded recovery. No implementation task is open after TASK-039; future OECD/Eurostat mapping advancement should begin from `artifacts/reports/canonicalization-deferred-mapping-advancement-requirements-20260618.json`.
