# DEC-014 — First minimal research-facing canonical output

Status: accepted
Date: 2026-06-04
Related task: TASK-027
Preceded by: TASK-026
Follow-on task: TASK-028
Governing context: DEC-005, DEC-007, DEC-011, DEC-013

## Decision

MacroForge will next implement a first minimal research-facing output from the existing canonical data.

The follow-on implementation task is:

- TASK-028 — Implement first canonical GDP snapshot report.

TASK-028 should produce a small deterministic report artifact from current canonical facts and source/lineage metadata. The report should validate that MacroForge's canonical substrate can support basic analysis without source-specific leakage.

The accepted report shape is a boring canonical GDP snapshot/audit report, not a broad research layer. It should include:

- country GDP comparison across available canonical GDP observations;
- source coverage summary;
- missingness / expected-coverage notes for the bounded fixture universe;
- source lineage summary;
- duplicate-grain check;
- annual-vs-quarterly coexistence notes where the current bounded data permits them.

## Why this option now

TASK-026 proved that WDI, OECD/SDMX, and Eurostat can coexist in one isolated PostgreSQL database with:

- 3 sources;
- 3 dataset releases;
- 20 canonical fact rows;
- 0 duplicate fact grains;
- 0 failing quality checks;
- annual and quarterly periods;
- WDI/OECD/Eurostat canonical territories;
- source lineage and provider mapping coverage.

That is enough reliability to ask the next product question: can canonical facts support a useful research/reporting artifact without querying source-specific staging tables or leaking provider-specific structures into analysis?

This is the smallest useful step toward MacroForge's research-platform purpose. It is more valuable now than adding another source because it tests the canonical layer's analytical usefulness. It is also safer than a mart/research framework because it can be one explicit report generator with clear SQL and tests.

## Why not another source

Another source would increase ingestion breadth before MacroForge has proven that the current canonical substrate produces analysis. TASK-026 already validated three-source coexistence. The next unknown is not whether more source shapes can be loaded; it is whether current canonical facts, dimensions, lineage, and quality metadata are useful for a first research-facing artifact.

New source onboarding remains deferred.

## Why not framework extraction

The current source-specific loader posture remains preferable.

TASK-026 did not reveal enough repeated source-semantic boilerplate to justify a generalized ingestion framework. The immediate next work should query canonical tables after loading, not abstract loaders. Framework extraction remains deferred until repeated analytical/reporting or refresh workflows demonstrate stable common mechanics that can be extracted without hiding source semantics.

## Why not broad schema refactoring

No broad schema refinement is accepted.

TASK-026 passed with the current canonical-domain schema. The first research-facing report may reveal future needs around indicator ontology, unit comparability, frequency aggregation, aggregate territories, or mart tables, but those should be observed through a small report first rather than preemptively designed.

TASK-028 may add report code/tests and report artifacts only. It must not add migrations or modify canonical schema unless it discovers a direct blocker, in which case it should stop and open a separate governance task rather than refactor broadly.

## Accepted TASK-028 scope

TASK-028 may add:

- a fresh implementation dry-run;
- RED/GREEN tests for report generation;
- a small report module/script;
- deterministic report artifact(s) under `artifacts/reports/`;
- small source-agnostic SQL/query helpers if they remain report-specific and mechanical;
- documentation/state/handoff updates required for closeout.

The report must:

- use only canonical tables plus `meta` source, dataset, lineage, and quality metadata for analysis;
- avoid staging-table queries except for explicitly labeled audit/debug sections, and default to no staging-table dependency;
- produce deterministic output from a known isolated or clearly safe database path;
- include coverage, missingness, source lineage, and duplicate-grain checks;
- keep the analytical scope small and boring;
- preserve source-specific loaders and existing schemas.

A suitable implementation strategy is to reuse the TASK-026 isolated combined-source database setup, then run report queries only against `curated.*` and `meta.*` tables.

## Rejected scope / non-goals

DEC-014 does not approve:

- new source onboarding;
- FRED onboarding;
- live source fetches;
- live/default `macro` writes;
- generalized source/plugin/JSON-stat/SDMX ingestion framework;
- broad schema refactoring;
- new migrations;
- provider-specific fact columns;
- aggregate membership history;
- unit conversion framework;
- canonical indicator ontology;
- mart schema implementation;
- dashboard/UI/notebook work;
- orchestration or scheduling;
- git push.

## Reconsideration triggers

Reopen governance before or after TASK-028 if:

- a canonical-only report cannot answer basic coverage/missingness/lineage questions without staging tables;
- unit comparability blocks even descriptive GDP reporting;
- indicator identity is too provider-specific for a meaningful canonical report;
- annual/quarterly coexistence cannot be represented clearly without new frequency/aggregation policy;
- duplicate-grain or lineage checks fail under the combined canonical database;
- report SQL requires substantial copy/paste or hidden assumptions that suggest a mart/query layer design is needed.

## Evidence reviewed

Context bundle:

- `context/active_context.md`
- `context/context_audit.md`
- `context/context_audit.json`

The compact governance context exceeded the default budget, so TASK-027 used justified `project_wide_review` mode under the context policy:

- context mode: `project_wide_review`;
- estimated tokens: 21767;
- budget tokens: 64000;
- within budget: true;
- raw logs excluded: true;
- summaries used: true.

Implementation/report evidence:

- `artifacts/reports/combined-source-canonical-smoke-20260604.json`:
  - status `succeeded`;
  - sources: `EUROSTAT_NAMQ_GDP`, `OECD_NAAG`, `WDI`;
  - 20 canonical fact rows;
  - 0 duplicate fact grains;
  - 0 failing quality checks;
  - canonical frequencies `A` and `Q`;
  - canonical territories `AUS`, `DEU`, `DNK`, `FRA`, `USA`.
- TASK-026 outcome and handoff.
- DEC-013 post-third-source architecture review.
- User direction in TASK-027: prefer first minimal research-facing output; no new sources; no generalized ingestion framework; no broad schema refactoring unless directly required.

## Consequences

MacroForge advances from canonical-substrate validation to the first explicit research/reporting artifact.

The next task remains intentionally narrow. If TASK-028 succeeds, MacroForge will have evidence that the canonical tables support analysis. If TASK-028 exposes gaps, those gaps should become focused governance decisions rather than being solved through broad schema or framework work inside the report task.

No implementation was performed under TASK-027.
No git push was performed.
