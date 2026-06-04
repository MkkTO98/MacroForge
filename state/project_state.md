# Project State

Project: MacroForge
Template: python_data_project
Canonical path: `/home/mkkto/srv/projectforge/workspace/projects/macroforge`
Last updated UTC: 2026-06-04T08:39:47Z

## Current state

MacroForge has been freshly generated from ProjectForge and initialized from curated reconstruction evidence. Previous deleted MacroForge files are historical evidence only.

Initialization artifacts are complete. TASK-004 through TASK-020 are complete; TASK-021 is open:

- TASK-004: v0 PostgreSQL schema foundation exists as raw SQL, schema docs, health query, and schema tests.
- TASK-005: WDI live smoke support bundle evidence was normalized offline into an 8-row raw evidence slice with checksums and report. The current session did not retry the blocked World Bank HTTP request.
- TASK-006: WDI smoke rows load idempotently into isolated PostgreSQL staging/curated tables with no duplicate canonical grain.
- TASK-007: validation reporting and rerun runbook exist, and the validation report passes against an isolated PostgreSQL smoke database.
- TASK-008: post-vertical-slice architecture review is complete in DEC-005. The immediate architecture remains raw SQL/PostgreSQL/psql-based; hardening, a minimal source contract, and a no-key OECD/SDMX-style second-source spike are next.
- TASK-009: WDI vertical slice can be rerun with one isolated smoke command via `src/macroforge/wdi_smoke.py`; the command refuses live `macro` database writes.
- TASK-010: minimal source contract and WDI mapping exist in `docs/data/source-contract.md`.
- TASK-011: OECD/SDMX-style public source spike is complete in `artifacts/reports/oecd-sdmx-second-source-spike-20260603.md`; candidate is viable for a bounded next source-specific evidence slice.
- TASK-012: OECD/SDMX fixture-backed raw-evidence normalization is complete with source-specific parser/normalizer code, tests, project-layout raw XML, normalized metadata, and report evidence. No PostgreSQL load/schema change/general SDMX framework was introduced.
- TASK-013: OECD/SDMX live no-key rerunnable smoke command is complete. The command fetches the public endpoint with a source-specific User-Agent, writes project-layout evidence artifacts, defaults to bounded AUS/USA + B1GQ filters, and avoids PostgreSQL/schema/framework expansion.
- TASK-014: OECD/SDMX PostgreSQL promotion design is complete in DEC-006. It accepts promotion only after adding a narrow source-specific `staging.oecd_sdmx_observation` migration; the existing curated fact model remains sufficient for the bounded slice.
- TASK-015: OECD/SDMX PostgreSQL loader implementation is complete. It added `staging.oecd_sdmx_observation`, a source-specific loader from recorded normalized OECD evidence, isolated PostgreSQL idempotency tests, and a smoke load report preserving `USD_EXC`/`USD_PPP` plus observed SDMX attributes in the existing curated model.
- TASK-016: Post-second-source architecture review is complete in DEC-007. The decision keeps source-specific raw-SQL/PostgreSQL/psql architecture, keeps raw SQL migrations, rejects generalized source/SDMX/framework work for now, and accepts only tiny shared mechanical helper plus validation/reporting hardening.
- TASK-017: Shared validation and loader reporting hardening is complete. It added a tiny shared `db_helpers.py` module, tests, and behavior-preserving refactors for WDI/OECD loader and WDI validation mechanics without schema/source/framework/live behavior changes.
- TASK-018: Next scope decision after shared validation/reporting hardening is complete. DEC-008 chooses bounded source-specific OECD/SDMX codelist and label enrichment before a third-source spike.
- TASK-019: OECD/SDMX codelist and label enrichment spike is complete. It added bounded fixture-backed codelist parser/writer tests, source-specific label parsing/reporting in `oecd_sdmx.py`, project-layout metadata/report artifacts from recorded fixture/local XML, and source-contract documentation without live fetches, schema changes, PostgreSQL label loads, live `macro` writes, generalized SDMX/source framework work, third-source onboarding, or research/mart implementation.
- TASK-020: Third no-key source architecture spike is complete. DEC-009 accepted a bounded Eurostat `namq_10_gdp` public JSON-stat slice to validate the canonical model, ingestion framework posture, metadata architecture, and fact table design. The spike produced raw/normalized/report evidence and found report-only schema recommendations: period identity must support quarterly/monthly periods, territory modeling must account for provider geography codes and aggregates, and provider dimension/code metadata needs a clearer home before third-source PostgreSQL promotion.
- DEC-010: Canonical-domain schema evolution is accepted over provider-centric identities. It refines the TASK-020 response: structured period fields, ISO3 country identity, explicit territory types for aggregates, and provider period/territory codes as mappings/metadata rather than curated identities.
- TASK-021: Canonical period, territory, and provider mapping schema evolution design is open. It should produce a concrete schema design plan before any executable migration or Eurostat/third-source PostgreSQL promotion.
- Task-completion summary policy is now active in `AGENTS.md` and `context/context_policy.yaml`: completing agents should update task/state/handoff, refresh affected summaries, inspect refreshed `_SUMMARY.md` files for stale curated sections, and run final verification after governance/summary edits.

## Files changed in the completed implementation sequence

Core code/tests:

- `src/macroforge/wdi.py`
- `src/macroforge/wdi_loader.py`
- `src/macroforge/wdi_validation.py`
- `src/macroforge/wdi_smoke.py`
- `src/macroforge/oecd_sdmx.py`
- `src/macroforge/oecd_sdmx_loader.py`
- `src/macroforge/db_helpers.py`
- `tests/fixtures/oecd_sdmx_naag_sample.xml`
- `tests/test_oecd_sdmx.py`
- `tests/test_oecd_sdmx_loader.py`
- `tests/test_oecd_sdmx_codelists.py`
- `tests/fixtures/oecd_sdmx_naag_structure_sample.xml`
- `tests/test_db_helpers.py`
- `tests/test_wdi.py`
- `tests/test_wdi_loader.py`
- `tests/test_wdi_validation.py`
- `tests/test_wdi_smoke.py`
- `tests/test_schema_foundation.py`
- `pyproject.toml`

Database/docs/runbooks:

- `db/migrations/001_v0_schema_foundation.sql`
- `db/migrations/002_oecd_sdmx_staging.sql`
- `db/schema/v0_schema_foundation.md`
- `db/queries/schema_health_check.sql`
- `docs/data/v0-data-model.md`
- `docs/data/source-contract.md`
- `docs/architecture/canonical-domain-schema-evolution.md`
- `docs/runbooks/wdi-v1-runbook.md`

Evidence/reports:

- `data/raw/wdi/worldbank_wdi_NY.GDP.MKTP.CD_USA_DNK_2020_2021_raw.json`
- `data/raw/wdi/worldbank_wdi_SP.POP.TOTL_USA_DNK_2020_2021_raw.json`
- `data/metadata/wdi/wdi-smoke-manifest.json`
- `data/metadata/wdi/wdi-smoke-normalized.json`
- `artifacts/reports/wdi-smoke-20260602.md`
- `artifacts/reports/wdi-load-smoke-20260602.json`
- `artifacts/reports/wdi-validation-smoke-20260602.json`
- `artifacts/reports/wdi-validation-smoke-20260602.md`
- `artifacts/reports/wdi-isolated-smoke-rerun-20260603.json`
- `artifacts/reports/oecd-sdmx-second-source-spike-20260603.md`
- `data/raw/oecd_sdmx/oecd_sdmx_naag_2020_2021_raw.xml`
- `data/metadata/oecd_sdmx/oecd-sdmx-smoke-normalized.json`
- `artifacts/reports/oecd-sdmx-smoke-20260603.md`
- `artifacts/reports/oecd-sdmx-live-smoke-20260603.md`
- `artifacts/reports/oecd-sdmx-load-smoke-20260603.json`
- `data/raw/oecd_sdmx/oecd_sdmx_naag_structure_20260604.xml`
- `data/metadata/oecd_sdmx/oecd-sdmx-codelist-labels-20260604.json`
- `artifacts/reports/oecd-sdmx-codelist-labels-20260604.md`
- `data/raw/eurostat/eurostat-namq-10-gdp-2023q1-2023q2-raw.json`
- `data/metadata/eurostat/eurostat-namq-10-gdp-architecture-spike-normalized.json`
- `artifacts/reports/eurostat-third-source-architecture-spike-20260604.md`

Project operating-system updates:

- `artifacts/decisions/DEC-005-post-vertical-slice-architecture-and-next-source-scope.md`
- `artifacts/tasks/backlog.md`
- `artifacts/tasks/TASK-004-recreate-v0-postgresql-schema-foundation.md`
- `artifacts/tasks/TASK-005-recreate-narrow-wdi-extract-raw-evidence-slice.md`
- `artifacts/tasks/TASK-006-implement-postgresql-loader-for-wdi-staging-curated-facts.md`
- `artifacts/tasks/TASK-007-add-runbook-and-validation-reporting.md`
- `artifacts/tasks/TASK-008-review-architecture-after-first-vertical-slice.md`
- `artifacts/tasks/TASK-009-harden-wdi-vertical-slice-rerunnable-local-operation.md`
- `artifacts/tasks/TASK-010-define-minimal-source-contract-for-second-source-spike.md`
- `artifacts/tasks/TASK-011-spike-no-key-oecd-sdmx-style-second-source.md`
- `artifacts/tasks/TASK-012-implement-oecd-sdmx-raw-evidence-normalization.md`
- `artifacts/tasks/TASK-013-harden-oecd-sdmx-live-rerunnable-smoke-command.md`
- `artifacts/tasks/TASK-014-design-oecd-sdmx-postgresql-promotion.md`
- `artifacts/decisions/DEC-006-oecd-sdmx-postgresql-promotion.md`
- `artifacts/tasks/TASK-015-implement-oecd-sdmx-postgresql-loader.md`
- `artifacts/tasks/TASK-016-review-architecture-after-second-source.md`
- `artifacts/decisions/DEC-007-post-second-source-architecture-and-next-scope.md`
- `artifacts/tasks/TASK-017-harden-shared-validation-and-loader-reporting.md`
- `artifacts/tasks/TASK-018-decide-next-scope-after-shared-validation-reporting.md`
- `artifacts/decisions/DEC-008-next-scope-after-shared-validation-reporting.md`
- `artifacts/tasks/TASK-019-spike-oecd-sdmx-codelist-label-enrichment.md`
- `artifacts/decisions/DEC-009-third-source-spike-scope.md`
- `artifacts/tasks/TASK-020-spike-third-no-key-source-eurostat-architecture-validation.md`
- `artifacts/decisions/DEC-010-canonical-domain-schema-evolution.md`
- `artifacts/tasks/TASK-021-design-canonical-period-territory-provider-mapping-schema-evolution.md`
- `simulation/dry_runs/20260604_083947-canonical-domain-schema-design-note.md`
- `simulation/dry_runs/20260604_081341-task-020-third-no-key-source-spike-eurostat.md`
- `simulation/dry_runs/20260604_075457-implement-task-019-oecd-sdmx-codelist-label-enrichment.md`
- `simulation/dry_runs/20260604_073353-implement-task-017-shared-validation-loader-reporting.md`
- `simulation/dry_runs/20260603_214803-open-task-014-oecd-postgresql-promotion-design.md`
- `simulation/dry_runs/20260603_220913-implement-task-015-oecd-sdmx-postgresql-loader.md`
- `simulation/dry_runs/20260603_222247-open-task-016-post-second-source-architecture-review.md`
- `simulation/dry_runs/20260603_223359-execute-task-016-post-second-source-architecture-review.md`
- folder `_SUMMARY.md` files for affected areas
- `state/active_goal.md`
- `state/project_state.md`
- `state/architecture.md`
- `context/latest_handoff.md`

## Verification completed

Canonical-domain schema design note / DEC-010 verification:

```text
python3 tools/build_context.py --project . --model-target cloud --context-mode governance --task-type architecture_decision --task "Re-evaluate TASK-020 Eurostat schema recommendations from canonical-domain perspective: compare provider-centric vs canonical-domain schema evolution for periods, territories, provider mappings, and long-term heterogeneous macro source integration" --decisions DEC-009 --model-selected gpt-5.5 --model-reason "Current user requested a schema design re-evaluation and comparison note after Eurostat architecture spike"

{
  "context": "/home/mkkto/srv/projectforge/workspace/projects/macroforge/context/active_context.md",
  "audit": "/home/mkkto/srv/projectforge/workspace/projects/macroforge/context/context_audit.json",
  "estimated_tokens": 7645,
  "budget_tokens": 10000,
  "within_budget": true,
  "context_mode": "governance"
}

python3 tools/validate_dry_run.py simulation/dry_runs/20260604_083947-canonical-domain-schema-design-note.md

valid: simulation/dry_runs/20260604_083947-canonical-domain-schema-design-note.md
```

Final tests/coherence after DEC-010/TASK-021 governance/summary/handoff updates:

```text
PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests -q && python3 tools/check_coherence.py --project . --json

.................................                                        [100%]
33 passed in 1.74s
{
  "mode": "generated",
  "blocks": [],
  "warnings": []
}
```

TASK-020 third-source architecture spike verification before governance/summary closeout:

```text
python3 tools/validate_dry_run.py simulation/dry_runs/20260604_081341-task-020-third-no-key-source-spike-eurostat.md

valid: simulation/dry_runs/20260604_081341-task-020-third-no-key-source-spike-eurostat.md

Eurostat public no-key source fetch/artifact generation:

{
  "content_type": "application/json",
  "normalized": "data/metadata/eurostat/eurostat-namq-10-gdp-architecture-spike-normalized.json",
  "raw_artifact": "data/raw/eurostat/eurostat-namq-10-gdp-2023q1-2023q2-raw.json",
  "raw_bytes": 3262,
  "report": "artifacts/reports/eurostat-third-source-architecture-spike-20260604.md",
  "row_count": 4,
  "sha256": "914888671969cf31253dc0e951aaa8bee66bbf8ec03d1ff193bc6b1feda1865a",
  "status": 200
}

sha256sum data/raw/eurostat/eurostat-namq-10-gdp-2023q1-2023q2-raw.json && wc -c data/raw/eurostat/eurostat-namq-10-gdp-2023q1-2023q2-raw.json

914888671969cf31253dc0e951aaa8bee66bbf8ec03d1ff193bc6b1feda1865a  data/raw/eurostat/eurostat-namq-10-gdp-2023q1-2023q2-raw.json
3262 data/raw/eurostat/eurostat-namq-10-gdp-2023q1-2023q2-raw.json
```

Final tests/coherence after TASK-020 governance/summary/handoff updates:

```text
PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests -q && python3 tools/check_coherence.py --project . --json

.................................                                        [100%]
33 passed in 1.72s
{
  "mode": "generated",
  "blocks": [],
  "warnings": []
}
```


TASK-019 implementation verification before governance/summary closeout:

```text
python3 tools/validate_dry_run.py simulation/dry_runs/20260604_075457-implement-task-019-oecd-sdmx-codelist-label-enrichment.md

valid: simulation/dry_runs/20260604_075457-implement-task-019-oecd-sdmx-codelist-label-enrichment.md

PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests/test_oecd_sdmx_codelists.py -q

....                                                                     [100%]
4 passed in 0.03s

PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests/test_oecd_sdmx.py tests/test_oecd_sdmx_codelists.py -q

...........                                                              [100%]
11 passed in 0.03s

PYTHONPATH=src python3 -m macroforge.oecd_sdmx --input-structure-xml tests/fixtures/oecd_sdmx_naag_structure_sample.xml --project-root . --write-codelist-labels --structure-endpoint 'https://sdmx.oecd.org/public/rest/v1/dataflow/OECD.SDD.NAD/all/latest'

{
  "normalized_labels": "data/metadata/oecd_sdmx/oecd-sdmx-codelist-labels-20260604.json",
  "raw_structure_artifact": "data/raw/oecd_sdmx/oecd_sdmx_naag_structure_20260604.xml",
  "report": "artifacts/reports/oecd-sdmx-codelist-labels-20260604.md"
}

PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests -q

.................................                                        [100%]
33 passed in 1.67s
```

Final verification after TASK-019 governance/summary/handoff updates:

```text
PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests -q && python3 tools/check_coherence.py --project . --json

.................................                                        [100%]
33 passed in 1.79s
{
  "mode": "generated",
  "blocks": [],
  "warnings": []
}
```

Latest final verification after completing TASK-018, accepting DEC-008, opening TASK-019, updating state/handoff/summaries, and writing the final handoff:

```text
PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests -q && python3 tools/check_coherence.py --project . --json

.............................                                            [100%]
29 passed in 1.74s
{
  "mode": "generated",
  "blocks": [],
  "warnings": []
}
```

TASK-017 implementation verification before governance/summary closeout:

```text
python3 tools/validate_dry_run.py simulation/dry_runs/20260604_073353-implement-task-017-shared-validation-loader-reporting.md

valid: simulation/dry_runs/20260604_073353-implement-task-017-shared-validation-loader-reporting.md

PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests/test_db_helpers.py tests/test_wdi_loader.py tests/test_oecd_sdmx_loader.py tests/test_wdi_validation.py -q

.........                                                                [100%]
9 passed in 1.75s

PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests -q

.............................                                            [100%]
29 passed in 2.09s

python3 tools/check_coherence.py --project . --json

{
  "mode": "generated",
  "blocks": [],
  "warnings": []
}
```

Final verification after TASK-017 governance/handoff/summary updates and TASK-018 opening:

```text
PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests -q && python3 tools/check_coherence.py --project . --json

.............................                                            [100%]
29 passed in 1.85s
{
  "mode": "generated",
  "blocks": [],
  "warnings": []
}
```

Final verification after updating TASK-016 artifact, project state, latest handoff, and affected summaries for closeout:

```text
PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests -q && python3 tools/check_coherence.py --project . --json

.........................                                                [100%]
25 passed in 1.67s
{
  "mode": "generated",
  "blocks": [],
  "warnings": []
}
```

Final handoff cleanup after completing TASK-016 replaced the pending verification placeholder, reran the full MacroForge test suite plus generated-project coherence, and reran coherence after recording verification:

```text
PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests -q && python3 tools/check_coherence.py --project . --json

.........................                                                [100%]
25 passed in 1.71s
{
  "mode": "generated",
  "blocks": [],
  "warnings": []
}

python3 tools/check_coherence.py --project . --json

{
  "mode": "generated",
  "blocks": [],
  "warnings": []
}
```

Latest full MacroForge test suite and generated-project coherence after completing TASK-016, accepting DEC-007, opening TASK-017, and updating state/handoff/summaries:

```text
PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests -q && python3 tools/check_coherence.py --project . --json

.........................                                                [100%]
25 passed in 1.73s
{
  "mode": "generated",
  "blocks": [],
  "warnings": []
}
```

Latest full MacroForge test suite and generated-project coherence after opening TASK-016 and updating state/handoff/summaries:

```text
PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests -q && python3 tools/check_coherence.py --project . --json

.........................                                                [100%]
25 passed in 1.79s
{
  "mode": "generated",
  "blocks": [],
  "warnings": []
}
```

Latest full MacroForge test suite after completing TASK-015 implementation:

```text
PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests -q

.........................                                                [100%]
25 passed in 1.63s
```

Latest isolated PostgreSQL TASK-015 smoke executed a temporary database, applied migrations `001` and `002`, ran the OECD/SDMX loader twice with the same run key, and inspected database truth:

```text
{
  "attribute_sets": 1,
  "fact_rows": 8,
  "lineage_events": 2,
  "quality_checks": 4,
  "staging_rows": 8,
  "unit_codes": [
    "USD_EXC",
    "USD_PPP"
  ]
}
{
  "attribute_sets": 1,
  "fact_rows": 8,
  "lineage_events": 2,
  "quality_checks": 4,
  "staging_rows": 8,
  "unit_codes": [
    "USD_EXC",
    "USD_PPP"
  ]
}
8
8
USD_EXC,USD_PPP
{"DECIMALS": "2", "OBS_STATUS": "A", "CONF_STATUS": "F"}
```

Final full-suite/coherence verification after recording TASK-015 governance and summary updates:

```text
PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests -q && python3 tools/check_coherence.py --project . --json

.........................                                                [100%]
25 passed in 1.64s
{
  "mode": "generated",
  "blocks": [],
  "warnings": []
}
```

Earlier full-suite/coherence evidence after TASK-014 remains:

```text
PYTHONPATH=src uvx --from pytest --with pyyaml pytest tests -q
python3 tools/check_coherence.py --project . --json

......................                                                   [100%]
22 passed in 1.40s
{
  "mode": "generated",
  "blocks": [],
  "warnings": []
}
```

TASK-007 isolated validation report status:

```text
"status": "pass"
```

## Remaining risks / cautions

- The current session must not retry the previously blocked World Bank HTTP request. TASK-005 uses the support bundle at `artifacts/handoffs/wdi-live-smoke-support-20260602/` as live API evidence.
- The default database name remains `macro`, but implementation verification intentionally used isolated temporary PostgreSQL databases. Do not load into a live `macro` database without explicit user approval and a fresh dry-run.
- Raw data artifacts and metadata are ignored by default in `.gitignore`; if they need versioning, force-add deliberately or create a fixture policy decision.
- TASK-006/TASK-007 use a minimal psql-based loader/validator. DEC-005 keeps that approach for immediate hardening and defers Alembic/SQLAlchemy/orchestration until schema evolution or multiple manual source pipelines justify them.
- TASK-013 live no-key OECD/SDMX smoke succeeded with a source-specific User-Agent header. Treat that header as part of the source-specific operational contract unless OECD access behavior changes.
- The live bounded OECD/SDMX smoke now returns 8 rows because `UNIT_MEASURE` includes both `USD_EXC` and `USD_PPP`; future PostgreSQL promotion must explicitly decide unit/grain handling before schema or curated-load work.
- The normalized OECD/SDMX evidence and TASK-019 label evidence are source-specific and bounded. Do not convert labels into schema changes, broad codelist harvesting, or a generalized SDMX framework without a new accepted decision.
- TASK-020 Eurostat evidence validates the broad canonical observation model but identifies schema gaps around period, territory, and provider metadata. DEC-010 refines the response: use structured canonical periods, keep ISO3 as canonical country identity, add territory types for aggregates, and store provider codes in mappings/metadata. Do not promote Eurostat or another third source into PostgreSQL until those gaps are resolved by a new accepted decision.

## Stable defaults

- ProjectForge-native file-backed operating system.
- PostgreSQL analytical store.
- Filesystem raw evidence/checksums/run logs/reports.
- World Bank WDI first v1 source.
- Default database name `macro` unless live verification proves otherwise.
- No paid/credentialed APIs, autonomous deployment, Docker/cloud dependency, or git push in v1 without explicit decision and human approval.
- Local execution / cloud governance.
- Standard task-completion summary policy: affected-summary refresh, summary inspection, and final verification after governance/summary edits.

## Active task

TASK-021 is open: design canonical period, territory, and provider mapping schema evolution.

Do not implement broad source/framework work, schema changes, third-source PostgreSQL promotion, research/mart work, or live `macro` writes without a fresh accepted decision and dry-run.

## Source of truth

Durable project truth lives in this project: state files, decisions, tasks, docs, context summaries, and run evidence. Raw historical exports are evidence only until curated.
