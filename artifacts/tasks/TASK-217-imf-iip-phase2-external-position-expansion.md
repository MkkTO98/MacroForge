# TASK-217 — IMF IIP Phase 2 external-position stock repository expansion

## Status

Implemented and locally verified; unpublished. Do not commit or push without explicit authorization.

## Selection decision

Selected task: broaden IMF International Investment Position (IIP) annual external-position stock evidence beyond the prior USA/JPN and G7 bounded panels into a broad country-level repository capability.

Why this outranks alternatives:

1. Analytical capability gained is first-order: external assets, liabilities, and net international investment positions are core external-vulnerability, debtor/creditor-status, and macro-financial balance-sheet inputs.
2. It directly complements the newly published TASK-216 IMF BOP current-account flow capability with stock-position evidence from the adjacent IMF SDMX external-sector family.
3. Existing MacroForge evidence already identifies International Investment Position stock observations as Developing, limited to USA/JPN and G7 coverage.
4. The source path is proven by TASK-088, TASK-135, TASK-148, and the broader IMF SDMX handling discipline exercised in TASK-216.
5. It pressure-tests the post-TASK-216 question of whether one more BOP/IIP relationship campaign confirms stable source-specific responsibilities without reopening architecture.
6. It advances repository construction more than governance cleanup, documentation polish, or another already mature WDI/BIS extension.

Strong alternatives rejected:

- Another IMF BOP component family: valuable, but TASK-216 just added broad current-account flows. IIP stock positions add a complementary balance-sheet class rather than more same-family BOP flow detail.
- Another BIS scalar campaign: proven and useful, but BIS policy/DSR/credit-gap monitoring is already operationally useful after TASK-213 through TASK-215; IIP closes a larger external-sector stock gap.
- Residual WDI annual-scalar campaign: high execution confidence, but WDI annual-scalar confidence cells are already broad after TASK-189 through TASK-206 and the accepted transition prioritizes diverse-source macroeconomic enrichment.
- Trade/company/financial-asset ingestion: explicitly outside the current repository-construction guardrail unless separately requested.
- Architecture cleanup/shared extraction: no contradiction currently justifies architecture reopening; implementation evidence should come first.

## Objective

Scale the proven IMF IIP position stock path into a broad, source-specific, annual scalar repository expansion while preserving source/dataset/as-of/run identity separation, provider evidence, explicit missingness, whole-series absence, territory mapping, unit semantics, lineage, quality checks, idempotence, and duplicate prevention.

## Analytical capability

Annual IMF IIP external balance-sheet monitoring by country:

- external asset position stocks;
- external liability position stocks;
- net international investment position;
- USD million scale where provider-supported;
- annual 2010-2024 coverage;
- provider as-of evidence from IMF SDMX dataset metadata.

## Source and dataset identity

- Canonical source: `IMF_SDMX_IIP_API_V1`
- Provider dataset: `IMF:IIP`
- Dataflow: `IIP`
- API/protocol: IMF external SDMX 2.1 API
- Release/as-of identity: derived from provider DataSet `UPDATE_DATE`, `PUBLICATION_DATE`, or response `Prepared` evidence; not from query window, campaign name, acquisition timestamp, or official-release assumptions.
- Run: `task-217-imf-iip-external-position-phase2`

## Intended coverage

Candidate universe before value acquisition:

- Accepted canonical country entities present in IMF IIP provider country codelist.
- Annual periods 2010 through 2024.
- Selected position families:
  - `A_P.IIP` — external asset positions;
  - `L_P.IIP` — external liability positions;
  - `NETAL_P.NIIP` — net international investment position.
- Unit: `USD`, provider scale preserved.
- Frequency: annual.

Candidate cells are computed deterministically as accepted countries × three selected position series × 15 annual periods after metadata/territory reconciliation and before values.

## Confidence cell

High confidence for source access and scalar compatibility; moderate operational risk because broad country coverage may expose whole-series absences, metadata differences from BOP, and older IIP task-local source identities.

Evidence basis:

- TASK-088 two-country IIP proof.
- TASK-135/TASK-148 G7 IIP operational evidence.
- TASK-216 broad IMF BOP/SDMX identity, as-of, missingness, and chunking discipline.

## Acceptance criteria

- Frozen prediction created before value acquisition.
- Raw metadata and value chunks preserved byte-for-byte in attempt and active locations.
- Acquisition errors block normalization/loading.
- Candidate reconciliation accounts for provider-valued facts, explicit-missing facts, whole-series absences, incompatible series, aggregates, unsupported entities, and unknown identifiers separately.
- Provider source, dataset, as-of/release, campaign, and run identities remain distinct.
- Only territory is removed from complete provider series identity; accounting entry, IIP indicator, unit, scale, frequency, and provider attributes are preserved in source-scoped indicator identity/attributes.
- PostgreSQL load uses existing deterministic scalar/revision-aware substrate.
- Staging/fact counts agree.
- Observed versus explicit-missing counts agree.
- Failed quality checks are zero.
- Duplicate canonical-key groups are zero.
- Same-run idempotence produces zero growth.
- Simulated later-as-of coexistence is verified.
- Focused TASK-217 tests and relevant IMF IIP/BOP compatibility tests pass.
- JSON/checksum validation, coherence, context health, architecture-reality audit, and `git diff --check` pass after final state/handoff edits.

## Exclusions

- No BLS, WEO, BIS, FRED-detour, trade, company, or financial-asset ingestion.
- No generic IMF framework, universal SDMX adapter, multidimensional architecture, IIP ontology, BOP/IIP accounting framework, or shared helper extraction unless concrete implementation evidence requires it.
- No commit or push without separate authorization.
- No modification of unrelated pre-existing working-tree changes.

## Expected artifacts

- `tools/task217_imf_iip_phase2_campaign.py`
- `tests/test_task217_imf_iip_phase2_campaign.py`
- `artifacts/reports/task-217-imf-iip-frozen-pre-execution-prediction.json`
- `artifacts/reports/task-217-imf-iip-provider-structure-and-evidence-report.json`
- `artifacts/reports/task-217-imf-iip-postgresql-load-report.json`
- `artifacts/reports/task-217-imf-iip-prediction-evaluation.json`
- `artifacts/reports/task-217-imf-iip-extraction-decision.json`
- `artifacts/reports/task-217-imf-iip-artifact-checksums.txt`
- `artifacts/reports/task-217-imf-iip-load.sql`
- `data/raw/task217_imf_iip_phase2_campaign/active/*`
- `data/processed/task217_imf_iip_phase2_campaign/active/*`
- Continuity updates to state, handoff, summaries, and capability atlas as needed.

## Database verification requirements

Verify run-scoped:

- source rows;
- dataset/as-of rows;
- staging rows;
- curated facts;
- observed facts;
- explicit-missing facts;
- selected indicators;
- territories;
- periods;
- failed quality checks;
- duplicate canonical-key groups;
- same-run idempotence;
- later-as-of coexistence;
- total repository fact count.

## Stop conditions

Stop before promotion/loading if:

- provider metadata cannot establish source/dataset/as-of evidence;
- acquisition errors remain unresolved;
- candidate reconciliation is incomplete;
- incompatible provider series are returned;
- territory semantics cannot be resolved without architecture change;
- load would require overwriting unrelated runs or touching unrelated working-tree paths;
- scalar identity cannot preserve IIP accounting, position, unit, scale, frequency, and as-of semantics.
