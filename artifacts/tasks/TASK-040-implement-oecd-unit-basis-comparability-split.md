# TASK-040 — Implement OECD unit-basis comparability split for canonicalization evidence

Status: complete
Created: 2026-06-18
Depends on: TASK-039
Governing evidence: TASK-038 lifecycle validation; TASK-039 deferred mapping advancement requirements
Dry-run: `simulation/dry_runs/20260618_120000-task-040-oecd-unit-basis-comparability.md`

## Objective

Implement a bounded deterministic OECD unit-basis comparability split for existing GDP canonicalization evidence so future mapping advancement can distinguish OECD `USD_EXC` and `USD_PPP` basis evidence without reinterpreting the full lifecycle artifact.

## Why this task

TASK-039 records OECD `B1GQ` as deferred because MacroForge lacks an explicit unit-basis policy distinguishing exchange-rate USD from PPP USD. This is the highest-value next implementation step because it advances canonical mapping/comparability capability while remaining bounded, deterministic, source-specific, and non-authoritative.

## Recurring effort reduced

- Canonical mapping: makes OECD unit-basis differences machine-readable rather than prose-only caveats.
- Validation: adds deterministic checks that each OECD unit profile remains separate and no single comparable GDP mapping is silently approved.
- Provider integration: improves handling of existing OECD provider metadata without onboarding a new source.
- Future agent recovery/context: creates compact JSON/Markdown artifacts that start from TASK-039 requirements.

## Scope allowed

This task may:

- add fixture-backed tests for OECD basis splitting;
- add deterministic helper/writer functions in `src/macroforge/canonicalization_state.py`;
- create a bounded JSON artifact under `artifacts/reports/`;
- create a concise Markdown artifact under `artifacts/reports/`;
- update task/backlog/state/handoff/summaries.

## Explicit non-goals

Do not:

- mutate accepted/base mapping state;
- mutate `artifacts/manifests/canonical_assets.json`;
- auto-apply mapping updates;
- call AI/models;
- live-fetch data;
- write to live/default `macro`;
- add migrations or PostgreSQL canonicalization persistence;
- implement currency/unit conversion;
- aggregate quarterly to annual;
- integrate GDP snapshot/report behavior;
- create basis-specific canonical concepts as accepted truth;
- generalize a provider/source metadata framework;
- add provider-specific fact columns;
- push to git.

## Acceptance criteria

- Dry-run validates before source edits.
- RED test fails because the OECD unit-basis comparability writer/helper does not exist yet.
- Deterministic artifact records separate OECD `USD_EXC` and `USD_PPP` basis candidates for existing `B1GQ` evidence.
- Artifact states that no conversion, aggregation, report integration, auto-apply, accepted/base state mutation, or manifest base mutation occurred.
- Artifact explicitly links to TASK-039 advancement requirements.
- Artifact includes checks proving basis separation, caveat preservation, no accepted-state mutation, no auto-apply, no conversion, and no report integration.
- JSON and Markdown artifacts are generated and read back.
- Targeted tests, full tests, coherence, and context-health pass after closeout edits.

## Outcome

Complete. TASK-040 added deterministic OECD unit-basis comparability helpers and tests, generated `artifacts/reports/canonicalization-oecd-unit-basis-comparability-20260618.json` and `.md`, and recorded separate `USD_EXC` exchange-rate and `USD_PPP` PPP comparability candidates for existing OECD `B1GQ` GDP evidence. The output preserves TASK-039 boundaries: no accepted/base mapping state mutation, no canonical asset manifest mutation, no report integration, no auto-apply, no unit/currency conversion, no frequency aggregation, no model calls, no live fetches, no migrations, and no live/default `macro` writes.

Closeout evidence: full tests passed (`70 passed in 4.84s`), coherence passed with no blocks, context health passed with no blocks, recovery reported no blockers or pending questions, unrelated deterministic report churn was restored, and the implementation was committed locally as `58492f7 Add OECD unit-basis comparability evidence`.
