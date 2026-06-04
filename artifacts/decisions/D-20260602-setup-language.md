# Decision: Setup - language

Date: 2026-06-02
Status: Accepted
Severity: L2
Section: architecture

## Question
Primary programming language or runtime?

## Answer
Python 3.12+ for ingestion, validation, CLI/tools, and agent-operable workflows; SQL/PostgreSQL for schema, constraints, views, and queryable storage; Markdown/YAML/JSON/JSONL for project operating artifacts.

## Consequence
Agents must consult this artifact before asking the same question again. If status is Deferred and the issue becomes blocking, create a question in `question_queue/pending/`.
