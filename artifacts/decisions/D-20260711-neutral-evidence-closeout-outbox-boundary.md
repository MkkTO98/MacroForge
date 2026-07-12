# Decision — Neutral Evidence Closeout Outbox Boundary

Date: 2026-07-11
Status: accepted

## Decision

A. Closeout-triggered neutral export publication validated.

## Boundary

MacroForge publishes immutable producer-owned neutral evidence releases to a MacroForge-owned outbox after successful canonical release closeout. Consumers copy/poll and validate independently.

## Selected trigger

Successful canonical release closeout: durable PostgreSQL canonical facts, succeeded pipeline run, dataset release identity, zero failed quality checks, and complete subscription selection.

## Non-decisions

No KnowledgeForge integration, no consumer runtime dependency, no scheduling, no webhook/event bus, no canonical ingestion rollback coupling, no contract revision, and no metadata enrichment beyond retained v1 evidence.
