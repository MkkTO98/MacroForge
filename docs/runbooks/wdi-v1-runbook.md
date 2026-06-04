# WDI V1 Runbook

## Purpose

This runbook lets a future agent rerun and verify the current WDI vertical-slice smoke path without reading raw chat history.

It covers:

1. Generate raw/metadata artifacts from the live support bundle.
2. Apply the v0 PostgreSQL schema to an isolated local database.
3. Load WDI smoke rows into staging and curated tables.
4. Rerun the loader to prove idempotency.
5. Generate validation reports.
6. Run tests and coherence checks.

## Network policy

Do not retry the previously blocked World Bank HTTP request in this session. TASK-005 uses the live no-key API support bundle at:

`artifacts/handoffs/wdi-live-smoke-support-20260602/`

## Smoke slice

- Source: World Bank WDI
- Countries: USA, DNK
- Indicators: `NY.GDP.MKTP.CD`, `SP.POP.TOTL`
- Years: 2020-2021
- Expected rows: 8 observations

## Step 1 — Generate raw/metadata artifacts from support bundle

```bash
PYTHONPATH=src python3 -m macroforge.wdi smoke-from-bundle   --bundle artifacts/handoffs/wdi-live-smoke-support-20260602   --output-root .   --project-layout
```

Expected output paths:

- `data/raw/wdi/`
- `data/metadata/wdi/wdi-smoke-manifest.json`
- `data/metadata/wdi/wdi-smoke-normalized.json`
- `artifacts/reports/wdi-smoke-20260602.md`

Known raw checksums:

- `NY.GDP.MKTP.CD`: `fe79eb846324a5d69df9518844e08b41add5377ac4f968208bd1152898d91167`
- `SP.POP.TOTL`: `bfda0ac8ed98a9a68ceb6af210f893f2a57e1313b829c1fd9cb73c70b04d5c0b`

## Step 2 — Load and validate in isolated PostgreSQL

Use an isolated database for smoke verification unless the user explicitly approves loading into the live `macro` database.

Single-command TASK-009 rerun:

```bash
PYTHONPATH=src python3 -m macroforge.wdi_smoke --project-root .
```

This command creates a unique isolated `macroforge_wdi_smoke_*` database, applies `db/migrations/001_v0_schema_foundation.sql`, loads WDI rows twice with the same run key, validates the database state, writes `artifacts/reports/wdi-isolated-smoke-rerun-20260603.json`, and drops the isolated database in a cleanup step.

The command refuses `--db macro` to prevent accidental live database writes.

Expanded manual equivalent:

```bash
set -euo pipefail
DB="macroforge_wdi_smoke"
createdb "$DB"
trap 'dropdb --if-exists "$DB" >/dev/null 2>&1 || true' EXIT

psql -v ON_ERROR_STOP=1 -d "$DB" -f db/migrations/001_v0_schema_foundation.sql

PYTHONPATH=src python3 -m macroforge.wdi_loader   --db "$DB"   --normalized data/metadata/wdi/wdi-smoke-normalized.json   --run-key wdi-smoke-rerun   --report artifacts/reports/wdi-load-smoke-20260602.json

# Rerun to verify idempotency.
PYTHONPATH=src python3 -m macroforge.wdi_loader   --db "$DB"   --normalized data/metadata/wdi/wdi-smoke-normalized.json   --run-key wdi-smoke-rerun   --report artifacts/reports/wdi-load-smoke-20260602.json

PYTHONPATH=src python3 -m macroforge.wdi_validation   --db "$DB"   --expected-rows 8   --json-report artifacts/reports/wdi-validation-smoke-20260602.json   --markdown-report artifacts/reports/wdi-validation-smoke-20260602.md
```

Expected validation status: `pass`.

Expected count shape after idempotent rerun:

```text
staging_rows=8
fact_rows=8
lineage_events=2
quality_checks=2
no_duplicate_fact_grain=0
```

## Step 3 — Project verification

```bash
uvx --from pytest --with pyyaml pytest tests/test_wdi.py tests/test_wdi_loader.py tests/test_wdi_validation.py -q
uvx --from pytest --with pyyaml pytest tests -q
python3 tools/check_coherence.py --project . --json
```

Current full-suite verification from TASK-007:

```text
12 passed in 1.10s
```

Current coherence:

```text
{
  "mode": "generated",
  "blocks": [],
  "warnings": []
}
```

## Live `macro` database caution

The default database name is `macro`, but these smoke steps intentionally use isolated temporary databases. Do not load into the live `macro` database without explicit user approval and a fresh dry-run.
