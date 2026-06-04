# Decision: Setup - storage

Date: 2026-06-02
Status: Accepted
Severity: L3
Section: architecture

## Question
Does the project need persistent storage? If yes, which kind?

## Answer
Yes. PostgreSQL is the authoritative analytical store. Filesystem stores immutable raw source artifacts, checksums, run logs, reports, curated context, decisions, tasks, and handoffs. Git stores code/docs/config/templates but not secrets, raw large datasets, database dumps, or private exports.

## Consequence
Agents must consult this artifact before asking the same question again. If status is Deferred and the issue becomes blocking, create a question in `question_queue/pending/`.
