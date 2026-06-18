# Largest Remaining Canonicalization Architecture Uncertainty

Date: 2026-06-13
Timestamp UTC: 2026-06-13T18:46:30Z
Scope: Recommendation artifact only. No TASK-038 was created, selected, or started. No implementation was performed.

## Goal

Identify the single largest remaining uncertainty in MacroForge after TASK-037 closeout, optimizing for the question:

> Which uncertainty, if resolved next, would most increase confidence in MacroForge's canonicalization architecture?

This report intentionally does not optimize for easiest task, next backlog item, or smallest implementation.

## Context considered

Current MacroForge evidence considered:

- Canonicalization state foundation: TASK-032, DEC-018, `src/macroforge/canonicalization_state.py`, `artifacts/reports/canonicalization-state-foundation-20260605.json`.
- Deterministic proposal workflow: TASK-034, DEC-019, `artifacts/reports/canonicalization-proposal-workflow-20260613.json`.
- WDI metadata enrichment: TASK-037, DEC-021, `artifacts/reports/canonicalization-wdi-unit-metadata-enrichment-20260613.json`.
- ArchitectureHarvest findings: first MacroForge ArchitectureHarvest review, local relevance map, adopted `MF-AH-REV-001`, and deferred candidates `MF-AH-REV-002` through `MF-AH-REV-005`.
- Manifest registry implementation: DEC-020 and `artifacts/manifests/canonical_assets.json`.
- Current accepted decisions and backlog through TASK-037.

## Ranking method

Uncertainties are ranked by expected confidence gain for MacroForge's canonicalization architecture, not by implementation ease.

Evaluation dimensions:

1. Architecture centrality: whether the uncertainty blocks the accepted DEC-018 canonicalization architecture from becoming a trustworthy system.
2. Sequencing leverage: whether resolving it clarifies several later decisions at once.
3. Evidence leverage: whether existing TASK-032/TASK-034/TASK-037/ArchitectureHarvest evidence can be used directly.
4. Confounding reduction: whether it avoids mixing multiple unresolved variables, such as AI quality, persistence, source metadata sparsity, and review policy.
5. Failure information value: whether a negative result would force a meaningful architecture change.

## Top 5 uncertainties

### 1. Review-to-accepted-state lifecycle and check gating

Uncertainty:

Can MacroForge turn review-required canonicalization proposals into governed accepted/provisional mapping state with explicit validation/check gates, lineage, ownership, and replayable audit evidence, without collapsing into manual-every-mapping governance or unsafe auto-apply behavior?

Why it ranks first:

- DEC-018's core architecture is not just proposal generation. It is a governed lifecycle: provider evidence -> canonicalization run -> proposal -> review -> accepted/provisional mapping state -> curated facts/reports.
- TASK-032 proved state representation.
- TASK-034 proved proposal mechanics.
- TASK-037 reduced the strongest source-metadata blocker.
- What remains unproven is the architecture's central governance hinge: the transition from proposal evidence to accepted/provisional mapping state.
- ArchitectureHarvest reinforces this gap: after the manifest registry (`MF-AH-REV-001`), the next high-confidence external patterns are explicit lineage edges (`MF-AH-REV-002`) and accepted-state checks/contracts (`MF-AH-REV-003`). Those map directly to review-to-accepted-state lifecycle confidence.
- Resolving this uncertainty would clarify whether MacroForge's canonicalization architecture can scale beyond static fixture proposals before adding AI/model calls, persistence, or report integration.

Evidence already available:

- DEC-018 requires proposal state separate from accepted/provisional mapping state and routes high-impact GDP concepts to review.
- TASK-032 audit passes for proposal/accepted-state separation, review routing, supersession fields, and unknown-unit caveats.
- TASK-034 audit passes for generated-from-provider-evidence, no-auto-apply, high-impact review routing, and proposal/accepted-state separation.
- TASK-037 audit passes for WDI metadata enrichment while preserving no-auto-apply, review routing, and accepted-state separation.
- `artifacts/manifests/canonical_assets.json` has stable asset keys, roles, statuses, owner/review authority, artifact pointers, version fields, and caveats.
- ArchitectureHarvest candidates `MF-AH-REV-002` and `MF-AH-REV-003` provide strong pattern evidence for explicit lineage edges and check artifacts after manifest adoption.

Evidence still missing:

- No artifact records a complete review decision over generated canonicalization proposals.
- No bounded lifecycle artifact links provider evidence -> proposal -> review decision -> accepted/provisional mapping update -> canonical asset manifest status.
- No accepted-state check contract defines what must pass before a mapping can move from review-required proposal to accepted/provisional state.
- No replay test proves that accepted mapping state can be regenerated, audited, or rejected without mutating proposal evidence.
- No calibration evidence shows where human review is mandatory versus optional for high-impact concepts, low-confidence mappings, unit conflicts, or unchanged mappings.
- No policy distinguishes safe acceptance of metadata-improved WDI evidence from unsafe auto-application.

Confidence impact if resolved:

Very high. It would validate or falsify the central governance loop of MacroForge canonicalization before AI/model assistance, database persistence, or report integration are introduced.

### 2. AI-assisted proposal quality and calibration

Uncertainty:

Once deterministic workflow and source metadata are sufficient, can an AI-assisted proposer generate auditable, useful mapping/canonical-creation proposals with confidence/reasoning/provenance that improves throughput without degrading governance quality?

Why it ranks second:

- DEC-018's target architecture is AI-assisted, not permanently deterministic-only.
- DEC-019 intentionally deferred AI/model calls until deterministic lifecycle mechanics were proven.
- TASK-037 removed the most obvious source-metadata blocker for WDI, making AI quality closer to a real future question.
- However, AI proposal quality should not be tested before the review-to-accepted-state lifecycle exists; otherwise model quality, review policy, and acceptance semantics would be confounded.

Evidence already available:

- Accepted DEC-018 architecture for AI-assisted auditable canonicalization.
- Deterministic proposal workflow provides a baseline output shape and expected audit behavior.
- WDI unit metadata enrichment reduces one source of false uncertainty.
- Review routing treats confidence as routing metadata, not truth.

Evidence still missing:

- No prompt/provider/model configuration is accepted for canonicalization.
- No AI proposal benchmark, gold/silver review set, or calibration sample exists.
- No quality rubric compares AI proposals against deterministic proposals and human review outcomes.
- No policy exists for confidence thresholds, sampling, or hallucination containment.

Confidence impact if resolved:

High, but only after lifecycle/check gating is tested. It would validate whether the long-term AI-assisted premise can outperform deterministic scaffolding safely.

### 3. Source metadata adequacy across providers without a generalized metadata framework

Uncertainty:

Can MacroForge continue enriching provider metadata source-specifically enough to support canonicalization quality, or does canonicalization now need a minimal shared metadata evidence contract before more sources/indicators are added?

Why it ranks third:

- TASK-037 proved bounded WDI enrichment works for one indicator and one source.
- OECD and Eurostat still have partial caveats, scale/currency/frequency differences, and conversion deferrals.
- The architecture intentionally avoids generalized source metadata frameworks. That remains correct until local pressure proves otherwise, but the pressure is growing around units, currency basis, scale, price basis, and frequency semantics.
- This uncertainty affects proposal quality but is narrower than the accepted-state lifecycle.

Evidence already available:

- Existing WDI/OECD/Eurostat GDP evidence.
- TASK-032 unit comparability profiles.
- TASK-034 caveat propagation.
- TASK-037 WDI fixture-backed unit metadata enrichment.
- DEC-021 explicitly rejects broad source metadata framework extraction for TASK-037.

Evidence still missing:

- No cross-provider evidence contract for minimum unit/currency/frequency metadata required by canonicalization proposals.
- No source-specific enrichment evidence beyond WDI's existing GDP unit metadata improvement.
- No measurement of which proposal caveats are still caused by missing metadata versus real economic non-comparability.
- No decision about when repeated source-specific metadata fields justify a tiny shared evidence schema.

Confidence impact if resolved:

Medium-high. It would clarify whether MacroForge can preserve source-specific loaders while still producing high-quality canonicalization evidence.

### 4. Canonicalization state persistence and report integration boundary

Uncertainty:

When should canonicalization state become part of reproducible curated facts/reports, and should it remain file-backed or gain PostgreSQL persistence?

Why it ranks fourth:

- Current canonicalization state and proposal artifacts are file-backed and separate from the GDP snapshot report.
- DEC-018 ultimately connects accepted/provisional mapping state to curated facts/reports.
- Persistence/report integration matters for reproducibility, but integrating too early would freeze uncertain review semantics.
- It should follow lifecycle/check validation, not precede it.

Evidence already available:

- Canonical GDP snapshot report from accepted canonical/domain tables.
- TASK-032/TASK-034/TASK-037 file-backed canonicalization artifacts.
- Manifest registry asset pointers.
- ArchitectureHarvest evidence favoring typed assets/checks/lineage without forcing runtime adoption.

Evidence still missing:

- No accepted-state lifecycle output to integrate into reports.
- No schema design for canonicalization persistence.
- No report showing canonicalization review state alongside canonical GDP outputs.
- No reproducibility check from source evidence through canonicalization state into report selection.

Confidence impact if resolved:

Medium-high, but resolving it before review-to-accepted-state semantics risks hardening the wrong state model.

### 5. Versioning, supersession, staleness, and rollback semantics for canonical mappings

Uncertainty:

Can MacroForge safely evolve canonical mappings, proposals, metadata evidence, and reports over time with explicit version, supersession, deprecation, staleness, and rollback semantics?

Why it ranks fifth:

- TASK-032 included version/supersession fields and DEC-020 manifest status/version pointers.
- ArchitectureHarvest `MF-AH-REV-005` identifies schema/mapping/proposal version and staleness modeling as high-confidence but deferred.
- This becomes critical when accepted mappings start changing or reports depend on them.
- It is important but should be tested as part of, or immediately after, the review-to-accepted-state lifecycle.

Evidence already available:

- TASK-032 supersession fields passed validation.
- Manifest has version, `supersedes`, and `superseded_by` fields.
- DEC-018 lists changed accepted mappings and re-canonicalization proposals as review-required.

Evidence still missing:

- No concrete supersession scenario has been exercised.
- No stale mapping or metadata-evidence invalidation example exists.
- No rollback/replay artifact proves report reproducibility across mapping versions.
- No policy distinguishes retired, rejected, superseded, provisional, and accepted mapping states in operational workflows.

Confidence impact if resolved:

Medium. It is essential for long-term maintainability, but depends on the accepted-state lifecycle becoming concrete.

## Recommended next uncertainty to resolve

Resolve uncertainty #1: review-to-accepted-state lifecycle and check gating.

Recommended framing:

> Prove that MacroForge can move from generated canonicalization proposals to governed accepted/provisional mapping state using explicit review decisions, check gates, lineage pointers, and manifest updates, without AI/model calls, database persistence, report integration, unit conversion, or auto-apply behavior.

This is the largest remaining architecture uncertainty because it tests the central DEC-018 promise after TASK-032/TASK-034/TASK-037 have removed earlier blockers:

- The state surface exists.
- The deterministic workflow loop exists.
- The sharpest WDI source metadata blocker is reduced.
- The manifest vocabulary exists.
- ArchitectureHarvest now points toward lineage/check artifacts as the next useful pressure test.

If this lifecycle works, MacroForge can make higher-confidence decisions about AI proposal quality, persistence, report integration, and versioning. If it fails, the architecture needs revision before those larger capabilities are useful.

## Candidate bounded task for resolving it

Candidate task title:

`Decide and simulate bounded canonicalization proposal review-to-accepted-state lifecycle`

Purpose:

Create a bounded governance/design-and-simulation artifact over the existing WDI/OECD/Eurostat GDP proposal set that proves or falsifies the review-to-accepted-state lifecycle before implementation expansion.

Allowed scope:

- Use only existing TASK-032/TASK-034/TASK-037 fixture-backed canonicalization evidence.
- Create a fresh dry-run if implementation-like artifacts or state changes are proposed.
- Define a tiny review-decision fixture or report artifact for the existing three GDP mapping proposals.
- Define minimal accepted-state check gates for high-impact GDP mappings.
- Link proposal IDs, review decisions, accepted/provisional mapping state, canonical asset manifest entries, and relevant report/evidence artifacts.
- Produce an audit/recommendation artifact showing whether each mapping could remain provisional, become accepted, remain review-required, or be rejected/deferred.
- Preserve no-auto-apply: any simulated acceptance must be a review artifact, not automatic mutation of accepted state.
- Keep the work file-backed and reversible.

Rejected scope:

- Do not create TASK-038 without explicit user approval.
- Do not call AI/models.
- Do not configure prompts/providers/embeddings.
- Do not live-fetch data.
- Do not add new sources or indicators.
- Do not add PostgreSQL migrations or canonicalization persistence.
- Do not integrate canonicalization state into the GDP snapshot report.
- Do not perform unit/currency conversion or quarterly-to-annual aggregation.
- Do not auto-apply accepted mapping updates.
- Do not adopt dbt, Dagster, orchestration runtime behavior, or a generalized ingestion framework.

Candidate acceptance evidence:

- A recommendation/design artifact ranks review outcomes for WDI, OECD, and Eurostat GDP mappings using existing evidence.
- A tiny lifecycle diagram/table exists for evidence -> proposal -> review decision -> accepted/provisional state -> manifest/check/lineage pointer.
- Required check gates are explicit, including high-impact review, unit/currency/frequency caveats, source metadata evidence role, non-aggregation, no conversion, and report-impact flags.
- The artifact identifies whether current evidence is sufficient for any mapping to move beyond `provisional_review_required`.
- Coherence and Architecture-to-Reality Audit report no blocks or warnings after artifact creation.

## Why not choose the easier next item

A smaller next item could enrich another source metadata field, add a manifest entry, or create a simple check artifact. Those would be useful, but they would not answer the architectural question with the highest confidence value: whether the canonicalization lifecycle can safely cross the boundary from proposal generation to governed accepted/provisional mapping state.

## Recommendation status

Recommendation only. No task was created. No decision was accepted. No implementation was performed.
