# TASK-215 BIS credit-gap Phase 2 processed artifacts

Active processed artifacts for TASK-215 BIS WS_CREDIT_GAP quarterly credit-to-GDP-gap expansion.

## Active artifacts

- `active/task-215-bis-credit-gap-normalized.json` — 2,752 normalized quarterly country scalar observations from 43 provider-advertised BIS WS_CREDIT_GAP series over 2010-Q1 through 2025-Q4.
- `active/task-215-bis-credit-gap-manifest.json` — active artifact manifest with source, dataset, snapshot, run, candidate, observed/missing, dimensional compatibility, and checksum metadata.

## Scope

- Source: `BIS_PUBLIC_SDMX_API`
- Provider dataset: `BIS:WS_CREDIT_GAP`
- Snapshot/as-of identity: `bis-ws-credit-gap-snapshot-prepared-20260712t162752z`
- Snapshot meaning: acquired BIS SDMX response snapshot from provider Prepared timestamp, not official BIS publication release.
- Frequency: quarterly
- Periods: 2010-Q1 through 2025-Q4
- Territories: 43 accepted territories
- Aggregate excluded: `XM` Euro area aggregate
- Selected dimensions: `TC_BORROWERS=P`, `TC_LENDERS=A`, `CG_DTYPE=C`
- Unit: percentage points
- Observed facts: 2,752
- Explicit-missing facts: 0

## Notes

Canonical indicator identity removes only territory from the complete provider series key and preserves borrower sector, lender sector, credit-gap measure, unit, and frequency.
