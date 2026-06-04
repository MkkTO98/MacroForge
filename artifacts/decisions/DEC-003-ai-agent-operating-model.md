# DEC-003 — AI Agent Operating Model

Status: Accepted
Date: 2026-06-02

## Decision

MacroForge uses ProjectForge-native AI-first project operations: local execution for routine implementation/testing/debugging/summarization and cloud governance only for high-leverage architecture, audit, strategy, redesign, consistency review, high ambiguity, repeated local failure, explicit user request, or safety-critical reasoning.

## Agent permissions

Agents may:

- inspect files and curated context;
- create or edit docs/code for accepted tasks;
- run local tests and coherence checks;
- produce run evidence and handoffs.

Agents must pause/escalate for:

- secrets or credentials;
- destructive operations;
- schema/architecture policy changes not covered by decisions;
- production data;
- money/billing;
- deployment/public exposure;
- git push;
- unresolved blocking questions.

## Context rule

Use summaries, state, decisions, tasks, and curated reconstruction docs first. Raw exports/logs are audit or recovery evidence only.
