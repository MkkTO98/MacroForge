# Decision: Setup - available_models

Date: 2026-06-02
Status: Accepted
Severity: L2
Section: model_routing

## Question
Which local models are installed or expected?

## Answer
Local models are preferred when sufficient, but exact installed local models are not assumed. Hermes/Codex/premium models may be used for hard planning, debugging, code review, and generation when local models fail or risk is high.

## Consequence
Agents must consult this artifact before asking the same question again. If status is Deferred and the issue becomes blocking, create a question in `question_queue/pending/`.
