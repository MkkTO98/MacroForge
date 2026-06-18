# Canonicalization Review Lifecycle Validation — TASK-038

Date: 2026-06-14
Status: succeeded
Scope: bounded file-backed simulation over existing TASK-032/TASK-034/TASK-037 WDI/OECD/Eurostat GDP evidence only.

## Question tested

Can MacroForge reduce future manual canonicalization effort while preserving trust, provenance, and review-gated semantic correctness by moving from proposal state to governed accepted/provisional mapping-state deltas?

## Result

Adopt narrowly.

The lifecycle is viable in bounded file-backed form:

- WDI `NY.GDP.MKTP.CD` -> `MACRO_GDP_OUTPUT`: governed provisional outcome.
- OECD `B1GQ` -> `MACRO_GDP_OUTPUT`: deferred outcome.
- Eurostat `B1GQ` -> `MACRO_GDP_OUTPUT`: deferred outcome.

This proves partial governed progress without pretending all GDP-like mappings are comparable.

## Evidence artifact

Primary JSON artifact:

`artifacts/reports/canonicalization-review-lifecycle-20260614.json`

It contains:

- explicit review decisions;
- explicit check-gate definitions;
- per-decision check results;
- accepted/provisional state deltas;
- manifest deltas;
- lineage edges;
- replay inputs with paths and checksums;
- scope-boundary preservation.

## Why WDI is governed provisional

TASK-037 reduced WDI's generic `unknown_unit_metadata` blocker by representing `NY.GDP.MKTP.CD` as current-USD source metadata evidence. That is enough for explicit review to move the mapping from generic review-required posture to review-approved provisional state.

It is not enough for accepted truth because:

- GDP is high-impact;
- WDI unit metadata remains source evidence, not canonical truth;
- no conversion/comparability policy is applied;
- report integration remains deferred.

## Why OECD is deferred

OECD `B1GQ` remains deferred because the bounded evidence contains multiple unit/comparability profiles: `USD_EXC` and `USD_PPP`. The lifecycle preserves this ambiguity rather than collapsing exchange-rate USD and PPP USD into one approved comparable GDP mapping.

## Why Eurostat is deferred

Eurostat `B1GQ` remains deferred because quarterly current-price million EUR values cannot be treated as comparable to annual/current-USD evidence without explicit conversion and aggregation policy. TASK-038 explicitly rejects conversion, aggregation, and report integration.

## Manual-effort reduction demonstrated

The task replaces ad hoc manual mapping approval with reusable file-backed surfaces:

1. proposal id;
2. mapping update proposal id;
3. explicit review decision;
4. check-gate results;
5. accepted/provisional state delta;
6. manifest delta;
7. lineage edge;
8. replay declaration.

Future mappings can reuse the same lifecycle shape instead of requiring hidden reviewer judgment or manual prose reconstruction.

## Boundaries preserved

TASK-038 did not change code, tests, migrations, schemas, workers, pipelines, source loaders, source data, accepted mapping base state, the canonical asset manifest base file, or GDP reports. It did not call models, live-fetch data, write to live/default `macro`, perform unit/currency conversion, aggregate frequency, or auto-apply accepted-state changes.
