# Five-Source Architectural Retrospective — 2026-06-30

Status: baseline retrospective
Review type: bounded architectural decision gate
Scope: heterogeneous implementation evidence through TASK-057

## Executive conclusion

MacroForge has objectively learned that the current architecture is more stable than the project could justify claiming before repeated heterogeneous source work.

Across OECD, BEA, Treasury Fiscal Data, ECB SDW, IMF MFS_IR, and BIS WS_CBPOL, the evidence repeatedly shows:

1. `ObservedIngestionPackage` is correctly placed as the boundary after source-specific acquisition and normalization.
2. Deterministic post-boundary mechanics are stable across materially different source shapes.
3. Most new implementation uncertainty is before the boundary: acquisition, provider semantics, metadata preservation, source identity, period handling, and fixture choice.
4. SDMX commonality is real and accumulating, but still mostly protocol / payload-family evidence rather than a proven MacroForge architectural boundary.
5. No shared infrastructure extraction is currently justified under the Constitution / DEC-022 gate.
6. The prediction-ledger methodology is improving architectural judgment because recent predictions are becoming accurate enough to guide source selection and prevent premature extraction.

Decision-gate answer:

```text
Continue heterogeneous source implementation without architectural change: Yes.
Exactly one extraction justified now: No.
Marginal effort trend: decreasing or stable, with effort concentrating before the observed boundary.
```

This retrospective is a baseline. Future retrospectives should measure change against these conclusions rather than re-summarize the same evidence.

## Reviewed evidence

Primary reviewed implementations:

| Source / task | Shape | Status in evidence base |
|---|---|---|
| OECD_NAAG / TASK-012..015 family | SDMX GenericData XML, later source-specific PostgreSQL promotion | Earlier SDMX and canonical-load baseline; source-specific, no generalized SDMX framework. |
| BEA NIPA / TASK-053 | interactive table / table-line metadata | First post-methodology bounded evidence slice; no observed-boundary or substrate evolution. |
| Treasury Fiscal Data / TASK-054 | row-oriented public government JSON API | Confirmed endpoint/query/pagination/row identity fit before observed boundary. |
| ECB SDW / TASK-055 | SDMX GenericData XML exchange-rate series | Tested whether SDMX was becoming a boundary; concluded protocol-level commonality only. |
| IMF MFS_IR / TASK-056 | SDMX StructureSpecificData plus dataflow/DSD/codelist metadata | Strengthened SDMX-family evidence, but provider interpretation remained IMF-specific. |
| BIS WS_CBPOL / TASK-057 | SDMX StructureSpecificData central-bank-policy-rate series | Fourth SDMX-family provider; strengthened evidence without justifying extraction. |

Additional context:

- WDI and Eurostat matter as canonical-loaded baselines: they demonstrate that current deterministic canonical loading exists where scoped, but they do not by themselves justify broad provider frameworks.
- BLS_CPI matters as an additional bounded noncanonical source, but the current formal retrospective evidence is strongest from TASK-053 through TASK-057 plus OECD.

## 1. Prediction accuracy review

### OECD_NAAG baseline

Pre-implementation architectural posture:

- A bounded OECD/SDMX slice could preserve raw SDMX evidence and normalize a small subset without building a generalized SDMX framework.
- PostgreSQL promotion, if accepted, should remain narrow and source-specific.

Actual outcome:

- TASK-012 implemented bounded OECD/SDMX raw-evidence normalization without PostgreSQL load, schema change, live default database writes, or generalized SDMX framework.
- TASK-014 accepted PostgreSQL promotion only through narrow source-specific staging because the existing permanent staging table was WDI-specific.
- TASK-015 implemented source-specific OECD promotion rather than a generic SDMX framework.

Unexpected observations:

- OECD live access needed operational hardening such as a source-specific `User-Agent` header in TASK-013.
- OECD generated early evidence that SDMX mechanics recur, but one SDMX provider was insufficient for extraction.

Prediction accuracy:

- Mostly accurate for source-specific-first posture.
- Less formal than later tasks because the prediction-ledger methodology had not fully stabilized.

### TASK-053 — BEA NIPA

Architectural predictions made:

- Existing substrate components would remain unchanged.
- No additive `ObservedIngestionPackage` evolution would be required for annual/quarterly BEA table observations.
- Engineering effort would concentrate in acquisition, provider interpretation, and normalization.
- BEA would produce reusable pre-boundary evidence, not a reusable post-boundary capability.

Actual outcome:

- All five predictions were confirmed.
- BEA iTableCore NIPA Table 1.1.1 normalized into 252 quarterly observed observations.
- No observed-package or deterministic-substrate evolution was required.

Unexpected observations:

- Conventional BEA API access had API-key friction, so bounded public iTableCore evidence was a better fit.
- Interactive-table structure required source-specific interpretation of prompts, headers, stubs, line numbers, and period columns.

Prediction accuracy:

- Accurate.

### TASK-054 — Treasury Fiscal Data

Architectural predictions made:

- `ObservedIngestionPackage` and deterministic substrate would remain unchanged.
- Treasury endpoint identity, query fields, filters, sort order, pagination metadata, labels, data types, fiscal date, categorical row identity, and endpoint metadata would fit existing fields.
- Effort would concentrate in deterministic API query capture, endpoint metadata interpretation, monthly period normalization, and row identity construction.
- No reusable post-boundary capability would emerge.

Actual outcome:

- All key predictions were confirmed.
- The `avg_interest_rates` endpoint produced 16 monthly observations from one bounded fixture.
- No contract, substrate, canonical loading, or generalized pagination infrastructure was introduced.

Unexpected observations:

- Source-slice choice mattered: a daily endpoint would have created contract pressure outside the task objective, so a monthly endpoint was selected.

Prediction accuracy:

- Accurate.

### TASK-055 — ECB SDW

Architectural predictions made:

- No observed-contract evolution if the ECB slice used monthly observations.
- No deterministic-substrate evolution.
- ECB would show SDMX commonality at XML/protocol level, but provider interpretation would remain source-specific enough that no SDMX Interpretation Layer was justified.
- Repeated SDMX mechanics should be recorded as future extraction evidence only.

Actual outcome:

- Predictions were confirmed.
- ECB monthly EUR/USD exchange-rate evidence preserved SDMX query, structure, series, attribute, and observation evidence through existing fields.
- ECB-specific `EXR`, currency dimensions, exchange-rate unit construction, structure metadata, and provider indicator semantics dominated provider meaning.

Unexpected observations:

- No material surprise was recorded; the observed SDMX repetition was predicted.

Prediction accuracy:

- Accurate.

### TASK-056 — IMF MFS_IR

Architectural predictions made:

- No observed-contract evolution would be required for IMF COUNTRY, INDICATOR, FREQUENCY, TIME_PERIOD, values, series attributes, observation attributes, dataflow identity, DSD identity, dimension order, and codelist evidence.
- No deterministic-substrate evolution.
- IMF would strengthen repeated SDMX evidence but provider interpretation would remain IMF-specific enough to avoid generic extraction.
- Future SDMX extraction evidence would increase but not satisfy the extraction gate.

Actual outcome:

- Observed contract and deterministic substrate required no evolution.
- IMF preserved dataflow `MFS_IR`, version `9.0.0`, DSD `DSD_MFS_IR`, dimensions, codelists, series attributes, and observation attributes through existing observed-package fields.
- The implementation produced six USA/JPN monthly observations.

Unexpected observations:

- The SDMX-boundary prediction was classified as partially confirmed because IMF both strengthened SDMX-family recurrence and showed payload-shape divergence from ECB: IMF used StructureSpecificData while ECB used GenericData.
- This was not an architectural surprise requiring action; it refined the SDMX understanding.

Prediction accuracy:

- Accurate overall; one prediction was partially confirmed in a useful way.

### TASK-057 — BIS WS_CBPOL

Architectural predictions made:

- No `ObservedIngestionPackage` evolution.
- No deterministic-substrate evolution.
- BIS would add source-specific StructureSpecificData parsing, dataflow identity, reference-area handling, series attributes, observation status/confidentiality, and policy-rate identity construction.
- SDMX extraction evidence would increase, but generic SDMX extraction would remain unjustified.
- Effort distribution would be low acquisition, medium provider interpretation, low-medium normalization, low observed-package construction, very low substrate, no canonical loading, and medium testing.

Actual outcome:

- Predictions were confirmed or mostly confirmed.
- BIS produced six US/JP monthly policy-rate observations through the existing observed package.
- Contract validation, replay, comparison, and fingerprinting worked unchanged.
- Public BIS API access was straightforward; most effort was bounded normalization and tests.

Unexpected observations:

- No material architectural surprise.

Prediction accuracy:

- Accurate / mostly accurate.

### Recurring prediction errors

No recurring prediction failures were found.

Recurring calibration pattern:

- Early estimates increasingly correctly predict that contract and substrate changes are unlikely.
- The main uncertainty is now usually provider-specific pre-boundary semantics, not post-boundary architecture.
- The most important near-miss was not an error but a refinement: SDMX evidence keeps getting stronger, while source-neutral extraction evidence remains insufficient.

Architectural meaning:

- MacroForge's implementation predictions are improving.
- If future tasks become less predictable, that will be important evidence, not merely implementation noise.

## 2. Architectural stability assessment

| Subsystem | Assessment | Evidence |
|---|---|---|
| `ObservedIngestionPackage` | Strengthening | BEA table/line metadata, Treasury row JSON, ECB GenericData, IMF StructureSpecificData, and BIS StructureSpecificData all fit existing fields without contract evolution. Confidence ledger is now 91%. |
| Deterministic post-boundary substrate | Strengthening | TASK-053..057 required no substrate redesign. Validation, fingerprinting, package comparison, replay, lineage, and feedback remained unchanged. Confidence ledger is now 86%. |
| Source-specific acquisition layer | Stable / strengthening | Every heterogeneous source required provider-specific acquisition/parsing/metadata interpretation. Source-specific adapters preserved boundedness and auditability. |
| Canonical mapping approach | Stable where scoped; uncertain for broader domains | WDI/OECD/Eurostat canonical-loaded paths exist. BEA/Treasury/ECB/IMF/BIS intentionally stayed evidence-only, so no new canonical-mapping generalization is justified. |
| Lineage | Stable for current scope | No reviewed implementation required lineage redesign; post-boundary lineage remains part of the stable substrate. Evidence is indirect because bounded slices mostly tested package construction and validation. |
| Validation | Strengthening | Every reviewed bounded slice used contract validation successfully; no source-specific validation branches were needed after the boundary. |
| Replay/fingerprinting | Strengthening | ECB, IMF, and BIS lessons explicitly record deterministic package fingerprints and replay/package comparison working unchanged. |
| Testing methodology | Strengthening | RED/GREEN targeted tests plus adjacent regressions repeatedly caught scope and boundary behavior; anti-framework assertions prevented accidental architecture broadening. |
| Documentation methodology | Strengthening | Prediction ledgers, Implementation Lessons, surprise log, confidence ledger, cost index, and pain records transformed implementations into reusable judgment. This methodology is not just narrative; it changed source-selection and extraction restraint. |

No subsystem requires reconsideration now.

Uncertain areas are uncertain because they have not been exercised, not because evidence contradicts them:

- broad canonical loading for evidence-only slices;
- revision/vintage semantics;
- trade/industry/company ingestion;
- cross-source semantic reconciliation;
- canonical entity infrastructure.

## 3. Architectural convergence review

### Contract convergence

Evidence is strong that materially different providers fit the current observed contract:

- BEA table/line identity fit provider indicator fields, labels, attributes, raw evidence, and release key.
- Treasury endpoint/query/pagination/record-date/categorical-row evidence fit existing fields.
- ECB SDMX query/structure/series/attribute/observation evidence fit existing fields.
- IMF dataflow/DSD/dimension/codelist/series/observation attributes fit existing fields.
- BIS dataflow/reference-area/series/observation attributes fit existing fields.

Conclusion:

- Contract convergence after source-specific normalization is strong.
- This strengthens `ObservedIngestionPackage`; it does not imply a shared pre-boundary framework.

### Algorithm convergence

Post-boundary algorithms are converged:

- validation;
- package fingerprinting;
- package comparison/replay;
- lineage/feedback where scoped.

Pre-boundary algorithms are not sufficiently converged:

- BEA table parsing differs from Treasury row JSON.
- Treasury endpoint metadata differs from BEA table metadata.
- ECB GenericData differs from IMF/BIS StructureSpecificData.
- IMF and BIS both use StructureSpecificData, but their provider identities, dataflows, attributes, and semantic meanings differ.

Conclusion:

- Algorithm convergence is strong after the observed boundary.
- Algorithm convergence is weak-to-emerging before the boundary, especially for SDMX XML mechanics.

### Implementation convergence

Implementation convergence is strong only in the repeated testing/adapter shape:

- source-specific module;
- fixture-backed parser/normalizer;
- valid `ObservedIngestionPackage` construction;
- contract validation;
- deterministic replay/fingerprint tests;
- anti-framework tests.

Actual parsing/metadata implementation remains provider-specific.

Conclusion:

- Implementation convergence justifies continuing the methodology.
- It does not justify extracting a generic source framework or SDMX layer.

## 4. Marginal implementation cost review

Relative trend from TASK-053 through TASK-057:

- Engineering effort: decreasing or stable. BEA was Medium; Treasury Low-Medium; ECB/IMF Medium due to SDMX/provider metadata; BIS Low-Medium.
- Implementation uncertainty: decreasing. Later tasks more accurately predicted no contract/substrate changes.
- Architectural surprises: decreasing / near zero. The surprise log records no material architectural surprises for TASK-053..057.
- Documentation effort: not clearly decreasing in raw volume, but becoming more useful. The reports are becoming calibration artifacts rather than one-off summaries.
- Prediction quality: improving. Later tasks explicitly predicted SDMX strengthening without extraction and were confirmed.

The important learning is not that source work is becoming trivial. It is that MacroForge now predicts where difficulty will be: before the boundary, in source semantics and fixture/scoping decisions.

## 5. Architectural surprise review

Recorded surprises:

- No material architectural surprises have been recorded for TASK-053 through TASK-057.

Classification of notable observations:

| Observation | Classification | Reason |
|---|---|---|
| BEA API-key friction led to iTableCore bounded evidence | Expected in hindsight / source acquisition friction | Did not change architecture; reinforced bounded fixture choice. |
| Treasury daily endpoint would have caused period-contract pressure, so monthly endpoint was selected | Methodology improvement | Improved source-slice selection discipline; not contract failure. |
| ECB repeated SDMX XML mechanics with OECD | Expected in prediction | Recorded as future extraction evidence; no action. |
| IMF used StructureSpecificData rather than ECB-style GenericData | Genuine refinement, not architectural surprise | Strengthened SDMX-family evidence while weakening any simplistic generic-SDMX assumption. |
| BIS public API access was straightforward and substrate work negligible | Expected simplicity | Reinforced prediction accuracy and low post-boundary effort. |

Are surprises becoming less frequent?

Yes, within the current evidence loop. This is not because sources are identical; it is because the architecture and methodology are increasingly good at predicting that provider-specific semantics dominate before the boundary.

## 6. Infrastructure extraction evidence

| Candidate | Contract convergence | Algorithm convergence | Implementation convergence | Evidence strength | Recommendation |
|---|---|---|---|---|---|
| SDMX handling | Medium. OECD/ECB/IMF/BIS all expose SDMX-family concepts, but shapes differ. | Low-Medium. GenericData and StructureSpecificData share XML mechanics, but provider interpretation diverges. | Low-Medium. Adapters share broad pattern but not enough source-neutral implementation. | Accumulating, not sufficient. | Continue observing. Begin targeted evidence gathering only if future SDMX work shows duplicated defects or a natural intermediate representation. |
| Fixture management | Medium. Every bounded source uses fixtures and hashes. | Medium. Capture/checksum/replay patterns recur. | Medium. Actual fixture paths and source rules differ. | Moderate. | Continue observing; extraction investigation may become reasonable if fixture capture/checking becomes repeated operational pain. |
| Metadata preservation | High after boundary; low-medium before boundary. | Low-medium. Preservation destination is converged; interpretation is provider-specific. | Medium. All adapters use `attributes`, `raw_evidence`, and `source_payload`, but provider metadata structures vary. | Strong for contract, weak for provider framework. | Continue current pattern; do not create provider metadata framework. |
| Validation utilities | High. Contract validation works across all reviewed sources. | High post-boundary. | High post-boundary. | Strong, already part of substrate. | Continue using; no new extraction needed. |
| Parsing helpers | Low-medium. XML/JSON/table parsing repeats only at a superficial level. | Low. Algorithms vary by provider shape. | Low. Shared helpers would likely create source conditionals. | Weak. | Avoid generic parsing layer for now. |
| Source registry / plugin system | Low. Source-specific modules are sufficient. | Low. No repeated orchestration problem. | Low. No evidence of registry pain. | Weak. | Avoid. |
| Pagination/query provenance helpers | Medium for JSON/API sources; not broad. | Low-medium. Treasury showed bounded pagination metadata; other sources differ. | Low. | Weak-to-moderate. | Continue observing. |
| Canonical entity layer | Low for current bounded evidence-only slices. | Low. | Low. | Insufficient. | Avoid until repeated approved mapping/canonicalization work satisfies the extraction gate. |
| Revision/vintage handling | Not tested. | Not tested. | Not tested. | None. | Monitor only; do not design yet. |

No candidate satisfies the full extraction doctrine:

1. contract convergence;
2. algorithm convergence;
3. implementation convergence;
4. deterministic verification;
5. acceptable coupling;
6. measurable future effort reduction.

## 7. Architectural maturity assessment

| Capability | Maturity | Evidence |
|---|---|---|
| `ObservedIngestionPackage` | Stable for current heterogeneous bounded-source scope | WDI/OECD/Eurostat plus BEA, Treasury, ECB, IMF, and BIS all fit; no recent contract evolution. |
| Deterministic substrate | Stable | TASK-053..057 required no redesign; validation/replay/fingerprinting repeatedly worked unchanged. |
| Source-specific ingestion methodology | Stable | Repeated source-specific adapters kept provider semantics before the boundary and avoided framework drift. |
| SDMX-family understanding | Emerging | OECD/ECB/IMF/BIS evidence now distinguishes protocol recurrence from actionable extraction convergence. |
| Fixture methodology | Emerging to stable | Fixture-backed bounded slices with hashes/fingerprints are now routine, but fixture capture management itself is not yet extracted infrastructure. |
| Lineage | Stable for current scoped behavior | No reviewed source forced lineage changes; evidence is supportive but less directly stressed than validation/fingerprinting. |
| Validation | Stable | Contract validation passed across all recent heterogeneous sources. |
| Architectural prediction methodology | Emerging to stable | Prediction quality has been Accurate or Mostly Accurate in recent tasks; confidence ledger is now useful for restraint. |
| Implementation methodology | Stable | Prediction -> implementation -> verification -> lessons -> confidence update -> future selection is producing better judgment and fewer surprises. |
| Canonical loading | Stable only where scoped; emerging overall | WDI/OECD/Eurostat are canonical-loaded paths; BEA/Treasury/ECB/IMF/BIS are intentionally evidence-only, so broad canonical loading is not mature. |
| Company ingestion | Experimental / not implemented | No company evidence in current implementation base. |
| Trade ingestion | Experimental / not implemented | No trade evidence in current implementation base. |
| Revision/vintage handling | Experimental / not implemented | No ALFRED/FRED-style vintage implementation evidence yet. |

## 8. Methodology review

The current sequence is working:

```text
Prediction
-> Implementation
-> Verification
-> Lessons
-> Confidence update
-> Future source selection
```

Evidence that it is improving architectural understanding:

- TASK-053 established the post-boundary stability expectation after BEA.
- TASK-054 confirmed that source-slice selection matters and prevented unnecessary period-contract pressure.
- TASK-055 converted SDMX from vague similarity into a hypothesis with strengthen/weaken/falsify criteria.
- TASK-056 refined SDMX understanding by showing IMF StructureSpecificData both increases recurrence and weakens simplistic generic-layer assumptions.
- TASK-057 confirmed that even a fourth SDMX-family provider does not automatically satisfy extraction gates.

Weaknesses:

- Documentation volume is rising. The value is currently justified because it improves prediction quality, but future retrospectives should watch whether documentation becomes ritual rather than decision-relevant evidence.
- Some older baseline sources such as OECD were implemented before the current prediction-ledger format, so comparison with newer tasks is less precise.
- Effort estimates remain qualitative. That is acceptable now, but if future decisions hinge on marginal cost, a lightweight comparable effort metric may become useful.

Conclusion:

- The methodology is converging.
- It should remain frozen unless repeated evidence shows it is producing prediction theater rather than prediction improvement.

## 9. Recommendations

### Continue

- Continue source-specific-first implementation.
  - Evidence: BEA, Treasury, ECB, IMF, and BIS all concentrated real uncertainty before `ObservedIngestionPackage`.

- Continue using `ObservedIngestionPackage` as the handoff boundary.
  - Evidence: five recent heterogeneous slices plus OECD fit without contract evolution.

- Continue deterministic post-boundary validation, replay, fingerprinting, and lineage mechanics unchanged.
  - Evidence: repeated tests and implementation lessons show no substrate redesign was needed.

- Continue prediction ledgers and post-implementation calibration.
  - Evidence: recent predictions were accurate enough to prevent premature SDMX extraction and improve candidate selection.

- Continue recording SDMX as a watched extraction candidate.
  - Evidence: OECD/ECB/IMF/BIS show repeated SDMX-family concepts, but not enough source-neutral convergence.

### Monitor

- Monitor SDMX-family duplication.
  - Evidence: SDMX recurrence is now real across four providers; watch for duplicated defects, natural intermediate representation, or converged algorithmic parsing.

- Monitor fixture-management effort.
  - Evidence: fixtures, hashes, and deterministic replay are recurring, but fixture handling has not yet become a major pain center.

- Monitor canonical-loading pressure.
  - Evidence: WDI/OECD/Eurostat are canonical-loaded; recent bounded sources are intentionally evidence-only. The architecture has not yet learned how BEA/Treasury/ECB/IMF/BIS should enter canonical loading.

- Monitor documentation overhead.
  - Evidence: documentation currently improves prediction quality, but volume is increasing.

- Monitor revision/vintage semantics.
  - Evidence: not yet tested; likely to stress observation identity more than recent sources.

### Avoid

- Avoid generic SDMX extraction now.
  - Evidence: ECB GenericData, IMF StructureSpecificData, and BIS StructureSpecificData share concepts but still require provider-specific interpretation.

- Avoid provider metadata framework extraction now.
  - Evidence: BEA table metadata, Treasury endpoint metadata, ECB SDMX structure metadata, IMF DSD/codelists, and BIS attributes preserve well through existing fields but do not share one algorithm.

- Avoid source registry/plugin infrastructure.
  - Evidence: no reviewed implementation showed orchestration or registry pain; source-specific modules remained clearer.

- Avoid canonical entity infrastructure from this evidence alone.
  - Evidence: DEC-023 allows future emergence but current implementations do not show contract/algorithm/implementation convergence for entity infrastructure.

- Avoid broad provider support when a bounded slice produces enough evidence.
  - Evidence: BEA, Treasury, ECB, IMF, and BIS each delivered architectural learning without broad support.

## Baseline answer: what MacroForge objectively learned

MacroForge did not merely learn that several sources can be implemented.

It learned that:

1. The observed boundary is probably correctly placed.
2. Deterministic post-boundary mechanics are more stable than previously proven.
3. Provider interpretation is the dominant source of implementation uncertainty.
4. Repeated vocabulary is not enough for extraction; SDMX demonstrates this clearly.
5. The system can now predict, before implementation, that most bounded heterogeneous sources will stress pre-boundary interpretation rather than post-boundary architecture.
6. The methodology itself is becoming a reusable architectural asset because it improves prediction accuracy and prevents premature abstractions.

Future retrospectives should compare against this baseline by asking:

- Did any new source require observed-package evolution?
- Did any new source require deterministic-substrate evolution?
- Did any extraction candidate move from vocabulary recurrence to contract / algorithm / implementation convergence?
- Did prediction quality remain Accurate / Mostly Accurate?
- Did documentation and methodology continue to reduce future engineering, human, or LLM effort?

Until those answers change, MacroForge should preserve the current architecture and continue evidence-driven, source-specific heterogeneous implementation.