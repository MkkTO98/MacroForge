# TASK-214 BIS DSR credit-cycle Phase 2 processed artifacts

Active processed artifacts for TASK-214 BIS WS_DSR quarterly debt-service-ratio expansion.

## Active artifacts

- `active/task-214-bis-dsr-credit-cycle-normalized.json` — 2,904 normalized quarterly country-sector scalar observations from 66 provider-advertised BIS WS_DSR series over 2015-Q1 through 2025-Q4.
- `active/task-214-bis-dsr-credit-cycle-manifest.json` — active artifact manifest with source, dataset, snapshot, run, candidate, observed/missing, and checksum metadata.

## Scope

- Source: `BIS_PUBLIC_SDMX_API`
- Provider dataset: `BIS:WS_DSR`
- Snapshot/as-of identity: `bis-ws-dsr-snapshot-prepared-20260712t150728z`
- Snapshot meaning: acquired BIS SDMX response snapshot from provider Prepared timestamp, not official BIS publication release.
- Frequency: quarterly
- Territories: 32 accepted non-aggregate territories
- Borrower sectors: households and NPISHs, non-financial corporations, private non-financial sector
- Observed facts: 2,904
- Explicit-missing facts: 0

## Notes

Canonical indicator identity removes only territory from the complete provider series key and preserves borrower sector, unit, and frequency.
