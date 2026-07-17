# Analytical Capability Planning Framework

Status: accepted planning and governance layer
Date: 2026-07-08
Related task: `artifacts/tasks/TASK-168-analytical-capability-planning-framework.md`
Related investigation: `artifacts/reports/R-20260708-analytical-capability-planning-framework.md`
Related decision: `artifacts/decisions/D-20260708-analytical-capability-planning-framework.md`
Related frameworks: `docs/architecture/domain-centric-repository-development-framework.md`, `docs/architecture/confidence-escalation-framework.md`

## Purpose

The Analytical Capability Planning Framework (ACPF) refines DRDF by adding an analytical-capability layer between macroeconomic domain selection and confidence-cell scope sizing.

ACPF answers:

```text
What downstream analytical function should MacroForge make possible inside the selected macroeconomic domain?
```

DRDF answers:

```text
Which macroeconomic domain should MacroForge develop, and why does that domain matter now?
```

CEF answers:

```text
What is the largest ingestion scope supporting that target capability that can now be executed with acceptable evidence-backed confidence?
```

ACPF is planning/governance only. It is not runtime infrastructure, a capability registry implementation, a semantic ontology, a source/provider framework, a data catalog, a scoring engine, a schema change, a KnowledgeForge substitute, or authorization for ingestion.

## Accepted planning hierarchy

Future repository-development planning should use this hierarchy:

```text
Strategic objective
  -> Macroeconomic domain
      -> Analytical capability
          -> Capability maturity / completeness gap
              -> Confidence cell
                  -> CEF-sized campaign / slice
                      -> Source-specific implementation task
```

Domains remain the portfolio-level organizing unit. Analytical capabilities become the operational planning unit for repository usefulness inside a domain. Confidence cells remain the CEF unit for safe ingestion scope.

## Definition

An analytical capability is a source-backed repository function that lets downstream systems perform a class of economic analysis without reconstructing the basic data, relationships, context, provenance, and caveats from raw provider structures.

A capability is not:

- a provider;
- a dataset family;
- an indicator list;
- a campaign;
- a dashboard;
- a model output;
- an investment conclusion;
- a KnowledgeForge semantic concept;
- a generic software capability.

A valid analytical capability must name:

1. Analytical objective.
2. Economic question addressed.
3. Required conceptual components.
4. Required repository support.
5. Dependencies on other capabilities or cross-domain support.
6. Explicit boundaries and non-goals.
7. Completion/stopping criteria.

## Why capabilities are the correct planning layer

The evidence supports analytical capability as the planning layer between domain and confidence cell because downstream analysis is performed through functions, not through provider mirrors or raw domains.

Examples from implemented MacroForge evidence:

- Labour is a domain; USA monthly labor-core monitoring is a capability requiring unemployment, labor-force participation, civilian employment, labor-force level, monthly frequency, national geography, provenance, validation, and known missing wage/turnover/demographic dimensions.
- Trade is a domain; trade-balance or trade-flow analysis is a capability requiring exports, imports, reporter/partner roles where applicable, values, period, geography, direction, units, and boundary notes about missing product/mirror/quantity evidence.
- External sector is a domain; external vulnerability analysis is a capability requiring current account or trade evidence, IIP positions, reserves/liquidity, external debt where available, GDP/FX/price context where used, and source-backed caveats.
- Prices is a domain; inflation monitoring is a capability requiring price index observations, inflation-rate or index-level semantics, frequency, geography, core/headline/component boundaries where available, validation, and known source comparability caveats.

Domain alone is too broad to produce concrete stopping criteria. Confidence cell alone is too source-facing to answer whether a useful analytical workflow is supported. Capability provides the missing bridge.

## Capability model

Each capability record should contain the following fields when used in planning artifacts:

```text
Capability name:
Domain:
Analytical objective:
Economic question:
Conceptual components:
Repository support required:
Current support evidence:
Dependencies:
Maturity gaps:
Downstream consumers:
Stopping criteria:
Non-goals / boundaries:
Candidate confidence cells:
```

### Conceptual components

Conceptual components describe the economic ingredients required by the analysis, not provider indicators. Examples:

- value flows;
- price/index evidence;
- stocks and positions;
- rates and yields;
- denominators such as GDP or population;
- geography and counterparty roles;
- sector, product, instrument, or classification roles;
- frequency, period, release, or vintage context;
- validation, lineage, and provenance evidence.

### Repository support

Repository support means MacroForge can provide deterministic, source-backed, provenance-preserving observations and supporting metadata at the required grain. It may include:

- canonical-loaded observations where approved;
- operational PostgreSQL-loaded datasets where scoped;
- evidence-only observed packages where sufficient for bounded analysis;
- source attributes, units, frequency, geography, classifications, raw evidence, checksums, reports, and validation artifacts;
- explicit gaps and caveats.

## Capability dependency model

Capabilities naturally depend on other capabilities or support evidence when the target workflow requires contextual variables that are not part of the same source family.

Accepted dependency types:

1. Numerator / denominator dependency
   - Example: trade openness depends on trade values and GDP.
2. Stock / flow dependency
   - Example: debt-burden analysis depends on debt stocks, fiscal flows, GDP, and interest costs.
3. Nominal / real / price-context dependency
   - Example: real-income or real-rate analysis depends on nominal values plus price/inflation evidence.
4. Domestic / external-context dependency
   - Example: external vulnerability depends on external positions/flows plus domestic GDP, reserves, FX, or debt context.
5. Rate / level dependency
   - Example: labor-market monitoring depends on unemployment rates and employment/labor-force levels.
6. Classification/reference dependency
   - Example: product-level trade depends on product classification evidence and reporter/partner geography evidence.
7. Release/revision/vintage dependency
   - Example: point-in-time macro analysis depends on vintage/release evidence, not only latest values.
8. Validation/lineage dependency
   - Example: any downstream analytical package depends on traceable source evidence, checksums, replay, and caveats.

Dependency edges should be recorded only when the analytical workflow genuinely requires the upstream support. Do not create dependency graphs for aesthetic completeness.

## Capability maturity methodology

Capability maturity is dimensional. Do not collapse maturity into a single score unless a later implementation proves that a scalar improves planning decisions without hiding blockers.

Track these dimensions:

1. Conceptual completeness
   - Are the economic components required by the workflow represented?
2. Repository support
   - Are source-backed observations and metadata available at the required grain?
3. Operational maturity
   - Can supporting evidence be refreshed, replayed, loaded, and verified deterministically where scoped?
4. Validation maturity
   - Are checks strong enough to catch wrong values, wrong grains, missing components, duplicates, mapping drift, and source anomalies?
5. Geographic coverage
   - Is the geography adequate for the intended workflow?
6. Historical/frequency coverage
   - Is the time span/frequency adequate for the workflow?
7. Provider/source confidence
   - Are the source paths authoritative or sufficiently cross-checkable for the workflow?
8. Dependency readiness
   - Are required supporting capabilities available at compatible scope?
9. Downstream readiness
   - Can KnowledgeForge, InsightForge, BriefForge, or future EIP consumers use the capability without reconstructing basic context?
10. Boundary clarity
   - Are caveats and non-goals explicit enough to prevent false analytical claims?

Recommended labels:

- Discovered: capability is named but not yet specified.
- Specified: objective, components, dependencies, and boundaries are defined.
- Supported: enough evidence exists for a bounded workflow, but operations/validation may be partial.
- Operationally Useful: deterministic operational evidence supports the intended current workflow.
- Analytically Complete for Current Scope: core workflow is supported; remaining missing evidence is marginal or explicitly out of scope.
- Blocked/Frozen: a dependency, identity boundary, semantics question, or authority gate prevents progress.

## Analytical completeness

A capability is analytically complete for a stated scope when MacroForge supports the intended analytical workflow well enough that downstream systems do not need to reconstruct basic evidence, context, dependencies, provenance, validation status, or caveats; and when remaining missing datasets would mostly add detail, breadth, redundancy, or convenience rather than change the workflow's first-order analytical validity.

Distinctions:

- Analytically complete: the intended workflow can be performed with adequate source-backed evidence and explicit caveats.
- Provider complete: all relevant datasets from a provider/source family are ingested. This is not required and may be wasteful.
- Dataset complete: all fields/series in a dataset family are ingested. This is not required unless the workflow demands it.
- Exhaustive collection: every available indicator/source is collected. This is explicitly not a MacroForge objective.

Completeness must always be scope-qualified:

```text
Analytically complete for USA monthly labor-core monitoring, 2015-M01 through 2024-M12.
Operationally useful but not analytically complete for bilateral product-level trade exposure.
Not complete for cross-provider GDP comparability because unit/frequency/conversion policy remains unresolved.
```

## Downstream validation

Downstream EIP systems naturally consume capabilities rather than raw providers or broad domains.

KnowledgeForge:
- consumes capability-backed evidence to ground claims and knowledge objects;
- should not copy MacroForge datasets or treat provider structures as semantic truth;
- benefits when capability records name dependencies, boundaries, and evidence status.

InsightForge:
- needs analysis-ready capability packages such as inflation monitoring, trade-balance analysis, labor-cycle monitoring, or external vulnerability context;
- should not have to infer workflow readiness from provider coverage alone.

BriefForge:
- needs concise, traceable evidence packages for narrative briefs;
- consumes capabilities like labour-market monitoring, inflation monitoring, trade balance, external vulnerability, or fiscal burden more naturally than `WDI`, `FRED`, or `UN Comtrade` provider sets.

Future EIP analytical systems:
- should request repository support by capability and scope, then inspect evidence, dependencies, maturity, and caveats;
- should not use provider completeness as a proxy for analytical readiness.

## Stopping criteria

Capability-based planning improves stopping criteria because each expansion can stop when the intended workflow is adequately supported.

A capability may stop at `Analytically Complete for Current Scope` when:

1. Required conceptual components are represented.
2. Dependencies are supported at compatible scope or explicitly out of scope.
3. Geography, history, frequency, unit, and classification coverage match the workflow.
4. Validation and provenance are adequate for deterministic reuse.
5. Boundary notes prevent common false inferences.
6. Additional provider/dataset acquisition would mostly add marginal detail or breadth rather than unlock a new core workflow.
7. CEF either confirms no larger safe scope is currently needed or identifies any remaining work as lower priority.

Stopping is not justified by row count, provider count, dataset count, or campaign completion alone.

## Governance rules

1. A future repository-expansion task should name the target domain and analytical capability before CEF selects a concrete scope.
2. A capability plan should describe conceptual components and dependencies before listing indicators or providers.
3. CEF remains responsible for confidence cells, promotion/regression, campaign size, and localized safety constraints.
4. Source-specific implementation remains responsible for acquisition, parsing, normalization, and scoped loading.
5. Do not build a capability registry, ontology, graph, API, scoring engine, dashboard, or schema unless repeated planning/execution evidence shows that file-backed records no longer reduce recurring effort enough.
6. Capability dependency claims require workflow evidence; do not invent dependencies for completeness.
7. Downstream readiness claims must include caveats and non-goals.

## Non-authorization

This framework does not authorize:

- ingestion campaigns;
- source onboarding;
- schema changes;
- provider mirroring;
- dataset-complete acquisition;
- generic source/provider/domain/capability frameworks;
- runtime capability registry implementation;
- KnowledgeForge semantics or claims;
- InsightForge/BriefForge implementation;
- Companies/canonical identity work;
- production/live ingestion;
- git push.
