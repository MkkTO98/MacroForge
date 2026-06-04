# TASK-012 — Implement OECD/SDMX raw-evidence normalization

Status: completed
Created: 2026-06-03
Completed: 2026-06-03
Decision: DEC-005
Preceded by: TASK-011
Source report: `artifacts/reports/oecd-sdmx-second-source-spike-20260603.md`
Contract: `docs/data/source-contract.md`
Dry-run/preflight: `simulation/dry_runs/20260603_094428-open-task-012.md`

## Goal

Implement a bounded OECD/SDMX smoke evidence slice that proves MacroForge can preserve raw SDMX GenericData XML evidence and normalize a small source-specific subset into the existing minimal source contract shape.

This task intentionally stops before PostgreSQL load, schema changes, orchestration, or a generalized SDMX framework.

## Scope

In scope:

- Use the public no-key OECD SDMX endpoint identified in TASK-011, or a recorded raw XML fixture if live access is unavailable.
- Preserve the raw XML artifact with endpoint metadata, byte count, content type, retrieval timestamp, and SHA-256 checksum.
- Normalize a small bounded subset from `OECD.SDD.NAD,DSD_NAAG@DF_NAAG_I`, preferably two `REF_AREA` values and one `MEASURE` over 2020-2021, so the slice remains comparable to the WDI smoke slice.
- Map SDMX fields to `docs/data/source-contract.md`, including series-key dimensions, observation time period, observation value, unit, and observation attributes.
- Produce a machine-readable normalized metadata/output file and a human-readable report.
- Add tests for XML parsing, checksum/metadata behavior, bounded filtering, and report/contract shape.
- Update runbook/state/handoff artifacts with exact verification output.

Out of scope:

- Loading OECD rows into PostgreSQL.
- Changing `db/migrations/001_v0_schema_foundation.sql` or any database schema.
- Introducing Alembic, SQLAlchemy, Dagster/Airflow, Docker, or a generalized ingestion/source plugin framework.
- Implementing broad SDMX codelist/label enrichment beyond what is necessary to preserve code-only normalized evidence.
- Using paid, credentialed, or production data APIs.
- Writing to a live `macro` database.

## Proposed implementation shape

Suggested files, subject to TDD refinement:

- `src/macroforge/oecd_sdmx.py` — source-specific fetch/parse/normalize helpers.
- `tests/test_oecd_sdmx.py` — XML parsing, filtering, checksum/report tests.
- `data/raw/oecd_sdmx/...` — ignored raw XML artifact if live fetch succeeds or fixture policy permits local evidence.
- `data/metadata/oecd_sdmx/...` — ignored normalized metadata/evidence output.
- `artifacts/reports/oecd-sdmx-smoke-20260603.md` — human-readable evidence report.
- Optional runbook/docs update if the command surface is non-obvious.

## Acceptance criteria

- A source-specific command or function can fetch or read the bounded OECD SDMX GenericData XML evidence without credentials.
- Raw evidence metadata records endpoint, content type, byte count, SHA-256 checksum, retrieval/source timestamp when available, and local artifact path when written.
- Normalized output contains a small bounded set of observations and maps at least:
  - `source_code`
  - `provider_dataset_code`
  - `indicator_code` / SDMX `MEASURE`
  - `territory_code` / SDMX `REF_AREA`
  - `period`
  - `frequency`
  - `value`
  - `unit`
  - observation attributes such as `CONF_STATUS`, `DECIMALS`, and `OBS_STATUS`
  - source payload/dimension evidence sufficient to trace back to the XML.
- Tests cover XML parsing from a fixture, bounded filtering, checksum/metadata generation, and normalized contract shape.
- The report explicitly compares the normalized OECD/SDMX shape to the WDI source contract and records any schema pressure discovered.
- Full test suite passes.
- Generated-project coherence passes.
- No live `macro` database write occurs.
- No PostgreSQL schema change occurs.

## Verification plan

Run after implementation:

```bash
uvx --from pytest --with pyyaml pytest tests -q
python3 tools/check_coherence.py --project . --json
```

If a command-line smoke entry point is added, run it against an isolated/output-only path and record exact output in the task outcome and `context/latest_handoff.md`.

## Outcome

Implemented the bounded OECD/SDMX raw-evidence normalization slice without PostgreSQL load, schema change, live `macro` database write, paid/credentialed API use, or generalized SDMX framework.

Created source-specific parser/normalizer support in `src/macroforge/oecd_sdmx.py` with fixture-backed tests in `tests/test_oecd_sdmx.py` and `tests/fixtures/oecd_sdmx_naag_sample.xml`.

Generated fixture-backed TASK-012 project-layout smoke artifacts:

- `data/raw/oecd_sdmx/oecd_sdmx_naag_2020_2021_raw.xml`
- `data/metadata/oecd_sdmx/oecd-sdmx-smoke-normalized.json`
- `artifacts/reports/oecd-sdmx-smoke-20260603.md`

The normalized fixture-backed slice contains 3 observations for `MEASURE=B1GQ`, territories `AUS` and `USA`, and periods 2020-2021 where present. Raw fixture evidence records 2808 bytes and SHA-256 `0b540b6038363218839814397a7c6028b72a4ed31c5442af04a6edc7baeda47e`.

The accidental generic root-level output directories `raw/`, `metadata/`, and `reports/` were absent when final governance resumed.

## TDD evidence

Initial RED for the new OECD/SDMX module:

```text
ImportError: cannot import name 'oecd_sdmx' from 'macroforge'
```

Project-layout writer RED before implementation:

```text
AttributeError: module 'macroforge.oecd_sdmx' has no attribute 'write_project_smoke_artifacts'
```

Targeted GREEN from the implementation session:

```text
PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests/test_oecd_sdmx.py -q

.....                                                                    [100%]
5 passed in 0.02s
```

Full-suite/coherence evidence from the artifact-generation session:

```text
PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests -q
python3 tools/check_coherence.py --project . --json

....................                                                     [100%]
20 passed in 1.40s
{
  "mode": "generated",
  "blocks": [],
  "warnings": []
}
```

Final verification after governance updates is recorded in `context/latest_handoff.md` and `state/project_state.md`.

## Notes

The purpose of TASK-012 is to learn from the smallest useful second-source evidence slice. If XML parsing, live access, or endpoint filtering creates friction, record that evidence rather than widening scope. A future PostgreSQL-load task or schema decision can be opened only after this normalized shape is accepted.
