# TASK-209 Forecast-Vintage and Decision-Evidence Integrity Audit

Date: 2026-07-11
Status: complete

## Scope

Bounded integrity audit before committing TASK-209. No TASK-210 work. No BLS/TASK-208 calls. No FRED-detour work.

## Release / vintage evidence

Preserved raw artifact:

- `data/raw/task209_imf_weo_g20_projection_phase2_campaign/task-209-imf-weo-g20-projections-2026-2028.json`
- acquisition timestamp: `2026-07-11T13:29:29+00:00`
- API surface: IMF DataMapper API
- API version in response payloads: `1`
- metadata URLs:
  - `https://www.imf.org/external/datamapper/api/v1/indicators`
  - `https://www.imf.org/external/datamapper/api/v1/countries`

Exact provider edition evidence preserved in indicator metadata:

- `source`: `World Economic Outlook (April 2026)` for all six indicators.
- indicator `last-modified` values:
  - `2026-04-08 16:07:34`
  - `2026-04-08 16:07:35`
  - `2026-04-08 16:07:39`
  - `2026-04-08 16:07:42`
  - `2026-04-08 16:07:43`
  - `2026-04-08 16:07:44`

Provider publication/release date:

- Not directly exposed in the preserved DataMapper API payload.
- Strongest preserved release/as-of evidence is the provider source string `World Economic Outlook (April 2026)`, indicator last-modified timestamps, and acquisition timestamp.

Deterministic release key after correction:

- `world-economic-outlook-april-2026`

The raw artifact is sufficient to reproduce which WEO edition string was acquired and when it was acquired. It is not sufficient to establish an exact IMF publication date beyond the provider source string and last-modified timestamps.

## Value-status semantics

The preserved DataMapper payload does not expose row-level actual/estimate/projection status for the 2026-2028 values.

Corrected status treatment:

- `curated.fact_observation.observation_status` remains `observed` because the row is an observed provider-supplied scalar fact under the existing database constraint.
- Row attributes preserve `value_status = provider_current_weo_value_status_unspecified`.
- The final report must not describe these values as observed economic outcomes.
- Honest status finding: provider-supplied current-WEO scalar values with row-level actual/estimate/projection status unspecified by preserved API evidence.

## Revision / vintage behavior

Pre-audit implementation mismatch:

- TASK-209 used a hardcoded release key and a fixed run key.
- A later WEO edition would have risked same-run overwrite behavior instead of clean release/run coexistence.
- Classification: implementation mismatch, not architecture contradiction.

Correction applied:

- Source identity remains `IMF_WEO_DATAMAPPER_API_V1`.
- Dataset/release identity is distinct from source identity.
- Release key is derived from provider edition metadata: `world-economic-outlook-april-2026`.
- Run key is release-specific: `task-209-imf-weo-g20-projection-phase2-world-economic-outlook-april-2026`.
- Dataset release metadata preserves release evidence.
- Same-release reruns are idempotent.
- Simulated later release regression proves `World Economic Outlook (October 2026)` maps to `world-economic-outlook-october-2026` and a distinct run key.
- Legacy pre-correction TASK-209 run/release rows were removed only after verifying 0 fact/staging/lineage/quality references.

Architecture verdict: existing revision-aware scalar substrate is sufficient; no new forecast architecture is justified.

## Indicator and unit semantics

| Provider/canonical id | Subject | Unit | Scale / measure type | Frequency |
| --- | --- | --- | --- | --- |
| `NGDP_RPCH` / `IMF_WEO:NGDP_RPCH` | Real GDP growth; GDP at constant prices | Annual percent change | percentage change | annual |
| `NGDPD` / `IMF_WEO:NGDPD` | GDP at current prices | Billions of U.S. dollars | currency amount | annual |
| `PCPIPCH` / `IMF_WEO:PCPIPCH` | Average CPI inflation rate | Annual percent change | percentage change | annual |
| `LUR` / `IMF_WEO:LUR` | Unemployment rate | Percent | percentage rate | annual |
| `GGXCNL_NGDP` / `IMF_WEO:GGXCNL_NGDP` | General government net lending/borrowing | Percent of GDP | ratio | annual |
| `GGXWDG_NGDP` / `IMF_WEO:GGXWDG_NGDP` | General government gross debt | Percent of GDP | ratio | annual |

Collision protection:

- Provider indicator code is source-scoped in `curated.dim_indicator`.
- Unit is stored separately in `curated.dim_unit` and fact keys include `unit_id`.
- Attribute hashes include provider release key, provider indicator id, canonical indicator id, unit semantics, and status limitation.
- Regression coverage checks that semantically different units/measures remain distinct.

## Frozen prediction and outcome

Frozen pre-execution prediction now preserved in the campaign report:

- expected observation scale: approximately 342 candidate cells;
- expected coverage: 19 G20 countries excluding EU aggregate, 6 WEO indicators, 2026-2028;
- expected provider risks: possible missing country/indicator/year values or sparse WEO coverage; low transport risk from proven IMF DataMapper path;
- expected architectural compatibility: existing scalar fact substrate plus dataset release should represent one WEO forecast vintage without redesign;
- expected implementation friction: low to moderate; source-specific normalization and loader required.

Actual result:

- 342 candidate cells; 339 provider-supplied scalar values loaded;
- 3 provider-missing Saudi Arabia `LUR` cells for 2026-2028;
- 0 acquisition errors;
- implementation needed a narrow release/vintage correction before commit.

Prediction verdict: Mostly Accurate.

Reason IMF WEO was selected:

- It added official non-BLS macroeconomic projection/release evidence from a proven IMF provider path.
- It stayed outside deferred trade, company, and financial-asset scopes.
- It tested forecast-vintage/release discipline that WDI annual-scalar and BLS monthly labor breadth do not cover.

## Final capability wording

TASK-209 is a bounded IMF WEO G20 projection capability proof. It should not be described as broad forecast infrastructure or as observed economic outcomes.

## Corrected database result

Final run-scoped tuple:

```text
342|342|6|19|3|2|2|0|0|339|3
```

Meaning: staging rows, curated facts, indicators, territories, annual periods, lineage events, quality checks, failed quality checks, duplicate canonical-key groups.
