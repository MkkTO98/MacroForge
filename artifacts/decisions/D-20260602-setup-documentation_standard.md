# Decision: Setup - documentation_standard

Date: 2026-06-02
Status: Accepted
Severity: L2
Section: quality

## Question
Documentation standard: minimal, normal, rigorous, or project-specific?

## Answer
Rigorous but concise. Maintain PROJECT_CONTEXT, state, decisions, tasks, runbooks, architecture, glossary, data model, source catalog, and run summaries. Prefer durable artifacts over chat-only explanations.

## Consequence
Agents must consult this artifact before asking the same question again. If status is Deferred and the issue becomes blocking, create a question in `question_queue/pending/`.
