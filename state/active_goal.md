# Active Goal

## Goal

Govern the exact 15-path `TASK-PF-20260801` workstream with a publication-transition fixed point: external review, commit, push, and verified remote publication must change authority without forcing mutation of the reviewed candidate bytes.

## Transition invariant

Do not infer live authority from this file alone. Derive the repository condition from authenticated Git observations and combine it with authenticated, byte-recoverable external review evidence using `evaluate_publication_transition`:

- working-tree candidate without exact approving evidence -> independent review required;
- exact authenticated `BLOCK` -> correction required and publication prohibited;
- exact authenticated `PASS` for the working-tree bytes -> bounded publication permitted;
- approved local commit ahead of authoritative remote -> push and remote verification required;
- exact approved commit verified at authoritative remote -> workstream closed, with no implicit successor activation.

Missing, malformed, ambiguous, unauthenticated, non-recoverable, or different-byte evidence fails closed. Local commit is not remote publication.

## Durable context

- Authority baseline: `main` at `37cbbbd076926a1dfcecaab11a4c03305d123284`.
- Exact publication boundary: the code-owned 15-path tuple in `tools/check_coherence.py`.
- Latest recorded publication review: `BLOCKED / PUBLICATION TRANSITION DEFECT`, report SHA-256 `d728d980fdc056cfac58020443de332f7b74131c12c2d5d817b12c8d1cdd0e15`.
- Sixth correction: v3 transition-invariant lifecycle semantics and fail-closed evaluator.
- Complete predecessor suite evidence: `488 passed, 2 failed`, both baseline-identical absent ignored-WDI-fixture failures; not green.
- Prior independent re-audit: 79 executed passes and one separate `CAP_MKNOD` platform skip.

## Boundaries

No state in this file grants staging, commit, push, publication, PostgreSQL mutation, WDI repair, cleanup, `TASK-220`, or successor work. Authorization must come from the authenticated external transition condition.
