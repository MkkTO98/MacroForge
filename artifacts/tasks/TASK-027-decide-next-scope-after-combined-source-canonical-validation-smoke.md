# TASK-027 — Decide next scope after combined-source canonical validation smoke

Status: complete
Created: 2026-06-04
Completed: 2026-06-04
Depends on: TASK-026
Relevant decisions: DEC-005, DEC-007, DEC-011, DEC-013

## Objective

Review MacroForge after TASK-026 proved WDI, OECD/SDMX, and Eurostat can coexist in one isolated PostgreSQL database with canonical facts, dimensions, provider mappings, lineage, and quality checks.

Decide the next bounded scope before implementing any new source, framework, mart/research layer, orchestration, or schema refinement.

## Inputs

Use at minimum:

- TASK-026 outcome and combined source report;
- `artifacts/reports/combined-source-canonical-smoke-20260604.json`;
- DEC-013;
- current schema/loader/test state;
- active project state and architecture state.

## Questions to answer

1. Has the three-source canonical substrate reached enough reliability to start a first research/mart/query slice?
2. If not, what single reliability gap should be addressed next?
3. Do current source-specific loaders still remain preferable to framework extraction?
4. Is any schema refinement justified by TASK-026 evidence, or should schema remain unchanged?
5. Should the next scope be:
   - governance/design for a first research-facing output;
   - bounded reliability/reporting hardening;
   - source coverage expansion;
   - schema refinement;
   - or framework extraction?

## Acceptance criteria

- Create a fresh governance dry-run before edits.
- Record an accepted decision artifact.
- Create exactly one next implementation/design task.
- Do not implement the chosen next scope in this task.
- Update state, backlog, summaries, and handoff.
- Run full tests and ProjectForge coherence.

## Explicit non-goals

Do not:

- add a source;
- add a migration;
- implement mart/research outputs;
- implement a generalized ingestion framework;
- live-fetch sources;
- write to live/default `macro`;
- push to git.


## Outcome

TASK-027 is complete.

DEC-014 accepts the user's preferred next scope: create the first minimal research-facing output from existing canonical data.

The follow-on task is TASK-028 — Implement first canonical GDP snapshot report.

Decision summary:

- Next scope: small deterministic canonical GDP snapshot/audit report.
- Purpose: validate that canonical facts can support analysis without source-specific leakage.
- Use only `curated.*` canonical tables plus `meta.*` source/dataset/lineage/quality metadata for core report queries.
- Do not query staging tables except optional explicitly labeled audit/debug sections.
- Include coverage, missingness, source lineage, duplicate-grain checks, and quality status.
- Use an isolated or clearly safe database path.
- Add report-generation tests.
- Do not add sources, extract a generalized ingestion framework, or broadly refactor schema.

Verification will be recorded after closeout updates.
