# TASK-042 — Deterministic GDP research/report eligibility classification artifact

Status: complete
Date: 2026-06-19

## Purpose

Create a compact downstream-consumable eligibility surface for existing MacroForge GDP evidence.

The task resolves the specific blocker identified by TASK-041: downstream consumers lacked one deterministic artifact that states whether current GDP evidence is eligible, profile-specific, deferred, unsupported, or blocked for research/report use.

## Scope

Included:

- existing WDI GDP evidence;
- existing OECD GDP evidence split into `USD_EXC` and `USD_PPP` profiles;
- existing Eurostat quarterly GDP evidence;
- existing MacroForge review, lineage, quality, mapping, and comparability artifacts;
- relevant InsightForge findings that pressure-tested those boundaries.

Excluded:

- new data ingestion;
- new sources;
- conversion policy;
- aggregation policy;
- reporting frameworks;
- dashboards;
- pipelines;
- agents;
- PostgreSQL writes;
- canonical GDP evidence modification;
- accepted manifest mutation;
- canonical observation mutation;
- non-GDP scope.

## Deliverables

1. Eligibility-classification design:
   - embedded in `artifacts/reports/gdp-eligibility-classification-20260619.json` under `classification_model`;
   - summarized in `artifacts/reports/R-20260619-gdp-eligibility-classification-validation.md`.

2. Eligibility-classification artifact:
   - `artifacts/reports/gdp-eligibility-classification-20260619.json`.

3. Validation report:
   - `artifacts/reports/R-20260619-gdp-eligibility-classification-validation.md`.

4. Updated research-readiness assessment:
   - included in the validation report under Phase 5.

5. Recommendation on v1 stopping point:
   - MacroForge has reached a reasonable v1 stopping point for current EIP needs after this artifact, unless a downstream consumer produces a concrete blocker.

## Classification result

| Evidence | Current compact status |
| --- | --- |
| WDI `NY.GDP.MKTP.CD` annual evidence | Eligible for bounded WDI-only descriptive findings; governed provisional; not accepted truth; cross-source comparison unsupported; comparable report integration deferred. |
| OECD `B1GQ` `USD_EXC` annual evidence | Deferred for broader use; eligible only for OECD-only profile-preserving descriptive findings; exchange-rate profile must remain separate; not report-eligible today. |
| OECD `B1GQ` `USD_PPP` annual evidence | Deferred for broader use; eligible only for OECD-only profile-preserving descriptive findings; PPP profile must remain separate; not report-eligible today and unsupported for exchange-rate/current-USD outputs. |
| Eurostat `B1GQ` quarterly `CP_MEUR` evidence | Deferred for broader use; eligible only for Eurostat-only same-frequency/same-unit descriptive findings; cross-source annual/current-USD comparison blocked by missing frequency/currency/scale policy. |

## Validation performed

Validation checked that:

- the JSON artifact parses;
- exactly four classifications exist;
- WDI, OECD `USD_EXC`, OECD `USD_PPP`, and Eurostat `CP_MEUR` classifications are present;
- every classification has evidence pointers;
- no classification approves cross-source comparable GDP use;
- no classification approves conversion;
- no classification approves aggregation;
- downstream questions can be answered from the artifact without re-reading all underlying reports.

## Final judgment

TASK-042 solves the immediate blocker from TASK-041: current GDP eligibility is now compact, deterministic, file-backed, auditable, and downstream-consumable.

It intentionally does not resolve comparability. It makes the current comparability status explicit.

MacroForge should stop expanding at v1 unless InsightForge or another downstream consumer creates a concrete evidence-backed blocker that the current eligibility artifact cannot answer.
