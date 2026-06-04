# TASK-005 — Recreate narrow WDI extract/raw evidence slice

Status: completed on 2026-06-02

## Acceptance

USA/DNK GDP/population 2020-2021 smoke result with raw artifact, checksum, and report.

## Delivered files

- `tests/test_wdi.py`
- `src/macroforge/wdi.py`
- `data/raw/wdi/worldbank_wdi_NY.GDP.MKTP.CD_USA_DNK_2020_2021_raw.json`
- `data/raw/wdi/worldbank_wdi_SP.POP.TOTL_USA_DNK_2020_2021_raw.json`
- `data/metadata/wdi/wdi-smoke-manifest.json`
- `data/metadata/wdi/wdi-smoke-normalized.json`
- `artifacts/reports/wdi-smoke-20260602.md`
- `docs/runbooks/wdi-v1-runbook.md`

## Evidence source

The current session did not retry the blocked World Bank HTTP request. It used the live no-key API support bundle produced by another Hermes session at:

`artifacts/handoffs/wdi-live-smoke-support-20260602/`

That bundle records HTTP status, URLs, bytes, sha256 checksums, source metadata, and the raw WDI payloads.

## Verification

Targeted WDI tests:

```text
4 passed in 0.02s
```

Full tests:

```text
9 passed in 0.24s
```

Coherence:

```text
{
  "mode": "generated",
  "blocks": [],
  "warnings": []
}
```
