# Revision-Semantics Architectural Assessment — 2026-06-30

Status: architectural analysis
Scope: revision semantics only; provider-neutral; no implementation authorized
Inputs: Strategic Constitution v1.1, DEC-022, DEC-023, current architecture state, five-source architectural retrospective, next architectural frontier assessment, `ObservedIngestionPackage` v1 contract, architectural confidence ledger

## Executive answer

The smallest high-evidence revision-aware experiment should test this behavior:

```text
The same provider-backed economic period is published in one release/vintage and later republished with a changed numeric value under a later release/vintage, while provider, dataset, indicator, territory, unit, frequency, and economic period remain stable.
```

The revision semantics to test first are:

```text
ordinary release-vintage revisions for a small current-period statistical series.
```

This should be preferred over benchmark revisions, rebasing, methodological revisions, seasonal-adjustment revisions, or publication corrections as the first revision experiment because it isolates the central architectural question:

```text
Does publication-time identity belong in source evidence / release evidence, or does it require contract/substrate evolution?
```

The first experiment should not try to test every revision behavior. It should deliberately exclude broad benchmark, methodology, rebase, and classification changes unless the provider exposes them as unavoidable metadata for the selected bounded slice.

No provider is selected here. No implementation task is created. No redesign or extraction is recommended.

## Architecture baseline used for this assessment

Current MacroForge architecture is:

```text
Source-specific acquisition
-> Source-specific normalization
-> ObservedIngestionPackage v1
-> Deterministic post-boundary substrate
-> Existing source-specific staging/canonical load SQL where scoped
-> Validation
-> Canonical PostgreSQL where scoped
```

Accepted evidence from the retrospective and frontier assessment:

- `ObservedIngestionPackage` is very strongly supported for current bounded numeric observations.
- Deterministic post-boundary substrate is stable for current heterogeneous source shapes.
- Source-specific acquisition and provider interpretation remain the correct default.
- Revision/vintage behavior is not yet tested.
- DEC-022 says the current post-boundary architecture remains assumed correct unless repeated implementation evidence falsifies it.
- DEC-023 says MacroForge owns source-backed observations, provenance, reproducibility, lineage, validation, and observational identity; KnowledgeForge owns reusable meaning, claims, causal interpretation, confidence, contradictions, and epistemic state.

The revision experiment should therefore try to falsify the current boundary without redesigning it first.

# 1. Revision taxonomy

## 1.1 Release vintages / realtime releases

Definition:

A provider publishes the same economic concept and period at multiple publication dates or vintages. The value may or may not change across vintages.

What changes:

- publication/vintage date;
- release instance;
- sometimes the numeric value;
- sometimes source status flags or notes;
- sometimes source payload metadata.

What remains stable:

- provider;
- dataset / series identity;
- economic period being measured;
- indicator concept as represented by provider;
- territory and frequency;
- usually unit and seasonal-adjustment status.

Architectural assumptions stressed:

- whether publication/vintage is part of observation identity or release/provenance identity;
- whether `release_key`, `raw_evidence`, `input_filters`, `attributes`, and `source_payload` can preserve vintage evidence;
- whether replay/fingerprinting can treat changed values as expected source-backed revisions rather than drift;
- whether lineage can preserve first-publication vs later-vintage evidence without interpreting economic meaning.

Assessment:

This is the best first revision semantics target because it isolates revision behavior while keeping provider/indicator/period stable.

## 1.2 Rolling revisions

Definition:

A provider regularly revises recent periods as more complete data arrives, often according to a known rolling window.

What changes:

- recent historical values;
- sometimes observation statuses;
- sometimes preliminary/final flags;
- later releases may revise several adjacent periods at once.

What remains stable:

- provider, dataset, indicator, territory, unit, frequency;
- observation periods;
- publication cadence or update window may be stable.

Architectural assumptions stressed:

- repeated expected value changes for multiple periods;
- deterministic comparison across release packages;
- lineage representation of a revision sequence;
- validation rules that distinguish expected source revisions from unexpected nondeterminism.

Assessment:

Architecturally valuable, but slightly broader than a minimal first experiment because it may revise many periods and introduce policy about revision windows.

## 1.3 Benchmark revisions

Definition:

A provider periodically revises long historical spans after incorporating more comprehensive source data, censuses, surveys, annual accounts, or major reconciliation exercises.

What changes:

- many historical values;
- sometimes levels, growth rates, and derived components;
- sometimes base years, classification references, or historical source methods;
- release metadata and explanatory notes are often material.

What remains stable:

- broad provider dataset identity;
- many provider series identifiers may remain stable;
- economic periods and territory codes usually remain stable;
- provider may explicitly label the benchmark event.

Architectural assumptions stressed:

- large-scale expected value changes across historical periods;
- release identity and lineage event semantics;
- whether a benchmark is source evidence or a higher-level event object;
- whether canonical observations need benchmark-release awareness;
- MacroForge/KnowledgeForge boundary, because explaining economic meaning of benchmark changes belongs to KnowledgeForge.

Assessment:

High evidence, but too much for the first revision experiment. Benchmark revisions mix revision identity with event classification and methodological interpretation.

## 1.4 Methodological revisions

Definition:

A provider changes the statistical method used to produce a series, potentially changing historical values and metadata.

What changes:

- value calculation method;
- historical values;
- source notes, concepts, attributes;
- sometimes provider indicator definitions or series breaks.

What remains stable:

- provider and sometimes series code;
- economic period labels;
- broad economic concept may remain similar but not necessarily identical.

Architectural assumptions stressed:

- source indicator identity stability;
- whether methodology metadata belongs in provider attributes/source payload or requires first-class representation;
- KnowledgeForge boundary, because interpreting methodology impact is semantic/evaluative;
- canonical mapping status if a provider series code remains stable but meaning changes.

Assessment:

Important later. Not first because it conflates revision semantics with concept-definition drift.

## 1.5 Rebasing / reference-year changes

Definition:

A provider changes the reference year/base period for index or real-value series.

What changes:

- numeric values for index-level series;
- base-year/reference-period metadata;
- sometimes units or scale;
- potentially series comparability across vintages.

What remains stable:

- provider and dataset;
- underlying economic phenomenon;
- economic periods;
- territory and frequency.

Architectural assumptions stressed:

- unit/reference-period identity;
- whether a rebase is a revision to a value or a new provider indicator/unit identity;
- validation/fingerprint behavior when many values shift mechanically;
- boundary between source-observed values and KnowledgeForge interpretation of comparability.

Assessment:

Not a first target. It stresses unit/reference-period semantics more than pure revision identity.

## 1.6 Seasonal-adjustment revisions

Definition:

Seasonally adjusted values change as models are re-estimated or as new observations arrive.

What changes:

- seasonally adjusted values;
- sometimes adjustment factors;
- recent and sometimes historical periods;
- possible provider attributes related to seasonal adjustment.

What remains stable:

- unadjusted economic period identity;
- provider, dataset, territory, frequency;
- seasonal-adjustment flag or series code may remain stable.

Architectural assumptions stressed:

- whether seasonal-adjustment status is sufficiently preserved as provider indicator/unit/attributes;
- repeated expected revisions without provider concept changes;
- lineage and replay over model-driven value changes;
- KnowledgeForge boundary around interpreting why adjusted values changed.

Assessment:

A useful later revision subtype. It is acceptable only if the selected minimal experiment keeps adjustment metadata stable and does not require interpreting adjustment methodology.

## 1.7 Publication corrections / errata

Definition:

A provider corrects an error in a release or observation after publication.

What changes:

- corrected values or metadata;
- publication notes / correction notices;
- sometimes release status.

What remains stable:

- provider, dataset, economic period, concept, territory, frequency;
- the original release may remain historically accessible or may be overwritten.

Architectural assumptions stressed:

- preservation of superseded source evidence;
- lineage event distinction between ordinary revision and correction;
- replay reproducibility if original erroneous values are no longer accessible;
- KnowledgeForge boundary if classifying quality/error meaning.

Assessment:

High pressure but poor first target unless the provider exposes both before and after states reproducibly. Corrections may be sporadic and hard to bound deterministically.

## 1.8 Preliminary / final status transitions

Definition:

An observation is first released as preliminary/advance/provisional and later as revised/final.

What changes:

- value;
- status flag;
- release instance/vintage;
- sometimes confidence/quality notes from provider.

What remains stable:

- provider, dataset, indicator, territory, unit, frequency, economic period.

Architectural assumptions stressed:

- observation status representation;
- source attributes and status codes;
- whether finality belongs in `observation_status`, `attributes`, release evidence, or canonical semantics;
- lineage sequence of source statuses.

Assessment:

Strong first-experiment candidate if available as part of ordinary release-vintage data. It should be treated as provider evidence, not KnowledgeForge confidence.

## 1.9 Classification revisions

Definition:

The classification scheme used by a provider changes, such as industry, product, geography, sector, or instrument codes.

What changes:

- category/code definitions;
- mapping of observations to categories;
- historical comparability;
- sometimes series identifiers.

What remains stable:

- provider and broad domain;
- some economic periods and measures;
- possibly high-level aggregates.

Architectural assumptions stressed:

- source classification identity;
- canonical mapping posture;
- entity/classification infrastructure temptation;
- KnowledgeForge boundary around semantic equivalence and mapping confidence.

Assessment:

Architecturally important but not appropriate for the first revision experiment. It tests classification/entity uncertainty more than pure revision/vintage behavior.

# 2. Architectural pressure analysis

## Pressure scale

- Low: current architecture likely handles it as source evidence with little new stress.
- Medium: stresses existing fields/behavior but likely remains source-specific/pre-boundary.
- High: may reveal contract/substrate ambiguity or require careful boundary discipline.
- Very High: likely mixes multiple architectural unknowns and should not be the first test unless unavoidable.

| Revision category | Observation identity | Provider identity | Release identity | Lineage | Replay | Deterministic validation | Fingerprinting | Provenance | Canonical observation representation | MacroForge / KnowledgeForge boundary |
|---|---|---|---|---|---|---|---|---|---|---|
| Release vintages / realtime releases | High: same period can have multiple source-backed values. | Low: provider stays stable. | High: release/vintage is the main variable. | High: first vs later publication matters as source event evidence. | High: changed values are expected across vintages. | Medium: package validity remains deterministic, but changed values must not be misread as parser drift. | High: package fingerprints should differ deterministically across vintages. | High: vintage URLs/checksums/as-of metadata are essential. | Medium-High: question is whether vintage remains release/provenance evidence or enters canonical identity. | Medium: MacroForge stores observed vintages; KnowledgeForge interprets economic significance. |
| Rolling revisions | High: multiple periods may change over a rolling window. | Low. | High. | High: revision sequence matters. | High. | Medium-High: expected multi-period change requires clear deterministic comparison framing. | High. | High. | Medium-High. | Medium. |
| Benchmark revisions | High. | Low-Medium: provider stable but benchmark series/version may change. | Very High: benchmark release identity is central. | Very High: benchmark event may affect long history. | High. | High: many expected changes. | High. | Very High: explanatory metadata important. | High: may challenge canonical comparability. | High: interpretation of benchmark meaning belongs to KnowledgeForge. |
| Methodological revisions | Very High: same code may no longer mean exactly the same concept. | Medium. | High. | High. | High. | High. | High. | Very High. | Very High: concept continuity may be ambiguous. | Very High: semantic interpretation and confidence belong to KnowledgeForge. |
| Rebasing / reference-year changes | High. | Low. | High. | Medium-High. | High. | High. | High. | High. | Very High if base/reference period is not captured in unit/attributes. | High: comparability interpretation belongs to KnowledgeForge. |
| Seasonal-adjustment revisions | Medium-High. | Low. | Medium-High. | Medium-High. | High. | Medium. | High. | Medium-High. | Medium if adjustment status is stable; High if adjustment method/version changes. | Medium-High. |
| Publication corrections / errata | High. | Low. | High. | Very High: correction vs ordinary revision may matter. | Very High if original value disappears. | High. | High. | Very High. | Medium-High. | High: error interpretation should not become MacroForge claim semantics. |
| Preliminary / final status transitions | High. | Low. | High. | High. | High. | Medium. | High. | High. | Medium: status may remain attributes/evidence. | Medium: finality is provider status, not MacroForge truth confidence. |
| Classification revisions | Very High. | Medium. | High. | High. | Medium-High. | High. | High. | High. | Very High: classification identity and canonical mapping are stressed. | Very High: semantic equivalence belongs to KnowledgeForge unless explicitly scoped as source evidence. |

## Interpretation grounded in current architecture

### Observation identity

Current `ObservedIngestionPackage` observation fields identify provider indicator, territory, provider period, frequency, unit, value, attributes, and source payload. They do not contain an explicit vintage/as-of field.

That is not yet a flaw. Under the current architecture, `release_key`, `raw_evidence`, `input_filters`, `attributes`, and `source_payload` are source-specific evidence fields. The first revision experiment should test whether those fields can preserve vintage identity without lossy encoding.

The first experiment should therefore maximize pressure on this question while minimizing unrelated concept changes.

### Provider identity

Revision-aware statistics usually preserve provider identity. This is useful because the first experiment should avoid adding provider-identity novelty. The recent retrospective already shows provider identity can remain source-specific for BEA/Treasury/ECB/IMF/BIS.

### Release identity

Release identity is the central pressure point. `ObservedIngestionPackage.release_key` already exists as a source-specific deterministic dataset-release key. The experiment should test whether two releases/vintages of the same series can be represented as distinct source-backed releases without changing the observed contract.

### Lineage

DEC-023 places observational lineage inside MacroForge. A revision-aware source stresses whether lineage can record publication/revision sequence without making claims about why the revision happened or whether the later value is more true. Those interpretations belong to KnowledgeForge.

### Replay

Current replay/fingerprinting evidence is strong for stable snapshots. Revision-aware sources introduce expected differences across release time. The experiment should distinguish:

- replaying the same vintage should be identical;
- comparing different vintages should reveal deterministic source-backed differences;
- changed value across vintages should not be automatically classified as nondeterministic drift.

### Deterministic validation

Validation should still verify package shape, row counts, required fields, deterministic ordering, and source-backed evidence. It should not decide whether a revised value is economically more correct. The experiment should test whether validation remains contract-focused rather than semantics-focused.

### Fingerprinting

Fingerprints should change when source-backed vintage evidence or values change. That is desirable. The pressure is not whether fingerprints change; it is whether the system can explain that two fingerprints correspond to two distinct release/vintage evidentiary states.

### Provenance

Revision semantics require stronger provenance than static snapshots: acquisition URL/path, retrieval/as-of date if applicable, provider release/vintage metadata, raw fixture checksums, and source payload evidence must be preserved. This likely remains pre-boundary/source-specific unless evidence proves otherwise.

### Canonical observation representation

Canonical loading is out of scope for the first experiment unless explicitly approved later. The assessment should not assume a canonical schema change. The first evidence-only revision slice should clarify whether canonical representation may eventually need vintage-aware identity, but it should not design it now.

### MacroForge / KnowledgeForge boundary

MacroForge should represent source-backed release/vintage facts:

- what the provider published;
- when or under which vintage/release it was published;
- which economic period the value describes;
- which values changed across provider-backed releases;
- source evidence and reproducibility handles.

KnowledgeForge should own:

- claims that a later value is more accurate;
- explanations for why a revision occurred;
- confidence in old vs new values;
- causal/economic interpretation of revisions;
- semantic comparability judgments across methodology/rebase/classification changes.

# 3. Minimal architectural experiment

## Target semantics

The minimum meaningful experiment should test:

```text
ordinary release-vintage revision of numeric observations, including at least one changed value for the same economic period across two distinct provider-backed releases/vintages.
```

## Required characteristics

The smallest useful provider-neutral implementation would have:

- One provider-backed dataset family.
- One provider-backed indicator/series.
- One territory or equivalent reporting unit.
- One frequency.
- One unit and stable seasonal-adjustment / transformation status.
- Two distinct release/vintage states.
- At least one economic period present in both release/vintage states.
- At least one numeric value that differs between the two release/vintage states for the same provider, indicator, territory, unit, frequency, and economic period.
- Preferably one numeric value that remains unchanged across the two release/vintage states as a control observation.
- Preferably one adjacent period that appears only in the later release/vintage, to separate new-publication behavior from revision behavior.

## Minimal observation count

Minimum viable evidence:

```text
2 releases/vintages × 2 economic periods = 4 observed rows
```

But the better minimum is:

```text
2 releases/vintages × 3 economic periods = 6 observed rows
```

The 6-row version is preferred because it can include:

1. one revised overlapping period;
2. one unchanged overlapping period;
3. one period that is newly published or tests coverage consistency.

This remains comparable in scale to recent bounded IMF/BIS slices while producing much higher architectural novelty.

## Temporal scope

Use a small window:

- two release/vintage states;
- two or three economic periods;
- no long historical span;
- no benchmark/rebase/methodology event unless unavoidable.

## Required metadata

The eventual source must expose enough source-backed metadata to preserve:

- provider identity;
- dataset / series identity;
- economic period;
- publication/release/vintage identity;
- acquisition/retrieval evidence;
- numeric value;
- unit/frequency;
- observation status if available;
- provider attributes/notes sufficient to distinguish preliminary/final/revised status if exposed;
- raw evidence checksum or equivalent fixture reproducibility handle.

## Required replay behavior

The minimal experiment should be able to prove these provider-neutral replay properties:

1. Same vintage, same fixture/input -> same observed package and same fingerprint.
2. Later vintage with changed source-backed value -> different observed package and different fingerprint.
3. Difference across vintages is explainable from source-backed release/vintage evidence, not parser nondeterminism.
4. The package for each vintage independently satisfies `ObservedIngestionPackage` validation.
5. The implementation can report the changed overlapping observation without asserting that either value is economically final, correct, or superior.

## Exclusions for the first experiment

Do not intentionally include:

- broad benchmark revision events;
- methodology changes;
- rebasing/reference-year changes;
- classification revisions;
- company filings;
- cross-provider reconciliation;
- canonical entity design;
- canonical loading;
- source framework extraction;
- revision explanation or confidence claims.

# 4. Provider-neutral requirements

The eventual provider/source should satisfy these properties.

## Access and reproducibility

Required:

- Publicly accessible without secrets, paid access, or fragile interactive workflow.
- Deterministic acquisition path for the bounded slice.
- Historical release/vintage states are reproducibly accessible, or raw source artifacts can be fixture-captured with source-backed evidence.
- Terms and rate limits permit bounded evidence capture.
- Source evidence can be checksummed and retained.

Strongly preferred:

- Stable URLs, query parameters, archive paths, or release/vintage identifiers.
- Machine-readable payloads.
- Provider exposes release/vintage metadata directly rather than requiring inference from file naming alone.

## Revision semantics

Required:

- At least two distinct releases/vintages for the same provider-backed series.
- At least one overlapping economic period across those releases/vintages.
- At least one value differs for the same overlapping economic period.
- Provider-backed evidence distinguishes the two releases/vintages.

Strongly preferred:

- At least one unchanged overlapping value as a control.
- At least one explicit preliminary/revised/final/status attribute, if present without broadening scope.
- Revision type is ordinary release/vintage update, not benchmark/methodology/rebase/classification change.

## Boundedness

Required:

- Can be scoped to one provider dataset, one indicator, one territory/reporting unit, two releases/vintages, and two or three periods.
- Does not require broad provider support.
- Does not require a provider metadata framework.
- Does not require canonical loading to produce architectural evidence.

## Evidence quality

Required:

- Raw evidence can be stored or referenced deterministically.
- Value differences can be independently traced to source-backed release/vintage artifacts.
- Metadata is sufficient to distinguish economic period from publication/vintage period.
- The source can support RED/GREEN tests around revision behavior before implementation.

## Boundary safety

Required:

- The source lets MacroForge represent observed values and release evidence without explaining causal reasons for revisions.
- The bounded slice does not require semantic truth judgments, confidence scoring, or cross-source reconciliation.
- The selected data does not force canonical entity infrastructure, graph/catalog systems, or KnowledgeForge-style claim modeling.

# 5. Architectural predictions

These predictions should be recorded before provider selection. Confidence is qualitative and based on current implementation evidence.

## Prediction 1 — `ObservedIngestionPackage` should remain unchanged for ordinary release-vintage revisions

Confidence: Moderate-High.

Supporting evidence:

- Recent heterogeneous sources fit existing fields without contract evolution.
- `release_key`, `raw_evidence`, `input_filters`, `attributes`, and `source_payload` are intentionally source-specific evidence carriers.
- The contract already distinguishes economic period from source/release evidence at package level.

Expected behavior:

- Each release/vintage can be represented as a distinct observed package or distinct source release evidence.
- Observation rows can preserve the same provider period with different values under different package/release evidence.

Weakening observations:

- Vintage/as-of evidence must be stuffed into unrelated fields with unclear semantics.
- A source exposes revision identity at observation level in a way that cannot be preserved through `attributes` or `source_payload` without loss.
- Tests require source-specific post-boundary validation branches.

Falsifying observations:

- Multiple ordinary release-vintage observations cannot be represented without adding a first-class vintage/as-of field to the observed contract.
- The same provider/economic-period/value sequence cannot be deterministically distinguished by release evidence.
- Existing fields force lossy encoding that prevents replay or lineage explanation.

## Prediction 2 — Deterministic replay should remain unchanged for same-vintage replay, but comparison semantics will need careful documentation

Confidence: Moderate.

Supporting evidence:

- Deterministic fingerprinting and package comparison already worked unchanged across ECB, IMF, and BIS.
- Fingerprints are supposed to change when input source evidence changes.

Expected behavior:

- Replaying the same vintage should produce identical package/fingerprint.
- Comparing different vintages should produce deterministic differences.
- The implementation can describe those differences as source-backed revision evidence without changing core replay mechanics.

Weakening observations:

- Existing comparison output cannot distinguish expected cross-vintage differences from accidental parser drift even in documentation/tests.
- Fingerprints change due to retrieval-time metadata that is not provider-semantic.

Falsifying observations:

- Same-vintage replay is nondeterministic under deterministic fixture inputs.
- Cross-vintage comparison cannot be made reproducible from retained raw evidence.
- Substrate comparison requires source-specific conditional logic to avoid false failures.

## Prediction 3 — Revision semantics belong primarily before or at the observed boundary as source/release evidence, not as KnowledgeForge claims

Confidence: High.

Supporting evidence:

- DEC-023 places source-backed observations, provenance, reproducibility, lineage, and observational identity in MacroForge.
- KnowledgeForge owns confidence-bearing claims, explanations, causal relationships, and semantic interpretation.
- Recent implementations kept provider semantics source-specific before the boundary.

Expected behavior:

- Provider release/vintage metadata is parsed source-specifically.
- MacroForge preserves the observed revision facts.
- KnowledgeForge, not MacroForge, later interprets whether a revision improves accuracy or changes economic conclusions.

Weakening observations:

- Provider revision metadata is inseparable from explanatory claims in the raw payload.
- Capturing the observation requires classifying revision reasons beyond provider-supplied status.

Falsifying observations:

- MacroForge cannot preserve revision evidence without asserting semantic truth, confidence, or causal explanation.
- The source requires cross-source or model-based interpretation to identify the revision at all.

## Prediction 4 — Implementation effort will concentrate in pre-boundary source semantics and fixture design

Confidence: High.

Supporting evidence:

- TASK-053..057 repeatedly concentrated effort in acquisition, provider interpretation, period handling, and metadata preservation.
- Revision-aware sources add release/vintage interpretation, which is source metadata before the boundary.

Expected behavior:

- The hardest parts will be selecting a bounded slice, capturing two reproducible vintages, preserving release/as-of metadata, and constructing tests that distinguish revision from drift.
- Post-boundary package validation should remain low-effort.

Weakening observations:

- Most effort shifts into post-boundary lineage/replay/fingerprint code.
- Source acquisition is trivial but observed identity ambiguity dominates after package construction.

Falsifying observations:

- The ordinary revision slice requires substantial substrate redesign before any source-specific parsing is difficult.
- Existing post-boundary components cannot accept revision evidence without structural changes.

## Prediction 5 — The first experiment will clarify canonical-loading risk but should not require canonical loading

Confidence: Moderate-High.

Supporting evidence:

- BEA/Treasury/ECB/IMF/BIS were evidence-only and still produced useful architectural evidence.
- Canonical loading beyond WDI/OECD/Eurostat remains weakly evidenced.
- DEC-023 does not authorize schema/entity design from vision alone.

Expected behavior:

- Evidence-only packages will be sufficient to determine whether revision identity pressures the observed boundary.
- The experiment may produce future questions about canonical observation identity, but should not answer them by design.

Weakening observations:

- Revision behavior cannot be evaluated without simulating canonical identity collision.
- Observation identity pressure only appears after canonical load.

Falsifying observations:

- No meaningful revision architecture evidence can be obtained without canonical persistence.
- The source's revision behavior is entirely about canonical fact replacement semantics rather than observed evidence representation.

## Prediction 6 — Ordinary release-vintage revisions are a better first test than benchmark/methodology/rebase/classification revisions

Confidence: High.

Supporting evidence:

- The frontier assessment identified the core uncertainty as time-versioned observational truth.
- Benchmark, methodology, rebase, and classification revisions mix revision semantics with concept identity, unit/base semantics, or canonical mapping questions.

Expected behavior:

- Ordinary release-vintage revisions isolate publication-time identity with minimal unrelated semantic change.
- More complex revision categories should be deferred until ordinary vintage behavior is understood.

Weakening observations:

- No provider-neutral ordinary release-vintage slice can be found with deterministic access and changed overlapping values.
- Available ordinary vintages lack release metadata, while benchmark/rebase sources expose clearer source-backed metadata.

Falsifying observations:

- Ordinary release-vintage data produces no changed overlapping values and therefore cannot stress revision semantics.
- Only benchmark/methodology/rebase examples provide reproducible revision evidence.

# 6. Provider selection criteria

Provider selection should happen only after this assessment. It should maximize architectural evidence, not domain popularity.

## Mandatory criteria

The chosen source should:

1. expose at least two reproducible release/vintage states;
2. include at least one changed value for the same economic period across those states;
3. keep provider, dataset, indicator, territory/reporting unit, unit, frequency, and economic period stable for the changed observation;
4. provide provider-backed release/vintage metadata;
5. be publicly accessible without credentials, payment, secrets, or fragile browser-only workflow;
6. allow a bounded fixture with deterministic checksums;
7. be small enough for RED/GREEN tests and manual architectural review;
8. avoid forcing canonical loading, provider framework extraction, source registry work, or entity infrastructure;
9. preserve the MacroForge/KnowledgeForge boundary by requiring only source-observed values and provenance, not interpretation.

## Evidence-maximizing criteria

Prefer a source that maximizes:

- explicit distinction between economic period and publication/vintage period;
- direct provider evidence for each vintage/release;
- one changed overlapping value and one unchanged control value;
- clear raw payload provenance;
- simple dimensional identity;
- stable unit/frequency/indicator semantics;
- deterministic re-acquisition or stable archival access;
- small enough data shape to keep architecture visible.

## Risk-minimizing criteria

Avoid, for the first revision experiment, sources that require:

- benchmark revision interpretation;
- methodology-change interpretation;
- rebasing/reference-year conversion;
- classification mapping;
- seasonal-adjustment model explanation;
- publication correction/error judgment;
- broad historical archives;
- multiple providers;
- cross-source reconciliation;
- canonical schema evolution;
- large bulk processing;
- company/entity/security-master semantics.

## Tie-breakers

If multiple candidates satisfy the mandatory criteria, choose the one that:

1. has the smallest reproducible slice;
2. exposes the clearest release/vintage metadata;
3. has the least unrelated dimensional complexity;
4. has the clearest changed-value evidence;
5. has the lowest access fragility;
6. is most likely to produce a definitive Confirmed / Partially confirmed / Refuted prediction review.

# Final answer

The revision behavior MacroForge should test first is:

```text
ordinary release-vintage revision of a small numeric statistical series: two provider-backed releases/vintages, two or three economic periods, at least one overlapping period with a changed value, and stable provider/indicator/territory/unit/frequency semantics.
```

This is the smallest experiment that can produce high architectural evidence because it directly stresses the unresolved question identified by the frontier assessment:

```text
Can MacroForge represent multiple source-backed values for the same economic period across publication time while preserving identity, lineage, replay, validation, reproducibility, and the MacroForge/KnowledgeForge boundary?
```

The first experiment should not test benchmark revisions, methodology changes, rebasing, classification revisions, or company-style events. Those are important later but mix multiple unresolved architectural questions. The next implementation should isolate publication-time revision semantics before broadening to more complex revision categories.
