# Folder Summary: data/raw/treasury

## Purpose
Bounded U.S. Treasury Fiscal Data raw fixture evidence for TASK-054.

## Contains
<!-- PROJECTFORGE:BEGIN-CONTAINS -->
- `treasury-avg-interest-rates-2026-05-31-raw.json`
<!-- PROJECTFORGE:END-CONTAINS -->

## Active Work
- `treasury-avg-interest-rates-2026-05-31-raw.json` is the bounded TASK-054 public Fiscal Data API fixture for endpoint `avg_interest_rates`, fields `record_date,security_desc,avg_interest_rate_amt`, filter `record_date:eq:2026-05-31`, sorted by `security_desc`, with 16 records.
- Fixture SHA-256: `3433749c3d4ec6ca35fbd0091752583e1f55cc70a9ca40bbd06b17106a0f4fec`.

## Needs Attention
- This is bounded evidence only, not broad Treasury Fiscal Data support.
- Do not add live fetch, generalized acquisition, pagination framework, canonical loading, or production writes without a new accepted task.
