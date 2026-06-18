# Minimal AI-assisted canonicalization layer

Status: accepted design proposal for TASK-030
Date: 2026-06-05
Related task: TASK-030
Decision: `artifacts/decisions/DEC-018-minimal-ai-assisted-canonicalization-layer.md`
Preceded by: DEC-015, DEC-016
Seed evidence: `artifacts/reports/canonical-gdp-snapshot-20260604.md`

## Problem statement

TASK-028 proved that MacroForge can generate a deterministic GDP snapshot from `curated.*` plus `meta.*` only. The report succeeded with 3 sources, 20 canonical fact rows, 16 bounded GDP observations, 0 missing observations, 0 duplicate fact grains, and 0 failing quality checks.

That success exposed the next semantic boundary:

- OECD `B1GQ`, Eurostat `B1GQ`, and WDI `NY.GDP.MKTP.CD` are GDP-ish, but MacroForge does not yet represent their relationship to a shared source-agnostic economic concept.
- Units differ: `CP_MEUR`, `USD_EXC`, `USD_PPP`, and WDI's current `unknown` unit representation.
- Annual and quarterly rows coexist correctly, but that must not imply aggregation, conversion, or direct comparability.
- Provider metadata and source evidence exist in different forms, but there is no governed canonicalization process that turns evidence into auditable mapping state.

DEC-015 identified the comparability gap. DEC-016 refined the solution: MacroForge should not become a manually curated warehouse where humans define and approve every provider-indicator mapping. The design target is an auditable AI-assisted canonicalization layer:

```text
Provider Indicator Evidence
-> Automated Canonicalization Layer
-> Mapping Proposal or Canonical-Creation Proposal
-> Confidence / Reasoning / Evidence / Version
-> Human Review for exceptions
-> Accepted Mapping State
-> Canonical Indicator
-> Curated Facts
```

TASK-030 is governance/design-only. This document does not implement migrations, code, unit conversion, report generation, new sources, live fetches, live/default database writes, or framework extraction.

## Design principles

1. Canonical concepts are durable analytical identities, not provider codes.
2. Provider indicators are evidence-bearing source objects, not canonical truth.
3. Automated canonicalization creates auditable proposals, not opaque curated facts.
4. Confidence scores route review; they do not prove correctness.
5. Human governance focuses on policies, thresholds, high-impact concepts, low-confidence/conflicting cases, new canonical concept proposals, audit sampling, and schema/model changes.
6. Accepted mapping state is the gate between proposals and curated facts.
7. Re-canonicalization must version and supersede previous mappings rather than overwrite history.
8. Unit/comparability metadata blocks false comparison before it enables conversion.
9. Frequency and period semantics stay explicit; annual and quarterly observations are not aggregated unless a later accepted task designs that policy.
10. Keep the first implementation boring: state tables/files and tests before model calls or broad ontology work.

## Traditional manual warehouse model vs AI-assisted canonicalization

A traditional warehouse model would have humans manually define canonical indicators, map every provider indicator, review units, and approve the mapping before facts can be treated as canonical.

That model is useful for a very small universe of high-value indicators, but it does not scale to MacroForge's intended direction: many heterogeneous public sources, many indicators, repeated metadata changes, and future re-canonicalization as better logic appears.

MacroForge should keep manual governance for leverage points:

- policy and threshold definition;
- high-impact economic concepts;
- low-confidence or conflicting proposals;
- new canonical concept proposals;
- audit sampling of auto-accept candidates;
- schema/model changes;
- material re-canonicalization that affects published reports.

It should reject manual approval as the default path for every provider indicator.

The AI-assisted model fits MacroForge better because provider metadata can be treated as evidence for reproducible proposal generation. The system can generate mapping hypotheses, store confidence/reasoning/provenance, and route only exceptions or high-risk items to humans.

## Minimal conceptual data model

This is a conceptual model, not a migration specification. The follow-on implementation task should decide exact table/file names, columns, and fixture shape.

### 1. Provider indicator evidence

Purpose: normalized evidence about a provider's indicator or series identity before canonical mapping.

Minimum fields:

- stable evidence id;
- source/provider id, for example `WDI`, `OECD_NAAG`, `EUROSTAT_NAMQ_GDP`;
- dataset/collection/release id;
- provider indicator code, for example `NY.GDP.MKTP.CD` or `B1GQ`;
- provider title/name when available;
- provider description/methodology text when available;
- provider dimension context and code-list labels when available;
- provider unit code and unit label/description when available;
- frequency hints;
- territory/geography hints;
- source URLs and documentation references;
- raw artifact path/checksum references;
- evidence version/checksum;
- observed example values or bounded fixture references when useful for audit.

Provider evidence should live outside curated facts. It can be assembled from existing raw/staging/meta evidence and enriched later as source-specific metadata improves.

### 2. Canonicalization run

Purpose: a reproducible run record for proposal generation.

Minimum fields:

- run id;
- timestamp;
- operator/agent identity when relevant;
- method type, for example deterministic rules, embeddings, LLM, hybrid;
- method/ruleset/model/prompt version;
- input evidence version/checksum set;
- candidate canonical concept catalog version;
- thresholds used;
- policy version;
- output proposal checksum or artifact reference.

For the first implementation, this can be deterministic and fixture-backed. No LLM/model call is required.

### 3. Canonical indicator concept

Purpose: source-agnostic analytical identity.

Minimum fields:

- canonical concept id/code, for example a future `GDP`-like concept code, not a provider code;
- label;
- definition;
- domain/category;
- measure type, for example flow, stock, index, rate, count;
- default comparability caveats;
- lifecycle status: proposed, active, deprecated, superseded;
- version or valid interval;
- supersession pointer when replaced/merged/split.

Deferred fields include full ontology hierarchy, semantic embeddings, topic graph, and broader macro knowledge graph relations.

### 4. Mapping proposal

Purpose: generated, auditable hypothesis linking provider evidence to an existing canonical concept.

Minimum fields:

- proposal id;
- canonicalization run id;
- provider indicator evidence id;
- proposed canonical concept id/version;
- relationship type: exact, close, broader, narrower, related, not comparable, no match;
- confidence score;
- confidence band: auto-accept candidate, review required, reject/no match;
- reasoning summary;
- evidence references/citations;
- proposed unit/comparability treatment;
- proposed frequency/period treatment;
- status: proposed, auto_accept_candidate, review_required, accepted, rejected, superseded;
- created timestamp;
- reviewer/review timestamp/review notes when reviewed;
- supersedes/superseded_by pointers.

Mapping proposals are immutable audit evidence. Acceptance creates accepted mapping state rather than mutating the original proposal into history-less truth.

### 5. Canonical creation proposal

Purpose: proposed new canonical concept when no existing concept fits.

Minimum fields:

- creation proposal id;
- canonicalization run id;
- proposed canonical concept code/label/definition;
- supporting provider evidence ids;
- duplication-risk notes against existing concepts;
- proposed domain/measure type/default caveats;
- confidence score/band;
- reasoning/evidence references;
- status: proposed, review_required, accepted, rejected, superseded;
- review notes and lineage.

New concept creation should be review-required by default until there is explicit policy for low-risk auto-creation.

### 6. Accepted mapping state

Purpose: governed state that curated facts and reports can reference.

Minimum fields:

- accepted mapping id/version;
- provider indicator evidence id or provider indicator identity;
- canonical concept id/version;
- source/dataset scope where valid;
- relationship type;
- unit/comparability profile reference;
- frequency/period applicability;
- accepted status: accepted, provisional, deprecated, superseded;
- acceptance source: auto-accepted under policy, human-reviewed, imported trusted rule;
- accepted from proposal id;
- accepted timestamp;
- policy/run version;
- supersession lineage;
- affected facts/report scope if superseded.

Curated facts should use accepted or explicitly provisional mapping state according to policy. Opaque proposal output should not directly create source-agnostic analytical facts.

### 7. Unit/comparability profile

Purpose: express whether observations can be grouped or compared without performing conversion.

Minimum fields:

- provider unit code and label;
- normalized unit family, for example currency, index, rate, count, unknown;
- currency when known;
- scale/multiplier when known;
- price basis, for example current, constant/real, chain-linked, unknown;
- valuation basis, for example market prices/basic prices when known;
- PPP vs exchange-rate basis when known;
- seasonal-adjustment hint when relevant;
- unit metadata quality: complete, partial, unknown, conflicting;
- comparability group id or caveat text;
- conversion status: none, deferred, not_applicable, future_required.

The first implementation should represent comparability and caveats, not conversion.

### 8. Review queue/status

Purpose: route exceptions, not every mapping.

Review-required triggers:

- confidence below auto-accept threshold;
- conflicting proposals for one provider indicator;
- one proposal affects an existing accepted mapping;
- new canonical concept creation;
- high-impact concept, for example GDP, CPI, unemployment, policy rates, fiscal balances;
- unit metadata unknown/conflicting for a concept where unit semantics matter;
- relationship type is close/broader/narrower/related rather than exact;
- proposed mapping would affect published or user-facing reports.

Auto-accept candidate criteria should be conservative and policy-controlled. The first implementation may store auto-accept candidates but keep acceptance manual or fixture-policy-based until calibration evidence exists.

### 9. Re-canonicalization and supersession lineage

Purpose: preserve old mappings while allowing improved logic.

Rules:

- Never overwrite accepted mapping history silently.
- New runs create new proposals against explicit evidence/catalog/policy versions.
- A changed accepted mapping creates a new mapping version and supersedes the old one.
- Supersession records reason, proposal/run id, reviewer or policy source, and affected fact/report scope.
- Reports should cite the mapping version used so old outputs remain reproducible.
- Deprecated concepts and mappings remain readable for audit.

## GDP seed examples

These examples are seed evidence for the design, not GDP-specific hard-coding.

### OECD `B1GQ`

Evidence:

- source: `OECD_NAAG`;
- provider indicator: `B1GQ`;
- frequency in bounded facts: annual;
- observed units: `USD_EXC`, `USD_PPP`;
- territories: AUS, USA;
- report role: GDP-ish annual observations.

Expected proposal behavior:

- propose a mapping to a source-agnostic GDP/output concept candidate;
- relationship likely `close` or `exact` only if the provider description and measure metadata are sufficient;
- create separate unit/comparability profiles for `USD_EXC` and `USD_PPP`;
- route to review if GDP is classified high-impact or if unit comparability is incomplete.

### Eurostat `B1GQ`

Evidence:

- source: `EUROSTAT_NAMQ_GDP`;
- dataset: `namq_10_gdp` bounded fixture;
- provider indicator: `B1GQ`;
- frequency: quarterly;
- observed unit: `CP_MEUR`;
- territories: DEU, FRA;
- report role: GDP-ish quarterly observations.

Expected proposal behavior:

- propose the same broad GDP/output concept candidate if metadata supports it;
- preserve quarterly frequency as explicit applicability, not aggregation input;
- unit profile records current-price million euro semantics when available from metadata;
- route to review because frequency and unit differ from OECD/WDI annual current-dollar examples.

### WDI `NY.GDP.MKTP.CD`

Evidence:

- source: `WDI`;
- provider indicator: `NY.GDP.MKTP.CD`;
- frequency: annual;
- observed provider unit in current report: `unknown`;
- likely title/description from WDI evidence should identify GDP at market prices in current US dollars when available.

Expected proposal behavior:

- propose GDP/current-dollar market-price concept mapping only if provider title/description evidence is captured;
- set unit metadata quality to partial/unknown until WDI unit semantics are explicitly represented;
- route to review or mark provisional because the current report artifact records unit as `unknown`.

## Required vs deferred scope

### Required for the next implementation task

- Add a minimal state surface for provider indicator evidence, canonicalization runs, mapping proposals, canonical creation proposals, accepted mapping state, and unit/comparability profiles.
- Use existing bounded fixtures/report evidence only.
- Use deterministic fixture-backed proposal examples first; no model calls required.
- Preserve accepted/provisional mapping versioning and supersession fields from the start.
- Add tests that prove proposals are stored separately from accepted mapping state.
- Add tests that unknown/conflicting units prevent direct comparability.
- Add tests that annual/quarterly facts remain distinct and unaggregated.
- Generate an audit artifact showing the OECD/Eurostat/WDI GDP seed evidence and proposed/accepted/provisional mapping states.

### Deferred

- LLM/embedding canonicalization calls;
- broad provider catalog ingestion;
- new sources;
- live source fetches;
- unit conversion;
- quarterly-to-annual aggregation;
- mart/report/dashboard work;
- generalized ingestion framework;
- full ontology/knowledge graph;
- automatic low-risk canonical concept creation;
- calibrated confidence thresholds from large reviewed samples.

## Migration/code implications if accepted

The design implies a follow-on implementation task that may add a small schema/file-backed state foundation. It should be separate from TASK-030 and should start with a fresh implementation dry-run.

The likely implementation shape is one bounded migration or equivalent state artifact for:

- provider indicator evidence;
- canonicalization run records;
- canonical indicator concepts;
- mapping proposals;
- canonical creation proposals;
- accepted mapping state;
- unit/comparability profiles;
- supersession lineage.

If implemented in PostgreSQL, it should remain source-agnostic and should not widen `curated.fact_observation` with provider-specific columns. If facts need mapping references, that should be done through accepted mapping state or explicit report joins, not provider-specific fact fields.

## Test implications

The follow-on task should include tests for:

- dry-run validation and scope boundaries;
- schema/state artifact existence and basic constraints;
- proposal immutability vs accepted mapping state;
- confidence band routing;
- high-impact review routing;
- unit metadata quality and comparability caveats;
- annual/quarterly non-aggregation;
- supersession lineage;
- deterministic fixture-backed GDP proposal report;
- no live/default `macro` writes.

## Rejected alternatives

### Manual canonical indicator registry as default

Rejected. It scales poorly and conflicts with DEC-016. Manual governance remains for policies, high-impact review, exceptions, audits, and schema/model changes.

### Report-local metadata only

Rejected as the primary design. Report-local caveats are useful but do not create reusable governed mapping state for future reports and source onboarding.

### Provider codes as canonical identities

Rejected. It conflicts with DEC-010/DEC-011 and would make provider representations canonical.

### Immediate unit conversion engine

Rejected. MacroForge first needs explicit unit/comparability metadata and quality flags. Conversion requires a later accepted design.

### New source or framework extraction before canonicalization state

Rejected. More sources and frameworks would increase semantic debt before the current source substrate can represent mapping/comparability honestly.

### Opaque model output directly into curated facts

Rejected. Automated output must be captured as proposal evidence and accepted/provisional mapping state before it affects curated facts or reports.

## Acceptance criteria for follow-on implementation

The follow-on task is accepted only if it:

- starts with a fresh implementation dry-run;
- remains bounded to existing WDI/OECD/Eurostat fixture evidence;
- implements minimal state/proposal/mapping/versioning mechanics only;
- writes deterministic audit artifacts;
- keeps unit conversion, aggregation, new sources, live fetches, framework extraction, dashboards, and broad ontology work out of scope;
- runs full tests and generated-project coherence after state/handoff/summary updates.
