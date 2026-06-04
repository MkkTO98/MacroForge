# Decision: Setup - logging

Date: 2026-06-02
Status: Accepted
Severity: L2
Section: quality

## Question
Any logging needs beyond ProjectForge's MacroForge-like default?

## Answer
Use ProjectForge default logging plus MacroForge-specific run evidence: raw append-only run logs, derived summaries, actions, command outputs/pointers, checksums, source metadata, validation reports, lineage, decisions, tasks, and handoffs. Raw logs are evidence; summaries/indexes are regeneratable; decisions/tasks/docs are promoted truth.

## Consequence
Agents must consult this artifact before asking the same question again. If status is Deferred and the issue becomes blocking, create a question in `question_queue/pending/`.
