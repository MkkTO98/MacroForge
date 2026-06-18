# DEC-013 — Post-third-source architecture and next scope

Status: accepted
Date: 2026-06-04
Related task: TASK-025
Preceded by: TASK-024
Governing context: DEC-005, DEC-007, DEC-010, DEC-011, DEC-012
Follow-on task: TASK-026

## Decision

MacroForge will keep its source-specific raw-SQL/PostgreSQL/psql architecture after the bounded third-source PostgreSQL promotion.

Three implemented or database-backed source paths now justify one bounded cross-source reliability step, but they still do not justify a generalized ingestion framework, plugin registry, generalized JSON-stat framework, ORM, migration framework, orchestration platform, mart/research layer, or FRED onboarding.

The next implementation scope is:

- TASK-026 — Implement combined-source canonical validation smoke.

TASK-026 should create a single isolated PostgreSQL smoke path that applies all current migrations, runs the existing bounded loaders/evidence for WDI, OECD/SDMX, and Eurostat into the same temporary database, and writes a combined canonical data-health report.

## Answers to TASK-025 review questions

### 1. Do three sources justify extracting more shared mechanics?

Yes, but only shared reliability/reporting mechanics, not a source framework.

The evidence now includes:

- WDI source-specific PostgreSQL vertical slice;
- OECD/SDMX source-specific staging and curated load;
- Eurostat source-specific staging and curated load;
- canonical period/territory/provider mapping schema from TASK-022;
- tiny mechanical helpers from TASK-017.

This is enough to prove that a combined database-level validation/reporting smoke is valuable. It is not enough to hide source semantics behind a generic loader interface. The sources still differ materially in raw format, staging shape, provider dimensions, unit semantics, metadata, release keys, and operational fetch posture.

Allowed shared mechanics now:

- all-migrations application helper or script logic;
- combined isolated smoke runner;
- combined canonical fact/dimension/provider-mapping checks;
- shared JSON report envelope for combined data-health evidence;
- small SQL/query helpers if they remain mechanical and source-agnostic.

Still deferred:

- base loader classes;
- plugin registries;
- generalized source manifests;
- generalized JSON-stat parsing framework;
- generalized SDMX framework;
- orchestration/scheduling.

### 2. Are TASK-022 canonical tables sufficient after Eurostat implementation?

Yes for the current bounded evidence.

TASK-024 proved that the accepted canonical-domain schema supports:

- annual WDI/OECD-style periods;
- quarterly Eurostat periods;
- ISO3 canonical country identity;
- provider geography mappings such as `DE -> DEU` and `FR -> FRA`;
- provider period mappings such as `2023-Q1 -> 2023 Q1`;
- bounded provider code dictionaries;
- source-agnostic facts without provider-specific fact columns.

No immediate schema refinement is accepted.

Reopen schema design only if:

- Eurostat aggregate geographies such as `EU27_2020` or `EA20` are promoted;
- cross-source unit comparability requires explicit unit-conversion policy;
- indicator ontology/canonical concept mapping becomes necessary for research queries;
- current uniqueness constraints fail under a broader fixture;
- provider mappings become many-to-one or time-varying in a way current tables cannot express.

### 3. What is the next best step?

The next best step is validation/reporting hardening at the combined canonical database level.

Rationale:

- A third source has been implemented, but each source has mostly been verified in its own isolated smoke database.
- Before adding new sources or research/mart outputs, MacroForge should prove that WDI, OECD/SDMX, and Eurostat can coexist in one temporary database without canonical-key collisions, duplicate fact grains, broken provider mappings, or inconsistent lineage/quality reporting.
- This directly supports later research/mart work by making the canonical substrate auditable.
- It also tests whether current source-specific loaders are operationally composable without prematurely generalizing them.

TASK-026 should therefore implement a combined-source canonical validation smoke, not a new source or mart slice.

### 4. What should remain deferred?

Deferred until a later accepted decision:

- live `macro` writes;
- live production Eurostat ingestion;
- FRED onboarding;
- another source spike;
- mart/research outputs;
- generalized source/plugin/JSON-stat/SDMX framework;
- provider-specific fact columns;
- aggregate membership history;
- unit conversion framework;
- canonical indicator ontology;
- Alembic/SQLAlchemy/orchestration/scheduling;
- git push.

## Reconsideration triggers

Reopen the framework/tooling decision if at least two of these become true after TASK-026:

- the combined smoke requires copying substantial non-source-semantic boilerplate across three loaders;
- all three sources share a stable operation sequence that can be extracted without hiding source semantics;
- migration ordering or persistent-database upgrade concerns become hard to audit with raw SQL;
- source-specific runbooks become the bottleneck after combined isolated smoke is reliable;
- research/mart work requires repeatable cross-source data refreshes rather than ad hoc isolated smokes;
- another JSON-stat source repeats Eurostat parsing/mapping patterns.

## Consequences

MacroForge remains intentionally boring and auditable. The project advances from isolated source-specific loader proofs to a combined canonical substrate proof.

TASK-026 is implementation work and must start with a fresh implementation dry-run and TDD. It may add tests, a combined smoke module/script, and a report artifact, but it must not add loaders, migrations, sources, framework abstractions, mart outputs, or live database writes.

## Evidence reviewed

Context bundle:

- `context/active_context.md`
- `context/context_audit.md`
- `context/context_audit.json`

The compact governance context exceeded the default budget, so TASK-025 used justified `project_wide_review` mode under the context policy:

- context mode: `project_wide_review`;
- estimated tokens: 22118;
- budget tokens: 64000;
- within budget: true;
- raw logs excluded: true;
- summaries used: true;
- review justification: architecture review after three source-specific PostgreSQL paths needing broader consistency/gap review.

Implementation/report evidence:

- `artifacts/reports/oecd-sdmx-load-smoke-20260603.json`:
  - 8 staging rows;
  - 8 fact rows;
  - 2 lineage events;
  - 4 quality checks;
  - units `USD_EXC`, `USD_PPP`.
- `artifacts/reports/eurostat-namq-load-smoke-20260604.json`:
  - 4 staging rows;
  - 4 fact rows;
  - canonical periods `2023 Q1`, `2023 Q2`;
  - canonical territories `DEU`, `FRA`;
  - provider dimensions `freq`, `geo`, `na_item`, `s_adj`, `time`, `unit`.
- Prior WDI validation/load reports recorded in project state.
- Source-specific loader and schema summaries for WDI, OECD/SDMX, and Eurostat.

## Non-goals

This decision does not approve implementation under TASK-025 and does not approve any scope beyond TASK-026.

No git push was performed.
