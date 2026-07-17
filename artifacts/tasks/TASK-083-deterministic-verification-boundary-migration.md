# TASK-083 — Deterministic verification boundary migration

Status: complete
Completed UTC: 2026-07-01T16:42:47Z

## Purpose

Implement the second constitutional implementation-architecture migration for MacroForge by strengthening the boundary between generic deterministic verification and source-specific canonical reconstruction.

## Scope

In scope:

- Remove WDI/OECD/Eurostat source-specific reconstruction branches from `src/macroforge/deterministic_change_verification.py`.
- Keep deterministic verification responsible for orchestration, contract validation, deterministic package comparison, and verification evidence objects.
- Move loaded observed-package reconstruction into explicit canonical loader modules:
  - `src/macroforge/wdi_loader.py`
  - `src/macroforge/oecd_sdmx_loader.py`
  - `src/macroforge/eurostat_namq_loader.py`
- Update deterministic change verification tests to call loader-owned reconstruction explicitly.

Out of scope:

- Repository redesign.
- `sources/` namespace migration.
- Generic provider abstractions.
- Provider registries, plugins, auto-discovery, dependency injection, or runtime dispatch systems.
- Canonical loader decomposition beyond the narrow reconstruction ownership move.
- ProjectForge compatibility or governance redesign.

## Implementation summary

Changed implementation files:

- `src/macroforge/deterministic_change_verification.py`
  - Removed direct database querying, source-code branching, source-specific SQL, and `ObservedObservation` reconstruction.
  - Now compares an expected observed package with an already reconstructed loaded package.
  - Still validates expected and loaded package contracts and returns deterministic comparison evidence.

- `src/macroforge/wdi_loader.py`
  - Added `reconstruct_loaded_observed_package(db_name, expected_package)` for WDI canonical/staging reconstruction.
  - Owns WDI-specific reconstruction SQL and staging row count.

- `src/macroforge/oecd_sdmx_loader.py`
  - Added `reconstruct_loaded_observed_package(db_name, expected_package)` for OECD_NAAG canonical/staging reconstruction.
  - Owns OECD-specific reconstruction SQL and staging row count.

- `src/macroforge/eurostat_namq_loader.py`
  - Added `reconstruct_loaded_observed_package(db_name, expected_package)` for EUROSTAT_NAMQ_GDP canonical/staging reconstruction.
  - Owns Eurostat-specific reconstruction SQL and staging row count.

Changed tests:

- `tests/test_deterministic_change_verification.py`
  - Added a boundary test proving the deterministic verifier no longer contains WDI/OECD/Eurostat source-specific reconstruction branches or staging-table SQL.
  - Updated the full canonical-load verification test so expected packages are reconstructed by source loaders and then passed into the deterministic verifier.

## Architectural rationale

The constitutional processing model distinguishes the deterministic substrate from source-specific canonical reconstruction:

```text
Observed contract
-> Deterministic substrate
-> Canonical loading
-> Validation
-> Canonical observation store
```

Before TASK-083, `deterministic_change_verification.py` appeared generic but contained provider-specific branches and SQL for WDI, OECD, and Eurostat. That made the deterministic layer partly responsible for source-specific canonical reconstruction.

After TASK-083:

- canonical loaders reconstruct their own loaded observed packages;
- deterministic verification only compares and validates packages already supplied to it;
- source-specific SQL remains explicit and local to the source-specific loader path;
- no generic reconstruction framework, provider registry, plugin layer, runtime dispatch, or source namespace migration was introduced.

## Compatibility summary

Observable verification behavior was preserved:

- The same WDI/OECD/Eurostat canonical load paths are exercised.
- The same observed packages are compared after canonical loading.
- Contract verification still validates both expected and reconstructed packages.
- Deterministic equivalence still requires matching fingerprints, row counts, expected row counts, observation counts, and no differing observations.

The Python call shape changed inside the project test path from:

```python
verify_loaded_observed_package(db_name, expected_package)
```

to:

```python
loaded_package = source_loader.reconstruct_loaded_observed_package(db_name, expected_package)
verify_loaded_observed_package(expected_package, loaded_package)
```

That is intentional: reconstruction ownership moved to canonical loaders while deterministic comparison stayed generic.

## Verification

RED evidence:

- `uvx pytest tests/test_deterministic_change_verification.py -q`
  - failed as expected before implementation:
    - static boundary test found `WDI` in `deterministic_change_verification.py`;
    - integration test failed because loader-owned `reconstruct_loaded_observed_package` functions did not exist yet.

GREEN evidence:

- `uvx pytest tests/test_deterministic_change_verification.py -q`
  - `2 passed`

- `uvx pytest tests/test_deterministic_change_verification.py tests/test_observed_ingestion.py tests/test_wdi_loader.py tests/test_oecd_sdmx_loader.py tests/test_eurostat_namq_loader.py tests/test_combined_source_smoke.py -q`
  - `23 passed`

- `uvx pytest tests/test_deterministic_change_verification.py tests/test_observed_ingestion.py tests/test_contract_drift.py tests/test_ingestion_feedback.py tests/test_wdi.py tests/test_oecd_sdmx.py tests/test_wdi_loader.py tests/test_oecd_sdmx_loader.py tests/test_eurostat_namq_loader.py tests/test_combined_source_smoke.py -q`
  - `44 passed`

- `uvx pytest -q`
  - `256 passed`

Note: full regression regenerated deterministic report JSONs only by changing temporary database-name fields. Those report JSONs were restored because they were outside the task scope.

## Remaining boundary observations for future migrations

Do not fix under TASK-083:

- Canonical loaders still contain mixed responsibilities: SQL generation, canonical loading, source-specific reconstruction, lineage insertion, quality checks, report writing, and CLI behavior. TASK-083 intentionally moved only reconstruction ownership, not loader architecture.
- Each loader now contains a local `_json_rows` helper for reconstruction. This duplication is acceptable under this migration because creating a shared reconstruction/query framework was explicitly out of scope.
- `src/macroforge/` remains a flat namespace; a `sources/` namespace migration remains explicitly out of scope.
- `canonicalization_state.py` still contains source-specific canonicalization examples/branches. That belongs to a separate canonicalization-state migration, not deterministic verification.
