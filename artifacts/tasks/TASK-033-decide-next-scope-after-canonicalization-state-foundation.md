# TASK-033 — Decide next scope after minimal canonicalization state foundation

Status: complete
Created: 2026-06-05
Completed: 2026-06-05
Depends on: TASK-032
Governing decisions: DEC-019, DEC-018, DEC-016, DEC-015
Decision: `artifacts/decisions/DEC-019-next-scope-deterministic-canonicalization-proposal-workflow.md`
Decision analysis: `docs/architecture/canonicalization-next-scope-decision-analysis.md`
Follow-on task: `artifacts/tasks/TASK-034-implement-tiny-deterministic-canonicalization-proposal-workflow.md`

## Objective

Review TASK-032 results and decide the next bounded MacroForge scope after the minimal canonicalization state foundation.

The decision should use the generated audit artifact, tests, and existing design boundaries to choose whether MacroForge should next enrich provider evidence, promote canonicalization state into PostgreSQL schema, add deterministic proposal/report integration, calibrate review policy, or defer canonicalization work in favor of another bounded research/data task.

## Scope allowed

TASK-033 may create:

- a fresh governance dry-run;
- a decision note or architecture note if needed;
- one decision artifact accepting the next bounded scope;
- at most one follow-on task;
- state/backlog/roadmap/handoff/summary updates required for closeout.

## Required context

- `artifacts/reports/canonicalization-state-foundation-20260605.json`
- `src/macroforge/canonicalization_state.py`
- `tests/test_canonicalization_state.py`
- `docs/architecture/minimal-ai-assisted-canonicalization-layer.md`
- DEC-018, DEC-016, DEC-015
- TASK-032 outcome

## Questions to answer

1. Did TASK-032 prove enough state mechanics to justify a PostgreSQL migration next, or should file-backed canonicalization state remain the next iteration boundary?
2. Is the next blocker provider evidence richness, unit metadata, review policy calibration, report integration, or schema persistence?
3. Should WDI unit evidence be enriched before broader canonicalization mechanics?
4. Should any auto-accept behavior remain deferred until reviewed examples exist?
5. What is the smallest next task that improves semantic correctness without adding sources, model calls, conversion, aggregation, or a broad ontology/framework?

## Acceptance criteria

- Fresh governance dry-run is created and validated before edits.
- TASK-032 audit artifact and tests are inspected.
- A decision artifact records the selected next scope and rejected alternatives.
- At most one follow-on task is opened.
- State/backlog/architecture/roadmap/handoff/summaries are updated.
- Full tests and generated-project coherence pass after closeout.

## Outcome

TASK-033 completed DEC-019 and `docs/architecture/canonicalization-next-scope-decision-analysis.md`.

Decision: choose option A, a tiny deterministic proposal-generation workflow over the existing bounded GDP fixture set. The choice optimizes uncertainty reduction over capability by validating the TASK-032 canonicalization workflow before AI/model dependence, PostgreSQL persistence, additional state expansion, report integration, or new sources.

Follow-on task: TASK-034.

## Explicit non-goals

Do not:

- implement code or migrations under TASK-033;
- call models for canonicalization;
- onboard a new source;
- live-fetch sources;
- write to live/default `macro`;
- implement unit conversion;
- aggregate quarterly to annual;
- create a mart/dashboard/UI/notebook;
- extract a generalized ingestion/source framework;
- add provider-specific fact columns;
- push to git.
