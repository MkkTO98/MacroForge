"""TASK-223 source-specific SEC Corporate Portfolio proof-tranche ingestion.

The module authenticates the published TASK-222 manifest and frozen TASK-223
selection ledger, reacquires only frozen SEC-filing documents, preserves exact
source occurrence evidence, and constructs Migration-005 load objects. Provider
bodies remain in caller-selected temporary storage and never enter reports.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import mimetypes
import os
from pathlib import Path
import subprocess
import time
from typing import Any, Callable, Mapping
from urllib.parse import unquote, urlparse

from macroforge.sec_corporate_portfolio import acquisition_url_allowed, canonical_manifest_identity
from macroforge.sec_corporate_reporting import (
    ParserInvariantError,
    parse_extension_schema,
    parse_inline_instance,
    parse_instance,
)
from macroforge.sec_corporate_reporting_loader import (
    CorporateFilingLoad,
    FilingDocumentLoad,
    PostgreSQLLoadTimeout,
    load_corporate_filings_to_postgres,
)

TASK222_SERIALIZED_SHA256 = "9cde110033fd3e8f22bedf768f01e7f90dd2c72784ad4f43172e5220ad9edf9f"
TASK222_SEMANTIC_IDENTITY = "937056b9e903daa5e3550ed18cb1dff6d34bb1fbc49e3bb8e1f51a8d4420516a"


class TrancheAuthenticationError(ValueError):
    pass


class AcquisitionIdentityError(ValueError):
    pass


@dataclass(frozen=True)
class AcquiredDocument:
    accession: str
    url: str
    local_path: Path
    byte_length: int
    sha256: str
    requested_url: str
    final_url: str
    http_status: int


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def _without_identity(value: Mapping[str, Any], key: str) -> dict[str, Any]:
    return {name: item for name, item in value.items() if name != key}


def _ledger_source_identity(ledger: Mapping[str, Any]) -> tuple[str | None, str | None, int | None]:
    source = ledger.get("source_manifest")
    if isinstance(source, Mapping):
        return (
            str(source.get("semantic_identity") or "") or None,
            str(source.get("serialized_sha256") or "") or None,
            int(source["byte_length"]) if "byte_length" in source else None,
        )
    semantic = str(ledger.get("source_manifest_sha256") or "") or None
    return semantic, None, None


def authenticate_tranche(
    manifest_path: str | Path, ledger_path: str | Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Authenticate both artifacts and every selected package/absence identity."""
    manifest_bytes = Path(manifest_path).read_bytes()
    ledger_bytes = Path(ledger_path).read_bytes()
    try:
        manifest = json.loads(manifest_bytes)
        ledger = json.loads(ledger_bytes)
    except json.JSONDecodeError as error:
        raise TrancheAuthenticationError("manifest or ledger is not JSON") from error
    if not isinstance(manifest, dict) or not isinstance(ledger, dict):
        raise TrancheAuthenticationError("manifest and ledger must be JSON objects")
    semantic = canonical_manifest_identity(manifest)
    if manifest.get("manifest_sha256") != semantic:
        raise TrancheAuthenticationError("TASK-222 manifest semantic identity mismatch")
    source_semantic, source_serialized, source_length = _ledger_source_identity(ledger)
    if source_semantic != semantic:
        raise TrancheAuthenticationError("ledger does not bind the TASK-222 semantic identity")
    if source_serialized is not None and source_serialized != sha256(manifest_bytes).hexdigest():
        raise TrancheAuthenticationError("ledger does not bind the serialized TASK-222 bytes")
    if source_length is not None and source_length != len(manifest_bytes):
        raise TrancheAuthenticationError("ledger does not bind the TASK-222 byte length")
    ledger_identity = sha256(_canonical(_without_identity(ledger, "ledger_sha256"))).hexdigest()
    if ledger.get("ledger_sha256") != ledger_identity:
        raise TrancheAuthenticationError("TASK-223 ledger identity mismatch")

    packages = {str(item.get("accession")): item for item in manifest.get("package_results", [])}
    acts = list(ledger.get("filing_acts", []))
    accessions = [str(item.get("accession")) for item in acts]
    if accessions != list(ledger.get("frozen_accessions", [])) or len(set(accessions)) != len(accessions):
        raise TrancheAuthenticationError("frozen accession ordering or uniqueness mismatch")
    for act in acts:
        accession = str(act.get("accession"))
        package = packages.get(accession)
        if package is None or package.get("outcome") != "compatible":
            raise TrancheAuthenticationError(f"selected package is absent or incompatible: {accession}")
        package_identity = str(package.get("manifest_sha256") or "")
        if package_identity != canonical_manifest_identity(package):
            raise TrancheAuthenticationError(f"selected package identity mismatch: {accession}")
        expected = str(
            act.get("manifest_package_identity")
            or act.get("package_manifest_sha256")
            or ""
        )
        if expected != package_identity:
            raise TrancheAuthenticationError(f"ledger/package binding mismatch: {accession}")
        for field in ("cik", "form", "xbrl_format"):
            if field in act and str(act[field]) != str(package.get(field)):
                raise TrancheAuthenticationError(f"ledger/package {field} mismatch: {accession}")
    absences = list(ledger.get("explicit_absences", []))
    absence_identities = [
        str(item.get("expected_explicit_absence_identity") or item.get("absence_identity") or "")
        for item in absences
    ]
    if sorted(absence_identities) != sorted(ledger.get("frozen_absence_identities", [])):
        raise TrancheAuthenticationError("frozen explicit-absence identities mismatch")
    if any(item.get("disposition") != "acquisition_cessation_absence" for item in absences):
        raise TrancheAuthenticationError("unsupported explicit-absence disposition")
    return manifest, ledger


def _safe_name(url: str) -> str:
    name = Path(unquote(urlparse(url).path)).name
    if not name or name in {".", ".."} or "/" in name or "\\" in name:
        raise AcquisitionIdentityError("unsafe SEC filing document name")
    return name


def acquire_frozen_documents(
    manifest: Mapping[str, Any],
    ledger: Mapping[str, Any],
    destination: str | Path,
    fetch: Callable[[str], bytes],
) -> dict[str, AcquiredDocument]:
    """Reacquire exactly the selected SEC-owned filing documents and verify identity."""
    destination = Path(destination)
    packages = {str(item["accession"]): item for item in manifest["package_results"]}
    acquired: dict[str, AcquiredDocument] = {}
    for act in ledger["filing_acts"]:
        accession = str(act["accession"])
        package = packages[accession]
        filing_documents = [item for item in package["documents"] if item.get("owner") == "sec_filing"]
        if not filing_documents:
            raise AcquisitionIdentityError(f"package has no SEC-filing documents: {accession}")
        seen_names: set[str] = set()
        for record in sorted(filing_documents, key=lambda item: item["url"]):
            url = str(record["url"])
            if url in acquired or not acquisition_url_allowed(url):
                raise AcquisitionIdentityError(f"duplicate or disallowed frozen URL: {url}")
            name = _safe_name(url)
            if name in seen_names:
                raise AcquisitionIdentityError(f"duplicate filing document name: {accession}/{name}")
            seen_names.add(name)
            body = fetch(url)
            if not isinstance(body, bytes):
                raise AcquisitionIdentityError("fetch did not return bytes")
            digest = sha256(body).hexdigest()
            if len(body) != int(record["byte_length"]) or digest != record["sha256"]:
                raise AcquisitionIdentityError(f"frozen document identity mismatch: {url}")
            evidence_getter = getattr(fetch, "retrieval_evidence", None)
            if not callable(evidence_getter):
                raise AcquisitionIdentityError("bounded retrieval evidence is required")
            evidence = evidence_getter(url)
            frozen_evidence = record.get("retrieval_evidence") or {}
            expected_final = frozen_evidence.get("final_url", url)
            valid = (
                isinstance(evidence, Mapping)
                and evidence.get("requested_url") == url
                and evidence.get("final_url") == expected_final
                and acquisition_url_allowed(str(evidence.get("final_url") or ""))
                and evidence.get("http_status") == 200
                and evidence.get("byte_length") == len(body)
                and evidence.get("sha256") == digest
                and evidence.get("method") == "bounded_exact_url_get"
            )
            if not valid:
                raise AcquisitionIdentityError(f"retrieval evidence mismatch: {url}")
            local_path = destination / accession / name
            local_path.parent.mkdir(parents=True, exist_ok=True)
            local_path.write_bytes(body)
            acquired[url] = AcquiredDocument(
                accession, url, local_path, len(body), digest, url,
                str(evidence["final_url"]), 200,
            )
    return acquired


def authenticate_frozen_documents(
    manifest: Mapping[str, Any], ledger: Mapping[str, Any], root: str | Path,
) -> dict[str, AcquiredDocument]:
    """Reauthenticate an existing frozen provider tree without network access."""
    root = Path(root)
    packages = {str(item["accession"]): item for item in manifest["package_results"]}
    acquired: dict[str, AcquiredDocument] = {}
    for act in ledger["filing_acts"]:
        accession = str(act["accession"])
        records = [item for item in packages[accession]["documents"] if item.get("owner") == "sec_filing"]
        for record in sorted(records, key=lambda item: item["url"]):
            url = str(record["url"])
            if url in acquired or not acquisition_url_allowed(url):
                raise AcquisitionIdentityError(f"duplicate or disallowed frozen URL: {url}")
            path = root / accession / _safe_name(url)
            length, digest = _path_identity(path)
            if length != int(record["byte_length"]) or digest != record["sha256"]:
                raise AcquisitionIdentityError(f"preserved document identity mismatch: {url}")
            evidence = record.get("retrieval_evidence") or {}
            final_url = str(evidence.get("final_url", url))
            if not acquisition_url_allowed(final_url):
                raise AcquisitionIdentityError(f"preserved final URL is disallowed: {url}")
            acquired[url] = AcquiredDocument(
                accession, url, path, length, digest, url, final_url,
                int(evidence.get("http_status", 200)),
            )
    return acquired


def _document_role(record: Mapping[str, Any], *, parser_source: bool, inline: bool) -> str:
    roles = set(record.get("roles", []))
    if parser_source:
        return "inline_xbrl_instance" if inline else "sec_rendered_xbrl_instance"
    preferences = (
        "primary_document", "extension_schema", "calculation_linkbase",
        "definition_linkbase", "label_linkbase", "presentation_linkbase",
        "instance_document",
    )
    return next((role for role in preferences if role in roles), sorted(roles)[0] if roles else "package_document")


def _media_type(name: str) -> str:
    return mimetypes.guess_type(name)[0] or "application/octet-stream"


def _path_identity(path: Path) -> tuple[int, str]:
    digest = sha256()
    length = 0
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            length += len(chunk)
            digest.update(chunk)
    return length, digest.hexdigest()


def _dei_values(report: Any, local_name: str) -> set[str]:
    return {
        item.lexical_value.strip()
        for item in report.occurrences
        if item.concept.rsplit("}", 1)[-1] == local_name
    }


def _validate_dei_identity(report: Any, *, accession: str, cik: str, form_type: str) -> None:
    if _dei_values(report, "EntityCentralIndexKey") != {cik}:
        raise AcquisitionIdentityError(f"DEI CIK does not bind parser source to filing: {accession}")
    if _dei_values(report, "DocumentType") != {form_type}:
        raise AcquisitionIdentityError(f"DEI document type does not bind parser source to filing: {accession}")


def build_filing_load(
    act: Mapping[str, Any],
    package: Mapping[str, Any],
    acquired: Mapping[str, AcquiredDocument],
) -> CorporateFilingLoad:
    """Construct one immutable source-specific load from authenticated acquired bytes."""
    accession = str(act["accession"])
    if (
        package.get("accession") != accession
        or str(package.get("cik")).zfill(10) != str(act.get("cik")).zfill(10)
        or package.get("form") != act.get("form")
        or package.get("outcome") != "compatible"
    ):
        raise TrancheAuthenticationError("filing act and compatible package identity do not match")
    inline = str(package["xbrl_format"]) == "inline"
    filing_records = [item for item in package["documents"] if item.get("owner") == "sec_filing"]
    if inline:
        primary_name = str(act["primary_document"])
        candidates = [item for item in filing_records if _safe_name(str(item["url"])) == primary_name]
    else:
        candidates = [item for item in filing_records if "instance_document" in item.get("roles", [])]
    if len(candidates) != 1:
        raise ParserInvariantError(f"exactly one parser source is required: {accession}")
    source_record = candidates[0]
    source = acquired.get(str(source_record["url"]))
    if source is None:
        raise AcquisitionIdentityError(f"parser source was not acquired: {accession}")
    dts_records = [
        item for item in filing_records
        if set(item.get("roles", [])) & {
            "extension_schema", "calculation_linkbase", "definition_linkbase",
            "label_linkbase", "presentation_linkbase",
        }
    ]
    dts_identity = sha256(_canonical([
        {"url": item["url"], "sha256": item["sha256"], "roles": sorted(item.get("roles", []))}
        for item in sorted(dts_records, key=lambda row: row["url"])
    ])).hexdigest()
    parser = parse_inline_instance if inline else parse_instance
    local_length, local_sha256 = _path_identity(source.local_path)
    if (
        source.sha256 != source_record["sha256"]
        or source.byte_length != int(source_record["byte_length"])
        or local_length != source.byte_length
        or local_sha256 != source.sha256
    ):
        raise AcquisitionIdentityError(f"parser source identity drifted after acquisition: {accession}")
    report = parser(source.local_path, accession=accession, dts_manifest_sha256=dts_identity)
    if report.source_sha256 != local_sha256:
        raise AcquisitionIdentityError(f"parser source identity drifted during parsing: {accession}")
    _validate_dei_identity(
        report, accession=accession, cik=str(act["cik"]).zfill(10), form_type=str(act["form"]),
    )
    documents: list[FilingDocumentLoad] = []
    declarations: list[dict[str, Any]] = []
    for record in sorted(filing_records, key=lambda item: item["url"]):
        item = acquired.get(str(record["url"]))
        if item is None:
            raise AcquisitionIdentityError(f"frozen filing document was not acquired: {record['url']}")
        name = _safe_name(item.url)
        parser_source = item.url == source.url
        documents.append(FilingDocumentLoad(
            name, _document_role(record, parser_source=parser_source, inline=inline),
            item.url, _media_type(name), item.byte_length, item.sha256, str(item.local_path),
        ))
        if "extension_schema" in record.get("roles", []):
            declarations.extend(parse_extension_schema(item.local_path))
    relation = act.get("amendment_relationship") or act.get("relationship_proposal")
    original = str(relation.get("original_accession")) if isinstance(relation, Mapping) else None
    issuer = str(act.get("company") or act.get("issuer") or "")
    package_identity = str(package["manifest_sha256"])
    return CorporateFilingLoad(
        accession=accession,
        form_type=str(act["form"]),
        filed_date=str(act["filing_date"]),
        accepted_at=str(act["accepted_at"]),
        report_period_end=str(act["report_date"]),
        primary_document_name=str(act["primary_document"]),
        amendment_flag=str(act["form"]).endswith("/A"),
        amendment_description=None,
        source_manifest_sha256=package_identity,
        dts_manifest_sha256=dts_identity,
        report=report,
        documents=tuple(documents),
        extension_declarations=tuple(declarations),
        parser_attempt_key="task223-source-specific-v1",
        parser_contract="sec-inline-xbrl-source-v1" if inline else "sec-traditional-xbrl-instance-v1",
        parser_version="1",
        parser_selection_status="accepted",
        cik=str(act["cik"]).zfill(10),
        issuer_name=issuer,
        relationship_original_accession=original,
        relationship_status="proposed" if original else None,
    )


def acquisition_report(
    manifest: Mapping[str, Any],
    ledger: Mapping[str, Any],
    acquired: Mapping[str, AcquiredDocument],
) -> dict[str, Any]:
    """Return deterministic metadata-only acquisition accounting."""
    acts = list(ledger["filing_acts"])
    absences = list(ledger["explicit_absences"])
    expected_urls = {
        str(document["url"])
        for package in manifest["package_results"]
        if package.get("accession") in set(ledger["frozen_accessions"])
        for document in package["documents"] if document.get("owner") == "sec_filing"
    }
    if set(acquired) != expected_urls:
        raise AcquisitionIdentityError("acquisition set differs from frozen SEC-filing document set")
    payload: dict[str, Any] = {
        "schema": "macroforge.task223.corporate-proof-acquisition-report.v1",
        "source_manifest_sha256": str(manifest["manifest_sha256"]),
        "ledger_sha256": str(ledger["ledger_sha256"]),
        "filing_dispositions": {"loaded": len(acts), "explicit_absence": len(absences)},
        "filing_act_count": len(acts),
        "explicit_absence_count": len(absences),
        "document_count": len(acquired),
        "documents": [
            {"accession": item.accession, "url": item.url, "requested_url": item.requested_url,
             "final_url": item.final_url, "http_status": item.http_status,
             "byte_length": item.byte_length, "sha256": item.sha256}
            for item in sorted(acquired.values(), key=lambda value: value.url)
        ],
        "provider_bodies_persisted_in_report": False,
        "semantic_equivalence_claimed": False,
        "rights_or_release_authority": False,
    }
    payload["report_sha256"] = sha256(_canonical(payload)).hexdigest()
    return payload


def build_proof_campaign(
    manifest: Mapping[str, Any], ledger: Mapping[str, Any],
    acquired: Mapping[str, AcquiredDocument],
) -> tuple[CorporateFilingLoad, ...]:
    """Build the frozen campaign in predecessor-before-amendment order."""
    packages = {str(item["accession"]): item for item in manifest["package_results"]}
    acts = {str(item["accession"]): item for item in ledger["filing_acts"]}
    pending = set(acts)
    ordered: list[str] = []
    while pending:
        ready = []
        for accession in pending:
            relation = acts[accession].get("amendment_relationship") or acts[accession].get("relationship_proposal")
            predecessor = str(relation.get("original_accession")) if isinstance(relation, Mapping) else None
            if predecessor is None or predecessor in ordered:
                ready.append(accession)
        if not ready:
            raise TrancheAuthenticationError("amendment predecessor is absent or cyclic")
        for accession in sorted(ready, key=lambda item: (str(acts[item]["accepted_at"]), item)):
            ordered.append(accession)
            pending.remove(accession)
    return tuple(build_filing_load(acts[item], packages[item], acquired) for item in ordered)


def load_proof_campaign(
    loads: tuple[CorporateFilingLoad, ...], *, database_url: str,
    knowledge_cutoff: str, psql_path: str = "psql",
    deadline: float | None = None, work_deadline: float | None = None,
    reconciliation_deadline: float | None = None, hard_deadline: float | None = None,
    campaign_id: str = "task223",
    phase: str = "load", progress: Callable[[dict[str, Any]], None] | None = None,
) -> list[dict[str, Any]]:
    """Commit each filing independently so exact restart replays completed acts."""
    if deadline is not None and work_deadline is not None:
        raise ValueError("deadline and work_deadline are mutually exclusive")
    effective_work_deadline = work_deadline if work_deadline is not None else deadline
    if reconciliation_deadline is not None:
        if effective_work_deadline is None or not effective_work_deadline < reconciliation_deadline:
            raise ValueError("require work deadline < reconciliation deadline")
    if hard_deadline is not None:
        if reconciliation_deadline is None or not reconciliation_deadline < hard_deadline:
            raise ValueError("require reconciliation deadline < hard deadline")
    dispositions: list[dict[str, Any]] = []
    for index, load in enumerate(loads, 1):
        now = time.monotonic()
        if deadline is not None and now >= deadline:
            raise TimeoutError("TASK-223 whole-campaign deadline expired")
        remaining_work = (
            float("inf") if effective_work_deadline is None
            else effective_work_deadline - now
        )
        if work_deadline is not None and remaining_work < 150.0:
            raise PostgreSQLLoadTimeout("TASK-223 work deadline leaves no complete filing window")
        app_hash = sha256(f"{campaign_id}|{phase}|{index}|{load.accession}".encode()).hexdigest()[:20]
        application_name = f"macroforge-task223-{phase}-{app_hash}"[:63]
        if progress:
            progress({"event": "filing_load_started", "phase": phase,
                      "accession": load.accession, "completed": index - 1,
                      "total": len(loads), "application_name": application_name})
        result = load_corporate_filings_to_postgres(
            (load,), database_url=database_url, knowledge_cutoff=knowledge_cutoff,
            psql_path=psql_path, deadline=effective_work_deadline,
            reconciliation_deadline=reconciliation_deadline,
            application_name=application_name,
            statement_timeout_seconds=120.0, lock_timeout_seconds=15.0,
            idle_transaction_timeout_seconds=60.0, client_timeout_seconds=150.0,
            governance_closure=False,
        )
        dispositions.append({
            "accession": load.accession, "status": "loaded",
            "filing_count": result.filing_count, "document_count": result.document_count,
            "occurrence_count": result.occurrence_count, "slot_count": result.slot_count,
            "relationship_count": result.relationship_count,
            "replay_fingerprint": result.replay_fingerprint,
        })
        if progress:
            progress({"event": "filing_load_committed", "phase": phase,
                      "accession": load.accession, "completed": index,
                      "total": len(loads), "application_name": application_name})
    return dispositions


def stable_postgres_state(
    database_url: str, *, psql_path: str = "psql", deadline: float | None = None,
    application_name: str = "macroforge-task223-state",
) -> dict[str, Any]:
    """Hash all Corporate Reporting and owned meta rows, excluding surrogate UUIDs/runtime clocks."""
    table_query = """
      SELECT table_schema||'.'||table_name
      FROM information_schema.tables
      WHERE table_type='BASE TABLE'
        AND (table_schema='corporate_reporting' OR
             (table_schema='meta' AND table_name IN
              ('source','dataset_release','pipeline_run','quality_check','lineage_event')))
      ORDER BY 1;
    """

    def psql(statement: str) -> str:
        remaining = float("inf") if deadline is None else deadline - time.monotonic()
        timeout = min(30.0, remaining)
        if timeout <= 20.0:
            raise TimeoutError("TASK-223 deadline leaves no bounded state-query window")
        app_literal = "'" + application_name.replace("'", "''") + "'"
        bounded = (
            f"SET application_name={app_literal};\n"
            "SET statement_timeout='20s';\nSET lock_timeout='5s';\n"
            "SET idle_in_transaction_session_timeout='10s';\n" + statement
        )
        completed = subprocess.run(
            [psql_path, "-X", "-v", "ON_ERROR_STOP=1", "-q", "-A", "-t", "-d", database_url],
            input=bounded, text=True, capture_output=True, timeout=timeout,
            env={**os.environ, "PGAPPNAME": application_name},
        )
        if completed.returncode:
            raise RuntimeError(completed.stderr.strip() or completed.stdout.strip())
        return completed.stdout.strip()

    tables = [line for line in psql(table_query).splitlines() if line]
    state: dict[str, Any] = {}
    volatile = {"recorded_at", "finished_at", "started_at", "created_at", "updated_at", "loaded_at", "ingested_at"}
    for qualified in tables:
        schema, table = qualified.split(".", 1)
        column_rows = psql(
            "SELECT column_name||'|'||data_type FROM information_schema.columns "
            f"WHERE table_schema='{schema}' AND table_name='{table}' ORDER BY ordinal_position;"
        ).splitlines()
        excluded = [
            row.split("|", 1)[0] for row in column_rows
            if row.endswith("|uuid") or row.split("|", 1)[0] in volatile
        ]
        remove = "ARRAY[" + ",".join("'" + name.replace("'", "''") + "'" for name in excluded) + "]::text[]"
        query = (
            "WITH rows AS (SELECT to_jsonb(t)-" + remove + " AS payload FROM "
            + qualified + " t) SELECT json_build_object('count',count(*),'sha256',"
            "encode(digest(COALESCE(string_agg(payload::text,E'\\n' ORDER BY payload::text),''),'sha256'),'hex')) FROM rows;"
        )
        state[qualified] = json.loads(psql(query))
    payload: dict[str, Any] = {"tables": state}
    payload["state_sha256"] = sha256(_canonical(payload)).hexdigest()
    return payload
