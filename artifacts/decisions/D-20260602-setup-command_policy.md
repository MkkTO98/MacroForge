# Decision: Setup - command_policy

Date: 2026-06-02
Status: Accepted
Severity: L3
Section: governance

## Question
Command permission model: layered default, restrictive allowlist, or project-specific?

## Answer
Layered default with restrictive denylist and escalation. Hermes may use Hermes-native tools for normal reads/edits/tests. Recurring or manual commands should go through project wrappers/dry-run policy. Mutating infra, secrets, production data, deploys, broad deletes, and git push require human approval.

## Consequence
Agents must consult this artifact before asking the same question again. If status is Deferred and the issue becomes blocking, create a question in `question_queue/pending/`.
