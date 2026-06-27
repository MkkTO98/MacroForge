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
- `TASK-022-implement-minimal-canonical-domain-schema-migration.md`
- `TASK-023-design-bounded-eurostat-postgresql-promotion.md`
- `TASK-024-implement-bounded-eurostat-postgresql-loader.md`
- `TASK-025-review-architecture-after-bounded-third-source-postgresql-promotion.md`
- `TASK-026-implement-combined-source-canonical-validation-smoke.md`
- `TASK-027-decide-next-scope-after-combined-source-canonical-validation-smoke.md`
- `TASK-028-implement-first-canonical-gdp-snapshot-report.md`
- `TASK-029-decide-next-scope-after-first-canonical-gdp-snapshot-report.md`
- `TASK-030-design-minimal-canonical-indicator-unit-comparability.md`
- `TASK-031-architecture-reality-remediation-hygiene.md`
- `TASK-032-implement-minimal-canonicalization-state-foundation.md`
- `TASK-033-decide-next-scope-after-canonicalization-state-foundation.md`
- `TASK-034-implement-tiny-deterministic-canonicalization-proposal-workflow.md`
- `TASK-035-implement-narrow-architectureharvest-canonical-asset-manifest.md`
- `TASK-036-decide-next-scope-after-deterministic-canonicalization-proposal-workflow.md`
- `TASK-037-implement-bounded-wdi-unit-metadata-enrichment-for-canonicalization-evidence.md`
- `TASK-038-simulate-bounded-canonicalization-review-lifecycle.md`
- `TASK-039-persist-deferred-mapping-advancement-requirements.md`
- `TASK-040-implement-oecd-unit-basis-comparability-split.md`
- `TASK-041-comparability-research-readiness-assessment.md`
- `TASK-042-gdp-eligibility-classification-artifact.md`
- `TASK-043-implement-trigger-gated-metaharvest-consultation.md`
- `TASK-044-repair-wdi-isolated-smoke-workflow.md`
- `TASK-045-make-oecd-eurostat-fixtures-clean-clone-safe.md`
- `TASK-046-extract-observed-common-ingestion-representation.md`
- `TASK-PF-20260614-continuity-recovery-adoption.md`
- `backlog.md`
<!-- PROJECTFORGE:END-CONTAINS -->

## Active Work
- TASK-001 through TASK-046 are complete.
- `backlog.md` now records Deterministic Change Verification as Verified after isolated PostgreSQL WDI/OECD/Eurostat package equivalence proof; next transition is Verified -> Adopted.
- Future shared infrastructure extraction should follow the Constitution sequence: discover repeated implementation, identify evidence, prove equivalence, extract shared contract, validate deterministically, then extract shared implementation.
- Governance is complete/frozen for v1.1. The active ArchitectureHarvest trigger for implementation expected to become a reusable dependency of multiple future capabilities is `foundational_capability_extraction`.

## Needs Attention
- Before advancing Deterministic Change Verification to Adopted, require the verified path to become the required change-verification path for relevant ingestion/package changes.
- Before foundational capability extraction, perform deep ArchitectureHarvest consultation using `foundational_capability_extraction`.
- Dataset expansion should remain behind reusable diagnostics/replay infrastructure unless a concrete downstream blocker justifies earlier work.
