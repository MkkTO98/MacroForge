# Decision: Setup - branch_strategy

Date: 2026-06-02
Status: Accepted
Severity: L2
Section: governance

## Question
Branch strategy: single branch, feature branches, agent branches, or defer until needed?

## Answer
Agent branches or feature branches for implementation work; main stays stable. Exact remote workflow deferred until git remote/push policy is reviewed after rebuild.

## Consequence
Agents must consult this artifact before asking the same question again. If status is Deferred and the issue becomes blocking, create a question in `question_queue/pending/`.
