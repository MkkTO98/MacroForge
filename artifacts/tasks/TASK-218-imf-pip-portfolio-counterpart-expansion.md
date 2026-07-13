# TASK-218 — IMF PIP portfolio-counterpart repository expansion

Status: Implemented and locally verified; not staged or published.

## Objective

Build a bounded but analytically useful IMF Portfolio Investment Positions by Counterpart Economy (PIP, formerly CPIS) repository capability. The campaign extends the external-sector sequence after TASK-216 BOP current-account flows and TASK-217 IIP external-position stocks by adding reporter/counterpart portfolio-investment exposure positions.

## Candidate selection and ranking

Selected task: IMF PIP/CPIS annual portfolio investment positions by counterpart economy for a 24-economy investment-relevant matrix over 2020-2024.

Why selected now:

1. It closes a first-order external-sector gap that TASK-216 and TASK-217 intentionally left open: cross-border holder/issuer relationship exposure.
2. It complements IIP stock totals with portfolio instrument/counterpart decomposition rather than duplicating aggregate IIP coverage.
3. It uses a proven IMF SDMX acquisition/load confidence cell while still pressure-testing relationship/counterpart semantics.
4. It has high future value for vulnerability, concentration, and cross-border exposure analysis without designing KnowledgeForge or InsightForge consumer logic.

Strong alternatives rejected:

- IMF DIP/CDIS direct-investment counterpart positions: valuable but selected after PIP only if counterpart-position semantics prove safe; PIP is more liquid-market relevant and closer to IIP portfolio categories.
- IMF GFS statement/balance-sheet expansion: high fiscal value, but current external-sector sequence has a stronger immediate capability chain and PIP is a cleaner continuation of BOP/IIP evidence.
- Another BIS campaign: useful but less urgent after TASK-213 through TASK-215 already advanced BIS monetary/credit/debt-service capabilities.
- WDI residual campaign: lower marginal macro capability because WDI annual-scalar breadth is already large and Phase 1 has reached diminishing returns.
- BLS/labor monthly extension: valuable but less globally investment-relevant than external position counterpart exposure.
- Trade/company/financial-asset work: excluded by current guardrails.
- Cleanup/governance/architecture extraction: explicitly excluded; architecture is frozen absent contradiction.

## Source, dataset, release, and run identities

- Canonical source: `IMF_SDMX_PIP_API_V1`
- Source name: International Monetary Fund SDMX PIP API
- Provider dataset: `IMF:PIP`
- Dataflow: `PIP`
- Dataflow version expected: `5.0.0`
- Data structure expected: `DSD_PIP` / `5.0.0`
- Release/as-of identity rule: derive `imf-pip-asof-*` from provider `UPDATE_DATE`, `PUBLICATION_DATE`, or SDMX `Prepared` evidence. Do not use query-window bounds as release identity.
- Run key: `task-218-imf-pip-portfolio-counterpart-phase2`

## Analytical capability

Annual country-level portfolio-investment exposure monitoring by:

- reporting economy as canonical territory;
- counterpart economy preserved in source-scoped indicator identity and attributes;
- instrument family: total portfolio investment, equity, and debt securities;
- annual USD provider values with provider scale preserved;
- explicit missing years inside returned series;
- whole-series absence separately recorded when a reporter/counterpart/instrument series is absent.

## Scope

- Frequency: annual
- Periods: 2020-2024
- Reporter economies: AUS, BEL, BRA, CAN, CHE, CHN, DEU, DNK, ESP, FRA, GBR, HKG, IND, IRL, ITA, JPN, KOR, LUX, MEX, NLD, NOR, SGP, SWE, USA
- Counterpart economies: same 24-economy set
- Accounting entry: `A` assets
- Sector: `S1` total economy
- Counterpart sector: `S1` total economy
- Indicators:
  - `P_TOTINV_P_USD` — portfolio investment total investment positions
  - `P_F51_P_USD` — portfolio investment equity positions
  - `P_F3_P_USD` — portfolio investment debt securities positions
- Expected series: 24 reporters × 24 counterparts × 3 indicators = 1,728
- Expected cells: 1,728 × 5 annual periods = 8,640

## Frozen prediction

Frozen before value acquisition in `artifacts/reports/task-218-imf-pip-frozen-pre-execution-prediction.json`.

Predicted before acquisition:

- Candidate cells: 8,640
- Provider-valued facts: approximately 6,048
- Explicit-missing facts: approximately 1,296
- Whole-series absence: approximately 1,296 cells
- Territory mapping success: all 24 selected economies must exist in IMF provider metadata and canonical territory substrate.
- Unit: USD with provider scale `6` preserved in unit/attributes.
- Acquisition risk: moderate; metadata is large but proven available, value acquisition chunked by six reporter economies.
- Implementation friction: moderate-high because counterpart relationship semantics must be preserved without a new schema dimension.
- PostgreSQL growth: observed plus explicit-missing rows only; up to 72 source-scoped PIP indicators.
- Architecture compatibility: expected compatible inside bounded scalar representation if counterpart economy remains in source-scoped indicator identity and attributes.

## Acceptance criteria

- Metadata and values acquired from IMF public SDMX PIP API with raw request evidence and timestamps preserved.
- Active raw artifacts promoted only after all value chunks succeed.
- Normalized artifact reconciles candidate cells into provider-valued facts, explicit-missing facts, and whole-series absences.
- Source/dataset/release/run identities are distinct.
- PostgreSQL load succeeds through deterministic scalar/revision-aware substrate.
- Same-run idempotence produces zero fact growth.
- Simulated later as-of/release coexists without overwriting the active PIP release.
- Duplicate canonical-key groups remain zero.
- Failed quality checks remain zero.
- Focused tests pass.
- Checksums validate all TASK-218 active artifacts.

## Stop conditions

Stop before promotion/loading if:

- PIP metadata does not evidence source/dataset/as-of identity;
- selected economy codes are missing from IMF metadata or canonical territories;
- value acquisition has unresolved errors;
- returned series contain incompatible dimensions;
- counterpart semantics cannot be preserved without loss;
- PostgreSQL load cannot be made idempotent.

## Evidence artifacts

Expected TASK-218-owned boundary:

- `tools/task218_imf_pip_phase2_campaign.py`
- `tests/test_task218_imf_pip_phase2_campaign.py`
- `artifacts/tasks/TASK-218-imf-pip-portfolio-counterpart-expansion.md`
- `artifacts/reports/task-218-imf-pip-*.json`
- `artifacts/reports/task-218-imf-pip-load.sql`
- `artifacts/reports/task-218-imf-pip-artifact-checksums.txt`
- `data/raw/task218_imf_pip_phase2_campaign/active/*`
- `data/processed/task218_imf_pip_phase2_campaign/active/*`

## Publication exclusions

Do not include:

- `state/recent_changes.md`
- TASK-207 FRED-detour files
- TASK-208 historical/temporary artifacts
- older `_attempts/` directories except TASK-218 attempt evidence if publication is later authorized
- neutral-evidence optional reports
- unrelated summaries or pre-existing residue
- TASK-218 staging/commit/push without later explicit authorization
