# Architecture State

## Current architecture

MacroForge is a ProjectForge-managed data/research project whose governing purpose is to progressively reduce the recurring effort required to build, maintain, validate, canonicalize, and use trusted macroeconomic data for investment-relevant research. The project OS is file-backed and summary-first. The domain platform begins with a WDI-to-PostgreSQL vertical slice and has grown through bounded source-specific WDI, OECD/SDMX, and Eurostat slices into a canonical-domain PostgreSQL substrate plus fixture-backed canonicalization state, deterministic proposal workflow, a tiny file-backed canonical asset manifest registry, post-workflow next-scope governance, and bounded WDI unit metadata enrichment.

Trusted macroeconomic databases and datasets are outputs of MacroForge. The effort-reduction system is the project. PostgreSQL stores accepted analytical data, but trust also requires source evidence, reproducibility evidence, lineage, quality checks, canonical mapping status, validation, replay/rerun paths, and human review for high-impact economic meaning.

## Target v1 flow

WDI source payload -> immutable raw artifact + checksum -> staging observation rows -> curated dimensions/facts -> lineage/quality checks -> query/report output.

## Database schemas

TASK-004 created the first raw SQL migration for:

- `meta`
- `staging`
- `curated`

`mart` remains documented for later analytical/reporting use.

## Current implementation status

Schema foundation, WDI raw evidence normalization, PostgreSQL load, validation reporting, isolated rerun hardening, minimal source contract, OECD/SDMX evidence/loader path, bounded Eurostat evidence/loader path, canonical-domain period/territory/provider mapping migration, combined-source canonical validation smoke, first canonical GDP snapshot report, minimal canonicalization state foundation, post-foundation next-scope governance, narrow MetaHarvest compatibility canonical asset manifest integration, tiny deterministic canonicalization proposal workflow, post-workflow next-scope governance, bounded WDI unit metadata enrichment, and bounded review-to-accepted/provisional lifecycle validation, and deferred mapping advancement-requirements persistence are complete.

TASK-030 completed the governance/design step for canonical indicator/unit comparability. DEC-018 accepts a minimal AI-assisted canonicalization layer design that treats provider indicators as evidence, automated output as auditable proposals, accepted/provisional mapping state as the gate to curated facts/reports, and confidence as review-routing metadata rather than truth.

TASK-032 implemented the first fixture-backed canonicalization state foundation in `src/macroforge/canonicalization_state.py`, with tests in `tests/test_canonicalization_state.py` and audit output in `artifacts/reports/canonicalization-state-foundation-20260605.json`. It is file-backed/deterministic and does not yet add PostgreSQL schema persistence.

TASK-033 completed DEC-019, selecting a tiny deterministic proposal-generation workflow as the next uncertainty-reduction step before AI/model dependence, PostgreSQL persistence, richer state expansion, report integration, or new sources.

TASK-035 completed DEC-020 and implemented `MF-AH-REV-001` narrowly as `artifacts/manifests/canonical_assets.json`. The registry is file-backed JSON, seeded only from existing artifacts, and does not adopt dbt, Dagster, orchestration runtime behavior, generalized ingestion framework behavior, database migrations, or raw loader changes.

TASK-034 implemented the DEC-019 deterministic workflow loop over existing TASK-032 state. `src/macroforge/canonicalization_state.py` generates TASK-034 workflow proposals and mapping update proposals from provider evidence, writes `artifacts/reports/canonicalization-proposal-workflow-20260613.json`, routes all high-impact GDP mappings to review, propagates unit/frequency caveats, preserves annual/quarterly non-aggregation, and avoids accepted-state mutation or auto-apply behavior.

TASK-036 completed DEC-021, selecting bounded WDI unit metadata enrichment as the next uncertainty-reduction step because TASK-034 proved workflow mechanics while exposing WDI `unknown_unit_metadata` as the sharpest remaining blocker.

TASK-037 implemented DEC-021 narrowly. `src/macroforge/canonicalization_state.py` now has a WDI-specific fixture-backed enrichment path for existing `NY.GDP.MKTP.CD` evidence. The enriched WDI unit profile remains evidence metadata, not canonical truth: it marks current USD metadata evidence, keeps `conversion_status: deferred`, keeps `comparable_without_conversion: false`, preserves proposal/accepted-state separation, and leaves non-WDI profiles unchanged. The bounded audit artifact is `artifacts/reports/canonicalization-wdi-unit-metadata-enrichment-20260613.json`.

TASK-038 validated the DEC-018 proposal -> review -> accepted/provisional lifecycle in bounded file-backed form without source/code/schema/runtime changes. `artifacts/reports/canonicalization-review-lifecycle-20260614.json` records explicit review decisions, check gates, state deltas, manifest deltas, lineage edges, and replay inputs for existing WDI/OECD/Eurostat GDP evidence. WDI reached a governed provisional outcome after explicit review; OECD and Eurostat remain deferred because unit basis, currency, and frequency caveats remain material. TASK-039 persisted those OECD/Eurostat advancement requirements in `artifacts/reports/canonicalization-deferred-mapping-advancement-requirements-20260618.json` without mutating base accepted mapping state or `artifacts/manifests/canonical_assets.json`.

## Current architecture decisions

DEC-005 keeps the immediate architecture intentionally minimal: raw SQL migrations, PostgreSQL, psql/Python loaders, CLI runbooks, and tests. Alembic, SQLAlchemy, orchestration platforms, Docker, and broad source frameworks are deferred until real schema evolution, multiple manual source pipelines, or repeated non-semantic duplication prove that abstraction would reduce recurring effort without weakening trust.

DEC-006 through DEC-021 remain as previously recorded. TASK-037 completed the DEC-021 bounded WDI unit metadata enrichment implementation without changing accepted canonical mappings or source/database architecture. TASK-038 validated the DEC-018 lifecycle as file-backed deltas and replay evidence only; no new decision accepts production application, persistence, AI/model use, report integration, or direct manifest/base-state mutation.

## Next architecture work

No next architecture task is open. Any future task that attempts to advance OECD or Eurostat GDP mapping status must start from `artifacts/reports/canonicalization-deferred-mapping-advancement-requirements-20260618.json` and preserve boundaries unless a new accepted decision changes them: no production state mutation, model calls, migrations, report integration, conversion/aggregation, new sources, generalized framework extraction, or git push without explicit approval.
