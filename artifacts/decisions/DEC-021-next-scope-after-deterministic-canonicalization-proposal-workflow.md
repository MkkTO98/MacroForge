# DEC-021 — Next scope after deterministic canonicalization proposal workflow

Status: accepted
Date: 2026-06-13
Related task: TASK-036
Preceded by: TASK-034, DEC-019, DEC-018, DEC-016, DEC-015
Analysis note: `docs/architecture/canonicalization-post-proposal-next-scope-decision-analysis.md`
Follow-on task: TASK-037 — Implement bounded WDI unit metadata enrichment for canonicalization evidence

## Decision

MacroForge will next implement a bounded WDI unit metadata enrichment task for the existing GDP canonicalization evidence.

The selected option is A from the TASK-036 analysis: enrich WDI unit metadata before AI-assisted proposal generation, PostgreSQL persistence, report integration, review-policy calibration, or new sources.

## Why this option

TASK-034 proved the deterministic canonicalization proposal workflow mechanically. The workflow generated 3 provider-evidence-derived proposals and 3 mapping update proposals with all checks passing.

The strongest remaining uncertainty exposed by TASK-034 is not proposal mechanics. It is source evidence quality:

- WDI `NY.GDP.MKTP.CD` remains blocked by `unknown_unit_metadata`;
- OECD and Eurostat have explicit unit profiles and caveats;
- all GDP mappings remain review-required because GDP is high-impact;
- no proposal is auto-applied.

WDI unit enrichment is the best next step because it:

- directly addresses the sharpest blocker in the TASK-034 audit artifact;
- remains small and source-specific;
- validates whether better provider evidence improves deterministic canonicalization output;
- avoids confounding AI/model quality with missing metadata;
- keeps PostgreSQL persistence and report integration deferred until state semantics are better proven.

## Accepted follow-on scope

TASK-037 should implement only bounded WDI unit metadata enrichment for canonicalization evidence.

The follow-on task may:

- create a fresh implementation dry-run;
- add fixture-backed tests for WDI indicator/unit metadata extraction or representation;
- use recorded or fixture-backed WDI metadata for `NY.GDP.MKTP.CD`;
- update WDI provider evidence/unit profile generation so WDI no longer appears as generic `unknown` when source evidence is available;
- regenerate or write a bounded canonicalization evidence/proposal audit artifact showing the changed WDI unit caveat;
- preserve TASK-034 separation between proposals and accepted/provisional mapping state;
- update task/state/handoff/summaries and run full tests/coherence.

## Rejected or deferred scope

This decision does not approve:

- AI/model canonicalization calls;
- prompt/provider setup;
- embeddings/vector search;
- live source fetches unless a future task explicitly asks and gets approval;
- live/default `macro` database writes;
- PostgreSQL migrations or canonicalization persistence;
- unit conversion or currency conversion;
- quarterly-to-annual aggregation;
- canonical GDP snapshot report integration;
- new source onboarding;
- generalized WDI/source metadata framework extraction;
- accepted mapping auto-apply or mutation;
- provider-specific columns in curated facts;
- broad ontology/knowledge graph work;
- git push.

## Reconsideration triggers

Reopen this decision if TASK-037 shows that:

- WDI unit metadata cannot be represented without a broader source metadata model;
- WDI metadata remains insufficient even after bounded enrichment;
- deterministic proposal quality remains blocked by non-unit evidence;
- review routing remains equivalent to manual-every-mapping after explicit WDI unit evidence exists;
- AI/model assistance becomes the next central uncertainty once source evidence is no longer the blocker.

## Evidence reviewed

- `artifacts/tasks/TASK-036-decide-next-scope-after-deterministic-canonicalization-proposal-workflow.md`
- `simulation/dry_runs/20260613_190712-dry-run.md`
- `artifacts/tasks/TASK-034-implement-tiny-deterministic-canonicalization-proposal-workflow.md`
- `artifacts/reports/canonicalization-proposal-workflow-20260613.json`
- `src/macroforge/canonicalization_state.py`
- `tests/test_canonicalization_proposal_workflow.py`
- `artifacts/decisions/DEC-019-next-scope-deterministic-canonicalization-proposal-workflow.md`
- `artifacts/decisions/DEC-018-minimal-ai-assisted-canonicalization-layer.md`
- `docs/architecture/minimal-ai-assisted-canonicalization-layer.md`
- `docs/architecture/canonicalization-next-scope-decision-analysis.md`

## Consequences

MacroForge preserves the staged uncertainty-reduction sequence:

1. prove canonicalization state representation — complete in TASK-032;
2. prove deterministic proposal workflow — complete in TASK-034;
3. enrich the most blocking source evidence — selected for TASK-037;
4. only then reconsider AI-assisted proposal generation, review calibration, PostgreSQL persistence, or report integration.

No implementation was performed under TASK-036.
No git push was performed.
