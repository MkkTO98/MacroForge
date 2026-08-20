# DEC-025 Corporate Reporting candidate and governed-release representation precedence

Date: 2026-08-20
Status: accepted for TASK-225 implementation
Supersedes: no prior decision; refines DEC-024

## Decision

Use one phase-dependent canonical representation:

1. Before governed admission, source-native candidate v1 is canonical for the non-governed private-analysis candidate.
2. After separately authorized governed admission, authority-derived v3 release bytes are canonical.
3. Historical v2 release bytes and stored `corporate_release` / `corporate_release_item` forms are compatibility representations only. They must agree with authority-derived v3 or resolution fails closed.
4. Candidate v1 cannot override governed v3 and cannot be treated as a governed release.

Candidate persistence therefore uses dedicated append-only Migration 006 tables. It must not reuse governed release, membership, mapping, rights, quality, eligibility, reservation, completion, or publication tables.

## Rationale

Migration 005 contains both historical release/item storage and authority-derived v3 resolution. Without explicit precedence, identical economic evidence could acquire competing release identities. Phase-dependent precedence preserves source-native candidate usefulness while keeping authority closure and publication semantics under the existing governed v3 owner.

This is the smallest extension that represents exact candidate membership, portfolio absences, independent state axes, replay, and relational integrity without inventing parallel governed authority.

## Consequences

- TASK-225 can persist and replay a deterministic candidate only in exact disposable `macroforge_task225_candidate_<12 lowercase hex>` databases carrying the exact runner-installed TASK-225 boundary marker.
- Comparative claims remain blocked because every slot is deliberately unmapped and accepted mappings remain zero.
- Rights, quality, eligibility, publication, redistribution, and delivery remain non-authoritative or prohibited.
- A later admission task must create fresh governed authority and derive v3 bytes; it may not promote candidate rows by reinterpretation.
- Any disagreement among v3 and compatibility representations is a hard failure, not an automatic repair.
