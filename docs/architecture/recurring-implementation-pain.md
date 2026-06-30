# Recurring Implementation Pain

Status: active lightweight implementation-methodology artifact
Created: 2026-06-30

## Purpose

This artifact records recurring engineering difficulties observed during heterogeneous source implementations.

Repeated implementation pain, not repeated code, is the primary evidence for future architectural extraction candidates.

The goal is to avoid framework-first thinking while still noticing when repeated source work is becoming unnecessarily expensive or fragile.

## Update rule

After every heterogeneous source implementation, record:

- implementation/task;
- pain observed, if any;
- whether it repeats earlier pain;
- current action;
- evidence that would justify future extraction.

No pain is an acceptable entry.

Do not record ordinary implementation details unless they explain recurring cost, fragility, or repeated reasoning burden.

## Current records

| Implementation | Pain observed | Repeats earlier pain? | Current action | Future extraction evidence threshold |
|---|---|---|---|---|
| TASK-053 BEA NIPA bounded slice | BEA API-key friction made the public iTableCore path preferable for bounded evidence; interactive-table structure required source-specific interpretation of prompts, headers, stubs, line numbers, and period columns. | Partially repeats source-specific metadata interpretation burden, but table structure is not yet repeated enough for extraction. | Keep BEA interpretation source-specific. | Another official table-style provider with similar prompt/header/stub/line mechanics causing comparable implementation pain without source-specific semantic divergence. |
| TASK-054 Treasury Fiscal Data bounded slice | Needed source-slice selection discipline to choose monthly `avg_interest_rates` rather than a daily endpoint that would force contract evolution outside the task objective. | Repeats bounded-scope selection pain, not implementation-framework pain. | Keep source selection explicit in prediction ledger. | Multiple sources requiring scope gymnastics solely because the observed contract lacks a genuinely shared period concept. |
| TASK-055 ECB SDW bounded slice | SDMX GenericData XML mechanics repeated across OECD and ECB, but ECB semantic interpretation still required source-specific dataflow/dimension/unit/indicator handling. | Repeats SDMX XML parsing mechanics; does not yet repeat enough semantic convergence to extract. | Record as future extraction evidence, not architectural action. | A third SDMX provider, or a second deeper SDMX slice, shows stable source-neutral contract, algorithm, and implementation convergence while reducing engineering/human/LLM effort without source-specific conditionals. |

## Review use

During the five-source Retrospective Review, identify which pains repeated and whether any exactly one extraction candidate has enough evidence.

If repeated pain is absent or does not satisfy the extraction gate, explicitly continue heterogeneous source implementation without architectural change.
