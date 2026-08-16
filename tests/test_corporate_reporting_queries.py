"""TASK-221 RED contract: PostgreSQL is the only Corporate authority trust root.

Expected production API (intentionally absent before remediation A):

    CorporateAuthorityRef(root_id: UUID)
    PostgresCorporateAuthorityStore(database_url: str)
    release_as_of(*, authority: CorporateAuthorityRef,
                  store: PostgresCorporateAuthorityStore) -> Mapping[str, object]

The reference is only an identifier.  The store must resolve and validate the entire
canonical closure; no Filing/KnowledgeSnapshot/digest/payload supplied by a caller is
an authority.
"""
from dataclasses import replace
from datetime import datetime, timezone
from hashlib import sha256
import inspect
from pathlib import Path
import subprocess
from collections.abc import Iterator
import uuid

import pytest

import macroforge.corporate_reporting_queries as queries
from macroforge.corporate_reporting_queries import (
    AmbiguousSelection, FactAuthority, Filing, KnowledgeSnapshot, RevisionAuthority,
)

UTC = timezone.utc
ROOT = Path(__file__).resolve().parents[1]
MIGRATIONS = (
    ROOT / "db/migrations/001_v0_schema_foundation.sql",
    ROOT / "db/migrations/005_corporate_reporting_foundation.sql",
)
A0 = "0001104659-23-034448"


def _psql(database: str, sql: str) -> str:
    result = subprocess.run(
        ["psql", "-X", "-v", "ON_ERROR_STOP=1", "-At", "-d", database, "-c", sql],
        check=True, text=True, capture_output=True,
    )
    return result.stdout.strip()


@pytest.fixture(scope="module")
def canonical_authority_database() -> Iterator[tuple[str, str]]:
    """Migrate an isolated DB and persist a synthetic (never Gatos) authority root.

    The current 005 schema has no authority-root relation.  For RED, the persisted
    eligibility revision is the proposed root identifier; its FK closure includes
    cutoffs/snapshot members, policy, expected selection, parser selection/run,
    mapping and source/canonical concepts, filing manifest, quality checks and
    eligibility.  Resolution/conflict/rights/equivalence branches are required by
    the proposed resolver whenever selected facts use them.
    """
    database = f"macroforge_task221_query_red_{uuid.uuid4().hex[:12]}"
    subprocess.run(["createdb", database], check=True, capture_output=True, text=True)
    try:
        for migration in MIGRATIONS:
            subprocess.run(
                ["psql", "-X", "-v", "ON_ERROR_STOP=1", "-d", database, "-f", str(migration)],
                check=True, capture_output=True, text=True,
            )
        import hashlib, json
        evidence_path = Path("/tmp") / f"{database}-synthetic.htm"
        evidence_bytes = b"<html><body><ix:nonFraction>1</ix:nonFraction></body></html>\n"
        evidence_path.write_bytes(evidence_bytes)
        evidence_hash = hashlib.sha256(evidence_bytes).hexdigest()
        canonical = lambda value: json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
        source_manifest = hashlib.sha256(canonical([
            ["synthetic.htm", "primary", len(evidence_bytes), evidence_hash]
        ])).hexdigest()
        selection_material = {"selection_code": "task221-assets", "selection_version": "v1",
                              "scope_kind": "consolidated_registrant", "period_policy": {},
                              "applicability": {}, "rights_output_family": "private_analysis"}
        selection_sha = hashlib.sha256(canonical(selection_material)).hexdigest()
        expected_key = hashlib.sha256(canonical({"axis": "expected_selection", **selection_material})).hexdigest()
        parser_key = hashlib.sha256(canonical({"axis": "parser_selection", "accession": A0})).hexdigest()
        check_set = [{"check_id": "closure", "status": "passed", "evidence_sha256": "9" * 64}]
        quality_root = hashlib.sha256(canonical(check_set)).hexdigest()
        # The snapshot is assembled in two SQL phases; suspend only its deferred
        # aggregate check, then restore it after writing the genuinely recomputed root.
        _psql(database, "DROP TRIGGER trg_cr_snapshot_manifest ON corporate_reporting.knowledge_snapshot_member; "
                         "DROP TRIGGER trg_cr_immutable_knowledge_snapshot ON corporate_reporting.knowledge_snapshot;")
        root_output = _psql(database, f"""
WITH s AS (
 INSERT INTO meta.source(source_code,source_name) VALUES('TASK221-SYNTHETIC','TASK-221 synthetic authority') RETURNING source_id
), d AS (
 INSERT INTO meta.dataset_release(source_id,provider_dataset_code,release_key,raw_sha256)
 SELECT source_id,'SEC-SYNTHETIC','task221-r1',repeat('1',64) FROM s RETURNING dataset_release_id,source_id
), p AS (
 INSERT INTO meta.pipeline_run(run_key,source_id,dataset_release_id,pipeline_name,status)
 SELECT 'task221-synthetic',source_id,dataset_release_id,'task221-test','succeeded' FROM d RETURNING pipeline_run_id,dataset_release_id
), e AS (
 INSERT INTO corporate_reporting.reporting_entity(entity_kind) VALUES('registrant') RETURNING entity_id
), f AS (
 INSERT INTO corporate_reporting.filing_submission(dataset_release_id,filer_entity_id,accession,form_type,filed_date,accepted_at,report_period_end,primary_document_name,amendment_flag,source_manifest_sha256)
 SELECT p.dataset_release_id,e.entity_id,'0001104659-23-034448','10-K','2023-03-20','2023-03-20T16:07:02Z','2021-12-31','synthetic.htm',false,'{source_manifest}' FROM p,e RETURNING filing_id
), pr AS (
 INSERT INTO corporate_reporting.parser_run(pipeline_run_id,filing_id,parser_attempt_key,parser_contract,parser_version,source_manifest_sha256,resolution_policy_sha256,status,parser_output_sha256,recorded_at)
 SELECT p.pipeline_run_id,f.filing_id,'attempt-1','synthetic-xbrl-v1','1','{source_manifest}',repeat('3',64),'succeeded',repeat('4',64),'2023-07-01Z' FROM p,f RETURNING parser_run_id,filing_id,pipeline_run_id
), cc AS (
 INSERT INTO corporate_reporting.canonical_concept(canonical_code,label,value_kind,period_type,status)
 VALUES('TASK221_SYNTHETIC_ASSETS','Synthetic assets','numeric','instant','accepted') RETURNING canonical_concept_id
), kr_expected AS (
 INSERT INTO corporate_reporting.knowledge_revision(axis_type,object_key,pipeline_run_id,evidence_fingerprint,recorded_at)
 SELECT 'expected_selection','{expected_key}',pipeline_run_id,repeat('5',64),'2023-07-01Z' FROM pr RETURNING knowledge_revision_id,axis_type,object_key,pipeline_run_id
), expected AS (
 INSERT INTO corporate_reporting.expected_selection_revision(knowledge_revision_id,object_key,selection_code,selection_version,canonical_concept_id,scope_kind,period_policy,applicability_predicate,rights_output_family,selection_sha256,status,recorded_at)
 SELECT knowledge_revision_id,object_key,'task221-assets','v1',canonical_concept_id,'consolidated_registrant','{{}}','{{}}','private_analysis','{selection_sha}','accepted','2023-07-01Z' FROM kr_expected,cc RETURNING expected_selection_revision_id,knowledge_revision_id
), kr_parser AS (
 INSERT INTO corporate_reporting.knowledge_revision(axis_type,object_key,pipeline_run_id,evidence_fingerprint,recorded_at)
 SELECT 'parser_selection','{parser_key}',pipeline_run_id,repeat('7',64),'2023-07-01Z' FROM pr RETURNING knowledge_revision_id,axis_type,object_key
), parser_selection AS (
 INSERT INTO corporate_reporting.parser_run_selection_revision(knowledge_revision_id,object_key,filing_id,parser_run_id,status,rationale,recorded_at)
 SELECT k.knowledge_revision_id,k.object_key,pr.filing_id,pr.parser_run_id,'accepted','synthetic','2023-07-01Z' FROM kr_parser k,pr RETURNING knowledge_revision_id
), snap AS (
 INSERT INTO corporate_reporting.knowledge_snapshot(sec_cutoff,knowledge_cutoff,manifest_sha256,recorded_at)
 VALUES('2023-07-01Z','2023-08-01Z',repeat('8',64),'2023-08-01Z') RETURNING knowledge_snapshot_id
), members AS (
 INSERT INTO corporate_reporting.knowledge_snapshot_member(knowledge_snapshot_id,axis_type,object_key,knowledge_revision_id)
 SELECT snap.knowledge_snapshot_id,k.axis_type,k.object_key,k.knowledge_revision_id FROM snap,kr_expected k
 UNION ALL SELECT snap.knowledge_snapshot_id,k.axis_type,k.object_key,k.knowledge_revision_id FROM snap,kr_parser k
), quality AS (
 INSERT INTO meta.quality_check(pipeline_run_id,check_name,check_status,severity,observed_value,expected_value,details)
 SELECT pipeline_run_id,'closure','pass','error',1,1,'{{"evidence_sha256":"{'9' * 64}"}}' FROM pr
), kr_eligibility AS (
 INSERT INTO corporate_reporting.knowledge_revision(axis_type,object_key,pipeline_run_id,evidence_fingerprint,recorded_at)
 SELECT 'release_eligibility',corporate_reporting.canonical_sha256(jsonb_build_object('axis','release_eligibility','filing','{A0}','policy','private-analysis-v1','selection','{selection_sha}','snapshot',snap.knowledge_snapshot_id::text)),pipeline_run_id,'{quality_root}','2023-08-01Z' FROM pr,snap RETURNING knowledge_revision_id,object_key
)
INSERT INTO corporate_reporting.corporate_release_eligibility_revision(knowledge_revision_id,object_key,filing_id,expected_selection_revision_id,knowledge_snapshot_id,policy_id,status,reason_codes,source_manifest_sha256,quality_decision_sha256,recorded_at)
SELECT k.knowledge_revision_id,k.object_key,f.filing_id,expected.expected_selection_revision_id,snap.knowledge_snapshot_id,policy.policy_id,'eligible','[]','{source_manifest}','{quality_root}','2023-08-01Z'
FROM kr_eligibility k,f,expected,snap,corporate_reporting.corporate_release_policy policy
WHERE policy.policy_version='private-analysis-v1'
RETURNING eligibility_revision_id::text;
""")
        root_id = root_output.splitlines()[0]
        _psql(database, rf"""
DO $$
DECLARE f uuid; pr uuid; doc uuid; scope uuid; tax uuid; sc uuid; ctx uuid; unit_id uuid;
 occ uuid; interp uuid; slot uuid; kr uuid; snap uuid; cc uuid; expected uuid;
 slot_hash text; occurrence_hash text; context_hash text; unit_hash text; resolution_key text;
BEGIN
 SELECT filing_id INTO f FROM corporate_reporting.filing_submission WHERE accession='0001104659-23-034448';
 SELECT parser_run_id INTO pr FROM corporate_reporting.parser_run WHERE filing_id=f;
 SELECT knowledge_snapshot_id INTO snap FROM corporate_reporting.knowledge_snapshot;
 SELECT canonical_concept_id INTO cc FROM corporate_reporting.canonical_concept WHERE canonical_code='TASK221_SYNTHETIC_ASSETS';
 SELECT expected_selection_revision_id INTO expected FROM corporate_reporting.expected_selection_revision WHERE canonical_concept_id=cc;
 INSERT INTO corporate_reporting.filing_document(filing_id,document_name,document_role,source_url,media_type,byte_length,sha256,local_evidence_locator,archive_sequence)
 VALUES(f,'synthetic.htm','primary','https://example.invalid/synthetic.htm','text/html',{len(evidence_bytes)},'{evidence_hash}','{evidence_path}',1) RETURNING document_id INTO doc;
 INSERT INTO corporate_reporting.reporting_scope(filing_id,reporting_entity_id,scope_kind,scope_label,evidence_fingerprint)
 SELECT f,filer_entity_id,'consolidated_registrant','synthetic',repeat('1',64) FROM corporate_reporting.filing_submission WHERE filing_id=f RETURNING scope_id INTO scope;
 INSERT INTO corporate_reporting.taxonomy_set(parser_run_id,filing_id,entry_schema_document_id,dts_manifest_sha256,namespace_inventory,resolution_status)
 VALUES(pr,f,doc,repeat('a',64),'["urn:task221"]','resolved') RETURNING taxonomy_set_id INTO tax;
 INSERT INTO corporate_reporting.source_concept(parser_run_id,filing_id,taxonomy_set_id,namespace_uri,local_name,declaration_status,declaration_document_id,declaration_sha256,data_type_qname,period_type,extension_flag)
 VALUES(pr,f,tax,'urn:task221','Assets','declared',doc,'{evidence_hash}','xbrli:monetaryItemType','instant',false) RETURNING source_concept_id INTO sc;
 context_hash := corporate_reporting.canonical_sha256(jsonb_build_array('sec','0000000000',jsonb_build_array('instant','2021-12-31'),'[]'::jsonb));
 INSERT INTO corporate_reporting.xbrl_context(parser_run_id,filing_id,source_context_id,reporting_scope_id,entity_scheme,entity_value,period_kind,instant_date,raw_xml_sha256,semantic_context_sha256)
 VALUES(pr,f,'C1',scope,'sec','0000000000','instant','2021-12-31',repeat('b',64),context_hash) RETURNING context_id INTO ctx;
 unit_hash := corporate_reporting.canonical_sha256(jsonb_build_object('denominator','[]'::jsonb,'numerator','["USD"]'::jsonb));
 INSERT INTO corporate_reporting.xbrl_unit_semantics(parser_run_id,filing_id,numerator_measures,denominator_measures,semantic_unit_sha256)
 VALUES(pr,f,'["USD"]','[]',unit_hash) RETURNING unit_semantics_id INTO unit_id;
 INSERT INTO corporate_reporting.xbrl_source_unit_alias(parser_run_id,filing_id,source_unit_id,unit_semantics_id,raw_xml_sha256)
 VALUES(pr,f,'USD',unit_id,repeat('c',64));
 occurrence_hash := corporate_reporting.canonical_sha256(jsonb_build_object('concept','task:Assets','context','C1','decimals','0','lang',NULL,'nil',false,'ordinal',1,'precision',NULL,'unit','USD','value','1'));
 INSERT INTO corporate_reporting.fact_occurrence(filing_id,document_id,source_ordinal,source_fact_id,source_concept_qname,source_context_ref,source_unit_ref,lexical_value,nil_flag,decimals,occurrence_sha256)
 VALUES(f,doc,1,'F1','task:Assets','C1','USD','1',false,'0',occurrence_hash) RETURNING fact_occurrence_id INTO occ;
 INSERT INTO corporate_reporting.fact_occurrence_interpretation(parser_run_id,fact_occurrence_id,filing_id,source_concept_id,context_id,source_unit_alias_id,normalized_numeric)
 SELECT pr,occ,f,sc,ctx,source_unit_alias_id,1 FROM corporate_reporting.xbrl_source_unit_alias WHERE parser_run_id=pr RETURNING fact_occurrence_interpretation_id INTO interp;
 slot_hash := corporate_reporting.canonical_sha256(jsonb_build_object('accession','0001104659-23-034448','correspondence',jsonb_build_array('{{urn:task221}}Assets',corporate_reporting.context_payload(ctx),unit_hash,NULL),'dts',repeat('a',64)));
 INSERT INTO corporate_reporting.fact_semantic_slot(parser_run_id,filing_id,reporting_scope_id,source_concept_id,semantic_context_sha256,semantic_unit_sha256,slot_sha256)
 VALUES(pr,f,scope,sc,context_hash,unit_hash,slot_hash) RETURNING fact_slot_id INTO slot;
 INSERT INTO corporate_reporting.fact_slot_occurrence(parser_run_id,fact_slot_id,fact_occurrence_interpretation_id,fact_occurrence_id,filing_id)
 VALUES(pr,slot,interp,occ,f);
 resolution_key := corporate_reporting.canonical_sha256(jsonb_build_object('accession','{A0}','axis','concept_mapping','scope','consolidated_registrant','source_concept',sc::text));
 INSERT INTO corporate_reporting.knowledge_revision(axis_type,object_key,pipeline_run_id,evidence_fingerprint,recorded_at)
 SELECT 'concept_mapping',resolution_key,pipeline_run_id,repeat('d',64),'2023-07-01Z' FROM corporate_reporting.parser_run WHERE parser_run_id=pr RETURNING knowledge_revision_id INTO kr;
 INSERT INTO corporate_reporting.concept_mapping_revision(knowledge_revision_id,object_key,source_concept_id,canonical_concept_id,reporting_scope_kind,status,rationale,evidence_fingerprint,recorded_at)
 VALUES(kr,resolution_key,sc,cc,'consolidated_registrant','accepted','synthetic',repeat('d',64),'2023-07-01Z');
 INSERT INTO corporate_reporting.knowledge_snapshot_member VALUES(snap,'concept_mapping',resolution_key,kr);
 resolution_key := corporate_reporting.canonical_sha256(jsonb_build_object('accession','0001104659-23-034448','axis','fact_resolution','parser_output',repeat('4',64),'parser_run',pr::text,'slot',slot_hash));
 INSERT INTO corporate_reporting.knowledge_revision(axis_type,object_key,pipeline_run_id,evidence_fingerprint,recorded_at)
 SELECT 'fact_resolution',resolution_key,pipeline_run_id,repeat('e',64),'2023-07-01Z' FROM corporate_reporting.parser_run WHERE parser_run_id=pr RETURNING knowledge_revision_id INTO kr;
 INSERT INTO corporate_reporting.fact_resolution_revision(knowledge_revision_id,object_key,parser_run_id,filing_id,fact_slot_id,selected_occurrence_id,status,value_fingerprint,reason_code,recorded_at)
 VALUES(kr,resolution_key,pr,f,slot,occ,'accepted_identical',occurrence_hash,'identical','2023-07-01Z');
 INSERT INTO corporate_reporting.knowledge_snapshot_member VALUES(snap,'fact_resolution',resolution_key,kr);
 resolution_key := corporate_reporting.canonical_sha256(jsonb_build_object('axis','corporate_rights','filing','{A0}','output_family','private_analysis'));
 INSERT INTO corporate_reporting.knowledge_revision(axis_type,object_key,pipeline_run_id,evidence_fingerprint,recorded_at)
 SELECT 'corporate_rights',resolution_key,pipeline_run_id,repeat('f',64),'2023-07-01Z' FROM corporate_reporting.parser_run WHERE parser_run_id=pr RETURNING knowledge_revision_id INTO kr;
 INSERT INTO corporate_reporting.corporate_rights_revision(knowledge_revision_id,object_key,filing_id,output_family,decision_status,redistribution_status,remote_delivery_enabled,evidence_fingerprint,recorded_at)
 VALUES(kr,resolution_key,f,'private_analysis','accepted','unresolved',false,repeat('f',64),'2023-07-01Z');
 INSERT INTO corporate_reporting.knowledge_snapshot_member VALUES(snap,'corporate_rights',resolution_key,kr);
 resolution_key := corporate_reporting.canonical_sha256(jsonb_build_object('axis','corporate_quality_gate','check_set_sha256','{quality_root}','filing','{A0}'));
 INSERT INTO corporate_reporting.knowledge_revision(axis_type,object_key,pipeline_run_id,evidence_fingerprint,recorded_at)
 SELECT 'corporate_quality_gate',resolution_key,pipeline_run_id,'{quality_root}','2023-07-01Z' FROM corporate_reporting.parser_run WHERE parser_run_id=pr RETURNING knowledge_revision_id INTO kr;
 INSERT INTO corporate_reporting.corporate_quality_gate_revision(knowledge_revision_id,object_key,filing_id,check_set,check_set_sha256,decision_status,recorded_at)
 VALUES(kr,resolution_key,f,'[{{"check_id":"closure","status":"passed","evidence_sha256":"{'9' * 64}"}}]','{quality_root}','accepted','2023-07-01Z');
 INSERT INTO corporate_reporting.knowledge_snapshot_member VALUES(snap,'corporate_quality_gate',resolution_key,kr);
END $$;
""")
        _psql(database, """
          UPDATE corporate_reporting.knowledge_snapshot s SET manifest_sha256=(
            SELECT corporate_reporting.canonical_sha256(jsonb_agg(
              jsonb_build_array(m.axis_type,m.object_key,m.knowledge_revision_id::text)
              ORDER BY m.axis_type,m.object_key,m.knowledge_revision_id::text))
            FROM corporate_reporting.knowledge_snapshot_member m
            WHERE m.knowledge_snapshot_id=s.knowledge_snapshot_id);
          CREATE CONSTRAINT TRIGGER trg_cr_snapshot_manifest AFTER INSERT OR UPDATE OR DELETE
            ON corporate_reporting.knowledge_snapshot_member DEFERRABLE INITIALLY DEFERRED
            FOR EACH ROW EXECUTE FUNCTION corporate_reporting.check_snapshot_manifest();
          CREATE TRIGGER trg_cr_immutable_knowledge_snapshot BEFORE UPDATE OR DELETE
            ON corporate_reporting.knowledge_snapshot FOR EACH ROW
            EXECUTE FUNCTION corporate_reporting.reject_admitted_update();
        """)
        assert _psql(database, "SELECT count(*) FROM corporate_reporting.knowledge_snapshot_member") == "6"
        yield database, root_id
    finally:
        subprocess.run(["dropdb", "--if-exists", database], check=True, capture_output=True, text=True)


def _clone_authority_database(source: str) -> str:
    clone = f"macroforge_task221_mutation_{uuid.uuid4().hex[:12]}"
    subprocess.run(["createdb", "-T", source, clone], check=True, capture_output=True, text=True)
    return clone


@pytest.mark.parametrize(
    ("mutation", "message"),
    (
        ("DROP TRIGGER trg_cr_immutable_corporate_release_eligibility_revision ON corporate_reporting.corporate_release_eligibility_revision; "
         "UPDATE corporate_reporting.corporate_release_eligibility_revision SET quality_decision_sha256=repeat('1',64)", "quality"),
        ("DROP TRIGGER trg_cr_immutable_knowledge_snapshot ON corporate_reporting.knowledge_snapshot; "
         "UPDATE corporate_reporting.knowledge_snapshot SET manifest_sha256=repeat('8',64)", "manifest"),
        ("DROP TRIGGER trg_cr_immutable_knowledge_snapshot ON corporate_reporting.knowledge_snapshot; "
         "UPDATE corporate_reporting.knowledge_snapshot SET knowledge_cutoff='2023-06-01Z'", "future|missing"),
        ("DROP TRIGGER trg_cr_immutable_parser_run ON corporate_reporting.parser_run; "
         "UPDATE corporate_reporting.parser_run SET source_manifest_sha256=repeat('2',64)", "source manifest"),
    ),
)
def test_recomputed_quality_snapshot_cutoff_and_source_roots_fail_closed(
    canonical_authority_database, mutation: str, message: str,
) -> None:
    source, root_id = canonical_authority_database
    database = _clone_authority_database(source)
    try:
        _psql(database, mutation)
        store = queries.PostgresCorporateAuthorityStore(database)
        with pytest.raises(AmbiguousSelection, match=message):
            store.resolve(queries.CorporateAuthorityRef(root_id))
    finally:
        subprocess.run(["dropdb", "--if-exists", database], check=True, capture_output=True, text=True)


def test_wrong_authority_object_key_and_selection_digest_inserts_are_rejected(
    canonical_authority_database,
) -> None:
    database, _ = canonical_authority_database
    statements = (
        """BEGIN; INSERT INTO corporate_reporting.knowledge_revision(axis_type,object_key,pipeline_run_id,evidence_fingerprint)
          SELECT 'parser_selection',repeat('1',64),pipeline_run_id,repeat('1',64) FROM corporate_reporting.parser_run LIMIT 1;
          INSERT INTO corporate_reporting.parser_run_selection_revision(knowledge_revision_id,object_key,filing_id,parser_run_id,status,rationale)
          SELECT knowledge_revision_id,object_key,p.filing_id,p.parser_run_id,'accepted','wrong key'
          FROM corporate_reporting.knowledge_revision k,corporate_reporting.parser_run p
          WHERE k.axis_type='parser_selection' AND k.object_key=repeat('1',64); COMMIT;""",
        """BEGIN; INSERT INTO corporate_reporting.knowledge_revision(axis_type,object_key,pipeline_run_id,evidence_fingerprint)
          SELECT 'expected_selection',repeat('1',64),pipeline_run_id,repeat('1',64) FROM corporate_reporting.parser_run LIMIT 1;
          INSERT INTO corporate_reporting.expected_selection_revision(knowledge_revision_id,object_key,selection_code,selection_version,canonical_concept_id,scope_kind,period_policy,applicability_predicate,rights_output_family,selection_sha256,status)
          SELECT k.knowledge_revision_id,k.object_key,'wrong','v1',canonical_concept_id,'consolidated_registrant','{}','{}','private_analysis',repeat('1',64),'accepted'
          FROM corporate_reporting.knowledge_revision k,corporate_reporting.canonical_concept
          WHERE k.axis_type='expected_selection' AND k.object_key=repeat('1',64) LIMIT 1; COMMIT;""",
        """BEGIN; INSERT INTO corporate_reporting.knowledge_revision(axis_type,object_key,pipeline_run_id,evidence_fingerprint)
          SELECT 'corporate_rights',repeat('1',64),pipeline_run_id,repeat('1',64) FROM corporate_reporting.parser_run LIMIT 1;
          INSERT INTO corporate_reporting.corporate_rights_revision(knowledge_revision_id,object_key,filing_id,output_family,decision_status,redistribution_status,remote_delivery_enabled,evidence_fingerprint)
          SELECT k.knowledge_revision_id,k.object_key,p.filing_id,'private_analysis','accepted','unresolved',false,repeat('1',64)
          FROM corporate_reporting.knowledge_revision k,corporate_reporting.parser_run p
          WHERE k.axis_type='corporate_rights' AND k.object_key=repeat('1',64) LIMIT 1; COMMIT;""",
    )
    for statement in statements:
        with pytest.raises(subprocess.CalledProcessError):
            _psql(database, statement)


def test_optional_accepted_relationship_and_equivalence_close_and_detached_member_fails(
    canonical_authority_database,
) -> None:
    source, root_id = canonical_authority_database
    database = _clone_authority_database(source)
    try:
        _psql(database, rf"""
          DROP TRIGGER trg_cr_snapshot_manifest ON corporate_reporting.knowledge_snapshot_member;
          DROP TRIGGER trg_cr_immutable_knowledge_snapshot ON corporate_reporting.knowledge_snapshot;
          DO $$ DECLARE selected uuid; predecessor uuid; predecessor_release uuid; pipeline uuid; doc uuid; left_sc uuid; right_sc uuid;
            tax uuid; snap uuid; key text; kr uuid;
          BEGIN
            SELECT f.filing_id,p.pipeline_run_id,d.document_id INTO selected,pipeline,doc
            FROM corporate_reporting.filing_submission f
            JOIN corporate_reporting.parser_run p USING(filing_id)
            JOIN corporate_reporting.filing_document d USING(filing_id) WHERE f.accession='{A0}' LIMIT 1;
            SELECT knowledge_snapshot_id INTO snap FROM corporate_reporting.knowledge_snapshot;
            INSERT INTO meta.dataset_release(source_id,provider_dataset_code,release_key,raw_sha256)
            SELECT r.source_id,'SEC-SYNTHETIC','task221-predecessor',repeat('1',64)
            FROM meta.dataset_release r JOIN corporate_reporting.filing_submission f
              ON f.dataset_release_id=r.dataset_release_id WHERE f.filing_id=selected
            RETURNING dataset_release_id INTO predecessor_release;
            INSERT INTO corporate_reporting.filing_submission(dataset_release_id,filer_entity_id,accession,form_type,filed_date,
              accepted_at,report_period_end,primary_document_name,amendment_flag,source_manifest_sha256)
            SELECT predecessor_release,filer_entity_id,'0001104659-23-000001','10-K','2023-03-01','2023-03-01Z',
              report_period_end,'predecessor.htm',false,repeat('1',64)
            FROM corporate_reporting.filing_submission WHERE filing_id=selected RETURNING filing_id INTO predecessor;
            key:=corporate_reporting.canonical_sha256(jsonb_build_object('axis','filing_relationship',
              'predecessor','0001104659-23-000001','successor','{A0}','type','restates'));
            INSERT INTO corporate_reporting.knowledge_revision(axis_type,object_key,pipeline_run_id,evidence_fingerprint,recorded_at)
              VALUES('filing_relationship',key,pipeline,repeat('1',64),'2023-07-01Z') RETURNING knowledge_revision_id INTO kr;
            INSERT INTO corporate_reporting.filing_relationship_revision(knowledge_revision_id,object_key,
              predecessor_filing_id,successor_filing_id,relationship_type,evidence_document_id,
              evidence_excerpt_fingerprint,assertion_status,recorded_at)
              VALUES(kr,key,predecessor,selected,'restates',doc,repeat('1',64),'accepted','2023-07-01Z');
            INSERT INTO corporate_reporting.knowledge_snapshot_member VALUES(snap,'filing_relationship',key,kr);
            SELECT source_concept_id,taxonomy_set_id INTO left_sc,tax FROM corporate_reporting.source_concept LIMIT 1;
            INSERT INTO corporate_reporting.source_concept(parser_run_id,filing_id,taxonomy_set_id,namespace_uri,local_name,
              declaration_status,declaration_document_id,declaration_sha256,data_type_qname,period_type,extension_flag)
            SELECT parser_run_id,filing_id,taxonomy_set_id,namespace_uri,'AssetsEquivalent','declared',
              declaration_document_id,declaration_sha256,data_type_qname,period_type,false
            FROM corporate_reporting.source_concept WHERE source_concept_id=left_sc RETURNING source_concept_id INTO right_sc;
            key:=corporate_reporting.canonical_sha256(jsonb_build_object('axis','concept_equivalence',
              'left',left_sc::text,'right',right_sc::text));
            INSERT INTO corporate_reporting.knowledge_revision(axis_type,object_key,pipeline_run_id,evidence_fingerprint,recorded_at)
              VALUES('concept_equivalence',key,pipeline,repeat('2',64),'2023-07-01Z') RETURNING knowledge_revision_id INTO kr;
            INSERT INTO corporate_reporting.source_concept_equivalence_revision(knowledge_revision_id,object_key,
              left_source_concept_id,right_source_concept_id,status,scope,rationale,evidence_fingerprint,recorded_at)
              VALUES(kr,key,left_sc,right_sc,'accepted','synthetic-chain','synthetic accepted evidence',repeat('2',64),'2023-07-01Z');
            INSERT INTO corporate_reporting.knowledge_snapshot_member VALUES(snap,'concept_equivalence',key,kr);
          END $$;
          UPDATE corporate_reporting.knowledge_snapshot s SET manifest_sha256=(SELECT corporate_reporting.canonical_sha256(
            jsonb_agg(jsonb_build_array(m.axis_type,m.object_key,m.knowledge_revision_id::text)
              ORDER BY m.axis_type,m.object_key,m.knowledge_revision_id::text))
            FROM corporate_reporting.knowledge_snapshot_member m WHERE m.knowledge_snapshot_id=s.knowledge_snapshot_id);
        """)
        store = queries.PostgresCorporateAuthorityStore(database)
        closed = store.resolve(queries.CorporateAuthorityRef(root_id))
        assert len(closed["relationships"]) == len(closed["equivalences"]) == 1
        _psql(database, "DROP TRIGGER trg_cr_immutable_filing_relationship_revision ON corporate_reporting.filing_relationship_revision; "
                        "UPDATE corporate_reporting.filing_relationship_revision SET assertion_status='proposed'")
        with pytest.raises(AmbiguousSelection, match="relationship"):
            store.resolve(queries.CorporateAuthorityRef(root_id))
    finally:
        subprocess.run(["dropdb", "--if-exists", database], check=True, capture_output=True, text=True)


def _legacy_release_inputs() -> tuple[list[Filing], KnowledgeSnapshot]:
    authority = FactAuthority("parser-key", "resolution-key", "mapping-key", "expected-key", "concept-id", "dts")
    filing = Filing(
        A0, "0001517006", "2021-12-31", datetime(2023, 3, 20, tzinfo=UTC),
        {"assets": "1"}, fact_authority={"assets": authority},
    )
    rows = tuple(
        RevisionAuthority(axis, key, "accepted-revision", status, datetime(2023, 3, 21, tzinfo=UTC))
        for axis, key, status in (
            ("parser_selection", "parser-key", "accepted"),
            ("fact_resolution", "resolution-key", "accepted_identical"),
            ("concept_mapping", "mapping-key", "accepted"),
            ("expected_selection", "expected-key", "accepted"),
        )
    )
    return [filing], KnowledgeSnapshot("caller-snapshot", datetime(2023, 8, 1, tzinfo=UTC), rows)


def test_expected_api_is_postgres_store_plus_opaque_authority_ref(canonical_authority_database) -> None:
    database, root_id = canonical_authority_database
    assert hasattr(queries, "CorporateAuthorityRef"), "missing proposed CorporateAuthorityRef API"
    assert hasattr(queries, "PostgresCorporateAuthorityStore"), "missing proposed PostgreSQL authority resolver"
    ref = queries.CorporateAuthorityRef(root_id)  # type: ignore[attr-defined]
    store = queries.PostgresCorporateAuthorityStore(database)  # type: ignore[attr-defined]
    result = queries.release_as_of(authority=ref, store=store)  # type: ignore[call-arg]
    assert result["authority_root_id"] == root_id


def test_database_authority_is_a_complete_non_metadata_fact_closure(canonical_authority_database) -> None:
    """An eligibility row alone must never be mistaken for release authority."""
    database, root_id = canonical_authority_database
    store = queries.PostgresCorporateAuthorityStore(database)
    closed = store.resolve(queries.CorporateAuthorityRef(root_id))
    assert closed["rights"]["status"] == "accepted"
    assert closed["rights"]["redistribution_status"] == "unresolved"
    assert closed["rights"]["remote_delivery_enabled"] is False
    assert closed["quality"]["check_set"] == [
        {"check_id": "closure", "status": "passed", "evidence_sha256": "9" * 64}
    ]
    assert closed["relationships"] == [] and closed["equivalences"] == []
    assert closed["items"][0]["value"] == "1"
    assert closed["items"][0]["canonical_concept"] == "TASK221_SYNTHETIC_ASSETS"
    assert len(closed["documents"]) == 1


def _publication_counts(database: str) -> tuple[str, str]:
    return (
        _psql(database, "SELECT count(*) FROM corporate_reporting.corporate_publication_reservation"),
        _psql(database, "SELECT count(*) FROM corporate_reporting.corporate_publication_completion"),
    )


def test_concrete_store_exposes_no_standalone_reservation_transition(
    canonical_authority_database, tmp_path: Path,
) -> None:
    from macroforge.corporate_reporting_release import build_private_release

    source, root_id = canonical_authority_database
    database = _clone_authority_database(source)
    try:
        ref = queries.CorporateAuthorityRef(root_id)
        store = queries.PostgresCorporateAuthorityStore(database)
        release = build_private_release(authority=ref, store=store)
        target = tmp_path / "direct-reservation.json"
        transition = getattr(store, "record_publication", None)
        if callable(transition):
            transition(ref, release.release_id, str(target), sha256(release.payload).hexdigest())
        assert not callable(transition), "concrete store exposes standalone reservation authority"
        assert _publication_counts(database) == ("0", "0")
        assert list(tmp_path.iterdir()) == []
    finally:
        subprocess.run(["dropdb", "--if-exists", database], check=True, capture_output=True, text=True)


def test_concrete_store_exposes_no_generic_sql_lifecycle_writer(
    canonical_authority_database, tmp_path: Path,
) -> None:
    source, root_id = canonical_authority_database
    database = _clone_authority_database(source)
    try:
        store = queries.PostgresCorporateAuthorityStore(database)
        generic_sql = getattr(store, "_sql", None)
        if callable(generic_sql):
            generic_sql(
                "INSERT INTO corporate_reporting.corporate_publication_reservation"
                "(root_id,release_sha256,target,target_sha256) VALUES"
                f"('{root_id}'::uuid,'{'a' * 64}','{tmp_path / 'forged.json'}','{'b' * 64}');"
            )
        assert not callable(generic_sql), "concrete store exposes an arbitrary lifecycle SQL writer"
        assert _publication_counts(database) == ("0", "0")
        assert list(tmp_path.iterdir()) == []
    finally:
        subprocess.run(["dropdb", "--if-exists", database], check=True, capture_output=True, text=True)


def test_concrete_store_cannot_complete_an_existing_pending_reservation(
    canonical_authority_database, tmp_path: Path,
) -> None:
    source, root_id = canonical_authority_database
    database = _clone_authority_database(source)
    try:
        target = tmp_path / "never-installed.json"
        _psql(
            database,
            "INSERT INTO corporate_reporting.corporate_publication_reservation"
            "(root_id,release_sha256,target,target_sha256) VALUES"
            f"('{root_id}'::uuid,'{'a' * 64}','{target}','{'b' * 64}')",
        )
        store = queries.PostgresCorporateAuthorityStore(database)
        transition = getattr(store, "complete_publication", None)
        if callable(transition):
            transition(queries.CorporateAuthorityRef(root_id))
        assert not callable(transition), "concrete store exposes standalone completion authority"
        assert _publication_counts(database) == ("1", "0")
        assert _psql(
            database,
            "SELECT status FROM corporate_reporting.corporate_publication_authority"
            f" WHERE root_id='{root_id}'::uuid",
        ) == "reserved"
        assert list(tmp_path.iterdir()) == []
    finally:
        subprocess.run(["dropdb", "--if-exists", database], check=True, capture_output=True, text=True)


def test_database_build_and_publication_are_root_bound_idempotent_and_failure_safe(
    canonical_authority_database, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    from macroforge.corporate_reporting_release import (
        EligibilityError, ImmutableReleaseConflict, build_private_release, publish_database_anchored,
        publish_local_immutable,
    )
    import macroforge.corporate_reporting_release as publication

    database, root_id = canonical_authority_database
    ref = queries.CorporateAuthorityRef(root_id)
    store = queries.PostgresCorporateAuthorityStore(database)
    release = build_private_release(authority=ref, store=store)
    envelope = __import__("json").loads(release.payload)
    assert envelope["items"][0]["value"] == "1"
    assert envelope["items"][0]["mapping"]["source_qname"] == "{urn:task221}Assets"
    target = tmp_path / "private-release.json"
    conflict = tmp_path / "preexisting-conflict.json"
    conflict.write_bytes(b"different\n")
    with pytest.raises(ImmutableReleaseConflict, match="different bytes"):
        publish_database_anchored(authority=ref, store=store, target=conflict)
    assert _psql(database, "SELECT count(*) FROM corporate_reporting.corporate_publication_reservation") == "0"
    assert _psql(database, "SELECT count(*) FROM corporate_reporting.corporate_publication_completion") == "0"

    real_link = publication.os.link
    monkeypatch.setattr(
        publication.os, "link",
        lambda *_: (_ for _ in ()).throw(OSError("synthetic install failure")),
    )
    with pytest.raises(OSError, match="synthetic install failure"):
        publish_database_anchored(authority=ref, store=store, target=target)
    assert not target.exists()
    assert not (tmp_path / ".corporate-publication-status.jsonl").exists()
    assert _psql(database, "SELECT count(*) FROM corporate_reporting.corporate_publication_reservation") == "1"
    assert _psql(database, "SELECT count(*) FROM corporate_reporting.corporate_publication_completion") == "0"
    with pytest.raises((TypeError, EligibilityError), match="authority|database|disabled|governed"):
        publish_local_immutable(target, release)
    assert not target.exists()

    monkeypatch.setattr(publication.os, "link", real_link)
    real_fsync = publication.os.fsync

    def fail_directory_fsync(fd: int) -> None:
        import stat
        if stat.S_ISDIR(publication.os.fstat(fd).st_mode):
            raise OSError("synthetic directory durability failure")
        real_fsync(fd)

    monkeypatch.setattr(publication.os, "fsync", fail_directory_fsync)
    with pytest.raises(OSError, match="synthetic directory durability failure"):
        publish_database_anchored(authority=ref, store=store, target=target)
    assert target.read_bytes() == release.payload
    assert (tmp_path / ".corporate-publication-status.jsonl").exists()
    assert _psql(database, "SELECT count(*) FROM corporate_reporting.corporate_publication_reservation") == "1"
    assert _psql(database, "SELECT count(*) FROM corporate_reporting.corporate_publication_completion") == "0"

    monkeypatch.setattr(publication.os, "fsync", real_fsync)
    first = publish_database_anchored(authority=ref, store=store, target=target)
    second = publish_database_anchored(authority=ref, store=store, target=target)
    assert first == second
    assert target.read_bytes() == release.payload
    status_log = tmp_path / ".corporate-publication-status.jsonl"
    statuses = [row["status"] for row in map(__import__("json").loads, status_log.read_text().splitlines())]
    assert statuses == ["published", "identical", "identical"]
    assert _psql(database, "SELECT count(*) FROM corporate_reporting.corporate_publication_reservation") == "1"
    assert _psql(database, "SELECT count(*) FROM corporate_reporting.corporate_publication_completion") == "1"
    with pytest.raises((AmbiguousSelection, ImmutableReleaseConflict), match="distinct|already|different"):
        publish_database_anchored(
            authority=ref, store=store, target=tmp_path / "other.json",
        )
    assert not (tmp_path / "other.json").exists()
    assert _psql(database, "SELECT count(*) FROM corporate_reporting.corporate_publication_reservation") == "1"
    assert _psql(database, "SELECT count(*) FROM corporate_reporting.corporate_publication_completion") == "1"


@pytest.mark.parametrize("attack", ("fabricated", "copied", "deserialized", "different_semantics"))
def test_caller_release_bytes_cannot_enter_any_governed_publication_interface(
    canonical_authority_database, tmp_path: Path, attack: str,
) -> None:
    import json
    from hashlib import sha256
    from macroforge.corporate_reporting_release import CorporateRelease, publish_database_anchored

    database, root_id = canonical_authority_database
    ref = queries.CorporateAuthorityRef(root_id)
    store = queries.PostgresCorporateAuthorityStore(database)
    body = {"schema": "fabricated", "authority_root_id": root_id, "meaning": attack}
    release_id = sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    payload = json.dumps({**body, "release_id": release_id}, sort_keys=True, separators=(",", ":")).encode() + b"\n"
    supplied = CorporateRelease(release_id, payload, "private_analysis")
    target = tmp_path / f"attack-{attack}.json"
    before = (_psql(database, "SELECT count(*) FROM corporate_reporting.corporate_publication_reservation"),
              _psql(database, "SELECT count(*) FROM corporate_reporting.corporate_publication_completion"))
    with pytest.raises(TypeError, match="release|unexpected keyword"):
        publish_database_anchored(authority=ref, store=store, target=target, release=supplied)
    assert not target.exists()
    assert not (tmp_path / ".corporate-publication-status.jsonl").exists()
    assert before == (
        _psql(database, "SELECT count(*) FROM corporate_reporting.corporate_publication_reservation"),
        _psql(database, "SELECT count(*) FROM corporate_reporting.corporate_publication_completion"),
    )


@pytest.mark.parametrize("authority", (object(), queries.CorporateAuthorityRef(uuid.uuid4())))
def test_synthetic_forged_or_nonexistent_authority_cannot_publish(
    canonical_authority_database, tmp_path: Path, authority: object,
) -> None:
    from macroforge.corporate_reporting_release import publish_database_anchored

    database, _ = canonical_authority_database
    store = queries.PostgresCorporateAuthorityStore(database)
    target = tmp_path / f"forged-{uuid.uuid4().hex}.json"
    before = (_psql(database, "SELECT count(*) FROM corporate_reporting.corporate_publication_reservation"),
              _psql(database, "SELECT count(*) FROM corporate_reporting.corporate_publication_completion"))
    with pytest.raises((TypeError, AmbiguousSelection), match="authority|database|root|resolution"):
        publish_database_anchored(authority=authority, store=store, target=target)
    assert not target.exists()
    assert before == (
        _psql(database, "SELECT count(*) FROM corporate_reporting.corporate_publication_reservation"),
        _psql(database, "SELECT count(*) FROM corporate_reporting.corporate_publication_completion"),
    )


def test_release_as_of_has_no_authority_free_or_caller_payload_signature() -> None:
    parameters = inspect.signature(queries.release_as_of).parameters
    assert tuple(parameters) == ("authority", "store")
    assert parameters["authority"].kind is inspect.Parameter.KEYWORD_ONLY


def test_legacy_authority_free_release_path_is_closed() -> None:
    filings, snapshot = _legacy_release_inputs()
    with pytest.raises((TypeError, AmbiguousSelection), match="authority|store|unexpected|positional"):
        queries.release_as_of(
            filings, "0001517006", "2021-12-31", {"assets"},
            datetime(2023, 7, 1, tzinfo=UTC), snapshot,
        )


@pytest.mark.parametrize("axis", ("concept_mapping", "filing_relationship", "fact_resolution", "fact_semantic_slot", "source_concept"))
def test_accepted_key_with_detached_different_payload_cannot_authorize(axis: str) -> None:
    """A key/status pair never authenticates mapping/edge/resolution/slot/concept payload."""
    filings, snapshot = _legacy_release_inputs()
    # Replace (rather than duplicate) any matching terminal: the accepted key is
    # unchanged but the detached revision/payload identity differs.  Unused axes
    # are also injected because complete closure must authenticate them, not ignore
    # caller-supplied relationship/slot/concept material.
    forged = RevisionAuthority(axis, "mapping-key", f"detached-{axis}-payload", "accepted", datetime(2023, 3, 21, tzinfo=UTC))
    terminals = tuple(
        forged if row.axis == axis and row.object_key == "mapping-key" else row
        for row in snapshot.terminals
    )
    if forged not in terminals:
        terminals += (forged,)
    caller_snapshot = replace(snapshot, terminals=terminals)
    with pytest.raises((TypeError, AmbiguousSelection), match="authority|store|detached|database|positional"):
        queries.release_as_of(
            filings, "0001517006", "2021-12-31", {"assets"},
            datetime(2023, 7, 1, tzinfo=UTC), caller_snapshot,
        )
