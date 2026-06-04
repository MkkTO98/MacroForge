# TASK-006 — Implement PostgreSQL loader for WDI staging/curated facts

Status: completed on 2026-06-03

## Acceptance

Idempotent rerun and no duplicate canonical grain.

## Delivered files

- `tests/test_wdi_loader.py`
- `src/macroforge/wdi_loader.py`
- `artifacts/reports/wdi-load-smoke-20260602.json`
- Updated `docs/runbooks/wdi-v1-runbook.md`

## Verification

RED was confirmed first with missing loader import:

```text
ImportError: cannot import name 'wdi_loader' from 'macroforge'
```

Targeted loader tests:

```text
2 passed in 0.40s
```

Isolated PostgreSQL smoke load rerun output:

```text
{
  "fact_rows": 8,
  "lineage_events": 2,
  "quality_checks": 2,
  "staging_rows": 8
}
{
  "fact_rows": 8,
  "lineage_events": 2,
  "quality_checks": 2,
  "staging_rows": 8
}
8|8|2|2
```

Full tests:

```text
11 passed in 0.62s
```

Coherence:

```text
{
  "mode": "generated",
  "blocks": [],
  "warnings": []
}
```
