# MacroForge Task Backlog

## Completed vertical-slice foundation tasks

1. TASK-001 — Rebuild MacroForge scaffold with current ProjectForge.
2. TASK-002 — Import curated reconstruction context.
3. TASK-003 — Establish source-of-truth and precedence decisions.
4. TASK-004 — Recreate v0 PostgreSQL schema foundation.
5. TASK-005 — Recreate narrow WDI extract/raw evidence slice.
6. TASK-006 — Implement PostgreSQL loader for WDI staging/curated facts.
7. TASK-007 — Add runbook and validation reporting.

## Completed review task

8. TASK-008 — Review architecture after first vertical slice.

Decision: `artifacts/decisions/DEC-005-post-vertical-slice-architecture-and-next-source-scope.md`.

## Completed hardening/source tasks

9. TASK-009 — Harden WDI vertical slice for rerunnable local operation.
10. TASK-010 — Define minimal source contract for second-source spike.
11. TASK-011 — Spike no-key OECD/SDMX-style second source.

## Completed second-source implementation task

12. TASK-012 — Implement OECD/SDMX raw-evidence normalization.

TASK-012 completed the bounded source-specific implementation proposed by the TASK-011 spike report. It produced fixture-backed raw XML, normalized metadata, and report evidence without PostgreSQL schema changes, live `macro` database writes, or a generalized SDMX framework.

## Completed live second-source hardening task

13. TASK-013 — Harden OECD/SDMX live no-key rerunnable smoke command.

TASK-013 proved the TASK-012 OECD/SDMX evidence slice can be rerun against the public no-key OECD endpoint and write only MacroForge project-layout artifacts. It remains an evidence/normalization smoke command: no PostgreSQL schema changes, no live `macro` database writes, and no generalized SDMX framework.

## Completed design task

14. TASK-014 — Design OECD/SDMX PostgreSQL promotion.

TASK-014 completed DEC-006. The decision accepts PostgreSQL promotion only after a narrow source-specific staging migration: add `staging.oecd_sdmx_observation`, keep the existing curated fact model, map `MEASURE` to indicator, map `UNIT_MEASURE` to unit, and preserve SDMX attributes in `curated.dim_attribute_set`.

## Completed OECD/SDMX PostgreSQL promotion task

15. TASK-015 — Implement OECD/SDMX PostgreSQL loader.

TASK-015 added `db/migrations/002_oecd_sdmx_staging.sql`, `src/macroforge/oecd_sdmx_loader.py`, isolated PostgreSQL idempotency tests, and `artifacts/reports/oecd-sdmx-load-smoke-20260603.json`. The bounded OECD/SDMX slice now loads 8 staging rows and 8 curated facts, preserving `USD_EXC`/`USD_PPP` and observed SDMX attributes.

## Completed implementation hardening task

16. TASK-016 — Review architecture after second source. Complete.

TASK-016 created `artifacts/decisions/DEC-007-post-second-source-architecture-and-next-scope.md`. DEC-007 keeps the current source-specific raw-SQL/PostgreSQL/psql architecture, rejects generalized source/SDMX/framework work for now, keeps raw SQL migrations, and accepts only tiny shared mechanical helper plus validation/reporting hardening.

17. TASK-017 — Harden shared validation and loader reporting. Complete.

TASK-017 created and validated a fresh implementation dry-run, added `src/macroforge/db_helpers.py` plus `tests/test_db_helpers.py`, and refactored WDI/OECD loader and WDI validation code to share only tiny mechanical helpers for SQL/JSONB literal rendering, psql execution/scalar/count parsing, and JSON report writing. It preserved source-specific semantics, schemas, report compatibility, isolated PostgreSQL behavior, no-live-fetch behavior, and live `macro` refusal boundaries.

## Completed next-scope governance task

18. TASK-018 — Decide next source/data reliability scope after TASK-017. Complete.

TASK-018 created `artifacts/decisions/DEC-008-next-scope-after-shared-validation-reporting.md`. DEC-008 chooses bounded source-specific OECD/SDMX codelist and label enrichment before a third-source spike because the current second source is technically loaded but still semantically code-heavy.

## Completed codelist/label enrichment task

19. TASK-019 — Spike OECD/SDMX codelist and label enrichment. Complete.

TASK-019 created and validated a fresh implementation dry-run, added fixture-backed codelist parsing/writer tests, extended `src/macroforge/oecd_sdmx.py` with bounded source-specific label parsing/reporting, generated project-layout label metadata/report artifacts from recorded fixture/local XML, and updated the source contract. It preserved the no-live-fetch, no-schema-change, no-PostgreSQL-label-load, no-live-`macro`, and no-generalized-framework boundaries.

## Completed third-source architecture spike

20. TASK-020 — Spike third no-key source for architecture validation. Complete.

TASK-020 accepted DEC-009 and used a bounded public no-key Eurostat `namq_10_gdp` JSON-stat slice to validate MacroForge's canonical model, ingestion framework posture, metadata architecture, and fact table design. It produced raw/normalized/report evidence and found two high-priority schema gaps before third-source PostgreSQL promotion: period identity must support quarterly/monthly `period_code` values, and territory identity must not assume ISO3 provider codes.

## Completed canonical-domain schema re-evaluation

21. DEC-010 — Prefer canonical-domain schema evolution over provider-centric identities. Accepted.

The canonical-domain design note at `docs/architecture/canonical-domain-schema-evolution.md` re-evaluates TASK-020 from the user's stated domain principle: provider representations must not become canonical identities. Periods should use structured canonical fields; provider period strings belong in mapping metadata. ISO3 remains the canonical country identifier; aggregate regions require `territory_type` and provider mappings rather than weakened ISO3 semantics.

## Completed bounded canonical-domain schema design

22. TASK-021 — Design canonical period, territory, and provider mapping schema evolution. Complete.

TASK-021 produced `docs/architecture/minimal-canonical-domain-schema-design.md` and DEC-011. The accepted design is intentionally minimal: structured canonical periods for annual/quarterly/monthly/daily-ready rows, territory typing with ISO3-preserved countries and optional aggregate/economic-area rows, provider period/territory mappings, and minimal provider code dictionaries. It does not widen `curated.fact_observation` with provider-specific columns.

## Completed canonical-domain schema implementation task

23. TASK-022 — Implement minimal canonical-domain schema migration. Complete.

TASK-022 implemented `db/migrations/003_canonical_domain_dimensions.sql`, added TDD coverage for structured periods, territory typing, provider mappings/code dictionaries, and updated WDI/OECD loaders for compatibility with canonical-domain period/territory mappings. It did not write to live `macro`, promote Eurostat, onboard FRED, implement generalized source/framework work, add aggregate membership history, or create research/mart scope.

## Completed Eurostat promotion design task

24. TASK-023 — Design bounded Eurostat PostgreSQL promotion against canonical-domain schema. Complete.

TASK-023 created `docs/architecture/bounded-eurostat-postgresql-promotion-design.md` and DEC-012. The accepted design promotes only the recorded Eurostat `namq_10_gdp` fixture through a future source-specific staging migration/loader against the TASK-022 canonical-domain schema. It preserves canonical quarterly periods, ISO3 country territories, provider mappings/dictionaries, and the unchanged source-agnostic fact table.

## Completed Eurostat implementation task

25. TASK-024 — Implement bounded Eurostat PostgreSQL loader. Complete.

TASK-024 implemented only DEC-012: source-specific migration 004, source-specific loader from the recorded normalized fixture, isolated PostgreSQL idempotency tests, and a small load report. It did not live-fetch Eurostat in tests, write to live `macro`, broaden beyond the fixture, onboard FRED, widen facts with provider columns, or build a generalized JSON-stat/source framework.

## Completed post-third-source architecture review

26. TASK-025 — Review architecture after bounded third-source PostgreSQL promotion. Complete.

TASK-025 created DEC-013. DEC-013 keeps the source-specific raw-SQL/PostgreSQL/psql architecture after WDI, OECD/SDMX, and Eurostat bounded database paths. Three-source pressure justifies a combined-source canonical validation smoke, not a generalized ingestion framework or research/mart slice.

## Completed combined-source validation smoke

27. TASK-026 — Implement combined-source canonical validation smoke. Complete.

TASK-026 implemented a bounded combined smoke in an isolated temporary PostgreSQL database. It applies migrations 001-004, runs existing WDI/OECD/Eurostat bounded loaders, verifies combined canonical fact/dimension/provider mapping/lineage/quality checks, writes `artifacts/reports/combined-source-canonical-smoke-20260604.json`, and drops the temporary database. The report succeeded with 3 sources, 3 dataset releases, 20 curated facts, 0 duplicate fact grains, and 0 failing quality checks.

## Completed post-combined-smoke governance task

28. TASK-027 — Decide next scope after combined-source canonical validation smoke. Complete.

TASK-027 created DEC-014. DEC-014 accepts the user-preferred next scope: a first minimal research-facing canonical output, specifically a small deterministic canonical GDP snapshot/audit report from existing canonical facts plus source/lineage metadata. It rejects new sources, generalized ingestion framework extraction, and broad schema refactoring.

## Completed first research-facing report task

29. TASK-028 — Implement first canonical GDP snapshot report. Complete.

TASK-028 created `src/macroforge/canonical_gdp_snapshot.py`, tests, and deterministic JSON/Markdown report artifacts. The report is generated from an isolated combined-source PostgreSQL database using existing bounded loaders and core queries over `curated.*` plus `meta.*` only. It reports 20 canonical fact rows, 16 GDP snapshot observations, 0 missing bounded GDP observations, 0 duplicate fact grains, and 0 failing quality checks.

## Completed post-first-report governance task

30. TASK-029 — Decide next scope after first canonical GDP snapshot report. Complete.

TASK-029 created DEC-015. DEC-015 selects focused canonical indicator and unit comparability governance/design as the next bounded scope after the first canonical GDP snapshot report. It rejects new sources, framework extraction, report expansion, migrations, and unit conversion implementation for now.

## Completed architecture-reality remediation hygiene task

31. TASK-031 — Architecture-to-Reality remediation hygiene. Complete.

TASK-031 implemented the user-approved remediation from the completed Architecture-to-Reality Audit. It fixed OECD/SDMX staging validation/documentation drift, added inherited context-health and architecture-reality audit tools, compacted `state/project_state.md` while preserving the previous ledger in a report artifact, refreshed README/architecture overview, reconciled historical Desktop architecture concepts, and aligned logging/command-governance docs. It did not redesign MacroForge or expand TASK-030 scope.

## Completed AI-assisted canonicalization design task

32. TASK-030 — Design minimal AI-assisted canonicalization and comparability layer. Complete.

TASK-030 created `docs/architecture/minimal-ai-assisted-canonicalization-layer.md` and DEC-018. DEC-018 accepts a minimal AI-assisted canonicalization layer where provider indicator evidence feeds canonicalization runs, auditable mapping/canonical-creation proposals, confidence/reasoning/provenance, exception-focused review, accepted/provisional mapping state, canonical indicator concepts, and versioned re-canonicalization lineage. It rejects manual-every-indicator governance and does not approve implementation under TASK-030.

## Completed canonicalization state foundation task

33. TASK-032 — Implement minimal canonicalization state foundation. Complete.

TASK-032 implemented `src/macroforge/canonicalization_state.py`, `tests/test_canonicalization_state.py`, and `artifacts/reports/canonicalization-state-foundation-20260605.json`. It proved fixture-backed provider indicator evidence, canonicalization run records, mapping proposals, unit/comparability profiles, accepted/provisional mapping state, high-impact review routing, annual/quarterly non-aggregation, and supersession/versioning mechanics without migrations, model calls, live fetches, live `macro` writes, unit conversion, aggregation, new sources, framework extraction, or provider-specific fact columns.

## Completed canonicalization next-scope governance task

34. TASK-033 — Decide next scope after minimal canonicalization state foundation. Complete.

TASK-033 produced DEC-019 and `docs/architecture/canonicalization-next-scope-decision-analysis.md`. DEC-019 selected option A: a tiny deterministic canonicalization proposal-generation workflow over the existing bounded GDP fixture evidence. The choice explicitly optimizes uncertainty reduction over capability: validate the TASK-032 workflow loop before introducing AI/model dependence, PostgreSQL persistence, richer state, report integration, or new sources.

## Completed deterministic canonicalization proposal workflow

35. TASK-034 — Implement tiny deterministic canonicalization proposal workflow. Complete.

TASK-034 added a deterministic proposal workflow over the existing TASK-032 WDI/OECD/Eurostat GDP fixture state. It produces provider-evidence-derived workflow proposals, review-required mapping update proposals, unit/comparability caveat propagation, annual/quarterly no-aggregation behavior, and a deterministic audit artifact at `artifacts/reports/canonicalization-proposal-workflow-20260613.json`. It did not call models, mutate accepted mapping state, auto-apply mapping updates, write to databases, live-fetch data, implement unit conversion, aggregate frequencies, or broaden framework/report scope.

## Completed post-proposal-workflow governance task

36. TASK-036 — Decide next scope after deterministic canonicalization proposal workflow. Complete.

TASK-036 created DEC-021 and `docs/architecture/canonicalization-post-proposal-next-scope-decision-analysis.md`. DEC-021 selects bounded WDI unit metadata enrichment as the next uncertainty-reduction step because TASK-034 proved deterministic workflow mechanics while exposing WDI `unknown_unit_metadata` as the sharpest blocker. It rejects AI/model calls, prompt/provider setup, migrations, new sources, live fetches, live `macro` writes, unit conversion, frequency aggregation, report integration, broad framework extraction, provider-specific fact columns, accepted mapping mutation, auto-apply behavior, and git push for this governance step.

## Completed bounded WDI unit metadata enrichment task

37. TASK-037 — Implement bounded WDI unit metadata enrichment for canonicalization evidence. Complete.

TASK-037 added a source-specific fixture-backed WDI metadata enrichment path for existing `NY.GDP.MKTP.CD` canonicalization evidence. It replaces WDI's generic proposal blocker `unknown_unit_metadata` with explicit current-USD metadata evidence in the bounded proposal workflow while marking the metadata as source evidence, not canonical truth. It produced `artifacts/reports/canonicalization-wdi-unit-metadata-enrichment-20260613.json` and preserved no model calls, no live fetches, no migrations, no unit conversion, no accepted mapping mutation, no auto-apply behavior, no non-WDI changes, no report integration beyond the bounded audit artifact, and no generalized metadata/source framework.

## Completed bounded review lifecycle validation task

38. TASK-038 — Simulate bounded canonicalization proposal review-to-accepted/provisional lifecycle. Complete.

TASK-038 validated the proposal -> review -> accepted/provisional lifecycle in bounded file-backed form using only existing WDI/OECD/Eurostat GDP canonicalization evidence. It produced `artifacts/reports/canonicalization-review-lifecycle-20260614.json` and `.md`, demonstrating one governed provisional outcome for WDI and deferred outcomes for OECD and Eurostat, with explicit review decisions, check gates, state deltas, manifest deltas, lineage, and replay evidence. It preserved no code changes, no model calls, no live fetches, no migrations, no source/report integration, no conversion/aggregation, no manifest base mutation, and no accepted-state auto-apply.


## Completed deferred-mapping advancement requirements task

39. TASK-039 — Persist deferred mapping advancement requirements after TASK-038. Complete.

TASK-039 created `artifacts/reports/canonicalization-deferred-mapping-advancement-requirements-20260618.json` and `.md`, recording the rationale, missing evidence/policy, semantic blocker, minimum advancement condition, caveats, evidence pointers, replay requirements, and forbidden shortcuts for TASK-038 deferred OECD and Eurostat GDP mappings. It did not change source code, tests, schemas, source evidence, accepted/base mapping state, the canonical asset manifest, or GDP reports.

## Completed OECD unit-basis comparability task

40. TASK-040 — Implement OECD unit-basis comparability split for canonicalization evidence. Complete.

TASK-040 implemented the first TASK-039 advancement requirement for OECD `B1GQ`: deterministic separation of `USD_EXC` exchange-rate and `USD_PPP` PPP comparability basis candidates. It added tested helper/writer functions in `src/macroforge/canonicalization_state.py` and generated `artifacts/reports/canonicalization-oecd-unit-basis-comparability-20260618.json` and `.md`. It preserved no accepted/base mapping mutation, no manifest base mutation, no report integration, no auto-apply, no model calls, no live fetches, no migrations, no live/default `macro` writes, no unit/currency conversion, and no frequency aggregation.

## Completed comparability/research-readiness assessment

41. TASK-041 — Bounded MacroForge comparability and research-readiness assessment. Complete.

TASK-041 produced `artifacts/reports/R-20260619-comparability-research-readiness-assessment.md` and `artifacts/tasks/TASK-041-comparability-research-readiness-assessment.md`. It found MacroForge partially research-ready for same-source descriptive and boundary findings, but not yet ready for trustworthy cross-source GDP research because deterministic eligibility/comparability classification and conversion/aggregation policy remain absent. It recommended TASK-042: create a deterministic GDP research/report eligibility classification artifact over existing evidence only. It preserved no implementation, no new data, no schemas, no pipelines, no agents, no dashboards, no report-generation systems, no architecture redesign, no manifest/base-state mutation, no PostgreSQL writes, no conversion, and no aggregation.

## Completed GDP eligibility classification task

42. TASK-042 — Deterministic GDP research/report eligibility classification artifact. Complete.

TASK-042 produced `artifacts/reports/gdp-eligibility-classification-20260619.json`, `artifacts/reports/R-20260619-gdp-eligibility-classification-validation.md`, and `artifacts/tasks/TASK-042-gdp-eligibility-classification-artifact.md`. It created a compact downstream-consumable contract for current GDP evidence: WDI is eligible only for bounded WDI-only descriptive findings with governed provisional caveats; OECD `USD_EXC` and `USD_PPP` remain deferred/profile-specific; Eurostat `CP_MEUR` remains deferred/profile-specific with cross-source annual/current-USD comparison blocked by missing frequency/currency/scale policy. It recommends treating MacroForge as a reasonable v1 stopping point for current EIP needs unless a concrete downstream blocker appears. It preserved no new data, new sources, conversion, aggregation, reporting framework, dashboard, pipeline, agent, PostgreSQL write, canonical evidence mutation, accepted manifest mutation, or canonical observation mutation.

## Completed trigger-gated MetaHarvest consultation implementation

43. TASK-043 — Implement trigger-gated MetaHarvest consultation helper. Complete.

TASK-043 implemented the approved Phase 1 trigger-gated MetaHarvest consultation helper at `tools/consult_metaharvest.py`, with versioned structured task classification, a Consultation Contract that only returns `consult`/`do_not_consult`, a separate Retrieval Contract that only runs after consultation is requested, bounded primary/keyword/adjacent retrieval, mandatory Authority note, confidence semantics, non-blocking failure behavior, tests, and minimal documentation at `docs/architecture/metaharvest-trigger-gated-consultation.md`. It preserved no startup consultation, no eager retrieval, no automatic adoption/task creation, no runtime/orchestration framework, no MetaHarvest authority, no MetaHarvest mutation, and unchanged behavior when no trigger matches.

## Completed WDI operational hardening

44. TASK-044 — Repair WDI isolated smoke workflow. Complete.

TASK-044 resolved the first operational pre-freeze blocker from the operational capability validation report. The WDI-only isolated smoke now applies both `001_v0_schema_foundation.sql` and `003_canonical_domain_dimensions.sql` before loading/validation, matching the current WDI loader's canonical-domain schema requirements. It updated the WDI smoke tests and WDI runbook, preserved isolated temporary PostgreSQL execution and live `macro` refusal, and did not change WDI loader semantics, schemas, sources, reports, conversion, aggregation, frameworks, or model behavior.

## Completed fixture-persistence operational hardening

45. TASK-045 — Make OECD/Eurostat fixtures clean-clone safe. Complete.

TASK-045 resolved the remaining operational pre-freeze blocker from the operational capability validation report. It updated `.gitignore` so generated `data/` artifacts remain ignored by default while the bounded OECD/Eurostat fixture evidence required for combined reconstruction is explicitly unignored and commit-eligible. It added a fixture-persistence test, preserved current loader paths and behavior, and did not fetch live data, add sources, change schemas/migrations, mutate canonical state, introduce frameworks, or write to live/default `macro`.
