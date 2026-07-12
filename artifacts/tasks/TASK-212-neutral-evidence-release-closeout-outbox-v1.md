# TASK-212 — Neutral Evidence Release Closeout Outbox v1

Status: completed
Date: 2026-07-11

## Objective

Connect the proven MacroForge neutral evidence exporter to successful canonical release closeout through a MacroForge-owned subscription registry, outbox publisher, and export-status registry.

## Outcome

Decision A: closeout-triggered neutral export publication validated.

## Files changed

- `src/macroforge/neutral_evidence_release_outbox.py`
- `config/neutral_evidence_release_subscriptions.json`
- `tests/test_neutral_evidence_release_outbox.py`
- `artifacts/exports/neutral-evidence-release/outbox/`
- `artifacts/reports/neutral-evidence-closeout-outbox-v1-20260711/`

## First published outbox export

- Export: `artifacts/exports/neutral-evidence-release/outbox/macroforge-wdi-trade-share-dnk-swe-nor-annual-v1/macroforge-wdi-1990-2024-2b1a1c3d9e65b182/macroforge-wdi-1990-2024-2b1a1c3d9e65b182.neutral-release.json`
- Manifest: `artifacts/exports/neutral-evidence-release/outbox/macroforge-wdi-trade-share-dnk-swe-nor-annual-v1/macroforge-wdi-1990-2024-2b1a1c3d9e65b182/manifest.json`
- Registry: `artifacts/exports/neutral-evidence-release/outbox/export-status-registry.jsonl`
- Release identity: `macroforge-wdi-1990-2024-2b1a1c3d9e65b182`
- Release fingerprint: `sha256:def8c318100cf14526cbdac87335e6b1646681b2176fd684c66ac7cc9d7add67`
- Export SHA-256: `1906821add91de87538f29bbbc254c8d52d5f6734ba7f00aced45fe2c5358f86`
- Item count: 210

## Verification

Targeted tests: `21 passed in 2.94s`.
Full MacroForge suite: `784 passed, 1 skipped in 806.60s (0:13:26)`. Full verification logs are under `artifacts/reports/neutral-evidence-closeout-outbox-v1-20260711/verification/` and `.../final-verification/`.
