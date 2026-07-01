# TASK-057 — Bounded BIS WS_CBPOL SDMX Evidence Slice

Status: implemented and verified
Date: 2026-06-30

## Objective

Implement the smallest Bank for International Settlements central-bank policy-rate evidence slice that maximizes architectural learning without broadening MacroForge's architecture.

Selected bounded slice:

- Source: Bank for International Settlements public SDMX API
- Dataflow: `WS_CBPOL`
- Indicator concept: central bank policy rates
- Frequency: monthly
- Reference areas: `US`, `JP`
- Periods: `2024-01` through `2024-03`
- Expected observations: 6

## Why this is the next recommended source

TASK-056 strengthened SDMX-family extraction evidence across OECD/ECB/IMF but did not justify generic SDMX extraction. BIS is the next high-leverage bounded source because it adds another independent institutional SDMX provider, uses reachable public data, and exercises dataflow/series/attribute metadata without access-key friction.

This is not selected for business value alone. It is selected to test whether the SDMX-family pattern is converging toward extraction or still remains source-specific before `ObservedIngestionPackage`.

## Non-goals

Do not implement:

- broad BIS support;
- broad WS_CBPOL support;
- generic SDMX infrastructure;
- source registry/plugin infrastructure;
- canonical loading;
- database writes;
- generic policy-rate model;
- IMF/BIS reconciliation logic;
- KnowledgeForge claims or cross-source truth assertions.

## Pre-implementation prediction ledger

### Prediction 1 — Observed contract evolution

Prediction: `ObservedIngestionPackage` will require no evolution.

Probability of required contract modification: 5%.

Expected reason: BIS policy-rate observations should fit existing provider indicator, territory, period, frequency, unit, value, attributes, raw evidence, and source payload fields.

### Prediction 2 — Deterministic substrate evolution

Prediction: deterministic post-boundary substrate will require no evolution.

Probability of substrate modification: 3%.

Expected reason: package fingerprinting, contract validation, comparison, and replay should operate unchanged once BIS-specific normalization produces the existing observed package shape.

### Prediction 3 — New pre-boundary patterns

Expected source-specific pre-boundary work:

- BIS SDMX StructureSpecificData parsing;
- BIS dataflow identity preservation;
- BIS reference-area code interpretation (`US`, `JP`);
- BIS series-level policy-rate metadata preservation (`SOURCE_REF`, `COMPILATION`, `DECIMALS`, `TITLE`);
- BIS observation-level status/confidentiality attributes;
- source-specific policy-rate indicator identity construction.

### Prediction 4 — Reusable lessons

Expected reusable lesson: another SDMX-family provider will increase evidence about repeated SDMX mechanics, but source-specific dataflow, code, and attribute interpretation will still dominate enough to avoid generic SDMX extraction.

### Prediction 5 — Effort distribution

Expected relative effort:

- Acquisition: Low
- Provider interpretation: Medium
- Normalization: Low-Medium
- Observed package construction: Low
- Substrate: Very Low
- Canonical loading: None
- Verification/testing: Medium

## Acceptance criteria

- A source-specific BIS adapter normalizes the bounded fixture.
- The adapter builds a valid `ObservedIngestionPackage` with six observations.
- Fixture evidence is preserved with source URL and SHA-256.
- Tests prove deterministic replay and contract validity.
- Anti-framework tests prove no generic SDMX/BIS/client/database layer was introduced.
- Closeout records whether predictions were confirmed, partially confirmed, or refuted.
