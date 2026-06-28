# Deterministic Ingestion Substrate Execution Model

Date: 2026-06-27
Status: complete
Scope: implementation-oriented architectural clarification; no production code changes

## Objective

Document the deterministic execution model that has already emerged through implementation.

This clarification does not introduce a framework, redesign MacroForge, modify production code, or change capability maturity. It records only the execution order and interfaces supported by current implementation evidence.

## Capabilities covered

- Observed Boundary and Contract Stability
- Contract Validation and Drift Detection
- Deterministic Change Verification
- Canonical Lineage Event Generation

## Deterministic Ingestion Substrate execution model

The canonical execution model currently supported by implementation evidence is:

```text
Source-specific acquisition/parsing/normalization
  ↓
ObservedIngestionPackage construction
  ↓
Contract validation and drift detection on expected package
  ↓
Source-specific staging/canonical load SQL
  ├─ Canonical lineage event generation during loader-owned persistence
  ↓
Canonical PostgreSQL representation
  ↓
Deterministic change verification by reconstructing loaded package
  ↓
Contract validation and drift detection on reconstructed package
  ↓
Expected-vs-reconstructed package comparison/fingerprint equivalence
```

Important nuance: not all steps are fully wired as mandatory runtime steps today. The order above is the canonical substrate execution model implied by implemented contracts and tests. Contract Validation and Drift Detection is currently Specified, not Verified, so its placement is a future verification target rather than a claim that all loaders already enforce it.

## Capability interaction diagram

```text
            Source-specific code
  acquisition -> parsing -> normalization
                         |
                         v
              ObservedIngestionPackage v1
                         |
                         | consumed by
                         v
        Contract Validation and Drift Detection
        - deterministic issue report
        - fingerprint reproducibility
                         |
                         | package accepted as load input/evidence
                         v
          source-specific staging/canonical load SQL
                         |
                         | supplies explicit artifacts, row-count SQL,
                         | details, optional checksums
                         v
           Canonical Lineage Event Generation
           - raw_to_staging event
           - staging_to_curated event
                         |
                         v
            Canonical PostgreSQL representation
                         |
                         | reconstructed into
                         v
              ObservedIngestionPackage v1
                         |
                         | consumed by
                         v
        Contract Validation and Drift Detection
        - reconstructed-package invariant report
                         |
                         | consumed by
                         v
          Deterministic Change Verification
          - compare expected vs reconstructed package
          - fingerprint equivalence
          - row/observation count equivalence
          - changed-observation diagnostics
```

## Implementation evidence for execution order

### 1. Observed boundary comes after source-specific normalization

Evidence:

- `src/macroforge/observed_ingestion.py` defines `ObservedIngestionPackage` and `ObservedObservation`.
- The same module provides `build_wdi_observed_package`, `build_oecd_observed_package`, and `build_eurostat_observed_package` adapters from current normalized WDI/OECD/Eurostat artifacts.
- `tests/test_observed_ingestion.py` verifies that the adapters preserve existing WDI, OECD, and Eurostat loader semantics.

Conclusion: the boundary is after source-specific normalization and before shared deterministic substrate mechanics.

### 2. Contract drift validation consumes observed packages

Evidence:

- `src/macroforge/contract_drift.py` imports `ObservedIngestionPackage`, `ObservedObservation`, `canonical_attribute_hash`, and `observed_package_fingerprint`.
- `validate_observed_package_contract(package)` takes one `ObservedIngestionPackage` and returns a `ContractDriftReport` with deterministic source code, validity, fingerprints, and issue tuple.
- `tests/test_contract_drift.py` validates WDI, OECD_NAAG, and EUROSTAT_NAMQ_GDP packages and asserts deterministic issue codes/paths/messages for drift.

Conclusion: contract drift validation naturally runs immediately after package construction and should also run against reconstructed packages when the capability is verified.

### 3. Canonical lineage event generation composes with loader-owned persistence

Evidence:

- `src/macroforge/lineage_generation.py` exposes `canonical_lineage_events(...)` and `lineage_values_sql(...)`.
- The module generates exactly two converged event semantics: `raw_to_staging` and `staging_to_curated`.
- It requires loader-supplied artifacts, row-count SQL, details, and optional raw checksum.
- TASK-048 verified that persistence remains loader-owned: loaders still own `INSERT INTO meta.lineage_event`, source/run lookup, staging/canonical SQL, and idempotency behavior.
- `tests/test_lineage_generation.py` verifies deterministic event order and SQL VALUES rendering.

Conclusion: lineage generation belongs during the loader-owned load/persistence phase, after the source has enough explicit artifact and row-count evidence, but before or alongside the canonical PostgreSQL output being audited.

### 4. Deterministic change verification occurs after load

Evidence:

- `src/macroforge/deterministic_change_verification.py` exposes `verify_loaded_observed_package(db_name, expected_package)`.
- It reconstructs an observed package from staging/canonical PostgreSQL outputs and compares it to the expected package with `compare_observed_packages`.
- `tests/test_deterministic_change_verification.py` creates an isolated PostgreSQL database, applies migrations, loads WDI/OECD/Eurostat fixtures, builds expected packages, and asserts equivalence for all supported sources.

Conclusion: deterministic change verification naturally occurs after the load into isolated PostgreSQL, using the observed package as the comparison contract.

## Capability interface summary

| Capability | Primary input | Primary output | Deterministic guarantees | Upstream assumptions |
| --- | --- | --- | --- | --- |
| Observed Boundary and Contract Stability | Source-specific normalized WDI/OECD/Eurostat artifacts | `ObservedIngestionPackage` containing source identity, provider dataset identity, release key, raw evidence, input filters, row counts, and observations | Stable public internal package contract; deterministic package fingerprinting; deterministic comparison diagnostics | Acquisition/parsing/normalization has already produced source-specific normalized artifacts; source-specific semantics remain outside the package boundary |
| Contract Validation and Drift Detection | `ObservedIngestionPackage` | `ContractDriftReport` containing `source_code`, `valid`, `fingerprint`, `recomputed_fingerprint`, and deterministic issue tuple | Deterministic invariant checks; deterministic issue codes/paths/messages; fingerprint reproducibility check | Package fields follow `ObservedIngestionPackage` v1 structure; validation is contract-level only, not economic correctness or source semantic judgment |
| Canonical Lineage Event Generation | Explicit loader-supplied raw/staging/curated artifacts, scoped row-count SQL, details, optional checksum | Two `CanonicalLineageEvent` specs and deterministic SQL VALUES clause | Stable two-event order: `raw_to_staging`, `staging_to_curated`; storage-independent event semantics; deterministic SQL rendering | Loader owns persistence, source/run lookup, scoped row-count SQL, and staging/canonical SQL; source-specific behavior is not inside lineage generation |
| Deterministic Change Verification | Isolated PostgreSQL database name plus expected `ObservedIngestionPackage` | `ObservedPackageComparison` between expected and reconstructed package | Deterministic expected-vs-loaded equivalence; matching fingerprints; row-count, expected-row-count, observation-count checks; changed-observation diagnostics | Migrations/loaders have produced staging and canonical tables; expected package was built from the same source evidence; source-specific reconstruction SQL exists for current supported sources |

## Interface stability determination

The interfaces are sufficiently stable to guide future substrate extensions, with bounded caveats.

Stable enough now:

- `ObservedIngestionPackage` is the shared handoff and comparison contract across WDI, OECD_NAAG, and EUROSTAT_NAMQ_GDP.
- Package fingerprints and comparisons are deterministic and tested.
- Contract drift reports have deterministic issue structure and are tested for all supported sources.
- Lineage generation has a narrow stable two-event interface and preserves loader-owned persistence.
- Deterministic change verification has a clear post-load interface: expected package plus isolated database produces comparison evidence.

Caveats:

- Contract Validation and Drift Detection is only Specified; its canonical placement is clear, but it is not yet Verified in the accepted deterministic verification path.
- Deterministic Change Verification still contains source-specific reconstruction branches for current sources. This is acceptable for a proof helper but is not a source-agnostic substrate API.
- Loader-owned persistence means lineage generation is a substrate component by semantics, not a complete lineage subsystem.

Conclusion: future substrate extensions can use these interfaces as guidance, but should not treat them as a license to build a framework or prematurely generic loader API.

## Future substrate extension points

Implementation evidence suggests extension points, not new capabilities to implement now.

Natural extension points:

1. After expected `ObservedIngestionPackage` construction:
   - contract-level checks;
   - package diagnostics;
   - package fingerprint/evidence capture.

2. During loader-owned load/persistence:
   - deterministic event specification;
   - row-count evidence capture;
   - checksum/artifact evidence capture.

3. After isolated load reconstruction:
   - reconstructed-package contract checks;
   - expected-vs-reconstructed equivalence;
   - deterministic diagnostics for changed observations.

4. After comparison evidence:
   - bounded ingestion diagnostics and recovery evidence, if future implementation proves repeated deterministic patterns.

Non-extension areas unless new evidence appears:

- acquisition frameworks;
- parser frameworks;
- provider metadata interpretation;
- source-specific quality semantics;
- economic correctness validation;
- canonical mapping acceptance/review semantics;
- graph/catalog systems;
- orchestration/runtime systems.

## Technical debt recorded

Low-priority future maintenance item:

`state/project_state.md` and `state/architecture.md` are increasingly mixing current operational state with accumulated architectural history. This is not blocking current work, but after additional capability transitions MacroForge should consider separating concise current-state recovery files from longer architectural history/evidence summaries.

Do not implement this refactoring now.

## Recommendation for next genuine implementation capability

Recommended next implementation remains:

```text
Contract Validation and Drift Detection: Specified -> Verified
```

Narrow implementation direction:

- exercise `validate_observed_package_contract` in the accepted deterministic verification path;
- validate expected packages and reconstructed packages where appropriate;
- preserve WDI/OECD_NAAG/EUROSTAT_NAMQ_GDP source coverage;
- assert deterministic valid reports and/or deterministic issue surfaces;
- do not advance beyond Verified;
- do not introduce a generalized validation framework or runtime substrate object.

Rationale: this is the smallest next implementation that makes the documented substrate execution model real in deterministic verification without broadening MacroForge's architecture.
