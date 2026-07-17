# TASK-142 — WDI Trade Core Operational Dataset

Status: complete.

## Strategic context

MacroForge is in Operational Repository Construction. Repository progress is evaluated by which section most limits MacroForge's usefulness as an independent operational economic repository.

## Selection

Selected repository section: Trade.

Why Trade limited repository usefulness: MacroForge had bounded bilateral goods-trade evidence and services-trade intensity evidence, but no validated operational trade dataset with broad historical/geographic coverage, deterministic refresh, PostgreSQL loading, and quality validation. After Inflation and Labor reached bounded Operationally Useful status through TASK-140 and TASK-141, Trade was the weakest core economic section for an independent economist using MacroForge as a repository.

## Scope

Provider: World Bank WDI.

Dataset: WDI Trade Core Operational Dataset.

Indicators:

- `NE.EXP.GNFS.CD` — exports of goods and services, current US dollars.
- `NE.IMP.GNFS.CD` — imports of goods and services, current US dollars.
- `NE.EXP.GNFS.ZS` — exports of goods and services as percent of GDP.
- `NE.IMP.GNFS.ZS` — imports of goods and services as percent of GDP.

Countries: 217 WDI non-aggregate countries selected by the existing WDI country-catalog pattern.

Period: 2000 through 2023 annual observations.

Row count: 217 countries × 4 indicators × 24 years = 20,832 rows.

## Repository Section Contribution

1. Repository section improved: Trade.
2. Trade provided the greatest current increase in overall repository usefulness because it moved from bounded evidence only to broad operational core coverage while macroeconomy, demographics, energy, inflation, and labor already had operational datasets or operationally useful bounded coverage.
3. Section status after implementation: Developing. Evidence: broad WDI exports/imports operational coverage with deterministic raw evidence, normalized artifact, refresh manifest/delta, PostgreSQL load/replay verification, and quality checks. Trade is not yet Operationally Useful because bilateral partner/product detail remains bounded-only and no product taxonomy, mirror reconciliation, or derived trade-balance layer has been justified.

## Non-goals preserved

- No full WDI catalog ingestion.
- No generic trade framework.
- No product taxonomy.
- No bilateral partner hierarchy.
- No trade balance analytics beyond source-backed observations.
- No KnowledgeForge semantics.
- No architecture or ObservedIngestionPackage redesign.
- No Controlled Expansion.

## Implementation files

- `src/macroforge/wdi_trade_core.py` — source-specific normalization, observed package construction, manifest, and delta helpers.
- `src/macroforge/wdi_loader.py` — source-specific `load_wdi_trade_core_operational_to_postgres` wrapper over existing WDI loader mechanics.
- `tests/test_wdi_trade_core_operational.py` — RED/GREEN tests for fixture, normalization, deterministic package, manifest/delta, PostgreSQL load, and non-goal boundaries.
- `data/raw/wdi_trade_core_operational/wdi-trade-core-all-countries-4i-2000-2023.json` — raw WDI fixture.
- `data/metadata/wdi_trade_core_operational/wdi-trade-core-normalized.json` — normalized operational artifact.
- `data/operational/wdi_trade_core_operational/wdi-trade-core-refresh-manifest.json` — refresh manifest.
- `data/operational/wdi_trade_core_operational/wdi-trade-core-refresh-delta-report.json` — no-change delta evidence.
- `artifacts/reports/task-142-wdi-trade-core-operational-load-report.json` — PostgreSQL load report.

## Verification evidence

RED:

- `uvx pytest tests/test_wdi_trade_core_operational.py -q`
- Result: collection failed because `load_wdi_trade_core_operational_to_postgres` / TASK-142 module behavior did not exist yet.

GREEN:

- `uvx pytest tests/test_wdi_trade_core_operational.py -q`
- Result: `6 passed in 22.55s`.

Operational load/replay:

- PostgreSQL load counts: `staging_rows=20832`, `fact_rows=20832`, `lineage_events=2`, `quality_checks=2`.
- PostgreSQL shape: `20832|4|217|24|2`.
- Package fingerprint: `8fbd0ad54db70fa31159b199d0fbb7c1c9194eb471b026b4a8465080549cd114`.
- Raw fixture SHA256: `d537645e66831fab3d75238ca5205d3790699dd7357ebdc909c0f158aa8bd262`.

## Selection Retrospective

Trade won over further labor, inflation, macroeconomy, demographics, and energy expansion because those sections already had operational datasets or operationally useful bounded coverage, while Trade lacked broad operational historical/geographic coverage. The representational gain was moving trade from bounded bilateral/service-intensity evidence to a broad country-year operational panel for exports/imports in levels and GDP shares. The outcome matched the expected marginal gain: the section moved from Initial bounded evidence to Developing repository section without architecture pressure.
