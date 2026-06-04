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

Status: second-source PostgreSQL promotion, post-second-source architecture review, shared validation/reporting hardening, TASK-018 next-scope decision, TASK-019 codelist/label enrichment, TASK-020 third-source architecture spike, and DEC-010 canonical-domain schema re-evaluation complete. TASK-021 canonical schema design is open.

Add one source with a different shape/friction to test abstraction. Per DEC-005, TASK-011 tested a bounded no-key OECD/SDMX-style candidate and found it viable. TASK-012 implemented a bounded source-specific raw-evidence normalization slice using SDMX GenericData XML fixture evidence, normalized metadata, and a report. TASK-013 hardened that slice into a live no-key rerunnable smoke command that writes project-layout evidence artifacts. TASK-014 completed DEC-006, which accepted PostgreSQL promotion only after a narrow source-specific staging migration. TASK-015 implemented that migration and loader against recorded normalized OECD evidence in isolated PostgreSQL smoke databases. TASK-016 completed DEC-007, keeping architecture source-specific and raw-SQL/psql-based while accepting only tiny shared validation/reporting/helper hardening. TASK-017 completed that bounded hardening with a tiny shared mechanical helper module and preserved source-specific behavior. TASK-018 completed DEC-008, choosing bounded OECD/SDMX codelist and label enrichment before a third-source spike. TASK-019 completed that enrichment as source-specific filesystem metadata/report evidence, without schema changes or generalized SDMX/source framework work. TASK-020 completed DEC-009 with a bounded Eurostat third-source architecture spike and found schema design gaps around quarterly period identity, provider territory codes, and provider dimension metadata. DEC-010 then re-evaluated those recommendations from a canonical-domain perspective: structured periods and ISO3 country identity should remain canonical, while provider period/territory codes belong in mappings/metadata. TASK-021 is open to design the concrete schema evolution.

## Milestone 4 — Research layer

- Query notebooks/reports.
- Macro briefs backed by canonical facts and citations.
- Analyst workflows and AI-assisted research roles.

## Milestone 5 — Broader automation

- Scheduling after manual reliability.
- CI/data validation automation.
- Optional containerized agents.
- Dataset catalog UI.
