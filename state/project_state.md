# Project State

Project: MacroForge
Template: python_data_project
Canonical path: `/home/mkkto/srv/EIP/projects/MacroForge`
Last updated: 2026-07-01

## Current state

MacroForge is governed by Strategic Constitution v1.1. Its strategic asset is reusable deterministic ingestion capability for transforming heterogeneous public economic evidence into canonical, auditable observations. PostgreSQL databases and datasets are outputs of that capability, not sources of truth by themselves.

TASK-004 through TASK-065 are complete. Recent work contains completed bounded source slices and governance artifacts for TASK-056 through TASK-065. Preserve those artifacts; they are the durable evidence trail.

## Source coverage summary

Canonical-loaded paths:

- WDI.
- OECD_NAAG.
- EUROSTAT_NAMQ_GDP.

Bounded evidence-only slices with no broad provider support or canonical PostgreSQL loaders:

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

## Current capability summary

- `ObservedIngestionPackage` is the public internal handoff boundary after source-specific acquisition and normalization.
- Deterministic post-boundary mechanics include package fingerprinting/comparison, Deterministic Change Verification, Canonical Lineage Event Generation, Contract Validation and Drift Detection, and Deterministic Ingestion Feedback.
- DEC-022 records the next-ten-source optimization target, Implementation Lessons requirement, evidence-gated extraction rule, and stability-review technical debt.
- DEC-023 records the accepted long-term world-economy observation-domain direction as non-binding scope clarification, not implementation authorization.
- `docs/architecture/domain-coverage-assessment.md` tracks compact domain coverage state.

## Current governance posture

- Evidence-Accumulating Source Expansion remains the active phase.
- TASK-059 through TASK-065 expanded labor, trade, demographics, input-output, financial-flow, energy, and financial-market curve coverage without architecture evolution.
- Decision gate: no architectural action is currently recommended; continue bounded Domain Expansion Mode unless implementation evidence triggers an exception.
- Architecture reviews should remain exception-triggered by repeated implementation surprises, extraction-threshold evidence, fundamentally new source-family uncertainty, or contradiction of current architectural beliefs.
- Methodology is stable infrastructure. Changes require extraction-grade repeated implementation evidence and measurable improvement, not elegance, consistency, or theory.
- Do not push without explicit approval.

## Durable recovery anchors

- Constitution: `CONSTITUTION.md`
- Active goal: `state/active_goal.md`
- Architecture state: `state/architecture.md`
- Latest handoff: `context/latest_handoff.md`
- Backlog/task chronology: `artifacts/tasks/backlog.md`
- DEC-022: `artifacts/decisions/DEC-022-next-ten-source-expansion-optimization.md`
- DEC-023: `artifacts/decisions/DEC-023-long-term-domain-vision-and-knowledgeforge-boundary.md`
- Observed package contract: `docs/architecture/observed-ingestion-representation.md`
- Domain coverage: `docs/architecture/domain-coverage-assessment.md`
- Confidence ledger: `docs/architecture/architectural-confidence-ledger.md`
- Surprise log: `docs/architecture/architectural-surprise-log.md`
- Marginal source cost index: `docs/architecture/marginal-source-cost-index.md`
- Recurring implementation pain: `docs/architecture/recurring-implementation-pain.md`

## Historical detail location

Implementation histories, row counts, fixture hashes, prediction reviews, verification outputs, and source-specific lessons belong in task/report/domain artifacts, not in primary state:

- TASK artifacts: `artifacts/tasks/`
- Implementation lessons: `artifacts/reports/L-*.md`
- Architecture/audit reports: `artifacts/reports/R-*.md`
- Folder summaries: `_SUMMARY.md` files
