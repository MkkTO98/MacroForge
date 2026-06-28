# TASK-054 — Bounded U.S. Treasury Fiscal Data Evidence Slice

Status: Complete
Created: 2026-06-28
Completed: 2026-06-28
Selection report: `artifacts/reports/R-20260628-task-054-candidate-source-selection.md`
Related decision: `artifacts/decisions/DEC-022-next-ten-source-expansion-optimization.md`

## Objective

Implement one bounded U.S. Treasury Fiscal Data API evidence slice through `ObservedIngestionPackage` to test whether row-oriented, paginated government JSON fiscal data requires any post-boundary architectural evolution.

The task optimizes for architectural learning per unit of implementation effort, not dataset popularity or indicator count.

## Candidate bounded source

Initial recommended target:

- Provider: U.S. Treasury Fiscal Data
- Source shape: public no-key JSON API with endpoint metadata
- Candidate endpoint: one small bounded endpoint such as `debt_to_penny` or `avg_interest_rates`
- Evidence type: fixture-backed bounded API response
- Goal: source-specific normalization and observed-package construction, not broad Treasury support

## Recurring effort reduction hypothesis

This task should permanently reduce future source-implementation effort by improving MacroForge's implementation knowledge for:

- deterministic API query provenance;
- public endpoint metadata preservation;
- bounded pagination discipline;
- fiscal date/period normalization;
- row-oriented government JSON table handling;
- categorical row identity construction without framework extraction.

## Non-goals

- Do not implement broad Treasury support.
- Do not build a source framework.
- Do not extract a pagination framework.
- Do not redesign the Deterministic Ingestion Substrate.
- Do not redesign `ObservedIngestionPackage`.
- Do not add canonical PostgreSQL loading.
- Do not write to live/default `macro`.
- Do not introduce semantic fiscal or economic interpretation conclusions.
- Do not extract reusable infrastructure unless multiple independent implementations demonstrate contract convergence, algorithm convergence, implementation convergence, deterministic verification, acceptable coupling, and measurable future effort reduction.

## Pre-implementation prediction ledger

1. Expected unchanged substrate components

Expected to remain unchanged:

- `ObservedIngestionPackage` and `ObservedObservation` dataclasses;
- package fingerprinting and comparison;
- contract validation and drift reporting;
- Deterministic Change Verification;
- Canonical Lineage Event Generation;
- Deterministic Ingestion Feedback;
- existing WDI, OECD_NAAG, EUROSTAT_NAMQ_GDP, BLS_CPI, and BEA_NIPA implementations.

2. Expected contract evolution

No `ObservedIngestionPackage` contract evolution is expected.

Treasury endpoint identity, query fields, filters, sort order, page metadata, labels, data types, fiscal date, provider value fields, and endpoint metadata should fit into existing source identity, provider dataset identity, release key, raw evidence, input filters, observation attributes, and provider indicator fields.

3. Expected engineering-effort concentration

- Acquisition: Low to Medium.
- Provider interpretation: Medium.
- Normalization: Medium.
- Observed package construction: Low.
- Deterministic substrate: Very Low.
- Canonical loading: None.
- Verification: Low.
- Testing: Medium.

4. Expected new reusable pre-boundary patterns

Likely pre-boundary evidence:

- deterministic API query provenance;
- endpoint metadata preservation;
- bounded pagination discipline;
- fiscal-date or fiscal-period normalization;
- row-oriented government JSON table handling;
- categorical row identity construction.

These should be documented as evidence, not extracted into shared infrastructure yet.

5. Expected new reusable post-boundary capability

No new reusable post-boundary capability is expected.

If this prediction holds, TASK-054 will further reinforce that repeated source difficulty is concentrated before `ObservedIngestionPackage`, while post-boundary deterministic mechanics remain reusable.

## Implementation workflow if accepted

RED -> minimal implementation -> targeted GREEN -> cross-source regression -> full/proportionate verification -> restore deterministic artifacts if needed -> Implementation Lessons artifact -> standard ProjectForge closeout.

## Acceptance criteria if accepted

- One bounded Treasury Fiscal Data raw fixture is recorded under `data/raw/treasury/`.
- A source-specific Treasury module normalizes the fixture into a valid `ObservedIngestionPackage`.
- Tests prove row count, selected observation identity/value semantics, metadata preservation, deterministic fingerprint/replay, and contract validity.
- Existing source package tests/regressions still pass.
- No substrate, observed-boundary, source-framework, canonical loader, migration, or live-write scope is introduced.
- A short `Implementation Lessons` artifact records confirmed/incorrect predictions, unexpected difficulties, reusable patterns, and future prediction changes.


## Outcome

Implemented and verified.

Implemented:

- `src/macroforge/treasury_fiscal_data.py`
- `tests/test_treasury_fiscal_data.py`
- `data/raw/treasury/treasury-avg-interest-rates-2026-05-31-raw.json`
- `data/raw/treasury/_SUMMARY.md`
- `artifacts/reports/L-20260628-task-054-implementation-lessons.md`

The bounded Treasury Fiscal Data evidence slice normalized one public `avg_interest_rates` API fixture for `record_date=2026-05-31` into 16 monthly observed observations and constructed a valid `ObservedIngestionPackage` without evolving the contract or changing post-boundary substrate components.

## Post-implementation prediction review

1. Existing substrate components unchanged — Confirmed.
   - No changes were required to `ObservedIngestionPackage`, fingerprinting/comparison, contract validation, Deterministic Change Verification, Canonical Lineage Event Generation, Deterministic Ingestion Feedback, or existing source implementations.

2. Additive `ObservedIngestionPackage` evolution — Confirmed as unnecessary.
   - Treasury endpoint identity, query provenance, labels, data types, pagination metadata, record date, categorical security description, and value field fit in existing package fields, raw evidence, input filters, attributes, and source payload.

3. Engineering-effort concentration — Confirmed.
   - Effort concentrated in deterministic API fixture capture, endpoint metadata preservation, monthly period interpretation from `record_date`, and provider indicator identity construction from `security_desc`.

4. New reusable pre-boundary patterns — Confirmed.
   - Treasury generated evidence for API query provenance, endpoint metadata preservation, bounded pagination metadata, fiscal date/monthly period normalization, and row-oriented government JSON table handling. These are evidence points, not extraction justification.

5. New reusable post-boundary capability — Confirmed as absent.
   - No post-boundary capability emerged. The current deterministic substrate remains the correct architecture.

## Implementation family retrospective

What this source taught MacroForge:

- Row-oriented public government JSON APIs can preserve deterministic query provenance and provider endpoint metadata before the observed boundary.
- Categorical API rows can construct provider indicator identity without changing the observed contract.

What this source taught about previous implementations:

- BEA table metadata and Treasury endpoint metadata are both provider-specific evidence patterns rather than justification for a shared provider metadata framework.
- TASK-054 further strengthens the default assumption from TASK-053: new source shapes should be expected to stress pre-boundary normalization before post-boundary substrate design.

## Verification

RED:

```text
uvx --from pytest --with pyyaml pytest tests/test_treasury_fiscal_data.py -q
```

Result:

```text
ModuleNotFoundError: No module named 'macroforge.treasury_fiscal_data'
1 error in 0.12s
```

Targeted GREEN:

```text
uvx --from pytest --with pyyaml pytest tests/test_treasury_fiscal_data.py -q
```

Result:

```text
4 passed in 0.03s
```

Cross-source regression:

```text
uvx --from pytest --with pyyaml pytest tests/test_treasury_fiscal_data.py tests/test_bea_nipa.py tests/test_bls_cpi.py tests/test_contract_drift.py tests/test_observed_ingestion.py tests/test_deterministic_change_verification.py tests/test_lineage_generation.py tests/test_ingestion_feedback.py -q
```

Result:

```text
32 passed in 1.75s
```

Full verification:

```text
uvx --from pytest --with pyyaml pytest tests -q
```

Result:

```text
118 passed in 6.59s
```

Known deterministic report JSON artifacts regenerated by full verification were restored afterward.
