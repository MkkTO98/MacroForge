# TASK-028 — Implement first canonical GDP snapshot report

Status: complete
Created: 2026-06-04
Completed: 2026-06-04
Depends on: TASK-027
Governing decision: DEC-014

## Objective

Implement MacroForge's first minimal research-facing report from existing canonical data.

The report should be a small deterministic GDP snapshot/audit artifact that proves the canonical substrate can support basic analysis without source-specific leakage.

## Scope allowed

TASK-028 may add:

- a fresh implementation dry-run;
- RED/GREEN tests for report generation;
- a small report module/script, for example `src/macroforge/canonical_gdp_snapshot.py`;
- deterministic report artifact(s) under `artifacts/reports/`, for example JSON plus Markdown;
- small report-specific SQL/query helpers if they remain source-agnostic and mechanical;
- documentation/state/handoff/summaries required for closeout.

## Expected implementation shape

Recommended safe path:

1. Create and validate a fresh TASK-028 implementation dry-run.
2. Write RED tests for report generation before adding the report module.
3. Reuse the TASK-026 isolated combined-source database setup or an equally safe temporary database path.
4. Populate the database only from existing bounded evidence/loaders.
5. Run report queries against canonical tables and `meta` lineage/source metadata.
6. Write deterministic report artifact(s).
7. Verify tests, generated report contents, full test suite, and ProjectForge coherence.

## Required report content

The report must include at minimum:

1. Metadata:
   - report name;
   - generated date or deterministic fixture timestamp;
   - database safety mode / isolated database note;
   - sources included.
2. Coverage:
   - fact row counts by source;
   - country/territory coverage;
   - period/frequency coverage;
   - indicator/unit coverage.
3. Missingness / bounded expected coverage:
   - expected countries and periods from the current bounded fixture universe;
   - missing country/source/period combinations where meaningful;
   - clear note where cross-source comparability is intentionally limited by fixture scope.
4. GDP snapshot:
   - country GDP observations from canonical facts only;
   - group by source, canonical territory, canonical period, indicator, and unit;
   - keep annual and quarterly rows explicit rather than aggregating them.
5. Source lineage:
   - source and dataset release references;
   - lineage event counts or latest lineage artifacts per source.
6. Data quality/audit:
   - duplicate canonical fact grain check;
   - failing quality-check count;
   - report status that succeeds only when required checks pass.

## Query boundary

The report analysis must use only:

- `curated.*` canonical tables;
- `meta.source`;
- `meta.dataset_release`;
- `meta.pipeline_run`;
- `meta.lineage_event`;
- `meta.quality_check`.

Do not query `staging.*` tables for the core report.

If staging tables are queried at all, they must be confined to an explicitly labeled optional audit/debug section and tests must prove the core report does not depend on staging tables.

## Acceptance criteria

- A dry-run for TASK-028 is created and validated before implementation.
- RED tests fail before the report generator exists.
- Tests prove report generation works from an isolated or clearly safe database path.
- Tests prove the core report does not query staging tables.
- Tests prove the report uses canonical tables plus `meta` lineage/source metadata.
- The generated report artifact is deterministic.
- The report includes coverage, missingness, source lineage, duplicate-grain checks, and quality status.
- The report keeps annual and quarterly observations explicit; no implicit frequency aggregation or unit conversion.
- Full test suite passes.
- ProjectForge coherence passes.
- Task/state/handoff/summaries are updated after implementation.

## Explicit non-goals

Do not:

- add a new source;
- live-fetch sources;
- write to live/default `macro`;
- add a migration;
- broadly refactor schema;
- add provider-specific fact columns;
- implement unit conversion;
- implement canonical indicator ontology;
- aggregate quarterly to annual or compare levels as if units/frequencies were harmonized;
- create a mart schema;
- build a dashboard/UI/notebook;
- extract a generalized ingestion framework;
- add orchestration/scheduling;
- push to git.

## Notes

This task should stay small and boring. It is a report/audit artifact to test analytical usability of the canonical layer, not a full research product.

If implementation finds that a meaningful canonical report requires schema changes, source ontology, unit conversion, or staging-table leakage, stop and record the blocker as a follow-on governance task rather than expanding TASK-028.


## Outcome

TASK-028 is complete.

Implementation created:

- `src/macroforge/canonical_gdp_snapshot.py`
- `tests/test_canonical_gdp_snapshot.py`
- `artifacts/reports/canonical-gdp-snapshot-20260604.json`
- `artifacts/reports/canonical-gdp-snapshot-20260604.md`

The report generator creates an isolated temporary PostgreSQL database, applies migrations 001-004, loads existing bounded WDI/OECD/Eurostat evidence through existing source-specific loaders, queries only `curated.*` and `meta.*` tables for the core report, writes deterministic JSON and Markdown report artifacts, and drops the isolated database.

Report result:

- status: succeeded
- canonical fact rows in coverage: 20
- GDP snapshot observations: 16
- sources: `EUROSTAT_NAMQ_GDP`, `OECD_NAAG`, `WDI`
- territories: `AUS`, `DEU`, `DNK`, `FRA`, `USA`
- frequencies: annual and quarterly
- bounded expected GDP observations: 16
- missing GDP observations: 0
- duplicate fact grains: 0
- failing quality checks: 0
- core query boundary: `curated_and_meta_only`

The report keeps annual and quarterly rows explicit, performs no unit conversion, performs no frequency aggregation, and does not query staging tables for core report content. Staging artifact names appear only as lineage metadata values recorded in `meta.lineage_event`.

Verification passed:

```text
PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests/test_canonical_gdp_snapshot.py -q

......                                                                   [100%]
6 passed in 0.91s
```

```text
PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests -q

..................................................                       [100%]
50 passed in 5.20s
```

```text
PYTHONPATH=src python3 -m macroforge.canonical_gdp_snapshot --project-root . --json-report artifacts/reports/canonical-gdp-snapshot-20260604.json --markdown-report artifacts/reports/canonical-gdp-snapshot-20260604.md

status: succeeded
fact_rows_total: 20
missing_observations: 0
duplicate_fact_grains: 0
```
