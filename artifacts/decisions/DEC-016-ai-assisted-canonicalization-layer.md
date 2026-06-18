# DEC-016 — TASK-030 refinement: AI-assisted auditable canonicalization layer

Status: accepted
Date: 2026-06-04
Related task: TASK-030
Refines: DEC-015
Design note: `docs/architecture/ai-assisted-canonicalization-governance-review.md`

## Decision

TASK-030 will be modified rather than continued unchanged or replaced.

The modified TASK-030 should design a minimal AI-assisted auditable canonicalization layer for provider indicators and units. It should not design a traditional manual canonical indicator registry where every new provider indicator requires manual canonical concept creation or manual approval.

DEC-015 remains valid as the identification of the semantic gap exposed by TASK-028:

- MacroForge can now generate a canonical/meta-only GDP snapshot report.
- That report exposes that OECD `B1GQ`, Eurostat `B1GQ`, and WDI `NY.GDP.MKTP.CD` are GDP-ish but not yet explicitly mapped to a shared canonical concept or comparable unit semantics.

DEC-016 refines the solution direction:

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

## Rationale

MacroForge's original purpose is a long-lived AI-first macroeconomic and investing research platform, not a conventional manually curated data warehouse.

The long-term platform should ingest heterogeneous public datasets and normalize them into a canonical analytical model at scale. If canonical indicators are manually created and mapped provider-by-provider, source expansion eventually becomes a manual taxonomy/governance bottleneck.

The correct governance posture is not to eliminate human governance. It is to move human governance up the leverage curve:

- define policies, thresholds, and canonicalization rules;
- audit uncertain, conflicting, low-confidence, or high-impact mappings;
- review new canonical concept proposals;
- inspect samples of auto-accepted mappings;
- approve schema/model changes;
- preserve reproducibility and mapping history.

At scale, automated canonicalization should propose mappings and canonical concept creation using provider metadata, descriptions, code-list context, units, dimensions, and source evidence. Humans should review exceptions and policy-sensitive cases.

## Required TASK-030 direction

TASK-030 must design, at conceptual level only, the minimum architecture needed for:

1. automatic canonical indicator mapping;
2. automatic canonical indicator creation proposals;
3. mapping confidence scores and confidence bands;
4. mapping reasoning/evidence storage;
5. mapping provenance, including model/ruleset/prompt version;
6. human review queue/status for exceptions;
7. accepted mapping state that can gate curated facts;
8. future re-canonicalization and supersession when improved logic becomes available.

The design should preserve these fields for each proposed mapping when available:

- provider code;
- provider dataset/collection;
- provider description/title;
- provider metadata and dimensions;
- provider unit metadata;
- canonical target candidate;
- relationship type;
- confidence score/band;
- reasoning/evidence;
- timestamp/version;
- canonicalization run id;
- review status;
- supersession lineage.

## Required distinction

TASK-030 must explicitly distinguish:

- canonical concepts as durable analytical identities;
- mapping proposals as generated, auditable hypotheses;
- accepted mappings as governed state;
- curated facts as analytical facts that should reference accepted/provisional mapping state according to policy.

## Traditional manual model assessment

The traditional data-warehouse governance model is acceptable for a small number of high-value indicators, but it does not align with MacroForge's scaling goal.

It is retained only for:

- policy definition;
- high-impact concept review;
- uncertain mappings;
- new canonical concept review;
- audit sampling;
- exception handling.

It is rejected as the default path for all provider indicators.

## AI-assisted model assessment

The AI-assisted canonicalization model better aligns with MacroForge because it:

- scales across many sources and indicators;
- preserves audit evidence;
- supports confidence-based review routing;
- enables reproducible re-canonicalization;
- allows source expansion without linear manual mapping burden;
- keeps humans focused on governance rather than clerical mapping.

## Scope still not approved

DEC-016 does not approve:

- implementation;
- PostgreSQL migrations;
- schema changes;
- report code;
- new source onboarding;
- live source fetches;
- live/default `macro` writes;
- unit conversion implementation;
- quarterly-to-annual aggregation;
- mart/dashboard work;
- generalized ingestion framework extraction;
- provider-specific fact columns;
- git push.

## TASK-030 acceptance criteria after refinement

TASK-030 should be considered successful if it produces:

- a design note for the minimal auditable AI-assisted canonicalization layer;
- a decision artifact accepting or deferring the design;
- at most one follow-on implementation task if accepted;
- explicit required-vs-deferred architecture boundaries;
- example handling for existing GDP evidence, without making GDP a manual special case;
- final state/handoff/summary updates and verification.

## Reconsideration triggers

Reopen this decision if:

- provider metadata is too sparse to support useful automated proposals;
- confidence scoring cannot be made auditable or calibrated;
- accepted mappings cannot be versioned without destabilizing curated facts;
- human review queues become as heavy as full manual governance;
- future source onboarding reveals that canonicalization and ingestion framework design cannot be separated.

## Consequences

TASK-030 remains the active next design task, but its orientation changes.

Before DEC-016, TASK-030 could be read as a small manual GDP canonical concept/unit comparability design.

After DEC-016, TASK-030 is a scalable governance/architecture design task for auditable automated canonicalization, with current GDP observations serving as the seed evidence case.

No implementation was performed under this review.
No migrations or schema changes were performed.
No git push was performed.
