# TASK-058 — Bounded ALFRED Revision-Vintage Evidence Slice

Status: complete
Started: 2026-06-30
Completed: 2026-06-30

## Objective

Implement the smallest bounded revision-vintage evidence slice capable of testing whether MacroForge can represent multiple source-backed values for the same economic period across publication time while preserving observation identity, release identity, lineage, replay, validation, fingerprinting, reproducibility, and the MacroForge / KnowledgeForge boundary.

## Accepted planning chain

- Strategic Constitution v1.1.
- DEC-022.
- DEC-023.
- Five-source architectural retrospective.
- Next architectural frontier assessment.
- Revision-semantics architectural assessment.
- Revision-source selection assessment.

## Scope

Provider: ALFRED.

Bounded slice shape:

- One ALFRED series.
- Two provider-backed vintages.
- Two quarterly observation periods.
- Four observed rows total.
- At least one overlapping period whose value changes across vintages.
- At least one overlapping period whose value remains unchanged across vintages.
- No broad ALFRED/FRED support.
- No API-key infrastructure.
- No canonical loading.
- No generic revision infrastructure.
- No KnowledgeForge semantics.

## Pre-implementation architectural predictions

### Prediction 1 — ObservedIngestionPackage remains unchanged

Confidence: Moderate-High.

Evidence:

- WDI, OECD_NAAG, EUROSTAT_NAMQ_GDP, BLS_CPI, BEA_NIPA, TREASURY_FISCAL_DATA, ECB_SDW, IMF_MFS_IR, and BIS_CBPOL have fit the observed package contract without recent contract evolution.
- The revision-source selection assessment predicted ALFRED-style vintage semantics should fit through release_key, raw_evidence, input_filters, attributes, and source_payload.

Weakening evidence:

- Vintage identity cannot be preserved without lossy encoding.
- Multiple vintages of the same economic period make observed-row identity ambiguous.

Falsifying evidence:

- A first-class observed contract field is required to distinguish vintage/as-of identity.
- Existing package/release evidence cannot distinguish two provider-backed vintages deterministically.

### Prediction 2 — deterministic replay remains unchanged for same-vintage inputs

Confidence: High.

Evidence:

- Existing package fingerprinting and comparison were stable across recent heterogeneous sources.
- ALFRED CSV evidence with fixed vintage dates and fixed observation window should be deterministic.

Weakening evidence:

- Returned metadata includes nondeterministic retrieval-time fields that affect fingerprints.

Falsifying evidence:

- Same fixture produces different observed rows or fingerprints across replays.

### Prediction 3 — lineage pressure increases but remains source-evidence lineage

Confidence: Moderate.

Evidence:

- DEC-023 assigns source-backed observations, provenance, reproducibility, lineage, validation, and observational identity to MacroForge.
- ALFRED exposes what value was available at a vintage/realtime date without requiring MacroForge to explain why a revision occurred.

Weakening evidence:

- Implementation cannot distinguish revised values from parser drift without semantic interpretation.

Falsifying evidence:

- MacroForge must assert economic correctness or revision cause to preserve the evidence.

### Prediction 4 — validation remains contract-focused

Confidence: High.

Evidence:

- Recent source slices required no source-specific post-boundary validation branches.
- The bounded ALFRED slice can validate package shape, required fields, row ordering, vintage overlap, changed control, and unchanged control without economic interpretation.

Weakening evidence:

- Validation must distinguish expected revision from drift through new substrate semantics.

Falsifying evidence:

- Existing contract validation rejects two source-backed values for the same economic period when release/vintage evidence differs.

### Prediction 5 — fingerprinting differs across vintages and is deterministic within vintage

Confidence: High.

Evidence:

- Fingerprints are source-evidence fingerprints; changed source-backed values should change fingerprints.
- Same-vintage package construction should replay identically.

Weakening evidence:

- Fingerprint differences cannot be explained by provider-backed vintage metadata.

Falsifying evidence:

- Same-vintage fingerprinting is unstable or cross-vintage difference is indistinguishable from nondeterministic drift.

### Prediction 6 — release identity is the central pressure point

Confidence: Very High.

Evidence:

- The accepted experiment intentionally isolates publication/vintage identity while holding series, period, unit, and frequency stable.

Weakening evidence:

- Selected ALFRED evidence does not expose clear vintage identifiers.

Falsifying evidence:

- Changed overlapping values cannot be tied to distinct provider-backed vintage evidence.

### Prediction 7 — implementation effort concentrates before the observed boundary

Confidence: High.

Evidence:

- TASK-053 through TASK-057 repeatedly concentrated effort in acquisition, metadata interpretation, normalization, and fixture design.

Weakening evidence:

- Most work shifts to post-boundary comparison, validation, lineage, or fingerprint changes.

Falsifying evidence:

- The deterministic substrate requires redesign before source-specific parsing/normalization can represent the evidence.

## Closeout checklist

- [x] RED test observed.
- [x] GREEN implementation observed.
- [x] Deterministic fixture preserved.
- [x] Implementation lessons written.
- [x] Confidence ledger updated.
- [x] Surprise log reviewed/updated.
- [x] Marginal cost and recurring pain reviewed/updated.
- [x] State, handoff, and summaries updated.
- [x] Verification completed.
