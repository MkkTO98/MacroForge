# TASK-013 — Harden OECD/SDMX live no-key rerunnable smoke command

Status: completed
Created: 2026-06-03
Completed: 2026-06-03
Preceded by: TASK-012
Decision context: DEC-005 and TASK-012 outcome
Dry-run/preflight: `simulation/dry_runs/20260603_132255-task-013-oecd-live-rerunnable-smoke.md`

## Goal

Harden the bounded OECD/SDMX second-source evidence slice into a live no-key rerunnable smoke command that fetches the public OECD endpoint and writes MacroForge project-layout evidence artifacts.

This task is operational hardening only. It must not load PostgreSQL, change schema, introduce a generalized SDMX framework, or use paid/credentialed APIs.

## Scope

In scope:

- Add a tested CLI/main path that can run from the project root and write only:
  - `data/raw/oecd_sdmx/oecd_sdmx_naag_2020_2021_raw.xml`
  - `data/metadata/oecd_sdmx/oecd-sdmx-smoke-normalized.json`
  - `artifacts/reports/oecd-sdmx-smoke-20260603.md`
- Fetch the public no-key OECD SDMX endpoint:
  - `https://sdmx.oecd.org/public/rest/v1/data/OECD.SDD.NAD,DSD_NAAG@DF_NAAG_I/.?startPeriod=2020&endPeriod=2021`
- Keep the bounded filters at `REF_AREA in {AUS, USA}` and `MEASURE in {B1GQ}` unless explicitly overridden.
- Preserve raw bytes, content type, endpoint, byte count, checksum, normalized metadata, and human-readable report.
- Make reruns deterministic/idempotent at the artifact path level: rerunning the command overwrites the same smoke evidence files rather than creating generic root-level `raw/`, `metadata/`, or `reports/` directories.
- Record exact live command output and verification output.

Out of scope:

- PostgreSQL writes or schema changes.
- Loading OECD rows into staging/curated tables.
- Generalized SDMX framework/plugin architecture.
- Codelist label enrichment beyond code preservation.
- Paid, credentialed, or production APIs.
- Git push.

## Acceptance criteria

- Tests prove the CLI/main path supports project-layout artifact writing for a fixture-backed payload.
- Targeted OECD/SDMX tests pass.
- Live command succeeds or, if upstream/network access fails, the blocker is recorded exactly without fabricated artifacts.
- If live command succeeds, generated artifacts exist at the project-layout paths and root-level `raw/`, `metadata/`, and `reports/` are absent.
- Full test suite passes.
- Generated-project coherence passes.
- State, handoff, backlog, roadmap, task summary, and affected folder summaries are updated.

## Verification plan

```bash
PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests/test_oecd_sdmx.py -q
PYTHONPATH=src python3 -m macroforge.oecd_sdmx --project-root . --fetch --territory AUS --territory USA --measure B1GQ
PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests -q
python3 tools/check_coherence.py --project . --json
```

Also check:

```bash
test ! -d raw
test ! -d metadata
test ! -d reports
```

## Outcome

Implemented and verified the live no-key rerunnable smoke command.

Changes:

- Added `--project-root` CLI support so the command writes MacroForge project-layout artifacts instead of generic root-level `raw/`, `metadata/`, and `reports/` directories.
- Added default bounded CLI filters: `REF_AREA in {AUS, USA}` and `MEASURE in {B1GQ}` when the caller does not specify filters.
- Added a source-specific `User-Agent` header required by the OECD endpoint; the first live attempt without it returned `HTTP Error 403: Forbidden`.
- Added tests for project-layout CLI behavior and the fetch header.
- Ran the live no-key command twice to verify rerunnable same-path output behavior.

Live command:

```bash
PYTHONPATH=src python3 -m macroforge.oecd_sdmx --project-root . --fetch --territory AUS --territory USA --measure B1GQ
```

Exact successful output:

```text
{
  "normalized": "data/metadata/oecd_sdmx/oecd-sdmx-smoke-normalized.json",
  "raw_artifact": "data/raw/oecd_sdmx/oecd_sdmx_naag_2020_2021_raw.xml",
  "report": "artifacts/reports/oecd-sdmx-smoke-20260603.md"
}
```

Final live evidence:

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

Rerun/path hygiene:

```text
raw sha256 after rerun: d81d56186d66adddf487a08389d75607af3d9da4fccfd08c690f810337d76a31
root raw dir: absent
root metadata dir: absent
root reports dir: absent
```

TASK-013 report: `artifacts/reports/oecd-sdmx-live-smoke-20260603.md`.

## Verification evidence

Targeted TDD evidence:

```text
PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests/test_oecd_sdmx.py::test_cli_project_root_writes_project_layout_without_generic_root_dirs -q

F                                                                        [100%]
SystemExit: 2
pytest: error: unrecognized arguments: --project-root ...
```

```text
PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests/test_oecd_sdmx.py::test_fetch_payload_sends_user_agent_required_by_oecd -q

F                                                                        [100%]
KeyError: 'User-agent'
```

Targeted GREEN:

```text
PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests/test_oecd_sdmx.py -q

.......                                                                  [100%]
7 passed in 0.03s
```

Final full verification is recorded in `context/latest_handoff.md` and `state/project_state.md`.

## Notes

TASK-013 exists because TASK-012 intentionally stopped at fixture-backed normalization. This task proves operational rerunnability against the no-key live source while still avoiding database/schema/framework expansion.
