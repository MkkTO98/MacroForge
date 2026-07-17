# D-20260708 — Confidence Escalation Framework Accepted as Repository Expansion Orchestration Policy

Status: accepted
Date: 2026-07-08
Related task: `artifacts/tasks/TASK-163-confidence-escalation-framework.md`
Related architecture: `docs/architecture/confidence-escalation-framework.md`

## Decision

Accept the Confidence Escalation Framework (CEF) as a permanent MacroForge repository-expansion orchestration policy.

CEF governs this question:

```text
What is the largest ingestion scope that can now be executed with acceptable confidence based on accumulated evidence?
```

CEF is added as an additional capability. It does not replace architecture, ingestion, validation, operational evolution, repository-section maturity, or existing workstreams.

## Architectural classification

CEF is classified as:

1. architectural capability — evidence-based escalation/localized regression of ingestion scope;
2. operational methodology — future Workstream A planning should use it to size ingestion tasks;
3. orchestration policy — it governs promotion from isolated slices toward larger operational batches/families when evidence supports it;
4. repository governance artifact — it records how repository expansion becomes more throughput-oriented without abandoning evidence-first discipline.

CEF is not constitutional at this time. The existing Constitution already provides the controlling principles: evidence-first architecture, source-specific-first posture, deterministic validation, no premature extraction, and lightweight maturity tracking.

CEF is not a runtime framework, source registry, scheduler, provider mirror, production ingestion system, or generic provider/source abstraction.

## Basis

The investigation found existing evidence that a CEF belongs in MacroForge:

- `CONSTITUTION.md` requires evidence-gated architecture and explicitly values uncertainty reduction.
- `DEC-022` says implementation evidence should reduce future engineering, human, or LLM effort and that architecture should evolve only when repeated evidence justifies it.
- `D-20260703-operational-repository-v1-accepted-evolution.md` makes Operational Repository Evolution the primary activity and requires repository-section contribution in future implementations.
- `docs/architecture/capability-maturity-model.md` already tracks `Evidence-Accumulating Source Expansion` as a planning capability.
- `docs/architecture/architectural-confidence-ledger.md`, `architectural-surprise-log.md`, `marginal-source-cost-index.md`, and `recurring-implementation-pain.md` already collect evidence needed for promotion/regression decisions.
- Completed source and operational tasks through TASK-162 show that many source-specific slices are now low-cost, but provider mirrors, generic frameworks, and production/live ingestion remain explicitly unauthorized without stronger evidence.

## Deepest supported abstraction

The accepted abstraction is the ingestion confidence cell:

```text
provider or source family
+ acquisition/parser family
+ dataset family or dataflow
+ observation representation class
+ operational scope
+ canonicalization/loading authority, if any
```

This prevents an indicator-specific framework. It generalizes across scalar indicators, matrices, bilateral trade flows, revision-vintage observations, issuer facts, operational panels, parser families, and provider capabilities.

## Confidence dimensions

CEF uses separate evidence dimensions rather than one score:

- architectural confidence;
- provider/source confidence;
- parser/acquisition confidence;
- representation confidence;
- validation confidence;
- operational confidence;
- mapping/canonicalization confidence where in scope.

A scope may be ready for evidence-only ingestion while still not ready for canonical mapping, broad provider support, or production/live operation.

## Escalation methodology

Promotion proceeds only when explicit evidence supports the larger scope:

1. Stage 0 — source-path discovery.
2. Stage 1 — isolated bounded evidence slice.
3. Stage 2 — stratified evidence sample.
4. Stage 3 — small representative operational batch.
5. Stage 4 — thematic or dataset-family operational ingestion.
6. Stage 5 — provider-capability expansion.
7. Stage 6 — continuous production ingestion candidate, not currently authorized.

Promotion must not be based solely on a fixed number of successful ingestions.

## Regression methodology

Regression is localized to the smallest confidence cell justified by evidence.

Default regression scope order:

1. row/observation;
2. series/indicator/concept;
3. dataset member/table;
4. dataset/dataflow family;
5. parser/acquisition family;
6. provider/source family;
7. observation representation class;
8. post-boundary substrate;
9. architecture-wide confidence.

Failures widen only when evidence shows a shared cause.

## Consequences

- Future Workstream A planning should include a brief Confidence Escalation Assessment when choosing scope.
- Routine ingestion can become increasingly throughput-oriented inside confidence cells with strong evidence.
- New providers, parser families, representation classes, or canonicalization scopes should start small unless existing evidence proves the same confidence cell applies.
- Architecture remains authoritative. CEF cannot override Mandatory Decision Gates, validation failures, project boundaries, or human approval requirements.
- No code implementation is required now; deterministic support tools may be proposed later only if repeated use proves manual CEF assessment is recurring friction.

## Non-authorization

This decision does not authorize:

- architecture redesign;
- Controlled Expansion;
- provider mirroring;
- ingest-everything behavior;
- generic source/provider frameworks;
- canonical loaders for evidence-only slices;
- Companies/canonical identity work;
- production/live ingestion;
- scheduling/default writes;
- weakening tests, validation, closeout, or architecture review gates;
- git push.
