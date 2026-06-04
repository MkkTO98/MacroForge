# Decision: Setup - external_services

Date: 2026-06-02
Status: Accepted
Severity: L3
Section: architecture

## Question
Will the project depend on external APIs, cloud services, databases, or paid services?

## Answer
Public no-key data sources first: World Bank WDI or UN WPP/UNPD. Later possible sources include OECD, IMF, Eurostat, FRED, SEC/filings/fundamentals/equities. No paid services or credentialed APIs in v1 without explicit decision and secrets policy.

## Consequence
Agents must consult this artifact before asking the same question again. If status is Deferred and the issue becomes blocking, create a question in `question_queue/pending/`.
