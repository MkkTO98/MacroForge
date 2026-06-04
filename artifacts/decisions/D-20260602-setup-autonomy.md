# Decision: Setup - autonomy

Date: 2026-06-02
Status: Accepted
Severity: L3
Section: operating_model

## Question
Agent autonomy: conservative, balanced, aggressive, or project-specific?

## Answer
balanced-to-aggressive local autonomy inside strict project boundaries: agents may inspect files, propose plans, edit docs/code for accepted tasks, run local tests, and produce run evidence. Agents must pause/escalate for secrets, destructive operations, schema/architecture policy changes, production data, billing, deployment, git push, or unresolved blocking questions.

## Consequence
Agents must consult this artifact before asking the same question again. If status is Deferred and the issue becomes blocking, create a question in `question_queue/pending/`.
