# TASK-010 — Define minimal source contract for second-source spike

Status: completed
Created: 2026-06-03
Completed: 2026-06-03
Decision: DEC-005

## Goal

Define the smallest source contract needed to compare WDI with a second source without building a broad ingestion framework prematurely.

## Scope

The contract should describe:

- source code/name/provider dataset code
- raw artifact metadata and checksum expectations
- normalized observation row fields
- source grain, frequency, and as-of/vintage behavior
- staging and curated load assumptions
- validation checks required before a source is accepted

## Acceptance criteria

- A concise contract/spec file exists under docs or artifacts.
- WDI is mapped to the contract as the first concrete example.
- The contract explicitly lists what is intentionally not generalized yet.
- A follow-up second-source spike can use the contract without changing the current WDI loader.
- Tests/coherence pass if any code or scaffold files change.

## Outcome

Created `docs/data/source-contract.md`.

The contract defines source identity, raw evidence, normalized observation row shape, grain/vintage behavior, staging/curated assumptions, and required validation checks. It maps WDI as the first concrete example and explicitly defers plugin registries, orchestration, ORM layers, Alembic, generalized SDMX parsing, and paid/credentialed source workflows.

## Notes

Do not create plugin registries, orchestration, or ORM layers for this task.
