# TASK-037 — Implement bounded WDI unit metadata enrichment for canonicalization evidence

Status: complete
Created: 2026-06-13
Depends on: TASK-036
Governing decisions: DEC-021, DEC-018, DEC-016, DEC-015

## Objective

Implement the smallest source-specific WDI unit metadata enrichment needed to improve canonicalization evidence for the existing GDP fixture set.

TASK-034 proved deterministic proposal workflow mechanics but left WDI `NY.GDP.MKTP.CD` blocked by `unknown_unit_metadata`. TASK-037 should enrich WDI provider evidence enough that canonicalization state/proposal output can represent explicit WDI unit/currency metadata and caveats without unit conversion, accepted-state mutation, AI/model calls, database persistence, report integration, new sources, or generalized framework work.

## Scope allowed

TASK-037 may create or modify:

- a fresh implementation dry-run;
- tests written before implementation;
- small source-specific WDI metadata fixture(s) or recorded local evidence for `NY.GDP.MKTP.CD`;
- bounded WDI provider evidence/unit profile logic in `src/macroforge/canonicalization_state.py` or a tiny source-specific helper if tests justify it;
- a bounded regenerated or new audit artifact under `artifacts/reports/` showing enriched WDI unit metadata in canonicalization evidence/proposals;
- task/state/handoff/summaries needed for closeout.

## Required properties

- Use only existing bounded WDI GDP scope and local fixture/recorded metadata.
- Preserve source-specific behavior; do not extract a generalized provider metadata framework.
- Preserve TASK-034 proposal/accepted-state separation.
- Preserve `auto_apply: false` for mapping update proposals.
- Preserve GDP high-impact review-required routing.
- Represent WDI unit metadata as evidence/caveat metadata, not as unit conversion or comparability proof.
- Keep annual/quarterly frequency semantics explicit and non-aggregated.

## Acceptance criteria

- Fresh implementation dry-run is created and validated before edits.
- TDD RED check is observed before implementation.
- Tests prove WDI GDP unit metadata is represented from fixture/recorded source evidence instead of generic `unknown` when available.
- Tests prove WDI enrichment changes the canonicalization evidence/proposal caveat while preserving review-required routing.
- Tests prove no unit conversion, frequency aggregation, accepted mapping mutation, or auto-apply behavior is introduced.
- A deterministic audit artifact is generated/read back.
- Full tests pass.
- `python3 tools/check_coherence.py --project . --json` reports no blocks or warnings after closeout updates.

## Implementation summary

TASK-037 added a bounded WDI-specific enrichment path in `src/macroforge/canonicalization_state.py`.

The enrichment uses only fixture-backed metadata for existing WDI GDP provider evidence:

- source: `WDI`
- dataset: `WDI`
- provider indicator: `NY.GDP.MKTP.CD`
- existing unit profile: `unit:WDI:unknown`
- metadata source marker: `fixture:wdi:NY.GDP.MKTP.CD:unit_metadata`

The enriched profile marks the WDI GDP unit as current USD metadata evidence with `metadata_evidence_role: source_metadata_not_canonical_truth`, `conversion_status: deferred`, and `comparable_without_conversion: false`. The unit profile identity is intentionally unchanged so the task enriches evidence metadata without inventing a new canonical unit identity or performing conversion.

## Evidence produced

- Fresh implementation dry-run: `simulation/dry_runs/20260613_172928-task-037-wdi-unit-metadata-enrichment.md`
- Bounded audit artifact: `artifacts/reports/canonicalization-wdi-unit-metadata-enrichment-20260613.json`

The audit artifact shows all TASK-037 checks passing:

- `wdi_unknown_unit_metadata_reduced`
- `non_wdi_sources_unchanged`
- `metadata_evidence_not_canonical_truth`
- `no_unit_conversion`
- `proposal_state_separate_from_accepted_mapping_state`
- `high_impact_review_routing_preserved`
- `no_auto_apply_mapping_updates`

## Verification

Dry-run validation passed:

```text
python3 tools/validate_dry_run.py simulation/dry_runs/20260613_172928-task-037-wdi-unit-metadata-enrichment.md
valid: simulation/dry_runs/20260613_172928-task-037-wdi-unit-metadata-enrichment.md
```

TDD RED check was observed before implementation:

```text
uvx --from pytest --with pyyaml pytest tests/test_canonicalization_proposal_workflow.py -q
....FFFF                                                                 [100%]
4 failed, 4 passed in 0.05s
```

Targeted implementation tests passed:

```text
uvx --from pytest --with pyyaml pytest tests/test_canonicalization_proposal_workflow.py tests/test_canonicalization_state.py -q
..............                                                           [100%]
14 passed in 0.03s
```

Full tests passed before closeout updates:

```text
uvx --from pytest --with pyyaml pytest tests -q
....................................................................     [100%]
68 passed in 4.91s
```

Final closeout verification passed:

```text
uvx --from pytest --with pyyaml pytest tests -q
....................................................................     [100%]
68 passed in 5.55s
```

```text
python3 tools/check_coherence.py --project . --json
{
  "mode": "generated",
  "blocks": [],
  "warnings": []
}
```

```text
python3 tools/architecture_reality_audit.py --project . --json
{
  "latest_architecture_reality_audit": "artifacts/reports/R-20260613-architecture-reality-audit.md",
  "completed_tasks_since_latest_audit": 0,
  "blocks": [],
  "warnings": []
}
```

Closeout artifacts:

- `artifacts/handoffs/HANDOFF-20260613-task-037-closeout-detail.md`
- `artifacts/reports/R-20260613-architecture-reality-audit.md`
- `artifacts/reports/TASK-037-closeout-report-20260613.md`

Unrelated deterministic reports were restored and verified unchanged after tests:

- `artifacts/reports/canonical-gdp-snapshot-20260604.json`
- `artifacts/reports/combined-source-canonical-smoke-20260604.json`

## Boundaries preserved

TASK-037 did not call models, live-fetch data, add sources, add migrations, write to live/default `macro`, perform unit/currency conversion, aggregate frequencies, mutate accepted mapping state, auto-apply mapping updates, integrate the GDP snapshot report, or broaden into a generalized metadata/source framework.

## Explicit non-goals

Do not:

- call an LLM/model for canonicalization;
- configure prompts/model providers/embeddings;
- onboard a new source;
- live-fetch sources without a separate explicit approval;
- write to live/default `macro`;
- implement PostgreSQL migrations or canonicalization persistence;
- implement unit or currency conversion;
- aggregate quarterly to annual;
- integrate canonicalization state into the canonical GDP snapshot report;
- create mart/dashboard/report scope beyond bounded audit output;
- broaden into a generalized metadata/source framework;
- add provider-specific fact columns;
- auto-accept or mutate accepted/provisional mapping state;
- push to git.
