# TASK-049 — Specify Contract Validation and Drift Detection

Status: complete
Date: 2026-06-27
Capability: Contract Validation and Drift Detection
Transition: Discovered -> Specified

## Objective

Implement the smallest capability necessary to specify how MacroForge detects divergence from the verified `ObservedIngestionPackage` v1 contract.

## Scope

Included:

- WDI;
- OECD_NAAG;
- EUROSTAT_NAMQ_GDP;
- existing verified `ObservedIngestionPackage` v1 contract;
- deterministic package/observation invariants;
- drift issue codes, paths, and messages.

Excluded:

- generalized validation frameworks;
- plugin systems;
- schema redesign;
- dataset expansion;
- semantic economic correctness rules;
- model calls;
- repair behavior.

## Files changed

Production:

- `src/macroforge/contract_drift.py`

Tests:

- `tests/test_contract_drift.py`

Governance/state/reporting:

- `artifacts/reports/R-20260627-contract-validation-drift-detection-specification.md`
- `docs/architecture/capability-maturity-model.md`
- `state/active_goal.md`
- `state/project_state.md`
- `state/architecture.md`
- `context/latest_handoff.md`
- affected `_SUMMARY.md` files
- `artifacts/tasks/backlog.md`

## RED evidence

```text
uvx --from pytest --with pyyaml pytest tests/test_contract_drift.py -q
ModuleNotFoundError: No module named 'macroforge.contract_drift'
1 error
```

## GREEN / verification evidence

```text
uvx --from pytest --with pyyaml pytest tests/test_contract_drift.py -q
4 passed in 0.02s
```

```text
uvx --from pytest --with pyyaml pytest tests/test_contract_drift.py tests/test_observed_ingestion.py -q
11 passed in 0.04s
```

```text
uvx --from pytest --with pyyaml pytest tests/test_contract_drift.py tests/test_observed_ingestion.py tests/test_deterministic_change_verification.py tests/test_lineage_generation.py tests/test_wdi_loader.py tests/test_oecd_sdmx_loader.py tests/test_eurostat_namq_loader.py tests/test_combined_source_smoke.py -q
27 passed in 3.37s
```

```text
uvx --from pytest --with pyyaml pytest tests -q
101 passed in 6.00s
```

Report JSON restore check:

```text
git status --short -- artifacts/reports/*.json
<no output>
```

## Outcome

Contract Validation and Drift Detection is now Specified.

Not advanced beyond Specified.

## Architectural assessment

The implementation strengthens convergence toward a single deterministic ingestion substrate because the new drift specification operates directly on `ObservedIngestionPackage`, the verified observed boundary. It does not create a parallel framework or source-specific validation layer.

The next transition, if requested, should verify this capability by integrating the invariant checks into the accepted deterministic verification path where appropriate, including reconstructed loaded packages. Do not broaden into economic validation or provider-specific semantics.
