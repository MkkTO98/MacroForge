# Architectural Confidence Ledger

Status: active lightweight architectural reasoning ledger
Created: 2026-06-29

## Purpose

This ledger records the important architectural assumptions currently guiding MacroForge.

It is intentionally lightweight. Confidence values are disciplined engineering estimates, not statistical claims.

Use this ledger to:

- make architectural assumptions explicit;
- identify which implementation evidence supports or weakens them;
- improve future source-implementation estimates;
- prevent convenience-driven architecture changes;
- keep extraction evidence-gated.

Update this ledger after materially informative implementations, especially heterogeneous source slices.

After every heterogeneous source implementation, perform a post-implementation calibration step for each tracked assumption:

- confidence before implementation;
- confidence after implementation;
- evidence supporting the update;
- whether confidence increased, decreased, or remained unchanged.

Also record one lightweight implementation-level field:

- Prediction Quality: Accurate, Mostly Accurate, Mixed, or Poor.

Support Prediction Quality with short evidence only. The goal is trend observation, not numerical scoring.

Over time, this ledger should answer one question:

```text
Is MacroForge becoming better at predicting future implementation behavior?
```

The objective is to improve MacroForge's future implementation estimates, not to create statistical precision.

## Prediction Quality scale

- Accurate: predictions were materially correct and useful for implementation decisions.
- Mostly Accurate: predictions were directionally correct with minor misses or under-specified details.
- Mixed: important predictions were both confirmed and refuted, or predictions were too uneven to guide future decisions confidently.
- Poor: predictions missed important behavior, effort centers, or architectural pressure.

Repeated Poor or Mixed prediction quality should increase architectural attention even when implementation succeeds, because it indicates missing understanding.

## Confidence scale

- 0-30%: weak assumption; likely wrong or under-evidenced.
- 31-60%: plausible but uncertain.
- 61-80%: supported by repeated evidence but still falsifiable.
- 81-95%: strongly supported; changes require substantial contrary evidence.
- 96-100%: reserved for invariants or explicit project policy, not empirical architecture bets.

## Current assumptions

### 1. ObservedIngestionPackage boundary is correctly placed

Current confidence: 95%.

Assumption:

```text
The boundary between source-specific acquisition/normalization and deterministic shared post-boundary mechanics is currently placed correctly at `ObservedIngestionPackage`.
```

Supporting evidence:

- WDI, OECD_NAAG, EUROSTAT_NAMQ_GDP, BLS_CPI, BEA_NIPA, and TREASURY_FISCAL_DATA can be represented through the observed package model.
- TASK-053 BEA table/line evidence required no contract evolution.
- TASK-054 Treasury row-oriented API evidence required no contract evolution.
- TASK-055 ECB SDW monthly exchange-rate evidence required no contract evolution while preserving SDMX structure/query evidence.
- TASK-056 IMF MFS_IR monthly interest-rate evidence required no contract evolution while preserving IMF dataflow, DSD, dimension-order, codelist, series-attribute, and observation-attribute evidence.
- TASK-057 BIS WS_CBPOL monthly policy-rate evidence required no contract evolution while preserving BIS dataflow, reference-area, series-attribute, and observation-attribute evidence.
- TASK-058 ALFRED GDP revision-vintage evidence preserved two provider-backed vintages and multiple source-backed values for the same economic period without observed-package evolution.
- TASK-059 ILOSTAT unemployment-rate evidence preserved annual labor-market observations and labor classification/status/source evidence without observed-package evolution.
- TASK-060 UN Comtrade trade evidence preserved bilateral reporter/partner/direction/product/value-basis evidence without observed-package evolution.
- TASK-061 WDI demographic foundation evidence preserved eight demographic concepts without observed-package evolution.
- TASK-062 Eurostat input-output matrix evidence preserved product-by-product matrix cells, product-role pairs, stock-flow roles, JSON-stat flat indexes, and CPA labels without observed-package evolution.
- TASK-063 IMF BOP financial-account evidence preserved asset/liability accounting entries, direct/portfolio investment categories, BPM6 methodology, scale, and access/security metadata without observed-package evolution.
- TASK-064 Eurostat energy balance evidence preserved energy balance components, fuel/product categories, KTOE energy units, JSON-stat flat indexes, and official energy-accounting labels without observed-package evolution.
- TASK-065 FRED yield-curve evidence preserved same-period market curve points, tenor metadata, percent yield units, and CSV row/column evidence without observed-package evolution.
- Post-boundary fingerprinting, comparison, validation, lineage, and feedback operate across heterogeneous source shapes.

Future implementations that can increase confidence:

- Additional materially different sources if they pass through the boundary without loss of provenance.
- More revision-aware sources if vintage semantics can be represented without muddying observation identity.

Future implementations that can decrease confidence:

- Any source requiring lossy encoding into provider indicator/territory/period fields.
- Any repeated need to add observed fields for source families rather than true shared semantics.
- Any post-boundary component requiring source-specific conditionals.

### 2. Deterministic Ingestion Substrate is sufficiently stable for continued heterogeneous source expansion

Current confidence: 88%.

Assumption:

```text
The current deterministic post-boundary substrate is stable enough that more architectural knowledge comes from bounded heterogeneous source implementations than from substrate-first refinement.
```

Supporting evidence:

- Deterministic Change Verification, Canonical Lineage Event Generation, Contract Validation and Drift Detection, and Deterministic Ingestion Feedback are Verified for current scopes.
- TASK-053, TASK-054, TASK-055, TASK-056, TASK-057, TASK-058, TASK-059, TASK-060, and TASK-061 required no substrate redesign.
- Recent implementation effort has repeatedly concentrated before the boundary.

Future implementations that can increase confidence:

- Another materially different source passing through unchanged substrate mechanics.
- Three consecutive heterogeneous implementations without post-boundary redesign, triggering a bounded stability review.

Future implementations that can decrease confidence:

- Repeated substrate explanation failures.
- Need for source-specific substrate branches.
- Contract validation/fingerprint/lineage semantics failing for common macroeconomic source patterns.

### 3. Most future engineering effort belongs before the observed boundary

Current confidence: 88%.

Assumption:

```text
For near-term trustworthy economic sources, most new implementation effort will be acquisition, provider interpretation, source-specific normalization, and identity construction before `ObservedIngestionPackage`.
```

Supporting evidence:

- BLS_CPI, BEA_NIPA, and TREASURY_FISCAL_DATA all concentrated work before the observed boundary.
- TASK-054 confirmed query provenance, endpoint metadata, fiscal period handling, and categorical row identity as pre-boundary concerns.
- TASK-055 confirmed ECB SDMX dataflow, series key, structure metadata, exchange-rate unit construction, and provider identity remain pre-boundary concerns.
- TASK-056 confirmed IMF SDMX StructureSpecificData parsing, dataflow/DSD/codelist metadata preservation, dimension-order handling, interest-rate identity, and IMF series/observation attributes remain pre-boundary concerns.
- TASK-057 confirmed BIS SDMX StructureSpecificData parsing, reference-area handling, policy-rate identity, and BIS series/observation attributes remain pre-boundary concerns.
- TASK-058 confirmed ALFRED CSV/vintage-column parsing, release-vintage identity, changed/unchanged overlap checks, and revision-summary construction remain pre-boundary concerns.
- TASK-059 confirmed ILOSTAT JSON parsing, labor classification code preservation, source-code preservation, and observation-status interpretation remain pre-boundary concerns.
- TASK-060 confirmed UN Comtrade JSON parsing, reporter/partner role preservation, trade-direction/product identity, value-basis handling, and quantity/weight metadata preservation remain pre-boundary concerns.
- TASK-061 confirmed WDI demographic indicator selection, multi-indicator unit/concept metadata, per-indicator API acquisition, and fixture shaping remain pre-boundary concerns.
- Post-boundary changes have been Low to Very Low in recent source slices.

Future implementations that can increase confidence:

- Additional non-SDMX sources with new payload shapes but unchanged post-boundary mechanics.
- More revision or trade sources if source-specific identity construction dominates effort.

Future implementations that can decrease confidence:

- Sources whose main difficulty is post-boundary comparison, validation, lineage, or canonical semantics.
- Repeated contract changes after the boundary.
- Provider families where shared pre-boundary layers become obviously necessary.

### 4. Provider interpretation should remain source-specific for now

Current confidence: 88%.

Assumption:

```text
Provider metadata interpretation should remain source-specific until repeated implementations show stable semantic convergence.
```

Supporting evidence:

- BEA table/line metadata and Treasury endpoint metadata were both useful but not shared enough to justify provider metadata infrastructure.
- OECD SDMX, Eurostat JSON-stat, BEA iTable, BLS API, and Treasury API all expose different provider semantics.
- ECB SDW shares SDMX GenericData mechanics with OECD, but EXR dataflow dimensions, unit construction, and structure metadata interpretation remained ECB-specific.
- IMF MFS_IR repeats SDMX-family dataflow/DSD/codelist concepts, but StructureSpecificData shape, MFS_IR metadata filtering, interest-rate identity, and IMF access/security/IFS attributes remained IMF-specific.
- BIS WS_CBPOL repeats SDMX-family dataflow/series/observation concepts, but reference-area interpretation, policy-rate identity, and BIS source/status/confidentiality attributes remained BIS-specific.
- TASK-058 ALFRED revision-vintage behavior required source-specific GDP vintage-column parsing, vintage date interpretation, release identity preservation, and changed/unchanged overlap analysis.
- TASK-059 ILOSTAT labor-market behavior required source-specific interpretation of `source`, `sex`, `classif1`, and `obs_status` codes without generic labor/classification infrastructure.
- TASK-060 UN Comtrade trade behavior required source-specific interpretation of reporter/partner roles, flow direction, product classification, FOB/CIF value basis, and quantity/weight fields without generic trade infrastructure.
- TASK-061 WDI demographic behavior required source-specific interpretation of demographic foundation indicators, concept categories, and unit labels without generic demographic infrastructure.
- Shared infrastructure with source-specific conditionals is explicitly rejected by the Strategic Constitution.

Future implementations that can increase confidence:

- Additional sources whose provider semantics differ despite superficial payload similarity.
- Additional revision-aware sources if ordinary revision semantics remain provider-specific.

Future implementations that can decrease confidence:

- Multiple providers showing nearly identical metadata interpretation algorithms.
- Repeated duplicated provider-metadata code with stable algorithms and no source-specific conditionals.

### 5. SDMX commonality is currently only protocol-level

Current confidence: 82%.

Assumption:

```text
SDMX is currently an acquisition/protocol family, not yet a MacroForge architectural boundary.
```

Supporting evidence:

- Current strong SDMX evidence is mainly OECD; one provider is insufficient for extraction.
- Similar XML/dataflow vocabulary does not prove convergent provider semantics.
- TASK-055 ECB SDW showed repeated SDMX XML mechanics but source-specific provider interpretation remained substantial.
- TASK-056 IMF MFS_IR strengthened repeated SDMX-family evidence across OECD/ECB/IMF, but IMF StructureSpecificData differed from ECB GenericData and still required source-specific IMF interpretation.
- TASK-057 BIS WS_CBPOL strengthened repeated SDMX-family evidence across OECD/ECB/IMF/BIS, but BIS StructureSpecificData and provider attribute interpretation remained source-specific.
- DEC-022 requires repeated implementation evidence before extraction.

Future implementations that can increase confidence:

- More SDMX-family providers showing shared syntax but source-specific semantics.

Future implementations that can decrease confidence:

- SDMX providers naturally producing the same intermediate normalized SDMX representation before `ObservedIngestionPackage`.
- Multiple SDMX implementations requiring substantially identical algorithms for structure parsing, codelist interpretation, key normalization, and observation construction.

### 6. Future reusable capability extraction should remain evidence-driven

Current confidence: 95%.

Assumption:

```text
Reusable infrastructure should be extracted only after implementation evidence demonstrates contract convergence, algorithm convergence, implementation convergence, deterministic verification, acceptable coupling, and measurable future effort reduction.
```

Supporting evidence:

- Strategic Constitution v1.1 explicitly governs extraction this way.
- Earlier tiny helper extractions were safer when they were mechanical and evidence-backed.
- Premature framework extraction remains a recurring project risk.
- TASK-053 through TASK-061 generated useful patterns without justifying extraction.

Future implementations that can increase confidence:

- Any source implementation where restraint avoids unnecessary complexity.
- Any later extraction candidate succeeding because repeated evidence made scope obvious.

Future implementations that can decrease confidence:

- Repeated duplicated code causing defects, drift, or high maintenance burden because extraction was delayed too long.
- Local agents repeatedly spending high LLM/human effort on identical source-family mechanics.

### 7. Source-specific first remains the correct posture for provider acquisition/parsing

Current confidence: 88%.

Assumption:

```text
New provider acquisition and parsing should start source-specific; shared mechanics should be extracted only after repeated non-semantic duplication appears.
```

Supporting evidence:

- WDI, OECD, Eurostat, BLS, BEA, and Treasury each had materially different acquisition and payload shapes.
- Source-specific slices preserved boundedness and auditability.
- Repeated post-boundary stability suggests the pre-boundary adapter posture is working.
- TASK-055 kept ECB SDW source-specific while still producing a valid observed package and explicit future extraction evidence.
- TASK-056 kept IMF MFS_IR source-specific while preserving third-provider SDMX evidence and avoiding generic IMF/SDMX framework extraction.
- TASK-057 kept BIS WS_CBPOL source-specific while preserving fourth-provider SDMX-family evidence and avoiding generic BIS/SDMX framework extraction.
- TASK-058 kept ALFRED GDP revision-vintage parsing source-specific while avoiding broad FRED/ALFRED support, generic revision infrastructure, or API-key infrastructure.
- TASK-059 kept ILOSTAT unemployment parsing source-specific while avoiding broad ILOSTAT support, generic labor infrastructure, classification frameworks, or canonical loading.
- TASK-060 kept UN Comtrade trade parsing source-specific while avoiding broad Comtrade support, generic trade infrastructure, product classification frameworks, mirror trade, or canonical loading.
- TASK-061 kept WDI demographic foundation parsing source-specific while avoiding broad demographic support, projection systems, demographic frameworks, or canonical loading.

Future implementations that can increase confidence:

- Additional source-specific adapters remaining small, auditable, deterministic, and framework-free.

Future implementations that can decrease confidence:

- Multiple providers sharing enough acquisition/parsing logic to make independent adapters wasteful.
- Repeated provider-specific adapters differing only in endpoint constants.

### 8. Prediction-ledger implementation improves future estimation quality

Current confidence: 87%.

Assumption:

```text
Writing pre-implementation predictions and evaluating them after implementation will improve MacroForge's ability to estimate future source implementations.
```

Supporting evidence:

- TASK-053 and TASK-054 prediction reviews clarified that post-boundary effort remained lower than expected and pre-boundary work dominated.
- TASK-055 prediction review clarified that repeated SDMX XML mechanics are real but not yet architecture-boundary evidence.
- TASK-056 prediction review clarified that repeated SDMX-family dataflow/DSD/codelist concepts now span OECD, ECB, and IMF, while source-specific IMF StructureSpecificData and metadata interpretation still dominate.
- TASK-058 prediction review confirmed the revision-source planning chain: ordinary ALFRED release-vintage semantics fit the existing boundary while producing weak early evidence only, not extraction justification.
- TASK-059 prediction review accurately anticipated normal domain-expansion behavior: no boundary/substrate pressure, source-specific ILOSTAT interpretation, and no architectural action.
- TASK-060 prediction review accurately anticipated normal trade-domain expansion behavior: no boundary/substrate pressure, source-specific UN Comtrade interpretation, and no architectural action.
- TASK-061 prediction review accurately anticipated normal demographic-domain expansion behavior: no boundary/substrate pressure, source-specific WDI demographic interpretation, and no architectural action.
- The prediction review format turns implementation into reusable judgment, not just completed code.

Future implementations that can increase confidence:

- Later source slices where prediction errors directly improve candidate ranking.

Future implementations that can decrease confidence:

- Prediction ledgers becoming ritual documentation without changing future decisions.
- Predictions being too vague to classify as Confirmed, Partially confirmed, or Refuted.

## Post-implementation calibration template

Use this template after every heterogeneous source implementation.

```markdown
## Calibration — TASK-XXX source name

Date:
Related task:
Related prediction ledger:
Related implementation lessons:
Related surprise-log entry, if any:
Prediction Quality: Accurate / Mostly Accurate / Mixed / Poor
Prediction Quality evidence:

| Assumption | Confidence before | Confidence after | Direction | Evidence supporting update |
|---|---:|---:|---|---|
| ObservedIngestionPackage boundary is correctly placed | | | increased/decreased/unchanged | |
| Deterministic Ingestion Substrate is sufficiently stable | | | increased/decreased/unchanged | |
| Most future engineering effort belongs before the observed boundary | | | increased/decreased/unchanged | |
| Provider interpretation should remain source-specific for now | | | increased/decreased/unchanged | |
| SDMX commonality is currently only protocol-level | | | increased/decreased/unchanged | |
| Future reusable capability extraction should remain evidence-driven | | | increased/decreased/unchanged | |
| Source-specific first remains correct for acquisition/parsing | | | increased/decreased/unchanged | |
| Prediction-ledger implementation improves future estimation quality | | | increased/decreased/unchanged | |
```

## Calibration — TASK-055 ECB SDW bounded exchange-rate evidence slice

Date: 2026-06-29
Related task: `artifacts/tasks/TASK-055-bounded-ecb-sdw-architectural-experiment.md`
Related prediction ledger: `artifacts/tasks/TASK-055-bounded-ecb-sdw-architectural-experiment.md`
Related implementation lessons: `artifacts/reports/L-20260629-task-055-implementation-lessons.md`
Related surprise-log entry, if any: `docs/architecture/architectural-surprise-log.md` records no material TASK-055 surprises.
Prediction Quality: Accurate
Prediction Quality evidence: TASK-055 predictions correctly anticipated no observed-package evolution, no deterministic substrate evolution, source-specific ECB SDW interpretation before the observed boundary, and future SDMX extraction evidence without immediate extraction justification.

| Assumption | Confidence before | Confidence after | Direction | Evidence supporting update |
|---|---:|---:|---|---|
| ObservedIngestionPackage boundary is correctly placed | 85% | 88% | increased | ECB SDW monthly exchange-rate evidence preserved SDMX query, structure, series, attribute, and observation evidence through existing `raw_evidence`, `attributes`, and `source_payload`; contract validation passed without observed-package evolution. |
| Deterministic Ingestion Substrate is sufficiently stable | 80% | 83% | increased | Existing validation, fingerprinting, and package comparison worked unchanged; no post-boundary production code changed. |
| Most future engineering effort belongs before the observed boundary | 82% | 84% | increased | Implementation effort centered on ECB-specific SDMX interpretation, period/unit/indicator identity, and metadata preservation before the boundary. |
| Provider interpretation should remain source-specific for now | 78% | 82% | increased | ECB shared GenericData XML mechanics with OECD, but EXR dataflow dimensions, unit construction, structure metadata, and provider indicator semantics remained ECB-specific. |
| SDMX commonality is currently only protocol-level | 70% | 78% | increased | ECB confirmed repeated SDMX XML/protocol mechanics while not producing enough source-neutral semantic convergence to justify an SDMX Interpretation Layer. |
| Future reusable capability extraction should remain evidence-driven | 95% | 95% | unchanged | TASK-055 produced future extraction evidence around repeated SDMX mechanics but did not satisfy the contract/algorithm/implementation convergence gate. |
| Source-specific first remains correct for acquisition/parsing | 82% | 84% | increased | A bounded source-specific ECB adapter stayed small, auditable, deterministic, and framework-free while preserving provider evidence. |
| Prediction-ledger implementation improves future estimation quality | 75% | 80% | increased | The prediction ledger cleanly separated confirmed architecture stability from future SDMX extraction evidence, improving the next SDMX-family estimate. |

## Calibration — TASK-056 IMF MFS_IR bounded SDMX evidence slice

Date: 2026-06-30
Related task: `artifacts/tasks/TASK-056-bounded-imf-mfs-ir-sdmx-evidence-slice.md`
Related prediction ledger: `artifacts/tasks/TASK-056-bounded-imf-mfs-ir-sdmx-evidence-slice.md`
Related implementation lessons: `artifacts/reports/L-20260630-task-056-implementation-lessons.md`
Related surprise-log entry, if any: `docs/architecture/architectural-surprise-log.md` records no material TASK-056 surprises.
Prediction Quality: Accurate
Prediction Quality evidence: TASK-056 predictions correctly anticipated no observed-package evolution, no deterministic substrate evolution, source-specific IMF MFS_IR interpretation before the observed boundary, and stronger SDMX-family extraction evidence without immediate generic SDMX extraction justification.

| Assumption | Confidence before | Confidence after | Direction | Evidence supporting update |
|---|---:|---:|---|---|
| ObservedIngestionPackage boundary is correctly placed | 88% | 90% | increased | IMF MFS_IR monthly interest-rate evidence preserved IMF dataflow, DSD, dimension order, codelist, source-query, series-attribute, and observation-attribute evidence through existing `raw_evidence`, `attributes`, and `source_payload`; contract validation passed without observed-package evolution. |
| Deterministic Ingestion Substrate is sufficiently stable | 83% | 85% | increased | Existing validation, fingerprinting, and package comparison worked unchanged; no post-boundary production code changed. |
| Most future engineering effort belongs before the observed boundary | 84% | 85% | increased | Implementation effort centered on IMF-specific StructureSpecificData parsing, metadata filtering, dataflow/DSD/codelist preservation, dimension order, and provider identity before the boundary. |
| Provider interpretation should remain source-specific for now | 82% | 84% | increased | IMF repeated SDMX-family concepts but required IMF-specific dataflow, DSD, codelist, StructureSpecificData, access/security/IFS attribute, and interest-rate identity interpretation. |
| SDMX commonality is currently only protocol-level | 78% | 80% | increased | IMF strengthened repeated SDMX-family evidence across OECD/ECB/IMF while also showing payload-shape and provider-semantics differences that do not justify a source-neutral SDMX Interpretation Layer. |
| Future reusable capability extraction should remain evidence-driven | 95% | 95% | unchanged | TASK-056 strengthened future SDMX extraction evidence but did not satisfy contract/algorithm/implementation convergence gates. |
| Source-specific first remains correct for acquisition/parsing | 84% | 85% | increased | A bounded source-specific IMF adapter preserved third-provider SDMX evidence without broad IMF support, generic SDMX infrastructure, or substrate extraction. |
| Prediction-ledger implementation improves future estimation quality | 80% | 82% | increased | TASK-056 separated confirmed architecture stability from stronger-but-still-insufficient SDMX extraction evidence, improving future SDMX-family source estimates. |

## Calibration — TASK-057 BIS WS_CBPOL bounded SDMX evidence slice

Date: 2026-06-30
Related task: `artifacts/tasks/TASK-057-bounded-bis-cbpol-sdmx-evidence-slice.md`
Related prediction ledger: `artifacts/tasks/TASK-057-bounded-bis-cbpol-sdmx-evidence-slice.md`
Related implementation lessons: `artifacts/reports/L-20260630-task-057-implementation-lessons.md`
Related surprise-log entry, if any: `docs/architecture/architectural-surprise-log.md` records no material TASK-057 surprises.
Prediction Quality: Accurate
Prediction Quality evidence: TASK-057 predictions correctly anticipated no observed-package evolution, no deterministic substrate evolution, source-specific BIS interpretation before the observed boundary, and stronger SDMX-family extraction evidence without generic SDMX extraction justification.

| Assumption | Confidence before | Confidence after | Direction | Evidence supporting update |
|---|---:|---:|---|---|
| ObservedIngestionPackage boundary is correctly placed | 90% | 91% | increased | BIS WS_CBPOL policy-rate evidence preserved dataflow, reference-area, series-attribute, observation-attribute, and raw source payload evidence through existing fields; contract validation passed without observed-package evolution. |
| Deterministic Ingestion Substrate is sufficiently stable | 85% | 86% | increased | Existing validation, fingerprinting, and package comparison worked unchanged; no post-boundary production code changed. |
| Most future engineering effort belongs before the observed boundary | 85% | 86% | increased | Implementation effort centered on BIS-specific StructureSpecificData parsing, policy-rate identity, and provider attribute interpretation before the boundary. |
| Provider interpretation should remain source-specific for now | 84% | 85% | increased | BIS repeated SDMX-family concepts but required BIS-specific reference-area, source/ref, compilation, status, confidentiality, and policy-rate identity interpretation. |
| SDMX commonality is currently only protocol-level | 80% | 82% | increased | BIS strengthened SDMX-family evidence across OECD/ECB/IMF/BIS while still not producing enough source-neutral convergence to justify extraction. |
| Future reusable capability extraction should remain evidence-driven | 95% | 95% | unchanged | TASK-057 strengthened future SDMX extraction evidence but did not satisfy contract/algorithm/implementation convergence gates. |
| Source-specific first remains correct for acquisition/parsing | 85% | 86% | increased | A bounded source-specific BIS adapter preserved fourth-provider SDMX evidence without broad BIS support, generic SDMX infrastructure, or substrate extraction. |
| Prediction-ledger implementation improves future estimation quality | 82% | 83% | increased | TASK-057 confirmed the prediction-ledger pattern can distinguish repeated protocol evidence from actionable extraction evidence. |

## Calibration — TASK-058 ALFRED GDP revision-vintage evidence slice

Date: 2026-06-30
Related task: `artifacts/tasks/TASK-058-bounded-alfred-revision-vintage-evidence-slice.md`
Related prediction ledger: `artifacts/tasks/TASK-058-bounded-alfred-revision-vintage-evidence-slice.md`
Related implementation lessons: `artifacts/reports/L-20260630-task-058-implementation-lessons.md`
Related surprise-log entry, if any: `docs/architecture/architectural-surprise-log.md` records no material TASK-058 architectural surprises.
Prediction Quality: Accurate
Prediction Quality evidence: TASK-058 predictions correctly anticipated no observed-package evolution, no deterministic substrate evolution, source-specific ALFRED vintage interpretation before the observed boundary, and weak early revision-infrastructure evidence without extraction justification. The only notable observation was expected in hindsight: an unchanged value control still differs at package-comparison level because vintage identity is preserved in attributes/source payload.

| Assumption | Confidence before | Confidence after | Direction | Evidence supporting update |
|---|---:|---:|---|---|
| ObservedIngestionPackage boundary is correctly placed | 91% | 92% | increased | ALFRED preserved two provider-backed vintages and multiple source-backed values for the same economic period through existing release key, raw evidence, attributes, and source payload; contract validation passed without observed-package evolution. |
| Deterministic Ingestion Substrate is sufficiently stable | 86% | 87% | increased | Existing validation, fingerprinting, and package comparison worked unchanged; same-fixture replay produced identical fingerprints and per-vintage package comparison identified evidence differences deterministically. |
| Most future engineering effort belongs before the observed boundary | 86% | 87% | increased | Implementation effort centered on ALFRED-specific CSV/vintage-column parsing, release-vintage identity, changed/unchanged overlap checks, and fixture design before the boundary. |
| Provider interpretation should remain source-specific for now | 85% | 86% | increased | ALFRED revision-vintage behavior required provider-specific GDP vintage-column interpretation and release identity preservation; no general revision/provider abstraction was justified. |
| SDMX commonality is currently only protocol-level | 82% | 82% | unchanged | TASK-058 was intentionally non-SDMX and did not materially update SDMX extraction evidence. |
| Future reusable capability extraction should remain evidence-driven | 95% | 95% | unchanged | TASK-058 produced first revision-pattern evidence but not contract/algorithm/implementation convergence; extraction remains unjustified. |
| Source-specific first remains correct for acquisition/parsing | 86% | 87% | increased | A bounded source-specific ALFRED adapter remained small, auditable, deterministic, and framework-free while preserving revision-vintage evidence. |
| Prediction-ledger implementation improves future estimation quality | 83% | 84% | increased | The planning chain's predictions accurately isolated the revision behavior, confirmed architecture stability, and prevented premature generic revision infrastructure. |


## Calibration — TASK-059 ILOSTAT unemployment-rate evidence slice

Date: 2026-06-30
Related task: `artifacts/tasks/TASK-059-bounded-ilostat-unemployment-rate-evidence-slice.md`
Related prediction ledger: `artifacts/tasks/TASK-059-bounded-ilostat-unemployment-rate-evidence-slice.md`
Related implementation lessons: `artifacts/reports/L-20260630-task-059-implementation-lessons.md`
Related surprise-log entry, if any: `docs/architecture/architectural-surprise-log.md` records no material TASK-059 architectural surprises.
Prediction Quality: Accurate
Prediction Quality evidence: TASK-059 predictions correctly anticipated normal Domain Expansion Mode behavior: no observed-package evolution, no deterministic substrate evolution, source-specific ILOSTAT labor-classification/status/source interpretation before the observed boundary, and no architectural action.

| Assumption | Confidence before | Confidence after | Direction | Evidence supporting update |
|---|---:|---:|---|---|
| ObservedIngestionPackage boundary is correctly placed | 92% | 93% | increased | ILOSTAT annual unemployment-rate observations preserved indicator, territory, annual period, unit, value, source code, sex classification, age classification, and status evidence through existing fields; contract validation passed without observed-package evolution. |
| Deterministic Ingestion Substrate is sufficiently stable | 87% | 88% | increased | Existing validation, fingerprinting, and package comparison worked unchanged; same-fixture replay produced identical fingerprints. |
| Most future engineering effort belongs before the observed boundary | 87% | 88% | increased | Implementation effort centered on ILOSTAT-specific JSON parsing, code interpretation, and fixture scoping before the boundary. |
| Provider interpretation should remain source-specific for now | 86% | 87% | increased | ILOSTAT required source-specific preservation of labor classification/status/source codes; no generic provider metadata or labor classification framework was justified. |
| SDMX commonality is currently only protocol-level | 82% | 82% | unchanged | TASK-059 was non-SDMX and did not materially update SDMX extraction evidence. |
| Future reusable capability extraction should remain evidence-driven | 95% | 95% | unchanged | TASK-059 added labor-domain coverage but did not produce contract/algorithm/implementation convergence for any extraction candidate. |
| Source-specific first remains correct for acquisition/parsing | 87% | 88% | increased | A bounded source-specific ILOSTAT adapter remained small, auditable, deterministic, and framework-free while preserving labor-market evidence. |
| Prediction-ledger implementation improves future estimation quality | 84% | 85% | increased | The prediction ledger accurately forecast normal domain-expansion behavior and prevented unnecessary architecture review. |

## Calibration — TASK-060 UN Comtrade bilateral total-goods trade evidence slice

Date: 2026-06-30
Related task: `artifacts/tasks/TASK-060-bounded-un-comtrade-bilateral-total-goods-trade-evidence-slice.md`
Related prediction ledger: `artifacts/tasks/TASK-060-bounded-un-comtrade-bilateral-total-goods-trade-evidence-slice.md`
Related implementation lessons: `artifacts/reports/L-20260630-task-060-implementation-lessons.md`
Related surprise-log entry, if any: `docs/architecture/architectural-surprise-log.md` records no material TASK-060 architectural surprises.
Prediction Quality: Accurate
Prediction Quality evidence: TASK-060 predictions correctly anticipated normal Domain Expansion Mode behavior: no observed-package evolution, no deterministic substrate evolution, source-specific UN Comtrade reporter/partner/flow/product/value-basis interpretation before the observed boundary, and no architectural action.

| Assumption | Confidence before | Confidence after | Direction | Evidence supporting update |
|---|---:|---:|---|---|
| ObservedIngestionPackage boundary is correctly placed | 93% | 94% | increased | UN Comtrade bilateral trade observations preserved reporter, partner, trade direction, aggregate product, annual period, nominal value, value-basis, quantity/weight metadata, and raw source payload evidence through existing fields; contract validation passed without observed-package evolution. |
| Deterministic Ingestion Substrate is sufficiently stable | 88% | 89% | increased | Existing validation, fingerprinting, and package comparison worked unchanged; same-fixture replay produced identical fingerprints. |
| Most future engineering effort belongs before the observed boundary | 88% | 89% | increased | Implementation effort centered on UN Comtrade-specific JSON parsing, reporter/partner role preservation, flow/product identity, and value-basis/quantity metadata handling before the boundary. |
| Provider interpretation should remain source-specific for now | 87% | 88% | increased | UN Comtrade required source-specific preservation of trade roles, direction, product classification, FOB/CIF value-basis, and estimation/reporting flags; no generic trade or classification framework was justified. |
| SDMX commonality is currently only protocol-level | 82% | 82% | unchanged | TASK-060 was non-SDMX and did not materially update SDMX extraction evidence. |
| Future reusable capability extraction should remain evidence-driven | 95% | 95% | unchanged | TASK-060 added first trade-domain coverage but did not produce contract/algorithm/implementation convergence for any extraction candidate. |
| Source-specific first remains correct for acquisition/parsing | 88% | 89% | increased | A bounded source-specific UN Comtrade adapter remained small, auditable, deterministic, and framework-free while preserving trade-domain evidence. |
| Prediction-ledger implementation improves future estimation quality | 85% | 86% | increased | The prediction ledger accurately forecast normal trade-domain expansion behavior and prevented unnecessary trade infrastructure or architecture review. |

## Calibration — TASK-061 WDI demographic foundation evidence slice

Date: 2026-06-30
Related task: `artifacts/tasks/TASK-061-bounded-demographic-foundation-evidence-slice.md`
Related prediction ledger: `artifacts/tasks/TASK-061-bounded-demographic-foundation-evidence-slice.md`
Related implementation lessons: `artifacts/reports/L-20260630-task-061-implementation-lessons.md`
Related surprise-log entry, if any: `docs/architecture/architectural-surprise-log.md` records no material TASK-061 architectural surprises.
Prediction Quality: Accurate
Prediction Quality evidence: TASK-061 predictions correctly anticipated normal Domain Expansion Mode behavior: no observed-package evolution, no deterministic substrate evolution, source-specific WDI demographic indicator/unit/concept interpretation before the observed boundary, and no architectural action.

| Assumption | Confidence before | Confidence after | Direction | Evidence supporting update |
|---|---:|---:|---|---|
| ObservedIngestionPackage boundary is correctly placed | 94% | 95% | increased | WDI demographic foundation observations preserved eight indicators, two countries, two annual periods, units, demographic concepts, source URLs, request metadata, and raw source payload evidence through existing fields; contract validation passed without observed-package evolution. |
| Deterministic Ingestion Substrate is sufficiently stable | 89% | 90% | increased | Existing validation, fingerprinting, and package comparison worked unchanged; same-fixture replay produced identical fingerprints. |
| Most future engineering effort belongs before the observed boundary | 89% | 90% | increased | Implementation effort centered on WDI-specific per-indicator acquisition, indicator/unit/concept metadata, and fixture shaping before the boundary. |
| Provider interpretation should remain source-specific for now | 88% | 89% | increased | WDI demographics required source-specific foundation-concept and unit metadata preservation; no generic demographic framework was justified. |
| SDMX commonality is currently only protocol-level | 82% | 82% | unchanged | TASK-061 was non-SDMX and did not materially update SDMX extraction evidence. |
| Future reusable capability extraction should remain evidence-driven | 95% | 95% | unchanged | TASK-061 added first demographic foundation coverage but did not produce contract/algorithm/implementation convergence for any extraction candidate. |
| Source-specific first remains correct for acquisition/parsing | 89% | 90% | increased | A bounded source-specific WDI demographic adapter remained small, auditable, deterministic, and framework-free while preserving foundational demographic evidence. |
| Prediction-ledger implementation improves future estimation quality | 86% | 87% | increased | The prediction ledger accurately forecast normal demographic-domain expansion behavior and prevented unnecessary demographic infrastructure or architecture review. |


## Calibration — TASK-062 Eurostat input-output matrix evidence slice

Date: 2026-07-01
Related task: `artifacts/tasks/TASK-062-bounded-eurostat-input-output-matrix-evidence-slice.md`
Related implementation lessons: `artifacts/reports/L-20260701-task-062-implementation-lessons.md`

Prediction Quality: Accurate.

Calibration summary:

- Observed boundary confidence remained 95%. Matrix cells fit through existing provider indicator, attribute, and source-payload fields.
- Deterministic substrate confidence remained high. Replay, fingerprinting, comparison, and contract validation required no evolution.
- Source-specific-first confidence increased directionally. Eurostat JSON-stat dimension-order/flat-index and product-role interpretation remained source-specific pre-boundary work.
- Extraction confidence remains low for generic matrix/input-output infrastructure. One matrix slice is evidence, not convergence.

Architectural decision: continue Domain Expansion Mode; no architectural action is recommended.


## Calibration — TASK-063 IMF BOP financial-account evidence slice

Date: 2026-07-01
Related task: `artifacts/tasks/TASK-063-bounded-imf-bop-financial-account-evidence-slice.md`
Related implementation lessons: `artifacts/reports/L-20260701-task-063-implementation-lessons.md`

Prediction Quality: Accurate.

Calibration summary:

- Observed boundary confidence remained 95%. BOP financial-account flows fit through existing provider indicator, attribute, and source-payload fields.
- Deterministic substrate confidence remained high. Replay, fingerprinting, comparison, and contract validation required no evolution.
- Source-specific-first confidence increased directionally. IMF BOP accounting-entry and investment-category interpretation remained source-specific pre-boundary work.
- Extraction confidence remains low for generic BOP/financial-flow infrastructure. One bounded financial-flow slice is evidence, not convergence.

Architectural decision: continue Domain Expansion Mode; no architectural action is recommended.
