-- Corporate Reporting SEC/XBRL foundation (frozen first vertical slice).
-- Additive and idempotent: shared meta owners are referenced, never replaced.
CREATE EXTENSION IF NOT EXISTS pgcrypto;
CREATE SCHEMA IF NOT EXISTS corporate_reporting;

CREATE TABLE IF NOT EXISTS corporate_reporting.reporting_entity (
 entity_id uuid PRIMARY KEY DEFAULT gen_random_uuid(), entity_kind text NOT NULL CHECK(entity_kind IN ('registrant','other')), created_at timestamptz NOT NULL DEFAULT now());
CREATE TABLE IF NOT EXISTS corporate_reporting.entity_identifier (
 entity_identifier_id uuid PRIMARY KEY DEFAULT gen_random_uuid(), entity_id uuid NOT NULL REFERENCES corporate_reporting.reporting_entity(entity_id), scheme text NOT NULL, normalized_value text NOT NULL,
 evidence_document_id uuid, recorded_at timestamptz NOT NULL DEFAULT now(), UNIQUE(scheme,normalized_value),
 CHECK(scheme <> 'sec:cik' OR normalized_value ~ '^[0-9]{10}$'));
CREATE TABLE IF NOT EXISTS corporate_reporting.filing_submission (
 filing_id uuid PRIMARY KEY DEFAULT gen_random_uuid(), dataset_release_id uuid NOT NULL UNIQUE REFERENCES meta.dataset_release(dataset_release_id), filer_entity_id uuid NOT NULL REFERENCES corporate_reporting.reporting_entity(entity_id),
 accession text NOT NULL UNIQUE CHECK(accession ~ '^[0-9]{10}-[0-9]{2}-[0-9]{6}$'), form_type text NOT NULL, filed_date date NOT NULL, accepted_at timestamptz NOT NULL, report_period_end date NOT NULL,
 primary_document_name text NOT NULL, amendment_flag boolean NOT NULL, amendment_description text, source_manifest_sha256 text NOT NULL CHECK(source_manifest_sha256 ~ '^[0-9a-f]{64}$'),
 UNIQUE(filing_id,filer_entity_id), UNIQUE(filing_id,report_period_end));
CREATE TABLE IF NOT EXISTS corporate_reporting.filing_document (
 document_id uuid PRIMARY KEY DEFAULT gen_random_uuid(), filing_id uuid NOT NULL REFERENCES corporate_reporting.filing_submission(filing_id), document_name text NOT NULL, document_role text NOT NULL,
 source_url text NOT NULL, media_type text NOT NULL, byte_length bigint NOT NULL CHECK(byte_length>=0), sha256 text NOT NULL CHECK(sha256 ~ '^[0-9a-f]{64}$'), local_evidence_locator text, archive_sequence integer,
 UNIQUE(filing_id,document_name), UNIQUE(filing_id,sha256,document_role), UNIQUE(document_id,filing_id));
ALTER TABLE corporate_reporting.entity_identifier DROP CONSTRAINT IF EXISTS entity_identifier_evidence_document_id_fkey;
ALTER TABLE corporate_reporting.entity_identifier ADD CONSTRAINT entity_identifier_evidence_document_id_fkey FOREIGN KEY(evidence_document_id) REFERENCES corporate_reporting.filing_document(document_id) DEFERRABLE INITIALLY DEFERRED;

CREATE TABLE IF NOT EXISTS corporate_reporting.parser_run (
 parser_run_id uuid PRIMARY KEY DEFAULT gen_random_uuid(), pipeline_run_id uuid NOT NULL REFERENCES meta.pipeline_run(pipeline_run_id), filing_id uuid NOT NULL REFERENCES corporate_reporting.filing_submission(filing_id),
 parser_attempt_key text NOT NULL, parser_contract text NOT NULL, parser_version text NOT NULL, source_manifest_sha256 text NOT NULL CHECK(source_manifest_sha256 ~ '^[0-9a-f]{64}$'), resolution_policy_sha256 text NOT NULL CHECK(resolution_policy_sha256 ~ '^[0-9a-f]{64}$'),
 status text NOT NULL CHECK(status IN ('started','succeeded','failed')), metrics_sha256 text CHECK(metrics_sha256 ~ '^[0-9a-f]{64}$'), parser_output_sha256 text CHECK(parser_output_sha256 ~ '^[0-9a-f]{64}$'), recorded_at timestamptz NOT NULL DEFAULT now(),
 UNIQUE(pipeline_run_id,filing_id,parser_contract,parser_version,source_manifest_sha256,resolution_policy_sha256,parser_output_sha256), UNIQUE(parser_run_id,filing_id));
ALTER TABLE corporate_reporting.parser_run ADD COLUMN IF NOT EXISTS parser_attempt_key text;
-- An earlier unpublished 005 shape may already carry the old UPDATE-only guard.
-- Drop it only inside this migration before the deterministic legacy backfill;
-- the complete UPDATE/DELETE guard is recreated below in the same transaction.
DROP TRIGGER IF EXISTS trg_cr_immutable_parser_run ON corporate_reporting.parser_run;
-- Preserve every legacy attempt: a constant backfill collides when a filing has several.
UPDATE corporate_reporting.parser_run
SET parser_attempt_key='legacy-' || parser_run_id::text
WHERE parser_attempt_key IS NULL;
ALTER TABLE corporate_reporting.parser_run ALTER COLUMN parser_attempt_key SET NOT NULL;
DO $$ BEGIN
 IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conrelid='corporate_reporting.parser_run'::regclass AND conname='uq_cr_parser_attempt') THEN
  ALTER TABLE corporate_reporting.parser_run ADD CONSTRAINT uq_cr_parser_attempt UNIQUE(filing_id,parser_attempt_key);
 END IF;
END $$;
CREATE TABLE IF NOT EXISTS corporate_reporting.knowledge_revision (
 knowledge_revision_id uuid PRIMARY KEY DEFAULT gen_random_uuid(), axis_type text NOT NULL, object_key text NOT NULL CHECK(object_key ~ '^[0-9a-f]{64}$'), predecessor_revision_id uuid,
 pipeline_run_id uuid NOT NULL REFERENCES meta.pipeline_run(pipeline_run_id), source_effective_at timestamptz, evidence_fingerprint text NOT NULL CHECK(evidence_fingerprint ~ '^[0-9a-f]{64}$'), recorded_at timestamptz NOT NULL DEFAULT now(),
 UNIQUE(knowledge_revision_id,axis_type,object_key), UNIQUE(predecessor_revision_id,axis_type,object_key),
 FOREIGN KEY(predecessor_revision_id,axis_type,object_key) REFERENCES corporate_reporting.knowledge_revision(knowledge_revision_id,axis_type,object_key) DEFERRABLE INITIALLY DEFERRED);
CREATE UNIQUE INDEX IF NOT EXISTS uq_cr_knowledge_root ON corporate_reporting.knowledge_revision(axis_type,object_key) WHERE predecessor_revision_id IS NULL;
CREATE UNIQUE INDEX IF NOT EXISTS uq_cr_knowledge_child ON corporate_reporting.knowledge_revision(predecessor_revision_id) WHERE predecessor_revision_id IS NOT NULL;

CREATE TABLE IF NOT EXISTS corporate_reporting.filing_relationship_revision (
 relationship_revision_id uuid PRIMARY KEY DEFAULT gen_random_uuid(), knowledge_revision_id uuid NOT NULL UNIQUE, axis_type text NOT NULL DEFAULT 'filing_relationship' CHECK(axis_type='filing_relationship'), object_key text NOT NULL,
 predecessor_filing_id uuid NOT NULL, successor_filing_id uuid NOT NULL, relationship_type text NOT NULL CHECK(relationship_type IN ('amends','restates')),
 evidence_document_id uuid NOT NULL, evidence_excerpt_fingerprint text NOT NULL CHECK(evidence_excerpt_fingerprint ~ '^[0-9a-f]{64}$'), assertion_status text NOT NULL CHECK(assertion_status IN ('accepted','proposed','deferred','rejected')), recorded_at timestamptz NOT NULL DEFAULT now(),
 CHECK(predecessor_filing_id<>successor_filing_id), FOREIGN KEY(knowledge_revision_id,axis_type,object_key) REFERENCES corporate_reporting.knowledge_revision(knowledge_revision_id,axis_type,object_key), FOREIGN KEY(predecessor_filing_id) REFERENCES corporate_reporting.filing_submission(filing_id), FOREIGN KEY(successor_filing_id) REFERENCES corporate_reporting.filing_submission(filing_id), FOREIGN KEY(evidence_document_id,successor_filing_id) REFERENCES corporate_reporting.filing_document(document_id,filing_id));

CREATE TABLE IF NOT EXISTS corporate_reporting.reporting_scope (
 scope_id uuid PRIMARY KEY DEFAULT gen_random_uuid(), filing_id uuid NOT NULL REFERENCES corporate_reporting.filing_submission(filing_id), reporting_entity_id uuid NOT NULL REFERENCES corporate_reporting.reporting_entity(entity_id),
 scope_kind text NOT NULL, scope_label text, parent_scope_id uuid, evidence_fingerprint text NOT NULL CHECK(evidence_fingerprint ~ '^[0-9a-f]{64}$'),
 UNIQUE(scope_id,filing_id), FOREIGN KEY(parent_scope_id,filing_id) REFERENCES corporate_reporting.reporting_scope(scope_id,filing_id) DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE IF NOT EXISTS corporate_reporting.taxonomy_set (
 taxonomy_set_id uuid PRIMARY KEY DEFAULT gen_random_uuid(), parser_run_id uuid NOT NULL, filing_id uuid NOT NULL, entry_schema_document_id uuid NOT NULL,
 dts_manifest_sha256 text NOT NULL CHECK(dts_manifest_sha256 ~ '^[0-9a-f]{64}$'), namespace_inventory jsonb NOT NULL, resolution_status text NOT NULL CHECK(resolution_status IN ('resolved','unresolved_external')),
 UNIQUE(taxonomy_set_id,filing_id), UNIQUE(parser_run_id,taxonomy_set_id,filing_id), FOREIGN KEY(parser_run_id,filing_id) REFERENCES corporate_reporting.parser_run(parser_run_id,filing_id), FOREIGN KEY(entry_schema_document_id,filing_id) REFERENCES corporate_reporting.filing_document(document_id,filing_id));
CREATE TABLE IF NOT EXISTS corporate_reporting.source_concept (
 source_concept_id uuid PRIMARY KEY DEFAULT gen_random_uuid(), parser_run_id uuid NOT NULL, filing_id uuid NOT NULL, taxonomy_set_id uuid NOT NULL, namespace_uri text NOT NULL, local_name text NOT NULL,
 declaration_status text NOT NULL CHECK(declaration_status IN ('declared','referenced_unresolved')), declaration_document_id uuid, declaration_sha256 text, data_type_qname text, substitution_group_qname text, period_type text CHECK(period_type IS NULL OR period_type IN ('instant','duration')),
 balance text CHECK(balance IS NULL OR balance IN ('debit','credit')), abstract boolean, nillable boolean, extension_flag boolean NOT NULL,
 UNIQUE(parser_run_id,taxonomy_set_id,namespace_uri,local_name), UNIQUE(source_concept_id,filing_id), UNIQUE(parser_run_id,source_concept_id,filing_id), FOREIGN KEY(parser_run_id,filing_id) REFERENCES corporate_reporting.parser_run(parser_run_id,filing_id), FOREIGN KEY(parser_run_id,taxonomy_set_id,filing_id) REFERENCES corporate_reporting.taxonomy_set(parser_run_id,taxonomy_set_id,filing_id), FOREIGN KEY(declaration_document_id,filing_id) REFERENCES corporate_reporting.filing_document(document_id,filing_id));
CREATE TABLE IF NOT EXISTS corporate_reporting.source_concept_equivalence_revision (
 equivalence_revision_id uuid PRIMARY KEY DEFAULT gen_random_uuid(), knowledge_revision_id uuid NOT NULL UNIQUE, axis_type text NOT NULL DEFAULT 'concept_equivalence' CHECK(axis_type='concept_equivalence'), object_key text NOT NULL, left_source_concept_id uuid NOT NULL REFERENCES corporate_reporting.source_concept(source_concept_id), right_source_concept_id uuid NOT NULL REFERENCES corporate_reporting.source_concept(source_concept_id),
 status text NOT NULL CHECK(status IN ('accepted','proposed','deferred','rejected')), scope text NOT NULL, rationale text NOT NULL, evidence_fingerprint text NOT NULL CHECK(evidence_fingerprint ~ '^[0-9a-f]{64}$'), recorded_at timestamptz NOT NULL DEFAULT now(), CHECK(left_source_concept_id<>right_source_concept_id), FOREIGN KEY(knowledge_revision_id,axis_type,object_key) REFERENCES corporate_reporting.knowledge_revision(knowledge_revision_id,axis_type,object_key));

CREATE TABLE IF NOT EXISTS corporate_reporting.xbrl_context (
 context_id uuid PRIMARY KEY DEFAULT gen_random_uuid(), parser_run_id uuid NOT NULL, filing_id uuid NOT NULL, source_context_id text NOT NULL, reporting_scope_id uuid NOT NULL,
 entity_scheme text NOT NULL, entity_value text NOT NULL, period_kind text NOT NULL CHECK(period_kind IN ('instant','duration','forever')), start_date date, end_date date, instant_date date,
 raw_xml_sha256 text NOT NULL CHECK(raw_xml_sha256 ~ '^[0-9a-f]{64}$'), semantic_context_sha256 text NOT NULL CHECK(semantic_context_sha256 ~ '^[0-9a-f]{64}$'),
 UNIQUE(parser_run_id,filing_id,source_context_id), UNIQUE(parser_run_id,filing_id,semantic_context_sha256,raw_xml_sha256), UNIQUE(context_id,filing_id), UNIQUE(parser_run_id,context_id,filing_id),
 FOREIGN KEY(parser_run_id,filing_id) REFERENCES corporate_reporting.parser_run(parser_run_id,filing_id), FOREIGN KEY(reporting_scope_id,filing_id) REFERENCES corporate_reporting.reporting_scope(scope_id,filing_id),
 CHECK((period_kind='instant' AND instant_date IS NOT NULL AND start_date IS NULL AND end_date IS NULL) OR (period_kind='duration' AND instant_date IS NULL AND start_date IS NOT NULL AND end_date IS NOT NULL AND start_date<=end_date) OR (period_kind='forever' AND instant_date IS NULL AND start_date IS NULL AND end_date IS NULL)));
CREATE TABLE IF NOT EXISTS corporate_reporting.xbrl_context_dimension (
 context_dimension_id uuid PRIMARY KEY DEFAULT gen_random_uuid(), context_id uuid NOT NULL, filing_id uuid NOT NULL, location text NOT NULL CHECK(location IN ('segment','scenario')), axis_namespace text NOT NULL, axis_local_name text NOT NULL,
 member_kind text NOT NULL CHECK(member_kind IN ('explicit','typed')), member_namespace text, member_local_name text, typed_member_canonical_xml text,
 typed_member_sha256 text GENERATED ALWAYS AS (CASE WHEN member_kind='typed' THEN encode(digest(typed_member_canonical_xml,'sha256'),'hex') ELSE NULL END) STORED,
 UNIQUE(context_id,location,axis_namespace,axis_local_name), FOREIGN KEY(context_id,filing_id) REFERENCES corporate_reporting.xbrl_context(context_id,filing_id), CHECK((member_kind='explicit' AND member_namespace IS NOT NULL AND member_local_name IS NOT NULL AND typed_member_canonical_xml IS NULL AND typed_member_sha256 IS NULL) OR (member_kind='typed' AND member_namespace IS NULL AND member_local_name IS NULL AND typed_member_canonical_xml IS NOT NULL AND typed_member_sha256 ~ '^[0-9a-f]{64}$')));
-- Upgrade the prior caller-owned digest column by bounded derived-column recreation.
DO $$
DECLARE generated text; constraint_name text;
BEGIN
 SELECT is_generated INTO generated FROM information_schema.columns
 WHERE table_schema='corporate_reporting' AND table_name='xbrl_context_dimension'
   AND column_name='typed_member_sha256';
 IF generated IS DISTINCT FROM 'ALWAYS' THEN
  FOR constraint_name IN SELECT conname FROM pg_constraint
   WHERE conrelid='corporate_reporting.xbrl_context_dimension'::regclass
     AND contype='c' AND pg_get_constraintdef(oid) LIKE '%typed_member_sha256%'
  LOOP
   EXECUTE format('ALTER TABLE corporate_reporting.xbrl_context_dimension DROP CONSTRAINT %I',constraint_name);
  END LOOP;
  ALTER TABLE corporate_reporting.xbrl_context_dimension DROP COLUMN typed_member_sha256;
  ALTER TABLE corporate_reporting.xbrl_context_dimension ADD COLUMN typed_member_sha256 text
   GENERATED ALWAYS AS (CASE WHEN member_kind='typed' THEN encode(digest(typed_member_canonical_xml,'sha256'),'hex') ELSE NULL END) STORED;
  ALTER TABLE corporate_reporting.xbrl_context_dimension ADD CONSTRAINT ck_cr_context_dimension_member_shape
   CHECK((member_kind='explicit' AND member_namespace IS NOT NULL AND member_local_name IS NOT NULL AND typed_member_canonical_xml IS NULL AND typed_member_sha256 IS NULL)
      OR (member_kind='typed' AND member_namespace IS NULL AND member_local_name IS NULL AND typed_member_canonical_xml IS NOT NULL AND typed_member_sha256 ~ '^[0-9a-f]{64}$'));
 END IF;
END $$;
CREATE TABLE IF NOT EXISTS corporate_reporting.xbrl_unit_semantics (
 unit_semantics_id uuid PRIMARY KEY DEFAULT gen_random_uuid(), parser_run_id uuid NOT NULL, filing_id uuid NOT NULL, numerator_measures jsonb NOT NULL, denominator_measures jsonb NOT NULL,
 semantic_unit_sha256 text NOT NULL CHECK(semantic_unit_sha256 ~ '^[0-9a-f]{64}$'), UNIQUE(parser_run_id,filing_id,semantic_unit_sha256), UNIQUE(unit_semantics_id,filing_id),
 FOREIGN KEY(parser_run_id,filing_id) REFERENCES corporate_reporting.parser_run(parser_run_id,filing_id), CHECK(jsonb_typeof(numerator_measures)='array' AND jsonb_array_length(numerator_measures)>0 AND jsonb_typeof(denominator_measures)='array'));
CREATE TABLE IF NOT EXISTS corporate_reporting.xbrl_source_unit_alias (
 source_unit_alias_id uuid PRIMARY KEY DEFAULT gen_random_uuid(), parser_run_id uuid NOT NULL, filing_id uuid NOT NULL, source_unit_id text NOT NULL, unit_semantics_id uuid NOT NULL, raw_xml_sha256 text NOT NULL CHECK(raw_xml_sha256 ~ '^[0-9a-f]{64}$'),
 UNIQUE(parser_run_id,filing_id,source_unit_id), UNIQUE(source_unit_alias_id,filing_id), UNIQUE(parser_run_id,source_unit_alias_id,filing_id), FOREIGN KEY(parser_run_id,filing_id) REFERENCES corporate_reporting.parser_run(parser_run_id,filing_id), FOREIGN KEY(unit_semantics_id,filing_id) REFERENCES corporate_reporting.xbrl_unit_semantics(unit_semantics_id,filing_id));

CREATE TABLE IF NOT EXISTS corporate_reporting.fact_occurrence (
 fact_occurrence_id uuid PRIMARY KEY DEFAULT gen_random_uuid(), filing_id uuid NOT NULL, document_id uuid NOT NULL, source_ordinal bigint NOT NULL CHECK(source_ordinal>0), source_fact_id text,
 source_concept_qname text NOT NULL, source_context_ref text NOT NULL, source_unit_ref text, xml_lang text, lexical_value text NOT NULL, nil_flag boolean NOT NULL, decimals text, precision text, inline_format text, inline_scale integer, inline_sign text, occurrence_sha256 text NOT NULL CHECK(occurrence_sha256 ~ '^[0-9a-f]{64}$'),
 UNIQUE(filing_id,document_id,source_ordinal), UNIQUE(filing_id,occurrence_sha256), UNIQUE(fact_occurrence_id,filing_id),
 FOREIGN KEY(document_id,filing_id) REFERENCES corporate_reporting.filing_document(document_id,filing_id));
-- Immutable source evidence is parser-independent. Concept/context/unit resolution
-- and normalized values are owned by one parser run through this authority.
CREATE TABLE IF NOT EXISTS corporate_reporting.fact_occurrence_interpretation (
 fact_occurrence_interpretation_id uuid PRIMARY KEY DEFAULT gen_random_uuid(), parser_run_id uuid NOT NULL, fact_occurrence_id uuid NOT NULL, filing_id uuid NOT NULL, source_concept_id uuid NOT NULL, context_id uuid NOT NULL, source_unit_alias_id uuid, normalized_numeric numeric, normalized_boolean boolean,
 UNIQUE(parser_run_id,fact_occurrence_id), UNIQUE(fact_occurrence_interpretation_id,filing_id), UNIQUE(parser_run_id,fact_occurrence_interpretation_id,fact_occurrence_id,filing_id),
 FOREIGN KEY(parser_run_id,filing_id) REFERENCES corporate_reporting.parser_run(parser_run_id,filing_id), FOREIGN KEY(fact_occurrence_id,filing_id) REFERENCES corporate_reporting.fact_occurrence(fact_occurrence_id,filing_id), FOREIGN KEY(parser_run_id,source_concept_id,filing_id) REFERENCES corporate_reporting.source_concept(parser_run_id,source_concept_id,filing_id), FOREIGN KEY(parser_run_id,context_id,filing_id) REFERENCES corporate_reporting.xbrl_context(parser_run_id,context_id,filing_id), FOREIGN KEY(parser_run_id,source_unit_alias_id,filing_id) REFERENCES corporate_reporting.xbrl_source_unit_alias(parser_run_id,source_unit_alias_id,filing_id));
CREATE TABLE IF NOT EXISTS corporate_reporting.fact_semantic_slot (
 fact_slot_id uuid PRIMARY KEY DEFAULT gen_random_uuid(), parser_run_id uuid NOT NULL, filing_id uuid NOT NULL, reporting_scope_id uuid NOT NULL, source_concept_id uuid NOT NULL, semantic_context_sha256 text NOT NULL, semantic_unit_sha256 text, xml_lang text, slot_sha256 text NOT NULL CHECK(slot_sha256 ~ '^[0-9a-f]{64}$'),
 UNIQUE(parser_run_id,filing_id,slot_sha256), UNIQUE(fact_slot_id,filing_id), UNIQUE(parser_run_id,fact_slot_id,filing_id), FOREIGN KEY(parser_run_id,filing_id) REFERENCES corporate_reporting.parser_run(parser_run_id,filing_id), FOREIGN KEY(reporting_scope_id,filing_id) REFERENCES corporate_reporting.reporting_scope(scope_id,filing_id), FOREIGN KEY(parser_run_id,source_concept_id,filing_id) REFERENCES corporate_reporting.source_concept(parser_run_id,source_concept_id,filing_id));
CREATE TABLE IF NOT EXISTS corporate_reporting.fact_slot_occurrence (
 parser_run_id uuid NOT NULL, fact_slot_id uuid NOT NULL, fact_occurrence_interpretation_id uuid NOT NULL, fact_occurrence_id uuid NOT NULL, filing_id uuid NOT NULL, PRIMARY KEY(parser_run_id,fact_slot_id,fact_occurrence_id), UNIQUE(parser_run_id,fact_occurrence_id), UNIQUE(parser_run_id,fact_slot_id,fact_occurrence_id,filing_id),
 FOREIGN KEY(parser_run_id,fact_slot_id,filing_id) REFERENCES corporate_reporting.fact_semantic_slot(parser_run_id,fact_slot_id,filing_id), FOREIGN KEY(parser_run_id,fact_occurrence_interpretation_id,fact_occurrence_id,filing_id) REFERENCES corporate_reporting.fact_occurrence_interpretation(parser_run_id,fact_occurrence_interpretation_id,fact_occurrence_id,filing_id));
-- Upgrade the prior unpublished 005 shape: filing equality alone did not prove
-- that a semantic slot owned its source concept through the same parser run.
ALTER TABLE corporate_reporting.fact_semantic_slot
 DROP CONSTRAINT IF EXISTS fact_semantic_slot_source_concept_id_filing_id_fkey;
DO $$ BEGIN
 IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conrelid='corporate_reporting.fact_semantic_slot'::regclass
                AND conname='fact_semantic_slot_parser_run_id_source_concept_id_filing_id_fkey') THEN
  ALTER TABLE corporate_reporting.fact_semantic_slot
   ADD CONSTRAINT fact_semantic_slot_parser_run_id_source_concept_id_filing_id_fkey
   FOREIGN KEY(parser_run_id,source_concept_id,filing_id)
   REFERENCES corporate_reporting.source_concept(parser_run_id,source_concept_id,filing_id);
 END IF;
END $$;
ALTER TABLE corporate_reporting.fact_slot_occurrence DROP CONSTRAINT IF EXISTS fact_slot_occurrence_fact_slot_id_fkey;
DO $$ BEGIN
 IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conrelid='corporate_reporting.fact_slot_occurrence'::regclass AND conname='fact_slot_occurrence_parser_run_id_fact_slot_id_filing_id_fkey') THEN
  ALTER TABLE corporate_reporting.fact_slot_occurrence ADD CONSTRAINT fact_slot_occurrence_parser_run_id_fact_slot_id_filing_id_fkey FOREIGN KEY(parser_run_id,fact_slot_id,filing_id) REFERENCES corporate_reporting.fact_semantic_slot(parser_run_id,fact_slot_id,filing_id);
 END IF;
END $$;
CREATE TABLE IF NOT EXISTS corporate_reporting.fact_resolution_revision (
 resolution_revision_id uuid PRIMARY KEY DEFAULT gen_random_uuid(), knowledge_revision_id uuid NOT NULL UNIQUE, axis_type text NOT NULL DEFAULT 'fact_resolution' CHECK(axis_type='fact_resolution'), object_key text NOT NULL, parser_run_id uuid NOT NULL, filing_id uuid NOT NULL, fact_slot_id uuid NOT NULL, selected_occurrence_id uuid,
 status text NOT NULL CHECK(status IN ('accepted_identical','conflict','deferred','rejected')), value_fingerprint text, reason_code text NOT NULL, recorded_at timestamptz NOT NULL DEFAULT now(),
 FOREIGN KEY(knowledge_revision_id,axis_type,object_key) REFERENCES corporate_reporting.knowledge_revision(knowledge_revision_id,axis_type,object_key), FOREIGN KEY(parser_run_id,fact_slot_id,filing_id) REFERENCES corporate_reporting.fact_semantic_slot(parser_run_id,fact_slot_id,filing_id), FOREIGN KEY(parser_run_id,fact_slot_id,selected_occurrence_id,filing_id) REFERENCES corporate_reporting.fact_slot_occurrence(parser_run_id,fact_slot_id,fact_occurrence_id,filing_id) DEFERRABLE INITIALLY DEFERRED,
 CHECK((status='accepted_identical' AND selected_occurrence_id IS NOT NULL) OR (status<>'accepted_identical' AND selected_occurrence_id IS NULL)));

CREATE TABLE IF NOT EXISTS corporate_reporting.canonical_concept (
 canonical_concept_id uuid PRIMARY KEY DEFAULT gen_random_uuid(), canonical_code text NOT NULL UNIQUE, label text NOT NULL, value_kind text NOT NULL, period_type text NOT NULL CHECK(period_type IN ('instant','duration')), status text NOT NULL CHECK(status IN ('proposed','accepted','deferred','rejected')));
CREATE TABLE IF NOT EXISTS corporate_reporting.concept_mapping_revision (
 mapping_revision_id uuid PRIMARY KEY DEFAULT gen_random_uuid(), knowledge_revision_id uuid NOT NULL UNIQUE, axis_type text NOT NULL DEFAULT 'concept_mapping' CHECK(axis_type='concept_mapping'), object_key text NOT NULL, source_concept_id uuid NOT NULL REFERENCES corporate_reporting.source_concept(source_concept_id), canonical_concept_id uuid NOT NULL REFERENCES corporate_reporting.canonical_concept(canonical_concept_id), reporting_scope_kind text NOT NULL,
 status text NOT NULL CHECK(status IN ('accepted','proposed','deferred','rejected')), rationale text NOT NULL, evidence_fingerprint text NOT NULL CHECK(evidence_fingerprint ~ '^[0-9a-f]{64}$'), recorded_at timestamptz NOT NULL DEFAULT now(), FOREIGN KEY(knowledge_revision_id,axis_type,object_key) REFERENCES corporate_reporting.knowledge_revision(knowledge_revision_id,axis_type,object_key));
CREATE TABLE IF NOT EXISTS corporate_reporting.expected_selection_revision (
 expected_selection_revision_id uuid PRIMARY KEY DEFAULT gen_random_uuid(), knowledge_revision_id uuid NOT NULL UNIQUE, axis_type text NOT NULL DEFAULT 'expected_selection' CHECK(axis_type='expected_selection'), object_key text NOT NULL, selection_code text NOT NULL, selection_version text NOT NULL, canonical_concept_id uuid NOT NULL REFERENCES corporate_reporting.canonical_concept(canonical_concept_id), scope_kind text NOT NULL, period_policy jsonb NOT NULL, applicability_predicate jsonb NOT NULL, rights_output_family text NOT NULL, selection_sha256 text NOT NULL CHECK(selection_sha256 ~ '^[0-9a-f]{64}$'), status text NOT NULL CHECK(status IN ('accepted','proposed','deferred','rejected')), recorded_at timestamptz NOT NULL DEFAULT now(), FOREIGN KEY(knowledge_revision_id,axis_type,object_key) REFERENCES corporate_reporting.knowledge_revision(knowledge_revision_id,axis_type,object_key));
CREATE TABLE IF NOT EXISTS corporate_reporting.fact_absence_revision (
 absence_revision_id uuid PRIMARY KEY DEFAULT gen_random_uuid(), knowledge_revision_id uuid NOT NULL UNIQUE, axis_type text NOT NULL DEFAULT 'fact_absence' CHECK(axis_type='fact_absence'), object_key text NOT NULL, filing_id uuid NOT NULL REFERENCES corporate_reporting.filing_submission(filing_id), expected_selection_revision_id uuid NOT NULL REFERENCES corporate_reporting.expected_selection_revision(expected_selection_revision_id), parser_run_id uuid NOT NULL, status text NOT NULL CHECK(status IN ('not_reported','not_applicable','unknown','parser_failed')), reason_code text NOT NULL, evidence_fingerprint text NOT NULL CHECK(evidence_fingerprint ~ '^[0-9a-f]{64}$'), recorded_at timestamptz NOT NULL DEFAULT now(), FOREIGN KEY(knowledge_revision_id,axis_type,object_key) REFERENCES corporate_reporting.knowledge_revision(knowledge_revision_id,axis_type,object_key), FOREIGN KEY(parser_run_id,filing_id) REFERENCES corporate_reporting.parser_run(parser_run_id,filing_id));
CREATE TABLE IF NOT EXISTS corporate_reporting.parser_run_selection_revision (
 parser_run_selection_revision_id uuid PRIMARY KEY DEFAULT gen_random_uuid(), knowledge_revision_id uuid NOT NULL UNIQUE, axis_type text NOT NULL DEFAULT 'parser_selection' CHECK(axis_type='parser_selection'), object_key text NOT NULL, filing_id uuid NOT NULL REFERENCES corporate_reporting.filing_submission(filing_id), parser_run_id uuid NOT NULL,
 status text NOT NULL CHECK(status IN ('accepted','proposed','deferred','rejected')), rationale text NOT NULL, recorded_at timestamptz NOT NULL DEFAULT now(), FOREIGN KEY(knowledge_revision_id,axis_type,object_key) REFERENCES corporate_reporting.knowledge_revision(knowledge_revision_id,axis_type,object_key), FOREIGN KEY(parser_run_id,filing_id) REFERENCES corporate_reporting.parser_run(parser_run_id,filing_id));
ALTER TABLE corporate_reporting.parser_run_selection_revision DROP CONSTRAINT IF EXISTS parser_run_selection_revision_status_check;
ALTER TABLE corporate_reporting.parser_run_selection_revision ADD CONSTRAINT parser_run_selection_revision_status_check CHECK(status IN ('accepted','proposed','deferred','rejected'));
CREATE TABLE IF NOT EXISTS corporate_reporting.knowledge_snapshot (
 knowledge_snapshot_id uuid PRIMARY KEY DEFAULT gen_random_uuid(), sec_cutoff timestamptz NOT NULL, knowledge_cutoff timestamptz NOT NULL, manifest_sha256 text NOT NULL CHECK(manifest_sha256 ~ '^[0-9a-f]{64}$'), recorded_at timestamptz NOT NULL DEFAULT now(), UNIQUE(sec_cutoff,knowledge_cutoff,manifest_sha256));
CREATE TABLE IF NOT EXISTS corporate_reporting.knowledge_snapshot_member (
 knowledge_snapshot_id uuid NOT NULL REFERENCES corporate_reporting.knowledge_snapshot(knowledge_snapshot_id), axis_type text NOT NULL, object_key text NOT NULL, knowledge_revision_id uuid NOT NULL, PRIMARY KEY(knowledge_snapshot_id,axis_type,object_key),
 FOREIGN KEY(knowledge_revision_id,axis_type,object_key) REFERENCES corporate_reporting.knowledge_revision(knowledge_revision_id,axis_type,object_key));
CREATE TABLE IF NOT EXISTS corporate_reporting.corporate_release_policy (
 policy_id uuid PRIMARY KEY DEFAULT gen_random_uuid(), policy_version text NOT NULL UNIQUE, policy_sha256 text NOT NULL UNIQUE CHECK(policy_sha256 ~ '^[0-9a-f]{64}$'), allowed_output_family text NOT NULL CHECK(allowed_output_family='private_analysis'));
CREATE TABLE IF NOT EXISTS corporate_reporting.corporate_release_eligibility_revision (
 eligibility_revision_id uuid PRIMARY KEY DEFAULT gen_random_uuid(), knowledge_revision_id uuid NOT NULL UNIQUE, axis_type text NOT NULL DEFAULT 'release_eligibility' CHECK(axis_type='release_eligibility'), object_key text NOT NULL, filing_id uuid NOT NULL REFERENCES corporate_reporting.filing_submission(filing_id), expected_selection_revision_id uuid NOT NULL REFERENCES corporate_reporting.expected_selection_revision(expected_selection_revision_id), knowledge_snapshot_id uuid NOT NULL REFERENCES corporate_reporting.knowledge_snapshot(knowledge_snapshot_id), policy_id uuid NOT NULL REFERENCES corporate_reporting.corporate_release_policy(policy_id),
 status text NOT NULL CHECK(status IN ('eligible','blocked')), reason_codes jsonb NOT NULL, source_manifest_sha256 text NOT NULL CHECK(source_manifest_sha256 ~ '^[0-9a-f]{64}$'), quality_decision_sha256 text NOT NULL CHECK(quality_decision_sha256 ~ '^[0-9a-f]{64}$'), recorded_at timestamptz NOT NULL DEFAULT now(), FOREIGN KEY(knowledge_revision_id,axis_type,object_key) REFERENCES corporate_reporting.knowledge_revision(knowledge_revision_id,axis_type,object_key));
CREATE TABLE IF NOT EXISTS corporate_reporting.corporate_release (
 release_id uuid PRIMARY KEY DEFAULT gen_random_uuid(), subscription_id text NOT NULL, selection_sha256 text NOT NULL CHECK(selection_sha256 ~ '^[0-9a-f]{64}$'), sec_cutoff timestamptz NOT NULL, knowledge_snapshot_id uuid NOT NULL REFERENCES corporate_reporting.knowledge_snapshot(knowledge_snapshot_id), release_fingerprint text NOT NULL UNIQUE CHECK(release_fingerprint ~ '^[0-9a-f]{64}$'), predecessor_release_id uuid REFERENCES corporate_reporting.corporate_release(release_id), eligibility_revision_id uuid NOT NULL UNIQUE REFERENCES corporate_reporting.corporate_release_eligibility_revision(eligibility_revision_id), publication_status text NOT NULL CHECK(publication_status IN ('private_ready','published_local','blocked')), UNIQUE(release_id,release_fingerprint));
CREATE TABLE IF NOT EXISTS corporate_reporting.corporate_release_item (
 release_id uuid NOT NULL REFERENCES corporate_reporting.corporate_release(release_id), item_ordinal integer NOT NULL CHECK(item_ordinal>0), item_fingerprint text NOT NULL CHECK(item_fingerprint ~ '^[0-9a-f]{64}$'), item_document jsonb NOT NULL, PRIMARY KEY(release_id,item_ordinal), UNIQUE(release_id,item_fingerprint));

-- Publication is anchored in the existing immutable release relation.  These bounded
-- columns avoid introducing a parallel generic publication subsystem.
ALTER TABLE corporate_reporting.corporate_release ADD COLUMN IF NOT EXISTS publication_target text;
ALTER TABLE corporate_reporting.corporate_release ADD COLUMN IF NOT EXISTS payload_sha256 text;
ALTER TABLE corporate_reporting.corporate_release ADD COLUMN IF NOT EXISTS recorded_at timestamptz NOT NULL DEFAULT now();
DO $$ BEGIN
 IF NOT EXISTS (SELECT 1 FROM pg_constraint WHERE conrelid='corporate_reporting.corporate_release'::regclass AND conname='ck_cr_release_payload_sha256') THEN
  ALTER TABLE corporate_reporting.corporate_release ADD CONSTRAINT ck_cr_release_payload_sha256
   CHECK(payload_sha256 IS NULL OR payload_sha256 ~ '^[0-9a-f]{64}$');
 END IF;
END $$;

-- Identity-bearing evidence and revision records are append-only. Reclosure is an
-- INSERT of a successor knowledge revision/parser attempt, never an UPDATE that
-- changes both payload and its claimed digest after admission.
CREATE OR REPLACE FUNCTION corporate_reporting.reject_admitted_update()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
 RAISE EXCEPTION 'admitted corporate reporting row is immutable: %.%', TG_TABLE_SCHEMA, TG_TABLE_NAME;
END $$;
DO $$
DECLARE table_name text;
BEGIN
 FOREACH table_name IN ARRAY ARRAY[
   'reporting_entity','entity_identifier','filing_submission','filing_document',
   'parser_run','reporting_scope','canonical_concept','corporate_release_policy',
   'taxonomy_set','source_concept','xbrl_context','xbrl_context_dimension',
   'xbrl_unit_semantics','xbrl_source_unit_alias','fact_occurrence',
   'fact_occurrence_interpretation','fact_semantic_slot','fact_slot_occurrence',
   'knowledge_revision','filing_relationship_revision',
   'source_concept_equivalence_revision','concept_mapping_revision',
   'expected_selection_revision','fact_absence_revision',
   'parser_run_selection_revision','fact_resolution_revision',
   'knowledge_snapshot','knowledge_snapshot_member',
   'corporate_release_eligibility_revision','corporate_release','corporate_release_item'
 ] LOOP
   EXECUTE format('DROP TRIGGER IF EXISTS %I ON corporate_reporting.%I',
                  'trg_cr_immutable_' || table_name, table_name);
   EXECUTE format('CREATE TRIGGER %I BEFORE UPDATE OR DELETE ON corporate_reporting.%I '
                  'FOR EACH ROW EXECUTE FUNCTION corporate_reporting.reject_admitted_update()',
                  'trg_cr_immutable_' || table_name, table_name);
 END LOOP;
END $$;

-- Logical digests are claims about owned payload, not caller-supplied identifiers.
-- Compact recursively; separator whitespace is removed structurally, never from strings.
CREATE OR REPLACE FUNCTION corporate_reporting.canonical_json(payload jsonb)
RETURNS text LANGUAGE sql IMMUTABLE STRICT PARALLEL SAFE AS $$
 SELECT CASE jsonb_typeof(payload)
  WHEN 'object' THEN '{' || COALESCE((SELECT string_agg(to_jsonb(key)::text || ':' || corporate_reporting.canonical_json(value),',' ORDER BY key COLLATE "C") FROM jsonb_each(payload)), '') || '}'
  WHEN 'array' THEN '[' || COALESCE((SELECT string_agg(corporate_reporting.canonical_json(value),',' ORDER BY ordinal) FROM jsonb_array_elements(payload) WITH ORDINALITY AS item(value,ordinal)), '') || ']'
  ELSE payload::text
 END
$$;
CREATE OR REPLACE FUNCTION corporate_reporting.canonical_sha256(payload jsonb)
RETURNS text LANGUAGE sql IMMUTABLE STRICT AS $$
 SELECT encode(digest(corporate_reporting.canonical_json(payload), 'sha256'), 'hex')
$$;
CREATE OR REPLACE FUNCTION corporate_reporting.canonical_sha256(payload text)
RETURNS text LANGUAGE sql IMMUTABLE STRICT AS $$
 SELECT encode(digest(payload, 'sha256'), 'hex')
$$;

CREATE OR REPLACE FUNCTION corporate_reporting.check_occurrence_logical_key()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
 IF NEW.occurrence_sha256 <> corporate_reporting.canonical_sha256(jsonb_build_object(
      'concept',NEW.source_concept_qname,'context',NEW.source_context_ref,
      'decimals',NEW.decimals,'lang',NEW.xml_lang,'nil',NEW.nil_flag,
      'ordinal',NEW.source_ordinal,'precision',NEW.precision,
      'unit',NEW.source_unit_ref,'value',NEW.lexical_value))
 THEN RAISE EXCEPTION 'source occurrence logical key mismatch'; END IF;
 RETURN NEW;
END $$;
DROP TRIGGER IF EXISTS trg_cr_occurrence_logical_key ON corporate_reporting.fact_occurrence;
CREATE CONSTRAINT TRIGGER trg_cr_occurrence_logical_key AFTER INSERT OR UPDATE ON corporate_reporting.fact_occurrence
 DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION corporate_reporting.check_occurrence_logical_key();

CREATE OR REPLACE FUNCTION corporate_reporting.context_payload(wanted_context_id uuid)
RETURNS jsonb LANGUAGE sql STABLE STRICT AS $$
 SELECT jsonb_build_array(
   c.entity_scheme,c.entity_value,
   CASE c.period_kind WHEN 'instant' THEN jsonb_build_array('instant',c.instant_date::text)
     WHEN 'duration' THEN jsonb_build_array('duration',c.start_date::text,c.end_date::text)
     ELSE jsonb_build_array('forever') END,
   COALESCE((SELECT jsonb_agg(jsonb_build_array(
       d.location,'{' || d.axis_namespace || '}' || d.axis_local_name,d.member_kind,
       CASE WHEN d.member_kind='explicit' THEN '{' || d.member_namespace || '}' || d.member_local_name ELSE NULL END,
       d.typed_member_sha256)
     ORDER BY d.location,'{' || d.axis_namespace || '}' || d.axis_local_name,d.member_kind,
       CASE WHEN d.member_kind='explicit' THEN '{' || d.member_namespace || '}' || d.member_local_name ELSE NULL END,
       d.typed_member_sha256)
     FROM corporate_reporting.xbrl_context_dimension d WHERE d.context_id=c.context_id),'[]'::jsonb))
 FROM corporate_reporting.xbrl_context c WHERE c.context_id=wanted_context_id
$$;

CREATE OR REPLACE FUNCTION corporate_reporting.check_context_logical_key()
RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE wanted uuid; actual text; claimed text;
BEGIN
 wanted := CASE WHEN TG_OP='DELETE' THEN OLD.context_id ELSE NEW.context_id END;
 SELECT corporate_reporting.canonical_sha256(corporate_reporting.context_payload(wanted)),
        semantic_context_sha256 INTO actual,claimed
 FROM corporate_reporting.xbrl_context WHERE context_id=wanted;
 IF actual IS DISTINCT FROM claimed THEN RAISE EXCEPTION 'semantic context logical key mismatch'; END IF;
 RETURN CASE WHEN TG_OP='DELETE' THEN OLD ELSE NEW END;
END $$;
DROP TRIGGER IF EXISTS trg_cr_context_logical_key ON corporate_reporting.xbrl_context;
CREATE CONSTRAINT TRIGGER trg_cr_context_logical_key AFTER INSERT OR UPDATE ON corporate_reporting.xbrl_context
 DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION corporate_reporting.check_context_logical_key();
DROP TRIGGER IF EXISTS trg_cr_dimension_context_logical_key ON corporate_reporting.xbrl_context_dimension;
CREATE CONSTRAINT TRIGGER trg_cr_dimension_context_logical_key AFTER INSERT OR UPDATE OR DELETE ON corporate_reporting.xbrl_context_dimension
 DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION corporate_reporting.check_context_logical_key();

CREATE OR REPLACE FUNCTION corporate_reporting.check_unit_logical_key()
RETURNS trigger LANGUAGE plpgsql AS $$
BEGIN
 IF NEW.semantic_unit_sha256 <> corporate_reporting.canonical_sha256(jsonb_build_object(
      'denominator',NEW.denominator_measures,'numerator',NEW.numerator_measures))
 THEN RAISE EXCEPTION 'semantic unit logical key mismatch'; END IF;
 RETURN NEW;
END $$;
DROP TRIGGER IF EXISTS trg_cr_unit_logical_key ON corporate_reporting.xbrl_unit_semantics;
CREATE CONSTRAINT TRIGGER trg_cr_unit_logical_key AFTER INSERT OR UPDATE ON corporate_reporting.xbrl_unit_semantics
 DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION corporate_reporting.check_unit_logical_key();

CREATE OR REPLACE FUNCTION corporate_reporting.check_slot_logical_key()
RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE expected text;
BEGIN
 SELECT corporate_reporting.canonical_sha256(jsonb_build_object(
   'accession',f.accession,'correspondence',jsonb_build_array(
     '{' || sc.namespace_uri || '}' || sc.local_name,
     corporate_reporting.context_payload(c.context_id),NEW.semantic_unit_sha256,NEW.xml_lang),
   'dts',t.dts_manifest_sha256)) INTO expected
 FROM corporate_reporting.filing_submission f
 JOIN corporate_reporting.source_concept sc ON sc.source_concept_id=NEW.source_concept_id
 JOIN corporate_reporting.taxonomy_set t ON t.taxonomy_set_id=sc.taxonomy_set_id
 JOIN corporate_reporting.xbrl_context c ON c.parser_run_id=NEW.parser_run_id
   AND c.filing_id=NEW.filing_id AND c.semantic_context_sha256=NEW.semantic_context_sha256
 WHERE f.filing_id=NEW.filing_id
   AND (NEW.semantic_unit_sha256 IS NULL OR EXISTS (
     SELECT 1 FROM corporate_reporting.xbrl_unit_semantics u
     WHERE u.parser_run_id=NEW.parser_run_id AND u.filing_id=NEW.filing_id
       AND u.semantic_unit_sha256=NEW.semantic_unit_sha256));
 IF expected IS NULL OR expected <> NEW.slot_sha256 THEN RAISE EXCEPTION 'semantic slot logical key mismatch'; END IF;
 RETURN NEW;
END $$;
DROP TRIGGER IF EXISTS trg_cr_slot_logical_key ON corporate_reporting.fact_semantic_slot;
CREATE CONSTRAINT TRIGGER trg_cr_slot_logical_key AFTER INSERT OR UPDATE ON corporate_reporting.fact_semantic_slot
 DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION corporate_reporting.check_slot_logical_key();

CREATE OR REPLACE FUNCTION corporate_reporting.check_resolution_logical_key()
RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE expected text;
BEGIN
 SELECT corporate_reporting.canonical_sha256(jsonb_build_object(
   'accession',f.accession,'axis','fact_resolution','parser_output',p.parser_output_sha256,
   'parser_run',NEW.parser_run_id::text,'slot',s.slot_sha256)) INTO expected
 FROM corporate_reporting.parser_run p
 JOIN corporate_reporting.filing_submission f ON f.filing_id=p.filing_id
 JOIN corporate_reporting.fact_semantic_slot s ON s.fact_slot_id=NEW.fact_slot_id
 WHERE p.parser_run_id=NEW.parser_run_id AND f.filing_id=NEW.filing_id;
 IF expected IS NULL OR expected <> NEW.object_key THEN RAISE EXCEPTION 'fact resolution logical key mismatch'; END IF;
 RETURN NEW;
END $$;
DROP TRIGGER IF EXISTS trg_cr_resolution_logical_key ON corporate_reporting.fact_resolution_revision;
CREATE CONSTRAINT TRIGGER trg_cr_resolution_logical_key AFTER INSERT OR UPDATE ON corporate_reporting.fact_resolution_revision
 DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION corporate_reporting.check_resolution_logical_key();

-- Accepted succession must be filing-identity scoped and acyclic. Deferred execution
-- permits a complete transaction to install evidence before checking the graph.
CREATE OR REPLACE FUNCTION corporate_reporting.check_filing_relationship() RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE mismatch boolean; cycle_found boolean;
BEGIN
 IF NEW.assertion_status <> 'accepted' THEN RETURN NEW; END IF;
 SELECT (p.filer_entity_id<>s.filer_entity_id OR p.report_period_end<>s.report_period_end) INTO mismatch
 FROM corporate_reporting.filing_submission p, corporate_reporting.filing_submission s
 WHERE p.filing_id=NEW.predecessor_filing_id AND s.filing_id=NEW.successor_filing_id;
 IF mismatch THEN RAISE EXCEPTION 'accepted filing relationship crosses filer/report period'; END IF;
 WITH RECURSIVE edges(a,b) AS (
   SELECT predecessor_filing_id,successor_filing_id FROM corporate_reporting.filing_relationship_revision WHERE assertion_status='accepted'
 ), walk(a,b) AS (SELECT a,b FROM edges UNION SELECT w.a,e.b FROM walk w JOIN edges e ON w.b=e.a)
 SELECT EXISTS(SELECT 1 FROM walk WHERE a=b) INTO cycle_found;
 IF cycle_found THEN RAISE EXCEPTION 'accepted filing relationship cycle'; END IF;
 RETURN NEW;
END $$;
DROP TRIGGER IF EXISTS trg_cr_filing_relationship ON corporate_reporting.filing_relationship_revision;
CREATE CONSTRAINT TRIGGER trg_cr_filing_relationship AFTER INSERT OR UPDATE ON corporate_reporting.filing_relationship_revision DEFERRABLE INITIALLY DEFERRED FOR EACH ROW EXECUTE FUNCTION corporate_reporting.check_filing_relationship();

INSERT INTO corporate_reporting.corporate_release_policy(policy_version,policy_sha256,allowed_output_family)
VALUES('private-analysis-v1',encode(digest('private-analysis-v1:private_analysis','sha256'),'hex'),'private_analysis') ON CONFLICT(policy_version) DO NOTHING;
INSERT INTO corporate_reporting.canonical_concept(canonical_code,label,value_kind,period_type,status)
VALUES('CORP_TOTAL_ASSETS','Total assets','numeric','instant','proposed') ON CONFLICT(canonical_code) DO NOTHING;

-- Eligibility itself is the persisted opaque authority root.  This view exposes only
-- database-derived state and cannot be inserted into or updated by production callers.
CREATE OR REPLACE VIEW corporate_reporting.corporate_authority_root AS
SELECT e.eligibility_revision_id AS root_id,
 CASE WHEN e.status='eligible' AND e.reason_codes='[]'::jsonb THEN 'accepted' ELSE 'blocked' END AS authority_status,
 p.allowed_output_family AS output_family, 'unresolved'::text AS redistribution_status,
 false AS remote_delivery_enabled,
 corporate_reporting.canonical_sha256(jsonb_build_object(
   'eligibility_revision_id',e.eligibility_revision_id,'filing_id',e.filing_id,
   'expected_selection_revision_id',e.expected_selection_revision_id,
   'knowledge_snapshot_id',e.knowledge_snapshot_id,'policy_id',e.policy_id,
   'status',e.status,'reason_codes',e.reason_codes,'source_manifest_sha256',e.source_manifest_sha256,
   'quality_decision_sha256',e.quality_decision_sha256)) AS closure_sha256,
 e.recorded_at AS admitted_at
FROM corporate_reporting.corporate_release_eligibility_revision e
JOIN corporate_reporting.corporate_release_policy p ON p.policy_id=e.policy_id;
CREATE OR REPLACE VIEW corporate_reporting.corporate_publication_act AS
SELECT r.release_id AS publication_act_id,r.eligibility_revision_id AS root_id,
 r.release_fingerprint AS release_sha256,r.publication_target AS target,r.payload_sha256 AS target_sha256,
 'published_local'::text AS status,r.recorded_at
FROM corporate_reporting.corporate_release r
WHERE r.publication_status='published_local';

-- Persisted Corporate-specific rights and exact quality authority.  These are local
-- revisions because the shared loader intentionally does not grant them.
CREATE TABLE IF NOT EXISTS corporate_reporting.corporate_rights_revision (
 rights_revision_id uuid PRIMARY KEY DEFAULT gen_random_uuid(), knowledge_revision_id uuid NOT NULL UNIQUE,
 axis_type text NOT NULL DEFAULT 'corporate_rights' CHECK(axis_type='corporate_rights'), object_key text NOT NULL,
 filing_id uuid NOT NULL REFERENCES corporate_reporting.filing_submission(filing_id),
 output_family text NOT NULL CHECK(output_family='private_analysis'),
 decision_status text NOT NULL CHECK(decision_status IN ('accepted','proposed','deferred','rejected')),
 redistribution_status text NOT NULL CHECK(redistribution_status IN ('unresolved','not_authorized')),
 remote_delivery_enabled boolean NOT NULL CHECK(remote_delivery_enabled=false),
 evidence_fingerprint text NOT NULL CHECK(evidence_fingerprint ~ '^[0-9a-f]{64}$'), recorded_at timestamptz NOT NULL DEFAULT now(),
 FOREIGN KEY(knowledge_revision_id,axis_type,object_key) REFERENCES corporate_reporting.knowledge_revision(knowledge_revision_id,axis_type,object_key));
CREATE TABLE IF NOT EXISTS corporate_reporting.corporate_quality_gate_revision (
 quality_gate_revision_id uuid PRIMARY KEY DEFAULT gen_random_uuid(), knowledge_revision_id uuid NOT NULL UNIQUE,
 axis_type text NOT NULL DEFAULT 'corporate_quality_gate' CHECK(axis_type='corporate_quality_gate'), object_key text NOT NULL,
 filing_id uuid NOT NULL REFERENCES corporate_reporting.filing_submission(filing_id),
 check_set jsonb NOT NULL CHECK(jsonb_typeof(check_set)='array' AND jsonb_array_length(check_set)>0),
 check_set_sha256 text NOT NULL CHECK(check_set_sha256 ~ '^[0-9a-f]{64}$'),
 decision_status text NOT NULL CHECK(decision_status IN ('accepted','rejected')), recorded_at timestamptz NOT NULL DEFAULT now(),
 FOREIGN KEY(knowledge_revision_id,axis_type,object_key) REFERENCES corporate_reporting.knowledge_revision(knowledge_revision_id,axis_type,object_key),
 CHECK(check_set_sha256=corporate_reporting.canonical_sha256(check_set)));

-- Admission formulas. Existing loader axes reproduce the loader's `_digest` JSON
-- preimages; the two local authority axes are defined here.
CREATE OR REPLACE FUNCTION corporate_reporting.check_authority_logical_key()
RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE expected_key text; expected_digest text; accession_value text; policy_version_value text;
BEGIN
 IF TG_TABLE_NAME='parser_run_selection_revision' THEN
  SELECT accession INTO accession_value FROM corporate_reporting.filing_submission WHERE filing_id=NEW.filing_id;
  expected_key:=corporate_reporting.canonical_sha256(jsonb_build_object('accession',accession_value,'axis','parser_selection'));
 ELSIF TG_TABLE_NAME='concept_mapping_revision' THEN
  SELECT f.accession INTO accession_value FROM corporate_reporting.source_concept s
   JOIN corporate_reporting.filing_submission f USING(filing_id) WHERE s.source_concept_id=NEW.source_concept_id;
  expected_key:=corporate_reporting.canonical_sha256(jsonb_build_object('accession',accession_value,'axis','concept_mapping',
    'scope',NEW.reporting_scope_kind,'source_concept',NEW.source_concept_id::text));
 ELSIF TG_TABLE_NAME='expected_selection_revision' THEN
  expected_digest:=corporate_reporting.canonical_sha256(jsonb_build_object(
    'applicability',NEW.applicability_predicate,'period_policy',NEW.period_policy,
    'rights_output_family',NEW.rights_output_family,'scope_kind',NEW.scope_kind,
    'selection_code',NEW.selection_code,'selection_version',NEW.selection_version));
  IF NEW.selection_sha256<>expected_digest THEN RAISE EXCEPTION 'expected selection digest mismatch'; END IF;
  expected_key:=corporate_reporting.canonical_sha256(jsonb_build_object(
    'applicability',NEW.applicability_predicate,'axis','expected_selection','period_policy',NEW.period_policy,
    'rights_output_family',NEW.rights_output_family,'scope_kind',NEW.scope_kind,
    'selection_code',NEW.selection_code,'selection_version',NEW.selection_version));
 ELSIF TG_TABLE_NAME='filing_relationship_revision' THEN
  SELECT accession INTO accession_value FROM corporate_reporting.filing_submission WHERE filing_id=NEW.predecessor_filing_id;
  SELECT corporate_reporting.canonical_sha256(jsonb_build_object('axis','filing_relationship','predecessor',accession_value,
    'successor',f.accession,'type',NEW.relationship_type)) INTO expected_key
   FROM corporate_reporting.filing_submission f WHERE f.filing_id=NEW.successor_filing_id;
 ELSIF TG_TABLE_NAME='source_concept_equivalence_revision' THEN
  expected_key:=corporate_reporting.canonical_sha256(jsonb_build_object('axis','concept_equivalence',
    'left',NEW.left_source_concept_id::text,'right',NEW.right_source_concept_id::text));
 ELSIF TG_TABLE_NAME='corporate_rights_revision' THEN
  SELECT accession INTO accession_value FROM corporate_reporting.filing_submission WHERE filing_id=NEW.filing_id;
  expected_key:=corporate_reporting.canonical_sha256(jsonb_build_object('axis','corporate_rights',
    'filing',accession_value,'output_family',NEW.output_family));
 ELSIF TG_TABLE_NAME='corporate_quality_gate_revision' THEN
  SELECT accession INTO accession_value FROM corporate_reporting.filing_submission WHERE filing_id=NEW.filing_id;
  IF NEW.check_set_sha256<>corporate_reporting.canonical_sha256(NEW.check_set) THEN
   RAISE EXCEPTION 'corporate quality digest mismatch'; END IF;
  expected_key:=corporate_reporting.canonical_sha256(jsonb_build_object('axis','corporate_quality_gate',
    'check_set_sha256',NEW.check_set_sha256,'filing',accession_value));
 ELSIF TG_TABLE_NAME='corporate_release_eligibility_revision' THEN
  SELECT f.accession,p.policy_version INTO accession_value,policy_version_value
   FROM corporate_reporting.filing_submission f,corporate_reporting.corporate_release_policy p
   WHERE f.filing_id=NEW.filing_id AND p.policy_id=NEW.policy_id;
  SELECT corporate_reporting.canonical_sha256(jsonb_build_object('axis','release_eligibility',
    'filing',accession_value,'policy',policy_version_value,'selection',x.selection_sha256,
    'snapshot',NEW.knowledge_snapshot_id::text)) INTO expected_key
   FROM corporate_reporting.expected_selection_revision x
   WHERE x.expected_selection_revision_id=NEW.expected_selection_revision_id;
 END IF;
 IF expected_key IS NULL OR NEW.object_key<>expected_key THEN
  RAISE EXCEPTION '% logical object key mismatch',TG_TABLE_NAME;
 END IF;
 RETURN NEW;
END $$;
DO $$ DECLARE t text; BEGIN FOREACH t IN ARRAY ARRAY[
 'concept_mapping_revision','parser_run_selection_revision','expected_selection_revision',
 'filing_relationship_revision','source_concept_equivalence_revision','corporate_rights_revision',
 'corporate_quality_gate_revision','corporate_release_eligibility_revision'] LOOP
 EXECUTE format('DROP TRIGGER IF EXISTS %I ON corporate_reporting.%I','trg_cr_authority_key_'||t,t);
 EXECUTE format('CREATE TRIGGER %I BEFORE INSERT ON corporate_reporting.%I FOR EACH ROW EXECUTE FUNCTION corporate_reporting.check_authority_logical_key()','trg_cr_authority_key_'||t,t);
END LOOP; END $$;

CREATE OR REPLACE FUNCTION corporate_reporting.check_snapshot_manifest()
RETURNS trigger LANGUAGE plpgsql AS $$
DECLARE wanted uuid; claimed text; actual text; cutoff timestamptz; sec timestamptz;
BEGIN
 wanted:=CASE WHEN TG_OP='DELETE' THEN OLD.knowledge_snapshot_id ELSE NEW.knowledge_snapshot_id END;
 SELECT manifest_sha256,knowledge_cutoff,sec_cutoff INTO claimed,cutoff,sec
 FROM corporate_reporting.knowledge_snapshot WHERE knowledge_snapshot_id=wanted;
 SELECT corporate_reporting.canonical_sha256(COALESCE(jsonb_agg(
   jsonb_build_array(m.axis_type,m.object_key,m.knowledge_revision_id::text)
   ORDER BY m.axis_type,m.object_key,m.knowledge_revision_id::text),'[]'::jsonb)) INTO actual
 FROM corporate_reporting.knowledge_snapshot_member m WHERE m.knowledge_snapshot_id=wanted;
 IF claimed IS DISTINCT FROM actual THEN RAISE EXCEPTION 'knowledge snapshot manifest mismatch'; END IF;
 IF EXISTS(SELECT 1 FROM corporate_reporting.knowledge_snapshot_member m
   JOIN corporate_reporting.knowledge_revision k USING(knowledge_revision_id)
   WHERE m.knowledge_snapshot_id=wanted AND (k.recorded_at>cutoff OR
    (k.source_effective_at IS NOT NULL AND k.source_effective_at>sec) OR EXISTS(
      SELECT 1 FROM corporate_reporting.knowledge_revision child
      WHERE child.predecessor_revision_id=k.knowledge_revision_id AND child.recorded_at<=cutoff)))
 THEN RAISE EXCEPTION 'knowledge snapshot member is future or nonterminal at cutoff'; END IF;
 RETURN CASE WHEN TG_OP='DELETE' THEN OLD ELSE NEW END;
END $$;
DROP TRIGGER IF EXISTS trg_cr_snapshot_manifest ON corporate_reporting.knowledge_snapshot_member;
CREATE CONSTRAINT TRIGGER trg_cr_snapshot_manifest AFTER INSERT OR UPDATE OR DELETE
 ON corporate_reporting.knowledge_snapshot_member DEFERRABLE INITIALLY DEFERRED
 FOR EACH ROW EXECUTE FUNCTION corporate_reporting.check_snapshot_manifest();

-- Immutable exact reservation is the publication act of authority. Completion records
-- that the already-reserved bytes were durably installed; neither row is mutable.
CREATE TABLE IF NOT EXISTS corporate_reporting.corporate_publication_reservation (
 publication_reservation_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
 root_id uuid NOT NULL UNIQUE REFERENCES corporate_reporting.corporate_release_eligibility_revision(eligibility_revision_id),
 release_sha256 text NOT NULL CHECK(release_sha256 ~ '^[0-9a-f]{64}$'), target text NOT NULL UNIQUE,
 target_sha256 text NOT NULL CHECK(target_sha256 ~ '^[0-9a-f]{64}$'), reserved_at timestamptz NOT NULL DEFAULT now());
CREATE TABLE IF NOT EXISTS corporate_reporting.corporate_publication_completion (
 publication_completion_id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
 publication_reservation_id uuid NOT NULL UNIQUE REFERENCES corporate_reporting.corporate_publication_reservation(publication_reservation_id),
 completed_at timestamptz NOT NULL DEFAULT now());
DO $$ DECLARE t text; BEGIN FOREACH t IN ARRAY ARRAY['corporate_rights_revision','corporate_quality_gate_revision','corporate_publication_reservation','corporate_publication_completion'] LOOP
 EXECUTE format('DROP TRIGGER IF EXISTS %I ON corporate_reporting.%I','trg_cr_immutable_'||t,t);
 EXECUTE format('CREATE TRIGGER %I BEFORE UPDATE OR DELETE ON corporate_reporting.%I FOR EACH ROW EXECUTE FUNCTION corporate_reporting.reject_admitted_update()','trg_cr_immutable_'||t,t);
END LOOP; END $$;

CREATE OR REPLACE VIEW corporate_reporting.corporate_publication_authority AS
SELECT r.publication_reservation_id AS publication_act_id,r.root_id,r.release_sha256,r.target,r.target_sha256,
 CASE WHEN c.publication_completion_id IS NULL THEN 'reserved' ELSE 'completed' END AS status,
 r.reserved_at AS recorded_at,c.completed_at
FROM corporate_reporting.corporate_publication_reservation r
LEFT JOIN corporate_reporting.corporate_publication_completion c USING(publication_reservation_id);
