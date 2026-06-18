# TASK-029 — Decide next scope after first canonical GDP snapshot report

Status: complete
Created: 2026-06-04
Completed: 2026-06-04
Depends on: TASK-028
Relevant decisions: DEC-014

## Objective

Review the first canonical GDP snapshot/audit report after TASK-028 and decide the next bounded MacroForge scope.

Use the report to determine whether the canonical substrate is ready for a slightly richer research-facing output, needs focused data-quality/schema governance, or should remain in reliability hardening before additional source or framework work.

## Inputs

Use at minimum:

- TASK-028 outcome;
- `artifacts/reports/canonical-gdp-snapshot-20260604.json`;
- `artifacts/reports/canonical-gdp-snapshot-20260604.md`;
- DEC-014;
- current schema/loader/test state;
- active project state and architecture state.

## Questions to answer

1. Did the canonical-only report prove basic analytical usability without staging-table leakage?
2. Did the report expose blockers around indicator identity, unit comparability, annual/quarterly coexistence, or lineage/quality metadata?
3. Should the next scope be:
   - a second small research-facing report;
   - source coverage expansion;
   - focused schema/design governance;
   - reliability/reporting hardening;
   - or framework extraction?
4. What is the single smallest useful next task?

## Acceptance criteria

- Create a fresh governance dry-run before edits.
- Record an accepted decision artifact if a new direction is chosen.
- Create exactly one next task.
- Do not implement the chosen next scope in this task.
- Update state, backlog, summaries, and handoff.
- Run full tests and ProjectForge coherence.

## Explicit non-goals

Do not:

- add a source;
- add a migration;
- implement a generalized ingestion framework;
- live-fetch sources;
- write to live/default `macro`;
- push to git.


## Outcome

TASK-029 is complete.

Decision:

- `artifacts/decisions/DEC-015-next-scope-canonical-indicator-unit-comparability.md`

DEC-015 selects focused canonical indicator and unit comparability governance/design as the next bounded scope.

Reason:

TASK-028 proved basic canonical/meta-only report generation with deterministic JSON/Markdown artifacts, 16 GDP snapshot observations, 0 missing bounded GDP observations, 0 duplicate fact grains, and 0 failing quality checks. It also exposed the next analytical boundary: MacroForge can list GDP-ish observations, but it cannot yet express whether OECD `B1GQ`, Eurostat `B1GQ`, and WDI `NY.GDP.MKTP.CD` share a canonical economic concept or comparable unit semantics.

Follow-on task:

- `artifacts/tasks/TASK-030-design-minimal-canonical-indicator-unit-comparability.md`

TASK-030 is a bounded design/governance task. It should not implement migrations, report code, source onboarding, unit conversion, quarterly aggregation, mart schema, dashboard work, framework extraction, live fetches, live `macro` writes, or git push.

Verification will be recorded during closeout after state/handoff/summary updates.


Final verification after governance/summary/handoff updates passed:

```text
PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests -q && python3 tools/check_coherence.py --project . --json

..................................................                       [100%]
50 passed in 5.13s
{
  "mode": "generated",
  "blocks": [],
  "warnings": []
}
```
