# MacroForge Constitution

MacroForge exists to progressively reduce the recurring effort required to build, maintain, validate, canonicalize, and use trusted macroeconomic data for investment-relevant research.

MacroForge is not merely a trusted macroeconomic database. Trusted macroeconomic databases and datasets are outputs of MacroForge. The project itself is the effort-reduction machine that makes trusted macroeconomic data increasingly cheaper, safer, clearer, and more reproducible to produce, maintain, validate, canonicalize, and use.

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
13. Future work must be evaluated by the question: which recurring effort does this reduce? Relevant recurring efforts include source onboarding, source maintenance, validation, canonical mapping, schema evolution, downstream analysis, and future agent recovery/context effort. If a proposed component does not clearly reduce one of these while preserving trust, defer it unless an accepted decision explains the exception.

## Trust doctrine

No data is trusted merely because it loaded.

Trust requires, where relevant:

- source evidence;
- reproducibility evidence such as checksum or equivalent;
- staging or equivalent source-preserving transform;
- lineage;
- quality checks;
- canonical mapping status;
- validation report;
- replay or rerun path;
- human review where high-impact economic meaning is involved.

PostgreSQL stores accepted analytical data. PostgreSQL is not, by itself, proof of truth.

## Source-specific-first doctrine

Start source-specific. Extract shared mechanics only after repeated non-semantic duplication appears.

Do not create generalized ingestion frameworks, plugin systems, base classes, schedulers, or orchestration systems merely because they seem architecturally elegant. Abstraction must be earned by recurring effort evidence.

## Canonical-domain doctrine

Provider representations are evidence. Canonical identities are domain concepts.

Provider codes must not become curated truth merely because they are easy to ingest. Canonical-domain semantics must not be sacrificed for ingestion convenience. High-impact economic concepts require review-gated acceptance.

## Automation and model-role doctrine

Automation is justified only when it reduces recurring effort without weakening trust.

Deterministic code owns parsing, transforms, checks, loads, validation, replay, and deterministic reports.

Local models may assist with bounded proposal work such as source documentation triage, metadata summarization, label extraction, mapping proposals, and anomaly explanation. Local models produce proposals, not truth.

Cloud LLMs and Hermes-level governance should handle doctrine, architecture, ambiguity, audit, consistency review, difficult error analysis, and bounded task orchestration.

Humans retain authority over purpose, risk boundaries, high-impact semantic decisions, schema doctrine, production/live authority, destructive actions, secrets, paid API use, and investment conclusions.

Automate proposals and checks. Do not automate authority.

## Governance doctrine

Governance exists to reduce future uncertainty and agent recovery cost.

Governance that does not improve trust, reproducibility, maintainability, semantic correctness, or recurring effort reduction should be pruned, consolidated, or deferred. Avoid governance theater.

A report, decision, manifest, registry, or artifact is justified only if it improves trust, reproducibility, recovery, maintainability, semantic correctness, or future effort reduction.

## Work that must never be silently automated

Do not silently automate:

- constitutional purpose changes;
- architecture doctrine changes;
- high-impact economic semantic acceptance;
- final truth assignment for canonical mappings based only on model confidence;
- unit/currency/frequency conversion policy;
- investment conclusions or portfolio decisions;
- live/default database writes;
- destructive operations;
- secrets or credential handling;
- paid or billing-sensitive API use;
- Git push or publication;
- broad source onboarding without purpose/evidence rationale;
- schema evolution that changes canonical meaning;
- suppression of validation failures;
- replacement of provenance/evidence with model summaries;
- human review policy changes;
- promotion from fixture evidence to production/live behavior.

## Default operating posture

The default is AI-first project execution under human-designed constraints. Humans specify constitution, risk boundaries, and project intent; agents execute inside those boundaries.

The next likely technical/design candidate remains bounded review-to-accepted/provisional canonicalization lifecycle validation. It should be framed as a test of whether MacroForge can reduce future manual canonicalization effort while preserving trust, provenance, and review-gated semantic correctness. It is not approved as an active task until explicitly created and accepted.
