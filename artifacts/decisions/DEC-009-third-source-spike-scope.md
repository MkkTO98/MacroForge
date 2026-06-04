# DEC-009 — Bounded third no-key source spike scope

Status: accepted
Date: 2026-06-04
Requested by: user
Related task: TASK-020

## Decision

Proceed with a bounded third no-key source spike using one additional public source: Eurostat quarterly national accounts GDP (`namq_10_gdp`).

The objective is limited to validating MacroForge's canonical model, ingestion framework posture, metadata architecture, and fact table design against one additional public source.

The spike should produce:

- raw public no-key source evidence,
- compact normalized metadata evidence,
- a short findings report,
- recommended schema changes if architecture gaps are found.

## Scope boundaries

TASK-020 must not pursue production-grade hardening beyond what is needed to identify architectural gaps.

Accepted boundaries:

- One additional public no-key source only.
- One bounded dataset/slice only.
- Report-first architecture validation.
- File-backed raw/normalized/report evidence is allowed.
- Live public no-key HTTP fetch is allowed for the bounded spike.
- No production database writes.
- No live `macro` database writes.
- No PostgreSQL promotion implementation.
- No executable schema migration in TASK-020.
- No generalized ingestion/source framework.
- No broad codelist harvest.
- No research/mart implementation.
- No credentialed or paid source.

## Source selection

Eurostat was selected because it is:

- public and no-key,
- macroeconomically relevant,
- structurally different from both WDI and OECD/SDMX,
- exposed as JSON-stat through the Eurostat dissemination API,
- useful for testing quarterly periods, provider geo codes, units, seasonal adjustment, and dimension metadata.

Bounded endpoint used by TASK-020:

```text
https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/namq_10_gdp?format=JSON&lang=en&freq=Q&unit=CP_MEUR&na_item=B1GQ&s_adj=NSA&geo=DE&geo=FR&time=2023-Q1&time=2023-Q2
```

## Rationale

WDI and OECD already validate annual macro observation loading for two source shapes. Eurostat adds a useful third shape because it introduces:

- JSON-stat dimensional payloads,
- quarterly periods (`2023-Q1`, `2023-Q2`),
- provider geography codes (`DE`, `FR`) rather than ISO3-style codes,
- provider dimension labels and code dictionaries,
- seasonal-adjustment qualifiers.

Those differences are sufficient to test whether the canonical model and current schema assumptions are ready for another source without implementing full ingestion.

## Consequences

The spike may recommend schema changes. Those recommendations are advisory until a later decision accepts an implementation plan.

If the spike identifies blocking schema gaps, the next task should be a schema/design decision rather than a source loader implementation.
