# TASK-209 — IMF WEO G20 Projection Phase 2 Campaign

Status: complete
Date: 2026-07-11
Type: Phase 2 diverse-source macroeconomic repository expansion / IMF WEO annual projection scalar campaign

## Scope

Execute one substantive non-BLS Phase 2 macroeconomic campaign from another proven provider without touching TASK-208, FRED detour files, trade, company, or asset ingestion.

Selected provider and source:

- Provider: IMF.
- Source/API: IMF WEO DataMapper API v1.
- Canonical source: `IMF_WEO_DATAMAPPER_API_V1`.
- Repository class: annual projection scalar time series.
- Capability: official IMF WEO macroeconomic projection breadth for G20 countries excluding the EU aggregate.

Candidate scope:

- Countries: 19 G20 countries excluding EU aggregate.
- Indicators: 6 WEO projection indicators:
  - `NGDP_RPCH` real GDP growth;
  - `NGDPD` GDP current prices;
  - `PCPIPCH` average CPI inflation;
  - `LUR` unemployment rate;
  - `GGXCNL_NGDP` general government net lending/borrowing;
  - `GGXWDG_NGDP` general government gross debt.
- Projection years: 2026, 2027, 2028.
- Candidate observation cells: 342.

## Result

Completed repository construction through PostgreSQL load and idempotent rerun.

Observed result:

- Loaded observations/facts: 342 (339 provider-valued, 3 explicit-missing).
- Provider exclusions: 0. Saudi Arabia unemployment-rate projection cells (`LUR`, 2026-2028) are explicit-missing facts.
- Acquisition errors: 0.
- Indicators: 6.
- Countries: 19.
- Periods: 3 annual projection years, 2026:2028.
- Lineage events: 2.
- Quality checks: 2.
- Failed quality checks: 0.
- Duplicate canonical-key groups: 0.

IMF DataMapper returned 339 provider-valued cells. The 3 Saudi Arabia `LUR` cells for 2026-2028 are explicit-missing facts because the SAU series exists but those requested year keys are absent; acquisition errors and provider exclusions are both zero.

## Artifacts

- Tool: `tools/task209_imf_weo_g20_projection_phase2_campaign.py`.
- Tests: `tests/test_task209_imf_weo_g20_projection_phase2_campaign.py`.
- Raw evidence: `data/raw/task209_imf_weo_g20_projection_phase2_campaign/task-209-imf-weo-g20-projections-2026-2028.json`.
- Normalized artifact: `data/processed/task209_imf_weo_g20_projection_phase2_campaign/task-209-imf-weo-g20-projections-normalized.json`.
- Manifest: `data/processed/task209_imf_weo_g20_projection_phase2_campaign/task-209-imf-weo-g20-projections-manifest.json`.
- Provider report: `artifacts/reports/task-209-imf-weo-g20-projections-provider-evidence-report.json`.
- Load report: `artifacts/reports/task-209-imf-weo-g20-projections-postgresql-load-report.json`.
- Campaign report: `artifacts/reports/task-209-imf-weo-g20-projections-campaign-report.json`.
- Checksums: `artifacts/reports/task-209-imf-weo-g20-projections-artifact-checksums.txt`.

## PostgreSQL verification

Run-scoped tuple:

```text
342|342|6|19|3|2|2|0|0|339|3
```

Meaning:

- staging rows: 342;
- curated facts: 342;
- indicators: 6;
- territories: 19;
- periods: 3;
- lineage events: 2;
- quality checks: 2;
- failed quality checks: 0;
- duplicate canonical-key groups: 0;
- observed/provider-valued facts: 339;
- explicit-missing facts: 3.

Idempotence rerun:

```text
first == second == {'task': 'TASK-209', 'run_key': 'task-209-imf-weo-g20-projection-phase2-world-economic-outlook-april-2026', 'staging_rows': 342, 'fact_rows': 342, 'indicator_count': 6, 'territory_count': 19, 'period_count': 3, 'lineage_events': 2, 'quality_checks': 2, 'failed_quality_checks': 0, 'observed_facts': 339, 'missing_facts': 3}
idempotent: True
```

Source verification:

```text
BLS_PUBLIC_API_V2
IMF_WEO_DATAMAPPER_API_V1
WDI
source count: 3
```

The repository source count rose from the prior WDI+BLS state because TASK-209 added a genuinely distinct provider/source: IMF WEO DataMapper API v1.

## Tests and checks

Completed before final closeout:

```text
python3 -m py_compile tools/task209_imf_weo_g20_projection_phase2_campaign.py tests/test_task209_imf_weo_g20_projection_phase2_campaign.py
PYTHONPATH=src:. uvx pytest -q tests/test_task209_imf_weo_g20_projection_phase2_campaign.py
# 7 passed

PYTHONPATH=src:. uvx pytest -q tests/test_task209_imf_weo_g20_projection_phase2_campaign.py tests/test_imf_weo_projections.py tests/test_imf_iip_g7_operational.py tests/test_imf_bop_g7_operational.py tests/test_imf_mfs_ir_operational.py
# 41 passed
```

Full-suite verification initially found one stale TASK-207 BLS test expectation from the accepted canonical BLS source correction. The test was narrowly updated from the old campaign-specific BLS source code to `BLS_PUBLIC_API_V2`; no FRED-detour files were touched.

Final full-suite and governance outputs: focused/relevant tests `41 passed`; full suite `752 passed, 1 skipped`; coherence/context-health/architecture audit all `0 block(s), 0 warning(s)`; `git diff --check` passed.

## Architecture verdict

Existing source-specific acquisition/normalization and the revision-aware scalar PostgreSQL substrate were sufficient after the narrow release/vintage correction documented in `artifacts/reports/task-209-forecast-vintage-decision-evidence-integrity-audit.md`. No architecture redesign, IMF framework, forecasting framework, trade/company/asset ingestion, or generic provider abstraction was introduced.


## Final closeout consistency check

Completed in `artifacts/reports/task-209-final-closeout-consistency-check.md`. The canonical raw IMF evidence exists at `data/raw/task209_imf_weo_g20_projection_phase2_campaign/task-209-imf-weo-g20-projections-2026-2028.json` with SHA-256 `d9817f3fbf6cbaf3f58caaf438e20f0077c4cd1785db9505e49791925eebec5c`; it is ignored by `data/raw/*`, so TASK-209 Git-based reproducibility requires force-adding that raw artifact or establishing an equivalent durable evidence store before commit.
