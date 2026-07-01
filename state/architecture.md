# Architecture State

## Current architecture

MacroForge is governed by Strategic Constitution v1.1. Its strategic asset is reusable deterministic ingestion capability for transforming heterogeneous public economic evidence into canonical, auditable observations.

Current ingestion architecture:

```text
Source-specific acquisition
-> Source-specific normalization
-> ObservedIngestionPackage v1
-> Deterministic post-boundary substrate
-> Existing source-specific staging/canonical load SQL where scoped
-> Validation
-> Canonical PostgreSQL where scoped
```

## Strategic extraction doctrine

Shared deterministic infrastructure should own post-observed-boundary mechanics only when multiple independent implementations demonstrate contract convergence, algorithm convergence, implementation convergence, deterministic verification, acceptable coupling, and measurable future implementation-effort reduction.

Source-specific behavior belongs before the boundary. Generic shared infrastructure must not contain source-specific conditionals.

After TASK-053 and DEC-022, the default assumption is that the current post-boundary architecture is correct. Future implementation should attempt to falsify this assumption through bounded heterogeneous sources, not proactively redesign the substrate or observed boundary.

DEC-023 and `docs/architecture/long-term-domain-vision.md` record MacroForge's accepted long-term world-economy observation-domain direction as non-binding scope clarification only. MacroForge owns source-backed observations, provenance, reproducibility, lineage, validation, and observational identity. KnowledgeForge owns reusable meaning, semantic identities, claims, hypotheses, relationship interpretation, evidence evaluation, confidence, uncertainty, contradictions, and epistemic state.

## Source implementation posture

Canonical-loaded paths:

- WDI.
- OECD_NAAG.
- EUROSTAT_NAMQ_GDP.

Bounded evidence-only slices:

- BLS_CPI.
- BEA_NIPA.
- TREASURY_FISCAL_DATA.
- ECB_SDW.
- IMF_MFS_IR.
- BIS_CBPOL.
- ALFRED_GDP_VINTAGE.
- ILOSTAT_UNEMPLOYMENT.
- UN_COMTRADE_TRADE.
- WDI_DEMOGRAPHICS.
- EUROSTAT_INPUT_OUTPUT.
- IMF_BOP_FINANCIAL_ACCOUNT.
- EUROSTAT_ENERGY_BALANCE.
- FRED_YIELD_CURVE.

Evidence-only slices do not imply broad provider support, canonical loading, generic source frameworks, provider metadata frameworks, or domain frameworks.

## Observed boundary and deterministic substrate

`ObservedIngestionPackage` is documented in `docs/architecture/observed-ingestion-representation.md` and implemented in `src/macroforge/observed_ingestion.py`.

Recent bounded sources through TASK-065 confirmed that heterogeneous shapes fit the existing contract through provider fields, attributes, raw evidence, and source payload without additive contract evolution.

Current post-boundary components remain unchanged:

- package fingerprinting/comparison;
- Deterministic Change Verification;
- Canonical Lineage Event Generation;
- Contract Validation and Drift Detection;
- Deterministic Ingestion Feedback.

Post-boundary substrate effort is currently low. Source acquisition, provider interpretation, and normalization remain the main effort centers.

## Capability maturity

Lifecycle: Discovered -> Specified -> Verified -> Adopted -> Shared -> Stable -> Mature.

- Observed Boundary and Contract Stability: Verified.
- Deterministic Change Verification: Verified.
- Canonical Lineage Event Generation: Verified.
- Contract Validation and Drift Detection: Verified.
- Deterministic Ingestion Feedback: Verified for current v1.1 scope.
- Shared Post-Boundary Infrastructure Extraction: Discovered.
- Evidence-Accumulating Source Expansion: Specified through TASK-065.

## Current architectural observation

The five-source retrospective baseline remains valid: continue heterogeneous source implementation without architectural change; no extraction is currently justified; marginal effort is decreasing or stable while effort remains concentrated before the observed boundary.

TASK-059 through TASK-065 expanded labor, trade, demographics, input-output, financial-flow, energy, and financial-market curve evidence. They confirmed normal Domain Expansion behavior: no observed-boundary, deterministic-substrate, lineage, replay, or validation pressure. No architectural action is recommended.

## Methodology evidence artifacts

- `docs/architecture/domain-coverage-assessment.md` tracks lightweight long-term domain coverage state.
- `docs/architecture/architectural-confidence-ledger.md` tracks assumptions, confidence, and prediction quality.
- `docs/architecture/architectural-surprise-log.md` tracks material prediction mismatches.
- `docs/architecture/marginal-source-cost-index.md` tracks implementation-cost trends.
- `docs/architecture/recurring-implementation-pain.md` tracks repeated implementation difficulties.
- `docs/architecture/long-term-domain-vision.md` records accepted non-binding long-term domain scope and the MacroForge/KnowledgeForge boundary.

## Deferred areas

Unless a new accepted task or decision changes scope, defer: broad source support, source frameworks, provider metadata frameworks, runtime orchestration, recovery automation, graph/catalog systems, semantic economic validation, conversion/aggregation, AI/model canonicalization, live production writes, generic revision infrastructure, generic SDMX infrastructure, generic labor/trade/demographic/input-output/financial-flow/energy/market-data infrastructure, and canonical loading for evidence-only slices.
