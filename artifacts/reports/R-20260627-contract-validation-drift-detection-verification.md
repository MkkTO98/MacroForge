# Contract Validation and Drift Detection Verification

Date: 2026-06-27
Status: complete
Capability transition: Contract Validation and Drift Detection — Specified -> Verified
Scope: WDI, OECD_NAAG, EUROSTAT_NAMQ_GDP; existing `ObservedIngestionPackage` v1 contract and accepted deterministic verification path only

## Objective

Verify the previously specified deterministic contract-drift capability by exercising `ObservedIngestionPackage` invariant checks in the accepted deterministic verification path.

This task did not broaden the capability into economic validation, semantic quality rules, provider-specific interpretation, generalized validation frameworks, orchestration, source frameworks, graph/catalog systems, or new datasets.

## Implementation summary

Added narrow verification-path integration in:

```text
src/macroforge/deterministic_change_verification.py
```

New public evidence shape:

```text
LoadedObservedPackageContractVerification
```

New helper:

```text
verify_loaded_observed_package_contracts(db_name, expected_package)
```

The helper returns:

- `expected_contract_report`: contract drift report for the expected fixture-backed `ObservedIngestionPackage`;
- `loaded_contract_report`: contract drift report for the package reconstructed from isolated PostgreSQL staging/canonical outputs;
- `comparison`: deterministic expected-vs-reconstructed `ObservedPackageComparison`.

The implementation reuses existing deterministic mechanics:

- `validate_observed_package_contract` from `contract_drift.py`;
- `_loaded_observed_package` reconstruction from `deterministic_change_verification.py`;
- `compare_observed_packages` from `observed_ingestion.py`.

No loader semantics, SQL schemas, source-specific provider interpretation, economic validation, quality rules, or runtime framework were changed.

## RED evidence

The first test change required a missing verification-path helper:

```text
uvx --from pytest --with pyyaml pytest tests/test_deterministic_change_verification.py -q
ImportError: cannot import name 'verify_loaded_observed_package_contracts' from 'macroforge.deterministic_change_verification'
1 error
```

This failed for the expected reason: the implementation did not yet expose deterministic contract validation for expected and reconstructed packages in the accepted verification path.

## Verification evidence

Targeted GREEN:

```text
uvx --from pytest --with pyyaml pytest tests/test_deterministic_change_verification.py -q
1 passed in 0.95s
```

Targeted substrate regression:

```text
uvx --from pytest --with pyyaml pytest tests/test_contract_drift.py tests/test_deterministic_change_verification.py tests/test_observed_ingestion.py -q
12 passed in 1.07s
```

Cross-source deterministic regression:

```text
uvx --from pytest --with pyyaml pytest tests/test_contract_drift.py tests/test_observed_ingestion.py tests/test_deterministic_change_verification.py tests/test_lineage_generation.py tests/test_wdi_loader.py tests/test_oecd_sdmx_loader.py tests/test_eurostat_namq_loader.py tests/test_combined_source_smoke.py -q
27 passed in 3.64s
```

Full verification:

```text
uvx --from pytest --with pyyaml pytest tests -q
101 passed in 6.54s
```

Full verification regenerated deterministic report JSON artifacts with temporary isolated database identifiers. They were restored because they were outside this task's intended change scope:

```text
git restore artifacts/reports/canonical-gdp-snapshot-20260604.json artifacts/reports/combined-source-canonical-smoke-20260604.json && git status --short -- artifacts/reports/*.json
<no output>
```

## Capability maturity transition

```text
Contract Validation and Drift Detection: Specified -> Verified
```

Not claimed:

```text
Adopted, Shared, Stable, or Mature
```

## Architectural observations

The implementation reinforced the emerging Deterministic Ingestion Substrate execution model without requiring a new framework.

Evidence observed:

```text
expected ObservedIngestionPackage + isolated loaded PostgreSQL state
-> expected package contract report
-> reconstructed loaded package contract report
-> expected-vs-reconstructed package comparison
```

This provides implementation evidence of a narrow deterministic execution contract for the accepted verification path:

- deterministic input boundary: expected `ObservedIngestionPackage` plus isolated loaded database state;
- deterministic precondition check: expected package satisfies contract invariants;
- deterministic postcondition check: reconstructed loaded package satisfies contract invariants;
- deterministic equivalence check: expected and reconstructed packages compare equivalent.

However, this is not yet sufficient to formalize a project-wide Deterministic Ingestion Substrate execution contract. It should remain an observation until repeated future substrate capabilities demonstrate the same entry/exit guarantees and ordering.

## Next recommended implementation capability

```text
Ingestion Diagnostics and Recovery Evidence: Discovered -> Specified
```

Reason: with contract validation now Verified inside the deterministic verification path, the next useful capability is compact deterministic diagnostics/recovery evidence from replay/change-verification outputs. This should remain bounded to evidence/reporting and should not expand into orchestration, source frameworks, semantic validation, economic correctness, catalog/graph systems, or new datasets.
