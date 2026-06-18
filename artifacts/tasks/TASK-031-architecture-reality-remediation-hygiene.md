# TASK-031 — Architecture-to-Reality remediation hygiene

Status: completed
Created: 2026-06-05
Completed: 2026-06-05
Governing decision: DEC-017
Dry-run: `simulation/dry_runs/20260605_133337-dry-run.md`

## Objective

Implement the user-approved remediation items from the completed Architecture-to-Reality Audit as a bounded hygiene/coherence pass.

## Scope implemented

- Fix validation/documentation drift around `staging.oecd_sdmx_observation` and migration 002 references.
- Add inherited lightweight context-health and Architecture-to-Reality Audit tooling.
- Compact `state/project_state.md` into a concise current-state artifact and preserve the previous ledger in a report artifact.
- Refresh high-level README and architecture overview through TASK-030 / DEC-016.
- Reconcile historical Desktop architecture concepts against current decisions.
- Align logging, command-governance, context policy, permission allowlist, and agent instructions with actual project operation.

## Explicit non-goals preserved

No MacroForge redesign, orchestration framework, generalized ingestion framework, ORM/Alembic layer, new dataset/source, canonicalization implementation, TASK-030 scope expansion, live/default `macro` write, or git push was performed.

## Outcome

Completed as a hygiene interruption. TASK-030 remains the active domain governance/design task.

## Validation

See `context/latest_handoff.md` and final response for exact command output.
