from __future__ import annotations

from dataclasses import replace
from hashlib import sha256
import json
from pathlib import Path
import shutil
import subprocess
from collections.abc import Iterator
import uuid

import pytest

from macroforge.sec_corporate_reporting import parse_instance
from macroforge.sec_corporate_reporting_loader import (
    CorporateFilingLoad,
    CorporateReportingStore,
    FilingDocumentLoad,
    IdentityConflict,
    QualityGateError,
    build_protected_gatos_loads,
    load_corporate_filings_to_postgres,
    load_protected_gatos_to_postgres,
)

PROJECT_ROOT = Path(__file__).parents[1]
FIXTURE = Path(__file__).parent / "fixtures/sec_corporate_reporting/compact-instance.xml"
MIGRATION = PROJECT_ROOT / "db/migrations/005_corporate_reporting_foundation.sql"
FOUNDATION = PROJECT_ROOT / "db/migrations/001_v0_schema_foundation.sql"
PROTECTED = Path("/tmp/macroforge-corporate-gatos-freeze-6DQdCj")
PROTECTED_INVENTORY = PROTECTED / "derived/evidence-inventory.json"
KNOWLEDGE_CUTOFF = "2026-08-09T23:00:00Z"
POSTGRES_TOOLS = all(shutil.which(command) for command in ("psql", "createdb", "dropdb"))
POSTGRES_SKIP = pytest.mark.skipif(
    not POSTGRES_TOOLS or not PROTECTED_INVENTORY.is_file(),
    reason="psql database tools or protected Gatos fixture unavailable",
)
POSTGRES_ONLY = pytest.mark.skipif(not POSTGRES_TOOLS, reason="psql database tools unavailable")


def _psql(database: str, sql: str) -> str:
    result = subprocess.run(
        ["psql", "-X", "-v", "ON_ERROR_STOP=1", "-A", "-t", "-d", database],
        input=sql, text=True, capture_output=True, check=True,
    )
    return result.stdout.strip()


def _psql_file(database: str, path: Path) -> None:
    subprocess.run(
        ["psql", "-X", "-v", "ON_ERROR_STOP=1", "-q", "-d", database, "-f", str(path)],
        text=True, capture_output=True, check=True,
    )


@pytest.fixture
def corporate_postgres() -> Iterator[str]:
    database = f"macroforge_cr_{uuid.uuid4().hex[:12]}"
    subprocess.run(["createdb", database], check=True, capture_output=True, text=True)
    try:
        yield database
    finally:
        subprocess.run(["dropdb", "--if-exists", database], check=True, capture_output=True, text=True)


def test_loader_exact_replay_conflict_and_rollback() -> None:
    report = parse_instance(FIXTURE, accession="0000000001-24-000001", dts_manifest_sha256="a" * 64)
    store = CorporateReportingStore()
    first = store.load(report, source_manifest_sha256="b" * 64)
    second = store.load(report, source_manifest_sha256="b" * 64)
    assert first == second and store.filing_count == 1 and store.occurrence_count == 5
    before = store.fingerprint
    with pytest.raises(IdentityConflict):
        store.load(report, source_manifest_sha256="c" * 64)
    assert store.fingerprint == before
    conflict = parse_instance(Path(__file__).parent / "fixtures/sec_corporate_reporting/compact-conflict.xml", accession="0000000001-24-000002", dts_manifest_sha256="a" * 64)
    store.load(conflict, source_manifest_sha256="d" * 64)
    assert store.filing_count == 2
    assert store.occurrence_count == 7
    assert store.conflicting_slot_count == 1


def test_complete_filing_chain_mismatches_fail_on_copied_roots(tmp_path: Path) -> None:
    if not PROTECTED_INVENTORY.is_file():
        pytest.skip("protected fixture unavailable (never treated as pass)")
    mutations = (
        ("document", "original/gato-20211231x10k_htm.xml", "bytes"),
        ("metadata", "submissions.json", "bytes"),
        ("archive-index", "original-index.json", "bytes"),
        ("missing", "amendment/gato-20211231.xsd", "missing"),
    )
    for name, relative, kind in mutations:
        root = tmp_path / name
        shutil.copytree(PROTECTED, root)
        path = root / relative
        if kind == "missing":
            path.unlink()
        else:
            path.write_bytes(path.read_bytes() + b"\n")
        with pytest.raises(QualityGateError, match="identity|missing"):
            build_protected_gatos_loads(root)


def test_migration_exact_model_and_scoped_integrity_contract() -> None:
    sql = MIGRATION.read_text()
    expected = {
        "reporting_entity", "entity_identifier", "filing_submission", "filing_document",
        "filing_relationship_revision", "reporting_scope", "taxonomy_set", "source_concept",
        "source_concept_equivalence_revision", "xbrl_context", "xbrl_context_dimension",
        "xbrl_unit_semantics", "parser_run", "xbrl_source_unit_alias", "fact_occurrence",
        "fact_occurrence_interpretation",
        "fact_semantic_slot", "fact_slot_occurrence", "fact_resolution_revision",
        "canonical_concept", "knowledge_revision", "concept_mapping_revision",
        "expected_selection_revision", "fact_absence_revision", "parser_run_selection_revision",
        "knowledge_snapshot", "knowledge_snapshot_member", "corporate_release_policy",
        "corporate_release_eligibility_revision", "corporate_release", "corporate_release_item",
        "corporate_rights_revision", "corporate_quality_gate_revision",
        "corporate_publication_reservation", "corporate_publication_completion",
    }
    created = {line.split()[5].split(".")[-1] for line in sql.splitlines() if line.startswith("CREATE TABLE IF NOT EXISTS corporate_reporting.")}
    assert expected == created
    assert sql.count("FOREIGN KEY") >= 25
    assert "fact_slot_occurrence" in sql and "DEFERRABLE INITIALLY DEFERRED" in sql
    assert "curated.dim_territory" not in sql and "staging.wdi_observation" not in sql
    assert "DROP SCHEMA" not in sql


@POSTGRES_SKIP
def test_postgresql_migration_rollback_clean_apply_and_reapply(corporate_postgres: str) -> None:
    _psql_file(corporate_postgres, FOUNDATION)
    # psql include executes the complete migration inside this explicit transaction.
    _psql(corporate_postgres, f"BEGIN;\n\\i {MIGRATION}\nROLLBACK;\n")
    assert _psql(corporate_postgres, "SELECT to_regnamespace('corporate_reporting') IS NULL;") == "t"
    _psql_file(corporate_postgres, MIGRATION)
    _psql_file(corporate_postgres, MIGRATION)
    assert _psql(corporate_postgres, "SELECT count(*) FROM pg_tables WHERE schemaname='corporate_reporting';") == "31"


@POSTGRES_SKIP
def test_postgresql_exact_gatos_load_replay_counts_values_and_boundaries(corporate_postgres: str) -> None:
    _psql_file(corporate_postgres, FOUNDATION)
    _psql_file(corporate_postgres, MIGRATION)
    territory_before = _psql(corporate_postgres, "SELECT count(*) FROM curated.dim_territory;")
    oip_before = _psql(corporate_postgres, "SELECT count(*) FROM curated.fact_observation;")
    wdi_before = _psql(corporate_postgres, "SELECT count(*) FROM staging.wdi_observation;")

    first = load_protected_gatos_to_postgres(database_url=corporate_postgres, fixture_root=PROTECTED,
                                             knowledge_cutoff=KNOWLEDGE_CUTOFF)
    second = load_protected_gatos_to_postgres(database_url=corporate_postgres, fixture_root=PROTECTED,
                                              knowledge_cutoff=KNOWLEDGE_CUTOFF)
    assert first == second
    assert (first.filing_count, first.document_count, first.occurrence_count,
            first.slot_count, first.relationship_count) == (2, 14, 1568, 1485, 1)

    counts = json.loads(_psql(corporate_postgres, """
      SELECT json_build_array(
        (SELECT count(*) FROM corporate_reporting.parser_run),
        (SELECT count(*) FROM corporate_reporting.taxonomy_set),
        (SELECT count(*) FROM corporate_reporting.xbrl_context),
        (SELECT count(*) FROM corporate_reporting.xbrl_unit_semantics),
        (SELECT count(*) FROM corporate_reporting.xbrl_source_unit_alias),
        (SELECT count(*) FROM corporate_reporting.fact_occurrence),
        (SELECT count(*) FROM corporate_reporting.fact_occurrence_interpretation),
        (SELECT count(*) FROM corporate_reporting.fact_semantic_slot),
        (SELECT count(*) FROM corporate_reporting.fact_slot_occurrence),
        (SELECT count(*) FROM corporate_reporting.fact_resolution_revision),
        (SELECT count(*) FROM corporate_reporting.parser_run_selection_revision),
        (SELECT count(*) FROM corporate_reporting.source_concept_equivalence_revision),
        (SELECT count(*) FROM corporate_reporting.concept_mapping_revision),
        (SELECT count(*) FROM meta.dataset_release r JOIN meta.source s USING(source_id) WHERE s.source_code='SEC_CORPORATE_REPORTING'),
        (SELECT count(*) FROM meta.pipeline_run WHERE pipeline_name='sec_corporate_reporting'),
        (SELECT count(*) FROM meta.quality_check q JOIN meta.pipeline_run p USING(pipeline_run_id) WHERE p.pipeline_name='sec_corporate_reporting'),
        (SELECT count(*) FROM meta.lineage_event l JOIN meta.pipeline_run p USING(pipeline_run_id) WHERE p.pipeline_name='sec_corporate_reporting'));
    """))
    assert counts == [2, 2, 382, 16, 16, 1568, 1568, 1485, 1568, 1485, 2, 2, 4, 2, 2, 46, 2]
    assert _psql(corporate_postgres, """
      SELECT string_agg(accession,',' ORDER BY accession)
      FROM corporate_reporting.filing_submission;
    """) == "0001104659-23-034448,0001104659-23-074911"
    assert _psql(corporate_postgres, """
      SELECT string_agg(accession || ':' || n::text,',' ORDER BY accession)
      FROM (
        SELECT f.accession, count(*) AS n
        FROM corporate_reporting.source_concept c
        JOIN corporate_reporting.filing_submission f USING(filing_id)
        WHERE c.declaration_status='declared' GROUP BY f.accession
      ) declared;
    """) == "0001104659-23-034448:119,0001104659-23-074911:127"

    # Persisted selected occurrences retain all four representative revisions.
    values = _psql(corporate_postgres, """
      SELECT c.local_name || ':' || string_agg(f.accession || '=' || o.lexical_value,',' ORDER BY f.accession)
      FROM corporate_reporting.fact_resolution_revision r
      JOIN corporate_reporting.fact_occurrence o ON o.fact_occurrence_id=r.selected_occurrence_id
      JOIN corporate_reporting.fact_occurrence_interpretation i
        ON i.parser_run_id=r.parser_run_id AND i.fact_occurrence_id=o.fact_occurrence_id
      JOIN corporate_reporting.source_concept c USING(source_concept_id)
      JOIN corporate_reporting.xbrl_context x USING(context_id)
      JOIN corporate_reporting.filing_submission f ON f.filing_id=o.filing_id
      WHERE (c.local_name='Assets' AND x.period_kind='instant' AND x.instant_date='2021-12-31'
             AND NOT EXISTS (SELECT 1 FROM corporate_reporting.xbrl_context_dimension d WHERE d.context_id=x.context_id)
             AND o.lexical_value IN ('367111000','345248000'))
         OR (c.local_name='EarningsPerShareDiluted' AND x.period_kind='duration'
             AND x.start_date='2021-01-01' AND x.end_date='2021-12-31'
             AND NOT EXISTS (SELECT 1 FROM corporate_reporting.xbrl_context_dimension d WHERE d.context_id=x.context_id)
             AND o.lexical_value IN ('-0.68','-1.03'))
         OR (c.local_name='ImpairmentOfInvestmentInAffiliates' AND x.period_kind='duration'
             AND x.start_date='2021-01-01' AND x.end_date='2021-12-31'
             AND (SELECT count(*) FROM corporate_reporting.xbrl_context_dimension d WHERE d.context_id=x.context_id)=2
             AND o.lexical_value IN ('51564000','80348000'))
         OR (c.local_name='AmendmentFlag' AND o.lexical_value IN ('false','true'))
      GROUP BY c.local_name ORDER BY c.local_name;
    """).splitlines()
    assert values == [
        "AmendmentFlag:0001104659-23-034448=false,0001104659-23-074911=true",
        "Assets:0001104659-23-034448=367111000,0001104659-23-074911=345248000",
        "EarningsPerShareDiluted:0001104659-23-034448=-0.68,0001104659-23-074911=-1.03",
        "ImpairmentOfInvestmentInAffiliates:0001104659-23-034448=51564000,0001104659-23-074911=80348000",
    ]
    assert _psql(corporate_postgres, "SELECT count(*) FROM corporate_reporting.concept_mapping_revision WHERE status='accepted';") == "0"
    assert _psql(corporate_postgres, "SELECT count(*) FROM corporate_reporting.source_concept_equivalence_revision WHERE status='accepted';") == "0"
    assert _psql(corporate_postgres, "SELECT assertion_status FROM corporate_reporting.filing_relationship_revision;") == "accepted"
    assert _psql(corporate_postgres, "SELECT count(*) FROM corporate_reporting.knowledge_snapshot_member;") == "1495"
    assert _psql(corporate_postgres, "SELECT bool_and(sec_cutoff <> knowledge_cutoff) FROM corporate_reporting.knowledge_snapshot;") == "t"
    assert _psql(corporate_postgres, "SELECT status FROM corporate_reporting.expected_selection_revision WHERE selection_code='CORP_TOTAL_ASSETS';") == "proposed"
    assert json.loads(_psql(corporate_postgres, "SELECT reason_codes FROM corporate_reporting.corporate_release_eligibility_revision;")) == ["human_mapping_authority_pending", "redistribution_rights_unknown"]
    assert _psql(corporate_postgres, "SELECT status FROM corporate_reporting.corporate_release_eligibility_revision;") == "blocked"
    assert _psql(corporate_postgres, "SELECT count(*) FROM corporate_reporting.corporate_release;") == "0"
    quality_states = json.loads(_psql(corporate_postgres, """
      SELECT json_object_agg(check_name, check_status) FROM meta.quality_check
      WHERE check_name IN ('artifact_integrity','extraction_completeness','filing_integrity',
       'context_integrity','dimension_integrity','unit_integrity','identity_integrity',
       'conflict_integrity','mapping_authority','temporal_cutoffs','rights_policy','release_completeness');
    """))
    assert quality_states["mapping_authority"] == "warn"
    assert quality_states["rights_policy"] == "warn"
    assert quality_states["release_completeness"] == "fail"
    assert _psql(corporate_postgres, "SELECT count(*) FROM curated.dim_territory;") == territory_before
    assert _psql(corporate_postgres, "SELECT count(*) FROM curated.fact_observation;") == oip_before
    assert _psql(corporate_postgres, "SELECT count(*) FROM staging.wdi_observation;") == wdi_before


@POSTGRES_SKIP
def test_postgresql_manifest_conflict_rolls_back_entire_batch(corporate_postgres: str) -> None:
    _psql_file(corporate_postgres, FOUNDATION)
    _psql_file(corporate_postgres, MIGRATION)
    loads = build_protected_gatos_loads(PROTECTED)
    load_corporate_filings_to_postgres(loads, database_url=corporate_postgres,
                                       knowledge_cutoff=KNOWLEDGE_CUTOFF)
    before = _psql(corporate_postgres, """
      SELECT json_build_array(
       (SELECT count(*) FROM corporate_reporting.filing_submission),
       (SELECT count(*) FROM corporate_reporting.fact_occurrence),
       (SELECT count(*) FROM meta.pipeline_run),
       (SELECT count(*) FROM meta.lineage_event));
    """)
    conflicting = replace(loads[0], source_manifest_sha256="f" * 64)
    with pytest.raises(IdentityConflict, match="CORPORATE_REPORTING_IDENTITY_CONFLICT"):
        load_corporate_filings_to_postgres((loads[1], conflicting), database_url=corporate_postgres,
                                           knowledge_cutoff=KNOWLEDGE_CUTOFF)
    after = _psql(corporate_postgres, """
      SELECT json_build_array(
       (SELECT count(*) FROM corporate_reporting.filing_submission),
       (SELECT count(*) FROM corporate_reporting.fact_occurrence),
       (SELECT count(*) FROM meta.pipeline_run),
       (SELECT count(*) FROM meta.lineage_event));
    """)
    assert after == before == "[2, 1568, 2, 2]"


@POSTGRES_SKIP
def test_postgresql_composite_scope_constraints_reject_cross_bound_evidence(corporate_postgres: str) -> None:
    _psql_file(corporate_postgres, FOUNDATION)
    _psql_file(corporate_postgres, MIGRATION)
    load_protected_gatos_to_postgres(database_url=corporate_postgres, fixture_root=PROTECTED,
                                     knowledge_cutoff=KNOWLEDGE_CUTOFF)
    adversarial = (
        # Revision payload cannot borrow a knowledge key from another axis.
        """INSERT INTO corporate_reporting.expected_selection_revision(
             expected_selection_revision_id,knowledge_revision_id,object_key,selection_code,selection_version,
             canonical_concept_id,scope_kind,period_policy,applicability_predicate,rights_output_family,
             selection_sha256,status,recorded_at)
           SELECT gen_random_uuid(),k.knowledge_revision_id,k.object_key,'FORGED','v1',e.canonical_concept_id,
             e.scope_kind,e.period_policy,e.applicability_predicate,e.rights_output_family,e.selection_sha256,
             'accepted',now()
           FROM corporate_reporting.knowledge_revision k
           CROSS JOIN LATERAL (SELECT * FROM corporate_reporting.expected_selection_revision LIMIT 1) e
           WHERE k.axis_type='parser_selection' LIMIT 1;""",
        # Context dimensions are filing-scoped through the composite context FK.
        """INSERT INTO corporate_reporting.xbrl_context_dimension(
             context_dimension_id,context_id,filing_id,location,axis_namespace,axis_local_name,
             member_kind,member_namespace,member_local_name)
           SELECT gen_random_uuid(),c.context_id,other.filing_id,'segment','urn:forged','Axis',
             'explicit','urn:forged','Member'
           FROM corporate_reporting.xbrl_context c
           CROSS JOIN LATERAL (SELECT filing_id FROM corporate_reporting.filing_submission
                               WHERE filing_id<>c.filing_id LIMIT 1) other LIMIT 1;""",
        # A resolution parser must own the selected slot and filing tuple.
        """UPDATE corporate_reporting.fact_resolution_revision r SET parser_run_id=other.parser_run_id
           FROM LATERAL (SELECT parser_run_id FROM corporate_reporting.parser_run
                         WHERE parser_run_id<>r.parser_run_id LIMIT 1) other
           WHERE r.resolution_revision_id=(SELECT resolution_revision_id
                 FROM corporate_reporting.fact_resolution_revision LIMIT 1);""",
        # Relationship prose evidence must be a document of the successor filing.
        """UPDATE corporate_reporting.filing_relationship_revision r SET evidence_document_id=d.document_id
           FROM corporate_reporting.filing_document d
           WHERE d.filing_id=r.predecessor_filing_id;""",
    )
    for statement in adversarial:
        with pytest.raises(subprocess.CalledProcessError):
            _psql(corporate_postgres, statement)


@POSTGRES_SKIP
def test_postgresql_same_manifest_immutable_replay_variants_and_shared_meta_conflict_roll_back(
    corporate_postgres: str,
) -> None:
    _psql_file(corporate_postgres, FOUNDATION)
    _psql_file(corporate_postgres, MIGRATION)
    loads = build_protected_gatos_loads(PROTECTED)
    load_corporate_filings_to_postgres(loads, database_url=corporate_postgres,
                                       knowledge_cutoff=KNOWLEDGE_CUTOFF)
    before = _psql(corporate_postgres, """SELECT json_build_array(
      (SELECT count(*) FROM corporate_reporting.filing_submission),
      (SELECT count(*) FROM corporate_reporting.filing_document),
      (SELECT count(*) FROM corporate_reporting.parser_run),
      (SELECT count(*) FROM corporate_reporting.taxonomy_set),
      (SELECT count(*) FROM meta.pipeline_run));""")
    base = loads[0]
    non_instance = next(i for i, d in enumerate(base.documents) if d.role != "sec_rendered_xbrl_instance")
    documents = list(base.documents)
    documents[non_instance] = replace(documents[non_instance], sha256="9" * 64)
    variants = (
        replace(base, documents=tuple(documents)),
        replace(base, form_type="8-K"),
        replace(base, dts_manifest_sha256="8" * 64,
                report=replace(base.report, dts_manifest_sha256="8" * 64)),
    )
    for variant in variants:
        with pytest.raises(IdentityConflict, match="CORPORATE_REPORTING_IDENTITY_CONFLICT"):
            load_corporate_filings_to_postgres((variant,), database_url=corporate_postgres,
                                               knowledge_cutoff=KNOWLEDGE_CUTOFF)
        assert _psql(corporate_postgres, """SELECT json_build_array(
          (SELECT count(*) FROM corporate_reporting.filing_submission),
          (SELECT count(*) FROM corporate_reporting.filing_document),
          (SELECT count(*) FROM corporate_reporting.parser_run),
          (SELECT count(*) FROM corporate_reporting.taxonomy_set),
          (SELECT count(*) FROM meta.pipeline_run));""") == before

    fake_output = replace(base, report=replace(base.report, parser_output_sha256="7" * 64))
    with pytest.raises(QualityGateError, match="parser output digest"):
        load_corporate_filings_to_postgres((fake_output,), database_url=corporate_postgres,
                                           knowledge_cutoff=KNOWLEDGE_CUTOFF)
    assert _psql(corporate_postgres, """SELECT json_build_array(
      (SELECT count(*) FROM corporate_reporting.filing_submission),
      (SELECT count(*) FROM corporate_reporting.filing_document),
      (SELECT count(*) FROM corporate_reporting.parser_run),
      (SELECT count(*) FROM corporate_reporting.taxonomy_set),
      (SELECT count(*) FROM meta.pipeline_run));""") == before

    _psql(corporate_postgres, "UPDATE meta.source SET source_name='forged' WHERE source_code='SEC_CORPORATE_REPORTING';")
    with pytest.raises(IdentityConflict, match="meta.source"):
        load_corporate_filings_to_postgres((base,), database_url=corporate_postgres,
                                           knowledge_cutoff=KNOWLEDGE_CUTOFF)
    assert _psql(corporate_postgres, "SELECT count(*) FROM corporate_reporting.filing_submission;") == "2"


@POSTGRES_SKIP
def test_postgresql_independent_parser_attempts_append_only_and_fail_closed(
    corporate_postgres: str,
) -> None:
    _psql_file(corporate_postgres, FOUNDATION)
    _psql_file(corporate_postgres, MIGRATION)
    initial = build_protected_gatos_loads(PROTECTED)
    load_corporate_filings_to_postgres(initial, database_url=corporate_postgres,
                                       knowledge_cutoff=KNOWLEDGE_CUTOFF)

    proposed = tuple(replace(load, parser_attempt_key="independent-review-v2",
                             parser_selection_status="proposed") for load in initial)
    first_proposal = load_corporate_filings_to_postgres(
        proposed, database_url=corporate_postgres, knowledge_cutoff=KNOWLEDGE_CUTOFF,
    )
    replay = load_corporate_filings_to_postgres(
        proposed, database_url=corporate_postgres, knowledge_cutoff=KNOWLEDGE_CUTOFF,
    )
    assert first_proposal == replay

    counts = json.loads(_psql(corporate_postgres, """
      SELECT json_build_array(
        (SELECT count(*) FROM corporate_reporting.parser_run),
        (SELECT count(*) FROM corporate_reporting.parser_run_selection_revision WHERE status='accepted'),
        (SELECT count(*) FROM corporate_reporting.parser_run_selection_revision WHERE status='proposed'),
        (SELECT count(*) FROM corporate_reporting.fact_occurrence),
        (SELECT count(*) FROM corporate_reporting.fact_resolution_revision),
        (SELECT count(*) FROM meta.pipeline_run WHERE pipeline_name='sec_corporate_reporting'),
        (SELECT count(*) FROM corporate_reporting.corporate_release));
    """))
    assert counts == [4, 2, 2, 1568, 2970, 4, 0]
    # Each stable filing-selection object is one root/child chain, never a fork.
    assert _psql(corporate_postgres, """
      SELECT count(*) FROM (
        SELECT object_key
        FROM corporate_reporting.knowledge_revision
        WHERE axis_type='parser_selection'
        GROUP BY object_key
        HAVING count(*)=2
           AND count(*) FILTER (WHERE predecessor_revision_id IS NULL)=1
      ) chains;
    """) == "2"
    assert _psql(corporate_postgres, """
      SELECT count(*) FROM corporate_reporting.knowledge_revision parent
      JOIN corporate_reporting.knowledge_revision child
        ON child.predecessor_revision_id=parent.knowledge_revision_id
      WHERE parent.axis_type='parser_selection';
    """) == "2"
    # Snapshots retain the explicitly accepted member, not the proposed chain tip.
    assert _psql(corporate_postgres, """
      SELECT count(*) FROM corporate_reporting.knowledge_snapshot_member m
      JOIN corporate_reporting.parser_run_selection_revision s
        ON s.knowledge_revision_id=m.knowledge_revision_id
      WHERE m.axis_type='parser_selection' AND s.status='accepted';
    """) == "2"
    assert _psql(corporate_postgres, """
      SELECT count(*) FROM corporate_reporting.knowledge_snapshot_member m
      JOIN corporate_reporting.parser_run_selection_revision s
        ON s.knowledge_revision_id=m.knowledge_revision_id
      WHERE m.axis_type='parser_selection' AND s.status='proposed';
    """) == "0"


@POSTGRES_SKIP
def test_postgresql_n_plus_one_conflict_preserves_every_occurrence_and_blocks_selection(
    corporate_postgres: str,
) -> None:
    _psql_file(corporate_postgres, FOUNDATION)
    _psql_file(corporate_postgres, MIGRATION)
    conflict_path = PROJECT_ROOT / "tests/fixtures/sec_corporate_reporting/compact-conflict.xml"
    report = parse_instance(
        conflict_path,
        accession="0000000001-24-000099",
        dts_manifest_sha256="a" * 64,
    )
    documents = (
        FilingDocumentLoad("compact-primary.htm", "primary_inline_xbrl", "file:///compact-primary.htm", "text/html", 1, "1" * 64, "authored-compact"),
        FilingDocumentLoad("compact-conflict.xml", "sec_rendered_xbrl_instance", "file:///compact-conflict.xml", "application/xml", conflict_path.stat().st_size, sha256(conflict_path.read_bytes()).hexdigest(), str(conflict_path)),
        FilingDocumentLoad("compact-schema.xsd", "extension_schema", "file:///compact-schema.xsd", "application/xml", 1, "2" * 64, "authored-compact"),
    )
    load = CorporateFilingLoad(
        report.accession, "10-K", "2024-01-02", "2024-01-02T12:00:00+00:00",
        "2023-12-31", "compact-primary.htm", False, None, "b" * 64,
        report.dts_manifest_sha256, report, documents, (),
    )
    result = load_corporate_filings_to_postgres(
        (load,), database_url=corporate_postgres,
        knowledge_cutoff="2026-08-09T00:00:00+00:00",
    )
    assert (result.occurrence_count, result.slot_count) == (2, 1)
    assert _psql(corporate_postgres, "SELECT count(*) FROM corporate_reporting.fact_slot_occurrence;") == "2"
    assert _psql(corporate_postgres, "SELECT status || ':' || coalesce(selected_occurrence_id::text,'NULL') FROM corporate_reporting.fact_resolution_revision;") == "conflict:NULL"
    assert _psql(corporate_postgres, "SELECT check_status FROM meta.quality_check WHERE check_name='conflict_integrity';") == "fail"
    assert _psql(corporate_postgres, "SELECT count(*) FROM corporate_reporting.corporate_release;") == "0"


@POSTGRES_SKIP
@pytest.mark.parametrize(
    ("logical_key", "mutation"),
    (
        pytest.param(
            "source_occurrence",
            "UPDATE corporate_reporting.fact_occurrence SET occurrence_sha256=repeat('f',64) "
            "WHERE fact_occurrence_id=(SELECT fact_occurrence_id FROM corporate_reporting.fact_occurrence LIMIT 1);",
            id="source-occurrence-key",
        ),
        pytest.param(
            "context",
            "UPDATE corporate_reporting.xbrl_context SET semantic_context_sha256=repeat('f',64) "
            "WHERE context_id=(SELECT context_id FROM corporate_reporting.xbrl_context LIMIT 1);",
            id="context-semantic-key",
        ),
        pytest.param(
            "unit",
            "UPDATE corporate_reporting.xbrl_unit_semantics SET semantic_unit_sha256=repeat('f',64) "
            "WHERE unit_semantics_id=(SELECT unit_semantics_id FROM corporate_reporting.xbrl_unit_semantics LIMIT 1);",
            id="unit-semantic-key",
        ),
        pytest.param(
            "slot",
            "UPDATE corporate_reporting.fact_semantic_slot SET slot_sha256=repeat('f',64) "
            "WHERE fact_slot_id=(SELECT fact_slot_id FROM corporate_reporting.fact_semantic_slot LIMIT 1);",
            id="slot-semantic-key",
        ),
        pytest.param(
            "fact_resolution",
            "INSERT INTO corporate_reporting.knowledge_revision("
            "knowledge_revision_id,axis_type,object_key,pipeline_run_id,evidence_fingerprint) "
            "SELECT 'ffffffff-ffff-4fff-8fff-fffffffffff1','fact_resolution',repeat('f',64),"
            "p.pipeline_run_id,repeat('e',64) FROM corporate_reporting.parser_run p LIMIT 1; "
            "INSERT INTO corporate_reporting.fact_resolution_revision("
            "resolution_revision_id,knowledge_revision_id,object_key,parser_run_id,filing_id,"
            "fact_slot_id,selected_occurrence_id,status,value_fingerprint,reason_code) "
            "SELECT 'ffffffff-ffff-4fff-8fff-fffffffffff2',"
            "'ffffffff-ffff-4fff-8fff-fffffffffff1',repeat('f',64),s.parser_run_id,s.filing_id,"
            "s.fact_slot_id,l.fact_occurrence_id,'accepted_identical',repeat('d',64),'forged' "
            "FROM corporate_reporting.fact_semantic_slot s "
            "JOIN corporate_reporting.fact_slot_occurrence l USING(fact_slot_id) LIMIT 1;",
            id="fact-resolution-object-key",
        ),
    ),
)
def test_postgresql_recomputes_logical_keys_at_admission_boundaries(
    corporate_postgres: str, logical_key: str, mutation: str,
) -> None:
    _psql_file(corporate_postgres, FOUNDATION)
    _psql_file(corporate_postgres, MIGRATION)
    load_protected_gatos_to_postgres(
        database_url=corporate_postgres, fixture_root=PROTECTED,
        knowledge_cutoff=KNOWLEDGE_CUTOFF,
    )
    # A syntactically valid digest is not proof of its semantic preimage. Every
    # admission path must independently derive the logical key from owned payload.
    with pytest.raises(subprocess.CalledProcessError):
        _psql(
            corporate_postgres,
            f"BEGIN; {mutation} SET CONSTRAINTS ALL IMMEDIATE; ROLLBACK; -- {logical_key}",
        )


@POSTGRES_SKIP
def test_postgresql_occurrence_slot_link_rejects_cross_parser_ownership(
    corporate_postgres: str,
) -> None:
    _psql_file(corporate_postgres, FOUNDATION)
    _psql_file(corporate_postgres, MIGRATION)
    initial = build_protected_gatos_loads(PROTECTED)
    load_corporate_filings_to_postgres(
        initial, database_url=corporate_postgres, knowledge_cutoff=KNOWLEDGE_CUTOFF,
    )
    attempt_b = tuple(
        replace(load, parser_attempt_key="cross-owner-b", parser_selection_status="proposed")
        for load in initial
    )
    load_corporate_filings_to_postgres(
        attempt_b, database_url=corporate_postgres, knowledge_cutoff=KNOWLEDGE_CUTOFF,
    )
    # Source occurrences are shared, but a B slot may not borrow A's parser-owned
    # interpretation of that source row. Filing and occurrence ids intentionally match.
    with pytest.raises(subprocess.CalledProcessError):
        _psql(corporate_postgres, """
          BEGIN;
          UPDATE corporate_reporting.fact_slot_occurrence bridge_b
          SET fact_occurrence_interpretation_id=interpretation_a.fact_occurrence_interpretation_id
          FROM corporate_reporting.parser_run parser_b,
               corporate_reporting.fact_occurrence_interpretation interpretation_a
          JOIN corporate_reporting.parser_run parser_a
            ON parser_a.parser_run_id=interpretation_a.parser_run_id
          WHERE bridge_b.parser_run_id=parser_b.parser_run_id
            AND parser_b.parser_attempt_key='cross-owner-b'
            AND parser_a.parser_attempt_key='protected-initial-v1'
            AND interpretation_a.fact_occurrence_id=bridge_b.fact_occurrence_id
            AND interpretation_a.filing_id=bridge_b.filing_id;
          SET CONSTRAINTS ALL IMMEDIATE;
          ROLLBACK;
        """)


@POSTGRES_SKIP
def test_postgresql_parser_attempts_coexist_with_independent_interpretations_and_replay(
    corporate_postgres: str,
) -> None:
    _psql_file(corporate_postgres, FOUNDATION)
    _psql_file(corporate_postgres, MIGRATION)
    attempt_a = build_protected_gatos_loads(PROTECTED)
    result_a = load_corporate_filings_to_postgres(
        attempt_a, database_url=corporate_postgres, knowledge_cutoff=KNOWLEDGE_CUTOFF,
    )
    attempt_b = tuple(
        replace(load, parser_attempt_key="independent-b", parser_selection_status="accepted")
        for load in attempt_a
    )
    result_b = load_corporate_filings_to_postgres(
        attempt_b, database_url=corporate_postgres, knowledge_cutoff=KNOWLEDGE_CUTOFF,
    )
    # A and B are independently replayable after both have been admitted.
    assert load_corporate_filings_to_postgres(
        attempt_a, database_url=corporate_postgres, knowledge_cutoff=KNOWLEDGE_CUTOFF,
    ) == result_a
    assert load_corporate_filings_to_postgres(
        attempt_b, database_url=corporate_postgres, knowledge_cutoff=KNOWLEDGE_CUTOFF,
    ) == result_b

    counts = json.loads(_psql(corporate_postgres, """
      SELECT json_build_array(
        (SELECT count(*) FROM corporate_reporting.parser_run),
        (SELECT count(*) FROM corporate_reporting.xbrl_context),
        (SELECT count(*) FROM corporate_reporting.xbrl_context_dimension),
        (SELECT count(*) FROM corporate_reporting.xbrl_unit_semantics),
        (SELECT count(*) FROM corporate_reporting.xbrl_source_unit_alias),
        (SELECT count(*) FROM corporate_reporting.fact_occurrence),
        (SELECT count(DISTINCT occurrence_sha256) FROM corporate_reporting.fact_occurrence),
        (SELECT count(*) FROM corporate_reporting.fact_occurrence_interpretation),
        (SELECT count(*) FROM corporate_reporting.fact_slot_occurrence),
        (SELECT count(*) FROM corporate_reporting.fact_semantic_slot),
        (SELECT count(*) FROM corporate_reporting.fact_resolution_revision));
    """))
    # Parser-owned interpretations are separate; immutable source occurrence
    # fingerprints are shared by A/B rather than redefined by parser ownership.
    assert counts == [4, 764, 1154, 32, 32, 1568, 1568, 3136, 3136, 2970, 2970]
    # Every B bridge resolves through B's own interpretation, while both parser
    # attempts point those interpretations at the same immutable source rows.
    assert _psql(corporate_postgres, """
      SELECT json_build_array(
        count(*), count(*) FILTER (WHERE i.parser_run_id=b.parser_run_id),
        count(DISTINCT b.fact_occurrence_id))
      FROM corporate_reporting.fact_slot_occurrence b
      JOIN corporate_reporting.fact_occurrence_interpretation i
        ON i.fact_occurrence_interpretation_id=b.fact_occurrence_interpretation_id
      JOIN corporate_reporting.parser_run p ON p.parser_run_id=b.parser_run_id
      WHERE p.parser_attempt_key='independent-b';
    """) == "[1568, 1568, 1568]"
    assert _psql(corporate_postgres, """
      SELECT count(*) FROM corporate_reporting.parser_run_selection_revision s
      WHERE s.status='accepted';
    """) == "4"
    # Selecting B is append-only: A evidence and both accepted selection records remain.
    assert _psql(corporate_postgres, """
      SELECT count(*) FROM corporate_reporting.parser_run p
      JOIN corporate_reporting.parser_run_selection_revision s USING(parser_run_id)
      WHERE p.parser_attempt_key IN ('protected-initial-v1','independent-b');
    """) == "4"


def _compact_postgres_load(accession: str, *, amendment: bool = False) -> CorporateFilingLoad:
    report = parse_instance(FIXTURE, accession=accession, dts_manifest_sha256="a" * 64)
    primary = f"{accession}-primary.htm"
    documents = (
        FilingDocumentLoad(primary, "primary_inline_xbrl", f"file:///{primary}", "text/html", 1,
                           sha256(primary.encode()).hexdigest(), "authored-compact"),
        FilingDocumentLoad(FIXTURE.name, "sec_rendered_xbrl_instance", FIXTURE.as_uri(),
                           "application/xml", FIXTURE.stat().st_size,
                           sha256(FIXTURE.read_bytes()).hexdigest(), str(FIXTURE)),
        FilingDocumentLoad(f"{accession}.xsd", "extension_schema", f"file:///{accession}.xsd",
                           "application/xml", 1, sha256(accession.encode()).hexdigest(),
                           "authored-compact"),
    )
    return CorporateFilingLoad(
        accession, "10-K/A" if amendment else "10-K", "2024-01-02",
        "2024-01-02T13:00:00+00:00" if amendment else "2024-01-02T12:00:00+00:00",
        "2024-12-31", primary, amendment, "compact amendment" if amendment else None,
        sha256((accession + ":manifest").encode()).hexdigest(), report.dts_manifest_sha256,
        report, documents, (),
    )


@POSTGRES_ONLY
def test_postgresql_transitive_append_only_and_parser_ownership_boundaries(
    corporate_postgres: str,
) -> None:
    """Coordinated payload/key reclosure must not rewrite admitted evidence or decisions."""
    _psql_file(corporate_postgres, FOUNDATION)
    _psql_file(corporate_postgres, MIGRATION)
    initial = (
        _compact_postgres_load("0001104659-23-034448"),
        _compact_postgres_load("0001104659-23-074911", amendment=True),
    )
    load_corporate_filings_to_postgres(
        initial, database_url=corporate_postgres, knowledge_cutoff=KNOWLEDGE_CUTOFF,
    )
    attempt_b = tuple(
        replace(load, parser_attempt_key="integrity-attempt-b", parser_selection_status="proposed")
        for load in initial
    )
    load_corporate_filings_to_postgres(
        attempt_b, database_url=corporate_postgres, knowledge_cutoff=KNOWLEDGE_CUTOFF,
    )
    # Accepted governance decisions are represented as successor revisions. Their
    # insertion remains legal even though every admitted revision is immutable.
    _psql(corporate_postgres, """
      INSERT INTO corporate_reporting.knowledge_revision(
        knowledge_revision_id,axis_type,object_key,predecessor_revision_id,pipeline_run_id,
        evidence_fingerprint,recorded_at)
      SELECT 'eeeeeeee-eeee-4eee-8eee-eeeeeeeeeee1','concept_mapping',object_key,
             knowledge_revision_id,pipeline_run_id,repeat('e',64),now()
      FROM corporate_reporting.knowledge_revision
      WHERE axis_type='concept_mapping' LIMIT 1;
      INSERT INTO corporate_reporting.concept_mapping_revision(
        mapping_revision_id,knowledge_revision_id,object_key,source_concept_id,
        canonical_concept_id,reporting_scope_kind,status,rationale,evidence_fingerprint)
      SELECT 'eeeeeeee-eeee-4eee-8eee-eeeeeeeeeee2',
             'eeeeeeee-eeee-4eee-8eee-eeeeeeeeeee1',object_key,source_concept_id,
             canonical_concept_id,reporting_scope_kind,'accepted','reviewed',repeat('e',64)
      FROM corporate_reporting.concept_mapping_revision LIMIT 1;
      INSERT INTO corporate_reporting.knowledge_revision(
        knowledge_revision_id,axis_type,object_key,predecessor_revision_id,pipeline_run_id,
        evidence_fingerprint,recorded_at)
      SELECT 'eeeeeeee-eeee-4eee-8eee-eeeeeeeeeee3','expected_selection',object_key,
             knowledge_revision_id,pipeline_run_id,repeat('e',64),now()
      FROM corporate_reporting.knowledge_revision
      WHERE axis_type='expected_selection' LIMIT 1;
      INSERT INTO corporate_reporting.expected_selection_revision(
        expected_selection_revision_id,knowledge_revision_id,object_key,selection_code,
        selection_version,canonical_concept_id,scope_kind,period_policy,
        applicability_predicate,rights_output_family,selection_sha256,status)
      SELECT 'eeeeeeee-eeee-4eee-8eee-eeeeeeeeeee4',
             'eeeeeeee-eeee-4eee-8eee-eeeeeeeeeee3',object_key,selection_code,
             selection_version,canonical_concept_id,scope_kind,period_policy,
             applicability_predicate,rights_output_family,selection_sha256,'accepted'
      FROM corporate_reporting.expected_selection_revision LIMIT 1;
    """)

    assert _psql(corporate_postgres, """
      SELECT is_generated FROM information_schema.columns
      WHERE table_schema='corporate_reporting' AND table_name='xbrl_context_dimension'
        AND column_name='typed_member_sha256';
    """) == "ALWAYS"
    assert _psql(corporate_postgres, """
      SELECT bool_and(typed_member_sha256=corporate_reporting.canonical_sha256(
        typed_member_canonical_xml))
      FROM corporate_reporting.xbrl_context_dimension WHERE member_kind='typed';
    """) == "t"

    adversarial = {
        "coordinated occurrence payload/key rewrite": """
          UPDATE corporate_reporting.fact_occurrence o SET lexical_value='forged',
            occurrence_sha256=corporate_reporting.canonical_sha256(
              '{"concept":' || to_jsonb(o.source_concept_qname)::text ||
              ',"context":' || to_jsonb(o.source_context_ref)::text ||
              ',"decimals":' || COALESCE(to_jsonb(o.decimals)::text,'null') ||
              ',"lang":' || COALESCE(to_jsonb(o.xml_lang)::text,'null') ||
              ',"nil":' || to_jsonb(o.nil_flag)::text || ',"ordinal":' || o.source_ordinal ||
              ',"precision":' || COALESCE(to_jsonb(o.precision)::text,'null') ||
              ',"unit":' || COALESCE(to_jsonb(o.source_unit_ref)::text,'null') ||
              ',"value":"forged"}')
          WHERE o.fact_occurrence_id=(SELECT fact_occurrence_id FROM corporate_reporting.fact_occurrence LIMIT 1);
        """,
        "coordinated typed XML/digest/context reclosure": """
          UPDATE corporate_reporting.xbrl_context_dimension
          SET typed_member_canonical_xml='<identifier code="B">Beta</identifier>',
              typed_member_sha256=corporate_reporting.canonical_sha256('<identifier code="B">Beta</identifier>')
          WHERE context_dimension_id=(SELECT context_dimension_id FROM corporate_reporting.xbrl_context_dimension
                                      WHERE member_kind='typed' LIMIT 1);
          UPDATE corporate_reporting.xbrl_context c
          SET semantic_context_sha256=corporate_reporting.canonical_sha256(
              corporate_reporting.context_payload(c.context_id))
          WHERE c.context_id IN (SELECT context_id FROM corporate_reporting.xbrl_context_dimension
                                 WHERE member_kind='typed');
        """,
        "accepted relationship rewrite": """
          UPDATE corporate_reporting.filing_relationship_revision
          SET relationship_type='amends', assertion_status='proposed'
          WHERE assertion_status='accepted';
        """,
        "mapping revision rewrite": """
          UPDATE corporate_reporting.concept_mapping_revision SET rationale='forged'
          WHERE status='accepted';
        """,
        "expected selection rewrite": """
          UPDATE corporate_reporting.expected_selection_revision SET status='rejected'
          WHERE status='accepted';
        """,
        "accepted parser selection rewrite": """
          UPDATE corporate_reporting.parser_run_selection_revision SET rationale='forged'
          WHERE status='accepted';
        """,
        "fact resolution rewrite": """
          UPDATE corporate_reporting.fact_resolution_revision SET reason_code='forged';
        """,
        "eligibility decision rewrite": """
          UPDATE corporate_reporting.corporate_release_eligibility_revision
          SET status='eligible', reason_codes='[]'::jsonb;
        """,
        "snapshot rewrite": """
          UPDATE corporate_reporting.knowledge_snapshot SET manifest_sha256=repeat('f',64);
        """,
        "snapshot member dependency rewrite": """
          UPDATE corporate_reporting.knowledge_revision SET evidence_fingerprint=repeat('f',64)
          WHERE knowledge_revision_id IN
            (SELECT knowledge_revision_id FROM corporate_reporting.knowledge_snapshot_member LIMIT 1);
        """,
        "source concept dependency rewrite": """
          UPDATE corporate_reporting.source_concept SET local_name=local_name || 'Forged'
          WHERE source_concept_id=(SELECT source_concept_id FROM corporate_reporting.fact_semantic_slot LIMIT 1);
        """,
        "taxonomy dependency rewrite": """
          UPDATE corporate_reporting.taxonomy_set SET dts_manifest_sha256=repeat('f',64)
          WHERE taxonomy_set_id=(SELECT taxonomy_set_id FROM corporate_reporting.source_concept
                                 WHERE source_concept_id=(SELECT source_concept_id
                                   FROM corporate_reporting.fact_semantic_slot LIMIT 1));
        """,
        "cross-parser source concept with coordinated slot digest": """
          INSERT INTO corporate_reporting.fact_semantic_slot(
            fact_slot_id,parser_run_id,filing_id,reporting_scope_id,source_concept_id,
            semantic_context_sha256,semantic_unit_sha256,xml_lang,slot_sha256)
          SELECT gen_random_uuid(),parser_a.parser_run_id,slot_a.filing_id,
            slot_a.reporting_scope_id,concept_b.source_concept_id,
            slot_a.semantic_context_sha256,slot_a.semantic_unit_sha256,'forged-language',
            corporate_reporting.canonical_sha256(
              '{"accession":' || to_jsonb(f.accession)::text || ',"correspondence":' ||
              regexp_replace(jsonb_build_array(
                '{' || concept_b.namespace_uri || '}' || concept_b.local_name,
                corporate_reporting.context_payload(context_a.context_id),
                slot_a.semantic_unit_sha256,'forged-language')::text,
                '([,:]) ', '\\1', 'g') || ',"dts":' ||
              to_jsonb(taxonomy_b.dts_manifest_sha256)::text || '}')
          FROM corporate_reporting.fact_semantic_slot slot_a
          JOIN corporate_reporting.parser_run parser_a USING(parser_run_id)
          JOIN corporate_reporting.filing_submission f ON f.filing_id=slot_a.filing_id
          JOIN corporate_reporting.xbrl_context context_a
            ON context_a.parser_run_id=slot_a.parser_run_id
           AND context_a.filing_id=slot_a.filing_id
           AND context_a.semantic_context_sha256=slot_a.semantic_context_sha256
          CROSS JOIN LATERAL (
            SELECT concept.* FROM corporate_reporting.source_concept concept
            JOIN corporate_reporting.parser_run parser_b USING(parser_run_id)
            WHERE parser_b.parser_attempt_key='integrity-attempt-b'
              AND concept.filing_id=slot_a.filing_id LIMIT 1
          ) concept_b
          JOIN corporate_reporting.taxonomy_set taxonomy_b
            ON taxonomy_b.taxonomy_set_id=concept_b.taxonomy_set_id
          WHERE parser_a.parser_attempt_key='protected-initial-v1' LIMIT 1;
        """,
    }
    admitted: list[str] = []
    rejection_errors: dict[str, str] = {}
    for name, statement in adversarial.items():
        try:
            _psql(corporate_postgres, f"BEGIN; {statement} SET CONSTRAINTS ALL IMMEDIATE; ROLLBACK;")
        except subprocess.CalledProcessError as exc:
            rejection_errors[name] = exc.stderr
            continue
        admitted.append(name)
    assert not admitted, "integrity boundary admitted: " + ", ".join(admitted)
    assert "foreign key constraint" in rejection_errors[
        "cross-parser source concept with coordinated slot digest"
    ].lower()

    # B is an append-only parser-selection successor, not an in-place rewrite.
    assert _psql(corporate_postgres, """
      SELECT count(*) FROM corporate_reporting.knowledge_revision child
      JOIN corporate_reporting.knowledge_revision parent
        ON parent.knowledge_revision_id=child.predecessor_revision_id
      WHERE child.axis_type='parser_selection';
    """) == "2"


@POSTGRES_ONLY
def test_postgresql_complete_identity_dependencies_reject_update_and_delete(corporate_postgres: str) -> None:
    _psql_file(corporate_postgres, FOUNDATION)
    _psql_file(corporate_postgres, MIGRATION)
    load_corporate_filings_to_postgres((_compact_postgres_load("0000000001-24-000201"),), database_url=corporate_postgres, knowledge_cutoff=KNOWLEDGE_CUTOFF)
    targets = {"reporting_entity": "entity_id", "entity_identifier": "entity_identifier_id", "filing_submission": "filing_id", "filing_document": "document_id", "reporting_scope": "scope_id", "parser_run": "parser_run_id", "taxonomy_set": "taxonomy_set_id", "source_concept": "source_concept_id", "xbrl_context": "context_id", "canonical_concept": "canonical_concept_id", "corporate_release_policy": "policy_id"}
    assert _psql(corporate_postgres, """SELECT count(*) FROM pg_trigger WHERE tgname LIKE 'trg_cr_immutable_%' AND (tgtype & 24)=24;""") == "35"
    for table, key in targets.items():
        assert int(_psql(corporate_postgres, f"SELECT count(*) FROM corporate_reporting.{table};")) > 0
        for operation in (f"UPDATE corporate_reporting.{table} SET {key}={key} WHERE {key}=(SELECT {key} FROM corporate_reporting.{table} LIMIT 1);", f"DELETE FROM corporate_reporting.{table} WHERE {key}=(SELECT {key} FROM corporate_reporting.{table} LIMIT 1);"):
            with pytest.raises(subprocess.CalledProcessError):
                _psql(corporate_postgres, operation)


@POSTGRES_ONLY
def test_postgresql_canonical_json_and_non_vacuous_key_admission(corporate_postgres: str) -> None:
    _psql_file(corporate_postgres, FOUNDATION)
    _psql_file(corporate_postgres, MIGRATION)
    payloads = [{"z": "space inside value", "a": ["x, y", {"colon": "a: b"}]}, {"nested": {"b": True, "a": None}, "number": 1.25}]
    for payload in payloads:
        expected = sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        literal = "'" + json.dumps(payload).replace("'", "''") + "'"
        assert _psql(corporate_postgres, f"SELECT corporate_reporting.canonical_sha256({literal}::jsonb);") == expected
    load_corporate_filings_to_postgres((_compact_postgres_load("0000000001-24-000202"),), database_url=corporate_postgres, knowledge_cutoff=KNOWLEDGE_CUTOFF)
    counts = json.loads(_psql(corporate_postgres, """SELECT json_build_array((SELECT count(*) FROM corporate_reporting.fact_occurrence),(SELECT count(*) FROM corporate_reporting.xbrl_context),(SELECT count(*) FROM corporate_reporting.xbrl_unit_semantics),(SELECT count(*) FROM corporate_reporting.fact_semantic_slot));"""))
    assert all(count > 0 for count in counts)
    with pytest.raises(subprocess.CalledProcessError):
        _psql(corporate_postgres, """BEGIN; INSERT INTO corporate_reporting.fact_occurrence(fact_occurrence_id,filing_id,document_id,source_ordinal,source_concept_qname,source_context_ref,lexical_value,nil_flag,occurrence_sha256) SELECT gen_random_uuid(),filing_id,document_id,999999,source_concept_qname,source_context_ref,'value with spaces',false,repeat('f',64) FROM corporate_reporting.fact_occurrence LIMIT 1; SET CONSTRAINTS ALL IMMEDIATE;""")
    forged_inserts = (
        """INSERT INTO corporate_reporting.xbrl_context(context_id,parser_run_id,filing_id,source_context_id,reporting_scope_id,entity_scheme,entity_value,period_kind,start_date,end_date,instant_date,raw_xml_sha256,semantic_context_sha256) SELECT gen_random_uuid(),parser_run_id,filing_id,source_context_id || '-forged',reporting_scope_id,entity_scheme,entity_value,period_kind,start_date,end_date,instant_date,raw_xml_sha256,repeat('f',64) FROM corporate_reporting.xbrl_context LIMIT 1;""",
        """INSERT INTO corporate_reporting.xbrl_unit_semantics(unit_semantics_id,parser_run_id,filing_id,numerator_measures,denominator_measures,semantic_unit_sha256) SELECT gen_random_uuid(),parser_run_id,filing_id,numerator_measures,denominator_measures,repeat('f',64) FROM corporate_reporting.xbrl_unit_semantics LIMIT 1;""",
        """INSERT INTO corporate_reporting.fact_semantic_slot(fact_slot_id,parser_run_id,filing_id,reporting_scope_id,source_concept_id,semantic_context_sha256,semantic_unit_sha256,xml_lang,slot_sha256) SELECT gen_random_uuid(),parser_run_id,filing_id,reporting_scope_id,source_concept_id,semantic_context_sha256,semantic_unit_sha256,'forged-language',repeat('f',64) FROM corporate_reporting.fact_semantic_slot LIMIT 1;""",
    )
    for statement in forged_inserts:
        with pytest.raises(subprocess.CalledProcessError):
            _psql(corporate_postgres, f"BEGIN; {statement} SET CONSTRAINTS ALL IMMEDIATE;")


@POSTGRES_ONLY
def test_postgresql_typed_hash_wrong_claim_xml_update_and_same_attempt_acceptance(corporate_postgres: str) -> None:
    _psql_file(corporate_postgres, FOUNDATION)
    _psql_file(corporate_postgres, MIGRATION)
    base = _compact_postgres_load("0000000001-24-000203")
    proposal = replace(base, parser_attempt_key="review-v2", parser_selection_status="proposed")
    load_corporate_filings_to_postgres((base,), database_url=corporate_postgres, knowledge_cutoff=KNOWLEDGE_CUTOFF)
    load_corporate_filings_to_postgres((proposal,), database_url=corporate_postgres, knowledge_cutoff=KNOWLEDGE_CUTOFF)
    accepted = replace(proposal, parser_selection_status="accepted")
    load_corporate_filings_to_postgres((accepted,), database_url=corporate_postgres, knowledge_cutoff=KNOWLEDGE_CUTOFF)
    load_corporate_filings_to_postgres((accepted,), database_url=corporate_postgres, knowledge_cutoff=KNOWLEDGE_CUTOFF)
    assert _psql(corporate_postgres, """SELECT string_agg(s.status,',' ORDER BY s.status DESC) FROM corporate_reporting.parser_run_selection_revision s JOIN corporate_reporting.parser_run p USING(parser_run_id) WHERE p.parser_attempt_key='review-v2';""") == "proposed,accepted"
    assert _psql(corporate_postgres, """SELECT count(*) FROM corporate_reporting.knowledge_revision child JOIN corporate_reporting.parser_run_selection_revision s ON s.knowledge_revision_id=child.knowledge_revision_id AND s.status='accepted' JOIN corporate_reporting.knowledge_revision parent ON parent.knowledge_revision_id=child.predecessor_revision_id JOIN corporate_reporting.parser_run_selection_revision prior ON prior.knowledge_revision_id=parent.knowledge_revision_id AND prior.status='proposed';""") == "1"
    assert int(_psql(corporate_postgres, "SELECT count(*) FROM corporate_reporting.xbrl_context_dimension WHERE member_kind='typed';")) > 0
    with pytest.raises(subprocess.CalledProcessError):
        _psql(corporate_postgres, """INSERT INTO corporate_reporting.xbrl_context_dimension(context_dimension_id,context_id,filing_id,location,axis_namespace,axis_local_name,member_kind,typed_member_canonical_xml,typed_member_sha256) SELECT gen_random_uuid(),context_id,filing_id,'scenario','urn:test','WrongClaimAxis','typed','<x>space value</x>',repeat('f',64) FROM corporate_reporting.xbrl_context LIMIT 1;""")
    with pytest.raises(subprocess.CalledProcessError):
        _psql(corporate_postgres, "UPDATE corporate_reporting.xbrl_context_dimension SET typed_member_canonical_xml='<x>changed value</x>' WHERE member_kind='typed';")


@POSTGRES_ONLY
def test_postgresql_prior_005_shape_upgrades_idempotently(corporate_postgres: str) -> None:
    _psql_file(corporate_postgres, FOUNDATION)
    _psql_file(corporate_postgres, MIGRATION)
    base = _compact_postgres_load("0000000001-24-000204")
    load_corporate_filings_to_postgres((base,), database_url=corporate_postgres, knowledge_cutoff=KNOWLEDGE_CUTOFF)
    load_corporate_filings_to_postgres((replace(base, parser_attempt_key="legacy-second", parser_selection_status="proposed"),), database_url=corporate_postgres, knowledge_cutoff=KNOWLEDGE_CUTOFF)
    _psql(corporate_postgres, """DROP TRIGGER trg_cr_immutable_parser_run ON corporate_reporting.parser_run; ALTER TABLE corporate_reporting.parser_run DROP CONSTRAINT uq_cr_parser_attempt; ALTER TABLE corporate_reporting.parser_run ALTER COLUMN parser_attempt_key DROP NOT NULL; UPDATE corporate_reporting.parser_run SET parser_attempt_key=NULL; CREATE TRIGGER trg_cr_immutable_parser_run BEFORE UPDATE ON corporate_reporting.parser_run FOR EACH ROW EXECUTE FUNCTION corporate_reporting.reject_admitted_update(); ALTER TABLE corporate_reporting.xbrl_context_dimension DROP CONSTRAINT xbrl_context_dimension_check; ALTER TABLE corporate_reporting.xbrl_context_dimension DROP COLUMN typed_member_sha256; ALTER TABLE corporate_reporting.xbrl_context_dimension ADD COLUMN typed_member_sha256 text; ALTER TABLE corporate_reporting.fact_slot_occurrence DROP CONSTRAINT fact_slot_occurrence_parser_run_id_fact_slot_id_filing_id_fkey; ALTER TABLE corporate_reporting.fact_slot_occurrence ADD CONSTRAINT fact_slot_occurrence_fact_slot_id_fkey FOREIGN KEY(fact_slot_id) REFERENCES corporate_reporting.fact_semantic_slot(fact_slot_id); ALTER TABLE corporate_reporting.fact_semantic_slot DROP CONSTRAINT fact_semantic_slot_parser_run_id_source_concept_id_filing_id_fkey; ALTER TABLE corporate_reporting.fact_semantic_slot ADD CONSTRAINT fact_semantic_slot_source_concept_id_filing_id_fkey FOREIGN KEY(source_concept_id,filing_id) REFERENCES corporate_reporting.source_concept(source_concept_id,filing_id);""")
    _psql_file(corporate_postgres, MIGRATION)
    _psql_file(corporate_postgres, MIGRATION)
    assert _psql(corporate_postgres, "SELECT count(*)=count(DISTINCT filing_id::text || ':' || parser_attempt_key) AND bool_and(parser_attempt_key IS NOT NULL) FROM corporate_reporting.parser_run;") == "t"
    assert _psql(corporate_postgres, "SELECT is_generated FROM information_schema.columns WHERE table_schema='corporate_reporting' AND table_name='xbrl_context_dimension' AND column_name='typed_member_sha256';") == "ALWAYS"
    assert _psql(corporate_postgres, "SELECT count(*) FROM pg_constraint WHERE conrelid='corporate_reporting.fact_slot_occurrence'::regclass AND conname='fact_slot_occurrence_parser_run_id_fact_slot_id_filing_id_fkey';") == "1"
    assert _psql(corporate_postgres, "SELECT count(*) FROM pg_constraint WHERE conrelid='corporate_reporting.fact_semantic_slot'::regclass AND conname='fact_semantic_slot_parser_run_id_source_concept_id_filing_id_fkey';") == "1"
