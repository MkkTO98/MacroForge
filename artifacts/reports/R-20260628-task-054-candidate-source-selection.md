# Report — TASK-054 Candidate Source Selection

Date: 2026-06-28
Status: candidate selected; implementation not started
Related decision: `artifacts/decisions/DEC-022-next-ten-source-expansion-optimization.md`
Related lessons: `artifacts/reports/L-20260628-task-053-implementation-lessons.md`

## Selection criterion

Which source is expected to teach MacroForge the most about trustworthy ingestion while requiring the least architectural change?

This criterion intentionally does not optimize for dataset popularity or indicator count. It optimizes for architectural diversity and implementation learning per unit of effort.

## Current default assumption

After TASK-053, the default assumption is that the current post-boundary architecture is correct:

```text
source-specific acquisition and normalization
-> ObservedIngestionPackage
-> deterministic post-boundary substrate
```

Future source work should attempt to falsify this assumption. It should not replace the assumption with proactive substrate redesign.

## Candidate assessment

### 1. U.S. Treasury Fiscal Data API — selected

Bounded target candidate: one small Fiscal Data API endpoint, preferably a daily or monthly fiscal table such as `debt_to_penny` or `avg_interest_rates`, normalized into an `ObservedIngestionPackage` fixture.

Live accessibility probe on 2026-06-28:

- `debt_to_penny`: HTTP 200 JSON with `data` and `meta`.
- `avg_interest_rates`: HTTP 200 JSON with `data` and `meta`.

Expected engineering-effort distribution:

- Acquisition: Low to Medium. Public no-key JSON API is accessible, but deterministic query construction, fields, filters, sorting, and pagination must be captured.
- Provider interpretation: Medium. Fiscal Data includes endpoint metadata, labels, data types, fiscal concepts, daily/monthly records, and possibly table-like categorical dimensions.
- Normalization: Medium. Values are row-oriented JSON rather than table/line or SDMX cube. Period/date handling and category-to-indicator identity need source-specific choices.
- Observed package construction: Low. Existing provider identity, territory, period, attributes, raw evidence, and release key should fit.
- Substrate: Very Low. No meaningful post-boundary evolution expected.
- Canonical loading: None. Out of scope.
- Verification: Low. Existing fingerprint, contract validation, and package replay expectations should apply.
- Testing: Medium. Tests should lock query provenance, pagination/metadata preservation if scoped, deterministic row ordering, contract validity, and no-framework boundaries.

Expected contract evolution: None.

Expected substrate evolution: None.

Expected reusable implementation knowledge:

- deterministic API query provenance;
- endpoint metadata preservation;
- bounded pagination discipline;
- fiscal-date or fiscal-period normalization;
- row-oriented government JSON table handling;
- categorical row identity construction without adding source-framework machinery.

Prediction confidence: High.

Why selected:

Treasury Fiscal Data is materially different from WDI, OECD, Eurostat, BLS, and BEA while remaining accessible and bounded. It should teach MacroForge about public API query provenance, pagination, endpoint metadata, and fiscal-period/date handling with low expected contract/substrate pressure.

### 2. ALFRED/FRED vintage-aware bounded series

Expected engineering-effort distribution:

- Acquisition: Medium to High. FRED/ALFRED API behavior may require an API key depending on endpoint and query.
- Provider interpretation: High. Vintage/realtime metadata introduces a distinction between observation period and data availability/revision period.
- Normalization: Medium.
- Observed package construction: Medium.
- Substrate: Low to Medium, depending on whether vintage identity can remain in release metadata/attributes or requires explicit contract treatment.
- Canonical loading: None.
- Verification: Medium.
- Testing: Medium.

Expected contract evolution: Possible. Vintage/realtime semantics may pressure `release_key`, attributes, or future explicit revision identity.

Expected substrate evolution: Possible but not expected for a very bounded artifact.

Expected reusable implementation knowledge:

- revision/vintage handling;
- realtime date versus observation date;
- release/calendar metadata;
- time-series metadata provenance.

Prediction confidence: Medium.

Reason not selected now:

High architectural value, but higher contract-pressure and access uncertainty than Treasury. It is a strong falsification candidate after one more low-friction heterogeneous source.

### 3. ECB Data Portal / SDMX bounded slice

Expected engineering-effort distribution:

- Acquisition: Medium. Public SDMX endpoint is reachable.
- Provider interpretation: Medium to High. SDMX structures and codelists need interpretation.
- Normalization: Medium.
- Observed package construction: Low.
- Substrate: Very Low.
- Canonical loading: None.
- Verification: Low to Medium.
- Testing: Medium.

Expected contract evolution: None.

Expected substrate evolution: None.

Expected reusable implementation knowledge:

- second independent SDMX-family source evidence;
- cross-provider SDMX similarities/differences;
- codelist/metadata interpretation pressure.

Prediction confidence: Medium to High.

Reason not selected now:

ECB is valuable, but because MacroForge already has OECD SDMX evidence, it is less architecturally diverse than Treasury Fiscal Data for the immediate next task.

## Selection

Select Treasury Fiscal Data API for TASK-054.

Recommended task title:

```text
TASK-054 — Bounded U.S. Treasury Fiscal Data Evidence Slice
```

Implementation objective:

```text
Implement one bounded U.S. Treasury Fiscal Data API evidence slice through ObservedIngestionPackage to test whether row-oriented, paginated government JSON fiscal data requires any post-boundary architectural evolution.
```

Non-goals:

- no broad Treasury support;
- no source framework;
- no pagination framework extraction;
- no canonical PostgreSQL loading;
- no live production writes;
- no semantic fiscal/economic interpretation;
- no substrate redesign;
- no observed-boundary redesign;
- no shared helper extraction unless repeated implementation evidence satisfies DEC-022's extraction gate.

## Prediction ledger for TASK-054

1. Existing substrate components should remain unchanged.
2. No `ObservedIngestionPackage` contract evolution is expected.
3. Engineering effort should concentrate in deterministic API query capture, endpoint metadata interpretation, fiscal date/period normalization, and row identity construction.
4. New reusable pre-boundary patterns should include API query provenance, endpoint metadata preservation, bounded pagination discipline, and fiscal-date normalization.
5. No new reusable post-boundary capability is expected.

## Verification target

If TASK-054 is accepted and implemented, verification should include:

- RED test proving the Treasury module/package builder is absent or incomplete;
- targeted GREEN tests for the bounded Treasury fixture/package;
- cross-source regression covering existing WDI/OECD/Eurostat/BLS/BEA observed packages and contract validation;
- full or proportionate test suite;
- deterministic report JSON restoration if the full suite regenerates known temporary-database reports;
- a short `Implementation Lessons` artifact after implementation.
