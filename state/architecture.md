# Architecture State

## Current architecture

MacroForge is a ProjectForge-managed data/research project governed by Strategic Constitution v1.1. Its strategic asset is reusable deterministic ingestion capability for transforming heterogeneous public economic evidence into canonical, auditable observations. PostgreSQL databases and datasets are outputs, not the primary asset.

The implementation currently combines source-specific WDI/OECD/Eurostat evidence paths, `ObservedIngestionPackage` v1 as a narrow shared handoff contract, a canonical-domain PostgreSQL substrate, deterministic file-backed canonicalization state/proposal mechanics, bounded review-lifecycle artifacts, and OECD unit-basis/status review evidence.

Trust requires source evidence, reproducibility evidence, lineage, quality checks, canonical mapping status, validation, replay/rerun paths, and human review for high-impact economic meaning.

## Current ingestion flow

```text
Source-specific acquisition
-> Source-specific normalization
-> ObservedIngestionPackage v1
-> Existing source-specific staging/canonical load SQL
-> Validation
-> Canonical PostgreSQL
```

## Strategic extraction doctrine

Shared deterministic infrastructure should progressively own post-observed-boundary mechanics only when evidence shows convergence. A repeated behavior becomes eligible for shared infrastructure only when the contract, algorithm, and implementation have converged. Textual similarity is insufficient.

Shared infrastructure must not depend on source-specific conditionals such as `if source == WDI`. Source-specific behavior belongs in adapters that produce the shared contract.

Before foundational capability extraction, increase ArchitectureHarvest consultation intensity to identify mature patterns, failure modes, blind spots, alternatives, and reasons not to extract. The active trigger is `foundational_capability_extraction`, applying when proposed implementation is expected to become a reusable dependency of multiple future capabilities.

## Current implementation state

MacroForge implementation is capability-complete through TASK-046 observed ingestion representation extraction. No open implementation task is active.

### Source-specific substrate

- WDI has raw evidence, loading, validation, isolated smoke checks repaired for the current canonical-domain schema state, first vertical-slice proof, and an `ObservedIngestionPackage` adapter.
- OECD/SDMX has recorded/live-smoke evidence, codelist/label metadata, staging observation support, loader behavior, bounded comparability artifacts, unignored bounded fixture files, and an `ObservedIngestionPackage` adapter.
- Eurostat `namq_10_gdp` has recorded fixture evidence, staging observation support, loader behavior, provider mappings/dictionaries, isolated load smoke evidence, unignored bounded fixture files, and an `ObservedIngestionPackage` adapter.
- Source-specific acquisition, parsing, source metadata, and staging remain source-specific.

### ObservedIngestionPackage v1

`ObservedIngestionPackage` v1 is documented in `docs/architecture/observed-ingestion-representation.md` and implemented in `src/macroforge/observed_ingestion.py`.

It is a public internal architectural contract extracted from current WDI/OECD/Eurostat behavior. It contains source identity, provider dataset identity, source-specific release key, raw evidence, input filters, row counts, and canonical-load-ready observations. It deliberately leaves source-specific acquisition, normalized artifacts, staging schemas, provider mappings, lineage, validation, canonicalization review, conversion/aggregation, and AI/model behavior outside the contract.

Changes to this representation should be treated as contract evolution requiring equivalence verification, not ordinary refactoring.

### Canonical-domain substrate

- Canonical periods are structured rather than provider-string identities.
- Country/territory identity preserves ISO3 and explicit territory types.
- Provider period/territory/code representations live in mappings/metadata rather than becoming curated identities.
- Source-agnostic curated facts exist, and combined-source canonical validation plus the first canonical GDP snapshot report are complete.
- PostgreSQL is the accepted analytical store, but database persistence alone is not treated as truth without evidence, lineage, checks, replayability, and review status.

### Canonicalization lifecycle

- DEC-018 accepts a minimal AI-assisted canonicalization/comparability design conceptually; implemented lifecycle mechanics remain deterministic and file-backed.
- The canonical asset manifest exists as a narrow file-backed pointer registry in `artifacts/manifests/canonical_assets.json`.
- WDI GDP evidence has a governed provisional lifecycle outcome; OECD and Eurostat GDP mappings remain deferred unless future review decisions explicitly advance them.

## Current architecture decisions

DEC-005 through DEC-021 remain as recorded. Strategic Constitution v1.1 now governs optimization. Governance is complete/frozen for v1.1; Deterministic Change Verification is Verified through isolated PostgreSQL end-to-end WDI/OECD/Eurostat package equivalence proof.

## Capability maturity

Lifecycle: Discovered -> Specified -> Verified -> Adopted -> Shared -> Stable -> Mature.

- Observed Boundary and Contract Stability: Specified. Target: Adopted, then Stable. Next transition: Specified -> Verified.
- Deterministic Change Verification: Verified. Target: Stable. Next transition: Verified -> Adopted.
- Contract Validation and Drift Detection: Discovered. Target: Verified. Next transition: Discovered -> Specified.
- Ingestion Diagnostics and Recovery Evidence: Discovered. Target: Verified. Next transition: Discovered -> Specified.
- Shared Post-Boundary Infrastructure Extraction: Discovered. Target: Verified readiness, not immediate Shared. Next transition: Discovered -> Specified after change-verification evidence and consultation.
- Canonicalization Governance and Mapping Advancement: Stable for file-backed lifecycle; Discovered/Specified for OECD/Eurostat advancement. Target: preserve Stable lifecycle; verify targeted advancement only when needed.
- Knowledge-Accumulating Source Expansion: Discovered. Target: Specified only after verification/diagnostics capabilities mature.

## Deferred areas

The following remain deferred unless a new accepted decision changes scope:

- new datasets or dataset deepening;
- production PostgreSQL persistence for canonicalization state;
- AI/model calls for canonicalization proposals;
- report integration of lifecycle-derived mappings;
- unit/currency conversion or frequency aggregation;
- generalized ingestion, plugin/source, metadata, orchestration, dbt/Dagster, Alembic, SQLAlchemy, Docker, or mart-layer expansion;
- direct mutation of accepted/base mapping state or canonical manifests without explicit review artifact approval.

## Next architecture work

No next architecture task is open. Governance is complete for v1.1 and frozen pending implementation-driven discoveries. The final freeze report is `artifacts/reports/R-20260627-final-governance-refinement-and-freeze.md`.

Recommended next transition: Deterministic Change Verification Verified -> Adopted. Do this by making the verified end-to-end path the required change-verification path for relevant ingestion/package changes; do not claim Shared until repeated implementation demonstrates extraction is justified and `foundational_capability_extraction` consultation has been performed if required.

Future architectural reports should only be produced when implementation uncovers uncertainty that cannot be resolved from the Constitution, capability graph, contracts, dependency graph, existing reports, or deterministic verification outputs.
