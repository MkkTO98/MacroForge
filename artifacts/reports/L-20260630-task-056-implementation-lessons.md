# TASK-056 Implementation Lessons — Bounded IMF MFS_IR SDMX Evidence Slice

Date: 2026-06-30
Task: `artifacts/tasks/TASK-056-bounded-imf-mfs-ir-sdmx-evidence-slice.md`
Status: implemented and verified

## Scope implemented

Implemented a bounded IMF MFS_IR SDMX evidence slice for two monthly country series:

```text
MFS_IR / USA+JPN.MFS166_RT_PT_A_PT.M / 2024-01..2024-03
```

Source data endpoint:

```text
https://api.imf.org/external/sdmx/2.1/data/MFS_IR/USA+JPN.MFS166_RT_PT_A_PT.M?startPeriod=2024-01&endPeriod=2024-03
```

Metadata/dataflow endpoint:

```text
https://api.imf.org/external/sdmx/2.1/dataflow/all/MFS_IR/latest?references=all
```

Raw fixtures:

```text
data/raw/imf_mfs_ir/imf-mfs-ir-usa-jpn-mfs166-2024m01-2024m03-raw.xml
data/raw/imf_mfs_ir/imf-mfs-ir-dataflow-references-20260630.xml
```

Raw SHA-256:

```text
f3717b6bdc1bc5076c3df1117aea2fa6625db13ade13d10d55220a9d2cfb7cea
```

Metadata SHA-256:

```text
2bd4baeaa6325f487ec2931b36cfaf4a096f7e8300b1b662a8d9632c2813b0fb
```

Observed-package fingerprint:

```text
20ff5865f2fa3a3afb38a37b5c32a8be146a955c6b9868728fd75cf6c67cb85e
```

## Prediction evaluation

### 1. `ObservedIngestionPackage` contract evolution

Prediction: no contract evolution should be required. IMF COUNTRY, INDICATOR, FREQUENCY, TIME_PERIOD, OBS_VALUE, series attributes, observation attributes, dataflow identity, DSD identity, dimension order, and relevant codelist evidence should fit through existing package fields, `raw_evidence`, `attributes`, and `source_payload`.

Result: Confirmed.

Evidence:

- IMF dataflow `MFS_IR`, version `9.0.0`, and DSD `DSD_MFS_IR` are preserved in package raw evidence/provider metadata.
- IMF dimensions `COUNTRY`, `INDICATOR`, `FREQUENCY`, and `TIME_PERIOD` fit existing territory, indicator, frequency, period, attributes, and source-payload fields.
- Series attributes `IFS_FLAG`, `OVERLAP`, `SCALE`, `ACCESS_SHARING_LEVEL`, and `SECURITY_CLASSIFICATION` are preserved without new package fields.
- Observation attribute `DERIVATION_TYPE` is preserved without new package fields.
- `validate_observed_package_contract` returned valid with no issues.

### 2. Deterministic Ingestion Substrate evolution

Prediction: no substrate evolution should be required. Existing validation, fingerprinting, comparison, lineage, and feedback mechanics should remain unchanged.

Result: Confirmed for the bounded evidence slice.

Evidence:

- Contract validation passed unchanged.
- `compare_observed_packages` showed deterministic replay equivalence.
- `observed_package_fingerprint` produced a stable 64-character fingerprint.
- No post-boundary production code was modified.

### 3. SDMX architectural boundary

Prediction: IMF will show repeated SDMX XML mechanics and metadata concepts, but provider interpretation will remain IMF-specific enough that no SDMX Interpretation Layer is justified during this task.

Result: Partially confirmed.

Evidence:

- IMF differs from TASK-055 ECB SDW at the XML payload shape level: IMF data observations use StructureSpecificData with dimension and attribute values encoded directly as element attributes, while TASK-055 ECB used GenericData with explicit SeriesKey/Value nodes.
- IMF metadata preservation required IMF-specific dataflow, DSD, dimension-order, and codelist filtering logic.
- Provider interpretation remained IMF-specific: MFS_IR indicator, country codelist, interest-rate unit choice, IMF dataflow version, and IMF-specific access/security/IFS attributes.
- However, IMF also strengthens repeated SDMX-family evidence: dataflow/version/DSD/codelist/dimension concepts now recur across OECD, ECB, and IMF.

Judgment: no SDMX Interpretation Layer is justified by TASK-056 alone, but future extraction evidence is stronger than after TASK-055.

### 4. Pre-boundary patterns expected

Prediction: IMF-specific pre-boundary patterns would include StructureSpecificData XML fixture parsing, IMF dataflow and DSD version preservation, dimension order, relevant codelist entries, series attributes, observation attributes, and provider indicator identity from IMF `INDICATOR`.

Result: Confirmed.

Evidence:

- `src/macroforge/imf_mfs_ir.py` is source-specific and handles only the bounded MFS_IR slice.
- Tests verify exact six-observation output, two countries, one indicator, one frequency, three monthly periods, expected values, dataflow/DSD metadata, dimension order, relevant codelists, and source attributes.
- The adapter deliberately does not generalize into an IMF client or SDMX layer.

### 5. Post-boundary expectations

Prediction: post-boundary deterministic mechanics remain unchanged; implementation effort remains before the observed boundary.

Result: Confirmed.

Evidence:

- New production code is limited to `src/macroforge/imf_mfs_ir.py`.
- Existing source-specific slice tests plus observed-ingestion tests passed without substrate modification.
- The task did not add canonical loading, SQL, staging tables, source registry behavior, or post-boundary source-specific conditionals.

### 6. Future extraction evidence

Prediction: TASK-056 may materially increase future SDMX extraction evidence because it is the third SDMX-family institutional source. It should not by itself trigger extraction unless it demonstrates stable source-neutral contract, algorithm, and implementation convergence without source-specific conditionals.

Result: Confirmed.

Evidence:

- SDMX-family concepts now repeat across OECD, ECB, and IMF.
- IMF's StructureSpecificData shape differs enough from ECB GenericData that generic extraction remains non-obvious.
- The strongest repeated pain is now around source selection, metadata evidence preservation, dataflow/DSD/codelist concepts, and XML mechanics, not a converged source-neutral provider interpretation algorithm.
- Extraction should remain deferred until repeated pain demonstrates contract, algorithm, and implementation convergence.

## Architectural judgment update

TASK-056 strengthens the current observed-boundary and deterministic-substrate architecture. IMF MFS_IR fits through existing `ObservedIngestionPackage` without contract or substrate evolution.

It also increases the evidence that SDMX-family sources deserve continued attention as a possible future extraction candidate. The key distinction is:

```text
SDMX concepts are recurring. A source-neutral SDMX interpretation architecture is still not proven.
```

The correct action is to record the repeated SDMX evidence and continue bounded heterogeneous source implementations, not extract a generic SDMX layer now.

## Reusable implementation pattern

For future bounded IMF/SDMX-family slices:

1. choose the smallest dimensioned query that tests provider identity without adding volume;
2. preserve dataflow agency/id/version, DSD id/version, dimension order, relevant codelist entries, source query URL, fixture hashes, series attributes, and observation attributes;
3. keep provider meaning source-specific;
4. map only bounded source-backed observation identity into `ObservedObservation` fields;
5. validate with the existing observed-package contract before considering extraction;
6. record repeated SDMX mechanics as future extraction evidence, not immediate architecture authority.

## Verification

RED evidence:

```text
uvx pytest tests/test_imf_mfs_ir.py -q
```

Result before implementation:

```text
ModuleNotFoundError: No module named 'macroforge.imf_mfs_ir'
```

Targeted GREEN:

```text
uvx pytest tests/test_imf_mfs_ir.py -q
```

Result:

```text
5 passed in 0.22s
```

Adjacent regression verification:

```text
uvx pytest tests/test_ecb_sdw.py tests/test_treasury_fiscal_data.py tests/test_bea_nipa.py tests/test_observed_ingestion.py tests/test_imf_mfs_ir.py -q
```

Result:

```text
25 passed in 0.87s
```

Syntax verification:

```text
python3 -m compileall -q src/macroforge tests/test_imf_mfs_ir.py
```

Result: passed with no output.
