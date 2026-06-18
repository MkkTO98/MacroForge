# MacroForge Roadmap

## Milestone 0 — Reconstruction and scaffold

Status: complete.

- Generate fresh ProjectForge project with current `python_data_project` template.
- Register canonical path.
- Import compact recovered context, not raw full exports.
- Create decisions, tasks, summaries, roadmap, and state artifacts.
- Verify generated-project coherence and tests.

## Milestone 1 — PostgreSQL/WDI vertical slice

Status: complete through architecture review (TASK-004 through TASK-008).

- Recreate/accept v0 schema decision.
- Implement raw SQL migration and schema verification tests.
- Implement WDI extract/raw/checksum writer.
- Implement staging and curated PostgreSQL loader.
- Implement validation queries and run report.
- Run tiny smoke slice: USA/DNK, GDP/population, 2020-2021.
- Review architecture after first vertical slice and record next source/framework scope in DEC-005.

## Milestone 2 — Hardening

Status: complete for current TASK-009/TASK-010 scope.

- Harden WDI vertical slice into a single rerunnable local smoke command/script (TASK-009).
- Idempotent reruns.
- Better failure handling.
- Source catalog documentation.
- Data quality checks and reports.
- WDI pipeline runbook.
- Backup/restore and DB environment documentation.
- Define a minimal source contract before the second-source spike (TASK-010).

## Milestone 3 — Second source

Status: second-source PostgreSQL promotion, post-second-source architecture review, shared validation/reporting hardening, TASK-018 next-scope decision, TASK-019 codelist/label enrichment, TASK-020 third-source architecture spike, DEC-010 canonical-domain schema re-evaluation, TASK-021 bounded canonical schema design, TASK-022 minimal schema migration implementation, TASK-023 bounded Eurostat PostgreSQL promotion design and TASK-024 bounded Eurostat loader implementation are complete. TASK-025 post-third-source architecture review is complete. TASK-026 combined-source canonical validation smoke, TASK-027 next-scope governance, TASK-028 first canonical GDP snapshot report, TASK-029 post-first-report next-scope governance, TASK-030 minimal AI-assisted canonicalization/comparability design, TASK-032 minimal canonicalization state foundation, TASK-033 post-canonicalization-state next-scope governance, TASK-035 narrow MetaHarvest compatibility canonical asset manifest integration, TASK-034 tiny deterministic canonicalization proposal workflow, TASK-036 post-proposal-workflow next-scope governance, and TASK-037 bounded WDI unit metadata enrichment are complete.

Add one source with a different shape/friction to test abstraction. Per DEC-005, TASK-011 tested a bounded no-key OECD/SDMX-style candidate and found it viable. TASK-012 implemented a bounded source-specific raw-evidence normalization slice using SDMX GenericData XML fixture evidence, normalized metadata, and a report. TASK-013 hardened that slice into a live no-key rerunnable smoke command that writes project-layout evidence artifacts. TASK-014 completed DEC-006, which accepted PostgreSQL promotion only after a narrow source-specific staging migration. TASK-015 implemented that migration and loader against recorded normalized OECD evidence in isolated PostgreSQL smoke databases. TASK-016 completed DEC-007, keeping architecture source-specific and raw-SQL/psql-based while accepting only tiny shared validation/reporting/helper hardening. TASK-017 completed that bounded hardening with a tiny shared mechanical helper module and preserved source-specific behavior. TASK-018 completed DEC-008, choosing bounded OECD/SDMX codelist and label enrichment before a third-source spike. TASK-019 completed that enrichment as source-specific filesystem metadata/report evidence, without schema changes or generalized SDMX/source framework work. TASK-020 completed DEC-009 with a bounded Eurostat third-source architecture spike and found schema design gaps around quarterly period identity, provider territory codes, and provider dimension metadata. DEC-010 then re-evaluated those recommendations from a canonical-domain perspective: structured periods and ISO3 country identity should remain canonical, while provider period/territory codes belong in mappings/metadata. TASK-021 completed DEC-011, a bounded minimal schema design for structured periods, territory typing, provider mappings, and provider dictionaries without fact widening or generalized ingestion. TASK-022 implemented that minimal migration and WDI/OECD compatibility updates. TASK-023 completed DEC-012, accepting a bounded source-specific Eurostat `namq_10_gdp` promotion design against the canonical-domain schema. TASK-024 implemented that bounded Eurostat loader/migration scope.

DEC-013 completed TASK-025 by keeping source-specific raw SQL/PostgreSQL/psql architecture and selecting TASK-026 combined-source canonical validation smoke before any new source/framework/research scope. TASK-026 completed that smoke with one isolated database containing WDI, OECD/SDMX, and Eurostat facts. TASK-027 completed DEC-014, selecting a first minimal research-facing canonical GDP snapshot/audit report as TASK-028 before new sources, framework extraction, or broad schema work. TASK-028 completed that report as deterministic JSON/Markdown artifacts from canonical facts plus metadata. TASK-029 completed DEC-015, selecting TASK-030 minimal canonical indicator/unit comparability design before more reports, new sources, framework extraction, or schema implementation. DEC-016 then refined TASK-030 so the design targets an auditable AI-assisted canonicalization layer rather than manual provider-indicator governance. TASK-030 completed DEC-018, accepting that minimal design. TASK-032 implemented a fixture-backed canonicalization state foundation. TASK-033 completed DEC-019, selecting TASK-034 to validate a deterministic proposal-generation workflow before AI/model dependence, persistence, richer state, or report integration. TASK-034 completed that deterministic workflow as provider-evidence-derived proposals, review-required mapping update proposals, unit/frequency caveat propagation, and deterministic audit output without accepted-state mutation or auto-apply behavior. TASK-036 completed DEC-021, selecting TASK-037 bounded WDI unit metadata enrichment as the next active implementation task before AI/model dependence, persistence, report integration, or new sources. TASK-037 completed that bounded enrichment as source-specific fixture metadata evidence for existing WDI GDP canonicalization evidence, without unit conversion, accepted mapping mutation, auto-apply, non-WDI changes, live fetches, migrations, or generalized metadata/source framework work.

## Milestone 4 — Research layer

- Query notebooks/reports.
- Macro briefs backed by canonical facts and citations.
- Analyst workflows and AI-assisted research roles.

## Milestone 5 — Broader automation

- Scheduling after manual reliability.
- CI/data validation automation.
- Optional containerized agents.
- Dataset catalog UI.
