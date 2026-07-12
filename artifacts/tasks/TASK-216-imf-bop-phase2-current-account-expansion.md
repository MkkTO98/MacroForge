# TASK-216 — IMF BOP Phase 2 current-account repository expansion

Status: complete; final full-suite and governance closeout verified in this session.

## Scope and protection

TASK-216 was selected as the next unoccupied task ID after repository inspection found maximum existing task artifact `TASK-215` and no existing `TASK-216` task artifact.

Scope protections followed:

- Did not reopen BIS, BLS, WEO, FRED-detour, trade, company, or financial-asset ingestion.
- Did not stage, commit, push, clean, restore, move, or delete files.
- Existing unrelated working-tree changes are preserved and remain outside the TASK-216 bounded file set.

## Selected BOP capability

Capability: annual IMF Balance of Payments current-account monitoring capability across a broad canonical country population.

Selected family:

- Current account balance (`CAB`)
- Goods (`G`)
- Services (`S`)
- Primary income (`IN1`)
- Secondary income (`IN2`)

All selected series use:

- Accounting entry: `NETCD_T` = net credit less debit
- Unit: `USD`
- Scale: `6` = millions
- Frequency: annual (`A`)
- Period range: 2010 through 2024

Rationale: current-account balances and components are first-order external-sector and external-vulnerability evidence. This is stronger than another BIS campaign or a small provider proof because recent repository work already had multiple BIS Phase 2 campaigns, while broad IMF BOP current-account coverage materially complements existing financial-account/IIP/reserves/WDI external evidence.

## Provider structure investigated

Provider/API:

- IMF external SDMX 2.1 API
- Metadata URL: `https://api.imf.org/external/sdmx/2.1/dataflow/all/BOP/latest?references=all`
- Data URL pattern: `https://api.imf.org/external/sdmx/2.1/data/BOP/{countries}.NETCD_T.{indicators}.USD.A?startPeriod=2010&endPeriod=2024`

Provider dataset and versions:

- Canonical source identity: `IMF_SDMX_BOP_API_V1`
- Provider dataset identity: `IMF:BOP`
- Dataflow: `BOP`, version `21.0.0`
- Data structure: `BOP`, version `24.0.0`

Complete selected series-key dimensions:

- `COUNTRY`
- `BOP_ACCOUNTING_ENTRY`
- `INDICATOR`
- `UNIT`
- `FREQUENCY`

Provider attributes preserved in normalized evidence include dataset/header metadata, series attributes such as `SCALE`, `METHODOLOGY`, `IFS_FLAG`, and observation attributes such as `DERIVATION_TYPE`, `PRECISION`, `OBS_STATUS`, access/security metadata where present.

## Frozen candidate universe

Frozen before value acquisition in `artifacts/reports/task-216-imf-bop-frozen-pre-execution-prediction.json`.

Universe:

- Accepted territories: 214 canonical country ISO3 codes advertised by IMF BOP metadata.
- Selected components: 5 current-account/current-account-component indicators.
- Periods: 15 annual periods, 2010-2024.
- Exact provider-advertised series: 1,070.
- Expected candidate cells: 16,050.

Frozen predictions:

- Expected provider-valued facts: 14,445.
- Expected explicit-missing facts: 802.
- Expected whole-series absence remainder: 803 candidate cells equivalent.
- Expected mapping failures: 0.
- Expected incompatible series: 0.
- Expected acquisition errors: 0.
- Expected PostgreSQL growth: observed plus explicit-missing rows only.
- Expected scalar compatibility: compatible if all non-territory BOP dimensions are retained in the source-scoped indicator identity/attributes.

## Acquisition and artifact publication

Implementation: `tools/task216_imf_bop_phase2_campaign.py`.

Acquisition behavior:

- Metadata response preserved under `data/raw/task216_imf_bop_phase2_campaign/active/`.
- Value acquisition used nine deterministic country chunks to bound URL length and transport risk.
- Exact source URLs, request parameters, headers, timestamps, content types, raw byte counts, and SHA-256 hashes are preserved in raw JSON sidecars.
- Attempt-specific directories are retained under `data/raw/task216_imf_bop_phase2_campaign/_attempts/`; active artifacts are promoted only after successful acquisition/normalization.
- Unresolved acquisition errors: 0.

Artifact scale:

- Active raw artifacts total: 6,238,209 bytes.
- Active processed artifacts total: 27,844,455 bytes.
- TASK-216 report artifacts total: 18,108,828 bytes.

## Results

Actual candidate reconciliation:

- Candidate cells: 16,050.
- Provider-valued facts: 13,600.
- Explicit-missing facts: 875.
- Whole-series absence: 105 series = 1,575 candidate cells.
- Loaded rows: 14,475 = observed plus explicit-missing facts.
- Incompatible series: 0.
- Acquisition errors: 0.

Territory/frequency/temporal coverage:

- Frozen accepted territories: 214.
- Territories with loaded observed/missing facts: 193.
- Period coverage in facts: 15 annual periods, 2010-2024.
- Frequency: annual.
- Unit: `USD_SCALE_6` / US dollars, millions.

Provider exclusions/classification:

- Provider aggregates were classified separately from accepted countries in the provider-structure report.
- Unsupported/non-sovereign/unknown provider codes are preserved as metadata partitions and not silently remapped.
- Whole-series absences are distinct from explicit missing observations and acquisition failures.

## Canonical identities

- Source: `IMF_SDMX_BOP_API_V1`
- Provider dataset: `IMF:BOP`
- Provider-derived as-of/release key: `imf-bop-asof-20260711t231424302015100z`
- Run: `task-216-imf-bop-current-account-phase2`
- Pipeline: `imf_bop_current_account_phase2_campaign`

Release/as-of identity is derived from provider response metadata (`Prepared`/dataset metadata evidence), not from query-window bounds. Campaign scope is in run metadata.

## PostgreSQL verification

First successful load:

- PostgreSQL growth: 14,475 facts.

Current verified run-scoped counts:

- Source rows for canonical BOP source: 1.
- Dataset release rows for selected as-of key: 1.
- Staging rows: 14,475.
- Curated fact rows: 14,475.
- Observed facts: 13,600.
- Explicit-missing facts: 875.
- Source-scoped indicators: 5.
- Loaded territories: 193.
- Periods: 15.
- Failed quality checks: 0.
- Duplicate canonical key groups: 0.

Idempotence/coexistence:

- Same-run idempotence reload verified: second load PostgreSQL growth 0, facts remained 14,475.
- Same-release idempotence uses `(source_id, provider_dataset_code, release_key)`.
- Simulated later snapshot coexistence verified with release key `imf-bop-asof-simulated-later-snapshot-task216`; two BOP as-of release rows coexist for `IMF_SDMX_BOP_API_V1` / `IMF:BOP`.

## Prediction evaluation

Verdict: Mostly Accurate.

- Candidate scale prediction: accurate, 16,050 expected and actual candidate cells.
- Provider-valued prediction: high by 845 facts (14,445 expected vs 13,600 actual).
- Missingness prediction: explicit missing was close directionally but under by 73 facts (802 expected vs 875 actual); whole-series absence was larger than expected.
- Provider behavior surprise: country chunking worked, but the provider returned whole-series absences for more country/component pairs than expected rather than explicit null observations.
- Territory/unit surprise: no selected-unit incompatibility; BOP provider territory catalogue is broader than canonical accepted countries and remains partitioned.
- Implementation friction: moderate-high, as predicted, due to identity correction, whole-series absence classification, and loader schema alignment.
- Source understanding gap: provider coverage by current-account component is less dense than assumed for a broad accepted-country universe.

## IMF-BOP extraction decision

No shared IMF-BOP-specific substrate was extracted.

Repeated responsibilities exist across earlier bounded BOP work and TASK-216: SDMX metadata parsing, series-key preservation, BOP component labels, and source/dataset/release identity discipline.

Extraction was rejected for this task because earlier bounded implementations used campaign-specific source identities and TASK-216 corrected the canonical identity boundary. Extracting now would risk freezing drift before one more BOP/IIP relationship campaign confirms stable responsibilities. No generic IMF framework, SDMX adapter, accounting ontology, campaign engine, or multidimensional schema was created.

## Architecture-to-reality verdict

Verdict: current scalar/revision-aware substrate remains compatible for this selected BOP current-account family.

Pressure-test outcomes:

- Scalar fact identity preserved BOP as-of/release evidence through dataset release identity.
- Units participate in semantic identity via `USD_SCALE_6` and indicator code/unit dimension preservation.
- Territory mapping scaled beyond G7/G20, with accepted countries, aggregates, unsupported entities, and unknown/unmapped provider codes separated.
- Explicit missing generation remained deterministic at scale.
- Source/dataset/release/run separation remained coherent after correcting canonical source identity to the actual BOP API.
- Raw evidence and atomic active-artifact promotion scaled with chunked acquisition.
- PostgreSQL loading remained performant and idempotent after schema-alignment fixes.
- Forecast limitations are not relevant to selected BOP historical/current annual flow observations, but provider value status remains `provider_bop_value_status_unspecified`.
- Overlap with WDI external-balance concepts is semantic complementarity, not collision: IMF BOP source-scoped component/unit/accounting-entry semantics remain distinct.

No architecture reopening is recommended from TASK-216 evidence.

## Identity/artifact/governance closeout audit

Closeout audit report: `artifacts/reports/task-216-imf-bop-identity-artifact-governance-closeout.json`.

Source identity verdict: `IMF_SDMX_BOP_API_V1` is the canonical source designation for the IMF external SDMX 2.1 BOP API/source boundary, not TASK-216 campaign scope. Base endpoint is `https://api.imf.org/external/sdmx/2.1/`; TASK-216 used metadata endpoint `dataflow/all/BOP/latest?references=all` and value endpoint pattern `data/BOP/{countries}.NETCD_T.{indicators}.USD.A?startPeriod=2010&endPeriod=2024`. Provider evidence records dataflow `BOP` v21.0.0 and DSD `DSD_BOP` v24.0.0. This remains separate from IMF WEO DataMapper and unrelated IMF APIs.

As-of identity verdict: `imf-bop-asof-20260711t231424302015100z` is derived from provider-supplied `DataSet` attribute `UPDATE_DATE="2026-07-11T23:14:24.302015100Z"` preserved in all nine value-chunk XML responses. `PUBLICATION_DATE="2026-07-11T23:14:24.269092200Z"` is also preserved. Chunk `Prepared` timestamps are acquisition/response-preparation times on 2026-07-12 and differ per chunk, so they do not define the shared key. The key is a provider dataset snapshot/as-of event, not query-window scope, campaign identity, acquisition timestamp, or proven official publication release.

Candidate accounting audit: `13,600 provider-valued + 875 explicit-missing + 1,575 whole-series-absent cells = 16,050 candidate cells`; loaded facts are `13,600 + 875 = 14,475`; acquisition errors 0; incompatible series 0. The 105 whole-series absences are exactly all five selected series absent for 21 territories: `ASM`, `CAF`, `CUB`, `ERI`, `GIB`, `GNQ`, `GRL`, `GUM`, `IMN`, `IRN`, `LIE`, `MAF`, `MCO`, `MNP`, `PRI`, `PRK`, `SOM`, `TCD`, `TKM`, `VGB`, `VIR`.

Artifact-scale audit: active raw artifacts total `6,238,209` bytes; normalized artifact `27,843,926` bytes; proposed publication boundary currently about `52,337,716` bytes before the closeout report and documentation edits are counted; largest individual file is `data/processed/task216_imf_bop_phase2_campaign/active/task-216-imf-bop-normalized.json` at `27,843,926` bytes. No file approaches the ordinary GitHub 100 MB hard limit; no deterministic partition was performed.

## Verification completed

Completed commands/results:

- `PYTHONPATH=src python3 -m py_compile tools/task216_imf_bop_phase2_campaign.py`: passed.
- Original focused TASK-216 + IMF BOP compatibility tests: `29 passed in 13.03s`.
- Post-audit focused TASK-216 + IMF BOP compatibility tests after as-of/candidate regression additions: `32 passed in 4.19s`.
- `PYTHONPATH=src:. uvx --from pytest pytest -q`: original closeout `835 passed in 831.29s (0:13:51)`; post-audit rerun `838 passed in 828.83s (0:13:48)`.
- Final JSON/checksum validation: `json_validated=6 checksum_entries=29 checksum_mismatches=0`.
- Final run-scoped PostgreSQL tuple: `1|1|14475|14475|13600|875|5|193|15|0|0|2` = source/release/staging/facts/observed/missing/indicators/territories/periods/failed-quality/duplicate-groups/BOP-as-of-coexistence-rows.
- Same-run idempotence and later-as-of coexistence remain verified from preserved load report and read-only database checks; acquisition was not rerun and repository data was not intentionally changed during this audit.
- Final governance checks after closeout edits: context health `0 block(s), 0 warning(s)`; coherence `0 block(s), 0 warning(s)`; architecture-reality-audit `0 block(s), 0 warning(s)`.

## Bounded raw-evidence whitespace publication exception

During bounded TASK-216 publication staging, full `git diff --cached --check` reported trailing-whitespace findings only in immutable provider-originated raw XML evidence under `data/raw/task216_imf_bop_phase2_campaign/active/`, specifically the staged provider metadata XML. The raw XML bytes were deliberately preserved byte-for-byte; no raw XML whitespace was normalized and raw checksums remain authoritative.

A staged whitespace check excluding only the exact approved raw XML evidence paths passed with zero findings for authored/non-raw staged files. Code, SQL, JSON, Markdown, manifest, state, tests, and processed artifacts had no staged whitespace findings. All staged raw XML blobs matched the approved checksum manifest and were referenced by the raw-values manifest or metadata evidence. This is a bounded TASK-216 raw-provider-evidence publication exception only; it is not permission to ignore authored whitespace in future commits.

## Recommendation

Next repository-construction step: pause additional BIS expansion and continue non-trade macro provider construction only if it closes a missing external-sector/fiscal/monetary capability. Transition toward trade remains strong soon, but TASK-216 itself did not expose a repository-class contradiction requiring architecture reconsideration.

## Bounded TASK-216 file set

Implementation and tests:

- `tools/task216_imf_bop_phase2_campaign.py`
- `tests/test_task216_imf_bop_phase2_campaign.py`

Reports:

- `artifacts/reports/task-216-imf-bop-artifact-checksums.txt`
- `artifacts/reports/task-216-imf-bop-extraction-decision.json`
- `artifacts/reports/task-216-imf-bop-frozen-pre-execution-prediction.json`
- `artifacts/reports/task-216-imf-bop-load.sql`
- `artifacts/reports/task-216-imf-bop-postgresql-load-report.json`
- `artifacts/reports/task-216-imf-bop-prediction-evaluation.json`
- `artifacts/reports/task-216-imf-bop-provider-structure-and-evidence-report.json`

Processed artifacts:

- `data/processed/task216_imf_bop_phase2_campaign/active/task-216-imf-bop-manifest.json`
- `data/processed/task216_imf_bop_phase2_campaign/active/task-216-imf-bop-normalized.json`

Raw active evidence:

- `data/raw/task216_imf_bop_phase2_campaign/active/task-216-imf-bop-metadata.json`
- `data/raw/task216_imf_bop_phase2_campaign/active/task-216-imf-bop-metadata.xml`
- `data/raw/task216_imf_bop_phase2_campaign/active/task-216-imf-bop-raw-values-manifest.json`
- `data/raw/task216_imf_bop_phase2_campaign/active/task-216-imf-bop-values-chunk-01.json`
- `data/raw/task216_imf_bop_phase2_campaign/active/task-216-imf-bop-values-chunk-01.xml`
- `data/raw/task216_imf_bop_phase2_campaign/active/task-216-imf-bop-values-chunk-02.json`
- `data/raw/task216_imf_bop_phase2_campaign/active/task-216-imf-bop-values-chunk-02.xml`
- `data/raw/task216_imf_bop_phase2_campaign/active/task-216-imf-bop-values-chunk-03.json`
- `data/raw/task216_imf_bop_phase2_campaign/active/task-216-imf-bop-values-chunk-03.xml`
- `data/raw/task216_imf_bop_phase2_campaign/active/task-216-imf-bop-values-chunk-04.json`
- `data/raw/task216_imf_bop_phase2_campaign/active/task-216-imf-bop-values-chunk-04.xml`
- `data/raw/task216_imf_bop_phase2_campaign/active/task-216-imf-bop-values-chunk-05.json`
- `data/raw/task216_imf_bop_phase2_campaign/active/task-216-imf-bop-values-chunk-05.xml`
- `data/raw/task216_imf_bop_phase2_campaign/active/task-216-imf-bop-values-chunk-06.json`
- `data/raw/task216_imf_bop_phase2_campaign/active/task-216-imf-bop-values-chunk-06.xml`
- `data/raw/task216_imf_bop_phase2_campaign/active/task-216-imf-bop-values-chunk-07.json`
- `data/raw/task216_imf_bop_phase2_campaign/active/task-216-imf-bop-values-chunk-07.xml`
- `data/raw/task216_imf_bop_phase2_campaign/active/task-216-imf-bop-values-chunk-08.json`
- `data/raw/task216_imf_bop_phase2_campaign/active/task-216-imf-bop-values-chunk-08.xml`
- `data/raw/task216_imf_bop_phase2_campaign/active/task-216-imf-bop-values-chunk-09.json`
- `data/raw/task216_imf_bop_phase2_campaign/active/task-216-imf-bop-values-chunk-09.xml`

Continuity files updated during final closeout:

- `artifacts/tasks/_SUMMARY.md`
- `artifacts/reports/_SUMMARY.md`
- `state/active_goal.md`
- `state/project_state.md`
- `state/architecture.md`
- `context/latest_handoff.md`
