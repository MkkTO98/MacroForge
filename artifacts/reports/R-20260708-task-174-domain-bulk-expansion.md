# TASK-174 Domain Bulk Expansion Report

Status: succeeded
Date: 2026-07-08

## Before

- PostgreSQL curated fact rows: 140616
- PostgreSQL staging WDI rows: 140616
- Loaded source providers: WDI
- WDI indicators: 27
- WDI countries: 217
- WDI year coverage: 2000-2023

## After

- PostgreSQL curated fact rows: 392431
- PostgreSQL staging WDI rows: 418471
- Loaded source providers: WDI
- WDI indicators: 74
- WDI countries: 217
- WDI year coverage: 2000-2024

## Rows added

Exact curated fact rows added: 251815

Staging rows added: 277855

## Domains materially improved

- International Trade, Tourism, and Supply Chains: 27 included indicators, 146475 normalized campaign rows.
- Monetary, Banking, Credit, and Financial Intermediation: 25 included indicators, 131380 normalized campaign rows.

## Largest candidate universe considered

{
  "candidate_indicators": 55,
  "candidate_presparsity_rows": 298375,
  "countries": 217,
  "date_range": "2000:2024",
  "provider_path": "World Bank WDI public API v2 through existing WDI annual scalar observed-package and PostgreSQL loader path",
  "target_domains": [
    "International Trade, Tourism, and Supply Chains",
    "Monetary, Banking, Credit, and Financial Intermediation"
  ]
}

## Why anything was excluded

- `FB.BNK.CAR.ZS`: unsupported_representation; unsupported WDI response shape for FB.BNK.CAR.ZS
- `FB.BNK.LQRS.ZS`: unsupported_representation; unsupported WDI response shape for FB.BNK.LQRS.ZS
- `FB.BNK.ZSCORE`: unsupported_representation; unsupported WDI response shape for FB.BNK.ZSCORE

## Repository-growth evidence

- `artifacts/reports/task-174-domain-bulk-inventory-before.json`
- `artifacts/reports/task-174-domain-bulk-preflight-report.json`
- `artifacts/reports/task-174-domain-bulk-classification-report.json`
- `artifacts/reports/task-174-domain-bulk-operational-expansion-report.json`
- `artifacts/reports/task-174-domain-bulk-coverage-report.json`
- `artifacts/reports/task-174-domain-bulk-exclusion-report.json`
- `artifacts/reports/task-174-domain-bulk-load-report.json`
- `artifacts/reports/task-174-domain-bulk-final-report.json`

## Next largest safe campaign

Expand the same implemented-compatible WDI annual scalar path to additional Trade and Monetary/Financial WDI indicators not yet loaded, then separately evaluate UN Comtrade only after its current hard-coded USA-Japan product normalizer is generalized by evidence or a source-specific bulk normalizer is added.
