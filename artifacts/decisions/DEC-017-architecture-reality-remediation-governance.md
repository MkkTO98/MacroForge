# DEC-017 — Architecture-to-Reality Remediation Governance

Status: accepted
Date: 2026-06-05

## Context

A comprehensive Architecture-to-Reality Audit found MacroForge broadly aligned with its accepted architecture, but with drift in validation coverage, primary state size, stale high-level documentation, logging policy wording, historical Desktop architecture reconciliation, and missing inherited lightweight audit/context-health tooling.

The user approved a bounded hygiene and coherence pass, not a redesign.

## Decision

MacroForge accepts the following governance corrections:

1. The primary audit trail is file-backed project governance:
   - task artifacts;
   - decision artifacts;
   - handoff artifacts;
   - state artifacts;
   - report artifacts for detailed evidence.
2. Operational logs are optional debugging artifacts. They are not the source of truth for normal project governance and are not required for ordinary task closeout.
3. MacroForge should inherit ProjectForge's lightweight Architecture-to-Reality Audit and context-health tooling where useful:
   - `tools/context_health.py`;
   - `tools/architecture_reality_audit.py`;
   - coherence integration for context health.
4. Historical Desktop architecture concepts must be classified against current decisions so future agents do not restore superseded wrappers, loader frameworks, status dimensions, bridge tables, or full run-folder assumptions by default.
5. The remediation must preserve current MacroForge boundaries:
   - no redesign;
   - no orchestration framework;
   - no generalized ingestion framework;
   - no ORM/Alembic layer;
   - no new datasets/sources;
   - no canonicalization implementation beyond TASK-030's approved design scope;
   - no git push.

## Consequences

- `logs/logging_policy.yaml`, `project.yaml`, agents, and governance docs describe logs as optional/debugging-oriented.
- State files should remain concise current-state pointers; historical detail belongs in task/report/handoff artifacts.
- Architecture-to-Reality Audits should run every 5-10 completed tasks and before major architecture/governance reviews.
- The historical architecture reconciliation note is now the durable reference for Desktop-era concepts.
