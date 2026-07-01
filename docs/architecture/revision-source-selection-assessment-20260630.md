# Revision-Source Selection Assessment — 2026-06-30

Status: architectural planning assessment
Scope: provider selection only; no implementation authorized
Inputs: Strategic Constitution v1.1, DEC-022, DEC-023, current architecture state, five-source architectural retrospective, next architectural frontier assessment, revision-semantics architectural assessment

## Executive answer

Recommended provider:

```text
ALFRED — ArchivaL Federal Reserve Economic Data, from the Federal Reserve Bank of St. Louis.
```

Reason:

ALFRED is purpose-built for the exact architectural experiment MacroForge has already defined: provider-backed economic data vintages where the same observation period can appear with different values across publication/realtime dates while series identity, observation period, frequency, and unit can remain stable.

This recommendation is not based on popularity, indicator count, economic usefulness, or future expansion potential. It is based on architectural cleanliness:

```text
ALFRED most directly exposes ordinary release-vintage semantics with the fewest unrelated architectural variables.
```

This assessment does not implement ALFRED, create a task, design code, recommend extraction, or authorize provider work.

## Accepted experiment being selected for

From `revision-semantics-architectural-assessment-20260630.md`, the target behavior is:

```text
ordinary release-vintage revision of a small numeric statistical series: two provider-backed releases/vintages, two or three economic periods, at least one changed overlapping value, and stable provider/indicator/territory/unit/frequency semantics.
```

The provider should maximize:

- explicit distinction between economic period and publication/vintage period;
- deterministic access to at least two vintages;
- one changed overlapping value;
- one unchanged overlapping control value if possible;
- stable provider/series/unit/frequency identity;
- small bounded evidence capture;
- no need for canonical loading, source framework extraction, broad provider support, or KnowledgeForge-style interpretation.

# 1. Candidate providers

## 1.1 ALFRED

Revision model exposed:

ALFRED describes itself as a collection of vintage versions of U.S. economic data. It exists to make it possible to gather data as reported by a source on past dates in history. ALFRED distinguishes source release dates / realtime dates from observation periods and records new and revised observations after source releases.

Architectural meaning:

ALFRED directly exposes the distinction MacroForge wants to test:

```text
observation period != publication/vintage/realtime date
```

The same series and observation period can be requested or represented under different realtime/vintage dates. This is precisely ordinary release-vintage behavior.

## 1.2 FRED API with realtime/vintage parameters

Revision model exposed:

The FRED `series/observations` API documents realtime and vintage-related parameters such as `realtime_start`, `realtime_end`, and `vintage_dates`, and returns observation values for a series. It can therefore expose vintage-aware behavior.

Architectural meaning:

FRED API semantics are close to ALFRED semantics, but API usage requires a registered API key. That makes it a weaker first MacroForge experiment if an equivalent ALFRED path can avoid secrets/credentials.

## 1.3 OECD revision-capable datasets

Revision model exposed:

OECD SDMX endpoints expose current statistical data and SDMX structure. Some OECD data may be revised over time as source datasets update, and some APIs support update-oriented access patterns, but ordinary historical release-vintage retrieval is not the core exposed product in the same way as ALFRED.

Architectural meaning:

OECD can expose revisions as changed current snapshots, but it is not the cleanest provider for retrieving two provider-backed historical vintages of the same observation period. It also overlaps strongly with existing OECD/SDMX evidence, reducing architectural novelty.

## 1.4 Eurostat dissemination API / bulk statistical files

Revision model exposed:

Eurostat datasets expose current data, status flags, and update timestamps. Values can be revised across dataset updates. However, ordinary historical release-vintage access is not the primary dissemination model for the standard API; retrieving exact prior vintages usually depends on external archive/release-file availability rather than a clean vintage API.

Architectural meaning:

Eurostat can test current-update/revision drift and status metadata, but it is less clean for the exact two-vintage experiment because historical vintage reproducibility is weaker than ALFRED-style realtime data.

## 1.5 IMF datasets with historical vintages

Revision model exposed:

IMF statistical APIs generally expose current datasets and rich dataset/series structure. Some IMF data are revised over time, but ordinary historical release-vintage retrieval for a tiny public slice is not the dominant simple access pattern.

Architectural meaning:

IMF would add revision questions on top of already-tested SDMX-family/source-specific parsing questions. That violates the current goal of isolating revision semantics from unrelated provider/protocol complexity.

## 1.6 National statistical office release archives

Revision model exposed:

Many national statistical offices publish release archives, historical press releases, data tables, or CSV/XLS files for past releases. These can contain preliminary and revised values.

Architectural meaning:

They may provide real revision evidence, but provider-by-provider access is heterogeneous. Many archives are HTML/PDF/XLS release documents, sometimes benchmark/methodology-heavy, and often require manual comparison to identify revisions. They are useful later but less clean for the first provider-neutral ordinary vintage test.

## 1.7 BEA historical release/archive material

Revision model exposed:

BEA publishes estimates over time and NIPA data are revised, including regular and benchmark revisions. Historical releases may be available through release/archive material.

Architectural meaning:

BEA is not ideal for the first revision experiment because BEA revision behavior often mixes ordinary release vintages with annual revisions, benchmark revisions, methodology changes, table/line complexity, and release-document interpretation. MacroForge already used BEA as a table/line evidence source in TASK-053; using BEA now would risk testing BEA-specific release complexity rather than clean vintage semantics.

# 2. Architectural fit

| Candidate | Provider-backed vintages | Deterministic acquisition | Reproducibility | Stable identities across releases | Bounded feasibility | Metadata quality | Accessibility | Implementation complexity | Architectural fit |
|---|---|---|---|---|---|---|---|---|---|
| ALFRED | Very strong. Vintage/realtime data is the core product. | Strong if using stable public vintage queries / downloadable artifacts. | Strong: designed for historical vintage access. | Strong: same series, observation period, frequency, unit can be held stable across vintages. | Very strong: one series, two vintages, two or three periods. | Strong: release/realtime/vintage semantics are explicit. | Strong if public web/download paths are used; no provider selected for implementation yet. | Low to moderate. Main work is source-specific interpretation and fixture design. | Best fit. |
| FRED API realtime/vintage parameters | Strong. API exposes realtime/vintage parameters. | Strong technically, but credential-dependent. | Strong with API key and stable queries. | Strong. | Very strong. | Strong. | Moderate because registered API key is required. | Low to moderate. | Strong semantics, weaker access fit than ALFRED. |
| OECD revision-capable datasets | Weak to moderate for historical vintages; strong for current SDMX snapshots. | Strong for current data. | Weak to moderate for exact historical vintages. | Moderate. | Moderate. | Strong SDMX metadata, weaker vintage metadata. | Strong. | Moderate, but overlaps existing OECD/SDMX evidence. | Not best: revision semantics are not isolated. |
| Eurostat dissemination/bulk | Weak to moderate for historical vintages; current update metadata is strong. | Strong for current API. | Weak to moderate for exact prior vintages. | Moderate. | Moderate. | Moderate to strong for statuses/update dates, weaker for release-vintage identity. | Strong. | Moderate. | Not best: tests update/current-snapshot behavior more than clean vintages. |
| IMF datasets | Weak to moderate for clean historical vintages. | Strong for current API/SDMX. | Weak to moderate for exact vintages. | Moderate. | Moderate. | Strong source metadata, but revision metadata less direct for first experiment. | Strong. | Moderate-high because IMF SDMX complexity already known. | Not best: adds protocol/provider complexity. |
| National statistical office archives | Variable. Some strong, many weak. | Variable. | Variable. | Variable. | Variable; often hard to bound. | Variable. | Usually public, but formats vary. | Moderate to high. | Later candidate, not clean first test. |
| BEA release/archive material | Moderate to strong, but often mixed with benchmark/annual/methodology revisions. | Moderate. | Moderate to strong if archive artifacts are stable. | Moderate. | Moderate, but careful slice selection needed. | Strong for releases, but interpretation-heavy. | Strong. | Moderate-high. | Not first: too much non-ordinary revision semantics. |

## Ranking by architectural fit

1. ALFRED.
2. FRED API realtime/vintage parameters.
3. Eurostat / OECD / IMF only if ALFRED is blocked or if no credential-free ALFRED path is usable.
4. National statistical office archives or BEA only after ordinary vintage behavior has been tested with a cleaner provider.

# 3. Smallest useful slice for the strongest candidate

Strongest candidate: ALFRED.

Provider-neutral shape specialized to ALFRED-style vintages:

- Number of vintages: 2.
- Number of economic periods: preferably 3.
- Number of observed rows: preferably 6 total rows, 2 vintages × 3 periods.
- Required overlap: at least 2 economic periods present in both vintages.
- Required changed value: at least 1 overlapping economic period must have a different numeric value across the two vintages.
- Required unchanged control value: preferably 1 overlapping economic period with the same numeric value across both vintages.
- Optional new-publication control: preferably 1 period present only in the later vintage, if the source shape naturally supports this without widening scope.

Required metadata:

- Provider identity: ALFRED / Federal Reserve Bank of St. Louis as source aggregator, plus original source metadata if exposed.
- Series identity: provider-backed series code and title/metadata if available.
- Economic period: observation date/period.
- Vintage/realtime identity: exact vintage/realtime date or release date used to retrieve the observation state.
- Numeric value.
- Unit, frequency, and seasonal-adjustment status if exposed.
- Retrieval/acquisition evidence.
- Raw source checksum / fixture hash.
- Provider attributes/notes necessary to preserve vintage evidence.

The smallest acceptable implementation should not require:

- more than one series;
- more than one provider;
- canonical loading;
- broad ALFRED support;
- FRED/ALFRED API key handling if a public deterministic path is available;
- benchmark, rebase, methodology, correction, or classification semantics.

# 4. Architectural predictions

These predictions should be used as the pre-implementation baseline if ALFRED implementation is later authorized.

## Prediction 1 — `ObservedIngestionPackage` should remain unchanged

Confidence: Moderate-High.

Evidence supporting it:

- `ObservedIngestionPackage` has already represented WDI, OECD, Eurostat, BLS, BEA, Treasury, ECB, IMF, and BIS source observations without recent contract evolution.
- The revision-semantics assessment predicts that ordinary release-vintage evidence should fit through `release_key`, `raw_evidence`, `input_filters`, `attributes`, and `source_payload`.
- ALFRED-style vintage semantics preserve stable series and observation-period identity while adding publication/realtime identity as source evidence.

Weakening conditions:

- ALFRED exposes vintage identity only at observation level and it cannot be preserved cleanly in existing attributes/source payload fields.
- Multiple vintages of the same period create ambiguous observed-row identity under package comparison.
- Tests require special post-boundary conditionals for ALFRED.

Falsifying conditions:

- A first-class vintage/as-of field is required in the observed contract to avoid lossy representation.
- The same economic-period observation cannot be distinguished across releases/vintages by existing package/release evidence.
- Existing `release_key`/raw evidence structures cannot represent two provider-backed vintages deterministically.

## Prediction 2 — Deterministic replay remains unchanged for same-vintage inputs

Confidence: High.

Evidence supporting it:

- Deterministic package construction/fingerprinting worked unchanged across recent heterogeneous slices.
- ALFRED-style queries should be deterministic when vintage/realtime dates and observation windows are fixed.

Weakening conditions:

- Returned data includes retrieval-time metadata that changes across runs and contaminates fingerprints.
- Public web/download access is less deterministic than documented API access.

Falsifying conditions:

- Same vintage + same bounded query/fixture produces different observed rows or fingerprints.
- Replay cannot be made deterministic without broad provider infrastructure or nondeterministic cleanup.

## Prediction 3 — Lineage pressure increases, but lineage should remain source-evidence lineage rather than KnowledgeForge interpretation

Confidence: Moderate.

Evidence supporting it:

- DEC-023 assigns source-backed observations, provenance, reproducibility, lineage, validation, and observational identity to MacroForge.
- ALFRED's release/vintage model cleanly separates what was known at a historical realtime date from later values.

Weakening conditions:

- The implementation cannot state why two packages differ without explanatory economic interpretation.
- Original source metadata is insufficient to distinguish ordinary revision from correction/benchmark/methodology change.

Falsifying conditions:

- MacroForge cannot preserve vintage sequence without asserting which value is more accurate or why the revision occurred.
- ALFRED evidence requires KnowledgeForge-style claim/confidence modeling to identify the revision at all.

## Prediction 4 — Validation remains contract-focused

Confidence: High.

Evidence supporting it:

- Recent source slices required no source-specific post-boundary validation branches.
- The first ALFRED slice can validate package shape, required fields, deterministic row ordering, raw evidence, and expected changed/unchanged overlap without interpreting economic meaning.

Weakening conditions:

- Distinguishing expected revision from parser drift requires validation semantics not currently present.
- Observation status/finality fields become mandatory for correctness but are not consistently available.

Falsifying conditions:

- Validation must decide whether a later vintage is economically more correct.
- Existing validation cannot accept two source-backed values for the same economic period even when release/vintage evidence differs.

## Prediction 5 — Fingerprinting will differ across vintages and that difference is expected

Confidence: High.

Evidence supporting it:

- Existing fingerprints are source-evidence fingerprints; changed source-backed values should produce changed fingerprints.
- The revision-semantics assessment explicitly predicts same-vintage sameness and cross-vintage difference.

Weakening conditions:

- Fingerprint differences cannot be explained from provider-backed release/vintage metadata.
- Metadata fields unrelated to source semantics dominate the fingerprint.

Falsifying conditions:

- Cross-vintage fingerprint changes are indistinguishable from nondeterministic drift under retained evidence.
- Same-vintage fingerprinting is unstable.

## Prediction 6 — Release identity becomes the central pressure point

Confidence: Very High.

Evidence supporting it:

- The entire accepted revision experiment isolates publication/vintage identity while holding series/period/unit/frequency stable.
- ALFRED is explicitly organized around vintage versions and release/realtime dates.

Weakening conditions:

- Candidate ALFRED slice fails to expose clear vintage/realtime identifiers for the selected observations.
- Release identity is only inferable from URL parameters, not provider-returned metadata or stable artifact names.

Falsifying conditions:

- ALFRED cannot provide two distinct provider-backed vintages for the same observation period.
- A changed overlapping value cannot be tied to distinct release/vintage evidence.

## Prediction 7 — Implementation effort concentrates before the observed boundary

Confidence: High.

Evidence supporting it:

- TASK-053..057 repeatedly concentrated effort in acquisition, provider metadata interpretation, normalization, period handling, and fixture design.
- ALFRED adds source-specific vintage/realtime interpretation before the boundary.

Weakening conditions:

- Most work shifts to post-boundary comparison/lineage/fingerprint changes.
- ALFRED source acquisition is trivial but observed-package identity requires contract changes.

Falsifying conditions:

- Implementation requires substrate redesign before source-specific parsing/normalization becomes meaningful.
- Existing deterministic mechanics cannot represent two release states without new shared infrastructure.

# 5. Recommendation

Recommend exactly one provider:

```text
ALFRED.
```

Why ALFRED is the cleanest architectural experiment:

1. It directly exposes the revision behavior MacroForge wants to test: vintage/realtime versions of economic data.
2. It keeps the experiment small: one series, two vintages, two or three periods.
3. It separates observation period from publication/vintage date more clearly than generic current-snapshot APIs.
4. It minimizes unrelated architectural variables: no product classifications, partner countries, company identities, benchmark-heavy event interpretation, or broad SDMX/provider-framework questions are needed.
5. It allows the experiment to focus on the current unresolved MacroForge question:

```text
Can multiple source-backed values for the same economic period be represented through existing observed-package/release/provenance evidence without contract or substrate redesign?
```

Why not FRED API first:

FRED API realtime/vintage parameters are semantically strong, but the documented API requires a registered API key. If ALFRED offers a credential-free deterministic path for the same revision semantics, ALFRED better satisfies MacroForge's no-secrets, reproducible, bounded evidence preference.

Why not OECD/Eurostat/IMF first:

They can revise data, but they are not purpose-built historical vintage providers for this exact experiment. They would mix the revision question with current-snapshot update mechanics, SDMX/provider interpretation, or weaker historical-vintage reproducibility.

Why not national statistical office or BEA archives first:

They may provide rich revision evidence, but their release archives often mix ordinary revisions with benchmark, methodology, rebase, correction, or document-archive complexity. That is valuable later but not the smallest clean test.

## Final assessment

The best provider for the final pre-implementation revision experiment is ALFRED because it gives MacroForge the cleanest possible test of ordinary release-vintage revisions with minimal unrelated complexity.

The subsequent implementation, if explicitly authorized later, should remain bounded to a tiny ALFRED slice and should begin with a prediction ledger based on the predictions above. It should not broaden into broad FRED/ALFRED support, API-key infrastructure, canonical loading, benchmark/methodology revision handling, or shared revision infrastructure.
