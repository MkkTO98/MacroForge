# Decision: Setup - git_remote

Date: 2026-06-02
Status: Accepted
Severity: L3
Section: governance

## Question
Should git remote/push be configured now or deferred?

## Answer
Defer remote/push configuration during rebuild. Preserve or configure GitHub only after scaffold verification and human approval. Remote push always requires human approval.

## Consequence
Agents must consult this artifact before asking the same question again. If status is Deferred and the issue becomes blocking, create a question in `question_queue/pending/`.
