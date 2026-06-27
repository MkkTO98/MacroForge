# MacroForge Capability Maturity Model

Status: active v1.1 implementation-planning model
Date: 2026-06-27
Scope: capability planning and maturity tracking only; not a runtime architecture

## Purpose

MacroForge implementation planning is now capability-maturity driven.

Tasks are execution units. Capabilities are the planning units.

A task is valuable when it moves a durable platform capability to a higher maturity state or preserves an already-mature capability under change.

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
  -> Capability D: Ingestion Diagnostics and Recovery Evidence
  -> Capability E: Shared Post-Boundary Infrastructure Extraction
  -> Capability F: Canonicalization Governance and Mapping Advancement
  -> Capability G: Knowledge-Accumulating Source Expansion
```

## Capability maturity table

| Capability | Current maturity | Target maturity for v1.1 | Remaining transition | Implementation work required |
| --- | --- | --- | --- | --- |
| Observed Boundary and Contract Stability | Specified | Adopted, then Stable | Specified -> Verified -> Adopted | Deterministic package replay/equivalence diagnostics proving WDI/OECD/Eurostat package behavior; then use verified package path as canonical boundary for relevant ingestion changes. |
| Deterministic Change Verification | Verified | Stable | Verified -> Adopted -> Shared -> Stable | End-to-end isolated PostgreSQL verification now proves WDI/OECD/Eurostat fixture -> loader -> staging/canonical output -> reconstructed observed package -> deterministic comparison equivalence. Next: adopt as the required change-verification path before shared extraction. |
| Contract Validation and Drift Detection | Discovered | Verified | Discovered -> Specified -> Verified | Add narrow invariant checks and drift signals derived from package/replay evidence; avoid generalized validation frameworks until repeated needs converge. |
| Ingestion Diagnostics and Recovery Evidence | Discovered | Verified | Discovered -> Specified -> Verified | Produce compact deterministic diagnostic artifacts from replay/change-verification outputs; support future agent recovery and debugging. |
| Shared Post-Boundary Infrastructure Extraction | Discovered | Verified readiness, not necessarily Shared | Discovered -> Specified -> Verified-readiness | Use deterministic change verification evidence plus `foundational_capability_extraction` consultation before extracting shared lineage, validation, quality, metadata, or canonical loading helpers. |
| Canonicalization Governance and Mapping Advancement | Stable for file-backed lifecycle; Discovered/Specified for OECD/Eurostat advancement | Stable for lifecycle; Verified for targeted advancement paths when needed | Preserve Stable lifecycle; advance targeted paths only through evidence | Keep file-backed lifecycle deterministic; add targeted review/diagnostic evidence only when a downstream blocker or accepted task requires OECD/Eurostat advancement. |
| Knowledge-Accumulating Source Expansion | Discovered | Specified after verification capabilities mature | Discovered -> Specified | Do not add/deepen sources by default; define source-expansion work only after deterministic change verification and diagnostics make each new source leave durable ingestion knowledge. |

## Next capability

The next capability should be named:

```text
Deterministic Change Verification
```

This name is broader and more accurate than `Replay and Equivalence Assurance`.

Replay and equivalence are mechanisms. The long-term capability is the ability to determine, with deterministic evidence, whether an implementation change preserves intended ingestion behavior or reveals drift.

This capability includes:

- replay;
- fingerprints;
- equivalence checks;
- contract invariant checks;
- drift detection;
- deterministic diagnostics;
- evidence for safe adoption of future shared infrastructure.

## Next maturity transition

Current maturity:

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
