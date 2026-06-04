# Handoff — MacroForge Initialization

Date: 2026-06-02
Agent: Hermes
Status: completed

## What changed

- Fresh MacroForge project generated from ProjectForge `python_data_project` template at `/home/mkkto/srv/projectforge/workspace/projects/macroforge`.
- Canonical ProjectForge registry points to `/home/mkkto/srv/projectforge/workspace/projects/macroforge`.
- Curated reconstruction docs created under `context/reconstruction/`.
- Project context, roadmap, architecture docs, data model docs, source catalog, glossary, WDI runbook placeholder, and folder summaries created.
- Durable decisions created:
  - DEC-001 import precedence and reconstruction.
  - DEC-002 v1 WDI/PostgreSQL vertical slice scope.
  - DEC-003 AI agent operating model.
  - DEC-004 v0 PostgreSQL schema foundation.
- Task backlog created with TASK-001 through TASK-008.
- `.gitignore` updated so raw data artifacts, raw exports, zips, `chat.html`, and `conversations.json` are not committed by default.

## Verification output

Generated-project coherence:

```text
{
  "mode": "generated",
  "blocks": [],
  "warnings": []
}
```

Generated-project tests:

```text
.                                                                        [100%]
1 passed in 0.01s
```

ProjectForge root coherence:

```text
{
  "mode": "root",
  "blocks": [],
  "warnings": []
}
```

ProjectForge root tests:

```text
.....................................................                    [100%]
53 passed in 3.39s
```

## Next recommended task

Start TASK-004: recreate v0 PostgreSQL schema foundation using raw SQL migrations and tests. Use database name `macro` by default unless live verification proves otherwise. Do not blindly restore old deleted schema/WDI files.
