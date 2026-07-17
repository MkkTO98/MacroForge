# TASK-180 — Capability Closure Assessment

Status: complete
Date: 2026-07-09

## Scope

Domain: Demographics, Human Capital, and Population Structure.
Capability: Detailed age-sex cohort structure / population-pyramid analysis.
Provider: World Bank WDI via existing annual-scalar confidence cell.
Period: 1990:2024.
Countries: 217.
Candidate WDI cohort indicators selected: 68.
Already loaded candidates before campaign: 0.
Remaining candidates fetched: 68.
Included indicators: 68.
Excluded indicators after provider preflight: 0.
Normalized rows: 516460.
Observed values: 516460.
Missing-value evidence rows: 0.

## PostgreSQL growth

Curated fact rows before: 861135.
Curated fact rows after first load: 1377595.
Curated fact rows added: 516460.
WDI indicators before: 114.
WDI indicators after: 182.
WDI indicators added: 68.
Post-rerun fact rows added: 0.
Duplicate key groups after rerun: 0.
Lineage preserved: True.
Canonical scope fingerprint: `4e008cfa8599c21b789c71e87ad35ccb`.

## Capability result

The Demographic Structure capability can now be considered operationally complete within the WDI annual-scalar confidence cell for national annual historical five-year female/male cohort counts and shares. This closes the TASK-179 population-pyramid/cohort-aging gap at WDI annual country-year granularity.

This does not complete projection scenarios, subnational cohorts, single-year full-age distributions, or cross-source validation.

## Provider boundary

WDI has been exhausted for the high-value five-year age-sex cohort closure target. Another provider is not justified for historical national annual five-year age-sex structure. UN Population Division becomes justified only for projection/scenario semantics, release/versioned future periods, or cross-source validation beyond WDI.

## Architecture result

The existing WDI annual-scalar path handled a large same-family demographic cohort campaign without schema redesign, provider mirror, generic demographic framework, canonical identity change, partitioning, or production scheduling.

See JSON final report: `artifacts/reports/task-180-final-campaign-report.json`.
