# D-20260709 — Architecture Maturity Freeze Policy

Status: accepted
Date: 2026-07-09
Related task: `artifacts/tasks/TASK-188-architecture-maturity-declaration-and-freeze-assessment.md`

## Decision

MacroForge accepts the TASK-188 maturity declaration: core scalar repository architecture and planning governance are architecturally mature for their stated scopes and should move into evidence-based maintenance.

## Frozen mature capabilities

- Source-specific acquisition and normalization boundary.
- ObservedIngestionPackage v1 scalar boundary.
- Deterministic post-boundary substrate for scalar observed packages.
- Source-neutral run/release/lineage/quality metadata recording.
- DRDF / ACPF / CEF planning governance.
- WDI implemented-compatible annual-scalar operational cell.
- Bounded revision-aware scalar convention.
- Capability closure / stopping discipline.

## Policy

The burden of proof reverses for these capabilities: they are stable unless future implementation demonstrates otherwise.

Future architecture work requires concrete evidence from new repository classes, operational implementation limitations, repeated implementation friction, canonical ambiguity, scale/performance failure, or repeated downstream query pain.

## Non-authorizations

This decision does not authorize ingestion, implementation, schema migration, provider onboarding, runtime orchestration, generic framework extraction, production scheduling, or broad source support.
