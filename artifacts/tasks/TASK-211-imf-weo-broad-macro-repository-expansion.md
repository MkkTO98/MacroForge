# TASK-211 — IMF WEO Broad Macro Repository Expansion

Status: complete
Date: 2026-07-11
Type: Phase 2 diverse-source macroeconomic repository expansion / IMF WEO annual current-release scalar campaign

Note: user prompt named this campaign TASK-210, but this working tree already contains completed `TASK-210-neutral-evidence-release-exporter-compatibility.md`. To preserve the existing completed TASK-210 and avoid artifact collision, this IMF WEO campaign is recorded as TASK-211.

## Precondition — TASK-209 preservation

Confirmed before implementation:

- `tools/task209_imf_weo_g20_projection_phase2_campaign.py` and `tests/test_task209_imf_weo_g20_projection_phase2_campaign.py` compile.
- `PYTHONPATH=src:. uvx pytest -q tests/test_task209_imf_weo_g20_projection_phase2_campaign.py` returned `7 passed`.
- TASK-209 artifacts remain present:
  - raw evidence SHA-256 `d9817f3fbf6cbaf3f58caaf438e20f0077c4cd1785db9505e49791925eebec5c`;
  - normalized artifact, manifest, provider report, load report, campaign report, and checksums exist.
- TASK-209 normalized counts remain: 342 candidate cells, 342 rows, 339 provider-valued facts, 3 explicit-missing facts, source `IMF_WEO_DATAMAPPER_API_V1`, release/run `world-economic-outlook-april-2026`.
- PostgreSQL compatibility query after TASK-211 still returned TASK-209 `342|342|339|3` for staging/facts/observed/missing.

## Exact analytical capability

Broad annual IMF WEO first-order macroeconomic current-release scalar repository capability for accepted canonical non-aggregate countries, covering historical years and current April 2026 WEO forecast horizon in one release/vintage.

Values are provider-supplied current-WEO scalar values. They are not classified as actual, estimate, or projection by calendar year because IMF DataMapper evidence did not expose row-level value status. Row attributes preserve `value_status = provider_current_weo_value_status_unspecified`.

## Candidate population

Frozen before value acquisition in:

`artifacts/reports/task-211-imf-weo-broad-macro-frozen-pre-execution-prediction.json`

Candidate universe:

- IMF provider countries in metadata: 241.
- Accepted canonical country candidates: 213, resolved through existing `curated.dim_territory` ISO3 country substrate.
- Provider aggregate entities classified separately: `ATI`, `ATL`.
- Unsupported/non-canonical provider entities classified separately: 26.
- Indicators: 12.
- Years: 2015-2028 inclusive, annual.
- Candidate cells before TASK-209 overlap exclusion: 35,784.
- Exact TASK-209 overlap excluded: 342 cells.
- Expected candidate cells after overlap exclusion: 35,442.

TASK-210/TASK-211 overlap policy: exact TASK-209 country-indicator-year cells were excluded from this broader campaign to avoid duplicate same-release facts while preserving TASK-209 semantics unchanged.

## Selected indicators and rationale

Selected IMF WEO indicators:

- `NGDP_RPCH` — real GDP growth;
- `NGDPD` — nominal GDP, current prices, billions of U.S. dollars;
- `NGDPDPC` — nominal GDP per capita, U.S. dollars;
- `PPPGDP` — PPP GDP, billions of international dollars;
- `PPPPC` — PPP GDP per capita;
- `PCPIPCH` — average CPI inflation;
- `LUR` — unemployment rate;
- `GGXCNL_NGDP` — general government net lending/borrowing, percent of GDP;
- `GGXWDG_NGDP` — general government gross debt, percent of GDP;
- `BCA` — current account balance, billions of U.S. dollars;
- `BCA_NGDPD` — current account balance, percent of GDP;
- `LP` — population, millions of people.

Rationale: first-order output, inflation, labor, fiscal balance/debt, external balance, population, and per-capita measures. The campaign deliberately did not ingest all WEO indicators.

## Acquisition and artifact publication

Implementation:

- Tool: `tools/task211_imf_weo_broad_macro_repository_expansion.py`.
- Tests: `tests/test_task211_imf_weo_broad_macro_repository_expansion.py`.

Atomic publication behavior:

- Value acquisition writes to attempt-specific raw directories under `data/raw/task211_imf_weo_broad_macro_repository_expansion/attempt-*`.
- Failed attempts are preserved and do not overwrite active artifacts.
- Successful active artifacts are promoted only after normalization, candidate reconciliation, zero unresolved acquisition errors, and manifest/report generation.
- Initial 213-country monolithic and 50-country chunk attempts produced provider 404 evidence and were preserved as failed attempts; 25-country chunks succeeded.

Active artifacts:

- Raw: `data/raw/task211_imf_weo_broad_macro_repository_expansion/active/task-211-imf-weo-broad-macro-2015-2028-raw.json` — 32,393,261 bytes, SHA-256 `3672b28bf4d92b941de90269e8ea50b737345d7489b506402a062afaa63d1f33`.
- Normalized: `data/processed/task211_imf_weo_broad_macro_repository_expansion/active/task-211-imf-weo-broad-macro-2015-2028-normalized.json` — 118,631,276 bytes, SHA-256 `c4c5746e89788db44534fdf911b375515d7088917b00ae8df2f63ae06ae824b8`.
- Manifest: `data/processed/task211_imf_weo_broad_macro_repository_expansion/active/task-211-imf-weo-broad-macro-2015-2028-manifest.json` — SHA-256 `ab304374927113db80a01fbce81e7ef126acfb5eeaf77904fe1001ff31dd4a76`.
- Checksums: `artifacts/reports/task-211-imf-weo-broad-macro-artifact-checksums.txt`.

## Result counts

Candidate reconciliation:

- Candidate cells after TASK-209 overlap exclusion: 35,442.
- Loaded rows/facts: 31,074.
- Provider-valued facts: 30,539.
- Explicit-missing facts: 535.
- Provider-excluded cells: 4,368.
- Provider exclusions: 312 whole country-indicator series absent after valid chunk acquisition.
- Acquisition errors in promoted active artifact: 0.
- Reconciliation total: 31,074 loaded rows + 4,368 provider-excluded cells = 35,442 candidate cells.

Loaded coverage:

- Loaded territories: 194.
- Loaded indicators: 12.
- Loaded annual periods: 14, 2015-2028.

## Source, dataset, release, run identities

Canonical source identity reused:

- `IMF_WEO_DATAMAPPER_API_V1`.

Dataset/release identities:

- TASK-209 remains `IMF:WEO:DATAMAPPER:PROJECTIONS | world-economic-outlook-april-2026`.
- TASK-211 adds `IMF:WEO:DATAMAPPER:BROAD_MACRO_ANNUAL | world-economic-outlook-april-2026`.

Run identity:

- `task-211-imf-weo-broad-macro-repository-expansion-world-economic-outlook-april-2026`.

Release identity was derived from provider indicator metadata: `World Economic Outlook (April 2026)`. API version evidence is preserved from DataMapper payload metadata. Exact publication date remains unavailable in provider evidence and is not inferred.

## PostgreSQL verification

Latest idempotence report:

```text
staging_rows=31074
fact_rows=31074
indicator_count=12
territory_count=194
period_count=14
lineage_events=2
quality_checks=3
failed_quality_checks=0
observed_facts=30539
missing_facts=535
duplicate_canonical_key_groups=0
release_identity_rows=1
idempotent=True
```

PostgreSQL total after idempotent rerun: 10,594,305 curated fact rows. Since this run contributes 31,074 run-scoped facts, the implied pre-TASK-211 total was 10,563,231 facts.

Source/release query returned:

```text
IMF_WEO_DATAMAPPER_API_V1|IMF:WEO:DATAMAPPER:BROAD_MACRO_ANNUAL|world-economic-outlook-april-2026|1
IMF_WEO_DATAMAPPER_API_V1|IMF:WEO:DATAMAPPER:PROJECTIONS|world-economic-outlook-april-2026|1
```

## Prediction evaluation

Prediction quality: Mostly Accurate.

- Candidate scale prediction was exact after preflight: 35,442 expected candidate cells and 35,442 reconciled candidate cells.
- Provider-valued prediction was accurate: expected roughly 30,000-35,000; actual 30,539.
- Missingness prediction was directionally mixed: explicit missing was lower than expected at 535 loaded missing facts, while 4,368 cells became whole-series provider exclusions.
- Provider behavior surprise: IMF DataMapper returned 404 for overly broad URL chunks; bounded 25-country chunking resolved transport fragility. This is implementation friction, not architecture contradiction.
- Territory surprise: 213 canonical country candidates became 194 loaded territories because 312 country-indicator series were absent from provider values and classified as provider exclusions.
- Unit/release surprise: selected `NI_GDP` was rejected before value acquisition because provider metadata showed AFR Regional Economic Outlook rather than WEO; `BCA` replaced it before frozen value acquisition so the final frozen prediction remained WEO-only.

## TASK-209/TASK-211 repeated implementation evidence

Repeated WEO-specific responsibilities occurred in both TASK-209 and TASK-211:

- release key derivation from provider `World Economic Outlook (April 2026)` metadata;
- source/dataset/release/run identity separation;
- source-scoped indicator/unit semantics;
- explicit missingness for absent/null year keys inside valid country-indicator series;
- same-release idempotent loading;
- later-release coexistence regression using simulated October 2026 metadata;
- raw checksum and lineage preservation.

TASK-211 additionally exposed recurring source-specific acquisition/promotion friction:

- DataMapper URL chunk size matters; 25-country chunks succeeded where larger URLs returned 404.
- Attempt-specific raw directories are necessary to keep failed acquisition evidence from overwriting active evidence.

## Structural extraction verdict

Implemented extraction: no new shared framework or generic provider engine.

What matured inside the WEO-specific script:

- deterministic release-key helper;
- WEO value-status convention;
- WEO indicator/unit semantic preservation;
- WEO attempt isolation and active promotion;
- WEO candidate reconciliation including provider-excluded cells.

Rejected extractions:

- generic provider framework — rejected; evidence is source-specific DataMapper behavior.
- universal campaign engine — rejected; chunking/promotion pressure is not yet cross-provider enough.
- forecast ontology — rejected; provider did not expose row-level actual/estimate/projection status.
- canonical territory architecture expansion — rejected; unsupported/absent provider entities were classifiable without changing canonical territory substrate.

## TASK-211 remediation before acceptance

A bounded remediation corrected the TASK-209/TASK-211 WEO substrate before acceptance:

- canonical WEO provider dataset identity consolidated to `IMF:WEO:DATAMAPPER`;
- TASK-209 and TASK-211 retain distinct run identities under the shared April 2026 release;
- narrow WEO/DataMapper substrate extracted in `src/macroforge/imf_weo_datamapper.py` for repeated source-specific responsibilities only;
- TASK-211 normalized active evidence replaced by 12 deterministic indicator partitions;
- TASK-209/TASK-211 staging upserts now refresh `dataset_release_id` and mutable provenance fields during corrected reruns;
- obsolete campaign-specific dataset-release rows were deleted only after zero external references were verified.

Post-delete PostgreSQL verification:

```text
obsolete dataset_release rows: 0
canonical IMF:WEO:DATAMAPPER April 2026 release rows: 1
canonical TASK-209/TASK-211 staging refs: 31,416
TASK-209 facts/observed/missing: 342/339/3
TASK-211 facts/observed/missing: 31,074/30,539/535
duplicate canonical-key groups: 0
repository fact total: 10,594,305
```

Cleanup evidence:

- `artifacts/reports/task-211-weo-dataset-release-cleanup-predelete-audit.json`
- `artifacts/reports/task-211-weo-dataset-release-cleanup-predelete-audit-after-loader.json`
- `artifacts/reports/task-211-weo-dataset-release-cleanup-diagnostic.md`
- `artifacts/reports/task-211-weo-dataset-release-cleanup-execution-audit.json`
- `artifacts/reports/task-211-weo-dataset-release-cleanup-execution-summary.json`

## Architecture-to-reality verdict

Supported / reaffirmed:

- current scalar fact identity preserved WEO releases through `dataset_release_id` and release-specific run keys;
- units and source-scoped indicators prevented semantic collisions between levels/growth/rates/ratios/per-capita measures;
- explicit missingness remained deterministic for valid country-indicator series;
- source/dataset/release/run separation remained coherent;
- PostgreSQL loading remained idempotent with 0 duplicate canonical-key groups;
- forecast-value limitations remained visible via `provider_current_weo_value_status_unspecified`;
- WDI overlap did not create canonical ambiguity because WEO indicators remain source-scoped and release-scoped.

Partially challenged but not contradicted:

- territory mapping beyond the G20: canonical ISO3 territory substrate scaled, but provider WEO coverage is sparser than canonical country coverage. This is provider availability evidence, not a canonical mismatch.
- raw/normalized artifact scale: active artifacts are large but manageable; future broader WEO campaigns should keep chunking and may need slimmer normalized reports if artifact size grows.

No architecture contradiction or redesign trigger appeared.

## Verification

Completed:

```text
python3 -m py_compile tools/task209_imf_weo_g20_projection_phase2_campaign.py tests/test_task209_imf_weo_g20_projection_phase2_campaign.py
PYTHONPATH=src:. uvx pytest -q tests/test_task209_imf_weo_g20_projection_phase2_campaign.py
# 7 passed

python3 -m py_compile tools/task211_imf_weo_broad_macro_repository_expansion.py tests/test_task211_imf_weo_broad_macro_repository_expansion.py
PYTHONPATH=src:. uvx pytest -q tests/test_task211_imf_weo_broad_macro_repository_expansion.py
# 6 passed

PYTHONPATH=src:. uvx pytest -q tests/test_task211_imf_weo_broad_macro_repository_expansion.py tests/test_task209_imf_weo_g20_projection_phase2_campaign.py tests/test_imf_weo_projections.py tests/test_imf_iip_g7_operational.py tests/test_imf_bop_g7_operational.py tests/test_imf_mfs_ir_operational.py tests/test_wdi_loader.py
# 42 passed

JSON validation over TASK-211 prediction/raw/normalized/manifest/report artifacts
# json-ok

TASK-211 PostgreSQL idempotence
# idempotent=True, duplicate_canonical_key_groups=0, failed_quality_checks=0

PYTHONPATH=src:. uvx pytest -q > artifacts/reports/task-211-full-suite.log 2>&1
# 763 passed, 1 skipped in 865.31s (0:14:25)

python3 tools/context_health.py
# context health: 0 block(s), 1 warning(s) — state/architecture.md approaching context-health limit

python3 tools/check_coherence.py
# coherence: 0 block(s), 1 warning(s) — same architecture-size warning

python3 tools/architecture_reality_audit.py
# architecture-reality-audit: 0 block(s), 0 warning(s)

git diff --check
# passed
```

## Scope protection

- Did not call BLS.
- Did not resume TASK-208.
- Did not modify TASK-207 FRED-detour files.
- Did not start trade, company, or financial-asset ingestion.
- Did not commit or push.

## Recommendation

WEO can scale further, but not by blindly ingesting all indicators. The next WEO step should either:

1. add a second coherent WEO family where provider metadata confirms WEO source identity, or
2. pause WEO and advance another macroeconomic provider if a larger first-order gap is higher value.

Architecture reconsideration is not required from TASK-211 evidence.
