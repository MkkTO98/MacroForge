# TASK-225 source-native private-analysis candidate contract v1

Status: corrected complete-suite acceptance established — 673 accounted, 657 passed, 16 protected-provider skips, and zero failures, errors, deselections, or unexecuted items; source-native private-analysis-only; non-governed
Owner: MacroForge Corporate Reporting
Canonical schema: `macroforge.corporate-reporting.source-native-candidate.v1`

## Purpose and authority boundary

This contract reduces recurring effort needed to authenticate and package an exact Corporate Reporting source-native tranche for private analysis without falsely implying semantic comparability or governed release authority. A candidate is not a governed release. It creates no accepted mapping, rights, quality, eligibility, publication, redistribution, or delivery authority.

## Exact input authority

The only admitted input is the authenticated TASK-223 tranche bound by:

- ledger internal identity `d55e413cae29d8abef44a871a22205d0504076ace916b1c643399ab7fb1a12b2`;
- source-manifest semantic identity `937056b9e903daa5e3550ed18cb1dff6d34bb1fbc49e3bb8e1f51a8d4420516a`;
- 19 exact accession identities;
- 147 exact source-document identities;
- 35,048 filing-qualified occurrence identities;
- 32,381 filing-qualified semantic-slot identities;
- two proposed, non-authoritative amendment relationships with restatement status undetermined;
- ten exact acquisition-cessation absence identities.

An accession, document, occurrence, slot, amendment, or absence outside this membership fails closed. Occurrence and slot hashes are filing-qualified: the owner identity is `(accession, hash)`, not the bare hash.

## Canonical candidate identity

Canonical JSON uses sorted object keys, UTF-8, no insignificant whitespace, and deterministic list ordering. `candidate_sha256` is SHA-256 of the canonical document with the `candidate_sha256` field absent. The delivered payload is that document with `candidate_sha256` inserted and one terminal newline. Candidate identity is independent of database name, insertion clock, and PostgreSQL row identifiers.

Every filing member binds source manifest identity; SEC-scoped CIK; distinct filer, reporting-entity, and reporting-scope identities; no universal-company identity; source documents; occurrences; slots; amendment state; acceptance clock; and report period. SEC cutoff, the explicitly inapplicable knowledge cutoff, candidate predecessor, and candidate revision identity are independent fields.

## Semantic and lifecycle dispositions

Every released source-native slot carries:

- `mapping.disposition = deliberately_unmapped`;
- `mapping.attribution = task225-source-native-contract-v1`;
- its independent `fact_resolution_status`.

`deliberately_unmapped` is not `accepted`, `absent`, `proposed`, `deferred`, `rejected`, or fact-resolution `conflict`. It supports source-native inspection only. Comparative claims require separately accepted mappings.

Portfolio expected-filing absence is represented only as an authenticated acquisition-cessation absence. It cannot alias extraction failure, malformed or missing packages, intentional exclusion, technical incompleteness, unresolved dependencies, nil facts, or fact-resolution conflict.

The independent candidate axes are technical completeness, source-membership completeness, semantic readiness, comparability, rights, quality, eligibility, publication, and delivery. Private-analysis candidate use is true; redistribution is not authorized; publication and remote delivery are false.

## Persistence and replay

Migration 006 owns append-only, non-governed candidate headers, filing members, absence members, and state axes. Database triggers bind every relational child to the exact canonical JSON array ordinal and digest. Header and children are immutable. Exact replay is a no-op. A conflicting insert or update fails atomically. Historical corrections require a successor candidate linked by the predecessor candidate's content-addressed SHA-256 identity. Because each disposable database is intentionally bound to one exact candidate, the predecessor is an external immutable identity rather than an impossible same-database foreign key; this linkage creates no authority to mutate or accept the predecessor.

Only exact disposable databases named `macroforge_task225_candidate_<12 lowercase hex>` and carrying the exact runner-installed TASK-225 boundary marker may hold candidate rows. Governed `macroforge` remains read-only. Candidate persistence never writes `corporate_release`, `corporate_release_item`, mapping, rights, quality, eligibility, reservation, completion, or shared publication tables.

## Representation precedence

Before governed admission, candidate v1 is the canonical non-governed source-native representation. After separately authorized governed admission, authority-derived v3 release bytes are canonical. Historical v2 and stored release/item representations are compatibility views only and must match authority-derived v3 or fail closed. Candidate v1 can never override governed v3.

## Verification chronology

The remediation rehearsal initialized two disposable databases from the independently replayed TASK-223 R4A and R4B source states and converged on:

- candidate SHA-256 `08ec6fb6c30b1eeeb9d62638c403954f32a00bb15874f3142e228a1b441e79a1`;
- payload file SHA-256 `6069a91c3841922bbff32bde5b6e60e2722fab571ecf5cc01f77d442bc999887`;
- payload length 13,090,189 bytes;
- candidate database state SHA-256 `a03e54ff68b4a18a741c46cd394a19e02b347fca973f58eb56162f08f577d6b0`.

The canonical rehearsal evidence is `artifacts/reports/task225-source-native-candidate-rehearsal.json`, SHA-256 `4a76043b533c11b4a890b9e532eb3e97ad0991c9d14fedf896f7f662ecd189a0`. It was regenerated after the successor correction against two new exact disposable databases. Both independently initialized source states converged on the identities above; replay was a no-op; rollback attacks were rejected without state change; governed authority counts remained zero; and both candidate databases were authenticated and removed by exact name before frozen-byte review.
