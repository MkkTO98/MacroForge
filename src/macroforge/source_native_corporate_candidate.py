"""Deterministic source-native Corporate Reporting release-candidate contract.

This module constructs non-governed private-analysis candidate bytes from exact
source evidence.  It deliberately does not create mapping, rights, quality,
eligibility, release, publication, redistribution, or delivery authority.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
import json
import os
import re
import subprocess
from typing import Any, Mapping, Sequence

from macroforge.sec_corporate_portfolio import canonical_manifest_identity


class CandidateContractError(RuntimeError):
    pass


_HASH = re.compile(r"^[0-9a-f]{64}$")
_ACCESSION = re.compile(r"^[0-9]{10}-[0-9]{2}-[0-9]{6}$")
_EXPECTED_COUNTS = {
    "filings": 19,
    "documents": 147,
    "occurrences": 35_048,
    "slots": 32_381,
    "amendments": 2,
    "absences": 10,
}
_EXPECTED_LEDGER_SHA256 = "d55e413cae29d8abef44a871a22205d0504076ace916b1c643399ab7fb1a12b2"
_EXPECTED_MANIFEST_SHA256 = "937056b9e903daa5e3550ed18cb1dff6d34bb1fbc49e3bb8e1f51a8d4420516a"
_EXPECTED_SEC_CUTOFF = "2026-06-30T23:59:59Z"
_SEC_CUTOFF = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$")
_EXPECTED_PERMISSIONS = {
    "private_analysis_candidate": True,
    "publication": False,
    "redistribution": "not_authorized",
    "remote_delivery": False,
}
_EXPECTED_KNOWLEDGE_CUTOFF = {
    "applicable": False,
    "reason": "no_governed_knowledge_closure",
    "value": None,
}
_EXPECTED_FAILURE_ACCOUNTING = {
    "extraction_failure": 0,
    "intentional_exclusion": 0,
    "malformed_package": 0,
    "missing_package": 0,
    "technical_incompleteness": 0,
    "unresolved_dependency": 0,
}


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def _require_hash(value: object, label: str) -> str:
    if not isinstance(value, str) or _HASH.fullmatch(value) is None:
        raise CandidateContractError(f"{label} identity is malformed")
    return value


def _exact_keys(value: object, keys: set[str], label: str) -> Mapping[str, Any]:
    if not isinstance(value, Mapping) or set(value) != keys:
        raise CandidateContractError(f"{label} fields are incomplete or unknown")
    return value


def _ledger_identity(ledger: Mapping[str, Any]) -> str:
    return sha256(_canonical({key: value for key, value in ledger.items() if key != "ledger_sha256"})).hexdigest()


def _authenticate_inputs(ledger: Mapping[str, Any], source_manifest: Mapping[str, Any]) -> None:
    if _ledger_identity(ledger) != ledger.get("ledger_sha256") or ledger.get("ledger_sha256") != _EXPECTED_LEDGER_SHA256:
        raise CandidateContractError("ledger identity mismatch")
    semantic = canonical_manifest_identity(source_manifest)
    if source_manifest.get("manifest_sha256") != semantic or semantic != _EXPECTED_MANIFEST_SHA256:
        raise CandidateContractError("source manifest identity mismatch")
    source = ledger.get("source_manifest")
    bound = source.get("semantic_identity") if isinstance(source, Mapping) else ledger.get("source_manifest_sha256")
    if bound != semantic:
        raise CandidateContractError("ledger/source manifest identity mismatch")


def _validate_sec_cutoff(value: object, *, authenticated_cutoff: object) -> str:
    if not isinstance(value, str) or _SEC_CUTOFF.fullmatch(value) is None:
        raise CandidateContractError("SEC cutoff is malformed or noncanonical")
    try:
        parsed = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except ValueError as error:
        raise CandidateContractError("SEC cutoff is malformed or noncanonical") from error
    canonical = parsed.strftime("%Y-%m-%dT%H:%M:%SZ")
    if canonical != value:
        raise CandidateContractError("SEC cutoff is malformed or noncanonical")
    if authenticated_cutoff != _EXPECTED_SEC_CUTOFF or value != authenticated_cutoff:
        raise CandidateContractError("SEC cutoff differs from authenticated source authority")
    return value


@dataclass(frozen=True)
class SourceNativeCandidate:
    candidate_sha256: str
    payload: bytes
    payload_without_identity: bytes


def _expected_documents(package: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    rows: dict[str, Mapping[str, Any]] = {}
    for raw in package.get("documents", ()):
        if not isinstance(raw, Mapping) or raw.get("owner") != "sec_filing":
            continue
        name = str(raw.get("url", "")).rsplit("/", 1)[-1]
        if not name or name in rows:
            raise CandidateContractError("source manifest document identity is duplicate")
        rows[name] = raw
    return rows


def _project_documents(
    accession: str, documents: object, expected: Mapping[str, Mapping[str, Any]],
) -> list[dict[str, Any]]:
    if not isinstance(documents, Sequence) or isinstance(documents, (str, bytes)):
        raise CandidateContractError("document membership is malformed")
    projected: list[dict[str, Any]] = []
    names: set[str] = set()
    for raw in documents:
        row = _exact_keys(raw, {"name", "role", "byte_length", "sha256"}, "document membership")
        name = row["name"]
        if not isinstance(name, str) or not name or name in names:
            raise CandidateContractError("document membership contains a duplicate identity")
        names.add(name)
        authority = expected.get(name)
        manifest_roles = set(authority.get("roles", ())) if authority is not None else set()
        allowed_roles = set(manifest_roles)
        if not manifest_roles:
            allowed_roles.add("package_document")
        if authority is not None and ({"primary_document", "inline_instance"} & manifest_roles):
            allowed_roles.add("inline_xbrl_instance")
        if authority is not None and "instance_document" in manifest_roles:
            allowed_roles.add("sec_rendered_xbrl_instance")
        if (authority is None or row["sha256"] != authority.get("sha256") or
                row["byte_length"] != authority.get("byte_length") or row["role"] not in allowed_roles):
            raise CandidateContractError(f"document identity differs from source manifest: {accession}/{name}")
        projected.append({
            "byte_length": int(row["byte_length"]), "name": name, "role": row["role"],
            "sha256": _require_hash(row["sha256"], "document"),
        })
    if names != set(expected):
        raise CandidateContractError(f"document membership is incomplete for {accession}")
    return sorted(projected, key=lambda row: (row["name"], row["role"], row["sha256"]))


def _project_occurrences(accession: str, values: object) -> list[str]:
    if not isinstance(values, Sequence) or isinstance(values, (str, bytes)):
        raise CandidateContractError("occurrence membership is malformed")
    projected: list[str] = []
    for raw in values:
        row = _exact_keys(raw, {"filing_accession", "sha256"}, "occurrence membership")
        if row["filing_accession"] != accession:
            raise CandidateContractError("cross-filing occurrence membership identity")
        projected.append(_require_hash(row["sha256"], "occurrence"))
    if len(projected) != len(set(projected)):
        raise CandidateContractError("duplicate occurrence membership identity")
    return sorted(projected)


def _project_slots(accession: str, values: object) -> list[dict[str, Any]]:
    if not isinstance(values, Sequence) or isinstance(values, (str, bytes)):
        raise CandidateContractError("slot membership is malformed")
    projected: list[dict[str, Any]] = []
    identities: set[str] = set()
    for raw in values:
        row = _exact_keys(
            raw,
            {"filing_accession", "slot_sha256", "source_concept_qname", "fact_resolution_status"},
            "slot membership",
        )
        if row["filing_accession"] != accession:
            raise CandidateContractError("cross-filing slot membership identity")
        identity = _require_hash(row["slot_sha256"], "slot")
        if identity in identities:
            raise CandidateContractError("duplicate slot membership identity")
        identities.add(identity)
        concept = row["source_concept_qname"]
        resolution = row["fact_resolution_status"]
        if not isinstance(concept, str) or not concept or resolution not in {
            "accepted_identical", "conflict", "deferred", "rejected",
        }:
            raise CandidateContractError("slot concept or fact-resolution status is malformed")
        projected.append({
            "fact_resolution_status": resolution,
            "mapping": {
                "attribution": "task225-source-native-contract-v1",
                "disposition": "deliberately_unmapped",
            },
            "slot_sha256": identity,
            "source_concept_qname": concept,
        })
    return sorted(projected, key=lambda row: row["slot_sha256"])


def _project_absences(ledger: Mapping[str, Any]) -> list[dict[str, Any]]:
    frozen = list(ledger.get("frozen_absence_identities", ()))
    raw_rows = ledger.get("explicit_absences")
    if not isinstance(raw_rows, list) or len(raw_rows) != _EXPECTED_COUNTS["absences"]:
        raise CandidateContractError("portfolio absence membership count mismatch")
    projected: list[dict[str, Any]] = []
    for raw in raw_rows:
        if not isinstance(raw, Mapping):
            raise CandidateContractError("portfolio absence membership is malformed")
        identity = raw.get("expected_explicit_absence_identity") or raw.get("absence_identity")
        if raw.get("disposition") != "acquisition_cessation_absence":
            raise CandidateContractError("portfolio absence disposition is unsupported")
        projected.append({
            "absence_identity": _require_hash(identity, "portfolio absence"),
            "cik": raw.get("cik"),
            "disposition": "acquisition_cessation_absence",
            "expected_form": raw.get("expected_form"),
            "fiscal_period": raw.get("fiscal_period"),
            "issuer_fiscal_year": raw.get("issuer_fiscal_year"),
            "slot_id": raw.get("slot_id"),
        })
    identities = [row["absence_identity"] for row in projected]
    if len(set(identities)) != len(identities) or sorted(identities) != sorted(frozen):
        raise CandidateContractError("portfolio absence membership identity mismatch")
    return sorted(projected, key=lambda row: row["absence_identity"])


def _project_amendment(raw: object, authority: object) -> dict[str, Any] | None:
    if authority is None:
        if raw is not None:
            raise CandidateContractError("unexpected amendment membership")
        return None
    ledger = _exact_keys(
        authority,
        {"authoritative", "basis", "original_accession", "restatement_status"},
        "ledger amendment authority",
    )
    relation = _exact_keys(raw, {"original_accession", "relationship_type", "status"}, "amendment revision")
    if (relation["original_accession"] != ledger["original_accession"] or
            relation["relationship_type"] != "amends" or relation["status"] != "proposed" or
            ledger["authoritative"] is not False or ledger["restatement_status"] != "undetermined"):
        raise CandidateContractError("amendment revision differs from ledger authority")
    return {
        "assertion_status": "proposed", "authoritative": False,
        "basis": ledger["basis"], "original_accession": ledger["original_accession"],
        "relationship_type": "amends", "restatement_status": "undetermined",
    }


def _state_axes() -> list[dict[str, str]]:
    values = {
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
    return [{"axis": key, "status": value} for key, value in sorted(values.items())]


def build_source_native_candidate(
    *, ledger: Mapping[str, Any], source_manifest: Mapping[str, Any],
    source_snapshot: Mapping[str, Any], sec_cutoff: str,
    predecessor_candidate_sha256: str | None,
) -> SourceNativeCandidate:
    """Build canonical candidate bytes from exact authenticated source membership."""
    _authenticate_inputs(ledger, source_manifest)
    _validate_sec_cutoff(sec_cutoff, authenticated_cutoff=source_manifest.get("acceptance_cutoff"))
    if predecessor_candidate_sha256 is not None:
        _require_hash(predecessor_candidate_sha256, "predecessor candidate")
    raw_filings = source_snapshot.get("filings")
    if not isinstance(raw_filings, list):
        raise CandidateContractError("filing membership is malformed")
    acts = {str(row.get("accession")): row for row in ledger.get("filing_acts", ()) if isinstance(row, Mapping)}
    frozen = list(ledger.get("frozen_accessions", ()))
    if len(acts) != _EXPECTED_COUNTS["filings"] or set(acts) != set(frozen):
        raise CandidateContractError("ledger filing membership identity mismatch")
    packages = {
        str(row.get("accession")): row for row in source_manifest.get("package_results", ())
        if isinstance(row, Mapping) and row.get("accession") in acts
    }
    accessions = [str(row.get("accession")) for row in raw_filings if isinstance(row, Mapping)]
    if len(raw_filings) != len(accessions) or len(set(accessions)) != len(accessions):
        raise CandidateContractError("filing membership contains malformed or duplicate identity")
    if set(accessions) != set(frozen):
        raise CandidateContractError("filing membership differs from frozen exact scope")

    filings: list[dict[str, Any]] = []
    for raw in raw_filings:
        row = _exact_keys(raw, {
            "accession", "cik", "form", "report_period", "accepted_at",
            "source_manifest_sha256", "documents", "occurrence_sha256s", "slots", "amendment",
        }, "filing membership")
        accession = str(row["accession"])
        act = acts[accession]
        package = packages.get(accession)
        if package is None or canonical_manifest_identity(package) != act.get("manifest_package_identity"):
            raise CandidateContractError(f"filing package manifest identity mismatch: {accession}")
        if any(row[key] != act[expected] for key, expected in (
            ("cik", "cik"), ("form", "form"), ("report_period", "report_date"),
            ("accepted_at", "accepted_at"), ("source_manifest_sha256", "manifest_package_identity"),
        )):
            raise CandidateContractError(f"filing identity differs from ledger: {accession}")
        amendment = _project_amendment(row["amendment"], act.get("amendment_relationship"))
        documents = _project_documents(accession, row["documents"], _expected_documents(package))
        occurrences = _project_occurrences(accession, row["occurrence_sha256s"])
        slots = _project_slots(accession, row["slots"])
        cik = str(row["cik"])
        filings.append({
            "accepted_at": row["accepted_at"], "accession": accession,
            "amendment": amendment, "cik": cik, "documents": documents,
            "filer_identity": {"scheme": "sec:cik", "value": cik}, "form": row["form"],
            "occurrence_sha256s": occurrences, "report_period": row["report_period"],
            "reporting_entity_identity": {
                "scheme": "macroforge:corporate-reporting-entity", "value": f"sec:cik:{cik}",
            },
            "reporting_scope": {
                "identity_sha256": sha256(_canonical({"accession": accession, "kind": "source_native_filing"})).hexdigest(),
                "kind": "source_native_filing",
            },
            "slots": slots, "source_manifest_sha256": row["source_manifest_sha256"],
            "universal_company_identity": None,
        })
    filings.sort(key=lambda row: row["accession"])
    absences = _project_absences(ledger)
    observed = {
        "filings": len(filings), "documents": sum(len(row["documents"]) for row in filings),
        "occurrences": sum(len(row["occurrence_sha256s"]) for row in filings),
        "slots": sum(len(row["slots"]) for row in filings),
        "amendments": sum(row["amendment"] is not None for row in filings),
        "absences": len(absences),
    }
    if observed != _EXPECTED_COUNTS:
        raise CandidateContractError(f"exact membership count mismatch: {observed}")
    if sum(row["cik"] is not None for row in absences) != len(absences):
        raise CandidateContractError("portfolio absence identity is incomplete")

    body: dict[str, Any] = {
        "contract": {"name": "source-native-private-analysis", "version": "1"},
        "cutoffs": {
            "knowledge": {"applicable": False, "reason": "no_governed_knowledge_closure", "value": None},
            "sec": sec_cutoff,
        },
        "failure_accounting": {
            "extraction_failure": 0, "intentional_exclusion": 0, "malformed_package": 0,
            "missing_package": 0, "technical_incompleteness": 0, "unresolved_dependency": 0,
        },
        "filings": filings,
        "permissions": {
            "private_analysis_candidate": True, "publication": False,
            "redistribution": "not_authorized", "remote_delivery": False,
        },
        "predecessor_candidate_sha256": predecessor_candidate_sha256,
        "producer": {"domain": "corporate_reporting", "name": "MacroForge"},
        "portfolio_absences": absences,
        "representation_precedence": {
            "candidate": "candidate_v1_is_canonical_before_governed_admission",
            "governed": "authority_derived_v3_is_canonical_after_admission",
            "historical": "v2_and_stored_items_are_compatibility_views_and_must_agree",
        },
        "schema": "macroforge.corporate-reporting.source-native-candidate.v1",
        "state_axes": _state_axes(),
    }
    canonical = _canonical(body)
    identity = sha256(canonical).hexdigest()
    payload = _canonical({**body, "candidate_sha256": identity}) + b"\n"
    return SourceNativeCandidate(identity, payload, canonical)


def _validate_candidate_document(document: Mapping[str, Any]) -> None:
    _exact_keys(document, {
        "contract", "cutoffs", "failure_accounting", "filings", "permissions",
        "portfolio_absences", "predecessor_candidate_sha256", "producer",
        "representation_precedence", "schema", "state_axes",
    }, "candidate document")
    if _canonical(document.get("contract")) != _canonical({
        "name": "source-native-private-analysis", "version": "1",
    }):
        raise CandidateContractError("candidate private-analysis contract is malformed")
    cutoffs = _exact_keys(document.get("cutoffs"), {"knowledge", "sec"}, "candidate cutoffs")
    _validate_sec_cutoff(cutoffs.get("sec"), authenticated_cutoff=_EXPECTED_SEC_CUTOFF)
    if _canonical(cutoffs.get("knowledge")) != _canonical(_EXPECTED_KNOWLEDGE_CUTOFF):
        raise CandidateContractError("candidate knowledge cutoff posture is malformed")
    if _canonical(document.get("permissions")) != _canonical(_EXPECTED_PERMISSIONS):
        raise CandidateContractError("candidate private-analysis permission posture is not exact")
    if _canonical(document.get("failure_accounting")) != _canonical(_EXPECTED_FAILURE_ACCOUNTING):
        raise CandidateContractError("candidate failure accounting is malformed")
    if _canonical(document.get("state_axes")) != _canonical(_state_axes()):
        raise CandidateContractError("candidate private-analysis state axes are not exact")
    if document.get("schema") != "macroforge.corporate-reporting.source-native-candidate.v1":
        raise CandidateContractError("candidate schema is malformed")
    if _canonical(document.get("producer")) != _canonical({
        "domain": "corporate_reporting", "name": "MacroForge",
    }):
        raise CandidateContractError("candidate producer is malformed")
    expected_precedence = {
        "candidate": "candidate_v1_is_canonical_before_governed_admission",
        "governed": "authority_derived_v3_is_canonical_after_admission",
        "historical": "v2_and_stored_items_are_compatibility_views_and_must_agree",
    }
    if _canonical(document.get("representation_precedence")) != _canonical(expected_precedence):
        raise CandidateContractError("candidate representation precedence is malformed")
    predecessor = document.get("predecessor_candidate_sha256")
    if predecessor is not None:
        _require_hash(predecessor, "predecessor candidate")

    filings = document.get("filings")
    absences = document.get("portfolio_absences")
    if not isinstance(filings, list) or not isinstance(absences, list):
        raise CandidateContractError("candidate exact membership is malformed")
    try:
        observed = {
            "filings": len(filings),
            "documents": sum(len(row["documents"]) for row in filings),
            "occurrences": sum(len(row["occurrence_sha256s"]) for row in filings),
            "slots": sum(len(row["slots"]) for row in filings),
            "amendments": sum(row["amendment"] is not None for row in filings),
            "absences": len(absences),
        }
    except (KeyError, TypeError) as error:
        raise CandidateContractError("candidate exact membership is malformed") from error
    if observed != _EXPECTED_COUNTS:
        raise CandidateContractError(f"candidate exact membership count mismatch: {observed}")
    for filing in filings:
        if not isinstance(filing, Mapping):
            raise CandidateContractError("candidate filing membership is malformed")
        for slot in filing["slots"]:
            if not isinstance(slot, Mapping) or _canonical(slot.get("mapping")) != _canonical({
                "attribution": "task225-source-native-contract-v1",
                "disposition": "deliberately_unmapped",
            }):
                raise CandidateContractError("candidate mapping posture is not deliberately unmapped")
    if any(
        not isinstance(row, Mapping) or row.get("disposition") != "acquisition_cessation_absence"
        for row in absences
    ):
        raise CandidateContractError("candidate absence posture is malformed")


def _verify_candidate(candidate: SourceNativeCandidate) -> Mapping[str, Any]:
    if type(candidate) is not SourceNativeCandidate:
        raise CandidateContractError("exact SourceNativeCandidate value is required")
    try:
        document = json.loads(candidate.payload)
        identity = document.pop("candidate_sha256")
    except (json.JSONDecodeError, KeyError, TypeError) as error:
        raise CandidateContractError("candidate payload is malformed") from error
    canonical = _canonical(document)
    actual = sha256(canonical).hexdigest()
    expected_payload = _canonical({**document, "candidate_sha256": actual}) + b"\n"
    if (identity != actual or candidate.candidate_sha256 != actual or
            candidate.payload_without_identity != canonical or candidate.payload != expected_payload):
        raise CandidateContractError("candidate canonical identity or digest mismatch")
    _validate_candidate_document(document)
    return {**document, "candidate_sha256": actual}


def representation_precedence(
    representation: str, *, candidate_sha256: str,
    governed_release_sha256: str | None = None, compatibility_sha256: str | None = None,
) -> str:
    """Resolve the one canonical representation and fail closed on compatibility drift."""
    _require_hash(candidate_sha256, "candidate")
    if representation == "candidate_v1":
        if governed_release_sha256 is not None:
            raise CandidateContractError("candidate_v1 cannot override governed v3")
        return representation
    if representation == "governed_v3":
        _require_hash(governed_release_sha256, "governed release")
        return representation
    if representation in {"historical_v2", "stored_release_items"}:
        governed = _require_hash(governed_release_sha256, "governed release")
        compatibility = _require_hash(compatibility_sha256, "compatibility")
        if compatibility != governed:
            raise CandidateContractError("historical compatibility representation disagrees with governed v3")
        return "governed_v3"
    raise CandidateContractError("unknown release representation")


def _sql_literal(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def _run_psql(database_url: str, statement: str, *, timeout: float = 180.0) -> str:
    env = dict(os.environ)
    env["PGAPPNAME"] = "macroforge-task225-candidate"
    completed = subprocess.run(
        ["psql", "-X", "-v", "ON_ERROR_STOP=1", "-q", "-A", "-t", "-d", database_url],
        input=statement, text=True, capture_output=True, timeout=timeout, env=env,
    )
    if completed.returncode:
        raise CandidateContractError(completed.stderr.strip() or "candidate PostgreSQL operation failed")
    return completed.stdout.strip()


def persist_source_native_candidate(
    *, database_url: str, candidate: SourceNativeCandidate,
) -> dict[str, Any]:
    """Atomically admit one immutable candidate in disposable PostgreSQL scope."""
    document = _verify_candidate(candidate)
    payload_text = candidate.payload.decode().strip()
    payload_sha256 = sha256(candidate.payload).hexdigest()
    predecessor = document["predecessor_candidate_sha256"]
    predecessor_sql = "NULL" if predecessor is None else _sql_literal(predecessor)
    values: list[str] = [
        "BEGIN;",
        "SET LOCAL lock_timeout='5s'; SET LOCAL statement_timeout='120s'; SET LOCAL search_path=pg_catalog;",
        "SELECT corporate_reporting.assert_source_native_candidate_boundary("
        f"{_sql_literal(candidate.candidate_sha256)});",
        "INSERT INTO corporate_reporting.source_native_candidate"
        "(candidate_sha256,contract_version,sec_cutoff,knowledge_cutoff_applicable,"
        "predecessor_candidate_sha256,payload_sha256,candidate_document) VALUES ("
        f"{_sql_literal(candidate.candidate_sha256)},'1',{_sql_literal(document['cutoffs']['sec'])}::timestamptz,"
        f"false,{predecessor_sql},{_sql_literal(payload_sha256)},{_sql_literal(payload_text)}::jsonb) "
        "ON CONFLICT(candidate_sha256) DO NOTHING;",
    ]
    for ordinal, filing in enumerate(document["filings"], 1):
        member = _canonical(filing).decode()
        values.append(
            "INSERT INTO corporate_reporting.source_native_candidate_filing_member"
            "(candidate_sha256,item_ordinal,accession,member_sha256,member_document) VALUES ("
            f"{_sql_literal(candidate.candidate_sha256)},{ordinal},{_sql_literal(filing['accession'])},"
            f"{_sql_literal(sha256(member.encode()).hexdigest())},{_sql_literal(member)}::jsonb) "
            "ON CONFLICT(candidate_sha256,item_ordinal) DO NOTHING;"
        )
    for ordinal, absence in enumerate(document["portfolio_absences"], 1):
        member = _canonical(absence).decode()
        values.append(
            "INSERT INTO corporate_reporting.source_native_candidate_absence_member"
            "(candidate_sha256,item_ordinal,absence_identity,disposition,member_sha256,member_document) VALUES ("
            f"{_sql_literal(candidate.candidate_sha256)},{ordinal},{_sql_literal(absence['absence_identity'])},"
            f"{_sql_literal(absence['disposition'])},{_sql_literal(sha256(member.encode()).hexdigest())},"
            f"{_sql_literal(member)}::jsonb) ON CONFLICT(candidate_sha256,item_ordinal) DO NOTHING;"
        )
    for axis in document["state_axes"]:
        values.append(
            "INSERT INTO corporate_reporting.source_native_candidate_state_axis"
            "(candidate_sha256,axis_name,status) VALUES ("
            f"{_sql_literal(candidate.candidate_sha256)},{_sql_literal(axis['axis'])},{_sql_literal(axis['status'])}) "
            "ON CONFLICT(candidate_sha256,axis_name) DO NOTHING;"
        )
    values.extend([
        "SELECT jsonb_build_object('candidate_sha256',candidate_sha256,'payload_sha256',payload_sha256)::text "
        "FROM corporate_reporting.source_native_candidate WHERE candidate_sha256="
        f"{_sql_literal(candidate.candidate_sha256)};",
        "COMMIT;",
    ])
    output = _run_psql(database_url, "\n".join(values))
    rows = [line for line in output.splitlines() if line.startswith("{")]
    if len(rows) != 1:
        raise CandidateContractError("candidate persistence did not resolve one exact row")
    result = json.loads(rows[0])
    if result != {"candidate_sha256": candidate.candidate_sha256, "payload_sha256": payload_sha256}:
        raise CandidateContractError("candidate replay conflicts with persisted identity")
    return result


def candidate_database_state(database_url: str) -> dict[str, Any]:
    statement = """
    WITH counts AS (
      SELECT jsonb_build_object(
       'absence_members',(SELECT count(*) FROM ONLY corporate_reporting.source_native_candidate_absence_member),
       'candidates',(SELECT count(*) FROM ONLY corporate_reporting.source_native_candidate),
       'filing_members',(SELECT count(*) FROM ONLY corporate_reporting.source_native_candidate_filing_member),
       'state_axes',(SELECT count(*) FROM ONLY corporate_reporting.source_native_candidate_state_axis)) value
    ), rows AS (
      SELECT 'candidate' kind,candidate_sha256 key,candidate_document value FROM ONLY corporate_reporting.source_native_candidate
      UNION ALL SELECT 'filing',candidate_sha256||':'||item_ordinal,member_document FROM ONLY corporate_reporting.source_native_candidate_filing_member
      UNION ALL SELECT 'absence',candidate_sha256||':'||item_ordinal,member_document FROM ONLY corporate_reporting.source_native_candidate_absence_member
      UNION ALL SELECT 'axis',candidate_sha256||':'||axis_name,jsonb_build_object('axis',axis_name,'status',status) FROM ONLY corporate_reporting.source_native_candidate_state_axis
    ) SELECT jsonb_build_object('counts',(SELECT value FROM counts),'state_sha256',
      encode(digest(COALESCE(string_agg(kind||':'||key||':'||corporate_reporting.canonical_json(value),E'\\n' ORDER BY kind,key),''),'sha256'),'hex'))::text FROM rows;
    """
    output = _run_psql(database_url, statement)
    try:
        return json.loads(output)
    except json.JSONDecodeError as error:
        raise CandidateContractError("candidate database state is malformed") from error


def read_source_native_snapshot(database_url: str) -> dict[str, Any]:
    """Read exact source membership from one TASK-223-compatible disposable database."""
    statement = """
    WITH filings AS (
      SELECT f.filing_id,f.accession,i.normalized_value cik,f.form_type form,f.report_period_end::text report_period,
       to_char(f.accepted_at AT TIME ZONE 'UTC','YYYY-MM-DD"T"HH24:MI:SS.MS"Z"') accepted_at,
       f.source_manifest_sha256
      FROM corporate_reporting.filing_submission f
      JOIN corporate_reporting.entity_identifier i ON i.entity_id=f.filer_entity_id AND i.scheme='sec:cik'
    )
    SELECT jsonb_build_object('filings',jsonb_agg(jsonb_build_object(
      'accession',f.accession,'cik',f.cik,'form',f.form,'report_period',f.report_period,
      'accepted_at',f.accepted_at,'source_manifest_sha256',f.source_manifest_sha256,
      'documents',(SELECT jsonb_agg(jsonb_build_object('name',d.document_name,'role',d.document_role,
        'byte_length',d.byte_length,'sha256',d.sha256) ORDER BY d.document_name,d.document_role,d.sha256)
        FROM corporate_reporting.filing_document d WHERE d.filing_id=f.filing_id),
      'occurrence_sha256s',(SELECT jsonb_agg(jsonb_build_object('filing_accession',f.accession,
        'sha256',o.occurrence_sha256) ORDER BY o.occurrence_sha256)
        FROM corporate_reporting.fact_occurrence o WHERE o.filing_id=f.filing_id),
      'slots',(SELECT jsonb_agg(resolved.slot_document ORDER BY resolved.slot_sha256) FROM (
        SELECT s.slot_sha256,jsonb_build_object('filing_accession',f.accession,
        'slot_sha256',s.slot_sha256,'source_concept_qname','{'||c.namespace_uri||'}'||c.local_name,
        'fact_resolution_status',CASE WHEN count(DISTINCT jsonb_build_array(o.lexical_value,o.nil_flag,o.decimals,o.precision))>1
          THEN 'conflict' ELSE 'accepted_identical' END) slot_document
        FROM corporate_reporting.fact_semantic_slot s
        JOIN corporate_reporting.source_concept c ON c.source_concept_id=s.source_concept_id
        JOIN corporate_reporting.fact_slot_occurrence so ON so.fact_slot_id=s.fact_slot_id AND so.parser_run_id=s.parser_run_id
        JOIN corporate_reporting.fact_occurrence o ON o.fact_occurrence_id=so.fact_occurrence_id
        WHERE s.filing_id=f.filing_id GROUP BY s.fact_slot_id,s.slot_sha256,c.namespace_uri,c.local_name
       ) resolved),
      'amendment',(SELECT jsonb_build_object('original_accession',p.accession,'relationship_type',r.relationship_type,
        'status',r.assertion_status) FROM corporate_reporting.filing_relationship_revision r
        JOIN corporate_reporting.filing_submission p ON p.filing_id=r.predecessor_filing_id
        WHERE r.successor_filing_id=f.filing_id)
    ) ORDER BY f.accession))::text FROM filings f;
    """
    output = _run_psql(database_url, statement, timeout=300.0)
    try:
        value = json.loads(output)
    except json.JSONDecodeError as error:
        raise CandidateContractError("source snapshot query returned malformed JSON") from error
    if not isinstance(value, dict):
        raise CandidateContractError("source snapshot query returned no membership")
    return value
