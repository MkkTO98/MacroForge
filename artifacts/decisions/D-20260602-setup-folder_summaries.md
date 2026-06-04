# Decision: Setup - folder_summaries

Date: 2026-06-02
Status: Accepted
Severity: L2
Section: quality

## Question
Should every core folder maintain a _SUMMARY.md for agent navigation?

## Answer
Yes. Every core folder should maintain _SUMMARY.md for low-token agent navigation and context budgeting.

## Consequence
Agents must consult this artifact before asking the same question again. If status is Deferred and the issue becomes blocking, create a question in `question_queue/pending/`.
