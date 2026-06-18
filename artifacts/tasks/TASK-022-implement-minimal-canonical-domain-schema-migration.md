# TASK-022 — Implement minimal canonical-domain schema migration

Status: complete
Created: 2026-06-04
Completed: 2026-06-04
Governing decision: DEC-011
Design note: `docs/architecture/minimal-canonical-domain-schema-design.md`

## Objective

Implement the minimal canonical-domain schema evolution accepted in DEC-011 as a new tested migration and compatibility update.

This task should preserve MacroForge's source-agnostic curated observation model while adding structured periods, territory typing, and provider mapping metadata.

## Scope

Allowed:

- Create a new migration, likely `db/migrations/003_canonical_domain_dimensions.sql`.
- Update schema docs and health checks as needed.
- Add/update schema tests for structured periods, territory typing, provider period/territory mappings, and provider code dictionaries.
- Update WDI/OECD loaders only as needed for compatibility with the new canonical dimensions.
- Use isolated PostgreSQL test databases only.

Not allowed:

- Do not edit `001_v0_schema_foundation.sql` as the primary change path.
- Do not promote Eurostat to PostgreSQL.
- Do not add a FRED loader.
- Do not build a generalized ingestion/source framework.
- Do not widen `curated.fact_observation` with provider-specific columns.
- Do not add aggregate membership history.
- Do not add unit conversion or indicator ontology.
- Do not write to a live `macro` database.

## Acceptance criteria

- [x] Start with a fresh implementation dry-run.
- [x] Use TDD for schema constraints and loader compatibility.
- [x] New migration adds the accepted minimal canonical-domain schema changes.
- [x] Annual WDI smoke remains idempotent in isolated PostgreSQL.
- [x] Annual OECD smoke remains idempotent in isolated PostgreSQL.
- [x] Tests cover annual, quarterly, monthly, and daily-ready period rows.
- [x] Tests cover country ISO3 preservation and optional aggregate/economic-area rows.
- [x] Tests cover provider period and territory mappings.
- [x] Tests cover provider code-list/code uniqueness.
- [x] Tests prove `curated.fact_observation` is not widened with provider-specific columns.
- [x] Final verification runs full tests and ProjectForge coherence.

## Implementation notes

Use `docs/architecture/minimal-canonical-domain-schema-design.md` as the schema contract.

Prefer explicit raw SQL and psql/Python testing, consistent with DEC-005, DEC-007, and current project architecture.

## Outcome

Implemented `db/migrations/003_canonical_domain_dimensions.sql` as a bounded raw SQL migration. It adds structured canonical period fields/constraints, canonical territory typing/code constraints, and explicit provider period/territory/code dictionary metadata tables without widening `curated.fact_observation`.

Compatibility updates:

- WDI loader now writes structured annual periods, canonical ISO3 country territories, and provider period/territory mappings.
- OECD/SDMX loader now writes structured annual periods, canonical ISO3 country territories, and provider period/territory mappings.
- Schema health check and schema/data docs include the TASK-022 canonical-domain additions.

Verification:

```text
PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests -q

35 passed in 2.51s
```

Next task: `artifacts/tasks/TASK-023-design-bounded-eurostat-postgresql-promotion.md`.
