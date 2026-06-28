# TASK-052 — Deterministic Ingestion Feedback

Status: complete
Completed UTC: 2026-06-27T16:20:56Z

## Objective

Build Deterministic Ingestion Feedback from existing deterministic verification evidence.

The objective was not to create a diagnostics subsystem. The objective was to make existing deterministic verification easier for future developers, future Hermes sessions, and future local LLMs to understand.

## Scope

Used only existing deterministic evidence:

- `ContractDriftReport` from contract validation.
- `ObservedPackageComparison` from package fingerprint/equivalence comparison.
- `CanonicalLineageEvent` tuples from existing lineage generation.
- implementation evidence from WDI, OECD_NAAG, EUROSTAT_NAMQ_GDP, and bounded BLS_CPI tasks.

Explicitly not introduced:

- orchestration;
- recovery automation;
- source frameworks;
- generalized diagnostics platform;
- graph system;
- runtime monitoring;
- source onboarding;
- live fetch;
- PostgreSQL migration;
- canonical loader changes.

## Implementation summary

Added:

- `src/macroforge/ingestion_feedback.py`
- `tests/test_ingestion_feedback.py`

The module introduces deterministic, storage-independent feedback dataclasses and builders:

- `DeterministicIngestionFeedback`
- `SourceEngineeringEffortProfile`
- `deterministic_feedback_from_contract_report(...)`
- `deterministic_feedback_from_package_comparison(...)`
- `deterministic_feedback_from_lineage_events(...)`
- `source_engineering_effort_profiles()`

These functions convert existing verification artifacts into deterministic explanations. They do not execute verification, repair failures, load sources, or own source-specific semantics.

## Deterministic feedback outputs introduced

### Contract feedback

Input: `ContractDriftReport`.

Answers:

- Which contract failed?
- Where did it fail?
- Which deterministic guarantee was violated?
- What is the most likely inspection location?

Example tested failure:

```text
BLS_CPI observed package violates 1 deterministic contract invariant.
invalid_month at package.observations[0].period_month
Inspection hint: Inspect package.observations[0].period_month.
```

### Package comparison feedback

Input: `ObservedPackageComparison`.

Answers:

- What changed?
- Which observation differs?
- Which fields changed?
- Which fingerprint/equivalence guarantee was violated?
- What is the most likely observation identity requiring inspection?

Example tested failure:

```text
EUROSTAT_NAMQ_GDP observed package comparison found non-equivalent fingerprints.
Observation index 1, identity B1GQ/DE/2023-Q2, changed field: value.
```

### Lineage feedback

Input: existing `CanonicalLineageEvent` tuple.

Answers:

- Where did the deterministic lineage transition occur?
- Does the existing two-step event order remain visible?
- Which lineage event should be inspected?

Example tested success:

```text
BLS_CPI lineage evidence has deterministic raw_to_staging -> staging_to_curated event order.
```

### Engineering-effort metric

Introduced a lightweight qualitative source effort profile for each implemented source:

- acquisition;
- provider interpretation;
- normalization;
- observed package construction;
- deterministic substrate;
- canonical loading;
- deterministic verification;
- testing;
- Substrate Effort Ratio.

This is intentionally not numerical measurement and not a governance subsystem.

## Qualitative engineering-effort distribution

| Source | Acquisition | Provider interpretation | Normalization | Observed package construction | Deterministic substrate | Canonical loading | Deterministic verification | Testing | Substrate Effort Ratio |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| WDI | Medium | Medium | Medium | Low | Low | Medium | Medium | Medium | Low |
| OECD_NAAG | Medium | High | High | Low | Low | High | Medium | High | Low |
| EUROSTAT_NAMQ_GDP | Medium | High | High | Low | Low | High | Medium | High | Low |
| BLS_CPI | Low | Medium | Medium | Low | Very Low | None | Low | Medium | Very Low |

## Updated Substrate Effort Ratio assessment

TASK-052 preserves the TASK-051 conclusion:

```text
Post-boundary engineering effort is Low to Very Low.
```

The strongest evidence is still BLS_CPI: a fourth heterogeneous, monthly, series-oriented source required only minimal additive evolution after the `ObservedIngestionPackage` boundary. TASK-052 then converted that deterministic evidence into reusable feedback outputs instead of adding new architecture.

## Capability maturity assessment

The refined capability is:

```text
Deterministic Ingestion Feedback
```

Maturity after TASK-052:

```text
Verified for current v1.1 scope
```

Why Verified is justified:

- deterministic tests prove contract feedback from existing contract reports;
- deterministic tests prove package-comparison feedback from existing package comparison evidence;
- deterministic tests prove lineage feedback from existing lineage event evidence;
- deterministic tests prove effort-profile coverage across WDI, OECD_NAAG, EUROSTAT_NAMQ_GDP, and BLS_CPI;
- no new source framework, orchestration, runtime monitor, recovery automation, or graph system was introduced.

Do not advance this capability to Adopted/Shared/Stable until a future task makes deterministic feedback a required path for relevant verification/reporting commands.

## RED / GREEN / verification evidence

RED command:

```bash
uvx --from pytest --with pyyaml pytest tests/test_ingestion_feedback.py -q
```

RED result:

```text
ModuleNotFoundError: No module named 'macroforge.ingestion_feedback'
1 error in 0.09s
```

Second RED for lineage feedback:

```bash
uvx --from pytest --with pyyaml pytest tests/test_ingestion_feedback.py::test_lineage_feedback_explains_existing_two_step_lineage_guarantee -q
```

RED result:

```text
ImportError: cannot import name 'deterministic_feedback_from_lineage_events' from 'macroforge.ingestion_feedback'
1 error in 0.04s
```

Targeted GREEN command:

```bash
uvx --from pytest --with pyyaml pytest tests/test_ingestion_feedback.py -q
```

Targeted GREEN result:

```text
5 passed in 0.03s
```

Targeted substrate regression command:

```bash
uvx --from pytest --with pyyaml pytest tests/test_ingestion_feedback.py tests/test_contract_drift.py tests/test_observed_ingestion.py tests/test_lineage_generation.py -q
```

Result:

```text
20 passed in 0.06s
```

Cross-source regression command:

```bash
uvx --from pytest --with pyyaml pytest tests/test_ingestion_feedback.py tests/test_bls_cpi.py tests/test_contract_drift.py tests/test_observed_ingestion.py tests/test_wdi_loader.py tests/test_oecd_sdmx_loader.py tests/test_eurostat_namq_loader.py tests/test_deterministic_change_verification.py tests/test_lineage_generation.py -q
```

Result:

```text
30 passed in 2.90s
```

Full verification command:

```bash
uvx --from pytest --with pyyaml pytest tests -q
```

Result:

```text
110 passed in 5.93s
```

Known regenerated deterministic report JSON diffs were restored after the full suite:

- `artifacts/reports/canonical-gdp-snapshot-20260604.json`
- `artifacts/reports/combined-source-canonical-smoke-20260604.json`

## Recommendation for next implementation capability

Next recommended implementation capability:

```text
Adopt deterministic feedback as an optional report surface for the accepted deterministic verification path.
```

Recommended next task shape:

```text
TASK-053 — Attach Deterministic Ingestion Feedback to deterministic verification reports without changing source loading behavior.
```

Scope should remain narrow:

- consume existing `verify_loaded_observed_package_contracts(...)` evidence;
- produce a compact deterministic feedback summary for WDI/OECD/Eurostat verification;
- do not make feedback required yet unless tests prove the integration seam is stable;
- do not add orchestration, recovery automation, source frameworks, runtime monitoring, graph systems, or new sources.
