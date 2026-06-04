# TASK-021 — Design canonical period, territory, and provider mapping schema evolution

Status: open
Created: 2026-06-04
Governing decision: DEC-010
Related design note: `docs/architecture/canonical-domain-schema-evolution.md`

## Objective

Design the concrete schema evolution needed to preserve MacroForge's source-agnostic canonical observation model while supporting quarterly/monthly/daily periods, ISO3 country identity, aggregate territories, and provider code mappings.

This is a design task, not an implementation task.

## Acceptance criteria

- [ ] Start from DEC-010 and the canonical-domain design note.
- [ ] Inspect the current v0 migration, WDI loader, OECD loader, and TASK-020 Eurostat evidence.
- [ ] Propose concrete schema changes for `curated.dim_period` using structured fields and canonical interval identity.
- [ ] Propose concrete schema changes for `curated.dim_territory` preserving ISO3 country semantics and adding `territory_type` / aggregate support.
- [ ] Propose provider mapping metadata for period and territory codes without promoting provider codes to canonical identities.
- [ ] Explain migration/backfill implications for existing WDI/OECD smoke loaders and tests.
- [ ] Explicitly decide whether the change should be implemented as a new migration rather than editing `001_v0_schema_foundation.sql`.
- [ ] No executable migration or loader implementation unless a later task accepts it with a fresh dry-run.

## Boundaries

Do not implement schema changes in this task.

Do not promote Eurostat to PostgreSQL.

Do not replace source-specific loaders with a generalized ingestion framework.

Do not remove source/release/run lineage from facts.

Do not weaken ISO3 semantics for canonical country territories.

Provider representations belong in raw/staging/source payload/metadata/mapping layers, not as canonical curated identities.
