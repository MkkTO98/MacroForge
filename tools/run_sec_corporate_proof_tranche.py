#!/usr/bin/env python3
"""Run the authenticated TASK-223 SEC proof tranche outside governed state."""
from __future__ import annotations

import argparse
from datetime import date
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import signal
import subprocess
import time
from typing import Any, Iterable
from uuid import uuid4

from macroforge.sec_corporate_proof_tranche import (
    acquisition_report,
    acquire_frozen_documents,
    authenticate_frozen_documents,
    authenticate_tranche,
    build_proof_campaign,
    load_proof_campaign,
    stable_postgres_state,
)
from macroforge.sec_corporate_reporting_loader import (
    CANCEL_POLL_SECONDS,
    RECONCILIATION_QUERY_TIMEOUT_SECONDS,
    TERMINATE_POLL_SECONDS,
)
from tools.build_sec_corporate_portfolio_manifest import BoundedFetcher, configured_sec_identity


CAMPAIGN_TIMEOUT_SECONDS = 7200.0
RECONCILIATION_SCHEDULING_MARGIN_SECONDS = 5.0
TERMINAL_EVIDENCE_RESERVE_SECONDS = 5.0
# Four fixed probes/actions plus two poll windows, each of which may overrun by
# one bounded query, and an explicit scheduling margin.
RECONCILIATION_RESERVE_SECONDS = (
    4 * RECONCILIATION_QUERY_TIMEOUT_SECONDS
    + CANCEL_POLL_SECONDS + RECONCILIATION_QUERY_TIMEOUT_SECONDS
    + TERMINATE_POLL_SECONDS + RECONCILIATION_QUERY_TIMEOUT_SECONDS
    + RECONCILIATION_SCHEDULING_MARGIN_SECONDS
)
_TARGET = re.compile(
    r"^macroforge_task223_(?P<round>r[1-9][0-9]*)(?P<side>[ab])_"
    r"(?P<epoch>[1-9][0-9]*)_(?P<nonce>[1-9][0-9]*)$"
)
_FORBIDDEN_DATABASES = frozenset({"macroforge", "postgres", "template0", "template1"})
_TERMINAL_EMITTER: Any = None


def validate_database_targets(targets: Iterable[str]) -> tuple[str, str]:
    """Materialize once and require one canonical a/b TASK-223 disposable pair."""
    materialized = tuple(targets)
    if len(materialized) != 2 or not all(isinstance(target, str) for target in materialized):
        raise ValueError("TASK-223 database targets must be exactly two canonical names")
    pair = (materialized[0], materialized[1])
    if pair[0] == pair[1]:
        raise ValueError("TASK-223 database targets must be exactly two distinct names")
    matches = []
    for target in pair:
        if target in _FORBIDDEN_DATABASES:
            raise ValueError("TASK-223 database targets include a forbidden database")
        match = _TARGET.fullmatch(target)
        if match is None or len(target.encode("utf-8")) > 63:
            raise ValueError("TASK-223 database targets must be canonical disposable identifiers")
        matches.append(match)
    pair_keys = {(m.group("round"), m.group("epoch"), m.group("nonce")) for m in matches}
    if pair_keys.__len__() != 1 or {m.group("side") for m in matches} != {"a", "b"}:
        raise ValueError("TASK-223 database targets must be the matching a/b disposable pair")
    return pair


def _authenticate_database_target(target: str, *, psql_path: str = "psql") -> None:
    env = dict(os.environ)
    for key in ("PGDATABASE", "PGSERVICE", "PGSERVICEFILE", "PGOPTIONS", "PGAPPNAME"):
        env.pop(key, None)
    env["PGAPPNAME"] = "macroforge-task223-target-preflight"
    completed = subprocess.run(
        [psql_path, "-X", "-v", "ON_ERROR_STOP=1", "-q", "-A", "-t", "-d", target],
        input="SELECT current_database();\n", text=True, capture_output=True,
        timeout=RECONCILIATION_QUERY_TIMEOUT_SECONDS, env=env,
    )
    if completed.returncode:
        raise ValueError(f"TASK-223 database target authentication failed: {target}")
    actual = completed.stdout.strip()
    if actual != target:
        raise ValueError(f"current_database() mismatch for TASK-223 target {target}: {actual}")


def authenticate_database_targets(targets: Iterable[str], *, psql_path: str = "psql") -> tuple[str, str]:
    materialized = validate_database_targets(targets)
    for target in materialized:
        _authenticate_database_target(target, psql_path=psql_path)
    return materialized


def campaign_deadlines(started: float) -> tuple[float, float, float]:
    hard = started + CAMPAIGN_TIMEOUT_SECONDS
    reconciliation = hard - TERMINAL_EVIDENCE_RESERVE_SECONDS
    work = reconciliation - RECONCILIATION_RESERVE_SECONDS
    return hard, reconciliation, work


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def extraction_record(load: Any) -> dict[str, Any]:
    durations: list[int] = []
    dei: dict[str, set[str]] = {}
    for occurrence in load.report.occurrences:
        local = occurrence.concept.rsplit("}", 1)[-1]
        if local in {"DocumentType", "DocumentPeriodEndDate", "AmendmentFlag", "EntityCentralIndexKey"}:
            dei.setdefault(local, set()).add(occurrence.lexical_value)
    for context in load.report.contexts.values():
        if context.period[0] == "duration":
            durations.append((date.fromisoformat(context.period[2]) - date.fromisoformat(context.period[1])).days + 1)
    week_lengths = sorted({days // 7 for days in durations if days % 7 == 0 and 350 <= days <= 380})
    return {
        "accession": load.accession,
        "cik": load.cik,
        "form": load.form_type,
        "xbrl_format": "inline" if load.parser_contract == "sec-inline-xbrl-source-v1" else "traditional",
        "source_manifest_sha256": load.source_manifest_sha256,
        "dts_manifest_sha256": load.dts_manifest_sha256,
        "source_sha256": load.report.source_sha256,
        "parser_output_sha256": load.report.parser_output_sha256,
        "document_count": len(load.documents),
        "fact_count": len(load.report.occurrences),
        "context_count": len(load.report.contexts),
        "unit_count": len(load.report.units),
        "dimensioned_context_count": load.report.metrics["dimensioned_context_count"],
        "typed_member_count": load.report.metrics["typed_member_count"],
        "duplicate_slot_count": load.report.metrics["duplicate_slot_count"],
        "conflicting_slot_count": load.report.metrics["conflicting_slot_count"],
        "nil_occurrence_count": load.report.metrics.get("nil_occurrence_count", sum(item.nil for item in load.report.occurrences)),
        "inline_scale_count": load.report.metrics.get("inline_scale_count", 0),
        "inline_sign_count": load.report.metrics.get("inline_sign_count", 0),
        "dei_observed_values": {key: sorted(values) for key, values in sorted(dei.items())},
        "fiscal_duration_days": sorted(set(durations)),
        "fiscal_week_lengths": week_lengths,
        "relationship_original_accession": load.relationship_original_accession,
        "relationship_status": load.relationship_status,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--ledger", type=Path, required=True)
    parser.add_argument("--temporary-provider-root", type=Path, required=True)
    parser.add_argument("--reuse-provider-root", action="store_true")
    parser.add_argument("--status-file", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--database", action="append", default=[])
    parser.add_argument("--knowledge-cutoff", default="2026-08-18T00:00:00Z")
    parser.add_argument("--minimum-interval-seconds", type=float, default=0.12)
    args = parser.parse_args()

    global _TERMINAL_EMITTER
    started = time.monotonic()
    hard_deadline, reconciliation_deadline, work_deadline = campaign_deadlines(started)
    databases = authenticate_database_targets(args.database)
    campaign_id = uuid4().hex
    args.status_file.parent.mkdir(parents=True, exist_ok=True)
    args.status_file.touch(exist_ok=False)

    def emit(event: dict[str, Any]) -> None:
        payload = {
            "campaign_id": campaign_id,
            "elapsed_seconds": round(time.monotonic() - started, 6),
            "remaining_seconds": max(0.0, round(hard_deadline - time.monotonic(), 6)),
            **event,
        }
        line = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        with args.status_file.open("a", encoding="utf-8") as handle:
            handle.write(line + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        print(line, flush=True)

    _TERMINAL_EMITTER = emit

    def deadline_expired(_signum: int, _frame: Any) -> None:
        raise TimeoutError("TASK-223 whole-campaign 7200-second deadline expired")

    signal.signal(signal.SIGALRM, deadline_expired)
    hard_remaining = hard_deadline - time.monotonic()
    if hard_remaining <= 0:
        raise TimeoutError("TASK-223 whole-campaign 7200-second deadline expired during target preflight")
    signal.setitimer(signal.ITIMER_REAL, hard_remaining)
    emit({
        "event": "campaign_started", "deadline_seconds": CAMPAIGN_TIMEOUT_SECONDS,
        "database_targets": list(databases),
        "work_budget_seconds": work_deadline - started,
        "reconciliation_reserve_seconds": RECONCILIATION_RESERVE_SECONDS,
        "terminal_evidence_reserve_seconds": TERMINAL_EVIDENCE_RESERVE_SECONDS,
    })
    emit({"event": "target_preflight_passed", "database_targets": list(databases)})

    manifest, ledger = authenticate_tranche(args.manifest, args.ledger)
    emit({"event": "tranche_authenticated", "filing_acts": len(ledger["filing_acts"]),
          "explicit_absences": len(ledger["explicit_absences"])})
    if args.reuse_provider_root:
        acquired = authenticate_frozen_documents(
            manifest, ledger, args.temporary_provider_root,
        )
    else:
        fetch = BoundedFetcher(
            configured_sec_identity(), minimum_interval_seconds=args.minimum_interval_seconds,
        )
        acquired = acquire_frozen_documents(
            manifest, ledger, args.temporary_provider_root, fetch,
        )
    emit({"event": "acquisition_authenticated", "documents": len(acquired),
          "network_used": not args.reuse_provider_root})
    acquisition = acquisition_report(manifest, ledger, acquired)
    loads = build_proof_campaign(manifest, ledger, acquired)
    extraction = [extraction_record(load) for load in loads]
    if len(loads) != 19 or len({load.cik for load in loads}) != 15:
        raise RuntimeError("proof campaign does not contain the frozen 19 acts / 15 CIKs")
    traditional = [item for item in extraction if item["xbrl_format"] == "traditional"]
    if len(traditional) != 1 or traditional[0]["accession"] != "0001104659-21-062988" or traditional[0]["fact_count"] <= 0:
        raise RuntimeError("traditional Gatos proof is absent or empty")

    database_proofs = []
    for database_index, database in enumerate(databases, 1):
        emit({"event": "database_started", "database_ordinal": database_index})
        first = load_proof_campaign(
            loads, database_url=database, knowledge_cutoff=args.knowledge_cutoff,
            work_deadline=work_deadline, reconciliation_deadline=reconciliation_deadline,
            hard_deadline=hard_deadline, campaign_id=campaign_id,
            phase=f"d{database_index}-load", progress=emit,
        )
        before_replay = stable_postgres_state(
            database, deadline=work_deadline,
            application_name=f"macroforge-task223-d{database_index}-state1-{campaign_id[:12]}",
        )
        replay = load_proof_campaign(
            loads, database_url=database, knowledge_cutoff=args.knowledge_cutoff,
            work_deadline=work_deadline, reconciliation_deadline=reconciliation_deadline,
            hard_deadline=hard_deadline, campaign_id=campaign_id,
            phase=f"d{database_index}-replay", progress=emit,
        )
        after_replay = stable_postgres_state(
            database, deadline=work_deadline,
            application_name=f"macroforge-task223-d{database_index}-state2-{campaign_id[:12]}",
        )
        if before_replay != after_replay:
            raise RuntimeError("exact replay changed stable PostgreSQL state")
        database_proofs.append({
            "load_dispositions": first,
            "replay_dispositions": replay,
            "stable_state": after_replay,
            "replay_noop": True,
        })
        emit({"event": "database_completed", "database_ordinal": database_index,
              "state_sha256": after_replay["state_sha256"]})
    if len(database_proofs) > 1 and len({item["stable_state"]["state_sha256"] for item in database_proofs}) != 1:
        raise RuntimeError("fresh proof databases have different stable state identities")

    report: dict[str, Any] = {
        "schema": "macroforge.task223.corporate-proof-tranche-report.v1",
        "campaign_control": {
            "campaign_id": campaign_id,
            "database_targets": list(databases),
            "target_preflight": "passed",
            "hard_deadline_seconds": CAMPAIGN_TIMEOUT_SECONDS,
            "reconciliation_reserve_seconds": RECONCILIATION_RESERVE_SECONDS,
            "terminal_evidence_reserve_seconds": TERMINAL_EVIDENCE_RESERVE_SECONDS,
        },
        "source_manifest": {
            "semantic_identity": manifest["manifest_sha256"],
            "serialized_sha256": sha256(args.manifest.read_bytes()).hexdigest(),
            "byte_length": len(args.manifest.read_bytes()),
        },
        "ledger_sha256": ledger["ledger_sha256"],
        "counts": {
            "filing_acts": len(loads),
            "explicit_absences": len(ledger["explicit_absences"]),
            "unique_ciks": len({load.cik for load in loads}),
            "documents": len(acquired),
            "facts": sum(len(load.report.occurrences) for load in loads),
            "contexts": sum(len(load.report.contexts) for load in loads),
            "units": sum(len(load.report.units) for load in loads),
            "amendment_proposals": sum(load.relationship_original_accession is not None for load in loads),
        },
        "acquisition": acquisition,
        "extraction": extraction,
        "explicit_absences": ledger["explicit_absences"],
        "database_proofs": database_proofs,
        "provider_bodies_persisted_in_report_or_database": False,
        "semantic_equivalence_claimed": False,
        "restatement_status": "undetermined",
        "mapping_authority": False,
        "rights_or_release_authority": False,
        "remote_delivery_enabled": False,
    }
    report["report_sha256"] = sha256(canonical(report)).hexdigest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_bytes(canonical(report) + b"\n")
    signal.setitimer(signal.ITIMER_REAL, 0)
    emit({
        "event": "campaign_succeeded",
        "output": str(args.output), "report_sha256": report["report_sha256"],
        "counts": report["counts"],
        "database_state_sha256": [item["stable_state"]["state_sha256"] for item in database_proofs],
    })
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BaseException as error:
        signal.setitimer(signal.ITIMER_REAL, 0)
        if _TERMINAL_EMITTER is not None and not isinstance(error, SystemExit):
            _TERMINAL_EMITTER({
                "event": "campaign_timed_out" if isinstance(error, TimeoutError) else "campaign_failed",
                "error_type": type(error).__name__, "message": str(error),
            })
        raise
