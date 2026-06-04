# OECD/SDMX live no-key smoke hardening report

Date: 2026-06-03
Task: TASK-013

## Result

TASK-013 hardened the TASK-012 source-specific OECD/SDMX evidence slice into a live no-key rerunnable smoke command.

Command:

```bash
PYTHONPATH=src python3 -m macroforge.oecd_sdmx --project-root . --fetch --territory AUS --territory USA --measure B1GQ
```

Exact successful command output:

```text
{
  "normalized": "data/metadata/oecd_sdmx/oecd-sdmx-smoke-normalized.json",
  "raw_artifact": "data/raw/oecd_sdmx/oecd_sdmx_naag_2020_2021_raw.xml",
  "report": "artifacts/reports/oecd-sdmx-smoke-20260603.md"
}
```

A first live attempt failed with HTTP 403 using only the SDMX `Accept` header. TASK-013 added a source-specific `User-Agent` header and test coverage for it. The live no-key command then succeeded.

## Final live artifact evidence

```text
raw file: 1002311
raw sha256: d81d56186d66adddf487a08389d75607af3d9da4fccfd08c690f810337d76a31
row_count: 8
filters: {'measure_codes': ['B1GQ'], 'territory_codes': ['AUS', 'USA']}
content_type: application/vnd.sdmx.genericdata+xml; version=2.1; charset=utf-8
raw_metadata_sha256: d81d56186d66adddf487a08389d75607af3d9da4fccfd08c690f810337d76a31
raw_metadata_bytes: 1002311
units: ['USD_EXC', 'USD_PPP']
```

Rerun/path hygiene check:

```text
raw sha256 after rerun: d81d56186d66adddf487a08389d75607af3d9da4fccfd08c690f810337d76a31
root raw dir: absent
root metadata dir: absent
root reports dir: absent
```

The command overwrites the same project-layout evidence paths and does not create generic root-level output directories.

## Scope boundaries

- No PostgreSQL schema change.
- No live `macro` database write.
- No generalized SDMX framework.
- No paid or credentialed API.
- No git push.

## Remaining schema pressure

Live OECD evidence returns 8 rows for the bounded measure/territory/time filter because `UNIT_MEASURE` includes both `USD_EXC` and `USD_PPP`. This reinforces the TASK-012 schema-pressure note: future PostgreSQL promotion should explicitly decide how units, codelist labels, and richer SDMX attributes participate in canonical grain.
