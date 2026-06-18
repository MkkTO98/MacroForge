# TASK-032 — Implement minimal canonicalization state foundation

Status: complete
Created: 2026-06-05
Completed: 2026-06-05
Depends on: TASK-030
Governing decisions: DEC-018, DEC-016, DEC-015
Design note: `docs/architecture/minimal-ai-assisted-canonicalization-layer.md`
Implementation: `src/macroforge/canonicalization_state.py`
Tests: `tests/test_canonicalization_state.py`
Audit artifact: `artifacts/reports/canonicalization-state-foundation-20260605.json`

## Objective

Implement the smallest fixture-backed state foundation needed to prove MacroForge can represent provider indicator evidence, canonicalization runs, mapping proposals, canonical creation proposals, unit/comparability profiles, accepted/provisional mapping state, and supersession lineage for the existing bounded WDI/OECD/Eurostat GDP evidence.

This task should prove the design mechanics. It should not implement AI/model calls or a broad ontology.

## Scope allowed

TASK-032 may create:

- a fresh implementation dry-run;
- a minimal migration or file-backed state artifact for canonicalization state, as justified by the dry-run;
- fixture-backed tests for the accepted state model;
- deterministic seed/audit artifacts for the bounded GDP examples;
- small source-agnostic helper code only if needed to write/read the state or report;
- state/backlog/handoff/summary updates required for closeout.

## Required implementation properties

- Preserve provider indicator evidence separately from canonical concepts.
- Preserve generated mapping proposals separately from accepted/provisional mapping state.
- Store canonicalization run provenance: method/ruleset/model/prompt version, thresholds, input evidence versions/checksums, and timestamp.
- Store confidence score/band and reasoning/evidence references for proposals.
- Store unit/comparability profiles with currency, scale, price basis, PPP/exchange-rate basis, provider unit code, metadata quality, and no-conversion caveats where available.
- Represent annual and quarterly observations explicitly without aggregation.
- Store supersession/versioning fields from the first implementation.
- Produce deterministic audit output for the seed evidence:
  - OECD `B1GQ` with `USD_EXC`/`USD_PPP` annual rows;
  - Eurostat `B1GQ` with `CP_MEUR` quarterly rows;
  - WDI `NY.GDP.MKTP.CD` with current `unknown` unit rows.

## Acceptance criteria

- Fresh dry-run is created and validated before edits.
- Tests cover proposal state vs accepted mapping state separation.
- Tests cover unknown/conflicting unit metadata blocking direct comparability.
- Tests cover annual/quarterly non-aggregation.
- Tests cover confidence/review routing, including high-impact review routing for GDP-like concepts.
- Tests cover supersession lineage.
- A deterministic audit artifact is generated from existing bounded fixture/report evidence.
- Full tests pass.
- `python3 tools/check_coherence.py --project . --json` reports no blocks or warnings.
- Task/backlog/state/architecture/roadmap/handoff/summaries are updated after implementation.

## Explicit non-goals

Do not:

- call an LLM/model for canonicalization;
- onboard a new source;
- live-fetch sources;
- write to live/default `macro`;
- implement unit conversion;
- aggregate quarterly to annual;
- create a mart schema;
- create a dashboard/UI/notebook;
- extract a generalized ingestion/source framework;
- add provider-specific fact columns;
- broaden beyond the existing bounded WDI/OECD/Eurostat GDP evidence;
- push to git.

## Notes

Use deterministic fixture-backed behavior first. Auto-accept candidates may be represented as states, but broad automatic acceptance should remain deferred until calibration evidence and policy exist.
