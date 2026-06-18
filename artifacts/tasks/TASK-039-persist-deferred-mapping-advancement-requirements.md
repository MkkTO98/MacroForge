# TASK-039 — Persist deferred mapping advancement requirements after TASK-038

Status: complete
Created: 2026-06-18
Completed: 2026-06-18
Depends on: TASK-038
Governing evidence: TASK-038 lifecycle validation
Dry-run: `simulation/dry_runs/20260618_084552-task-039-deferred-mapping-advancement-requirements.md`

## Objective

Persist the concrete advancement requirements for the TASK-038 deferred OECD and Eurostat GDP mappings so future work can resume from explicit evidence instead of reinterpreting the full lifecycle artifact.

## Recurring effort reduced

- Canonical mapping: records exact blockers and minimum advancement conditions for deferred mappings.
- Validation: preserves gate/replay requirements before any status movement.
- Future agent recovery/context: gives future agents a compact first-read artifact for OECD/Eurostat advancement work.

## Scope allowed

- Create this task artifact.
- Create one JSON requirements artifact under `artifacts/reports/`.
- Create one concise Markdown requirements report under `artifacts/reports/`.
- Update backlog, state, handoff, README, and affected summaries for synchronization/closeout.

## Explicit non-goals

Do not change source code, tests, migrations, schemas, source evidence, accepted/base mapping state, `artifacts/manifests/canonical_assets.json`, GDP reports, or live/default databases. Do not call models, live-fetch data, implement conversion or aggregation, integrate report behavior, create a metadata framework, redesign the lifecycle, reorganize directories, create projects, or push to git.

## Acceptance criteria

- Dry-run validates before artifact creation.
- JSON artifact records, for each TASK-038 deferred OECD/Eurostat mapping: rationale, missing evidence/policy, semantic blocker, minimum advancement condition, caveats to preserve, evidence pointers, replay requirements, and forbidden shortcuts.
- Markdown report summarizes the same requirements for human/agent recovery.
- Deterministic invariant validation passes.
- State/backlog/handoff/summaries reflect TASK-039 completion and remove active-surface staleness around TASK-038.
- Recovery, coherence, context-health, and tests pass after closeout edits.

## Outcome

Complete.

Created:

- `artifacts/reports/canonicalization-deferred-mapping-advancement-requirements-20260618.json`
- `artifacts/reports/canonicalization-deferred-mapping-advancement-requirements-20260618.md`

The artifact records:

- OECD `B1GQ` remains blocked by unresolved exchange-rate USD versus PPP USD basis policy.
- Eurostat `B1GQ` remains blocked by missing quarterly/current-price/million-EUR frequency, currency, and scale policy.
- WDI remains governed provisional as reference only, not accepted truth.

## Validation

Dry-run validation passed before artifact creation:

```text
python3 tools/validate_dry_run.py simulation/dry_runs/20260618_084552-task-039-deferred-mapping-advancement-requirements.md
valid: simulation/dry_runs/20260618_084552-task-039-deferred-mapping-advancement-requirements.md
```

Final verification output is recorded in `context/latest_handoff.md`.

## Boundaries preserved

TASK-039 did not change source code, tests, migrations, schemas, source loaders, source evidence, accepted/base mapping state, the canonical asset manifest base file, or GDP reports. It did not call models, live-fetch data, write to live/default `macro`, perform unit/currency conversion, aggregate frequency, integrate reports, create generalized framework behavior, auto-apply mapping changes, or push to git.
