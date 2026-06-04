# TASK-018 — Decide next source/data reliability scope after TASK-017

Status: complete
Created: 2026-06-04
Preceded by: TASK-017
Governing decision: DEC-007

## Goal

Choose the next bounded MacroForge milestone after shared validation/reporting hardening.

## Why now

TASK-017 completed the immediate post-second-source hardening accepted by DEC-007. The project now has:

- WDI and OECD/SDMX source-specific PostgreSQL loaders;
- isolated idempotency test coverage for both sources;
- a tiny shared mechanical helper module for SQL/JSONB literals, psql execution/scalar/count parsing, and JSON report writing;
- no generalized source/SDMX framework, no schema changes, no live fetches, and no live `macro` writes from TASK-017.

DEC-007 recommended choosing next between codelist/label enrichment, a bounded third-source spike, or later research-layer work after TASK-017 evidence.

## Scope

In scope:

- Review TASK-017 implementation evidence and current project state.
- Decide whether the next implementation should be:
  - OECD/SDMX codelist/label enrichment;
  - a bounded no-key third-source spike;
  - additional runbook/reliability hardening;
  - or deferral into a different milestone.
- Record the decision and open the next implementation task if warranted.

Out of scope:

- Implementing the chosen source/enrichment work directly inside this task.
- Generalized source framework, SDMX framework, plugin registry, or source base class.
- Schema changes without a fresh decision and dry-run.
- Live `macro` database writes.
- Paid, credentialed, production, deployment, or git-push actions.

## Acceptance criteria

- TASK-017 evidence and DEC-007 triggers are reviewed.
- A decision artifact records the chosen next scope and non-goals.
- If implementation should proceed, a follow-on task artifact is created with scope/acceptance criteria.
- State, roadmap, handoff, backlog, and affected summaries are updated.
- Generated-project coherence passes after governance updates.

## Outcome

Completed 2026-06-04.

Decision recorded:

- `artifacts/decisions/DEC-008-next-scope-after-shared-validation-reporting.md`

DEC-008 chooses bounded source-specific OECD/SDMX codelist and label enrichment before a third-source spike. The rationale is that TASK-017 stabilized shared mechanics, while the largest known weakness in the second source is now semantic explainability: the existing OECD/SDMX path preserves codes such as `B1GQ`, `AUS`, `USA`, `USD_EXC`, `USD_PPP`, `CONF_STATUS`, `DECIMALS`, and `OBS_STATUS`, but labels/descriptions remain outside the current observation payload and reports.

Follow-on task opened:

- `artifacts/tasks/TASK-019-spike-oecd-sdmx-codelist-label-enrichment.md`

TASK-019 must begin with a fresh implementation dry-run and TDD. It should use recorded fixture evidence before any live no-key fetch, produce bounded project-layout metadata/report evidence, and avoid generalized SDMX/source framework work, schema changes, live `macro` writes, third-source onboarding, and research/mart work.

## Context used

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
- `artifacts/tasks/TASK-017-harden-shared-validation-and-loader-reporting.md`
- `artifacts/decisions/DEC-002-v1-scope-wdi-postgres-vertical-slice.md`
- `artifacts/decisions/DEC-005-post-vertical-slice-architecture-and-next-source-scope.md`
- `artifacts/decisions/DEC-006-oecd-sdmx-postgresql-promotion.md`
- `artifacts/decisions/DEC-007-post-second-source-architecture-and-next-scope.md`
- `src/macroforge/db_helpers.py`
- `docs/data/source-contract.md`
- `artifacts/reports/oecd-sdmx-second-source-spike-20260603.md`
- `artifacts/reports/oecd-sdmx-smoke-20260603.md`
- `artifacts/reports/oecd-sdmx-live-smoke-20260603.md`

## Verification evidence

Context audit:

```text
python3 tools/build_context.py --project . --model-target cloud --context-mode governance --task-type architecture_decision --task "TASK-018 decide next bounded source/data reliability scope after TASK-017 shared validation/reporting hardening" --task-file artifacts/tasks/TASK-018-decide-next-scope-after-shared-validation-reporting.md --decisions DEC-005,DEC-006,DEC-007 --model-selected gpt-5.5 --model-reason "Current Hermes session is using cloud governance reasoning for a bounded architecture/source-scope decision under context_policy."

{
  "context": "/home/mkkto/srv/projectforge/workspace/projects/macroforge/context/active_context.md",
  "audit": "/home/mkkto/srv/projectforge/workspace/projects/macroforge/context/context_audit.json",
  "estimated_tokens": 7244,
  "budget_tokens": 10000,
  "within_budget": true,
  "context_mode": "governance"
}
```

Post-governance tests and coherence before final handoff write:

```text
PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests -q && python3 tools/check_coherence.py --project . --json

.............................                                            [100%]
29 passed in 1.70s
{
  "mode": "generated",
  "blocks": [],
  "warnings": []
}
```

Final verification after handoff write:

```text
PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests -q && python3 tools/check_coherence.py --project . --json

.............................                                            [100%]
29 passed in 1.74s
{
  "mode": "generated",
  "blocks": [],
  "warnings": []
}
```
