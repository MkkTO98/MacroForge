# Contract Validation and Drift Detection Specification

Date: 2026-06-27
Status: complete
Capability transition: Contract Validation and Drift Detection — Discovered -> Specified
Scope: WDI, OECD_NAAG, EUROSTAT_NAMQ_GDP; existing verified `ObservedIngestionPackage` v1 contract only

## Objective

Specify the smallest deterministic capability needed to detect implementation drift from the verified `ObservedIngestionPackage` v1 contract.

This task does not validate economic correctness, repair drift, introduce a generalized validation framework, expand datasets, redesign schemas, call models, or expand Deterministic Change Verification.

## Implementation summary

Added a narrow contract-drift module:

```text
src/macroforge/contract_drift.py
```

It exposes:

- `ContractDriftIssue`: deterministic issue code/path/message.
- `ContractDriftReport`: deterministic report for one observed package.
- `validate_observed_package_contract(package)`: validates one `ObservedIngestionPackage` against the current v1 invariants and returns a report.

Added tests:

```text
tests/test_contract_drift.py
```

The implementation is intentionally a deterministic invariant specification, not a validation framework. It contains no source registry, plugin API, schema migration, model call, repair behavior, or economic correctness rule.

## RED first evidence

The first targeted test run failed before production code existed:

```text
uvx --from pytest --with pyyaml pytest tests/test_contract_drift.py -q
ModuleNotFoundError: No module named 'macroforge.contract_drift'
1 error
```

## Contract drift model

Contract drift means a package or observation diverges from the verified `ObservedIngestionPackage` v1 boundary in a way that future deterministic ingestion work should not silently accept.

A drift report is deterministic:

```text
source_code
valid
fingerprint
recomputed_fingerprint
issues
```

Each issue is deterministic:

```text
code
path
message
```

The drift model only detects divergence. It does not infer intent, repair data, mutate source artifacts, mutate database state, or adjudicate economic truth.

## Implemented deterministic invariants

Package-level invariants:

1. `source_code`, `source_name`, `provider_dataset_code`, and `release_key` must be non-empty strings.
2. `raw_evidence` must remain a source-specific dictionary.
3. `input_filters` must remain a source-specific dictionary.
4. `row_count` must equal the number of observations.
5. `expected_row_count` must be non-negative.
6. package fingerprint must be reproducible when recomputed.

Observation-level invariants:

1. `provider_indicator_code`, `provider_territory_code`, `provider_period_code`, `frequency`, `unit_code`, `observation_status`, and `attribute_hash` must be non-empty strings.
2. Current v1 supported frequencies are only `A` and `Q`.
3. Current supported observations require `period_year`.
4. Annual observations must not set `period_quarter`.
5. Quarterly observations require `period_quarter` in `1..4`.
6. `attributes` must be a dictionary.
7. Empty attributes require the existing `empty` sentinel hash.
8. Non-empty attributes require canonical sorted/compact JSON SHA-256 hashing via `canonical_attribute_hash`.
9. `source_payload` must remain a source-specific dictionary.

These invariants are deliberately mechanical and contract-level. They do not validate whether GDP values are economically correct, whether a unit is analytically comparable, whether a territory mapping should be accepted, or whether source data is semantically trustworthy.

## Tests added

`tests/test_contract_drift.py` covers:

1. WDI, OECD_NAAG, and EUROSTAT_NAMQ_GDP packages satisfy the deterministic contract invariants.
2. package-level drift reports deterministic issue codes/paths/messages for missing required package fields and row-count mismatch.
3. observation-level drift reports deterministic issue codes/paths/messages for invalid attribute hashes and invalid quarterly periods.
4. observation-level drift reports deterministic issue codes/paths/messages for missing required current-source fields, unsupported frequency, and missing `period_year`.

## Supported sources covered

The tests cover all currently supported verified observed-boundary sources:

- WDI;
- OECD_NAAG;
- EUROSTAT_NAMQ_GDP.

## Verification

Targeted GREEN:

```text
uvx --from pytest --with pyyaml pytest tests/test_contract_drift.py -q
4 passed in 0.02s
```

Observed boundary regression:

```text
uvx --from pytest --with pyyaml pytest tests/test_contract_drift.py tests/test_observed_ingestion.py -q
11 passed in 0.04s
```

Cross-source deterministic regression including Deterministic Change Verification, lineage, loaders, and combined-source smoke:

```text
uvx --from pytest --with pyyaml pytest tests/test_contract_drift.py tests/test_observed_ingestion.py tests/test_deterministic_change_verification.py tests/test_lineage_generation.py tests/test_wdi_loader.py tests/test_oecd_sdmx_loader.py tests/test_eurostat_namq_loader.py tests/test_combined_source_smoke.py -q
27 passed in 3.37s
```

Full verification:

```text
uvx --from pytest --with pyyaml pytest tests -q
101 passed in 6.00s
```

The full test run temporarily regenerated deterministic report JSON files. They were restored because the changes were outside this task's scope:

```text
git restore artifacts/reports/canonical-gdp-snapshot-20260604.json artifacts/reports/combined-source-canonical-smoke-20260604.json

git status --short -- artifacts/reports/*.json
<no output>
```

## Capability maturity update

```text
Contract Validation and Drift Detection: Discovered -> Specified
```

Not claimed:

```text
Verified, Adopted, Shared, Stable, or Mature
```

Rationale: the task created a durable evidence-backed contract drift model and deterministic invariant specification that future verification can test against. It does not yet claim full Verified maturity because this task intentionally stops at the user-requested target.

## Architectural convergence assessment

### 1. Is MacroForge still converging toward a single shared deterministic ingestion substrate?

Yes. The new invariant layer begins immediately after the Observed Boundary and validates `ObservedIngestionPackage` packages independent of source-specific acquisition/parsing/loading internals. This strengthens the intended substrate: source-specific adapters produce packages; shared deterministic substrate can then validate, fingerprint, compare, generate lineage, and eventually support additional deterministic post-boundary mechanics.

### 2. Which extracted capabilities are now clearly part of that substrate?

Clearly substrate-aligned:

- `ObservedIngestionPackage` v1 observed boundary representation.
- Deterministic package fingerprinting.
- Deterministic package comparison.
- Deterministic Change Verification's reconstructed-package equivalence path.
- Canonical Lineage Event Generation.
- Contract Drift issue/report model and package invariant checks.

### 3. Which capabilities remain source-specific by design?

Still source-specific by design:

- acquisition and fetching;
- source-specific normalization;
- provider metadata parsing;
- source-specific staging schemas and SQL load details;
- provider period/territory/code mapping semantics;
- source-specific quality contexts;
- canonicalization review/approval semantics;
- dataset scope and fixture selection.

### 4. Is the current extraction strategy reducing future engineering effort for both new datasets and existing dataset updates?

Yes, with a narrow caveat. The shared substrate now provides one place to detect drift from the observed contract before changes silently propagate into downstream deterministic verification or lineage behavior. For new datasets, future adapters get a concrete target boundary. For existing dataset updates, invariant failures provide deterministic issue codes/paths/messages rather than requiring humans or LLMs to infer which contract assumption changed.

The caveat: this remains Specified, not Verified. It should become fully Verified only when the invariant layer is exercised as part of the accepted change-verification path, including reconstructed packages where appropriate.

### 5. Has any architectural fragmentation become visible?

No new fragmentation became visible. The implementation avoided another disconnected helper by making the drift model operate directly on `ObservedIngestionPackage`, the existing shared boundary. It did not introduce a parallel validation architecture, source registry, plugin layer, schema system, or economic-quality subsystem.

The remaining fragmentation risk is future overgrowth: if drift checks start absorbing source-specific provider semantics or economic quality rules, they would weaken the substrate by turning a contract boundary checker into a mixed validation framework. That risk is documented and should be resisted in the next transition.
