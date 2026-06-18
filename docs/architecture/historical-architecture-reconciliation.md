# Historical Architecture Reconciliation

Date: 2026-06-05

Purpose: Reconcile historical Desktop/ChatGPT architecture concepts against the current MacroForge file-backed ProjectForge architecture so future agents do not accidentally restore superseded designs.

## Authority rule

Historical Desktop exports, PDFs, scaffold archives, and deleted-project files are evidence. Current MacroForge authority is the file-backed project state, accepted decision artifacts, active task artifacts, and validated implementation in this repository.

## Classification table

| Historical concept | Classification | Current treatment | Rationale |
| --- | --- | --- | --- |
| `mf_task.sh` wrapper | Superseded | Replaced by Hermes-native task execution plus ProjectForge task artifacts, dry-runs, and `tools/check_coherence.py`/`tools/update_context_summaries.py`. | Current AGENTS.md says Hermes tools are the normal execution layer. A separate task wrapper is not needed for normal Hermes work. |
| `mf_db.sh` wrapper | Superseded | Replaced by explicit raw SQL migrations, source-specific Python loaders, isolated PostgreSQL smoke commands, and documented verification commands. | Database safety is enforced through decisions, dry-runs, isolated temp DBs, and live/default `macro` refusal boundaries rather than a shell wrapper. |
| `mf_git.sh` wrapper | Superseded | Replaced by normal local git inspection/mutation under ProjectForge permission rules; remote push still requires human approval. | GitHub push and destructive/history-changing operations remain human-gated. A wrapper may be reconsidered only if git workflow becomes repetitive and error-prone. |
| `mf_test.sh` wrapper | Superseded | Replaced by explicit test/coherence commands reported in handoffs and final summaries. | Tests are run directly via Hermes/terminal. The current convention is to report exact command output, not hide it behind a wrapper. |
| OS-level agent users | Deferred | Not implemented in MacroForge. Use file-backed policy, Hermes approvals, explicit dry-runs, and no production/live write defaults for now. | The project currently operates locally with no production data, secrets, deployment, or paid APIs. OS-level isolation may be revisited for production or multi-agent service operation. |
| Shared loader framework | Rejected for now | Current implementation uses source-specific loaders plus a tiny mechanical `db_helpers.py` helper. | DEC-007 and DEC-013 explicitly reject generalized source/SDMX/JSON-stat/plugin frameworks until repeated source pressure justifies them. |
| One shared PostgreSQL loader module | Replaced | Shared mechanics are limited to SQL/JSONB literal rendering, psql execution/parsing, and JSON report writing in `src/macroforge/db_helpers.py`. | This preserves behavior and avoids premature semantic framework extraction. |
| `dim_status` / `status_id` | Deferred/rejected for current scope | Current facts use `observation_status` text and source attributes/quality checks. No status dimension is implemented. | Existing bounded reports do not require a status dimension. Add only if validation/reporting pressure justifies it. |
| `value_text` in fact observations | Deferred | Current `curated.fact_observation.value` is numeric; non-numeric values remain out of scope. | Current WDI/OECD/Eurostat slices are numeric macro observations. Text values need a future accepted design. |
| `bridge_source_indicator` | Replaced | Provider/source indicator identity remains in source-scoped `curated.dim_indicator`; future canonical concept mapping is reserved for TASK-030 design. | Current canonical-domain design avoids provider-centric identities while preserving source-specific indicators. TASK-030 should design auditable canonicalization/mapping rather than restore a bridge table blindly. |
| Full per-run folders | Replaced/deferred | Evidence and reports are stored in project-layout `data/raw`, `data/metadata`, `artifacts/reports`, task artifacts, handoffs, and optional logs. | Full run folders are not required for current governance. They may be reconsidered if operational replay/debugging needs exceed current report artifacts. |

## Current project position

MacroForge should not restore the historical wrapper-first operating model. It should continue with Hermes-native execution, ProjectForge file-backed governance, raw SQL migrations, source-specific loaders, isolated database verification, optional debug logs, and summary-first context.

Future restoration or implementation of any deferred concept requires a new decision artifact, risk-scaled dry-run, and validation plan.
