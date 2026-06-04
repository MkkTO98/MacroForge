# Decision: Setup - non_goals

Date: 2026-06-02
Status: Accepted
Severity: L2
Section: identity

## Question
What should this project explicitly not try to do in v1?

## Answer
Do not make AI-generated research briefs the first milestone; prove the data loop first. Do not build many pipelines before grain/schema/idempotency/logging/validation are stable. Do not add Airflow/Dagster/Prefect before several manual/local pipelines exist. Do not give agents raw shell, secrets, production, deployment, or billing authority. Do not treat raw ChatGPT exports as canonical truth. Do not overbuild a universal framework before real source variation is observed.

## Consequence
Agents must consult this artifact before asking the same question again. If status is Deferred and the issue becomes blocking, create a question in `question_queue/pending/`.
