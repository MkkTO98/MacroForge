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
- `CONSTITUTION.md` contains MacroForge Strategic Constitution v1.1: optimize for decreasing marginal cost of trustworthy economic-data ingestion while preserving determinism, auditability, provenance, and canonical consistency.
- TASK-054 is implemented and verified. `artifacts/reports/L-20260628-task-054-implementation-lessons.md` records the one durable implementation lesson and confirms the previous estimation model remains valid.
- DEC-022 accepts the next-ten-source optimization target: make future heterogeneous trustworthy source implementations progressively cheaper and assume the current post-boundary architecture is correct unless repeated implementation evidence falsifies it.
- `artifacts/reports/R-20260627-deterministic-ingestion-substrate-effort-assessment.md` records that the Deterministic Ingestion Substrate is already measurably reducing future post-boundary engineering/human/LLM effort, but source-specific acquisition/parsing/SQL/mapping remain substantial and should not be extracted yet.
- TASK-050 completed Contract Validation and Drift Detection Specified -> Verified by validating expected and reconstructed WDI/OECD/Eurostat package contracts inside the deterministic verification path.
- TASK-049 completed Contract Validation and Drift Detection Discovered -> Specified through narrow deterministic `ObservedIngestionPackage` invariant checks.
- `artifacts/reports/R-20260627-deterministic-ingestion-substrate-emergence-assessment.md` recognizes an emerging Deterministic Ingestion Substrate architectural layer after `ObservedIngestionPackage`; this is not a new framework and did not change capability maturity.
- `artifacts/reports/R-20260627-deterministic-ingestion-substrate-execution-model.md` documents the substrate's canonical execution order, capability interfaces, extension points, and low-priority state/history technical debt.
- TASK-048 completed Canonical Lineage Event Generation Specified -> Verified through narrow behavior-preserving extraction and final closeout verification.
- Evidence-based consistency review promoted Observed Boundary and Contract Stability from Specified to Verified without production implementation.
- Governance is complete for v1.1 and frozen pending implementation-driven discoveries; final freeze report is `artifacts/reports/R-20260627-final-governance-refinement-and-freeze.md`.
- `docs/architecture/capability-maturity-model.md` is the active implementation-planning model: Discovered -> Specified -> Verified -> Adopted -> Shared -> Stable -> Mature, with lightweight Verified prerequisites, evidence-based maturity interpretation, and the standard foundational extraction checklist.
- MacroForge remains in implementation-driven development; Observed Boundary and Contract Stability, Deterministic Change Verification, Canonical Lineage Event Generation, Contract Validation and Drift Detection, and Deterministic Ingestion Feedback are Verified.

## Needs Attention
- Evaluate every proposed implementation task by whether it permanently reduces future deterministic engineering, human effort, or LLM reasoning for trustworthy economic datasets.
- Extract shared infrastructure only after contract, algorithm, and implementation converge from evidence. Shared infrastructure must not contain source-specific conditionals; source-specific behavior belongs in adapters.
- TASK-054 is implemented and verified: bounded U.S. Treasury Fiscal Data average-interest-rates evidence slice through `ObservedIngestionPackage`; substrate evolution remains reactive to implementation evidence, not designed ahead of it.
