# Decision: Setup - testing

Date: 2026-06-02
Status: Accepted
Severity: L2
Section: quality

## Question
Testing standard for v1?

## Answer
Tests must be run before summarizing code changes. Minimum v1 testing: smoke/coherence tests, unit tests for parsers/mappers/loaders, SQL migration/schema verification, validation queries for data quality, and end-to-end test or dry-run evidence for the first ingestion slice.

## Consequence
Agents must consult this artifact before asking the same question again. If status is Deferred and the issue becomes blocking, create a question in `question_queue/pending/`.
