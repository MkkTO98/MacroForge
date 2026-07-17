# TASK-178 — PostgreSQL Growth Report

Status: complete

## Scope

Domain: Demographics, Human Capital, and Population Structure.
Capability: Demographic Structure and Human Capital Core.
Provider: World Bank WDI via existing annual-scalar confidence cell.
Period: 1990:2024.
Countries: 217.
Candidate indicators assessed: 30.
Included indicators: 28.
Excluded indicators: 2.
Normalized rows: 212660.
Observed values: 179395.
Missing-value evidence rows: 33265.

## PostgreSQL growth

Curated fact rows before: 648475.
Curated fact rows after first load: 861135.
Curated fact rows added: 212660.
WDI indicators before: 86.
WDI indicators after: 114.
WDI indicators added: 28.
Post-rerun fact rows added: 0.
Duplicate key groups after rerun: 0.
Lineage preserved: True.
Canonical scope fingerprint: `8f109ec016108a3035981a8180cd991d`.

## Capability result

Before campaign, Demographics had useful total population, growth, broad age-share, dependency-ratio, fertility, life-expectancy, and urbanization-share coverage, but lacked sex-specific structure, births/deaths, mortality depth, urban/rural stocks, density context, education depth, health prevention/workforce/access, and forced migration stocks.

After campaign, those gaps are materially reduced for the WDI annual country-year scope. Remaining gaps are detailed age/sex pyramids, projections/scenarios, subnational demographics, cross-source demographic validation, and higher-resolution migration flows.

## Architecture result

The existing WDI annual-scalar path handled broader demographic indicator diversity and sparse-provider behavior without schema redesign. No provider mirror, generic demographic framework, partitioning, canonical identity change, or production scheduling is justified by observed evidence.

See JSON final report: `artifacts/reports/task-178-final-campaign-report.json`.
