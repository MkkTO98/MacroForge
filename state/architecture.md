# Architecture State

## Current architecture

MacroForge is governed by Strategic Constitution v1.1. Its strategic asset is reusable deterministic ingestion capability for transforming heterogeneous public economic evidence into canonical, auditable observations.

The current ingestion architecture remains:

```text
Source-specific acquisition
-> Source-specific normalization
-> ObservedIngestionPackage v1
-> Deterministic post-boundary substrate
-> Existing source-specific staging/canonical load SQL where scoped
-> Validation
-> Canonical PostgreSQL where scoped
```

BLS_CPI, BEA_NIPA, TREASURY_FISCAL_DATA, and ECB_SDW are bounded evidence slices only. They do not imply broad provider support or canonical loading.

## Strategic extraction doctrine

Shared deterministic infrastructure should own post-observed-boundary mechanics only when multiple independent implementations demonstrate contract convergence, algorithm convergence, implementation convergence, deterministic verification, acceptable coupling, and measurable future implementation-effort reduction. Source-specific behavior belongs before the boundary. Generic shared infrastructure must not contain source-specific conditionals.

After TASK-053, the default assumption is that the current post-boundary architecture is correct. Future implementation should attempt to falsify this assumption through bounded heterogeneous sources, not proactively redesign the substrate or observed boundary.

## Current implementation state

TASK-004 through TASK-055 are complete.

Source evidence currently includes:

- WDI: source-specific evidence/loading/validation and `ObservedIngestionPackage` adapter.
- OECD_NAAG: SDMX evidence/loading/validation and `ObservedIngestionPackage` adapter.
- EUROSTAT_NAMQ_GDP: fixture evidence/loading/validation and `ObservedIngestionPackage` adapter.
- BLS_CPI: bounded monthly evidence slice with no canonical loader or broad BLS support.
- BEA_NIPA: bounded TASK-053 table/line-code evidence slice with no canonical loader or broad BEA support.
- TREASURY_FISCAL_DATA: bounded TASK-054 row-oriented government JSON API evidence slice with no canonical loader or broad Treasury support.
- ECB_SDW: bounded TASK-055 monthly EUR/USD exchange-rate SDMX evidence slice with no canonical loader, broad ECB support, or SDMX Interpretation Layer.

## ObservedIngestionPackage v1

`ObservedIngestionPackage` is documented in `docs/architecture/observed-ingestion-representation.md` and implemented in `src/macroforge/observed_ingestion.py`. It contains source identity, provider dataset identity, release key, raw evidence, input filters, row counts, and observations.

TASK-053 confirmed BEA NIPA table/line identity, quarterly periods, USA territory, release description, and table metadata fit the existing contract through provider indicator fields, attributes, raw evidence, and release key. No additive contract evolution was required.

## Deterministic ingestion substrate

Current post-boundary components:

- package fingerprinting/comparison;
- Deterministic Change Verification;
- Canonical Lineage Event Generation;
- Contract Validation and Drift Detection;
- Deterministic Ingestion Feedback.

TASK-053 did not change any of these. The BEA evidence slice reinforces that post-boundary substrate effort is currently low, while source acquisition, provider interpretation, and normalization remain the main effort centers.

## Capability maturity

Lifecycle: Discovered -> Specified -> Verified -> Adopted -> Shared -> Stable -> Mature.

- Observed Boundary and Contract Stability: Verified.
- Deterministic Change Verification: Verified.
- Canonical Lineage Event Generation: Verified.
- Contract Validation and Drift Detection: Verified.
- Deterministic Ingestion Feedback: Verified for current v1.1 scope.
- Shared Post-Boundary Infrastructure Extraction: Discovered.
- Evidence-Accumulating Source Expansion: Specified through TASK-055.

## Architectural observation after TASK-053

Repeated implementation evidence did not justify architectural evolution.

TASK-053 produced new pre-boundary evidence: table/line-code normalization, interactive-table header interpretation, row-stub identity construction, release-description capture, and provider table metadata preservation. This is useful evidence, not yet a repeated pattern that justifies shared infrastructure.

No new post-boundary capability emerged. The correct action is to preserve the current architecture and continue implementation-driven evidence accumulation through bounded heterogeneous sources.

After every heterogeneous source implementation, record a short `Implementation Lessons` artifact covering confirmed predictions, incorrect predictions, unexpected difficulties, reusable implementation patterns, and future prediction changes.

Future technical debt only: if three consecutive heterogeneous source implementations complete without meaningful post-boundary architectural evolution, perform one bounded Deterministic Ingestion Substrate Stability Review. Do not perform that review now.

## Next source selection

TASK-054 implemented a bounded U.S. Treasury Fiscal Data API average-interest-rates evidence slice. It taught MacroForge about row-oriented government JSON, deterministic API query provenance, endpoint metadata preservation, bounded pagination metadata, and categorical row identity while requiring no observed-boundary or substrate evolution.

TASK-055 is implemented and verified. Its objective was an architectural experiment using bounded ECB SDW evidence to test whether SDMX is becoming an architectural boundary or remains an acquisition protocol whose commonality ends before `ObservedIngestionPackage`. The result strengthens the current observed-boundary and source-specific-first posture while recording future extraction evidence around repeated SDMX GenericData mechanics. Architectural confidence assumptions are tracked in `docs/architecture/architectural-confidence-ledger.md`; material prediction mismatches are tracked in `docs/architecture/architectural-surprise-log.md`.

The implementation methodology is frozen and treated as stable infrastructure until repeated implementation evidence demonstrates measurable improvement under the same standard as architectural extraction. Future heterogeneous implementations should follow the default loop: select source, predict, implement, verify, implementation lessons, surprise log, confidence calibration with Prediction Quality, marginal source cost update, recurring pain update, then continue. After every five heterogeneous source implementations, perform exactly one bounded Retrospective Review decision gate: answer whether to continue source implementation without architectural change, whether exactly one hypothesis justifies extraction, and whether engineering/human/LLM marginal effort decreased. No redesign, new capability systems, roadmap, speculative architecture, framework-first proposals, or methodology tweaks for elegance/consistency/theory are allowed.

## Methodology evidence artifacts

- `docs/architecture/marginal-source-cost-index.md` tracks approximate engineering, human, LLM reasoning, and architectural-confidence estimates for trend detection.
- `docs/architecture/recurring-implementation-pain.md` tracks repeated source-implementation difficulties; repeated pain, not repeated code, is the primary evidence for future extraction candidates.

## Deferred areas

Unless a new accepted task or decision changes scope, defer: broad source support, source frameworks, provider metadata frameworks, runtime orchestration, recovery automation, graph/catalog systems, semantic economic validation, conversion/aggregation, AI/model canonicalization, live production writes, and canonical loading for BLS_CPI, BEA_NIPA, the bounded Treasury evidence slice, or the bounded ECB SDW evidence slice.
