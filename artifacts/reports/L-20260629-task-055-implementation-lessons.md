# TASK-055 Implementation Lessons — Bounded ECB SDW Architectural Experiment

Date: 2026-06-29
Task: `artifacts/tasks/TASK-055-bounded-ecb-sdw-architectural-experiment.md`
Status: implemented and verified

## Scope implemented

Implemented a bounded ECB Statistical Data Warehouse evidence slice for the monthly EUR/USD exchange-rate series:

```text
EXR / M.USD.EUR.SP00.A / 2026-05
```

Source endpoint:

```text
https://data-api.ecb.europa.eu/service/data/EXR/M.USD.EUR.SP00.A?startPeriod=2026-05&endPeriod=2026-05
```

Raw fixture:

```text
data/raw/ecb_sdw/ecb-exr-usd-eur-2026-05-raw.xml
```

Raw SHA-256:

```text
166b0f3f30daeb6fd78ce67d7af6a81f00bb7f718cd627c0e53b865060da85a4
```

Observed-package fingerprint:

```text
6532a0f00854803140a71fbcc41391c4ea0fa630fdc3ff9401e55e1d8ab7c844
```

## Prediction evaluation

### 1. `ObservedIngestionPackage` contract evolution

Prediction: no contract evolution should be required if the bounded ECB slice uses annual, quarterly, or monthly observations.

Result: Confirmed.

Evidence:

- ECB monthly period `2026-05` mapped cleanly to existing `frequency="M"`, `period_year=2026`, `period_month=5`, and provider period code `2026-M05`.
- ECB exchange-rate identity mapped to provider indicator fields without adding observed-package fields.
- ECB SDMX series attributes, observation attributes, structure metadata, and query evidence were preserved through existing `raw_evidence`, `attributes`, and `source_payload` fields.
- `validate_observed_package_contract` returned valid with no issues.

### 2. Deterministic Ingestion Substrate evolution

Prediction: no substrate evolution should be required; existing fingerprinting, comparison, contract validation, lineage, and feedback should operate unchanged.

Result: Confirmed for the bounded evidence slice.

Evidence:

- Contract validation passed unchanged.
- `compare_observed_packages` showed deterministic replay equivalence.
- `observed_package_fingerprint` produced a stable 64-character fingerprint.
- No post-boundary production code was modified.

### 3. SDMX architectural boundary

Prediction: ECB will show SDMX commonality at acquisition/XML/protocol level, but provider interpretation will remain source-specific enough that no SDMX Interpretation Layer is justified yet.

Result: Confirmed, with future extraction evidence recorded.

Evidence:

- ECB and OECD both use SDMX GenericData XML mechanics: series key, observation dimension, observation value, and attributes.
- ECB-specific interpretation dominated the provider meaning: `EXR`, `CURRENCY`, `CURRENCY_DENOM`, `EXR_TYPE`, `EXR_SUFFIX`, ECB structure metadata, exchange-rate unit construction, and ECB area identity.
- A source-neutral SDMX Interpretation Layer is not justified from this bounded ECB slice alone.
- The repeated XML mechanics are evidence to watch, not evidence to extract now.

### 4. Pre-boundary patterns expected

Prediction: ECB-specific pre-boundary patterns would include SDMX XML acquisition/query provenance, dataflow identity and key capture, codelist/attribute interpretation, frequency/unit/dimension handling, deterministic provider indicator construction, and evidence about OECD/ECB convergence.

Result: Confirmed.

Evidence:

- Source-specific normalizer preserves source URL, content type, raw artifact path, SHA-256, message ID, prepared timestamp, sender, structure ID, structure URN, dataset action, valid-from date, and dimension-at-observation.
- Deterministic indicator code is `EXR:USD_EUR:SP00:A`.
- Unit code is `USD_PER_EUR`; unit label is `US dollar per euro`.
- Provider metadata interpretation remained ECB-specific.

### 5. Post-boundary expectations

Prediction: post-boundary deterministic mechanics remain unchanged; any implementation effort remains before the observed boundary.

Result: Confirmed.

Evidence:

- New production code is limited to the source-specific ECB pre-boundary adapter at `src/macroforge/ecb_sdw.py`.
- New tests assert that the module does not introduce a generic SDMX layer, source plugin, database writes, SQL, live loader, or framework.

### 6. Future extraction evidence

Prediction: TASK-055 may produce evidence worth recording for a possible future SDMX Interpretation Layer, but will not by itself satisfy the extraction gate.

Result: Confirmed.

Evidence:

- Repeated SDMX GenericData parsing mechanics are now visible across OECD and ECB.
- The repeated mechanics are not yet sufficient for extraction because provider semantics, bounded series meaning, units, labels, and identity construction remain source-specific.
- A future IMF SDMX or second ECB/OECD slice could determine whether repetition is merely XML boilerplate or a stable source-neutral pre-boundary representation.

## Architectural judgment update

TASK-055 strengthens the current architecture. ECB SDW fits through the existing observed boundary without contract or substrate evolution. It also creates legitimate future extraction evidence around SDMX GenericData mechanics, but not enough to justify an SDMX Interpretation Layer now.

The best current judgment is:

```text
SDMX commonality is real at the XML/protocol mechanics level, but still not a MacroForge architectural boundary. Provider interpretation remains source-specific before ObservedIngestionPackage.
```

## Reusable implementation pattern

For bounded SDMX-family source slices:

1. keep acquisition and provider interpretation source-specific;
2. preserve raw query URL, content type, raw checksum, message/structure metadata, series dimensions, series attributes, observation dimension, observation value, and observation attributes;
3. map only the bounded provider meaning into `ObservedObservation` fields;
4. validate against the existing observed-package contract before considering any extraction;
5. record repeated SDMX mechanics as future extraction evidence, not as automatic extraction approval.

## Verification

Targeted test command:

```text
PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests/test_ecb_sdw.py -q
```

Result:

```text
5 passed in 0.02s
```
