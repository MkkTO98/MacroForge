# Active Goal

Project: MacroForge

## Current milestone

Milestone 3 is complete through TASK-045 OECD/Eurostat fixture-persistence hardening.

## Purpose

MacroForge exists to reduce the recurring effort required to build, maintain, validate, canonicalize, and use trusted macroeconomic data for investment-relevant research. Trusted databases/datasets are outputs; the project itself is the effort-reduction machine.

## Current objective

No implementation task is open. The post-freeze v1.1 architecture assessment is complete at `artifacts/reports/R-20260626-post-freeze-v11-architectural-assessment.md`; its single next implementation recommendation is `TASK-046 — Define and validate NormalizedObservationPackage v1 for existing WDI/OECD/Eurostat evidence`.

MacroForge is analytically v1-complete for current EIP needs unless a downstream consumer produces a concrete blocker. TASK-044 repaired WDI-only isolated smoke; TASK-045 made the bounded OECD/Eurostat fixture evidence unignored/commit-eligible for clean-clone reconstruction. No known operational pre-freeze blockers remain, but final v1 freeze should still run fresh full verification and include all commit-eligible fixture files.

Database-state review found canonicalization/review/comparability/eligibility semantics remain file-backed. PostgreSQL persistence should wait until eligibility semantics are deterministic and a downstream need is proven.

## Current defaults

- Evaluate work by recurring effort reduction across source onboarding/maintenance, validation, canonical mapping, schema evolution, downstream analysis, or agent recovery.
- Use isolated temporary PostgreSQL databases unless fresh dry-run and explicit approval allow otherwise.
- Preserve canonical-domain identities: structured periods, ISO3 country identity, explicit territory types, and provider codes as mappings/metadata.
- Treat PostgreSQL as accepted analytical store, not proof of truth by itself.
- Use `artifacts/manifests/canonical_assets.json` as the minimal file-backed canonicalization pointer registry.
- Keep MetaHarvest consultation advisory-only: no startup consultation, no routine-work retrieval, no automatic adoption, and no MacroForge authority.

## Latest evidence anchors

- TASK-038 lifecycle validation: `artifacts/reports/canonicalization-review-lifecycle-20260614.json` and `.md`
- TASK-039 deferred requirements: `artifacts/reports/canonicalization-deferred-mapping-advancement-requirements-20260618.json` and `.md`
- TASK-040 OECD basis split/status review: `artifacts/reports/canonicalization-oecd-unit-basis-comparability-20260618.json` and `.md`, plus `artifacts/reports/canonicalization-oecd-mapping-status-review-20260618.json` and `.md`
- TASK-041 research-readiness assessment: `artifacts/reports/R-20260619-comparability-research-readiness-assessment.md`
- TASK-042 GDP eligibility classification: `artifacts/reports/gdp-eligibility-classification-20260619.json` and `artifacts/reports/R-20260619-gdp-eligibility-classification-validation.md`
- Post-freeze v1.1 architecture assessment: `artifacts/reports/R-20260626-post-freeze-v11-architectural-assessment.md`
- TASK-043 MetaHarvest consultation: `artifacts/tasks/TASK-043-implement-trigger-gated-metaharvest-consultation.md` and `docs/architecture/metaharvest-trigger-gated-consultation.md`
- TASK-044 WDI smoke hardening: `artifacts/tasks/TASK-044-repair-wdi-isolated-smoke-workflow.md`
- TASK-045 fixture persistence: `artifacts/tasks/TASK-045-make-oecd-eurostat-fixtures-clean-clone-safe.md`
- Operational validation: `artifacts/reports/R-20260619-operational-capability-validation.md`
- Task chronology/recovery: `artifacts/tasks/backlog.md` and `artifacts/reports/_SUMMARY.md`

## Preserved boundaries

Recent review/canonicalization/consultation work did not call models for canonicalization, live-fetch data, add sources, add migrations, write to live/default `macro`, implement conversion/aggregation, integrate GDP reports, extract generalized frameworks, add provider-specific fact columns, auto-apply mappings, mutate accepted/base state, mutate `artifacts/manifests/canonical_assets.json`, create startup MetaHarvest behavior, or push to git.

Future work keeps those boundaries unless a new accepted task/decision explicitly changes them.
