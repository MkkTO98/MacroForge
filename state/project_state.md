# Project State

## Current status

TASK-219 IMF DIP/CDIS direct-investment counterpart expansion is complete, verified, committed, and pushed as `a4404481ecd61767b330b2ba4fba6d0038916cde`. TASK-219 closeout state/handoff updates are being finalized.

Do not begin TASK-220 until the closeout commit is pushed or explicitly deferred. Preserve unrelated working-tree residue untouched.

## Recent completed work

- TASK-218 IMF PIP/CPIS reporter-counterpart portfolio-position expansion was completed, verified, committed, and pushed as `c92d70c20c82662970284595617dcc3cbca930d1`.
- TASK-219 was selected over IMF GFS, additional IMF BOP, BIS, BLS, residual WDI, cleanup, and architecture-only work because IMF DIP/CDIS adds a high-value direct-investment relationship-position capability and provides a second pressure test for the reporter/counterpart representation proven in TASK-218.
- TASK-219 confirmed IMF SDMX DIP dataflow `DIP` version `12.0.1`, DSD `DSD_DIP` version `13.0.0`, and provider title Direct Investment Positions by Counterpart Economy (formerly CDIS).
- Frozen candidate universe: 24 reporters × 24 counterparts × 6 direct-investment direction/instrument concepts × 2020-2024, annual frequency, `DV_TYPE=O`, 3,456 expected series, 17,280 expected cells.
- Preserved request URLs/parameters, metadata response, raw SDMX XML chunks, raw HTTP/acquisition metadata, response headers, timestamps, checksums, normalized artifact, manifest, relationship-proliferation report, prediction evaluation, extraction decision, and load SQL.
- Loaded canonical PostgreSQL facts through source `IMF_SDMX_DIP_API_V1`, provider dataset `IMF:DIP`, as-of key `imf-dip-asof-20251210t162520656782100z`, run key `task-219-imf-dip-direct-investment-counterpart-phase2`.
- Actual TASK-219 result: 16,215 loaded facts = 14,755 observed/provider-valued + 1,460 explicit-missing; 213 whole-series absences (1,065 candidate cells); 0 acquisition errors; 0 incompatible series; 144 source-scoped indicators.
- TASK-219 publication included a bounded raw-provider XML whitespace exception only for immutable IMF metadata XML at `data/raw/task219_imf_dip_phase2_campaign/active/task-219-imf-dip-metadata.xml`; raw XML was not normalized or rewritten.

## Verification snapshot

TASK-219 verification:

- Focused TASK-219 tests: `6 passed in 0.59s`.
- TASK-216/TASK-217/TASK-218/TASK-219 compatibility tests: `24 passed in 17.49s`.
- JSON boundary validation: `json_boundary_validated=16`.
- Checksum reconciliation: 22 entries, 0 missing targets, 0 mismatches.
- Raw-reference reconciliation: 11 active raw files, 11 raw refs, 0 unreferenced, 0 missing refs.
- PostgreSQL verification tuple: `task219_db|1|1|1|16215|16215|14755|1460|0|0|0`.
- Repository total after TASK-219: `10,651,727`.
- Same-run idempotence: growth 0.
- Later-as-of coexistence: simulated later release verified inside rollback; no simulated rows persisted.
- Sensitive-material, absolute-path/environment-leakage, and non-raw authored-whitespace scans: 0 hits.
- Context health: 0 blocks, 0 warnings.
- Coherence: 0 blocks, 0 warnings.
- Architecture-reality audit: 0 blocks, 1 warning (`5 completed task(s) since last Architecture-to-Reality Audit`).

## Architecture verdict

TASK-219 reaffirms current architecture. The existing scalar/revision-aware substrate preserved reporter territory, counterpart identity in source-scoped indicator identity/attributes, direct-investment direction and instrument semantics, provider-derived as-of evidence, source/dataset/run separation, unit semantics, annual periods, explicit-missing facts, lineage/quality evidence, duplicate prevention, idempotence, and later-release coexistence.

Representation verdict: **B — current scalar/source-scoped indicator representation remains operationally sufficient, but relationship indicator proliferation should continue to be monitored.**

No IMF-DIP shared substrate was extracted. TASK-218 and TASK-219 share a relationship representation pattern, but PIP and DIP provider semantics still differ materially. Extraction now would risk premature generic IMF SDMX/relationship machinery.

## Guardrails

Do not stage, commit, clean, restore, delete, move, or push unrelated residue. Preserve TASK-207 FRED-detour evidence, TASK-208 attempt/temp artifacts, neutral-evidence optional reports, older attempt directories, unrelated summaries, scaffold/MetaHarvest residue, and all other unrelated working-tree paths unless explicitly authorized.
