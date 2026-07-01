# TASK-065 — Bounded FRED U.S. Treasury Yield Curve Evidence Slice

Status: complete
Started: 2026-07-01

## Observation-family evaluation

The question is not which economic domain is least covered, but which remaining observation family most increases MacroForge's representational coverage after TASK-056 through TASK-064.

Candidate observation families considered:

| Observation family | Coverage gain | Bounded implementation path | Reason |
| --- | --- | --- | --- |
| Financial market curve/surface observations | Very high | FRED monthly U.S. Treasury constant-maturity yield curve, two periods, four tenors | Selected. Introduces same-period term-structure/cross-sectional market pricing shape rather than another scalar time series. |
| Official event observations | High | Policy meetings, releases, legislation, shocks | Valuable but official bounded event APIs are less clean and would likely require document/event semantics earlier than needed. |
| Geospatial/subnational observations | High | Regional indicators or boundaries | Valuable, but likely more spatial/canonical-entity pressure than needed for the next source slice. |
| Product-level classification observations | Medium-high | UN Comtrade HS detail | Expands trade coverage but not as fundamentally new as curve/surface shape. |
| Holder/issuer stock positions | Medium-high | CPIS/IIP | Important, but adjacent to TASK-063 financial-flow work and less broadening than market term-structure shape. |
| Projection/scenario observations | Medium-high | Population or macro forecasts | Adds forecast semantics but risks mixing observed reality with projections before more market/state observation shapes exist. |

## Recommendation

Implement the smallest useful first financial-market curve observation slice using FRED's public no-key CSV graph endpoint for monthly U.S. Treasury constant-maturity yield series.

Selected slice:

- Provider: Federal Reserve Bank of St. Louis FRED.
- Dataset/feed: FRED CSV graph export for `GS1M`, `GS1`, `GS10`, `GS30`.
- Territory: United States (`USA`).
- Periods: `2024-01`, `2024-02`.
- Tenors: `GS1M`, `GS1`, `GS10`, `GS30`.
- Unit: percent.
- Expected observations: 8 = 2 periods × 4 tenors.

## Selection note

The initially attractive official Treasury daily yield-curve XML feed exposed a cleaner Treasury-native daily curve, but daily frequency is outside the current `ObservedIngestionPackage` contract validation envelope (`A`, `Q`, `M`). Preserving the validated architecture is more important than adding a daily-frequency exception. The selected FRED monthly Treasury yield-curve slice preserves the same observation family while staying inside the current validated contract.

## Why this is the clear winner

MacroForge already represents scalar time series, revision vintages, bilateral flows, matrix cells, financial-account flows, and energy-balance cells. It still lacks an observation family where one period contains a cross-sectional financial-market curve: the same observed period across multiple maturities/tenors.

Yield curve observations add a fundamentally new shape:

```text
market period × tenor/maturity → yield value
```

This shape is central to macro/investment understanding because it preserves term-structure evidence needed for later reasoning about monetary expectations, risk-free discount rates, recession signals, financing conditions, and asset valuation. Those future concepts belong to KnowledgeForge; TASK-065 only preserves source-backed observations.

## Metadata to preserve

- Source URL and raw fixture path/SHA-256.
- Series IDs and CSV columns.
- Full CSV row count.
- Selected periods and selected tenor fields.
- Tenor code, tenor label, tenor months, and tenor years.
- Raw observation date.
- Raw source payload for selected observations.

## Explicit non-goals

- No broad FRED support.
- No generic market-data infrastructure.
- No generic yield-curve framework.
- No curve interpolation, slope/spread derivation, duration math, or yield-curve analytics.
- No canonical loader.
- No canonical instrument/tenor semantics.
- No KnowledgeForge reasoning.
- No architecture redesign or infrastructure extraction.

## Prediction ledger

| Area | Prediction |
| --- | --- |
| ObservedIngestionPackage | Should fit without contract changes: provider indicator can represent tenor; monthly period stays inside the current contract; attributes/source payload can preserve curve metadata. |
| Deterministic substrate | Should require no changes; replay and fingerprinting are ordinary package mechanics. |
| Lineage | Should be straightforward: URL, raw fixture path, SHA-256, CSV metadata, selected periods/tenors. |
| Replay | Should be deterministic after sorting by period then tenor. |
| Validation | Existing contract validation should be enough; no yield-curve semantic validation should be added. |
| Main implementation effort | Source-specific CSV parsing and tenor field selection. |
| Main risk | Avoid broad FRED support and avoid derived curve analytics. |
| Architectural pressure | Expected none; classify as Normal Domain Expansion if confirmed. |

## Acceptance checklist

- [x] RED tests written and observed failing.
- [x] Deterministic fixture recorded.
- [x] Source-specific parser/package builder implemented.
- [x] Targeted tests pass.
- [x] Implementation lessons written.
- [x] Domain coverage updated.
- [x] Architecture monitoring ledgers updated.
- [x] State/handoff/summaries updated.
- [x] Final verification complete.

## Result

Implemented bounded FRED monthly U.S. Treasury yield curve evidence slice. Raw fixture SHA-256: `0870977a6dc92d4eb841235ed1335c32ad88914387fe7588ffeeb851e3411a2f`. Package fingerprint: `d7646c4ce18dfacf430fe66cfe170694d18a9aa2af97fcd13251e47276778633`.
