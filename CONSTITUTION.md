# ProjectForge Constitution

ProjectForge exists to create and maintain boring, legible, reusable project environments for agent-assisted work.

## Non-negotiable rules

1. Project state must be explicit on disk, not hidden in chat memory.
2. Setup answers and deferred specifications must be stored as decision artifacts under `artifacts/decisions/`.
3. Agents must not silently invent project-wide policy. If a decision is absent, ambiguous, or conflicting, use deferred specification and clarification severity rules.
4. GitHub pushes require human approval by default. Auto-commit is allowed only after validation passes and policy permits it.
5. Dry-run/preflight is mandatory according to the risk-scaled dry-run policy in `simulation/dry_run_policy.yaml`.
6. Capability failures escalate to stronger local models before cloud models and before humans. Permission, safety, credential, destructive, monetary, or strategic decisions escalate to humans.
7. Specialized agents are never created silently. ProjectForge may request one with a short explanation; after approval, it may generate the agent automatically.
8. Skills should be small and composable by default. Large playbooks are allowed only for complex domains.
9. Metrics must be used to improve agents, tools, model routing, templates, and task workflows, but not to justify opaque automation.
10. The system must remain understandable from ordinary files: Markdown, YAML, JSON, and JSONL.
11. Raw logs are audit/debug artifacts only and must not be loaded into normal task context.
12. Cloud/Codex model calls require a context audit. Compact governance calls use the configured governance budget; justified project-wide reviews, redesigns, strategic reviews, gap analyses, and architecture audits may use the larger configured project-wide review budget.

## Default operating posture

The default is AI-first project execution under human-designed constraints. Humans specify constitution, risk boundaries, and project intent; agents execute inside those boundaries.
