# Project State

## State representation

`TASK-PF-20260801` uses `macroforge-ignored-artifact-governance-lifecycle-v3`. Its current pointers are transition invariants, not snapshots that claim a review is pending, a review is the sole next gate, a local commit is published, or a successor is active.

## Stable authority facts

- Authority baseline: branch `main`, commit `37cbbbd076926a1dfcecaab11a4c03305d123284`.
- Publication boundary: one code-owned canonical 15-path tuple.
- Latest blocked review remains immutable evidence: `BLOCKED / PUBLICATION TRANSITION DEFECT`, SHA-256 `d728d980fdc056cfac58020443de332f7b74131c12c2d5d817b12c8d1cdd0e15`.
- Review verdicts are external evidence bound to exact candidate bytes; they change authority, not repository-byte truth.
- Local commit and verified authoritative-remote publication are distinct states.
- Verified publication closes this workstream without implicitly activating a successor.

## Condition-derived transition

1. Working-tree difference and no authenticated exact-byte approval: independent review required.
2. Working-tree difference and authenticated exact-byte `BLOCK`: correction required; publication prohibited.
3. Working-tree difference and authenticated exact-byte `PASS`: bounded publication permitted without another candidate edit.
4. Approved local commit with authoritative remote not equal: push and remote verification required.
5. Exact approved commit verified at authoritative remote: workstream closed; no successor automatically activated.

The evaluator fails closed for missing, malformed, mismatched, ambiguous, unauthenticated, or non-recoverable evidence.

## Verification posture

Predecessor complete-suite evidence remains exactly `488 passed, 2 failed`, with both failures baseline-identical absent ignored-WDI-fixture failures; the suite is not claimed green. The prior independent correction re-audit produced 79 executed passes plus one separate `CAP_MKNOD` platform skip. Changed implementation requires fresh successor verification and independent transition audit; their external evidence can advance authority without editing these bytes.

## Constraints

These records do not authorize staging, commit, push, publication, PostgreSQL mutation, WDI repair, unrelated cleanup, successor ingestion, or `TASK-220` activation.
