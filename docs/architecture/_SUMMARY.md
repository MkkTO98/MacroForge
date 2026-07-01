# Folder Summary: docs/architecture

## Purpose
Architecture documentation for MacroForge data/research platform.

## Contains
<!-- PROJECTFORGE:BEGIN-CONTAINS -->
- `ai-assisted-canonicalization-governance-review.md`
- `architectural-confidence-ledger.md`
- `architectural-surprise-log.md`
- `bounded-eurostat-postgresql-promotion-design.md`
- `domain-coverage-assessment.md`
- `five-source-architectural-retrospective-20260630.md`
- `canonical-domain-schema-evolution.md`
- `canonicalization-next-scope-decision-analysis.md`
- `canonicalization-post-proposal-next-scope-decision-analysis.md`
- `capability-maturity-model.md`
- `historical-architecture-reconciliation.md`
- `long-term-domain-vision.md`
- `marginal-source-cost-index.md`
- `recurring-implementation-pain.md`
- `metaharvest-trigger-gated-consultation.md`
- `next-architectural-frontier-assessment-20260630.md`
- `revision-semantics-architectural-assessment-20260630.md`
- `revision-source-selection-assessment-20260630.md`
- `minimal-ai-assisted-canonicalization-layer.md`
- `minimal-canonical-domain-schema-design.md`
- `observed-ingestion-representation.md`
- `overview.md`
<!-- PROJECTFORGE:END-CONTAINS -->

## Active Work
- `domain-coverage-assessment.md` tracks lightweight long-term domain coverage state. TASK-065 updated only the Financial Market Curve observation-family section: current maturity is initial bounded financial-account flow evidence, represented concepts are IMF BOP asset/liability accounting entries and direct/portfolio investment categories, and major gaps remain broader BOP coverage, IIP/CPIS/CDIS/BIS sources, instrument/counterparty detail, and canonical loading.
- `architectural-confidence-ledger.md` records lightweight confidence estimates for current MacroForge architectural assumptions, includes post-implementation calibration through TASK-063, and requires calibration after every heterogeneous source implementation: confidence before, confidence after, direction, evidence for every tracked assumption, and a lightweight Prediction Quality value: Accurate, Mostly Accurate, Mixed, or Poor.
- `architectural-surprise-log.md` records only material prediction mismatches from heterogeneous source implementations; TASK-063 recorded no material architectural surprise, and summaries belong in implementation lessons, not the surprise log.
- `marginal-source-cost-index.md` records approximate engineering, human, LLM reasoning, and architectural-confidence estimates after heterogeneous implementations for trend detection, not precision.
- `recurring-implementation-pain.md` records recurring implementation difficulties; repeated pain, not repeated code, is the primary evidence for future extraction candidates.
- `long-term-domain-vision.md` records the accepted non-binding long-term observation-domain scope for MacroForge and the MacroForge/KnowledgeForge boundary. It is scope clarification only: not a roadmap, not implementation authorization, not source priority, and not permission for canonical entity, graph/catalog, source framework, or provider metadata infrastructure.
- `five-source-architectural-retrospective-20260630.md` is the baseline multi-source retrospective. It concludes that MacroForge should continue heterogeneous source implementation without architectural change, that no extraction is justified now, and that marginal effort is decreasing or stable while effort remains concentrated before the observed boundary.
- `next-architectural-frontier-assessment-20260630.md` records the source-family-level frontier assessment after the retrospective. It recommends revision-aware statistical releases as the next architectural frontier because revision/vintage semantics are the highest-value untested stress on observation identity, lineage, replay, validation, and MacroForge/KnowledgeForge separation.
- `revision-semantics-architectural-assessment-20260630.md` defines the provider-neutral revision behavior to test first: ordinary release-vintage revision of a small numeric statistical series with two releases/vintages, two or three economic periods, at least one changed overlapping value, and stable provider/indicator/territory/unit/frequency semantics.
- `revision-source-selection-assessment-20260630.md` selects ALFRED as the cleanest provider for that revision experiment because it directly exposes vintage/realtime versions of economic data while minimizing unrelated benchmark, methodology, rebase, classification, API-key, SDMX, and canonical-loading complexity.
- TASK-065 implemented the first bounded FRED monthly U.S. Treasury yield-curve evidence slice. It behaved as normal Domain Expansion Mode after selecting monthly frequency to preserve the current contract, added initial financial-market curve observation-family coverage, and required no contract/substrate evolution.
- TASK-064 implemented the first bounded Eurostat energy balance evidence slice. It behaved as normal Domain Expansion Mode, added initial official energy-accounting coverage, required no contract/substrate evolution, and updated only the affected Energy domain in `domain-coverage-assessment.md`.
- TASK-063 implemented the first bounded IMF BOP financial-account evidence slice. It behaved as normal Domain Expansion Mode, added initial international financial-flow coverage, required no contract/substrate evolution, and updated only the affected International Financial-Flow domain in `domain-coverage-assessment.md`.
- TASK-062 implemented the first bounded Eurostat input-output matrix evidence slice. It behaved as normal Domain Expansion Mode, added initial industry/input-output matrix coverage, required no contract/substrate evolution, and updated only the affected Industry/Input-Output domain in `domain-coverage-assessment.md`.
- TASK-061 implemented the first bounded WDI demographic foundation evidence slice. It behaved as normal Domain Expansion Mode, added initial demographic foundation coverage, required no contract/substrate evolution, and updated only the affected Demographics domain in `domain-coverage-assessment.md`.
- TASK-060 implemented the first bounded UN Comtrade bilateral total-goods trade evidence slice. It behaved as normal Domain Expansion Mode, added initial direct international-trade coverage, required no contract/substrate evolution, and updated only the affected Trade domain in `domain-coverage-assessment.md`.
- TASK-059 implemented the first bounded ILOSTAT unemployment-rate labor-market evidence slice. It behaved as normal Domain Expansion Mode, added initial direct labor-market coverage, required no contract/substrate evolution, and updated only the affected Labor domain in `domain-coverage-assessment.md`.
- TASK-058 implemented the selected bounded ALFRED GDP revision-vintage evidence slice. Ordinary release-vintage semantics fit the current `ObservedIngestionPackage` boundary and deterministic substrate; revision infrastructure extraction remains unjustified and future revision work should gather more evidence before extraction investigation.
- `capability-maturity-model.md` is the active v1.1 implementation-planning model. It uses the lifecycle Discovered -> Specified -> Verified -> Adopted -> Shared -> Stable -> Mature, records lightweight Verified prerequisites for safe advancement, records Observed Boundary and Contract Stability plus Canonical Lineage Event Generation plus Contract Validation and Drift Detection plus Deterministic Ingestion Feedback as Verified, includes the standard foundational capability extraction checklist, and now records next-ten-source Evidence-Accumulating Source Expansion through completed TASK-054 Treasury Fiscal Data evidence.
- `observed-ingestion-representation.md` documents `ObservedIngestionPackage` v1 as a public internal architectural contract extracted from implemented WDI/OECD/Eurostat behavior. It records field purpose/ownership/status, invariants, boundaries, compatibility expectations, versioning policy, and explicit out-of-contract areas.
- `metaharvest-trigger-gated-consultation.md` documents the implemented Phase 1 helper at `tools/consult_metaharvest.py`: scoped task/governance preflight only, separate Consultation/Retrieval Contracts, versioned internal taxonomy, bounded advisory retrieval, non-blocking failure, and mandatory Authority note.
- `minimal-ai-assisted-canonicalization-layer.md` remains the accepted TASK-030 design for provider evidence, canonicalization runs, mapping/canonical-creation proposals, confidence/provenance/review state, accepted mappings, unit/comparability profiles, and re-canonicalization lineage.

## Needs Attention
- Treat `ObservedIngestionPackage` field/semantic changes as contract evolution, not routine implementation refactoring.
- Treat the long-term domain vision as non-binding scope clarification subordinate to the Constitution, DEC-022, current architecture state, and the bounded heterogeneous-source execution loop.
- TASK-055 showed SDMX GenericData mechanics repeating across OECD and ECB, but did not justify an SDMX Interpretation Layer. Continue source-specific-first implementation until repeated evidence satisfies the extraction gate.
- The first five-source retrospective is complete; use `five-source-architectural-retrospective-20260630.md` as the baseline for future retrospectives and do not re-litigate extraction without new evidence.
- The next architectural frontier assessment recommends revision-aware statistical releases as the next source-family experiment; this is not provider selection, implementation authorization, or infrastructure design.
- The revision-semantics assessment narrows the desired first test to ordinary release-vintage revisions only; defer benchmark, methodology, rebasing, seasonal-adjustment, correction, classification, and company/event semantics unless explicitly authorized later.
- The revision-source selection assessment recommends ALFRED for the first revision experiment because it best satisfies the already-accepted ordinary release-vintage criteria. TASK-058 implemented that bounded ALFRED GDP evidence slice and confirmed no contract/substrate evolution was required; decision gate: gather more revision evidence before extraction investigation. TASK-059 returned MacroForge to normal Domain Expansion Mode with ILOSTAT labor evidence and no architectural action. TASK-060 continued Domain Expansion Mode with UN Comtrade trade evidence and no architectural action. TASK-061 continued Domain Expansion Mode with WDI demographic foundation evidence and no architectural action. TASK-062 continued Domain Expansion Mode with Eurostat input-output matrix evidence and no architectural action. TASK-063 continued Domain Expansion Mode with IMF BOP financial-account evidence and no architectural action. TASK-064 continued Domain Expansion Mode with Eurostat energy balance evidence and no architectural action. TASK-065 continued Domain Expansion Mode with FRED U.S. Treasury yield-curve evidence and no architectural action.
- Outside the five-source Retrospective Review decision gate, follow the frozen execution loop: select source, predict, implement, verify, lessons, surprise log, confidence calibration including Prediction Quality, cost-index update, pain update, then continue. Methodology changes now require extraction-grade repeated implementation evidence; elegance, consistency, or theoretical appeal are insufficient.
- Preserve no unit conversion, report integration, database persistence, AI/model calls, generalized ingestion frameworks, plugin systems, or source registries unless explicitly changed by a new task/decision.
