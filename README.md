# MacroForge

MacroForge is a **ProjectForge-generated, AI-native macroeconomic and investing research platform** that focuses on reducing recurring effort for building, validating, and maintaining trusted macroeconomic observations.

MacroForge turns heterogeneous public economic evidence into deterministic, auditable workflows so that each new source contributes reusable operational knowledge (not just another dataset).

## What this repository is

- A live project generated and governed under ProjectForge.
- A long-lived infrastructure for deterministic source-specific ingestion and evidence-driven canonicalization.
- A project owned by its own state and decisions (`CONSTITUTION.md`, `state/*.md`, `artifacts/*`, `decisions/*`).

It is not a general-purpose data platform or orchestration platform. Its scope is narrowly bounded: deterministic acquisition → staging/validation → canonical observation artifacts with provenance.

## Current status

**Status:** Architecturally stable, evidence-validated v1.x posture.

- Governed by `CONSTITUTION.md` (v1.1).
- Source implementation is in **Domain Expansion Mode** (source-specific first, shared extraction only where repeated evidence supports it).
- **TASK-004 through TASK-066 are complete**.
- Most recent completed task: `TASK-066` (bounded Census housing construction evidence slice).

## What MacroForge currently covers

- Canonical-loaded path: `WDI`, `OECD_NAAG`, `EUROSTAT_NAMQ_GDP`.
- Bounded evidence-only slices include:
  - `BLS_CPI`
  - `BEA_NIPA`
  - `TREASURY_FISCAL_DATA`
  - `ECB_SDW`
  - `IMF_MFS_IR`
  - `BIS_CBPOL`
  - `ALFRED_GDP_VINTAGE`
  - `ILOSTAT_UNEMPLOYMENT`
  - `UN_COMTRADE_TRADE`
  - `WDI_DEMOGRAPHICS`
  - `EUROSTAT_INPUT_OUTPUT`
  - `IMF_BOP_FINANCIAL_ACCOUNT`
  - `EUROSTAT_ENERGY_BALANCE`
  - `FRED_YIELD_CURVE`
  - `CENSUS_HOUSING_CONSTRUCTION`

## Core implementation posture

MacroForge intentionally keeps architecture minimal and stable:

- Source-specific acquisition/parsing/mapping remains source-owned.
- Shared deterministic substrate handles observed ingestion packages, validation, lineage, and verification.
- `ObservedIngestionPackage` is the implementation boundary between source-specific pre-boundary work and shared post-boundary mechanics.
- PostgreSQL is the accepted analytical store; it is not proof of truth by itself.
- Operational logs are optional and support debugging; source evidence, tasks, decisions, and state are primary audit artifacts.

## Implemented foundation

- Raw SQL migrations under version control.
- Multi-schema PostgreSQL model (`meta`, `staging`, and `curated`).
- Source-specific loaders for the bounded implemented sources.
- Canonical-domain foundations for periods, provider/territory mappings, and domain-ready fact records.
- Combined-source deterministic validation and deterministic report smoke tests.

## Governance and change discipline

Potentially broad architectural changes are avoided until implementation evidence justifies extraction.

- No broad framework expansion or generalized orchestration without accepted architecture-level evidence.
- No generic live/default database auto-writes without explicit decision and verification evidence.
- Pushes and releases follow explicit continuity handoff and check discipline in this repository.

## For current status

Read first:

- `state/active_goal.md`
- `state/project_state.md`
- `state/architecture.md`
- `context/latest_handoff.md`
- `artifacts/tasks/backlog.md`

## Repository quality controls

Before reporting code, schema, governance, or state changes, run the relevant checks:

```bash
python3 tools/check_coherence.py --project .
python3 tools/context_health.py --project .
python3 tools/architecture_reality_audit.py --project .
uvx pytest -q
```

## References

- `AGENTS.md` (operating rules)
- `context/context_policy.yaml` (completion and context policy)
- `docs/architecture/overview.md` (architecture summary)
- `docs/architecture/observed-ingestion-representation.md` (boundary contract)
- `docs/architecture/domain-coverage-assessment.md` (coverage state)
- `artifacts/decisions/` (durable decisions)
- `artifacts/tasks/` (durable task and closeout records)
