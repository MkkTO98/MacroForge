# Confidence Escalation Framework for Repository Expansion

Status: accepted architectural orchestration policy
Date: 2026-07-08
Related task: `artifacts/tasks/TASK-163-confidence-escalation-framework.md`
Related decision: `artifacts/decisions/D-20260708-confidence-escalation-framework.md`

## Purpose

The Confidence Escalation Framework (CEF) governs how MacroForge chooses the largest ingestion scope that can now be executed with acceptable confidence based on accumulated evidence.

CEF does not replace existing workstreams. It sits above them as planning and orchestration policy:

```text
Architecture / decisions remain authoritative
        -> CEF evaluates evidence and selects safe ingestion scope
        -> existing workstreams execute bounded implementations
        -> tests, reports, ledgers, and task closeout update evidence
        -> CEF scope is promoted, held, or locally regressed
```

CEF exists to increase repository-expansion throughput without weakening MacroForge's evidence-first architecture.

## Architectural investigation result

### Does CEF belong in MacroForge?

Yes, but only as an orchestration policy and lightweight governance artifact.

Evidence:

- `CONSTITUTION.md` makes uncertainty reduction an explicit objective and requires evidence-gated evolution.
- `DEC-022` says implementation is the source of architectural truth and future source work should reduce future engineering, human, or LLM effort.
- `D-20260703-operational-repository-v1-accepted-evolution.md` makes Operational Repository Evolution MacroForge's primary activity and requires repository-section contribution for each implementation.
- `docs/architecture/capability-maturity-model.md` already treats capabilities as planning units and records `Evidence-Accumulating Source Expansion`.
- `docs/architecture/architectural-confidence-ledger.md`, `architectural-surprise-log.md`, `marginal-source-cost-index.md`, and `recurring-implementation-pain.md` already collect the evidence needed to decide when scope should expand or contract.
- Repeated operational tasks through TASK-162 show that sequential bounded ingestion is now often cheap, but architecture still rejects provider mirrors, generic frameworks, and production/live behavior without evidence.

Therefore CEF is justified because it reduces recurring planning effort and makes scope escalation explicit. It is not justified as a new runtime framework, provider framework, source registry, scheduler, scoring engine, or replacement for architecture governance.

### Where should it live?

CEF lives in `docs/architecture/confidence-escalation-framework.md` because it is architecture-governed methodology. State files may summarize the current posture, and task artifacts should apply the framework when selecting future ingestion scope.

CEF should also be referenced from:

- `state/architecture.md` as current architecture posture;
- `docs/architecture/overview.md` as orchestration policy;
- `docs/architecture/capability-maturity-model.md` as a planning capability;
- `artifacts/decisions/` as an accepted durable decision.

### Constitutional, operational, or implementation guidance?

CEF should not be constitutional now. The Constitution already contains sufficient principles: evidence-first evolution, source-specific-first boundaries, no premature generalization, deterministic validation, and lightweight maturity tracking.

CEF is:

1. architectural capability: it formalizes evidence-based escalation and localized regression;
2. operational methodology: it guides future task selection and scope sizing;
3. orchestration policy: it determines when to move from isolated slices to batches, families, provider areas, or continuous production-like operation;
4. repository governance artifact: it records how repository expansion becomes increasingly throughput-oriented.

CEF is not implementation code until a future task proves that deterministic support would reduce recurring planning effort.

## Deepest supported abstraction

CEF is not indicator-specific.

The deepest currently supported abstraction is the **ingestion confidence cell**:

```text
provider or source family
+ acquisition / parser family
+ dataset family or dataflow
+ observation representation class
+ operational scope
+ canonicalization / loading authority, if any
```

A confidence cell is intentionally compositional. It can describe:

- a provider capability, such as WDI annual country-indicator panels;
- a parser family, such as SDMX StructureSpecificData under IMF dataflows;
- a dataset family, such as BLS labor-core monthly national data;
- an observation representation class, such as scalar annual country-period observations, matrix cells, revision-vintage observations, issuer financial-statement facts, or bilateral trade flows;
- an operational scope, such as bounded fixture evidence, G7 panel, full non-aggregate WDI country panel, PostgreSQL-loaded operational dataset, or continuous refresh candidate.

This is deeper than `indicator` because repeated evidence shows MacroForge's real uncertainty often lives at provider semantics, parser shape, frequency, observation representation, mapping, and operational scope boundaries rather than at single economic indicators.

## Confidence dimensions

CEF rejects a single confidence score. Confidence is multidimensional and evidence-specific.

### 1. Architectural confidence

Question: does the current architecture represent this scope without changing core contracts or adding forbidden abstractions?

Evidence:

- `ObservedIngestionPackage` fit;
- no post-boundary source-specific conditionals;
- no contract evolution pressure;
- no Mandatory Decision Gate triggered;
- architectural confidence ledger and surprise log outcomes.

### 2. Provider / source confidence

Question: is the provider/source behavior sufficiently understood for the proposed scope?

Evidence:

- stable source identity, endpoint, license/no-key posture, metadata, and response shape;
- raw evidence checksums and deterministic fixture reconstruction;
- known access limitations, pagination, missing values, revisions, frequency, and provider-specific semantics.

### 3. Parser / acquisition confidence

Question: can MacroForge acquire and parse the payload deterministically across the proposed scope?

Evidence:

- parser tests across diverse rows, periods, territories, or payload structures;
- fixtures covering empty, sparse, missing, status-coded, large, or structurally unusual records;
- repeated parser reuse without provider conditionals leaking into shared infrastructure.

### 4. Representation confidence

Question: can the normalized observations preserve all relevant source evidence without lossy encoding?

Evidence:

- observation grain stated and tested;
- source attributes preserved;
- frequency, period, unit, territory, vintage, matrix, bilateral, or issuer semantics represented without schema distortion;
- contract validation passes.

### 5. Validation confidence

Question: are checks strong enough to catch incorrect ingestion for this scope?

Evidence:

- raw checksum, row count, uniqueness, required field, fingerprint, package equivalence, delta, quality, load, and report checks;
- explicit failure modes and deterministic diagnostics.

### 6. Operational confidence

Question: can the ingestion be rerun, refreshed, loaded, compared, and handed off at the proposed scope without unusual manual intervention?

Evidence:

- refresh manifests, delta reports, load reports, deterministic replay, isolated PostgreSQL evidence where scoped;
- task closeout and handoff quality;
- marginal source cost and recurring pain trends.

### 7. Mapping / canonicalization confidence

Question: are canonical mappings or loaded analytical identities justified for the proposed scope?

Evidence:

- accepted canonical path or source-specific operational load;
- mapping review artifacts;
- no unresolved semantic identity boundary;
- no deferred canonical identity gate.

If a scope is evidence-only, mapping/canonicalization confidence may be explicitly low or out of scope while architectural, provider, parser, representation, validation, and operational confidence may still be high enough for bounded ingestion.

## Escalation stages

CEF escalation is stage-based but not count-based. Promotion requires explicit evidence across relevant confidence dimensions.

### Stage 0 — Source-path discovery

Use when source path, payload shape, license/no-key status, or scope feasibility is uncertain.

Allowed work:

- source discovery;
- compact fixture probing;
- candidate comparison;
- no durable architecture changes.

Promotion evidence:

- exact source path known;
- bounded fixture obtainable;
- likely observation grain identified;
- no immediate policy block.

### Stage 1 — Isolated bounded evidence slice

Use when architectural learning is high and confidence is low/moderate.

Allowed work:

- one small provider/dataset/representation slice;
- deterministic fixture, normalizer, observed package, and tests;
- no broad loader, no provider framework, no source family abstraction.

Promotion evidence:

- contract validation passes;
- package fingerprint/replay is deterministic;
- representation preserves source semantics;
- no material architecture surprise or the surprise is documented and bounded.

### Stage 2 — Stratified evidence sample

Use when a single slice passed but uncertainty remains about heterogeneity within the same confidence cell.

Allowed work:

- deliberately diverse sample selected to stress known variation;
- examples may include annual/quarterly/monthly frequency, dense/sparse series, different units, index/percent/currency values, country/territory breadth, missing values, status-coded observations, unusual metadata structures, large series, and edge-case identifiers.

Promotion evidence:

- representative stress cases pass;
- failures are understood and localized;
- validation catches expected defects;
- no hidden schema or parser pressure appears.

### Stage 3 — Small representative operational batch

Use when stratified evidence supports more throughput but full family ingestion may still be premature.

Allowed work:

- small batch over a provider/dataset family or repository section;
- deterministic normalized artifact, refresh manifest, delta report, and load/report validation where scoped.

Promotion evidence:

- refresh/load/replay checks pass;
- cost and pain remain low or understood;
- failures do not expose broader architectural uncertainty;
- repository-section contribution is clear.

### Stage 4 — Thematic or dataset-family operational ingestion

Use when provider/parser/representation/validation confidence is high for a dataset family.

Allowed work:

- broader family ingestion such as labor core, trade core, financial accounts core, G7 position panel, or selected official release family;
- still source-specific unless extraction gates are independently satisfied.

Promotion evidence:

- multiple representative slices/batches passed;
- validation is sufficient for the family;
- operational refresh behavior is deterministic;
- maturity evidence supports repository usefulness.

### Stage 5 — Provider-capability expansion

Use only when a provider capability, not merely a dataset, is well understood.

Allowed work:

- provider-level expansion inside proved acquisition/parser/representation boundaries;
- provider-local helpers only if they satisfy extraction doctrine or remain explicitly source-local.

Promotion evidence:

- repeated dataset-family evidence within provider;
- stable provider semantics;
- no recurring source-specific surprises;
- measured planning/implementation cost reduction.

### Stage 6 — Continuous production ingestion candidate

Use only after explicit acceptance. This stage is not currently authorized by existing MacroForge decisions.

Allowed work requires a future decision covering:

- live/default writes;
- scheduling;
- production data authority;
- monitoring/alerting;
- rollback/recovery;
- maintenance ownership;
- cost/secrets/billing posture if relevant.

Promotion evidence:

- stable operational refresh;
- regression protection;
- accepted production/live authority;
- human approval where required.

## Promotion rule

Promotion requires a written `Confidence Escalation Assessment` in the task artifact or report answering:

1. Current confidence cell.
2. Current stage.
3. Proposed next stage/scope.
4. Evidence supporting each relevant confidence dimension.
5. Known counterevidence or unresolved uncertainty.
6. Why the proposed scope is the largest acceptable scope now.
7. What evidence would force localized regression.

Promotion must never be based solely on a fixed number of successful ingestions.

## Regression methodology

Failures regress only the smallest confidence cell justified by evidence.

Regression scope should be selected in this order:

1. observation or fixture row;
2. specific indicator/series/concept;
3. dataset member or table;
4. dataset/dataflow family;
5. parser/acquisition family;
6. provider/source family;
7. observation representation class;
8. post-boundary substrate;
9. architecture-wide confidence.

Do not regress unrelated sections merely because one local failure occurred.

Examples:

- A bad Energy dataset fixture normally regresses that Energy dataset family or parser case, not GDP, inflation, labor, or trade.
- A daily-frequency FX failure regresses daily market-data/frequency support, not monthly FX evidence or all FRED ingestion.
- A contract-validation bug in shared post-boundary code may regress validation confidence across all affected users of that contract.
- A canonical identity failure in Companies does not automatically regress evidence-only WDI country-year panels.

A failure may widen regression only if evidence shows shared cause: common parser algorithm, shared post-boundary invariant, shared loader SQL, shared canonical mapping, or common provider behavior.

## Stratified evidence methodology

Representative sampling is often stronger than sequential convenience testing because it maximizes architectural evidence per implementation effort.

A stratified sample should deliberately cover the variation that could falsify the confidence cell. Candidate strata include:

- frequency: annual, quarterly, monthly, daily where authorized;
- value type: level, index, percent, currency, ratio, count, stock, flow;
- density: dense series, sparse series, missing-heavy series;
- geography: single-country, multi-country, subnational, bilateral reporter/partner;
- dimensionality: scalar, curve, matrix, issuer fact, bilateral trade, revision vintage;
- metadata: ordinary labels, multilingual labels, large codelists, status flags, confidentiality flags;
- period behavior: revisions, vintage/as-of dates, release calendars, non-calendar fiscal periods;
- size: tiny fixture, moderate batch, large operational panel;
- validation risk: duplicate grain, missing unit, unexpected unit, empty response, partial response.

The sample should be recorded before implementation so success cannot be cherry-picked after the fact.

## Operational integration

After TASK-167, CEF operates underneath the Domain-Centric Repository Development Framework (DRDF). DRDF governs the domain objective and maturity gap; CEF governs the largest safe ingestion scope inside that objective.

Future Workstream A planning should use CEF as follows:

1. Identify the target macroeconomic domain and domain maturity gap using `docs/architecture/domain-centric-repository-development-framework.md`.
2. Translate the gap into one or more candidate confidence cells.
3. Read the smallest relevant evidence: state, latest handoff, task artifacts, decisions, capability atlas, domain coverage, confidence ledger, surprise log, cost index, pain log, and relevant tests.
4. Determine current stage and confidence dimensions for the candidate cell.
5. Choose the largest safe next scope.
6. Execute through existing workstreams.
7. Update evidence artifacts and record whether scope should promote, hold, or locally regress.
8. Update affected domain maturity evidence.

CEF assists scope planning; it does not grant authority to skip tests, closeout, decisions, domain objective selection, or architecture gates.

## Repository expansion strategy

CEF changes the default shape of expansion as confidence grows:

- low confidence: maximize learning through small, diverse, falsification-oriented slices;
- moderate confidence: use stratified samples and small operational batches;
- high confidence: increase throughput inside validated families and repository sections;
- very high confidence: consider provider-capability expansion only with explicit evidence;
- production/live: remain blocked until separately authorized.

This preserves evidence-first philosophy because throughput is earned by evidence. Architecture still evolves only when failures, repeated pain, or extraction gates justify it.

## Interaction with existing workstreams

- Architecture workstream: CEF records when evidence is enough for larger scope, but architecture remains authoritative.
- Ingestion workstream: CEF sizes the next ingestion task; ingestion remains source-specific unless extraction is justified.
- Validation workstream: CEF requires validation confidence before scope expansion.
- Operational Repository Evolution: CEF selects between bounded slice, stratified sample, operational batch, or family ingestion.
- Maturity tracking: CEF complements capability and repository-section maturity; it does not replace those labels.
- Pipeline validation: CEF uses pipeline validation evidence as one confidence dimension.
- Future providers: CEF is provider-agnostic; new providers start at Stage 0 or Stage 1 unless existing evidence proves the same confidence cell applies.

## Latest operational application evidence

TASK-165 applied CEF as an execution-governance method rather than documentation only. The WDI implemented-compatible annual scalar campaign evaluated all 27 remaining implemented-compatible WDI annual scalar indicators across 217 non-aggregate countries and 2000-2023. All 27 passed deterministic preflight and were loaded as one campaign bundle: 140,616 staging rows, 140,616 curated facts, 27 indicators, 217 territories, 2000-2023 coverage, and passing WDI quality checks.

Confidence implication: operational confidence increases inside the implemented-compatible WDI annual scalar country-indicator confidence cell. The increase is bounded and does not authorize full WDI catalog ingestion, provider mirroring, generic WDI framework extraction, arbitrary metadata/catalog ingestion, non-scalar representations, KnowledgeForge semantics, Companies/canonical identity work, or production/live ingestion.

Evidence artifacts:

- `artifacts/reports/R-20260708-task-165-wdi-implemented-compatible-campaign.md`
- `artifacts/tasks/TASK-165-wdi-implemented-compatible-annual-scalar-expansion-campaign.md`
- `artifacts/reports/task-165-wdi-campaign-updated-confidence-assessment.json`

## Mandatory boundaries

CEF does not authorize:

- provider mirrors;
- ingest-everything behavior;
- generic provider/source frameworks;
- canonical loaders for evidence-only slices;
- Companies/canonical identity work while frozen;
- runtime orchestration, scheduling, live/default writes, or production ingestion;
- weakening source-specific-first posture;
- suppressing validation failures;
- promotion based only on success counts.

## Verification of design requirements

- Generalizes across providers: confidence cell abstraction covers WDI, FRED, BLS, IMF, SEC, Eurostat, Census, UN Comtrade, and future providers by provider/source family, parser family, dataset family, representation class, and operational scope.
- Evidence-based confidence: confidence dimensions require concrete architecture, source, parser, representation, validation, operational, and mapping evidence.
- Localized escalation/regression: promotion and regression are scoped to the smallest evidence-supported confidence cell.
- Architecture/operations separation: architecture remains authoritative; CEF is planning/orchestration policy; existing workstreams execute implementation.
- Repository expansion improvement: routine ingestion becomes larger only after evidence supports the larger scope, preserving rigor while reducing repeated planning friction.
