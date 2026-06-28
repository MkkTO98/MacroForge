# TASK-053 — Bounded BEA NIPA Evidence Slice

Status: Complete
Created: 2026-06-27

## Objective

Implement one bounded BEA NIPA evidence slice as the first source in MacroForge's Evidence-Accumulating Source Expansion phase.

The task tests whether another heterogeneous trustworthy source can pass through the existing deterministic ingestion boundary while generating implementation evidence that either reinforces or challenges the current architecture.

## Scope

Implement a narrow BEA NIPA table evidence slice through `ObservedIngestionPackage`.

Initial bounded source target:

- Provider: U.S. Bureau of Economic Analysis
- Dataset family: NIPA
- Evidence slice: one NIPA table selected for GDP/product-account evidence
- Goal: source-specific normalization and observed-package construction, not broad BEA support

## Non-goals

- Do not broaden BEA support.
- Do not build a source framework.
- Do not redesign the Deterministic Ingestion Substrate.
- Do not extract reusable infrastructure unless implementation evidence clearly demands it.
- Do not add production database writes unless explicitly scoped later.
- Do not add canonical loading unless implementation evidence and task scope require it.
- Do not introduce investment or economic interpretation conclusions.

## Pre-implementation prediction

### 1. Expected unchanged substrate components

Expected to remain completely unchanged:

- `ObservedIngestionPackage` fingerprinting and package comparison.
- `ObservedObservation` identity fields.
- Contract validation and drift reporting.
- Deterministic Ingestion Feedback.
- Canonical Lineage Event Generation.
- Deterministic Change Verification.
- Existing WDI, OECD_NAAG, EUROSTAT_NAMQ_GDP, and BLS_CPI loaders/tests.

### 2. Possible additive `ObservedIngestionPackage` evolution

No additive contract evolution is expected if the BEA slice is bounded to annual or quarterly table observations. The existing fields should express:

- table/line code as provider indicator identity;
- NIPA table title/line description as labels;
- USA as provider territory;
- annual or quarterly period structure;
- BEA table metadata in attributes/raw evidence.

Possible additive pressure: if BEA revision/release metadata cannot be represented cleanly in `release_key`, `raw_evidence`, or `attributes`, but this is expected to be source-specific for the bounded slice.

### 3. Expected engineering-effort concentration

- Acquisition: Medium. BEA public API key requirements may complicate live access, so bounded fixture acquisition may require BEA iTable evidence rather than broad API integration.
- Provider interpretation: High. BEA NIPA table/line metadata and interactive table structure differ materially from existing source shapes.
- Normalization: High. Table headers, line numbers, row stubs, frequencies, and period columns must be normalized into observations.
- Observed package construction: Low to Medium. Existing observed-package shape should fit after normalization.
- Deterministic substrate: Very Low. No substrate redesign expected.
- Canonical loading: None. Out of scope.
- Verification: Low to Medium. Existing fingerprint/contract checks should apply.
- Testing: Medium. Tests must lock the bounded table shape, row extraction, period parsing, attributes, and contract validity.

### 4. Expected new reusable pre-boundary patterns

Likely pre-boundary evidence:

- table/line-code normalization;
- interactive-table header interpretation;
- release-description capture;
- source-specific acquisition fallback when official API requires credentials;
- provider table metadata preservation before the observed boundary.

These should be documented as evidence, not extracted into shared infrastructure yet.

### 5. Expected new reusable post-boundary capability

No new reusable post-boundary capability is expected. If the prediction holds, BEA should reinforce that repeated source difficulty is concentrated before `ObservedIngestionPackage`, while post-boundary deterministic mechanics remain reusable.

## Implementation workflow

RED -> minimal implementation -> targeted GREEN -> cross-source regression -> full verification -> restore deterministic artifacts if needed -> post-implementation review.

## Outcome

Status: Complete.

Implemented:

- `src/macroforge/bea_nipa.py`
- `tests/test_bea_nipa.py`
- `data/raw/bea/bea-nipa-t10101-itablecore-20260625-raw.json`
- `data/raw/bea/_SUMMARY.md`
- `artifacts/reports/R-20260627-bounded-bea-nipa-evidence-slice.md`

The bounded BEA NIPA evidence slice normalized BEA iTableCore NIPA Table 1.1.1 evidence into 252 quarterly observed observations and constructed a valid `ObservedIngestionPackage` without evolving the contract or changing post-boundary substrate components.

## Post-implementation prediction review

1. Existing substrate components unchanged — Confirmed.
   - No changes were required to `ObservedIngestionPackage`, fingerprinting/comparison, contract validation, ingestion feedback, lineage generation, deterministic change verification, or existing source implementations.

2. Additive `ObservedIngestionPackage` evolution — Confirmed as unnecessary.
   - BEA table/line metadata fit into existing provider identity, attributes, raw evidence, and release-key fields.

3. Engineering-effort concentration — Confirmed.
   - Effort concentrated in acquisition, provider interpretation, and normalization. Observed-package construction and deterministic verification were low effort. Canonical loading remained out of scope.

4. New reusable pre-boundary patterns — Confirmed.
   - BEA generated evidence for table/line-code normalization, interactive-table header interpretation, row-stub identity, and release-description capture. These are evidence points, not yet shared infrastructure.

5. New reusable post-boundary capability — Confirmed as absent.
   - No post-boundary capability emerged. The current deterministic substrate remains the correct architecture.

## Verification

RED:

```text
uvx --from pytest --with pyyaml pytest tests/test_bea_nipa.py -q
```

Result:

```text
ModuleNotFoundError: No module named 'macroforge.bea_nipa'
1 error in 0.11s
```

Targeted GREEN:

```text
uvx --from pytest --with pyyaml pytest tests/test_bea_nipa.py -q
```

Result:

```text
4 passed in 0.60s
```

Cross-source regression:

```text
34 passed in 3.31s
```

Full verification:

```text
114 passed in 6.73s
```

Known deterministic report JSON artifacts were restored after full verification.
