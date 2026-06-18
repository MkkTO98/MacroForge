# TASK-030 — Design minimal AI-assisted canonicalization and comparability layer

Status: complete
Created: 2026-06-04
Completed: 2026-06-05
Depends on: TASK-029
Governing decisions: DEC-015, DEC-016, DEC-018
Primary design review: `docs/architecture/ai-assisted-canonicalization-governance-review.md`
Final design: `docs/architecture/minimal-ai-assisted-canonicalization-layer.md`
Outcome decision: `artifacts/decisions/DEC-018-minimal-ai-assisted-canonicalization-layer.md`
Follow-on task: `artifacts/tasks/TASK-032-implement-minimal-canonicalization-state-foundation.md`

## Objective

Design the smallest auditable AI-assisted canonicalization layer needed for provider indicators, canonical indicator concepts, unit/comparability metadata, mapping confidence, provenance, and future re-canonicalization.

The goal is not to manually create a canonical GDP concept registry. The goal is to decide how MacroForge should scale from provider indicator evidence to governed canonical mappings without requiring humans to manually define and approve every provider indicator.

The design should support this long-term flow:

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

## Background

TASK-028 proved that MacroForge can generate a deterministic canonical GDP snapshot/audit report from `curated.*` plus `meta.*` only.

The report exposed a semantic gap:

- OECD `B1GQ` and Eurostat `B1GQ` are GDP-ish provider indicators but do not yet share an explicit MacroForge canonical economic concept.
- WDI `NY.GDP.MKTP.CD` is GDP current USD, but currently appears alongside provider-specific GDP codes without a canonical concept mapping.
- Units differ across `CP_MEUR`, `USD_EXC`, `USD_PPP`, and WDI's current `unknown` unit representation.
- Annual and quarterly rows coexist correctly but must not imply aggregation or direct comparability.

DEC-016 refined the TASK-030 direction: this semantic gap should not be solved by assuming manual canonical indicator maintenance. MacroForge's long-term objective is an AI-assisted macroeconomic knowledge system that can scale across many sources and indicators while preserving auditability and reproducibility.

## Scope allowed

TASK-030 may create:

- a fresh governance/design dry-run;
- a design note under `docs/architecture/`, for example `minimal-ai-assisted-canonicalization-layer.md`;
- a decision artifact accepting or deferring the proposed canonicalization architecture;
- exactly one follow-on implementation task if appropriate;
- state/backlog/roadmap/handoff/summary updates required for closeout.

## Questions to answer

1. What is the minimum canonicalization architecture needed to avoid manual provider-indicator governance at scale?
2. What evidence should be stored for each provider indicator?
   - provider code;
   - provider dataset/collection;
   - provider title/name;
   - provider description/methodology;
   - provider metadata/dimensions/code-list context;
   - unit/frequency/territory hints;
   - source URLs and raw artifact/checksum references.
3. What is the minimum canonical indicator concept representation?
4. How should automated mapping proposals be represented?
   - canonical target candidate;
   - relationship type;
   - confidence score;
   - confidence band;
   - reasoning/evidence;
   - method/model/ruleset/prompt version;
   - timestamp/run id.
5. How should automatic canonical indicator creation proposals be represented when no existing concept fits?
6. What review states and thresholds are needed?
   - auto-accept candidate;
   - review required;
   - rejected/no match;
   - high-impact always-review;
   - conflicting proposals.
7. How should accepted mappings gate or annotate curated facts?
8. How should unit/comparability semantics be handled without implementing conversion?
   - currency;
   - scale/multiplier;
   - price basis/current-vs-real;
   - PPP vs exchange-rate basis;
   - provider unit code;
   - unknown/incomplete unit metadata quality.
9. How should annual and quarterly GDP rows remain explicit without accidental aggregation?
10. How should mapping versions support future re-canonicalization when improved logic becomes available?
11. What should be implemented next, and what should remain deferred?

## Required design output

The design note should include:

- problem statement from TASK-028 and DEC-016 evidence;
- principles for AI-assisted canonicalization;
- comparison against a traditional manual warehouse governance model;
- minimal conceptual data model proposal;
- required-vs-deferred scope;
- example mapping-proposal flow for existing bounded fixtures:
  - OECD `B1GQ`;
  - Eurostat `B1GQ`;
  - WDI `NY.GDP.MKTP.CD`;
  - observed units `CP_MEUR`, `USD_EXC`, `USD_PPP`, and WDI current `unknown`;
- how confidence, reasoning, evidence, and provenance are stored;
- how human review focuses on exceptions and high-impact/low-confidence cases;
- re-canonicalization and supersession rules;
- rejected alternatives;
- migration/code implications if accepted;
- test implications;
- acceptance criteria for the follow-on implementation task.

## Acceptance criteria

- Create and validate a fresh dry-run before edits.
- Use TASK-028 report evidence, DEC-015, DEC-016, and the AI-assisted governance review as primary context.
- Produce a bounded design note.
- Record an accepted or explicitly deferred decision.
- Create no more than one follow-on task.
- Do not implement migrations or code under TASK-030 unless a new task explicitly supersedes this scope.
- Update task/backlog/state/architecture/roadmap/handoff/summaries.
- Run full tests and ProjectForge coherence.

## Explicit non-goals

Do not:

- add a new source;
- live-fetch sources;
- write to live/default `macro`;
- add a PostgreSQL migration;
- implement report code;
- implement unit conversion;
- aggregate quarterly to annual;
- create a mart schema;
- create a dashboard/UI/notebook;
- extract a generalized ingestion framework;
- add provider-specific fact columns;
- push to git.

Also do not design TASK-030 as a manual approval workflow for every provider indicator. Governance should focus on policies, thresholds, auditability, high-impact concepts, and exceptional/low-confidence cases.

## Notes

Keep the design small and boring, but make the scaling posture explicit. The immediate GDP case is the seed evidence, not a reason to hard-code GDP or to create a permanently manual taxonomy process.


## Pre-task governance review completed

A governance review was completed before executing TASK-030 implementation/design work.

Files created by the review:

- `simulation/dry_runs/20260604_233107-pre-task-030-ai-assisted-canonicalization-governance-review.md`
- `docs/architecture/ai-assisted-canonicalization-governance-review.md`
- `artifacts/decisions/DEC-016-ai-assisted-canonicalization-layer.md`

Files updated by the review closeout:

- `artifacts/tasks/TASK-030-design-minimal-canonical-indicator-unit-comparability.md`
- `artifacts/tasks/backlog.md`
- `state/active_goal.md`
- `state/project_state.md`
- `state/architecture.md`
- `docs/roadmap.md`
- affected `_SUMMARY.md` files
- `context/latest_handoff.md`

Outcome:

- TASK-030 remains open.
- TASK-030 was modified by DEC-016 to target a minimal AI-assisted auditable canonicalization and comparability layer.
- TASK-030 should not proceed as a manual canonical indicator registry or a manual approval workflow for every provider indicator.

Verification already run for the review closeout:

```text
PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests -q && python3 tools/check_coherence.py --project . --json

..................................................                       [100%]
50 passed in 5.64s
{
  "mode": "generated",
  "blocks": [],
  "warnings": []
}
```

Remaining risks for TASK-030:

- provider metadata may be too sparse for reliable automated proposals in some sources;
- confidence scores must be treated as routing signals, not truth;
- accepted mapping state and re-canonicalization versioning must be designed before implementation;
- auto-accept thresholds and high-impact always-review rules need explicit policy.

Next recommended task:

Proceed with TASK-030 as refined by DEC-016: produce the bounded design note and decision artifact for the minimal AI-assisted canonicalization layer. Do not implement migrations, schema changes, code, source onboarding, or reports under TASK-030.


Session-closeout final verification:

```text
PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests -q && python3 tools/check_coherence.py --project . --json

..................................................                       [100%]
50 passed in 5.45s
{
  "mode": "generated",
  "blocks": [],
  "warnings": []
}
```
