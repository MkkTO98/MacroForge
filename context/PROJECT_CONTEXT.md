# MacroForge Project Context

MacroForge is a long-lived, personal/internal, AI-first platform for macroeconomic and later investment/equity research.

## Source hierarchy

1. Current user instruction and current MacroForge project artifacts.
2. Curated reconstruction documents under `context/reconstruction/`.
3. ProjectForge setup answers and generated setup decisions.
4. Historical exports/scaffold archives as evidence only.
5. Deleted prior implementation artifacts as design evidence only, never as files to blindly restore.

## Current truth

- ProjectForge is the outer operating system.
- MacroForge is a generated/managed project under ProjectForge at `workspace/projects/macroforge`.
- First implementation source is World Bank WDI.
- Default DB name is `macro` unless a live verification step proves otherwise.
- PostgreSQL is the authoritative analytical store.
- Filesystem stores raw artifacts, checksums, run logs, reports, context, decisions, tasks, and handoffs.
- AI agents are accelerators inside explicit boundaries; they are not authorities for architecture, secrets, deployment, billing, or git push.

## V1 scope

- Recreated scaffold and curated reconstruction artifacts.
- PostgreSQL schema foundation.
- One WDI vertical slice: raw evidence, checksum, staging transform, idempotent load, metadata, lineage, quality checks, and query/report output.
- Tests and run evidence.

## V1 non-goals

- No AI-generated research briefs as the first milestone.
- No many-provider ingestion spree.
- No Airflow/Dagster/Prefect yet.
- No Docker/cloud/public deployment dependency.
- No paid or credentialed API source in v1.
- No raw chat export import into normal context.
- No broad universal framework before real source variation is observed.
