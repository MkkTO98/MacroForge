# Bounded BLS Monthly Evidence Slice Implementation Review

Date UTC: 2026-06-27
Task: `artifacts/tasks/TASK-051-bounded-bls-monthly-evidence-slice.md`
Status: complete

## Conclusion

TASK-051 confirms that the current architecture survives a monthly, series-oriented source with minimal contract evolution.

The implementation did not add general BLS support. It used BLS CPI series `CUUR0000SA0` for 2023 as a bounded architectural experiment.

## Key implementation evidence

Added:

- `src/macroforge/bls_cpi.py` — source-specific fixture normalizer and observed-package builder.
- `data/raw/bls/bls-cpi-cuur0000sa0-2023-raw.json` — deterministic recorded BLS raw fixture.
- `tests/test_bls_cpi.py` — bounded parser/package/anti-framework tests.

Minimal contract evolution:

- `ObservedObservation.period_month: int | None`.
- Contract drift validation now allows `A`, `Q`, and `M`.
- Monthly observations require `period_month` 1-12 and no `period_quarter`.
- Annual/quarterly observations must not set `period_month`.

No PostgreSQL loader, migration, production write, live fetch path, source framework, series framework, acquisition framework, provider metadata framework, plugin system, orchestration, runtime redesign, model call, conversion, aggregation, or dataset expansion was added.

## Engineering-effort assessment

Effort concentrated before the observed boundary:

- acquisition: low;
- provider interpretation: medium;
- normalization: medium;
- observed-package construction: low;
- deterministic substrate: very low;
- canonical loading: none;
- deterministic verification: low;
- testing: medium.

Compared with WDI/OECD_NAAG/EUROSTAT_NAMQ_GDP, TASK-051 supports the accepted substrate-utilization conclusion: engineering effort is migrating toward acquisition/provider interpretation/normalization while remaining stable or decreasing after `ObservedIngestionPackage`.

## Architectural answer

The current source-specific ownership model remains correct before `ObservedIngestionPackage`.

Weak repeated pre-boundary evidence is accumulating around recorded fixtures, checksums, source URLs, provider period parsing, provider identifier/label preservation, source payload retention, and stable observation ordering. This is not yet enough to extract a reusable Source Interpretation Layer.

## Verification

RED:

```text
uvx --from pytest --with pyyaml pytest tests/test_bls_cpi.py tests/test_contract_drift.py::test_monthly_observation_contract_requires_month_between_one_and_twelve -q
```

Result:

```text
ModuleNotFoundError: No module named 'macroforge.bls_cpi'
1 error in 0.10s
```

Targeted GREEN:

```text
uvx --from pytest --with pyyaml pytest tests/test_bls_cpi.py tests/test_contract_drift.py -q
8 passed in 0.04s
```

Cross-source regression:

```text
uvx --from pytest --with pyyaml pytest tests/test_bls_cpi.py tests/test_contract_drift.py tests/test_observed_ingestion.py tests/test_wdi_loader.py tests/test_oecd_sdmx_loader.py tests/test_eurostat_namq_loader.py tests/test_deterministic_change_verification.py -q
22 passed in 2.95s
```

Full verification:

```text
uvx --from pytest --with pyyaml pytest tests -q
105 passed in 6.69s
```

Generated report JSON diffs were limited to isolated temporary database names and were restored.

## Capability outcome

No broad capability maturity advancement was recorded.

`Observed Boundary and Contract Stability` and `Contract Validation and Drift Detection` remain Verified, now with minimal monthly A/Q/M contract coverage.

## Future technical debt

After approximately six materially different sources, require:

**Pre-Boundary Pattern Emergence Review**

Question:

> Has implementation evidence now justified extracting a reusable Source Interpretation Layer before the ObservedIngestionPackage boundary?

Do not extract unless repeated implementations demonstrate contract convergence, algorithm convergence, implementation convergence, deterministic verification, acceptable coupling, and measurable engineering-effort reduction.

## Recommended next task

TASK-052 should specify deterministic ingestion diagnostics/recovery evidence from existing observed-package verification outputs. BLS monthly contract evidence may be used as a bounded input example if useful, but TASK-052 should not create a pre-boundary layer.
