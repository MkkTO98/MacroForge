# TASK-062 — Bounded Eurostat Input-Output Matrix Evidence Slice

Status: complete
Started: 2026-07-01

## Objective

Implement a normal Domain Expansion Mode evidence slice that introduces MacroForge's first matrix-shaped economic observation structure without redesigning MacroForge or extracting generic matrix/input-output infrastructure.

## Provider and bounded slice

Provider: Eurostat dissemination API.

Dataset: `naio_10_cp1700` — symmetric input-output table at basic prices, product by product.

Bounded filters:

- `geo`: `DE`, `FR`
- `time`: `2020`
- `unit`: `MIO_EUR`
- `stk_flow`: `DOM`, `IMP`
- `prd_use`: `CPA_A01`, `CPA_C10-12`
- `prd_ava`: `CPA_A01`, `CPA_C10-12`
- `freq`: `A`

Expected observation count: 16 matrix-cell observations.

## Prediction ledger

| Area | Prediction | Confidence | Result |
| --- | --- | ---: | --- |
| ObservedIngestionPackage | Matrix cells can fit existing package by treating provider indicator code as the dataset/flow/product-role combination and preserving matrix roles in attributes/source payload. | 0.85 | Confirmed. |
| Deterministic substrate | Fingerprinting, comparison, replay, and contract validation require no evolution. | 0.90 | Confirmed. |
| Lineage | Existing raw URL/query, raw SHA-256, raw artifact path, and provider metadata are sufficient for lineage. | 0.90 | Confirmed. |
| Replay | Rebuilding the package from the fixture should produce identical observations and fingerprint. | 0.95 | Confirmed. |
| Validation | Existing contract validation should accept matrix-cell observations without new contract fields. | 0.85 | Confirmed. |
| Acquisition | Eurostat JSON-stat API acquisition should be deterministic but filter encoding and sparse/dense value indexing may take modest provider-specific effort. | 0.75 | Confirmed. |
| Provider interpretation | Main effort should be interpreting JSON-stat dimension order/indexing and product-role semantics. | 0.80 | Confirmed. |
| Normalization | Source-specific matrix-cell normalization should be low-medium effort and should not justify a generic matrix abstraction. | 0.85 | Confirmed. |
| Canonical loading | Not in scope; no canonical loader should be added. | 0.99 | Confirmed. |

## Expected new observational structures

- Matrix cell observation.
- Two-sided product classification roles: product available/supplied and product used/consumed.
- Product-by-product many-to-many economic relationship evidence.
- Domestic/imported stock-flow partition.
- Sparse/dense JSON-stat cube decoding for a bounded matrix slice.

## Existing structures reused

- Source-specific acquisition and normalization.
- Deterministic fixture preservation.
- `ObservedIngestionPackage` construction.
- Existing contract validation.
- Deterministic package replay/fingerprinting.
- Existing ProjectForge closeout and evidence artifacts.

## Explicit non-goals

- No full input-output database.
- No broad Eurostat NAIO support.
- No generic matrix framework.
- No generic supply-use/input-output infrastructure.
- No CPA classification framework or hierarchy inference.
- No industry/product canonicalization.
- No derived multipliers or Leontief inverse.
- No supply-chain reasoning.
- No canonical loading.
- No KnowledgeForge semantics.
- No architectural redesign.

## Acceptance criteria

- [x] RED tests are written and observed failing before production code.
- [x] Deterministic fixture is recorded under `data/raw/eurostat_input_output/`.
- [x] Source-specific parser normalizes the bounded 16-cell matrix slice.
- [x] `ObservedIngestionPackage` construction preserves matrix-role metadata and validates through existing contract checks.
- [x] Deterministic replay/fingerprint test passes.
- [x] Anti-framework/non-goal tests pass.
- [x] Implementation lessons are written.
- [x] Industry/input-output coverage assessment is updated.
- [x] Confidence/pain/cost/surprise artifacts are updated.
- [x] State/handoff/summaries are updated.
- [x] Targeted and full verification pass, with known warnings recorded.

## Architectural monitoring

Result: this was normal Domain Expansion. The implementation introduced matrix-shaped source evidence while leaving `ObservedIngestionPackage`, deterministic substrate, lineage, replay, and validation unchanged. No architectural action is recommended.
