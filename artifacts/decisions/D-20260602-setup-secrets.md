# Decision: Setup - secrets

Date: 2026-06-02
Status: Accepted
Severity: L4
Section: governance

## Question
Will the project handle secrets/API keys/credentials? If yes, specify where they should live.

## Answer
Yes eventually, but v1 starts with no required secrets. Secrets/API keys/credentials must live outside git in environment files, OS secret store, or service-specific config with strict permissions. Agents receive only role-required secrets and never raw secret dumps. No paid/credentialed sources until explicit decision.

## Consequence
Agents must consult this artifact before asking the same question again. If status is Deferred and the issue becomes blocking, create a question in `question_queue/pending/`.
