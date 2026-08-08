# TASK-PF-20260801 — Ignored-artifact preservation governance

Status model: fixed-point publication transition; live condition is derived from authenticated Git state and external review evidence, not asserted by these bytes
Task class: bounded ProjectForge/MacroForge governance correction
Authority baseline: `37cbbbd076926a1dfcecaab11a4c03305d123284`

## Objective

Preserve ignored/untracked artifact evidence safely and enforce one exact 15-path publication boundary. The sixth bounded correction additionally makes lifecycle and current-state representations stable across review, local commit, and verified remote publication.

## Durable history

1. Initial authorship produced an unpublished 15-path candidate.
2. The first independent publication review blocked publication.
3. The first bounded correction remained unpublished.
4. The second independent publication review blocked lifecycle openness, unsafe special-file inspection, false observation completeness, and unbounded marker reading.
5. The second correction addressed those findings.
6. The third independent implementation audit blocked output-family cardinality bypass, caller-defined boundary authority, and stale lifecycle truth.
7. The third correction established unconditional one-family cardinality and code-owned exact-path authority.
8. The first independent correction audit blocked one-sided caller observations receiving false completeness.
9. The fourth correction separated argument suppliedness from empty bytes and forced one-sided calls to incomplete caller-supplied-unverified semantics.
10. The independent correction re-audit passed 79 executed probes, with zero failures and one explicit `CAP_MKNOD` platform skip. The skip was not counted as a pass.
11. The independent closeout-consistency audit passed against its exact predecessor bytes.
12. The next publication review blocked stale current-pointer wording while finding implementation, evidence integrity, and boundary sound.
13. The fifth correction reconciled those lifecycle/current-pointer words without changing implementation.
14. The independent lifecycle delta audit passed against the exact fifth-correction bytes.
15. The latest exact-candidate publication review returned `BLOCKED / PUBLICATION TRANSITION DEFECT`; report SHA-256 `d728d980fdc056cfac58020443de332f7b74131c12c2d5d817b12c8d1cdd0e15`, Hermes session `macroforge-successor-publication-review-20260808-d728d980fdc056cf`, payload `192848`. It remains a BLOCK and grants no authority.
16. The sixth correction replaces transient live review/publication assertions with the v3 state-conditioned fixed-point contract.

## Preserved enforcement guarantees

- Exactly one record-specific output family.
- The record and supplied boundary each equal one code-owned canonical 15-path tuple.
- Unknown claim-bearing fields fail closed.
- Descriptor-pinned, no-follow regular-file inspection and prompt special-file rejection.
- Independent canonical Git discovery owns observation completeness.
- Caller-supplied populations are verified only when both are explicitly supplied and both match independent discovery.
- Bounded `CACHEDIR.TAG` and PYC inspection.
- Prospective-only reproducibility, provider-rights qualification, and preservation/publication scope separation.
- Deterministic capture and comparison.

## Publication fixed-point contract

The v3 record and current pointers encode an invariant rather than a live verdict:

| Authenticated condition | Required transition |
| --- | --- |
| Working-tree candidate; no exact approving evidence | Independent publication review required |
| Working-tree candidate; exact authenticated `BLOCK` | Correction required; publication prohibited |
| Working-tree candidate; exact authenticated `PASS` | Bounded publication permitted without candidate mutation |
| Local commit ahead of authoritative remote; exact `PASS` retained | Push and remote verification required |
| Exact approved commit verified at authoritative remote | Workstream closed; no successor implicitly activated |

Missing, malformed, ambiguous, unauthenticated, non-recoverable, or different-byte evidence fails closed. A review verdict changes external authority, not the reviewed bytes. Local commit is not verified publication.

## Verification evidence

Predecessor evidence remains historical and is not continuity over changed production bytes. The predecessor complete suite was exactly `488 passed, 2 failed`; both failures were baseline-identical absent ignored `data/metadata/wdi/wdi-smoke-normalized.json` failures, so the suite was not green. The prior independent re-audit recorded 79 executed passes and one separate `CAP_MKNOD` platform skip.

The sixth correction used RED/GREEN TDD in an isolated Git-backed export. The new transition test failed first because `evaluate_publication_transition` did not exist, then passed after the minimal extension. The affected ignored-artifact module passed `42` tests before the transition test was merged into the exact-history regression to preserve the established complete-suite count. Final verification and independent transition-audit evidence are external authority inputs and do not require mutation of this transition-invariant record.

No staging, commit, push, publication, PostgreSQL mutation, WDI repair, cleanup, unrelated work, successor ingestion, or `TASK-220` activation is authorized by this record.
