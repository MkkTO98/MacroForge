# Trigger-Gated MetaHarvest Consultation

Status: implemented Phase 1 helper
Implementation: `tools/consult_metaharvest.py`
Design source: `artifacts/reports/R-20260626-metaharvest-trigger-gated-consultation-implementation-design.md`

## Purpose

MacroForge can optionally consult MetaHarvest during task-scope/governance classification when a proposed task materially matches the existing consultation triggers in `architecture/architectureharvest/relevance_map.yaml`.

This is an advisory preflight helper only. It does not change MacroForge authority, create tasks, mutate MetaHarvest, mutate canonical data, add runtime orchestration, or run during startup.

## Invocation point

Run the helper only after normal MacroForge recovery has identified a specific user request, active task, or proposed task scope:

```bash
python3 tools/consult_metaharvest.py --task-summary '<scoped task summary>'
```

or:

```bash
python3 tools/consult_metaharvest.py --task-file artifacts/tasks/<task>.md
```

Do not call it as unconditional startup behavior. Routine work such as status inspection, existing tests, closeout, fixture refreshes, and report regeneration should return `do_not_consult` and perform no MetaHarvest retrieval.

## Contracts

### Consultation Contract

`ConsultationContract` decides only whether consultation should occur.

Inputs:

- versioned structured task classification (`task_classification_version: 1`);
- `architecture/architectureharvest/relevance_map.yaml`;
- active consultation triggers;
- MacroForge governance boundaries.

Output:

- `consult`; or
- `do_not_consult`.

It must not perform retrieval, inspect MetaHarvest records, create tasks, adopt findings, or influence retrieval strategy.

### Retrieval Contract

`RetrievalContract` runs only after the Consultation Contract returns `consult`.

It supports:

1. one primary problem query;
2. one keyword fallback;
3. up to two adjacent-problem fallbacks;
4. bounded deeper inspection of selected records.

Default deeper-read cap is 3 records. The governance/design absolute cap is 5 records and requires explicit `--allow-governance-deeper-cap`.

Retrieval failures are non-blocking. If MetaHarvest or `tools/query_knowledge.py` is unavailable, the helper records the failure in the advisory output and exits successfully so MacroForge execution can continue.

## Advisory output

The helper prints a compact `MetaHarvest Advisory` block containing:

- Reason triggered;
- Retrieved records;
- Confidence;
- Relevant prior decisions;
- Recommended considerations;
- Ignored because;
- Authority note.

The Authority note is mandatory:

> MetaHarvest provides historical architectural context only. MacroForge retains full ownership of design decisions. Consultation is advisory rather than authoritative.

Confidence values are limited to `High`, `Medium`, and `Low`. They describe retrieval relevance/transferability only and never imply authority.
