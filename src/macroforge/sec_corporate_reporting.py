"""SEC filing-instance normalization for the bounded Corporate Reporting slice.

The parser intentionally consumes SEC-rendered XBRL instances, not Inline XBRL.  It
uses expanded names, filing/DTS identity and canonical fingerprints throughout;
source context/unit aliases are retained only as evidence.
"""
from __future__ import annotations

from dataclasses import dataclass
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
from typing import Any, Mapping
import xml.etree.ElementTree as ET

XBRLI = "http://www.xbrl.org/2003/instance"
XBRLDI = "http://xbrl.org/2006/xbrldi"
XML = "http://www.w3.org/XML/1998/namespace"
XSI = "http://www.w3.org/2001/XMLSchema-instance"
XSD = "http://www.w3.org/2001/XMLSchema"


class ParserInvariantError(ValueError):
    pass


class ManifestError(ValueError):
    pass


def _canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def _digest(value: Any) -> str:
    return sha256(_canonical(value)).hexdigest()


def _parse_with_namespace_scopes(
    path: Path,
) -> tuple[ET.Element, dict[int, Mapping[str, str]]]:
    """Parse XML while retaining the namespace bindings in scope per element.

    ElementTree expands element and attribute names but discards the lexical
    namespace declarations needed to interpret QName-valued text/attributes.
    A document-wide prefix map is incorrect because prefixes may be rebound on
    any descendant or independently in sibling subtrees.
    """
    scopes: dict[int, Mapping[str, str]] = {}
    scope_stack: list[dict[str, str]] = []
    pending: list[tuple[str, str]] = []
    root: ET.Element | None = None
    for event, value in ET.iterparse(path, events=("start-ns", "start", "end")):
        if event == "start-ns":
            prefix, uri = value
            pending.append((prefix or "", uri))
        elif event == "start":
            element = value
            scope = dict(scope_stack[-1]) if scope_stack else {}
            for prefix, uri in pending:
                if uri:
                    scope[prefix] = uri
                else:
                    scope.pop(prefix, None)
            pending.clear()
            scope_stack.append(scope)
            scopes[id(element)] = scope
            if root is None:
                root = element
        else:
            scope_stack.pop()
    if root is None:
        raise ParserInvariantError("empty XML instance")
    return root, scopes


def _qname(text: str, ns: Mapping[str, str]) -> str:
    text = text.strip()
    if text.startswith("{"):
        return text
    if ":" in text:
        prefix, local = text.split(":", 1)
        if prefix not in ns:
            raise ParserInvariantError(f"unbound QName prefix: {prefix}")
        return f"{{{ns[prefix]}}}{local}"
    if "" not in ns:
        raise ParserInvariantError(f"unbound QName: {text}")
    return f"{{{ns['']}}}{text}"


def _canonical_xml(
    element: ET.Element,
    namespace_scopes: Mapping[int, Mapping[str, str]] | None = None,
) -> str:
    """Return prefix/attribute-order independent XML identity.

    V1 excludes comments and strips text at element boundaries while preserving
    internal text. Namespace prefixes are rewritten deterministically.
    """
    # XML C14N cannot know that an attribute's *value* is a QName.  Expand the
    # QName-valued attributes consumed by this bounded parser while leaving
    # arbitrary colon-containing strings untouched.  Work on a copy so neither
    # the parsed evidence tree nor the preserved filing-document bytes change.
    canonical = deepcopy(element)
    xsi_type = f"{{{XSI}}}type"
    for source, copy in zip(element.iter(), canonical.iter(), strict=True):
        qname_attributes = [xsi_type] if xsi_type in copy.attrib else []
        if source.tag == f"{{{XSD}}}element":
            qname_attributes.extend(
                name for name in ("type", "substitutionGroup") if name in copy.attrib
            )
        if qname_attributes:
            if namespace_scopes is None or id(source) not in namespace_scopes:
                raise ParserInvariantError("QName attribute requires namespace bindings")
            for name in qname_attributes:
                copy.attrib[name] = _qname(
                    copy.attrib[name], namespace_scopes[id(source)],
                )
    xml = ET.tostring(canonical, encoding="unicode", short_empty_elements=True)
    return ET.canonicalize(xml_data=xml, with_comments=False, strip_text=True,
                           rewrite_prefixes=True)


@dataclass(frozen=True)
class Dimension:
    location: str
    axis: str
    member_kind: str
    member: str | None = None
    typed_member_canonical_xml: str | None = None
    typed_member_sha256: str | None = None

    def semantic(self) -> tuple[Any, ...]:
        return (self.location, self.axis, self.member_kind, self.member,
                self.typed_member_sha256)


@dataclass(frozen=True)
class Context:
    source_id: str
    entity_scheme: str
    entity_value: str
    period: tuple[str, ...]
    dimensions: tuple[Dimension, ...]
    raw_xml_sha256: str
    semantic_hash: str

    def correspondence(self) -> tuple[Any, ...]:
        return (self.entity_scheme, self.entity_value, self.period,
                tuple(d.semantic() for d in self.dimensions))


@dataclass(frozen=True)
class Unit:
    source_id: str
    numerator: tuple[str, ...]
    denominator: tuple[str, ...]
    raw_xml_sha256: str
    semantic_hash: str


@dataclass(frozen=True)
class Occurrence:
    source_ordinal: int
    concept: str
    context_ref: str
    unit_ref: str | None
    xml_lang: str | None
    lexical_value: str
    nil: bool
    decimals: str | None
    precision: str | None
    occurrence_sha256: str

    @property
    def value_fingerprint(self) -> str:
        return _digest({"nil": self.nil, "value": self.lexical_value})


@dataclass
class SemanticSlot:
    slot_sha256: str
    correspondence_key: tuple[Any, ...]
    occurrences: list[Occurrence]
    status: str = "deferred"
    selected_occurrence: Occurrence | None = None


@dataclass(frozen=True)
class Drift:
    status: str
    changed_metrics: tuple[str, ...]


@dataclass
class ParserReport:
    accession: str
    dts_manifest_sha256: str
    source_sha256: str
    contexts: dict[str, Context]
    units: dict[str, Unit]
    occurrences: list[Occurrence]
    slots: dict[str, SemanticSlot]
    metrics: dict[str, int]
    parser_output_sha256: str

    @property
    def computed_parser_output_sha256(self) -> str:
        """Recompute output identity so a replaced digest cannot forge a report."""
        output = [
            {"slot": slot.slot_sha256, "status": slot.status,
             "occurrences": [occurrence.occurrence_sha256 for occurrence in slot.occurrences]}
            for slot in sorted(self.slots.values(), key=lambda value: value.slot_sha256)
        ]
        return _digest(output)

    @property
    def canonical_metrics_bytes(self) -> bytes:
        return _canonical(self.metrics)

    @property
    def metrics_sha256(self) -> str:
        return sha256(self.canonical_metrics_bytes).hexdigest()

    def classify_drift(self, baseline: Mapping[str, int]) -> Drift:
        changed = tuple(sorted(k for k in set(self.metrics) | set(baseline)
                               if self.metrics.get(k) != baseline.get(k)))
        structural = {"conflicting_slot_count"}
        if any(k in structural and self.metrics.get(k, 0) > baseline.get(k, 0) for k in changed):
            return Drift("block", changed)
        return Drift("review" if changed else "match", changed)


@dataclass(frozen=True)
class VerifiedManifest:
    record_count: int
    filing_chain_count: int
    filing_document_count: int


@dataclass(frozen=True)
class FilingComparison:
    common_slots: int
    original_only: int
    amendment_only: int
    changed_common: int
    representative_changes: dict[str, tuple[str, str]]


def _parse_context(
    element: ET.Element,
    namespace_scopes: Mapping[int, Mapping[str, str]],
) -> Context:
    source_id = element.attrib["id"]
    identifier = element.find(f".//{{{XBRLI}}}identifier")
    if identifier is None or identifier.text is None:
        raise ParserInvariantError(f"context {source_id} lacks entity identifier")
    period_el = element.find(f"{{{XBRLI}}}period")
    if period_el is None:
        raise ParserInvariantError(f"context {source_id} lacks period")
    instant = period_el.find(f"{{{XBRLI}}}instant")
    start = period_el.find(f"{{{XBRLI}}}startDate")
    end = period_el.find(f"{{{XBRLI}}}endDate")
    forever = period_el.find(f"{{{XBRLI}}}forever")
    if instant is not None and instant.text and start is None and end is None and forever is None:
        period = ("instant", instant.text.strip())
    elif start is not None and start.text and end is not None and end.text and instant is None and forever is None:
        period = ("duration", start.text.strip(), end.text.strip())
    elif forever is not None and instant is None and start is None and end is None:
        period = ("forever",)
    else:
        raise ParserInvariantError(f"context {source_id} has invalid period")
    dimensions: list[Dimension] = []
    for location in ("segment", "scenario"):
        holder = element.find(f".//{{{XBRLI}}}{location}")
        if holder is None:
            continue
        for member in list(holder):
            if member.tag == f"{{{XBRLDI}}}explicitMember":
                member_scope = namespace_scopes[id(member)]
                dimensions.append(Dimension(
                    location, _qname(member.attrib["dimension"], member_scope),
                    "explicit", _qname(member.text or "", member_scope),
                ))
            elif member.tag == f"{{{XBRLDI}}}typedMember":
                children = list(member)
                if len(children) != 1:
                    raise ParserInvariantError("typedMember must contain exactly one value element")
                typed_xml = _canonical_xml(children[0], namespace_scopes)
                typed_hash = sha256(typed_xml.encode()).hexdigest()
                dimensions.append(Dimension(location, _qname(
                                                member.attrib["dimension"],
                                                namespace_scopes[id(member)]),
                                            "typed", typed_member_canonical_xml=typed_xml,
                                            typed_member_sha256=typed_hash))
            else:
                raise ParserInvariantError(f"unsupported dimensional child {member.tag}")
    dimensions.sort(key=lambda d: d.semantic())
    keys = [d.semantic()[:3] for d in dimensions]
    if len(keys) != len(set(keys)):
        raise ParserInvariantError(f"context {source_id} repeats a dimension")
    raw = ET.tostring(element, encoding="utf-8")
    semantic = (identifier.attrib.get("scheme", ""), identifier.text.strip(), period,
                tuple(d.semantic() for d in dimensions))
    return Context(source_id, identifier.attrib.get("scheme", ""), identifier.text.strip(),
                   period, tuple(dimensions), sha256(raw).hexdigest(), _digest(semantic))


def _parse_unit(
    element: ET.Element,
    namespace_scopes: Mapping[int, Mapping[str, str]],
) -> Unit:
    source_id = element.attrib["id"]
    direct = element.findall(f"{{{XBRLI}}}measure")
    divide = element.find(f"{{{XBRLI}}}divide")
    if direct and divide is not None:
        raise ParserInvariantError("unit cannot contain measures and divide")
    if direct:
        numerator = tuple(sorted(
            _qname(m.text or "", namespace_scopes[id(m)]) for m in direct
        ))
        denominator: tuple[str, ...] = ()
    elif divide is not None:
        num_holder = divide.find(f"{{{XBRLI}}}unitNumerator")
        den_holder = divide.find(f"{{{XBRLI}}}unitDenominator")
        if num_holder is None or den_holder is None:
            raise ParserInvariantError("divide requires numerator and denominator")
        nums = num_holder.findall(f"{{{XBRLI}}}measure")
        dens = den_holder.findall(f"{{{XBRLI}}}measure")
        if not nums or not dens or len(list(num_holder)) != len(nums) or len(list(den_holder)) != len(dens):
            raise ParserInvariantError("divide requires only non-empty measure lists")
        numerator = tuple(sorted(
            _qname(m.text or "", namespace_scopes[id(m)]) for m in nums
        ))
        denominator = tuple(sorted(
            _qname(m.text or "", namespace_scopes[id(m)]) for m in dens
        ))
    else:
        raise ParserInvariantError(f"unit {source_id} has no valid measure semantics")
    raw = ET.tostring(element, encoding="utf-8")
    return Unit(source_id, numerator, denominator, sha256(raw).hexdigest(),
                _digest({"numerator": numerator, "denominator": denominator}))


def parse_instance(path: str | Path, *, accession: str, dts_manifest_sha256: str) -> ParserReport:
    path = Path(path)
    root, namespace_scopes = _parse_with_namespace_scopes(path)
    contexts = {e.attrib["id"]: _parse_context(e, namespace_scopes)
                for e in root.findall(f"{{{XBRLI}}}context")}
    units = {e.attrib["id"]: _parse_unit(e, namespace_scopes)
             for e in root.findall(f"{{{XBRLI}}}unit")}
    occurrences: list[Occurrence] = []
    slots: dict[str, SemanticSlot] = {}
    for child in list(root):
        if "contextRef" not in child.attrib:
            continue
        ordinal = len(occurrences) + 1
        context_ref = child.attrib["contextRef"]
        unit_ref = child.attrib.get("unitRef")
        if context_ref not in contexts:
            raise ParserInvariantError(f"fact references unknown context {context_ref}")
        if unit_ref is not None and unit_ref not in units:
            raise ParserInvariantError(f"fact references unknown unit {unit_ref}")
        lexical = "".join(child.itertext()).strip()
        nil = child.attrib.get("{http://www.w3.org/2001/XMLSchema-instance}nil", "false").lower() in ("1", "true")
        lang = child.attrib.get(f"{{{XML}}}lang")
        concept = child.tag
        occ_data = {"ordinal": ordinal, "concept": concept, "context": context_ref,
                    "unit": unit_ref, "lang": lang, "value": lexical, "nil": nil,
                    "decimals": child.attrib.get("decimals"), "precision": child.attrib.get("precision")}
        occurrence = Occurrence(ordinal, concept, context_ref, unit_ref, lang, lexical, nil,
                                child.attrib.get("decimals"), child.attrib.get("precision"), _digest(occ_data))
        occurrences.append(occurrence)
        context = contexts[context_ref]
        unit_hash = units[unit_ref].semantic_hash if unit_ref else None
        correspondence = (concept, context.correspondence(), unit_hash, lang)
        slot_hash = _digest({"accession": accession, "dts": dts_manifest_sha256,
                             "correspondence": correspondence})
        slots.setdefault(slot_hash, SemanticSlot(slot_hash, correspondence, [])).occurrences.append(occurrence)
    for slot in slots.values():
        values = {o.value_fingerprint for o in slot.occurrences}
        if len(values) == 1:
            slot.status = "accepted_identical"
            slot.selected_occurrence = min(slot.occurrences, key=lambda o: (o.occurrence_sha256, o.source_ordinal))
        else:
            slot.status = "conflict"
            slot.selected_occurrence = None
    metrics = {
        "context_count": len(contexts),
        "instant_context_count": sum(c.period[0] == "instant" for c in contexts.values()),
        "duration_context_count": sum(c.period[0] == "duration" for c in contexts.values()),
        "dimensioned_context_count": sum(bool(c.dimensions) for c in contexts.values()),
        "typed_member_count": sum(d.member_kind == "typed" for c in contexts.values() for d in c.dimensions),
        "unit_count": len(units), "fact_count": len(occurrences), "semantic_slot_count": len(slots),
        "duplicate_slot_count": sum(len(s.occurrences) > 1 for s in slots.values()),
        "duplicate_occurrence_excess": sum(len(s.occurrences) - 1 for s in slots.values()),
        "conflicting_slot_count": sum(s.status == "conflict" for s in slots.values()),
    }
    output = [{"slot": s.slot_sha256, "status": s.status,
               "occurrences": [o.occurrence_sha256 for o in s.occurrences]} for s in sorted(slots.values(), key=lambda x: x.slot_sha256)]
    return ParserReport(accession, dts_manifest_sha256, sha256(path.read_bytes()).hexdigest(),
                        contexts, units, occurrences, slots, metrics, _digest(output))


def validate_protected_manifest(root: str | Path, manifest_path: str | Path) -> VerifiedManifest:
    root, manifest_path = Path(root), Path(manifest_path)
    data = json.loads(manifest_path.read_text())
    records = data.get("records")
    if not isinstance(records, list) or not records:
        raise ManifestError("manifest records missing")
    for record in records:
        path = root / record["path"]
        if not path.is_file():
            raise ManifestError(f"missing protected artifact: {record['path']}")
        payload = path.read_bytes()
        if len(payload) != record["bytes"]:
            raise ManifestError(f"byte length mismatch: {record['path']}")
        if sha256(payload).hexdigest() != record["sha256"]:
            raise ManifestError(f"sha256 mismatch: {record['path']}")
    filing_docs = [r for r in records if r.get("accession") and r.get("archive_index_member") is True]
    for record in filing_docs:
        index_name = "original-index.json" if record["accession"].endswith("034448") else "amendment-index.json"
        index = json.loads((root / index_name).read_text())
        members = {item["name"]: int(item["size"]) for item in index["directory"]["item"]
                   if str(item.get("size", "")).strip()}
        name = Path(record["path"]).name
        if members.get(name) != record["bytes"]:
            raise ManifestError(f"archive membership mismatch: {record['path']}")
    return VerifiedManifest(len(records), sum(r.get("category") == "filing_chain" for r in records), len(filing_docs))


def compare_filings(original: ParserReport, amendment: ParserReport, *, allow_qname_correspondence: bool = False) -> FilingComparison:
    if not allow_qname_correspondence and original.dts_manifest_sha256 != amendment.dts_manifest_sha256:
        raise ParserInvariantError("cross-DTS QName correspondence requires explicit equivalence")
    def keyed(report: ParserReport) -> dict[tuple[Any, ...], SemanticSlot]:
        return {s.correspondence_key: s for s in report.slots.values()}
    left, right = keyed(original), keyed(amendment)
    common = set(left) & set(right)
    changed: dict[str, tuple[str, str]] = {}
    changed_count = 0
    wanted = {"Assets", "EarningsPerShareDiluted", "ImpairmentOfInvestmentInAffiliates", "AmendmentFlag"}
    for key in common:
        a, b = left[key].selected_occurrence, right[key].selected_occurrence
        if a and b and a.value_fingerprint != b.value_fingerprint:
            changed_count += 1
            local = key[0].split("}")[-1]
            # Representative unqualified Assets is the consolidated (dimensionless) slot.
            dimensions = key[1][3]
            if local in wanted and (local != "Assets" or not dimensions):
                changed[local] = (a.lexical_value, b.lexical_value)
    return FilingComparison(len(common), len(set(left) - set(right)), len(set(right) - set(left)), changed_count, changed)


def parse_extension_schema(path: str | Path) -> list[dict[str, Any]]:
    """Parse only locally declared extension elements; imported taxonomy metadata stays unresolved."""
    path = Path(path)
    root, namespace_scopes = _parse_with_namespace_scopes(path)
    xsd = XSD
    target = root.attrib.get("targetNamespace", "")
    result = []
    for element in root.findall(f"{{{xsd}}}element"):
        element_scope = namespace_scopes[id(element)]
        result.append({"namespace_uri": target, "local_name": element.attrib["name"],
                       "declaration_sha256": sha256(
                           _canonical_xml(element, namespace_scopes).encode()
                       ).hexdigest(),
                       "data_type_qname": (_qname(element.attrib["type"], element_scope)
                                           if "type" in element.attrib else None),
                       "substitution_group_qname": (_qname(
                           element.attrib["substitutionGroup"], element_scope)
                           if "substitutionGroup" in element.attrib else None),
                       "period_type": element.attrib.get("{http://www.xbrl.org/2003/instance}periodType"),
                       "balance": element.attrib.get("{http://www.xbrl.org/2003/instance}balance"),
                       "abstract": element.attrib.get("abstract") == "true",
                       "nillable": element.attrib.get("nillable") == "true"})
    return result
