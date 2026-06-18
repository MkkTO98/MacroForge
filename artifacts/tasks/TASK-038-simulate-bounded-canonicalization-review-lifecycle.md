# TASK-038 — Simulate bounded canonicalization proposal review-to-accepted/provisional lifecycle

Status: complete
Created: 2026-06-14
Depends on: TASK-037
Governing decisions: DEC-018, DEC-019, DEC-020, DEC-021
Dry-run: `simulation/dry_runs/20260614_151206-task-038-review-lifecycle-validation.md`

## Objective

Validate, without creating new architecture, whether MacroForge can move from canonicalization proposal state to governed accepted/provisional mapping state in a way that reduces future manual canonicalization effort while preserving trust, provenance, and review-gated semantic correctness.

This task must demonstrate a bounded lifecycle over existing WDI/OECD/Eurostat GDP fixture-backed evidence:

```text
provider evidence
-> proposal
-> explicit review decision
-> accepted/provisional state delta
-> explicit check gates
-> manifest delta
-> replayable evidence
```

## Recurring effort reduced

TASK-038 is justified only because it reduces recurring effort in these classes:

- canonical mapping: reusable decision/check/delta/replay pattern instead of manual ad hoc mapping approval;
- validation: explicit gates replace prose-only trust claims;
- downstream analysis: report-impact flags prevent unreviewed GDP comparability assumptions;
- source maintenance: future metadata changes can be traced through deltas rather than hidden edits;
- future agent recovery/context: lifecycle artifacts make review outcomes inspectable from files.

## Scope allowed

TASK-038 may create or modify:

- this task artifact;
- one validated dry-run artifact;
- one bounded lifecycle JSON artifact under `artifacts/reports/`;
- one concise lifecycle Markdown report under `artifacts/reports/`;
- task/state/handoff/backlog/summary closeout files.

The lifecycle artifact may contain:

- explicit review decisions for existing WDI/OECD/Eurostat GDP mapping proposals;
- explicit check gates and per-decision results;
- state deltas representing simulated governed movement, not base-state mutation;
- manifest deltas representing proposed registry movement, not direct manifest mutation;
- evidence links by stable artifact path, checksum, and ID;
- replay evidence proving all inputs and outputs are file-backed and deterministic.

## Required demonstrations

- At least one governed provisional outcome.
- At least one deferred or rejected outcome.
- Explicit review decisions.
- Explicit check gates.
- Explicit state deltas.
- Replayable evidence.
- No auto-apply.
- No mutation of existing proposal artifacts.
- No direct mutation of `artifacts/manifests/canonical_assets.json`.

## Explicit non-goals

Do not:

- create production architecture;
- change source code;
- create pipelines, workers, migrations, or schemas;
- add or modify tests;
- call AI/models;
- configure prompts/providers/embeddings;
- live-fetch data;
- add sources or indicators;
- add PostgreSQL persistence;
- write to live/default `macro`;
- perform unit/currency conversion;
- aggregate quarterly to annual;
- integrate canonicalization state into the GDP snapshot report;
- extract generalized metadata/source frameworks;
- mutate accepted mapping state automatically;
- directly edit `artifacts/manifests/canonical_assets.json`;
- push to git.

## Acceptance criteria

- Dry-run validates before artifact creation.
- Lifecycle artifact uses existing TASK-032/TASK-034/TASK-037 evidence only.
- Lifecycle artifact records one WDI governed provisional outcome.
- Lifecycle artifact records at least one OECD/Eurostat deferred outcome.
- Every reviewed mapping has a review decision, check-gate results, state delta, manifest delta, and replay links.
- Check gates explicitly include proposal existence, mapping update proposal existence, `auto_apply: false`, high-impact review, evidence links, caveat preservation, no conversion/aggregation, proposal immutability, allowed status, report-impact deferral, and declared replay inputs.
- A deterministic replay/invariant validation confirms the artifact shape and scope boundaries.
- Full tests pass.
- Coherence and architecture-reality audit report no blocks or warnings after closeout.

## Outcome

Complete.

TASK-038 created a bounded lifecycle simulation over existing WDI/OECD/Eurostat GDP canonicalization evidence only.

Evidence produced:

- Primary lifecycle JSON: `artifacts/reports/canonicalization-review-lifecycle-20260614.json`
- Concise lifecycle report: `artifacts/reports/canonicalization-review-lifecycle-20260614.md`

The lifecycle artifact demonstrates:

- WDI `NY.GDP.MKTP.CD` -> `MACRO_GDP_OUTPUT`: governed provisional outcome.
- OECD `B1GQ` -> `MACRO_GDP_OUTPUT`: deferred outcome.
- Eurostat `B1GQ` -> `MACRO_GDP_OUTPUT`: deferred outcome.
- Explicit review decisions for all three mappings.
- Explicit check gates and per-decision check results.
- Explicit state deltas and manifest deltas.
- Replayable evidence using declared artifact paths, SHA-256 checksums, and stable IDs.

## Validation

Dry-run validation passed before artifact creation:

```text
python3 tools/validate_dry_run.py simulation/dry_runs/20260614_151206-task-038-review-lifecycle-validation.md
valid: simulation/dry_runs/20260614_151206-task-038-review-lifecycle-validation.md
```

Lifecycle invariant validation passed:

```text
PASS: TASK-038 lifecycle artifact invariants satisfied
```

Final full tests/coherence/audit verification is recorded in `context/latest_handoff.md` after closeout.

## Boundaries preserved

TASK-038 did not change source code, tests, migrations, schemas, workers, pipelines, source loaders, accepted mapping base state, the canonical asset manifest base file, or GDP reports. It did not call models, live-fetch data, add sources/indicators, write to live/default `macro`, perform unit/currency conversion, aggregate frequency, integrate reports, create generalized metadata/source framework behavior, auto-apply accepted-state changes, or push to git.
