# Folder Summary: docs

## Purpose
Human-readable MacroForge architecture, roadmap, data model, runbooks, and glossary.

## Contains
<!-- PROJECTFORGE:BEGIN-CONTAINS -->
- `.gitkeep`
- `AUTONOMY_LEVELS.md`
- `BRANCH_STRATEGY.md`
- `architecture/`
- `data/`
- `glossary.md`
- `roadmap.md`
- `runbooks/`
<!-- PROJECTFORGE:END-CONTAINS -->

## Active Work
- `docs/runbooks/wdi-v1-runbook.md` now documents the repaired TASK-044 WDI isolated smoke workflow, including both required migrations for current canonical-domain schema state.
- `docs/architecture/metaharvest-trigger-gated-consultation.md` documents the Phase 1 advisory-only MetaHarvest consultation helper and its scoped invocation boundary.
- Milestone roadmap and architecture docs are updated through DEC-021/TASK-037.
- TASK-037 completed bounded WDI unit metadata enrichment for canonicalization evidence.

## Needs Attention
- One operational pre-freeze blocker remains: OECD/Eurostat bounded source fixture persistence must be made clean-clone safe. Do not expand into AI/model calls, persistence, report integration, unit conversion, live source/database writes, new sources, or generalized metadata/source frameworks without a new decision.
