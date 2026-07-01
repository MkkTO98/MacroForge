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
- `docs/architecture/domain-coverage-assessment.md` tracks lightweight long-term domain coverage state. TASK-059 updated only Labor, TASK-060 updated only Trade, TASK-061 updated only Demographics, TASK-062 updated only Industry/Input-Output, and TASK-063 updated only International Financial-Flow after the bounded WDI demographic foundation slice.
- `docs/architecture/long-term-domain-vision.md` records MacroForge's accepted long-term observation-domain vision as non-binding scope clarification only; implementation methodology and source selection remain governed by the Constitution, DEC-022, and bounded implementation evidence.
- `docs/architecture/five-source-architectural-retrospective-20260630.md` records the baseline multi-source retrospective through TASK-057 and concludes no architectural extraction is currently justified.
- `docs/architecture/next-architectural-frontier-assessment-20260630.md` records the source-family-level assessment recommending revision-aware statistical releases as the next architectural frontier, without selecting a provider or authorizing implementation.
- `docs/architecture/revision-semantics-architectural-assessment-20260630.md` defines the smallest provider-neutral revision behavior to test before provider selection: ordinary release-vintage revisions with changed overlapping values and stable source semantics.
- `docs/architecture/revision-source-selection-assessment-20260630.md` selects ALFRED as the cleanest provider for the ordinary release-vintage revision experiment. TASK-058 then implemented the bounded ALFRED GDP evidence slice without broad FRED/ALFRED support, canonical loading, generic revision infrastructure, or contract/substrate evolution.
- TASK-063 implemented a bounded IMF BOP financial-account evidence slice and continued Domain Expansion Mode without architectural action.
- TASK-062 implemented a bounded Eurostat input-output matrix evidence slice and continued Domain Expansion Mode without architectural action.
- TASK-061 implemented a bounded WDI demographic foundation evidence slice and continued Domain Expansion Mode without architectural action.
- TASK-060 implemented a bounded UN Comtrade bilateral total-goods trade evidence slice and continued Domain Expansion Mode without architectural action.
- TASK-059 implemented a bounded ILOSTAT unemployment-rate labor-market evidence slice and returned MacroForge to Domain Expansion Mode without architectural action.
- `docs/runbooks/wdi-v1-runbook.md` now documents the repaired TASK-044 WDI isolated smoke workflow, including both required migrations for current canonical-domain schema state.
- `docs/architecture/metaharvest-trigger-gated-consultation.md` documents the Phase 1 advisory-only MetaHarvest consultation helper and its scoped invocation boundary.
- Milestone roadmap and architecture docs are updated through DEC-021/TASK-037.
- TASK-037 completed bounded WDI unit metadata enrichment for canonicalization evidence.

## Needs Attention
- Do not treat the long-term domain vision as a fixed roadmap, source priority list, implementation authorization, canonical entity design, or permission for speculative infrastructure.
- Preserve bounded fixture persistence for source evidence, including TASK-060 UN Comtrade raw JSON, TASK-061 WDI demographic raw JSON, and TASK-062 Eurostat input-output raw JSON-stat, and TASK-063 IMF BOP financial-account raw SDMX XML. Do not expand into AI/model calls, persistence, report integration, unit conversion, live source/database writes, new broad sources, or generalized metadata/source frameworks without a new decision.
