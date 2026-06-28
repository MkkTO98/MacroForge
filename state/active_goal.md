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

No approved implementation task is currently open. Recommended next planning step: review TASK-054 Implementation Lessons before selecting TASK-055, with the success criterion that TASK-055 should become cheaper or more predictable because of TASK-054.
