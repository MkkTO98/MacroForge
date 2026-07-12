# Decision — Neutral Evidence-Release Exporter Boundary

Date: 2026-07-11
Status: accepted

## Decision

MacroForge may expose a bounded consumer-neutral projection of its own canonical observed evidence after successful canonical release/run completion.

Classification: B. Bounded optional export capability compatible with existing architecture, and implemented successfully for the bounded WDI trade-share scope.

## Rationale

Existing MacroForge architecture already owns observed data, source-specific normalization, canonical observations, run/release metadata, lineage, and quality records. It did not expose a public implementation-neutral export artifact. A small projection exporter preserves MacroForge architecture without coupling to KnowledgeForge.

## Boundaries

The exporter must not encode KnowledgeForge derivation logic, InsightForge interpretation, private database schemas, campaign implementation details, or shared runtime packages. Export artifacts must be manually transferable serialized artifacts.

## Trigger policy

Near term: manual export after successful canonical validation.
Future: successful canonical release closeout. Never publish incomplete or failed ingestion runs as valid releases.

## Artifact

`artifacts/exports/neutral-evidence-release/task-210-wdi-trade-share-dnk-swe-nor-1990-2024/macroforge-wdi-trade-share-dnk-swe-nor-1990-2024.neutral-release.json`

Release fingerprint: `sha256:def8c318100cf14526cbdac87335e6b1646681b2176fd684c66ac7cc9d7add67`
