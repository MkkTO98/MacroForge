# TASK-016 — Review architecture after second source

Status: complete
Created: 2026-06-03
Completed: 2026-06-03
Preceded by: TASK-015
Governing decisions: DEC-005, DEC-006
Outcome decision: DEC-007
Follow-on task: TASK-017
Dry-run/preflight: completed in `simulation/dry_runs/20260603_222247-open-task-016-post-second-source-architecture-review.md` and `simulation/dry_runs/20260603_223359-execute-task-016-post-second-source-architecture-review.md`

## Goal

Run a post-second-source architecture review now that MacroForge has two database-backed source-specific slices: WDI and bounded OECD/SDMX.

The review should decide what, if anything, is now justified after the second source: small shared helper extraction, validation/reporting hardening, migration/tooling changes, a third-source spike, or continued source-specific duplication.

This is a governance/design task, not an implementation task.

## Why now

DEC-005 deferred broad ingestion frameworks until a second source passed through the contract. TASK-015 completed that second source's PostgreSQL promotion. That creates enough evidence to review observed pressure without guessing.

The review must inspect actual implementation evidence, not just roadmap prose:

- WDI loader and smoke/validation path.
- OECD/SDMX parser, live smoke, loader, and staging migration.
- Current schema/migration shape.
- Tests and isolated smoke reports.
- Source contract and runbooks.

## Required context bundle

Because this is architecture/governance work under the local-execution/cloud-governance policy, begin by building and inspecting a governance context bundle before writing any decision:

```bash
python3 tools/build_context.py --project . --model-target cloud --context-mode governance --task-type architecture_decision --task "Review architecture after second database-backed source and decide next MacroForge source/framework scope" --task-file artifacts/tasks/TASK-016-review-architecture-after-second-source.md --decisions DEC-005 DEC-006 --model-selected "current Hermes model" --model-reason "Architecture governance review after WDI and OECD/SDMX slices; compact selected context required by project policy"
```

Then read:

- `context/active_context.md`
- `context/context_audit.md`

Confirm raw logs are excluded and the bundle fits the governance budget before reasoning or escalating.

## Required questions

The review must answer:

1. Do WDI + OECD/SDMX justify extracting a tiny shared loader helper now, or should duplication remain source-specific?
2. Does having two source-specific staging tables justify migration-tooling changes, or should raw SQL remain for now?
3. Should validation/reporting be hardened next, and if so should it be source-specific or shared?
4. Should the next source task be a third-source spike, codelist/label enrichment, runbook hardening, or research-layer work?
5. What exact triggers would justify a generalized source/SDMX framework later?
6. What must remain explicitly out of scope for the next task?

## Scope

In scope:

- Inspect implementation evidence from TASK-006 through TASK-015.
- Compare WDI and OECD/SDMX loader/schema/test/report patterns.
- Review DEC-005 and DEC-006 boundaries against current evidence.
- Write a new decision artifact, likely `artifacts/decisions/DEC-007-post-second-source-architecture-and-next-scope.md`.
- Open one or more follow-on task artifacts recommended by DEC-007.
- Update backlog, state, architecture, roadmap, handoff, and affected summaries.

Out of scope:

- Source/framework implementation.
- Refactoring loaders.
- Schema changes.
- Live `macro` database writes.
- Live data fetches.
- Generalized SDMX/source framework creation without an accepted DEC-007 decision.
- Alembic, SQLAlchemy, orchestration, Docker, scheduling, or mart/reporting work unless DEC-007 explicitly accepts a bounded follow-on task.
- Paid, credentialed, or production API use.
- Git push.

## Expected files

Likely files to create/update:

- `context/active_context.md`
- `context/context_audit.md`
- `context/context_audit.json`
- `artifacts/decisions/DEC-007-post-second-source-architecture-and-next-scope.md`
- follow-on task artifact(s), likely `artifacts/tasks/TASK-017-...md`
- `artifacts/tasks/backlog.md`
- `state/active_goal.md`
- `state/project_state.md`
- `state/architecture.md`
- `docs/roadmap.md`
- `context/latest_handoff.md`
- affected `_SUMMARY.md` files

Do not modify source code, schema migrations, or database artifacts unless the review explicitly opens a separate implementation task and the user asks to proceed with it later.

## Acceptance criteria

- Governance context bundle is built and inspected.
- `context/context_audit.md` confirms raw logs were excluded and budget policy was respected.
- Actual implementation evidence is inspected, including both WDI and OECD/SDMX loader/schema/test/report surfaces.
- DEC-007 is created and accepted/deferred with clear answers to the required questions.
- At least one concrete follow-on task is opened, or the decision explains why no new task is appropriate.
- Backlog, active goal, project state, architecture state, roadmap, handoff, and affected summaries point at the new decision/task state.
- Full tests pass.
- Generated-project coherence passes.
- No implementation, live database write, live fetch, generalized framework, or git push occurs.

## Verification plan

Run after the review/state updates:

```bash
PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests -q
python3 tools/check_coherence.py --project . --json
```

If recording verification output changes state/handoff, run a final coherence-only check:

```bash
python3 tools/check_coherence.py --project . --json
```

## Notes

This task exists because TASK-015 completed the second database-backed source slice. It should use evidence from two real source-specific paths to decide the next bounded step, not to justify broad framework work by default.


## Outcome

Completed in DEC-007:

`artifacts/decisions/DEC-007-post-second-source-architecture-and-next-scope.md`

TASK-016 decided that WDI + OECD/SDMX justify only tiny shared mechanical helper extraction and validation/reporting hardening. Raw SQL migrations remain; source-specific loaders remain; generalized source/SDMX/framework work remains deferred.

Follow-on task opened:

`artifacts/tasks/TASK-017-harden-shared-validation-and-loader-reporting.md`

The governance context bundle was built and inspected. The final context audit recorded 8062 estimated tokens, 10000 token budget, within budget, raw logs excluded, and summaries used.

Final handoff cleanup on 2026-06-03 replaced the pending verification placeholder in `context/latest_handoff.md`, reran the full test suite plus generated-project coherence, refreshed/inspected affected summaries, updated closeout records, and left TASK-017 open/unimplemented.

```text
PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests -q && python3 tools/check_coherence.py --project . --json

.........................                                                [100%]
25 passed in 1.67s
{
  "mode": "generated",
  "blocks": [],
  "warnings": []
}
```

Earlier cleanup verification also passed:

```text
PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests -q && python3 tools/check_coherence.py --project . --json

.........................                                                [100%]
25 passed in 1.71s
{
  "mode": "generated",
  "blocks": [],
  "warnings": []
}

python3 tools/check_coherence.py --project . --json

{
  "mode": "generated",
  "blocks": [],
  "warnings": []
}
```
