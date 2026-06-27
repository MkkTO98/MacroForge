# TASK-046 — Extract observed common ingestion representation

Status: complete
Date: 2026-06-26

## Objective

Extract the shared ingestion representation identified in `artifacts/reports/R-20260626-observed-common-ingestion-representation-discovery.md` as an equivalence-first implementation.

This task did not attempt to improve, redesign, or generalize ingestion. The purpose was to prove that the representation already present across WDI, OECD, and Eurostat can be captured without changing behavior.

## Scope implemented

- Added `src/macroforge/observed_ingestion.py` with immutable observed package/observation dataclasses.
- Added source-specific adapter functions for the existing WDI, OECD, and Eurostat normalized artifacts.
- Centralized the repeated canonical attribute hash helper.
- Updated WDI/OECD/Eurostat loaders to consume the extracted representation only where it preserves existing semantics.
- Preserved source-specific acquisition, normalized artifacts, staging tables, SQL load flow, provider mapping behavior, lineage behavior, quality checks, and canonical fact semantics.
- Added fixture-backed tests for all supported sources.
- Added architecture documentation for the representation boundary.

## Explicit non-goals preserved

No generalized ingestion framework, plugin architecture, base loader, source registry, database schema change, canonicalization semantic change, validation semantic change, lineage semantic change, provider mapping change, AI/model call, conversion, aggregation, dataset expansion, or dataset deepening was introduced.

## Files created

- `src/macroforge/observed_ingestion.py`
- `tests/test_observed_ingestion.py`
- `docs/architecture/observed-ingestion-representation.md`
- `artifacts/tasks/TASK-046-extract-observed-common-ingestion-representation.md`

## Files modified

- `src/macroforge/wdi_loader.py`
- `src/macroforge/oecd_sdmx_loader.py`
- `src/macroforge/eurostat_namq_loader.py`
- project state/handoff/summary files during closeout

## Equivalence verification

The relevant loader and combined-source tests passed after extraction:

```text
uvx --from pytest --with pyyaml pytest tests/test_wdi_loader.py tests/test_oecd_sdmx_loader.py tests/test_eurostat_namq_loader.py tests/test_combined_source_smoke.py -q
............                                                             [100%]
12 passed in 2.51s
```

These tests exercise the current WDI, OECD, and Eurostat loaders against isolated PostgreSQL databases where available and verify canonical dimensions, fact rows, provider period/territory mappings, lineage event counts, quality check counts, duplicate fact-grain absence, and combined-source smoke outputs.

Final verification is recorded in `context/latest_handoff.md`.

## Outcome

The extraction preserved behavior and made the observed common handoff explicit. The representation is now available as a tested internal contract while preserving source-specific-first architecture boundaries.
