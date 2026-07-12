# TASK-213 BIS CBPOL processed artifacts

Processed artifacts for TASK-213 BIS WS_CBPOL monthly central-bank policy-rate Phase 2 campaign.

Contents:

- `active/task-213-bis-cbpol-policy-rate-normalized.json`: corrected normalized candidate grid with 5,106 cells, 5,082 provider-valued facts, 24 explicit missing cells represented for PostgreSQL as `observation_status='missing'`, 37 accepted territories including HK/HKG, and one canonical source-scoped policy-rate indicator independent of territory.
- `active/task-213-bis-cbpol-policy-rate-manifest.json`: candidate, source/dataset/run, and checksum summary.

Scope: source-specific WS_CBPOL policy-rate capability. This directory is not a generic BIS/SDMX normalized store.
