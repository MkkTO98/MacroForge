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

## Active design task

22. TASK-021 — Design canonical period, territory, and provider mapping schema evolution. Open.

TASK-021 should produce a concrete schema design plan for period structure, territory typing, aggregate support, and provider mappings before any executable migration or third-source PostgreSQL promotion.

Schema/WDI/OECD/Eurostat work must continue to be recreated cleanly from decisions and tests. Do not write to live `macro`, implement source/framework refactors beyond accepted decision scope, implement migrations, promote Eurostat, or create a generalized source framework without a new accepted decision and dry-run.
