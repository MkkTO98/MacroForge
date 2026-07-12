# TASK-213 — BIS CBPOL Policy-Rate Phase 2 Repository Expansion

Status: complete, corrected, verified, not committed
Date: 2026-07-12
Type: Phase 2 diverse-source macroeconomic repository expansion / BIS monthly monetary-policy scalar campaign

## Task ID selection

Repository inspection showed TASK-211 and TASK-212 already occupied. The next unoccupied task ID was TASK-213.

## Selected BIS dataset and capability

Selected dataset: `BIS:WS_CBPOL` (`dataflow/BIS/WS_CBPOL/1.0`).

Capability: broad cross-country monthly central-bank policy-rate repository evidence for monetary-policy stance and financial-condition analysis.

This was the strongest next Phase 2 target because TASK-057 had already proven a bounded BIS WS_CBPOL path, the Capability Atlas still showed monetary policy/market-rates as established but not broad or operationally cross-country, and WS_CBPOL could scale materially without combining unrelated BIS families or opening trade/company/asset-market ingestion.

## Frozen prediction and correction

Frozen prediction was recorded before acquisition in:

`artifacts/reports/task-213-bis-cbpol-policy-rate-frozen-pre-execution-prediction.json`

Original prediction summary:

- Dataset: `BIS:WS_CBPOL`.
- Candidate countries: 36 accepted countries.
- Frequency: monthly.
- Periods: 2015-M01 through 2026-M06, 138 months.
- Expected cells: 4,968.
- Expected provider-valued/explicit-missing cells: 4,900-4,968.
- Expected unit: percent, provider `UNIT_MEASURE=368`, `UNIT_MULT=0`.
- Expected exclusions: `XM` aggregate, `HK` non-sovereign.
- Expected architecture: existing monthly scalar substrate should suffice.

Bounded pre-commit correction found two modelling errors in the first completion:

1. Indicator identity was over-specific: `REF_AREA` was redundantly encoded in both territory identity and indicator identity.
2. Hong Kong was incorrectly classified outside the accepted candidate grid even though canonical territory `HKG` / Hong Kong SAR already existed in PostgreSQL.

Prediction-quality verdict after correction: Mixed. Scale/provider-behavior prediction was close, but identity modelling and Hong Kong selection were wrong.

## Exact corrected candidate universe

Accepted BIS reference areas:

`AU`, `BR`, `CA`, `CH`, `CL`, `CN`, `CO`, `CZ`, `DK`, `GB`, `HU`, `HK`, `ID`, `IL`, `IN`, `IS`, `JP`, `KR`, `KW`, `MA`, `MK`, `MX`, `MY`, `NO`, `NZ`, `PE`, `PH`, `PL`, `RO`, `RS`, `RU`, `SA`, `SE`, `TH`, `TR`, `US`, `ZA`.

Selection exclusions:

- `XM`: aggregate selection exclusion, deliberately outside the country/territory candidate grid.

Unsupported entities:

- none.

Mapping failures:

- none.

Provider exclusions / acquisition errors:

- provider exclusions: 0.
- acquisition errors in promoted active artifacts: 0.

Grid:

- 37 accepted territories x 138 monthly periods x 1 BIS policy-rate measure = 5,106 candidate cells.

## Corrected results

Candidate reconciliation:

- Candidate cells: 5,106.
- Loaded rows/facts: 5,106.
- Provider-valued facts: 5,082.
- Explicit missing facts: 24, represented in PostgreSQL as `observation_status='missing'` with source attributes preserving explicit candidate-grid absence.
- Whole-series absence for selected territories: 0.
- Provider exclusions: 0.
- Acquisition errors in promoted active artifacts: 0.
- Incompatible dimensional series: 0.

Coverage:

- Territories loaded: 37.
- Canonical source-scoped indicator identities loaded for this run: 1.
- Canonical indicator identity: `BIS:WS_CBPOL:CENTRAL_BANK_POLICY_RATE:PERCENT:M`.
- Periods: 138 monthly periods, 2015-M01 through 2026-M06.
- Unit: percent.
- Dimensions/attributes preserved: `FREQ`, `REF_AREA`, `TIME_PERIOD`, `SOURCE_REF`, `COMPILATION`, `DECIMALS`, `TITLE`, `OBS_STATUS`, `OBS_CONF`, provider unit attributes, provider series key, snapshot release key, provider prepared timestamp, and raw checksum.

## Canonical indicator-identity verdict

All selected BIS WS_CBPOL series represent the same provider-defined central-bank policy-rate measure:

- measure: `central_bank_policy_rate`
- frequency: monthly (`M`)
- unit: percent (`UNIT_MEASURE=368`, `UNIT_MULT=0`)

`REF_AREA` is a territory dimension, not a measure distinction. The corrected canonical indicator identity is therefore independent of territory:

`BIS:WS_CBPOL:CENTRAL_BANK_POLICY_RATE:PERCENT:M`

Country/territory-specific `TITLE`, `SOURCE_REF`, `COMPILATION`, decimals, observation status, confidentiality, provider series key, and provider territory identifier are preserved as attributes/source payload, not as separate canonical indicators.

Regression tests prove:

- territory changes do not create another indicator;
- measure/unit/frequency changes still produce distinct identities;
- cross-country retrieval can use one canonical policy-rate indicator plus territory.

## Corrected snapshot/release identity

The original release key `bis-ws-cbpol-current-snapshot-2015m01-2026m06` was derived from the requested observation window and was not a stable provider snapshot identity.

Corrected release key:

`bis-ws-cbpol-snapshot-prepared-20260712t114554z`

Derivation:

- provider prepared timestamp from active raw evidence: `2026-07-12T11:45:54Z`;
- raw checksum preserved in release metadata and row attributes;
- requested start/end periods are retained in request metadata and run input filters, not in release identity.

A different query window against the same provider prepared timestamp maps to the same release key. A later prepared timestamp maps to a distinct release key and can coexist.

No BIS publication date was fabricated; `meta.dataset_release.release_date` is loaded as `NULL` for the corrected snapshot because the provider evidence supplied a prepared timestamp, not a publication date.

## Artifacts

Raw:

- `data/raw/task213_bis_cbpol_policy_rate_phase2_campaign/active/task-213-bis-cbpol-policy-rate-2015m01-2026m06-raw.xml`
- `data/raw/task213_bis_cbpol_policy_rate_phase2_campaign/active/task-213-bis-cbpol-policy-rate-2015m01-2026m06-raw-metadata.json`

Processed:

- `data/processed/task213_bis_cbpol_policy_rate_phase2_campaign/active/task-213-bis-cbpol-policy-rate-normalized.json`
- `data/processed/task213_bis_cbpol_policy_rate_phase2_campaign/active/task-213-bis-cbpol-policy-rate-manifest.json`

Reports:

- `artifacts/reports/task-213-bis-cbpol-policy-rate-frozen-pre-execution-prediction.json`
- `artifacts/reports/task-213-bis-cbpol-policy-rate-provider-evidence-report.json`
- `artifacts/reports/task-213-bis-cbpol-policy-rate-postgresql-load-report.json`
- `artifacts/reports/task-213-bis-cbpol-policy-rate-prediction-evaluation.json`
- `artifacts/reports/task-213-bis-cbpol-policy-rate-artifact-checksums.txt`
- `artifacts/reports/task-213-bis-cbpol-policy-rate-load.sql`

## Raw and processed artifact sizes

Corrected active artifact sizes from filesystem/checksum reports:

- Raw XML: 415,944 bytes.
- Raw metadata JSON: 1,240 bytes.
- Normalized JSON: 12,027,452 bytes.
- Manifest JSON: 1,546 bytes.

## Canonical identities

- Source: `BIS_PUBLIC_SDMX_API`.
- Provider dataset: `BIS:WS_CBPOL`.
- Snapshot/release key: `bis-ws-cbpol-snapshot-prepared-20260712t114554z`.
- Run key: `task-213-bis-cbpol-policy-rate-phase2`.
- Canonical indicator: `BIS:WS_CBPOL:CENTRAL_BANK_POLICY_RATE:PERCENT:M`.

Source identity deliberately represents the BIS public SDMX API. Dataset identity represents BIS WS_CBPOL. Snapshot identity represents the provider prepared snapshot. Campaign scope lives in run metadata and artifacts.

## PostgreSQL corrected results

Corrected run-scoped verification:

- Staging rows: 5,106.
- Fact rows: 5,106.
- Observed facts: 5,082.
- Explicit missing facts: 24.
- Indicators: 1.
- Territories: 37.
- Periods: 138.
- Lineage events: 2.
- Quality checks: 3.
- Failed quality checks: 0.
- Duplicate canonical-key groups: 0.
- Canonical source rows: 1.
- Corrected BIS WS_CBPOL snapshot rows: 1.
- Obsolete window-bound BIS WS_CBPOL snapshot rows: 0 after authorized bounded cleanup.
- Obsolete country-encoded `BIS:WS_CBPOL:M.%` indicator rows: 0 after authorized bounded cleanup.

Same-run idempotence rerun produced zero repository growth.

Later-snapshot coexistence simulation inserted one hypothetical later `BIS:WS_CBPOL` snapshot inside a transaction and rolled back successfully, proving coexistence without overwriting the corrected snapshot.

## Obsolete metadata audit and cleanup

Authorized bounded pre-publication cleanup was performed after complete reference audits passed. Audit artifact: `artifacts/reports/task-213-bis-cbpol-metadata-cleanup-reference-audit.json`. Post-cleanup verification artifact: `artifacts/reports/task-213-bis-cbpol-metadata-cleanup-post-verification.json`.

Pre-delete reference audit:

- Legacy window-bound release `bis-ws-cbpol-current-snapshot-2015m01-2026m06`:
  - resolved dataset release rows: 1
  - external `dataset_release_id` references across discovered relations: 0
  - fact references: 0
  - staging references: 0
  - pipeline-run references: 0
  - provider-code-list references: 0
- Legacy country-encoded indicators `BIS:WS_CBPOL:M.%`:
  - resolved indicator rows: 36
  - external `indicator_id` references across discovered relations: 0
  - external exact-code occurrences outside `curated.dim_indicator`: 0
  - fact references: 0

Cleanup transaction deleted exactly one obsolete dataset-release row and exactly 36 obsolete indicator rows. No curated facts, staging rows, canonical source, canonical snapshot, canonical indicator, run, lineage, or quality rows were deleted.

## TASK-057 / TASK-213 repeated evidence

Repeated responsibilities:

- BIS WS_CBPOL StructureSpecificData parsing.
- BIS dataflow identity preservation.
- BIS reference-area handling.
- Series-level metadata preservation (`SOURCE_REF`, `COMPILATION`, `DECIMALS`, `TITLE`).
- Observation-level status/confidentiality preservation.
- Source-specific policy-rate identity construction.
- Provider-prepared snapshot release-key derivation.

No shared extraction was performed. The repeated work is real, but the stable boundary remains BIS WS_CBPOL-specific and is not yet evidence for a generic BIS client, universal SDMX adapter, financial-data ontology, or campaign engine. TASK-213 remains a source-specific campaign script.

## Architecture-to-reality verdict

Reaffirmed, with corrected semantics.

The existing scalar monthly fact substrate preserved source/dataset/snapshot/run separation, unit identity, territory identity, period identity, lineage, quality checks, canonical duplicate prevention, and same-run idempotence. WS_CBPOL did not expose a dimensional repository-class mismatch.

The correction improved semantic identity: `REF_AREA` is now represented by territory identity and attributes, not duplicated in the canonical indicator identity.

BIS should scale further only within one coherent family at a time. The next BIS candidate should likely be property prices or credit/debt-service measures if provider dimensions can be represented without flattening. Phase 2 can also move to another macroeconomic provider when the goal is broader domain diversity; this campaign does not require architectural reconsideration.

## Verification

Completed after correction:

- Focused TASK-213 + TASK-057 BIS compatibility + cleanup invariant tests: `19 passed in 0.57s`.
- Full suite: `802 passed in 845.70s (0:14:05)`.
- PostgreSQL post-cleanup verification: staging/facts `5106/5106`; provider-valued/explicit-missing `5082/24`; territories/periods `37/138`; HK facts `138`; failed quality checks `0`; duplicate canonical-key groups `0`; repository total fact count unchanged by cleanup; same-run idempotence repository growth `0`.
- Source/dataset/snapshot verification after cleanup: canonical BIS source rows `1`; canonical `BIS:WS_CBPOL` snapshot rows `1`; obsolete window-bound snapshot rows `0`.
- Indicator identity verification after cleanup: canonical policy-rate indicator rows `1`; obsolete country-encoded indicator rows `0`.
- JSON validation/checksum reconciliation: `json_validated=9 checksum_entries=9 checksum_mismatches=0`.
- Governance: coherence `0 block(s), 0 warning(s)`; context health `0 block(s), 0 warning(s)`; architecture-reality audit `0 block(s), 0 warning(s)`; `git diff --check` exit `0`.
- Later-snapshot coexistence simulation: `later_snapshot_simulation_rows|1`, rolled back.
