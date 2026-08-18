# TASK-222 — Corporate Portfolio v1 accession/disposition manifest and package-compatibility validator

Status: **GIT-PUBLISHED AND TECHNICALLY CLOSED; no successor active**

## Authority

User-authorized bounded successor to the completed TASK-221 post-pilot scope review. Baseline: `3e2cfc2d5db3d0236a8e468868d2a690d76d7b15`. Work occurs only in the detached isolated worktree `/home/mkkto/srv/EIP/worktrees/MacroForge-corporate-portfolio-v1-manifest-validator`.

## Goal

Implement a source-specific SEC Corporate Portfolio v1 manifest builder and package-compatibility validator that reduces recurring accession/package validation effort while preserving official-source provenance, deterministic replay, explicit dispositions, and fail-closed outcomes.

## Frozen logical corpus

- 15 accepted CIKs named in the task authorization.
- Issuer fiscal years 2021–2025.
- SEC acceptance cutoff `2026-06-30T23:59:59Z`.
- Forms `10-K`, `10-Q`, `10-K/A`, `10-Q/A`.
- Proposed expectations: 300 original slots; 290 observed originals; 10 acquisition-cessation absences; 21 amendments; 311 filing acts.
- These are frozen expectations, not authority to force current evidence to agree.

## Required outputs

1. Deterministic 300-row expected-original-slot ledger and exact disposition per slot.
2. Exact metadata manifest for every included filing act, with amendments preserved separately.
3. Evidence-backed Gatos and Marathon cessation absences.
4. Original-to-amendment relationship proposals that do not assert restatement authority.
5. Issuer fiscal-year/period evidence, including Cal-Maine 52/53-week treatment.
6. Per-accession package inventory: primary, instance where separate, extension schema, available calculation/presentation/definition/label linkbases, recursively referenced external DTS dependencies, roles, owners, URLs, byte lengths, SHA-256 identities, and retrieval evidence.
7. Inline/traditional XBRL classification, including traditional-XBRL Gatos accession `0001104659-21-062988`.
8. Exactly one classified terminal compatibility outcome for every attempted package.
9. Explicit deterministic dependency closure/stop rules and fail-closed discrepancy reporting.

## Required terminal outcomes

`compatible`, `acquisition failure`, `metadata discrepancy`, `missing package component`, `package-role ambiguity`, `unsupported traditional XBRL`, `unsupported Inline XBRL`, `unresolved external dependency`, `malformed package`, or `explicit governed exclusion`.

No attempted package may have a silent or unclassified outcome.

## SEC discipline

- Authority sources: SEC submissions metadata, EDGAR filing indexes, filing/package documents, and referenced XBRL dependencies.
- Company Facts is not accession, package, mapping, comparability, or release authority.
- Use only configured `macroforge.secUserAgent` request identity at a bounded rate.
- Provider bodies remain ephemeral outside Git and governed PostgreSQL. Retain only metadata, URLs, lengths, hashes, dependency relationships, compatibility outcomes, and retrieval evidence.
- Provider count discrepancies are preserved and classified; frozen expectations are never silently regenerated.

## Authored-fixture verification

Cover Inline and traditional XBRL, full/partial amendments, multiple/non-restating amendments, 52/53-week calendars, acquisition cessation, misleading filenames, missing/multiple roles, external DTS references, dependency cycles/bounds, dimensions/typed members, USD/shares/USD-share, Inline scale/sign, duplicates/conflicts, deterministic replay identity, and SEC-vs-frozen discrepancy.

## Implementation-scope exclusions

The implementation phase did not authorize governed PostgreSQL ingestion; Migration 005 change; query/release semantic change; mapping acceptance; reporting-scope authority; final restatement authority; semantic metric selection/formulas; eligibility/rights/quality authority; release reservation/completion; market/securities/corporate-action/estimate/global-identity work; remote delivery; Git publication; provider-body persistence; generic provider-neutral framework; or reopening TASK-221. Git publication was separately reviewed and authorized after implementation completion.

## Acceptance criteria

- [x] Isolated baseline and protected live-tree identities authenticated.
- [x] Exactly 300 expected original slots produced deterministically.
- [x] Every slot and attempted package has one explicit disposition/outcome.
- [x] Current official SEC evidence is compared to `300/290/10/21/311`; discrepancies fail closed.
- [x] Complete package-role and bounded recursive dependency evidence is retained without provider bodies.
- [x] Required authored tests pass without bytecode/cache pollution.
- [x] Related Corporate Reporting tests pass.
- [x] Exact candidate path/hash freeze and fresh adversarial review complete.
- [x] Governed PostgreSQL authority counts and protected live tree remain unchanged.
- [x] At the implementation-closeout checkpoint, nothing was staged, committed, pushed, data-published, or remotely delivered.

## Completion evidence

- Final repository report: `artifacts/reports/sec-corporate-portfolio-v1-manifest-20260630.json`.
- Final report size: `9,767,049` bytes; serialized SHA-256 `9cde110033fd3e8f22bedf768f01e7f90dd2c72784ad4f43172e5220ad9edf9f`; semantic identity `937056b9e903daa5e3550ed18cb1dff6d34bb1fbc49e3bb8e1f51a8d4420516a`.
- Final official-source E/F builds are byte-identical and preserve exact `300/290/10/21/311` accounting, `311 compatible` terminal outcomes, `16,653` acquired dependency edges, and zero unresolved packages.
- Permanent adversarial coverage includes duplicate-accession failure, exact amendment base-form/report-date matching, traditional-XBRL fact features, dependency URL policy, redirect-before-follow rejection, final-URL-before-read rejection, and exact per-document retrieval evidence.
- Final focused verification: `30 passed`; related Corporate Reporting selection: `58 passed, 16 skipped`. The skips require unavailable protected provider fixtures and remain skips.
- The earlier complete repository suite ran `590` items: `572 passed, 16 skipped, 2 failed in 505.13s`. Both failures were isolated-worktree absences of ignored `data/metadata/wdi/wdi-smoke-normalized.json`, not TASK-222 regressions. After provisioning that authenticated fixture and adding four permanent URL/redirect tests, the authoritative final suite executed `594/594`: `578 passed, 16 skipped`, with zero failed, errors, deselected, or unexecuted items and exit status `0`. The 16 protected-provider skips remain skips.
- Final implementation freeze identity: `00cab9c83a49e8e601fd48d3611f1fee604f8c034c2aa6b4819dc28e9dfd8c75` before continuity-only closeout edits.
- Fresh independent adversarial review authenticated the freeze and returned unconditional `PASS`.
- No provider bodies, credentials, or unrelated environment data entered Git or governed PostgreSQL.

## Git publication and terminal reconciliation

The implementation-ready state above was the truthful pre-publication checkpoint. A separate publication-readiness review authenticated the frozen eight-path TASK-222 boundary and preservation of ten inherited protected paths. Under later explicit user authorization, exactly those eight TASK-222 paths were committed as `4f2647d5350d580848e0bf9431f20aff1c1d9c20`, with parent `3e2cfc2d5db3d0236a8e468868d2a690d76d7b15`, and pushed by non-force fast-forward to remote `main`; local `origin/main` advanced to the same commit. All ten protected paths were excluded.

The live checked-out `main` branch was deliberately left at the parent because its 39 tracked-unstaged and 1,070 untracked paths are protected external state. Git publication covered authored implementation and manifest metadata only. It did not perform PostgreSQL ingestion, create a MacroForge governed data release, accept mappings or rights, authorize redistribution, enable remote delivery, or activate a successor.

## Current next action

No successor task is active. These reconciliation bytes record the already-known implementation publication commit and do not predict a future governance-commit hash. Their own Git durability must be authenticated independently. Any ingestion, data release, rights or mapping acceptance, redistribution, remote delivery, or successor activation requires separate explicit authority.
