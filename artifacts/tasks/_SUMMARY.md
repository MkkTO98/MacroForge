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
- `TASK-047-select-first-foundational-extraction-candidate.md`
- `TASK-048-verify-canonical-lineage-event-generation.md`
- `TASK-049-specify-contract-validation-drift-detection.md`
- `TASK-050-verify-contract-validation-drift-detection.md`
- `TASK-051-bounded-bls-monthly-evidence-slice.md`
- `TASK-052-deterministic-ingestion-feedback.md`
- `TASK-053-bounded-bea-nipa-evidence-slice.md`
- `TASK-054-bounded-us-treasury-fiscal-data-evidence-slice.md`
- `TASK-PF-20260614-continuity-recovery-adoption.md`
- `backlog.md`
<!-- PROJECTFORGE:END-CONTAINS -->

## Active Work
- TASK-001 through TASK-054 are complete.
- `backlog.md` records Observed Boundary and Contract Stability, Deterministic Change Verification, Canonical Lineage Event Generation, Contract Validation and Drift Detection, and Deterministic Ingestion Feedback as Verified for current scopes.
- TASK-054 completed bounded U.S. Treasury Fiscal Data through `ObservedIngestionPackage` without contract evolution or substrate redesign, adding row-oriented government JSON/API metadata evidence.
- Future foundational shared infrastructure extraction should use the standardized checklist in `docs/architecture/capability-maturity-model.md`: contract/algorithm/implementation convergence, deterministic verification, consultation, acceptable coupling, and satisfied prerequisites.

## Needs Attention
- Observed Boundary and Contract Stability, Canonical Lineage Event Generation, Contract Validation and Drift Detection, and Deterministic Ingestion Feedback remain Verified; do not advance them beyond Verified without separate adoption tasks.
- TASK-054 is complete. Select TASK-055 only after reviewing TASK-054 lessons and optimizing for architectural learning per unit of implementation effort.
- Do not extract quality checks, provider metadata frameworks, canonical dimensions, canonical fact upserts, graph/catalog/runtime systems, recovery automation, or source frameworks without a new evidence threshold and consultation.
