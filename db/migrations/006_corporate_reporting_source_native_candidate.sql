-- TASK-225 source-native Corporate Reporting private-analysis release candidate.
-- DISPOSABLE-ONLY: this migration must never install in governed macroforge.
-- Candidate rows confer no mapping, rights, quality, eligibility, release,
-- publication, redistribution, or delivery authority.

BEGIN;

-- Do not inherit caller-controlled name resolution into the boundary guard.
SET LOCAL search_path = pg_catalog, public;

-- Fail before the first candidate DDL unless the actual backend is the exact,
-- runner-marked TASK-225 disposable database for one authenticated candidate.
DO $$
DECLARE marker record;
BEGIN
 IF current_database() !~ '^macroforge_task225_candidate_[0-9a-f]{12}$'
    OR to_regclass('public.macroforge_task225_rehearsal_boundary') IS NULL THEN
  RAISE EXCEPTION 'TASK-225 database boundary rejected migration in %', current_database();
 END IF;
 IF (SELECT count(*) FROM public.macroforge_task225_rehearsal_boundary) IS DISTINCT FROM 1 THEN
  RAISE EXCEPTION 'TASK-225 database boundary marker cardinality is invalid';
 END IF;
 SELECT database_name,purpose,contract_version,expected_candidate_sha256,expected_sec_cutoff
 INTO marker
 FROM public.macroforge_task225_rehearsal_boundary
 WHERE singleton IS TRUE
 FOR UPDATE;
 IF NOT FOUND
    OR marker.database_name::text IS DISTINCT FROM current_database()
    OR marker.purpose IS DISTINCT FROM 'task225_source_native_candidate_rehearsal_v1'
    OR marker.contract_version IS DISTINCT FROM '1'
    OR marker.expected_candidate_sha256 !~ '^[0-9a-f]{64}$'
    OR marker.expected_sec_cutoff IS DISTINCT FROM '2026-06-30T23:59:59Z' THEN
  RAISE EXCEPTION 'TASK-225 database boundary marker is absent, stale, or contradictory';
 END IF;
 IF to_regclass('corporate_reporting.source_native_candidate') IS NOT NULL
    OR to_regclass('corporate_reporting.source_native_candidate_filing_member') IS NOT NULL
    OR to_regclass('corporate_reporting.source_native_candidate_absence_member') IS NOT NULL
    OR to_regclass('corporate_reporting.source_native_candidate_state_axis') IS NOT NULL THEN
  RAISE EXCEPTION 'TASK-225 candidate surface already exists';
 END IF;
END $$;

CREATE OR REPLACE FUNCTION corporate_reporting.assert_source_native_candidate_boundary(
 expected_candidate_sha256 text
) RETURNS void LANGUAGE plpgsql SET search_path=pg_catalog,public AS $$
DECLARE marker record;
BEGIN
 IF current_database() !~ '^macroforge_task225_candidate_[0-9a-f]{12}$' THEN
  RAISE EXCEPTION 'TASK-225 database boundary rejected actual database %', current_database();
 END IF;
 IF (SELECT count(*) FROM public.macroforge_task225_rehearsal_boundary) IS DISTINCT FROM 1 THEN
  RAISE EXCEPTION 'TASK-225 database boundary marker cardinality is invalid';
 END IF;
 SELECT b.database_name,b.purpose,b.contract_version,b.expected_candidate_sha256 AS candidate_sha256,
        b.expected_sec_cutoff
 INTO marker
 FROM public.macroforge_task225_rehearsal_boundary b
 WHERE b.singleton IS TRUE
 FOR KEY SHARE;
 IF NOT FOUND
    OR marker.database_name::text IS DISTINCT FROM current_database()
    OR marker.purpose IS DISTINCT FROM 'task225_source_native_candidate_rehearsal_v1'
    OR marker.contract_version IS DISTINCT FROM '1'
    OR marker.candidate_sha256 IS DISTINCT FROM expected_candidate_sha256
    OR marker.expected_sec_cutoff IS DISTINCT FROM '2026-06-30T23:59:59Z' THEN
  RAISE EXCEPTION 'TASK-225 database boundary marker is absent, stale, contradictory, or candidate-mismatched';
 END IF;
END $$;

CREATE TABLE corporate_reporting.source_native_candidate (
 candidate_sha256 text PRIMARY KEY CHECK(candidate_sha256 ~ '^[0-9a-f]{64}$'),
 contract_version text NOT NULL CHECK(contract_version='1'),
 sec_cutoff timestamptz NOT NULL,
 knowledge_cutoff_applicable boolean NOT NULL CHECK(knowledge_cutoff_applicable IS FALSE),
 predecessor_candidate_sha256 text CHECK(
  predecessor_candidate_sha256 IS NULL
  OR predecessor_candidate_sha256 ~ '^[0-9a-f]{64}$'),
 payload_sha256 text NOT NULL CHECK(payload_sha256 ~ '^[0-9a-f]{64}$'),
 candidate_document jsonb NOT NULL,
 recorded_at timestamptz NOT NULL DEFAULT now(),
 CONSTRAINT source_native_candidate_schema_exact CHECK (
  ((candidate_document->>'schema')='macroforge.corporate-reporting.source-native-candidate.v1') IS TRUE),
 CONSTRAINT source_native_candidate_permissions_exact CHECK (
  ((candidate_document->'permissions') =
   '{"private_analysis_candidate":true,"publication":false,"redistribution":"not_authorized","remote_delivery":false}'::jsonb) IS TRUE),
 CONSTRAINT source_native_candidate_knowledge_exact CHECK (
  ((candidate_document->'cutoffs'->'knowledge') =
   '{"applicable":false,"reason":"no_governed_knowledge_closure","value":null}'::jsonb) IS TRUE),
 CONSTRAINT source_native_candidate_sec_cutoff_exact CHECK (
  ((candidate_document->'cutoffs'->>'sec')='2026-06-30T23:59:59Z') IS TRUE),
 CONSTRAINT source_native_candidate_contract_exact CHECK (
  ((candidate_document->'contract') =
   '{"name":"source-native-private-analysis","version":"1"}'::jsonb) IS TRUE),
 CONSTRAINT source_native_candidate_producer_exact CHECK (
  ((candidate_document->'producer') =
   '{"domain":"corporate_reporting","name":"MacroForge"}'::jsonb) IS TRUE),
 CONSTRAINT source_native_candidate_precedence_exact CHECK (
  ((candidate_document->'representation_precedence') =
   '{"candidate":"candidate_v1_is_canonical_before_governed_admission","governed":"authority_derived_v3_is_canonical_after_admission","historical":"v2_and_stored_items_are_compatibility_views_and_must_agree"}'::jsonb) IS TRUE),
 CONSTRAINT source_native_candidate_failure_accounting_exact CHECK (
  ((candidate_document->'failure_accounting') =
   '{"extraction_failure":0,"intentional_exclusion":0,"malformed_package":0,"missing_package":0,"technical_incompleteness":0,"unresolved_dependency":0}'::jsonb) IS TRUE),
 CONSTRAINT source_native_candidate_state_axes_exact CHECK (
  ((candidate_document->'state_axes') =
   '[{"axis":"comparability","status":"blocked_no_accepted_mappings"},{"axis":"delivery","status":"prohibited"},{"axis":"eligibility","status":"blocked_no_governed_authority"},{"axis":"publication","status":"prohibited"},{"axis":"quality","status":"candidate_evidence_only"},{"axis":"rights","status":"private_analysis_candidate_only"},{"axis":"semantic_readiness","status":"source_native_only"},{"axis":"source_membership_completeness","status":"complete"},{"axis":"technical_completeness","status":"complete"}]'::jsonb) IS TRUE)
);

CREATE TABLE corporate_reporting.source_native_candidate_filing_member (
 candidate_sha256 text NOT NULL REFERENCES corporate_reporting.source_native_candidate(candidate_sha256),
 item_ordinal integer NOT NULL CHECK(item_ordinal>0),
 accession text NOT NULL CHECK(accession ~ '^[0-9]{10}-[0-9]{2}-[0-9]{6}$'),
 member_sha256 text NOT NULL CHECK(member_sha256 ~ '^[0-9a-f]{64}$'),
 member_document jsonb NOT NULL,
 PRIMARY KEY(candidate_sha256,item_ordinal),
 UNIQUE(candidate_sha256,accession),
 UNIQUE(candidate_sha256,member_sha256)
);

CREATE TABLE corporate_reporting.source_native_candidate_absence_member (
 candidate_sha256 text NOT NULL REFERENCES corporate_reporting.source_native_candidate(candidate_sha256),
 item_ordinal integer NOT NULL CHECK(item_ordinal>0),
 absence_identity text NOT NULL CHECK(absence_identity ~ '^[0-9a-f]{64}$'),
 disposition text NOT NULL CHECK(disposition='acquisition_cessation_absence'),
 member_sha256 text NOT NULL CHECK(member_sha256 ~ '^[0-9a-f]{64}$'),
 member_document jsonb NOT NULL,
 PRIMARY KEY(candidate_sha256,item_ordinal),
 UNIQUE(candidate_sha256,absence_identity),
 UNIQUE(candidate_sha256,member_sha256)
);

CREATE TABLE corporate_reporting.source_native_candidate_state_axis (
 candidate_sha256 text NOT NULL REFERENCES corporate_reporting.source_native_candidate(candidate_sha256),
 axis_name text NOT NULL CHECK(axis_name IN (
  'technical_completeness','source_membership_completeness','semantic_readiness',
  'comparability','rights','quality','eligibility','publication','delivery')),
 status text NOT NULL,
 PRIMARY KEY(candidate_sha256,axis_name)
);

CREATE OR REPLACE FUNCTION corporate_reporting.check_source_native_candidate_header()
RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog,public AS $$
DECLARE
 expected_sha text;
 expected_payload_sha text;
 documents_count bigint;
 occurrences_count bigint;
 slots_count bigint;
 amendments_count bigint;
 allowed_keys text[]:=ARRAY[
  'candidate_sha256','contract','cutoffs','failure_accounting','filings','permissions',
  'portfolio_absences','predecessor_candidate_sha256','producer',
  'representation_precedence','schema','state_axes'];
BEGIN
 PERFORM corporate_reporting.assert_source_native_candidate_boundary(NEW.candidate_sha256);
 IF jsonb_typeof(NEW.candidate_document) IS DISTINCT FROM 'object'
    OR NOT (NEW.candidate_document ?& allowed_keys)
    OR EXISTS (
      SELECT 1 FROM jsonb_object_keys(NEW.candidate_document) key
      WHERE NOT (key=ANY(allowed_keys))) THEN
  RAISE EXCEPTION 'candidate document fields are incomplete or unknown';
 END IF;
 expected_sha:=corporate_reporting.canonical_sha256(NEW.candidate_document-'candidate_sha256');
 expected_payload_sha:=corporate_reporting.canonical_sha256(
  corporate_reporting.canonical_json(NEW.candidate_document)||E'\n');
 IF NEW.candidate_document->>'candidate_sha256' IS DISTINCT FROM NEW.candidate_sha256
    OR expected_sha IS DISTINCT FROM NEW.candidate_sha256
    OR expected_payload_sha IS DISTINCT FROM NEW.payload_sha256 THEN
  RAISE EXCEPTION 'candidate canonical identity or payload digest mismatch';
 END IF;
 IF NEW.candidate_document->'contract'->>'version' IS DISTINCT FROM NEW.contract_version
    OR NEW.candidate_document->'cutoffs'->>'sec' IS DISTINCT FROM '2026-06-30T23:59:59Z'
    OR (NEW.candidate_document->'cutoffs'->>'sec')::timestamptz IS DISTINCT FROM NEW.sec_cutoff
    OR (NEW.candidate_document->'cutoffs'->'knowledge'->>'applicable')::boolean
       IS DISTINCT FROM NEW.knowledge_cutoff_applicable
    OR NEW.candidate_document->>'predecessor_candidate_sha256'
       IS DISTINCT FROM NEW.predecessor_candidate_sha256 THEN
  RAISE EXCEPTION 'candidate header differs from canonical document';
 END IF;
 IF jsonb_typeof(NEW.candidate_document->'filings') IS DISTINCT FROM 'array'
    OR jsonb_typeof(NEW.candidate_document->'portfolio_absences') IS DISTINCT FROM 'array'
    OR jsonb_typeof(NEW.candidate_document->'state_axes') IS DISTINCT FROM 'array'
    OR jsonb_array_length(NEW.candidate_document->'filings') IS DISTINCT FROM 19
    OR jsonb_array_length(NEW.candidate_document->'portfolio_absences') IS DISTINCT FROM 10
    OR jsonb_array_length(NEW.candidate_document->'state_axes') IS DISTINCT FROM 9 THEN
  RAISE EXCEPTION 'candidate exact membership cardinality mismatch';
 END IF;
 SELECT COALESCE(sum(jsonb_array_length(filing->'documents')),0),
        COALESCE(sum(jsonb_array_length(filing->'occurrence_sha256s')),0),
        COALESCE(sum(jsonb_array_length(filing->'slots')),0),
        count(*) FILTER (WHERE filing->'amendment' IS DISTINCT FROM 'null'::jsonb)
 INTO documents_count,occurrences_count,slots_count,amendments_count
 FROM jsonb_array_elements(NEW.candidate_document->'filings') filing;
 IF documents_count IS DISTINCT FROM 147
    OR occurrences_count IS DISTINCT FROM 35048
    OR slots_count IS DISTINCT FROM 32381
    OR amendments_count IS DISTINCT FROM 2 THEN
  RAISE EXCEPTION 'candidate detailed source membership accounting mismatch';
 END IF;
 IF EXISTS (
  SELECT 1
  FROM jsonb_array_elements(NEW.candidate_document->'filings') filing,
       LATERAL jsonb_array_elements(filing->'slots') slot
  WHERE (slot->'mapping') IS DISTINCT FROM
   '{"attribution":"task225-source-native-contract-v1","disposition":"deliberately_unmapped"}'::jsonb
 ) OR EXISTS (
  SELECT 1 FROM jsonb_array_elements(NEW.candidate_document->'portfolio_absences') absence
  WHERE absence->>'disposition' IS DISTINCT FROM 'acquisition_cessation_absence'
 ) THEN
  RAISE EXCEPTION 'candidate source-native permission or mapping posture mismatch';
 END IF;
 RETURN NEW;
END $$;
CREATE TRIGGER trg_cr_source_native_candidate_header
 BEFORE INSERT ON corporate_reporting.source_native_candidate
 FOR EACH ROW EXECUTE FUNCTION corporate_reporting.check_source_native_candidate_header();

CREATE OR REPLACE FUNCTION corporate_reporting.check_source_native_candidate_member()
RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog,public AS $$
DECLARE candidate jsonb; expected jsonb;
BEGIN
 PERFORM corporate_reporting.assert_source_native_candidate_boundary(NEW.candidate_sha256);
 SELECT candidate_document INTO STRICT candidate
 FROM corporate_reporting.source_native_candidate WHERE candidate_sha256=NEW.candidate_sha256;
 IF TG_TABLE_NAME='source_native_candidate_filing_member' THEN
  expected:=candidate->'filings'->(NEW.item_ordinal-1);
  IF expected IS NULL OR expected->>'accession' IS DISTINCT FROM NEW.accession THEN
   RAISE EXCEPTION 'candidate membership ordinal/accession mismatch';
  END IF;
 ELSIF TG_TABLE_NAME='source_native_candidate_absence_member' THEN
  expected:=candidate->'portfolio_absences'->(NEW.item_ordinal-1);
  IF expected IS NULL OR expected->>'absence_identity' IS DISTINCT FROM NEW.absence_identity
     OR expected->>'disposition' IS DISTINCT FROM NEW.disposition THEN
   RAISE EXCEPTION 'candidate membership ordinal/absence mismatch';
  END IF;
 END IF;
 IF expected IS DISTINCT FROM NEW.member_document
    OR corporate_reporting.canonical_sha256(expected) IS DISTINCT FROM NEW.member_sha256 THEN
  RAISE EXCEPTION 'candidate membership document/digest mismatch';
 END IF;
 RETURN NEW;
END $$;
CREATE TRIGGER trg_cr_source_native_filing_member BEFORE INSERT
 ON corporate_reporting.source_native_candidate_filing_member
 FOR EACH ROW EXECUTE FUNCTION corporate_reporting.check_source_native_candidate_member();
CREATE TRIGGER trg_cr_source_native_absence_member BEFORE INSERT
 ON corporate_reporting.source_native_candidate_absence_member
 FOR EACH ROW EXECUTE FUNCTION corporate_reporting.check_source_native_candidate_member();

CREATE OR REPLACE FUNCTION corporate_reporting.check_source_native_candidate_axis()
RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog,public AS $$
DECLARE expected jsonb;
BEGIN
 PERFORM corporate_reporting.assert_source_native_candidate_boundary(NEW.candidate_sha256);
 SELECT axis INTO STRICT expected FROM (
  SELECT value axis FROM corporate_reporting.source_native_candidate c,
   LATERAL jsonb_array_elements(c.candidate_document->'state_axes') value
  WHERE c.candidate_sha256=NEW.candidate_sha256 AND value->>'axis'=NEW.axis_name
 ) resolved;
 IF expected->>'status' IS DISTINCT FROM NEW.status THEN
  RAISE EXCEPTION 'candidate state axis differs from canonical document';
 END IF;
 RETURN NEW;
END $$;
CREATE TRIGGER trg_cr_source_native_candidate_axis BEFORE INSERT
 ON corporate_reporting.source_native_candidate_state_axis
 FOR EACH ROW EXECUTE FUNCTION corporate_reporting.check_source_native_candidate_axis();

CREATE OR REPLACE FUNCTION corporate_reporting.assert_source_native_candidate_complete()
RETURNS trigger LANGUAGE plpgsql SET search_path=pg_catalog,public AS $$
DECLARE identity text:=COALESCE(NEW.candidate_sha256,OLD.candidate_sha256);
BEGIN
 PERFORM corporate_reporting.assert_source_native_candidate_boundary(identity);
 IF (SELECT count(*) FROM ONLY corporate_reporting.source_native_candidate_filing_member
     WHERE candidate_sha256=identity) IS DISTINCT FROM 19
    OR (SELECT count(*) FROM ONLY corporate_reporting.source_native_candidate_absence_member
        WHERE candidate_sha256=identity) IS DISTINCT FROM 10
    OR (SELECT count(*) FROM ONLY corporate_reporting.source_native_candidate_state_axis
        WHERE candidate_sha256=identity) IS DISTINCT FROM 9 THEN
  RAISE EXCEPTION 'candidate relational membership is incomplete';
 END IF;
 RETURN NULL;
END $$;

-- Every direct INSERT and COPY must close the exact 19/10/9 relation by commit.
DO $$ DECLARE table_name text; BEGIN
 FOREACH table_name IN ARRAY ARRAY[
  'source_native_candidate','source_native_candidate_filing_member',
  'source_native_candidate_absence_member','source_native_candidate_state_axis'
 ] LOOP
  EXECUTE format(
   'CREATE CONSTRAINT TRIGGER %I AFTER INSERT ON corporate_reporting.%I '
   'DEFERRABLE INITIALLY DEFERRED FOR EACH ROW '
   'EXECUTE FUNCTION corporate_reporting.assert_source_native_candidate_complete()',
   'trg_cr_complete_'||table_name,table_name);
 END LOOP;
END $$;

-- Marker and candidate history are append-only. Corrections require a fresh
-- disposable database or a successor candidate, never mutation in place.
CREATE TRIGGER trg_cr_immutable_task225_rehearsal_boundary
 BEFORE INSERT OR UPDATE OR DELETE ON public.macroforge_task225_rehearsal_boundary
 FOR EACH ROW EXECUTE FUNCTION corporate_reporting.reject_admitted_update();
CREATE TRIGGER trg_cr_no_truncate_task225_rehearsal_boundary
 BEFORE TRUNCATE ON public.macroforge_task225_rehearsal_boundary
 FOR EACH STATEMENT EXECUTE FUNCTION corporate_reporting.reject_admitted_update();
DO $$ DECLARE table_name text; BEGIN
 FOREACH table_name IN ARRAY ARRAY[
  'source_native_candidate','source_native_candidate_filing_member',
  'source_native_candidate_absence_member','source_native_candidate_state_axis'
 ] LOOP
  EXECUTE format('CREATE TRIGGER %I BEFORE UPDATE OR DELETE ON corporate_reporting.%I '
                 'FOR EACH ROW EXECUTE FUNCTION corporate_reporting.reject_admitted_update()',
                 'trg_cr_immutable_'||table_name,table_name);
  EXECUTE format('CREATE TRIGGER %I BEFORE TRUNCATE ON corporate_reporting.%I '
                 'FOR EACH STATEMENT EXECUTE FUNCTION corporate_reporting.reject_admitted_update()',
                 'trg_cr_no_truncate_'||table_name,table_name);
 END LOOP;
END $$;

COMMIT;
