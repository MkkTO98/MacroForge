# MacroForge Domain Coverage Assessment

Status: active lightweight domain-coverage map
Created: 2026-06-30

## Purpose

This document tracks MacroForge's long-term observation-domain coverage at a high level.

It is not an architectural review, roadmap, implementation authorization, source priority list, or canonical entity design. It is a lightweight coverage map that should be updated only for the affected domain when bounded implementations materially change coverage.

## Labor market domain

Last updated: 2026-06-30
Related implementation: `artifacts/tasks/TASK-059-bounded-ilostat-unemployment-rate-evidence-slice.md`
Related lessons: `artifacts/reports/L-20260630-task-059-implementation-lessons.md`

### Current coverage maturity

Initial bounded evidence.

MacroForge now has one source-specific labor-market evidence slice through ILOSTAT annual unemployment-rate observations for USA and Japan in 2023-2024. The slice is evidence-only: no broad ILOSTAT support, no canonical loading, no labor classification framework, no KnowledgeForge semantics, and no general labor-market infrastructure.

### Newly represented concepts

- Labor-market observation domain.
- Unemployment rate.
- Annual frequency labor observation.
- Total-sex classification evidence: `SEX_T`.
- Age 15+ classification evidence: `AGE_YTHADULT_YGE15`.
- ILOSTAT provider row fields: `ref_area`, `source`, `indicator`, `sex`, `classif1`, `time`, `obs_value`, and `obs_status`.
- Percent-of-labor-force unit representation as source-backed observation metadata.

### Remaining major gaps

- Employment levels and rates.
- Labor-force participation.
- Wages and earnings.
- Hours worked.
- Job vacancies.
- Underemployment and informality.
- Demographic breakdowns by sex, age group, education, and other classifications.
- Higher-frequency labor observations where available.
- Country breadth beyond USA/Japan.
- Multiple labor providers and cross-provider comparison.
- Canonical labor-domain mappings and canonical loading.
- Labor-market source update/release behavior.

### Candidate future expansion directions

- Add a bounded employment or labor-force-participation slice from ILOSTAT.
- Add a bounded wage/earnings slice if a compact no-key provider path is available.
- Add a national source labor slice, such as BLS unemployment/employment, to compare official national-source labor evidence against ILOSTAT.
- Add demographic breakdowns only after the simple total-population labor-rate path remains cheap and deterministic.
- Consider canonical labor mapping only after repeated source evidence demonstrates recurring mapping pain and satisfies the extraction gate.

## International trade domain

Last updated: 2026-06-30
Related implementation: `artifacts/tasks/TASK-060-bounded-un-comtrade-bilateral-total-goods-trade-evidence-slice.md`
Related lessons: `artifacts/reports/L-20260630-task-060-implementation-lessons.md`

### Current coverage maturity

Initial bounded evidence.

MacroForge now has one source-specific international-trade evidence slice through UN Comtrade annual bilateral total-goods import/export observations for USA and Japan in 2023. The slice is evidence-only: no broad UN Comtrade support, no generic trade infrastructure, no product classification framework, no quantity/volume interpretation, no mirror trade reconciliation, no canonical loading, and no KnowledgeForge semantics.

### Newly represented concepts

- International-trade observation domain.
- Bilateral reporter-partner trade relationship.
- Reporter country evidence: USA / `reporterCode=842`.
- Partner country evidence: Japan / `partnerCode=392`.
- Trade direction evidence: import (`M`) and export (`X`).
- Annual goods-trade period.
- Aggregate product/classification slot: `cmdCode=TOTAL`, All Commodities.
- UN Comtrade HS classification evidence: `classificationSearchCode=HS`, `classificationCode=H6`.
- Nominal trade value in current US dollars via `primaryValue`, with source-backed FOB/CIF value-basis metadata.
- Quantity/weight fields preserved as source evidence but not interpreted.

### Remaining major gaps

- Product-level HS trade observations.
- Product classification hierarchy.
- Quantity, volume, weight, and unit interpretation.
- Multiple years and update/release behavior.
- Multiple reporters and partners.
- Mirror trade comparison and asymmetry handling.
- Services trade.
- Re-exports, re-imports, customs, and mode-of-transport semantics.
- Trade balances and other derived trade measures.
- BACI, IMF DOTS, Eurostat COMEXT, WTO, and national-source comparison.
- Canonical product, country-role, and trade-direction mappings.
- Canonical loading.

### Candidate future expansion directions

- Add a bounded product-level UN Comtrade HS slice after the aggregate bilateral path remains cheap and deterministic.
- Add a bounded IMF DOTS bilateral aggregate trade slice to compare macro bilateral trade evidence against UN Comtrade.
- Add a bounded BACI slice when bulk-file acquisition is justified by product-level or mirror-cleaned trade evidence needs.
- Add a bounded Eurostat COMEXT slice only when EU-specific product trade coverage becomes useful.
- Consider canonical trade mapping only after repeated trade-source evidence demonstrates recurring mapping pain and satisfies the extraction gate.

## Demographics domain

Last updated: 2026-06-30
Related implementation: `artifacts/tasks/TASK-061-bounded-demographic-foundation-evidence-slice.md`
Related lessons: `artifacts/reports/L-20260630-task-061-implementation-lessons.md`

### Current coverage maturity

Initial foundation evidence.

MacroForge now has one source-specific demographic foundation evidence slice through World Bank WDI annual observations for USA and Japan in 2022-2023. The slice is intentionally broader than a minimal domain-entry task because demographics are foundational inputs for later economic analysis, but it remains evidence-only: no broad WDI demographic support, no generic demographic framework, no projection system, no detailed age pyramid, no migration system, no canonical loading, and no KnowledgeForge semantics.

### Newly represented concepts

- Demographic observation domain.
- Total population: `SP.POP.TOTL`.
- Annual population growth: `SP.POP.GROW`.
- Age structure: ages 0-14, 15-64, and 65+ as percent of total population.
- Fertility rate: `SP.DYN.TFRT.IN`.
- Life expectancy at birth: `SP.DYN.LE00.IN`.
- Urbanization: urban population as percent of total population, `SP.URB.TOTL.IN.ZS`.
- Annual country demographic observations for USA and Japan.
- WDI indicator, country, period, unit, request, and source-row metadata.

### Remaining major gaps

- Sex-specific demographic breakdowns.
- Single-year or five-year cohort age structure.
- Detailed age pyramids.
- Migration flows and net migration.
- Mortality rates, infant mortality, and cause-specific mortality.
- Dependency ratios.
- Population density and land-area context.
- Household composition.
- Regional/subnational demographics.
- Educational attainment.
- Projection scenarios and population forecasting.
- UN Population Division cross-source demographic evidence.
- Canonical demographic mappings and canonical loading.

### Highest-value future demographic expansion

The highest-value next demographic expansion is a bounded UN Population Division slice that introduces cross-source demographic evidence for the same foundational concepts or a narrowly scoped migration/mortality detail slice if a concrete downstream analysis requires it.

Do not create a generic demographic framework until multiple demographic sources demonstrate recurring source-neutral contract, algorithm, and implementation convergence with measurable effort reduction.

## Industry and input-output domain

Last updated: 2026-07-01
Related implementation: `artifacts/tasks/TASK-062-bounded-eurostat-input-output-matrix-evidence-slice.md`
Related lessons: `artifacts/reports/L-20260701-task-062-implementation-lessons.md`

### Current coverage maturity

Initial bounded matrix evidence.

MacroForge now has one source-specific Eurostat input-output matrix evidence slice through `naio_10_cp1700` for Germany and France in 2020. The slice is evidence-only: no broad Eurostat NAIO support, no supply-use/input-output framework, no CPA classification framework, no product hierarchy inference, no multipliers, no canonical loading, and no KnowledgeForge semantics.

### Newly represented concepts

- Industry/input-output observation domain.
- Product-by-product matrix cell observations.
- Two product roles in one observation: product available/supplied (`prd_ava`) and product used/consumed (`prd_use`).
- Stock/use flow partition: imports (`IMP`) and domestic uses (`DOM`).
- CPA product classification evidence for `CPA_A01` and `CPA_C10-12`.
- Annual country input-output matrix evidence for Germany and France.
- Eurostat JSON-stat dimension order, flat index, label, source, update, unit, geography, product-role, and flow metadata.

### Remaining major gaps

- Full product and industry coverage.
- Supply-use tables beyond symmetric product-by-product tables.
- Industry-by-industry input-output tables.
- Multi-year input-output observations and update/release behavior.
- Additional countries and cross-country comparability.
- Product/industry hierarchy interpretation.
- Domestic/imported use interpretation beyond source-role preservation.
- Derived input-output analytics such as technical coefficients, multipliers, and Leontief inverse.
- OECD ICIO or other international input-output sources.
- Canonical product/industry mappings and canonical loading.

### Highest-value future input-output expansion

The highest-value future expansion is a second bounded matrix/cube source or a slightly broader Eurostat NAIO slice that adds another matrix shape, such as industry-by-industry or supply-use evidence, only after the current product-by-product matrix slice remains cheap and deterministic.

Do not create a generic input-output or matrix framework until multiple independent matrix/cube implementations demonstrate recurring source-neutral contract, algorithm, and implementation convergence with measurable effort reduction.

## International financial-flow domain

Last updated: 2026-07-01
Related implementation: `artifacts/tasks/TASK-063-bounded-imf-bop-financial-account-evidence-slice.md`
Related lessons: `artifacts/reports/L-20260701-task-063-implementation-lessons.md`

### Current coverage maturity

Initial bounded financial-account flow evidence.

MacroForge now has one source-specific IMF BOP financial-account evidence slice for USA and Japan in 2022-2023. The slice is evidence-only: no broad IMF BOP support, no financial-account framework, no IIP/CPIS/CDIS/BIS support, no financial instrument hierarchy, no partner-country or holder/issuer relationships, no canonical financial semantics, no canonical loading, and no KnowledgeForge semantics.

### Newly represented concepts

- International financial-flow observation domain.
- Balance of Payments financial-account transaction observations.
- Asset-side flow: net acquisition of financial assets (`A_NFA_T`).
- Liability-side flow: net incurrence of liabilities (`L_NIL_T`).
- Investment category evidence: direct investment (`D_F`) and portfolio investment (`P_F`).
- Annual country financial-account observations for USA and Japan.
- IMF BOP dataflow, DSD, dimension order, accounting-entry, investment-category, unit, scale, methodology, access/security, and observation attribute metadata.

### Remaining major gaps

- Full BOP financial-account category coverage.
- Other investment, reserve assets, derivatives, and instrument-level detail.
- Current account and capital account observations.
- International Investment Position stock observations.
- CPIS/CDIS holder/issuer or direct-investment relationship evidence.
- BIS cross-border banking relationship evidence.
- Partner-country/resident/non-resident counterparty dimensions beyond BOP aggregate scope.
- Quarterly/monthly frequency where available.
- Additional countries, periods, and update/release behavior.
- Canonical financial-account mappings and canonical loading.

### Highest-value future financial-flow expansion

The highest-value future expansion is a bounded IIP or CPIS/CDIS slice if the next objective is to add stock-position or holder/issuer relationship evidence, respectively. Do not create a generic Balance of Payments or financial-flow framework until multiple financial-flow sources demonstrate recurring source-neutral contract, algorithm, and implementation convergence with measurable effort reduction.

## Energy domain

Last updated: 2026-07-01
Related implementation: `artifacts/tasks/TASK-064-bounded-eurostat-energy-balance-evidence-slice.md`
Related lessons: `artifacts/reports/L-20260701-task-064-implementation-lessons.md`

### Current coverage maturity

Initial bounded energy-accounting evidence.

MacroForge now has one source-specific Eurostat complete energy balance evidence slice for Germany and France in 2022-2023. The slice is evidence-only: no broad Eurostat Energy support, no generic JSON-stat infrastructure, no generic energy infrastructure, no canonical energy semantics, no canonical loading, no energy-balance validation, no unit conversion, and no KnowledgeForge semantics.

### Newly represented concepts

- Energy observation domain.
- Official energy balance component dimension: `nrg_bal`.
- Energy product/fuel category dimension: `siec`.
- Primary production (`PPRD`).
- Imports (`IMP`).
- Exports (`EXP`).
- Final consumption - energy use (`FC_E`).
- Total energy product (`TOTAL`).
- Renewables and biofuels (`RA000`).
- Energy unit `KTOE` — thousand tonnes of oil equivalent.
- Annual country energy-balance cells for Germany and France.
- Eurostat JSON-stat dimension order, flat index, label, source, update, unit, geography, balance-component, and energy-product metadata.

### Remaining major gaps

- Full energy balance component coverage.
- Full energy product/fuel coverage.
- Electricity generation and capacity observations.
- Oil, gas, coal, electricity, renewables, and nuclear detail beyond the bounded two-product slice.
- Energy prices and expenditures.
- Energy reserves and resources.
- Country breadth beyond Germany/France.
- Multi-provider energy evidence such as EIA, IEA, UN Energy Statistics, and national statistical offices.
- Unit conversion and comparability profiles.
- Derived balances such as net imports, energy dependency, renewable shares, and energy intensity.
- Canonical energy mappings and canonical loading.

### Highest-value future energy expansion

The highest-value future expansion is a second bounded official energy source or a slightly broader Eurostat energy slice that adds electricity generation or a deeper fuel/product split only when a concrete downstream analysis requires it. Do not create a generic energy framework until multiple energy sources demonstrate recurring source-neutral contract, algorithm, and implementation convergence with measurable effort reduction.

## Financial market curve observation family

Last updated: 2026-07-01
Related implementation: `artifacts/tasks/TASK-065-bounded-fred-yield-curve-evidence-slice.md`
Related lessons: `artifacts/reports/L-20260701-task-065-implementation-lessons.md`

### Current coverage maturity

Initial bounded curve evidence.

MacroForge now has one source-specific FRED monthly U.S. Treasury yield-curve evidence slice for 2024-01 and 2024-02. The slice is evidence-only: no broad FRED support, no generic market-data infrastructure, no generic yield-curve framework, no interpolation, no yield-spread/slope analytics, no canonical instrument/tenor semantics, no canonical loading, and no KnowledgeForge semantics.

### Newly represented concepts

- Financial market curve observation family.
- Same-period cross-sectional term-structure observations.
- U.S. Treasury constant-maturity yield tenors: `GS1M`, `GS1`, `GS10`, `GS30`.
- Tenor metadata: labels, months, and years.
- Monthly market curve point observations.
- Percent yield unit.
- FRED CSV row/column evidence and source-backed series IDs.

### Remaining major gaps

- Daily yield curve observations.
- Additional tenors.
- Yield spreads, slopes, inversions, interpolation, and curve fitting.
- Non-U.S. sovereign yield curves.
- Corporate credit curves and spreads.
- Inflation-linked and real yield curves.
- Equity prices, commodity prices, volatility, and other market-data families.
- Multi-provider market evidence.
- Canonical instrument/tenor mappings and canonical loading.

### Highest-value future curve/market expansion

The highest-value future expansion is either a second bounded official market curve source or a broader U.S. Treasury curve slice only if a concrete downstream need requires additional tenors or daily frequency. Do not create a generic market-data or yield-curve framework until multiple market sources demonstrate recurring source-neutral contract, algorithm, and implementation convergence with measurable effort reduction.

## Update rule

When a future bounded implementation affects a domain or observation family, update only that section unless the task explicitly authorizes a broader coverage review.
