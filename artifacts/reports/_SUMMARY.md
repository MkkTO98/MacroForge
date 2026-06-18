# Folder Summary: artifacts/reports

## Purpose
This folder is part of the ProjectForge file-backed operating system for `artifacts/reports`.

## Contains
<!-- PROJECTFORGE:BEGIN-CONTAINS -->
- `.gitkeep`
- `R-20260605-architecture-reality-audit.md`
- `R-20260613-architecture-reality-audit.md`
- `R-20260613-largest-canonicalization-uncertainty.md`
- `R-20260613-review-to-accepted-lifecycle-validation-design.md`
- `TASK-037-closeout-report-20260613.md`
- `canonical-gdp-snapshot-20260604.json`
- `canonical-gdp-snapshot-20260604.md`
- `canonicalization-deferred-mapping-advancement-requirements-20260618.json`
- `canonicalization-deferred-mapping-advancement-requirements-20260618.md`
- `canonicalization-proposal-workflow-20260613.json`
- `canonicalization-review-lifecycle-20260614.json`
- `canonicalization-review-lifecycle-20260614.md`
- `canonicalization-state-foundation-20260605.json`
- `canonicalization-wdi-unit-metadata-enrichment-20260613.json`
- `combined-source-canonical-smoke-20260604.json`
- `eurostat-namq-load-smoke-20260604.json`
- `eurostat-third-source-architecture-spike-20260604.md`
- `oecd-sdmx-codelist-labels-20260604.md`
- `oecd-sdmx-live-smoke-20260603.md`
- `oecd-sdmx-load-smoke-20260603.json`
- `oecd-sdmx-second-source-spike-20260603.md`
- `oecd-sdmx-smoke-20260603.md`
- `project-state-history-before-architecture-reality-remediation-20260605.md`
- `wdi-isolated-smoke-rerun-20260603.json`
- `wdi-load-smoke-20260602.json`
- `wdi-smoke-20260602.md`
- `wdi-validation-smoke-20260602.json`
- `wdi-validation-smoke-20260602.md`
<!-- PROJECTFORGE:END-CONTAINS -->

## Active Work
- TASK-039 produced `canonicalization-deferred-mapping-advancement-requirements-20260618.json` and `.md`, persisting concrete rationale, missing evidence/policy, semantic blockers, minimum advancement conditions, caveats, evidence pointers, replay requirements, and forbidden shortcuts for TASK-038 deferred OECD/Eurostat mappings.
- TASK-038 produced `canonicalization-review-lifecycle-20260614.json` and `.md`, validating the bounded proposal -> review -> accepted/provisional lifecycle with one WDI governed provisional outcome and OECD/Eurostat deferred outcomes. It records explicit review decisions, check gates, state deltas, manifest deltas, lineage, and replay evidence without mutating base state or the canonical asset manifest.
- `R-20260613-review-to-accepted-lifecycle-validation-design.md` remains the prior recommendation-only design artifact that TASK-038 executed in bounded form.
- `R-20260613-largest-canonicalization-uncertainty.md` remains the prior recommendation-only artifact that identified review-to-accepted-state lifecycle and check gating as the largest remaining canonicalization architecture uncertainty after TASK-037.
- TASK-037 closeout produced `TASK-037-closeout-report-20260613.md`, recording final tests, coherence, audit validation, and deterministic report cleanup.
- `R-20260613-architecture-reality-audit.md` records the Architecture-to-Reality Audit run for TASK-037 closeout; final JSON validation reported 0 blocks and 0 warnings.
- TASK-037 produced `canonicalization-wdi-unit-metadata-enrichment-20260613.json`, recording fixture-backed WDI `NY.GDP.MKTP.CD` unit metadata evidence, reduced WDI `unknown_unit_metadata` in proposal evidence, unchanged non-WDI profiles, preserved no-unit-conversion policy, review-required routing, no accepted-state mutation, and no auto-apply behavior.
- TASK-034 produced `canonicalization-proposal-workflow-20260613.json`, recording deterministic provider-evidence-derived workflow proposals, review-required mapping update proposals, unit/frequency caveat propagation, no accepted-state mutation, and no-auto-apply behavior for existing WDI/OECD/Eurostat GDP fixture evidence.
- TASK-032 produced `canonicalization-state-foundation-20260605.json`, recording deterministic fixture-backed canonicalization state for existing WDI/OECD/Eurostat GDP evidence with passing checks for proposal/accepted-state separation, unit comparability caveats, non-aggregation, review routing, and supersession fields.
- TASK-028 produced `canonical-gdp-snapshot-20260604.json` and `.md`, recording the first canonical-only GDP snapshot/audit report with 16 GDP observations, 0 missing bounded GDP observations, 0 duplicate fact grains, and 0 failing quality checks.

## Needs Attention
- Do not treat the TASK-032, TASK-034, TASK-037, or TASK-038 canonicalization reports as live `macro` database writes, PostgreSQL persistence, model canonicalization, conversion, aggregation, accepted production ontology, auto-applied mapping state, or direct canonical asset manifest mutation.
