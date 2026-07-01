# TASK-063 — Bounded IMF BOP Financial-Account Evidence Slice

Status: complete
Started: 2026-07-01

## Recommendation

Implement the smallest useful first international financial-flow observation slice using IMF Balance of Payments (BOP) annual financial-account data.

Selected provider and dataset:

- Provider: International Monetary Fund.
- Dataset/dataflow: `BOP` — Balance of Payments.
- Slice: USA/JPN annual financial-account transaction observations for 2022-2023.

## Why this source

IMF BOP is the cleanest first implementation for international financial-flow observations because it directly exposes Balance of Payments financial-account transaction structures through a public SDMX API. Compared with IIP, it represents flows rather than stock positions. Compared with CPIS/CDIS, it avoids survey-specific holder/issuer relationship complexity for the first slice. Compared with BIS cross-border banking statistics, it better matches the requested Balance of Payments/financial-account structure while remaining compact.

## Bounded slice

Use exactly this bounded key:

```text
BOP/USA+JPN.A_NFA_T+L_NIL_T.D_F+P_F.USD.A?startPeriod=2022&endPeriod=2023
```

Dimensions:

- countries: `USA`, `JPN`;
- accounting entries:
  - `A_NFA_T` — Assets, Net acquisition of financial assets;
  - `L_NIL_T` — Liabilities, Net incurrence of liabilities;
- indicators:
  - `D_F` — Direct investment, Total financial assets/liabilities;
  - `P_F` — Portfolio investment, Total financial assets/liabilities;
- unit: `USD`;
- frequency: annual `A`;
- periods: 2022 and 2023.

Expected observation count:

```text
2 countries × 2 accounting entries × 2 investment categories × 2 years = 16 observations
```

## New observation structures introduced

- International financial-flow observation domain.
- Balance of Payments financial-account transaction semantics.
- Asset/liability accounting-entry distinction.
- Net acquisition of financial assets vs net incurrence of liabilities.
- Investment category distinction: direct investment vs portfolio investment.
- Resident/non-resident framing through Balance of Payments scope, preserved as provider metadata rather than interpreted semantics.
- IMF BOP-specific country/accounting-entry/indicator/unit/frequency dimensional key.

## Existing structures reused

- IMF public SDMX acquisition pattern.
- StructureSpecificData XML parsing.
- Existing `ObservedIngestionPackage` boundary.
- Existing deterministic raw fixture and SHA-256 lineage.
- Existing replay/fingerprint comparison.
- Existing contract validation.
- Existing source-specific-first methodology.

## Explicit non-goals

Do not implement:

- broad IMF BOP support;
- broad IMF API support;
- broad financial-account framework;
- IIP, CPIS, CDIS, or BIS support;
- current-account or capital-account coverage;
- services/trade income detail;
- financial instrument hierarchy;
- partner-country or holder/issuer relationships;
- canonical financial semantics;
- canonical loading;
- KnowledgeForge logic;
- generic SDMX extraction;
- generic Balance of Payments infrastructure.

## Prediction ledger

| Area | Prediction | Confidence | Result |
| --- | --- | --- | --- |
| ObservedIngestionPackage | Existing provider indicator, territory, period, unit, attributes, and source payload fields can preserve BOP financial-account flow observations without contract evolution. | 0.90 | Confirmed. |
| Deterministic substrate | Fingerprinting, comparison, replay, and contract validation require no evolution. | 0.95 | Confirmed. |
| Lineage | Existing raw URL/query, raw SHA-256, metadata URL/SHA, and artifact path evidence are sufficient. | 0.90 | Confirmed. |
| Replay | Rebuilding the package from the fixture should produce identical observations and fingerprint. | 0.95 | Confirmed. |
| Validation | Existing contract validation should accept BOP financial-flow observations without new contract fields. | 0.90 | Confirmed. |
| Acquisition | IMF BOP StructureSpecificData query should be deterministic and compact for the selected 16-observation slice. | 0.85 | Confirmed. |
| Provider interpretation | Main effort should be preserving IMF BOP accounting-entry, investment-category, unit, scale, methodology, and observation attributes source-specifically. | 0.85 | Confirmed. |
| Normalization | Source-specific IMF BOP normalization should be low-medium effort and should not justify generic BOP/financial-flow infrastructure. | 0.90 | Confirmed. |
| Canonical loading | Not in scope; no canonical loader should be added. | 0.99 | Confirmed. |

## Acceptance checklist

- [x] RED tests are written and observed failing before production code.
- [x] Deterministic fixture is recorded under `data/raw/imf_bop_financial_account/`.
- [x] Source-specific parser normalizes the bounded 16-observation financial-account slice.
- [x] `ObservedIngestionPackage` construction preserves BOP accounting-entry and investment-category metadata and validates through existing contract checks.
- [x] Deterministic replay/fingerprint test passes.
- [x] Anti-framework/non-goal tests pass.
- [x] Implementation lessons are written.
- [x] Financial-flow coverage assessment is updated.
- [x] Confidence/pain/cost/surprise artifacts are updated.
- [x] State/handoff/summaries are updated.
- [x] Targeted and full verification pass, with known warnings recorded.

## Architectural monitoring expectation

Result: this was normal Domain Expansion. The implementation introduced international financial-account flow evidence while leaving `ObservedIngestionPackage`, deterministic substrate, lineage, replay, and validation unchanged. No architectural action is recommended.
