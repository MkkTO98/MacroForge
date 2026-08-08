# Latest Handoff

## Stable handoff

The exact 15-path `TASK-PF-20260801` workstream now uses a publication-transition fixed point. Determine live state from authenticated Git observations plus byte-recoverable external review evidence; do not treat this handoff as a live verdict.

## Durable chronology

- Earlier implementation/correction blocks and passes remain in the v3 closeout event history.
- Independent closeout-consistency audit PASS remains predecessor evidence only.
- The wording-only successor's independent delta audit passed.
- Its subsequent exact-candidate publication review returned `BLOCKED / PUBLICATION TRANSITION DEFECT`; report SHA-256 `d728d980fdc056cfac58020443de332f7b74131c12c2d5d817b12c8d1cdd0e15`, Hermes session `macroforge-successor-publication-review-20260808-d728d980fdc056cf`, payload `192848`. It remains a BLOCK.
- The sixth correction minimally extends the existing lifecycle validator and continuity doctrine; it does not create a parallel publication subsystem.

## Transition routing

- Working-tree candidate, no exact approving review -> independent publication review.
- Exact authenticated `BLOCK` -> correction; no publication.
- Exact authenticated `PASS` for candidate bytes -> bounded publication may proceed without candidate mutation.
- Local commit ahead of remote -> push and verify authoritative-remote equality.
- Exact approved commit at authoritative remote -> close this workstream; do not implicitly activate a successor.

Missing, malformed, mismatched, ambiguous, unauthenticated, or non-recoverable evidence fails closed. Local commit is not verified publication.

## Verification context

- Predecessor exact suite: `488 passed, 2 failed`; both failures baseline-identical missing ignored `data/metadata/wdi/wdi-smoke-normalized.json`; not green.
- Prior correction re-audit: 79 executed passes and one explicit `CAP_MKNOD` platform skip.
- Sixth-correction RED/GREEN was performed in an isolated Git-backed export. Fresh full affected verification and an independent transition audit must bind to exact successor bytes; those external results do not require this file to change.
- No PostgreSQL work or WDI repair belongs to this workstream.

## Recovery

Resume with:
`cd /home/mkkto/srv/EIP/projects/MacroForge && PYTHONDONTWRITEBYTECODE=1 python3 tools/recover_session.py --project . --json`

Then derive the applicable transition from authenticated Git and review evidence. Do not assume one unconditional next action from prose.
