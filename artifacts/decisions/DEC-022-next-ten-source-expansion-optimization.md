# DEC-022 — Next-Ten-Source Expansion Optimization

Status: accepted
Date: 2026-06-28
Related task: TASK-053
Related report: `artifacts/reports/R-20260627-bounded-bea-nipa-evidence-slice.md`
Related lessons: `artifacts/reports/L-20260628-task-053-implementation-lessons.md`

## Decision

MacroForge will now optimize implementation planning for making the next ten heterogeneous trustworthy economic source implementations progressively cheaper.

The default architectural assumption is:

```text
Source-specific acquisition and normalization
-> ObservedIngestionPackage
-> existing deterministic post-boundary substrate
```

is correct unless repeated implementation evidence falsifies it.

Future implementation should attempt to falsify this assumption through bounded heterogeneous source work rather than replace it through proactive substrate redesign.

## Rationale

TASK-053 confirms another important architectural hypothesis: a fifth materially different source required no meaningful post-boundary architectural evolution.

Current source evidence includes:

- WDI;
- OECD_NAAG;
- EUROSTAT_NAMQ_GDP;
- bounded BLS_CPI monthly evidence;
- bounded BEA_NIPA table/line evidence.

Across these implementations, effort has concentrated before the observed boundary in acquisition, provider interpretation, source-specific normalization, and source-specific mapping decisions. The deterministic post-boundary substrate has continued to survive heterogeneous implementations without meaningful redesign.

MacroForge is no longer primarily proving that the Deterministic Ingestion Substrate can work. It is now proving that the substrate continues to work across an increasingly diverse collection of trustworthy economic data sources.

## New implementation planning rule

Every proposed implementation task must first answer:

```text
Will this permanently reduce the engineering, human, or LLM effort required to implement future trustworthy economic datasets?
```

If the answer is no, the task is unlikely to be highest leverage.

Implementation remains the source of architectural truth.

## Architectural stability rule

Assume the current post-boundary architecture is correct.

Only evolve it if repeated implementation evidence demonstrates insufficiency.

Do not proactively redesign:

- the Deterministic Ingestion Substrate;
- the observed boundary;
- source frameworks;
- provider metadata frameworks;
- runtime orchestration;
- recovery automation;
- graph/catalog systems.

Do not extract reusable infrastructure because it appears elegant.

Extract only when multiple independent implementations demonstrate:

1. contract convergence;
2. algorithm convergence;
3. implementation convergence;
4. deterministic verification;
5. acceptable coupling;
6. measurable reduction in future implementation effort.

## Lightweight Implementation Lessons artifact

After every heterogeneous source implementation, add one short artifact titled `Implementation Lessons`.

Record only:

1. which predictions were confirmed;
2. which predictions were incorrect;
3. unexpected implementation difficulties;
4. new reusable implementation patterns observed;
5. which future implementation predictions should now change.

This is not another architectural report. It is accumulated implementation evidence intended to improve future engineering judgment for humans and local models.

## Future technical debt

Do not implement this now.

If three consecutive heterogeneous source implementations complete without requiring meaningful post-boundary architectural evolution, perform one bounded `Deterministic Ingestion Substrate Stability Review`.

The review should answer only:

- Has the substrate remained stable across repeated heterogeneous implementations?
- Has any post-boundary capability required meaningful redesign?
- Has repeated implementation evidence justified additional substrate work?

If the answer is no, future effort should continue prioritizing new source implementation rather than substrate refinement.

## Consequences

- Architecture should increasingly become an outcome of successful implementations rather than a prerequisite for them.
- TASK-054 selection should optimize for architectural learning per unit of implementation effort.
- Dataset popularity and indicator count are secondary to architectural diversity and bounded implementation value.
- Substrate evolution remains reactive and evidence-gated.
