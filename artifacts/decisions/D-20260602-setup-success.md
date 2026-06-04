# Decision: Setup - success

Date: 2026-06-02
Status: Accepted
Severity: L3
Section: identity

## Question
What counts as success for v1?

## Answer
V1 succeeds when MacroForge has a ProjectForge-generated project operating system plus one real macro data vertical slice: extract one public dataset, preserve immutable raw evidence and checksum, transform to staging, load idempotently into PostgreSQL canonical tables, record source/release/run/lineage/quality metadata, validate row counts/keys/duplicates/sanity checks, and produce an inspectable query or report output with a reproducible run summary.

## Consequence
Agents must consult this artifact before asking the same question again. If status is Deferred and the issue becomes blocking, create a question in `question_queue/pending/`.
