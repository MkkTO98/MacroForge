# General Instructions

ProjectForge is a boring, explicit operating structure for agent-supported projects.
Agents must prefer readable files, explicit decisions, and reversible changes over clever hidden automation.

Mandatory discipline:
- Consult `CONSTITUTION.md`, concise `state/` files, relevant `artifacts/decisions/`, active task artifacts, folder summaries, and `context/latest_handoff.md` before changing files. Generate a fresh `context/active_context.md` bundle only when an explicit task/model-target context bundle is needed.
- Evaluate proposed work by asking which recurring effort it reduces: source onboarding, source maintenance, validation, canonical mapping, schema evolution, downstream analysis, or future agent recovery/context effort.
- Preserve trust boundaries: PostgreSQL stores accepted analytical data but does not itself prove truth; source evidence, reproducibility evidence, lineage, quality checks, canonical mapping status, validation, replay/rerun paths, and human review for high-impact economic meaning are the trust basis.
- Preserve source-specific-first discipline. Start source-specific and extract shared mechanics only after repeated non-semantic duplication appears; do not add generalized ingestion, plugin, scheduler, orchestration, or model machinery for architectural elegance alone.
- Automate proposals and checks, not authority. Local models may assist bounded proposal work; humans retain authority over purpose, risk, high-impact semantic decisions, schema doctrine, live/production authority, destructive actions, secrets, paid API use, and investment conclusions.
- Include `Context used:` in every run report.
- Use dry-run/preflight according to `simulation/dry_run_policy.yaml`.
- Store durable choices and deferred specifications as decision artifacts.
- Do not push to GitHub without human approval.
- Do not create specialized agents without requesting approval and explaining why.
- If capability fails, escalate through local review, stronger local model, Codex/premium model, then human.
- If permissions, secrets, money, destructive operations, or production data are involved, escalate to human directly.

Architecture-to-Reality Audit discipline:
- Run `tools/architecture_reality_audit.py` every 5-10 completed tasks, before major architecture changes, and before major governance reviews.
- Run `tools/context_health.py` when state/context files grow or context drift is suspected.
- Treat operational logs as optional debugging records; primary governance continuity comes from task, decision, state, handoff, and report artifacts.
