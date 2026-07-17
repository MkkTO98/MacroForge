# TASK-082 — Observed boundary implementation-architecture migration

Status: complete
Completed UTC: 2026-07-01T16:26:03Z

## Purpose

Implement the first constitutional implementation-architecture migration for MacroForge by protecting the Observed layer boundary without redesigning the repository or changing behavior.

## Scope

In scope:

- Split WDI/OECD/Eurostat observed-package construction out of `src/macroforge/observed_ingestion.py`.
- Keep the observed layer responsible for the observed contract, deterministic attribute hashing, package fingerprinting, and package comparison.
- Preserve compatibility wrappers for existing callers that still import the legacy builder names from `macroforge.observed_ingestion`.
- Update canonical loaders and directly affected tests to import source-owned observed-package builders explicitly.

Out of scope:

- Source-module namespace reorganization.
- Provider frameworks.
- Builder registries, plugins, discovery, dependency injection, or runtime abstractions.
- Deterministic Change Verification restructuring.
- Canonical loader restructuring.
- Canonicalization-state restructuring.
- ProjectForge compatibility or governance redesign.

## Implementation summary

Changed implementation files:

- `src/macroforge/observed_ingestion.py`
  - Now contains only the Observed contract/data classes, deterministic attribute hash, package fingerprinting, package comparison, and thin compatibility wrappers.
  - Removed WDI/OECD/Eurostat release-key logic, provider-specific attribute logic, provider-specific status/precision logic, and direct observation construction.

- `src/macroforge/wdi_observed.py`
  - New explicit WDI observed-package construction module.
  - Owns WDI release-key logic and WDI observation packaging.

- `src/macroforge/oecd_sdmx_observed.py`
  - New explicit OECD_NAAG observed-package construction module.
  - Owns OECD release-key logic, observation-status logic, decimal precision logic, and observation packaging.

- `src/macroforge/eurostat_namq_observed.py`
  - New explicit Eurostat NAMQ GDP observed-package construction module.
  - Owns Eurostat release-key logic, Eurostat attribute payload construction, and observation packaging.

- `src/macroforge/wdi_loader.py`
  - Imports WDI observed-package construction from `macroforge.wdi_observed`.

- `src/macroforge/oecd_sdmx_loader.py`
  - Imports OECD observed-package construction from `macroforge.oecd_sdmx_observed`.

- `src/macroforge/eurostat_namq_loader.py`
  - Imports Eurostat observed-package construction from `macroforge.eurostat_namq_observed`.

Changed tests:

- `tests/test_observed_ingestion.py`
  - Imports WDI/OECD/Eurostat builders from their new source-owned modules.
  - Adds a boundary test proving `observed_ingestion.py` no longer owns provider-specific release/status/attribute construction or direct `ObservedObservation(...)` packaging.
  - Adds compatibility coverage proving the legacy observed-ingestion wrapper still produces the same deterministic fingerprint as the source-owned WDI builder.

- `tests/test_contract_drift.py`
  - Imports WDI/OECD/Eurostat builders from source-owned modules.

- `tests/test_ingestion_feedback.py`
  - Imports WDI/Eurostat builders from source-owned modules.

- `tests/test_deterministic_change_verification.py`
  - Imports WDI/OECD/Eurostat builders from source-owned modules.

## Architectural rationale

The migration better reflects the constitutional processing model:

```text
Source-specific acquisition
-> Source-specific normalization
-> ObservedIngestionPackage
-> Deterministic post-boundary substrate
```

Before this migration, `observed_ingestion.py` both defined the Observed contract and knew how WDI, OECD, and Eurostat constructed observed packages. That blurred the source-specific pre-boundary responsibility with the shared observed boundary.

After this migration:

- source-specific observed-package construction lives in source-owned modules;
- the observed layer defines what an observed package is and how packages are deterministically hashed/compared;
- canonical loaders call explicit source-owned builders;
- no generic provider framework, registry, plugin layer, discovery mechanism, or abstraction was introduced.

## Compatibility summary

Existing behavior is preserved by:

- keeping the `ObservedObservation`, `ObservedIngestionPackage`, `ObservedPackageComparison`, `EMPTY_ATTRIBUTE_HASH`, `UNKNOWN_UNIT_CODE`, `canonical_attribute_hash`, `observed_package_fingerprint`, and `compare_observed_packages` APIs in `macroforge.observed_ingestion`;
- preserving legacy compatibility wrappers for:
  - `build_wdi_observed_package`;
  - `build_oecd_observed_package`;
  - `build_eurostat_observed_package`;
- preserving deterministic output as proven by existing semantic tests, loader tests, deterministic change verification, and full regression.

## Verification

RED evidence:

- `uvx pytest tests/test_observed_ingestion.py -q`
  - failed as expected after the test import was moved to the new source-owned builder modules because those modules did not exist yet:
  - `ModuleNotFoundError: No module named 'macroforge.eurostat_namq_observed'`

GREEN evidence:

- `uvx pytest tests/test_observed_ingestion.py -q`
  - `9 passed`

- `uvx pytest tests/test_observed_ingestion.py tests/test_contract_drift.py tests/test_ingestion_feedback.py tests/test_deterministic_change_verification.py tests/test_wdi.py tests/test_oecd_sdmx.py tests/test_wdi_loader.py tests/test_oecd_sdmx_loader.py tests/test_eurostat_namq_loader.py tests/test_combined_source_smoke.py -q`
  - `43 passed`

- `uvx pytest -q`
  - `255 passed`

Note: full pytest regenerated deterministic report JSONs outside this task scope; they were restored afterward per MacroForge convention.

## Remaining boundary observations for future migrations

Do not fix under TASK-082:

- `deterministic_change_verification.py` still contains source-specific WDI/OECD/Eurostat loaded-package reconstruction branches. That is a future deterministic-verification boundary migration, explicitly out of this task scope.
- Canonical loaders still mix loader SQL, lineage insertion, quality-check/report mechanics, and CLI behavior. That is a future canonical-loading/verification migration, explicitly out of this task scope.
- `src/macroforge/` remains a flat source-module namespace. Grouping source modules under `sources/` remains a possible future migration, explicitly out of this task scope.
- `canonicalization_state.py` remains a large accumulated canonical mapping/proposal/audit module. That is explicitly out of this task scope.
