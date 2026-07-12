# Architecture State

## Current architecture

MacroForge is governed by Strategic Constitution v1.1. Its strategic asset is deterministic ingestion for public economic evidence.

Current ingestion architecture:

```text
Source-specific acquisition
-> Source-specific normalization
-> ObservedIngestionPackage v1
-> Deterministic post-boundary substrate
-> Existing source-specific staging/canonical load SQL where scoped
-> Validation
-> Canonical PostgreSQL where scoped
```

## Strategic extraction doctrine

Shared deterministic infrastructure owns post-boundary mechanics only after independent implementations show convergence, deterministic verification, acceptable coupling, and measurable future effort reduction. Source-specific behavior belongs before the boundary. Generic shared infrastructure must not contain source-specific conditionals.

After TASK-053 and DEC-022, the default assumption is that the current post-boundary architecture is correct. Future implementation should attempt to falsify this assumption through bounded heterogeneous sources, not proactively redesign the substrate or observed boundary.

DEC-023 and `docs/architecture/long-term-domain-vision.md` record MacroForge's observation-domain boundary: MacroForge owns source-backed observations, provenance, reproducibility, lineage, validation, and observational identity; KnowledgeForge owns reusable meaning, semantic identities, claims, hypotheses, relationship interpretation, evidence evaluation, confidence, uncertainty, contradictions, and epistemic state.

## Source implementation posture

Canonical-loaded paths: WDI, OECD_NAAG, EUROSTAT_NAMQ_GDP.

Bounded evidence-only and operational slices span many official/public providers through TASK-165. Evidence-only slices do not imply broad provider support, canonical loading, generic frameworks, or capability registries.

## Observed boundary and deterministic substrate

`ObservedIngestionPackage` is documented in `docs/architecture/observed-ingestion-representation.md` and implemented in `src/macroforge/observed_ingestion.py`. Source-specific observed-package construction lives in explicit source-owned modules where extracted; compatibility wrappers remain narrow.

Current post-boundary components: package fingerprinting/comparison, contract validation, source-specific loaded package reconstruction, lineage-event generation, quality/drift checks, and deterministic feedback.

Post-boundary substrate effort is currently low. Source acquisition, provider interpretation, normalization, capability-level planning/selection, and repository-class validation remain the main effort centers.

## Capability maturity

TASK-188 declares the following constitutionally mature for stated scopes and frozen pending future falsification:

- source-specific acquisition and normalization boundary;
- ObservedIngestionPackage v1 scalar boundary;
- deterministic post-boundary substrate for scalar observed packages;
- source-neutral run/release/lineage/quality metadata recording;
- DRDF / ACPF / CEF planning governance;
- WDI implemented-compatible annual-scalar operational cell;
- bounded revision-aware scalar convention;
- capability closure / stopping discipline.

Shared Post-Boundary Infrastructure Extraction remains Discovered and negatively frozen: do not extract generic shared frameworks without repeated convergent implementation evidence.

## Current planning architecture

TASK-163 accepted CEF as file-backed orchestration policy over confidence cells. TASK-167 accepted DRDF for domain portfolio selection. TASK-168 accepted ACPF between domain and confidence cell. These are governance layers only: no runtime framework, ontology/schema change, semantic system, canonical identity work, production/live authority, source registry, or scoring engine.

Accepted planning hierarchy:

```text
Strategic objective -> macroeconomic domain -> analytical capability -> maturity/completeness gap -> confidence cell -> CEF-sized campaign/slice -> source-specific implementation task
```

DRDF selects/governs the macroeconomic domain. ACPF specifies analytical capability, dependencies, gap, and stopping criteria. CEF selects the largest safe evidence-backed ingestion scope. Existing source-specific workstreams execute implementation.

## WDI annual-scalar scaling evidence

TASK-165 through TASK-204 scaled the WDI implemented-compatible annual-scalar cell across major macro/development domains. Current WDI/GFDD/ILO/Barro-Lee annual-scalar coverage: 1,394 indicators, 217 non-aggregate countries, 1990-2024 annual periods, and 10,424,284 curated facts.

Architecture verdict: overlapping WDI campaigns require run-scoped validation, checkpoint/resume hygiene, correction reloads that remove obsolete facts and refresh lineage/quality, and bounded chunking. They still do not justify schema redesign, provider mirrors, generic source frameworks, canonical identity changes, or production scheduling.

## BLS monthly scalar Phase 2 evidence

TASK-208 completed a corrected BLS public API v2 U.S. labor-market breadth campaign: 36 seasonally adjusted monthly series, 7,116 facts, 198 monthly periods from 2010-M01 through 2026-M06, 0 provider exclusions, 0 acquisition errors, and 0 duplicate canonical-key groups. TASK-207 and TASK-208 now share canonical source identity `BLS_PUBLIC_API_V2`; campaign differences live in dataset/release/run metadata.

Architecture verdict: reaffirmed. The existing source-specific monthly scalar path, monthly periods, canonical source/dataset/run separation, lineage, quality checks, missing-value handling, atomic artifact publication, and same-run idempotence were sufficient. The exposed defects were implementation hygiene: campaign-specific source identities, two malformed JOLTS candidate identifiers, and a temporary BLS unregistered daily-threshold blocker. None require schema redesign, provider framework extraction, or source-independent time-series architecture.

## Cross-repository-class generalization posture

TASK-181 through TASK-188 validated source-specific acquisition/normalization, deterministic file-backed evidence, scalar observed-package handoff, source-neutral run/release/lineage/quality metadata, DRDF/ACPF/CEF governance, and bounded ALFRED revision-aware scalar conventions. The current architecture preserved changed/unchanged vintages and expected absences without schema redesign.

Still unvalidated outside this workstream: relationship/matrix roles, event identity, entity filing/accounting contexts, and whether attributes/source_payload remain sufficient when non-WDI classes scale.

No revision/vintage subsystem, schema redesign, provider mirror, production scheduling, or generic time-series framework is justified. Future architecture work requires concrete implementation evidence: new repository class pressure, observed operational limitation, repeated implementation friction, canonical ambiguity, scale/performance failure, or repeated downstream query pain.

## Methodology evidence artifacts

Core methodology artifacts:
- `docs/architecture/domain-coverage-assessment.md`
- `docs/capability-atlas.md`
- `docs/architecture/architectural-confidence-ledger.md`
- `docs/architecture/architectural-surprise-log.md`
- `docs/architecture/marginal-source-cost-index.md`
- `docs/architecture/recurring-implementation-pain.md`
- `docs/architecture/long-term-domain-vision.md`
- `docs/architecture/domain-centric-repository-development-framework.md`
- `docs/architecture/analytical-capability-planning-framework.md`
- `docs/architecture/confidence-escalation-framework.md`

## Deferred areas

Unless accepted task/decision changes scope, defer broad source support, generic provider/source/domain frameworks, runtime orchestration, semantic graph/catalog systems, live production writes, generic revision/SDMX infrastructure, issuer/entity registries, KnowledgeForge semantics, downstream-system implementation, relationship frameworks, graph models, and canonical identity extraction.

## Neutral evidence outbox boundary

TASK-212 validates a MacroForge-owned producer outbox for neutral evidence releases. The accepted trigger is successful canonical release closeout: transactionally durable canonical facts, succeeded pipeline run, dataset release identity, zero failed quality checks, and complete subscription selection. The outbox is producer-owned and consumer-neutral; consumers copy/poll immutable artifacts and validate independently. MacroForge must not write into consumer inboxes, import consumer code, query consumer databases, or encode consumer derivations. Scheduling/event buses remain out of scope until repeated producer-side generation evidence justifies automation.
