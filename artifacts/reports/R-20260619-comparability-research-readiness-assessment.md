# MacroForge Comparability and Research-Readiness Assessment

Date: 2026-06-19
Status: completed bounded assessment; no implementation
Scope: MacroForge maturity assessment focused exclusively on comparability and research-readiness for trustworthy InsightForge research.

## Boundaries preserved

This assessment did not implement code, ingest data, modify schemas, create pipelines, create agents, create dashboards, create report-generation systems, create projects, redesign architecture, mutate MacroForge canonical manifests, mutate accepted/base mapping state, write to PostgreSQL, or modify MacroForge source evidence.

Evidence reviewed was limited to current MacroForge state, architecture, decisions, manifests, canonicalization/comparability reports, and actual InsightForge findings/pressure-test results.

Primary MacroForge evidence:

- `CONSTITUTION.md`
- `state/active_goal.md`
- `state/project_state.md`
- `state/architecture.md`
- `context/latest_handoff.md`
- `artifacts/manifests/canonical_assets.json`
- `artifacts/reports/_SUMMARY.md`
- `artifacts/tasks/backlog.md`
- `artifacts/reports/canonicalization-review-lifecycle-20260614.md`
- `artifacts/reports/canonicalization-deferred-mapping-advancement-requirements-20260618.md`
- `artifacts/reports/canonicalization-oecd-unit-basis-comparability-20260618.md`
- `artifacts/reports/canonicalization-oecd-mapping-status-review-20260618.md`
- `artifacts/decisions/DEC-014-first-minimal-research-facing-canonical-output.md`
- `artifacts/decisions/DEC-015-next-scope-canonical-indicator-unit-comparability.md`
- `artifacts/decisions/DEC-018-minimal-ai-assisted-canonicalization-layer.md`
- `artifacts/decisions/DEC-020-architectureharvest-canonical-asset-manifest-registry.md`
- `artifacts/decisions/DEC-021-next-scope-after-deterministic-canonicalization-proposal-workflow.md`

Primary InsightForge evidence:

- `IF-A-20260619-001-wdi-usa-dnk-gdp-direction.md`
- `IF-A-20260619-002-eurostat-deu-fra-quarterly-direction.md`
- `IF-A-20260619-003-oecd-unit-profile-comparison.md`
- `IF-A-20260619-004-cross-source-usa-comparability-boundary.md`
- `R-20260619-analytical-model-pressure-test.md`
- `R-20260619-hypothesis-validation-pressure-test.md`
- `R-20260619-knowledge-accumulation-pressure-test.md`

## Executive assessment

MacroForge is no longer blocked on basic ingestion or canonical storage mechanics. It can load bounded WDI/OECD/Eurostat GDP evidence, preserve lineage, run isolated combined-source validation, produce a deterministic canonical GDP snapshot, and expose enough caveats for InsightForge to produce safe same-source descriptive findings and boundary findings.

MacroForge is not yet research-ready for trustworthy cross-source GDP research. The limiting gap is not data availability. It is comparability eligibility: MacroForge can identify and preserve unit/frequency/source caveats, but it does not yet have a deterministic eligibility surface that tells downstream research which rows are allowed to be compared, excluded, or placed into separate comparability groups.

The smallest real remaining bottleneck is therefore not a new source, dashboard, report system, or broad architecture redesign. It is a deterministic GDP report/research eligibility classification artifact over existing evidence only.

Current research-readiness classification:

- Same-source descriptive research: partially ready.
- Cross-source descriptive comparison: not ready except as a boundary/non-support conclusion.
- Basis-specific OECD comparison: partially prepared but not eligible.
- Eurostat-to-annual/current-USD comparison: not ready.
- InsightForge hypothesis support: weakly ready for methodological/comparability hypotheses inside reports only; not ready for accepted economic hypotheses.

## Phase 1 — Comparability capability inventory

### 1. Current comparability capabilities

Classification: partially implemented.

Implemented capabilities:

- MacroForge preserves source-specific unit/profile evidence in canonical/report artifacts.
- MacroForge records that no unit conversion or frequency aggregation is performed.
- MacroForge distinguishes annual and quarterly periods structurally.
- MacroForge has explicit canonicalization state/proposal mechanics that represent unit/comparability profiles and caveats.
- TASK-040 deterministically split OECD `B1GQ` into `USD_EXC` exchange-rate and `USD_PPP` PPP comparability-basis candidates.
- The OECD mapping-status review keeps `USD_EXC` and `USD_PPP` disjoint and rejects current report eligibility.

Partially implemented or file-backed only:

- Comparability semantics exist in artifacts, reports, and manifest caveats, but are not materialized as a persistent/queryable provider surface.
- WDI current-USD metadata has been enriched for canonicalization evidence, but the older canonical GDP snapshot still exposes WDI `unit_code` as unknown, which InsightForge correctly treated as a comparison blocker.
- OECD basis candidates exist, but no review-approved policy says whether `USD_EXC` is comparable to WDI current-USD evidence or whether `USD_PPP` requires a separate profile/report treatment.
- Eurostat comparability remains blocked by frequency/currency/scale policy absence.

Absent capability:

- No accepted conversion policy.
- No accepted aggregation policy.
- No deterministic downstream eligibility classifier yet.
- No accepted cross-source comparable GDP grouping.

### 2. Current eligibility capabilities

Classification: planned / partially implemented.

Implemented capabilities:

- MacroForge can record lifecycle outcomes: governed provisional for WDI, deferred for OECD and Eurostat.
- MacroForge can record current report eligibility implications in review artifacts.
- Current handoff/state identify the next smallest implementation as deterministic GDP report eligibility classification.

Partially implemented or planned:

- Eligibility semantics are present as prose/JSON review decisions, not yet as a deterministic classifier artifact.
- Existing reports can say OECD is not currently eligible and Eurostat is deferred, but there is no single canonical eligibility table/artifact that InsightForge can cite as the current eligibility contract.

Absent capability:

- No accepted/reviewed deterministic eligibility artifact classifying WDI/OECD USD_EXC/OECD USD_PPP/Eurostat for research use.
- No queryable PostgreSQL eligibility surface.
- No downstream-facing contract that cleanly separates eligible, deferred, excluded, and profile-specific comparable groups.

### 3. Current unit handling capabilities

Classification: partially implemented.

Implemented capabilities:

- Provider unit codes are preserved rather than collapsed.
- OECD `USD_EXC` and `USD_PPP` are distinguished as separate unit/comparability profiles.
- Eurostat `CP_MEUR` is preserved and caveated as current-price million-euro evidence requiring conversion policy before broader comparison.
- WDI unit metadata enrichment exists in bounded canonicalization evidence after TASK-037.

Partially implemented:

- Unit metadata and caveats exist in file-backed canonicalization artifacts but are not fully integrated into the older GDP snapshot interface used by InsightForge.
- Unit profiles can block unsafe mapping advancement, but do not yet produce a compact downstream eligibility status.

Absent capability:

- No unit conversion implementation.
- No currency conversion policy.
- No price-basis/scale conversion policy.
- No accepted measurement model sufficient to compare WDI current USD, OECD exchange-rate USD, OECD PPP USD, and Eurostat current-price million EUR as one research-ready set.

### 4. Current conversion-policy capabilities

Classification: absent by design.

Implemented capability:

- MacroForge explicitly refuses silent unit/currency conversion and quarterly-to-annual aggregation.
- Missing conversion/aggregation policy is preserved as a blocker rather than papered over.

Planned or deferred:

- Future review-approved policy could distinguish OECD exchange-rate USD, OECD PPP USD, WDI current USD, and Eurostat CP_MEUR/quarterly treatment.

Absent capability:

- No accepted conversion policy.
- No conversion engine.
- No frequency aggregation policy.
- No report-impact policy for converted or profile-specific values.

This absence is currently a strength for trust and a limitation for research breadth.

### 5. Current lineage capabilities

Classification: implemented for bounded artifacts; partially implemented for future research workflows.

Implemented capabilities:

- WDI/OECD/Eurostat bounded sources have raw/staging/curated/report evidence and validation artifacts.
- Canonical GDP snapshot records lineage, source metadata, quality checks, missingness, duplicate-grain checks, and bounded observation completeness.
- Canonicalization review lifecycle artifacts record replay inputs, checksums, state deltas, manifest deltas, and lineage edges.
- `canonical_assets.json` links raw/staging/canonical/report/mapping/validation assets to owner/review authority, artifact paths, evidence pointers, statuses, caveats, versions, and supersession fields.

Partially implemented:

- Lineage is file-backed and auditable, but current latest state says canonicalization/review/comparability/eligibility semantics are not materialized into a persistent PostgreSQL provider surface.
- InsightForge can cite exact MacroForge artifacts, but not a single current research-readiness contract.

Absent or deferred:

- No queryable research-eligibility lineage surface.
- No live/current database containing current canonical metadata in this environment.

## Phase 2 — Research-readiness gap analysis

### What prevented stronger InsightForge conclusions?

#### Blocker A — WDI/OECD direct USA GDP level comparison was not justified

Evidence:

- IF-A-004 found WDI and OECD USA rows exist for 2020/2021, but direct comparison is unsupported.
- MacroForge GDP snapshot recorded no unit conversion/frequency aggregation.
- WDI `unit_code` appeared unknown in the snapshot.
- OECD rows separate `USD_EXC` and `USD_PPP` profiles.
- Manifest caveats marked WDI/OECD mappings provisional with direct-comparability caveats.

Cause classification:

- MacroForge: primary. It lacks a deterministic downstream eligibility/comparability contract for cross-source GDP rows.
- InsightForge: secondary but correctly handled. It refused to overclaim and produced a boundary finding.
- Governance: primary/secondary. Conversion and report-eligibility policy is deliberately absent or deferred.
- Missing evidence: primary. No accepted evidence says WDI current-USD rows and OECD `USD_EXC` rows are report-safe comparable.

#### Blocker B — OECD `USD_EXC` and `USD_PPP` could not be collapsed

Evidence:

- IF-A-003 found Australia differs across profiles while USA happens to match across profiles.
- TASK-040 split OECD evidence into exchange-rate and PPP basis candidates.
- OECD mapping-status review concluded both profiles remain deferred and separate.

Cause classification:

- MacroForge: partly solved distinction, but not policy/eligibility.
- InsightForge: correctly preserved the profile boundary.
- Governance: primary. No review-approved exchange-rate-vs-PPP treatment policy exists.
- Missing evidence: primary. Stable interpretation and downstream report-impact decisions are missing.

#### Blocker C — Eurostat could support same-source quarterly direction but not broader comparison

Evidence:

- IF-A-002 safely compared DEU/FRA within Eurostat, same frequency and unit.
- Deferred mapping requirements say Eurostat quarterly current-price million EUR values cannot be treated as comparable to annual/current-USD evidence without conversion and aggregation policy.

Cause classification:

- MacroForge: primary for missing frequency/currency/scale policy.
- InsightForge: correctly limited conclusion to same-source/same-frequency/same-unit direction.
- Governance: primary. No conversion or aggregation policy.
- Missing evidence: primary. No accepted conversion, scale, or quarterly-to-annual treatment.

#### Blocker D — Economic hypotheses could not be accepted

Evidence:

- InsightForge hypothesis pressure test found H1 post-2020 rebound weak/not accepted; H4 USA OECD profile equality explanation not justified.
- Same row-level evidence can support descriptive findings but not causal, explanatory, or investment-relevant claims.

Cause classification:

- MacroForge: secondary. Better comparability would help, but more economic evidence/time-series context would also be needed.
- InsightForge: primary for artifact maturity. Hypotheses remain reserved and unactivated.
- Governance: primary. Hypothesis acceptance policy does not exist and should not be created prematurely.
- Missing evidence: primary. Broader periods, territories, real/nominal treatment, methodology docs, counterevidence, and causal context are absent.

#### Blocker E — Current state is evidence-rich but not compactly downstream-consumable

Evidence:

- MacroForge has multiple review reports and manifest caveats.
- Current latest handoff says eligibility semantics are file-backed and not materialized into persistent PostgreSQL.
- Current active goal says the smallest next step is a deterministic GDP report eligibility classification artifact.

Cause classification:

- MacroForge: primary. The evidence exists but needs a compact deterministic eligibility surface for downstream use.
- InsightForge: secondary. It can cite artifacts but must manually reconstruct the boundary each time.
- Governance: secondary. Current policy intentionally delayed eligibility until semantics were clear.
- Missing evidence: not exactly; this is more missing classification than missing source data.

## Phase 3 — Minimal research-readiness roadmap

Assumptions preserved:

- no new datasets;
- no new sources;
- no dashboards;
- no reporting systems;
- no schema changes unless separately approved later;
- no broad architecture expansion.

### Ranked improvement 1 — Deterministic GDP research/report eligibility classification artifact

Description:

Create a deterministic, reviewed artifact over existing canonical GDP inputs and review artifacts classifying current GDP evidence into eligibility states:

- WDI `NY.GDP.MKTP.CD`: governed provisional candidate, not accepted truth.
- OECD `USD_EXC`: deferred exchange-rate candidate requiring policy/evidence.
- OECD `USD_PPP`: deferred PPP candidate requiring profile/exclusion policy/evidence.
- Eurostat `CP_MEUR` quarterly evidence: deferred on frequency/currency/scale policy.

Expected value: very high.

Why:

- Directly addresses the blocker that stopped InsightForge cross-source conclusions.
- Converts scattered caveats into a single citable downstream contract.
- Improves research usefulness without new sources, conversion, dashboards, or schema change.
- Aligns with current MacroForge active goal and handoff.

Implementation complexity: low to medium.

Dependency risk: low.

Risks:

- Must avoid accidentally approving comparability.
- Must remain classification-only.
- Must not mutate manifests, accepted state, or reports.

### Ranked improvement 2 — Review-approved basis treatment decision for OECD `USD_EXC` and `USD_PPP`

Description:

A bounded review-decision task that decides whether OECD `USD_EXC` can become a governed provisional exchange-rate/current-USD candidate and whether OECD `USD_PPP` should remain excluded from exchange-rate GDP comparisons or become a separate PPP profile candidate.

Expected value: high.

Why:

- OECD profile ambiguity repeatedly blocked InsightForge synthesis.
- TASK-040 already distinguished profiles; the remaining gap is treatment policy.

Implementation complexity: medium.

Dependency risk: medium.

Risks:

- Requires stable unit metadata interpretation and explicit report-impact decision.
- Could overreach if it tries to implement conversion or integrate reports.
- Should probably follow the eligibility classifier, not precede it.

### Ranked improvement 3 — WDI current-USD eligibility reconciliation between enriched canonicalization evidence and GDP snapshot interface

Description:

Make explicit how TASK-037 WDI current-USD metadata enrichment affects downstream research eligibility, while preserving that WDI remains governed provisional and source evidence is not canonical truth.

Expected value: medium-high.

Why:

- InsightForge saw WDI `unit_code` unknown in the GDP snapshot and therefore correctly blocked direct comparison.
- If MacroForge now has WDI current-USD source metadata evidence, the downstream contract needs to reflect what that does and does not permit.

Implementation complexity: low to medium.

Dependency risk: medium.

Risks:

- Could be confused with converting WDI into accepted truth.
- Could tempt report integration before eligibility semantics are explicit.

### Ranked improvement 4 — Eurostat frequency/currency/scale decision: defer, separate, or define minimum future policy

Description:

A bounded governance artifact deciding whether Eurostat quarterly current-price million EUR evidence should remain excluded from current cross-source GDP research, be treated as a separate quarterly/euro profile, or require future conversion/aggregation policy before any research use beyond same-source findings.

Expected value: medium.

Why:

- Eurostat can already support same-source quarterly direction findings.
- Its broader cross-source usefulness remains blocked by three simultaneous policy gaps: frequency, currency, and scale.

Implementation complexity: medium.

Dependency risk: medium-high.

Risks:

- High risk of scope creep into conversion or aggregation.
- Less urgent than WDI/OECD because Eurostat is further from current annual/current-USD comparability.

### Ranked improvement 5 — PostgreSQL persistence of current canonicalization/eligibility metadata

Description:

Persist current canonical concepts, mapping lifecycle status, unit/comparability profiles, eligibility status, caveats, and review-artifact pointers to PostgreSQL after deterministic eligibility semantics are explicit.

Expected value: medium, later.

Why:

- Useful for queryability and future tooling.
- Not needed to answer the immediate research-readiness blocker.

Implementation complexity: medium-high.

Dependency risk: high if done too early.

Risks:

- Premature persistence can fossilize uncertain semantics.
- Current latest handoff explicitly says persistence should follow eligibility semantics, not precede them.

## Phase 4 — Boundary review

### Improvement 1 — GDP research/report eligibility classification artifact

Belongs in: MacroForge.

Reason:

Eligibility of MacroForge evidence for downstream research is a source/canonicalization/comparability contract. InsightForge should cite it, not define it.

Reject from:

- InsightForge, because InsightForge must not become upstream data/comparability authority.
- BriefForge, because this is not briefing/presentation.
- EII, because this is not user-facing intelligence.

### Improvement 2 — OECD basis treatment decision

Belongs in: MacroForge.

Reason:

Exchange-rate-vs-PPP basis treatment is upstream semantic comparability policy. MacroForge owns provider evidence, mapping state, unit profiles, and report eligibility boundaries.

Reject from:

- InsightForge, except as downstream boundary findings or candidate methodological hypotheses.
- BriefForge/EII, because they should consume established semantics rather than decide them.

### Improvement 3 — WDI current-USD eligibility reconciliation

Belongs in: MacroForge.

Reason:

This reconciles source metadata enrichment with canonicalization/research eligibility. It is upstream evidence semantics.

Reject from:

- InsightForge, because InsightForge can observe WDI caveats but must not decide WDI mapping/eligibility truth.

### Improvement 4 — Eurostat frequency/currency/scale treatment

Belongs in: MacroForge.

Reason:

Frequency, currency, and scale comparability are upstream evidence and canonicalization policy.

Reject from:

- InsightForge, except for same-source findings and explicit non-comparability findings.
- BriefForge/EII, because presentation/product layers cannot create conversion/aggregation authority.

### Improvement 5 — PostgreSQL persistence of current eligibility metadata

Belongs in: MacroForge, but only later.

Reason:

If eligibility metadata becomes queryable, it is part of MacroForge's trusted-data substrate. It should not be created by InsightForge, BriefForge, or EII.

Reject for now:

- As an immediate next task. It depends on deterministic eligibility semantics and should not be used to resolve conceptual uncertainty.

## Phase 5 — Recommendation

### 1. Current research-readiness assessment

MacroForge is partially research-ready.

It is ready for:

- bounded same-source descriptive findings;
- lineage-backed evidence citation;
- caveat-aware boundary findings;
- methodological/comparability pressure testing;
- demonstrating that canonical/meta-only outputs can feed InsightForge safely when conclusions stay narrow.

It is not ready for:

- trusted cross-source GDP level comparison;
- accepted economic hypotheses from current GDP evidence;
- exchange-rate-vs-PPP synthesis;
- Eurostat annual/current-USD comparison;
- conversion, aggregation, or broader research outputs.

The strongest maturity signal is that MacroForge correctly blocks unsafe conclusions. The remaining question is whether it can make those blocks compact, deterministic, and downstream-consumable without expanding architecture.

### 2. Top blockers

1. Missing deterministic eligibility classification.
   - Current comparability decisions are distributed across reports, manifest caveats, state files, and InsightForge boundary findings.
   - Downstream research needs one current eligibility contract.

2. OECD basis-policy absence.
   - `USD_EXC` and `USD_PPP` are now distinguished, but no accepted policy determines report/research eligibility.

3. WDI current-USD metadata not cleanly reflected in downstream research interface.
   - TASK-037 improved WDI metadata evidence, but existing InsightForge findings relied on a snapshot where WDI unit was unknown.

4. Eurostat frequency/currency/scale policy absence.
   - Eurostat can support same-source quarterly findings but not cross-source annual/current-USD comparison.

5. File-backed semantics not yet compactly queryable.
   - This is real but should be solved after eligibility semantics are explicit.

### 3. Ranked improvements

1. Deterministic GDP research/report eligibility classification artifact.
   - Value: very high.
   - Complexity: low-medium.
   - Dependency risk: low.

2. OECD basis-specific treatment review.
   - Value: high.
   - Complexity: medium.
   - Dependency risk: medium.

3. WDI current-USD eligibility reconciliation.
   - Value: medium-high.
   - Complexity: low-medium.
   - Dependency risk: medium.

4. Eurostat frequency/currency/scale treatment decision.
   - Value: medium.
   - Complexity: medium.
   - Dependency risk: medium-high.

5. PostgreSQL persistence of eligibility/comparability metadata.
   - Value: medium later.
   - Complexity: medium-high.
   - Dependency risk: high if premature.

### 4. Recommended next MacroForge task

Recommended next implementation task:

`TASK-042 — Create deterministic GDP research/report eligibility classification artifact`

This assessment itself is recorded as `TASK-041` because it is a completed bounded review, not the implementation of the eligibility classifier.

Purpose:

Create a compact, deterministic, reviewable classification over existing MacroForge GDP evidence and existing review artifacts only, so downstream InsightForge research has one current contract for what is eligible, deferred, profile-specific, or blocked.

Scope boundaries:

- Existing canonical GDP inputs only.
- Existing review/canonicalization artifacts only.
- No new sources.
- No new data ingestion.
- No schema changes.
- No conversion.
- No aggregation.
- No report integration.
- No manifest/base-state mutation.
- No PostgreSQL persistence.
- No dashboards or report-generation system.

Expected output:

A file-backed artifact classifying WDI, OECD `USD_EXC`, OECD `USD_PPP`, and Eurostat GDP evidence for current research/report eligibility, with evidence pointers, caveats, forbidden interpretations, and downstream-use notes.

This is smaller and more valuable than building retrieval, dashboards, additional reports, or database persistence.

### 5. Recommended stopping point for MacroForge v1-complete for current EIP needs

MacroForge can reasonably be considered v1-complete for current EIP needs when all of the following are true:

1. Existing WDI/OECD/Eurostat bounded GDP evidence remains reproducible with lineage, quality checks, and canonical snapshot evidence.
2. A deterministic GDP eligibility classification artifact exists and is reviewed.
3. The eligibility artifact makes explicit:
   - WDI governed provisional status and downstream-use limits;
   - OECD `USD_EXC` deferred or provisional treatment conditions;
   - OECD `USD_PPP` deferred/separate-profile treatment;
   - Eurostat frequency/currency/scale deferral;
   - no conversion/no aggregation boundaries;
   - exact evidence pointers and caveats.
4. InsightForge can cite that eligibility artifact to determine whether a proposed finding is same-source descriptive, cross-source eligible, profile-specific, deferred, or unsupported.
5. No additional immediate research blockers remain that can be solved without new data, new policy, conversion/aggregation decisions, or broader product scope.

At that point, MacroForge v1 should stop expanding and let InsightForge continue producing findings within the eligibility contract. Further MacroForge work should resume only when InsightForge produces a concrete, evidence-backed blocker that cannot be handled by current eligibility/caveat surfaces.

## Final judgment

The bottlenecks are real and worth solving, but the smallest worthwhile solution is narrow.

MacroForge does not need a new architecture, source, dashboard, report system, agent, or pipeline. It needs one deterministic research/report eligibility classification layer over the evidence it already has.

Proceed with the eligibility classifier next if MacroForge work continues. Postpone PostgreSQL persistence, conversion policy, aggregation policy, additional sources, and broader research infrastructure until that classifier proves insufficient.
