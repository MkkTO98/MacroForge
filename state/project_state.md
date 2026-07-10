# Project State

Project: MacroForge
Template: python_data_project
Canonical path: `/home/mkkto/srv/EIP/projects/MacroForge`
Last updated: 2026-07-10

MacroForge is in Operational Repository Evolution mode under Strategic Constitution v1.1. Architecture is frozen/evidence-maintained: source-specific pre-boundary work, `ObservedIngestionPackage` v1, deterministic post-boundary substrate, scoped canonical SQL, and evidence-gated extraction.

## Current phase

Phase 2 diverse-source macroeconomic enrichment is active.

Accepted transition:

- Bulk WDI annual-scalar Phase 1 is no longer the default.
- WDI may still be used later for a specific coherent target with clear material gain, but no residual WDI campaign should be scheduled automatically.
- Trade, company, and financial-asset construction remain deferred.

## Repository state after TASK-207

PostgreSQL `macroforge` currently records:

- curated facts: 10,555,773;
- indicators: 1,423;
- sources: 2;
- pipeline runs: 39;
- lineage events: 78;
- quality checks: 79.

TASK-207 added the first Phase 2 diverse-source campaign:

- source: BLS public API v2;
- domain: U.S. monthly labor market;
- repository class: monthly scalar time-series observations;
- run key: `task-207-bls-us-labor-monthly-phase2`;
- run-scoped facts: 2,374;
- series: 12;
- monthly periods: 198;
- coverage: 2010-M01 through 2026-M06;
- duplicate canonical key groups: 0;
- failed quality checks: 0;
- idempotence: same-scope rerun produced zero net growth.

## Architecture posture

Architecture remains frozen / evidence-maintained. TASK-207 did not reveal canonical ambiguity, repository-class mismatch, provider-semantic preservation failure, scaling failure, or repeated operational friction requiring redesign.

The existing substrate supports monthly scalar observations when source-specific semantics are preserved in provider payloads and attribute sets.

## Active continuity note

A failed FRED live-acquisition detour from the same session produced untracked TASK-207 FRED files. Cleanup was blocked by command policy; those files are not the accepted TASK-207 result. Preserve or remove them only with explicit user-approved cleanup scope.
