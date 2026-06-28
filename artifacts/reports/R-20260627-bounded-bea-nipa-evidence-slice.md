# Report — TASK-053 Bounded BEA NIPA Evidence Slice

Date: 2026-06-27
Status: Implemented and verified

## Purpose

TASK-053 begins MacroForge's Evidence-Accumulating Source Expansion phase by implementing one bounded BEA NIPA evidence slice.

The implementation goal was not broad BEA support. The goal was to determine whether a materially different trustworthy economic source could pass through the existing deterministic ingestion boundary while producing implementation evidence that reinforces or challenges the current architecture.

## Implemented slice

- Provider: U.S. Bureau of Economic Analysis
- Dataset family: NIPA
- Bounded evidence: NIPA Table 1.1.1, Percent Change From Preceding Period in Real Gross Domestic Product
- Acquisition evidence: public BEA iTableCore `GetSteps` response for Survey category and table key 1
- Raw fixture: `data/raw/bea/bea-nipa-t10101-itablecore-20260625-raw.json`
- Source module: `src/macroforge/bea_nipa.py`
- Tests: `tests/test_bea_nipa.py`

The implemented source-specific module normalizes BEA interactive table rows into observed observations and constructs an `ObservedIngestionPackage` without adding framework behavior or redesigning the substrate.

## Pre-implementation prediction review

### 1. Existing substrate components expected to remain unchanged

Classification: Confirmed.

The following stayed unchanged:

- `ObservedIngestionPackage` and `ObservedObservation` dataclasses;
- deterministic fingerprinting and package comparison;
- contract validation/drift reporting;
- Deterministic Ingestion Feedback;
- Canonical Lineage Event Generation;
- Deterministic Change Verification;
- existing WDI, OECD_NAAG, EUROSTAT_NAMQ_GDP, and BLS_CPI implementations.

BEA passed through the current observed-package contract using existing annual/quarterly/monthly frequency support, existing attributes, existing raw evidence, and existing release-key behavior.

### 2. Possible additive ObservedIngestionPackage contract evolution

Classification: Confirmed.

No additive contract evolution was required. BEA-specific table/line semantics fit into the existing contract:

- `provider_indicator_code`: `T10101:L<line_number>`;
- `provider_indicator_label`: BEA line description;
- `provider_territory_code`: `USA`;
- `provider_period_code`: quarterly period such as `2024-Q1`;
- `attributes`: BEA table key, table id, line number, line description, section name, subtitle, release description, and cell style metadata;
- `raw_evidence`: source URL, raw artifact path, raw SHA-256, and release description.

The prediction that release metadata would remain source-specific was confirmed.

### 3. Engineering-effort concentration

Classification: Confirmed.

Observed effort distribution:

- Acquisition: Medium. BEA's conventional API required an API key, but the public iTableCore path provided bounded evidence without broad acquisition infrastructure.
- Provider interpretation: High. Most effort went into understanding BEA's interactive table shape, nested prompt data, table key, title, subtitle, header rows, row stubs, and line numbers.
- Normalization: High. The BEA table required converting two header rows plus data rows into line/period observations.
- Observed package construction: Low. Once normalized, package construction was direct.
- Deterministic substrate: Very Low. No substrate code changed.
- Canonical loading: None. Out of scope.
- Verification: Low. Existing fingerprint/comparison/contract validation applied directly.
- Testing: Medium. Tests lock table identity, row count, first observation semantics, contract validity, deterministic replay, and no-framework boundaries.

This reinforces the prior engineering-effort assessment: effort concentrates before `ObservedIngestionPackage`, while post-boundary mechanics are reusable.

### 4. Expected new reusable pre-boundary patterns

Classification: Confirmed.

The implementation generated new pre-boundary evidence:

- table/line-code normalization for official table-based economic data;
- interactive-table header interpretation;
- row-stub and line-number identity construction;
- release-description capture;
- source-specific acquisition fallback when a conventional public API path requires credentials;
- preservation of provider table metadata as attributes before canonical interpretation.

These are now evidence points, not extracted abstractions. One BEA implementation is insufficient to justify shared infrastructure.

### 5. Expected new reusable post-boundary capability

Classification: Confirmed.

No new reusable post-boundary capability emerged. The existing deterministic substrate handled the BEA package unchanged.

## Architectural observations

Repeated implementation evidence did not justify architectural evolution.

TASK-053 reinforces the current architecture:

- source-specific normalization should remain source-specific;
- `ObservedIngestionPackage` remains the correct handoff boundary;
- deterministic post-boundary mechanics are reusable across heterogeneous sources;
- architectural extraction should wait for repeated evidence across more sources, especially if table/line-code or interactive-table patterns recur.

The correct architectural action is therefore no substrate redesign.

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
uvx --from pytest --with pyyaml pytest tests/test_bea_nipa.py tests/test_bls_cpi.py tests/test_contract_drift.py tests/test_observed_ingestion.py tests/test_wdi_loader.py tests/test_oecd_sdmx_loader.py tests/test_eurostat_namq_loader.py tests/test_deterministic_change_verification.py tests/test_lineage_generation.py tests/test_ingestion_feedback.py -q
```

Result:

```text
34 passed in 3.31s
```

Full verification:

```text
uvx --from pytest --with pyyaml pytest tests -q
```

Result:

```text
114 passed in 6.73s
```

The full test run regenerated known deterministic report JSON artifacts only through temporary isolated database identifiers. They were restored afterward.

## Outcome

TASK-053 confirms that MacroForge's next phase should be Evidence-Accumulating Source Expansion.

Every new source should continue to produce explicit prediction/review evidence so MacroForge improves not only source coverage but also its ability to predict where future implementation effort will concentrate.
