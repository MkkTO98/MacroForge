# DEC-023 — Long-Term Domain Vision and KnowledgeForge Boundary

Status: accepted
Date: 2026-06-30
Related vision: `docs/architecture/long-term-domain-vision.md`
Related decision: `artifacts/decisions/DEC-022-next-ten-source-expansion-optimization.md`
Related boundary: `/home/mkkto/srv/EIP/projects/KnowledgeForge/docs/interfaces.md`

## Decision

MacroForge accepts a long-term domain vision: it may gradually expand toward a broad, source-backed, canonical observation substrate for the world economy.

This is accepted only as a non-binding architectural vision. It is not a fixed roadmap, not implementation authorization, not source-selection priority, not a schema design, and not permission to introduce speculative infrastructure.

The current implementation methodology remains unchanged:

```text
Select heterogeneous source
-> Predict
-> Implement
-> Verify
-> Implementation Lessons
-> Architectural Surprise Log
-> Architectural Confidence calibration
-> Marginal Source Cost Index update
-> Recurring Implementation Pain update
-> Continue with the next heterogeneous source
```

Future architecture continues to evolve only from repeated implementation evidence.

## Artifact classification

The accepted direction is represented by two minimum artifacts:

1. `docs/architecture/long-term-domain-vision.md`
   - Type: non-binding architectural vision.
   - Purpose: define long-term observation scope and project boundaries without defining order or implementation commitments.

2. This decision record.
   - Type: architectural decision.
   - Purpose: record the formal status, constraints, and boundary interpretation so the vision cannot be mistaken for a roadmap or implementation authorization.

No separate roadmap, implementation strategy, task artifact, canonical entity design, or new interface specification is approved by this decision.

## MacroForge responsibility

MacroForge owns source-backed observable economic evidence and the deterministic ingestion/canonicalization capability required to make that evidence reproducible and analytically usable.

MacroForge may own or expose:

- ingestion;
- validation;
- canonicalization of observations where scoped and approved;
- observational lineage;
- reproducibility handles;
- source observational identities;
- canonical observational identifiers;
- dataset, series, source, release, and version references;
- source indicator metadata;
- quality and lineage metadata;
- evidence references;
- quantitative and source-backed economic observations.

MacroForge does not infer final semantic truth, causal meaning, confidence-bearing claims, or investment conclusions from loaded data alone.

## KnowledgeForge responsibility

KnowledgeForge owns governed reusable knowledge constructed from or referencing MacroForge observations and other evidence sources.

KnowledgeForge owns:

- reusable concepts;
- semantic identities;
- mappings from source indicators to canonical concepts where those mappings are knowledge objects;
- durable claims;
- hypotheses;
- causal and relationship representations;
- knowledge dependencies;
- negative knowledge;
- methodological knowledge;
- evidence-backed empirical claims;
- evidence evaluations;
- confidence, uncertainty, contradictions, and competing explanations;
- provenance and epistemic state for knowledge objects;
- lifecycle and governance state of knowledge objects.

KnowledgeForge may reference MacroForge artifacts. It should not copy full MacroForge observational datasets into its own persistent store.

## Boundary rule

If an artifact is primarily about measured/source-observed economic values, provenance, reproducibility, lineage, validation, or canonical observational identity, it belongs to MacroForge.

If an artifact is primarily about reusable meaning, semantic identity, claims, hypotheses, causal relationships, relationship interpretation, evidence evaluation, confidence, uncertainty, contradictions, methodological meaning, or epistemic state, it belongs to KnowledgeForge.

## Rationale

The accepted architectural review concluded that MacroForge should be allowed to expand from current macroeconomic source slices toward broader world-economy observations, but only under existing governance constraints.

This formalization is needed because the direction is strategically important but easy to misread as a roadmap. Without an explicit status decision, future agents could incorrectly treat country data -> trade -> industry -> flows -> companies as an ordered implementation sequence or as permission to design canonical entity infrastructure.

The vision belongs in architecture documentation because it defines durable scope boundaries and long-term domain intent. It does not belong in `CONSTITUTION.md` because the Constitution already governs the stronger optimization objective and explicitly is not a fixed roadmap. It does not belong in `docs/roadmap.md` because the roadmap is evidence-driven and non-fixed. It does not belong as a task because no implementation work is authorized.

## Explicit non-authorizations

This decision does not authorize:

- implementation tasks;
- future source priorities;
- source onboarding;
- implementation milestones;
- broad provider support;
- production/live behavior;
- canonical entity infrastructure;
- graph/catalog systems;
- source frameworks;
- provider metadata frameworks;
- semantic validation systems;
- AI/model canonicalization;
- changes to `ObservedIngestionPackage`;
- changes to the deterministic post-boundary substrate;
- changes to the frozen methodology;
- changes to MacroForge / KnowledgeForge project boundaries.

## Domain scope posture

MacroForge may eventually cover source-backed observations across country macroeconomics, demographics, labor, housing, government finance, monetary/credit/banking/interest-rate data, exchange rates, international trade, industry/sector structure, financial flows, energy/commodities, companies/issuers, official classifications, and release/revision/vintage/publication-event evidence.

These are observation scope possibilities, not roadmap phases. They do not imply commitment to any source, order, implementation sequence, database schema, entity model, or infrastructure layer.

## Canonical entity posture

A future canonical entity capability may naturally emerge from repeated source and mapping implementations.

This decision does not authorize a canonical entity layer.

Any future entity-oriented infrastructure must satisfy the existing extraction gate:

1. contract convergence;
2. algorithm convergence;
3. implementation convergence;
4. deterministic verification;
5. acceptable coupling;
6. measurable reduction in future implementation effort.

Observation-facing identities may be introduced only where needed by approved bounded source/canonicalization work and must preserve source evidence, mapping status, and human authority over high-impact economic semantics.

## Consistency check

This decision preserves:

- Strategic Constitution v1.1: implementation-first, evidence-driven, source-specific-first, deterministic, auditable ingestion capability remains the strategic asset.
- DEC-022: next-source planning remains optimized for reducing marginal future implementation effort, and the current post-boundary architecture remains assumed correct unless repeated evidence falsifies it.
- Current architecture: `ObservedIngestionPackage` remains the boundary after source-specific acquisition/normalization; deterministic post-boundary substrate remains unchanged.
- KnowledgeForge interface definitions: MacroForge owns observations and reproducibility; KnowledgeForge owns reusable meaning, claims, relationships, evidence evaluation, and epistemic state.

No architectural drift, implementation commitment, infrastructure authorization, or project-boundary change is introduced.

## Consequences

Future agents should treat `docs/architecture/long-term-domain-vision.md` as scope clarification only.

When selecting future work, agents must still follow the Constitution, DEC-022, current architecture state, architectural confidence/pain/cost evidence, and the bounded heterogeneous-source execution loop.

If a future proposal attempts to use the vision as justification for speculative infrastructure or fixed source ordering, this decision rejects that interpretation.
