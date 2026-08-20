from __future__ import annotations

from dataclasses import replace
import csv
from hashlib import sha256
import io
import json
import os
from pathlib import Path
import shutil
import subprocess
from typing import Any

import pytest

from macroforge.source_native_corporate_candidate import (
    CandidateContractError,
    SourceNativeCandidate,
    build_source_native_candidate,
    candidate_database_state,
    persist_source_native_candidate,
    representation_precedence,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
LEDGER = PROJECT_ROOT / "artifacts/reports/task223-corporate-proof-tranche-ledger.json"
SOURCE_MANIFEST = PROJECT_ROOT / "artifacts/reports/sec-corporate-portfolio-v1-manifest-20260630.json"
MIGRATIONS = (
    PROJECT_ROOT / "db/migrations/001_v0_schema_foundation.sql",
    PROJECT_ROOT / "db/migrations/005_corporate_reporting_foundation.sql",
    PROJECT_ROOT / "db/migrations/006_corporate_reporting_source_native_candidate.sql",
)
POSTGRES_TOOLS = all(shutil.which(command) for command in ("psql", "createdb", "dropdb"))
POSTGRES_ONLY = pytest.mark.skipif(not POSTGRES_TOOLS, reason="PostgreSQL tools unavailable")


def _hash(label: str) -> str:
    return sha256(label.encode()).hexdigest()


def _distribute(total: int, count: int) -> list[int]:
    quotient, remainder = divmod(total, count)
    return [quotient + (index < remainder) for index in range(count)]


def _snapshot() -> dict[str, Any]:
    ledger = json.loads(LEDGER.read_bytes())
    manifest = json.loads(SOURCE_MANIFEST.read_bytes())
    packages = {row["accession"]: row for row in manifest["package_results"]}
    acts = ledger["filing_acts"]
    occurrence_counts = _distribute(35_048, len(acts))
    slot_counts = _distribute(32_381, len(acts))
    filings = []
    for index, (act, occurrence_count, slot_count) in enumerate(
        zip(acts, occurrence_counts, slot_counts, strict=True)
    ):
        accession = act["accession"]
        package_documents = [row for row in packages[accession]["documents"] if row.get("owner") == "sec_filing"]
        filings.append({
            "accession": accession,
            "cik": act["cik"],
            "form": act["form"],
            "report_period": act["report_date"],
            "accepted_at": act["accepted_at"],
            "source_manifest_sha256": act["manifest_package_identity"],
            "documents": [
                {"name": Path(row["url"]).name, "role": sorted(row.get("roles") or ["package_document"])[0],
                 "byte_length": row["byte_length"], "sha256": row["sha256"]}
                for row in package_documents
            ],
            "occurrence_sha256s": [
                {"filing_accession": accession,
                 "sha256": _hash(f"occurrence:{accession}:{ordinal}")}
                for ordinal in range(occurrence_count)
            ],
            "slots": [
                {"filing_accession": accession,
                 "slot_sha256": _hash(f"slot:{accession}:{ordinal}"),
                 "source_concept_qname": f"{{urn:issuer:{index}}}Concept{ordinal % 17}",
                 "fact_resolution_status": "conflict" if ordinal == 0 and index == 0 else "accepted_identical"}
                for ordinal in range(slot_count)
            ],
            "amendment": (
                None if act.get("amendment_relationship") is None else {
                    "original_accession": act["amendment_relationship"]["original_accession"],
                    "relationship_type": "amends", "status": "proposed",
                }
            ),
        })
    return {"filings": filings}


@pytest.fixture(scope="module")
def candidate() -> SourceNativeCandidate:
    ledger = json.loads(LEDGER.read_bytes())
    return build_source_native_candidate(
        ledger=ledger,
        source_manifest=json.loads(SOURCE_MANIFEST.read_bytes()),
        source_snapshot=_snapshot(),
        sec_cutoff="2026-06-30T23:59:59Z",
        predecessor_candidate_sha256=None,
    )


def _psql(database: str, statement: str, *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["psql", "-X", "-v", "ON_ERROR_STOP=1", "-q", "-A", "-t", "-d", database],
        input=statement, text=True, capture_output=True, check=check,
    )


_MARKER_PURPOSE = "task225_source_native_candidate_rehearsal_v1"
_CANONICAL_SEC_CUTOFF = "2026-06-30T23:59:59Z"


def _self_consistent_candidate(document: dict[str, Any]) -> SourceNativeCandidate:
    body = {key: value for key, value in document.items() if key != "candidate_sha256"}
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    identity = sha256(canonical).hexdigest()
    payload = json.dumps(
        {**body, "candidate_sha256": identity},
        sort_keys=True, separators=(",", ":"), ensure_ascii=False,
    ).encode() + b"\n"
    return SourceNativeCandidate(identity, payload, canonical)


def _install_boundary(database: str, candidate_sha256: str, *, purpose: str = _MARKER_PURPOSE) -> None:
    _psql(database, f"""
      CREATE TABLE public.macroforge_task225_rehearsal_boundary (
        singleton boolean PRIMARY KEY DEFAULT true CHECK(singleton IS TRUE),
        database_name name NOT NULL,
        purpose text NOT NULL,
        contract_version text NOT NULL,
        expected_candidate_sha256 text NOT NULL,
        expected_sec_cutoff text NOT NULL
      );
      INSERT INTO public.macroforge_task225_rehearsal_boundary
        (singleton,database_name,purpose,contract_version,expected_candidate_sha256,expected_sec_cutoff)
      VALUES (true,current_database(),'{purpose}','1','{candidate_sha256}','{_CANONICAL_SEC_CUTOFF}');
    """)


def _create_marked_database(tmp_path: Path, label: str, candidate_sha256: str) -> str:
    suffix = sha256(f"{tmp_path}:{label}".encode()).hexdigest()[:12]
    database = f"macroforge_task225_candidate_{suffix}"
    subprocess.run(["createdb", database], check=True, capture_output=True, text=True)
    try:
        for migration in MIGRATIONS[:2]:
            subprocess.run(
                ["psql", "-X", "-v", "ON_ERROR_STOP=1", "-q", "-d", database, "-f", str(migration)],
                check=True, capture_output=True, text=True,
            )
        _install_boundary(database, candidate_sha256)
    except BaseException:
        subprocess.run(["dropdb", "--if-exists", database], check=True, capture_output=True, text=True)
        raise
    return database


def _apply_candidate_migration(database: str, *, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["psql", "-X", "-v", "ON_ERROR_STOP=1", "-q", "-d", database, "-f", str(MIGRATIONS[2])],
        check=check, capture_output=True, text=True,
    )


def _direct_header_insert(database: str, attack: SourceNativeCandidate) -> subprocess.CompletedProcess[str]:
    document = json.loads(attack.payload)
    encoded = attack.payload.decode().strip().replace("'", "''")
    payload_sha256 = sha256(attack.payload).hexdigest()
    predecessor = document["predecessor_candidate_sha256"]
    predecessor_sql = "NULL" if predecessor is None else f"'{predecessor}'"
    return _psql(database, f"""
      BEGIN;
      INSERT INTO corporate_reporting.source_native_candidate
        (candidate_sha256,contract_version,sec_cutoff,knowledge_cutoff_applicable,
         predecessor_candidate_sha256,payload_sha256,candidate_document)
      VALUES ('{attack.candidate_sha256}','1','{document['cutoffs']['sec']}'::timestamptz,false,
              {predecessor_sql},'{payload_sha256}','{encoded}'::jsonb);
      COMMIT;
    """, check=False)


def _direct_header_copy(database: str, attack: SourceNativeCandidate) -> subprocess.CompletedProcess[str]:
    document = json.loads(attack.payload)
    row = io.StringIO()
    csv.writer(row, lineterminator="\n").writerow([
        attack.candidate_sha256, "1", document["cutoffs"]["sec"], "false",
        document["predecessor_candidate_sha256"], sha256(attack.payload).hexdigest(),
        attack.payload.decode().strip(),
    ])
    statement = (
        "BEGIN; COPY corporate_reporting.source_native_candidate "
        "(candidate_sha256,contract_version,sec_cutoff,knowledge_cutoff_applicable,"
        "predecessor_candidate_sha256,payload_sha256,candidate_document) FROM STDIN WITH (FORMAT csv);\n"
        + row.getvalue() + "\\.\nCOMMIT;\n"
    )
    return _psql(database, statement, check=False)


def test_candidate_binds_exact_frozen_membership_and_is_order_deterministic(
    candidate: SourceNativeCandidate,
) -> None:
    payload = json.loads(candidate.payload)
    assert payload["schema"] == "macroforge.corporate-reporting.source-native-candidate.v1"
    assert payload["producer"] == {"domain": "corporate_reporting", "name": "MacroForge"}
    assert payload["contract"] == {"name": "source-native-private-analysis", "version": "1"}
    assert payload["cutoffs"] == {
        "knowledge": {"applicable": False, "reason": "no_governed_knowledge_closure", "value": None},
        "sec": "2026-06-30T23:59:59Z",
    }
    assert len(payload["filings"]) == 19
    assert len(payload["portfolio_absences"]) == 10
    assert sum(len(row["documents"]) for row in payload["filings"]) == 147
    assert sum(len(row["occurrence_sha256s"]) for row in payload["filings"]) == 35_048
    assert sum(len(row["slots"]) for row in payload["filings"]) == 32_381
    assert sum(row["amendment"] is not None for row in payload["filings"]) == 2
    assert candidate.candidate_sha256 == sha256(candidate.payload_without_identity).hexdigest()

    ledger = json.loads(LEDGER.read_bytes())
    shuffled = _snapshot()
    shuffled["filings"].reverse()
    for filing in shuffled["filings"]:
        filing["documents"].reverse()
        filing["occurrence_sha256s"].reverse()
        filing["slots"].reverse()
    replay = build_source_native_candidate(
        ledger=ledger, source_manifest=json.loads(SOURCE_MANIFEST.read_bytes()),
        source_snapshot=shuffled,
        sec_cutoff="2026-06-30T23:59:59Z", predecessor_candidate_sha256=None,
    )
    assert replay == candidate


@pytest.mark.parametrize("mutation", ("missing", "extra", "duplicate", "changed_hash", "cross_filing"))
def test_candidate_fails_closed_on_exact_membership_tampering(mutation: str) -> None:
    ledger = json.loads(LEDGER.read_bytes())
    snapshot = _snapshot()
    if mutation == "missing":
        snapshot["filings"].pop()
    elif mutation == "extra":
        snapshot["filings"].append(dict(snapshot["filings"][0], accession="0000000000-00-000000"))
    elif mutation == "duplicate":
        snapshot["filings"].append(snapshot["filings"][0])
    elif mutation == "changed_hash":
        snapshot["filings"][0]["documents"][0]["sha256"] = "f" * 64
    else:
        moved = snapshot["filings"][0]["occurrence_sha256s"].pop()
        snapshot["filings"][1]["occurrence_sha256s"].append(moved)
    with pytest.raises(CandidateContractError, match="membership|identity|count|duplicate|manifest"):
        build_source_native_candidate(
            ledger=ledger, source_manifest=json.loads(SOURCE_MANIFEST.read_bytes()),
            source_snapshot=snapshot,
            sec_cutoff="2026-06-30T23:59:59Z", predecessor_candidate_sha256=None,
        )


def test_mapping_absence_failure_conflict_and_state_axes_cannot_alias(
    candidate: SourceNativeCandidate,
) -> None:
    payload = json.loads(candidate.payload)
    slots = [slot for filing in payload["filings"] for slot in filing["slots"]]
    assert slots and {slot["mapping"]["disposition"] for slot in slots} == {"deliberately_unmapped"}
    assert all(slot["mapping"]["attribution"] == "task225-source-native-contract-v1" for slot in slots)
    assert any(slot["fact_resolution_status"] == "conflict" for slot in slots)
    assert not any(slot["mapping"]["disposition"] in {"accepted", "absent", "deferred", "rejected", "conflict"} for slot in slots)
    assert {row["disposition"] for row in payload["portfolio_absences"]} == {"acquisition_cessation_absence"}
    assert payload["failure_accounting"] == {
        "extraction_failure": 0, "intentional_exclusion": 0,
        "malformed_package": 0, "missing_package": 0,
        "technical_incompleteness": 0, "unresolved_dependency": 0,
    }
    axes = {row["axis"]: row["status"] for row in payload["state_axes"]}
    assert axes == {
        "comparability": "blocked_no_accepted_mappings",
        "delivery": "prohibited",
        "eligibility": "blocked_no_governed_authority",
        "publication": "prohibited",
        "quality": "candidate_evidence_only",
        "rights": "private_analysis_candidate_only",
        "semantic_readiness": "source_native_only",
        "source_membership_completeness": "complete",
        "technical_completeness": "complete",
    }
    assert payload["permissions"] == {
        "private_analysis_candidate": True, "publication": False,
        "redistribution": "not_authorized", "remote_delivery": False,
    }


def test_entity_scope_and_identity_namespaces_are_non_aliasing(candidate: SourceNativeCandidate) -> None:
    filing = json.loads(candidate.payload)["filings"][0]
    assert filing["filer_identity"] == {"scheme": "sec:cik", "value": filing["cik"]}
    assert filing["reporting_entity_identity"] != filing["filer_identity"]
    assert filing["reporting_scope"]["kind"] == "source_native_filing"
    assert filing["universal_company_identity"] is None


def test_representation_precedence_is_explicit_and_fail_closed() -> None:
    assert representation_precedence("candidate_v1", candidate_sha256="a" * 64) == "candidate_v1"
    assert representation_precedence("governed_v3", candidate_sha256="a" * 64,
                                     governed_release_sha256="b" * 64) == "governed_v3"
    with pytest.raises(CandidateContractError, match="compatibility|disagree"):
        representation_precedence("historical_v2", candidate_sha256="a" * 64,
                                  governed_release_sha256="b" * 64,
                                  compatibility_sha256="c" * 64)


@pytest.mark.parametrize("malformed", (
    "Z", "arbitrary textZ", "2026-13-01T00:00:00Z", "2026-02-30T00:00:00Z",
    "2025-02-29T00:00:00Z", "2026-01-01T24:00:00Z", "2026-01-01T23:60:00Z",
    "2026-01-01T23:59:60Z", "2026-06-30T23:59:59", "2026-06-30T23:59:59+00:00",
    "2026-06-30T23:59:59z", "2026-06-30T23:59:59ZZ", " 2026-06-30T23:59:59Z",
    "2026-06-30T23:59:59Z ", "2026-06-30T23:59:59Zsuffix",
    "2026-06-30T23:59:59.000Z", "2026-06-30 23:59:59Z",
    "2026-06-30T22:59:59Z",
))
def test_sec_cutoff_rejects_malformed_noncanonical_or_unbound_values(malformed: str) -> None:
    with pytest.raises(CandidateContractError, match="SEC cutoff"):
        build_source_native_candidate(
            ledger=json.loads(LEDGER.read_bytes()),
            source_manifest=json.loads(SOURCE_MANIFEST.read_bytes()),
            source_snapshot=_snapshot(), sec_cutoff=malformed,
            predecessor_candidate_sha256=None,
        )


_PERMISSION_ATTACKS = (
    "private_null", "publication_null", "redistribution_null", "delivery_null",
    "private_missing", "publication_missing", "redistribution_missing", "delivery_missing",
    "multiple_null", "private_false", "publication_true", "redistribution_allowed",
    "delivery_true", "publication_string_false", "delivery_string_false", "extra_permission",
)


def _permission_attack(candidate: SourceNativeCandidate, attack_name: str) -> SourceNativeCandidate:
    document = json.loads(candidate.payload)
    permissions = document["permissions"]
    if attack_name == "private_null":
        permissions["private_analysis_candidate"] = None
    elif attack_name == "publication_null":
        permissions["publication"] = None
    elif attack_name == "redistribution_null":
        permissions["redistribution"] = None
    elif attack_name == "delivery_null":
        permissions["remote_delivery"] = None
    elif attack_name.endswith("_missing"):
        key = {
            "private_missing": "private_analysis_candidate", "publication_missing": "publication",
            "redistribution_missing": "redistribution", "delivery_missing": "remote_delivery",
        }[attack_name]
        del permissions[key]
    elif attack_name == "multiple_null":
        permissions.update({key: None for key in permissions})
    elif attack_name == "private_false":
        permissions["private_analysis_candidate"] = False
    elif attack_name == "publication_true":
        permissions["publication"] = True
    elif attack_name == "redistribution_allowed":
        permissions["redistribution"] = "authorized"
    elif attack_name == "delivery_true":
        permissions["remote_delivery"] = True
    elif attack_name == "publication_string_false":
        permissions["publication"] = "false"
    elif attack_name == "delivery_string_false":
        permissions["remote_delivery"] = "false"
    elif attack_name == "extra_permission":
        permissions["governed_release"] = False
    else:  # pragma: no cover - parameter list and helper must remain closed together
        raise AssertionError(attack_name)
    return _self_consistent_candidate(document)


@pytest.mark.parametrize("attack_name", _PERMISSION_ATTACKS)
def test_application_verifier_rejects_every_nonexact_permission_posture(
    candidate: SourceNativeCandidate, attack_name: str,
) -> None:
    attack = _permission_attack(candidate, attack_name)
    with pytest.raises(CandidateContractError, match="permission|private-analysis"):
        persist_source_native_candidate(
            database_url="postgresql:///task225_should_not_connect", candidate=attack,
        )


@POSTGRES_ONLY
def test_migration_rejects_wrong_named_unclassified_database_before_ddl(tmp_path: Path) -> None:
    database = f"macroforge_task225_wrong_{sha256(str(tmp_path).encode()).hexdigest()[:12]}"
    subprocess.run(["createdb", database], check=True, capture_output=True, text=True)
    try:
        for migration in MIGRATIONS[:2]:
            subprocess.run(
                ["psql", "-X", "-v", "ON_ERROR_STOP=1", "-q", "-d", database, "-f", str(migration)],
                check=True, capture_output=True, text=True,
            )
        attempted = _apply_candidate_migration(database, check=False)
        assert attempted.returncode != 0
        assert "TASK-225 database boundary" in attempted.stderr
        assert _psql(database, "SELECT to_regclass('corporate_reporting.source_native_candidate') IS NULL;").stdout.strip() == "t"
    finally:
        subprocess.run(["dropdb", "--if-exists", database], check=True, capture_output=True, text=True)


@POSTGRES_ONLY
def test_migration_rejects_wrong_purpose_marker_before_ddl(tmp_path: Path, candidate: SourceNativeCandidate) -> None:
    database = _create_marked_database(tmp_path, "wrong-purpose", candidate.candidate_sha256)
    try:
        _psql(database, "UPDATE public.macroforge_task225_rehearsal_boundary SET purpose='governed';")
        attempted = _apply_candidate_migration(database, check=False)
        assert attempted.returncode != 0
        assert "TASK-225 database boundary" in attempted.stderr
        assert _psql(database, "SELECT to_regclass('corporate_reporting.source_native_candidate') IS NULL;").stdout.strip() == "t"
    finally:
        subprocess.run(["dropdb", "--if-exists", database], check=True, capture_output=True, text=True)


@pytest.mark.parametrize("attack_name", _PERMISSION_ATTACKS)
@POSTGRES_ONLY
def test_raw_sql_rejects_nonexact_permissions_atomically(
    tmp_path: Path, candidate: SourceNativeCandidate, attack_name: str,
) -> None:
    attack = _permission_attack(candidate, attack_name)
    database = _create_marked_database(tmp_path, f"raw-{attack_name}", attack.candidate_sha256)
    try:
        _apply_candidate_migration(database)
        attempted = _direct_header_insert(database, attack)
        assert attempted.returncode != 0, attack_name
        assert "permission" in attempted.stderr.lower() or "private-analysis" in attempted.stderr.lower()
        assert _psql(database, "SELECT count(*) FROM corporate_reporting.source_native_candidate;").stdout.strip() == "0"
    finally:
        subprocess.run(["dropdb", "--if-exists", database], check=True, capture_output=True, text=True)


@pytest.mark.parametrize(("field", "replacement", "constraint"), (
    ("producer", {"domain": "corporate_reporting", "name": "Impostor"}, "producer_exact"),
    ("representation_precedence", {
        "candidate": "candidate_v1_is_canonical_before_governed_admission",
        "governed": "candidate_v1_may_override_governed_v3",
        "historical": "v2_and_stored_items_are_compatibility_views_and_must_agree",
    }, "precedence_exact"),
))
@POSTGRES_ONLY
def test_raw_sql_rejects_nonexact_producer_or_representation_precedence(
    tmp_path: Path, candidate: SourceNativeCandidate,
    field: str, replacement: object, constraint: str,
) -> None:
    document = json.loads(candidate.payload)
    document[field] = replacement
    attack = _self_consistent_candidate(document)
    database = _create_marked_database(tmp_path, f"raw-{field}", attack.candidate_sha256)
    try:
        _apply_candidate_migration(database)
        attempted = _direct_header_insert(database, attack)
        assert attempted.returncode != 0
        assert constraint in attempted.stderr
        assert _psql(
            database, "SELECT count(*) FROM corporate_reporting.source_native_candidate;",
        ).stdout.strip() == "0"
    finally:
        subprocess.run(["dropdb", "--if-exists", database], check=True, capture_output=True, text=True)


@POSTGRES_ONLY
def test_migration_pins_search_path_before_boundary_resolution(
    tmp_path: Path, candidate: SourceNativeCandidate,
) -> None:
    database = _create_marked_database(tmp_path, "search-path", candidate.candidate_sha256)
    try:
        _psql(database, """
          CREATE FUNCTION public.current_database() RETURNS name
          LANGUAGE sql IMMUTABLE AS $$ SELECT 'macroforge'::name $$;
        """)
        env = dict(os.environ)
        env["PGOPTIONS"] = "-c search_path=public,pg_catalog"
        attempted = subprocess.run(
            ["psql", "-X", "-v", "ON_ERROR_STOP=1", "-q", "-d", database,
             "-f", str(MIGRATIONS[2])],
            check=False, capture_output=True, text=True, env=env,
        )
        assert attempted.returncode == 0, attempted.stderr
        assert _psql(
            database, "SELECT to_regclass('corporate_reporting.source_native_candidate') IS NOT NULL;",
        ).stdout.strip() == "t"
    finally:
        subprocess.run(["dropdb", "--if-exists", database], check=True, capture_output=True, text=True)


@POSTGRES_ONLY
def test_successor_persists_external_predecessor_identity_in_single_candidate_database(
    tmp_path: Path,
) -> None:
    predecessor_sha256 = "a" * 64
    successor = build_source_native_candidate(
        ledger=json.loads(LEDGER.read_bytes()),
        source_manifest=json.loads(SOURCE_MANIFEST.read_bytes()),
        source_snapshot=_snapshot(),
        sec_cutoff=_CANONICAL_SEC_CUTOFF,
        predecessor_candidate_sha256=predecessor_sha256,
    )
    database = _create_marked_database(tmp_path, "successor", successor.candidate_sha256)
    try:
        _apply_candidate_migration(database)
        persisted = persist_source_native_candidate(database_url=database, candidate=successor)
        assert persisted["candidate_sha256"] == successor.candidate_sha256
        assert _psql(
            database,
            "SELECT predecessor_candidate_sha256 FROM corporate_reporting.source_native_candidate;",
        ).stdout.strip() == predecessor_sha256
        assert _psql(
            database,
            "SELECT count(*) FROM corporate_reporting.source_native_candidate;",
        ).stdout.strip() == "1"
    finally:
        subprocess.run(["dropdb", "--if-exists", database], check=True, capture_output=True, text=True)


@POSTGRES_ONLY
def test_persistence_rejects_candidate_identity_mismatch_before_mutation(
    tmp_path: Path, candidate: SourceNativeCandidate,
) -> None:
    database = _create_marked_database(tmp_path, "identity-mismatch", candidate.candidate_sha256)
    try:
        _apply_candidate_migration(database)
        different = build_source_native_candidate(
            ledger=json.loads(LEDGER.read_bytes()),
            source_manifest=json.loads(SOURCE_MANIFEST.read_bytes()), source_snapshot=_snapshot(),
            sec_cutoff=_CANONICAL_SEC_CUTOFF, predecessor_candidate_sha256="a" * 64,
        )
        with pytest.raises(CandidateContractError, match="TASK-225 database boundary"):
            persist_source_native_candidate(database_url=database, candidate=different)
        assert _psql(database, "SELECT count(*) FROM corporate_reporting.source_native_candidate;").stdout.strip() == "0"
    finally:
        subprocess.run(["dropdb", "--if-exists", database], check=True, capture_output=True, text=True)


@POSTGRES_ONLY
def test_governed_macroforge_migration_is_rejected_before_ddl() -> None:
    env = dict(os.environ)
    env["PGOPTIONS"] = "-cdefault_transaction_read_only=on"
    attempted = subprocess.run(
        ["psql", "-X", "-v", "ON_ERROR_STOP=1", "-q", "-d", "macroforge", "-f", str(MIGRATIONS[2])],
        check=False, capture_output=True, text=True, env=env,
    )
    assert attempted.returncode != 0
    assert "TASK-225 database boundary" in attempted.stderr
    assert _psql(
        "macroforge", "SELECT to_regclass('corporate_reporting.source_native_candidate') IS NULL;",
    ).stdout.strip() == "t"


@POSTGRES_ONLY
def test_marker_immutability_deferred_closure_missing_marker_and_copy_boundary(
    tmp_path: Path, candidate: SourceNativeCandidate,
) -> None:
    database = _create_marked_database(tmp_path, "indirect-bypasses", candidate.candidate_sha256)
    try:
        _apply_candidate_migration(database)
        for relation in (
            "public.macroforge_task225_rehearsal_boundary",
            "corporate_reporting.source_native_candidate_filing_member",
            "corporate_reporting.source_native_candidate_absence_member",
            "corporate_reporting.source_native_candidate_state_axis",
        ):
            truncated = _psql(database, f"TRUNCATE TABLE {relation};", check=False)
            assert truncated.returncode != 0, relation
            assert "immutable" in truncated.stderr.lower(), relation
        truncated = _psql(database, """
          TRUNCATE TABLE
            corporate_reporting.source_native_candidate,
            corporate_reporting.source_native_candidate_filing_member,
            corporate_reporting.source_native_candidate_absence_member,
            corporate_reporting.source_native_candidate_state_axis;
        """, check=False)
        assert truncated.returncode != 0
        assert "immutable" in truncated.stderr.lower()

        marker_attack = _psql(
            database,
            "UPDATE public.macroforge_task225_rehearsal_boundary SET purpose='governed';",
            check=False,
        )
        assert marker_attack.returncode != 0
        assert "immutable" in marker_attack.stderr.lower()

        incomplete = _direct_header_insert(database, candidate)
        assert incomplete.returncode != 0
        assert "relational membership is incomplete" in incomplete.stderr
        assert _psql(database, "SELECT count(*) FROM corporate_reporting.source_native_candidate;").stdout.strip() == "0"

        different = build_source_native_candidate(
            ledger=json.loads(LEDGER.read_bytes()),
            source_manifest=json.loads(SOURCE_MANIFEST.read_bytes()), source_snapshot=_snapshot(),
            sec_cutoff=_CANONICAL_SEC_CUTOFF, predecessor_candidate_sha256="b" * 64,
        )
        copied = _direct_header_copy(database, different)
        assert copied.returncode != 0
        assert "TASK-225 database boundary" in copied.stderr
        assert _psql(database, "SELECT count(*) FROM corporate_reporting.source_native_candidate;").stdout.strip() == "0"

        _psql(database, """
          ALTER TABLE public.macroforge_task225_rehearsal_boundary
            DISABLE TRIGGER trg_cr_immutable_task225_rehearsal_boundary;
          DELETE FROM public.macroforge_task225_rehearsal_boundary;
          ALTER TABLE public.macroforge_task225_rehearsal_boundary
            ENABLE TRIGGER trg_cr_immutable_task225_rehearsal_boundary;
        """)
        with pytest.raises(CandidateContractError, match="TASK-225 database boundary"):
            persist_source_native_candidate(database_url=database, candidate=candidate)
        assert _psql(database, "SELECT count(*) FROM corporate_reporting.source_native_candidate;").stdout.strip() == "0"
    finally:
        subprocess.run(["dropdb", "--if-exists", database], check=True, capture_output=True, text=True)


@POSTGRES_ONLY
def test_candidate_schema_persistence_replay_n_plus_one_and_atomic_rollback(
    tmp_path: Path, candidate: SourceNativeCandidate,
) -> None:
    database = f"macroforge_task225_candidate_{sha256(str(tmp_path).encode()).hexdigest()[:12]}"
    subprocess.run(["createdb", database], check=True, capture_output=True, text=True)
    try:
        for migration in MIGRATIONS[:2]:
            subprocess.run(
                ["psql", "-X", "-v", "ON_ERROR_STOP=1", "-q", "-d", database, "-f", str(migration)],
                check=True, capture_output=True, text=True,
            )
        _install_boundary(database, candidate.candidate_sha256)
        _apply_candidate_migration(database)
        first = persist_source_native_candidate(database_url=database, candidate=candidate)
        before = candidate_database_state(database)
        replay = persist_source_native_candidate(database_url=database, candidate=candidate)
        assert replay == first
        assert candidate_database_state(database) == before
        assert before["counts"] == {"absence_members": 10, "candidates": 1, "filing_members": 19, "state_axes": 9}

        payload = json.loads(candidate.payload)
        filing = payload["filings"][0]
        bad_member = json.dumps({**filing, "accession": payload["filings"][1]["accession"]}, separators=(",", ":"))
        failed = _psql(database, f"""
          BEGIN;
          INSERT INTO corporate_reporting.source_native_candidate_filing_member
            (candidate_sha256,item_ordinal,accession,member_sha256,member_document)
          VALUES ('{candidate.candidate_sha256}',20,'{payload['filings'][1]['accession']}',
                  '{sha256(bad_member.encode()).hexdigest()}','{bad_member.replace("'", "''")}'::jsonb);
          COMMIT;
        """, check=False)
        assert failed.returncode != 0
        assert "candidate membership" in failed.stderr.lower() or "duplicate" in failed.stderr.lower()
        assert candidate_database_state(database) == before

        forged = replace(candidate, payload=candidate.payload.replace(b"source_native_filing", b"universal_company"))
        with pytest.raises(CandidateContractError, match="canonical|identity|digest"):
            persist_source_native_candidate(database_url=database, candidate=forged)
        assert candidate_database_state(database) == before
    finally:
        subprocess.run(["dropdb", "--if-exists", database], check=True, capture_output=True, text=True)
