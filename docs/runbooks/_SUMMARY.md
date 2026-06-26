# Folder Summary: docs/runbooks

## Purpose
Operational runbooks for safe reproducible pipeline execution.

## Contains
<!-- PROJECTFORGE:BEGIN-CONTAINS -->
- `wdi-v1-runbook.md`
<!-- PROJECTFORGE:END-CONTAINS -->

## Active Work
- WDI runbook documents the repaired TASK-044 isolated smoke workflow: unique temporary database, migrations `001` and `003`, double WDI load, validation, report write, and cleanup.

## Needs Attention
- Keep WDI smoke runs isolated; do not use live/default `macro` without explicit approval and fresh dry-run.
