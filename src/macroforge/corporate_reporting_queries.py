"""Fail-closed pure point-in-time semantics for Corporate Reporting."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
import json
import subprocess
from typing import Any, Iterable, Mapping
from uuid import UUID


class AmbiguousSelection(RuntimeError):
    pass


@dataclass(frozen=True)
class RevisionAuthority:
    axis: str
    object_key: str
    revision_id: str
    status: str
    recorded_at: datetime


@dataclass(frozen=True)
class FactAuthority:
    parser_selection_key: str
    resolution_key: str
    mapping_key: str
    expected_selection_key: str
    source_concept_id: str
    dts_manifest_sha256: str
    equivalence_key: str | None = None
    absence_key: str | None = None


@dataclass(frozen=True)
class Filing:
    accession: str
    filer_cik: str
    report_period: str
    accepted_at: datetime
    facts: Mapping[str, str]
    predecessor_accession: str | None = None
    relationship_key: str | None = None
    source_available_at: datetime | None = None
    fact_authority: Mapping[str, FactAuthority] = field(default_factory=dict)


@dataclass(frozen=True)
class KnowledgeSnapshot:
    snapshot_id: str
    knowledge_cutoff: datetime
    terminals: tuple[RevisionAuthority, ...]

    def select(self, axis: str, object_key: str, *, statuses: frozenset[str] = frozenset({"accepted", "accepted_identical", "not_reported"})) -> RevisionAuthority | None:
        """Select one cutoff-eligible terminal; future knowledge is invisible.

        Absence is useful to exclude a candidate edge, while multiplicity can never
        be silently resolved. ``require`` below additionally rejects absence.
        """
        rows = [r for r in self.terminals if r.axis == axis and r.object_key == object_key
                and r.recorded_at <= self.knowledge_cutoff and r.status in statuses]
        if len(rows) > 1:
            raise AmbiguousSelection(
                f"expected at most one eligible {axis} terminal for {object_key}; found {len(rows)}"
            )
        return rows[0] if rows else None

    def require(self, axis: str, object_key: str, *, statuses: frozenset[str] = frozenset({"accepted", "accepted_identical", "not_reported"})) -> RevisionAuthority:
        row = self.select(axis, object_key, statuses=statuses)
        if row is None:
            raise AmbiguousSelection(
                f"expected exactly one eligible {axis} terminal for {object_key}; found 0"
            )
        return row


@dataclass(frozen=True)
class HistoryItem:
    accession: str
    accepted_at: datetime
    value: str


@dataclass(frozen=True)
class MappingAssertion:
    source_concept_id: str
    parser_run_id: str
    dts_manifest_sha256: str
    filing_accession: str
    reporting_scope_kind: str
    canonical_concept: str
    status: str


@dataclass(frozen=True)
class ClosedSelection:
    selection_code: str
    status: str


@dataclass(frozen=True)
class SelectionOutcome:
    state: str
    explicit_absence: bool


_SELECTION_STATES = frozenset({
    "zero", "nil", "source_absent", "expected_artifact_unavailable",
    "extraction_failure", "context_unresolved", "mapping_unresolved",
    "rights_blocked", "release_exclusion", "unknown",
})


def resolve_accepted_mapping(
    mappings: Iterable[MappingAssertion], *, source_concept_id: str,
    parser_run_id: str, dts_manifest_sha256: str, filing_accession: str,
    reporting_scope_kind: str, canonical_concept: str,
) -> MappingAssertion:
    matches = [m for m in mappings if m.status == "accepted"
               and m.source_concept_id == source_concept_id
               and m.parser_run_id == parser_run_id
               and m.dts_manifest_sha256 == dts_manifest_sha256
               and m.filing_accession == filing_accession
               and m.reporting_scope_kind == reporting_scope_kind
               and m.canonical_concept == canonical_concept]
    if len(matches) != 1:
        raise AmbiguousSelection(
            f"expected exactly one accepted exact-scope mapping; found {len(matches)}"
        )
    return matches[0]


def classify_selection_outcome(
    selection: ClosedSelection, *, parser_status: str, state: str,
) -> SelectionOutcome:
    if state not in _SELECTION_STATES:
        raise ValueError(f"unsupported selection state: {state}")
    if selection.status != "accepted":
        return SelectionOutcome(
            "mapping_unresolved" if selection.status == "proposed" else "unknown", False,
        )
    if parser_status != "succeeded":
        return SelectionOutcome("extraction_failure", False)
    return SelectionOutcome(state, state == "source_absent")


def source_available(filing: Filing, sec_cutoff: datetime) -> bool:
    available = filing.source_available_at or filing.accepted_at
    return filing.accepted_at <= sec_cutoff and available <= sec_cutoff


def _authorize_fact(filing: Filing, concept: str, snapshot: KnowledgeSnapshot) -> None:
    authority = filing.fact_authority.get(concept)
    if authority is None:
        raise AmbiguousSelection(f"missing authority for {filing.accession}:{concept}")
    snapshot.require("parser_selection", authority.parser_selection_key)
    snapshot.require("fact_resolution", authority.resolution_key)
    snapshot.require("concept_mapping", authority.mapping_key)
    snapshot.require("expected_selection", authority.expected_selection_key)
    if concept not in filing.facts:
        if authority.absence_key is None:
            raise AmbiguousSelection(f"unproven absence for {filing.accession}:{concept}")
        snapshot.require("fact_absence", authority.absence_key)


def as_reported(filings: Iterable[Filing], accession: str, *, snapshot: KnowledgeSnapshot,
                selection: set[str]) -> Filing:
    matches = [f for f in filings if f.accession == accession]
    if len(matches) != 1:
        raise KeyError(accession)
    for concept in selection:
        _authorize_fact(matches[0], concept, snapshot)
    return matches[0]


def known_as_of(filings: Iterable[Filing], filer_cik: str, report_period: str,
                selection: set[str], sec_cutoff: datetime,
                snapshot: KnowledgeSnapshot) -> Filing | None:
    if not selection:
        raise AmbiguousSelection("closed selection is empty")
    eligible = [f for f in filings if f.filer_cik == filer_cik and
                f.report_period == report_period and source_available(f, sec_cutoff)]
    if not eligible:
        return None
    by_accession = {f.accession: f for f in eligible}
    successors: dict[str, list[Filing]] = {}
    for candidate in eligible:
        if candidate.predecessor_accession not in by_accession:
            continue
        if not candidate.relationship_key:
            raise AmbiguousSelection("successor lacks relationship authority key")
        relationship = snapshot.select("filing_relationship", candidate.relationship_key)
        if relationship is None:
            # The SEC filing may exist while the internal relationship revision is
            # still future knowledge; such a successor is invisible at this snapshot.
            continue
        covered = selection & set(candidate.facts)
        if covered and covered != selection:
            raise AmbiguousSelection("relevant amendment is partial for closed selection")
        if covered == selection:
            for concept in selection:
                _authorize_fact(candidate, concept, snapshot)
            successors.setdefault(candidate.predecessor_accession, []).append(candidate)
    if any(len(rows) != 1 for rows in successors.values()):
        raise AmbiguousSelection("multiple eligible terminal amendments")
    roots = [f for f in eligible if f.predecessor_accession is None]
    complete_roots = [f for f in roots if selection <= set(f.facts)]
    if len(complete_roots) != 1:
        raise AmbiguousSelection("zero or multiple complete roots")
    selected = complete_roots[0]
    for concept in selection:
        _authorize_fact(selected, concept, snapshot)
    seen: set[str] = set()
    while selected.accession in successors:
        if selected.accession in seen:
            raise AmbiguousSelection("succession cycle")
        seen.add(selected.accession)
        selected = successors[selected.accession][0]
    return selected


def revision_history(filings: Iterable[Filing], concept: str,
                     snapshot: KnowledgeSnapshot) -> list[HistoryItem]:
    rows = sorted((f for f in filings if concept in f.facts),
                  key=lambda f: (f.accepted_at, f.accession))
    for filing in rows:
        _authorize_fact(filing, concept, snapshot)
    for left, right in zip(rows, rows[1:]):
        a, b = left.fact_authority[concept], right.fact_authority[concept]
        if a.dts_manifest_sha256 != b.dts_manifest_sha256:
            key = b.equivalence_key or a.equivalence_key
            if key is None:
                raise AmbiguousSelection("cross-DTS history lacks equivalence authority")
            try:
                snapshot.require("concept_equivalence", key)
            except AmbiguousSelection as error:
                raise AmbiguousSelection("cross-DTS history lacks accepted equivalence authority") from error
    return [HistoryItem(f.accession, f.accepted_at, f.facts[concept]) for f in rows]


def latest_verified(filings: Iterable[Filing], filer_cik: str, report_period: str,
                    selection: set[str], current_sec_cutoff: datetime,
                    snapshot: KnowledgeSnapshot) -> Filing | None:
    return known_as_of(filings, filer_cik, report_period, selection,
                       current_sec_cutoff, snapshot)


_RELEASE_AUTHORITY_FIELDS = frozenset({
    "subscription_revision_id", "sec_cutoff", "knowledge_cutoff",
    "knowledge_snapshot_id", "policy", "expected_selection_revision_id",
    "amendment_selection_revision_id", "parser_authority_revision_ids",
    "mapping_revision_ids", "equivalence_revision_ids", "rights", "quality",
    "filing_accessions", "selected_accession", "source_manifest_sha256",
    "source_hashes", "conflict",
})
_HEX = frozenset("0123456789abcdef")


def _closed_mapping(value: object, label: str, fields: frozenset[str]) -> Mapping[str, Any]:
    if not isinstance(value, Mapping) or set(value) != set(fields):
        raise AmbiguousSelection(f"release authority {label} fields are incomplete or unknown")
    return value


def _authority_hash(value: object, label: str) -> None:
    if not isinstance(value, str) or len(value) != 64 or any(c not in _HEX for c in value):
        raise AmbiguousSelection(f"release authority {label} hash is malformed")


def _validate_synthetic_release_authority(
    authority: Mapping[str, Any], *, filings: tuple[Filing, ...], selected: Filing,
    sec_cutoff: datetime, snapshot: KnowledgeSnapshot,
) -> None:
    """Recompute observable closure and validate this model's synthetic evidence.

    Source bytes, rights records and quality records are outside this bounded pure
    model.  Consequently only its explicit synthetic fixture convention is accepted;
    this cannot promote real proposed mappings or unknown rights.
    """
    if set(authority) != set(_RELEASE_AUTHORITY_FIELDS):
        raise AmbiguousSelection("release authority fields are incomplete or unknown")
    accessions = tuple(sorted(f.accession for f in filings if source_available(f, sec_cutoff)))
    recomputed = {
        "sec_cutoff": sec_cutoff.isoformat(),
        "knowledge_cutoff": snapshot.knowledge_cutoff.isoformat(),
        "knowledge_snapshot_id": snapshot.snapshot_id,
        "filing_accessions": accessions,
        "selected_accession": selected.accession,
    }
    for key, expected in recomputed.items():
        if authority[key] != expected:
            raise AmbiguousSelection(f"stale release authority {key}")

    policy = _closed_mapping(authority["policy"], "policy", frozenset({"id", "version", "sha256"}))
    _closed_mapping(authority["rights"], "rights", frozenset({"revision_id", "status"}))
    quality = _closed_mapping(authority["quality"], "quality", frozenset({
        "set_revision_id", "decision_revision_id", "evidence_sha256",
    }))
    _closed_mapping(authority["conflict"], "conflict", frozenset({"revision_id", "policy", "state"}))
    source_hashes = _closed_mapping(authority["source_hashes"], "source hashes", frozenset(accessions))
    _authority_hash(policy["sha256"], "policy")
    _authority_hash(quality["evidence_sha256"], "quality evidence")
    _authority_hash(authority["source_manifest_sha256"], "source manifest")
    for accession, value in source_hashes.items():
        _authority_hash(value, f"source {accession}")

    expected_synthetic: dict[str, object] = {
        "subscription_revision_id": "synthetic-subscription-r1",
        "policy": {"id": "synthetic-policy", "version": "private-v1", "sha256": "a" * 64},
        "expected_selection_revision_id": "synthetic-expected-r1",
        "amendment_selection_revision_id": "synthetic-amendment-r1",
        "parser_authority_revision_ids": ("synthetic-parser-r1",),
        "mapping_revision_ids": ("synthetic-mapping-r1",),
        "equivalence_revision_ids": ("synthetic-equivalence-r1",),
        "rights": {"revision_id": "synthetic-rights-r1", "status": "accepted_private_analysis"},
        "quality": {"set_revision_id": "synthetic-quality-set-r1",
                    "decision_revision_id": "synthetic-quality-decision-r1", "evidence_sha256": "b" * 64},
        "source_manifest_sha256": "c" * 64,
        "source_hashes": {accession: chr(ord("d") + index) * 64
                          for index, accession in enumerate(accessions)},
        "conflict": {"revision_id": "synthetic-conflict-r1",
                     "policy": "identical_duplicates_only-v1", "state": "no_conflict"},
    }
    for key, expected in expected_synthetic.items():
        if authority[key] != expected:
            if key == "rights":
                raise AmbiguousSelection("rights authority is stale or unaccepted")
            if key == "conflict":
                raise AmbiguousSelection("conflict authority is stale or unresolved")
            raise AmbiguousSelection(f"stale release authority {key}")


@dataclass(frozen=True)
class CorporateAuthorityRef:
    """Opaque database authority identifier; it intentionally carries no payload."""

    root_id: UUID

    def __init__(self, root_id: UUID | str) -> None:
        object.__setattr__(self, "root_id", root_id if isinstance(root_id, UUID) else UUID(str(root_id)))


class PostgresCorporateAuthorityStore:
    """Small concrete PostgreSQL resolver using the installed ``psql`` client.

    Keeping the adapter dependency-free is useful for offline loaders, while argv and
    UUID validation ensure caller text is never interpreted as SQL.
    """

    def __init__(self, database_url: str) -> None:
        if not isinstance(database_url, str) or not database_url:
            raise TypeError("database URL is required")
        self.database_url = database_url

    def resolve(self, authority: CorporateAuthorityRef) -> Mapping[str, Any]:
        if type(authority) is not CorporateAuthorityRef:
            raise TypeError("an opaque CorporateAuthorityRef is required")
        root = str(authority.root_id)
        statement = f"""
WITH root AS (
 SELECT e.*,s.sec_cutoff,s.knowledge_cutoff,s.manifest_sha256,
        f.accession,f.report_period_end,f.accepted_at,f.source_manifest_sha256 AS filing_manifest,
        p.policy_version,p.policy_sha256,p.allowed_output_family,
        x.knowledge_revision_id AS expected_kr,x.selection_code,
        x.selection_sha256,x.scope_kind,x.status AS expected_status,c.canonical_code
 FROM corporate_reporting.corporate_release_eligibility_revision e
 JOIN corporate_reporting.filing_submission f USING(filing_id)
 JOIN corporate_reporting.knowledge_snapshot s USING(knowledge_snapshot_id)
 JOIN corporate_reporting.corporate_release_policy p USING(policy_id)
 JOIN corporate_reporting.expected_selection_revision x USING(expected_selection_revision_id)
 JOIN corporate_reporting.canonical_concept c USING(canonical_concept_id)
 WHERE e.eligibility_revision_id='{root}'::uuid
), parser AS (
 SELECT ps.*,pr.source_manifest_sha256,pr.parser_output_sha256,pr.status AS parser_status,
        pr.pipeline_run_id,pr.recorded_at AS parser_recorded_at
 FROM root r JOIN corporate_reporting.knowledge_snapshot_member sm ON sm.knowledge_snapshot_id=r.knowledge_snapshot_id
 JOIN corporate_reporting.parser_run_selection_revision ps ON ps.knowledge_revision_id=sm.knowledge_revision_id
 JOIN corporate_reporting.parser_run pr ON pr.parser_run_id=ps.parser_run_id AND pr.filing_id=ps.filing_id
 WHERE ps.filing_id=r.filing_id AND ps.status='accepted' AND pr.status='succeeded'
), items AS (
 SELECT jsonb_build_object(
  'item_key',r.selection_code,'provider','SEC','accession',r.accession,
  'report_period',r.report_period_end,'canonical_concept',r.canonical_code,'scope',r.scope_kind,
  'dimensions',COALESCE((SELECT jsonb_agg(jsonb_build_object('axis','{{'||d.axis_namespace||'}}'||d.axis_local_name,
    'member_kind',d.member_kind,'explicit_member',CASE WHEN d.member_kind='explicit' THEN '{{'||d.member_namespace||'}}'||d.member_local_name END,
    'typed_member',CASE WHEN d.member_kind='typed' THEN jsonb_build_object('sha256',d.typed_member_sha256) END)
    ORDER BY d.location,d.axis_namespace,d.axis_local_name) FROM corporate_reporting.xbrl_context_dimension d WHERE d.context_id=xc.context_id),'[]'::jsonb),
  'unit',CASE WHEN u.unit_semantics_id IS NULL THEN NULL ELSE jsonb_build_object('numerator',u.numerator_measures,'denominator',u.denominator_measures) END,
  'state',CASE WHEN o.nil_flag THEN 'nil' ELSE 'reported' END,
  'value',CASE WHEN o.nil_flag THEN NULL ELSE COALESCE(i.normalized_numeric::text,i.normalized_boolean::text,o.lexical_value) END,
  'mapping_evidence_fingerprint',cm.evidence_fingerprint,'resolution_evidence_fingerprint',kr.evidence_fingerprint,
  'source_occurrence_fingerprints',jsonb_build_array(o.occurrence_sha256),
  'parser_selection_revision_id',p.parser_run_selection_revision_id::text,
  'resolution_revision_id',fr.resolution_revision_id::text,'mapping_revision_id',cm.mapping_revision_id::text,
  'absence_revision_id',NULL,'source_concept',jsonb_build_object('id',sc.source_concept_id::text,
    'qname','{{'||sc.namespace_uri||'}}'||sc.local_name,'dts_manifest_sha256',t.dts_manifest_sha256),
  'slot',jsonb_build_object('id',fs.fact_slot_id::text,'sha256',fs.slot_sha256),
  'conflict',jsonb_build_object('state','no_conflict','resolution_status',fr.status)
 ) item
 FROM root r JOIN parser p ON true
 JOIN corporate_reporting.concept_mapping_revision cm ON cm.canonical_concept_id=(SELECT canonical_concept_id FROM corporate_reporting.expected_selection_revision WHERE expected_selection_revision_id=r.expected_selection_revision_id)
  AND cm.reporting_scope_kind=r.scope_kind AND cm.status='accepted'
 JOIN corporate_reporting.knowledge_snapshot_member mm ON mm.knowledge_snapshot_id=r.knowledge_snapshot_id AND mm.knowledge_revision_id=cm.knowledge_revision_id
 JOIN corporate_reporting.source_concept sc ON sc.source_concept_id=cm.source_concept_id AND sc.parser_run_id=p.parser_run_id
 JOIN corporate_reporting.taxonomy_set t USING(taxonomy_set_id)
 JOIN corporate_reporting.fact_semantic_slot fs ON fs.source_concept_id=sc.source_concept_id AND fs.parser_run_id=p.parser_run_id
 JOIN corporate_reporting.fact_resolution_revision fr ON fr.fact_slot_id=fs.fact_slot_id AND fr.parser_run_id=p.parser_run_id AND fr.status='accepted_identical'
 JOIN corporate_reporting.knowledge_revision kr ON kr.knowledge_revision_id=fr.knowledge_revision_id
 JOIN corporate_reporting.knowledge_snapshot_member rm ON rm.knowledge_snapshot_id=r.knowledge_snapshot_id AND rm.knowledge_revision_id=fr.knowledge_revision_id
 JOIN corporate_reporting.fact_occurrence o ON o.fact_occurrence_id=fr.selected_occurrence_id
 JOIN corporate_reporting.fact_occurrence_interpretation i ON i.fact_occurrence_id=o.fact_occurrence_id AND i.parser_run_id=p.parser_run_id
 JOIN corporate_reporting.xbrl_context xc USING(context_id)
 LEFT JOIN corporate_reporting.xbrl_source_unit_alias ua ON ua.source_unit_alias_id=i.source_unit_alias_id
 LEFT JOIN corporate_reporting.xbrl_unit_semantics u USING(unit_semantics_id)
), document AS (
 SELECT jsonb_build_object('document_id',d.document_id::text,'name',d.document_name,'role',d.document_role,
  'sha256',d.sha256,'byte_length',d.byte_length,'local_evidence_locator',d.local_evidence_locator) value
 FROM root r JOIN corporate_reporting.filing_document d USING(filing_id)
), rights AS (
 SELECT jsonb_build_object('revision_id',rr.rights_revision_id::text,'status',rr.decision_status,
  'output_family',rr.output_family,'redistribution_status',rr.redistribution_status,
  'remote_delivery_enabled',rr.remote_delivery_enabled,'evidence_fingerprint',rr.evidence_fingerprint) value
 FROM root r JOIN corporate_reporting.knowledge_snapshot_member sm ON sm.knowledge_snapshot_id=r.knowledge_snapshot_id
 JOIN corporate_reporting.corporate_rights_revision rr ON rr.knowledge_revision_id=sm.knowledge_revision_id
 WHERE rr.filing_id=r.filing_id
), quality AS (
 SELECT jsonb_build_object('revision_id',q.quality_gate_revision_id::text,'status',q.decision_status,
  'check_set',q.check_set,'check_set_sha256',q.check_set_sha256) value
 FROM root r JOIN corporate_reporting.knowledge_snapshot_member sm ON sm.knowledge_snapshot_id=r.knowledge_snapshot_id
 JOIN corporate_reporting.corporate_quality_gate_revision q ON q.knowledge_revision_id=sm.knowledge_revision_id
 WHERE q.filing_id=r.filing_id
), pipeline_quality AS (
 SELECT jsonb_build_object('check_id',q.check_name,
  'status',CASE q.check_status WHEN 'pass' THEN 'passed' ELSE q.check_status END,
  'evidence_sha256',q.details->>'evidence_sha256') value
 FROM parser p JOIN meta.quality_check q USING(pipeline_run_id)
), relationship AS (
 SELECT jsonb_build_object('revision_id',x.relationship_revision_id::text,'status',x.assertion_status,
  'predecessor_accession',pf.accession,'successor_accession',sf.accession,
  'relationship_type',x.relationship_type,'evidence_document_id',x.evidence_document_id::text) value
 FROM root r JOIN corporate_reporting.knowledge_snapshot_member sm ON sm.knowledge_snapshot_id=r.knowledge_snapshot_id
 JOIN corporate_reporting.filing_relationship_revision x ON x.knowledge_revision_id=sm.knowledge_revision_id
 JOIN corporate_reporting.filing_submission pf ON pf.filing_id=x.predecessor_filing_id
 JOIN corporate_reporting.filing_submission sf ON sf.filing_id=x.successor_filing_id
), equivalence AS (
 SELECT jsonb_build_object('revision_id',x.equivalence_revision_id::text,'status',x.status,
  'left_source_concept_id',x.left_source_concept_id::text,'right_source_concept_id',x.right_source_concept_id::text,
  'scope',x.scope,'evidence_fingerprint',x.evidence_fingerprint) value
 FROM root r JOIN corporate_reporting.knowledge_snapshot_member sm ON sm.knowledge_snapshot_id=r.knowledge_snapshot_id
 JOIN corporate_reporting.source_concept_equivalence_revision x ON x.knowledge_revision_id=sm.knowledge_revision_id
)
SELECT jsonb_build_object(
 'authority_root_id',r.eligibility_revision_id::text,'output_family',r.allowed_output_family,
 'subscription_id','corporate:'||r.accession,'sec_cutoff',r.sec_cutoff,'knowledge_cutoff',r.knowledge_cutoff,
 'knowledge_snapshot_id',r.knowledge_snapshot_id::text,'snapshot_manifest_sha256',r.manifest_sha256,
 'filing',jsonb_build_object('accession',r.accession,'report_period',r.report_period_end,'source_manifest_sha256',r.filing_manifest),
 'policy',jsonb_build_object('id',r.policy_id::text,'version',r.policy_version,'sha256',r.policy_sha256,'output_family',r.allowed_output_family),
 'expected_selection',jsonb_build_object('revision_id',r.expected_selection_revision_id::text,'selection_sha256',r.selection_sha256,
  'status',r.expected_status,'canonical_concept',r.canonical_code,'scope',r.scope_kind),
 'eligibility',jsonb_build_object('revision_id',r.eligibility_revision_id::text,'status',r.status,'reason_codes',r.reason_codes,
  'source_manifest_sha256',r.source_manifest_sha256,'quality_decision_sha256',r.quality_decision_sha256),
 'documents',(SELECT COALESCE(jsonb_agg(value ORDER BY value->>'name'),'[]') FROM document),
 'parser_selections',(SELECT COALESCE(jsonb_agg(jsonb_build_object('revision_id',parser_run_selection_revision_id::text,'parser_run_id',parser_run_id::text,'status',status)),'[]') FROM parser),
 'items',(SELECT COALESCE(jsonb_agg(item ORDER BY item->>'item_key'),'[]') FROM items),
 'rights',(SELECT value FROM rights),'quality',(SELECT value FROM quality),
 'relationships',(SELECT COALESCE(jsonb_agg(value ORDER BY value->>'revision_id'),'[]') FROM relationship),
 'equivalences',(SELECT COALESCE(jsonb_agg(value ORDER BY value->>'revision_id'),'[]') FROM equivalence),
 'pipeline_quality_checks',(SELECT COALESCE(jsonb_agg(value ORDER BY value->>'check_id'),'[]') FROM pipeline_quality),
 'parser_source_manifest_sha256',(SELECT source_manifest_sha256 FROM parser),
 'parser_recorded_at',(SELECT parser_recorded_at FROM parser),'filing_accepted_at',r.accepted_at,
 'snapshot_members',(SELECT jsonb_agg(jsonb_build_object('axis',sm.axis_type,'object_key',sm.object_key,
   'revision_id',sm.knowledge_revision_id::text,'recorded_at',kr.recorded_at,
   'source_effective_at',kr.source_effective_at,
   'terminal_at_cutoff',NOT EXISTS(SELECT 1 FROM corporate_reporting.knowledge_revision child
      WHERE child.predecessor_revision_id=kr.knowledge_revision_id AND child.recorded_at<=r.knowledge_cutoff))
   ORDER BY sm.axis_type,sm.object_key,sm.knowledge_revision_id)
   FROM corporate_reporting.knowledge_snapshot_member sm JOIN corporate_reporting.knowledge_revision kr USING(knowledge_revision_id)
   WHERE sm.knowledge_snapshot_id=r.knowledge_snapshot_id)
)::text FROM root r
WHERE r.status='eligible' AND r.reason_codes='[]'::jsonb AND r.expected_status='accepted'
 AND r.allowed_output_family='private_analysis' AND r.source_manifest_sha256=r.filing_manifest
 AND r.sec_cutoff<=r.knowledge_cutoff AND r.accepted_at<=r.sec_cutoff
 AND r.expected_kr IN (SELECT knowledge_revision_id FROM corporate_reporting.knowledge_snapshot_member WHERE knowledge_snapshot_id=r.knowledge_snapshot_id);
"""
        result = subprocess.run(
            ["psql", "-X", "-v", "ON_ERROR_STOP=1", "-At", "-d", self.database_url],
            input=statement, text=True, capture_output=True,
        )
        if result.returncode:
            raise AmbiguousSelection(
                f"database authority resolution failed: {result.stderr.strip()}"
            )
        raw = result.stdout.strip()
        if not raw:
            raise AmbiguousSelection("missing, inactive, or incomplete database authority")
        document = json.loads(raw)
        required_axes = {"expected_selection", "parser_selection", "concept_mapping", "fact_resolution",
                         "corporate_rights", "corporate_quality_gate"}
        optional_axes = {"filing_relationship", "concept_equivalence"}
        members = document.get("snapshot_members") or []
        axes = {row.get("axis") for row in members}
        rights, quality = document.get("rights"), document.get("quality")
        if (not required_axes <= axes or not axes <= required_axes | optional_axes or
                len(document.get("parser_selections", ())) != 1 or
                len(document.get("items", ())) != 1 or not document.get("documents") or
                not isinstance(rights, Mapping) or rights.get("status") != "accepted" or
                rights.get("output_family") != "private_analysis" or
                rights.get("redistribution_status") not in {"unresolved", "not_authorized"} or
                rights.get("remote_delivery_enabled") is not False or
                not isinstance(quality, Mapping) or quality.get("status") != "accepted" or
                not quality.get("check_set")):
            raise AmbiguousSelection("database authority closure is incomplete")
        cutoff = datetime.fromisoformat(str(document["knowledge_cutoff"]))
        sec_cutoff = datetime.fromisoformat(str(document["sec_cutoff"]))
        if (datetime.fromisoformat(str(document["filing_accepted_at"])) > sec_cutoff or
                datetime.fromisoformat(str(document["parser_recorded_at"])) > cutoff):
            raise AmbiguousSelection("filing/parser source is future at its cutoff")
        for member in members:
            effective = member.get("source_effective_at")
            if (datetime.fromisoformat(str(member["recorded_at"])) > cutoff or
                    (effective is not None and datetime.fromisoformat(str(effective)) > sec_cutoff) or
                    member.get("terminal_at_cutoff") is not True):
                raise AmbiguousSelection("snapshot contains a future or nonterminal knowledge revision")
        from hashlib import sha256
        from pathlib import Path
        canonical = lambda value: json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()
        manifest_members = sorted(
            [[row["axis"], row["object_key"], row["revision_id"]] for row in members]
        )
        if document["snapshot_manifest_sha256"] != sha256(canonical(manifest_members)).hexdigest():
            raise AmbiguousSelection("knowledge snapshot manifest is not canonical and exact")
        source_members: list[list[object]] = []
        document_ids: set[str] = set()
        for source in document["documents"]:
            locator = source.get("local_evidence_locator")
            try:
                payload = Path(locator).read_bytes() if isinstance(locator, str) and locator else None
            except OSError as error:
                raise AmbiguousSelection("document local evidence is unavailable") from error
            if payload is None or len(payload) != source["byte_length"] or sha256(payload).hexdigest() != source["sha256"]:
                raise AmbiguousSelection("document byte hash/evidence verification failed")
            document_ids.add(source["document_id"])
            source_members.append([source["name"], source["role"],
                                   source["byte_length"], source["sha256"]])
        source_manifest = sha256(canonical(sorted(
            source_members, key=lambda row: (str(row[0]), str(row[1]), str(row[2]), str(row[3]))
        ))).hexdigest()
        if any(value != source_manifest for value in (
                document["filing"]["source_manifest_sha256"],
                document["eligibility"]["source_manifest_sha256"],
                document["parser_source_manifest_sha256"],)):
            raise AmbiguousSelection("filing/parser/eligibility source manifest is detached from complete documents")
        expected_quality = sorted(document.get("pipeline_quality_checks") or [], key=lambda row: row["check_id"])
        actual_quality = sorted(quality["check_set"], key=lambda row: row["check_id"])
        expected_quality_hash = sha256(canonical(actual_quality)).hexdigest()
        if (actual_quality != expected_quality or quality["check_set_sha256"] != expected_quality_hash or
                document["eligibility"]["quality_decision_sha256"] != expected_quality_hash or any(
                    set(check) != {"check_id", "status", "evidence_sha256"} or
                    check["status"] != "passed" or not _HASH64(check["evidence_sha256"])
                    for check in actual_quality)):
            raise AmbiguousSelection("quality check set/digest is not exact for selected parser pipeline")
        selected_accession = document["filing"]["accession"]
        for edge in document["relationships"]:
            if (edge.get("status") != "accepted" or selected_accession not in {
                    edge.get("predecessor_accession"), edge.get("successor_accession")} or
                    edge.get("evidence_document_id") not in document_ids):
                raise AmbiguousSelection("detached or unaccepted filing relationship in snapshot")
        selected_source_ids = {row["source_concept"]["id"] for row in document["items"]}
        for edge in document["equivalences"]:
            if edge.get("status") != "accepted" or not selected_source_ids & {
                    edge.get("left_source_concept_id"), edge.get("right_source_concept_id")}:
                raise AmbiguousSelection("detached or unaccepted concept equivalence in snapshot")
        closure = {key: value for key, value in document.items() if key != "closure_sha256"}
        document["closure_sha256"] = sha256(canonical(closure)).hexdigest()
        return document

def _HASH64(value: object) -> bool:
    return isinstance(value, str) and len(value) == 64 and all(c in "0123456789abcdef" for c in value)


def release_as_of(*, authority: CorporateAuthorityRef,
                  store: PostgresCorporateAuthorityStore) -> Mapping[str, object]:
    """Resolve one complete point-in-time authority solely through PostgreSQL."""
    if type(store) is not PostgresCorporateAuthorityStore:
        raise TypeError("a concrete PostgreSQL authority store is required")
    return store.resolve(authority)
