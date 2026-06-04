# Decision: Setup - specialized_agents

Date: 2026-06-02
Status: Accepted
Severity: L2
Section: operating_model

## Question
Which project-specialized agents seem useful, if any?

## Answer
Useful local roles: operator/context-manager, planner, builder/coder, reviewer, researcher/analyst, data-steward, auditor, incident-responder/ops, teacher/explainer. Specialized agents should be invoked through explicit task contracts and bounded context bundles, not given broad autonomous scope.

## Consequence
Agents must consult this artifact before asking the same question again. If status is Deferred and the issue becomes blocking, create a question in `question_queue/pending/`.
