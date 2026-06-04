# Decision: Setup - deployment

Date: 2026-06-02
Status: Accepted
Severity: L2
Section: architecture

## Question
Local only, server, web, cloud, mobile, or undecided?

## Answer
Home server/local server first. Use the existing local PostgreSQL service unless explicitly changed later. Docker/cloud/public deployment deferred until the first vertical slice works and has a decision artifact.

## Consequence
Agents must consult this artifact before asking the same question again. If status is Deferred and the issue becomes blocking, create a question in `question_queue/pending/`.
