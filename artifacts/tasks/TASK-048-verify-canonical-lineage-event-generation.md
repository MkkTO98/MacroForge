# TASK-048 — Verify canonical lineage event generation extraction

Status: complete
Date: 2026-06-27

## Objective

Implement the first maturity transition for the selected foundational capability without advancing beyond Verified.

Previous selected capability name: `Deterministic Lineage Event Emission`.

Refined capability name: `Canonical Lineage Event Generation`.

Target transition:

```text
Canonical Lineage Event Generation: Specified -> Verified
```

## Capability name refinement

`Canonical Lineage Event Generation` is preferred over `Deterministic Lineage Event Emission` because this task extracted the durable semantic algorithm, not persistence/emission. It is also preferred over broader `Canonical Lineage Generation` because the current evidence supports exactly canonical lineage events, not a graph/catalog/runtime lineage system.

## Scope completed

- Added `src/macroforge/lineage_generation.py`.
- Added `tests/test_lineage_generation.py` with TDD RED/GREEN evidence.
- Extracted only the shared two-event lineage generation algorithm:
  - `raw_to_staging`
  - `staging_to_curated`
- Refactored WDI/OECD/Eurostat loader lineage VALUES construction to consume the shared generated event specs.
- Kept persistence as loader-owned thin consumer SQL.
- Ran targeted loader tests, cross-source deterministic verification tests, and the full test suite.
- Recorded extraction evidence and repeatable evaluation template in `artifacts/reports/R-20260627-canonical-lineage-generation-verification.md`.

## Explicit non-goals preserved

No storage extraction, persistence extraction, orchestration extraction, schema migration, source expansion, live/default `macro` write, provider metadata extraction, quality-check extraction, canonical dimension extraction, fact-upsert extraction, validation-helper expansion, graph/catalog/runtime system, source registry, plugin system, model call, or git push was performed.

## Verification

```text
uvx --from pytest --with pyyaml pytest tests/test_lineage_generation.py -q
3 passed in 0.01s

uvx --from pytest --with pyyaml pytest tests/test_lineage_generation.py tests/test_wdi_loader.py tests/test_oecd_sdmx_loader.py tests/test_eurostat_namq_loader.py -q
9 passed in 1.73s

uvx --from pytest --with pyyaml pytest tests/test_lineage_generation.py tests/test_wdi_loader.py tests/test_oecd_sdmx_loader.py tests/test_eurostat_namq_loader.py tests/test_combined_source_smoke.py tests/test_deterministic_change_verification.py -q
16 passed in 3.23s

uvx --from pytest --with pyyaml pytest tests -q
97 passed in 5.80s

git diff --check
<no output; exit 0>

python3 tools/check_coherence.py --project .
WARN: context health: state/project_state.md is approaching context-health limit (9265/12000 chars)
WARN: context health: state/architecture.md is approaching context-health limit (10677/12000 chars)
coherence: 0 block(s), 2 warning(s)

python3 tools/context_health.py --project .
WARN: state/project_state.md is approaching context-health limit (9265/12000 chars)
WARN: state/architecture.md is approaching context-health limit (10677/12000 chars)
context health: 0 block(s), 2 warning(s)
```

No deterministic report JSON files remain modified after restoring temporary isolated database identifier changes.

The RED test failed first with:

```text
ModuleNotFoundError: No module named 'macroforge.lineage_generation'
```

## Outcome

Capability maturity updated to:

```text
Canonical Lineage Event Generation: Verified
```

Do not claim Adopted, Shared, Stable, or Mature from this task.
