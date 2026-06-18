# Folder Summary: logs

## Purpose
This folder is part of the ProjectForge file-backed operating system for `logs`.

## Contains
<!-- PROJECTFORGE:BEGIN-CONTAINS -->
- `agents/`
- `derived/`
- `logging_policy.yaml`
- `raw/`
<!-- PROJECTFORGE:END-CONTAINS -->

## Active Work
- Operational logs are optional debugging artifacts only; primary governance continuity lives in task, decision, state, handoff, and report artifacts.

## Needs Attention
- Do not treat empty JSONL operational logs as missing project state. Read logs only for debugging/forensic/failure investigation when governance artifacts are insufficient.
