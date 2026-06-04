# Decision: Setup - model_policy

Date: 2026-06-02
Status: Accepted
Severity: L2
Section: model_routing

## Question
Model policy: smallest sufficient, fastest, highest quality, or project-specific?

## Answer
Smallest sufficient local model by default; escalate by task risk and capability: local small for search/summarize/simple edits, stronger local for planning/refactor/review, premium/Codex only for difficult coding, architecture, debugging, or final review.

## Consequence
Agents must consult this artifact before asking the same question again. If status is Deferred and the issue becomes blocking, create a question in `question_queue/pending/`.
