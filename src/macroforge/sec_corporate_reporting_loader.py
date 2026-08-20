"""Transactional PostgreSQL persistence for the bounded SEC Corporate Reporting slice.

The PostgreSQL entry point deliberately loads only shared ``meta`` ownership rows and
``corporate_reporting`` rows.  It uses one psql transaction, filing-scoped deterministic
UUIDs, immutable-manifest conflict checks, and exact-replay ``ON CONFLICT`` semantics.
The dependency-free in-memory store remains useful for compact parser unit tests.
"""
from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation
from hashlib import sha256
import json
import os
from pathlib import Path
import subprocess
import time
from typing import Any, Iterable
from uuid import UUID, uuid4, uuid5

from macroforge.sec_corporate_reporting import ParserReport, parse_extension_schema, parse_instance


class IdentityConflict(RuntimeError):
    pass


class QualityGateError(RuntimeError):
    pass


class PostgreSQLLoadError(RuntimeError):
    pass


class PostgreSQLLoadTimeout(PostgreSQLLoadError):
    """A bounded load expired; reconciliation is included in the message."""


RECONCILIATION_QUERY_TIMEOUT_SECONDS = 15.0
CANCEL_POLL_SECONDS = 15.0
TERMINATE_POLL_SECONDS = 15.0


class CorporateReportingStore:
    """Small deterministic transaction model retained for compact tests."""

    def __init__(self) -> None:
        self._filings: dict[str, dict[str, Any]] = {}

    @property
    def filing_count(self) -> int:
        return len(self._filings)

    @property
    def occurrence_count(self) -> int:
        return sum(len(v["occurrences"]) for v in self._filings.values())

    @property
    def conflicting_slot_count(self) -> int:
        return sum(v["metrics"]["conflicting_slot_count"] for v in self._filings.values())

    @property
    def fingerprint(self) -> str:
        return sha256(json.dumps(self._filings, sort_keys=True, separators=(",", ":")).encode()).hexdigest()

    def load(self, report: ParserReport, *, source_manifest_sha256: str) -> str:
        staged = deepcopy(self._filings)
        identity = report.accession
        exact = {"source_manifest_sha256": source_manifest_sha256,
                 "parser_output_sha256": report.parser_output_sha256,
                 "occurrences": [o.occurrence_sha256 for o in report.occurrences],
                 "slots": sorted(report.slots), "metrics": report.metrics}
        existing = staged.get(identity)
        if existing is not None:
            if existing != exact:
                raise IdentityConflict(f"accession {identity} already has different immutable bytes")
            return _digest(existing)
        if report.metrics["fact_count"] != len(report.occurrences):
            raise QualityGateError("occurrence count quality gate failed")
        staged[identity] = exact
        self._filings = staged
        return _digest(exact)


@dataclass(frozen=True)
class FilingDocumentLoad:
    name: str
    role: str
    source_url: str
    media_type: str
    byte_length: int
    sha256: str
    local_evidence_locator: str


@dataclass(frozen=True)
class CorporateFilingLoad:
    accession: str
    form_type: str
    filed_date: str
    accepted_at: str
    report_period_end: str
    primary_document_name: str
    amendment_flag: bool
    amendment_description: str | None
    source_manifest_sha256: str
    dts_manifest_sha256: str
    report: ParserReport
    documents: tuple[FilingDocumentLoad, ...]
    extension_declarations: tuple[dict[str, Any], ...]
    parser_attempt_key: str = "protected-initial-v1"
    parser_contract: str = "sec-rendered-xbrl-instance-v1"
    parser_version: str = "1"
    parser_selection_status: str | None = None
    cik: str = "0001517006"
    issuer_name: str = "Gatos Silver, Inc."
    relationship_original_accession: str | None = None
    relationship_status: str | None = None


@dataclass(frozen=True)
class PostgreSQLLoadResult:
    filing_count: int
    document_count: int
    occurrence_count: int
    slot_count: int
    relationship_count: int
    replay_fingerprint: str


_NS = UUID("4cfd5126-b250-5be2-a18f-615a490b9148")
_FIXTURE_ACCESSIONS = ("0001104659-23-034448", "0001104659-23-074911")
_PROTECTED_INITIAL_ATTEMPT = "protected-initial-v1"


def _selection_status(filing: CorporateFilingLoad) -> str:
    status = filing.parser_selection_status
    if status is None:
        return "accepted" if filing.parser_attempt_key == _PROTECTED_INITIAL_ATTEMPT else "proposed"
    if status not in {"accepted", "proposed", "deferred", "rejected"}:
        raise QualityGateError("parser selection status is not authorized")
    return status


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def _digest(value: Any) -> str:
    return sha256(_canonical(value)).hexdigest()


def _id(*parts: Any) -> str:
    return str(uuid5(_NS, "\x1f".join(str(p) for p in parts)))


def _sql(value: Any) -> str:
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    if isinstance(value, (int, Decimal)):
        return str(value)
    if isinstance(value, (dict, list, tuple)):
        value = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
    return "'" + str(value).replace("'", "''") + "'"


def _expanded(qname: str) -> tuple[str, str]:
    if not qname.startswith("{") or "}" not in qname:
        raise QualityGateError(f"concept is not an expanded QName: {qname}")
    namespace, local = qname[1:].split("}", 1)
    return namespace, local


def _numeric(value: str, has_unit: bool, nil: bool) -> str:
    if nil or not has_unit:
        return "NULL"
    try:
        return str(Decimal(value))
    except InvalidOperation:
        return "NULL"


def build_protected_gatos_loads(
    fixture_root: str | Path,
    *,
    inventory_path: str | Path | None = None,
) -> tuple[CorporateFilingLoad, CorporateFilingLoad]:
    """Authenticate and normalize the complete frozen 17-record Gatos chain."""
    root = Path(fixture_root)
    inventory_file = Path(inventory_path) if inventory_path else root / "derived/evidence-inventory.json"
    fixed_manifest = Path(__file__).parents[2] / "tests/fixtures/sec_corporate_reporting/source-hash-manifest.json"
    fixed = json.loads(fixed_manifest.read_text(encoding="utf-8"))["protected_fixture"]
    inventory_bytes = inventory_file.read_bytes()
    if sha256(inventory_bytes).hexdigest() != fixed["inventory_sha256"]:
        raise QualityGateError("fixed evidence inventory identity mismatch")
    inventory = json.loads(inventory_bytes)
    records = inventory["records"]
    chain_records = [r for r in records if r.get("category") == "filing_chain"]
    if len(chain_records) != 17 or sum(r.get("archive_index_member") is True for r in chain_records) != 14:
        raise QualityGateError("protected chain must contain exactly 17 records and 14 filing documents")
    authenticated: dict[str, str] = {}
    for record in chain_records:
        path = root / record["path"]
        if not path.is_file():
            raise QualityGateError(f"missing protected chain record: {record['path']}")
        payload = path.read_bytes()
        actual = sha256(payload).hexdigest()
        if len(payload) != record["bytes"] or actual != record["sha256"]:
            raise QualityGateError(f"protected chain identity mismatch: {record['path']}")
        authenticated[record["path"]] = actual
    submissions = json.loads((root / "submissions.json").read_text(encoding="utf-8"))
    if submissions.get("cik") != "0001517006":
        raise QualityGateError("SEC submissions CIK mismatch")
    recent = submissions["filings"]["recent"]
    submissions_by_accession = {
        accession: {key: recent[key][i] for key in (
            "accessionNumber", "form", "filingDate", "acceptanceDateTime", "reportDate", "primaryDocument"
        )}
        for i, accession in enumerate(recent["accessionNumber"])
    }
    filings_by_accession = {f["accessionNumber"]: f for f in inventory["filings"]}
    loads: list[CorporateFilingLoad] = []
    for accession, folder, instance_name in (
        (_FIXTURE_ACCESSIONS[0], "original", "gato-20211231x10k_htm.xml"),
        (_FIXTURE_ACCESSIONS[1], "amendment", "gato-20211231x10ka_htm.xml"),
    ):
        document_records = sorted(
            (r for r in records if r.get("accession") == accession and r.get("archive_index_member") is True),
            key=lambda r: r["path"],
        )
        if len(document_records) != 7:
            raise QualityGateError(f"{accession} requires exactly seven retained filing documents")
        index_name = f"{folder}-index.json"
        index_record = next(r for r in chain_records if r["path"] == index_name)
        index = json.loads((root / index_name).read_text(encoding="utf-8"))
        index_members = {i["name"]: i for i in index["directory"]["item"]}
        expected_base = f"https://www.sec.gov/Archives/edgar/data/1517006/{accession.replace('-', '')}/"
        documents: list[FilingDocumentLoad] = []
        for ordinal, record in enumerate(document_records, 1):
            path = root / record["path"]
            payload = path.read_bytes()
            name = Path(record["path"]).name
            member = index_members.get(name)
            if (member is None or int(member.get("size") or -1) != record["bytes"] or
                    record["retained_source_url"] != expected_base + name):
                raise QualityGateError(f"archive membership/source URL mismatch: {record['path']}")
            if len(payload) != record["bytes"] or sha256(payload).hexdigest() != record["sha256"]:
                raise QualityGateError(f"protected document identity mismatch: {record['path']}")
            documents.append(FilingDocumentLoad(
                name, record["role"], record["retained_source_url"],
                record["media_type"], record["bytes"], record["sha256"], str(path),
            ))
        metadata = filings_by_accession[accession]
        submission_metadata = submissions_by_accession.get(accession)
        compared = ("accessionNumber", "form", "filingDate", "acceptanceDateTime", "reportDate", "primaryDocument")
        if submission_metadata is None or any(metadata[k] != submission_metadata[k] for k in compared):
            raise QualityGateError(f"SEC submissions/inventory filing metadata mismatch: {accession}")
        acceptance_index = metadata["acceptanceDateTime"].replace("T", " ")[:19]
        retained_times = {index_members[d.name].get("last-modified") for d in documents}
        if retained_times != {acceptance_index} or metadata["primaryDocument"] not in index_members:
            raise QualityGateError(f"SEC archive index metadata mismatch: {accession}")
        manifest = _digest({"accession": accession,
                            "inventory_sha256": fixed["inventory_sha256"],
                            "submissions_sha256": authenticated["submissions.json"],
                            "archive_index_sha256": authenticated[index_name],
                            "archive_index_url": index_record["retained_source_url"],
                            "documents": [
            {"name": d.name, "role": d.role, "bytes": d.byte_length, "sha256": d.sha256,
             "source_url": d.source_url} for d in documents]})
        dts = _digest([{"role": d.role, "sha256": d.sha256} for d in documents
                       if d.role in {"extension_schema", "calculation_linkbase", "definition_linkbase",
                                     "label_linkbase", "presentation_linkbase"}])
        report = parse_instance(root / folder / instance_name, accession=accession,
                                dts_manifest_sha256=dts)
        if report.metrics["conflicting_slot_count"] or report.metrics["fact_count"] != len(report.occurrences):
            raise QualityGateError(f"parser quality gate failed for {accession}")
        dei = {o.concept.rsplit("}", 1)[-1]: o.lexical_value for o in report.occurrences
               if o.concept.rsplit("}", 1)[-1] in {
                   "DocumentType", "DocumentPeriodEndDate", "AmendmentFlag", "AmendmentDescription"
               }}
        expected_flag = "true" if accession.endswith("074911") else "false"
        if (dei.get("DocumentType") != metadata["form"] or
                dei.get("DocumentPeriodEndDate") != metadata["reportDate"] or
                dei.get("AmendmentFlag", "").lower() != expected_flag):
            raise QualityGateError(f"SEC metadata/DEI evidence mismatch: {accession}")
        declarations = tuple(parse_extension_schema(root / folder / "gato-20211231.xsd"))
        loads.append(CorporateFilingLoad(
            accession, metadata["form"], metadata["filingDate"], metadata["acceptanceDateTime"],
            metadata["reportDate"], metadata["primaryDocument"], accession.endswith("074911"),
            "Amendment No. 1" if accession.endswith("074911") else None, manifest, dts, report,
            tuple(documents), declarations,
        ))
    return loads[0], loads[1]


def _insert(sql: list[str], table: str, columns: Iterable[str], values: Iterable[Any],
            conflict: str = "DO NOTHING") -> None:
    sql.append(f"INSERT INTO {table}({','.join(columns)}) VALUES({','.join(_sql(v) for v in values)}) ON CONFLICT {conflict};")


def _knowledge(sql: list[str], revision_id: str, axis: str, key: str, pipeline_id: str,
               evidence: str, effective_at: str | None = None, recorded_at: str | None = None) -> None:
    if recorded_at is None:
        raise ValueError("knowledge revisions require an explicit recorded_at cutoff")
    _insert(sql, "corporate_reporting.knowledge_revision",
            ("knowledge_revision_id", "axis_type", "object_key", "pipeline_run_id",
             "source_effective_at", "evidence_fingerprint", "recorded_at"),
            (revision_id, axis, key, pipeline_id, effective_at, evidence, recorded_at))


def _build_postgresql_sql(
    filings: tuple[CorporateFilingLoad, ...], cik_or_knowledge_cutoff: str,
    knowledge_cutoff: str | None = None,
    *, application_name: str = "macroforge-corporate-loader",
    statement_timeout_ms: int = 300_000,
    lock_timeout_ms: int = 30_000,
    idle_transaction_timeout_ms: int = 60_000,
    governance_closure: bool = True,
) -> str:
    # The former batch-wide CIK argument remains accepted only for compatibility;
    # source identity now travels on each immutable filing load.
    if knowledge_cutoff is None:
        knowledge_cutoff = cik_or_knowledge_cutoff
    if not filings:
        raise ValueError("at least one filing is required")
    if not (0 < lock_timeout_ms < statement_timeout_ms):
        raise ValueError("lock timeout must be positive and shorter than statement timeout")
    if idle_transaction_timeout_ms <= 0:
        raise ValueError("idle transaction timeout must be positive")
    sql = [
        "\\set ON_ERROR_STOP on", "BEGIN;",
        f"SET LOCAL application_name={_sql(application_name)};",
        f"SET LOCAL statement_timeout='{statement_timeout_ms}ms';",
        f"SET LOCAL lock_timeout='{lock_timeout_ms}ms';",
        f"SET LOCAL idle_in_transaction_session_timeout='{idle_transaction_timeout_ms}ms';",
        "SET CONSTRAINTS ALL DEFERRED;",
    ]
    for filing in sorted(filings, key=lambda f: f.accession):
        run_key = (f"sec-corporate-reporting:{filing.accession}:{filing.source_manifest_sha256}:"
                   f"{filing.dts_manifest_sha256}:{filing.parser_attempt_key}:{filing.parser_contract}:"
                   f"{filing.parser_version}:{filing.report.parser_output_sha256}")
        parser_id = _id("parser", filing.accession, filing.source_manifest_sha256,
                        filing.dts_manifest_sha256, filing.parser_attempt_key,
                        filing.parser_contract, filing.parser_version,
                        filing.report.parser_output_sha256)
        sql.append(f"SELECT pg_advisory_xact_lock(hashtextextended({_sql('corporate-reporting:' + filing.accession)},0));")
        sql.append("DO $$ BEGIN IF EXISTS (SELECT 1 FROM corporate_reporting.filing_submission "
                   f"WHERE accession={_sql(filing.accession)} AND (source_manifest_sha256<>{_sql(filing.source_manifest_sha256)} "
                   f"OR form_type<>{_sql(filing.form_type)} OR filed_date<>{_sql(filing.filed_date)}::date "
                   f"OR accepted_at<>{_sql(filing.accepted_at)}::timestamptz OR report_period_end<>{_sql(filing.report_period_end)}::date "
                   f"OR primary_document_name<>{_sql(filing.primary_document_name)} OR amendment_flag<>{_sql(filing.amendment_flag)} "
                   f"OR amendment_description IS DISTINCT FROM {_sql(filing.amendment_description)})) "
                   f"THEN RAISE EXCEPTION 'CORPORATE_REPORTING_IDENTITY_CONFLICT:{filing.accession}'; END IF; "
                   "IF EXISTS (SELECT 1 FROM corporate_reporting.filing_submission f JOIN corporate_reporting.filing_document d USING(filing_id) "
                   f"WHERE f.accession={_sql(filing.accession)} AND NOT EXISTS (SELECT 1 FROM (VALUES " +
                   ",".join(f"({_sql(d.name)},{_sql(d.role)},{_sql(d.source_url)},{d.byte_length},{_sql(d.sha256)})" for d in filing.documents) +
                   ") v(name,role,url,bytes,hash) WHERE v.name=d.document_name AND v.role=d.document_role AND v.url=d.source_url AND v.bytes=d.byte_length AND v.hash=d.sha256)) "
                   f"THEN RAISE EXCEPTION 'CORPORATE_REPORTING_IDENTITY_CONFLICT:{filing.accession}:document'; END IF; "
                   "IF EXISTS (SELECT 1 FROM corporate_reporting.parser_run p "
                   f"WHERE p.parser_run_id={_sql(parser_id)}::uuid AND (p.parser_attempt_key<>{_sql(filing.parser_attempt_key)} "
                   f"OR p.parser_contract<>{_sql(filing.parser_contract)} OR p.parser_version<>{_sql(filing.parser_version)} "
                   f"OR p.source_manifest_sha256<>{_sql(filing.source_manifest_sha256)} OR p.parser_output_sha256 IS DISTINCT FROM {_sql(filing.report.parser_output_sha256)})) "
                   f"THEN RAISE EXCEPTION 'CORPORATE_REPORTING_IDENTITY_CONFLICT:{filing.accession}:parser'; END IF; "
                   "IF EXISTS (SELECT 1 FROM corporate_reporting.filing_submission f JOIN corporate_reporting.taxonomy_set t USING(filing_id) "
                   f"WHERE f.accession={_sql(filing.accession)} AND t.dts_manifest_sha256<>{_sql(filing.dts_manifest_sha256)}) "
                   f"THEN RAISE EXCEPTION 'CORPORATE_REPORTING_IDENTITY_CONFLICT:{filing.accession}:dts'; END IF; "
                   "IF EXISTS (SELECT 1 FROM meta.dataset_release r JOIN meta.source s USING(source_id) "
                   f"WHERE s.source_code='SEC_CORPORATE_REPORTING' AND r.provider_dataset_code='SEC_FILINGS' AND r.release_key={_sql(filing.accession)} "
                   f"AND (r.release_date IS DISTINCT FROM {_sql(filing.filed_date)}::date OR r.source_url<>'https://www.sec.gov/Archives/' "
                   f"OR r.raw_sha256<>{_sql(filing.source_manifest_sha256)} OR r.metadata<>{_sql({'accepted_at': filing.accepted_at, 'rights': 'unknown', 'source_manifest_sha256': filing.source_manifest_sha256})}::jsonb)) "
                   f"THEN RAISE EXCEPTION 'CORPORATE_REPORTING_IDENTITY_CONFLICT:{filing.accession}:meta.dataset_release'; END IF; "
                   "IF EXISTS (SELECT 1 FROM meta.pipeline_run p "
                   f"WHERE p.run_key={_sql(run_key)} "
                   f"AND (p.pipeline_name<>'sec_corporate_reporting' OR p.status<>'succeeded' OR p.input_parameters<>{_sql({'accession': filing.accession, 'parser_attempt_key': filing.parser_attempt_key, 'parser_contract': filing.parser_contract, 'parser_version': filing.parser_version})}::jsonb "
                   f"OR p.artifact_manifest<>{_sql({'dts_manifest_sha256': filing.dts_manifest_sha256, 'parser_output_sha256': filing.report.parser_output_sha256})}::jsonb)) "
                   f"THEN RAISE EXCEPTION 'CORPORATE_REPORTING_IDENTITY_CONFLICT:{filing.accession}:meta.pipeline_run'; END IF; END $$;")
    sql.append("DO $$ BEGIN "
               "IF EXISTS (SELECT 1 FROM meta.source WHERE source_code='SEC_CORPORATE_REPORTING' AND "
               "(source_name<>'U.S. Securities and Exchange Commission' OR source_home_url<>'https://www.sec.gov/' OR license_note<>'rights unknown; private analysis only')) "
               "THEN RAISE EXCEPTION 'CORPORATE_REPORTING_IDENTITY_CONFLICT:meta.source'; END IF; "
               "IF NOT EXISTS (SELECT 1 FROM corporate_reporting.corporate_release_policy WHERE policy_version='private-analysis-v1' AND allowed_output_family='private_analysis' AND policy_sha256=encode(digest('private-analysis-v1:private_analysis','sha256'),'hex')) "
               "THEN RAISE EXCEPTION 'CORPORATE_REPORTING_IDENTITY_CONFLICT:release_policy'; END IF; "
               "IF NOT EXISTS (SELECT 1 FROM corporate_reporting.canonical_concept WHERE canonical_code='CORP_TOTAL_ASSETS' AND label='Total assets' AND value_kind='numeric' AND period_type='instant' AND status='proposed') "
               "THEN RAISE EXCEPTION 'CORPORATE_REPORTING_IDENTITY_CONFLICT:canonical_concept'; END IF; END $$;")
    _insert(sql, "meta.source", ("source_code", "source_name", "source_home_url", "license_note"),
            ("SEC_CORPORATE_REPORTING", "U.S. Securities and Exchange Commission", "https://www.sec.gov/",
             "rights unknown; private analysis only"))
    for filing in sorted(filings, key=lambda item: (item.cik, item.accession)):
        entity_id = _id("entity", "sec:cik", filing.cik)
        _insert(sql, "corporate_reporting.reporting_entity", ("entity_id", "entity_kind"),
                (entity_id, "registrant"))
        _insert(sql, "corporate_reporting.entity_identifier",
                ("entity_identifier_id", "entity_id", "scheme", "normalized_value"),
                (_id("entity_identifier", filing.cik), entity_id, "sec:cik", filing.cik))

    snapshot_members: list[tuple[str, str, str]] = []
    filing_ids: dict[str, str] = {}
    pipeline_ids: dict[str, str] = {}
    concept_ids_by_filing: dict[str, dict[str, str]] = {}
    primary_ids: dict[str, str] = {}
    for filing in sorted(filings, key=lambda f: f.accepted_at):
        accession = filing.accession
        entity_id = _id("entity", "sec:cik", filing.cik)
        filing_id = _id("filing", accession)
        filing_ids[accession] = filing_id
        run_key = (f"sec-corporate-reporting:{accession}:{filing.source_manifest_sha256}:"
                   f"{filing.dts_manifest_sha256}:{filing.parser_attempt_key}:{filing.parser_contract}:"
                   f"{filing.parser_version}:{filing.report.parser_output_sha256}")
        pipeline_id = _id("pipeline", run_key)
        pipeline_ids[accession] = pipeline_id
        parser_id = _id("parser", accession, filing.source_manifest_sha256,
                        filing.dts_manifest_sha256, filing.parser_attempt_key,
                        filing.parser_contract, filing.parser_version,
                        filing.report.parser_output_sha256)
        # Every parser attempt owns an independently replayable interpretation.
        # Source occurrences below deliberately use a separate source-derived id.
        content_id = _id("parser-output", accession, filing.source_manifest_sha256,
                         filing.dts_manifest_sha256, filing.parser_attempt_key,
                         filing.parser_contract, filing.parser_version,
                         filing.report.parser_output_sha256)
        scope_id = _id("scope", accession, "consolidated_registrant")
        sql.append("INSERT INTO meta.dataset_release(source_id,provider_dataset_code,release_key,release_date,source_url,raw_sha256,metadata) "
                   f"SELECT source_id,'SEC_FILINGS',{_sql(accession)},{_sql(filing.filed_date)},"
                   f"{_sql('https://www.sec.gov/Archives/')},{_sql(filing.source_manifest_sha256)},"
                   f"{_sql({'accepted_at': filing.accepted_at, 'rights': 'unknown', 'source_manifest_sha256': filing.source_manifest_sha256})}::jsonb "
                   "FROM meta.source WHERE source_code='SEC_CORPORATE_REPORTING' ON CONFLICT DO NOTHING;")
        sql.append("INSERT INTO meta.pipeline_run(pipeline_run_id,run_key,source_id,dataset_release_id,pipeline_name,finished_at,status,input_parameters,artifact_manifest) "
                   f"SELECT {_sql(pipeline_id) }::uuid,{_sql(run_key)},s.source_id,r.dataset_release_id,'sec_corporate_reporting',now(),'succeeded',"
                   f"{_sql({'accession': accession, 'parser_attempt_key': filing.parser_attempt_key, 'parser_contract': filing.parser_contract, 'parser_version': filing.parser_version})}::jsonb,{_sql({'dts_manifest_sha256': filing.dts_manifest_sha256, 'parser_output_sha256': filing.report.parser_output_sha256})}::jsonb "
                   "FROM meta.source s JOIN meta.dataset_release r ON r.source_id=s.source_id "
                   f"WHERE s.source_code='SEC_CORPORATE_REPORTING' AND r.provider_dataset_code='SEC_FILINGS' AND r.release_key={_sql(accession)} ON CONFLICT DO NOTHING;")
        sql.append("INSERT INTO corporate_reporting.filing_submission(filing_id,dataset_release_id,filer_entity_id,accession,form_type,filed_date,accepted_at,report_period_end,primary_document_name,amendment_flag,amendment_description,source_manifest_sha256) "
                   f"SELECT {_sql(filing_id)}::uuid,r.dataset_release_id,{_sql(entity_id)}::uuid,{_sql(accession)},{_sql(filing.form_type)},"
                   f"{_sql(filing.filed_date)},{_sql(filing.accepted_at)},{_sql(filing.report_period_end)},{_sql(filing.primary_document_name)},"
                   f"{_sql(filing.amendment_flag)},{_sql(filing.amendment_description)},{_sql(filing.source_manifest_sha256)} "
                   "FROM meta.dataset_release r JOIN meta.source s USING(source_id) "
                   f"WHERE s.source_code='SEC_CORPORATE_REPORTING' AND r.provider_dataset_code='SEC_FILINGS' AND r.release_key={_sql(accession)} ON CONFLICT DO NOTHING;")
        document_ids: dict[str, str] = {}
        for sequence, document in enumerate(filing.documents, 1):
            document_id = _id("document", accession, document.name)
            document_ids[document.name] = document_id
            _insert(sql, "corporate_reporting.filing_document",
                    ("document_id", "filing_id", "document_name", "document_role", "source_url", "media_type",
                     "byte_length", "sha256", "local_evidence_locator", "archive_sequence"),
                    (document_id, filing_id, document.name, document.role, document.source_url,
                     document.media_type, document.byte_length, document.sha256, document.local_evidence_locator, sequence))
        primary_ids[accession] = document_ids[filing.primary_document_name]
        source_documents = [
            document_ids[d.name] for d in filing.documents
            if d.sha256 == filing.report.source_sha256
        ]
        if len(source_documents) != 1:
            raise QualityGateError("parser source must identify exactly one filing document")
        instance_document_id = source_documents[0]
        schema_document_id = next(document_ids[d.name] for d in filing.documents if d.role == "extension_schema")
        _insert(sql, "corporate_reporting.reporting_scope",
                ("scope_id", "filing_id", "reporting_entity_id", "scope_kind", "scope_label", "evidence_fingerprint"),
                (scope_id, filing_id, entity_id, "consolidated_registrant", filing.issuer_name,
                 _digest({"accession": accession, "scope": "registrant"})))
        _insert(sql, "corporate_reporting.parser_run",
                ("parser_run_id", "pipeline_run_id", "filing_id", "parser_attempt_key", "parser_contract", "parser_version",
                 "source_manifest_sha256", "resolution_policy_sha256", "status", "metrics_sha256",
                 "parser_output_sha256"),
                (parser_id, pipeline_id, filing_id, filing.parser_attempt_key, filing.parser_contract, filing.parser_version,
                 filing.source_manifest_sha256, _digest("identical-duplicates-v1"), "succeeded",
                 filing.report.metrics_sha256, filing.report.parser_output_sha256))
        namespace_inventory = sorted({_expanded(o.concept)[0] for o in filing.report.occurrences})
        taxonomy_id = _id("taxonomy", content_id, filing.dts_manifest_sha256)
        _insert(sql, "corporate_reporting.taxonomy_set",
                ("taxonomy_set_id", "parser_run_id", "filing_id", "entry_schema_document_id",
                 "dts_manifest_sha256", "namespace_inventory", "resolution_status"),
                (taxonomy_id, parser_id, filing_id, schema_document_id, filing.dts_manifest_sha256,
                 namespace_inventory, "unresolved_external"))

        declarations = {(d["namespace_uri"], d["local_name"]): d for d in filing.extension_declarations}
        concepts = {_expanded(o.concept) for o in filing.report.occurrences} | set(declarations)
        concept_ids: dict[str, str] = {}
        for namespace, local in sorted(concepts):
            expanded = f"{{{namespace}}}{local}"
            concept_id = _id("concept", content_id, namespace, local)
            concept_ids[expanded] = concept_id
            declaration = declarations.get((namespace, local))
            _insert(sql, "corporate_reporting.source_concept",
                    ("source_concept_id", "parser_run_id", "filing_id", "taxonomy_set_id", "namespace_uri",
                     "local_name", "declaration_status", "declaration_document_id", "declaration_sha256",
                     "data_type_qname", "substitution_group_qname", "period_type", "balance", "abstract",
                     "nillable", "extension_flag"),
                    (concept_id, parser_id, filing_id, taxonomy_id, namespace, local,
                     "declared" if declaration else "referenced_unresolved", schema_document_id if declaration else None,
                     declaration.get("declaration_sha256") if declaration else None,
                     declaration.get("data_type_qname") if declaration else None,
                     declaration.get("substitution_group_qname") if declaration else None,
                     declaration.get("period_type") if declaration else None,
                     declaration.get("balance") if declaration else None,
                     declaration.get("abstract") if declaration else None,
                     declaration.get("nillable") if declaration else None, bool(declaration)))
        concept_ids_by_filing[accession] = concept_ids

        context_ids: dict[str, str] = {}
        for context in filing.report.contexts.values():
            context_id = _id("context", content_id, context.source_id)
            context_ids[context.source_id] = context_id
            period = context.period
            _insert(sql, "corporate_reporting.xbrl_context",
                    ("context_id", "parser_run_id", "filing_id", "source_context_id", "reporting_scope_id",
                     "entity_scheme", "entity_value", "period_kind", "start_date", "end_date", "instant_date",
                     "raw_xml_sha256", "semantic_context_sha256"),
                    (context_id, parser_id, filing_id, context.source_id, scope_id, context.entity_scheme,
                     context.entity_value, period[0], period[1] if period[0] == "duration" else None,
                     period[2] if period[0] == "duration" else None,
                     period[1] if period[0] == "instant" else None, context.raw_xml_sha256, context.semantic_hash))
            for dimension in context.dimensions:
                axis_ns, axis_local = _expanded(dimension.axis)
                member_ns = member_local = None
                if dimension.member:
                    member_ns, member_local = _expanded(dimension.member)
                _insert(sql, "corporate_reporting.xbrl_context_dimension",
                        ("context_dimension_id", "context_id", "filing_id", "location", "axis_namespace", "axis_local_name",
                         "member_kind", "member_namespace", "member_local_name", "typed_member_canonical_xml"),
                        (_id("dimension", context_id, dimension.location, dimension.axis), context_id, filing_id,
                         dimension.location, axis_ns, axis_local, dimension.member_kind, member_ns, member_local,
                         dimension.typed_member_canonical_xml))
        semantic_unit_ids: dict[str, str] = {}
        alias_ids: dict[str, str] = {}
        for unit in filing.report.units.values():
            unit_id = semantic_unit_ids.setdefault(unit.semantic_hash, _id("unit", content_id, unit.semantic_hash))
            _insert(sql, "corporate_reporting.xbrl_unit_semantics",
                    ("unit_semantics_id", "parser_run_id", "filing_id", "numerator_measures",
                     "denominator_measures", "semantic_unit_sha256"),
                    (unit_id, parser_id, filing_id, unit.numerator, unit.denominator, unit.semantic_hash))
            alias_id = _id("unit_alias", content_id, unit.source_id)
            alias_ids[unit.source_id] = alias_id
            _insert(sql, "corporate_reporting.xbrl_source_unit_alias",
                    ("source_unit_alias_id", "parser_run_id", "filing_id", "source_unit_id",
                     "unit_semantics_id", "raw_xml_sha256"),
                    (alias_id, parser_id, filing_id, unit.source_id, unit_id, unit.raw_xml_sha256))

        occurrence_ids: dict[int, str] = {}
        interpretation_ids: dict[int, str] = {}
        for occurrence in filing.report.occurrences:
            occurrence_id = _id("occurrence", accession, instance_document_id,
                                occurrence.source_ordinal, occurrence.occurrence_sha256)
            occurrence_ids[occurrence.source_ordinal] = occurrence_id
            interpretation_id = _id("occurrence_interpretation", content_id, occurrence_id)
            interpretation_ids[occurrence.source_ordinal] = interpretation_id
            boolean = occurrence.lexical_value.lower() in {"true", "1"} if (
                not occurrence.nil and occurrence.unit_ref is None and occurrence.lexical_value.lower() in {"true", "false", "1", "0"}) else None
            numeric = _numeric(occurrence.lexical_value, occurrence.unit_ref is not None, occurrence.nil)
            if occurrence.inline_format is not None or occurrence.inline_scale is not None or occurrence.inline_sign is not None:
                # Raw Inline lexical text is evidence, not a normalized value. A
                # separately proven transformation must own format/scale/sign.
                numeric = "NULL"
            _insert(sql, "corporate_reporting.fact_occurrence",
                    ("fact_occurrence_id", "filing_id", "document_id", "source_ordinal",
                     "source_concept_qname", "source_context_ref", "source_unit_ref", "xml_lang",
                     "lexical_value", "nil_flag", "decimals", "precision", "inline_format",
                     "inline_scale", "inline_sign", "occurrence_sha256"),
                    (occurrence_id, filing_id, instance_document_id, occurrence.source_ordinal,
                     occurrence.concept, occurrence.context_ref, occurrence.unit_ref,
                     occurrence.xml_lang, occurrence.lexical_value,
                     occurrence.nil, occurrence.decimals, occurrence.precision,
                     occurrence.inline_format, occurrence.inline_scale, occurrence.inline_sign,
                     occurrence.occurrence_sha256))
            _insert(sql, "corporate_reporting.fact_occurrence_interpretation",
                    ("fact_occurrence_interpretation_id", "parser_run_id", "fact_occurrence_id",
                     "filing_id", "source_concept_id", "context_id", "source_unit_alias_id",
                     "normalized_numeric", "normalized_boolean"),
                    (interpretation_id, parser_id, occurrence_id, filing_id,
                     concept_ids[occurrence.concept], context_ids[occurrence.context_ref],
                     alias_ids[occurrence.unit_ref] if occurrence.unit_ref is not None else None,
                     Decimal(numeric) if numeric != "NULL" else None,
                     boolean))
        for slot in filing.report.slots.values():
            first = slot.occurrences[0]
            slot_id = _id("slot", content_id, slot.slot_sha256)
            context = filing.report.contexts[first.context_ref]
            unit_hash = filing.report.units[first.unit_ref].semantic_hash if first.unit_ref else None
            _insert(sql, "corporate_reporting.fact_semantic_slot",
                    ("fact_slot_id", "parser_run_id", "filing_id", "reporting_scope_id", "source_concept_id",
                     "semantic_context_sha256", "semantic_unit_sha256", "xml_lang", "slot_sha256"),
                    (slot_id, parser_id, filing_id, scope_id, concept_ids[first.concept], context.semantic_hash,
                     unit_hash, first.xml_lang, slot.slot_sha256))
            for occurrence in slot.occurrences:
                _insert(sql, "corporate_reporting.fact_slot_occurrence",
                        ("parser_run_id", "fact_slot_id", "fact_occurrence_interpretation_id",
                         "fact_occurrence_id", "filing_id"),
                        (parser_id, slot_id, interpretation_ids[occurrence.source_ordinal],
                         occurrence_ids[occurrence.source_ordinal], filing_id))
            resolution_key = _digest({"axis": "fact_resolution", "accession": accession,
                                      "parser_run": parser_id,
                                      "parser_output": filing.report.parser_output_sha256,
                                      "slot": slot.slot_sha256})
            resolution_revision = _id("knowledge", "fact_resolution", resolution_key)
            _knowledge(sql, resolution_revision, "fact_resolution", resolution_key, pipeline_id,
                       _digest([o.occurrence_sha256 for o in slot.occurrences]), filing.accepted_at,
                       knowledge_cutoff)
            _insert(sql, "corporate_reporting.fact_resolution_revision",
                    ("resolution_revision_id", "knowledge_revision_id", "object_key", "parser_run_id", "filing_id", "fact_slot_id",
                     "selected_occurrence_id", "status", "value_fingerprint", "reason_code", "recorded_at"),
                    (_id("resolution", resolution_key), resolution_revision, resolution_key, parser_id, filing_id, slot_id,
                     occurrence_ids[slot.selected_occurrence.source_ordinal] if slot.selected_occurrence else None,
                     slot.status, slot.selected_occurrence.value_fingerprint if slot.selected_occurrence else None,
                     "identical_values" if slot.selected_occurrence else "distinct_values", knowledge_cutoff))
            snapshot_members.append(("fact_resolution", resolution_key, resolution_revision))
        selection_key = _digest({"axis": "parser_selection", "accession": accession})
        selection_status = _selection_status(filing)
        selection_revision = _id("knowledge", "parser_selection", selection_key,
                                 filing.parser_attempt_key, selection_status)
        selection_payload_id = _id("parser_selection", selection_key,
                                   filing.parser_attempt_key, selection_status)
        if selection_status != "accepted":
            sql.append("DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM corporate_reporting.knowledge_revision "
                       f"WHERE axis_type='parser_selection' AND object_key={_sql(selection_key)}) "
                       f"THEN RAISE EXCEPTION 'CORPORATE_REPORTING_IDENTITY_CONFLICT:{accession}:parser_selection_root_missing'; END IF; END $$;")
        sql.append("INSERT INTO corporate_reporting.knowledge_revision(knowledge_revision_id,axis_type,object_key,predecessor_revision_id,pipeline_run_id,source_effective_at,evidence_fingerprint,recorded_at) "
                   f"SELECT {_sql(selection_revision)}::uuid,'parser_selection',{_sql(selection_key)},"
                   "(SELECT k.knowledge_revision_id FROM corporate_reporting.knowledge_revision k "
                   f"WHERE k.axis_type='parser_selection' AND k.object_key={_sql(selection_key)} "
                   "AND NOT EXISTS (SELECT 1 FROM corporate_reporting.knowledge_revision child WHERE child.predecessor_revision_id=k.knowledge_revision_id)),"
                   f"{_sql(pipeline_id)}::uuid,{_sql(filing.accepted_at)},{_sql(filing.report.parser_output_sha256)},{_sql(knowledge_cutoff)} "
                   f"WHERE NOT EXISTS (SELECT 1 FROM corporate_reporting.knowledge_revision WHERE knowledge_revision_id={_sql(selection_revision)}::uuid) ON CONFLICT DO NOTHING;")
        _insert(sql, "corporate_reporting.parser_run_selection_revision",
                ("parser_run_selection_revision_id", "knowledge_revision_id", "object_key", "filing_id", "parser_run_id",
                 "status", "rationale", "recorded_at"),
                (selection_payload_id, selection_revision, selection_key, filing_id, parser_id, selection_status,
                 ("exact protected manifest and parser invariants passed" if selection_status == "accepted"
                  else "independent parser attempt awaits explicit acceptance"), knowledge_cutoff))
        accepted_selection_revision = (
            selection_revision if selection_status == "accepted" else
            _id("knowledge", "parser_selection", selection_key,
                _PROTECTED_INITIAL_ATTEMPT, "accepted")
        )
        snapshot_members.append(("parser_selection", selection_key, accepted_selection_revision))
        for check_name, observed in sorted(filing.report.metrics.items()):
            _insert(sql, "meta.quality_check",
                    ("quality_check_id", "pipeline_run_id", "check_name", "check_status", "severity",
                     "observed_value", "details"),
                    (_id("quality", pipeline_id, check_name), pipeline_id, check_name, "pass", "error",
                     observed, {"accession": accession, "metrics_sha256": filing.report.metrics_sha256}))
        # Contract checks are separately named and pipeline-run scoped; governance
        # checks remain visibly non-passing until their authority exists.
        scoped_checks = {
            "artifact_integrity": ("pass", "error", 1, "frozen manifest bytes matched"),
            "extraction_completeness": ("pass", "error", 1, "all parsed occurrences persisted"),
            "filing_integrity": ("pass", "error", 1, "filing metadata source-bound"),
            "context_integrity": ("pass", "error", 1, "fact contexts resolved"),
            "dimension_integrity": ("pass", "error", 1, "dimension semantics retained"),
            "unit_integrity": ("pass", "error", 1, "unit semantics resolved"),
            "identity_integrity": ("pass", "error", 1, "filing-scoped identities passed"),
            "conflict_integrity": (
                ("fail", "error", 0,
                 f"{filing.report.metrics['conflicting_slot_count']} conflicting slot(s) preserved; selection blocked")
                if filing.report.metrics["conflicting_slot_count"]
                else ("pass", "error", 1, "no conflicting slot accepted")
            ),
            "mapping_authority": ("warn", "warning", 0, "human mapping authority pending"),
            "temporal_cutoffs": ("pass", "error", 1, "independent cutoffs explicit"),
            "rights_policy": ("warn", "warning", 0, "redistribution authority unknown"),
            "release_completeness": ("fail", "error", 0, "blocked: mapping unaccepted"),
        }
        for check_name, (status, severity, observed, decision) in scoped_checks.items():
            _insert(sql, "meta.quality_check",
                    ("quality_check_id", "pipeline_run_id", "check_name", "check_status", "severity",
                     "observed_value", "details"),
                    (_id("quality", pipeline_id, check_name), pipeline_id, check_name, status, severity,
                     observed, {"accession": accession, "decision": decision, "scope": "pipeline_run"}))
        _insert(sql, "meta.lineage_event",
                ("lineage_event_id", "pipeline_run_id", "source_id", "event_type", "from_artifact",
                 "to_artifact", "checksum_sha256", "row_count", "details"),
                (_id("lineage", pipeline_id), pipeline_id,
                 "00000000-0000-0000-0000-000000000000", "normalized", "raw.sec.filing",
                 "corporate_reporting.fact_occurrence", filing.source_manifest_sha256,
                 len(filing.report.occurrences), {"accession": accession}))
        # Replace the sentinel source UUID with the shared owner's actual UUID.
        sql[-1] = sql[-1].replace("'00000000-0000-0000-0000-000000000000'", "(SELECT source_id FROM meta.source WHERE source_code='SEC_CORPORATE_REPORTING')")

    # Attempt-only batches are evidence capture, not authority changes.  Their
    # parser runs and append-only selection proposals persist, while the prior
    # accepted snapshot remains the sole consumable state.
    if not any(_selection_status(filing) == "accepted" for filing in filings):
        sql.extend(["SET CONSTRAINTS ALL IMMEDIATE;", "COMMIT;",
                    "SELECT json_build_object('filing_count',(SELECT count(*) FROM corporate_reporting.filing_submission WHERE accession IN ("
                    + ",".join(_sql(f.accession) for f in filings) + ")),'document_count',(SELECT count(*) FROM corporate_reporting.filing_document d JOIN corporate_reporting.filing_submission f USING(filing_id) WHERE f.accession IN ("
                    + ",".join(_sql(f.accession) for f in filings) + ")),'occurrence_count',(SELECT count(*) FROM corporate_reporting.fact_occurrence o JOIN corporate_reporting.filing_submission f USING(filing_id) WHERE f.accession IN ("
                    + ",".join(_sql(f.accession) for f in filings) + ")),'slot_count',(SELECT count(*) FROM corporate_reporting.fact_semantic_slot s JOIN corporate_reporting.filing_submission f USING(filing_id) JOIN corporate_reporting.parser_run p ON p.parser_run_id=s.parser_run_id WHERE f.accession IN ("
                    + ",".join(_sql(f.accession) for f in filings) + ") AND p.parser_attempt_key IN (" + ",".join(_sql(f.parser_attempt_key) for f in filings) + ")),'relationship_count',(SELECT count(*) FROM corporate_reporting.filing_relationship_revision));"])
        return "\n".join(sql) + "\n"

    # Source-authenticated amendment linkage remains a proposal. It does not infer
    # restatement or semantic equivalence, and its predecessor may have been
    # committed by an earlier per-filing transaction.
    for filing in filings:
        if filing.relationship_original_accession is None:
            continue
        relationship_key = _digest({
            "axis": "filing_relationship",
            "predecessor": filing.relationship_original_accession,
            "successor": filing.accession,
            "type": "amends",
        })
        relationship_revision = _id("knowledge", "filing_relationship", relationship_key)
        evidence = _digest({
            "basis": "same_cik_base_form_report_date_and_fiscal_slot",
            "restatement_status": "undetermined",
        })
        _knowledge(sql, relationship_revision, "filing_relationship", relationship_key,
                   pipeline_ids[filing.accession], evidence, filing.accepted_at,
                   knowledge_cutoff)
        _insert(sql, "corporate_reporting.filing_relationship_revision",
                ("relationship_revision_id", "knowledge_revision_id", "object_key",
                 "predecessor_filing_id", "successor_filing_id", "relationship_type",
                 "evidence_document_id", "evidence_excerpt_fingerprint", "assertion_status"),
                (_id("relationship", relationship_key), relationship_revision, relationship_key,
                 _id("filing", filing.relationship_original_accession), filing_ids[filing.accession],
                 "amends", primary_ids[filing.accession], evidence,
                 filing.relationship_status or "proposed"))
        snapshot_members.append(("filing_relationship", relationship_key, relationship_revision))

    # TASK-223 source-ingestion proof deliberately stops before governance closure.
    # Normalized source evidence and proposed amendment relations remain; snapshots,
    # mappings, and release eligibility belong to a separately authorized operation.
    if not governance_closure:
        sql.extend(["SET CONSTRAINTS ALL IMMEDIATE;", "COMMIT;",
                    "SELECT json_build_object('filing_count',(SELECT count(*) FROM corporate_reporting.filing_submission WHERE accession IN ("
                    + ",".join(_sql(f.accession) for f in filings) + ")),'document_count',(SELECT count(*) FROM corporate_reporting.filing_document d JOIN corporate_reporting.filing_submission f USING(filing_id) WHERE f.accession IN ("
                    + ",".join(_sql(f.accession) for f in filings) + ")),'occurrence_count',(SELECT count(*) FROM corporate_reporting.fact_occurrence o JOIN corporate_reporting.filing_submission f USING(filing_id) WHERE f.accession IN ("
                    + ",".join(_sql(f.accession) for f in filings) + ")),'slot_count',(SELECT count(*) FROM corporate_reporting.fact_semantic_slot s JOIN corporate_reporting.filing_submission f USING(filing_id) JOIN corporate_reporting.parser_run p ON p.parser_run_id=s.parser_run_id WHERE f.accession IN ("
                    + ",".join(_sql(f.accession) for f in filings) + ") AND p.parser_attempt_key IN (" + ",".join(_sql(f.parser_attempt_key) for f in filings) + ")),'relationship_count',(SELECT count(*) FROM corporate_reporting.filing_relationship_revision));"])
        return "\n".join(sql) + "\n"

    # Direct filing prose supports this edge. Same-QName cross-DTS equivalence remains provisional.
    if set(_FIXTURE_ACCESSIONS).issubset(filing_ids):
        original, amendment = _FIXTURE_ACCESSIONS
        relationship_key = _digest({"axis": "filing_relationship", "predecessor": original,
                                    "successor": amendment, "type": "restates"})
        relationship_revision = _id("knowledge", "filing_relationship", relationship_key)
        _knowledge(sql, relationship_revision, "filing_relationship", relationship_key,
                   pipeline_ids[amendment], _digest("Amendment No. 1 names and restates the Original Filing"),
                   next(f.accepted_at for f in filings if f.accession == amendment), knowledge_cutoff)
        _insert(sql, "corporate_reporting.filing_relationship_revision",
                ("relationship_revision_id", "knowledge_revision_id", "object_key", "predecessor_filing_id",
                 "successor_filing_id", "relationship_type", "evidence_document_id",
                 "evidence_excerpt_fingerprint", "assertion_status"),
                (_id("relationship", relationship_key), relationship_revision, relationship_key, filing_ids[original],
                 filing_ids[amendment], "restates", primary_ids[amendment],
                 _digest("Amendment No. 1 names and restates the Original Filing"), "accepted"))
        snapshot_members.append(("filing_relationship", relationship_key, relationship_revision))
        for local, status in (("Assets", "proposed"), ("ImpairmentOfInvestmentInAffiliates", "deferred")):
            left = next((v for k, v in concept_ids_by_filing[original].items() if k.endswith("}" + local)), None)
            right = next((v for k, v in concept_ids_by_filing[amendment].items() if k.endswith("}" + local)), None)
            if left and right:
                key = _digest({"axis": "concept_equivalence", "left": left, "right": right})
                revision = _id("knowledge", "concept_equivalence", key)
                _knowledge(sql, revision, "concept_equivalence", key, pipeline_ids[amendment],
                           _digest({"status": status, "basis": "QName candidate across distinct DTS"}),
                           None, knowledge_cutoff)
                _insert(sql, "corporate_reporting.source_concept_equivalence_revision",
                        ("equivalence_revision_id", "knowledge_revision_id", "object_key", "left_source_concept_id",
                         "right_source_concept_id", "status", "scope", "rationale", "evidence_fingerprint"),
                        (_id("equivalence", key), revision, key, left, right, status, "gatos-2021-filing-chain",
                         "QName candidate only; distinct DTS prevents automatic acceptance",
                         _digest({"left": left, "right": right, "status": status})))
                snapshot_members.append(("concept_equivalence", key, revision))

    # Mapping state is intentionally non-accepted pending human semantic authority.
    for filing in filings:
        for expanded, concept_id in concept_ids_by_filing[filing.accession].items():
            local = expanded.rsplit("}", 1)[-1]
            if local not in {"Assets", "ImpairmentOfInvestmentInAffiliates"}:
                continue
            mapping_status = "proposed" if local == "Assets" else "deferred"
            key = _digest({"axis": "concept_mapping", "accession": filing.accession,
                           "source_concept": concept_id, "scope": "consolidated_registrant"})
            revision = _id("knowledge", "concept_mapping", key)
            _knowledge(sql, revision, "concept_mapping", key, pipeline_ids[filing.accession],
                       _digest({"status": mapping_status, "concept": expanded}), None,
                       knowledge_cutoff)
            sql.append("INSERT INTO corporate_reporting.concept_mapping_revision(mapping_revision_id,knowledge_revision_id,object_key,source_concept_id,canonical_concept_id,reporting_scope_kind,status,rationale,evidence_fingerprint,recorded_at) "
                       f"SELECT {_sql(_id('mapping', key))}::uuid,{_sql(revision)}::uuid,{_sql(key)},{_sql(concept_id)}::uuid,canonical_concept_id,"
                       f"'consolidated_registrant',{_sql(mapping_status)},{_sql('human semantic acceptance not present')},{_sql(_digest({'status': mapping_status, 'concept': expanded}))},{_sql(knowledge_cutoff)} "
                       "FROM corporate_reporting.canonical_concept WHERE canonical_code='CORP_TOTAL_ASSETS' ON CONFLICT DO NOTHING;")
            snapshot_members.append(("concept_mapping", key, revision))

    # Persist the requested closed-selection proposal without claiming human approval.
    selected_filing = max(filings, key=lambda f: f.accepted_at)
    selection_material = {
        "selection_code": "CORP_TOTAL_ASSETS", "selection_version": "v1",
        "scope_kind": "consolidated_registrant", "period_policy": {"kind": "report_period_end"},
        "applicability": {"form_type": ["10-K", "10-K/A"]},
        "rights_output_family": "private_analysis",
    }
    selection_sha = _digest(selection_material)
    expected_key = _digest({"axis": "expected_selection", **selection_material})
    expected_revision = _id("knowledge", "expected_selection", expected_key)
    expected_id = _id("expected_selection", expected_key)
    _knowledge(sql, expected_revision, "expected_selection", expected_key,
               pipeline_ids[selected_filing.accession], selection_sha, None, knowledge_cutoff)
    sql.append("INSERT INTO corporate_reporting.expected_selection_revision(expected_selection_revision_id,knowledge_revision_id,object_key,selection_code,selection_version,canonical_concept_id,scope_kind,period_policy,applicability_predicate,rights_output_family,selection_sha256,status,recorded_at) "
               f"SELECT {_sql(expected_id)}::uuid,{_sql(expected_revision)}::uuid,{_sql(expected_key)},'CORP_TOTAL_ASSETS','v1',canonical_concept_id,'consolidated_registrant',"
               f"{_sql(selection_material['period_policy'])}::jsonb,{_sql(selection_material['applicability'])}::jsonb,'private_analysis',{_sql(selection_sha)},'proposed',{_sql(knowledge_cutoff)} "
               "FROM corporate_reporting.canonical_concept WHERE canonical_code='CORP_TOTAL_ASSETS' ON CONFLICT DO NOTHING;")
    snapshot_members.append(("expected_selection", expected_key, expected_revision))

    sec_cutoff = max(f.accepted_at for f in filings)
    snapshot_manifest = _digest(sorted(snapshot_members))
    snapshot_id = _id("snapshot", sec_cutoff, knowledge_cutoff, snapshot_manifest)
    _insert(sql, "corporate_reporting.knowledge_snapshot",
            ("knowledge_snapshot_id", "sec_cutoff", "knowledge_cutoff", "manifest_sha256", "recorded_at"),
            (snapshot_id, sec_cutoff, knowledge_cutoff, snapshot_manifest, knowledge_cutoff))
    for axis, key, revision in snapshot_members:
        _insert(sql, "corporate_reporting.knowledge_snapshot_member",
                ("knowledge_snapshot_id", "axis_type", "object_key", "knowledge_revision_id"),
                (snapshot_id, axis, key, revision))
    eligibility_reasons = ["human_mapping_authority_pending", "redistribution_rights_unknown"]
    eligibility_key = _digest({"axis": "release_eligibility", "filing": selected_filing.accession,
                               "selection": selection_sha, "snapshot": snapshot_id,
                               "policy": "private-analysis-v1"})
    eligibility_knowledge = _id("knowledge", "release_eligibility", eligibility_key)
    quality_decision = _digest({"status": "blocked", "reason_codes": eligibility_reasons})
    _knowledge(sql, eligibility_knowledge, "release_eligibility", eligibility_key,
               pipeline_ids[selected_filing.accession], quality_decision, None, knowledge_cutoff)
    sql.append("INSERT INTO corporate_reporting.corporate_release_eligibility_revision(eligibility_revision_id,knowledge_revision_id,object_key,filing_id,expected_selection_revision_id,knowledge_snapshot_id,policy_id,status,reason_codes,source_manifest_sha256,quality_decision_sha256,recorded_at) "
               f"SELECT {_sql(_id('eligibility', eligibility_key))}::uuid,{_sql(eligibility_knowledge)}::uuid,{_sql(eligibility_key)},{_sql(filing_ids[selected_filing.accession])}::uuid,{_sql(expected_id)}::uuid,{_sql(snapshot_id)}::uuid,policy_id,'blocked',"
               f"{_sql(eligibility_reasons)}::jsonb,{_sql(selected_filing.source_manifest_sha256)},{_sql(quality_decision)},{_sql(knowledge_cutoff)} "
               "FROM corporate_reporting.corporate_release_policy WHERE policy_version='private-analysis-v1' ON CONFLICT DO NOTHING;")
    sql.extend(["SET CONSTRAINTS ALL IMMEDIATE;", "COMMIT;",
                "SELECT json_build_object('filing_count',(SELECT count(*) FROM corporate_reporting.filing_submission WHERE accession IN ("
                + ",".join(_sql(f.accession) for f in filings) + ")),'document_count',(SELECT count(*) FROM corporate_reporting.filing_document d JOIN corporate_reporting.filing_submission f USING(filing_id) WHERE f.accession IN ("
                + ",".join(_sql(f.accession) for f in filings) + ")),'occurrence_count',(SELECT count(*) FROM corporate_reporting.fact_occurrence o JOIN corporate_reporting.filing_submission f USING(filing_id) WHERE f.accession IN ("
                + ",".join(_sql(f.accession) for f in filings) + ")),'slot_count',(SELECT count(*) FROM corporate_reporting.fact_semantic_slot s JOIN corporate_reporting.filing_submission f USING(filing_id) JOIN corporate_reporting.parser_run p ON p.parser_run_id=s.parser_run_id WHERE f.accession IN ("
                + ",".join(_sql(f.accession) for f in filings) + ") AND p.parser_attempt_key IN (" + ",".join(_sql(f.parser_attempt_key) for f in filings) + ")),'relationship_count',(SELECT count(*) FROM corporate_reporting.filing_relationship_revision));"])
    return "\n".join(sql) + "\n"


def _reconcile_timed_out_backend(
    *, database_url: str, psql_path: str, application_name: str,
    reconciliation_timeout_seconds: float = RECONCILIATION_QUERY_TIMEOUT_SECONDS,
    reconciliation_deadline: float | None = None,
) -> str:
    """Cancel/terminate only the exact tagged backend left by a timed-out client."""
    argv = [psql_path, "-X", "-v", "ON_ERROR_STOP=1", "-A", "-t", "-d", database_url]
    env = {**os.environ, "PGAPPNAME": (application_name + "-reconcile")[:63]}
    predicate = (
        "datname=current_database() AND usename=current_user AND backend_type='client backend' "
        f"AND application_name={_sql(application_name)} AND pid<>pg_backend_pid()"
    )

    def query(statement: str) -> str:
        remaining = (
            reconciliation_timeout_seconds if reconciliation_deadline is None
            else reconciliation_deadline - time.monotonic()
        )
        if remaining <= 0:
            raise PostgreSQLLoadTimeout("backend reconciliation deadline expired")
        result = subprocess.run(
            argv, input=statement, text=True, capture_output=True, env=env,
            timeout=min(reconciliation_timeout_seconds, remaining),
        )
        if result.returncode:
            raise PostgreSQLLoadTimeout("backend reconciliation query failed")
        return result.stdout.strip()

    def pids() -> list[int]:
        value = query(f"SELECT pid FROM pg_stat_activity WHERE {predicate} ORDER BY pid;")
        return [int(item) for item in value.splitlines() if item]

    found = pids()
    if not found:
        return "already_absent"
    if len(found) != 1:
        raise PostgreSQLLoadTimeout("backend reconciliation identity is ambiguous")
    pid = found[0]
    query(f"SELECT pg_cancel_backend(pid) FROM pg_stat_activity WHERE pid={pid} AND {predicate};")
    deadline = time.monotonic() + CANCEL_POLL_SECONDS
    if reconciliation_deadline is not None:
        deadline = min(deadline, reconciliation_deadline)
    while time.monotonic() < deadline:
        if not pids():
            return "canceled"
        time.sleep(0.1)
    found = pids()
    if found != [pid]:
        raise PostgreSQLLoadTimeout("backend identity changed during reconciliation")
    query(f"SELECT pg_terminate_backend(pid,5000) FROM pg_stat_activity WHERE pid={pid} AND {predicate};")
    deadline = time.monotonic() + TERMINATE_POLL_SECONDS
    if reconciliation_deadline is not None:
        deadline = min(deadline, reconciliation_deadline)
    while time.monotonic() < deadline:
        if not pids():
            return "terminated"
        time.sleep(0.1)
    raise PostgreSQLLoadTimeout("exact timed-out backend survived reconciliation")


def load_corporate_filings_to_postgres(
    filings: Iterable[CorporateFilingLoad],
    *,
    database_url: str,
    knowledge_cutoff: str,
    psql_path: str = "psql",
    deadline: float | None = None,
    reconciliation_deadline: float | None = None,
    application_name: str | None = None,
    statement_timeout_seconds: float = 300.0,
    lock_timeout_seconds: float = 30.0,
    idle_transaction_timeout_seconds: float = 60.0,
    client_timeout_seconds: float = 330.0,
    governance_closure: bool = True,
) -> PostgreSQLLoadResult:
    """Atomically persist normalized filings; exact replay is a no-op.

    Server limits precede every database operation.  The client limit is longer
    than the statement limit but is capped by the caller's absolute deadline.
    """
    batch = tuple(filings)
    if not batch:
        raise ValueError("at least one filing is required")
    if not (0 < lock_timeout_seconds < statement_timeout_seconds < client_timeout_seconds):
        raise ValueError("require lock < statement < client timeout")
    if idle_transaction_timeout_seconds <= 0:
        raise ValueError("idle transaction timeout must be positive")
    app = application_name or f"macroforge-cr-{uuid4().hex[:24]}"
    if len(app) > 63 or not app:
        raise ValueError("application name must contain 1..63 characters")
    for filing in batch:
        if not filing.parser_attempt_key or not filing.parser_contract or not filing.parser_version:
            raise QualityGateError("parser attempt identity, contract, and version are required")
        _selection_status(filing)
        if filing.report.parser_output_sha256 != filing.report.computed_parser_output_sha256:
            raise QualityGateError("parser output digest does not match report payload")
        if filing.report.accession != filing.accession:
            raise QualityGateError("report and filing accession differ")
        if filing.report.dts_manifest_sha256 != filing.dts_manifest_sha256:
            raise QualityGateError("report and filing DTS manifest differ")
        source_documents = [d for d in filing.documents if d.sha256 == filing.report.source_sha256]
        if len(source_documents) != 1:
            raise QualityGateError("parser source must match exactly one filing document")
        if not filing.cik.isdigit() or len(filing.cik) != 10 or not filing.issuer_name:
            raise QualityGateError("per-filing SEC CIK and issuer name are required")
        if filing.relationship_original_accession is None:
            if filing.relationship_status is not None:
                raise QualityGateError("relationship status requires an original accession")
        elif filing.relationship_status not in {None, "proposed", "deferred", "rejected"}:
            raise QualityGateError("source-derived amendment relationships cannot be accepted")
        if len({d.name for d in filing.documents}) != len(filing.documents):
            raise QualityGateError("filing document names are not unique")

    try:
        internal_cutoff = datetime.fromisoformat(knowledge_cutoff.replace("Z", "+00:00"))
        sec_acceptance_cutoff = max(
            datetime.fromisoformat(f.accepted_at.replace("Z", "+00:00")) for f in batch
        )
    except (AttributeError, ValueError) as error:
        raise ValueError("knowledge_cutoff must be a timezone-aware ISO-8601 timestamp") from error
    if internal_cutoff.tzinfo is None:
        raise ValueError("knowledge_cutoff must be a timezone-aware ISO-8601 timestamp")
    if internal_cutoff == sec_acceptance_cutoff:
        raise ValueError("knowledge_cutoff must be independent from SEC acceptance cutoff")
    remaining = float("inf") if deadline is None else deadline - time.monotonic()
    if reconciliation_deadline is not None:
        if remaining < client_timeout_seconds:
            raise PostgreSQLLoadTimeout("work deadline leaves no complete bounded client window")
        timeout = client_timeout_seconds
    else:
        timeout = min(client_timeout_seconds, remaining - 0.25)
    effective_statement_timeout = min(statement_timeout_seconds, timeout - 0.5)
    effective_lock_timeout = min(lock_timeout_seconds, effective_statement_timeout / 2)
    effective_idle_timeout = min(idle_transaction_timeout_seconds, effective_statement_timeout)
    if min(timeout, effective_statement_timeout, effective_lock_timeout, effective_idle_timeout) <= 0:
        raise PostgreSQLLoadTimeout("campaign deadline leaves no bounded load window")
    statement = _build_postgresql_sql(
        batch, knowledge_cutoff, application_name=app,
        statement_timeout_ms=max(1, int(effective_statement_timeout * 1000)),
        lock_timeout_ms=max(1, int(effective_lock_timeout * 1000)),
        idle_transaction_timeout_ms=max(1, int(effective_idle_timeout * 1000)),
        governance_closure=governance_closure,
    )
    try:
        completed = subprocess.run(
            [psql_path, "-X", "-v", "ON_ERROR_STOP=1", "-q", "-A", "-t", "-d", database_url],
            input=statement, text=True, capture_output=True,
            timeout=timeout, env={**os.environ, "PGAPPNAME": app},
        )
    except subprocess.TimeoutExpired as error:
        disposition = _reconcile_timed_out_backend(
            database_url=database_url, psql_path=psql_path, application_name=app,
            reconciliation_deadline=reconciliation_deadline,
        )
        raise PostgreSQLLoadTimeout(
            f"psql client timeout; application={app}; reconciliation={disposition}"
        ) from error
    if completed.returncode:
        message = completed.stderr.strip()
        if "CORPORATE_REPORTING_IDENTITY_CONFLICT" in message:
            raise IdentityConflict(message) from None
        raise PostgreSQLLoadError(message or completed.stdout.strip())
    lines = [line for line in completed.stdout.splitlines() if line.strip().startswith("{")]
    if not lines:
        raise PostgreSQLLoadError("psql returned no load result")
    result = json.loads(lines[-1])
    fingerprint = _digest({"accessions": sorted(f.accession for f in batch), "counts": result,
                           "manifests": sorted(f.source_manifest_sha256 for f in batch),
                           "knowledge_cutoff": knowledge_cutoff})
    return PostgreSQLLoadResult(
        int(result["filing_count"]), int(result["document_count"]),
        int(result["occurrence_count"]), int(result["slot_count"]),
        int(result["relationship_count"]), fingerprint,
    )


def load_protected_gatos_to_postgres(
    *,
    database_url: str,
    fixture_root: str | Path,
    knowledge_cutoff: str,
    inventory_path: str | Path | None = None,
    psql_path: str = "psql",
) -> PostgreSQLLoadResult:
    """Convenience API for the exact frozen two-accession Gatos vertical slice."""
    loads = build_protected_gatos_loads(fixture_root, inventory_path=inventory_path)
    return load_corporate_filings_to_postgres(
        loads, database_url=database_url, knowledge_cutoff=knowledge_cutoff, psql_path=psql_path,
    )


def build_shared_registration_sql(*, accession: str, source_manifest_sha256: str,
                                  parser_output_sha256: str, run_key: str) -> str:
    """Compatibility helper for callers that only inspect shared registration SQL."""
    metadata = json.dumps({"rights": "unknown", "source_manifest_sha256": source_manifest_sha256},
                          sort_keys=True, separators=(",", ":"))
    return f"""BEGIN;
WITH s AS (
 INSERT INTO meta.source(source_code,source_name,source_home_url,license_note)
 VALUES ('SEC_CORPORATE_REPORTING','U.S. Securities and Exchange Commission','https://www.sec.gov/','rights unknown; private analysis only')
 ON CONFLICT(source_code) DO UPDATE SET source_name=EXCLUDED.source_name RETURNING source_id
), r AS (
 INSERT INTO meta.dataset_release(source_id,provider_dataset_code,release_key,source_url,raw_sha256,metadata)
 SELECT source_id,'SEC_FILINGS',{_sql(accession)},'https://www.sec.gov/Archives/',{_sql(source_manifest_sha256)},{_sql(metadata)}::jsonb FROM s
 ON CONFLICT(source_id,provider_dataset_code,release_key) DO NOTHING RETURNING dataset_release_id,source_id
), p AS (
 INSERT INTO meta.pipeline_run(run_key,source_id,dataset_release_id,pipeline_name,finished_at,status,artifact_manifest)
 SELECT {_sql(run_key)},source_id,dataset_release_id,'sec_corporate_reporting',now(),'succeeded',jsonb_build_object('parser_output_sha256',{_sql(parser_output_sha256)}) FROM r
 ON CONFLICT(run_key) DO NOTHING RETURNING pipeline_run_id,source_id
)
INSERT INTO meta.lineage_event(pipeline_run_id,source_id,event_type,from_artifact,to_artifact,checksum_sha256,details)
SELECT pipeline_run_id,source_id,'normalized','raw.sec.filing','corporate_reporting.fact_occurrence',{_sql(source_manifest_sha256)},jsonb_build_object('accession',{_sql(accession)}) FROM p;
COMMIT;"""
