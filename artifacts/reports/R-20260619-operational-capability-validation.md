# MacroForge Operational Capability Validation

Date: 2026-06-19
Status: completed bounded operational validation
Scope: verify what MacroForge can actually do today before freezing development.

## Boundaries preserved

This task did not add features, add sources, expand architecture, add schemas, create dashboards, create agents, create report-generation systems, create new projects, commit, or push.

Operational validation did execute existing workflows against isolated temporary PostgreSQL databases and `/tmp` output paths. One existing WDI smoke workflow was tested and failed; the failure is recorded below.

## Executive verdict

MacroForge is analytically v1-complete but not yet operationally freeze-ready.

The combined PostgreSQL reconstruction path works today for the current bounded WDI/OECD/Eurostat evidence. However, two operational freeze blockers remain:

1. The WDI-only isolated smoke runbook/workflow is stale and fails because it applies only migration `001_v0_schema_foundation.sql` while the current WDI loader expects later canonical-domain columns such as `curated.dim_territory.territory_type`.
2. OECD and Eurostat source fixture artifacts required for reconstruction exist in the working tree under ignored `data/` paths, but are not tracked by git. A final commit without resolving this would not be self-contained for clean-clone reconstruction.

Therefore MacroForge should not be frozen or committed as v1-final until those two operational blockers are resolved.

## Phase 1 — Existing source refresh audit

### Supported source inventory

| Source | Source name | Ingestion path | Last successful evidence | Current status | Refresh operational today? | Tested in this validation | Confidence | Blockers |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `WDI` | World Bank World Development Indicators | `src/macroforge/wdi.py` support-bundle/raw normalization; `src/macroforge/wdi_loader.py`; `src/macroforge/wdi_smoke.py`; migration `001` in WDI-only smoke; all migrations in combined smoke/snapshot | `artifacts/reports/wdi-isolated-smoke-rerun-20260603.json`, plus successful combined validation in this run | Partially operational | Raw/metadata regeneration from support bundle works; WDI-only isolated DB smoke fails; WDI participates successfully in combined reconstruction | Yes | Medium | WDI-only smoke workflow stale against current schema evolution. Live World Bank refresh is intentionally not tested; runbook says use support bundle. |
| `OECD_NAAG` | OECD/SDMX bounded NAAG GDP evidence | `src/macroforge/oecd_sdmx.py`; `src/macroforge/oecd_sdmx_loader.py`; migration `002`; combined smoke/snapshot workflows | `artifacts/reports/oecd-sdmx-load-smoke-20260603.json`, `artifacts/reports/combined-source-canonical-smoke-20260604.json`, current `/tmp` combined validation | Operational from existing fixture in working tree | Yes, fixture-backed load through combined smoke | Yes | Medium-high for current working tree; low for clean clone | Required normalized/raw fixture files under ignored `data/` paths are not tracked by git. |
| `EUROSTAT_NAMQ_GDP` | Eurostat quarterly national accounts GDP bounded fixture | `src/macroforge/eurostat_namq_loader.py`; migration `004`; combined smoke/snapshot workflows | `artifacts/reports/eurostat-namq-load-smoke-20260604.json`, `artifacts/reports/combined-source-canonical-smoke-20260604.json`, current `/tmp` combined validation | Operational from existing fixture in working tree | Yes, fixture-backed load through combined smoke | Yes | Medium-high for current working tree; low for clean clone | Required normalized/raw fixture files under ignored `data/` paths are not tracked by git. |

### Bounded refresh validation performed

#### WDI raw/metadata support-bundle refresh

Command executed:

```bash
PYTHONPATH=src python3 -m macroforge.wdi smoke-from-bundle \
  --bundle artifacts/handoffs/wdi-live-smoke-support-20260602 \
  --output-root /tmp/macroforge-opval/wdi-refresh \
  --project-layout
```

Result: succeeded.

Output paths reported by command:

```text
/tmp/macroforge-opval/wdi-refresh/data/metadata/wdi/wdi-smoke-manifest.json
/tmp/macroforge-opval/wdi-refresh/data/metadata/wdi/wdi-smoke-normalized.json
/tmp/macroforge-opval/wdi-refresh/data/raw/wdi
/tmp/macroforge-opval/wdi-refresh/artifacts/reports/wdi-smoke-20260602.md
```

Interpretation: WDI support-bundle artifact regeneration works without live network.

#### WDI isolated smoke validation

Command executed:

```bash
PYTHONPATH=src python3 -m macroforge.wdi_smoke \
  --project-root . \
  --report /tmp/macroforge-opval/wdi-isolated-smoke.json
```

Result: failed.

Reproduction/debug result:

```text
psql:/tmp/macroforge-wdi-load-debug.sql:107: ERROR:  column "territory_type" of relation "dim_territory" does not exist
LINE 4: INSERT INTO curated.dim_territory (territory_type, iso3_code...
```

Cause: `wdi_smoke.py` applies only `db/migrations/001_v0_schema_foundation.sql`, but the current WDI loader now expects canonical-domain schema columns introduced by later migrations.

Interpretation: WDI-only operational refresh is not reliable today. WDI can still load as part of the all-migrations combined workflow.

#### Combined source reconstruction/refresh validation

Command executed:

```bash
PYTHONPATH=src python3 -m macroforge.combined_source_smoke \
  --project-root . \
  --report /tmp/macroforge-opval2/combined-source-smoke.json
```

Result: succeeded.

Observed output:

```text
status: succeeded
sources: EUROSTAT_NAMQ_GDP, OECD_NAAG, WDI
source_count: 3
dataset_release_count: 3
staging rows: WDI 8, OECD 8, Eurostat 4
fact_rows_by_source: WDI 8, OECD_NAAG 8, EUROSTAT_NAMQ_GDP 4
fact_rows_total: 20
duplicate_fact_grain_count: 0
failing_quality_checks: 0
checks: all pass
cleanup: dropdb --if-exists executed
```

Interpretation: current all-source fixture-backed PostgreSQL reconstruction works in an isolated database.

#### Canonical GDP snapshot reconstruction validation

Command executed:

```bash
PYTHONPATH=src python3 -m macroforge.canonical_gdp_snapshot \
  --project-root . \
  --json-report /tmp/macroforge-opval2/canonical-gdp-snapshot.json \
  --markdown-report /tmp/macroforge-opval2/canonical-gdp-snapshot.md
```

Result: succeeded.

Observed output:

```text
status: succeeded
fact_rows_total: 20
missing_observations: 0
duplicate_fact_grains: 0
```

Snapshot checks:

```text
annual_and_quarterly_explicit: pass
core_query_boundary: pass
missingness_bounded_fixture_complete: pass
no_duplicate_fact_grain: pass
quality_checks_pass: pass
```

Interpretation: current canonical reporting reconstruction works from existing fixture-backed source artifacts in the working tree.

## Phase 2 — PostgreSQL reconstruction audit

### Current reconstruction procedure that works

The current reliable reconstruction path is:

1. Start from existing working tree with ignored source fixtures present under `data/`.
2. Create isolated temporary PostgreSQL database.
3. Apply migrations in order:
   - `db/migrations/001_v0_schema_foundation.sql`
   - `db/migrations/002_oecd_sdmx_staging.sql`
   - `db/migrations/003_canonical_domain_dimensions.sql`
   - `db/migrations/004_eurostat_namq_staging.sql`
4. Load WDI normalized evidence from `data/metadata/wdi/wdi-smoke-normalized.json`.
5. Load OECD normalized evidence from `data/metadata/oecd_sdmx/oecd-sdmx-smoke-normalized.json`.
6. Load Eurostat normalized evidence from `data/metadata/eurostat/eurostat-namq-10-gdp-architecture-spike-normalized.json`.
7. Validate combined source counts, lineage, mappings, quality checks, duplicate grains, canonical frequencies, and canonical territories.
8. Optionally generate canonical GDP snapshot from `curated.*` plus `meta.*` only.
9. Drop isolated temporary database.

This is implemented by:

```bash
PYTHONPATH=src python3 -m macroforge.combined_source_smoke --project-root . --report /tmp/combined-source-smoke.json
PYTHONPATH=src python3 -m macroforge.canonical_gdp_snapshot --project-root . --json-report /tmp/canonical-gdp-snapshot.json --markdown-report /tmp/canonical-gdp-snapshot.md
```

### Reconstruction possible?

Yes, from the current working tree.

Not safely proven from a clean clone/final commit, because OECD and Eurostat source fixtures under `data/` are ignored and not tracked.

Tracked data files currently are only summaries/placeholders:

```text
data/_SUMMARY.md
data/curated/_SUMMARY.md
data/metadata/_SUMMARY.md
data/raw/_SUMMARY.md
data/staging/_SUMMARY.md
```

Ignored but required source fixture files exist today:

```text
data/raw/wdi: 2 files
data/metadata/wdi: 2 files
data/raw/oecd_sdmx: 2 files
data/metadata/oecd_sdmx: 2 files
data/raw/eurostat: 1 file
data/metadata/eurostat: 1 file
```

WDI raw support bundle is tracked under `artifacts/handoffs/wdi-live-smoke-support-20260602/`, so WDI data/metadata can be regenerated. No equivalent tracked source fixture bundle was confirmed for OECD/Eurostat in this validation.

### Reconstruction documented?

Partially.

Documented:

- WDI runbook exists at `docs/runbooks/wdi-v1-runbook.md`, but its isolated smoke command is stale.
- Combined reconstruction is implemented in code and tests, but there is no single current operational runbook stating the all-migrations reconstruction command and its clean-clone prerequisites.
- State/handoff artifacts point to current capabilities and recovery anchors.

### Reconstruction deterministic?

Partially.

Deterministic aspects:

- Migrations are explicit SQL files.
- Combined smoke uses isolated temporary DB and fixed expected counts.
- Canonical GDP snapshot has deterministic `generated_at` and deterministic content except temporary database name in metadata.
- Current validation produced 20 fact rows, 0 duplicate fact grains, 0 failing quality checks, and all required checks passing.

Non-deterministic/noisy aspects:

- Temporary database names appear in JSON report metadata and can cause git diffs if default report paths are used.
- WDI-only smoke runbook is not deterministic-successful because it applies stale migration set.
- Clean-clone reconstruction is not deterministic unless source fixture persistence is resolved.

### Confidence assessment

- Current working-tree combined reconstruction: high.
- Current working-tree WDI-only isolated refresh: low; confirmed failing.
- Clean-clone reconstruction after final commit as currently staged: low to medium, because required ignored fixtures may be absent.
- Freeze readiness: not yet ready.

## Phase 3 — Repository hygiene review

### Current git state summary

Modified tracked files:

| File | Classification | Recommendation |
| --- | --- | --- |
| `artifacts/reports/_SUMMARY.md` | generated artifact summary | Commit if it only reflects accepted report/task additions after final cleanup. |
| `artifacts/tasks/_SUMMARY.md` | generated artifact summary | Commit if it reflects accepted task additions after final cleanup. |
| `artifacts/tasks/backlog.md` | reports/governance state | Commit if TASK-041/TASK-042/v1 closure entries are intended. |
| `context/latest_handoff.md` | generated/current state | Commit after updating with this operational validation result. |
| `simulation/dry_runs/_SUMMARY.md` | generated artifact summary | Commit if corresponding dry-run artifact is committed; otherwise regenerate after pruning. |
| `state/active_goal.md` | current state | Commit after adding operational freeze blocker if accepted. |
| `state/architecture.md` | architecture/current state | Commit only because it already reflects current state; do not add new architecture content from this task. |
| `state/project_state.md` | current state | Commit after adding operational freeze blocker if accepted. |
| `state/recent_changes.md` | current state | Commit after adding operational validation result. |

Volatile report diffs found and cleaned during validation:

- `artifacts/reports/canonical-gdp-snapshot-20260604.json`
- `artifacts/reports/combined-source-canonical-smoke-20260604.json`

They differed only by temporary database names in metadata. They were restored to HEAD to avoid commit noise.

Untracked files:

| File | Classification | Recommendation |
| --- | --- | --- |
| `artifacts/reports/R-20260619-comparability-research-readiness-assessment.md` | report | Commit if TASK-041 is part of v1 closeout. |
| `artifacts/reports/R-20260619-gdp-eligibility-classification-validation.md` | report | Commit with TASK-042. |
| `artifacts/reports/R-20260619-v1-closure-review.md` | report | Commit with v1 closeout, after operational blocker is recorded. |
| `artifacts/reports/R-20260619-operational-capability-validation.md` | report | Commit as the operational validation before freeze. |
| `artifacts/reports/canonicalization-oecd-mapping-status-review-20260618.json` | report/generated evidence | Commit if this is source of current OECD status. |
| `artifacts/reports/canonicalization-oecd-mapping-status-review-20260618.md` | report | Commit if this is source of current OECD status. |
| `artifacts/reports/gdp-eligibility-classification-20260619.json` | generated classification artifact | Commit with TASK-042. |
| `artifacts/tasks/TASK-041-comparability-research-readiness-assessment.md` | task record | Commit with TASK-041. |
| `artifacts/tasks/TASK-042-gdp-eligibility-classification-artifact.md` | task record | Commit with TASK-042. |
| `simulation/dry_runs/20260618_223001-oecd-mapping-status-review.md` | dry-run artifact | Commit if the OECD mapping-status review is committed; otherwise archive/prune consistently. |
| `artifacts/reports/R-20260619-metaharvest-trigger-gated-retrieval-future-work.md` | future-work note / scope-expansion candidate | Do not include in final MacroForge v1 commit unless explicitly approved. It is not required for operational v1 closure and risks reopening workflow scope. |

Ignored but operationally important files:

| Path | Classification | Recommendation |
| --- | --- | --- |
| `data/raw/wdi/*` and `data/metadata/wdi/*` | generated source artifacts | Do not rely on ignored copies for final commit; WDI can be regenerated from tracked support bundle. |
| `data/raw/oecd_sdmx/*` and `data/metadata/oecd_sdmx/*` | required source fixture artifacts | Must either be explicitly tracked, moved to a tracked fixture/evidence location, or regenerated from tracked artifacts before freeze. |
| `data/raw/eurostat/*` and `data/metadata/eurostat/*` | required source fixture artifacts | Must either be explicitly tracked, moved to a tracked fixture/evidence location, or regenerated from tracked artifacts before freeze. |
| `.pytest_cache/`, `__pycache__/` | temporary artifacts | Ignore/delete, do not commit. |

### Recommended commit plan

Do not commit yet.

Before final commit:

1. Fix or document the WDI-only smoke runbook/workflow mismatch so existing refresh validation does not fail.
   - Smallest fix likely: update `wdi_smoke.py`/runbook to apply the current migration chain required by `wdi_loader.py`, or explicitly retire WDI-only smoke in favor of combined reconstruction if that is the intended operational path.
   - This is an operational bug fix, not architecture expansion.

2. Resolve source fixture persistence for OECD and Eurostat.
   - Either commit the minimal bounded fixture files despite the broad `data/` ignore rule using explicit `git add -f`, or move/copy them into a tracked evidence/fixture location with a documented reconstruction path.
   - Do not add new data; preserve only current bounded fixtures.

3. Exclude or explicitly approve `R-20260619-metaharvest-trigger-gated-retrieval-future-work.md`.
   - It is a future-work/scope candidate, not part of operational v1 closure.

4. Regenerate summaries and run full checks.

5. Suggested final commit grouping:
   - Commit A: operational fix for reconstruction/refresh only, if code/runbook changes are required.
   - Commit B: v1 closeout evidence artifacts and state updates, including TASK-041/TASK-042/v1 closure/operational validation reports and minimal required fixture persistence.

## Phase 4 — Freeze readiness assessment

### 1. Can MacroForge reliably refresh existing data?

Not fully.

- WDI support-bundle raw/metadata regeneration works.
- Combined fixture-backed refresh/reconstruction works for WDI/OECD/Eurostat.
- WDI-only isolated smoke refresh fails today due to stale migration assumptions.
- Live source refresh is not established for current freeze; WDI live is explicitly not retried, OECD/Eurostat are bounded recorded fixtures.

Answer: partially, but not enough to freeze operationally.

### 2. Can MacroForge rebuild its PostgreSQL-backed state?

Yes from the current working tree.

Not proven from a final clean commit because OECD/Eurostat source fixture artifacts are ignored and untracked.

Answer: operationally yes in the current environment; repository-level reproducibility not yet guaranteed.

### 3. Is the repository in a healthy state?

Not yet.

Reasons:

- many v1 closeout artifacts are untracked;
- one future-work MetaHarvest note appears untracked and likely should not be included in v1 final commit without approval;
- required source fixture artifacts are ignored;
- WDI-only smoke workflow is stale;
- generated summary/state files need final consistency after operational blocker disposition.

### 4. What must be completed before a final commit?

Minimum before final commit:

1. Resolve the WDI-only smoke failure or formally retire it in favor of combined reconstruction.
2. Ensure all source fixtures required for clean-clone reconstruction are tracked or reproducibly regenerated from tracked artifacts.
3. Decide whether to exclude the MetaHarvest future-work note from the v1 commit.
4. Regenerate summaries.
5. Run:
   - `uvx --from pytest --with pyyaml pytest tests -q`
   - `PYTHONPATH=src python3 -m macroforge.combined_source_smoke --project-root . --report /tmp/combined-source-smoke.json`
   - `PYTHONPATH=src python3 -m macroforge.canonical_gdp_snapshot --project-root . --json-report /tmp/canonical-gdp-snapshot.json --markdown-report /tmp/canonical-gdp-snapshot.md`
   - `python3 tools/update_context_summaries.py --project .`
   - `python3 tools/check_coherence.py --project . --json`
   - `python3 tools/context_health.py --project . --json`
6. Confirm `git status --short` contains only intended commit files and no volatile generated report diffs.

### 5. Is MacroForge truly ready to enter maintenance mode?

No.

MacroForge is conceptually ready to freeze, but operationally it needs a small closure hardening step first.

This task discovered real operational blockers, not roadmap desires:

- WDI-only refresh workflow failure;
- source fixture persistence gap for clean-clone reconstruction.

Those should be fixed before declaring final v1 maintenance mode.

## Validation command record

Executed successfully:

```bash
command -v psql
command -v createdb
command -v dropdb
psql --version
createdb --version
python3 --version
```

Observed:

```text
/usr/bin/psql
/usr/bin/createdb
/usr/bin/dropdb
psql (PostgreSQL) 16.14 (Ubuntu 16.14-0ubuntu0.24.04.1)
createdb (PostgreSQL) 16.14 (Ubuntu 16.14-0ubuntu0.24.04.1)
Python 3.12.3
```

Executed successfully:

```bash
PYTHONPATH=src python3 -m macroforge.wdi smoke-from-bundle --bundle artifacts/handoffs/wdi-live-smoke-support-20260602 --output-root /tmp/macroforge-opval/wdi-refresh --project-layout
PYTHONPATH=src python3 -m macroforge.combined_source_smoke --project-root . --report /tmp/macroforge-opval2/combined-source-smoke.json
PYTHONPATH=src python3 -m macroforge.canonical_gdp_snapshot --project-root . --json-report /tmp/macroforge-opval2/canonical-gdp-snapshot.json --markdown-report /tmp/macroforge-opval2/canonical-gdp-snapshot.md
uvx --from pytest --with pyyaml pytest tests -q
```

Test result:

```text
70 passed in 5.73s
```

Executed and failed as expected after validation exposed stale workflow:

```bash
PYTHONPATH=src python3 -m macroforge.wdi_smoke --project-root . --report /tmp/macroforge-opval/wdi-isolated-smoke.json
```

Failure:

```text
ERROR: column "territory_type" of relation "dim_territory" does not exist
```

## Final operational judgment

Do not freeze yet.

The next action should be a bounded operational hardening fix, not a new roadmap item or architecture expansion:

1. repair/retire the stale WDI-only smoke workflow;
2. make required OECD/Eurostat bounded fixtures available from tracked commit state;
3. rerun the operational validation and commit only after git hygiene is clean.
