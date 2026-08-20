#!/usr/bin/env python3
"""Run TASK-225 source-native candidate rehearsal in two disposable databases."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re
import subprocess
import sys
import time
from typing import Any

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "src"))

from macroforge.source_native_corporate_candidate import (  # noqa: E402
    CandidateContractError,
    build_source_native_candidate,
    candidate_database_state,
    persist_source_native_candidate,
    read_source_native_snapshot,
)

_ALLOWED = re.compile(r"^macroforge_task225_candidate_[0-9a-f]{12}$")
_MARKER_PURPOSE = "task225_source_native_candidate_rehearsal_v1"
_EXPECTED_SEC_CUTOFF = "2026-06-30T23:59:59Z"


def _run(command: list[str], *, input_text: str | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(command, input=input_text, text=True, capture_output=True)
    if check and completed.returncode:
        raise CandidateContractError(
            f"command failed ({completed.returncode}): {' '.join(command)}\n{completed.stderr.strip()}"
        )
    return completed


def _sql_literal(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def _scalar(database: str, sql: str) -> str:
    return _run(["psql", "-X", "-q", "-A", "-t", "-v", "ON_ERROR_STOP=1", "-d", database, "-c", sql]).stdout.strip()


def _source_counts(database: str) -> dict[str, int]:
    raw = _scalar(database, """
      SELECT jsonb_build_object(
       'filings',(SELECT count(*) FROM corporate_reporting.filing_submission),
       'documents',(SELECT count(*) FROM corporate_reporting.filing_document),
       'occurrences',(SELECT count(*) FROM corporate_reporting.fact_occurrence),
       'slots',(SELECT count(*) FROM corporate_reporting.fact_semantic_slot),
       'amendments',(SELECT count(*) FROM corporate_reporting.filing_relationship_revision WHERE assertion_status='proposed'))::text;
    """)
    return {key: int(value) for key, value in json.loads(raw).items()}


def _authority_counts(database: str) -> dict[str, int]:
    tables = {
        "accepted_mappings": "corporate_reporting.concept_mapping_revision WHERE status='accepted'",
        "accepted_rights": "corporate_reporting.corporate_rights_revision WHERE decision_status='accepted'",
        "accepted_quality": "corporate_reporting.corporate_quality_gate_revision WHERE decision_status='accepted'",
        "accepted_eligibility": "corporate_reporting.corporate_release_eligibility_revision WHERE status='eligible'",
        "governed_releases": "corporate_reporting.corporate_release",
        "publication_reservations": "corporate_reporting.corporate_publication_reservation",
        "publication_completions": "corporate_reporting.corporate_publication_completion",
    }
    return {name: int(_scalar(database, f"SELECT count(*) FROM {source};")) for name, source in tables.items()}


def _create_database(target: str, source: str) -> None:
    if _ALLOWED.fullmatch(target) is None:
        raise CandidateContractError(f"target database is outside TASK-225 boundary: {target}")
    exists = _scalar("postgres", f"SELECT count(*) FROM pg_database WHERE datname={_sql_literal(target)};")
    if exists != "0":
        raise CandidateContractError(f"target database already exists: {target}")
    active = _scalar("postgres", f"SELECT count(*) FROM pg_stat_activity WHERE datname={_sql_literal(source)};")
    if active != "0":
        raise CandidateContractError(f"source database has active sessions: {source}")
    _run(["createdb", "--template", source, target])
    actual = _scalar(target, "SELECT current_database();")
    if actual != target:
        raise CandidateContractError(f"created database identity mismatch: expected {target}, got {actual}")


def _install_candidate_boundary(database: str, candidate_sha256: str) -> dict[str, str]:
    if _ALLOWED.fullmatch(database) is None or re.fullmatch(r"[0-9a-f]{64}", candidate_sha256) is None:
        raise CandidateContractError("TASK-225 boundary identity is malformed")
    statement = f"""
      BEGIN;
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
      VALUES (true,current_database(),{_sql_literal(_MARKER_PURPOSE)},'1',
              {_sql_literal(candidate_sha256)},{_sql_literal(_EXPECTED_SEC_CUTOFF)});
      COMMIT;
    """
    _run(["psql", "-X", "-q", "-v", "ON_ERROR_STOP=1", "-d", database], input_text=statement)
    raw = _scalar(database, """
      SELECT jsonb_build_object(
       'database',current_database(),'purpose',purpose,'contract_version',contract_version,
       'expected_candidate_sha256',expected_candidate_sha256,'expected_sec_cutoff',expected_sec_cutoff)::text
      FROM public.macroforge_task225_rehearsal_boundary WHERE singleton IS TRUE;
    """)
    evidence = json.loads(raw)
    expected = {
        "database": database, "purpose": _MARKER_PURPOSE, "contract_version": "1",
        "expected_candidate_sha256": candidate_sha256, "expected_sec_cutoff": _EXPECTED_SEC_CUTOFF,
    }
    if evidence != expected:
        raise CandidateContractError(f"TASK-225 boundary marker authentication failed: {evidence}")
    return evidence


def _apply_candidate_migration(database: str) -> None:
    _run([
        "psql", "-X", "-q", "-v", "ON_ERROR_STOP=1", "-d", database,
        "-f", str(PROJECT / "db/migrations/006_corporate_reporting_source_native_candidate.sql"),
    ])


def _rollback_attack(database: str, candidate_sha256: str) -> dict[str, Any]:
    before = candidate_database_state(database)
    attempted = _run(
        ["psql", "-X", "-q", "-A", "-t", "-v", "ON_ERROR_STOP=1", "-d", database],
        input_text=(
            "BEGIN; UPDATE corporate_reporting.source_native_candidate "
            f"SET contract_version='2' WHERE candidate_sha256='{candidate_sha256}'; COMMIT;"
        ),
        check=False,
    )
    after = candidate_database_state(database)
    if attempted.returncode == 0 or before != after:
        raise CandidateContractError("immutable-candidate rollback attack was not rejected atomically")
    return {
        "attempt_exit_status": attempted.returncode,
        "rejected": True,
        "state_unchanged": True,
        "stderr_sha256": sha256(attempted.stderr.encode()).hexdigest(),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-database-a", required=True)
    parser.add_argument("--source-database-b", required=True)
    parser.add_argument("--database-a", required=True)
    parser.add_argument("--database-b", required=True)
    parser.add_argument("--ledger", type=Path, default=PROJECT / "artifacts/reports/task223-corporate-proof-tranche-ledger.json")
    parser.add_argument("--manifest", type=Path, default=PROJECT / "artifacts/reports/sec-corporate-portfolio-v1-manifest-20260630.json")
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    if args.database_a == args.database_b or args.source_database_a == args.source_database_b:
        raise CandidateContractError("two distinct source and target databases are required")

    ledger_bytes = args.ledger.read_bytes()
    manifest_bytes = args.manifest.read_bytes()
    ledger = json.loads(ledger_bytes)
    manifest = json.loads(manifest_bytes)
    started = time.monotonic()
    targets = ((args.database_a, args.source_database_a), (args.database_b, args.source_database_b))
    database_evidence: list[dict[str, Any]] = []
    candidates = []
    for target, source in targets:
        source_counts = _source_counts(source)
        if source_counts != {"amendments": 2, "documents": 147, "filings": 19, "occurrences": 35_048, "slots": 32_381}:
            raise CandidateContractError(f"source database accounting mismatch: {source_counts}")
        source_authority = _authority_counts(source)
        if any(source_authority.values()):
            raise CandidateContractError(f"source database contains governed authority: {source_authority}")
        _create_database(target, source)
        snapshot = read_source_native_snapshot(target)
        candidate = build_source_native_candidate(
            ledger=ledger, source_manifest=manifest, source_snapshot=snapshot,
            sec_cutoff=_EXPECTED_SEC_CUTOFF, predecessor_candidate_sha256=None,
        )
        candidates.append(candidate)
        boundary = _install_candidate_boundary(target, candidate.candidate_sha256)
        _apply_candidate_migration(target)
        before = candidate_database_state(target)
        if before["counts"] != {"absence_members": 0, "candidates": 0, "filing_members": 0, "state_axes": 0}:
            raise CandidateContractError(f"fresh target candidate state is not empty: {before}")
        first = persist_source_native_candidate(database_url=target, candidate=candidate)
        after_first = candidate_database_state(target)
        second = persist_source_native_candidate(database_url=target, candidate=candidate)
        after_replay = candidate_database_state(target)
        if first != second or after_first != after_replay:
            raise CandidateContractError("exact candidate replay was not a no-op")
        rollback = _rollback_attack(target, candidate.candidate_sha256)
        if _source_counts(target) != source_counts or _authority_counts(target) != source_authority:
            raise CandidateContractError("candidate rehearsal changed source or governed authority state")
        database_evidence.append({
            "candidate_database_state": after_replay,
            "candidate_persistence": first,
            "database": target,
            "database_boundary": boundary,
            "rollback_attack": rollback,
            "source_database": source,
            "source_counts": source_counts,
            "governed_authority_counts": source_authority,
        })
    if candidates[0] != candidates[1]:
        raise CandidateContractError("two-database candidate bytes do not converge")
    candidate = candidates[0]
    report = {
        "candidate": {
            "candidate_sha256": candidate.candidate_sha256,
            "payload_byte_length": len(candidate.payload),
            "payload_file_sha256": sha256(candidate.payload).hexdigest(),
        },
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "databases": database_evidence,
        "duration_seconds": round(time.monotonic() - started, 6),
        "input_evidence": {
            "ledger_path": str(args.ledger), "ledger_serialized_sha256": sha256(ledger_bytes).hexdigest(),
            "manifest_path": str(args.manifest), "manifest_serialized_sha256": sha256(manifest_bytes).hexdigest(),
        },
        "result": "PASS",
        "schema": "macroforge.task225.source-native-candidate-rehearsal.v1",
        "two_database_convergence": True,
    }
    args.report.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(report, indent=2, sort_keys=True).encode() + b"\n"
    args.report.write_bytes(encoded)
    print(json.dumps({
        "candidate_sha256": candidate.candidate_sha256,
        "report": str(args.report), "report_sha256": sha256(encoded).hexdigest(), "result": "PASS",
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
