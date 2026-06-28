# Observed Boundary and Contract Stability Verification Review

Date: 2026-06-27
Status: complete
Scope: evidence-based capability model consistency review; no production code changes

## Objective

Determine whether `Observed Boundary and Contract Stability` is already eligible for promotion from Specified to Verified based on accumulated implementation evidence, without performing additional implementation.

## Decision

Outcome A applies.

```text
Observed Boundary and Contract Stability: Specified -> Verified
```

The promotion is justified by objective implementation evidence accumulated after TASK-046, not by a new implementation task.

## Evidence review

### 1. Extraction from three independent implementations

TASK-046 extracted `ObservedIngestionPackage` v1 from current WDI, OECD_NAAG, and EUROSTAT_NAMQ_GDP implementations.

Evidence:

- `src/macroforge/observed_ingestion.py` defines immutable `ObservedIngestionPackage` and `ObservedObservation` contracts.
- `build_wdi_observed_package`, `build_oecd_observed_package`, and `build_eurostat_observed_package` adapt three source-specific normalized artifacts into the same package contract.
- `docs/architecture/observed-ingestion-representation.md` documents the public internal boundary, field ownership, invariants, compatibility expectations, versioning policy, and explicit out-of-contract areas.
- TASK-046 verified loader/combined-source equivalence after extraction:

```text
uvx --from pytest --with pyyaml pytest tests/test_wdi_loader.py tests/test_oecd_sdmx_loader.py tests/test_eurostat_namq_loader.py tests/test_combined_source_smoke.py -q
12 passed in 2.51s
```

This proves the boundary was extracted from existing behavior across three implementations without changing downstream loader behavior.

### 2. Deterministic package fingerprints and package comparison

`tests/test_observed_ingestion.py` verifies deterministic replay/equivalence mechanics for the package boundary:

- WDI package preserves existing loader semantics.
- OECD package preserves existing loader semantics.
- Eurostat package preserves existing loader semantics.
- `observed_package_fingerprint` is deterministic for replayed packages.
- `compare_observed_packages` reports equivalent replay.
- `compare_observed_packages` reports deterministic changed-observation diagnostics.
- The module is guarded against becoming a generalized framework.

This proves the contract is not merely documented; it has deterministic comparison evidence.

### 3. End-to-end deterministic change verification

`tests/test_deterministic_change_verification.py` verifies WDI, OECD_NAAG, and EUROSTAT_NAMQ_GDP end-to-end through isolated PostgreSQL loading.

The test:

1. creates an isolated PostgreSQL database;
2. applies current migrations;
3. loads WDI, OECD_NAAG, and EUROSTAT_NAMQ_GDP fixture-backed evidence through current loaders;
4. builds expected `ObservedIngestionPackage` instances from source fixtures;
5. reconstructs loaded observed packages from staging/canonical PostgreSQL outputs;
6. compares expected and reconstructed packages deterministically.

Asserted evidence includes:

- source set is exactly `{WDI, OECD_NAAG, EUROSTAT_NAMQ_GDP}`;
- package comparison is equivalent for each source;
- left/right fingerprints match;
- row counts match;
- expected row counts match;
- observation counts match;
- differing observations are empty.

This satisfies the capability model definition of Verified: deterministic checks prove current behavior and preserve equivalence.

### 4. Canonical Lineage Event Generation depends on the boundary

TASK-048 verified `Canonical Lineage Event Generation` using the existing observed-boundary and deterministic-change-verification evidence.

Its cross-source verification included:

```text
uvx --from pytest --with pyyaml pytest tests/test_lineage_generation.py tests/test_wdi_loader.py tests/test_oecd_sdmx_loader.py tests/test_eurostat_namq_loader.py tests/test_combined_source_smoke.py tests/test_deterministic_change_verification.py -q
16 passed in 3.23s
```

The lineage extraction preserved expected lineage counts:

```text
{"EUROSTAT_NAMQ_GDP": 2, "OECD_NAAG": 2, "WDI": 2}
```

The successful extraction of a post-boundary capability without altering package equivalence is additional objective evidence that the observed boundary is stable enough to support downstream verified capability work.

## Capability dependency consistency assessment

The previous graph state was inconsistent:

```text
Observed Boundary and Contract Stability: Specified
  -> Deterministic Change Verification: Verified
  -> Canonical Lineage Event Generation: Verified
```

A parent capability can sometimes remain at a lower maturity than a child when the child uses only a narrow subset of the parent or when the parent is broad and intentionally not fully verified. That exception does not apply here.

In this case, Deterministic Change Verification fundamentally depends on reconstructing and comparing `ObservedIngestionPackage` outputs. Canonical Lineage Event Generation was verified by a test set that includes deterministic package equivalence across WDI/OECD/Eurostat. The child capabilities do not merely use an incidental subset of the boundary; their correctness rests on the boundary contract being deterministic and stable for current supported sources.

Therefore, leaving Observed Boundary and Contract Stability at Specified while dependent capabilities are Verified understated the actual implementation evidence.

## Maturity interpretation refinement

The capability model should explicitly record this principle:

> Capability maturity is determined by objective implementation evidence, not by the chronological order in which implementation tasks were completed or recorded.

This principle is supported by the implementation history. TASK-046 established the contract. Subsequent deterministic fingerprinting, package comparison, isolated PostgreSQL reconstruction, deterministic change verification, and lineage extraction provided additional proof after the initial capability state was recorded.

## Promotion scope

The promotion is limited to current supported evidence:

- WDI;
- OECD_NAAG;
- EUROSTAT_NAMQ_GDP;
- current `ObservedIngestionPackage` v1 fields/invariants;
- current fixture-backed source behavior;
- current downstream loader/canonical behavior.

Not claimed:

- Adopted: future work has not yet made the observed boundary the required canonical implementation path for all relevant ingestion changes.
- Shared/Stable/Mature: more adoption history, contract-evolution discipline, and broader regression history are still required.
- New sources, source expansion, generalized ingestion framework, parser abstraction, plugin registry, or runtime orchestration.

## Updated capability graph implication

After promotion:

```text
Observed Boundary and Contract Stability: Verified
  -> Deterministic Change Verification: Verified
  -> Canonical Lineage Event Generation: Verified
```

This graph is now dependency-consistent for current supported sources.

## Next capability requiring genuine new implementation

With Observed Boundary and Contract Stability now Verified, the next capability whose prerequisites are fully satisfied and which requires genuine new implementation is:

```text
Contract Validation and Drift Detection: Discovered -> Specified -> Verified
```

Recommended next implementation target:

- specify and implement narrow `ObservedIngestionPackage` invariant/drift checks derived from the existing contract and deterministic verification outputs;
- keep scope limited to current WDI/OECD/Eurostat package invariants;
- avoid generalized validation frameworks;
- do not expand Deterministic Change Verification itself;
- do not extract quality-check handling, provider metadata, canonical dimension mechanics, canonical upserts, runtime orchestration, graph/catalog behavior, source registries, or new datasets.

The smallest useful implementation is not another broad verification task. It is a narrow contract/drift check layer that detects boundary-breaking changes before or alongside existing package equivalence checks.
