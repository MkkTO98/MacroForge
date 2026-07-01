# TASK-057 Implementation Lessons — Bounded BIS WS_CBPOL SDMX Evidence Slice

Date: 2026-06-30
Task: `artifacts/tasks/TASK-057-bounded-bis-cbpol-sdmx-evidence-slice.md`
Status: implemented and verified

## Summary

TASK-057 implemented a source-specific Bank for International Settlements WS_CBPOL bounded SDMX evidence slice for monthly central bank policy rates for `US` and `JP`, 2024-01 through 2024-03.

It produced six observed observations through the existing `ObservedIngestionPackage` without broad BIS support, broad WS_CBPOL support, generic SDMX infrastructure, canonical loading, database writes, or KnowledgeForge semantics.

Raw fixture:

- `data/raw/bis_cbpol/bis-cbpol-us-jp-2024m01-2024m03-raw.xml`
- SHA-256: `ffbd9ee370f9874bf1010ea1a7014647bbfcfb4ea5d0ffa2ac26f9986d5af762`

Observed package fingerprint:

- `43a4c38e02ab0d4805bd973e14568deb9b424aecbf4fc2896b4b411e3446085d`

## Prediction review

### Prediction 1 — Observed contract evolution

Prediction: no `ObservedIngestionPackage` evolution required.

Result: Confirmed.

Evidence: BIS dataflow identity, reference area, monthly period, value, unit, series metadata, observation status/confidentiality, and raw source payload all fit existing observed package fields.

### Prediction 2 — Deterministic substrate evolution

Prediction: no deterministic substrate evolution required.

Result: Confirmed.

Evidence: contract validation, deterministic replay, package comparison, and fingerprinting worked unchanged.

### Prediction 3 — New pre-boundary patterns

Prediction: BIS would add source-specific SDMX StructureSpecificData parsing and provider attribute interpretation.

Result: Confirmed.

Evidence: implementation handled BIS-specific `WS_CBPOL` dataflow identity, `REF_AREA` values, `SOURCE_REF`, `COMPILATION`, `DECIMALS`, `TITLE`, `OBS_STATUS`, and `OBS_CONF` before the boundary.

### Prediction 4 — Reusable lessons

Prediction: SDMX-family extraction evidence would increase, but generic SDMX extraction would remain unjustified.

Result: Confirmed.

Evidence: BIS repeated SDMX-family dataflow/series/observation mechanics but did not eliminate provider-specific parsing and interpretation. It used the same conceptual observation values as IMF MFS_IR for US/JP policy rates, but source metadata, reference-area codes, dataflow identity, and attribute semantics still required source-specific handling.

### Prediction 5 — Effort distribution

Prediction: acquisition Low, provider interpretation Medium, normalization Low-Medium, observed package Low, substrate Very Low, canonical loading None, testing Medium.

Result: Mostly confirmed.

Evidence: public BIS API access was straightforward. Most effort was in explicit bounded normalization and tests; substrate and contract work were negligible.

## Architectural conclusion

TASK-057 strengthens the existing conclusion rather than changing it:

- `ObservedIngestionPackage` required no evolution.
- The deterministic substrate required no evolution.
- SDMX-family extraction evidence is stronger after OECD/ECB/IMF/BIS.
- Generic SDMX extraction is still not justified because provider-specific interpretation remains material.

## Verification

RED:

```text
uvx pytest tests/test_bis_cbpol.py -q
```

failed because `macroforge.bis_cbpol` did not exist.

GREEN and adjacent regression:

```text
uvx pytest tests/test_bis_cbpol.py -q
```

```text
5 passed in 0.03s
```

```text
uvx pytest tests/test_bis_cbpol.py tests/test_imf_mfs_ir.py tests/test_ecb_sdw.py tests/test_observed_ingestion.py -q
```

```text
22 passed in 0.23s
```

```text
python3 -m compileall -q src/macroforge/bis_cbpol.py tests/test_bis_cbpol.py
```

passed with no output.

## Future implication

TASK-057 likely makes the next five-source retrospective review more valuable than another immediate SDMX-family slice. The retrospective should decide whether continued heterogeneous source implementation without architectural change remains correct, or whether exactly one extraction candidate now has enough evidence.
