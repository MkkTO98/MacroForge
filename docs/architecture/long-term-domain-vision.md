# MacroForge Long-Term Domain Vision

Status: accepted non-binding architectural vision
Accepted by: architectural review and formalization request, 2026-06-30
Governing decision: `artifacts/decisions/DEC-023-long-term-domain-vision-and-knowledgeforge-boundary.md`

## Purpose

This document records MacroForge's accepted long-term domain direction without changing its implementation methodology.

MacroForge may gradually expand toward a broad, source-backed, canonical observation substrate for the world economy. This is a vision for domain scope, not an implementation roadmap, source priority list, architecture redesign, or authorization to build speculative infrastructure.

The governing objective remains the Strategic Constitution: reduce the marginal cost of acquiring, updating, validating, canonicalizing, and maintaining trustworthy economic data while preserving determinism, auditability, provenance, reproducibility, and canonical consistency.

## Non-roadmap status

This vision does not define implementation order.

It does not authorize:

- implementation tasks;
- source onboarding;
- future source selection;
- implementation milestones;
- canonical entity infrastructure;
- graph/catalog systems;
- source frameworks;
- provider metadata frameworks;
- semantic validation systems;
- changes to `ObservedIngestionPackage`;
- changes to the deterministic post-boundary substrate;
- changes to the frozen heterogeneous-source execution loop.

Actual source selection remains governed by implementation evidence, DEC-022, the Strategic Constitution, current architectural confidence/pain/cost evidence, and the bounded heterogeneous-source loop.

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

MacroForge must preserve provider/source evidence and mapping status. It must not infer final canonical truth, semantic meaning, causal relationships, or investment conclusions from data loading alone.

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

KnowledgeForge may reference MacroForge artifacts, but should not copy full MacroForge observational datasets into its own persistent store.

## Boundary rule

If an artifact is primarily about measured/source-observed economic values, their provenance, reproducibility, lineage, validation, or canonical observational identity, it belongs to MacroForge.

If an artifact is primarily about reusable meaning, semantic identity, claims, hypotheses, causal relationships, relationship interpretation, evidence evaluation, confidence, uncertainty, contradictions, methodological meaning, or epistemic state, it belongs to KnowledgeForge.

## Long-term observation domains

MacroForge may eventually cover any source-backed economic observation domain that satisfies the Constitution and reduces future trusted-data effort without weakening determinism, auditability, provenance, reproducibility, or canonical consistency.

Potential long-term observation domains include, without implying order or implementation commitment:

- country macroeconomic observations, including GDP, national accounts, GDP components, inflation, monetary indicators, fiscal indicators, and productivity;
- demographics and population observations;
- labor market observations, including employment, unemployment, wages, hours, participation, vacancies, and productivity-related labor measures;
- household, housing, income, consumption, and balance-sheet observations;
- government finance observations, including revenue, spending, debt, deficits, issuance, maturity structure, and fiscal operations;
- monetary, credit, banking, interest-rate, yield-curve, and financial-market reference observations;
- exchange-rate and currency observations;
- balance-of-payments, international investment position, reserves, external debt, FDI, portfolio investment, banking-flow, and other cross-border financial-flow observations;
- international trade observations, including country, partner, product/classification, value, volume, direction, and classification hierarchy evidence;
- industry and sector observations, including output, value added, employment, wages, productivity, investment, and supply-use/input-output evidence;
- energy and commodity observations, including production, consumption, trade, inventories, prices, and physical-unit evidence;
- company and issuer observations where source-backed and bounded, including identities, filings, reported financial statements, reported segment data, reported operational metrics, source-reported ownership, source-reported events, and reproducible filing/source references;
- official classifications and classification-version evidence where needed to preserve observational meaning, including geography, product, industry, sector, instrument, currency, unit, and frequency classifications;
- release, revision, vintage, and publication-event observations where needed for point-in-time macroeconomic research.

These domains are scope possibilities, not roadmap phases. Coverage should expand only through bounded implementation work that leaves MacroForge permanently more capable than before.

## Canonical entity posture

A future canonical entity capability may naturally emerge where repeated implementations demonstrate recurring mapping or identity pain.

This vision does not authorize a canonical entity layer now.

Any future entity-oriented infrastructure must satisfy the existing extraction gate:

1. contract convergence;
2. algorithm convergence;
3. implementation convergence;
4. deterministic verification;
5. acceptable coupling;
6. measurable reduction in future implementation effort.

Observation-facing identities may be introduced only where needed by approved source/canonicalization work and must preserve source evidence, mapping status, and human authority over high-impact economic semantics.

## Consistency constraints

This vision is subordinate to:

- `CONSTITUTION.md`;
- DEC-022;
- `state/architecture.md`;
- `docs/architecture/observed-ingestion-representation.md`;
- current MacroForge / KnowledgeForge interface boundaries.

If future work conflicts with this vision and the Constitution or DEC-022, the Constitution and DEC-022 govern.

This vision clarifies long-term scope. It does not broaden implementation authority.
