# Decision: Setup - purpose

Date: 2026-06-02
Status: Accepted
Severity: L3
Section: identity

## Question
What is the project's primary purpose?

## Answer
MacroForge is a long-lived AI-first macroeconomic and investing research platform. It starts as a PostgreSQL-backed macroeconomic data warehouse and expands into evidence-backed research workflows for macro, equities, firm-level data, filings, fundamentals, stocks, and investment analysis. It must preserve provenance, lineage, quality checks, run logs, decisions, and agent boundaries so local agents can do most implementation/research work from curated context rather than raw chat history.

## Consequence
Agents must consult this artifact before asking the same question again. If status is Deferred and the issue becomes blocking, create a question in `question_queue/pending/`.
