# Folder Summary: .

## Purpose
This folder is the relocated MacroForge project root at `/home/mkkto/srv/EIP/projects/MacroForge`, retaining ProjectForge-generated operating-system conventions.

## Contains
<!-- PROJECTFORGE:BEGIN-CONTAINS -->
- `.gitignore`
- `.gitkeep`
- `AGENTS.md`
- `CONSTITUTION.md`
- `README.md`
- `agents/`
- `architecture/`
- `artifacts/`
- `confidence/`
- `config/`
- `context/`
- `data/`
- `db/`
- `docs/`
- `hardware/`
- `instructions/`
- `knowledge/`
- `logs/`
- `memory/`
- `metrics/`
- `models/`
- `permissions/`
- `pipelines/`
- `policies/`
- `project.yaml`
- `pyproject.toml`
- `question_queue/`
- `recovery/`
- `simulation/`
- `skills/`
- `src/`
- `state/`
- `tests/`
- `tools/`
- `uv.lock`
- `workspace_config.yaml`
<!-- PROJECTFORGE:END-CONTAINS -->

## Active Work
- `CONSTITUTION.md` now contains MacroForge Strategic Constitution v1.1: optimize for decreasing marginal cost of trustworthy economic-data ingestion while preserving determinism, auditability, provenance, and canonical consistency.
- TASK-046 is complete and extracted `ObservedIngestionPackage` v1 from current WDI/OECD/Eurostat behavior.
- Governance is complete for v1.1 and frozen pending implementation-driven discoveries; final freeze report is `artifacts/reports/R-20260627-final-governance-refinement-and-freeze.md`.
- `docs/architecture/capability-maturity-model.md` is the active implementation-planning model: Discovered -> Specified -> Verified -> Adopted -> Shared -> Stable -> Mature.
- MacroForge has entered implementation-driven development; Deterministic Change Verification is Verified via isolated PostgreSQL WDI/OECD/Eurostat package equivalence proof.

## Needs Attention
- Evaluate future work by reduction in future deterministic engineering, human effort, LLM reasoning, future uncertainty; increase in confidence; knowledge accumulated; architectural leverage; complexity; and maintenance burden.
- Extract shared infrastructure only after contract, algorithm, and implementation converge from evidence. Shared infrastructure must not contain source-specific conditionals; source-specific behavior belongs in adapters.
- Before foundational capability extraction, use the active `foundational_capability_extraction` trigger for deep ArchitectureHarvest consultation. Routine implementation and diagnostic-only replay continue using bounded consultation policy.
