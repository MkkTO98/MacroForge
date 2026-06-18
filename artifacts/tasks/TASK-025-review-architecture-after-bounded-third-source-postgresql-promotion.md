# TASK-025 — Review architecture after bounded third-source PostgreSQL promotion

Status: complete
Created: 2026-06-04
Completed: 2026-06-04
Depends on: TASK-024
Relevant decisions: DEC-005, DEC-007, DEC-010, DEC-011, DEC-012
Outcome decision: DEC-013
Follow-on task: TASK-026

## Objective

Review MacroForge's architecture after three bounded source-specific PostgreSQL slices exist or are represented in the database path:

- WDI first-source vertical slice;
- OECD/SDMX second-source bounded loader;
- Eurostat `namq_10_gdp` bounded third-source loader.

Decide the next bounded scope before any additional implementation.

## Required review questions

- Does three-source pressure justify extracting more shared mechanics, or should source-specific loaders remain mostly separate?
- Are the TASK-022 canonical period/territory/provider mapping tables sufficient after Eurostat implementation evidence?
- Is the next best step:
  - another source spike,
  - small helper extraction,
  - validation/reporting hardening,
  - schema refinement,
  - first research/mart slice,
  - or a different bounded governance task?
- What should remain explicitly deferred?

## Expected output

- Governance context bundle and audit. Completed with justified `project_wide_review` context because compact governance context exceeded budget.
- Dry-run report for the governance review. Completed: `simulation/dry_runs/20260604_172528-task-025-post-third-source-architecture-review.md`.
- Architecture review note or decision artifact. Completed: `artifacts/decisions/DEC-013-post-third-source-architecture-and-next-scope.md`.
- Follow-on task artifact for the selected next scope. Completed: `artifacts/tasks/TASK-026-implement-combined-source-canonical-validation-smoke.md`.
- State/backlog/roadmap/handoff/summary updates. Completed during TASK-025 closeout.
- Final tests and coherence. Completed after governance updates.

## Boundaries

TASK-025 is governance-only unless a follow-on task explicitly authorizes implementation.

Do not:

- add new loaders;
- add migrations;
- generalize JSON-stat/source/plugin framework;
- onboard FRED;
- write to live `macro`;
- change fact grain;
- implement mart/research outputs;
- push to git.


## Outcome

DEC-013 keeps the current source-specific raw-SQL/PostgreSQL/psql architecture after the bounded third-source database path.

Three source paths justify a combined-source canonical validation smoke, not a generalized ingestion framework.

TASK-026 is opened as the next bounded implementation task. It should prove WDI, OECD/SDMX, and Eurostat coexist in one isolated PostgreSQL database, with combined canonical fact/dimension/provider mapping/lineage/quality checks and a single report artifact.

Deferred until a later accepted decision:

- live `macro` writes;
- live source fetches;
- FRED onboarding;
- new source spikes;
- generalized source/plugin/JSON-stat/SDMX framework;
- provider-specific fact columns;
- aggregate membership history;
- unit conversion framework;
- canonical indicator ontology;
- mart/research implementation;
- orchestration/scheduling;
- git push.
