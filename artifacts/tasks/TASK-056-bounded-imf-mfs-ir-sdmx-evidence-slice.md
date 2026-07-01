# TASK-056 — Bounded IMF MFS_IR SDMX Evidence Slice

Status: implemented and verified
Date: 2026-06-30
Related planning reference: `implementation-planning-assessments/references/macroforge-smallest-imf-evidence-slice.md`
Related confidence ledger: `docs/architecture/architectural-confidence-ledger.md`

## Task framing

TASK-056 implements the smallest IMF slice designed to maximize architectural evidence without broad IMF support.

The implementation is a bounded source-specific IMF MFS_IR SDMX evidence slice. It is not IMF support, IFS support, broad MFS support, a generic SDMX layer, canonical loading, provider metadata infrastructure, or a canonical entity layer.

## Bounded source slice

Dataflow:

```text
IMF.STA:MFS_IR(9.0.0)
Monetary and Financial Statistics (MFS), Interest Rate
```

Observation slice:

```text
COUNTRY: USA, JPN
INDICATOR: MFS166_RT_PT_A_PT
FREQUENCY: M
TIME_PERIOD: 2024-M01 through 2024-M03
Expected observations: 6
```

Source data URL used for fixture capture:

```text
https://api.imf.org/external/sdmx/2.1/data/MFS_IR/USA+JPN.MFS166_RT_PT_A_PT.M?startPeriod=2024-01&endPeriod=2024-03
```

Metadata/dataflow URL:

```text
https://api.imf.org/external/sdmx/2.1/dataflow/all/MFS_IR/latest?references=all
```

## Architectural hypothesis under test

Current hypothesis:

```text
A third SDMX-family institutional source can still be handled as source-specific acquisition/parsing/interpretation before ObservedIngestionPackage. SDMX commonality remains protocol/acquisition-level evidence, not yet a MacroForge architectural boundary.
```

Alternative hypothesis:

```text
IMF confirms enough stable SDMX contract, algorithm, and implementation convergence across OECD, ECB, and IMF that a future pre-boundary SDMX Interpretation Layer should be considered.
```

## Pre-implementation predictions

These predictions are evaluated in `artifacts/reports/L-20260630-task-056-implementation-lessons.md`.

1. `ObservedIngestionPackage` contract evolution

Prediction: no contract evolution should be required. IMF COUNTRY, INDICATOR, FREQUENCY, TIME_PERIOD, OBS_VALUE, series attributes, observation attributes, dataflow identity, DSD identity, dimension order, and relevant codelist evidence should fit through existing package fields, `raw_evidence`, `attributes`, and `source_payload`.

Probability that `ObservedIngestionPackage` requires modification: 20%.

2. Deterministic Ingestion Substrate evolution

Prediction: no substrate evolution should be required. Existing validation, fingerprinting, comparison, lineage, and feedback mechanics should remain unchanged.

Probability substrate requires modification: 10%.

3. SDMX architectural boundary

Prediction: IMF will show repeated SDMX XML mechanics and metadata concepts, but provider interpretation will remain IMF-specific enough that no SDMX Interpretation Layer is justified during this task.

Confidence: 78%.

4. Pre-boundary patterns expected

Expected IMF-specific pre-boundary patterns:

- StructureSpecificData XML fixture parsing;
- IMF dataflow and data-structure version preservation;
- IMF dimension order preservation;
- relevant IMF codelist entry preservation;
- series-level IMF attributes such as `IFS_FLAG`, `OVERLAP`, `SCALE`, `ACCESS_SHARING_LEVEL`, and `SECURITY_CLASSIFICATION`;
- observation-level `DERIVATION_TYPE` preservation;
- provider indicator identity from IMF `INDICATOR` rather than canonical monetary semantics.

5. Post-boundary expectations

Prediction: post-boundary deterministic mechanics remain unchanged; implementation effort remains before the observed boundary.

6. Future extraction evidence

Prediction: TASK-056 may materially increase future SDMX extraction evidence because it is the third SDMX-family institutional source. It should not by itself trigger extraction unless it demonstrates stable source-neutral contract, algorithm, and implementation convergence without source-specific conditionals.

## Evidence that would strengthen the current hypothesis

- Valid IMF `ObservedIngestionPackage` produced with no contract changes.
- Source-specific IMF adapter remains clearer and safer than a generic SDMX layer.
- IMF differs from ECB/OECD in message shape, metadata volume, codelists, DSD structure, or provider identity construction enough that shared interpretation would require provider-specific conditions.
- Post-boundary validation and replay mechanics work unchanged.

## Evidence that would weaken the current hypothesis

- IMF parsing and metadata interpretation are nearly identical to ECB/OECD.
- A small source-neutral SDMX representation emerges naturally before `ObservedIngestionPackage`.
- Independent source-specific SDMX adapters cause obvious duplicated fragility or repeated defects.

## Evidence that would falsify the current hypothesis

- Honest IMF representation cannot preserve dataflow/dimension/codelist/attribute evidence through the current package contract.
- IMF requires source-specific branches in shared post-boundary substrate.
- IMF, ECB, and OECD can all be handled by the same source-neutral SDMX-to-observed algorithm with little more than endpoint/dataflow configuration.

## Non-goals

- No broad IMF support.
- No broad MFS support.
- No IFS-wide support.
- No BOP/DOTS/IIP support.
- No canonical PostgreSQL loading.
- No canonical monetary indicator mapping.
- No generic SDMX parser or SDMX Interpretation Layer extraction.
- No provider metadata framework.
- No canonical entity layer.
- No KnowledgeForge claims, concepts, or semantic mappings.
- No production scheduling or update automation.

## Implementation closeout

Implementation Lessons artifact:

```text
artifacts/reports/L-20260630-task-056-implementation-lessons.md
```

Summary:

- Source-specific IMF adapter implemented at `src/macroforge/imf_mfs_ir.py`.
- Fixture-backed tests implemented at `tests/test_imf_mfs_ir.py`.
- Raw IMF evidence preserved under `data/raw/imf_mfs_ir/`.
- Existing observed contract and deterministic substrate required no evolution.
- Repeated SDMX mechanics are now stronger future extraction evidence, but no extraction is justified by TASK-056 alone.
