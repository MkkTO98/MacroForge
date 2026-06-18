# TASK-036 — Decide next scope after deterministic canonicalization proposal workflow

Status: complete
Created: 2026-06-13
Completed: 2026-06-13
Depends on: TASK-034
Governing decisions: DEC-019, DEC-018, DEC-016, DEC-015
Dry-run: `simulation/dry_runs/20260613_190712-dry-run.md`
Decision: `artifacts/decisions/DEC-021-next-scope-after-deterministic-canonicalization-proposal-workflow.md`
Decision analysis: `docs/architecture/canonicalization-post-proposal-next-scope-decision-analysis.md`
Follow-on task: `artifacts/tasks/TASK-037-implement-bounded-wdi-unit-metadata-enrichment-for-canonicalization-evidence.md`

## Objective

Review the completed TASK-034 deterministic canonicalization proposal workflow and decide the next smallest scope that reduces uncertainty without prematurely expanding capability.

TASK-034 proved that existing provider evidence can drive deterministic workflow proposals, review routing, mapping-update proposals, and audit output without mutating accepted/provisional mapping state. TASK-036 decides the next scope by uncertainty reduction.

## Scope allowed

TASK-036 may create or modify:

- a fresh governance dry-run;
- a decision analysis document comparing next-scope candidates;
- a new decision artifact selecting exactly one follow-on implementation or design task;
- one follow-on task artifact;
- bounded state, backlog, roadmap, handoff, and summary updates for closeout.

## Evidence reviewed

- `artifacts/tasks/TASK-034-implement-tiny-deterministic-canonicalization-proposal-workflow.md`;
- `artifacts/reports/canonicalization-proposal-workflow-20260613.json`;
- `src/macroforge/canonicalization_state.py`;
- `tests/test_canonicalization_proposal_workflow.py`;
- `artifacts/decisions/DEC-019-next-scope-deterministic-canonicalization-proposal-workflow.md`;
- `artifacts/decisions/DEC-018-minimal-ai-assisted-canonicalization-layer.md`;
- `docs/architecture/minimal-ai-assisted-canonicalization-layer.md`;
- `docs/architecture/canonicalization-next-scope-decision-analysis.md`.

## Outcome

Completed. TASK-036 created DEC-021 and selected exactly one follow-on task: TASK-037 — implement bounded WDI unit metadata enrichment for canonicalization evidence.

Rationale summary:

- TASK-034 proved deterministic proposal workflow mechanics.
- The strongest remaining blocker is source evidence quality: WDI GDP remains blocked by `unknown_unit_metadata` while OECD and Eurostat already carry explicit unit caveats.
- WDI metadata enrichment is smaller and less risky than AI-assisted proposal generation, PostgreSQL persistence, report integration, review-policy calibration, or new source expansion.
- Enriching WDI evidence first avoids confounding AI/model quality with missing provider metadata.

## Verification

Initial dry-run validation:

```text
python3 tools/validate_dry_run.py simulation/dry_runs/20260613_190712-dry-run.md
valid: simulation/dry_runs/20260613_190712-dry-run.md
```

Final post-closeout verification is recorded in `context/latest_handoff.md`.

## Explicit non-goals preserved

No implementation of TASK-037 was performed under TASK-036. No AI/model calls, prompt/provider setup, migrations, new sources, live fetches, live/default `macro` writes, unit conversion, frequency aggregation, report integration, broad ontology/framework extraction, provider-specific fact columns, accepted mapping mutation, auto-apply behavior, or git push was performed.
