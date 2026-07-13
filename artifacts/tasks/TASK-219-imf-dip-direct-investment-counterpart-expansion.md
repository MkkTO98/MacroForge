# TASK-219 — IMF DIP direct-investment counterpart expansion

Status: Completed, verified, committed, and pushed as `a4404481ecd61767b330b2ba4fba6d0038916cde`.

## Baseline

- Accepted previous published HEAD: `c92d70c20c82662970284595617dcc3cbca930d1`.
- Reconfirmed live baseline before implementation:
  - branch: `main`
  - `HEAD`: `c92d70c20c82662970284595617dcc3cbca930d1`
  - `origin/main`: `c92d70c20c82662970284595617dcc3cbca930d1`
  - ahead/behind: `0/0`
  - staged count: `0`
  - repository fact total: `10,635,512`
  - TASK-218 sampled committed paths clean: yes
- Existing unrelated dirty-tree residue is preserved and non-blocking; TASK-219 boundary must remain task-owned.

## Candidate ranking

1. **IMF DIP/CDIS direct-investment positions by counterpart economy — selected.**
   - Adds direct-investment relationship-position evidence adjacent to, but economically distinct from, TASK-218 PIP/CPIS portfolio positions.
   - Provides a second relationship-bearing external-sector pressure test for reporter/counterpart semantics, source-scoped indicator proliferation, and scalar substrate sufficiency.
   - IMF SDMX source path and metadata are confirmed (`DIP` dataflow version `12.0.1`, `DSD_DIP` version `13.0.0`).
   - Direction/instrument/entity semantics are visible in provider indicator codes and attributes; selected scope uses reported official data (`DV_TYPE=O`) and avoids derived counterparty estimates for the first broad campaign.
2. **IMF GFS fiscal expansion — rejected for TASK-219.**
   - High macro value but less directly tests the already-observed uncertain relationship boundary.
   - Better candidate after the current external-sector relationship sequence is either reaffirmed or challenged.
3. **Further IMF BOP component expansion — rejected.**
   - Useful completion path, but BOP is non-counterpart and would mostly deepen already-proven current-account/BOP scalar mechanics.
4. **BIS monetary/credit/liquidity/property/cross-border banking expansion — rejected.**
   - Valuable, but recent TASK-213 through TASK-215 already expanded BIS. DIP adds more new evidence about IMF counterpart semantics.
5. **BLS monthly price/labor extension — rejected.**
   - Good frequency value, lower current investment-relevance than cross-border direct-investment exposure and less relevant to relationship-boundary pressure testing.
6. **Residual WDI annual-scalar gaps — rejected.**
   - Phase 1 residual WDI has lower marginal value than a direct-investment relationship campaign after large WDI coverage.
7. **Other backlog candidates — rejected.**
   - Trade, companies, financial assets, speculative infrastructure, architecture-only work, and residue cleanup are outside the current guardrails.

## Selected source and dataset

- Canonical source: `IMF_SDMX_DIP_API_V1`.
- Provider dataset/dataflow: `IMF:DIP` / `DIP`.
- Provider title: Direct Investment Positions by Counterpart Economy (formerly CDIS).
- Dataflow version: `12.0.1`.
- Data structure: `DSD_DIP`, version `13.0.0`.
- Source path: IMF external SDMX 2.1 API.

## Analytical capability

Annual IMF Direct Investment Positions by Counterpart Economy for a bounded investment-relevant reporter/counterpart matrix.

The capability adds direct-investment exposure evidence by reporter economy, counterpart economy, direction, and instrument basis. Reporter economy is canonical territory; counterpart economy remains material source-scoped indicator/attribute semantics.

## Frozen pre-execution prediction

The machine-readable frozen prediction is written before value acquisition at:

- `artifacts/reports/task-219-imf-dip-frozen-pre-execution-prediction.json`

Planned scope:

- Reporters: 24 economies — AUS, BEL, BRA, CAN, CHE, CHN, DEU, DNK, ESP, FRA, GBR, HKG, IND, IRL, ITA, JPN, KOR, LUX, MEX, NLD, NOR, SGP, SWE, USA.
- Counterparts: same 24 economies.
- `DV_TYPE`: `O` reported official data.
- Indicators: 6.
  - `OTWD_D_NETAL_FALL_ALL`
  - `INWD_D_NETLA_FALL_ALL`
  - `OTWD_D_NETAL_F51_ALL`
  - `INWD_D_NETLA_F51_ALL`
  - `OTWD_D_NETAL_FL_ALL`
  - `INWD_D_NETLA_FL_ALL`
- Years: 2020–2024.
- Frequency: annual.
- Expected series: 24 × 24 × 6 = 3,456.
- Expected cells: 17,280.
- Expected provider-valued facts: 10,368.
- Expected explicit-missing facts: 3,456.
- Expected whole-series absence cells: 3,456.
- Unit/scale expectation: USD, scale 6 unless provider attributes establish otherwise.

## Identity model

- Source identity: IMF API/source boundary.
- Dataset identity: `IMF:DIP`.
- Release/as-of identity: derived from provider `UPDATE_DATE`, `PUBLICATION_DATE`, or response `Prepared` metadata.
- Run identity: `task-219-imf-dip-direct-investment-counterpart-phase2`.
- Territory identity: reporter economy as canonical `dim_territory` country.
- Counterpart identity: preserved in source-scoped indicator identity and attributes.
- Indicator identity includes `DV_TYPE`, provider DIP indicator, counterpart economy, unit, scale, and frequency.

## Acceptance criteria

- Metadata and values acquired from provider with exact request evidence.
- Attempt-specific raw evidence preserved; active artifacts promoted only after successful reconciliation.
- Candidate grid reconciles expected cells, provider-valued observations, explicit missingness, and whole-series absences.
- PostgreSQL load succeeds through current scalar/revision-aware substrate.
- Source/dataset/release/run identities remain separated.
- Observed/missing, duplicate-key, failed-quality, same-run idempotence, and later-as-of coexistence checks pass.
- Relationship-proliferation measurements are reported and compared to TASK-218.
- No architecture changes unless a concrete semantic collision or loss appears.

## Exclusions and stop conditions

Excluded:

- Derived counterparty estimates (`DV_TYPE=SCC`) for this first broad DIP campaign.
- Aggregates outside the selected country matrix.
- Universal SDMX helpers, generic IMF framework, counterpart ontology, relationship dimension, graph model, or schema redesign.
- Trade, company, securities, asset-price, or residue-cleanup work.

Stop before canonical load if:

- DIP reporter/counterpart direction cannot be established.
- Distinct DIP observations collapse to the same canonical key.
- Provider confidentiality/missingness semantics cannot be preserved.
- Release/as-of identity cannot be derived.
- Acquisition errors remain unresolved.
- Load cannot be idempotent.
- Implementation collides with ambiguous shared residue.

## Collision-safe file boundary

Expected TASK-219-owned files/directories only:

- `tools/task219_imf_dip_phase2_campaign.py`
- `tests/test_task219_imf_dip_phase2_campaign.py`
- `artifacts/tasks/TASK-219-imf-dip-direct-investment-counterpart-expansion.md`
- `artifacts/reports/task-219-imf-dip-*.json`
- `artifacts/reports/task-219-imf-dip-*.txt`
- `artifacts/reports/task-219-imf-dip-load.sql`
- `data/raw/task219_imf_dip_phase2_campaign/active/*`
- `data/processed/task219_imf_dip_phase2_campaign/active/*`
- `context/latest_handoff.md` only if a safe whole-file update is attributable at closeout.

No staging, committing, pushing, cleanup, restore, or deletion is authorized in this task.


## Implementation result

TASK-219 was implemented end to end without staging, committing, or pushing.

Actual results:

- Candidate cells: 17,280.
- Candidate series: 3,456.
- Compatible/returned series: 3,243.
- Whole-series absences: 213.
- Loaded facts: 16,215.
- Provider-valued/observed facts: 14,755.
- Explicit-missing facts: 1,460.
- Acquisition errors: 0.
- Incompatible series: 0.
- Canonical indicators: 144.
- Release/as-of key: `imf-dip-asof-20251210t162520656782100z`.
- Release/as-of date: `2025-12-10`.
- PostgreSQL tuple: `task219_db|1|1|1|16215|16215|14755|1460|0|0|0`.
- Repository fact total after load: `10,651,727`.

Relationship-proliferation verdict: **B — Representation remains operationally sufficient, but proliferation should continue to be monitored.**

Reason: TASK-219 doubled TASK-218's relationship indicator surface from 72 to 144 source-scoped indicators and increased relationship facts from 8,275 to 16,215 without canonical-key collisions, duplicate groups, idempotence failure, or release/as-of loss. The scalar representation remains adequate for bounded reporter/counterpart matrices, but continued relationship campaigns should watch indicator proliferation and human discoverability.

Prediction quality: **Mixed**.

- Candidate-cell prediction was accurate.
- Provider-valued facts were underpredicted: expected 10,368, actual 14,755.
- Explicit missingness was overpredicted: expected 3,456, actual 1,460.
- Whole-series absence was much lower than expected: predicted 3,456 cells equivalent, actual 213 series / 1,065 cells.
- The error reveals provider coverage was denser than expected, not a representation or architecture issue.

Extraction verdict: no shared IMF relationship-position substrate extracted. TASK-218 and TASK-219 repeat the relationship representation pattern, but PIP and DIP still differ materially in provider dimensions and semantic interpretation. Extracting now would risk a generic IMF SDMX/relationship framework rather than a narrow stable helper.

Verification completed:

- Focused TASK-219 tests: `6 passed in 0.60s`.
- TASK-216/TASK-217/TASK-218/TASK-219 compatibility tests: `24 passed in 17.49s`.
- JSON boundary validation: `json_boundary_validated=10`.
- Checksums: 22 entries, zero missing targets, zero mismatches.
- Raw reference closure: 11 active raw files, all referenced by manifest, zero unreferenced raw files.
- Sensitive-material scan: 0 hits.
- Absolute path / environment leakage scan: 0 hits.
- Authored whitespace scan: 0 hits.
- Database tuple: `task219_db|1|1|1|16215|16215|14755|1460|0|0|0`.
- Same-run idempotence: total growth 0, source growth 0.
- Later-as-of coexistence: rolled-back sample produced `simulated_later_rows|1|1`; post-rollback simulated release rows 0.

Final governance checks are recorded in the final response/handoff after the last continuity edit.
