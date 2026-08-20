# DEC-024 — Corporate Reporting placement and release-admission posture

Status: accepted
Date: 2026-08-20
Related tasks: `TASK-221`, `TASK-222`, `TASK-223`, `TASK-224`
Related decision: `DEC-023-long-term-domain-vision-and-knowledgeforge-boundary.md`
Admission analysis: `artifacts/reports/R-20260820-task-224-corporate-reporting-release-admission-gap-map.md`

## Decision

Corporate Reporting remains a **bounded sibling domain inside MacroForge**. Its `corporate_reporting` schema and SEC-specific modules provide sufficient isolation today. A stronger in-repository subproject/package and a separate Forge are rejected for now because TASK-221–223 prove a bounded SEC observational lifecycle, not independent deployment, ownership, storage, or consumer authority.

MacroForge retains ingestion under every placement: acquisition/authentication, filing/document evidence, immutable source occurrences, deterministic parsing, lineage, and validation. In the selected placement it also owns source-native normalization and producer-local release construction. It never owns reusable cross-source corporate identity, semantic truth, claims, investment analysis, or presentation.

The smallest correct successor is a **source-native private-analysis release-candidate admission contract and disposable rehearsal for the exact TASK-223 19-filing tranche**. It precedes semantic comparability. Mapping state remains explicit (`absent`, `proposed`, or later `accepted`) rather than becoming a prerequisite for source-native use. No successor is activated by this decision.

## Rationale

The proven work—acquisition, authentication, parsing, occurrence preservation, provenance, replay, and producer release control—belongs to MacroForge under DEC-023. Migration 005 already isolates Corporate Reporting while reusing shared run/release identities. TASK-223 converged two isolated databases at 19 filings, 147 documents, 35,048 occurrences, 32,381 semantic slots, and two proposed amendment relationships without authority leakage.

No separate deployment, owner, release operator, storage engine, consumer contract, or rights regime has been proven. Retention avoids duplicated metadata, migrations, tooling, and cross-project transactions. Directory neatness or domain size does not justify stronger packaging.

## Identity and semantic boundaries

- Universal identities such as time/location are referenced, not duplicated.
- CIK is an SEC source identifier; `reporting_entity` is an evidence anchor, not a legal-entity registry.
- Filer, reporting entity, and reporting scope remain distinct.
- Source concepts, extensions, slots, mapping states, conflicts, and deliberate no-map remain distinct.
- MacroForge mappings/snapshots govern producer-local normalization and release. Reusable cross-source semantics and claims belong to KnowledgeForge.
- Immutable occurrences never become mappings by reinterpretation.

## Revision, admission, and rights

Provider, amendment, extraction, entity, scope, mapping, rights, quality, eligibility, and release revisions remain independent. Source/knowledge point-in-time state and append-only release state use separate clocks; successors never mutate historical membership or bytes.

A source-native private-analysis candidate may precede accepted cross-company mappings but must expose mapping status and must not claim semantic comparability. Comparative analysis requires a later narrow metric-family pilot.

Rights remain separate assertions for access, storage, private analysis, derived-data use, redistribution, publication, and delivery. Current architecture supports only conservative private-analysis disposition. Redistribution remains unresolved/not authorized and remote delivery disabled. Public SEC access is not redistribution permission.

The canonical ordinary publication route is PostgreSQL-resolved authority plus immutable reservation/completion. Historical `corporate_release`/`corporate_release_item` and `corporate_publication_act` mechanisms are not a second authority; a successor must explicitly reconcile their precedence with authority-derived v3 release bytes.

## Future split triggers

Reconsider stronger packaging or a separate producer only when evidence establishes one or more qualitative conditions:

- independent deployment, migration, operating, or release cadence;
- rights, credentials, retention, or publication controls requiring separate operational authority;
- a non-SEC source forcing a stable multi-provider observational model that cannot remain source-specific without leaking into unrelated MacroForge domains;
- storage or compute requirements incompatible with MacroForge’s PostgreSQL/local-execution model;
- corporate semantics overwhelming repository/tooling boundaries despite current isolation;
- a stable independent consumer contract and owner able to accept immutable artifacts without shared databases, runtime packages, or cross-project rollback.

More filings, facts, tests, tables, or code are not split triggers.

If a separate producer is later justified, MacroForge still performs acquisition/authentication and deterministic parsing to immutable filing/document/source-occurrence evidence, then hands off versioned content-addressed manifests. The separated processor may own only post-ingestion corporate-domain normalization and release authority. Universal identities are referenced; CIK and source concepts stay source-scoped. Shared PostgreSQL tables, duplicated identities, and cross-project rollback are prohibited.

## Consequences

- TASK-224 creates no project, schema, authority, release, or database row.
- Reuse existing authority-root/resolver, mapping, rights, quality, eligibility, release, and publication mechanisms.
- The WDI outbox contributes design ideas, not a Corporate Reporting contract.
- KnowledgeForge receives nothing until the minimum contract in the gap report is accepted.
- Every successor remains inactive pending explicit authorization.
