# TASK-225 — Source-native Corporate Reporting private-analysis release-candidate admission contract and disposable rehearsal

Status: **COMPLETE — EXACT REVIEWED IMPLEMENTATION GIT-PUBLISHED; GOVERNANCE RECONCILIATION CLOSES TASK-225**

## Starting authority

Authorized on published TASK-224 commit `d20114aece9f9daf5d64b81880f103d76cff2715`. Isolated worktree: `/home/mkkto/srv/EIP/worktrees/MacroForge-task225-source-native-release-candidate`. TASK-224 lifecycle, `origin/main`, server `main`, exact frozen inputs, no-writer state, and PostgreSQL isolation passed before activation.

Frozen input owners:

- `artifacts/reports/task223-corporate-proof-tranche-ledger.json`: serialized SHA-256 `6fe4a5ad05836a7e290e71297e4d6ab328232cbfd5fefa2a0476370250061c9c`; internal identity `d55e413cae29d8abef44a871a22205d0504076ace916b1c643399ab7fb1a12b2`.
- `artifacts/reports/sec-corporate-portfolio-v1-manifest-20260630.json`: serialized SHA-256 `9cde110033fd3e8f22bedf768f01e7f90dd2c72784ad4f43172e5220ad9edf9f`; semantic identity `937056b9e903daa5e3550ed18cb1dff6d34bb1fbc49e3bb8e1f51a8d4420516a`.
- Canonical membership: the ledger’s exact 19 accessions and ten cessation-absence identities; observed accounting is 147 documents, 35,048 occurrences, 32,381 semantic slots, and two proposed amendment relationships.

## Objective

Extend the existing canonical Corporate Reporting release/authority owners to define and rehearse a deterministic versioned source-native private-analysis release candidate for exactly the frozen tranche. Prove content-bound membership identity, truthful mapping/no-map semantics, independent absence/failure/completeness and authority axes, release-representation precedence, rollback, replay, and two-database convergence.

Recurring effort reduced: downstream source-native analysis preparation, deterministic release validation, release-schema evolution uncertainty, and future recovery/context effort.

## Required semantics

- Candidate identity binds producer, contract/version, SEC cutoff, explicit non-applicable knowledge cutoff, exact membership content, dispositions, state axes, and predecessor relation.
- Exact frozen accession, document, occurrence, semantic-slot, amendment, and cessation-absence membership is immutable and duplicate-free.
- Filing-local absence, portfolio cessation absence, missing/malformed package, unresolved dependency, extraction failure, intentional exclusion, and technical incompleteness remain distinct.
- Existing mapping statuses remain unchanged. Candidate profile `absent` is not a mapping row. `deliberately_unmapped` is affirmative and attributable, not inferred from absence and not equivalent to deferred/rejected/fact conflict.
- Technical completeness, source membership completeness, semantic readiness, comparability, rights, quality, eligibility, publication, and delivery remain independent.
- One canonical candidate representation owns identity/digest; historical release/item forms are derived compatibility views or fail closed on disagreement.

## Database and authority boundary

Only uniquely named disposable `macroforge_task225_candidate_<12 lowercase hex>` databases carrying the exact runner-installed TASK-225 boundary marker may be mutated. Governed `macroforge` is read-only. No accepted mapping, governed rights/quality/eligibility/release/publication row, redistribution authority, remote delivery, downstream integration, portfolio expansion, or successor activation is permitted.

Two independently initialized disposable databases remain through local final evidence authentication, then are removed only by exact authenticated names before independent frozen-byte review. Independent review consumes canonical immutable evidence rather than mutable database state. No wildcard deletion.

## Verification

Follow strict TDD. Required order: contract/schema tests; focused negative tests; disposable rehearsal; rollback/replay; two-database determinism; applicable Corporate Reporting tests; one complete final-byte suite; coherence; context health; architecture reality; lifecycle/rights/publication checks; `git diff --check`; exact freeze; three independent identical-byte PASS reviews.

Before the complete suite, freeze tracked/untracked report paths that the suite can mutate and restore only authenticated suite residue.

## Closeout

Success required a reviewed deterministic candidate and disposable rehearsal, followed by a separately authorized exact-byte Git publication and governance reconciliation. The exact reviewed 29-path implementation was Git-published in commit `7379417873564f5412bcbd4fc2725ba7a1841c3d` by direct one-commit fast-forward. This governance reconciliation closes TASK-225 without governed admission, dataset release, redistribution permission, remote-delivery authority, or successor activation.

## Superseded pre-review outcome

Implementation and focused verification passed on the original candidate bytes. Migration 006, the candidate contract, persistence, deterministic runner, DEC-025, and the versioned contract specification were present. Focused TASK-225 tests passed `10 passed`; established Corporate Reporting integration passed `98 passed, 16 skipped`.

The original two-database rehearsal passed with exact 19/147/35,048/32,381/2/10 accounting, candidate SHA-256 `08ec6fb6c30b1eeeb9d62638c403954f32a00bb15874f3142e228a1b441e79a1`, payload file SHA-256 `6069a91c3841922bbff32bde5b6e60e2722fab571ecf5cc01f77d442bc999887`, and converged state SHA-256 `a03e54ff68b4a18a741c46cd394a19e02b347fca973f58eb56162f08f577d6b0`. Exact replay was a no-op and immutable-update attacks rolled back. Both disposable databases were authenticated and removed by exact name.

The first complete-suite attempt remains preserved as failed historical evidence: wrapper exit 124 after 600 seconds, 614 collected, 610 executed, 592 passed, 16 skipped, two missing-WDI-fixture failures, and four unexecuted. See `artifacts/reports/task225-incomplete-complete-suite-evidence.json`.

A replacement suite passed on the original bytes: wrapper exit 0, pytest exit 0, 614 collected and executed, 598 passed, 16 canonical protected-provider skips, zero failures/errors/deselections/unexecuted. See `artifacts/reports/task225-replacement-complete-suite-evidence.json`.

These results are historical only. Final review of freeze `1afcd39b94e99b424e4ccdd572099de537f45b2ae9e998b5aa62915654186bc8` returned FAIL / FAIL / UNCONDITIONAL PASS and correctly withheld unanimous acceptance. The failed freeze and review record remain superseded evidence and must not be represented as accepted.

## Historical remediation

The four review obligations are recorded in `artifacts/reports/task225-review-remediation-obligation-matrix.json`:

1. enforce actual disposable-database identity independently at Migration 006, persistence, and direct-SQL mutation boundaries;
2. make every private-analysis permission explicit, non-null, type-exact, and fail-closed in Python and SQL;
3. replace trailing-`Z` cutoff acceptance with canonical parse/round-trip and authenticated source-authority binding;
4. reconcile `context/_SUMMARY.md` and every related current-state claim.

At that remediation stage, implementation/schema/test changes invalidated the old focused, rehearsal, and complete-suite evidence. Fresh verification, two new disposable rehearsals, one final-byte complete suite, cleanup, canonical gates, a new exact freeze, and three fresh identical-byte unconditional PASS reviews were therefore required and were later completed.

Throughout remediation, governed accepted mapping/rights/quality/eligible-authority/release/publication counts remained zero; one inherited eligibility revision and authority root remained explicitly `blocked`. No governed release, redistribution permission, remote-delivery authority, or successor activation resulted.

## Remediated final-byte verification

The remediation obligations are implemented on exact candidate bytes and the invalidated gates have been rerun without reuse of rejected-byte acceptance:

- replacement focused gate: `68 passed`, zero skips/failures/errors/deselections/unexecuted; durable evidence `artifacts/reports/task225-remediation-focused-evidence.json`;
- applicable Corporate Reporting integration: `98 passed, 16 skipped`, zero failures/errors/deselections/unexecuted;
- fresh two-database rehearsal: PASS, exact replay no-op, rollback attacks rejected, candidate SHA-256 `08ec6fb6...`, payload SHA-256 `6069a91c...`, converged state SHA-256 `a03e54ff...`; canonical report SHA-256 `e688c360...`; both exact disposable databases authenticated and removed;
- exactly one final-byte complete suite: `672` collected/executed, `656 passed`, `16` protected-provider skips, zero failures/errors/deselections/unexecuted, wrapper exit zero; durable evidence `artifacts/reports/task225-final-byte-complete-suite-evidence.json`;
- fixture and suite residue: exact cleanup PASS; pre/post worktree manifest is byte-identical at 1,046 records with SHA-256 `2731dc31...`; no new cache/bytecode remains;
- canonical gates: coherence, context health, architecture reality, JSON validation, and `git diff --check` PASS with zero blocks/warnings;
- governed preservation: accepted mapping/rights/quality/eligible-authority/release/publication counts remain zero; one blocked eligibility revision and one blocked authority root remain; no TASK-225 relation, disposable database, relevant session, or prepared transaction remains.

Acceptance was withheld at that stage until a new exact-byte freeze received three independent unconditional PASS reviews. That gate was subsequently satisfied; any substantive byte change after a freeze would still invalidate its review.

## Rejected remediated freeze and successor correction

- Freeze `fd0cc9009e8ba4066d8914bcbcce8a12269f41cf08c5ccf8d491107a6b802fc2` was rejected unanimously after all three reviewers authenticated its 25 paths and aggregate `553ea49056dcf8bd26e06a85a9d3086e0d4ae68838249a476526fbf7d3ac9e67`.
- Reviewers found stale rehearsal chronology in the canonical contract and an impossible successor persistence contract: a same-table predecessor foreign key conflicted with the exact one-candidate database marker.
- A RED PostgreSQL regression reproduced the foreign-key rejection. Migration 006 now stores a syntactically constrained external predecessor identity without the impossible same-database foreign key, and the regression is GREEN.
- At that stage, this material SQL/test correction invalidated rehearsal, focused/integration acceptance, complete suite, continuity freeze, and reviews until fresh affected gates passed.
- The consumed complete-suite authorization is not reusable; a new complete-suite invocation requires fresh authorization.
- Fresh successor-corrected verification now passes: focused `69 passed`; Corporate Reporting integration `98 passed, 16 skipped`; two new disposable databases converged on candidate `08ec6fb...`, payload `6069a91c...`, and state `a03e54ff...`; rollback attacks were rejected without state change; canonical rehearsal report SHA-256 is `4a76043b...`; both databases were authenticated and removed exactly.
- Durable corrected-gate evidence: `artifacts/reports/task225-successor-correction-verification.json`.
- The first successor-corrected complete-suite attempt remains preserved as a timeout failure and was not reinterpreted. Diagnostic collection authenticated 673 items and classified the failure as ordinary cumulative runtime beyond the former 1,200-second cap.
- Exactly one authorized replacement complete suite passed on unchanged candidate bytes: wrapper/pytest exit zero, `673` collected/executed/accounted, `657 passed`, `16` protected-provider skips, zero failures/errors/deselections/unexecuted, and `[100%]` emitted in `1256.12s`.
- Durable accepted-suite evidence: `artifacts/reports/task225-successor-corrected-replacement-complete-suite-evidence.json`. The failed evidence remains separately preserved at `artifacts/reports/task225-successor-corrected-complete-suite-evidence.json`.
- Exact cleanup restored the 1,172-record pre-suite worktree baseline before writing the new evidence report, preserved all 11 cache/bytecode records and `pytest-3815`, and left no fixture, suite-created pytest root, TASK-225 database/session/process, or prepared transaction.
- The final exact 29-path candidate freeze and three unconditional identical-byte reviews completed before Git publication. The reviewed implementation was then published in commit `7379417873564f5412bcbd4fc2725ba7a1841c3d` by direct one-commit fast-forward; the accepted 673-item suite evidence remains unchanged.
- TASK-225's scoped implementation objective is complete, and this governance reconciliation closes the task. Git publication is not governed Corporate Reporting admission or dataset release. The source-native candidate remains private-analysis-only; accepted mappings, rights, quality, eligible authority, releases, publication reservations, and publication completions remain absent; no governed database write, redistribution permission, remote-delivery authority, downstream consumption authority, or successor activation occurred. No successor is active or defined, and the repository is idle pending explicit user direction.
