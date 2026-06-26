# GDP Research/Report Eligibility Classification Validation

Date: 2026-06-19
Status: completed
Task: TASK-042
Primary artifact: `artifacts/reports/gdp-eligibility-classification-20260619.json`
Scope: deterministic eligibility classification over existing MacroForge GDP evidence only.

## Boundaries preserved

This task did not ingest new data, add sources, create conversion policy, create aggregation policy, create a reporting framework, create dashboards, create pipelines, create agents, write to PostgreSQL, modify canonical GDP evidence, mutate accepted manifests, mutate canonical observations, or broaden beyond GDP.

The task created a file-backed downstream-consumable classification artifact and this validation report only.

## Phase 1 — Existing evidence summary

### WDI

Supported conclusions:

- WDI `NY.GDP.MKTP.CD` rows exist for DNK and USA in 2020 and 2021 in the canonical GDP snapshot.
- Same-source annual WDI direction-of-change findings are supported for those bounded rows.
- TASK-037 reduced the WDI unknown-unit-metadata blocker by representing current-USD source metadata evidence.
- TASK-038 moved WDI to a governed provisional outcome.

Where evidence stops:

- WDI source metadata is not canonical truth.
- The older GDP snapshot still exposes WDI `unit_code` as `unknown`.
- WDI is not accepted as directly comparable with OECD or Eurostat GDP rows.

Assumptions that would be required for stronger use:

- that WDI current-USD metadata is sufficient for direct exchange-rate-current-USD comparability;
- that WDI can be treated as accepted truth rather than governed provisional evidence;
- that downstream report integration can safely reconcile enriched metadata with the older GDP snapshot interface.

### OECD

Supported conclusions:

- OECD `B1GQ` annual rows exist for AUS and USA in 2020 and 2021.
- OECD rows contain separate `USD_EXC` and `USD_PPP` profiles.
- TASK-040 deterministically split OECD unit-basis evidence into exchange-rate and PPP basis candidates.
- The OECD mapping-status review concludes both profiles remain deferred today.
- Same-source/profile-preserving descriptive findings are supported, including the boundary that USD_EXC and USD_PPP must remain separate.

Where evidence stops:

- No review-approved policy says `USD_EXC` can be compared with WDI current-USD evidence.
- No review-approved policy says `USD_PPP` should enter a PPP-specific report profile or be excluded permanently.
- Identical USA values across `USD_EXC` and `USD_PPP` are observed row values, not a general comparability rule.

Assumptions that would be required for stronger use:

- that OECD `USD_EXC` is report-safe comparable with WDI current-USD evidence;
- that `USD_PPP` can be mixed with exchange-rate/current-USD evidence;
- that profile treatment can be decided without a review-approved basis policy.

### Eurostat

Supported conclusions:

- Eurostat `B1GQ` quarterly `CP_MEUR` rows exist for DEU and FRA in 2023 Q1 and Q2.
- Same-source, same-frequency, same-unit quarterly direction-of-change findings are supported for existing rows.
- TASK-038 and TASK-039 defer Eurostat broader mapping/report advancement because frequency, currency, and scale policy is absent.

Where evidence stops:

- Eurostat quarterly current-price million-euro values cannot be annualized or compared to USD evidence under current policy.
- No conversion, aggregation, or scale policy exists.

Assumptions that would be required for stronger use:

- that quarterly values may be aggregated to annual values;
- that EUR values may be converted to USD values;
- that million-EUR current-price scale/basis can be safely mixed with WDI/OECD evidence.

### InsightForge pressure-test evidence

InsightForge validated that MacroForge can support bounded findings:

- WDI-only annual direction finding.
- Eurostat-only quarterly direction finding.
- OECD same-source/profile-boundary finding.
- Cross-source WDI/OECD USA comparability boundary finding.

It also confirmed the blocker this task solves: downstream consumers should not need to reconstruct eligibility from multiple MacroForge reports and caveats.

## Phase 2 — Eligibility classification model

The smallest justified classification model uses five categories:

### `eligible`

Meaning: existing evidence may be used for the explicitly stated bounded use without additional upstream semantic policy.

Permitted use: same-source, same-frequency, same-unit/profile descriptive findings over existing bounded rows, with lineage and caveats cited.

Prohibited use: accepted truth claims, causal claims, investment signals, forecasting, cross-source level comparison, conversion, aggregation, or comparable-GDP report approval.

### `profile_specific`

Meaning: evidence may be used only inside an explicit unit/frequency/source profile; the profile boundary is part of the conclusion.

Permitted use: descriptive findings that preserve the profile boundary.

Prohibited use: mixing profiles, treating profile equality in one territory as interchangeability, or placing profile-specific rows into a common comparable GDP group.

### `deferred`

Meaning: GDP-like evidence exists, but current MacroForge review artifacts require additional policy/evidence before the proposed broader research/report use is allowed.

Permitted use: cite the deferral, produce boundary findings, and use rows only for narrower eligible/profile-specific descriptive uses.

Prohibited use: mapping/report advancement, report integration, comparable GDP outputs, or accepted conclusions without later review-approved policy.

### `unsupported`

Meaning: current evidence does not support the proposed conclusion even though relevant rows may exist.

Permitted use: a boundary finding stating that the conclusion is unsupported.

Prohibited use: treating row existence, matching values, or provider labels as proof of comparability.

### `blocked`

Meaning: an explicit missing policy or semantic blocker prevents a proposed use until resolved.

Permitted use: cite the blocker and stop the proposed use.

Prohibited use: silent conversion, aggregation, confidence-score workarounds, manual interpretation, or downstream assumptions.

## Phase 3 — Implemented eligibility artifact

Created:

- `artifacts/reports/gdp-eligibility-classification-20260619.json`

The artifact is:

- file-backed;
- auditable;
- reproducible;
- lineage-aware;
- downstream-consumable.

It classifies four GDP evidence surfaces:

| Evidence | Primary category | Same-source descriptive use | Profile-specific | Cross-source comparable use | Comparable report integration |
| --- | --- | --- | --- | --- | --- |
| WDI `NY.GDP.MKTP.CD` annual current-USD metadata evidence | `eligible` | eligible | false | unsupported | deferred |
| OECD `B1GQ` `USD_EXC` annual exchange-rate USD candidate | `deferred` | eligible when profile preserved | true | deferred | deferred/not eligible today |
| OECD `B1GQ` `USD_PPP` annual PPP USD candidate | `deferred` | eligible when profile preserved | true | deferred/unsupported for exchange-rate outputs | deferred/not eligible today |
| Eurostat `B1GQ` quarterly `CP_MEUR` evidence | `deferred` | eligible when same-frequency/same-unit preserved | true | blocked by frequency/currency/scale policy absence | deferred/not eligible today |

This deliberately does not make WDI, OECD, and Eurostat comparable. It records current status only.

## Phase 4 — Validation

A downstream consumer can answer the required questions from the JSON artifact without re-reading all underlying reports.

### Question: Is this evidence currently eligible for descriptive findings?

Answer rule from artifact:

- allowed only when `same_source_descriptive_use` starts with `eligible` and the finding preserves source/frequency/unit/profile scope.

Result:

- WDI: yes, WDI-only annual descriptive findings.
- OECD `USD_EXC`: yes, OECD-only profile-preserving findings.
- OECD `USD_PPP`: yes, OECD-only profile-preserving findings.
- Eurostat `CP_MEUR`: yes, Eurostat-only same-frequency/same-unit quarterly findings.

### Question: Is this evidence profile-specific?

Result:

- WDI: no, but still governed provisional and not cross-source approved.
- OECD `USD_EXC`: yes.
- OECD `USD_PPP`: yes.
- Eurostat `CP_MEUR`: yes.

### Question: Is this evidence deferred?

Result:

- WDI: not deferred for bounded same-source descriptive findings; comparable report integration is deferred.
- OECD `USD_EXC`: deferred for broader cross-source/report use.
- OECD `USD_PPP`: deferred for broader cross-source/report use and unsupported for exchange-rate/current-USD outputs.
- Eurostat `CP_MEUR`: deferred for broader cross-source/report use.

### Question: Is this evidence blocked?

Result:

- Direct cross-source WDI/OECD comparison: unsupported under current contract.
- Eurostat-to-annual/current-USD comparison: blocked by missing frequency/currency/scale policy.
- Any conversion or aggregation use: blocked by explicit policy absence.

### Determinism and reproducibility validation

Validation checks performed on the artifact:

- JSON parses successfully.
- Exactly four classifications exist.
- Required classification IDs are present.
- Each classification includes evidence pointers.
- No classification approves cross-source comparable GDP use.
- No classification approves conversion or aggregation.
- WDI, OECD `USD_EXC`, OECD `USD_PPP`, and Eurostat `CP_MEUR` are all represented.

## Phase 5 — Research-readiness reassessment

### 1. Remaining blockers

Remaining blockers after TASK-042:

1. OECD exchange-rate-vs-PPP treatment policy remains unresolved.
2. WDI current-USD metadata still needs downstream/report-interface reconciliation before cross-source use.
3. Eurostat frequency/currency/scale policy remains absent.
4. No accepted conversion or aggregation policy exists.
5. Eligibility is file-backed, not PostgreSQL-queryable, by design.

### 2. Are those blockers inside current MacroForge scope?

Inside current MacroForge scope only if downstream work produces a concrete blocker:

- OECD basis-treatment review.
- WDI current-USD downstream/report-interface reconciliation.
- Eurostat frequency/currency/scale treatment decision.

Outside current scope or explicitly not current v1 work:

- conversion implementation;
- aggregation implementation;
- dashboards;
- report-generation frameworks;
- agents;
- new sources;
- PostgreSQL persistence of eligibility metadata.

### 3. Can MacroForge be considered v1-complete for current EIP needs?

Yes, with one caveat: the artifact should be treated as the current file-backed eligibility contract and cited by InsightForge before MacroForge expands further.

MacroForge now has:

1. reproducible bounded WDI/OECD/Eurostat GDP evidence;
2. lineage and quality checks;
3. a canonical GDP snapshot;
4. review lifecycle evidence;
5. deferred mapping requirements;
6. OECD basis split evidence;
7. research-readiness assessment;
8. a compact deterministic GDP eligibility classification artifact.

That satisfies the v1 stopping criteria identified in TASK-041 for current EIP needs.

### 4. Next task if work continues

If work continues, the next task should not be implementation by default.

Smallest legitimate next task:

- a bounded OECD basis-treatment review only if InsightForge needs to go beyond boundary/profile-specific findings.

It should decide whether `USD_EXC` can become a governed provisional exchange-rate/current-USD candidate and whether `USD_PPP` needs a separate PPP profile or explicit exclusion.

### 5. Would continued work solve a blocker or expand scope?

Without a concrete downstream blocker, continued MacroForge work would mostly expand scope rather than solve the identified immediate blocker.

The blocker from TASK-041 was compact deterministic eligibility classification. TASK-042 solves that blocker without resolving comparability itself.

## Final recommendation

MacroForge has reached a reasonable v1 stopping point for current EIP needs.

Stop expanding MacroForge now unless InsightForge or another downstream consumer produces a concrete, evidence-backed blocker that cannot be handled by the new eligibility artifact.

Do not proceed to conversion, aggregation, PostgreSQL eligibility persistence, reporting frameworks, dashboards, agents, or new sources as speculative next steps.
