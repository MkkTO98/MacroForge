# Implementation Lessons — TASK-054 Bounded U.S. Treasury Fiscal Data Evidence Slice

Date: 2026-06-28
Status: implemented and verified
Related task: `artifacts/tasks/TASK-054-bounded-us-treasury-fiscal-data-evidence-slice.md`

## What this source taught MacroForge

Treasury Fiscal Data showed that a row-oriented public government JSON API can preserve deterministic query provenance, endpoint metadata, pagination metadata, fiscal record dates, and categorical row identity entirely before the `ObservedIngestionPackage` boundary.

The bounded `avg_interest_rates` slice produced 16 monthly observations from one endpoint/date fixture without requiring generalized acquisition, pagination infrastructure, canonical loading, or substrate changes.

## What this source taught us about previous implementations

TASK-054 strengthened the TASK-053/TASK-051 assumption that materially different source shapes still concentrate implementation effort before the observed boundary.

It also showed that BEA-style table metadata and Treasury-style endpoint metadata are both provider-specific evidence patterns, not reasons to generalize provider metadata infrastructure yet.

## Prediction review

1. Existing substrate components should remain unchanged.
   - Classification: Confirmed.
   - No changes were required to `ObservedIngestionPackage`, fingerprinting/comparison, contract validation, Deterministic Change Verification, Canonical Lineage Event Generation, Deterministic Ingestion Feedback, or existing source implementations.

2. No `ObservedIngestionPackage` contract evolution is expected.
   - Classification: Confirmed.
   - Endpoint identity, query filters, row metadata, record dates, pagination metadata, labels, data types, and categorical row identity fit in existing package fields, raw evidence, input filters, attributes, and source payload.

3. Engineering effort should concentrate in deterministic API query capture, endpoint metadata interpretation, fiscal date/period normalization, and row identity construction.
   - Classification: Confirmed.
   - Most work was source-specific fixture capture, metadata preservation, monthly period interpretation from `record_date`, and indicator-code construction from `security_desc`.

4. New reusable pre-boundary patterns should include API query provenance, endpoint metadata preservation, bounded pagination discipline, and fiscal-date normalization.
   - Classification: Confirmed.
   - These patterns were observed as implementation evidence only; no extraction was justified.

5. No new reusable post-boundary capability is expected.
   - Classification: Confirmed.
   - Existing deterministic substrate checks handled the Treasury package unchanged.

## Unexpected implementation difficulties

None requiring architecture change.

The only notable detail was choosing a monthly endpoint (`avg_interest_rates`) rather than a daily endpoint (`debt_to_penny`) because the current observed contract supports annual, quarterly, and monthly observations. This preserved the no-contract-evolution prediction while still exercising row-oriented API metadata and categorical row identity.

## One durable implementation lesson

Prefer the bounded source slice that exercises the most new pre-boundary provider shape while staying inside the existing observed contract; this maximizes architectural learning per unit of effort and keeps substrate-change claims evidence-based.

## Did this implementation change future source estimation?

No. The previous estimation model remains valid.

Future source estimates should continue to expect Low to Very Low post-boundary substrate effort and concentrate uncertainty estimates on acquisition, provider metadata interpretation, normalization, period/frequency handling, and source-specific row identity construction.
