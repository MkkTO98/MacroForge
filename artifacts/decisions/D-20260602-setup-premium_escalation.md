# Decision: Setup - premium_escalation

Date: 2026-06-02
Status: Accepted
Severity: L3
Section: model_routing

## Question
When should Codex/OpenAI be used instead of local models?

## Answer
Use premium/Codex only after local/context-first attempts are insufficient, or for high-impact architecture, security, schema, migrations, and final reviews. Always use bounded context bundles to minimize tokens.

## Consequence
Agents must consult this artifact before asking the same question again. If status is Deferred and the issue becomes blocking, create a question in `question_queue/pending/`.
