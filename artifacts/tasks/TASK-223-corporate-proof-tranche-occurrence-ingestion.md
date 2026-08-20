# TASK-223 — Corporate Portfolio v1 proof-tranche occurrence ingestion and isolated PostgreSQL rehearsal

Status: **REVIEWED — PUBLICATION-READY**

## Authority

User-authorized bounded successor to published TASK-222. Baseline: `6900a58f2a5850f6511e20a23f036efcf71ea9d8`. Work occurs only in detached isolated worktree `/home/mkkto/srv/EIP/worktrees/MacroForge-task223-corporate-proof-tranche-ingestion`.

## Goal

Implement and prove a source-specific SEC Corporate Reporting loader that consumes authenticated TASK-222 manifest records, reacquires exact official filing packages, extracts raw source occurrences, and ingests them into uniquely named disposable isolated PostgreSQL databases. The task must prove faithful deterministic multi-filer ingestion, replay, restart, amendment preservation, and explicit cessation absences without writing governed PostgreSQL or accepting mappings, releases, rights, redistribution, or delivery authority.

## Mandatory pre-implementation tranche

Derive and freeze only from `artifacts/reports/sec-corporate-portfolio-v1-manifest-20260630.json`:

1. one original 2023 fiscal-year `10-K` for each accepted CIK;
2. every exactly linked `10-K/A`;
3. Gatos traditional-XBRL accession `0001104659-21-062988`;
4. Cal-Maine fiscal-year-2025 `10-K` and exactly linked amendments;
5. all ten frozen acquisition-cessation absence identities.

Deduplicate accessions. Stop if any criterion is unsupported. The ledger must freeze issuer, accession, form, period, acceptance, amendment relation, format, package identity, and absence identity.

## Implementation boundary

- Reuse Migration 005 and existing Corporate Reporting contracts; do not modify schema doctrine for convenience.
- Remain source-specific; no provider-neutral framework.
- Preserve filing/document/occurrence/comparison/mapping/release separation.
- Keep contexts, units, documents, scopes, entities, and occurrences accession-local where required.
- Provider bodies may exist only in uniquely identified TASK-223 temporary storage outside Git and governed PostgreSQL.
- Permanent tests use authored synthetic fixtures; no SEC filing body may enter Git.
- Proof databases must be uniquely TASK-223-named disposable databases; governed database `macroforge` is read-only for authentication.

## Required proof

- Exact TASK-222 manifest authentication and frozen tranche ledger.
- Official SEC reacquisition with request identity, bounded rate, strict URL/redirect/final-URL policy, and exact requested/final/status/length/hash checks.
- Inline and traditional XBRL extraction, including nonzero Gatos facts.
- Multi-CIK campaign, exact/inexact amendments, Cal-Maine 52/53-week evidence, concepts, contexts, units, dimensions, nil/scale/sign/duplicate/conflict evidence, and explicit absences.
- Per-filing transaction rollback, safe restart, idempotent replay, no unintended updates, complete dispositions, and zero silent failures.
- Identical stable database-state identities across two fresh disposable databases.
- Deterministic metadata-only proof report with no provider bodies or semantic-equivalence claims.

## Verification

1. focused TASK-223 authored tests;
2. related Corporate Reporting tests;
3. isolated PostgreSQL proof tranche;
4. replay in one database;
5. deterministic second-database comparison;
6. required compilation, diff, recovery, context, coherence, and architecture checks;
7. governed PostgreSQL and live dirty-tree reauthentication;
8. exact candidate freeze and fresh independent adversarial review.

## Explicit exclusions

No governed PostgreSQL writes, production Corporate Reporting rows, mapping acceptance, semantic-equivalence inference, final reporting-scope authority, restatement classification, governed release, rights/redistribution authority, remote delivery, downstream Forge integration, complete 311-package ingestion, staging, commit, push, publication, successor activation, or retained provider body in Git.

## Acceptance criteria

- [x] Isolated baseline and live protected state remain authenticated.
- [x] Exact proof tranche frozen before production-code changes.
- [x] Existing schema faithfully represents every selected proof case; no schema gap remains.
- [x] Authored RED/GREEN tests cover required positive and adversarial cases.
- [x] Official proof tranche fully classified with no silent failure.
- [x] Replay and two-database stable-state identities pass.
- [x] Metadata-only proof report contains complete row and evidence accounting.
- [x] Governed PostgreSQL, publication authority, and live tree remain unchanged.
- [x] Exact candidate frozen and fresh independent review passes.

## Current next action

Await explicit publication authority for the exact post-record ten-path candidate. Publication must remain limited to staging, committing, and publishing those authenticated paths through the normal TASK-223 lifecycle. Do not rerun ingestion, replay, or the complete suite; do not activate TASK-224.

## Proven campaign checkpoint

Campaign `a4c0bc3a385b4612a8156222b3c07101` independently ingested and replayed the frozen 19-act/10-absence tranche in R4A/R4B. Fresh read-only reauthentication reproduced SHA-256 `6ec07fda17adc36825479552bc34baada697b0cfee7e535e914acf95545afe15` in both databases, with 19 filings, 147 documents, 35,048 occurrences, 32,381 semantic slots, two proposed amendment relationships, and zero mapping/snapshot/eligibility/release/publication/rights/quality authority.

The corrected complete suite ran exactly once against these exact implementation and test bytes using authenticated Python 3.11.15 and pytest 8.4.2: 604 collected and accounted, 588 passed, 16 protected-provider skips retained, zero failed, errored, deselected, or unexecuted, exit status zero. Exact suite residue was authenticated and non-recursively reconciled; the protected TASK-165 report retained its pre-suite SHA-256 `aee8ca86a9dd4c72f3ad5a217966bc7c8219d223523115c1addfcc7cfd479358`.

## Final independent review

Three independent read-only reviews authenticated the identical clean implementation freeze, canonical candidate SHA-256 `6676cb6230fa911d0c31a0a3bfe893f9c3822bace8c44edcb27ca93138689366`, and returned unconditional PASS:

1. Corporate Reporting boundary, authority separation, occurrence preservation, and exact 19-act/10-absence portfolio accounting: **PASS**.
2. Transaction rollback, replay, two-database convergence, target isolation, governed-database preservation, and zero authority leakage: **PASS**.
3. Permanent-test sufficiency, complete-suite accounting, exact suite-time byte identity, protected-skip honesty, and residue/protected-state separation: **PASS**.

No reviewer changed files, reran ingestion or pytest, or wrote PostgreSQL. TASK-223 is reviewed and publication-ready but is not committed, published, or closed.
