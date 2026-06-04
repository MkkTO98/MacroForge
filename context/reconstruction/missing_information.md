# Missing Information and Deferred Questions

## High impact

- Live PostgreSQL availability and connection details are not yet verified.
- The default database name is `macro`; change it only if live verification proves otherwise.
- Exact v0 schema details must be recreated through tests and decisions, not copied blindly from deleted files.

## Medium impact

- Exact GitHub remote and branch workflow.
- Whether brother/collaborator workflows remain in v1 scope.
- Whether OS-level users/wrappers should be implemented before or after the WDI vertical slice.
- Whether FRED API key access is acceptable for a later second source.

## Low impact

- Exact names of local agent roles/profiles.
- Whether `mart` schema appears in v0 or is documentation-only until later.
- Exact first report format.

## Current defaults

- Recreate schema/WDI cleanly from reconstruction.
- Use WDI first.
- Use `macro` as database name until live verification says otherwise.
