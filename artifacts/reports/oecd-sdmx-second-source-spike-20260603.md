# TASK-011 Evidence Report — OECD/SDMX-Style Second Source Spike

Date: 2026-06-03
Task: TASK-011
Decision: DEC-005
Contract: `docs/data/source-contract.md`

## Summary

The no-key OECD/SDMX-style second-source candidate is viable for a bounded next implementation spike, but it has enough shape and API differences from WDI that MacroForge should not jump directly to a broad source framework.

Recommendation: implement a tiny OECD annual-national-accounts smoke slice as the next source-specific path using the minimal source contract, not a generalized SDMX parser. Keep it report/fixture-sized first, then decide whether to promote it to PostgreSQL load.

## Source identity

- `source_code`: candidate `OECD_NAAG`
- `source_name`: OECD annual national accounts / NAAG Chapter 1 GDP dataflow
- `source_home_url`: `https://sdmx.oecd.org/`
- `provider_dataset_code`: `OECD.SDD.NAD,DSD_NAAG@DF_NAAG_I`
- `license_note`: no credentials used for this spike; public SDMX REST endpoint responded successfully.

## Candidate endpoint

Dataflow list endpoint tested:

```text
https://sdmx.oecd.org/public/rest/v1/dataflow/OECD.SDD.NAD/all/latest
```

Candidate data endpoint tested:

```text
https://sdmx.oecd.org/public/rest/v1/data/OECD.SDD.NAD,DSD_NAAG@DF_NAAG_I/.?startPeriod=2020&endPeriod=2021
```

## Live access evidence

The candidate data endpoint responded successfully without credentials.

```text
status 200
content_type application/vnd.sdmx.genericdata+xml; version=2.1; charset=utf-8
bytes 1002311
sha256 d1e67a62dd5f35ab7530781e73343d5c64e6d073bea1edc7d59b56b28cbe5546
series 832
obs 832
```

The dataflow list endpoint also responded successfully without credentials and returned OECD SDMX structure XML. The OECD.SDD.NAD agency/dataflow list contained 187 dataflows.

## Response shape

Response type is SDMX GenericData XML, not JSON.

First observed series key:

```json
[
  ["FREQ", "A"],
  ["REF_AREA", "AUS"],
  ["MEASURE", "B1GQ"],
  ["UNIT_MEASURE", "USD_EXC"],
  ["CHAPTER", "NAAG_I"]
]
```

First observation:

```json
{
  "ObsDimension": {"id": "TIME_PERIOD", "value": "2020"},
  "ObsValue": {"value": "1439.0230643897"},
  "Attributes": [
    ["CONF_STATUS", "F"],
    ["DECIMALS", "2"],
    ["OBS_STATUS", "A"]
  ]
}
```

## Contract fit

The candidate fits the current broad indicator/territory/period/value model, but with important differences from WDI.

### Fits current model

- `REF_AREA` can map to territory code.
- `MEASURE` can map to indicator/source measure code.
- `TIME_PERIOD` can map to annual period.
- `ObsValue.value` can map to observation value.
- `UNIT_MEASURE` can map to unit.
- Series/observation attributes can map to `dim_attribute_set` and `source_payload`.

### Differences from WDI

- XML SDMX GenericData rather than JSON list payload.
- Dimensions are split between `SeriesKey` and `ObsDimension`.
- Human-readable labels are not embedded in the observation response and require structure/codelist lookup or a deliberate code-only first pass.
- A broad unconstrained query returns 832 observations for 2020-2021, much larger than the 8-row WDI smoke slice.
- The URL key syntax is more complex than World Bank WDI's indicator/country/date query style.

## Viability conclusion

Viable for a bounded no-key second-source spike.

Do not implement a general SDMX framework yet. The next implementation should be a source-specific OECD smoke normalizer that proves MacroForge can handle XML SDMX dimensions and attributes while preserving the existing raw evidence/checksum/report discipline.

## Smallest proposed implementation task

Implement an OECD/SDMX smoke evidence slice, not a curated database load yet.

Suggested scope:

- Fetch or use a recorded raw OECD SDMX GenericData XML payload for `OECD.SDD.NAD,DSD_NAAG@DF_NAAG_I` over 2020-2021.
- Preserve raw XML artifact, byte count, SHA-256, endpoint, and response metadata.
- Normalize only a small bounded subset, for example two `REF_AREA` values and one `MEASURE`, to keep the smoke slice comparable to WDI.
- Produce a report mapping SDMX fields to `docs/data/source-contract.md`.
- Add tests for XML parsing and checksum/report behavior.
- Defer PostgreSQL staging/curated load until the normalized shape is accepted.

## Schema impact

No immediate schema change is required for the smoke evidence slice.

Possible future schema pressure to monitor:

- `dim_indicator` may need provider codelist labels/descriptions if code-only labels are insufficient.
- `dim_attribute_set` will matter more because SDMX observations carry attributes like `CONF_STATUS`, `DECIMALS`, and `OBS_STATUS`.
- Territory/measure codelist lookup may require a metadata enrichment step before curated load.

Create a new decision record before changing the schema for OECD/SDMX.

## Friction / risks

- SDMX URL construction and key filtering need careful documentation.
- Response payloads can become large quickly if dimensions are not constrained.
- Label/codelist retrieval adds complexity absent from the WDI smoke slice.
- A generalized SDMX parser would be tempting but premature after one candidate response.

## Commands/evidence collection

Evidence was collected with Python `urllib.request` from this project directory. No credentials, paid APIs, live `macro` database, or production data were used.

Representative evidence command output:

```text
status 200
content_type application/vnd.sdmx.genericdata+xml; version=2.1; charset=utf-8
bytes 1002311
sha256 d1e67a62dd5f35ab7530781e73343d5c64e6d073bea1edc7d59b56b28cbe5546
series 832 obs 832
first_series_dims [["FREQ", "A"], ["REF_AREA", "AUS"], ["MEASURE", "B1GQ"], ["UNIT_MEASURE", "USD_EXC"], ["CHAPTER", "NAAG_I"]]
first_obs_dim {'id': 'TIME_PERIOD', 'value': '2020'}
first_obs_value {'value': '1439.0230643897'}
first_obs_attrs [["CONF_STATUS", "F"], ["DECIMALS", "2"], ["OBS_STATUS", "A"]]
```
