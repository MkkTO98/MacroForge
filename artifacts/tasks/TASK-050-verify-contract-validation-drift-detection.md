# TASK-050 — Verify Contract Validation and Drift Detection

Status: complete
Date: 2026-06-27
Capability: Contract Validation and Drift Detection
Transition: Specified -> Verified

## Objective

Verify the previously specified deterministic `ObservedIngestionPackage` contract-drift checks by exercising them in the accepted deterministic verification path for current supported sources.

## Scope

Included:

- WDI;
- OECD_NAAG;
- EUROSTAT_NAMQ_GDP;
- existing `ObservedIngestionPackage` v1 contract;
- expected package contract validation;
- reconstructed loaded package contract validation;
- deterministic expected-vs-loaded package comparison.

Excluded:

- economic validation;
- semantic data-quality rules;
- provider-specific interpretation;
- generalized validation frameworks;
- orchestration;
- source frameworks;
- graph/catalog systems;
- new datasets;
- capability advancement beyond Verified.

## Files changed

Production:

- `src/macroforge/deterministic_change_verification.py`

Tests:

- `tests/test_deterministic_change_verification.py`

State/reporting:

- `artifacts/reports/R-20260627-contract-validation-drift-detection-verification.md`
- `docs/architecture/capability-maturity-model.md`
- `state/active_goal.md`
- `state/project_state.md`
- `state/architecture.md`
- `context/latest_handoff.md`
- affected `_SUMMARY.md` files
- `artifacts/tasks/backlog.md`

## RED evidence

```text
uvx --from pytest --with pyyaml pytest tests/test_deterministic_change_verification.py -q
ImportError: cannot import name 'verify_loaded_observed_package_contracts' from 'macroforge.deterministic_change_verification'
1 error
```

The failure was expected: the test required a deterministic verification-path helper that did not yet exist.

## Implementation summary

Added narrow verification-path evidence to `src/macroforge/deterministic_change_verification.py`:

- `LoadedObservedPackageContractVerification`;
- `verify_loaded_observed_package_contracts(db_name, expected_package)`.

The helper:

1. reconstructs the loaded observed package using the existing source-specific deterministic verification reconstruction path;
2. validates the expected package with `validate_observed_package_contract`;
3. validates the reconstructed loaded package with `validate_observed_package_contract`;
4. compares expected and reconstructed packages with `compare_observed_packages`;
5. returns all three deterministic evidence objects.

No loader behavior, schema, economic validation, provider semantics, source framework, or generalized validation framework was added.

## GREEN / verification evidence

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

Report JSON restore check:

```text
git restore artifacts/reports/canonical-gdp-snapshot-20260604.json artifacts/reports/combined-source-canonical-smoke-20260604.json && git status --short -- artifacts/reports/*.json
<no output>
```

## Outcome

Contract Validation and Drift Detection is Verified.

Not advanced beyond Verified.

## Architectural observation

Implementation revealed additional evidence of a narrow deterministic execution contract for the verification path:

```text
expected ObservedIngestionPackage + isolated loaded PostgreSQL state
-> expected package contract report
-> reconstructed loaded package contract report
-> expected-vs-loaded package comparison
```

This evidence is not yet sufficient to formalize a project-wide Deterministic Ingestion Substrate execution contract. It supports the existing execution-model interpretation, but no new architectural concept or framework was introduced.

## Next recommendation

Next genuine implementation capability candidate:

```text
Ingestion Diagnostics and Recovery Evidence: Discovered -> Specified
```

Rationale: now that contract validation is Verified in the deterministic verification path, the next useful work is to specify compact deterministic diagnostics/recovery evidence from replay/change-verification outputs, without broadening into frameworks, orchestration, economic validation, or source expansion.
