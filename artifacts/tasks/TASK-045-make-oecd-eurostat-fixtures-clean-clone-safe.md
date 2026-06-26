# TASK-045 — Make OECD/Eurostat fixtures clean-clone safe

Status: complete
Date: 2026-06-26

## Objective

Resolve the remaining operational pre-freeze blocker from `artifacts/reports/R-20260619-operational-capability-validation.md`: OECD/Eurostat bounded source fixture artifacts required for reconstruction existed only as ignored `data/` files, so a final commit would not be clean-clone safe.

## Scope

Minimal operational hardening only:

- preserve existing data locations used by current loaders, combined smoke, tests, and snapshot workflows;
- make only the bounded OECD/Eurostat fixture evidence unignored/trackable;
- keep generated `data/` artifacts ignored by default;
- do not add new sources, fetch live data, change loaders, add schemas/migrations, introduce frameworks, mutate canonical state, or write to live/default `macro`.

## Fixture evidence made trackable

OECD/SDMX:

- `data/raw/oecd_sdmx/oecd_sdmx_naag_2020_2021_raw.xml`
- `data/raw/oecd_sdmx/oecd_sdmx_naag_structure_20260604.xml`
- `data/metadata/oecd_sdmx/oecd-sdmx-smoke-normalized.json`
- `data/metadata/oecd_sdmx/oecd-sdmx-codelist-labels-20260604.json`

Eurostat:

- `data/raw/eurostat/eurostat-namq-10-gdp-2023q1-2023q2-raw.json`
- `data/metadata/eurostat/eurostat-namq-10-gdp-architecture-spike-normalized.json`

Folder summaries under those fixture directories are also unignored so the project OS remains navigable after commit.

## Implementation summary

Updated `.gitignore` to keep `data/raw/*` and `data/metadata/*` ignored by default while explicitly unignoring only the bounded OECD/Eurostat fixture directories, their `_SUMMARY.md` files, and the exact fixture files listed above.

Added `tests/test_fixture_persistence.py` to guard that the required OECD/Eurostat clean-clone fixture files exist and are not ignored by git.

Updated data folder summaries and project state/handoff/task records to reflect that the fixture-persistence blocker is resolved.

## Verification

TDD RED before `.gitignore` change:

```text
FAILED tests/test_fixture_persistence.py::test_required_oecd_and_eurostat_fixture_files_exist_and_are_not_gitignored
AssertionError: assert ['data/raw/oecd_sdmx/oecd_sdmx_naag_2020_2021_raw.xml', ...] == []
```

Focused test after fix:

```text
uvx --from pytest --with pyyaml pytest tests/test_fixture_persistence.py -q
1 passed in 0.01s
```

Trackability check:

```text
git ls-files --others --exclude-standard -- data/raw/oecd_sdmx data/metadata/oecd_sdmx data/raw/eurostat data/metadata/eurostat
```

Includes the bounded OECD/Eurostat fixture files and their folder summaries as unignored, commit-eligible files.

Operational combined reconstruction remains the final verification path for this task.

## Outcome

TASK-045 is complete. The bounded OECD/Eurostat fixture evidence required by combined reconstruction is no longer hidden behind default `data/` ignore rules and is ready to be included in the final v1 commit.
