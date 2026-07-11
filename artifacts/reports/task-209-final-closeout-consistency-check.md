# TASK-209 Final Closeout Consistency Check

Date: 2026-07-11
Status: complete

## Raw-evidence preservation

Canonical TASK-209 IMF raw artifact:

- path: `data/raw/task209_imf_weo_g20_projection_phase2_campaign/task-209-imf-weo-g20-projections-2026-2028.json`
- SHA-256: `d9817f3fbf6cbaf3f58caaf438e20f0077c4cd1785db9505e49791925eebec5c`
- durable local storage: repository working tree under `data/raw/task209_imf_weo_g20_projection_phase2_campaign/`
- Git status: ignored by `.gitignore` rule `data/raw/*`; final commit must include it with explicit force-add if Git-based reproducibility is desired.

The raw artifact contains:

- acquisition timestamp `2026-07-11T13:29:29+00:00`;
- six preserved IMF DataMapper requests and responses;
- API metadata with version `1`;
- indicator metadata source `World Economic Outlook (April 2026)` for all six indicators;
- indicator last-modified timestamps from `2026-04-08 16:07:34` through `2026-04-08 16:07:44`;
- provider values used to build the normalized TASK-209 facts.

Policy conclusion:

- MacroForge evidence-preservation practice preserves raw downloads by default.
- Because `data/raw/*` is ignored, the canonical raw artifact must be included in the bounded commit-ready set via explicit staging, or the final commit would only contain a checksum pointing to local ignored evidence.
- Do not claim Git-based reproducibility unless this raw artifact is force-added or another durable evidence store is explicitly established.

## Saudi Arabia LUR 2026-2028 evidence

Preserved raw request:

- indicator: `LUR`
- URL: `https://www.imf.org/external/datamapper/api/v1/LUR/ARG/AUS/BRA/CAN/CHN/FRA/DEU/IND/IDN/ITA/JPN/KOR/MEX/RUS/SAU/ZAF/TUR/GBR/USA`
- provider error: none
- response shape: valid `values.LUR` dictionary
- Saudi Arabia series: present as `values.LUR.SAU`
- Saudi Arabia series contains annual values through 2024, but no keys for 2026, 2027, or 2028.

Cell classification:

| Cell | Evidence | Classification |
| --- | --- | --- |
| SAU / LUR / 2026 | `values.LUR.SAU` exists; key `2026` absent; no provider error | absent from otherwise valid country-indicator series response |
| SAU / LUR / 2027 | `values.LUR.SAU` exists; key `2027` absent; no provider error | absent from otherwise valid country-indicator series response |
| SAU / LUR / 2028 | `values.LUR.SAU` exists; key `2028` absent; no provider error | absent from otherwise valid country-indicator series response |

Rule applied:

- TASK-209 has a deterministic candidate universe: 19 countries × 6 indicators × 3 years = 342 cells.
- When the provider returns a valid country-indicator series for a requested country but omits a requested candidate year, MacroForge preserves the expected but unavailable scalar cell as an explicit-missing fact.
- Whole-series absence, provider error, or unsupported response shape remains provider exclusion/acquisition error rather than synthesized fact.
- No values or actual/estimate/projection statuses are fabricated.

## Final accounting

Candidate cells: 342.

Non-overlapping accounting:

- observed/provider-valued facts: 339
- explicit-missing facts: 3
- provider exclusions: 0
- acquisition errors: 0
- total loaded facts: 342

Final PostgreSQL tuple:

```text
342|342|6|19|3|2|2|0|0|339|3
```

Meaning:

- staging rows: 342
- curated facts: 342
- indicators: 6
- territories: 19
- annual periods: 3
- lineage events: 2
- quality checks: 2
- failed quality checks: 0
- duplicate canonical-key groups: 0
- observed/provider-valued facts: 339
- explicit-missing facts: 3

## Architecture verdict

Existing revision-aware scalar architecture is sufficient. TASK-209 required no new forecast architecture. The final correction is a source-specific semantics reconciliation: absent year keys inside an otherwise valid country-indicator series are explicit-missing facts; they are not provider-valued observations and not provider exclusions.
