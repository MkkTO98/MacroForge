# Decision: Setup - clarification_channel

Date: 2026-06-02
Status: Accepted
Severity: L2
Section: operating_model

## Question
Where should blocking questions go: local queue only, Telegram later, email later, or other?

## Answer
Local question queue in the project by default. Hermes may ask in the current chat when the user is present. Telegram/email later only if configured by a separate decision.

## Consequence
Agents must consult this artifact before asking the same question again. If status is Deferred and the issue becomes blocking, create a question in `question_queue/pending/`.
