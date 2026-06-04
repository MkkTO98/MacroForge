# DEC-010 — Prefer canonical-domain schema evolution over provider-centric identities

Status: accepted
Date: 2026-06-04
Related evidence: TASK-020, DEC-009
Related design note: `docs/architecture/canonical-domain-schema-evolution.md`

## Decision

MacroForge will evolve its curated schema from a canonical-domain perspective rather than allowing provider representations to become canonical identities.

The Eurostat spike revealed valid limits in the current annual-only period model and ISO3-shaped territory implementation, but the response is not to make provider period strings or provider geography codes canonical.

Accepted direction:

- Periods should support annual, quarterly, monthly, and eventually daily frequencies through structured canonical fields.
- Provider period codes should remain source metadata/mappings.
- ISO3 should remain the canonical country identifier for country territories.
- Aggregate regions such as `EU27_2020` and `EA20` should be represented through explicit territory typing and provider mappings, not by weakening ISO3 country semantics.
- Curated observations should remain source-agnostic analytical facts with source/release/run lineage.
- Provider representations belong in raw artifacts, staging rows, source payloads, provider code dictionaries, and mapping tables.

## Rationale

MacroForge's long-term goal is to integrate many heterogeneous macroeconomic sources for investment research. That goal needs stable domain identities for time, territory, units, indicators, and facts.

Provider-centric identity is attractive because it speeds up ingestion, but it pushes source-specific semantics into the curated layer. Over many sources, that creates semantic debt: one country or period can appear under many provider-shaped identifiers, and downstream research becomes provider-aware.

Canonical-domain identity keeps ingestion source-specific while making the curated layer useful for cross-source investment research.

## Consequences

The TASK-020 schema recommendations are refined as follows:

- Replace the earlier provider-shaped `period_code` canonical recommendation with structured period fields and canonical interval identity.
- Preserve provider period strings in metadata/mapping.
- Preserve ISO3 as the canonical country identifier.
- Add territory typing for countries, regions, economic areas, and aggregates.
- Add provider territory mappings instead of replacing ISO3 semantics with provider geography codes.
- Add provider code-list/code metadata only where needed to support mapping, audit, and source fidelity.

## Non-goals

This decision does not approve:

- executable schema migration;
- Eurostat PostgreSQL promotion;
- a generalized ingestion framework;
- broad source onboarding;
- research/mart implementation;
- replacing source-specific staging loaders.

A follow-on task must design and validate the concrete migration plan before implementation.
