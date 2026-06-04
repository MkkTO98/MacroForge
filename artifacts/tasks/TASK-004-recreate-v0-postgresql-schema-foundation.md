# TASK-004 — Recreate v0 PostgreSQL schema foundation

Status: completed on 2026-06-02

## Acceptance

Raw SQL migration and schema checks pass against an isolated local PostgreSQL database.

## Delivered files

- `tests/test_schema_foundation.py`
- `db/migrations/001_v0_schema_foundation.sql`
- `db/schema/v0_schema_foundation.md`
- `db/queries/schema_health_check.sql`
- `docs/data/v0-data-model.md`

## TDD evidence

RED was confirmed first with missing migration/query/doc failures:

```text
4 failed in 0.21s
```

GREEN targeted schema tests passed:

```text
4 passed in 0.27s
```

## Notes

- Uses raw SQL, not Alembic, for v0 simplicity.
- Creates `meta`, `staging`, and `curated`; `mart` remains deferred.
- Uses `macro` as the default database name in docs unless live verification proves otherwise.
- WDI remains the first v1 source.
