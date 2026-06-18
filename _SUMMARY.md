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
- TASK-001 through TASK-039 are complete. Doctrine-only alignment states that MacroForge exists to progressively reduce recurring effort required to build, maintain, validate, canonicalize, and use trusted macroeconomic data for investment-relevant research.
- TASK-038 validated the proposal -> review -> accepted/provisional canonicalization lifecycle in bounded file-backed form: WDI reached governed provisional status, while OECD and Eurostat were deferred with explicit caveats.
- TASK-039 persisted concrete OECD/Eurostat deferred mapping advancement requirements in JSON/Markdown artifacts without code/schema/source/base-state/manifest/report changes.

## Needs Attention
- Evaluate future work by asking which recurring effort it reduces: source onboarding, source maintenance, validation, canonical mapping, schema evolution, downstream analysis, or future agent recovery/context effort.
- No implementation task is open. Before any future OECD/Eurostat mapping advancement, start from `artifacts/reports/canonicalization-deferred-mapping-advancement-requirements-20260618.json` and preserve current boundaries unless a new accepted decision changes them: no model calls, live fetches, new sources, migrations, live `macro` writes, unit/currency conversion, frequency aggregation, report integration, accepted-state auto-apply, direct lifecycle/base-state mutation, or git push without explicit approval.
