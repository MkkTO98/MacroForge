# Active Goal

Project: MacroForge

## Current milestone

Milestone 3 — canonical-domain PostgreSQL substrate, deterministic canonicalization proposal workflow, WDI unit metadata enrichment, review lifecycle validation, deferred mapping advancement-requirements persistence, and OECD unit-basis comparability split are complete.

## Purpose

MacroForge exists to progressively reduce the recurring effort required to build, maintain, validate, canonicalize, and use trusted macroeconomic data for investment-relevant research. Trusted macroeconomic databases and datasets are outputs; the project itself is the effort-reduction machine.

## Current objective

TASK-040 is complete. It implemented the first TASK-039 OECD advancement requirement by separating OECD `USD_EXC` exchange-rate and `USD_PPP` PPP basis candidates in deterministic audit artifacts without advancing accepted mapping status. Future OECD GDP mapping advancement should start from `artifacts/reports/canonicalization-oecd-unit-basis-comparability-20260618.json`; Eurostat advancement should still start from `artifacts/reports/canonicalization-deferred-mapping-advancement-requirements-20260618.json` and satisfy its minimum conditions before changing mapping status, accepted/base state, manifests, or reports.

## V1 success

MacroForge v1 succeeds when one World Bank WDI vertical slice proves raw evidence, checksum, staging transform, idempotent PostgreSQL load, metadata, lineage, quality checks, validation, and an inspectable report.

## Current defaults

- Evaluate future work by asking which recurring effort it reduces: source onboarding, source maintenance, validation, canonical mapping, schema evolution, downstream analysis, or future agent recovery/context effort.
- Use isolated temporary PostgreSQL databases for smoke verification unless a fresh dry-run and explicit approval allow otherwise.
- Preserve canonical-domain identities: structured periods, ISO3 country identity, explicit territory types for aggregates, and provider period/territory codes as mappings/metadata rather than curated identities.
- Treat PostgreSQL as the accepted analytical store, not proof of truth by itself.
- Treat confidence scores as review-routing metadata, not truth.
- Use `artifacts/manifests/canonical_assets.json` as the minimal file-backed pointer registry for existing accepted/provisional canonicalization artifacts.

## Latest completed evidence

- TASK-038: `artifacts/tasks/TASK-038-simulate-bounded-canonicalization-review-lifecycle.md`
- TASK-038 lifecycle JSON: `artifacts/reports/canonicalization-review-lifecycle-20260614.json`
- TASK-038 lifecycle report: `artifacts/reports/canonicalization-review-lifecycle-20260614.md`
- TASK-039: `artifacts/tasks/TASK-039-persist-deferred-mapping-advancement-requirements.md`
- TASK-039 requirements JSON: `artifacts/reports/canonicalization-deferred-mapping-advancement-requirements-20260618.json`
- TASK-039 requirements report: `artifacts/reports/canonicalization-deferred-mapping-advancement-requirements-20260618.md`
- TASK-040: `artifacts/tasks/TASK-040-implement-oecd-unit-basis-comparability-split.md`
- TASK-040 OECD basis JSON: `artifacts/reports/canonicalization-oecd-unit-basis-comparability-20260618.json`
- TASK-040 OECD basis report: `artifacts/reports/canonicalization-oecd-unit-basis-comparability-20260618.md`

## Preserved boundaries

TASK-038 through TASK-040 did not call models, live-fetch data, add sources, add migrations, write to live/default `macro`, implement unit/currency conversion, aggregate frequencies, integrate GDP reports, extract generalized metadata/source frameworks, add provider-specific fact columns, auto-apply accepted mappings, mutate base accepted state, mutate `artifacts/manifests/canonical_assets.json`, or push to git.
