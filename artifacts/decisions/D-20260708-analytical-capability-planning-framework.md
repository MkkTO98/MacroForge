# D-20260708 — Analytical Capability Planning Framework Accepted as DRDF Planning Layer

Status: accepted
Date: 2026-07-08
Related task: `artifacts/tasks/TASK-168-analytical-capability-planning-framework.md`
Related investigation: `artifacts/reports/R-20260708-analytical-capability-planning-framework.md`
Related architecture: `docs/architecture/analytical-capability-planning-framework.md`
Related frameworks: `docs/architecture/domain-centric-repository-development-framework.md`, `docs/architecture/confidence-escalation-framework.md`

## Decision

Accept the Analytical Capability Planning Framework (ACPF) as a lightweight planning layer between macroeconomic domains and confidence cells.

Analytical capability is accepted as the operational repository-development planning unit inside a selected macroeconomic domain.

## Accepted hierarchy

```text
Strategic objective
  -> Macroeconomic domain
      -> Analytical capability
          -> Capability maturity / completeness gap
              -> Confidence cell
                  -> CEF-sized campaign / slice
                      -> Source-specific implementation task
```

## Responsibility split

- DRDF governs domain portfolio choice and macroeconomic coherence.
- ACPF governs analytical function, capability dependencies, maturity/completeness gap, and stopping criteria.
- CEF governs largest safe ingestion scope using confidence cells and multidimensional confidence evidence.
- Source-specific implementation workstreams execute approved scopes.

## Basis

The decision is supported by `artifacts/reports/R-20260708-analytical-capability-planning-framework.md`.

Main evidence:

- Downstream analytical work is performed through functions, not through raw providers, dataset families, or broad domains.
- Domain planning alone is too broad to decide whether a workflow is supported.
- Confidence cells are necessary for scope safety but do not identify downstream analytical value.
- Existing MacroForge coverage artifacts already express gaps in capability-like terms: labor monitoring, trade balance/flows, external vulnerability, debt burden, inflation monitoring, housing pipeline, and similar workflows.
- Capability-level stopping criteria are clearer than provider-complete, dataset-complete, or exhaustive-collection criteria.

## Accepted capability definition

An analytical capability is a source-backed repository function that lets downstream systems perform a class of economic analysis without reconstructing basic data, relationships, context, provenance, validation status, and caveats from raw provider structures.

A capability must describe:

- analytical objective;
- economic question;
- conceptual components;
- required repository support;
- dependencies;
- maturity gaps;
- downstream consumers;
- stopping criteria;
- boundaries/non-goals;
- candidate confidence cells.

## Maturity and completeness

Capability maturity must remain dimensional. Do not reduce it to a single score.

Accepted dimensions:

- conceptual completeness;
- repository support;
- operational maturity;
- validation maturity;
- geographic coverage;
- historical/frequency coverage;
- provider/source confidence;
- dependency readiness;
- downstream readiness;
- boundary clarity.

A capability is analytically complete for a stated scope when MacroForge supports the intended workflow well enough that downstream systems do not need to reconstruct basic evidence, context, dependencies, provenance, validation status, or caveats, and remaining missing datasets would mostly add marginal detail, breadth, redundancy, or convenience.

## Consequences

- Future DRDF/CEF planning should name the target domain and analytical capability before selecting a confidence cell.
- Capability dependencies should be recorded only when required by the analytical workflow.
- Stopping criteria should be workflow-based, not provider-count, dataset-count, or row-count based.
- `docs/capability-atlas.md` remains an implemented-capability inventory and should not become a speculative capability catalog.
- `docs/architecture/domain-coverage-assessment.md` remains factual coverage state and should not be updated by planning-only tasks.

## Non-authorization

This decision does not authorize:

- ingestion campaigns;
- source onboarding;
- schema changes;
- provider mirroring;
- dataset-complete acquisition;
- generic source/provider/domain/capability frameworks;
- runtime capability registry implementation;
- KnowledgeForge semantics or claims;
- InsightForge or BriefForge implementation;
- Companies/canonical identity work;
- production/live ingestion;
- git push.
