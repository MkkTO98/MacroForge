# TASK-055 — Bounded ECB SDW Architectural Experiment

Status: implemented and verified
Date: 2026-06-29
Related source selection review: `artifacts/reports/R-20260629-task-055-source-selection-review.md`
Related confidence ledger: `docs/architecture/architectural-confidence-ledger.md`

## Task framing

TASK-055 is not primarily "implement another source."

TASK-055 is an architectural experiment using a bounded ECB SDW evidence slice to test a specific hypothesis:

```text
Is SDMX becoming an architectural boundary, or is it merely an acquisition protocol whose commonality ends before the ObservedIngestionPackage boundary?
```

Implementation was approved on 2026-06-29 after the final methodology cadence refinement and completed as a bounded source-specific ECB SDW evidence slice.

## Architectural hypothesis under test

Current hypothesis:

```text
SDMX commonality is currently protocol-level. SDMX acquisition/parsing/metadata interpretation should remain source-specific before the ObservedIngestionPackage boundary until multiple independent implementations show contract, algorithm, and implementation convergence sufficient to justify an SDMX Interpretation Layer.
```

Alternative hypothesis:

```text
SDMX is becoming a real architectural boundary before ObservedIngestionPackage: OECD, ECB, IMF, and similar SDMX providers share enough deterministic acquisition, structure parsing, codelist interpretation, dimension-key construction, and observation normalization that a bounded SDMX Interpretation Layer would reduce future engineering/human/LLM effort without source-specific conditionals or semantic leakage.
```

## Confidence before implementation

Confidence in current hypothesis: 70%.

Rationale:

- OECD SDMX provided earlier evidence, but one SDMX-family source is insufficient to justify a shared SDMX layer.
- Eurostat used JSON-stat rather than SDMX in current MacroForge evidence.
- BEA and Treasury both confirmed that provider metadata can remain source-specific before the boundary.
- Existing post-boundary mechanics have survived heterogeneous sources without redesign.
- DEC-022 requires extraction only after repeated implementation evidence demonstrates convergence, not vocabulary similarity.

## Expected confidence after successful implementation

If ECB SDW completes as a bounded evidence slice without contract/substrate evolution and with provider-specific SDMX interpretation, expected confidence in current hypothesis rises from 70% to 80%.

If ECB exposes strong algorithm/implementation convergence with OECD while still fitting before the boundary, confidence should shift differently:

- Confidence that `ObservedIngestionPackage` is correctly placed may rise.
- Confidence that SDMX commonality is only protocol-level may fall toward 55-60%.
- Confidence that a future pre-boundary SDMX Interpretation Layer may become justified should rise, but not enough to implement it during TASK-055.

If ECB cannot be represented honestly without a shared SDMX abstraction or contract changes, confidence in the current hypothesis should fall below 50%.

## Evidence that would strengthen the current hypothesis

The current hypothesis is strengthened if ECB implementation shows:

- ECB SDW can produce a valid `ObservedIngestionPackage` using source-specific adapter code only.
- ECB SDMX dimensions, codelists, attributes, units, and dataflow metadata require provider-specific interpretation rather than reusable OECD logic.
- Similar XML/SDMX mechanics exist, but semantic decisions still depend on ECB-specific dimensions and dataflow meaning.
- No `ObservedIngestionPackage` fields or semantics require evolution.
- No Deterministic Ingestion Substrate components require evolution.
- Reusing OECD code would require source-specific conditionals, fragile assumptions, or loss of ECB provider evidence.
- Post-boundary validation, fingerprinting, comparison, lineage, and feedback work unchanged.

## Evidence that would weaken the current hypothesis

The current hypothesis is weakened if ECB implementation shows:

- ECB and OECD require substantially identical deterministic SDMX acquisition/parsing/codelist/observation algorithms.
- Most ECB-specific code is mechanical repetition of OECD SDMX logic rather than provider interpretation.
- A small source-neutral SDMX helper could eliminate duplicated code without source-specific conditionals.
- Provider-specific semantic interpretation is thin and mostly parameterized by dataflow metadata.
- The same normalized intermediate shape naturally appears before `ObservedIngestionPackage`.
- Tests for OECD and ECB could share meaningful fixtures/expectations without hiding provider differences.

Weakening evidence should be recorded as future extraction evidence only. It must not trigger SDMX layer implementation inside TASK-055 unless a separate task approves that scope.

## Evidence that would falsify the current hypothesis

The current hypothesis is falsified if ECB implementation shows one or more of:

- Honest ECB representation cannot be built without introducing a reusable SDMX interpretation boundary before `ObservedIngestionPackage`.
- ECB and OECD share a convergent, source-neutral SDMX-to-observed algorithm where source-specific adapters add little beyond endpoint/dataflow configuration.
- Avoiding a shared SDMX layer creates obvious deterministic inconsistency, duplicated bug-prone parsing, or divergent semantics across OECD/ECB.
- Existing source-specific approach forces source-specific conditionals into post-boundary substrate code.
- The `ObservedIngestionPackage` boundary is too late to preserve necessary SDMX structure/provenance without lossy encoding.

If falsified, the correct outcome is not immediate broad SDMX implementation. The correct outcome is a future design task evaluating a bounded SDMX Interpretation Layer before the observed boundary.

## Pre-implementation predictions

These predictions must be evaluated after implementation as Confirmed, Partially confirmed, or Refuted.

1. `ObservedIngestionPackage` contract evolution

Prediction: No contract evolution should be required if the bounded ECB slice uses annual, quarterly, or monthly observations.

Probability that `ObservedIngestionPackage` requires modification: 15%.

2. Deterministic Ingestion Substrate evolution

Prediction: No substrate evolution should be required. Existing fingerprinting, comparison, contract validation, lineage, and feedback should operate unchanged.

Probability substrate requires modification: 10%.

3. SDMX architectural boundary

Prediction: ECB will show SDMX commonality at acquisition/XML/protocol level, but provider interpretation will remain source-specific enough that no SDMX Interpretation Layer is justified yet.

Confidence: 70%.

4. Pre-boundary patterns expected

Expected ECB-specific pre-boundary patterns:

- SDMX XML acquisition/query provenance;
- ECB dataflow identity and key capture;
- codelist/attribute interpretation;
- provider-specific frequency/unit/dimension handling;
- deterministic provider indicator construction from SDMX dimensions;
- explicit evidence about whether OECD/ECB mechanics are converging.

5. Post-boundary expectations

Prediction: Post-boundary deterministic mechanics remain unchanged; any implementation effort remains before the observed boundary.

6. Future extraction evidence

Prediction: TASK-055 may produce evidence worth recording for a possible future SDMX Interpretation Layer, but will not by itself satisfy the extraction gate.

## What would justify considering an SDMX Interpretation Layer in the future

A future SDMX Interpretation Layer before `ObservedIngestionPackage` becomes worth considering if ECB produces several of these outcomes, especially if later confirmed by IMF or another SDMX provider:

- OECD and ECB share the same deterministic SDMX message parsing steps.
- Dataflow, structure, codelist, key, attribute, observation, and unit handling converge algorithmically.
- Provider-specific differences can be isolated as configuration or explicit adapter hooks without source-specific conditionals in shared code.
- A common intermediate SDMX-normalized representation naturally appears before `ObservedIngestionPackage`.
- Separate OECD/ECB implementations duplicate enough mechanical code that future maintenance risk increases.
- Shared SDMX tests could verify provider-neutral behavior while preserving provider-specific semantic tests.
- The layer would reduce future engineering/human/LLM effort for IMF/ECB/OECD-like sources measurably.
- The layer would preserve determinism, provenance, replayability, and provider evidence better than independent adapters.

If these outcomes appear, the correct next step is a separate bounded design or extraction-candidate task, not immediate extraction inside TASK-055.

## What would justify not creating an SDMX Interpretation Layer

Do not create an SDMX Interpretation Layer if ECB shows:

- SDMX syntax is shared, but provider semantics dominate implementation effort.
- ECB and OECD differ materially in dataflow structure, key dimensions, codelist usage, attribute meaning, unit metadata, or period semantics.
- Shared parsing would require source-specific conditionals.
- A generic layer would hide provider evidence or make deterministic replay less transparent.
- Existing source-specific adapters remain small, clear, and cheap to maintain.
- Most future effort remains selecting bounded datasets, interpreting provider metadata, and constructing source-specific identities rather than parsing XML mechanics.
- Post-boundary substrate remains stable and no repeated implementation pain appears.

## Non-goals

- No implementation before explicit user approval.
- No broad ECB support.
- No SDMX framework or interpretation layer extraction.
- No IMF/FRED/Treasury/BEA implementation.
- No canonical PostgreSQL loading.
- No live production writes.
- No daily-period contract expansion unless explicitly approved.
- No substrate redesign unless the current architecture fails under bounded implementation evidence.

## Implementation closeout

Implementation Lessons artifact evaluating each prediction as Confirmed / Partially confirmed / Refuted:

```text
artifacts/reports/L-20260629-task-055-implementation-lessons.md
```

Summary:

- Existing `ObservedIngestionPackage` contract required no evolution.
- Existing deterministic post-boundary substrate required no evolution.
- ECB SDW showed repeated SDMX GenericData XML mechanics with OECD, but provider interpretation remained ECB-specific enough that no SDMX Interpretation Layer is justified by TASK-055 alone.
- Future SDMX extraction evidence exists and should be watched, especially if IMF or another SDMX provider confirms stable source-neutral mechanics.

The closeout evaluated each prediction as:

- Confirmed;
- Partially confirmed;
- Refuted.

Two calibration steps were performed:

1. `docs/architecture/architectural-surprise-log.md` records no material TASK-055 architectural surprises; repeated SDMX XML mechanics were consistent with the prediction ledger.
2. `docs/architecture/architectural-confidence-ledger.md` records TASK-055 calibration for every tracked architectural assumption.

The lessons, surprise log, and confidence calibration update MacroForge's architectural judgment, especially the assumptions about SDMX commonality, observed-boundary placement, and extraction timing.
