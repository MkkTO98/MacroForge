# TASK-224 Corporate Reporting governed-release admission gap map

Date: 2026-08-20
Decision: `artifacts/decisions/DEC-024-corporate-reporting-placement-and-release-admission.md`
Evidence baseline: TASK-221–223 published records at parent `99c45ea22331529d0287e8cc9c1ffc783608d7a7`

## Principal admission verdict

Choose a **source-native private-analysis release candidate with mapping explicitly absent/proposed** before a semantic-comparability pilot. The 19-filing tranche is already useful for source-native filing analysis, provenance inspection, taxonomy/extension research, and within-filing extraction checks. Accepted cross-company mappings are required for comparative claims, not for truthful source-native release membership.

TASK-224 creates no release. Existing governed authority counts remain unchanged.

## Placement option assessment

| Option | Evidence assessment | Verdict / reconsideration gate |
|---|---|---|
| Bounded sibling domain inside MacroForge | Migration 005 already isolates the schema; SEC modules/tests are source-specific; shared run/release metadata and one owner/runtime are useful; TASK-221–223 show no cross-domain leakage | **Selected.** Lowest complexity consistent with current evidence. |
| Stronger MacroForge subproject/package | Could sharpen import/migration/test ownership while retaining one repository, operator, database platform, and release authority, but no current dependency collision or independent cadence justifies the new boundary | **Rejected now.** Reconsider before a separate Forge if corporate code requires an independently versioned API, migration stream, test/runtime dependency set, or release cadence while operational authority still remains MacroForge-wide. |
| Separate Forge, with MacroForge retaining ingestion | Would isolate post-ingestion corporate normalization/release, but today would duplicate lifecycle/tooling and create a handoff without an independent owner, rights regime, deployment, storage need, or stable consumer contract | **Rejected now.** Reconsider only on DEC-024’s stronger operational split triggers; MacroForge still retains acquisition, authentication, parsing, and immutable source-occurrence evidence. |

More filings, tables, or code do not alone move the choice from the first row.

## Existing-mechanism classification

| Mechanism | Classification | Disposition |
|---|---|---|
| `corporate_reporting` schema; SEC parser/loader/proof runner | already present and sufficient | Keep source-specific and inside MacroForge. |
| Filing/document/occurrence/context/unit/slot identities and immutable replay | already present and sufficient | Reuse without reinterpretation. |
| `meta.dataset_release`, `meta.pipeline_run`, quality and lineage | already present and sufficient | Reuse shared MacroForge infrastructure. |
| Knowledge revisions, snapshots, mapping/equivalence assertions | already present but needing bounded extension | Existing mapping statuses are `accepted`, `proposed`, `deferred`, and `rejected`. Add an explicit source-native no-map disposition only in the successor contract; accepted mapping remains mandatory for comparability. |
| Rights, quality, eligibility, opaque authority root/resolver | already present but needing bounded extension | Specify a complete source-native admission closure; do not treat the SQL view alone as authority. |
| Multi-item release membership and canonical release model | already present but needing bounded extension | Reconcile authority-derived v3 bytes with historical release/item representation; one canonical precedence rule is required. |
| Publication reservation/completion | already present and sufficient | Canonical ordinary local publication route; not exercised by TASK-224 or its immediate successor rehearsal. |
| Portfolio-level expected-filing absence | genuinely absent | Current `fact_absence_revision` is filing-local; add only if release membership must carry cessation absence authority. |
| Accepted real mappings, rights, quality, eligibility, release membership | genuinely absent as governed facts | Must be created only by later separately authorized admission/publication work. |
| Broad comparability ontology, canonical company identity | intentionally deferred | Start with a narrow later metric family and separately governed identity work. |
| Investment claims, confidence, causal interpretation, InsightForge/BriefForge delivery | inappropriate for MacroForge | Keep downstream. |
| Separate Corporate Reporting Forge | intentionally deferred | Reassess only on DEC-024 split triggers. |

## Compact gap map

Block columns: SN = source-native release; CA = comparative analysis; PU = private use; RD = redistribution; DD = downstream delivery.

| Requirement | Current evidence | Owner | Status | Consequence if omitted | Earliest task | Blocks SN/CA/PU/RD/DD |
|---|---|---|---|---|---|---|
| Immutable 19-filing and 147-document membership | TASK-223 ledger, report, source identities and deterministic two-DB state | MacroForge | satisfied as proof; not governed membership | Candidate cannot prove exact scope | inactive successor | Y/Y/N/Y/Y |
| Deterministic release fingerprint | Stable-state hash exists; release builder hashes canonical JSON | MacroForge | partial | No stable release identity | inactive successor | Y/Y/N/Y/Y |
| SEC cutoff/as-of and knowledge cutoff | Filing acceptance, SEC cutoff, revision/snapshot clocks exist | MacroForge | satisfied | Point-in-time claims become ambiguous | inactive successor validates | Y/Y/N/Y/Y |
| Filer/reporting entity/reporting scope separation | Schema/parser preserve distinct records | MacroForge | satisfied | Entity/scope joins become unsafe | inactive successor validates | Y/Y/N/Y/Y |
| CIK scheme scope | `sec:cik` is explicit; no universal company identity exists | MacroForge | satisfied | Identity overlap with KnowledgeForge/other providers | inactive successor validates | Y/Y/Y/Y/Y |
| Occurrence/document provenance | TASK-223 proves immutable local source identities and slot provenance | MacroForge | satisfied | Results are unauditable | inactive successor validates | Y/Y/Y/Y/Y |
| Amendment status | Two links are proposed; restatement undetermined | MacroForge + human semantic authority | partial | Consumers may choose wrong terminal filing | later amendment review; candidate exposes status | N/Y/N/N/Y |
| Ten cessation absences | Deterministic ledger records; not governed DB rows | MacroForge | partial | “No filing” may be confused with failure | inactive successor specifies/persists candidate representation | Y/Y/N/N/Y |
| Extraction failure versus explicit absence | Per-filing rollback and runner failure evidence exist; failed attempt may not persist in DB | MacroForge | partial | Missing data becomes falsely complete | inactive successor | Y/Y/N/N/Y |
| Source taxonomy and company extensions | Preserved as parser-run/DTS-scoped concepts | MacroForge | satisfied | Source-native meaning is lost | inactive successor validates | Y/Y/Y/Y/Y |
| Explicit mapping disposition | Proposed/deferred mechanisms exist; resolver currently requires accepted mapping | MacroForge producer-local authority | partial | Source-native candidate is falsely blocked or falsely comparable | inactive successor | Y/Y/N/N/Y |
| Accepted cross-company mapping | Zero accepted mappings | Human semantic authority; reusable semantics in KnowledgeForge | absent | Comparative claims unsupported | later narrow comparability pilot | N/Y/N/N/Y |
| Mapping conflict/deliberate no-map | No mapping no-map status exists; fact-resolution `conflict` is a separate axis and must not be reused as mapping disposition | MacroForge/KnowledgeForge boundary | genuinely absent / bounded extension | Unmapped may be mistaken for failed or fact conflict | inactive successor | Y/Y/N/N/Y |
| Private-analysis rights disposition | Policy/output family exists; real accepted rights revision count is zero | Human rights authority | partial | Governed admission cannot assert allowed use | later rights/admission task; successor remains non-authority | Y/N/N/N/Y |
| Redistribution evidence | No permission; schema allows unresolved/not-authorized only | Human rights authority | absent | Illegal/unsupported redistribution risk | later official-source rights decision | N/N/N/Y/Y |
| Remote delivery permission | Hard-disabled | Human rights authority | prohibited now | No downstream transfer | separate future authority | N/N/N/N/Y |
| Technical completeness | TASK-223 complete proof; quality closure rows are warning/fail and lack release-grade evidence closure | MacroForge | partial | Eligibility cannot be honestly accepted | inactive successor | Y/Y/N/Y/Y |
| Semantic readiness status | Mapping axis exists but source-native/comparable profiles are not separated | MacroForge/KnowledgeForge | partial | Technical and semantic status collapse | inactive successor | Y/Y/N/N/Y |
| Release eligibility closure | One historical blocked row; resolver validates closure, but no real eligible tranche | MacroForge + human authorities | absent for tranche | No governed release authority | later admission task after rehearsal | Y/Y/N/Y/Y |
| Canonical multi-item membership model | Historical release/item tables and authority-derived v3 bytes coexist | MacroForge | partial | Competing release identities | inactive successor | Y/Y/N/Y/Y |
| Reservation/completion and append-only history | Implemented and fail-closed | MacroForge | satisfied | Publication cannot be recovered/audited | later publication task | N/N/N/Y/Y |
| Rollback/replay | Exact replay, conflict rollback, immutable successors exist | MacroForge | satisfied | Corrections may mutate history | inactive successor validates | Y/Y/N/Y/Y |
| KnowledgeForge consumer contract | Conceptual boundary exists; no Corporate Reporting contract | MacroForge producer + KnowledgeForge consumer | absent | Downstream may duplicate/blur identity and authority | after governed publication | N/N/N/N/Y |
| InsightForge/BriefForge integration | Outside task and downstream of KnowledgeForge | respective Forge | deferred | No analysis/presentation delivery | later tasks | N/N/N/N/N |

Private use here means local inspection/analysis of lawfully accessed evidence; it is not a governed release claim. Thus several admission gaps block source-native release but do not block continued local private analysis of TASK-223 evidence.

## Genuine source-native admission blockers

1. No exact governed multi-item membership and release fingerprint for the 19 filings plus explicit ten absence dispositions.
2. The resolver’s accepted-mapping requirement cannot truthfully represent a source-native profile with mapping absent/proposed.
3. Technical completeness, failed-ingestion, explicit-absence, and semantic-readiness dispositions are not closed as independent candidate axes.
4. Existing v3 authority-derived membership and historical `corporate_release_item` representation lack an explicit precedence/reconciliation rule.
5. No accepted rights/quality/eligibility closure exists for the real tranche. The immediate successor may rehearse this shape only in disposable PostgreSQL; it may not create governed authority.

## Deferrable improvements

- Portfolio scaling from 19 to 311 acts.
- Accepted cross-company mappings beyond a later narrow pilot.
- Authoritative restatement classification.
- Cross-provider company identity.
- Public redistribution and remote delivery.
- KnowledgeForge adapter, InsightForge analysis, and BriefForge delivery.
- A separate package, deployment, or Forge.

## Mapping disposition

The next implementation uses source concepts and semantic slots as its descriptive surface, but keeps two vocabularies separate:

- `mapping_disposition`: current `accepted`, `proposed`, `deferred`, or `rejected`, plus candidate-level `absent` and a newly specified `deliberately_unmapped` bounded extension;
- `fact_resolution_status`: existing resolution outcomes including `conflict`.

`deliberately_unmapped` does **not** exist in the current schema and must not be represented by `rejected`, `deferred`, or fact `conflict`. Only accepted mapping may support comparative claims. No TASK-223 proposal is promoted by TASK-224 or by the rehearsal.

A later comparability pilot should select one decision-useful, tightly defined balance-sheet metric family—recommended candidate: **total assets and its unit/scope/period comparability conditions**—because the existing schema already seeds a proposed `CORP_TOTAL_ASSETS` concept. The pilot must not attempt all 32,381 slots and must separately govern concept acceptance, source mappings, reporting scope, units, periods, amendment status, and conflict/no-map outcomes.

## Rights disposition

No external rights research is necessary to decide TASK-224 because current evidence already requires the conservative state:

- access evidence does not imply redistribution;
- local/private analysis is the only contemplated output family;
- storage and derived-data use remain distinct assertions;
- redistribution is unresolved/not authorized;
- publication and remote delivery are not authorized.

Any later rights decision must cite official SEC evidence with source URL, access date, preserved text/digest, interpretation, decision owner, and separately enumerated permissions. Until then, private-analysis-only candidate work may progress but governed publication/delivery remains blocked.

## Minimum downstream-readiness contract

KnowledgeForge may consume only after a separately accepted contract provides:

1. contract/version and producer identity;
2. stable release ID, canonical payload digest, predecessor/supersession link;
3. immutable ordered membership and explicit absence/failure dispositions;
4. SEC and knowledge cutoffs;
5. scheme-qualified `sec:cik`, filer, reporting entity, and reporting scope without universal-company claims;
6. accession, form, period, amendment/restatement status;
7. document/occurrence/slot provenance and parser/normalization identities;
8. explicit mapping status and comparability profile;
9. technical, rights, semantic, quality, and eligibility states as separate fields;
10. allowed-use, redistribution, publication, and delivery permissions;
11. append-only revision semantics and consumer compatibility rules.

KnowledgeForge must verify hashes, preserve the release reference, treat CIK as SEC-scoped, and own reusable semantic identities, mappings-as-knowledge, claims, derivations, and epistemic lifecycle. It must not query or write MacroForge PostgreSQL directly.

## Exact inactive successor specification

Provisional identifier/title: **TASK-225 — Source-native Corporate Reporting private-analysis release-candidate admission contract and disposable rehearsal**.

Status: **INACTIVE — NOT AUTHORIZED BY TASK-224**.

### Objective

Implement the smallest bounded extension that can deterministically construct and validate a multi-item source-native private-analysis release candidate for the exact TASK-223 tranche while exposing mapping, amendment, absence, failure, rights, quality, and eligibility states independently.

### Exact input tranche

The input authority is exactly:

- ledger `artifacts/reports/task223-corporate-proof-tranche-ledger.json`, 24,050 bytes, serialized SHA-256 `6fe4a5ad05836a7e290e71297e4d6ab328232cbfd5fefa2a0476370250061c9c`, internal canonical `ledger_sha256` `d55e413cae29d8abef44a871a22205d0504076ace916b1c643399ab7fb1a12b2`;
- source manifest `artifacts/reports/sec-corporate-portfolio-v1-manifest-20260630.json`, 9,767,049 bytes, serialized SHA-256 `9cde110033fd3e8f22bedf768f01e7f90dd2c72784ad4f43172e5220ad9edf9f`, semantic identity `937056b9e903daa5e3550ed18cb1dff6d34bb1fbc49e3bb8e1f51a8d4420516a`;
- frozen accessions: `0000003570-24-000040`, `0000034088-24-000018`, `0000045012-24-000007`, `0000093410-24-000013`, `0000101778-24-000023`, `0000797468-24-000034`, `0000821189-24-000011`, `0000831259-24-000011`, `0000915913-24-000016`, `0000915913-24-000094`, `0000950170-24-006884`, `0001104659-21-062988`, `0001163165-24-000010`, `0001164727-24-000016`, `0001506307-24-000011`, `0001562762-23-000287`, `0001562762-25-000170`, `0001628280-24-005761`, `0001628280-24-020639`;
- frozen cessation-absence identities: `11f7dd0b7005939ae30099620f13dac40109655ecff05e524c7cd94fef54831a`, `3900bc3e7aa533a85f3a243b074e6c4e7566c0f6d7c9ddd8b42c949457e19ad7`, `5db0829ab2d66c574f655c6abe831e8b41341b6358fad3ff22471c06f83b5b46`, `61b6000e7df7e588169b50c934f919615ad19f5d10f058f9acb582a6ea2355f3`, `6defb1443dc7d4c3f42977df755231e6de633c7e489005a7dbb9f0e1a2a95d60`, `6f7749f6cfe5a025f72d722213adb45a52c3411bd87821013fbd7f4bc56728e3`, `91a625fc25d50c09161615c6d47e8f1f8d6d2fdc0050cbb29a5b5291405109fc`, `9dcd3fdc1b30b9b93684520d2fdcb1b9485ed78681d1d201c1b73ba093e132c2`, `c3a3828fae55a25abc4b4f9a54f1d06a2d14b6c6e4774c5d9ca3426e8baac18a`, `f5566b5e11e8aca91db46472c10087252c863f695581c785acaa96eb7519e5e6`.

Replay must account for the ledger’s 19 filing acts (17 originals, two amendments, 15 CIKs), all 147 authenticated document identities, 35,048 occurrences, 32,381 semantic slots, two proposed amendment links with restatement undetermined, and ten absences. No additional issuer, accession, document, filing, amendment, or absence may enter the candidate. Any hash or identity mismatch stops before replay.

### Authorized database boundary

Only uniquely named disposable databases matching `macroforge_task225_%`. Governed `macroforge` is read-only for before/after authentication. No production or governed rows survive. Any needed source replay uses the existing TASK-223 ingestion path and authenticated evidence; it is setup, not portfolio expansion.

### Required artifacts

- versioned source-native admission-contract specification;
- deterministic candidate manifest and fingerprint containing exact membership/dispositions but no redistributed provider body;
- disposable-database rehearsal report and complete table/count/fingerprint accounting;
- rollback/replay and two-fresh-database convergence evidence;
- explicit mechanism-precedence decision for authority-derived release bytes versus historical release/item views;
- gap/authority report proving zero governed mapping, rights, eligibility, release, reservation, completion, redistribution, or delivery delta.

### Permitted authority

- add bounded production contract/validation code, migration only if representability cannot be achieved by existing tables, and permanent authored tests;
- represent source-native mapping status without accepting a mapping;
- represent portfolio expected-filing absence separately from extraction failure;
- construct non-authoritative candidate bytes in disposable scope;
- replay the exact 19-filing tranche in disposable scope.

### Prohibited authority

No accepted real mapping/equivalence, canonical company identity, rights approval, redistribution, governed eligibility/release/membership/publication, remote delivery, SEC portfolio scaling, KnowledgeForge/InsightForge/BriefForge integration, production database write, or successor activation.

### Deterministic acceptance criteria

1. Exact input scope is 19 filings, 147 documents, 35,048 occurrences, 32,381 slots, two proposed amendment links, ten explicit cessation absences, with every item accounted.
2. Candidate identity is identical after exact replay and across two fresh disposable databases.
3. Mapping status is explicit for every released semantic surface; zero accepted mappings are created.
4. Expected-filing absence, extraction failure, nil/reporting state, fact-resolution conflict, and the newly specified deliberate mapping no-map disposition cannot alias.
5. Filer, reporting entity, scope, CIK, and universal identities cannot alias.
6. Source and knowledge cutoffs plus candidate/release revision clocks are independently represented.
7. Historical candidate versions are immutable; exact replay is no-op; conflict rolls back atomically.
8. Rights remain private-analysis-only candidate disposition, redistribution unresolved/not authorized, remote delivery false.
9. No governed row or publication operation changes; disposable databases are removed only under exact cleanup authority.
10. Focused contract, relational N+1, alias/mix-and-match, rollback/replay, two-database, lifecycle, rights-boundary, publication-denial, and ordinary repository tests pass under separately granted test authority.
11. Final exact bytes pass independent adversarial review and standard ProjectForge closeout.

### Release disposition

The output is a **release candidate**, not a governed release. A later separately authorized task must perform official rights adjudication and governed admission; another later task may publish after fresh authority. No publication or downstream delivery occurs in TASK-225.

## Likely sequence

1. Source-native private-analysis release-candidate contract and disposable rehearsal.
2. Rights evidence/admission decision and governed source-native release admission.
3. Narrow total-assets comparability pilot.
4. Governed local publication after all relevant axes pass.
5. KnowledgeForge contract and consumption after delivery rights permit it.
6. InsightForge analysis.
7. BriefForge presentation-package delivery.

Rights adjudication precedes governed publication, but it need not block contract/rehearsal work. Comparability follows source-native candidate construction because mapping every slot is neither necessary nor justified.
