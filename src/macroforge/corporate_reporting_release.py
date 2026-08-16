"""Typed, fail-closed private Corporate Reporting release contract."""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
from typing import Any, Mapping


class EligibilityError(RuntimeError):
    pass


class ImmutableReleaseConflict(RuntimeError):
    pass


_HASH = re.compile(r"^[0-9a-f]{64}$")
_ITEM_FIELDS = frozenset({
    "item_key", "provider", "accession", "report_period", "canonical_concept",
    "scope", "dimensions", "unit", "state", "value",
    "mapping_evidence_fingerprint", "resolution_evidence_fingerprint",
    "source_occurrence_fingerprints", "parser_selection_revision_id",
    "resolution_revision_id", "mapping_revision_id", "absence_revision_id",
})
_EXTERNAL_EVIDENCE_FIELDS = frozenset({"source_refs", "mapping", "equivalence", "quality"})


def _hash(value: str, label: str) -> str:
    if not isinstance(value, str) or not _HASH.fullmatch(value):
        raise EligibilityError(f"malformed {label}")
    return value


@dataclass(frozen=True)
class ReleasePolicy:
    policy_id: str
    policy_version: str
    policy_sha256: str
    allowed_output_family: str = "private_analysis"


@dataclass(frozen=True)
class ExpectedSelection:
    revision_id: str
    selection_sha256: str
    status: str
    expected_item_keys: tuple[str, ...]


@dataclass(frozen=True)
class ReleaseEligibility:
    revision_id: str
    status: str
    reason_codes: tuple[str, ...]
    policy_id: str
    expected_selection_revision_id: str
    knowledge_snapshot_id: str
    source_manifest_sha256: str
    quality_decision_sha256: str


@dataclass(frozen=True)
class AuthorityRevisions:
    parser_source_revision_id: str
    expected_selection_revision_id: str
    knowledge_snapshot_id: str


@dataclass(frozen=True)
class ReleaseAuthorityEvidence:
    source_manifest: Mapping[str, Any]
    quality_decision: Mapping[str, Any]


def _validate_exact_mapping(value: object, label: str, allowed: set[str]) -> Mapping[str, Any]:
    if not isinstance(value, Mapping):
        raise EligibilityError(f"malformed {label}")
    unknown = set(value) - allowed
    missing = allowed - set(value)
    if unknown:
        raise EligibilityError(f"unknown {label} fields: {sorted(unknown)}")
    if missing:
        raise EligibilityError(f"{label} missing required fields: {sorted(missing)}")
    return value


def _validate_source_refs(value: object) -> None:
    if not isinstance(value, (tuple, list)):
        raise EligibilityError("malformed source_refs")
    for ref in value:
        row = _validate_exact_mapping(ref, "source ref", {"occurrence_sha256"})
        _hash(row["occurrence_sha256"], "source ref occurrence")


def _authority_evidence_roots(
    evidence: ReleaseAuthorityEvidence,
    authority: AuthorityRevisions,
) -> tuple[str, str]:
    """Validate and recompute the two release-authority roots."""
    if not isinstance(evidence, ReleaseAuthorityEvidence):
        raise EligibilityError("typed authority evidence is required")
    source = _validate_exact_mapping(
        evidence.source_manifest,
        "source manifest",
        {"schema", "provider", "source_set_id", "documents"},
    )
    if source["schema"] != "macroforge-corporate-source-manifest-v1" or source["provider"] != "SEC":
        raise EligibilityError("unsupported source manifest authority")
    if not isinstance(source["source_set_id"], str) or not source["source_set_id"]:
        raise EligibilityError("malformed source set identity")
    documents = source["documents"]
    if not isinstance(documents, (tuple, list)) or not documents:
        raise EligibilityError("source manifest has no documents")
    projected_documents: list[dict[str, str]] = []
    accessions: set[str] = set()
    for value in documents:
        row = _validate_exact_mapping(value, "source document", {"accession", "sha256"})
        accession = row["accession"]
        if not isinstance(accession, str) or not accession or accession in accessions:
            raise EligibilityError("malformed or duplicate source accession")
        accessions.add(accession)
        projected_documents.append({"accession": accession, "sha256": _hash(row["sha256"], "source document")})
    source_document = {
        "schema": source["schema"],
        "provider": source["provider"],
        "source_set_id": source["source_set_id"],
        "documents": sorted(projected_documents, key=lambda row: row["accession"]),
    }

    quality = _validate_exact_mapping(
        evidence.quality_decision,
        "quality decision",
        {"schema", "decision_id", "status", "knowledge_snapshot_id", "checks"},
    )
    if quality["schema"] != "macroforge-corporate-quality-decision-v1":
        raise EligibilityError("unsupported quality decision authority")
    if (not isinstance(quality["decision_id"], str) or not quality["decision_id"] or
            quality["status"] != "accepted" or
            quality["knowledge_snapshot_id"] != authority.knowledge_snapshot_id):
        raise EligibilityError("quality decision is not accepted and authority-bound")
    checks = quality["checks"]
    if not isinstance(checks, (tuple, list)) or not checks:
        raise EligibilityError("quality decision has no checks")
    projected_checks: list[dict[str, str]] = []
    check_ids: set[str] = set()
    for value in checks:
        row = _validate_exact_mapping(value, "quality check", {"check_id", "status", "evidence_sha256"})
        check_id = row["check_id"]
        if (not isinstance(check_id, str) or not check_id or check_id in check_ids or
                row["status"] != "passed"):
            raise EligibilityError("quality decision contains invalid, duplicate, or nonpassing checks")
        check_ids.add(check_id)
        projected_checks.append({
            "check_id": check_id,
            "status": row["status"],
            "evidence_sha256": _hash(row["evidence_sha256"], "quality check evidence"),
        })
    quality_document = {
        "schema": quality["schema"],
        "decision_id": quality["decision_id"],
        "status": quality["status"],
        "knowledge_snapshot_id": quality["knowledge_snapshot_id"],
        "checks": sorted(projected_checks, key=lambda row: row["check_id"]),
    }

    canonical = lambda document: json.dumps(
        document, sort_keys=True, separators=(",", ":"), ensure_ascii=False,
    ).encode()
    return sha256(canonical(source_document)).hexdigest(), sha256(canonical(quality_document)).hexdigest()


@dataclass(frozen=True)
class ReleaseItem:
    item_key: str
    provider: str
    accession: str
    report_period: str
    canonical_concept: str
    scope: str
    dimensions: tuple[Mapping[str, Any], ...]
    unit: Mapping[str, Any] | None
    state: str
    value: str | None
    mapping_evidence_fingerprint: str
    resolution_evidence_fingerprint: str
    source_occurrence_fingerprints: tuple[str, ...]
    parser_selection_revision_id: str
    resolution_revision_id: str
    mapping_revision_id: str
    absence_revision_id: str | None = None

    @classmethod
    def from_mapping(cls, item: Mapping[str, Any]) -> "ReleaseItem":
        # Recognize evidence containers before checking top-level fields, so a
        # nested internal-only key cannot be obscured by a generic rejection.
        if "source_refs" in item:
            _validate_source_refs(item["source_refs"])
        if "mapping" in item:
            _validate_exact_mapping(item["mapping"], "mapping", {"revision_id", "evidence_sha256"})
        if "equivalence" in item:
            _validate_exact_mapping(item["equivalence"], "equivalence", {"revision_id", "evidence_sha256"})
        if "quality" in item:
            _validate_exact_mapping(item["quality"], "quality", {"decision_sha256", "evidence_sha256"})
        unknown = set(item) - _ITEM_FIELDS - _EXTERNAL_EVIDENCE_FIELDS
        missing = (_ITEM_FIELDS - {"absence_revision_id"}) - set(item)
        if unknown or missing:
            detail = f"unknown item fields: {sorted(unknown)}" if unknown else f"item missing fields: {sorted(missing)}"
            raise EligibilityError(detail)
        try:
            return cls(**{key: item[key] for key in _ITEM_FIELDS if key in item})  # type: ignore[arg-type]
        except TypeError as error:
            raise EligibilityError(f"malformed item: {error}") from error


@dataclass(frozen=True)
class CorporateRelease:
    release_id: str
    payload: bytes
    output_family: str


def _validate_nested_item(item: ReleaseItem) -> None:
    if not isinstance(item.dimensions, (tuple, list)):
        raise EligibilityError("malformed dimensions")
    for dimension in item.dimensions:
        row = _validate_exact_mapping(
            dimension, "dimension", {"axis", "member_kind", "explicit_member", "typed_member"},
        )
        if not isinstance(row["axis"], str) or not row["axis"]:
            raise EligibilityError("malformed dimension axis")
        if row["member_kind"] == "explicit":
            if (not isinstance(row["explicit_member"], str) or not row["explicit_member"] or
                    row["typed_member"] is not None):
                raise EligibilityError("malformed explicit dimension member")
        elif row["member_kind"] == "typed":
            if row["explicit_member"] is not None:
                raise EligibilityError("malformed typed dimension member")
            member = _validate_exact_mapping(row["typed_member"], "typed member", {"sha256"})
            _hash(member["sha256"], "typed member")
        else:
            raise EligibilityError("malformed dimension member kind")
    if item.unit is not None:
        unit = _validate_exact_mapping(item.unit, "unit", {"numerator", "denominator"})
        numerator, denominator = unit["numerator"], unit["denominator"]
        if (not isinstance(numerator, (tuple, list)) or
                not isinstance(denominator, (tuple, list)) or not numerator or
                not all(isinstance(v, str) and v for v in (*numerator, *denominator))):
            raise EligibilityError("malformed unit")


def _validate_item(item: ReleaseItem, authority: AuthorityRevisions) -> None:
    if type(item) is not ReleaseItem:
        raise EligibilityError("items must be exact ReleaseItem values; subclasses are forbidden")
    if not item.item_key or not item.provider or not item.accession or not item.canonical_concept:
        raise EligibilityError("item identity fields must be non-empty")
    _validate_nested_item(item)
    for field in ("mapping_evidence_fingerprint", "resolution_evidence_fingerprint"):
        _hash(getattr(item, field), field)
    for fingerprint in item.source_occurrence_fingerprints:
        _hash(fingerprint, "source occurrence fingerprint")
    if item.parser_selection_revision_id != authority.parser_source_revision_id:
        raise EligibilityError("item parser/source revision is not contract-bound")
    if not item.resolution_revision_id or not item.mapping_revision_id:
        raise EligibilityError("item resolution/mapping revision is missing")
    if item.state == "reported":
        if item.value is None or not item.source_occurrence_fingerprints:
            raise EligibilityError("reported item lacks value/source occurrence evidence")
        if item.absence_revision_id is not None:
            raise EligibilityError("reported item carries absence authority")
    elif item.state == "nil":
        if item.value is not None or not item.source_occurrence_fingerprints:
            raise EligibilityError("nil item must have source occurrence evidence and no value")
        if item.absence_revision_id is not None:
            raise EligibilityError("nil item carries absence authority")
    elif item.state == "not_reported":
        if item.value is not None or item.source_occurrence_fingerprints or not item.absence_revision_id:
            raise EligibilityError("unproven absence")
    else:
        raise EligibilityError(f"item state {item.state} blocks release")


def _dimension_document(value: Mapping[str, Any]) -> dict[str, Any]:
    """Project one validated dimension through an explicit recursive allowlist."""
    typed = value["typed_member"]
    return {
        "axis": value["axis"],
        "member_kind": value["member_kind"],
        "explicit_member": value["explicit_member"],
        "typed_member": None if typed is None else {"sha256": typed["sha256"]},
    }


def _unit_document(value: Mapping[str, Any] | None) -> dict[str, Any] | None:
    if value is None:
        return None
    return {
        "numerator": list(value["numerator"]),
        "denominator": list(value["denominator"]),
    }


def _item_document(item: ReleaseItem) -> dict[str, Any]:
    """Emit only the frozen external item contract, never dataclass internals."""
    return {
        "item_key": item.item_key,
        "provider": item.provider,
        "accession": item.accession,
        "report_period": item.report_period,
        "canonical_concept": item.canonical_concept,
        "scope": item.scope,
        "dimensions": [_dimension_document(value) for value in item.dimensions],
        "unit": _unit_document(item.unit),
        "state": item.state,
        "value": item.value,
        "mapping_evidence_fingerprint": item.mapping_evidence_fingerprint,
        "resolution_evidence_fingerprint": item.resolution_evidence_fingerprint,
        "source_occurrence_fingerprints": list(item.source_occurrence_fingerprints),
        "parser_selection_revision_id": item.parser_selection_revision_id,
        "resolution_revision_id": item.resolution_revision_id,
        "mapping_revision_id": item.mapping_revision_id,
        "absence_revision_id": item.absence_revision_id,
    }


def _authority_document(authority: AuthorityRevisions) -> dict[str, str]:
    """Emit the complete current authority contract through an explicit allowlist."""
    return {
        "parser_source_revision_id": authority.parser_source_revision_id,
        "expected_selection_revision_id": authority.expected_selection_revision_id,
        "knowledge_snapshot_id": authority.knowledge_snapshot_id,
    }


def _build_private_release_from_values(
    subscription_id: str,
    sec_cutoff: str,
    items: tuple[ReleaseItem, ...],
    *,
    eligibility: ReleaseEligibility,
    policy: ReleasePolicy,
    expected_selection: ExpectedSelection,
    authority: AuthorityRevisions,
    authority_evidence: ReleaseAuthorityEvidence,
    output_family: str = "private_analysis",
) -> CorporateRelease:
    """Build bytes only when every item and authority exactly closes the selection."""
    if not all(isinstance(v, str) and v for v in (subscription_id, sec_cutoff)):
        raise EligibilityError("subscription and cutoff are required")
    if output_family != "private_analysis" or policy.allowed_output_family != output_family:
        raise EligibilityError("public or unauthorized output family")
    _hash(policy.policy_sha256, "policy hash")
    _hash(expected_selection.selection_sha256, "selection hash")
    _hash(eligibility.source_manifest_sha256, "source manifest hash")
    _hash(eligibility.quality_decision_sha256, "quality decision hash")
    source_root, quality_root = _authority_evidence_roots(authority_evidence, authority)
    if (source_root != eligibility.source_manifest_sha256 or
            quality_root != eligibility.quality_decision_sha256):
        raise EligibilityError("eligibility authority roots do not match recomputed evidence")
    if eligibility.status != "eligible" or eligibility.reason_codes:
        raise EligibilityError("eligibility is blocked")
    if expected_selection.status != "accepted":
        raise EligibilityError("expected selection is not accepted")
    if (eligibility.policy_id != policy.policy_id or
            eligibility.expected_selection_revision_id != expected_selection.revision_id or
            eligibility.knowledge_snapshot_id != authority.knowledge_snapshot_id or
            authority.expected_selection_revision_id != expected_selection.revision_id):
        raise EligibilityError("release authorities are not mutually bound")
    if not items or not expected_selection.expected_item_keys:
        raise EligibilityError("closed selection has no items")
    actual = tuple(item.item_key for item in items if isinstance(item, ReleaseItem))
    if len(actual) != len(items) or len(set(actual)) != len(actual):
        raise EligibilityError("duplicate or untyped release item")
    if set(actual) != set(expected_selection.expected_item_keys) or len(actual) != len(expected_selection.expected_item_keys):
        raise EligibilityError("release item set is partial or unexpected")
    for item in items:
        _validate_item(item, authority)
    item_documents = [_item_document(item) for item in sorted(items, key=lambda i: i.item_key)]
    body = {
        "schema": "macroforge-corporate-private-analysis-release-v2",
        "output_family": output_family,
        "subscription_id": subscription_id,
        "sec_cutoff": sec_cutoff,
        "selection_sha256": expected_selection.selection_sha256,
        "knowledge_snapshot_id": authority.knowledge_snapshot_id,
        "eligibility_revision_id": eligibility.revision_id,
        "source_manifest_sha256": eligibility.source_manifest_sha256,
        "quality_decision_sha256": eligibility.quality_decision_sha256,
        "policy": {"id": policy.policy_id, "version": policy.policy_version, "sha256": policy.policy_sha256},
        "authority": _authority_document(authority),
        "items": item_documents,
    }
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    release_id = sha256(canonical).hexdigest()
    payload = json.dumps({**body, "release_id": release_id}, sort_keys=True,
                         separators=(",", ":"), ensure_ascii=False).encode() + b"\n"
    return CorporateRelease(release_id, payload, output_family)


def build_private_release(*, authority: Any, store: Any) -> CorporateRelease:
    """Build canonical private bytes from a database-resolved opaque authority only."""
    from macroforge.corporate_reporting_queries import (
        CorporateAuthorityRef, PostgresCorporateAuthorityStore,
    )
    if type(authority) is not CorporateAuthorityRef:
        raise TypeError("database authority reference is required")
    if type(store) is not PostgresCorporateAuthorityStore:
        raise TypeError("concrete PostgreSQL authority store is required")
    resolved = store.resolve(authority)
    # Recursively project only the deliberately public authority metadata.  Source
    # locators, quality SQL/details and internal identifiers never enter the release.
    filing = resolved["filing"]
    policy = resolved["policy"]
    expected = resolved["expected_selection"]
    eligibility = resolved["eligibility"]
    public_items: list[dict[str, Any]] = []
    for raw in resolved["items"]:
        public_items.append({
            "item_key": raw["item_key"], "provider": raw["provider"],
            "accession": raw["accession"], "report_period": raw["report_period"],
            "canonical_concept": raw["canonical_concept"], "scope": raw["scope"],
            "dimensions": [{"axis": d["axis"], "member_kind": d["member_kind"],
                "explicit_member": d["explicit_member"],
                "typed_member": None if d["typed_member"] is None else {"sha256": d["typed_member"]["sha256"]}}
                for d in raw["dimensions"]],
            "unit": None if raw["unit"] is None else {
                "numerator": list(raw["unit"]["numerator"]), "denominator": list(raw["unit"]["denominator"])},
            "state": raw["state"], "value": raw["value"],
            "source_refs": [{"occurrence_sha256": value} for value in raw["source_occurrence_fingerprints"]],
            "mapping": {"revision_id": raw["mapping_revision_id"],
                "evidence_sha256": raw["mapping_evidence_fingerprint"],
                "source_qname": raw["source_concept"]["qname"],
                "dts_manifest_sha256": raw["source_concept"]["dts_manifest_sha256"]},
            "equivalence": [],
            "resolution": {"revision_id": raw["resolution_revision_id"],
                "evidence_sha256": raw["resolution_evidence_fingerprint"],
                "slot_sha256": raw["slot"]["sha256"], "conflict_state": raw["conflict"]["state"]},
            "parser_selection_revision_id": raw["parser_selection_revision_id"],
        })
    rights = resolved["rights"]
    quality = resolved["quality"]
    body = {
        "schema": "macroforge-corporate-private-analysis-release-v3",
        "output_family": "private_analysis",
        "authority_root_id": str(authority.root_id),
        "subscription_id": resolved["subscription_id"],
        "sec_cutoff": resolved["sec_cutoff"],
        "knowledge_cutoff": resolved["knowledge_cutoff"],
        "knowledge_snapshot_id": resolved["knowledge_snapshot_id"],
        "closure_sha256": resolved["closure_sha256"],
        "filing": {
            "accession": filing["accession"], "report_period": filing["report_period"],
            "source_manifest_sha256": filing["source_manifest_sha256"],
        },
        "policy": {"id": policy["id"], "version": policy["version"], "sha256": policy["sha256"]},
        "expected_selection": {
            "revision_id": expected["revision_id"], "selection_sha256": expected["selection_sha256"],
            "canonical_concept": expected["canonical_concept"], "scope": expected["scope"],
        },
        "eligibility": {
            "revision_id": eligibility["revision_id"],
            "source_manifest_sha256": eligibility["source_manifest_sha256"],
            "quality_decision_sha256": eligibility["quality_decision_sha256"],
        },
        "rights": {"revision_id": rights["revision_id"], "private_analysis": True,
                   "redistribution": rights["redistribution_status"], "remote_delivery": False},
        "quality": {"revision_id": quality["revision_id"],
                    "check_set_sha256": quality["check_set_sha256"]},
        "authority": {"snapshot_manifest_sha256": resolved["snapshot_manifest_sha256"],
                      "relationship_revision_ids": [row["revision_id"] for row in resolved["relationships"]],
                      "equivalence_revision_ids": [row["revision_id"] for row in resolved["equivalences"]]},
        "items": public_items,
    }
    canonical = json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    release_id = sha256(canonical).hexdigest()
    payload = json.dumps({**body, "release_id": release_id}, sort_keys=True,
                         separators=(",", ":"), ensure_ascii=False).encode() + b"\n"
    return CorporateRelease(release_id, payload, "private_analysis")


@dataclass(frozen=True)
class PublicationAct:
    publication_act_id: str
    authority_root_id: str
    release_sha256: str
    target: str
    target_sha256: str
    status: str
    recorded_at: str


def publish_database_anchored(*, authority: Any, store: Any,
                              target: str | Path) -> PublicationAct:
    """Resolve PostgreSQL authority, reserve, install derived bytes, then complete."""
    from macroforge.corporate_reporting_queries import (
        AmbiguousSelection, CorporateAuthorityRef, PostgresCorporateAuthorityStore,
    )
    if type(authority) is not CorporateAuthorityRef or type(store) is not PostgresCorporateAuthorityStore:
        raise TypeError("database authority reference and concrete PostgreSQL store are required")

    # Caller bytes never enter this interface.  The complete persisted closure is
    # independently resolved and projected into canonical bytes inside the governed act.
    release = build_private_release(authority=authority, store=store)
    release_id = _verify_release(release)
    target_path = Path(target).resolve()
    # Existing-path conflicts are a side-effect-free preflight.  A reservation is
    # authority for bytes that may be installed, never a record of a known rejection.
    if target_path.exists() and target_path.read_bytes() != release.payload:
        raise ImmutableReleaseConflict(f"target {target_path} already contains different bytes")
    digest = sha256(release.payload).hexdigest()
    # Lifecycle SQL is deliberately confined to this complete operation.  The concrete
    # store exposes resolution only; no caller can reserve or complete independently.
    root = str(authority.root_id)
    quoted_target = str(target_path).replace("'", "''")
    reservation_sql = f"""
BEGIN;
SELECT pg_advisory_xact_lock(hashtextextended('{root}',0));
INSERT INTO corporate_reporting.corporate_publication_reservation(root_id,release_sha256,target,target_sha256)
VALUES('{root}'::uuid,'{release_id}','{quoted_target}','{digest}')
ON CONFLICT(root_id) DO NOTHING;
SELECT jsonb_build_object('publication_act_id',publication_act_id::text,'authority_root_id',root_id::text,
 'release_sha256',release_sha256,'target',target,'target_sha256',target_sha256,'status',status,
 'recorded_at',recorded_at)::text FROM corporate_reporting.corporate_publication_authority
WHERE root_id='{root}'::uuid;
COMMIT;
"""
    reservation = subprocess.run(
        ["psql", "-X", "-v", "ON_ERROR_STOP=1", "-At", "-d", store.database_url],
        input=reservation_sql, text=True, capture_output=True,
    )
    if reservation.returncode:
        raise AmbiguousSelection(
            f"publication reservation failed: {reservation.stderr.strip()}"
        )
    reservation_lines = [
        line for line in reservation.stdout.splitlines() if line.startswith("{")
    ]
    if not reservation_lines:
        raise AmbiguousSelection("publication reservation was not persisted")
    reserved_act = json.loads(reservation_lines[-1])
    if (reserved_act["release_sha256"], reserved_act["target"],
            reserved_act["target_sha256"]) != (release_id, str(target_path), digest):
        raise AmbiguousSelection("authority already has a distinct publication act")

    # Keep both durable-writing primitives lexically confined to this governed path.
    # Neither is a module-level callable that caller-authored bytes can invoke.
    def append_status(status: str) -> None:
        log = target_path.parent / ".corporate-publication-status.jsonl"
        previous = sha256(log.read_bytes()).hexdigest() if log.exists() else "0" * 64
        record = {
            "release_id": release_id, "status": status, "target": target_path.name,
            "target_sha256": digest, "previous_log_sha256": previous,
        }
        line = json.dumps(record, sort_keys=True, separators=(",", ":")).encode() + b"\n"
        fd = os.open(log, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
        try:
            os.write(fd, line)
            os.fsync(fd)
        finally:
            os.close(fd)

    def install() -> str:
        target_path.parent.mkdir(parents=True, exist_ok=True)
        if target_path.exists():
            if target_path.read_bytes() != release.payload:
                raise ImmutableReleaseConflict(
                    f"target {target_path} already contains different bytes"
                )
            append_status("identical")
            directory_fd = os.open(target_path.parent, os.O_RDONLY)
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
            return "identical"
        fd, temporary = tempfile.mkstemp(prefix=f".{target_path.name}.", dir=target_path.parent)
        try:
            with os.fdopen(fd, "wb") as handle:
                handle.write(release.payload)
                handle.flush()
                os.fsync(handle.fileno())
            try:
                os.link(temporary, target_path)
            except FileExistsError:
                if target_path.read_bytes() != release.payload:
                    raise ImmutableReleaseConflict(
                        f"target {target_path} concurrently received different bytes"
                    )
                status = "identical"
            else:
                status = "published"
            if target_path.read_bytes() != release.payload:
                raise ImmutableReleaseConflict("published target bytes do not match release")
            append_status(status)
            directory_fd = os.open(target_path.parent, os.O_RDONLY)
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
            return status
        finally:
            try:
                os.unlink(temporary)
            except FileNotFoundError:
                pass

    install()
    completion_sql = f"""
BEGIN;
SELECT pg_advisory_xact_lock(hashtextextended('{root}',0));
INSERT INTO corporate_reporting.corporate_publication_completion(publication_reservation_id)
SELECT publication_reservation_id FROM corporate_reporting.corporate_publication_reservation
WHERE root_id='{root}'::uuid
ON CONFLICT(publication_reservation_id) DO NOTHING;
SELECT jsonb_build_object('publication_act_id',publication_act_id::text,'authority_root_id',root_id::text,
 'release_sha256',release_sha256,'target',target,'target_sha256',target_sha256,'status',status,
 'recorded_at',recorded_at)::text FROM corporate_reporting.corporate_publication_authority
WHERE root_id='{root}'::uuid;
COMMIT;
"""
    completion = subprocess.run(
        ["psql", "-X", "-v", "ON_ERROR_STOP=1", "-At", "-d", store.database_url],
        input=completion_sql, text=True, capture_output=True,
    )
    if completion.returncode:
        raise AmbiguousSelection(
            f"publication completion failed: {completion.stderr.strip()}"
        )
    completion_lines = [
        line for line in completion.stdout.splitlines() if line.startswith("{")
    ]
    if not completion_lines:
        raise AmbiguousSelection("publication completion was not persisted")
    act = json.loads(completion_lines[-1])
    if act["status"] != "completed":
        raise AmbiguousSelection("publication completion is not durable")
    return PublicationAct(**act)


def _verify_release(release: CorporateRelease) -> str:
    if release.output_family != "private_analysis":
        raise EligibilityError("public output cannot be published")
    try:
        envelope = json.loads(release.payload)
        claimed = envelope.pop("release_id")
    except (json.JSONDecodeError, KeyError, TypeError) as error:
        raise ImmutableReleaseConflict("malformed release payload") from error
    canonical = json.dumps(envelope, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
    actual = sha256(canonical).hexdigest()
    if claimed != actual or release.release_id != actual:
        raise ImmutableReleaseConflict("forged release identity")
    canonical_payload = json.dumps({**envelope, "release_id": actual}, sort_keys=True,
                                   separators=(",", ":"), ensure_ascii=False).encode() + b"\n"
    if canonical_payload != release.payload:
        raise ImmutableReleaseConflict("release payload is not exact canonical bytes")
    return actual


def publish_local_immutable(target: str | Path, release: CorporateRelease) -> str:
    """Fail-closed compatibility sentinel for the removed authority-free publisher."""
    del target, release
    raise TypeError(
        "authority-free publication is disabled; use the governed database publisher"
    )
