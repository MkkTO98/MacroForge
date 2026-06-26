# TASK-041 — Bounded MacroForge comparability and research-readiness assessment

Status: completed
Date: 2026-06-19
Type: bounded review / maturity assessment

## Objective

Assess the smallest remaining gaps between current MacroForge and a MacroForge capable of supporting trustworthy InsightForge research, focused exclusively on:

- cross-source comparability;
- unit semantics;
- eligibility boundaries;
- conversion-policy absence;
- lineage/research-readiness.

## Scope

Review existing MacroForge artifacts, decisions, manifests, state, architecture, and actual InsightForge findings/pressure-test results.

## Non-goals preserved

This task did not:

- implement code;
- ingest new data;
- modify schema;
- create pipelines;
- create agents;
- create dashboards;
- create report-generation systems;
- create new projects;
- perform broad architecture redesign;
- mutate MacroForge canonical manifests;
- mutate accepted/base mapping state;
- write to PostgreSQL;
- perform conversion, aggregation, or forecasting.

## Deliverable

Primary report:

- `artifacts/reports/R-20260619-comparability-research-readiness-assessment.md`

## Outcome

MacroForge is partially research-ready.

It can support:

- bounded same-source descriptive findings;
- lineage-backed evidence citation;
- caveat-aware boundary findings;
- methodological/comparability pressure testing.

It cannot yet support trustworthy cross-source GDP research because current evidence lacks a deterministic downstream eligibility/comparability contract.

The key finding is that the next bottleneck is not ingestion, storage, dashboards, new sources, or broad architecture. It is deterministic GDP research/report eligibility classification over existing evidence.

## Recommendation

Recommended next implementation task:

- `TASK-042 — Create deterministic GDP research/report eligibility classification artifact`

This should classify existing GDP evidence only:

- WDI `NY.GDP.MKTP.CD`: governed provisional candidate, not accepted truth.
- OECD `USD_EXC`: deferred exchange-rate candidate requiring future OECD policy/evidence.
- OECD `USD_PPP`: deferred PPP candidate requiring future PPP profile/exclusion policy/evidence.
- Eurostat `CP_MEUR` quarterly evidence: deferred on frequency/currency/scale policy.

It must not approve trusted comparable reporting, convert, aggregate, mutate manifests, persist to PostgreSQL, add sources, or create a generalized reporting framework.
