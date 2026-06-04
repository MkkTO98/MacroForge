# TASK-011 — Spike no-key OECD/SDMX-style second source

Status: completed
Created: 2026-06-03
Completed: 2026-06-03
Decision: DEC-005

## Goal

Run a bounded evidence-gathering spike for a no-key public second source with a different API/data shape than World Bank WDI, using OECD/SDMX-style data as the first candidate.

## Scope

- No paid or credentialed APIs.
- No full implementation unless the spike proves the source is viable.
- Prefer a tiny smoke slice comparable in size to the WDI smoke slice.
- Use the minimal source contract from TASK-010 if available.

## Acceptance criteria

- Evidence report records the candidate endpoint/source, access requirements, response shape, source metadata, and friction.
- If viable, report proposes the smallest implementation task and schema impact.
- If not viable, report explains why and recommends the next no-key candidate.
- No production/live `macro` database writes occur.
- Tests/coherence pass if project files change.

## Outcome

Created `artifacts/reports/oecd-sdmx-second-source-spike-20260603.md`.

The OECD/SDMX-style candidate is viable for a bounded next source-specific evidence slice. The tested endpoint responded with HTTP 200 and SDMX GenericData XML without credentials. The response shape differs materially from WDI: XML, series-key dimensions, observation dimensions, and observation attributes.

The report recommends a small OECD/SDMX raw-evidence/normalization implementation next, not a generalized SDMX framework or immediate PostgreSQL load.

## Evidence summary

```text
status 200
content_type application/vnd.sdmx.genericdata+xml; version=2.1; charset=utf-8
bytes 1002311
sha256 d1e67a62dd5f35ab7530781e73343d5c64e6d073bea1edc7d59b56b28cbe5546
series 832 obs 832
```

## Notes

The spike is allowed to conclude "do not implement this source yet." Evidence quality matters more than forcing an ingestion path.
