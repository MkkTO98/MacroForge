# TASK-026 — Implement combined-source canonical validation smoke

Status: complete
Created: 2026-06-04
Completed: 2026-06-04
Depends on: TASK-025
Governing decision: DEC-013

## Objective

Implement a bounded combined-source canonical validation smoke that proves WDI, OECD/SDMX, and Eurostat can coexist in one isolated PostgreSQL database using the existing source-specific loaders and current migrations.

The smoke should apply all existing migrations, load the existing bounded recorded evidence for each source, run canonical substrate checks, and write one combined data-health report artifact.

## Scope allowed

TASK-026 may add:

- a fresh implementation dry-run;
- RED/GREEN tests;
- a small source-agnostic combined smoke module or script;
- a combined source report artifact under `artifacts/reports/`;
- mechanical SQL/query helpers only if needed;
- documentation/state updates required for closeout.

Expected implementation shape:

1. Create a temporary isolated PostgreSQL database.
2. Apply migrations in order:
   - `001_v0_schema_foundation.sql`
   - `002_oecd_sdmx_staging.sql`
   - `003_canonical_domain_dimensions.sql`
   - `004_eurostat_namq_staging.sql`
3. Run existing bounded loaders/evidence for:
   - WDI recorded smoke evidence;
   - OECD/SDMX recorded normalized evidence;
   - Eurostat recorded normalized evidence.
4. Verify combined canonical substrate checks, including:
   - source count and dataset release count;
   - staging rows by source-specific staging table;
   - fact rows by source/dataset;
   - no duplicate source/dataset/indicator/territory/period/unit/attribute fact grain;
   - expected canonical frequencies include annual and quarterly;
   - expected canonical territories include WDI/OECD/Eurostat countries;
   - provider period mappings exist for all participating sources where applicable;
   - provider territory mappings exist for all participating sources where applicable;
   - quality checks and lineage events exist for each participating source.
5. Write a JSON report with explicit counts and `status: succeeded` only if all checks pass.

## Acceptance criteria

- A dry-run for TASK-026 is created and validated before implementation.
- RED tests fail before the combined smoke exists.
- Tests prove the smoke uses isolated temporary PostgreSQL only.
- Tests prove source-specific loaders remain source-specific; no generic source/plugin framework is introduced.
- The combined smoke report records WDI, OECD/SDMX, and Eurostat counts in one database.
- Full test suite passes.
- ProjectForge coherence passes.
- Task/state/handoff/summaries are updated after implementation.

## Explicit non-goals

Do not:

- add a new source;
- add a new migration;
- modify source-specific staging schemas unless a new decision approves it;
- write to live/default `macro`;
- live-fetch World Bank, OECD, or Eurostat;
- broaden Eurostat beyond the recorded `namq_10_gdp` fixture;
- onboard FRED;
- create a generalized source/plugin/JSON-stat/SDMX framework;
- add provider-specific fact columns;
- implement aggregate membership history;
- implement unit conversion or indicator ontology;
- implement mart/research outputs;
- add orchestration/scheduling;
- push to git.

## Notes

This task is intentionally a reliability substrate step between third-source implementation and any research/mart work. It should reveal whether current source-specific loaders compose cleanly in a shared canonical database before MacroForge adds either more source breadth or analytical outputs.


## Outcome

TASK-026 is complete.

Implementation created `src/macroforge/combined_source_smoke.py` and `tests/test_combined_source_smoke.py`, plus the combined report `artifacts/reports/combined-source-canonical-smoke-20260604.json`.

The smoke creates an isolated temporary PostgreSQL database, applies migrations 001-004, runs existing bounded WDI, OECD/SDMX, and Eurostat loaders against recorded evidence, runs combined canonical substrate checks, writes a JSON report, and drops the isolated database.

The implementation also made source-loader quality checks source-scoped where combined database execution exposed global-count coupling:

- WDI fact row quality check now counts WDI facts only.
- OECD fact row and attribute-set quality checks now count OECD facts only.
- Eurostat fact row and provider-mapping quality checks now count Eurostat rows/mappings only.

Combined report result:

- sources: 3 (`EUROSTAT_NAMQ_GDP`, `OECD_NAAG`, `WDI`)
- dataset releases: 3
- staging rows: Eurostat 4, OECD 8, WDI 8
- curated fact rows: 20 total
- fact rows by source: Eurostat 4, OECD 8, WDI 8
- duplicate fact grains: 0
- failing quality checks: 0
- canonical frequencies: annual and quarterly
- canonical territories include `AUS`, `DEU`, `DNK`, `FRA`, `USA`

Verification passed:

```text
PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests/test_combined_source_smoke.py -q

......                                                                   [100%]
6 passed in 1.06s
```

```text
PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests -q

............................................                             [100%]
44 passed in 4.60s
```

```text
PYTHONPATH=src python3 -m macroforge.combined_source_smoke --project-root . --report artifacts/reports/combined-source-canonical-smoke-20260604.json

status: succeeded
fact_rows_total: 20
failing_quality_checks: 0
```
