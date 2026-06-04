# Handoff — MacroForge DEC-010 complete; TASK-021 open

Timestamp UTC: 2026-06-04T08:39:47Z

## Status

DEC-010 is accepted and the canonical-domain schema design note is complete.

The user corrected the TASK-020 schema interpretation: provider representations should not become canonical identities. MacroForge should preserve source-agnostic canonical observations for long-term heterogeneous macroeconomic and investment research.

TASK-021 is open to design concrete schema evolution for canonical periods, canonical territories, and provider mappings. No executable migration or Eurostat PostgreSQL promotion has been implemented.

## Context used

- `CONSTITUTION.md`
- `instructions/GENERAL_INSTRUCTIONS.md`
- `context/context_policy.yaml`
- generated governance context bundle:
  - `context/active_context.md`
  - `context/context_audit.md`
- `state/active_goal.md`
- `state/project_state.md`
- `state/architecture.md`
- `context/latest_handoff.md`
- `db/migrations/001_v0_schema_foundation.sql`
- `docs/data/v0-data-model.md`
- `artifacts/reports/eurostat-third-source-architecture-spike-20260604.md`
- `artifacts/decisions/DEC-009-third-source-spike-scope.md`

## Files changed

Created:

- `docs/architecture/canonical-domain-schema-evolution.md`
- `artifacts/decisions/DEC-010-canonical-domain-schema-evolution.md`
- `artifacts/tasks/TASK-021-design-canonical-period-territory-provider-mapping-schema-evolution.md`
- `simulation/dry_runs/20260604_083947-canonical-domain-schema-design-note.md`

Updated:

- `artifacts/tasks/backlog.md`
- `state/active_goal.md`
- `state/project_state.md`
- `state/architecture.md`
- `docs/roadmap.md`
- `docs/data/source-contract.md`
- `artifacts/reports/eurostat-third-source-architecture-spike-20260604.md`
- affected `_SUMMARY.md` files
- `context/latest_handoff.md`

## Design conclusion

Canonical-domain schema evolution is better than provider-centric schema evolution for MacroForge.

Provider-centric evolution is fast for ingestion but lets provider period strings and geography codes become curated identities. That creates semantic debt across many heterogeneous sources.

Canonical-domain evolution keeps curated dimensions as stable analytical domain entities:

- Periods use structured canonical fields for annual, quarterly, monthly, and eventually daily observations.
- Provider period strings stay in metadata/mapping tables.
- ISO3 remains the canonical country identifier.
- Aggregate regions use `territory_type` and explicit aggregate/economic-area support.
- Provider geography codes map to canonical territories rather than replacing ISO3 semantics.
- Provider code dictionaries remain metadata/provenance and mapping evidence.

This better supports MacroForge's long-term goal of integrating many heterogeneous macroeconomic sources for investment research because downstream research can query stable domain identities instead of provider-shaped vocabularies.

## Boundaries preserved

- No executable schema migration.
- No PostgreSQL writes.
- No live `macro` writes.
- No Eurostat PostgreSQL promotion.
- No generalized ingestion framework.
- No research/mart implementation.
- No git commit/push.

## Verification so far

Governance context bundle:

```text
python3 tools/build_context.py --project . --model-target cloud --context-mode governance --task-type architecture_decision --task "Re-evaluate TASK-020 Eurostat schema recommendations from canonical-domain perspective: compare provider-centric vs canonical-domain schema evolution for periods, territories, provider mappings, and long-term heterogeneous macro source integration" --decisions DEC-009 --model-selected gpt-5.5 --model-reason "Current user requested a schema design re-evaluation and comparison note after Eurostat architecture spike"

{
  "context": "/home/mkkto/srv/projectforge/workspace/projects/macroforge/context/active_context.md",
  "audit": "/home/mkkto/srv/projectforge/workspace/projects/macroforge/context/context_audit.json",
  "estimated_tokens": 7645,
  "budget_tokens": 10000,
  "within_budget": true,
  "context_mode": "governance"
}
```

Dry-run validation:

```text
python3 tools/validate_dry_run.py simulation/dry_runs/20260604_083947-canonical-domain-schema-design-note.md

valid: simulation/dry_runs/20260604_083947-canonical-domain-schema-design-note.md
```

Final verification after governance/summary/handoff updates:

```text
PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests -q && python3 tools/check_coherence.py --project . --json

.................................                                        [100%]
33 passed in 1.74s
{
  "mode": "generated",
  "blocks": [],
  "warnings": []
}
```

## Remaining risks / next step

TASK-021 should decide the concrete schema design plan. It should not implement migrations. The next implementation task, if accepted later, should start with a fresh dry-run and tests.
