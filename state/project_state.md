# Project State

Project: MacroForge
Template: python_data_project
Canonical path: `/home/mkkto/srv/EIP/projects/MacroForge`
Last updated UTC: 2026-06-26T18:39:14Z

## Current state

MacroForge is a ProjectForge-generated autonomous EIP project and AI-first macroeconomic/investing research platform. Its purpose is to reduce recurring effort required to build, maintain, validate, canonicalize, and use trusted macroeconomic data for investment-relevant research. Trusted databases/datasets are outputs; the effort-reduction system is the project.

TASK-004 through TASK-045 are complete. MacroForge has source-specific WDI/OECD/Eurostat GDP evidence paths, a canonical-domain PostgreSQL foundation, deterministic file-backed canonicalization/proposal/review evidence, GDP eligibility classification, trigger-gated advisory-only MetaHarvest consultation, repaired WDI isolated smoke, and clean-clone-safe OECD/Eurostat fixture persistence.

Fresh sessions can recover with:

```bash
python3 tools/recover_session.py --project . --json
```

## Current capability summary

- Raw SQL/PostgreSQL foundation exists with `meta`, `staging`, and `curated` schemas; `mart` remains deferred.
- Source-specific bounded paths exist for WDI, OECD/SDMX, and Eurostat GDP evidence/loading/validation.
- Canonical-domain substrate exists for structured periods, ISO3-preserved territories, provider mappings/codes, units/attribute sets, and source-agnostic curated facts.
- Combined-source canonical validation and the first canonical GDP snapshot report are complete.
- Implemented canonicalization remains deterministic and file-backed; DEC-018 accepts the AI-assisted canonicalization design only conceptually.
- `artifacts/manifests/canonical_assets.json` is the narrow file-backed pointer registry for existing accepted/provisional canonicalization artifacts.
- TASK-042 created `artifacts/reports/gdp-eligibility-classification-20260619.json`: WDI is eligible only for bounded WDI-only descriptive findings with governed provisional caveats; OECD `USD_EXC`/`USD_PPP` are deferred/profile-specific; Eurostat `CP_MEUR` quarterly evidence is deferred/profile-specific with cross-source annual/current-USD use blocked by missing frequency/currency/scale policy.
- TASK-043 implemented `tools/consult_metaharvest.py`, a bounded advisory-only MetaHarvest consultation helper for scoped task/governance classification. It must not run during startup or routine work.
- TASK-044 and TASK-045 resolved the two operational blockers from `artifacts/reports/R-20260619-operational-capability-validation.md`.
- The post-freeze v1.1 assessment at `artifacts/reports/R-20260626-post-freeze-v11-architectural-assessment.md` recommends refactoring emerged ingestion infrastructure before expanding coverage. Its single next implementation recommendation is `TASK-046 — Define and validate NormalizedObservationPackage v1 for existing WDI/OECD/Eurostat evidence`.

## Active objective

No implementation task is open. Do not expand MacroForge scope unless the user explicitly opens the recommended v1.1 refactor task or a downstream consumer produces a concrete blocker. Fresh final verification is still required before any v1 freeze/commit.

The database-state review found canonicalization/review/comparability/eligibility semantics are file-backed rather than materialized into PostgreSQL. Queryable persistence should follow proven downstream need.

Future OECD GDP mapping advancement must start from the OECD mapping-status review plus OECD unit-basis comparability artifact and requires explicit review approval. Future Eurostat GDP mapping advancement must start from deferred mapping advancement requirements.

## Current governance posture

- Use Hermes tools directly for normal agent work; `tools/run.py` is for manual/non-Hermes audited command execution when useful.
- Evaluate future work by which recurring effort it reduces: source onboarding, source maintenance, validation, canonical mapping, schema evolution, downstream analysis, or agent recovery/context effort.
- Primary audit trail: task, decision, handoff, state, and report artifacts. Operational logs are optional debugging artifacts.
- Primary state artifacts should stay concise current-state pointers. Historical detail belongs in task/report/handoff artifacts.
- Run Architecture-to-Reality Audits every 5-10 completed tasks and before major architecture/governance reviews.

## Boundaries for next work

Until a new task/decision explicitly changes scope, future canonicalization lifecycle work must not:

- call AI/models for canonicalization or configure prompt/provider behavior;
- onboard new sources, live-fetch data, write to live/default `macro`, or add PostgreSQL migrations;
- mutate mapping status, accepted/base state, canonical manifests, or reports without explicit review artifact approval;
- implement unit/currency conversion, frequency aggregation, generalized metadata/source frameworks, provider-specific fact columns, or auto-apply mappings;
- push to git.

## Durable recovery anchors

- Active goal: `state/active_goal.md`
- Architecture state: `state/architecture.md`
- Latest handoff: `context/latest_handoff.md`
- Backlog/task chronology: `artifacts/tasks/backlog.md`
- Reports summary: `artifacts/reports/_SUMMARY.md`
- Canonical asset manifest: `artifacts/manifests/canonical_assets.json`
- GDP eligibility classification: `artifacts/reports/gdp-eligibility-classification-20260619.json`
- V1 closure review: `artifacts/reports/R-20260619-v1-closure-review.md`
- Operational capability validation: `artifacts/reports/R-20260619-operational-capability-validation.md`
- Post-freeze v1.1 architecture assessment: `artifacts/reports/R-20260626-post-freeze-v11-architectural-assessment.md`
- Canonicalization implementation/design: `src/macroforge/canonicalization_state.py`, `docs/architecture/minimal-ai-assisted-canonicalization-layer.md`
