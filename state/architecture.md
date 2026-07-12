# Architecture State

## Current architecture

MacroForge is governed by Strategic Constitution v1.1. Its strategic asset is deterministic ingestion for public economic evidence.

Current ingestion architecture:

```text
Source-specific acquisition
-> Source-specific normalization
-> ObservedIngestionPackage v1 where applicable
-> Deterministic post-boundary substrate
-> Source-specific staging/canonical load SQL where scoped
-> Validation
-> Canonical PostgreSQL where scoped
```

## Active doctrine

The default architecture posture remains evidence-first and source-specific-first. Shared deterministic infrastructure owns post-boundary mechanics only after independent implementations show convergence, deterministic verification, acceptable coupling, and measurable future effort reduction. Source acquisition, provider interpretation, source semantics, candidate selection, and normalization remain source-specific before the boundary.

After TASK-053 and DEC-022, assume the current post-boundary architecture is correct until bounded heterogeneous implementation evidence falsifies it. Do not redesign the substrate, observed boundary, schema, provider identities, source registry, runtime orchestration, production scheduling, semantic graph, or generic provider framework without concrete implementation evidence: repository-class mismatch, canonical ambiguity, source-boundary contradiction, release/vintage loss, provider-semantics loss, scaling/performance failure, or repeated downstream query pain.

DEC-023 and `docs/architecture/long-term-domain-vision.md` define the observation-domain boundary: MacroForge owns source-backed observations, provenance, reproducibility, lineage, validation, and observational identity. KnowledgeForge owns reusable meaning, semantic identities, claims, hypotheses, relationship interpretation, evidence evaluation, confidence, uncertainty, contradictions, and epistemic state.

## Accepted source-specific boundaries

Canonical-loaded and operational paths include WDI annual-scalar campaigns, OECD_NAAG, EUROSTAT_NAMQ_GDP, BLS monthly scalar campaigns, IMF WEO/DataMapper forecast-vintage scalar evidence, IMF BOP/IIP/reserves operational slices, BIS SDMX scalar campaigns, and neutral evidence-release/outbox capability where explicitly implemented.

Bounded evidence-only and operational slices remain source-specific evidence, not broad provider support. Evidence-only slices do not imply canonical loading, generic frameworks, production authority, or capability registries.

## Observed boundary and deterministic substrate

`ObservedIngestionPackage` is documented in `docs/architecture/observed-ingestion-representation.md` and implemented in `src/macroforge/observed_ingestion.py`. Source-specific observed-package construction lives in explicit source-owned modules where extracted; compatibility wrappers remain narrow.

Current post-boundary components: package fingerprinting/comparison, contract validation, source-specific loaded-package reconstruction, lineage-event generation, quality/drift checks, deterministic feedback, source/release/run metadata recording, and source-specific loader verification.

Post-boundary substrate effort is currently low. The main effort centers remain source acquisition, provider interpretation, normalization, capability-level planning/selection, repository-class validation, artifact publication discipline, and closeout verification.

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

## Planning architecture

Accepted planning hierarchy:

```text
Strategic objective -> macroeconomic domain -> analytical capability -> maturity/completeness gap -> confidence cell -> CEF-sized campaign/slice -> source-specific implementation task
```

DRDF selects/governs the macroeconomic domain. ACPF specifies analytical capability, dependencies, gap, and stopping criteria. CEF selects the largest safe evidence-backed ingestion scope. Existing source-specific workstreams execute implementation.

## Evidence-backed maturation highlights

WDI annual-scalar scaling evidence: TASK-165 through TASK-206 scaled the implemented-compatible annual-scalar cell across major macro/development domains. Architecture verdict: overlapping WDI campaigns require run-scoped validation, checkpoint/resume hygiene, correction reloads that remove obsolete same-run facts and refresh lineage/quality, and bounded chunking; they still do not justify schema redesign, provider mirrors, generic source frameworks, canonical identity changes, or production scheduling.

BLS monthly scalar evidence: TASK-207 and TASK-208 share canonical source identity `BLS_PUBLIC_API_V2`; campaign differences belong in dataset/release/run metadata. Architecture verdict: monthly periods, source/dataset/run separation, lineage, quality checks, missing-value handling, atomic publication, and same-run idempotence were sufficient. Exposed defects were implementation hygiene, not schema contradictions.

WEO/DataMapper forecast-vintage evidence: TASK-209 proved WEO release/vintage identity must be evidence-derived and release-specific. Source identity `IMF_WEO_DATAMAPPER_API_V1` is separate from WEO dataset/release identity. Provider-supplied forecast scalars must not be described as observed economic outcomes, and actual/estimate/projection status must not be inferred from calendar year alone.

BIS SDMX Phase 2 evidence: TASK-213 through TASK-215 reaffirmed scalar compatibility when the complete provider series key is audited and only territory is removed while material non-territory dimensions remain in indicator identity/attributes. `Prepared` timestamp is snapshot evidence, not official release semantics. Narrow BIS helpers may exist only where repeated stable contracts are proven; no universal SDMX/provider framework is justified.

TASK-216 IMF BOP evidence: TASK-216 scaled IMF BOP annual current-account monitoring using source `IMF_SDMX_BOP_API_V1`, dataset `IMF:BOP`, dataflow `BOP` v21.0.0 / DSD v24.0.0, provider dataset `UPDATE_DATE` as-of key `imf-bop-asof-20260711t231424302015100z`, run `task-216-imf-bop-current-account-phase2`, selected accounting entry `NETCD_T`, components `CAB/G/S/IN1/IN2`, `USD_SCALE_6`, and annual periods 2010-2024. It froze 214 accepted countries, 1,070 provider-advertised series, and 16,050 candidate cells, then loaded 14,475 facts: 13,600 provider-valued and 875 explicit-missing, with 105 whole-series absences, 0 acquisition errors, 0 incompatible series, 0 failed quality checks, 0 duplicate canonical-key groups, same-run idempotence, and simulated later-as-of coexistence.

TASK-216 architecture verdict: reaffirmed. The selected BOP family remained scalar-compatible because only territory was removed from the complete provider series key; accounting entry, component, unit, scale, frequency, provider attributes, source/dataset/as-of/run identity, lineage, and quality evidence were preserved. Whole-series absence remained distinct from explicit missing facts and acquisition failure. `IMF_SDMX_BOP_API_V1` denotes the IMF external SDMX 2.1 BOP API/source boundary, not TASK-216 scope and not WEO/DataMapper. No BOP/IMF generic framework, universal SDMX adapter, accounting ontology, campaign engine, multidimensional schema, or canonical identity change is justified. Revisit only if another BOP/IIP relationship campaign shows repeated stable source-specific responsibilities without freezing earlier campaign-specific identity drift.

## Neutral evidence outbox

TASK-212 validates a MacroForge-owned, consumer-neutral outbox for canonical closeout. MacroForge may publish immutable observed-evidence artifacts after durable canonical facts, succeeded run, release/run lineage, passing quality checks, and complete subscription selection. It must not write into consumer inboxes, import/query consumer systems, or encode consumer derivations.

## Deferred areas

Unless accepted task/decision changes scope, defer broad source support, generic provider/source/domain frameworks, runtime orchestration, semantic graph/catalog systems, live production writes, generic revision/SDMX infrastructure, issuer/entity registries, KnowledgeForge semantics, downstream-system implementation, relationship frameworks, graph models, and canonical identity extraction.
