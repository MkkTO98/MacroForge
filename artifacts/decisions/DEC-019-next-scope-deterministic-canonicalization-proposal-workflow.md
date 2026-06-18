# DEC-019 — Next scope: deterministic canonicalization proposal workflow

Status: accepted
Date: 2026-06-05
Related task: TASK-033
Preceded by: TASK-032, DEC-018, DEC-016, DEC-015
Analysis note: `docs/architecture/canonicalization-next-scope-decision-analysis.md`
Follow-on task: TASK-034 — Implement tiny deterministic canonicalization proposal workflow

## Decision

MacroForge will next implement a tiny deterministic proposal-generation workflow for the existing bounded WDI/OECD/Eurostat GDP fixture set.

The selected option is A: deterministic proposal-generation workflow for a tiny fixture set.

This choice optimizes for uncertainty reduction, not capability. The next task should validate whether the TASK-032 state foundation can support the actual canonicalization workflow loop:

```text
provider evidence
-> deterministic proposal generation
-> review routing
-> accepted/provisional mapping update proposal
-> audit report
```

## Why this option

TASK-032 proved that MacroForge can represent the minimum canonicalization state entities. It did not yet prove that those entities work as a lifecycle.

Option A is the best next step because it:

- has the smallest implementation surface: deterministic rules over existing fixture evidence;
- has the highest learning value: it exercises the state-to-proposal-to-review loop rather than adding capability;
- has low architectural risk: it keeps the work file-backed and avoids premature PostgreSQL persistence;
- maximally validates TASK-032: it uses provider evidence, run records, proposals, unit profiles, review routing, accepted/provisional mapping state, and audit output;
- avoids AI dependence before workflow validation, so failures are attributable to state/workflow design rather than model behavior.

## Alternatives considered

### B. AI-assisted proposal generation

Deferred. It may become valuable later, but doing it now would confound workflow uncertainty with model/prompt/provider uncertainty. It also introduces AI dependence before MacroForge has proven deterministic proposal lifecycle mechanics.

### C. Additional canonicalization state expansion

Deferred. TASK-032 already represented the minimum state surface. Expanding state now risks entity/schema bloat before workflow pressure proves which fields are actually needed.

### D. Alternative bounded scope

Deferred. WDI unit metadata enrichment, PostgreSQL persistence, report integration, review calibration, or a different data/report task may become appropriate later, but none validates the TASK-032 workflow loop as directly as a tiny deterministic proposal workflow.

## Accepted follow-on scope

TASK-034 should implement only a tiny deterministic proposal-generation workflow against the existing fixture-backed TASK-032 evidence.

Accepted output should include:

- a fresh implementation dry-run;
- failing tests before implementation;
- deterministic proposal-generation logic over existing provider evidence;
- explicit run/proposal audit output;
- review routing that keeps GDP high-impact mappings review-required;
- unit metadata caveat propagation, especially WDI unknown units;
- no automatic acceptance beyond existing fixture/provisional policy;
- proof that proposals remain separate from accepted/provisional mapping state.

## Rejected scope

This decision does not approve:

- AI/model proposal generation;
- prompt engineering or model-provider setup;
- embedding/vector search;
- PostgreSQL migrations for canonicalization state;
- additional canonicalization state expansion unless directly required by the deterministic workflow;
- new source onboarding;
- live fetches;
- live/default `macro` writes;
- unit conversion;
- quarterly-to-annual aggregation;
- mart/dashboard/reporting expansion beyond a bounded audit artifact;
- broad ontology/knowledge graph work;
- generalized ingestion/source framework extraction;
- provider-specific fact columns;
- git push.

## Reconsideration triggers

Reopen this decision if TASK-034 shows that:

- current provider evidence is too sparse even for deterministic proposals;
- current TASK-032 identifiers or state separation cannot support proposal lifecycle transitions;
- WDI unknown unit metadata blocks useful workflow validation and must be enriched first;
- proposal generation requires state fields not present in TASK-032;
- review routing becomes equivalent to manual-every-mapping governance;
- deterministic workflow succeeds and the next uncertainty becomes AI proposal quality rather than workflow mechanics.

## Evidence reviewed

- `context/context_audit.md`
- `artifacts/tasks/TASK-033-decide-next-scope-after-canonicalization-state-foundation.md`
- `artifacts/tasks/TASK-032-implement-minimal-canonicalization-state-foundation.md`
- `artifacts/reports/canonicalization-state-foundation-20260605.json`
- `src/macroforge/canonicalization_state.py`
- `tests/test_canonicalization_state.py`
- `docs/architecture/minimal-ai-assisted-canonicalization-layer.md`
- `docs/architecture/canonicalization-next-scope-decision-analysis.md`
- `artifacts/decisions/DEC-018-minimal-ai-assisted-canonicalization-layer.md`
- `artifacts/decisions/DEC-016-ai-assisted-canonicalization-layer.md`
- `artifacts/decisions/DEC-015-next-scope-canonical-indicator-unit-comparability.md`
- `simulation/dry_runs/20260605_215424-dry-run.md`

## Consequences

MacroForge keeps the AI-assisted long-term direction while reducing uncertainty in the least complex order:

1. prove state representation — completed in TASK-032;
2. prove deterministic workflow — selected for TASK-034;
3. only then consider AI-assisted proposal generation, schema persistence, richer state, or report integration.

No implementation was performed under TASK-033.
No git push was performed.
