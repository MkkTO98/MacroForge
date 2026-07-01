# TASK-060 — Bounded UN Comtrade Bilateral Total Goods Trade Evidence Slice

Status: complete
Started: 2026-06-30

## Objective

Implement a normal bounded heterogeneous source slice for UN Comtrade annual bilateral total-goods trade evidence.

This task expands MacroForge's international-trade observation coverage while preserving the current architecture.

This is not an architectural experiment. Architecture should evolve only if implementation evidence directly contradicts current assumptions.

## Scope

Provider: UN Comtrade public preview API.

Endpoint/filter shape:

- `typeCode=C`
- `freqCode=A`
- `classification=HS`
- `reporterCode=842` / USA
- `partnerCode=392` / Japan
- `flowCode=M,X`
- `cmdCode=TOTAL`
- `period=2023`
- `includeDesc=true`

Expected observations: exactly two annual bilateral total-goods trade observations.

Expected observed grain:

```text
provider dataset x reporter x partner x trade direction x product code x annual period
```

## Explicit non-goals

- No broad UN Comtrade support.
- No Comtrade API client framework.
- No generic trade infrastructure.
- No product classification framework.
- No HS hierarchy expansion.
- No quantity/volume interpretation.
- No mirror trade reconciliation.
- No services trade.
- No multi-year trade time series.
- No multiple reporters/partners.
- No canonical product/country/trade-direction mapping.
- No canonical loading.
- No KnowledgeForge semantics.
- No trade balance calculation.
- No architectural redesign.

## Prediction ledger

### Boundary and substrate predictions

| Area | Prediction | Confidence | Result |
| --- | --- | ---: | --- |
| ObservedIngestionPackage | Existing contract represents bilateral trade-value observations without evolution by using reporter as provider territory and preserving partner/direction/product fields as source-backed attributes/payload. | 90% | Confirmed. Reporter/partner/flow/product/value-basis metadata fit through existing attributes and source payload. |
| Deterministic substrate | Fingerprinting, comparison, contract validation, replay, and feedback require no changes. | 95% | Confirmed. No substrate code changed. |
| Lineage | Source URL, query filters, raw artifact path, SHA-256, content type, and provider row payloads are sufficient. | 95% | Confirmed. |
| Replay | Deterministic fixture normalization should replay byte-for-byte package fingerprints. | 95% | Confirmed. |
| Validation | Existing contract validation should pass for two observed annual nominal trade-value observations. | 90% | Confirmed. |

### Effort predictions

| Area | Expected effort | Prediction | Result |
| --- | --- | --- | --- |
| Acquisition | Low | Public preview JSON endpoint returns compact two-row payload. | Confirmed. |
| Provider interpretation | Medium | Reporter/partner/direction/product/value-basis metadata need careful preservation, but no semantic framework. | Confirmed. |
| Normalization | Low-Medium | Annual period, trade direction, total commodity, and nominal value should map source-specifically. | Confirmed. |
| Package construction | Low | Existing observed package pattern should be sufficient. | Confirmed. |
| Substrate | Low | No shared substrate code expected. | Confirmed. |
| Canonical loading | None | Out of scope. | Confirmed. |
| Verification | Low | Targeted tests plus full regression/coherence checks. | Confirmed. |
| Documentation/closeout | Medium | Trade-domain coverage assessment must be added/updated only for trade. | Confirmed. |

### Expected reusable implementation knowledge

- UN Comtrade public preview payload shape for bounded queries.
- Source-specific preservation of reporter, partner, flow, commodity/classification, value, and quantity/weight metadata.
- First trade-domain observed package pattern without trade infrastructure.

### Architectural monitoring expectation

This is expected to behave as normal Domain Expansion Mode. No architectural action should be recommended if the predictions hold.

## Acceptance checklist

- [x] Prediction ledger recorded before production code.
- [x] RED test observed.
- [x] Deterministic fixture preserved.
- [x] Source-specific parser implemented.
- [x] ObservedIngestionPackage construction verified.
- [x] Deterministic replay/fingerprint verified.
- [x] Implementation lessons written.
- [x] Trade-domain coverage assessment updated.
- [x] Confidence/pain/cost/surprise artifacts updated.
- [x] State/handoff/summaries updated.
- [x] Targeted tests pass.
- [x] Full regression tests pass.
- [x] Coherence/context/architecture checks pass or known warnings recorded.
