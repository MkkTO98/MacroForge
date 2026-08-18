"""Source-specific Corporate Portfolio v1 manifest and package validator.

This module is deliberately bounded to the fifteen TASK-222 issuers, issuer
fiscal years 2021--2025, and SEC 10-K/10-Q filing acts.  It does not ingest
PostgreSQL data, accept mappings, decide restatements, or create releases.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
import re
from typing import Any, Callable, Iterable, Mapping
from urllib.parse import urljoin, urlparse, urldefrag
import xml.etree.ElementTree as ET

ACCEPTANCE_LOWER_BOUND = "2020-01-01T00:00:00Z"
ACCEPTANCE_CUTOFF = "2026-06-30T23:59:59Z"
FISCAL_YEARS = tuple(range(2021, 2026))
FISCAL_PERIODS = ("Q1", "Q2", "Q3", "FY")
ALLOWED_FORMS = frozenset({"10-K", "10-Q", "10-K/A", "10-Q/A"})
_SEC_ACQUISITION_HOSTS = frozenset({"data.sec.gov", "www.sec.gov"})
_STANDARD_TAXONOMY_HOSTS = frozenset({"xbrl.fasb.org", "xbrl.sec.gov", "xbrl.org", "www.xbrl.org"})
TERMINAL_OUTCOMES = frozenset(
    {
        "compatible",
        "acquisition failure",
        "metadata discrepancy",
        "missing package component",
        "package-role ambiguity",
        "unsupported traditional XBRL",
        "unsupported Inline XBRL",
        "unresolved external dependency",
        "malformed package",
        "explicit governed exclusion",
    }
)

ISSUERS: tuple[dict[str, str], ...] = (
    {"issuer": "ExxonMobil", "cik": "0000034088"},
    {"issuer": "Chevron", "cik": "0000093410"},
    {"issuer": "ConocoPhillips", "cik": "0001163165"},
    {"issuer": "Occidental", "cik": "0000797468"},
    {"issuer": "EOG Resources", "cik": "0000821189"},
    {"issuer": "SLB", "cik": "0000087347"},
    {"issuer": "Halliburton", "cik": "0000045012"},
    {"issuer": "Cheniere Energy", "cik": "0000003570"},
    {"issuer": "Kinder Morgan", "cik": "0001506307"},
    {"issuer": "Freeport-McMoRan", "cik": "0000831259"},
    {"issuer": "Newmont", "cik": "0001164727"},
    {"issuer": "Albemarle", "cik": "0000915913"},
    {"issuer": "Gatos Silver", "cik": "0001517006"},
    {"issuer": "Marathon Oil", "cik": "0000101778"},
    {"issuer": "Cal-Maine Foods", "cik": "0000016160"},
)
ISSUER_BY_CIK = {row["cik"]: row["issuer"] for row in ISSUERS}

FROZEN_EXPECTATIONS = {
    "expected_original_slots": 300,
    "observed_originals": 290,
    "cessation_absences": 10,
    "observed_amendments": 21,
    "observed_filing_acts": 311,
}

CESSATION_EVIDENCE: dict[str, dict[str, str]] = {
    "0001517006": {
        "kind": "acquisition_cessation",
        "accession": "0001193125-25-007425",
        "accepted_at": "2025-01-16T08:36:13.000Z",
        "url": "https://www.sec.gov/Archives/edgar/data/1517006/000119312525007425/d871159d8k.htm",
        "description": "Gatos Silver acquisition closing 8-K; reporting ceased after FY2024 Q3.",
    },
    "0000101778": {
        "kind": "acquisition_cessation",
        "accession": "0001104659-24-122113",
        "accepted_at": "2024-11-22T16:23:38.000Z",
        "url": "https://www.sec.gov/Archives/edgar/data/101778/000110465924122113/tm2428994d1_8k.htm",
        "description": "Marathon Oil acquisition closing 8-K; reporting ceased after FY2024 Q3.",
    },
}
_CESSATION_SLOTS = {
    (cik, 2024, "FY") for cik in CESSATION_EVIDENCE
} | {
    (cik, 2025, period) for cik in CESSATION_EVIDENCE for period in FISCAL_PERIODS
}


@dataclass(frozen=True)
class PackageLimits:
    """Deterministic dependency-closure limits."""

    max_documents: int = 96
    max_external_documents: int = 64
    max_depth: int = 12
    max_total_bytes: int = 256 * 1024 * 1024

    def __post_init__(self) -> None:
        if (
            self.max_documents < 1
            or self.max_external_documents < 0
            or self.max_depth < 0
            or self.max_total_bytes < 1
        ):
            raise ValueError("package limits must be positive")


def _canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def canonical_manifest_identity(value: Mapping[str, Any]) -> str:
    """Return identity without trusting self-reported identity fields."""

    payload = {key: item for key, item in value.items() if key not in {"canonical_json", "manifest_sha256"}}
    return sha256(_canonical_json(payload).encode()).hexdigest()


def _finish(payload: dict[str, Any]) -> dict[str, Any]:
    canonical = _canonical_json(payload)
    return {**payload, "canonical_json": canonical, "manifest_sha256": sha256(canonical.encode()).hexdigest()}


def enrich_package_result(
    result: Mapping[str, Any],
    filing_act: Mapping[str, Any],
    index_retrieval_evidence: Mapping[str, Any] | None,
) -> dict[str, Any]:
    """Attach portfolio linkage and re-identify the exact enriched package record."""

    payload = {key: item for key, item in result.items() if key not in {"canonical_json", "manifest_sha256"}}
    payload.update(
        {
            "slot_id": f'{filing_act["cik"]}:{filing_act["issuer_fiscal_year"]}:{filing_act["fiscal_period"]}',
            "is_amendment": bool(filing_act["is_amendment"]),
            "relationship_proposal": filing_act.get("relationship_proposal"),
            "index_retrieval_evidence": index_retrieval_evidence,
        }
    )
    payload["manifest_sha256"] = canonical_manifest_identity(payload)
    return payload


def build_expected_original_slots() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for issuer in ISSUERS:
        for year in FISCAL_YEARS:
            for period in FISCAL_PERIODS:
                form = "10-K" if period == "FY" else "10-Q"
                calendar_kind = "52_53_week" if issuer["cik"] == "0000016160" else "calendar_year"
                rows.append(
                    {
                        "slot_id": f'{issuer["cik"]}:{year}:{period}',
                        "issuer": issuer["issuer"],
                        "cik": issuer["cik"],
                        "issuer_fiscal_year": year,
                        "fiscal_period": period,
                        "expected_form": form,
                        "acceptance_cutoff": ACCEPTANCE_CUTOFF,
                        "fiscal_calendar": calendar_kind,
                    }
                )
    return rows


def _fiscal_coordinates(cik: str, form: str, report_date: str) -> tuple[int, str, dict[str, str]] | None:
    try:
        year, month, _day = (int(part) for part in report_date.split("-"))
    except (TypeError, ValueError):
        return None
    base_form = form.removesuffix("/A")
    if base_form not in {"10-K", "10-Q"}:
        return None
    if cik == "0000016160":
        if base_form == "10-K" and month in {5, 6}:
            fiscal_year, period = year, "FY"
        elif base_form == "10-Q" and month in {8, 9}:
            fiscal_year, period = year + 1, "Q1"
        elif base_form == "10-Q" and month in {11, 12}:
            fiscal_year, period = year + 1, "Q2"
        elif base_form == "10-Q" and month in {2, 3}:
            fiscal_year, period = year, "Q3"
        else:
            return None
        evidence = {
            "calendar_kind": "52_53_week",
            "derivation": "cal_maine_authored_rule",
            "report_date": report_date,
            "basis": "issuer fiscal year ending near late May/early June; quarter ends vary by 52/53-week calendar",
        }
    else:
        if base_form == "10-K":
            fiscal_year, period = year, "FY"
        elif month in {3, 4}:
            fiscal_year, period = year, "Q1"
        elif month in {6, 7}:
            fiscal_year, period = year, "Q2"
        elif month in {9, 10}:
            fiscal_year, period = year, "Q3"
        else:
            return None
        evidence = {
            "calendar_kind": "calendar_year",
            "derivation": "report_date_month",
            "report_date": report_date,
            "basis": "calendar-year issuer form/report-date classification",
        }
    return fiscal_year, period, evidence


def _normalize_acceptance(value: Any) -> str:
    text = str(value or "")
    return text if text.endswith("Z") else text + ("Z" if text else "")


def _base_filing_record(row: Mapping[str, Any], fiscal_year: int, period: str, evidence: dict[str, str]) -> dict[str, Any]:
    form = str(row["form"])
    is_amendment = form.endswith("/A")
    return {
        "accession": str(row["accessionNumber"]),
        "issuer": ISSUER_BY_CIK[str(row["cik"])],
        "cik": str(row["cik"]),
        "form": form,
        "base_form": form.removesuffix("/A"),
        "is_amendment": is_amendment,
        "report_date": str(row["reportDate"]),
        "filing_date": str(row.get("filingDate") or ""),
        "accepted_at": _normalize_acceptance(row.get("acceptanceDateTime")),
        "primary_document": str(row.get("primaryDocument") or ""),
        "primary_document_description": str(row.get("primaryDocDescription") or ""),
        "is_xbrl": bool(int(row.get("isXBRL") or 0)),
        "is_inline_xbrl": bool(int(row.get("isInlineXBRL") or 0)),
        "issuer_fiscal_year": fiscal_year,
        "fiscal_period": period,
        "fiscal_calendar_evidence": evidence,
    }


def build_portfolio_manifest(submission_rows: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    """Build the exact bounded accession/disposition ledger from SEC submissions rows."""

    filings: list[dict[str, Any]] = []
    discrepancies: list[dict[str, Any]] = []
    seen_accessions: set[str] = set()
    for raw in submission_rows:
        cik = str(raw.get("cik") or "").zfill(10)
        form = str(raw.get("form") or "")
        accession = str(raw.get("accessionNumber") or "")
        accepted_at = _normalize_acceptance(raw.get("acceptanceDateTime"))
        if cik not in ISSUER_BY_CIK or form not in ALLOWED_FORMS:
            continue
        # A historical malformed/blank report date is not an in-scope corpus
        # discrepancy merely because the submissions history retains it.
        if not accepted_at or accepted_at < ACCEPTANCE_LOWER_BOUND or accepted_at > ACCEPTANCE_CUTOFF:
            continue
        if accession in seen_accessions:
            discrepancies.append(
                {
                    "classification": "metadata_discrepancy",
                    "code": "duplicate_accession",
                    "accession": accession,
                }
            )
            continue
        coordinates = _fiscal_coordinates(cik, form, str(raw.get("reportDate") or ""))
        if coordinates is None:
            discrepancies.append(
                {
                    "classification": "metadata_discrepancy",
                    "code": "unclassified_fiscal_coordinates",
                    "cik": cik,
                    "accession": accession,
                }
            )
            continue
        year, period, evidence = coordinates
        if year not in FISCAL_YEARS:
            continue
        seen_accessions.add(accession)
        filings.append(_base_filing_record({**raw, "cik": cik}, year, period, evidence))

    filings.sort(key=lambda item: (item["cik"], item["issuer_fiscal_year"], FISCAL_PERIODS.index(item["fiscal_period"]), item["accepted_at"], item["accession"]))
    originals = [item for item in filings if not item["is_amendment"]]
    amendments = [item for item in filings if item["is_amendment"]]
    original_by_slot: dict[tuple[str, int, str], list[dict[str, Any]]] = {}
    for item in originals:
        original_by_slot.setdefault((item["cik"], item["issuer_fiscal_year"], item["fiscal_period"]), []).append(item)

    slot_ledger: list[dict[str, Any]] = []
    for expected in build_expected_original_slots():
        key = (expected["cik"], expected["issuer_fiscal_year"], expected["fiscal_period"])
        candidates = original_by_slot.get(key, [])
        row = dict(expected)
        if len(candidates) == 1:
            original = candidates[0]
            row.update(
                {
                    "disposition": "observed_original",
                    "accession": original["accession"],
                    "accepted_at": original["accepted_at"],
                    "report_date": original["report_date"],
                    "fiscal_calendar_evidence": original["fiscal_calendar_evidence"],
                }
            )
        elif not candidates and key in _CESSATION_SLOTS:
            row.update(
                {
                    "disposition": "acquisition_cessation_absence",
                    "accession": None,
                    "cessation_evidence": dict(CESSATION_EVIDENCE[expected["cik"]]),
                }
            )
        else:
            row.update({"disposition": "metadata_discrepancy", "accession": None})
            discrepancies.append(
                {
                    "classification": "metadata_discrepancy",
                    "code": "missing_original" if not candidates else "multiple_originals_for_slot",
                    "slot_id": expected["slot_id"],
                    "accessions": [candidate["accession"] for candidate in candidates],
                }
            )
        slot_ledger.append(row)

    for amendment in amendments:
        key = (amendment["cik"], amendment["issuer_fiscal_year"], amendment["fiscal_period"])
        candidates = [
            candidate
            for candidate in original_by_slot.get(key, [])
            if candidate["base_form"] == amendment["base_form"]
            and candidate["report_date"] == amendment["report_date"]
        ]
        amendment["amendment_scope"] = "full_xbrl_package" if amendment["is_xbrl"] else "cover_only_or_partial"
        amendment["relationship_proposal"] = {
            "original_accession": candidates[0]["accession"] if len(candidates) == 1 else None,
            "basis": "same_cik_base_form_report_date_and_fiscal_slot",
            "restatement_status": "undetermined",
            "authoritative": False,
        }
        if len(candidates) != 1:
            discrepancies.append(
                {
                    "classification": "metadata_discrepancy",
                    "code": "amendment_original_ambiguous",
                    "accession": amendment["accession"],
                    "candidate_originals": [candidate["accession"] for candidate in candidates],
                }
            )

    filing_acts = sorted(originals + amendments, key=lambda item: (item["accepted_at"], item["accession"]))
    counts = {
        "expected_original_slots": len(slot_ledger),
        "observed_originals": len(originals),
        "cessation_absences": sum(item["disposition"] == "acquisition_cessation_absence" for item in slot_ledger),
        "observed_amendments": len(amendments),
        "observed_filing_acts": len(filing_acts),
    }
    for key, expected in FROZEN_EXPECTATIONS.items():
        if counts[key] != expected:
            discrepancies.append(
                {
                    "classification": "metadata_discrepancy",
                    "code": "frozen_count_mismatch",
                    "field": key,
                    "expected": expected,
                    "observed": counts[key],
                }
            )
    payload = {
        "schema": "macroforge.corporate-portfolio-v1.accession-disposition.v1",
        "source_authority": ["SEC submissions metadata", "EDGAR filing indexes", "EDGAR filing/package documents and referenced DTS dependencies"],
        "company_facts_authority": False,
        "acceptance_cutoff": ACCEPTANCE_CUTOFF,
        "frozen_expectations": dict(FROZEN_EXPECTATIONS),
        "counts": counts,
        "corpus_accepted": not discrepancies and counts == FROZEN_EXPECTATIONS,
        "expected_original_slots": slot_ledger,
        "filing_acts": filing_acts,
        "discrepancies": discrepancies,
    }
    return _finish(payload)


def _filing_base_url(filing: Mapping[str, Any]) -> str:
    cik = str(int(str(filing["cik"])))
    accession = str(filing["accessionNumber"]).replace("-", "")
    return f"https://www.sec.gov/Archives/edgar/data/{cik}/{accession}/"


def _index_names(index: Mapping[str, Any]) -> list[str]:
    try:
        items = index["directory"]["item"]
    except (KeyError, TypeError):
        return []
    names = [str(item.get("name") or "") for item in items if isinstance(item, Mapping)]
    return sorted(name for name in names if name and "/" not in name and "\\" not in name)


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _document_owner(url: str, filing_base: str) -> str:
    if url.startswith(filing_base):
        return "sec_filing"
    host = (urlparse(url).hostname or "").lower()
    if host.endswith("sec.gov"):
        return "sec_taxonomy"
    if host.endswith("fasb.org"):
        return "fasb_taxonomy"
    if host.endswith("xbrl.org"):
        return "xbrl_taxonomy"
    return "referenced_external_owner"


def _extract_references(root: ET.Element, current_url: str) -> list[tuple[str, str]]:
    references: set[tuple[str, str]] = set()
    for element in root.iter():
        local = _local_name(element.tag)
        for raw_key, raw_value in element.attrib.items():
            attr = _local_name(raw_key)
            mechanism: str | None = None
            if local in {"import", "include", "redefine"} and attr == "schemaLocation":
                mechanism = f"xsd:{local}"
            elif local in {"schemaRef", "linkbaseRef"} and attr == "href":
                mechanism = f"link:{local}"
            if mechanism is not None:
                value = str(raw_value).strip()
                if value:
                    resolved, _fragment = urldefrag(urljoin(current_url, value))
                    references.add((resolved, mechanism))
    return sorted(references)


def _classify_roles(url: str, root: ET.Element, filing_base: str, primary_url: str, inline: bool) -> list[str]:
    roles: set[str] = set()
    name = url.rsplit("/", 1)[-1].lower()
    local = _local_name(root.tag).lower()
    if url == primary_url:
        roles.add("primary_document")
    if inline and any("inlinexbrl" in str(element.tag).lower() for element in root.iter()):
        roles.add("inline_instance")
    if local == "xbrl":
        roles.add("instance_document")
    if local == "schema":
        roles.add("extension_schema" if url.startswith(filing_base) else "external_taxonomy_dependency")
    if local == "linkbase":
        suffix_roles = {
            "_cal": "calculation_linkbase",
            "_pre": "presentation_linkbase",
            "_def": "definition_linkbase",
            "_lab": "label_linkbase",
        }
        for marker, role in suffix_roles.items():
            if marker in name:
                roles.add(role)
        if not roles:
            children = {_local_name(element.tag) for element in root.iter()}
            for child, role in (
                ("calculationLink", "calculation_linkbase"),
                ("presentationLink", "presentation_linkbase"),
                ("definitionLink", "definition_linkbase"),
                ("labelLink", "label_linkbase"),
            ):
                if child in children:
                    roles.add(role)
    if not url.startswith(filing_base) and not roles:
        roles.add("external_taxonomy_dependency")
    return sorted(roles)


def _fact_features(root: ET.Element, *, inline: bool) -> dict[str, Any]:
    keys: dict[tuple[str, str, str], set[str]] = {}
    key_counts: dict[tuple[str, str, str], int] = {}
    units: set[str] = set()
    scale = False
    sign = False
    dimensions = False
    typed_members = False
    for element in root.iter():
        local_name = str(element.tag).rsplit("}", 1)[-1].lower()
        attributes = {str(key).rsplit("}", 1)[-1].lower(): value for key, value in element.attrib.items()}
        dimensions = dimensions or local_name in {"explicitmember", "typedmember"}
        typed_members = typed_members or local_name == "typedmember"
        if inline:
            if local_name not in {"nonfraction", "nonnumeric"}:
                continue
            fact_name = attributes.get("name", "")
        else:
            if "contextref" not in attributes:
                continue
            fact_name = str(element.tag)
        key = (fact_name, attributes.get("contextref", ""), attributes.get("unitref", ""))
        value = "".join(element.itertext()).strip()
        keys.setdefault(key, set()).add(value)
        key_counts[key] = key_counts.get(key, 0) + 1
        if attributes.get("unitref"):
            units.add(attributes["unitref"])
        if inline:
            scale = scale or "scale" in attributes
            sign = sign or "sign" in attributes
    return {
        "dimensions": dimensions,
        "typed_members": typed_members,
        "units": sorted(units),
        "inline_scale": scale,
        "inline_sign": sign,
        "duplicate_fact_keys": any(count > 1 for count in key_counts.values()),
        "conflicting_duplicate_values": any(len(values) > 1 for values in keys.values()),
    }


def acquisition_url_allowed(url: str) -> bool:
    """Confine acquisition to SEC endpoints and observed standard-taxonomy hosts."""

    try:
        parsed = urlparse(url)
        port = parsed.port
    except ValueError:
        return False
    if parsed.username or parsed.password or parsed.fragment or not parsed.hostname:
        return False
    host = parsed.hostname.lower()
    if host in _SEC_ACQUISITION_HOSTS:
        return parsed.scheme == "https" and port in {None, 443}
    if host in _STANDARD_TAXONOMY_HOSTS:
        if parsed.scheme == "http":
            return port in {None, 80}
        if parsed.scheme == "https":
            return port in {None, 443}
    return False


def validate_package(
    filing: Mapping[str, Any],
    index: Mapping[str, Any],
    fetch: Callable[[str], bytes],
    *,
    limits: PackageLimits = PackageLimits(),
    governed_exclusion: str | None = None,
) -> dict[str, Any]:
    """Inventory and validate one EDGAR package with deterministic closure.

    ``fetch`` is injected so authored tests are network-free and operational
    acquisition can keep provider bytes outside the repository.
    """

    accession = str(filing.get("accessionNumber") or "")
    base_payload: dict[str, Any] = {
        "schema": "macroforge.corporate-portfolio-v1.package-compatibility.v1",
        "accession": accession,
        "cik": str(filing.get("cik") or "").zfill(10),
        "form": str(filing.get("form") or ""),
        "xbrl_format": "inline" if bool(int(filing.get("isInlineXBRL") or 0)) else "traditional",
        "closure_rule": {
            "algorithm": "local_package_first_then_breadth_first_external_references",
            "reference_kinds": ["xsd:import", "xsd:include", "xsd:redefine", "link:schemaRef", "link:linkbaseRef"],
            "max_documents": limits.max_documents,
            "max_external_documents": limits.max_external_documents,
            "max_depth": limits.max_depth,
            "max_total_bytes": limits.max_total_bytes,
            "cycles": "classified_as_unresolved_external_dependency",
            "fetch_failure": "classified_as_acquisition_failure_or_unresolved_external_dependency",
        },
        "documents": [],
        "dependencies": [],
        "issues": [],
        "features": {
            "dimensions": False,
            "typed_members": False,
            "units": [],
            "inline_scale": False,
            "inline_sign": False,
            "duplicate_fact_keys": False,
            "conflicting_duplicate_values": False,
        },
    }
    if governed_exclusion:
        base_payload.update(
            {
                "outcome": "explicit governed exclusion",
                "issues": [{"code": "governed_exclusion", "detail": governed_exclusion}],
            }
        )
        return _finish(base_payload)
    if not bool(int(filing.get("isXBRL") or 0)):
        base_payload.update(
            {
                "outcome": "metadata discrepancy",
                "issues": [{"code": "submission_not_xbrl", "detail": "filing is in the portfolio but submissions metadata does not mark it XBRL"}],
            }
        )
        return _finish(base_payload)

    names = _index_names(index)
    primary_name = str(filing.get("primaryDocument") or "")
    if not names or not primary_name or primary_name not in names:
        base_payload.update(
            {
                "outcome": "missing package component",
                "issues": [{"code": "primary_document_missing", "detail": primary_name}],
            }
        )
        return _finish(base_payload)
    filing_base = _filing_base_url(filing)
    primary_url = urljoin(filing_base, primary_name)
    inline = base_payload["xbrl_format"] == "inline"

    # Inventory all local XML/XSD package components before spending the
    # separately bounded budget on external taxonomy closure.  This prevents
    # large shared taxonomies from hiding issuer linkbases.
    local_seed_urls = [primary_url]
    local_seed_urls.extend(
        urljoin(filing_base, name)
        for name in names
        if name.lower().endswith((".xml", ".xsd")) and name != primary_name
    )
    local_seed_urls = list(dict.fromkeys(local_seed_urls))
    visited: set[str] = set()
    documents: dict[str, dict[str, Any]] = {}
    parsed_roots: dict[str, ET.Element] = {}
    total_bytes = 0
    terminal_override: str | None = None
    issue_keys: set[tuple[str, str, str | None]] = set()
    dependency_keys: set[tuple[str, str, str]] = set()

    def promote_terminal(candidate: str) -> None:
        """Preserve the strongest causal failure seen for this package."""

        nonlocal terminal_override
        precedence = {
            None: 0,
            "unresolved external dependency": 1,
            "malformed package": 2,
            "acquisition failure": 3,
        }
        if precedence[candidate] > precedence[terminal_override]:
            terminal_override = candidate

    def issue(code: str, detail: str, url: str | None = None) -> None:
        key = (code, detail, url)
        if key in issue_keys:
            return
        issue_keys.add(key)
        record = {"code": code, "detail": detail}
        if url is not None:
            record["url"] = url
        base_payload["issues"].append(record)

    def acquire(
        url: str,
        depth: int,
        *,
        root_seed: bool = False,
        required_local: bool = False,
    ) -> list[tuple[str, str]]:
        nonlocal total_bytes
        url, _fragment = urldefrag(url)
        if url in visited:
            return []
        if depth > limits.max_depth or len(visited) >= limits.max_documents:
            issue("dependency_limit", "document-count or depth bound reached", url)
            promote_terminal("unresolved external dependency")
            return []
        try:
            body = fetch(url)
        except (OSError, KeyError, TimeoutError, ValueError) as exc:
            detail = str(getattr(exc, "reason", type(exc).__name__))
            issue("fetch_failed", detail, url)
            promote_terminal("acquisition failure" if root_seed or required_local else "unresolved external dependency")
            return []
        if not isinstance(body, bytes):
            issue("fetch_non_bytes", type(body).__name__, url)
            promote_terminal("acquisition failure" if root_seed or required_local else "unresolved external dependency")
            return []
        if total_bytes + len(body) > limits.max_total_bytes:
            issue("dependency_limit", "total-byte bound reached", url)
            promote_terminal("unresolved external dependency")
            return []
        total_bytes += len(body)
        visited.add(url)

        retrieval_evidence_getter = getattr(fetch, "retrieval_evidence", None)
        if callable(retrieval_evidence_getter):
            try:
                raw_retrieval_evidence = retrieval_evidence_getter(url)
                if not isinstance(raw_retrieval_evidence, Mapping):
                    raise TypeError("retrieval evidence is not a mapping")
                retrieval_evidence: dict[str, Any] = dict(raw_retrieval_evidence)
            except (KeyError, TypeError, ValueError) as exc:
                issue("retrieval_evidence_invalid", type(exc).__name__, url)
                promote_terminal("acquisition failure" if root_seed or required_local else "unresolved external dependency")
                return []
            evidence_valid = (
                retrieval_evidence.get("requested_url") == url
                and isinstance(retrieval_evidence.get("final_url"), str)
                and acquisition_url_allowed(retrieval_evidence["final_url"])
                and retrieval_evidence.get("http_status") == 200
                and retrieval_evidence.get("byte_length") == len(body)
                and retrieval_evidence.get("sha256") == sha256(body).hexdigest()
                and retrieval_evidence.get("method") == "bounded_exact_url_get"
            )
            if not evidence_valid:
                issue("retrieval_evidence_invalid", "bounded acquisition evidence does not match acquired bytes", url)
                promote_terminal("acquisition failure" if root_seed or required_local else "unresolved external dependency")
                return []
        else:
            retrieval_evidence = {
                "method": "exact_url_get",
                "source": "EDGAR filing index or recursively referenced DTS document",
            }
        # A traditional XBRL filing's primary SEC document is ordinary filing
        # HTML, not an XBRL package component.  Preserve its exact identity but
        # do not feed HTML entities to the XML package parser.
        if url == primary_url and not inline and not url.lower().endswith((".xml", ".xsd")):
            documents[url] = {
                "url": url,
                "owner": _document_owner(url, filing_base),
                "roles": ["primary_document"],
                "byte_length": len(body),
                "sha256": sha256(body).hexdigest(),
                "retrieval_evidence": retrieval_evidence,
            }
            return []

        try:
            root = ET.fromstring(body)
        except ET.ParseError as exc:
            issue("xml_malformed", str(exc), url)
            promote_terminal("malformed package")
            return []
        if url == primary_url:
            parsed_roots[url] = root
        roles = _classify_roles(url, root, filing_base, primary_url, inline)
        documents[url] = {
            "url": url,
            "owner": _document_owner(url, filing_base),
            "roles": roles,
            "byte_length": len(body),
            "sha256": sha256(body).hexdigest(),
            "retrieval_evidence": retrieval_evidence,
        }
        if url == primary_url and inline:
            base_payload["features"] = _fact_features(root, inline=True)
        elif not inline and "instance_document" in roles:
            base_payload["features"] = _fact_features(root, inline=False)
        references = _extract_references(root, url)
        for referenced_url, mechanism in references:
            key = (url, referenced_url, mechanism)
            if key in dependency_keys:
                continue
            dependency_keys.add(key)
            base_payload["dependencies"].append(
                {
                    "referring_document_url": url,
                    "referring_document_roles": roles,
                    "referenced_url": referenced_url,
                    "discovery_mechanism": mechanism,
                }
            )
        return references

    pending: list[tuple[str, int, tuple[str, ...]]] = []
    for seed in local_seed_urls:
        references = acquire(seed, 0, root_seed=seed == primary_url, required_local=True)
        pending.extend((reference_url, 1, (seed,)) for reference_url, _mechanism in references)

    external_documents = 0
    cursor = 0
    while cursor < len(pending):
        reference, depth, ancestry = pending[cursor]
        cursor += 1
        reference, _fragment = urldefrag(reference)
        if not acquisition_url_allowed(reference):
            issue("dependency_url_not_allowed", "dependency URL is outside the SEC/standard-taxonomy request policy", reference)
            promote_terminal("unresolved external dependency")
            continue
        if reference in ancestry:
            issue("dependency_cycle", "dependency points to an ancestor", reference)
            promote_terminal("unresolved external dependency")
            continue
        if reference in visited:
            continue
        is_external = not reference.startswith(filing_base)
        if is_external and external_documents >= limits.max_external_documents:
            issue("dependency_limit", "external-document bound reached", reference)
            promote_terminal("unresolved external dependency")
            continue
        before = len(visited)
        references = acquire(reference, depth, required_local=not is_external)
        if is_external and len(visited) > before:
            external_documents += 1
        pending.extend((child_url, depth + 1, ancestry + (reference,)) for child_url, _mechanism in references)

    base_payload["documents"] = [documents[url] for url in sorted(documents)]
    issues_by_url: dict[str, set[str]] = {}
    for issue_record in base_payload["issues"]:
        issue_url = issue_record.get("url")
        if issue_url:
            issues_by_url.setdefault(issue_url, set()).add(issue_record["code"])
    for dependency in base_payload["dependencies"]:
        referenced_url = dependency["referenced_url"]
        if referenced_url in documents:
            dependency["resolution"] = "acquired"
        elif "fetch_failed" in issues_by_url.get(referenced_url, set()):
            dependency["resolution"] = "acquisition_failed"
        elif "dependency_url_not_allowed" in issues_by_url.get(referenced_url, set()):
            dependency["resolution"] = "request_policy_rejected"
        elif "dependency_cycle" in issues_by_url.get(referenced_url, set()):
            dependency["resolution"] = "cycle"
        elif "dependency_limit" in issues_by_url.get(referenced_url, set()):
            dependency["resolution"] = "bounded"
        else:
            dependency["resolution"] = "not_acquired"
    base_payload["dependencies"] = sorted(
        base_payload["dependencies"],
        key=lambda row: (row["referring_document_url"], row["referenced_url"], row["discovery_mechanism"]),
    )
    primary_root = parsed_roots.get(primary_url)
    if primary_url not in documents:
        outcome = terminal_override or "acquisition failure"
    elif inline and primary_root is None:
        outcome = terminal_override or "malformed package"
    elif inline and primary_root is not None and not any("inlinexbrl" in str(element.tag).lower() for element in primary_root.iter()):
        issue("inline_namespace_missing", "submissions metadata says Inline XBRL but primary document has no Inline XBRL element", primary_url)
        outcome = "unsupported Inline XBRL"
    elif terminal_override == "malformed package":
        # Parsing failure is causal; do not downgrade it to the role that the
        # malformed document consequently failed to provide.
        outcome = "malformed package"
    elif not inline:
        instances = [url for url, document in documents.items() if "instance_document" in document["roles"]]
        if not instances:
            if terminal_override == "acquisition failure":
                outcome = "acquisition failure"
            else:
                issue("traditional_instance_missing", "no separate XBRL instance document found")
                outcome = "unsupported traditional XBRL"
        elif len(instances) > 1:
            issue("multiple_instance_documents", ",".join(sorted(instances)))
            outcome = "package-role ambiguity"
        else:
            schemas = [url for url, document in documents.items() if "extension_schema" in document["roles"]]
            if not schemas:
                if terminal_override == "acquisition failure":
                    outcome = "acquisition failure"
                else:
                    issue("extension_schema_missing", "traditional instance has no acquired extension schema")
                    outcome = "missing package component"
            else:
                outcome = terminal_override or "compatible"
    else:
        schemas = [url for url, document in documents.items() if "extension_schema" in document["roles"]]
        if not schemas:
            if terminal_override == "acquisition failure":
                outcome = "acquisition failure"
            else:
                issue("extension_schema_missing", "Inline document has no acquired extension schema")
                outcome = "missing package component"
        else:
            outcome = terminal_override or "compatible"

    if outcome not in TERMINAL_OUTCOMES:
        raise AssertionError(f"unclassified package outcome: {outcome}")
    base_payload["outcome"] = outcome
    return _finish(base_payload)
