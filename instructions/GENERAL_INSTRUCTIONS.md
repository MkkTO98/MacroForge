# General Instructions

ProjectForge is a boring, explicit operating structure for agent-supported projects.
Agents must prefer readable files, explicit decisions, and reversible changes over clever hidden automation.

Mandatory discipline:
- Consult `CONSTITUTION.md`, `state/`, relevant `artifacts/decisions/`, and the active context bundle before changing files.
- Include `Context used:` in every run report.
- Use dry-run/preflight according to `simulation/dry_run_policy.yaml`.
- Store durable choices and deferred specifications as decision artifacts.
- Do not push to GitHub without human approval.
- Do not create specialized agents without requesting approval and explaining why.
- If capability fails, escalate through local review, stronger local model, Codex/premium model, then human.
- If permissions, secrets, money, destructive operations, or production data are involved, escalate to human directly.
