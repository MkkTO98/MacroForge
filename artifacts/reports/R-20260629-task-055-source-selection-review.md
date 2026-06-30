# Report — TASK-055 Source Selection Review

Date: 2026-06-29
Status: recommendation only; implementation not approved or started
Related accepted task: `artifacts/tasks/TASK-054-bounded-us-treasury-fiscal-data-evidence-slice.md`
Related lessons: `artifacts/reports/L-20260628-task-054-implementation-lessons.md`
Related decision: `artifacts/decisions/DEC-022-next-ten-source-expansion-optimization.md`

## Purpose

TASK-054 is accepted. Do not begin TASK-055 immediately.

This review selects the bounded source implementation expected to produce the greatest architectural knowledge per unit of engineering effort.

Primary criterion:

```text
Which source is most likely to falsify or significantly stress the current MacroForge architecture while remaining realistically implementable as a bounded evidence slice?
```

The objective is implementation knowledge, not implementation count.

## Current evidence baseline

Current source evidence includes WDI, OECD_NAAG, EUROSTAT_NAMQ_GDP, bounded BLS_CPI, bounded BEA_NIPA, and bounded TREASURY_FISCAL_DATA.

The current default architecture is:

```text
source-specific acquisition and normalization
-> ObservedIngestionPackage
-> deterministic post-boundary substrate
```

TASK-053 and TASK-054 both confirmed that materially different source shapes can fit the existing observed boundary without post-boundary redesign:

- BEA_NIPA stressed table/line-code evidence, interactive-table metadata, release descriptions, and quarterly national-accounts periods.
- TREASURY_FISCAL_DATA stressed row-oriented government JSON, deterministic query provenance, endpoint metadata, pagination metadata, monthly fiscal record dates, and categorical row identity.

Both concentrated effort before the boundary. Neither required `ObservedIngestionPackage` evolution or Deterministic Ingestion Substrate evolution.

Therefore the next source should not be the easiest implementation. It should be the bounded implementation most likely to test the architecture's weakest current assumptions.

## Live accessibility probes

Bounded probes were run on 2026-06-29 to check realistic implementability:

- FRED series observations without key: HTTP 400.
- ALFRED/FRED vintage dates without key: HTTP 400.
- BEA NIPA SAMPLEUSER `GetData`: HTTP 200 JSON.
- ECB SDW dataflow endpoint: HTTP 200 SDMX structure XML.
- ECB SDW sample EXR data endpoint: HTTP 200 SDMX generic data XML.
- IMF new SDMX dataflow endpoint: HTTP 200 SDMX structure XML.
- IMF legacy dataservices host: DNS failure in current environment.
- Treasury `debt_to_penny`: HTTP 200 JSON.
- Treasury `avg_interest_rates`: HTTP 200 JSON.

Accessibility is not the primary ranking criterion, but it constrains whether a candidate is realistically implementable as a bounded evidence slice.

## Candidate comparison

Scale:

- Effort: Very Low, Low, Medium, High, Very High.
- Probabilities are implementation-planning estimates, not facts.

| Candidate | Expected implementation effort | Pre-boundary effort | Post-boundary effort | Contract evolution probability | Substrate evolution probability | Architectural learning value | Realistic boundedness |
|---|---:|---:|---:|---:|---:|---|---|
| ALFRED/FRED vintage-aware bounded slice | Medium-High | High | Medium | 45% | 25% | Very High | Medium, access/key risk |
| ECB SDW bounded slice | Medium | Medium-High | Low | 15% | 10% | High | High |
| IMF SDMX bounded slice | High | High | Low-Medium | 20% | 15% | High, but noisy | Medium |
| Additional Treasury endpoint | Low-Medium | Medium | Very Low | 5% | 5% | Medium | High |
| Additional BEA NIPA slice | Low-Medium | Medium | Very Low | 5% | 5% | Low-Medium | High |

## Candidate details

### 1. ALFRED/FRED vintage-aware bounded slice

Possible bounded target:

- one economic time series with two or more vintage/realtime dates;
- fixture-only or no-key-accessible evidence if available;
- no broad FRED/ALFRED support;
- no canonical loading;
- no live production fetch.

Architectural assumption tested:

```text
Observation period identity and source release identity can remain separate enough inside existing `release_key`, `attributes`, `input_filters`, `raw_evidence`, and `source_payload` without adding explicit revision/vintage fields to `ObservedObservation` or `ObservedIngestionPackage`.
```

Expected implementation effort: Medium-High.

Expected pre-boundary effort: High.

- Acquisition/access may require API key or fixture capture.
- Provider interpretation is meaningfully new: realtime start/end, vintage dates, revision calendars, observation period versus availability period.
- Normalization must avoid confusing economic observation date with vintage/revision date.
- Source identity must include enough vintage evidence for deterministic replay and comparison.

Expected post-boundary effort: Medium.

- Existing deterministic fingerprinting/comparison can likely compare package outputs.
- Contract validation may pass if vintage semantics are encoded in release metadata and attributes.
- The main risk is semantic insufficiency rather than mechanical inability.

Probability `ObservedIngestionPackage` contract requires evolution: 45%.

- If a bounded slice only preserves one vintage per package, existing fields may suffice.
- If the slice must represent multiple vintages for the same provider indicator/territory/period in one package, the current observation identity may be ambiguous because there is no explicit realtime/vintage dimension.

Probability Deterministic Ingestion Substrate requires evolution: 25%.

- Existing deterministic comparison can operate mechanically.
- Substrate evolution may be needed if equivalence/comparison must distinguish value revisions from ordinary source changes with first-class semantics.

Expected reusable implementation knowledge:

- distinction between observation period and data availability/revision period;
- vintage-aware release-key construction;
- deterministic fixture design for revisions;
- revision provenance preservation;
- when revision semantics belong in attributes versus the observed contract;
- whether current fingerprint/comparison explanations are sufficient for revised observations.

Expected reduction in future engineering, human, and LLM effort: High.

- Revision/vintage semantics are a recurring macroeconomic data problem.
- Learning how to encode or not encode them will reduce future ambiguity for FRED, ALFRED, OECD revisions, national account revisions, and release-calendar-sensitive analysis.

Falsification/stress value: Highest.

Main risk:

- Access friction may consume effort without producing architectural evidence. A fixture-based bounded slice can mitigate this, but the source must still preserve genuine vintage semantics rather than a synthetic duplicate.

### 2. ECB SDW bounded slice

Possible bounded target:

- one ECB Data Portal / SDW series or compact dataflow slice, likely exchange rates or a small monetary/financial series;
- SDMX XML fixture;
- no broad ECB support;
- no canonical loading.

Architectural assumption tested:

```text
A second independent SDMX-family provider can remain source-specific before the boundary, and SDMX commonality with OECD should not yet force shared SDMX infrastructure or provider metadata abstractions.
```

Expected implementation effort: Medium.

Expected pre-boundary effort: Medium-High.

- Acquisition is reachable via public SDMX endpoints.
- Provider interpretation requires SDMX key dimensions, codelists, attributes, units, frequency, and potentially ECB-specific dataflow/version semantics.
- Normalization tests whether OECD SDMX experience transfers without premature shared abstraction.

Expected post-boundary effort: Low.

- Annual/quarterly/monthly periods likely fit current fields if target is bounded appropriately.
- Provider dimensions and attributes likely fit existing provider/attribute payload fields.

Probability `ObservedIngestionPackage` contract requires evolution: 15%.

- Most likely no evolution for ordinary time-series observations.
- Risk increases if the selected ECB slice uses daily frequency, complex multi-currency pair identity, or dimensions not cleanly expressible as provider indicator/territory.

Probability Deterministic Ingestion Substrate requires evolution: 10%.

- Existing fingerprinting, validation, and feedback should work.
- Substrate pressure is more likely around explanation quality for dense SDMX dimension identities, not core mechanics.

Expected reusable implementation knowledge:

- second-provider SDMX comparison against OECD;
- evidence on whether SDMX parsing mechanics are converging;
- SDMX codelist and attribute mapping discipline;
- when SDMX helper extraction is justified or still premature;
- dimensional-key identity construction for financial/monetary series.

Expected reduction in future engineering, human, and LLM effort: High.

- If ECB resembles OECD enough, it provides the second independent evidence point for future SDMX extraction decisions.
- If it differs materially, it prevents premature overfitting to OECD's SDMX shape.

Falsification/stress value: High.

Main risk:

- It may mostly confirm the existing architecture rather than stress it. Its value is strongest as an extraction-gate test for future SDMX common mechanics.

### 3. IMF SDMX bounded slice

Possible bounded target:

- one IMF SDMX dataflow with a very small filtered series fixture;
- no broad IMF support;
- no canonical loading;
- avoid legacy dataservices host if unreachable; prefer current IMF SDMX endpoint if used.

Architectural assumption tested:

```text
The observed boundary can absorb a large institutional SDMX provider with deeper dataflow/dimension complexity without requiring source-framework, metadata-framework, or substrate evolution.
```

Expected implementation effort: High.

Expected pre-boundary effort: High.

- Acquisition is reachable through the newer IMF SDMX dataflow endpoint, but identifying a small stable data slice may require more source discovery than ECB.
- Provider interpretation likely involves larger dataflow catalog complexity, many dimensions, units, frequencies, possibly compact/generic SDMX variants, and provider-specific quirks.
- Normalization may require more human judgment to avoid overbuilding an IMF framework.

Expected post-boundary effort: Low-Medium.

- A carefully bounded time series should fit the current observed contract.
- Multi-dimensional IMF identities may stress provider_indicator_code construction and source-specific attributes.

Probability `ObservedIngestionPackage` contract requires evolution: 20%.

- Most likely avoidable with a narrow slice.
- Risk comes from dimensional identity that does not map naturally to indicator/territory/frequency/unit without lossy source-specific decisions.

Probability Deterministic Ingestion Substrate requires evolution: 15%.

- Core deterministic mechanics should likely survive.
- Feedback/reporting may need clearer explanations for high-dimensional provider identities, but that is not necessarily substrate evolution.

Expected reusable implementation knowledge:

- high-dimensional SDMX provider handling;
- selecting bounded slices from large dataflow catalogs;
- dimensional identity construction discipline;
- IMF endpoint/version/protocol quirks;
- evidence for or against eventual SDMX-family helper extraction.

Expected reduction in future engineering, human, and LLM effort: Medium-High.

- IMF is likely valuable eventually, but first-slice overhead may be high relative to clean architectural knowledge.
- Some effort may be spent on catalog/source discovery rather than testing the observed boundary.

Falsification/stress value: High, but less efficient than ECB or ALFRED/FRED.

Main risk:

- High setup/discovery cost may blur the lesson. A failure may reflect IMF endpoint discovery, not MacroForge architecture.

### 4. Additional Treasury Fiscal Data endpoints

Possible bounded targets:

- `debt_to_penny`, `mts_table_4`, or another Fiscal Data API endpoint with different frequency/category shape;
- no broad Treasury support;
- no pagination framework extraction.

Architectural assumption tested:

```text
Treasury endpoint variation remains provider-specific pre-boundary work and does not justify a Treasury framework, API pagination framework, or observed-boundary evolution after one successful Treasury endpoint.
```

Expected implementation effort: Low-Medium.

Expected pre-boundary effort: Medium.

- Acquisition/query provenance is already partially learned from TASK-054.
- New endpoint-specific metadata, daily dates, fiscal categories, or table concepts may require new normalization choices.

Expected post-boundary effort: Very Low.

- Monthly endpoints should fit directly.
- Daily endpoints may require either bounded aggregation avoidance or a contract decision because `ObservedIngestionPackage` currently explicitly preserves annual, quarterly, and monthly distinctions, not daily.

Probability `ObservedIngestionPackage` contract requires evolution: 5% for monthly endpoint; 35% for daily endpoint.

- A daily endpoint would stress period granularity and could force explicit daily support if selected honestly.
- A monthly endpoint would mostly confirm TASK-054.

Probability Deterministic Ingestion Substrate requires evolution: 5%.

Expected reusable implementation knowledge:

- endpoint-to-endpoint variation within a provider;
- when repeated Treasury query/pagination code becomes extraction-eligible;
- fiscal-date handling across multiple endpoint shapes;
- daily-frequency pressure if deliberately selected.

Expected reduction in future engineering, human, and LLM effort: Medium.

- Useful for provider-family learning, but weaker as a heterogeneous source because Treasury has already been sampled.

Falsification/stress value: Medium.

Main risk:

- Selecting another Treasury endpoint optimizes implementation count and provider depth more than heterogeneous architectural learning, unless the endpoint deliberately stresses daily frequency.

### 5. Additional BEA NIPA slice

Possible bounded target:

- another BEA NIPA table or a different NIPA table frequency/line structure;
- no broad BEA support;
- no canonical loading.

Architectural assumption tested:

```text
BEA table/line-code variation remains pre-boundary provider-specific normalization and does not justify BEA table infrastructure or observed-boundary evolution after one successful BEA slice.
```

Expected implementation effort: Low-Medium.

Expected pre-boundary effort: Medium.

- Table/line metadata patterns are already learned from TASK-053.
- New table shapes may test row-stub/header handling but are unlikely to challenge the observed boundary if bounded to annual/quarterly observations.

Expected post-boundary effort: Very Low.

Probability `ObservedIngestionPackage` contract requires evolution: 5%.

Probability Deterministic Ingestion Substrate requires evolution: 5%.

Expected reusable implementation knowledge:

- within-provider BEA table variation;
- stronger evidence for future BEA parser/helper extraction;
- table-family identity discipline.

Expected reduction in future engineering, human, and LLM effort: Medium.

- Useful if the next objective were making BEA support cheaper.
- Lower value for heterogeneous architecture falsification because BEA was just sampled in TASK-053.

Falsification/stress value: Low-Medium.

Main risk:

- Too convenient. It would likely confirm current assumptions without teaching much about architecture beyond BEA-specific variation.

## Ranking by architectural learning per unit of engineering effort

1. ECB SDW bounded slice.
2. ALFRED/FRED vintage-aware bounded slice.
3. IMF SDMX bounded slice.
4. Additional Treasury Fiscal Data endpoint.
5. Additional BEA NIPA slice.

## Why ECB ranks first despite ALFRED/FRED having higher falsification value

ALFRED/FRED is the strongest pure falsification candidate because vintage/revision semantics directly challenge the current observation/release identity model. However, implementation risk is meaningfully higher because no-key probes returned HTTP 400 and the work may require API-key handling or careful fixture acquisition before architectural learning begins.

ECB SDW is the better next bounded evidence slice because it has:

- high architectural learning value;
- reachable public endpoints in the current environment;
- independent SDMX-family evidence distinct from OECD;
- enough similarity to test whether shared SDMX mechanics are converging;
- enough provider difference to prevent overfitting to OECD;
- realistic bounded implementation size;
- meaningful but not excessive probability of stressing the observed boundary.

ECB optimizes the requested target better than convenience candidates: it is likely to teach whether MacroForge should continue treating SDMX parsing/metadata as source-specific or begin watching for extraction-eligible convergence after more evidence.

## Recommendation

Select ECB SDW as the recommended TASK-055 candidate, but do not implement it until explicitly approved.

Recommended task title:

```text
TASK-055 — Bounded ECB SDW Evidence Slice
```

Recommended implementation objective:

```text
Implement one bounded ECB SDW source slice through ObservedIngestionPackage to test whether a second independent SDMX-family provider stresses the current source-specific pre-boundary -> observed-boundary -> deterministic post-boundary architecture, and to gather evidence for or against future SDMX helper extraction.
```

Recommended bounded target shape:

- one small ECB SDW dataflow/series fixture;
- prefer monthly or quarterly frequency to avoid daily-period contract evolution unless the explicit goal is to test daily support;
- preserve SDMX URL/query evidence, dataflow identity, key dimensions, codelist/attribute evidence, provider period code, unit, and source payload;
- no broad ECB support;
- no SDMX framework extraction;
- no canonical PostgreSQL loading;
- no live production writes.

## Pre-implementation prediction ledger for ECB SDW

These predictions must be evaluated after implementation as Confirmed, Partially confirmed, or Refuted.

1. Expected contract evolution

Prediction: No `ObservedIngestionPackage` contract evolution should be required if the bounded slice uses annual, quarterly, or monthly observations.

Probability that `ObservedIngestionPackage` requires modification: 15%.

Risk condition: Contract pressure increases if the selected ECB slice uses daily observations, non-territory dimensional identities, or multiple dimensions that cannot be represented without lossy provider indicator construction.

2. Expected substrate evolution

Prediction: No Deterministic Ingestion Substrate evolution should be required.

Expected affected components: none.

Risk condition: Existing feedback/comparison may be less legible for dense SDMX keys, but that should be an explanation-quality issue, not core substrate evolution.

3. Expected new pre-boundary patterns

Prediction: ECB will produce reusable pre-boundary evidence for:

- independent SDMX XML acquisition/query provenance;
- SDMX dataflow identity capture;
- dimension-key normalization outside OECD;
- codelist/attribute interpretation;
- provider-specific unit/frequency handling;
- deterministic construction of provider indicator identity from multi-dimensional SDMX keys;
- deciding whether SDMX commonality is real convergence or superficial protocol similarity.

4. Expected reusable lessons

Prediction: ECB will clarify whether MacroForge should keep SDMX logic fully source-specific for now or begin recording repeated algorithm/implementation convergence toward a future bounded SDMX helper.

Expected lesson if confirmed:

- SDMX is a protocol family, not yet a shared MacroForge abstraction.
- Shared extraction remains premature until OECD and ECB demonstrate convergent parsing, dimension mapping, metadata preservation, and deterministic verification patterns.

Expected lesson if refuted:

- If ECB requires substantial duplicated mechanics identical to OECD, MacroForge should record a stronger extraction candidate for a future SDMX helper, but still not extract during TASK-055 unless explicitly scoped.

5. Expected effort distribution

Prediction:

- Acquisition: Medium.
- Provider interpretation: Medium-High.
- Normalization: Medium-High.
- Observed package construction: Low.
- Post-boundary substrate: Very Low to Low.
- Canonical loading: None.
- Verification: Medium.
- Testing: Medium.

6. Expected reduction in future engineering, human, and LLM effort

Prediction: High.

Reason: A second independent SDMX implementation will improve future estimates for ECB, IMF, OECD-like sources, and any future SDMX-family extraction decision. It should reduce future LLM/human ambiguity about whether repeated SDMX vocabulary is enough to justify shared code, or whether provider-specific dimension semantics still dominate.

## Non-goals for recommended TASK-055

- No implementation before explicit approval.
- No broad ECB support.
- No source framework.
- No SDMX framework extraction.
- No provider metadata framework.
- No canonical PostgreSQL loading.
- No live production writes.
- No daily-period support unless explicitly accepted as the contract-stress target.
- No substrate redesign unless implementation evidence makes the current architecture fail.
- No general IMF/FRED/Treasury/BEA work.

## Final assessment

ECB SDW is the best next candidate for architectural learning per unit of engineering effort.

ALFRED/FRED has the highest raw falsification value, but the access/key and vintage-fixture uncertainty makes it less efficient as the immediate next bounded slice. It should remain the next strong stress-test candidate after ECB or once a clean vintage fixture/access path is confirmed.

Additional Treasury and BEA slices are too convenient for the current objective. They would likely reduce implementation friction inside already-sampled provider families, but they are less likely to falsify or significantly stress MacroForge's current architecture.
