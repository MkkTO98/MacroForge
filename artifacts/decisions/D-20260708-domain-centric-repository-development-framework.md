# D-20260708 — Domain-Centric Repository Development Framework Accepted as Repository Development Planning Policy

Status: accepted
Date: 2026-07-08
Related task: `artifacts/tasks/TASK-167-domain-centric-repository-development-framework.md`
Related investigation: `artifacts/reports/R-20260708-domain-centric-repository-development-framework.md`
Related architecture: `docs/architecture/domain-centric-repository-development-framework.md`
Related framework: `docs/architecture/confidence-escalation-framework.md`

## Decision

Accept the Domain-Centric Repository Development Framework (DRDF) as MacroForge's repository-development planning policy during Operational Repository Evolution.

DRDF governs this question:

```text
Which analytically meaningful macroeconomic domain should MacroForge develop now, and what domain maturity gap matters most?
```

CEF continues to govern this separate question:

```text
What is the largest ingestion scope inside the selected target that can now be executed with acceptable evidence-backed confidence?
```

## Accepted planning hierarchy

Future repository-expansion planning should use this hierarchy:

```text
Strategic objective
  -> Macroeconomic domain
      -> Domain maturity gap
          -> Confidence cell
              -> CEF-sized campaign / slice
                  -> Source-specific implementation task
```

The macroeconomic domain is accepted as the primary repository-development planning unit. Provider, dataset family, confidence cell, and campaign remain valid subordinate units.

## Basis

The decision is supported by the investigation in `artifacts/reports/R-20260708-domain-centric-repository-development-framework.md`.

Main evidence:

- MacroForge's Constitution prioritizes trusted economic observations, uncertainty reduction, and downstream analytical usefulness over dataset count.
- Existing `docs/architecture/domain-coverage-assessment.md` and `docs/capability-atlas.md` already track repository usefulness by domain/coverage rather than provider count alone.
- `docs/architecture/long-term-domain-vision.md` accepts a broad source-backed observation-domain direction while explicitly preserving non-roadmap and non-implementation status.
- CEF already governs confidence-cell scope sizing, but CEF does not decide which economic domain is most valuable to complete.
- TASK-165 proved CEF can execute a large provider-capability campaign, but it also showed why broad provider-compatible expansion does not by itself define analytical completeness for any specific domain.
- Authoritative macro-statistical structures such as national accounts, IMF data/dissemination categories, and WDI topic organization support domain-oriented economic grouping rather than provider-only organization.

## Canonical planning domains

DRDF accepts the following lightweight domain model for planning and maturity assessment:

1. National Accounts and Real Activity.
2. Prices, Inflation, and Costs.
3. Labour, Employment, Wages, and Household Income.
4. Demographics, Human Capital, and Population Structure.
5. Government Finance and Public Debt.
6. Monetary, Banking, Credit, and Financial Intermediation.
7. Financial Markets, Asset Prices, and Market Reference Data.
8. External Sector and Cross-Border Finance.
9. International Trade, Tourism, and Supply Chains.
10. Industry, Production Structure, Agriculture, and Input-Output.
11. Energy, Commodities, Environment, and Climate Exposure.
12. Housing, Real Estate, and Construction.
13. Firms, Issuers, Business Formation, and Market Structure.

Cross-domain support areas include classification/reference evidence, release/revision/vintage evidence, and validation/lineage evidence.

This model is not an ontology, schema, source registry, implementation order, or KnowledgeForge semantic model.

## Domain maturity methodology

Domain maturity must remain dimensional rather than a single score.

Accepted dimensions:

- conceptual core coverage;
- analytical relationship coverage;
- geographic coverage;
- historical and frequency coverage;
- provider/source coverage;
- representation maturity;
- operational maturity;
- validation maturity;
- canonical/loading maturity;
- downstream readiness.

Analytical-completeness claims must be scope-qualified and evidence-backed.

## CEF integration

Future planning should proceed as:

```text
Select or continue active macroeconomic domain
        -> Assess domain maturity dimensions and analytical-completeness gaps
        -> Identify the highest-value maturity gap for downstream usefulness
        -> Translate the gap into candidate confidence cells
        -> CEF selects the largest safe next scope
        -> Existing source-specific workstreams execute
        -> Update CEF confidence
        -> Update domain maturity
        -> Decide continue/hold/transition
```

CEF remains responsible for how expansion occurs. DRDF governs what repository gap should be expanded.

## Consequences

- Future CEF planning artifacts should identify the target domain and maturity gap before selecting a campaign scope.
- Domain roadmaps guide strategy but do not create detailed implementation backlogs.
- `docs/architecture/domain-coverage-assessment.md` remains a lightweight factual coverage map and should be updated only for affected domains after implementations.
- Broad provider expansion is justified only when it advances a domain objective or tests a needed confidence cell.
- Provider diversity alone is not a sufficient repository-development objective.
- DRDF should reduce downstream context-reconstruction work for KnowledgeForge, InsightForge, BriefForge, and future EIP workflows.

## Non-authorization

This decision does not authorize:

- new ingestion campaigns;
- source onboarding;
- full WDI catalog ingestion;
- provider mirroring;
- provider diversity as an objective;
- generic source/provider/domain frameworks;
- a domain ontology;
- a data catalog;
- a scoring engine;
- schema changes;
- KnowledgeForge semantics;
- Companies/canonical identity work;
- production/live ingestion;
- weakening CEF, tests, closeout, or architecture gates;
- git push.
