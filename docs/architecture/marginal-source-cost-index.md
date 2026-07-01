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
| TASK-056 IMF MFS_IR bounded slice | SDMX StructureSpecificData XML interest-rate series plus large IMF dataflow/DSD/codelist metadata | Medium | Medium | Medium | Increased | Existing observed package and substrate held; IMF preserved dataflow, DSD, dimension order, codelist, series, and observation attribute evidence without contract evolution. | SDMX concepts now repeat across OECD/ECB/IMF, but IMF StructureSpecificData differs from ECB GenericData and source-specific interpretation still dominates. |
| TASK-057 BIS WS_CBPOL bounded slice | SDMX StructureSpecificData XML central-bank-policy-rate series | Low-Medium | Low-Medium | Low-Medium | Increased | Existing observed package and substrate held; BIS preserved dataflow, reference-area, series-attribute, and observation-attribute evidence without contract evolution. | SDMX concepts now repeat across OECD/ECB/IMF/BIS, but BIS provider interpretation remains source-specific. |
| TASK-058 ALFRED GDP revision-vintage bounded slice | two-vintage CSV release-vintage series | Low-Medium | Low-Medium | Medium | Increased | Existing observed package and substrate held; ALFRED preserved multiple provider-backed values for the same economic period, release identity, raw evidence, deterministic replay, and changed/unchanged overlap evidence without contract evolution. | First revision-vintage evidence shows value-period identity plus vintage identity must both be preserved, but one provider/slice is insufficient for extraction. |
| TASK-059 ILOSTAT unemployment-rate bounded slice | compact no-key JSON labor-market annual indicator query | Low | Low | Low | Increased | Existing observed package and substrate held; ILOSTAT preserved labor-market classification/status/source evidence through source-specific fields without contract evolution. | Labor classification/status code interpretation is source-specific; no generic labor or classification infrastructure justified. |
| TASK-060 UN Comtrade bilateral total-goods trade bounded slice | compact public preview JSON bilateral trade query | Low-Medium | Low-Medium | Low-Medium | Increased | Existing observed package and substrate held; UN Comtrade preserved reporter/partner/flow/product/value-basis/quantity metadata through source-specific fields without contract evolution. | Trade role, direction, product classification, FOB/CIF, estimation, and quantity/weight interpretation remain source-specific; no generic trade infrastructure justified. |
| TASK-061 WDI demographic foundation bounded slice | eight compact no-key WDI JSON indicator queries | Medium | Low-Medium | Low-Medium | Increased | Existing observed package and substrate held; WDI preserved population/growth/age/fertility/life-expectancy/urbanization evidence through source-specific fields without contract evolution. | Multiple indicators and unit/concept categories increase pre-boundary normalization effort but do not justify generic demographic infrastructure. |
| TASK-062 Eurostat input-output matrix bounded slice | compact JSON-stat product-by-product matrix cube | Medium | Medium | Medium | Increased | Existing observed package and substrate held; Eurostat preserved matrix cells, product-role pairs, stock-flow roles, JSON-stat flat indexes, and CPA labels without contract evolution. | JSON-stat cube decoding and product-role semantics are new source-specific pre-boundary effort; one matrix slice does not justify generic matrix/input-output infrastructure. |
| TASK-063 IMF BOP financial-account bounded slice | compact SDMX StructureSpecificData financial-account flow query | Low-Medium | Low-Medium | Low-Medium | Increased | Existing observed package and substrate held; IMF BOP preserved accounting-entry, investment-category, unit, scale, methodology, and observation attribute evidence without contract evolution. | BOP accounting-entry/investment-category interpretation remains source-specific; one financial-flow slice does not justify generic BOP or financial-flow infrastructure. |
| TASK-064 Eurostat energy balance bounded slice | compact JSON-stat official energy-balance cube | Low-Medium | Low-Medium | Low-Medium | Increased | Existing observed package and substrate held; Eurostat preserved energy balance components, fuel/product categories, KTOE units, and JSON-stat flat-index metadata without contract evolution. | Energy balance component/fuel interpretation remains source-specific; JSON-stat mechanics repeat, but one energy slice does not justify generic energy infrastructure. |
| TASK-065 FRED U.S. Treasury yield curve bounded slice | compact CSV multi-series monthly market curve export | Low-Medium | Low-Medium | Low-Medium | Increased | Existing observed package and substrate held after selecting monthly frequency; FRED preserved same-period tenor curve points, tenor metadata, percent yield units, and CSV metadata without contract evolution. | Daily Treasury feed would exceed current frequency validation; monthly curve evidence remains source-specific and does not justify generic market-data or yield-curve infrastructure. |

## Trend note

Current evidence suggests post-boundary engineering effort is decreasing or remaining very low, while source-specific pre-boundary interpretation remains the dominant cost center. TASK-056 increased SDMX-family extraction evidence, but did not show enough source-neutral algorithm or implementation convergence to justify extraction.

TASK-057 further increased SDMX-family extraction evidence, but again kept post-boundary effort very low and provider interpretation source-specific.

TASK-058 increased confidence that ordinary revision-vintage semantics fit through the current boundary. It should not trigger a new architectural planning cycle; if revision work continues later, gather more revision evidence before extraction investigation.

TASK-059 increased labor-domain coverage at low marginal implementation cost. It behaved as normal Domain Expansion Mode: post-boundary effort remained very low, while ILOSTAT labor classification/status/source interpretation remained source-specific.

TASK-060 increased international-trade coverage at low-medium marginal implementation cost. It behaved as normal Domain Expansion Mode: post-boundary effort remained very low, while UN Comtrade reporter/partner/flow/product/value-basis interpretation remained source-specific.

TASK-061 increased demographic coverage at medium marginal implementation cost because it intentionally covered eight foundational indicators. It still behaved as normal Domain Expansion Mode: post-boundary effort remained very low, while WDI demographic indicator/unit/concept interpretation remained source-specific.

TASK-062 increased input-output/matrix coverage at medium marginal implementation cost. It behaved as normal Domain Expansion Mode: post-boundary effort remained very low, while Eurostat JSON-stat dimension indexing and product-role interpretation remained source-specific.

TASK-063 increased international financial-flow coverage at low-medium marginal implementation cost. It behaved as normal Domain Expansion Mode: post-boundary effort remained very low, while IMF BOP accounting-entry and investment-category interpretation remained source-specific.

TASK-064 increased energy coverage at low-medium marginal implementation cost. It behaved as normal Domain Expansion Mode: post-boundary effort remained very low, while Eurostat energy balance component and fuel/product interpretation remained source-specific.

TASK-065 increased observation-family coverage with financial-market curve evidence at low-medium marginal implementation cost. It behaved as normal Domain Expansion Mode after selecting monthly FRED data to remain inside the validated contract; post-boundary effort remained very low, while tenor interpretation remained source-specific.

The next five-source Retrospective Review must use this table plus implementation lessons, confidence calibration, and recurring pain records to decide whether continued source implementation without architectural change remains correct.
