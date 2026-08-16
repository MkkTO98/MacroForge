# TASK-221 — Bounded Corporate Reporting Gatos vertical slice

Status: **GIT-PUBLISHED AND TECHNICALLY CLOSED; no successor active**

## Goal and outcome

Implement the frozen Gatos Silver, Inc. original `10-K` / amendment `10-K/A` Corporate Reporting slice with deterministic SEC/XBRL parsing, PostgreSQL persistence, knowledge-time/query semantics, release gating, lineage, amendment semantics, and preservation verification.

The exact 13-path implementation candidate was implemented, verification-complete, prospectively adopted from authenticated current bytes, and independently reviewed `PASS`. It was then included in the exact reviewed 20-path Git publication boundary and published under explicit user authority in commit `3be04c379409067e728ff851e7b98d3c08d8d864` (`feat: add SEC corporate reporting foundation`). Repository publication is complete; no Corporate Reporting data release or remote delivery occurred.

Frozen planning authority remains external under `/tmp/macroforge-corporate-gatos-freeze-6DQdCj/derived/`.

## Exact final candidate

Final freeze: `/tmp/task221-fourth-final-candidate-freeze-v1.json`

- manifest SHA-256: `2ef71bf434a911f520530d084b114369640a5d9804cac0a2bc94e06cedf9c5bd`;
- canonical identity serialization: `2,670` bytes;
- canonical SHA-256: `3816e7f4cf90190cbfa145b88304106e5af0611b138702ba56d0a8dec713907f`;
- pre-publication checkpoint branch/HEAD/local `origin/main`: `main` / `4d5fb7148c79bc25510a1b3ad4f594610389e8da` / same;
- pre-publication checkpoint staged/unmerged: `0/0`;
- intended Git mode for every candidate path: `100644`;
- recorded filesystem permission for every candidate path: `0600`.

The 13 frozen paths are:

1. `db/migrations/005_corporate_reporting_foundation.sql` — 55,752 bytes — `94513da9506c113ef7d2790aa9870b6fa72438fe5743389a04a5f056a633b45b`
2. `src/macroforge/corporate_reporting_queries.py` — 33,272 bytes — `c5a7f2d102127abe0bc6dc9fbc2d31421d1f281eef5d9d805f8fca1d811b3281`
3. `src/macroforge/corporate_reporting_release.py` — 31,568 bytes — `e61fe565186012d901462b4317424442775713642e9be684bf198418a862a59a`
4. `src/macroforge/sec_corporate_reporting.py` — 21,162 bytes — `a51e71fddceb86cbc2d335d13e1e87a6066cef05f345bd6cc5dc472f222f0995`
5. `src/macroforge/sec_corporate_reporting_loader.py` — 60,539 bytes — `d23b877b3f415dcec14d36418386dbfa7f7a75be3200a924628059260ef63478`
6. `tests/fixtures/sec_corporate_reporting/compact-conflict.xml` — 610 bytes — `0d405d966651fdc45935499a918ed0ee13fcf954d8d8b9840e53af728cda2b75`
7. `tests/fixtures/sec_corporate_reporting/compact-instance.xml` — 2,411 bytes — `a134f53c481487f5c6641736873828a9d8c2d5ed5d594ad625d81cb425780a09`
8. `tests/fixtures/sec_corporate_reporting/malformed-divide.xml` — 293 bytes — `946170be040eb912a783d0486aa0427d1039abe610b543a4c110daa215ab7072`
9. `tests/fixtures/sec_corporate_reporting/source-hash-manifest.json` — 828 bytes — `ed32ea19a35f87360dc2b5ce85b31358fa53e85786eac9c600dfe768ea7fef99`
10. `tests/test_corporate_reporting_queries.py` — 44,806 bytes — `b0b7d59781766df7cf394f5e93f900a411ce7230dfc5fb3fa8ab069b7cbb5eaf`
11. `tests/test_corporate_reporting_release.py` — 11,080 bytes — `92c6f8395944565eef56711dc6d7a1f5c0ba82b65a436c7e1d075f28cca9556b`
12. `tests/test_sec_corporate_reporting.py` — 16,087 bytes — `fb8eef2af11e34fac2b7ff346fd5215dfa4d1af9bd1602bb3945ad2cae5bc27d`
13. `tests/test_sec_corporate_reporting_loader.py` — 57,600 bytes — `56d3c5a7cd73df1b9e656a927c0df3b8ba226eea30d47909474958a489981fa5`

## Fourth-remediation outcome

The blocked predecessor exposed independently callable `PostgresCorporateAuthorityStore.record_publication(...)` and `complete_publication(...)` lifecycle transitions. The fourth bounded remediation removed both standalone store methods and left no equivalent protocol method, wrapper, alias, module helper, callback, generic SQL writer, or callable object.

The only ordinary production completion route is `publish_database_anchored(authority=..., store=..., target=...)`. It accepts no caller release payload, canonical JSON, installer/callback, completion token, success flag, or filesystem-success assertion. It performs PostgreSQL authority resolution, internal canonical-byte derivation, exact reservation, immutable installation, installed-byte verification, status persistence and fsync, directory durability, then completion persistence. Any earlier exception prevents completion. Exact replay remains bound to the original act; mismatched targets/digests conflict.

Historical writer provenance for the four intermediate fourth-remediation files remains unresolved. Their adoption is prospective from authenticated current bytes; no retrospective authorship claim is made. `tests/test_sec_corporate_reporting_loader.py` previously experienced an unexplained same-byte metadata rewrite. Current content identity is authenticated; historical metadata preservation is not claimed.

## Verification

Identical implementation/test bytes passed:

- lifecycle adversarial selection: `13 passed in 3.08s`;
- complete query module: `25 passed in 4.11s`;
- complete release module: `18 passed in 0.06s`;
- combined authority/query/release selection: `43 passed in 4.15s`;
- focused Corporate Reporting suite: `58 passed, 16 skipped in 10.08s`;
- Python compilation and `git diff --check`: PASS;
- coherence/context/recovery checks: zero blocks;
- architecture audit: zero blocks and only the known cadence warning for 22 completed tasks with indeterminate completion dates.

Renewed complete suite evidence:

- command: `PYTHONPATH=. .venv/bin/pytest -q`;
- managed wrapper PID: `376838`;
- UTC interval: `2026-08-13T07:29:21.229301706Z` to `2026-08-13T07:48:47.585687283Z`;
- result: `1 failed, 1027 passed, 16 skipped in 1165.45s`;
- sole failure: `tests/test_architectural_governance.py::test_architecture_reality_audit_includes_governance_without_dirtying_clean_audit`;
- classification: authenticated pre-existing governance-cadence warning concerning the same 22 temporally indeterminate completed tasks; no TASK-221 regression;
- external evidence: `/tmp/task221-renewed-complete-suite-20260813.{command,process,status,out}`.

The 16 skips are protected-Gatos integration cases requiring unavailable protected provider fixtures. They are skips, not passes. Each required TASK-221 parsing, loading, authority, release, lifecycle, replay, mismatch, failure, QName, parser-ownership, and allowlist behavior has active authored-fixture and, where relevant, isolated-PostgreSQL evidence. No protected bytes were fabricated, reconstructed, downloaded, or substituted.

## Independent review

The authenticated 23-question contract is 1,834 bytes with SHA-256 `136773b3dbd0570b2e91f309ac0dfec9809d10a2a945be9dc76c8c7024e60e14`.

One fresh read-only reviewer authenticated all 13 frozen identities and returned `PASS`. Answers 1–23 were all favorable:

1. constructed objects/digests are not authority;
2. authority is resolved from governed PostgreSQL state;
3. dependency closure is independently verified;
4. accepted keys cannot be substituted onto detached payloads;
5. copied/reconstructed/pickled/fabricated authority cannot create a publication act;
6. exact replay is idempotently bound and mismatches reject;
7. identity-bearing payloads cannot be rewritten with recomputed digests;
8. typed-member SHA derives from canonical typed XML;
9. accepted/terminal revisions cannot change in place;
10. semantic dependencies are immutable or independently revalidated;
11. parser-B slots cannot reference parser-A authority;
12. cross-parser violations reject relationally;
13. QName values use element-local scope;
14. descendant QName attributes work;
15. nested prefix rebinding works;
16. non-QName colon strings are preserved;
17. `release_as_of` has no authority-free path;
18. `known_as_of`/fact authorization resolves authoritative payloads;
19. release identity binds all selection-changing dependencies;
20. recursive allowlists are complete and leakage-resistant;
21. original filing/revision/point-in-time/conflict/mapping/rights/isolation invariants remain covered;
22. permanent adversarial tests are sufficient, including lifecycle confinement;
23. this exact candidate is ready for separate publication review.

The reviewer explicitly accepted prospective adoption despite unresolved historical writer provenance and the same-byte metadata incident, without converting either limitation into a false historical claim.

## Git publication and terminal reconciliation

The implementation-ready state above was the truthful pre-publication checkpoint. A separate publication-readiness review authenticated an exact 20-path boundary: the 13 implementation/test/fixture paths plus seven TASK-221 governance paths. Under later explicit user authorization, that exact boundary was committed and pushed as `3be04c379409067e728ff851e7b98d3c08d8d864`, with parent `4d5fb7148c79bc25510a1b3ad4f594610389e8da`. Committed blobs and modes matched the reviewed candidate, and post-push local HEAD, `origin/main`, and the server-advertised `refs/heads/main` were synchronized at the publication commit.

When these reconciliation bytes are present in authenticated repository HEAD, TASK-221 is Git-published and technically closed. The publication event does not authorize Corporate Reporting data release, mapping acceptance, provider redistribution, or remote data delivery. No successor task was automatically created or activated.

## Preservation and live state

- Both provenance directories and their sealed inventories remain preserved:
  - `/tmp/task221-provenance-evidence-20260813T054619Z-296074`
  - `/tmp/task221-provenance-evidence-20260813T053415Z-294541`
- All 126 pre-existing TASK-208 evidence records remain byte-identical.
- Two verification-generated WDI report rewrites were restored to authenticated pre-suite bytes.
- Four wholly new TASK-208 failure-capture residue files and two new test bytecode files were removed.
- Pre-existing Git-visible complement records were neither changed nor removed.
- Remaining ignored changes are verification-generated pytest/bytecode caches and are not candidate or publication evidence.
- Existing PostgreSQL table counts are unchanged; all observed DML counters remain zero.
- Corporate Reporting releases/reservations/completions: `0/0/0`.
- Accepted real mappings, eligible real revisions, redistribution rights, and quality authority: `0/0/0/0`.
- No Corporate Reporting data-publication artifact or status sidecar exists; remote delivery is disabled.

## Output families

| Family | Representative paths | Role | Terminal disposition / publication expectation |
|---|---|---|---|
| Corporate Reporting implementation | exact frozen 13-path manifest | authored project truth | Git-published in `3be04c379409067e728ff851e7b98d3c08d8d864`; technically closed |
| PostgreSQL state | Migration 005 and source-scoped tables | generated local verification state | local-only; not publication evidence |
| Provider filing evidence | protected Gatos material outside repository | local/provider evidence | external-only; redistribution rights unresolved |
| Verification/review evidence | task record and authenticated `/tmp` freeze/suite/provenance evidence | governance evidence | historical evidence supporting the completed Git publication |
| Runtime caches | pytest/bytecode cache families | generated/rebuildable | ignored; never publication material |

## Terminal state and next action

TASK-221 implementation and Git publication are complete. Mapping, eligible-revision, Corporate Reporting data-release, redistribution-rights, quality-authority, and remote-delivery gates remain fail-closed at zero or disabled. No successor is active. Any future Corporate Reporting work requires a separately selected and authorized task; repository publication must not be treated as data-release or provider-rights authority.

Resume command:

`cd /home/mkkto/srv/EIP/projects/MacroForge && PYTHONDONTWRITEBYTECODE=1 python3 tools/recover_session.py --project . --json`
