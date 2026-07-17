# TASK-176 — Repository Growth and Historical Scaling Campaign

Status: complete
Date: 2026-07-08
Mode: repository growth plus historical/overlap scaling validation

## Objective

Continue MacroForge's transition into a repository-scale engineering project by materially increasing PostgreSQL analytical coverage while validating historical expansion, overlapping ingestion, idempotent rerun behavior, duplicate prevention, lineage preservation, canonical stability, and deterministic results.

## Campaign selection

The selected campaign was not historical-only backfill.

Phase 1 assessment found:

- Historical backfill of the existing 74 loaded indicators over 1990-1999 offered a pre-sparsity gain of 160,580 candidate cells.
- Additional implemented-module candidates over 1990-2024 offered a pre-sparsity gain of 91,140 candidate cells.
- The combined loaded-plus-implemented-module WDI annual-scalar campaign over 1990-2024 produced the largest evidence-supported envelope: 86 indicators x 217 countries x 35 years = 653,170 candidate cells.

This combined campaign stayed inside the proven WDI public API v2 annual scalar country-indicator confidence cell and existing WDI observed-package/PostgreSQL loader path.

## Execution result

- Candidate indicators assessed: 86.
- Included indicators: 86.
- Excluded indicators: 0.
- Countries: 217 non-aggregate WDI countries.
- Period: 1990-2024.
- Normalized rows: 648,475.
- Observed values: 399,934.
- Explicit missing-value evidence rows: 248,541.

PostgreSQL growth:

- Curated WDI fact rows before first load: 392,431.
- Curated WDI fact rows after first load: 648,475.
- Curated fact rows added: 256,044.
- WDI indicators after campaign: 86.
- WDI period dimension after campaign: 35 annual periods.

## Historical and idempotence validation

Rerun validation used run key `task-176-repository-growth-historical-scaling-rerun`.

- Fact rows before rerun: 648,475.
- Fact rows after rerun: 648,475.
- Fact rows added by rerun: 0.
- Duplicate canonical key groups after rerun: 0.
- TASK-176 staging quality checks: pass.
- TASK-176 run-scoped fact quality checks: pass.
- Canonical scope fingerprint after rerun: `1792289f7dd85191f2b73f08dd809817`.
- Lineage preserved: true.

## Architecture stress observations

The existing schema and WDI annual-scalar loader scaled through the larger historical/overlap campaign without provider mirrors, schema redesign, partitioning, canonical identity changes, generic WDI framework extraction, or production scheduling.

Observed loader weakness: the inherited WDI quality check compared source-wide fact rows against the current package size, which is invalid after overlapping/incremental campaigns. TASK-176 corrected this to run-scoped fact-row validation in `src/macroforge/wdi_loader.py` before executing the campaign. This was evidence-supported hardening, not architecture redesign.

Observable throughput and memory:

- First load wall time: 3m20.79s.
- First load max RSS from `/usr/bin/time`: 6,309,972 KB.
- Rerun wall time: 1m22.41s.
- Rerun max RSS from `/usr/bin/time`: 5,678,164 KB.

## Deliverables

- `tools/task176_repository_growth_historical_scaling.py`
- `artifacts/reports/task-176-growth-opportunity-assessment.json`
- `artifacts/reports/task-176-repository-growth-preflight-report.json`
- `artifacts/reports/task-176-repository-growth-classification-report.json`
- `artifacts/reports/task-176-repository-growth-operational-report.json`
- `artifacts/reports/task-176-repository-growth-coverage-report.json`
- `artifacts/reports/task-176-repository-growth-confidence-report.json`
- `artifacts/reports/task-176-load-report.json`
- `artifacts/reports/task-176-idempotence-validation-report.json`
- `artifacts/reports/task-176-final-campaign-report.json`
- `artifacts/reports/R-20260708-task-176-repository-growth-and-historical-scaling-campaign.md`
- `artifacts/reports/R-20260708-task-176-repository-growth-report.md`
- `artifacts/reports/R-20260708-task-176-historical-scaling-validation.md`
- `artifacts/reports/R-20260708-task-176-idempotence-validation.md`
- `artifacts/reports/R-20260708-task-176-capability-improvement-report.md`
- `artifacts/reports/R-20260708-task-176-architecture-stress-observations.md`

## Verification

Executed successfully:

```text
PYTHONPATH=src python3 tools/task176_repository_growth_historical_scaling.py assess --db macroforge
PYTHONPATH=src python3 tools/task176_repository_growth_historical_scaling.py fetch --db macroforge
PYTHONPATH=src python3 tools/task176_repository_growth_historical_scaling.py artifacts --db macroforge
/usr/bin/time -v env PYTHONPATH=src python3 tools/task176_repository_growth_historical_scaling.py load --db macroforge
/usr/bin/time -v env PYTHONPATH=src python3 tools/task176_repository_growth_historical_scaling.py validate --db macroforge
PYTHONPATH=src python3 tools/task176_repository_growth_historical_scaling.py reports --db macroforge
```

Final governance verification is recorded in `context/latest_handoff.md`.

## Next largest evidence-supported campaign

The next largest safe repository expansion should continue WDI annual-scalar repository growth only if another source-module-backed or DB-loaded indicator family can be evidenced without arbitrary catalog crawling. If no larger implemented-compatible WDI set remains, run a deterministic growth-opportunity assessment before expanding to a new provider confidence cell.
