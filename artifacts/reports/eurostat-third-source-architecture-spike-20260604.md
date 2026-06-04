# Eurostat third-source architecture spike

Status: complete
Date: 2026-06-04
Task: TASK-020
Source: Eurostat quarterly national accounts GDP (`namq_10_gdp`)

## Objective

Validate MacroForge's canonical model, ingestion framework posture, metadata architecture, and fact table design against one additional public no-key source. This is architecture evidence only, not production-grade Eurostat ingestion.

## Evidence

- Endpoint: `https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/namq_10_gdp?format=JSON&lang=en&freq=Q&unit=CP_MEUR&na_item=B1GQ&s_adj=NSA&geo=DE&geo=FR&time=2023-Q1&time=2023-Q2`
- Raw artifact: `data/raw/eurostat/eurostat-namq-10-gdp-2023q1-2023q2-raw.json`
- Normalized artifact: `data/metadata/eurostat/eurostat-namq-10-gdp-architecture-spike-normalized.json`
- HTTP status: 200
- Content type: `application/json`
- Raw bytes: 3262
- Raw SHA-256: `914888671969cf31253dc0e951aaa8bee66bbf8ec03d1ff193bc6b1feda1865a`
- Rows normalized: 4

## Smoke slice

| geo | label | period | unit | adjustment | value |
| --- | --- | --- | --- | --- | --- |
| DE | Germany | 2023-Q1 | CP_MEUR | NSA | 1043520.0 |
| DE | Germany | 2023-Q2 | CP_MEUR | NSA | 1031880.0 |
| FR | France | 2023-Q1 | CP_MEUR | NSA | 684762.7 |
| FR | France | 2023-Q2 | CP_MEUR | NSA | 706147.7 |

## Findings

### Canonical model

PARTIAL. Eurostat still has the broad indicator/territory/period/unit/value shape, so the canonical model direction remains valid. But the current concrete dimensions are too annual/ISO3-shaped: quarterly periods would collapse under `curated.dim_period(frequency, period_year)`, and Eurostat `geo` values are provider territory codes, not ISO3 values.

### Ingestion framework

PARTIAL. The existing source-specific approach remains the right posture. A third source confirms a repeated raw artifact + checksum + normalized metadata + report workflow, but it is still too early to create a generalized ingestion framework. The immediate reusable seam should stay at contract/report conventions and tiny mechanical helpers.

### Metadata architecture

PARTIAL. `meta.source`, `meta.dataset_release`, and `meta.pipeline_run` can capture endpoint, filters, checksums, and run context. However, Eurostat's JSON-stat dimension dictionaries show that provider code lists/labels will become repeated metadata, not just ad hoc report text. This argues for a future metadata/codelist design before more sources are promoted.

### Fact table design

PARTIAL. `curated.fact_observation` remains plausible if dimensions are fixed. The fact grain should keep source-specific attributes such as seasonal adjustment in `attribute_set`. The blocking issue is not the fact table columns themselves; it is dimension identity around period and territory.

## Recommended schema changes

- HIGH: Replace or extend curated.dim_period natural key from (frequency, period_year) to (frequency, period_code), with period_code text such as 2023-Q1 plus optional year/quarter/month/start/end fields.
- HIGH: Rename or extend curated.dim_territory.iso3_code to source_territory_code/territory_code plus code_system so non-ISO3 provider codes like DE, FR, EU27_2020, EA20 are not mislabeled.
- MEDIUM: Add metadata storage for provider dimension/code dictionaries, either meta.provider_code_list or dataset_release.metadata conventions, before broad codelist reuse.
- MEDIUM: When promoting a third source, add source-specific staging.eurostat_namq_observation; do not build a generalized ingestion framework yet.
- LOW: Consider normalizing seasonal_adjustment into attributes for fact grain; keep as attribute_set initially.

## DEC-010 refinement

DEC-010 supersedes the provider-shaped wording of these report-only recommendations. The canonical-domain direction is:

- use structured canonical period fields and keep provider period strings in metadata/mapping;
- preserve ISO3 as the canonical country identifier;
- add `territory_type` and aggregate/economic-area support for non-country territories;
- map provider geography codes to canonical territories rather than replacing ISO3 semantics.

## Non-recommendations

- Do not production-harden Eurostat ingestion in TASK-020.
- Do not add a generalized source framework yet.
- Do not write Eurostat rows into PostgreSQL until schema decisions for period and territory are accepted.
- Do not broaden beyond one dataset and four observations for this spike.

## Verdict: PARTIAL

Eurostat validates MacroForge's canonical observation concept and source-specific ingestion posture, but exposes two concrete schema gaps that should be addressed before promoting a third source to PostgreSQL: period identity must support quarterly/monthly periods, and territory identity must not assume ISO3 codes.
