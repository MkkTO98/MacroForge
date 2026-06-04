# Folder Summary: artifacts/tasks

## Purpose
Durable task contracts, backlog, acceptance criteria, and current work status.

## Contains
<!-- PROJECTFORGE:BEGIN-CONTAINS -->
- `.gitkeep`
- `T-001-initial-validation.md`
- `TASK-001-rebuild-macroforge-scaffold-with-current-projectforge.md`
- `TASK-002-import-curated-reconstruction-context.md`
- `TASK-003-establish-source-of-truth-and-precedence-decisions.md`
- `TASK-004-recreate-v0-postgresql-schema-foundation.md`
- `TASK-005-recreate-narrow-wdi-extract-raw-evidence-slice.md`
- `TASK-006-implement-postgresql-loader-for-wdi-staging-curated-facts.md`
- `TASK-007-add-runbook-and-validation-reporting.md`
- `TASK-008-review-architecture-after-first-vertical-slice.md`
- `TASK-009-harden-wdi-vertical-slice-rerunnable-local-operation.md`
- `TASK-010-define-minimal-source-contract-for-second-source-spike.md`
- `TASK-011-spike-no-key-oecd-sdmx-style-second-source.md`
- `TASK-012-implement-oecd-sdmx-raw-evidence-normalization.md`
- `TASK-013-harden-oecd-sdmx-live-rerunnable-smoke-command.md`
- `TASK-014-design-oecd-sdmx-postgresql-promotion.md`
- `TASK-015-implement-oecd-sdmx-postgresql-loader.md`
- `TASK-016-review-architecture-after-second-source.md`
- `TASK-017-harden-shared-validation-and-loader-reporting.md`
- `TASK-018-decide-next-scope-after-shared-validation-reporting.md`
- `TASK-019-spike-oecd-sdmx-codelist-label-enrichment.md`
- `TASK-020-spike-third-no-key-source-eurostat-architecture-validation.md`
- `TASK-021-design-canonical-period-territory-provider-mapping-schema-evolution.md`
- `backlog.md`
<!-- PROJECTFORGE:END-CONTAINS -->

## Active Work
- TASK-001 through TASK-020 are complete.
- TASK-021 is open for canonical period, territory, and provider mapping schema design.

## Needs Attention
- Preserve DEC-010 boundaries: no executable migration, third-source PostgreSQL promotion, generalized source framework, or live `macro` write. Provider period/territory codes must remain mappings/metadata, not canonical curated identities.
