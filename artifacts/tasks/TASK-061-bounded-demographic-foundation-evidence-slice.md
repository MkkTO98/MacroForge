# TASK-061 — Bounded Demographic Foundation Evidence Slice

Status: complete
Started: 2026-06-30

## Objective

Implement a normal bounded Domain Expansion Mode demographic foundation evidence slice.

The task introduces the first reusable demographic foundation for MacroForge while preserving the validated source-specific -> `ObservedIngestionPackage` -> deterministic substrate architecture.

This is not an architectural experiment. Architecture should evolve only if implementation evidence directly contradicts current assumptions.

## Provider selection

Selected provider: World Bank World Development Indicators API.

Rationale:

- official public source with stable public API access;
- broad international country coverage;
- deterministic bounded JSON acquisition;
- well-defined indicator metadata;
- long-term continuity;
- directly covers the requested demographic foundation indicators in one provider family.

UN Population Division remains a high-quality future demographic source, but World Bank WDI is better for this first bounded implementation because it exposes the required foundation indicators through compact no-key API calls and matches existing MacroForge source-evidence patterns.

## Scope

Provider: World Bank WDI API.

Countries:

- USA
- Japan

Periods:

- 2022
- 2023

Indicators:

- `SP.POP.TOTL` — total population
- `SP.POP.GROW` — annual population growth
- `SP.POP.0014.TO.ZS` — population ages 0-14 (% of total population)
- `SP.POP.1564.TO.ZS` — population ages 15-64 (% of total population)
- `SP.POP.65UP.TO.ZS` — population ages 65 and above (% of total population)
- `SP.DYN.TFRT.IN` — fertility rate, total (births per woman)
- `SP.DYN.LE00.IN` — life expectancy at birth, total (years)
- `SP.URB.TOTL.IN.ZS` — urban population (% of total population)

Expected observations:

```text
8 indicators x 2 countries x 2 years = 32 observations
```

Expected observed grain:

```text
provider dataset x indicator x country x annual period
```

## Explicit non-goals

- No complete demographic database.
- No migration system.
- No household projections.
- No detailed age pyramid.
- No regional/subnational demographics.
- No household composition.
- No educational attainment.
- No ethnicity or religion.
- No projection scenarios.
- No population forecasting.
- No generic demographic framework.
- No broad WDI demographic infrastructure.
- No canonical loading.
- No KnowledgeForge semantics.
- No architectural redesign.

## Prediction ledger

### Boundary and substrate predictions

| Area | Prediction | Confidence | Result |
| --- | --- | ---: | --- |
| ObservedIngestionPackage | Existing contract represents demographic annual indicator observations without evolution by preserving WDI indicator/country/period/unit metadata as provider fields, attributes, raw evidence, and source payload. | 95% | Confirmed. WDI demographic indicator/country/period/unit evidence fit through existing fields. |
| Deterministic substrate | Fingerprinting, comparison, contract validation, replay, and feedback require no changes. | 95% | Confirmed. No substrate code changed. |
| Lineage | Per-indicator source URLs, query filters, raw artifact path, SHA-256, content type, and WDI row payloads are sufficient. | 95% | Confirmed. |
| Replay | Deterministic fixture normalization should replay byte-for-byte package fingerprints. | 95% | Confirmed. |
| Validation | Existing contract validation should pass for 32 observed annual demographic observations. | 95% | Confirmed. |

### Effort predictions

| Area | Expected effort | Prediction | Result |
| --- | --- | --- | --- |
| Acquisition | Low-Medium | Eight compact WDI no-key JSON calls must be captured into one deterministic fixture. | Confirmed; transient API timeouts were handled by retry. |
| Provider interpretation | Low-Medium | WDI indicator metadata, unit semantics, and category labels require source-specific preservation, but no demographic framework. | Confirmed. |
| Normalization | Medium | Multiple indicators and unit types require careful indicator-specific unit/category metadata while remaining source-specific. | Confirmed. |
| Package construction | Low | Existing observed package pattern should be sufficient. | Confirmed. |
| Substrate | Low | No shared substrate code expected. | Confirmed. |
| Canonical loading | None | Out of scope. | Confirmed. |
| Verification | Low | Targeted tests plus full regression/coherence checks. | Confirmed. |
| Documentation/closeout | Medium | Demographics domain coverage must be added/updated only for demographics. | Confirmed. |

### Expected reusable implementation knowledge

- WDI demographic foundation indicator set for population/growth/age structure/fertility/life expectancy/urbanization.
- Source-specific preservation of WDI indicator metadata and demographic concept categories.
- First demographic observed package pattern without demographic infrastructure.

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
- [x] Demographics-domain coverage assessment updated.
- [x] Confidence/pain/cost/surprise artifacts updated.
- [x] State/handoff/summaries updated.
- [x] Targeted tests pass.
- [x] Full regression tests pass.
- [x] Coherence/context/architecture checks pass or known warnings recorded.
