# TASK-062 Implementation Lessons — Bounded Eurostat Input-Output Matrix Evidence Slice

Status: complete
Date: 2026-07-01

## Scope implemented

TASK-062 implemented a normal Domain Expansion Mode evidence slice for Eurostat `naio_10_cp1700`, a symmetric input-output table at basic prices, product by product.

The bounded slice covers:

- geographies: Germany `DE` and France `FR`;
- period: `2020`;
- unit: `MIO_EUR`;
- stock/use flows: `IMP` imports and `DOM` domestic uses;
- product-used dimension: `CPA_A01` and `CPA_C10-12`;
- product-available dimension: `CPA_A01` and `CPA_C10-12`.

It produced 16 source-backed matrix-cell observations.

## New observational structure

This slice introduced MacroForge's first matrix-shaped economic evidence:

```text
country × year × stock-flow × product-used × product-available -> value
```

The key novelty is not a new indicator count. It is the preservation of two product roles in one observation:

- `prd_ava`: product available/supplied;
- `prd_use`: product used/consumed.

This records source-backed product-to-product relationship evidence without adding KnowledgeForge semantics.

## Prediction review

| Area | Result |
| --- | --- |
| ObservedIngestionPackage | Confirmed. Existing fields handled matrix cells by encoding the dataset/flow/product-role tuple in provider indicator code and preserving matrix roles in attributes/source payload. |
| Deterministic substrate | Confirmed. Fingerprinting, comparison, replay, and contract validation required no evolution. |
| Lineage | Confirmed. Raw URL/query, raw SHA-256, raw artifact path, and provider metadata were sufficient. |
| Replay | Confirmed. Rebuilding from the fixture produced deterministic package equivalence. |
| Validation | Confirmed. Existing contract validation accepted the package. |
| Acquisition | Confirmed. Eurostat repeated query parameters produced a compact deterministic JSON-stat fixture. |
| Provider interpretation | Confirmed. Most effort was JSON-stat dimension order/indexing and product-role semantics. |
| Normalization | Confirmed. Source-specific normalization was enough; no matrix abstraction is justified. |
| Canonical loading | Confirmed. No canonical loader was added. |

## Architectural monitoring

No unexpected pressure appeared on:

- `ObservedIngestionPackage`;
- deterministic substrate;
- lineage;
- replay;
- validation.

TASK-062 is normal Domain Expansion. No architectural action is recommended.

## Boundaries preserved

The implementation did not add:

- broad Eurostat NAIO support;
- generic matrix infrastructure;
- generic supply-use/input-output infrastructure;
- CPA classification framework;
- product hierarchy inference;
- derived multipliers;
- supply-chain reasoning;
- canonical loading;
- KnowledgeForge semantics.

## Implementation notes

Eurostat's JSON-stat response stores values by flat numeric index. The parser therefore records both:

- source dimension order; and
- JSON-stat flat index per observation.

This is useful evidence for future cube/matrix datasets, but one implementation is not enough to justify shared JSON-stat cube infrastructure. Keep Eurostat input-output behavior source-specific until repeated implementations demonstrate convergence and measurable effort reduction.

## Verification evidence

Targeted GREEN during implementation:

```text
uvx pytest tests/test_eurostat_input_output.py -q
5 passed in 0.04s
```

Fixture evidence:

```text
fixture_sha256 861277f7d0b7e38606754d35bfef224a398252416acb6454b7f56418e1939812
row_count 16
package_fingerprint ef3d91bd387c2d1a6733e107a4eca291638f70f80a038708d6de0e323445527d
```
