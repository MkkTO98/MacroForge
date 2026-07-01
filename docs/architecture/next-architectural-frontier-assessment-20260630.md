# Next Architectural Frontier Assessment — 2026-06-30

Status: architectural planning assessment
Scope: source-family selection only; no provider selected; no implementation authorized
Inputs: Strategic Constitution v1.1, DEC-022, DEC-023, five-source architectural retrospective, architecture state, confidence ledger, marginal source cost index, recurring implementation pain

## Executive answer

The next fundamentally different architectural question MacroForge should test is:

```text
Can MacroForge represent revision-aware / vintage-aware statistical observations without muddying observation identity, lineage, replay, validation, or the MacroForge / KnowledgeForge boundary?
```

Recommended next architectural frontier source family:

```text
Revision-aware statistical releases.
```

This is not a provider recommendation and not an implementation task. It identifies the next source family that would create the highest new architectural evidence after the five-source retrospective.

Why this follows from the retrospective:

- The retrospective showed `ObservedIngestionPackage` and deterministic post-boundary substrate are now stable across materially different current-period source shapes.
- It also explicitly identified revision/vintage handling as not tested.
- SDMX has already been stressed across OECD, ECB, IMF, and BIS; another SDMX-family provider would mostly reinforce known evidence unless it introduces a fundamentally different revision/vintage problem.
- Revision-aware sources would stress assumptions that recent sources mostly left untouched: observation identity over time, release/as-of semantics, historical replay, lineage event semantics, fingerprint comparison, and validation of changed values for the same economic period.

Decision:

```text
Highest architectural frontier: revision-aware statistical releases.
Not recommended as highest frontier now: another plain SDMX provider.
No extraction justified by this assessment.
No architecture redesign recommended.
```

## 1. Current architectural evidence map

| Architectural assumption | Evidence strength | Implementation evidence |
|---|---|---|
| `ObservedIngestionPackage` is correctly placed after source-specific acquisition/normalization | Very Strong | OECD, BEA, Treasury, ECB, IMF, and BIS all fit the observed contract without contract evolution. The confidence ledger records 91% confidence after TASK-057. |
| Deterministic post-boundary substrate is stable for current heterogeneous bounded sources | Strong | TASK-053 through TASK-057 required no redesign to validation, package fingerprinting/comparison, replay, lineage, or feedback. Retrospective classified the substrate as stable/strengthening. |
| Source-specific acquisition remains preferable by default | Strong | BEA table/line evidence, Treasury row JSON, ECB GenericData, IMF StructureSpecificData, and BIS StructureSpecificData each required source-specific parsing and provider interpretation. |
| Most implementation effort currently lies before the observed boundary | Strong | Retrospective and cost index show BEA, Treasury, ECB, IMF, and BIS effort concentrated in acquisition, source semantics, period handling, metadata preservation, and fixture/scoping decisions. |
| Provider metadata interpretation should remain source-specific | Strong | BEA table metadata, Treasury endpoint metadata, ECB exchange-rate dimensions, IMF DSD/codelists, and BIS policy-rate attributes preserve through common fields but do not share one algorithm. Confidence ledger records 85%. |
| SDMX is an acquisition/protocol family, not yet a MacroForge architectural boundary | Strong | OECD/ECB/IMF/BIS show repeated SDMX concepts, but GenericData vs StructureSpecificData and provider-specific semantics prevent contract/algorithm/implementation convergence. Confidence ledger records 82%. |
| Validation methodology is stable for bounded observed packages | Very Strong | Every reviewed bounded slice used contract validation successfully; no source-specific post-boundary validation branches were needed. |
| Replay/fingerprinting methodology is stable for bounded observed packages | Strong | ECB, IMF, and BIS explicitly recorded deterministic fingerprints / package comparison working unchanged; TASK-053..057 did not require replay redesign. |
| Prediction-ledger methodology improves implementation judgment | Strong | TASK-053..057 prediction quality was Accurate or Mostly Accurate; the retrospective found no recurring prediction failures and showed that predictions prevented premature SDMX extraction. |
| Canonical loading beyond WDI/OECD/Eurostat is stable | Weak | WDI/OECD/Eurostat are scoped canonical-loaded paths, but BEA/Treasury/ECB/IMF/BIS intentionally remained evidence-only. Retrospective classifies broad canonical loading as uncertain. |
| Revision/vintage observation semantics are understood | Weak | Retrospective explicitly says revision/vintage handling is not tested and experimental; confidence ledger lists ALFRED/FRED-style vintage semantics as a future falsification test. |
| Trade/product/partner-country observation semantics are understood | Weak | No trade evidence exists. DEC-023 permits future trade observation scope but does not authorize source priority or entity/classification infrastructure. |
| Company ingestion semantics are understood | Weak | No company evidence exists. DEC-023 keeps claims, strategy, management discussion, semantic identity, and confidence-bearing knowledge outside MacroForge / inside KnowledgeForge where appropriate. |

Summary:

MacroForge has substantially validated the current observed boundary, deterministic substrate, source-specific-first posture, and prediction methodology for current-period numeric observations. The highest remaining uncertainty is not another provider protocol; it is time-versioned observational truth.

## 2. Remaining architectural uncertainty

### A. Revision / vintage / as-of semantics

Current status: untested.

Architectural questions MacroForge cannot yet answer confidently:

- Is an observation identified only by provider, indicator, territory, period, and source slice, or must vintage/as-of/release instance participate in identity?
- Can revisions be represented as repeated observed values with release/as-of evidence, or do they require an additive contract concept?
- Can deterministic replay compare two packages when value changes are expected revisions rather than drift?
- Can lineage distinguish first publication, revision, benchmark revision, and later correction without embedding economic interpretation?
- Can MacroForge preserve revision evidence while leaving interpretation of why revisions matter to KnowledgeForge?

Why this matters architecturally:

Recent sources tested static or current bounded snapshots. They did not test the same economic period appearing with multiple source-backed values over publication time.

### B. Trade classifications and partner-country observations

Current status: untested.

Questions:

- Can observations with reporter country, partner country, product classification, direction, value, and volume fit without forcing premature canonical entity/classification infrastructure?
- Does `ObservedIngestionPackage` remain a good boundary when observation identity has multiple source dimensions beyond territory/period/indicator?
- Can classification hierarchy evidence remain provider/source-specific before a future approved canonical classification layer?

Risk:

Trade may quickly tempt canonical entity, product hierarchy, and relationship modeling. DEC-023 allows trade as future observation scope but does not authorize entity infrastructure.

### C. Bulk-file ingestion

Current status: weakly tested at fixture scale, not as an acquisition family.

Questions:

- Do large file downloads, archives, compression, checksums, and partial extraction create new acquisition/reproducibility mechanics?
- Is fixture methodology sufficient for bulk files, or does evidence capture become operationally painful?

Architectural novelty:

Primarily acquisition and fixture-management stress. It may not stress observation semantics as much as vintage or trade.

### D. Company filings

Current status: untested.

Questions:

- Can MacroForge restrict itself to source-backed observable quantitative facts from filings without drifting into KnowledgeForge's semantic/claim territory?
- Can semi-structured filing facts be bounded without designing company identity, segment, ownership, or textual claim infrastructure?

Risk:

Very high boundary risk. Company filings are architecturally valuable eventually, but they are more likely to broaden scope than to cleanly test one current assumption.

### E. Supply-use / input-output tables

Current status: untested.

Questions:

- Can matrix-like observations with industries, products, flows, use/supply axes, and valuation concepts fit the observed boundary?
- Does this stress classification and dimensional identity more than current series-oriented observations?

Architectural novelty:

High. But it overlaps with classification/entity uncertainty and may be less bounded than revision-aware statistical releases.

### F. Classification systems

Current status: untested as first-class sources.

Questions:

- Are official classifications observations, metadata, or future canonical/domain reference evidence?
- Can MacroForge ingest classification evidence without creating canonical entity infrastructure?

Risk:

High chance of infrastructure temptation. Useful later when multiple observational sources already require the same classification evidence.

### G. Financial market reference data

Current status: untested.

Questions:

- Can instrument/security identifiers, trading calendars, corporate actions, and market data quality fit MacroForge's observation scope?
- Does this blur MacroForge into security-master / investment-data infrastructure too early?

Risk:

High scope and licensing risk. Not the cleanest next architectural stressor.

## 3. Source family analysis

| Source family | New assumptions stressed | Assumptions left mostly untouched | Expected architectural learning | Boundedness | Risk | Overlap with existing evidence |
|---|---|---|---|---|---|---|
| Revision-aware statistical releases | Observation identity over release time; vintage/as-of semantics; expected value changes; replay/fingerprint interpretation; lineage event semantics | Most acquisition/parsing may remain familiar; no need for trade/company entity infrastructure | Highest: directly tests an explicitly untested weakness from retrospective and confidence ledger | High if scoped to one indicator, few periods, few vintages/releases | Medium | Low semantic overlap with current static snapshots; strong methodological continuity |
| International trade | Multi-party observations; reporter/partner/product/direction dimensions; classification hierarchy; value vs volume | Revision semantics; publication-vintage behavior | High: tests multidimensional identity and classification pressure | Medium if one reporter, partner, product, year/month | Medium-High | Moderate overlap in country/period/numeric observations, low overlap in product/partner hierarchy |
| Bulk statistical files | Large-file acquisition, checksum/archive capture, fixture management, streaming/partial parsing | Deep observation identity; vintage semantics; classification semantics | Medium: tests acquisition/reproducibility and fixture scaling | Medium | Medium | Moderate; fixtures/hashes already exist but not at bulk scale |
| Company filings | Semi-structured facts; filing events; company identity; segment facts; possible textual evidence boundary | Existing statistical-series assumptions | High but too broad: tests many boundaries at once | Low-Medium | High | Low overlap; high KnowledgeForge boundary risk |
| Supply-use / input-output tables | Matrix observations; industry/product classifications; flow axes; valuation concepts | Revision/as-of semantics unless source has vintages | High: tests dimensional cube/matrix representation | Medium-Low | High | Some overlap with national accounts; little with current observed identity |
| Classification systems | Source-backed code lists, hierarchy versions, validity periods | Numeric observation handling; replay of values | Medium: tests whether classification evidence is observation, metadata, or reference evidence | Medium | Medium-High | Some overlap with SDMX codelists, but little direct observation evidence |
| Energy statistics | Commodity/unit/flow/balance semantics; possibly stock/flow transformations | Revision semantics unless source is vintage-aware; company/filing boundary | Medium | Medium-High | Medium | Could resemble existing macro series if selected narrowly; less novel than vintage or trade |
| Financial flows / balance-of-payments style sources | Cross-border flow concepts, asset/liability direction, instrument/category dimensions | Revision semantics unless explicitly vintage-aware | Medium-High | Medium | Medium | May be SDMX-adjacent and overlap with IMF-style evidence; architectural novelty depends on source shape |
| Financial market reference data | Instruments, calendars, prices/yields, identifiers, possibly corporate actions | Official statistical-source posture | Medium-High but scope risky | Medium-Low | High | Low overlap, but may broaden MacroForge too early |

Assessment:

- Trade and input-output are architecturally important, but they mostly stress high-dimensional identity and classification/entity pressure.
- Company filings are too boundary-risky as the immediate next frontier.
- Bulk files stress acquisition mechanics but may not test the most important unvalidated architectural belief.
- Another SDMX provider mostly reinforces the already observed SDMX conclusion unless it also introduces revision/vintage behavior.
- Revision-aware statistical releases test the cleanest, highest-value unvalidated assumption: whether observed identity and deterministic replay still work when values change over publication time.

## 4. Architectural frontier recommendation

Recommended source family:

```text
Revision-aware statistical releases.
```

### Why this follows naturally from the retrospective

The retrospective concluded that MacroForge's current architecture is stable across different current-period provider shapes. It also named revision/vintage handling as experimental and untested.

The next frontier should therefore not be another source that mainly varies provider protocol. It should test whether the current architecture handles a different kind of observational truth:

```text
the same economic period observed at multiple publication/vintage times.
```

This is the first major unresolved question that could plausibly challenge current beliefs without requiring a redesign in advance.

### Why it has greater architectural value than another SDMX implementation

Another plain SDMX implementation would mostly test:

- source-specific acquisition/parsing;
- SDMX-family repetition;
- metadata preservation;
- continued lack of generic SDMX extraction.

Those beliefs are already Strong. OECD/ECB/IMF/BIS have produced enough evidence to say SDMX is worth monitoring but not extracting.

Revision-aware statistical releases would test beliefs that are currently Weak:

- whether observation identity needs vintage/as-of participation;
- whether replay/fingerprints distinguish expected source revisions from unexpected drift;
- whether lineage semantics can remain deterministic and observation-facing;
- whether release/as-of metadata is sufficient in existing fields or requires additive contract evolution;
- whether KnowledgeForge boundary remains clean when interpreting revisions.

### Expected new evidence

A bounded revision-aware source-family experiment should generate evidence about:

- first-publication vs revised observations;
- multiple values for the same provider/indicator/territory/economic period;
- source release timestamps or vintage dates;
- deterministic package comparisons across vintages;
- whether revision events are source observations or higher-level knowledge claims;
- whether `release_key`, `source_payload`, `raw_evidence`, and lineage metadata are sufficient.

### Current architectural beliefs it will strengthen or challenge

Likely strengthened if successful without contract/substrate evolution:

- `ObservedIngestionPackage` boundary is correctly placed.
- Deterministic substrate remains stable under temporal revision pressure.
- Most implementation effort remains pre-boundary.
- Source-specific interpretation remains preferable.

Likely challenged if implementation requires additive evolution:

- observation identity may need explicit vintage/as-of semantics;
- fingerprint/replay may need revision-aware comparison semantics;
- lineage may need first-publication/revision event distinctions;
- validation may need rules distinguishing expected revisions from source drift.

### Expected implementation patterns, without designing the implementation

The family is expected to introduce patterns around:

- bounded vintage selection;
- release/as-of evidence preservation;
- repeated observation keys with different vintage/release evidence;
- source-specific revision metadata interpretation;
- deterministic comparison of multiple source-backed packages over publication time.

No new infrastructure should be designed before the bounded implementation evidence exists.

## 5. Architectural belief register

This is the first formal belief register distilled from the retrospective. It does not replace the confidence ledger; it translates implementation evidence into falsifiable qualitative beliefs.

| Belief | Supporting evidence | Confidence | Strengthening evidence | Weakening / falsifying evidence |
|---|---|---|---|---|
| Source-specific acquisition remains preferable for new source families. | BEA, Treasury, ECB, IMF, and BIS each required source-specific acquisition/parsing/provider interpretation. | High | A revision-aware or trade source remains clear and bounded as a source-specific adapter. | Multiple future adapters differ only by endpoint constants or duplicate identical algorithms with maintenance defects. |
| Most implementation effort remains before `ObservedIngestionPackage`. | TASK-053..057 effort centered on acquisition, provider semantics, metadata, period handling, and source-slice choice; substrate effort was low/very low. | High | A revision-aware source concentrates effort in vintage metadata interpretation before the boundary. | A source's main effort shifts to post-boundary validation, lineage, replay, or contract evolution. |
| `ObservedIngestionPackage` is correctly placed for bounded numeric observations. | OECD, BEA, Treasury, ECB, IMF, and BIS all fit without contract evolution. | Very High for current scope | Revision-aware observations fit without muddying identity or lossy encoding. | Repeated sources require lossy encoding, new fields, or source-specific post-boundary branches. |
| Deterministic post-boundary substrate is stable for current bounded source shapes. | TASK-053..057 required no substrate redesign; validation/replay/fingerprinting worked unchanged. | High | Revision-aware comparison and lineage work unchanged or with source-specific pre-boundary handling only. | Expected revisions break replay/fingerprint/validation semantics in repeated ways. |
| Shared SDMX infrastructure is premature. | OECD/ECB/IMF/BIS show repeated SDMX concepts but insufficient algorithm/implementation convergence. | High | Further SDMX evidence still requires provider-specific interpretation and no duplicated defects. | Multiple SDMX implementations naturally converge on the same intermediate representation and duplicated maintenance pain appears. |
| Provider metadata framework extraction is premature. | Metadata preservation converges after the boundary, but BEA/Treasury/ECB/IMF/BIS interpretation algorithms differ. | High | Revision metadata remains source-specific and preservable through current fields. | Several providers require identical release/vintage metadata handling with repeated defects or high effort. |
| Prediction-ledger methodology improves architectural judgment. | Recent predictions were Accurate/Mostly Accurate and prevented premature extraction. | High | Next frontier predictions cleanly classify whether revision handling stresses boundary/substrate. | Prediction ledgers become vague, unclassified, or fail to influence source-family choice. |
| Canonical loading should not be generalized from current evidence-only slices. | WDI/OECD/Eurostat are scoped canonical-loaded paths; BEA/Treasury/ECB/IMF/BIS remained evidence-only. | Moderate-High | Future evidence-only frontier reveals identity issues before canonical loading is attempted. | Multiple evidence-only sources show canonical loading would be identical and low-risk but is delayed without reason. |
| Revision/vintage handling is a major untested architectural uncertainty. | Retrospective classifies it as experimental/not implemented; confidence ledger names ALFRED/FRED-style vintage semantics as a future test. | High as an uncertainty, Low as a solved capability | A bounded revision-aware source clarifies observation identity and replay/lineage semantics. | If a bounded vintage source behaves like ordinary snapshots and produces no new identity/replay pressure. |
| Trade/product/entity infrastructure should not be introduced from vision alone. | DEC-023 allows long-term trade/company/entity scope only as non-binding vision and rejects infrastructure authorization. | High | Trade implementation, when eventually attempted, preserves source-specific classification evidence without entity infrastructure. | Repeated trade/classification implementations demonstrate contract/algorithm/implementation convergence and measurable effort reduction from shared infrastructure. |

## 6. Methodology evolution

Question:

Should MacroForge explicitly distinguish between:

- implementation evidence;
- architectural beliefs;
- architectural confidence?

Assessment:

Yes, but only as a lightweight documentation distinction, not as a new process stage or infrastructure system.

Reasoning from observed experience:

- Implementation evidence is concrete: TASK-053 produced 252 BEA observations; TASK-054 produced 16 Treasury observations; TASK-055/056/057 preserved SDMX evidence without contract evolution.
- Architectural beliefs are falsifiable interpretations of that evidence: e.g., most effort is pre-boundary, SDMX extraction is premature, observed boundary is correctly placed.
- Architectural confidence is the qualitative/ledger estimate attached to those beliefs: e.g., observed boundary 91%, substrate 86%, SDMX protocol-level 82%.

The five-source retrospective already implicitly used all three. Making the distinction explicit would improve future retrospectives because it prevents three common errors:

1. treating completed implementation as proof of a broad belief;
2. treating a belief as if it were direct evidence;
3. treating confidence values as statistical facts rather than disciplined engineering estimates.

Recommended adoption:

```text
Adopt the distinction in future retrospective and planning documents as terminology only.
Do not create a new artifact type, process gate, schema, or infrastructure layer yet.
```

Suggested lightweight usage:

- Implementation evidence: what happened in code/tests/artifacts.
- Architectural belief: what MacroForge currently thinks because of that evidence.
- Architectural confidence: how strongly MacroForge should rely on that belief, and what would falsify it.

This is justified because the retrospective showed documentation is becoming decision-relevant, but also warned that documentation volume is rising. A terminology distinction improves precision without adding a new workflow.

## Final recommendation

After everything MacroForge has learned so far, the next fundamentally different architectural question should be:

```text
Can the current observed-boundary and deterministic-substrate architecture handle revision-aware statistical observations, where the same economic period can have multiple source-backed values across publication/vintage time?
```

The next architectural frontier source family should therefore be:

```text
Revision-aware statistical releases.
```

This recommendation is architectural, not domain-preference-based. It follows directly from the evidence:

- current-period heterogeneous sources have already strongly validated the observed boundary;
- SDMX has been tested enough to monitor rather than repeat immediately;
- revision/vintage behavior is explicitly untested;
- vintage semantics are likely to stress observation identity, lineage, replay, validation, and MacroForge/KnowledgeForge separation without requiring speculative design first.

No implementation, provider selection, task creation, extraction, or redesign is authorized by this assessment.