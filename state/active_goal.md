# Active Goal

Project: MacroForge

## Purpose

If development resumed tomorrow, this file identifies the active implementation phase and safest next action.

## Active implementation phase

Capability: Evidence-Accumulating Source Expansion

Current maturity: Specified through TASK-054 bounded U.S. Treasury Fiscal Data evidence slice.

Objective: make the next ten heterogeneous trustworthy source implementations progressively cheaper while preserving determinism, auditability, provenance, reproducibility, and canonical consistency.

Default assumption: the current source-specific pre-boundary -> `ObservedIngestionPackage` -> deterministic post-boundary substrate architecture is correct. Future implementation should attempt to falsify this assumption, not proactively replace it. Architecture evolves only when repeated implementation evidence demonstrates insufficiency.

## Current result

TASK-054 implemented a bounded U.S. Treasury Fiscal Data average-interest-rates evidence slice through `ObservedIngestionPackage` without substrate redesign, observed-boundary redesign, broad Treasury support, generalized acquisition, pagination framework extraction, canonical loading, or live writes.

The Treasury implementation confirmed that row-oriented public government JSON API evidence can preserve query provenance, endpoint metadata, pagination metadata, fiscal record dates, and categorical row identity before the observed boundary. Post-boundary deterministic substrate effort remained Very Low.

One durable implementation lesson: prefer the bounded source slice that exercises the most new pre-boundary provider shape while staying inside the existing observed contract.

## Next action

TASK-055 is implemented and verified in the current uncommitted worktree, but no further TASK-055 implementation should begin from methodology-only work. The implementation methodology is frozen and treated as stable infrastructure until repeated implementation evidence meets the same standard as architectural extraction. Every heterogeneous implementation must evaluate its prediction ledger, record material prediction mismatches in `docs/architecture/architectural-surprise-log.md`, calibrate tracked assumptions and Prediction Quality in `docs/architecture/architectural-confidence-ledger.md`, update `docs/architecture/marginal-source-cost-index.md`, and update `docs/architecture/recurring-implementation-pain.md`. After every five heterogeneous source implementations, perform exactly one bounded Retrospective Review decision gate: continue source implementation without architectural change, or recommend exactly one evidence-justified extraction. The safest next action is to return to implementation-driven development, not further methodology refinement.
