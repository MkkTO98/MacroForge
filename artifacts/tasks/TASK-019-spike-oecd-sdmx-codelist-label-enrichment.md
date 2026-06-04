# TASK-019 — Spike OECD/SDMX codelist and label enrichment

Status: complete
Created: 2026-06-04
Preceded by: TASK-018
Governing decision: DEC-008

## Goal

Add bounded, source-specific OECD/SDMX codelist and label evidence for the existing smoke slice so MacroForge can explain code-heavy OECD observations without introducing a generalized SDMX/source framework or schema change.

## Why now

TASK-017 completed shared mechanical helper hardening. DEC-008 chose codelist/label enrichment before a third-source spike because the current OECD/SDMX path is technically loaded but semantically code-heavy:

- `B1GQ` needs a measure label/description;
- `AUS` and `USA` need reference-area labels if available from the structure metadata;
- `USD_EXC` and `USD_PPP` need unit labels/descriptions;
- observed attributes such as `CONF_STATUS`, `DECIMALS`, and `OBS_STATUS` need source-specific interpretation where available.

This should improve explainability for future research without broadening ingestion architecture.

## Required first step

Begin with a fresh implementation dry-run before changing source/test/report code:

- classify risk as medium if any live no-key fetch command or project artifact generation is planned;
- list exact files to modify/create;
- confirm no schema changes, live `macro` writes, generalized framework work, third-source onboarding, or broad codelist harvesting;
- validate the dry-run with `python3 tools/validate_dry_run.py <path>`.

## Scope

In scope:

- Add recorded fixture evidence and tests for parsing OECD SDMX structure/codelist XML relevant to the current smoke slice.
- Preserve raw structure/codelist evidence with endpoint, byte count, checksum, and source metadata.
- Normalize only bounded label metadata for currently observed smoke-slice codes:
  - `MEASURE` / `B1GQ`;
  - `REF_AREA` / `AUS` and `USA`;
  - `UNIT_MEASURE` / `USD_EXC` and `USD_PPP`;
  - observed attributes `CONF_STATUS`, `DECIMALS`, and `OBS_STATUS` when available.
- Produce project-layout metadata and an inspectable report mapping codes to labels/descriptions.
- Update `docs/data/source-contract.md` with the OECD/SDMX enrichment evidence and limits.
- Use TDD: parser/normalizer tests first, then writer/report tests, then implementation.
- Use recorded fixtures before any live no-key command.

Out of scope:

- Generalized SDMX framework.
- Generalized source framework, plugin registry, source base class, or source discovery.
- Schema changes, migration rewrites, Alembic, ORM, or curated model changes.
- Live `macro` database writes.
- Loading labels into PostgreSQL.
- Broad codelist harvesting beyond the bounded smoke slice.
- Third-source onboarding.
- Research/mart/reporting layer work.
- Paid, credentialed, production, deployment, scheduling, or git-push actions.

## Acceptance criteria

- Fresh implementation dry-run is created and validated.
- Tests are added/updated before implementation.
- Recorded fixture-backed parsing proves label extraction for the bounded smoke-slice concepts.
- Project-layout writer test proves output paths and report shape before real artifact generation.
- Generated metadata/report records endpoint/source, checksum, byte count, relevant labels/descriptions, and limitations.
- Current WDI and OECD/SDMX loader tests remain compatible.
- Full test suite passes.
- Generated-project coherence passes.
- Task/state/handoff/summaries are updated on completion per `context/context_policy.yaml`.

## Verification plan

Run after implementation and governance updates:

```bash
PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests -q
python3 tools/check_coherence.py --project . --json
```

If recording verification output changes state/handoff, run a final coherence-only check:

```bash
python3 tools/check_coherence.py --project . --json
```

## Notes

If codelist parsing starts requiring generic SDMX provider abstractions, source registration, plugin lookup, schema changes, or broad code-list synchronization, stop and open a new design decision instead of expanding TASK-019.

## Outcome

Completed 2026-06-04.

Implemented bounded, source-specific OECD/SDMX codelist and label enrichment using strict TDD:

- Created and validated fresh implementation dry-run `simulation/dry_runs/20260604_075457-implement-task-019-oecd-sdmx-codelist-label-enrichment.md`.
- Added fixture-backed tests first in `tests/test_oecd_sdmx_codelists.py` and verified RED because the codelist enrichment API and CLI options did not exist.
- Added `tests/fixtures/oecd_sdmx_naag_structure_sample.xml` as bounded recorded structure/codelist evidence for the smoke-slice concepts.
- Extended `src/macroforge/oecd_sdmx.py` with source-specific codelist parsing, bounded label report rendering, project-layout metadata/report writing, and CLI support for `--input-structure-xml --write-codelist-labels`.
- Generated project-layout codelist artifacts from the recorded fixture/local XML, not live HTTP:
  - `data/raw/oecd_sdmx/oecd_sdmx_naag_structure_20260604.xml`
  - `data/metadata/oecd_sdmx/oecd-sdmx-codelist-labels-20260604.json`
  - `artifacts/reports/oecd-sdmx-codelist-labels-20260604.md`
- Updated `docs/data/source-contract.md` with the bounded OECD/SDMX enrichment evidence and limits.

No live fetch, schema change, PostgreSQL label load, live `macro` write, generalized SDMX/source framework, broad codelist harvest, third-source onboarding, research/mart work, dependency install, git push, or production action occurred.

## Verification evidence

Dry-run validation:

```text
python3 tools/validate_dry_run.py simulation/dry_runs/20260604_075457-implement-task-019-oecd-sdmx-codelist-label-enrichment.md

valid: simulation/dry_runs/20260604_075457-implement-task-019-oecd-sdmx-codelist-label-enrichment.md
```

RED before implementation:

```text
PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests/test_oecd_sdmx_codelists.py -q

4 failed with missing `parse_codelist_labels`, `render_codelist_markdown_report`, `write_project_codelist_artifacts`, and CLI codelist arguments.
```

Targeted GREEN after implementation:

```text
PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests/test_oecd_sdmx_codelists.py -q

....                                                                     [100%]
4 passed in 0.03s
```

OECD targeted regression check:

```text
PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests/test_oecd_sdmx.py tests/test_oecd_sdmx_codelists.py -q

...........                                                              [100%]
11 passed in 0.03s
```

Project artifact generation from recorded fixture/local XML:

```text
PYTHONPATH=src python3 -m macroforge.oecd_sdmx --input-structure-xml tests/fixtures/oecd_sdmx_naag_structure_sample.xml --project-root . --write-codelist-labels --structure-endpoint 'https://sdmx.oecd.org/public/rest/v1/dataflow/OECD.SDD.NAD/all/latest'

{
  "normalized_labels": "data/metadata/oecd_sdmx/oecd-sdmx-codelist-labels-20260604.json",
  "raw_structure_artifact": "data/raw/oecd_sdmx/oecd_sdmx_naag_structure_20260604.xml",
  "report": "artifacts/reports/oecd-sdmx-codelist-labels-20260604.md"
}
```

Full suite before governance closeout:

```text
PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests -q

.................................                                        [100%]
33 passed in 1.67s
```

Final tests/coherence are recorded in `state/project_state.md` and `context/latest_handoff.md` after governance and summary updates.
