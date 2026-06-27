# MacroForge Strategic Constitution v1.1

Status: active governing optimization objective
Adopted UTC: 2026-06-26T20:50:21Z

This document establishes the long-term governing principles for MacroForge.

It supersedes individual implementation preferences and serves as the optimization objective against which all future implementation work should be evaluated.

The goal of this document is not to prescribe a fixed roadmap.

Its purpose is to guide the continuous evolution of MacroForge for the remainder of its development.

## MacroForge's mission

MacroForge exists to transform heterogeneous public economic evidence into deterministic, canonical, auditable observations suitable for long-term analytical use.

Its primary asset is not its PostgreSQL database.

Its primary asset is an increasingly reusable, trustworthy, deterministic ingestion capability.

Data is an output.

Ingestion capability is the strategic asset.

## Primary optimization objective

Optimize MacroForge so that:

> The marginal cost of acquiring, updating, validating, and maintaining trustworthy economic data continuously decreases over time without sacrificing determinism, auditability, provenance, or canonical consistency.

Success is measured over years rather than individual implementation tasks.

## Long-term philosophy

MacroForge should continuously increase the proportion of the ingestion lifecycle executed by shared, deterministic, evidence-derived infrastructure while continuously decreasing:

- deterministic engineering effort;
- human judgment;
- LLM reasoning;

required to acquire, update, validate, and maintain trustworthy economic data.

Every architectural decision should move MacroForge toward this objective.

## Knowledge accumulation

MacroForge should not merely accumulate datasets.

It should accumulate ingestion knowledge.

Examples include:

- provider behavior;
- schema evolution;
- metadata interpretation;
- identifier mappings;
- validation knowledge;
- lineage patterns;
- parser knowledge;
- release behavior;
- provider-specific quirks.

Every newly supported dataset should leave the platform permanently more capable than before.

## Architectural philosophy

Good abstractions are extracted from implementation evidence.

They are not designed speculatively.

Shared infrastructure should emerge only after repeated implementation demonstrates stable common behavior.

Implementation drives architecture.

Architecture does not speculate beyond implementation evidence.

## Source-specific versus shared responsibilities

Source-specific responsibilities include:

- acquisition;
- authentication;
- downloading;
- parsing;
- source-specific metadata;
- source-specific staging.

Shared deterministic infrastructure should progressively own:

- observed ingestion representation;
- deterministic validation;
- canonical loading;
- lineage generation;
- quality checks;
- deterministic replay;
- diagnostics;
- verification;
- provider metadata infrastructure;
- future reusable canonical infrastructure.

The goal is not to eliminate source-specific acquisition.

The goal is to maximize deterministic shared infrastructure after the observed ingestion boundary.

## Rules for extracting shared infrastructure

A repeated behavior becomes eligible for shared infrastructure only when:

1. the contract has converged;
2. the algorithm has converged;
3. the implementation has converged.

Textual similarity alone is insufficient.

Evidence must come from existing implementations.

Extraction should reduce future work while preserving correctness.

## Shared infrastructure invariant

Shared infrastructure must never depend on source-specific conditionals.

If generic infrastructure requires logic such as:

- if source == WDI;
- if source == OECD;
- if source == EUROSTAT;

then the abstraction is likely incorrect.

Source-specific behavior belongs in adapters that produce the shared contract.

## Confidence before convenience

Reducing engineering effort is valuable.

Increasing confidence is mandatory.

MacroForge should prefer an implementation that produces greater confidence in correctness even if it yields slightly smaller engineering savings.

Determinism, provenance, auditability, and canonical consistency take precedence over convenience.

MacroForge should increase the proportion of future work that can be executed with high confidence from deterministic evidence rather than exploratory reasoning.

Uncertainty reduction is an explicit optimization objective. Tasks that create replay, diagnostics, contract validation, or equivalence evidence may be high leverage even when they do not immediately reduce code volume.

## Capability-oriented planning

MacroForge planning should use this hierarchy:

```text
Strategic Objective
  -> Durable Platform Capabilities
      -> Implementation Tasks
```

Capabilities represent durable platform abilities. Tasks implement or improve capabilities.

Use a lightweight capability maturity lifecycle:

- Discovered: repeated behavior or need has been observed.
- Specified: a narrow evidence-backed contract or target behavior is documented.
- Verified: deterministic checks prove current behavior and preserve equivalence.
- Adopted: the verified capability is the canonical implementation path MacroForge uses for the relevant scope.
- Shared: implementation has been extracted into reusable shared infrastructure without source-specific conditionals.
- Stable: the capability is used by multiple current paths and has regression protection.
- Mature: the capability can guide future source/dataset work with low uncertainty and minimal strategic intervention.

`Adopted` distinguishes proof from canonical use. A capability can be verified by deterministic equivalence checks without yet becoming the canonical implementation that future work depends on.

Track maturity only in state/backlog/handoff artifacts and the lightweight capability model document. Do not create a heavy portfolio-management subsystem.

Default development workflow after governance freeze:

```text
Implement
  -> Verify
  -> Update capability maturity
  -> Select next capability/task from evidence
  -> Implement
```

Future architectural reports should only be created when implementation exposes uncertainty that cannot be resolved from the Constitution, capability graph, contracts, dependency graph, or deterministic verification evidence.

## ArchitectureHarvest consultation

ArchitectureHarvest should not be consulted uniformly.

Instead, consultation intensity should increase dramatically whenever Hermes proposes extracting new shared infrastructure.

At these architectural extraction points, Hermes should perform a deep ArchitectureHarvest consultation to identify:

- existing implementations;
- mature design patterns;
- common failure modes;
- architectural blind spots;
- alternative approaches;
- reasons not to extract the abstraction.

The purpose is to strengthen shared infrastructure before it becomes part of MacroForge's long-term architecture.

The active consultation trigger for this class is:

```text
foundational_capability_extraction
```

This trigger applies when proposed implementation is expected to become a reusable dependency of multiple future capabilities. It deliberately uses capability language rather than current infrastructure terminology so the policy follows MacroForge's long-term optimization objective.

Routine implementation work should continue using the existing bounded consultation policy.

## AI usage

LLMs are advisory tools.

They assist semantic reasoning until deterministic infrastructure replaces repeated reasoning.

Success is measured by reducing future LLM reasoning rather than increasing AI usage.

## Negative objectives

MacroForge must not evolve into:

- a generalized ETL framework;
- a workflow orchestration platform;
- a plugin ecosystem;
- a generic data platform;
- an AI-driven ingestion engine.

Its scope remains deliberately narrow:

Acquire trustworthy economic evidence and transform it into canonical, deterministic, auditable observations.

## Task evaluation framework

Every proposed implementation task should be evaluated using the following criteria.

Estimate:

- reduction in future deterministic engineering;
- reduction in future human effort;
- reduction in future LLM reasoning;
- reduction in future uncertainty / increase in proportion of future work executable with high confidence;
- increase in confidence;
- knowledge accumulated;
- architectural leverage;
- implementation complexity introduced;
- long-term maintenance burden.

Tasks that compound future capability should receive higher priority than tasks that merely increase dataset count.

## Development sequence

MacroForge should generally evolve according to this sequence:

1. discover repeated implementation;
2. identify implementation evidence;
3. prove semantic equivalence;
4. extract shared contract;
5. validate deterministically;
6. extract shared implementation;
7. expand dataset coverage;
8. repeat.

Do not reverse this order without strong evidence.

## Roadmap governance

The implementation roadmap is no longer fixed.

Instead, Hermes should continuously reassess it after every completed architectural milestone.

Each reassessment should determine:

- whether dependencies have changed;
- whether higher-leverage infrastructure has emerged;
- whether ArchitectureHarvest consultation identifies better alternatives;
- whether the next task still maximizes long-term leverage.

The roadmap should evolve from implementation evidence rather than historical planning.

## Trust doctrine retained from prior constitution

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

## Authority and safety boundaries retained from prior constitution

Humans retain authority over purpose, risk boundaries, high-impact semantic decisions, schema doctrine, production/live authority, destructive actions, secrets, paid API use, and investment conclusions.

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

## Project state and operating rules retained from prior constitution

1. Project state must be explicit on disk, not hidden in chat memory.
2. Durable architectural/product decisions should be stored as decision artifacts under `artifacts/decisions/` when they need future authority beyond state/report artifacts.
3. Agents must not silently invent project-wide policy. If a decision is absent, ambiguous, or conflicting, use deferred specification and clarification severity rules.
4. GitHub pushes require human approval.
5. Dry-run/preflight remains mandatory according to the risk-scaled dry-run policy in `simulation/dry_run_policy.yaml` when the action is risky enough to require it.
6. Specialized agents are never created silently.
7. The system must remain understandable from ordinary files: Markdown, YAML, JSON, and JSONL.
8. Raw logs are audit/debug artifacts only and must not be loaded into normal task context.
9. Governance exists to reduce future uncertainty and agent recovery cost, not to create theater.
