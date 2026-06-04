# TASK-007 — Add runbook and validation reporting

Status: completed on 2026-06-03

## Acceptance

Future agent can rerun and verify the pipeline.

## Delivered files

- `tests/test_wdi_validation.py`
- `src/macroforge/wdi_validation.py`
- `artifacts/reports/wdi-validation-smoke-20260602.json`
- `artifacts/reports/wdi-validation-smoke-20260602.md`
- Updated `docs/runbooks/wdi-v1-runbook.md`

## Verification

RED was confirmed first with missing validation module import:

```text
ImportError: cannot import name 'wdi_validation' from 'macroforge'
```

Targeted validation test:

```text
1 passed in 0.50s
```

Isolated validation report status:

```text
"status": "pass"
```

Full tests:

```text
12 passed in 1.10s
```

Coherence:

```text
{
  "mode": "generated",
  "blocks": [],
  "warnings": []
}
```
