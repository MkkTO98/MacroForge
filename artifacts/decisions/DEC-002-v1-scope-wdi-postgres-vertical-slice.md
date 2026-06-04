# DEC-002 — V1 Scope: WDI/PostgreSQL Vertical Slice

Status: Accepted
Date: 2026-06-02

## Decision

V1 scope is one real macroeconomic data vertical slice using World Bank WDI as the first source and PostgreSQL as the authoritative analytical store.

## Accepted defaults

- First source: World Bank WDI.
- Default DB name: `macro`, unless live verification proves otherwise.
- Raw evidence and checksums are required.
- Staging and curated tables are required.
- Metadata, lineage, quality checks, and an inspectable report are required.

## Non-goals

- AI research briefs before data reliability.
- Many providers before WDI is proven.
- Paid/credentialed APIs in v1.
- Docker/cloud/public deployment dependency.
- Airflow/Dagster/Prefect before multiple stable manual pipelines exist.
