# TASK-143 — WDI Financial Accounts Core Operational Dataset

Status: complete.

## Strategic context

MacroForge is in Operational Repository Construction. Repository progress is evaluated by which repository section most limits MacroForge's usefulness as an independent operational economic repository.

## Selection

Selected repository section: Financial Accounts.

Why Financial Accounts limited repository usefulness: after TASK-140 through TASK-142, Inflation and Labor are bounded Operationally Useful, Trade is Developing, and macroeconomy/demographics/energy have broad WDI operational foundations. Financial Accounts still had bounded IMF G7 slices and related monetary/credit evidence, but no broad country-year operational panel with deterministic refresh, PostgreSQL loading, and quality validation. For an independent economist, this left a core macro-financial repository section weaker than the recently strengthened sections.

Housing was initially considered because it remains weak, but live FRED graph acquisition repeatedly timed out/failed in this environment before implementation. That was treated as an external source-access issue, not a Mandatory Decision Gate, and the next strongest deterministic bounded implementation was selected.

## Scope

Provider: World Bank WDI.

Dataset: WDI Financial Accounts Core Operational Dataset.

Indicators:

- `FS.AST.PRVT.GD.ZS` — domestic credit to private sector by banks, percent of GDP.
- `FM.LBL.BMNY.GD.ZS` — broad money, percent of GDP.
- `CM.MKT.LCAP.GD.ZS` — market capitalization of listed domestic companies, percent of GDP.
- `CM.MKT.LDOM.NO` — listed domestic companies, total count.

Countries: 217 WDI non-aggregate countries selected by the existing WDI country-catalog pattern.

Period: 2000 through 2023 annual observations.

Row count: 217 countries × 4 indicators × 24 years = 20,832 rows.

## Repository Section Contribution

1. Repository section improved: Financial Accounts.
2. Financial Accounts provided the greatest current increase in overall repository usefulness because it moved a core macro-financial section from bounded evidence only toward broad operational country-year coverage while stronger sections should not be expanded indefinitely.
3. Section status after implementation: Developing. Evidence: broad WDI domestic credit, broad money, equity-market capitalization, and listed-company-count operational coverage with deterministic raw evidence, normalized artifact, refresh manifest/delta, PostgreSQL load/replay verification, and quality checks. The section is not yet Operationally Useful because detailed financial-account flows/positions remain bounded, instrument/counterparty detail is limited, and no financial instrument hierarchy or cross-provider reconciliation has been justified.

## Non-goals preserved

- No full WDI catalog ingestion.
- No financial-accounts framework.
- No banking framework.
- No market-structure framework.
- No instrument hierarchy.
- No counterparty/holder graph.
- No KnowledgeForge semantics.
- No architecture or ObservedIngestionPackage redesign.
- No Controlled Expansion.

## Implementation files

- `src/macroforge/wdi_financial_accounts_core.py` — source-specific normalization, observed package construction, manifest, and delta helpers.
- `src/macroforge/wdi_loader.py` — source-specific `load_wdi_financial_accounts_core_operational_to_postgres` wrapper over existing WDI loader mechanics.
- `tests/test_wdi_financial_accounts_core_operational.py` — RED/GREEN tests.
- `data/raw/wdi_financial_accounts_core_operational/wdi-financial-accounts-core-all-countries-4i-2000-2023.json` — raw WDI fixture.
- `data/metadata/wdi_financial_accounts_core_operational/wdi-financial-accounts-core-normalized.json` — normalized operational artifact.
- `data/operational/wdi_financial_accounts_core_operational/wdi-financial-accounts-core-refresh-manifest.json` — refresh manifest.
- `data/operational/wdi_financial_accounts_core_operational/wdi-financial-accounts-core-refresh-delta-report.json` — refresh delta evidence.
- `artifacts/reports/task-143-wdi-financial-accounts-core-operational-load-report.json` — PostgreSQL load report.

## Verification evidence

RED:

- Initial TASK-143 housing RED: `uvx pytest tests/test_fred_housing_core_operational.py -q` failed because `macroforge.fred_housing_core` did not exist. Housing source acquisition was then blocked by repeated FRED graph endpoint timeouts/errors.
- Financial Accounts TDD proceeded with tests for the selected deterministic WDI source.

GREEN:

- `uvx pytest tests/test_wdi_financial_accounts_core_operational.py -q`
- Result: `6 passed in 22.68s`.

Operational load/replay:

- PostgreSQL load counts: `staging_rows=20832`, `fact_rows=20832`, `lineage_events=2`, `quality_checks=2`.
- PostgreSQL shape: `20832|4|217|24|2`.
- Package fingerprint: `1f40abc03c878a657bb74426ae2faeeb1f83131fba6cbffb0e37bc5391474617`.
- Raw fixture SHA256: `b959b323b0e99373e4e0e1131160d44dda807d60c83836f983434e28a5a33aa0`.

## Repository Completion Monitoring

1. Section improved: Financial Accounts.
2. Current maturity: Developing.
3. Remaining before Operationally Useful: broader flow/position operational coverage, better instrument/counterparty detail, and source-backed cross-provider comparison for key macro-financial concepts.
4. Weakest next section: Housing remains the weakest named core section because it has only bounded construction and price evidence and live FRED acquisition failed in this cycle.

## Selection Retrospective

Housing initially appeared to be the weakest section, but deterministic acquisition from FRED graph CSV failed repeatedly before implementation. Financial Accounts then won because WDI offered a deterministic, broad, source-specific operational panel that substantially improved an underdeveloped core macro-financial section without architecture pressure. The outcome matched expected marginal gain: the section moved from bounded evidence toward Developing operational repository status.

## Relationship primitive evidence

No new evidence. TASK-143 is country-period scalar financial-account/market-structure evidence, not a relationship implementation.

## Controlled Expansion readiness observation

No change from previous assessment.
