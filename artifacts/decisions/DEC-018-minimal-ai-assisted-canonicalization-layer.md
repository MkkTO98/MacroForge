# DEC-018 — Accept minimal AI-assisted canonicalization layer design

Status: accepted
Date: 2026-06-05
Related task: TASK-030
Follow-on task: TASK-032
Design note: `docs/architecture/minimal-ai-assisted-canonicalization-layer.md`
Preceded by: DEC-015, DEC-016

## Decision

MacroForge accepts the TASK-030 design for a minimal AI-assisted canonicalization and comparability layer.

The accepted architecture is conceptual and governance-level. It defines how MacroForge should move from provider indicator evidence to governed canonical mapping state without making humans manually define and approve every provider indicator.

Accepted flow:

```text
Provider Indicator Evidence
-> Canonicalization Run
-> Mapping Proposal or Canonical-Creation Proposal
-> Confidence / Reasoning / Evidence / Version
-> Human Review for exceptions
-> Accepted or Provisional Mapping State
-> Canonical Indicator Concept
-> Curated Facts / Reports through governed mapping state
```

## Accepted conceptual entities

The next implementation should design and test a minimal state surface for:

1. provider indicator evidence;
2. canonicalization run records;
3. canonical indicator concepts;
4. mapping proposals;
5. canonical creation proposals;
6. unit/comparability profiles;
7. review status/queue routing;
8. accepted/provisional mapping state;
9. re-canonicalization and supersession lineage.

## Rationale

TASK-028 proved canonical/meta-only reporting mechanics, but it also showed that current GDP observations are only informally comparable:

- OECD `B1GQ`;
- Eurostat `B1GQ`;
- WDI `NY.GDP.MKTP.CD`;
- units `CP_MEUR`, `USD_EXC`, `USD_PPP`, and WDI `unknown`;
- annual and quarterly observations in one report without conversion or aggregation.

DEC-015 correctly selected indicator/unit comparability design as the next semantic step. DEC-016 correctly refined that step away from manual-every-indicator governance and toward AI-assisted auditable canonicalization.

The accepted design keeps humans in the governance loop where they have leverage: policy, thresholds, high-impact concepts, low-confidence/conflicting cases, new canonical concept proposals, audit samples, schema/model changes, and material re-canonicalization. It rejects a workflow where every provider indicator creates a manual mapping task.

## Required implementation direction

TASK-032 should implement only the smallest fixture-backed state foundation needed to prove the design against existing bounded WDI/OECD/Eurostat GDP evidence.

Required properties:

- fresh implementation dry-run before edits;
- no live/default `macro` writes;
- no live source fetches;
- no new source onboarding;
- no report expansion beyond a bounded audit artifact;
- no unit conversion;
- no quarterly-to-annual aggregation;
- no generalized ingestion/source framework;
- no provider-specific fact columns;
- proposal state separate from accepted mapping state;
- accepted/provisional mapping state versioned from the start;
- unit metadata quality and comparability caveats represented explicitly;
- deterministic tests and audit artifacts.

## Required review posture

Confidence scores and bands are routing metadata, not truth.

Review should be required for:

- low-confidence mappings;
- conflicting proposals;
- high-impact concepts such as GDP, CPI, unemployment, policy rates, and fiscal balances;
- new canonical concept creation;
- unknown or conflicting unit metadata where comparability matters;
- changed accepted mappings that affect existing facts or reports;
- re-canonicalization proposals.

Auto-accept candidates may be represented but should not become broad automatic acceptance until MacroForge has calibration evidence and explicit policy.

## Consequences

TASK-030 is complete after this decision and closeout updates.

The next active domain task is TASK-032: implement the minimal canonicalization state foundation from existing bounded fixture evidence.

This decision does not approve:

- implementation under TASK-030;
- schema changes outside TASK-032;
- broad canonical ontology work;
- model/LLM canonicalization calls;
- new sources;
- live fetches;
- live/default `macro` writes;
- unit conversion;
- frequency aggregation;
- mart/dashboard work;
- generalized source or ingestion framework extraction;
- git push.

## Reconsideration triggers

Reopen this decision if:

- provider metadata remains too sparse to generate useful proposals even for bounded fixtures;
- mapping confidence cannot be made auditable or calibrated;
- accepted mapping versioning destabilizes fact/report reproducibility;
- review queues become equivalent to full manual governance;
- unit/comparability semantics require a larger measurement model before any small implementation is safe;
- source onboarding proves canonicalization cannot remain separate from ingestion framework design.

## Evidence reviewed

- `artifacts/reports/canonical-gdp-snapshot-20260604.md`
- `artifacts/decisions/DEC-015-next-scope-canonical-indicator-unit-comparability.md`
- `artifacts/decisions/DEC-016-ai-assisted-canonicalization-layer.md`
- `docs/architecture/ai-assisted-canonicalization-governance-review.md`
- `artifacts/tasks/TASK-030-design-minimal-canonical-indicator-unit-comparability.md`
- `simulation/dry_runs/20260605_212556-dry-run.md`

## Verification expectation

Closeout must update task/backlog/state/architecture/roadmap/handoff/summaries, then run full tests and generated-project coherence.
