# MacroForge Capability Maturity Model

Status: active v1.1 implementation-planning model
Date: 2026-06-27
Scope: capability planning and maturity tracking only; not a runtime architecture

## Purpose

MacroForge implementation planning is now capability-maturity driven.

Tasks are execution units. Capabilities are the planning units.

A task is valuable when it permanently reduces future deterministic engineering effort, human judgment, LLM reasoning, or uncertainty for trustworthy economic datasets while preserving determinism, auditability, provenance, reproducibility, and canonical consistency. Moving a durable platform capability to a higher maturity state is valuable only when implementation evidence shows it reduces future effort.

This document is the lightweight capability model for v1.1. It is not a new governance subsystem, registry, workflow engine, or strategic roadmap report.

## Final maturity lifecycle

```text
Discovered
  -> Specified
  -> Verified
  -> Adopted
  -> Shared
  -> Stable
  -> Mature
```

### Discovered

A repeated behavior, need, or architectural opportunity has been observed in implementation evidence.

A discovered capability is real enough to track, but not yet specified as a contract or target behavior.

### Specified

A narrow evidence-backed contract, target behavior, or acceptance boundary is documented.

A specified capability has a durable description that future implementation can test against.

### Verified

Deterministic checks prove current behavior and preserve equivalence.

A verified capability has replay, fingerprints, tests, diagnostics, or equivalent deterministic evidence proving that current implementation behavior is understood and preserved.

Capability maturity is determined by objective implementation evidence, not by the chronological order in which implementation tasks were completed or recorded. A capability may be promoted when later implementation evidence proves its definition, even if the original task only recorded an earlier maturity.

### Adopted

The verified capability has become the canonical implementation path MacroForge uses for the relevant scope.

Adopted distinguishes proof from operational authority. A capability can be verified without yet being the canonical implementation that future work should build on.

### Shared

Reusable shared implementation exists and is used without source-specific conditionals.

Shared capability has moved beyond canonical use in one place into reusable infrastructure across more than one current path.

### Stable

The capability is used by multiple current paths, documented, and regression-protected.

Stable capability has low churn and can be depended on by ordinary implementation without repeated architectural reconsideration.

### Mature

The capability can guide future source or dataset expansion with low uncertainty and minimal strategic intervention.

Mature capability reduces future deterministic engineering, human judgment, LLM reasoning, and uncertainty.

## Capability graph

```text
Strategic Objective
  Decrease the marginal cost of trustworthy economic-data ingestion
  without sacrificing determinism, auditability, provenance, or canonical consistency.

  -> Capability A: Observed Boundary and Contract Stability
  -> Capability B: Deterministic Change Verification
       - replay
       - fingerprints
       - equivalence checks
       - drift detection
       - diagnostics
  -> Capability C: Contract Validation and Drift Detection
  -> Capability D: Deterministic Ingestion Feedback
  -> Capability E: Shared Post-Boundary Infrastructure Extraction
       -> Capability E.1: Canonical Lineage Event Generation
  -> Capability F: Canonicalization Governance and Mapping Advancement
  -> Capability G: Evidence-Accumulating Source Expansion
```

## Capability prerequisites

Prerequisites are intentionally lightweight. They are not a planning subsystem, dependency scheduler, or roadmap. They record only capabilities that must already be Verified before the listed capability can safely advance beyond its current state.

Use `None` when no capability prerequisite has been established.

## Capability maturity table

| Capability | Current maturity | Target maturity for v1.1 | Verified prerequisites before safe advancement | Remaining transition | Implementation work required |
| --- | --- | --- | --- | --- | --- |
| Observed Boundary and Contract Stability | Verified | Adopted, then Stable | None | Verified -> Adopted | Accumulated TASK-046 through TASK-048 evidence already verifies current WDI/OECD/Eurostat boundary stability: extracted package contract, deterministic package fingerprints/comparison, end-to-end isolated PostgreSQL package equivalence, and downstream lineage extraction regression. Next: adopt by making the verified package boundary the required path for relevant ingestion changes. |
| Deterministic Change Verification | Verified | Stable | Observed Boundary and Contract Stability (Verified) | Verified -> Adopted -> Shared -> Stable | End-to-end isolated PostgreSQL verification now proves WDI/OECD/Eurostat fixture -> loader -> staging/canonical output -> reconstructed observed package -> deterministic comparison equivalence. Next: adopt as the required change-verification path before shared extraction. |
| Contract Validation and Drift Detection | Verified | Verified for v1.1; Adopted only after a future required-use task | Observed Boundary and Contract Stability (Verified); Deterministic Change Verification (Verified) | Verified -> Adopted only if future ingestion work makes contract validation a required gate | TASK-050 verified the narrow deterministic drift model by validating expected and reconstructed WDI/OECD/Eurostat packages inside the accepted deterministic verification path. Do not advance further without a separate adoption task. |
| Deterministic Ingestion Feedback | Verified for current v1.1 scope | Adopted only if a future task makes feedback a required report surface for deterministic verification | Deterministic Change Verification (Verified); Contract Validation and Drift Detection (Verified) | Verified -> Adopted | TASK-052 implemented deterministic explanatory feedback from existing contract reports, package comparisons, lineage events, and source effort profiles. Do not advance further without a separate adoption task that attaches feedback to accepted verification/report surfaces. |
| Shared Post-Boundary Infrastructure Extraction | Discovered | Verified readiness, not necessarily Shared | Deterministic Change Verification (Verified) | Discovered -> Specified -> Verified-readiness | Use deterministic change verification evidence plus `foundational_capability_extraction` consultation before extracting shared lineage, validation, quality, metadata, or canonical loading helpers. |
| Canonical Lineage Event Generation | Verified | Adopted only after future required-use task | Deterministic Change Verification (Verified) | Verified -> Adopted only if future source/loader work makes generated lineage the required canonical path | TASK-048 verified the narrow shared two-event generation algorithm for WDI/OECD/Eurostat while preserving loader-owned persistence SQL. Do not advance further without a separate adoption task. |
| Canonicalization Governance and Mapping Advancement | Stable for file-backed lifecycle; Discovered/Specified for OECD/Eurostat advancement | Stable for lifecycle; Verified for targeted advancement paths when needed | Deterministic Change Verification (Verified) for mapping changes that affect loaded observed/canonical outputs | Preserve Stable lifecycle; advance targeted paths only through evidence | Keep file-backed lifecycle deterministic; add targeted review/diagnostic evidence only when a downstream blocker or accepted task requires OECD/Eurostat advancement. |
| Evidence-Accumulating Source Expansion | Discovered | Specified through the next bounded heterogeneous source | Deterministic Change Verification (Verified); Deterministic Ingestion Feedback (Verified) | Discovered -> Specified | Current implementation evidence now supports source expansion as the next primary learning mechanism. Use a bounded heterogeneous source to validate, strengthen, and selectively evolve the substrate; keep substrate evolution reactive to implementation evidence. |

## Evidence-based consistency review

The capability model was reviewed after TASK-048 to ensure maturity reflects implementation evidence rather than historical task order.

Result:

```text
Observed Boundary and Contract Stability: Specified -> Verified
```

Supporting evidence:

- TASK-046 extracted `ObservedIngestionPackage` v1 from WDI, OECD_NAAG, and EUROSTAT_NAMQ_GDP implementations.
- `tests/test_observed_ingestion.py` proves source package semantics, deterministic fingerprints, equivalent replay comparison, deterministic changed-observation diagnostics, and anti-framework boundaries.
- `tests/test_deterministic_change_verification.py` proves end-to-end isolated PostgreSQL package equivalence for WDI, OECD_NAAG, and EUROSTAT_NAMQ_GDP by reconstructing loaded packages from staging/canonical outputs and comparing them with expected fixture-backed packages.
- TASK-048 verified Canonical Lineage Event Generation while preserving package equivalence and cross-source regression behavior.

Detailed review: `artifacts/reports/R-20260627-observed-boundary-contract-stability-verification-review.md`.

## Current implementation posture

Latest completed source implementation:

```text
TASK-054 — Bounded U.S. Treasury Fiscal Data Evidence Slice
```

Rationale: TASK-054 confirmed row-oriented public government JSON with endpoint metadata and bounded pagination metadata can pass through `ObservedIngestionPackage` without contract/substrate evolution. The accepted default assumption remains that the current post-boundary architecture is correct until repeated implementation evidence falsifies it. The next TASK-055 selection should use TASK-054's durable lesson: prefer the bounded source slice that exercises the most new pre-boundary provider shape while staying inside the existing observed contract.

Future source work should remain narrow:

- implement one bounded trustworthy source slice through `ObservedIngestionPackage`;
- use the source to attempt to falsify the default substrate-stability assumption;
- keep source-specific acquisition, parsing, provider metadata interpretation, staging/loading, and mapping decisions source-specific until repeated implementation pain justifies extraction;
- do not introduce orchestration, a source framework, pagination framework extraction, recovery automation, runtime monitoring, economic validation, semantic quality rules, graph/catalog systems, broad source support, or substrate-first feature work.

After every heterogeneous source implementation, add a short `Implementation Lessons` artifact. If three consecutive heterogeneous sources complete without meaningful post-boundary architectural evolution, record the future technical-debt trigger for one bounded Deterministic Ingestion Substrate Stability Review; do not run that review proactively.

## Contract Validation and Drift Detection verification

Contract Validation and Drift Detection is now:

```text
Verified
```

Completed transitions:

```text
Discovered -> Specified -> Verified
```

Evidence:

- TASK-049 specified deterministic `ObservedIngestionPackage` invariant checks and issue codes/paths/messages.
- TASK-050 added `verify_loaded_observed_package_contracts`, which validates expected and reconstructed loaded packages and returns contract reports plus package comparison evidence.
- `test_deterministic_change_verification.py` now verifies expected and reconstructed package contract reports are valid for WDI, OECD_NAAG, and EUROSTAT_NAMQ_GDP inside the isolated PostgreSQL verification path.

Detailed verification: `artifacts/reports/R-20260627-contract-validation-drift-detection-verification.md`.

Next target:

```text
Verified -> Adopted
```

Only pursue adoption after a separate task explicitly makes contract validation a required gate for relevant ingestion/package changes.

Deterministic Change Verification remains:

```text
Deterministic Change Verification: Verified
```

Completed transitions:

```text
Discovered -> Specified -> Verified
```

Evidence:

- `observed_package_fingerprint` and `compare_observed_packages` provide the deterministic comparison contract.
- `verify_loaded_observed_package` reconstructs the loaded observed package from isolated PostgreSQL staging/canonical outputs and compares it with the expected fixture-backed `ObservedIngestionPackage`.
- `test_deterministic_change_verification.py` proves equivalence for WDI, OECD, and Eurostat end-to-end.

Next target:

```text
Verified -> Adopted
```

The first implementation tasks specified and then verified deterministic `ObservedIngestionPackage` replay/equivalence diagnostics under Deterministic Change Verification.

## First implementation task

The first implementation task specified and implemented deterministic `ObservedIngestionPackage` replay/equivalence diagnostics as the first task under Deterministic Change Verification.

Implemented narrow scope:

- use current WDI/OECD/Eurostat fixture-backed behavior as evidence;
- produce deterministic fingerprints/equivalence output for existing packages;
- include narrow contract invariant checks only if they directly support replay/equivalence;
- preserve source-specific acquisition, normalization, staging, SQL loading, provider mappings, lineage, quality checks, canonical facts, and validation semantics;
- do not introduce a generalized ingestion framework;
- do not rename or redesign `ObservedIngestionPackage`;
- do not extract shared runtime infrastructure beyond diagnostic support;
- do not add new datasets or deepen existing datasets.

Completed maturity results:

```text
Deterministic Change Verification: Discovered -> Specified -> Verified.
```

Not claimed:

```text
Adopted, Shared, Stable, or Mature.
```

Next work may advance Deterministic Change Verification from Verified -> Adopted if MacroForge makes this end-to-end verification path the required change-verification path for relevant ingestion/package changes.

## Foundational capability extraction checklist

This checklist is the standard engineering template for future foundational capability extractions. It is not a new planning subsystem. It is the minimum evidence gate before extracting shared post-boundary infrastructure.

Before implementation, record:

1. Contract convergence: current implementations expose the same durable inputs, outputs, invariants, and ownership boundary.
2. Algorithm convergence: current implementations use the same semantic algorithm; differences are explicit inputs, not hidden source-specific branches.
3. Implementation convergence: repeated implementation exists in current source paths and can be extracted without introducing source-specific conditionals.
4. Deterministic verification availability: tests, replay, fingerprints, isolated database checks, or equivalent deterministic evidence can prove behavior before and after extraction.
5. ArchitectureHarvest consultation completed: `foundational_capability_extraction` consultation has investigated architectural patterns, failure modes, over-abstraction risks, minimal extraction, and reasons not to extract.
6. Semantic coupling acceptable: the extracted capability will not improperly own source-specific acquisition, provider semantics, persistence policy, runtime orchestration, catalog/graph behavior, or broader frameworks outside the evidence.
7. Capability prerequisites satisfied: every prerequisite listed in the capability model is already Verified, or the task is explicitly limited to documenting/specifying rather than advancing the dependent capability.

During and after implementation, record:

1. Capability name refined to durable semantic capability, not current mechanism.
2. Explicit extraction boundary and non-goals.
3. RED test or equivalent failing deterministic check proving the missing shared capability.
4. GREEN targeted tests proving the extracted capability.
5. Cross-source equivalence/regression tests proving supported behavior unchanged.
6. Full-suite or proportionate final verification.
7. Remaining coupling risks and reasons not to advance beyond the target maturity.

TASK-048 is the first completed instance of this checklist for `Canonical Lineage Event Generation`.

## Contract Validation and Drift Detection specification

TASK-049 moved Contract Validation and Drift Detection from Discovered to Specified.

Scope:

- current WDI, OECD_NAAG, and EUROSTAT_NAMQ_GDP packages only;
- existing verified `ObservedIngestionPackage` v1 contract only;
- deterministic contract drift detection only;
- no economic correctness validation;
- no repair behavior;
- no generalized validation framework.

Contract drift means a package or observation diverges from the verified `ObservedIngestionPackage` v1 boundary in a way that future deterministic ingestion work should not silently accept.

The specified report shape is:

```text
ContractDriftReport:
  source_code
  valid
  fingerprint
  recomputed_fingerprint
  issues

ContractDriftIssue:
  code
  path
  message
```

Specified deterministic invariants:

- required package fields are non-empty;
- `raw_evidence` and `input_filters` remain source-specific dictionaries;
- package `row_count` equals observation count;
- package `expected_row_count` is non-negative;
- package fingerprint is reproducible;
- required observation fields are non-empty;
- current supported frequencies are `A` and `Q`;
- current supported observations require `period_year`;
- annual observations do not set `period_quarter`;
- quarterly observations set `period_quarter` in `1..4`;
- `attributes` and `source_payload` remain dictionaries;
- empty attributes use the `empty` sentinel;
- non-empty attributes use canonical sorted/compact JSON SHA-256 hashing.

Implementation: `src/macroforge/contract_drift.py`.
Tests: `tests/test_contract_drift.py`.
Detailed report: `artifacts/reports/R-20260627-contract-validation-drift-detection-specification.md`.

## Default planning rule

Future planning should update this capability model rather than append a long sequential task list.

After each implementation task:

```text
Implement
  -> Verify
  -> Update capability maturity
  -> Select next capability transition from evidence
  -> Implement
```

Do not produce further governance or strategic reports unless implementation exposes genuinely new architectural uncertainty that cannot be resolved from the Constitution, this capability model, contracts, dependency graph, or deterministic verification evidence.
