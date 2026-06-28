# TASK-051 — Bounded BLS Monthly Evidence Slice

Status: complete
Completed UTC: 2026-06-27T16:03:02Z

## Objective

Implement a deliberately bounded BLS monthly CPI evidence slice as an architectural experiment, not as BLS dataset support.

Optimization question:

> Does this permanently reduce the future engineering, human, or LLM effort required to ingest trustworthy economic datasets?

## Scope kept deliberately small

- One provider: BLS.
- One series: `CUUR0000SA0`.
- One year: 2023.
- One deterministic recorded fixture.
- No generalized framework, plugin system, orchestration, runtime redesign, provider metadata framework, series framework, acquisition framework, model calls, production database writes, or dataset expansion.
- Source-specific implementation remains before `ObservedIngestionPackage`.
- Shared deterministic implementation remains after the observed boundary.

## Implementation summary

Added a source-specific bounded BLS CPI module:

- `src/macroforge/bls_cpi.py`
  - normalizes the recorded BLS raw fixture;
  - constructs an `ObservedIngestionPackage` from source-specific normalized rows;
  - contains no live fetch, SQL, framework, registry, plugin, or generalized acquisition behavior.

Added deterministic fixture evidence:

- `data/raw/bls/bls-cpi-cuur0000sa0-2023-raw.json`
- `data/raw/bls/_SUMMARY.md`

Minimal contract evolution:

- Added optional `ObservedObservation.period_month`.
- Extended contract drift validation from `A`/`Q` to `A`/`Q`/`M`.
- Added monthly invariant: frequency `M` requires `period_month` 1-12 and no `period_quarter`.
- Added annual/quarterly invariant: no `period_month` for `A` or `Q` observations.

No canonical PostgreSQL loader was added. That was intentional. The experiment's architectural question was whether the observed boundary survives monthly series-oriented evidence with minimal contract evolution, not whether BLS can be loaded into canonical facts.

## RED / GREEN evidence

RED command:

```bash
uvx --from pytest --with pyyaml pytest tests/test_bls_cpi.py tests/test_contract_drift.py::test_monthly_observation_contract_requires_month_between_one_and_twelve -q
```

RED result:

```text
ModuleNotFoundError: No module named 'macroforge.bls_cpi'
1 error in 0.10s
```

Targeted GREEN command:

```bash
uvx --from pytest --with pyyaml pytest tests/test_bls_cpi.py tests/test_contract_drift.py -q
```

Targeted GREEN result:

```text
8 passed in 0.04s
```

Cross-source regression command:

```bash
uvx --from pytest --with pyyaml pytest tests/test_bls_cpi.py tests/test_contract_drift.py tests/test_observed_ingestion.py tests/test_wdi_loader.py tests/test_oecd_sdmx_loader.py tests/test_eurostat_namq_loader.py tests/test_deterministic_change_verification.py -q
```

Cross-source regression result:

```text
22 passed in 2.95s
```

Full verification command:

```bash
uvx --from pytest --with pyyaml pytest tests -q
```

Full verification result:

```text
105 passed in 6.69s
```

Generated deterministic report JSON diffs were limited to isolated temporary database names and were restored:

- `artifacts/reports/canonical-gdp-snapshot-20260604.json`
- `artifacts/reports/combined-source-canonical-smoke-20260604.json`

## Engineering effort distribution

Qualitative effort distribution for TASK-051:

| Area | Effort | Evidence |
|---|---:|---|
| Acquisition | Low | One no-key BLS endpoint returned HTTP 200; one recorded raw JSON fixture was enough. |
| Provider interpretation | Medium | Required explicit series label, implicit USA territory, unit label, monthly period semantics, and footnote treatment. |
| Normalization | Medium | Required source-specific sorting from reverse chronological BLS order into stable ascending monthly order, `M01` parsing, value precision, and footnote normalization. |
| `ObservedIngestionPackage` construction | Low | Existing package shape fit with only a source-specific adapter and optional `period_month`. |
| Deterministic substrate | Very low | Existing fingerprinting/comparison/contract validation mechanics were reused. |
| Canonical loading | None | Intentionally not implemented. |
| Deterministic verification | Low | Existing contract validation and cross-source regression tests absorbed the new monthly evidence. |
| Testing | Medium | New tests were needed for BLS normalization/package behavior and monthly drift invariants. |

Comparison with WDI/OECD_NAAG/EUROSTAT_NAMQ_GDP:

- WDI required substantial source-specific normalized support-bundle interpretation but simple annual periods.
- OECD_NAAG required source-specific SDMX/provider-dimension interpretation and attribute/status handling.
- Eurostat required JSON-stat interpretation, quarterly period parsing, and richer provider metadata.
- BLS required monthly period parsing, series identity, implicit territory, and footnotes.
- In all four cases, effort remains concentrated before the observed boundary; effort after `ObservedIngestionPackage` is stable or decreasing.

## Post-implementation review questions

### 1. Which new reusable patterns emerged?

Emerging, not yet extractable:

- Acquisition pattern: no-key HTTP endpoint recorded as a deterministic raw fixture.
- Raw evidence pattern: raw path + checksum + source URL remain sufficient minimal provenance.
- Series identity pattern: a provider series ID can function as `provider_indicator_code` without a generalized series framework.
- Period parsing pattern: provider period tokens require source-specific parsing into structured period components.
- Attribute pattern: provider footnotes/status-like payloads can remain source-specific attributes plus source payload.
- Package construction pattern: once normalized, BLS package construction mostly reused the existing observed package shape.

### 2. Which assumptions of the Deterministic Ingestion Substrate were confirmed?

Confirmed:

- `ObservedIngestionPackage` remains the right boundary for this evidence slice.
- Deterministic package validation, fingerprinting, and regression tests reduce post-boundary reasoning.
- Source-specific normalization remains the right pre-boundary ownership model.
- The substrate did not need source-specific conditionals for BLS.

### 3. Which assumptions were falsified or pressured?

Pressured:

- `A`/`Q` frequency validation was too narrow.
- `period_year`/`period_quarter` was insufficient for a monthly source.
- Series-oriented provider identity is compatible with the observed boundary but needs explicit source-specific interpretation.
- Implicit territory (`USA`) can be handled source-specifically; it does not yet justify contract change.

Falsified:

- The assumption that the current observed observation fields fully covered near-term bounded heterogeneous sources. Minimal `period_month` evolution was required.

### 4. Did implementation reduce future engineering effort?

Yes, narrowly.

Future monthly sources now have:

- a tested optional `period_month` field;
- deterministic monthly contract drift checks;
- a source-specific example showing how series-oriented evidence can enter the observed boundary without framework extraction;
- a regression-protected proof that existing WDI/OECD/Eurostat annual/quarterly behavior survives monthly contract evolution.

### 5. Did implementation reduce future human effort?

Yes, by converting several judgment questions into bounded implementation precedent:

- monthly periods belong in minimal additive contract evolution, not in opaque `source_payload` only;
- implicit provider territory can remain source-specific for now;
- footnotes can remain source-specific attributes until repeated implementations prove stronger convergence;
- BLS-like series identity does not require a provider metadata framework.

### 6. Did implementation reduce future LLM reasoning?

Yes.

A future agent can inspect `tests/test_bls_cpi.py`, `src/macroforge/bls_cpi.py`, and the monthly contract drift tests instead of re-reasoning from scratch about monthly period support, BLS series ordering, footnotes, and whether a framework is required.

### 7. Should any new capability now be specified?

Not yet as a standalone architecture layer.

Evidence supports recording the following capability candidates, but not extracting them:

- Monthly Period Contract Support — implemented as minimal contract evolution, regression protected.
- Series-Oriented Provider Identity — observed as source-specific evidence.
- Provider Footnote/Status Metadata Preservation — observed as source-specific attributes/source payload.
- Source Acquisition Fixture Contract — emerging but not yet converged enough to extract.

### 8. Should any previously proposed capability now be rejected?

No capability is rejected, but priorities sharpen:

- Ingestion Diagnostics and Recovery Evidence remains valuable but should draw from observed/package verification evidence, not become orchestration.
- Shared Post-Boundary Infrastructure Extraction remains deferred beyond already-verified pieces.
- Provider metadata extraction remains premature.
- Generic reconstruction abstraction remains premature.
- Source framework/plugin ideas remain rejected.

### 9. If MacroForge had started today with the current substrate, which portions would no longer need to be written?

Would not need to be written:

- observed package dataclasses;
- deterministic attribute hashing;
- deterministic package fingerprinting;
- deterministic contract validation infrastructure;
- cross-source regression pattern;
- observed-boundary documentation pattern.

Still needed:

- BLS-specific raw fixture acquisition;
- BLS-specific series interpretation;
- BLS-specific period parsing;
- BLS-specific footnote normalization;
- BLS-specific package adapter.

### 10. Which portions remain fundamentally source-specific?

Likely source-specific:

- endpoint choice and bounded query shape;
- BLS `seriesID` meaning;
- CPI unit label (`Index 1982-84=100`);
- implicit USA territory;
- provider period token parsing from `M01`...`M12`;
- footnote filtering and interpretation;
- source label preservation.

### 11. Did implementation reveal evidence that a reusable pre-boundary layer is beginning to emerge?

Yes, but only weakly and not enough to extract.

Evidence is accumulating around:

- recorded raw fixture + checksum + source URL;
- source-specific period parsing into structured fields;
- provider identifier + label preservation;
- source payload retention;
- stable sort ordering before package construction.

The current source-specific ownership model remains correct because contract convergence, algorithm convergence, and implementation convergence are not yet proven before the observed boundary. Four sources are enough to observe pattern pressure; they are not enough to justify a reusable Source Interpretation Layer.

## Future technical-debt record

After approximately six materially different sources have been implemented, require a dedicated implementation review titled:

**Pre-Boundary Pattern Emergence Review**

Question:

> Has implementation evidence now justified extracting a reusable Source Interpretation Layer before the ObservedIngestionPackage boundary?

No extraction should occur unless repeated implementations demonstrate contract convergence, algorithm convergence, implementation convergence, deterministic verification, acceptable coupling, and measurable reduction in future engineering effort.

## Capability maturity outcome

No broad capability maturity advancement was recorded.

Reason:

- TASK-051 verifies minimal monthly contract evolution and adds durable implementation evidence.
- It does not add canonical BLS support.
- It does not make source expansion adopted or stable.
- It does not justify a pre-boundary architectural layer.

`Observed Boundary and Contract Stability` and `Contract Validation and Drift Detection` remain Verified with expanded A/Q/M contract coverage.

## Recommended next implementation task

Recommended TASK-052:

```text
Specify deterministic ingestion diagnostics/recovery evidence from existing observed-package verification outputs, including BLS monthly contract evidence only as a bounded input example if useful.
```

Rationale:

- TASK-051 confirms post-boundary substrate effort is low and stable.
- Pre-boundary patterns are emerging but not extractable.
- The next compounding substrate improvement should improve future failure diagnosis and source-update recovery without creating a pre-boundary framework.
- If another source is chosen instead, it should remain a bounded architectural experiment, not a dataset expansion.
