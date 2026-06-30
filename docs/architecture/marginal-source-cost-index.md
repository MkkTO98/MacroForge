# Marginal Source Cost Index

Status: active lightweight implementation-methodology artifact
Created: 2026-06-30

## Purpose

This index records intentionally approximate relative estimates after every heterogeneous source implementation.

The purpose is trend detection, not precise measurement.

Track whether MacroForge is reducing the marginal effort required to acquire, update, validate, and maintain future trustworthy economic sources without sacrificing determinism, auditability, provenance, reproducibility, or canonical consistency.

## Scale

Use Low / Medium / High / Very High, relative to recent MacroForge heterogeneous source implementations.

- Engineering effort: deterministic coding, fixture handling, parsing, normalization, tests, and verification.
- Human effort: judgment needed for scoping, source semantics, acceptance boundaries, and review.
- LLM reasoning effort: amount of agent reasoning/context needed to estimate, implement, debug, and close out safely.
- Architectural confidence: confidence produced by the implementation about whether the current architecture remains correct.

Values are approximate. Explanations matter more than numbers.

## Update rule

After every heterogeneous source implementation, append one row with:

- implementation/task;
- source shape;
- engineering effort;
- human effort;
- LLM reasoning effort;
- architectural confidence after implementation;
- evidence basis;
- recurring pain references.

Do not pause for architecture discussion to perfect the estimates.

## Historical index

| Implementation | Source shape | Engineering effort | Human effort | LLM reasoning effort | Architectural confidence after | Evidence basis | Recurring pain references |
|---|---|---|---|---|---|---|---|
| TASK-053 BEA NIPA bounded slice | interactive table / table-line metadata | Medium | Medium | Medium | Increased | Existing observed package and post-boundary substrate held; all predictions confirmed; complexity concentrated in source-specific iTableCore/table metadata interpretation. | Interactive table structure; API-key friction avoided by bounded public iTableCore path. |
| TASK-054 Treasury Fiscal Data bounded slice | row-oriented public government JSON API | Low-Medium | Low-Medium | Low-Medium | Increased | Existing observed package and substrate held; previous estimation model remained valid; monthly endpoint avoided unnecessary contract evolution. | Source-slice selection needed to avoid daily-period contract pressure. |
| TASK-055 ECB SDW bounded slice | SDMX GenericData XML exchange-rate series | Medium | Medium | Medium | Increased | Existing observed package and substrate held; repeated SDMX XML mechanics observed, but provider interpretation remained source-specific. | SDMX mechanics repeated, but provider-specific semantic interpretation still dominated. |

## Trend note

Current evidence suggests post-boundary engineering effort is decreasing or remaining very low, while source-specific pre-boundary interpretation remains the dominant cost center.

The next five-source Retrospective Review must use this table plus implementation lessons, confidence calibration, and recurring pain records to decide whether continued source implementation without architectural change remains correct.
