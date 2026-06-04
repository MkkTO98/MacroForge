# Decision: Setup - unanswered_blocking_policy

Date: 2026-06-02
Status: Accepted
Severity: L3
Section: operating_model

## Question
If a blocking question is unanswered, should the agent pause indefinitely, make conservative fallback, or stop the run?

## Answer
Pause and create a pending question for truly blocking issues. Use conservative fallback only for nonblocking implementation details, recording the assumption in state/decision artifacts.

## Consequence
Agents must consult this artifact before asking the same question again. If status is Deferred and the issue becomes blocking, create a question in `question_queue/pending/`.
