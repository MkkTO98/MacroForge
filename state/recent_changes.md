# Recent Changes

## 2026-07-10 — TASK-207 Phase 2 BLS monthly labor campaign

- Accepted Phase 2 transition away from automatic residual WDI bulk campaigns.
- Selected BLS public API v2 U.S. monthly labor-market evidence as the first diverse-source macroeconomic enrichment target.
- Recorded frozen selection prediction in `artifacts/reports/task-207-bls-us-labor-monthly-frozen-selection-prediction.json`.
- Implemented `tools/task207_bls_us_labor_monthly_phase2_campaign.py` with deterministic BLS acquisition chunks, raw evidence preservation, normalization, provider classification, PostgreSQL load, lineage/quality evidence, idempotence check, and prediction evaluation.
- Added `tests/test_task207_bls_us_labor_monthly_phase2_campaign.py`.
- Loaded 2,374 facts across 12 BLS monthly labor/payroll/wage/hours/JOLTS series for USA, 2010-M01 through 2026-M06.
- Verified run-scoped PostgreSQL counts: `2374|2374|12|198|2|3|0` for staging, facts, indicators, periods, lineage, quality, failed quality.
- Duplicate canonical key groups: 0.
- Prediction-quality verdict: Mostly Accurate.
- Architecture verdict: frozen/evidence-maintained; existing monthly scalar substrate sufficed.

## 2026-07-10 — TASK-206 corrected Phase 1 transition gate

- Corrected WDI/ASPIRE blank-`countryiso3code` handling with bounded `country.id` fallback for accepted non-aggregate territories.
- Regenerated and reloaded corrected social-protection all-programs evidence.
- Established Phase 1 transition gate: bulk WDI annual-scalar is no longer the default.
