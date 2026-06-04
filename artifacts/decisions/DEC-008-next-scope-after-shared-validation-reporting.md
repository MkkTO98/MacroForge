# DEC-008 — Next Scope After Shared Validation and Reporting

Status: Accepted
Date: 2026-06-04
Task: TASK-018
Preceded by: TASK-017
Governing context: DEC-002, DEC-005, DEC-006, DEC-007, TASK-018 governance context bundle

## Decision

MacroForge will do a bounded, source-specific OECD/SDMX codelist and label enrichment spike next, before a third-source spike or research/mart layer work.

The follow-on implementation task is:

- TASK-019 — Spike OECD/SDMX codelist and label enrichment.

TASK-019 should enrich the existing OECD/SDMX evidence path with recorded no-key codelist/structure evidence and labels/descriptions for the bounded smoke slice, but it must remain source-specific and evidence/report oriented first. It must not introduce a generalized SDMX framework, source framework, plugin registry, schema migration, curated schema change, live `macro` write, orchestration framework, paid/credentialed API, or research/mart layer.

## Why codelist enrichment before a third source

After TASK-017, the two proven database-backed source-specific slices are mechanically stable enough for the next decision. DEC-007 left two plausible next steps: codelist/label enrichment for OECD/SDMX or a bounded third-source spike.

Codelist/label enrichment is the better next step because:

1. The largest known weakness in the second source is not loader mechanics anymore; it is semantic metadata. The OECD/SDMX observation payload is code-heavy: `B1GQ`, `AUS`, `USA`, `USD_EXC`, `USD_PPP`, and attributes like `CONF_STATUS`, `DECIMALS`, and `OBS_STATUS` are currently preserved, but human-readable labels/descriptions are not part of the observation response.
2. A third source would add breadth, but it would leave the current second source less explainable for future analysis. MacroForge is a research platform, so code-only dimensions are a blocker for trustworthy human/AI interpretation before research/mart work.
3. DEC-007 explicitly named source codelists/labels/attribute semantics as one of the triggers that may justify broader abstraction later. Testing codelist enrichment on the existing OECD/SDMX slice produces direct evidence for whether this remains a source-specific add-on or begins to pressure a reusable SDMX metadata component.
4. The project already has a bounded OECD/SDMX no-key live endpoint, fixture evidence, normalized rows, PostgreSQL loader, and idempotency tests. Enrichment can be scoped narrowly around existing smoke dimensions without broadening API/source surface area.
5. The next step can be done without schema changes by writing/validating metadata artifacts and reports first. Any database/model change should require a later decision after the enrichment evidence exists.

## Scope accepted for TASK-019

TASK-019 may:

- Use recorded fixture evidence first for codelist/structure parsing tests.
- Optionally use the no-key OECD SDMX structure/codelist endpoint only inside a fresh dry-run-approved command path.
- Preserve raw structure/codelist evidence with checksum, byte count, endpoint, and metadata.
- Extract labels/descriptions for only the bounded smoke-slice concepts needed now, such as:
  - `MEASURE` / `B1GQ`;
  - `REF_AREA` / `AUS` and `USA`;
  - `UNIT_MEASURE` / `USD_EXC` and `USD_PPP`;
  - observed attributes `CONF_STATUS`, `DECIMALS`, and `OBS_STATUS` if present in retrieved structure metadata.
- Produce normalized metadata and an inspectable report that maps code values to labels/descriptions.
- Update the source contract documentation with the OECD/SDMX enrichment evidence and limitations.
- Evaluate whether the current curated model can remain unchanged for now.

## Scope rejected for TASK-019

TASK-019 must not include:

- generalized SDMX parser/framework work;
- generalized source framework, plugin registry, or source base class;
- schema changes, migration rewrites, Alembic, ORM, or curated model changes;
- loading labels into live `macro`;
- live `macro` database writes;
- broad codelist harvesting beyond the bounded smoke slice;
- third-source onboarding;
- research/mart/reporting layer implementation;
- paid, credentialed, production, deployment, scheduling, or git-push actions.

## Third-source timing

A bounded third-source spike remains valuable, but it should come after TASK-019 unless TASK-019 is blocked by OECD access/format instability.

The third-source spike should be reconsidered after TASK-019 if:

- OECD label/codelist enrichment succeeds and stays source-specific;
- no schema change is needed for labels/descriptions yet;
- the project can clearly explain WDI and OECD observations in reports;
- the next learning objective becomes source variation rather than metadata reliability.

If TASK-019 shows that SDMX codelist handling is much larger than expected, stop before framework extraction and record a new decision about whether to continue source-specific enrichment, defer labels, or do a third-source spike instead.

## Framework and migration triggers after TASK-019

DEC-007 framework triggers remain in force. TASK-019 alone does not authorize a generalized source/SDMX framework.

A reusable SDMX metadata helper may be reconsidered only after TASK-019 if all of the following are true:

- the bounded OECD codelist/label retrieval and parsing behavior is proven with tests and recorded evidence;
- the helper surface can remain mechanical and local, similar to `db_helpers.py`;
- no source registration, plugin lookup, inheritance hierarchy, or generic ingestion lifecycle is needed;
- a follow-on decision explicitly accepts the helper scope.

Migration tooling and schema changes remain deferred until the triggers in DEC-007 occur, such as a third nontrivial schema migration, persistent-environment upgrade/rollback needs, or label/metadata requirements that cannot be represented in existing filesystem reports/source metadata.

## Context and evidence reviewed

Context bundle:

- `context/active_context.md`
- `context/context_audit.md`
- `context/context_audit.json`

The context audit reported:

- context mode: governance;
- estimated tokens: 7244;
- budget tokens: 10000;
- within budget: True;
- raw logs excluded: True;
- summaries used: True.

Implementation and evidence inspected:

- `artifacts/tasks/TASK-017-harden-shared-validation-and-loader-reporting.md`
- `src/macroforge/db_helpers.py`
- `docs/data/source-contract.md`
- `artifacts/reports/oecd-sdmx-second-source-spike-20260603.md`
- `artifacts/reports/oecd-sdmx-smoke-20260603.md`
- `artifacts/reports/oecd-sdmx-live-smoke-20260603.md`
- `state/active_goal.md`
- `state/project_state.md`
- `state/architecture.md`
- `context/latest_handoff.md`

## Follow-on task

Open TASK-019:

`artifacts/tasks/TASK-019-spike-oecd-sdmx-codelist-label-enrichment.md`

TASK-019 should begin with a fresh implementation dry-run and TDD. It should produce fixture-backed parser tests and project-layout metadata/report writer tests before any live no-key fetch or project artifact generation.

## Verification / evidence used

Context used:

- `projectforge` skill
- `projectforge` reference `generated-project-post-vertical-slice-architecture-review.md`
- `CONSTITUTION.md`
- `instructions/GENERAL_INSTRUCTIONS.md`
- `context/context_policy.yaml`
- `context/active_context.md`
- `context/context_audit.md`
- `state/active_goal.md`
- `state/project_state.md`
- `state/architecture.md`
- `context/latest_handoff.md`
- `artifacts/tasks/TASK-018-decide-next-scope-after-shared-validation-reporting.md`
- `artifacts/decisions/DEC-002-v1-scope-wdi-postgres-vertical-slice.md`
- `artifacts/decisions/DEC-005-post-vertical-slice-architecture-and-next-source-scope.md`
- `artifacts/decisions/DEC-006-oecd-sdmx-postgresql-promotion.md`
- `artifacts/decisions/DEC-007-post-second-source-architecture-and-next-scope.md`
- implementation/evidence files listed above

Final tests and coherence are recorded in TASK-018, `state/project_state.md`, and `context/latest_handoff.md` after governance updates.
