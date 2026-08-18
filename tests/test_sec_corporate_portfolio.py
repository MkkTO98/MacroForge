from __future__ import annotations

import copy
from email.message import Message
from hashlib import sha256
from pathlib import Path
import sys
import urllib.error
import urllib.request

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.build_sec_corporate_portfolio_manifest import (  # noqa: E402
    BoundedAcquisitionFailure,
    BoundedFetcher,
    _PolicyRedirectHandler,
)
from macroforge.sec_corporate_portfolio import (
    ACCEPTANCE_CUTOFF,
    FROZEN_EXPECTATIONS,
    ISSUERS,
    PackageLimits,
    acquisition_url_allowed,
    build_expected_original_slots,
    build_portfolio_manifest,
    canonical_manifest_identity,
    enrich_package_result,
    validate_package,
)


def _row(cik: str, accession: str, form: str, report_date: str, *, inline: bool = True) -> dict:
    return {
        "cik": cik,
        "accessionNumber": accession,
        "form": form,
        "reportDate": report_date,
        "filingDate": report_date,
        "acceptanceDateTime": f"{report_date}T12:00:00.000Z",
        "primaryDocument": "misleading-name.htm" if inline else "instance.xml",
        "primaryDocDescription": form,
        "isXBRL": 1,
        "isInlineXBRL": int(inline),
    }


def _full_authored_corpus() -> list[dict]:
    rows: list[dict] = []
    serial = 1
    missing = {
        ("0001517006", 2024, "FY"),
        *(("0001517006", 2025, fp) for fp in ("Q1", "Q2", "Q3", "FY")),
        ("0000101778", 2024, "FY"),
        *(("0000101778", 2025, fp) for fp in ("Q1", "Q2", "Q3", "FY")),
    }
    for slot in build_expected_original_slots():
        key = (slot["cik"], slot["issuer_fiscal_year"], slot["fiscal_period"])
        if key in missing:
            continue
        year = slot["issuer_fiscal_year"]
        fp = slot["fiscal_period"]
        if slot["cik"] == "0000016160":
            dates = {"Q1": f"{year - 1}-08-28", "Q2": f"{year - 1}-11-27", "Q3": f"{year}-02-26", "FY": f"{year}-05-29"}
        else:
            dates = {"Q1": f"{year}-03-31", "Q2": f"{year}-06-30", "Q3": f"{year}-09-30", "FY": f"{year}-12-31"}
        rows.append(_row(slot["cik"], f"0000000000-{year % 100:02d}-{serial:06d}", slot["expected_form"], dates[fp]))
        serial += 1

    originals = list(rows)
    # 21 amendments: full, partial/cover-only, multiple amendments, and non-restatement proposals.
    for index in range(21):
        original = originals[index % 5]
        amendment = copy.deepcopy(original)
        amendment["accessionNumber"] = f"0000000001-25-{index + 1:06d}"
        amendment["form"] += "/A"
        amendment["primaryDocDescription"] = "cover-only amendment" if index == 1 else "amendment"
        amendment["isXBRL"] = 0 if index == 1 else 1
        amendment["isInlineXBRL"] = 0 if index == 1 else 1
        amendment["acceptanceDateTime"] = f"2025-12-{(index % 20) + 1:02d}T12:00:00.000Z"
        rows.append(amendment)
    return rows


def _inline_documents() -> tuple[dict, dict[str, bytes]]:
    primary = b'''<html xmlns:ix="http://www.xbrl.org/2013/inlineXBRL" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:link="http://www.xbrl.org/2003/linkbase"><head><link:schemaRef xlink:href="issuer-2025.xsd"/></head><body><ix:nonFraction name="us-gaap:Revenue" contextRef="c1" unitRef="usd" scale="6" sign="-">2</ix:nonFraction><ix:nonFraction name="dei:EntityCommonStockSharesOutstanding" contextRef="typed" unitRef="shares">3</ix:nonFraction><ix:nonFraction name="issuer:EarningsPerShare" contextRef="c1" unitRef="usdPerShare">1.25</ix:nonFraction><ix:nonNumeric name="issuer:Duplicate" contextRef="c1">A</ix:nonNumeric><ix:nonNumeric name="issuer:Duplicate" contextRef="c1">B</ix:nonNumeric><xbrldi:typedMember xmlns:xbrldi="http://xbrl.org/2006/xbrldi" dimension="issuer:Axis"><issuer:Domain xmlns:issuer="https://example.invalid/issuer">member</issuer:Domain></xbrldi:typedMember></body></html>'''
    schema = b'''<xsd:schema xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:link="http://www.xbrl.org/2003/linkbase" xmlns:xlink="http://www.w3.org/1999/xlink" targetNamespace="https://example.invalid/issuer"><xsd:import namespace="http://fasb.org/us-gaap/2025" schemaLocation="https://xbrl.fasb.org/us-gaap/2025/us-gaap-2025.xsd"/><link:linkbaseRef xlink:href="issuer-2025_cal.xml"/><link:linkbaseRef xlink:href="issuer-2025_pre.xml"/><link:linkbaseRef xlink:href="issuer-2025_def.xml"/><link:linkbaseRef xlink:href="issuer-2025_lab.xml"/></xsd:schema>'''
    external = b'<xsd:schema xmlns:xsd="http://www.w3.org/2001/XMLSchema" targetNamespace="http://fasb.org/us-gaap/2025"/>'
    linkbase = b'<link:linkbase xmlns:link="http://www.xbrl.org/2003/linkbase"/>'
    base = "https://www.sec.gov/Archives/edgar/data/34088/000000000025000001/"
    docs = {
        base + "misleading-name.htm": primary,
        base + "issuer-2025.xsd": schema,
        base + "issuer-2025_cal.xml": linkbase,
        base + "issuer-2025_pre.xml": linkbase,
        base + "issuer-2025_def.xml": linkbase,
        base + "issuer-2025_lab.xml": linkbase,
        "https://xbrl.fasb.org/us-gaap/2025/us-gaap-2025.xsd": external,
    }
    index = {"directory": {"item": [{"name": url.rsplit("/", 1)[-1], "size": len(body)} for url, body in docs.items() if url.startswith(base)]}}
    return index, docs


def _filing(*, inline: bool = True, form: str = "10-K", accession: str = "0000000000-25-000001") -> dict:
    return {
        "cik": "0000034088",
        "accessionNumber": accession,
        "form": form,
        "reportDate": "2025-12-31",
        "acceptanceDateTime": "2026-02-01T12:00:00.000Z",
        "primaryDocument": "misleading-name.htm" if inline else "instance.xml",
        "isXBRL": 1,
        "isInlineXBRL": int(inline),
    }


def test_frozen_ledger_is_exactly_15_by_5_by_4_and_deterministic() -> None:
    first = build_expected_original_slots()
    second = build_expected_original_slots()
    assert len(ISSUERS) == 15
    assert len(first) == 300
    assert first == second
    assert len({row["slot_id"] for row in first}) == 300
    assert {row["expected_form"] for row in first} == {"10-K", "10-Q"}
    assert ACCEPTANCE_CUTOFF == "2026-06-30T23:59:59Z"


def test_accession_disposition_manifest_exact_accounting_amendments_and_cessation() -> None:
    manifest = build_portfolio_manifest(_full_authored_corpus())
    assert manifest["counts"] == FROZEN_EXPECTATIONS
    assert manifest["corpus_accepted"] is True
    assert len(manifest["expected_original_slots"]) == 300
    assert len(manifest["filing_acts"]) == 311
    assert sum(row["disposition"] == "acquisition_cessation_absence" for row in manifest["expected_original_slots"]) == 10
    absent = [row for row in manifest["expected_original_slots"] if row["disposition"] == "acquisition_cessation_absence"]
    assert {row["cessation_evidence"]["accession"] for row in absent} == {"0001193125-25-007425", "0001104659-24-122113"}
    amendments = [row for row in manifest["filing_acts"] if row["is_amendment"]]
    assert len(amendments) == 21
    assert all(row["relationship_proposal"]["restatement_status"] == "undetermined" for row in amendments)
    assert any(row["amendment_scope"] == "cover_only_or_partial" for row in amendments)
    assert sum(row["relationship_proposal"]["original_accession"] == amendments[0]["relationship_proposal"]["original_accession"] for row in amendments) > 1


def test_cal_maine_52_53_week_fiscal_evidence_is_not_calendar_quarter_assumption() -> None:
    manifest = build_portfolio_manifest(_full_authored_corpus())
    cal = [row for row in manifest["filing_acts"] if row["cik"] == "0000016160" and not row["is_amendment"]]
    q1 = next(row for row in cal if row["issuer_fiscal_year"] == 2025 and row["fiscal_period"] == "Q1")
    assert q1["report_date"] == "2024-08-28"
    assert q1["fiscal_calendar_evidence"]["calendar_kind"] == "52_53_week"
    assert q1["fiscal_calendar_evidence"]["derivation"] == "cal_maine_authored_rule"


def test_current_observation_difference_fails_closed_without_rewriting_expectations() -> None:
    rows = _full_authored_corpus()
    rows.pop(next(i for i, row in enumerate(rows) if "/A" not in row["form"] and row["cik"] == "0000034088"))
    manifest = build_portfolio_manifest(rows)
    assert manifest["frozen_expectations"] == FROZEN_EXPECTATIONS
    assert manifest["counts"]["observed_originals"] == 289
    assert manifest["corpus_accepted"] is False
    assert {issue["classification"] for issue in manifest["discrepancies"]} == {"metadata_discrepancy"}


def test_historical_out_of_scope_act_with_unclassifiable_report_date_is_ignored() -> None:
    rows = _full_authored_corpus()
    rows.append({
        **_row("0000101778", "0000101778-11-000048", "10-K/A", ""),
        "acceptanceDateTime": "2011-06-01T12:00:00.000Z",
    })
    manifest = build_portfolio_manifest(rows)
    assert manifest["corpus_accepted"] is True
    assert manifest["counts"] == FROZEN_EXPECTATIONS
    assert not manifest["discrepancies"]


def test_inline_package_inventory_roles_features_dependencies_and_identity() -> None:
    index, docs = _inline_documents()
    fetch = docs.__getitem__
    result = validate_package(_filing(), index, fetch)
    assert result["outcome"] == "compatible"
    assert result["xbrl_format"] == "inline"
    roles = {role for document in result["documents"] for role in document["roles"]}
    assert {"primary_document", "inline_instance", "extension_schema", "calculation_linkbase", "presentation_linkbase", "definition_linkbase", "label_linkbase", "external_taxonomy_dependency"} <= roles
    assert result["features"] == {
        "dimensions": True,
        "typed_members": True,
        "units": ["shares", "usd", "usdPerShare"],
        "inline_scale": True,
        "inline_sign": True,
        "duplicate_fact_keys": True,
        "conflicting_duplicate_values": True,
    }
    assert all(document["byte_length"] > 0 and len(document["sha256"]) == 64 for document in result["documents"])
    assert canonical_manifest_identity(result) == canonical_manifest_identity(validate_package(_filing(), index, fetch))


def test_traditional_xbrl_gatos_accession_stays_in_scope_and_compatible() -> None:
    accession = "0001104659-21-062988"
    base = "https://www.sec.gov/Archives/edgar/data/1517006/000110465921062988/"
    instance = b'''<xbrli:xbrl xmlns:xbrli="http://www.xbrl.org/2003/instance" xmlns:link="http://www.xbrl.org/2003/linkbase" xmlns:xlink="http://www.w3.org/1999/xlink"><link:schemaRef xlink:href="gato-2021.xsd"/></xbrli:xbrl>'''
    schema = b'<xsd:schema xmlns:xsd="http://www.w3.org/2001/XMLSchema" targetNamespace="https://example.invalid/gato"/>'
    docs = {base + "instance.xml": instance, base + "gato-2021.xsd": schema}
    index = {"directory": {"item": [{"name": "instance.xml", "size": len(instance)}, {"name": "gato-2021.xsd", "size": len(schema)}]}}
    filing = {**_filing(inline=False, form="10-Q", accession=accession), "cik": "0001517006"}
    result = validate_package(filing, index, docs.__getitem__)
    assert result["accession"] == accession
    assert result["xbrl_format"] == "traditional"
    assert result["outcome"] == "compatible"
    assert any("instance_document" in document["roles"] for document in result["documents"])


def test_traditional_package_does_not_xml_parse_ordinary_filing_cover_html() -> None:
    accession = "0001104659-21-062988"
    base = "https://www.sec.gov/Archives/edgar/data/1517006/000110465921062988/"
    cover = b"<html><body>ordinary filing cover&nbsp;</body></html>"
    instance = b'''<xbrli:xbrl xmlns:xbrli="http://www.xbrl.org/2003/instance" xmlns:link="http://www.xbrl.org/2003/linkbase" xmlns:xlink="http://www.w3.org/1999/xlink"><link:schemaRef xlink:href="gato-2021.xsd"/></xbrli:xbrl>'''
    schema = b'<xsd:schema xmlns:xsd="http://www.w3.org/2001/XMLSchema" targetNamespace="https://example.invalid/gato"/>'
    docs = {
        base + "tm2113231d1_10q.htm": cover,
        base + "gato-20210331.xml": instance,
        base + "gato-2021.xsd": schema,
    }
    index = {"directory": {"item": [{"name": url.rsplit("/", 1)[-1], "size": len(body)} for url, body in docs.items()]}}
    filing = {
        **_filing(inline=False, form="10-Q", accession=accession),
        "cik": "0001517006",
        "primaryDocument": "tm2113231d1_10q.htm",
    }
    result = validate_package(filing, index, docs.__getitem__)
    assert result["outcome"] == "compatible"
    cover_record = next(document for document in result["documents"] if document["url"].endswith("tm2113231d1_10q.htm"))
    assert cover_record["roles"] == ["primary_document"]
    assert not any(issue["code"] == "xml_malformed" for issue in result["issues"])


def test_default_bound_closes_normal_shared_standard_taxonomy_graph() -> None:
    index, docs = _inline_documents()
    schema_url = next(url for url in docs if url.endswith("issuer-2025.xsd"))
    external_urls = [f"https://xbrl.fasb.org/test/standard-{number}.xsd" for number in range(16)]
    imports = "".join(f'<xsd:import schemaLocation="{url}"/>' for url in external_urls)
    docs[schema_url] = f'<xsd:schema xmlns:xsd="http://www.w3.org/2001/XMLSchema">{imports}</xsd:schema>'.encode()
    docs.update({url: b'<xsd:schema xmlns:xsd="http://www.w3.org/2001/XMLSchema"/>' for url in external_urls})
    result = validate_package(_filing(), index, docs.__getitem__)
    assert result["outcome"] == "compatible"
    assert sum(document["owner"] != "sec_filing" for document in result["documents"]) == 16


def test_local_indexed_component_acquisition_failure_is_not_missing_component() -> None:
    index, docs = _inline_documents()
    schema_url = next(url for url in docs if url.endswith("issuer-2025.xsd"))

    def fetch(url: str) -> bytes:
        if url == schema_url:
            raise OSError("transient timeout")
        return docs[url]

    result = validate_package(_filing(), index, fetch)
    assert result["outcome"] == "acquisition failure"
    assert any(issue["code"] == "fetch_failed" and issue["url"] == schema_url for issue in result["issues"])
    assert not any(issue["code"] == "extension_schema_missing" for issue in result["issues"])


def test_dependency_edges_record_exact_discovery_mechanism_and_referrer() -> None:
    index, docs = _inline_documents()
    result = validate_package(_filing(), index, docs.__getitem__)
    schema_url = next(url for url in docs if url.endswith("issuer-2025.xsd"))
    external_url = "https://xbrl.fasb.org/us-gaap/2025/us-gaap-2025.xsd"
    edge = next(edge for edge in result["dependencies"] if edge["referenced_url"] == external_url)
    assert edge["discovery_mechanism"] == "xsd:import"
    assert edge["referring_document_url"] == schema_url
    assert edge["referring_document_roles"] == ["extension_schema"]
    assert edge["resolution"] == "acquired"
    assert not any("example.invalid/issuer" in edge["referenced_url"] for edge in result["dependencies"])


def test_enriched_package_identity_covers_linkage_and_retrieval_evidence() -> None:
    index, docs = _inline_documents()
    result = validate_package(_filing(), index, docs.__getitem__)
    enriched = enrich_package_result(
        result,
        {"cik": "0000034088", "issuer_fiscal_year": 2025, "fiscal_period": "FY", "is_amendment": False},
        {"requested_url": "https://www.sec.gov/example/index.json", "http_status": 200},
    )
    assert enriched["manifest_sha256"] == canonical_manifest_identity(enriched)
    changed = copy.deepcopy(enriched)
    changed["slot_id"] = "different"
    assert changed["manifest_sha256"] != canonical_manifest_identity(changed)


@pytest.mark.parametrize(
    ("mutation", "expected"),
    [
        ("missing_schema", "missing package component"),
        ("multiple_instances", "package-role ambiguity"),
        ("not_inline", "unsupported Inline XBRL"),
        ("malformed", "malformed package"),
    ],
)
def test_package_failure_modes_are_explicit(mutation: str, expected: str) -> None:
    index, docs = _inline_documents()
    filing = _filing()
    if mutation == "missing_schema":
        schema_url = next(url for url in docs if url.endswith("issuer-2025.xsd"))
        docs.pop(schema_url)
        primary_url = next(url for url in docs if url.endswith("misleading-name.htm"))
        docs[primary_url] = docs[primary_url].replace(b'<link:schemaRef xlink:href="issuer-2025.xsd"/>', b"")
        index["directory"]["item"] = [item for item in index["directory"]["item"] if item["name"] != "issuer-2025.xsd"]
    elif mutation == "multiple_instances":
        filing = _filing(inline=False)
        base = "https://www.sec.gov/Archives/edgar/data/34088/000000000025000001/"
        instance = b'<xbrli:xbrl xmlns:xbrli="http://www.xbrl.org/2003/instance"/>'
        docs = {base + "instance.xml": instance, base + "other.xml": instance}
        index = {"directory": {"item": [{"name": "instance.xml", "size": len(instance)}, {"name": "other.xml", "size": len(instance)}]}}
    elif mutation == "not_inline":
        primary_url = next(url for url in docs if url.endswith("misleading-name.htm"))
        docs[primary_url] = b"<html><body>not inline</body></html>"
    elif mutation == "malformed":
        schema_url = next(url for url in docs if url.endswith("issuer-2025.xsd"))
        docs[schema_url] = b"<xsd:schema"
    result = validate_package(filing, index, docs.__getitem__)
    assert result["outcome"] == expected
    assert result["issues"]


def test_acquisition_failure_and_governed_exclusion_are_terminal() -> None:
    index, _ = _inline_documents()
    failure = validate_package(_filing(), index, lambda _: (_ for _ in ()).throw(OSError("offline")))
    exclusion = validate_package(_filing(), index, lambda _: b"", governed_exclusion="fixture policy")
    assert failure["outcome"] == "acquisition failure"
    assert exclusion["outcome"] == "explicit governed exclusion"


def test_dependency_cycle_and_traversal_bound_fail_closed() -> None:
    index, docs = _inline_documents()
    schema_url = next(url for url in docs if url.endswith("issuer-2025.xsd"))
    external_url = "https://xbrl.fasb.org/us-gaap/2025/us-gaap-2025.xsd"
    docs[external_url] = f'<xsd:schema xmlns:xsd="http://www.w3.org/2001/XMLSchema"><xsd:import schemaLocation="{schema_url}"/></xsd:schema>'.encode()
    cycle = validate_package(_filing(), index, docs.__getitem__)
    bounded = validate_package(_filing(), index, docs.__getitem__, limits=PackageLimits(max_documents=2, max_depth=1, max_total_bytes=10_000_000))
    assert cycle["outcome"] == "unresolved external dependency"
    assert any(issue["code"] == "dependency_cycle" for issue in cycle["issues"])
    assert bounded["outcome"] == "unresolved external dependency"
    assert any(issue["code"] == "dependency_limit" for issue in bounded["issues"])


def test_every_attempt_has_exactly_one_allowed_terminal_outcome() -> None:
    index, docs = _inline_documents()
    result = validate_package(_filing(), index, docs.__getitem__)
    assert isinstance(result["outcome"], str)
    assert result["outcome"] in {
        "compatible", "acquisition failure", "metadata discrepancy", "missing package component",
        "package-role ambiguity", "unsupported traditional XBRL", "unsupported Inline XBRL",
        "unresolved external dependency", "malformed package", "explicit governed exclusion",
    }
    assert sha256(result["canonical_json"].encode()).hexdigest() == result["manifest_sha256"]


def test_bounded_fetcher_retries_transient_timeout_without_volatile_attempt_metadata(monkeypatch: pytest.MonkeyPatch) -> None:
    calls: list[str] = []

    class Response:
        status = 200

        def __enter__(self) -> "Response":
            return self

        def __exit__(self, *_: object) -> None:
            return None

        def read(self, _: int) -> bytes:
            return b"stable"

        def geturl(self) -> str:
            return "https://xbrl.fasb.org/final.xsd"

    def urlopen(request: object, *, timeout: float) -> Response:
        calls.append(str(timeout))
        if len(calls) == 1:
            raise TimeoutError("transient")
        return Response()

    class Opener:
        def open(self, request: object, *, timeout: float) -> Response:
            return urlopen(request, timeout=timeout)

    monkeypatch.setattr("urllib.request.build_opener", lambda *_: Opener())
    fetcher = BoundedFetcher("test@example.invalid", minimum_interval_seconds=0)
    assert fetcher("https://xbrl.fasb.org/source.xsd") == b"stable"
    assert calls == ["10.0", "10.0"]
    assert fetcher.observations["https://xbrl.fasb.org/source.xsd"] == {
        "requested_url": "https://xbrl.fasb.org/source.xsd",
        "final_url": "https://xbrl.fasb.org/final.xsd",
        "http_status": 200,
        "byte_length": 6,
        "sha256": sha256(b"stable").hexdigest(),
        "method": "bounded_exact_url_get",
    }


def test_bounded_fetcher_retries_and_caches_stable_failures(monkeypatch: pytest.MonkeyPatch) -> None:
    calls = 0

    def unavailable(request, timeout):
        nonlocal calls
        calls += 1
        raise urllib.error.HTTPError(request.full_url, 404, "not found", Message(), None)

    class Opener:
        def open(self, request: object, *, timeout: float) -> object:
            return unavailable(request, timeout)

    monkeypatch.setattr("urllib.request.build_opener", lambda *_: Opener())
    fetcher = BoundedFetcher("MacroForge test contact@example.invalid", max_attempts=2, minimum_interval_seconds=0)
    with pytest.raises(BoundedAcquisitionFailure, match="http_404") as first:
        fetcher("https://xbrl.fasb.org/missing.xsd")
    assert first.value.reason == "http_404"
    with pytest.raises(BoundedAcquisitionFailure, match="http_404"):
        fetcher("https://xbrl.fasb.org/missing.xsd")
    assert calls == 2


def test_duplicate_accession_is_a_fail_closed_corpus_discrepancy() -> None:
    rows = _full_authored_corpus()
    rows.append(copy.deepcopy(rows[0]))
    result = build_portfolio_manifest(rows)
    assert result["corpus_accepted"] is False
    duplicates = [item for item in result["discrepancies"] if item["code"] == "duplicate_accession"]
    assert duplicates == [{
        "classification": "metadata_discrepancy",
        "code": "duplicate_accession",
        "accession": rows[0]["accessionNumber"],
    }]


def test_amendment_relationship_requires_same_base_form_and_report_date() -> None:
    rows = _full_authored_corpus()
    amendment = next(row for row in rows if str(row["form"]).endswith("/A"))
    amendment["reportDate"] = "2021-03-30"
    result = build_portfolio_manifest(rows)
    act = next(item for item in result["filing_acts"] if item["accession"] == amendment["accessionNumber"])
    assert act["relationship_proposal"]["original_accession"] is None
    discrepancy = next(item for item in result["discrepancies"] if item.get("accession") == amendment["accessionNumber"])
    assert discrepancy["code"] == "amendment_original_ambiguous"
    assert discrepancy["candidate_originals"] == []


def test_traditional_instance_retains_fact_features() -> None:
    base = "https://www.sec.gov/Archives/edgar/data/1517006/000110465921062988/"
    docs = {
        base + "tm2113231d1_10q.htm": b"<html><body>Gatos Mining &nbsp; filing cover</body></html>",
        base + "gatos-20210331.xml": b'''<xbrli:xbrl xmlns:xbrli="http://www.xbrl.org/2003/instance" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:link="http://www.xbrl.org/2003/linkbase" xmlns:xbrldi="http://xbrl.org/2006/xbrldi" xmlns:issuer="https://example.invalid/issuer"><link:schemaRef xlink:href="gatos-20210331.xsd"/><xbrli:context id="c1"><xbrli:entity><xbrli:identifier scheme="http://www.sec.gov/CIK">1517006</xbrli:identifier><xbrli:segment><xbrldi:explicitMember dimension="issuer:Axis">issuer:Member</xbrldi:explicitMember><xbrldi:typedMember dimension="issuer:TypedAxis"><issuer:Domain>typed</issuer:Domain></xbrldi:typedMember></xbrli:segment></xbrli:entity><xbrli:period><xbrli:instant>2021-03-31</xbrli:instant></xbrli:period></xbrli:context><xbrli:unit id="usd"><xbrli:measure>iso4217:USD</xbrli:measure></xbrli:unit><issuer:Revenue contextRef="c1" unitRef="usd">1</issuer:Revenue><issuer:Revenue contextRef="c1" unitRef="usd">2</issuer:Revenue></xbrli:xbrl>''',
        base + "gatos-20210331.xsd": b'<xsd:schema xmlns:xsd="http://www.w3.org/2001/XMLSchema" targetNamespace="https://example.invalid/issuer"/>',
    }
    index = {"directory": {"item": [{"name": url.rsplit("/", 1)[-1], "size": len(body)} for url, body in docs.items()]}}
    filing = _filing(inline=False, accession="0001104659-21-062988")
    filing["cik"] = "0001517006"
    filing["primaryDocument"] = "tm2113231d1_10q.htm"
    result = validate_package(filing, index, docs.__getitem__)
    assert result["outcome"] == "compatible"
    assert result["features"] == {
        "dimensions": True,
        "typed_members": True,
        "units": ["usd"],
        "inline_scale": False,
        "inline_sign": False,
        "duplicate_fact_keys": True,
        "conflicting_duplicate_values": True,
    }


def test_dependency_request_policy_rejects_local_file_without_fetching_it() -> None:
    index, docs = _inline_documents()
    schema_url = next(url for url in docs if url.endswith("issuer-2025.xsd"))
    docs[schema_url] = docs[schema_url].replace(
        b"</xsd:schema>",
        b'<xsd:import namespace="urn:unsafe" schemaLocation="file:///etc/passwd"/></xsd:schema>',
    )
    requested: list[str] = []

    def fetch(url: str) -> bytes:
        requested.append(url)
        return docs[url]

    result = validate_package(_filing(), index, fetch)
    assert result["outcome"] == "unresolved external dependency"
    assert "file:///etc/passwd" not in requested
    assert any(issue["code"] == "dependency_url_not_allowed" for issue in result["issues"])
    edge = next(edge for edge in result["dependencies"] if edge["referenced_url"] == "file:///etc/passwd")
    assert edge["resolution"] == "request_policy_rejected"


def test_bounded_fetcher_rejects_non_http_scheme_before_urlopen(monkeypatch: pytest.MonkeyPatch) -> None:
    called = False

    def forbidden(*args, **kwargs):
        nonlocal called
        called = True
        raise AssertionError("urlopen must not be called")

    monkeypatch.setattr("urllib.request.urlopen", forbidden)
    fetcher = BoundedFetcher("MacroForge test contact@example.invalid", minimum_interval_seconds=0)
    with pytest.raises(BoundedAcquisitionFailure, match="request_policy_rejected") as error:
        fetcher("file:///etc/passwd")
    assert error.value.reason == "request_policy_rejected"
    assert called is False


def test_acquisition_url_policy_enforces_scheme_specific_default_ports() -> None:
    assert acquisition_url_allowed("https://www.sec.gov/Archives/edgar/data/1/index.json")
    assert acquisition_url_allowed("https://xbrl.fasb.org/us-gaap/2025/us-gaap-2025.xsd")
    assert acquisition_url_allowed("http://www.xbrl.org/2003/xbrl-instance-2003-12-31.xsd")
    assert not acquisition_url_allowed("http://www.sec.gov/Archives/edgar/data/1/index.json")
    assert not acquisition_url_allowed("https://xbrl.fasb.org:80/us-gaap.xsd")
    assert not acquisition_url_allowed("http://www.xbrl.org:443/instance.xsd")
    assert not acquisition_url_allowed("https://evil.example/taxonomy.xsd")


def test_redirect_handler_rejects_forbidden_target_before_following() -> None:
    handler = _PolicyRedirectHandler()
    request = urllib.request.Request("https://www.sec.gov/Archives/edgar/data/1/index.json")
    with pytest.raises(BoundedAcquisitionFailure, match="request_policy_rejected"):
        handler.redirect_request(request, None, 302, "Found", Message(), "file:///etc/passwd")


def test_fetcher_rejects_forbidden_final_url_before_reading(monkeypatch: pytest.MonkeyPatch) -> None:
    read_called = False

    class Response:
        status = 200

        def __enter__(self) -> "Response":
            return self

        def __exit__(self, *_: object) -> None:
            return None

        def geturl(self) -> str:
            return "https://evil.example/redirected.xsd"

        def read(self, _: int) -> bytes:
            nonlocal read_called
            read_called = True
            return b"forbidden"

    class Opener:
        def open(self, request: object, *, timeout: float) -> Response:
            return Response()

    monkeypatch.setattr("urllib.request.build_opener", lambda *_: Opener())
    fetcher = BoundedFetcher("MacroForge test contact@example.invalid", minimum_interval_seconds=0)
    with pytest.raises(BoundedAcquisitionFailure, match="request_policy_rejected"):
        fetcher("https://www.sec.gov/Archives/edgar/data/1/issuer.xsd")
    assert read_called is False


def test_operational_retrieval_evidence_propagates_into_package_documents() -> None:
    index, docs = _inline_documents()

    class ObservedFetch:
        def __call__(self, url: str) -> bytes:
            return docs[url]

        def retrieval_evidence(self, url: str) -> dict:
            body = docs[url]
            return {
                "requested_url": url,
                "final_url": url,
                "http_status": 200,
                "byte_length": len(body),
                "sha256": sha256(body).hexdigest(),
                "method": "bounded_exact_url_get",
            }

    result = validate_package(_filing(), index, ObservedFetch())
    assert result["outcome"] == "compatible"
    assert all(document["retrieval_evidence"]["requested_url"] == document["url"] for document in result["documents"])
    assert all(document["retrieval_evidence"]["final_url"] == document["url"] for document in result["documents"])
    assert all(document["retrieval_evidence"]["http_status"] == 200 for document in result["documents"])
