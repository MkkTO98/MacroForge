from __future__ import annotations

from dataclasses import replace
from hashlib import sha256
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time
from collections.abc import Iterator
import uuid

import pytest

from macroforge.corporate_reporting_queries import (
    AmbiguousSelection, CorporateAuthorityRef, PostgresCorporateAuthorityStore,
)
from macroforge.corporate_reporting_release import publish_database_anchored
from macroforge.sec_corporate_proof_tranche import (
    AcquisitionIdentityError,
    TrancheAuthenticationError,
    acquisition_report,
    acquire_frozen_documents,
    authenticate_tranche,
    build_filing_load,
    load_proof_campaign,
    stable_postgres_state,
)
from macroforge.sec_corporate_reporting import parse_inline_instance
import macroforge.sec_corporate_reporting_loader as loader_module
from tools import run_sec_corporate_proof_tranche as runner_module
from macroforge.sec_corporate_reporting_loader import _build_postgresql_sql
from macroforge.sec_corporate_reporting_loader import (
    IdentityConflict,
    PostgreSQLLoadError,
    PostgreSQLLoadTimeout,
    load_corporate_filings_to_postgres,
)

PROJECT_ROOT = Path(__file__).parents[1]
POSTGRES_TOOLS = all(shutil.which(command) for command in ("psql", "createdb", "dropdb"))
POSTGRES_ONLY = pytest.mark.skipif(not POSTGRES_TOOLS, reason="psql database tools unavailable")


@pytest.fixture
def task223_postgres() -> Iterator[str]:
    database = f"macroforge_task223_{uuid.uuid4().hex[:12]}"
    subprocess.run(["createdb", database], check=True, capture_output=True, text=True)
    try:
        for migration in (
            PROJECT_ROOT / "db/migrations/001_v0_schema_foundation.sql",
            PROJECT_ROOT / "db/migrations/005_corporate_reporting_foundation.sql",
        ):
            subprocess.run(
                ["psql", "-X", "-v", "ON_ERROR_STOP=1", "-q", "-d", database, "-f", str(migration)],
                check=True, capture_output=True, text=True,
            )
        yield database
    finally:
        subprocess.run(["dropdb", "--if-exists", database], check=True, capture_output=True, text=True)


def _psql(database: str, statement: str) -> str:
    result = subprocess.run(
        ["psql", "-X", "-v", "ON_ERROR_STOP=1", "-A", "-t", "-d", database],
        input=statement, check=True, capture_output=True, text=True,
    )
    return result.stdout.strip()


def _canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()


def _inline(path: Path) -> bytes:
    body = b'''<html xmlns="http://www.w3.org/1999/xhtml"
      xmlns:ix="http://www.xbrl.org/2013/inlineXBRL"
      xmlns:xbrli="http://www.xbrl.org/2003/instance"
      xmlns:xbrldi="http://xbrl.org/2006/xbrldi"
      xmlns:iso4217="http://www.xbrl.org/2003/iso4217"
      xmlns:dei="http://xbrl.sec.gov/dei/2024"
      xmlns:ixt="http://www.xbrl.org/inlineXBRL/transformation/2020-02-12"
      xmlns:us-gaap="http://fasb.org/us-gaap/2024"
      xmlns:ex="urn:issuer">
      <head><title>authored inline</title></head><body>
       <ix:resources>
        <xbrli:context id="duration"><xbrli:entity><xbrli:identifier scheme="https://www.sec.gov/CIK">0000000001</xbrli:identifier><xbrli:segment><xbrldi:explicitMember dimension="ex:Axis">ex:Member</xbrldi:explicitMember></xbrli:segment></xbrli:entity><xbrli:period><xbrli:startDate>2023-01-01</xbrli:startDate><xbrli:endDate>2023-12-31</xbrli:endDate></xbrli:period></xbrli:context>
        <xbrli:context id="instant"><xbrli:entity><xbrli:identifier scheme="https://www.sec.gov/CIK">0000000001</xbrli:identifier></xbrli:entity><xbrli:period><xbrli:instant>2023-12-31</xbrli:instant></xbrli:period></xbrli:context>
        <xbrli:unit id="usd"><xbrli:measure>iso4217:USD</xbrli:measure></xbrli:unit>
       </ix:resources>
       <ix:nonNumeric name="dei:DocumentType" contextRef="duration">10-K</ix:nonNumeric>
       <ix:nonNumeric name="dei:EntityCentralIndexKey" contextRef="duration">0000000001</ix:nonNumeric>
       <ix:nonFraction name="us-gaap:Revenue" contextRef="duration" unitRef="usd" decimals="-6" scale="6" sign="-" format="ixt:num-dot-decimal">2</ix:nonFraction>
       <ix:nonFraction name="us-gaap:Assets" contextRef="instant" unitRef="usd" decimals="0">3</ix:nonFraction>
       <ix:nonFraction name="us-gaap:Assets" contextRef="instant" unitRef="usd" decimals="0">4</ix:nonFraction>
       <ix:nonFraction name="ex:NilFact" contextRef="instant" unitRef="usd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:nil="true"/>
      </body></html>'''
    path.write_bytes(body)
    return body


def _schema(path: Path) -> bytes:
    body = b'''<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:xbrli="http://www.xbrl.org/2003/instance" targetNamespace="urn:issuer"><xs:element name="NilFact" type="xs:decimal" substitutionGroup="xbrli:item"/></xs:schema>'''
    path.write_bytes(body)
    return body


def _manifest_and_ledger(tmp_path: Path) -> tuple[Path, Path, dict[str, bytes]]:
    inline = _inline(tmp_path / "issuer.htm")
    schema = _schema(tmp_path / "issuer.xsd")
    accession = "0000000001-24-000001"
    base = "https://www.sec.gov/Archives/edgar/data/1/000000000124000001/"
    documents = [
        {"url": base + "issuer.htm", "owner": "sec_filing", "roles": ["inline_instance", "primary_document"], "byte_length": len(inline), "sha256": sha256(inline).hexdigest(), "retrieval_evidence": {"requested_url": base + "issuer.htm", "final_url": base + "issuer.htm", "http_status": 200, "byte_length": len(inline), "sha256": sha256(inline).hexdigest(), "method": "bounded_exact_url_get"}},
        {"url": base + "issuer.xsd", "owner": "sec_filing", "roles": ["extension_schema"], "byte_length": len(schema), "sha256": sha256(schema).hexdigest(), "retrieval_evidence": {"requested_url": base + "issuer.xsd", "final_url": base + "issuer.xsd", "http_status": 200, "byte_length": len(schema), "sha256": sha256(schema).hexdigest(), "method": "bounded_exact_url_get"}},
    ]
    package = {"accession": accession, "cik": "0000000001", "form": "10-K", "xbrl_format": "inline", "outcome": "compatible", "documents": documents, "manifest_sha256": ""}
    package["manifest_sha256"] = sha256(_canonical({k: v for k, v in package.items() if k != "manifest_sha256"})).hexdigest()
    manifest = {"schema": "macroforge.corporate-portfolio-v1.validation-report.v1", "corpus_accepted": True, "package_results": [package], "manifest_sha256": ""}
    manifest["manifest_sha256"] = sha256(_canonical({k: v for k, v in manifest.items() if k != "manifest_sha256"})).hexdigest()
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_bytes(_canonical(manifest) + b"\n")
    act = {"issuer": "Authored Issuer", "cik": "0000000001", "accession": accession, "form": "10-K", "base_form": "10-K", "report_date": "2023-12-31", "filing_date": "2024-01-02", "accepted_at": "2024-01-02T12:00:00Z", "primary_document": "issuer.htm", "issuer_fiscal_year": 2023, "fiscal_period": "FY", "original_or_amendment": "original", "relationship_proposal": None, "xbrl_format": "inline", "package_manifest_sha256": package["manifest_sha256"]}
    ledger_payload = {"schema": "macroforge.task223.proof-tranche-ledger.v1", "source_manifest_sha256": manifest["manifest_sha256"], "filing_acts": [act], "frozen_accessions": [accession], "explicit_absences": [{"absence_identity": "a" * 64, "cik": "0000000002", "issuer": "Stopped Issuer", "issuer_fiscal_year": 2025, "fiscal_period": "FY", "disposition": "acquisition_cessation_absence"}], "frozen_absence_identities": ["a" * 64]}
    ledger = {**ledger_payload, "ledger_sha256": sha256(_canonical(ledger_payload)).hexdigest()}
    ledger_path = tmp_path / "ledger.json"
    ledger_path.write_bytes(_canonical(ledger) + b"\n")
    return manifest_path, ledger_path, {documents[0]["url"]: inline, documents[1]["url"]: schema}


def test_inline_occurrences_preserve_raw_scale_sign_nil_duplicates_and_conflict(tmp_path: Path) -> None:
    path = tmp_path / "inline.htm"
    source = _inline(path)
    report = parse_inline_instance(path, accession="0000000001-24-000001", dts_manifest_sha256="d" * 64)
    assert report.source_sha256 == sha256(source).hexdigest()
    revenue = next(item for item in report.occurrences if item.concept.endswith("}Revenue"))
    assert (revenue.lexical_value, revenue.inline_scale, revenue.inline_sign) == ("2", 6, "-")
    assert revenue.inline_format == "{http://www.xbrl.org/inlineXBRL/transformation/2020-02-12}num-dot-decimal"
    nil = next(item for item in report.occurrences if item.concept.endswith("}NilFact"))
    assert nil.nil and nil.lexical_value == ""
    conflict = next(slot for slot in report.slots.values() if slot.status == "conflict")
    assert len(conflict.occurrences) == 2 and conflict.selected_occurrence is None
    assert report.metrics["inline_scale_count"] == 1
    assert report.metrics["inline_sign_count"] == 1


def test_authentication_acquisition_and_report_are_exact_and_body_free(tmp_path: Path) -> None:
    manifest_path, ledger_path, bodies = _manifest_and_ledger(tmp_path)
    manifest, ledger = authenticate_tranche(manifest_path, ledger_path)

    class Fetch:
        def __call__(self, url: str) -> bytes:
            return bodies[url]
        def retrieval_evidence(self, url: str) -> dict[str, object]:
            body = bodies[url]
            return {"requested_url": url, "final_url": url, "http_status": 200, "byte_length": len(body), "sha256": sha256(body).hexdigest(), "method": "bounded_exact_url_get"}

    acquired = acquire_frozen_documents(manifest, ledger, tmp_path / "acquired", Fetch())
    assert len(acquired) == 2
    report = acquisition_report(manifest, ledger, acquired)
    encoded = _canonical(report)
    assert b"authored inline" not in encoded and report["provider_bodies_persisted_in_report"] is False
    assert report["filing_dispositions"] == {"loaded": 1, "explicit_absence": 1}

    class Changed(Fetch):
        def __call__(self, url: str) -> bytes:
            return bodies[url] + b"x"

    with pytest.raises(AcquisitionIdentityError):
        acquire_frozen_documents(manifest, ledger, tmp_path / "changed", Changed())

    class Redirected(Fetch):
        def retrieval_evidence(self, url: str) -> dict[str, object]:
            evidence = super().retrieval_evidence(url)
            evidence["final_url"] = "https://example.invalid/forged"
            return evidence

    with pytest.raises(AcquisitionIdentityError):
        acquire_frozen_documents(manifest, ledger, tmp_path / "redirected", Redirected())


def test_build_load_is_per_filing_cik_and_sql_has_no_batch_wide_gatos_authority(tmp_path: Path) -> None:
    manifest_path, ledger_path, bodies = _manifest_and_ledger(tmp_path)
    manifest, ledger = authenticate_tranche(manifest_path, ledger_path)

    class Fetch:
        def __call__(self, url: str) -> bytes:
            return bodies[url]
        def retrieval_evidence(self, url: str) -> dict[str, object]:
            body = bodies[url]
            return {"requested_url": url, "final_url": url, "http_status": 200, "byte_length": len(body), "sha256": sha256(body).hexdigest(), "method": "bounded_exact_url_get"}

    acquired = acquire_frozen_documents(manifest, ledger, tmp_path / "acquired", Fetch())
    load = build_filing_load(ledger["filing_acts"][0], manifest["package_results"][0], acquired)
    assert (load.cik, load.issuer_name) == ("0000000001", "Authored Issuer")
    assert any(item.inline_scale == 6 and item.inline_sign == "-" for item in load.report.occurrences)
    sql = _build_postgresql_sql((load,), "2026-08-18T00:00:00Z")
    assert "0000000001" in sql and "Authored Issuer" in sql
    assert "Gatos Silver, Inc." not in sql

    with pytest.raises(TrancheAuthenticationError, match="package identity"):
        build_filing_load(
            {**ledger["filing_acts"][0], "cik": "0000000002"},
            manifest["package_results"][0], acquired,
        )
    with pytest.raises(TrancheAuthenticationError, match="package identity"):
        build_filing_load(
            ledger["filing_acts"][0],
            {**manifest["package_results"][0], "form": "10-Q"}, acquired,
        )

    source_url = next(url for url in acquired if url.endswith("issuer.htm"))
    original_body = bodies[source_url]
    acquired[source_url].local_path.write_bytes(original_body + b"post-acquisition-drift")
    with pytest.raises(AcquisitionIdentityError, match="drifted after acquisition"):
        build_filing_load(ledger["filing_acts"][0], manifest["package_results"][0], acquired)

    def coherent_source(body: bytes):
        acquired[source_url].local_path.write_bytes(body)
        digest = sha256(body).hexdigest()
        package = manifest["package_results"][0]
        documents = [
            {**item, "byte_length": len(body), "sha256": digest}
            if item["url"] == source_url else item
            for item in package["documents"]
        ]
        return ({**package, "documents": documents},
                {**acquired, source_url: replace(acquired[source_url], byte_length=len(body), sha256=digest)})

    bad_cik_package, bad_cik_acquired = coherent_source(
        original_body.replace(b"0000000001", b"0000000002")
    )
    with pytest.raises(AcquisitionIdentityError, match="DEI CIK"):
        build_filing_load(ledger["filing_acts"][0], bad_cik_package, bad_cik_acquired)
    bad_form_package, bad_form_acquired = coherent_source(
        original_body.replace(b">10-K</ix:nonNumeric>", b">10-Q</ix:nonNumeric>")
    )
    with pytest.raises(AcquisitionIdentityError, match="DEI document type"):
        build_filing_load(ledger["filing_acts"][0], bad_form_package, bad_form_acquired)
    acquired[source_url].local_path.write_bytes(original_body)

    amendment = replace(load, accession="0000000001-24-000002", report=replace(load.report, accession="0000000001-24-000002"), relationship_original_accession=load.accession, relationship_status="proposed")
    amendment_sql = _build_postgresql_sql((amendment,), "2026-08-18T00:00:00Z")
    assert "filing_relationship_revision" in amendment_sql
    assert "'proposed'" in amendment_sql
    assert "'restates'" not in amendment_sql


def test_bounded_loader_attribution_timeout_reconciliation_and_deadline(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    manifest_path, ledger_path, bodies = _manifest_and_ledger(tmp_path)
    manifest, ledger = authenticate_tranche(manifest_path, ledger_path)

    class Fetch:
        def __init__(self) -> None:
            self.evidence: dict[str, dict[str, object]] = {}

        def __call__(self, url: str) -> bytes:
            body = bodies[url]
            self.evidence[url] = {
                "requested_url": url, "final_url": url, "http_status": 200,
                "byte_length": len(body), "sha256": sha256(body).hexdigest(),
                "method": "bounded_exact_url_get",
            }
            return body

        def retrieval_evidence(self, url: str) -> dict[str, object]:
            return self.evidence[url]

    load = build_filing_load(
        ledger["filing_acts"][0], manifest["package_results"][0],
        acquire_frozen_documents(manifest, ledger, tmp_path / "provider-bounded", Fetch()),
    )
    sql = _build_postgresql_sql(
        (load,), "2026-08-18T00:00:00Z", application_name="task223-exact-app",
        statement_timeout_ms=2000, lock_timeout_ms=500,
        idle_transaction_timeout_ms=1000, governance_closure=False,
    )
    assert sql.index("SET LOCAL application_name") < sql.index("SET CONSTRAINTS ALL DEFERRED")
    assert "SET LOCAL statement_timeout='2000ms'" in sql
    assert "SET LOCAL lock_timeout='500ms'" in sql
    assert "SET LOCAL idle_in_transaction_session_timeout='1000ms'" in sql
    assert "INSERT INTO corporate_reporting.knowledge_snapshot" not in sql
    assert "INSERT INTO corporate_reporting.concept_mapping_revision" not in sql
    assert "INSERT INTO corporate_reporting.corporate_release_eligibility_revision" not in sql

    captured: dict[str, object] = {}

    def timeout_run(*args: object, **kwargs: object) -> object:
        captured.update(kwargs)
        timeout = kwargs["timeout"]
        assert isinstance(timeout, (int, float))
        raise subprocess.TimeoutExpired(cmd="psql", timeout=timeout)

    monkeypatch.setattr(loader_module.subprocess, "run", timeout_run)
    monkeypatch.setattr(loader_module, "_reconcile_timed_out_backend", lambda **_kwargs: "canceled")
    with pytest.raises(PostgreSQLLoadTimeout, match="reconciliation=canceled"):
        load_corporate_filings_to_postgres(
            (load,), database_url="disposable", knowledge_cutoff="2026-08-18T00:00:00Z",
            application_name="task223-exact-app", statement_timeout_seconds=2,
            lock_timeout_seconds=.5, idle_transaction_timeout_seconds=1,
            client_timeout_seconds=3, governance_closure=False,
        )
    assert captured["timeout"] == 3
    assert captured["env"]["PGAPPNAME"] == "task223-exact-app"  # type: ignore[index]
    assert "SET LOCAL application_name='task223-exact-app'" in str(captured["input"])

    with pytest.raises(TimeoutError, match="whole-campaign deadline"):
        load_proof_campaign(
            (load,), database_url="unused", knowledge_cutoff="2026-08-18T00:00:00Z",
            deadline=0.0,
        )


def test_runner_target_boundary_rejects_every_noncanonical_or_unsafe_shape(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    valid_a = "macroforge_task223_r4a_1787071792_20113"
    valid_b = "macroforge_task223_r4b_1787071792_20113"
    invalid_sets: tuple[object, ...] = (
        (), (valid_a,), (valid_a, valid_b, "macroforge_task223_r4c_1787071792_20113"),
        (valid_a, valid_a), ("macroforge", valid_b), ("postgres", valid_b),
        ("template0", valid_b), ("template1", valid_b), ("arbitrary", valid_b),
        ('"' + valid_a + '"', valid_b), (valid_a + ";SELECT 1", valid_b),
        ("MacroForge_task223_r4a_1787071792_20113", valid_b),
        (valid_a, "macroforge_task223_not-disposable"),
    )
    connect_calls: list[str] = []
    monkeypatch.setattr(runner_module, "_authenticate_database_target",
                        lambda target, **_kwargs: connect_calls.append(target))
    for targets in invalid_sets:
        with pytest.raises(ValueError, match="TASK-223 database targets"):
            runner_module.validate_database_targets(targets)  # type: ignore[arg-type]
    assert connect_calls == []

    class Once:
        def __init__(self) -> None:
            self.iterations = 0
        def __iter__(self) -> Iterator[str]:
            self.iterations += 1
            if self.iterations > 1:
                raise AssertionError("target iterable consumed more than once")
            yield valid_a
            yield valid_b

    once = Once()
    assert runner_module.validate_database_targets(once) == (valid_a, valid_b)
    assert once.iterations == 1


def test_runner_invalid_target_fails_before_status_report_or_source_work(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    status = tmp_path / "status.jsonl"
    report = tmp_path / "report.json"
    source_calls: list[str] = []
    monkeypatch.setattr(
        runner_module, "authenticate_tranche",
        lambda *_args, **_kwargs: source_calls.append("source") or ({}, {}),
    )
    monkeypatch.setattr(sys, "argv", [
        "run_sec_corporate_proof_tranche.py",
        "--manifest", str(tmp_path / "missing-manifest.json"),
        "--ledger", str(tmp_path / "missing-ledger.json"),
        "--temporary-provider-root", str(tmp_path / "provider"),
        "--database", "macroforge",
        "--output", str(report), "--status-file", str(status),
        "--knowledge-cutoff", "2026-08-18T00:00:00Z",
    ])
    with pytest.raises(ValueError, match="TASK-223 database targets"):
        runner_module.main()
    assert source_calls == []
    assert not status.exists()
    assert not report.exists()


def test_runner_authenticates_actual_database_identity_and_defeats_redirects(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    valid_a = "macroforge_task223_r4a_1787071792_20113"
    valid_b = "macroforge_task223_r4b_1787071792_20113"
    calls: list[tuple[object, ...]] = []

    def redirected(argv: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        calls.append((tuple(argv), kwargs.get("input"), kwargs.get("env")))
        return subprocess.CompletedProcess(argv, 0, stdout="macroforge\n", stderr="")

    monkeypatch.setattr(runner_module.subprocess, "run", redirected)
    with pytest.raises(ValueError, match="current_database"):
        runner_module.authenticate_database_targets((valid_a, valid_b))
    assert len(calls) == 1
    assert valid_a in calls[0][0]
    assert "current_database()" in str(calls[0][1])
    assert "PGDATABASE" not in calls[0][2]  # type: ignore[operator]


def test_campaign_budget_reserves_full_reconciliation_and_terminal_windows(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    assert runner_module.RECONCILIATION_QUERY_TIMEOUT_SECONDS == 15.0
    assert runner_module.CANCEL_POLL_SECONDS == 15.0
    assert runner_module.TERMINATE_POLL_SECONDS == 15.0
    expected_reconciliation = (
        4 * runner_module.RECONCILIATION_QUERY_TIMEOUT_SECONDS
        + runner_module.CANCEL_POLL_SECONDS + runner_module.RECONCILIATION_QUERY_TIMEOUT_SECONDS
        + runner_module.TERMINATE_POLL_SECONDS + runner_module.RECONCILIATION_QUERY_TIMEOUT_SECONDS
        + runner_module.RECONCILIATION_SCHEDULING_MARGIN_SECONDS
    )
    assert runner_module.RECONCILIATION_RESERVE_SECONDS == expected_reconciliation
    hard, reconciliation, work = runner_module.campaign_deadlines(100.0)
    assert hard == 100.0 + 7200.0
    assert work < reconciliation < hard
    assert reconciliation == hard - runner_module.TERMINAL_EVIDENCE_RESERVE_SECONDS
    assert work == reconciliation - runner_module.RECONCILIATION_RESERVE_SECONDS

    manifest_path, ledger_path, bodies = _manifest_and_ledger(tmp_path)
    manifest, ledger = authenticate_tranche(manifest_path, ledger_path)

    class Fetch:
        def __call__(self, url: str) -> bytes:
            return bodies[url]
        def retrieval_evidence(self, url: str) -> dict[str, object]:
            body = bodies[url]
            return {
                "requested_url": url, "final_url": url, "http_status": 200,
                "byte_length": len(body), "sha256": sha256(body).hexdigest(),
                "method": "bounded_exact_url_get",
            }

    load = build_filing_load(
        ledger["filing_acts"][0], manifest["package_results"][0],
        acquire_frozen_documents(
            manifest, ledger, tmp_path / "budget-provider", Fetch()
        ),
    )
    invoked: list[str] = []
    monkeypatch.setattr(loader_module.subprocess, "run",
                        lambda *_args, **_kwargs: invoked.append("psql"))
    now = time.monotonic()
    with pytest.raises(PostgreSQLLoadTimeout, match="work deadline"):
        load_proof_campaign(
            (load,), database_url="macroforge_task223_r4a_1787071792_20113",
            knowledge_cutoff="2026-08-18T00:00:00Z", work_deadline=now + 149.999,
            reconciliation_deadline=now + 275.0, hard_deadline=now + 280.0,
        )
    assert invoked == []


def test_reconciliation_deadline_covers_cancel_terminate_and_fails_closed(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    clock = [100.0]
    monkeypatch.setattr(loader_module.time, "monotonic", lambda: clock[0])
    monkeypatch.setattr(loader_module.time, "sleep", lambda seconds: clock.__setitem__(0, clock[0] + seconds))
    outputs = iter(("41\n", "t\n", "41\n", "41\n", "41\n", "41\n", "t\n", ""))
    calls: list[tuple[str, float]] = []

    def run(_argv: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        timeout = float(kwargs["timeout"])
        assert timeout <= 15.0
        calls.append((str(kwargs["input"]), timeout))
        clock[0] += min(timeout, 5.0)
        return subprocess.CompletedProcess([], 0, stdout=next(outputs), stderr="")

    monkeypatch.setattr(loader_module.subprocess, "run", run)
    disposition = loader_module._reconcile_timed_out_backend(
        database_url="macroforge_task223_r4a_1787071792_20113", psql_path="psql",
        application_name="macroforge-task223-exact-app", reconciliation_deadline=225.0,
    )
    assert disposition == "terminated"
    assert any("pg_cancel_backend" in statement for statement, _ in calls)
    assert any("pg_terminate_backend" in statement for statement, _ in calls)
    assert all("datname=current_database()" in statement for statement, _ in calls)
    assert all("application_name='macroforge-task223-exact-app'" in statement for statement, _ in calls)
    assert clock[0] <= 225.0

    clock[0] = 225.0
    with pytest.raises(PostgreSQLLoadTimeout, match="reconciliation deadline"):
        loader_module._reconcile_timed_out_backend(
            database_url="macroforge_task223_r4a_1787071792_20113", psql_path="psql",
            application_name="macroforge-task223-exact-app", reconciliation_deadline=225.0,
        )


@POSTGRES_ONLY
def test_postgresql_source_specific_multicik_replay_relationship_and_per_filing_rollback(
    tmp_path: Path, task223_postgres: str,
) -> None:
    manifest_path, ledger_path, bodies = _manifest_and_ledger(tmp_path)
    manifest, ledger = authenticate_tranche(manifest_path, ledger_path)

    class Fetch:
        def __call__(self, url: str) -> bytes:
            return bodies[url]
        def retrieval_evidence(self, url: str) -> dict[str, object]:
            body = bodies[url]
            return {"requested_url": url, "final_url": url, "http_status": 200,
                    "byte_length": len(body), "sha256": sha256(body).hexdigest(),
                    "method": "bounded_exact_url_get"}

    acquired = acquire_frozen_documents(manifest, ledger, tmp_path / "acquired", Fetch())
    first = build_filing_load(ledger["filing_acts"][0], manifest["package_results"][0], acquired)
    cutoff = "2026-08-18T00:00:00Z"

    timeout_app = f"macroforge-task223-timeout-{uuid.uuid4().hex[:12]}"
    with pytest.raises(PostgreSQLLoadError, match="statement timeout|canceling statement"):
        load_corporate_filings_to_postgres(
            (first,), database_url=task223_postgres, knowledge_cutoff=cutoff,
            application_name=timeout_app, statement_timeout_seconds=.01,
            lock_timeout_seconds=.001, idle_transaction_timeout_seconds=1,
            client_timeout_seconds=2, governance_closure=False,
        )
    assert _psql(
        task223_postgres,
        "SELECT count(*) FROM corporate_reporting.filing_submission;",
    ) == "0"
    assert _psql(
        task223_postgres,
        "SELECT count(*) FROM pg_stat_activity WHERE application_name="
        + "'" + timeout_app + "';",
    ) == "0"

    first_result = load_corporate_filings_to_postgres(
        (first,), database_url=task223_postgres, knowledge_cutoff=cutoff, governance_closure=False,
    )
    progress: list[dict[str, object]] = []
    replay_dispositions = load_proof_campaign(
        (first,), database_url=task223_postgres, knowledge_cutoff=cutoff,
        deadline=time.monotonic() + 30, campaign_id="test-campaign",
        phase="replay", progress=progress.append,
    )
    assert replay_dispositions[0]["replay_fingerprint"] == first_result.replay_fingerprint
    assert [item["event"] for item in progress] == [
        "filing_load_started", "filing_load_committed",
    ]
    assert str(progress[0]["application_name"]).startswith("macroforge-task223-replay-")
    for absence in ledger["explicit_absences"]:
        cik = str(absence["cik"]).replace("'", "''")
        assert _psql(task223_postgres, f"""
          SELECT count(*) FROM corporate_reporting.fact_occurrence o
          JOIN corporate_reporting.filing_submission f USING(filing_id)
          JOIN corporate_reporting.entity_identifier i ON i.entity_id=f.filer_entity_id
          WHERE i.scheme='sec:cik' AND i.normalized_value='{cik}';
        """) == "0"

    second_path = tmp_path / "issuer-two.htm"
    second_body = bodies[next(url for url in bodies if url.endswith("issuer.htm"))].replace(
        b"0000000001", b"0000000002",
    )
    second_path.write_bytes(second_body)
    second_accession = "0000000002-24-000001"
    second_report = parse_inline_instance(
        second_path, accession=second_accession, dts_manifest_sha256=first.dts_manifest_sha256,
    )
    second_documents = tuple(
        replace(document, source_url=document.source_url.replace("/1/", "/2/"),
                byte_length=len(second_body), sha256=sha256(second_body).hexdigest(),
                local_evidence_locator=str(second_path))
        if document.sha256 == first.report.source_sha256 else document
        for document in first.documents
    )
    second = replace(
        first, accession=second_accession, cik="0000000002", issuer_name="Second Issuer",
        source_manifest_sha256="2" * 64, report=second_report, documents=second_documents,
        accepted_at="2024-02-01T12:00:00Z", filed_date="2024-02-01",
    )
    second_result = load_corporate_filings_to_postgres(
        (second,), database_url=task223_postgres, knowledge_cutoff=cutoff, governance_closure=False,
    )
    stable_before_replay = stable_postgres_state(task223_postgres)
    assert load_corporate_filings_to_postgres(
        (second,), database_url=task223_postgres, knowledge_cutoff=cutoff, governance_closure=False,
    ) == second_result
    assert stable_postgres_state(task223_postgres) == stable_before_replay

    amendment_accession = "0000000002-24-000002"
    amendment_report = parse_inline_instance(
        second_path, accession=amendment_accession, dts_manifest_sha256=first.dts_manifest_sha256,
    )
    amendment = replace(
        second, accession=amendment_accession, form_type="10-K/A", amendment_flag=True,
        source_manifest_sha256="3" * 64, report=amendment_report,
        accepted_at="2024-03-01T12:00:00Z", filed_date="2024-03-01",
        relationship_original_accession=second_accession, relationship_status="proposed",
    )
    load_corporate_filings_to_postgres(
        (amendment,), database_url=task223_postgres, knowledge_cutoff=cutoff, governance_closure=False,
    )
    assert _psql(task223_postgres, """
      SELECT json_build_array(
        (SELECT count(*) FROM corporate_reporting.reporting_entity),
        (SELECT count(*) FROM corporate_reporting.filing_submission),
        (SELECT count(*) FROM corporate_reporting.fact_occurrence WHERE inline_scale IS NOT NULL),
        (SELECT count(*) FROM corporate_reporting.fact_occurrence WHERE inline_sign IS NOT NULL),
        (SELECT count(*) FROM corporate_reporting.fact_occurrence o
          JOIN corporate_reporting.fact_occurrence_interpretation i USING (fact_occurrence_id)
          WHERE (o.inline_format IS NOT NULL OR o.inline_scale IS NOT NULL OR o.inline_sign IS NOT NULL)
            AND i.normalized_numeric IS NOT NULL),
        (SELECT count(*) FROM corporate_reporting.filing_relationship_revision
          WHERE relationship_type='amends' AND assertion_status='proposed'),
        (SELECT count(*) FROM corporate_reporting.corporate_release),
        (SELECT count(*) FROM corporate_reporting.corporate_rights_revision));
    """) == "[2, 3, 3, 3, 0, 1, 0, 0]"

    # Source evidence is deliberately non-authoritative. Proposed relationships
    # remain evidence and cannot create mapping, snapshot, rights, eligibility,
    # release, publication, redistribution, or delivery authority.
    assert _psql(task223_postgres, """
      SELECT json_build_array(
        (SELECT count(*) FROM corporate_reporting.knowledge_snapshot),
        (SELECT count(*) FROM corporate_reporting.knowledge_snapshot_member),
        (SELECT count(*) FROM corporate_reporting.concept_mapping_revision),
        (SELECT count(*) FROM corporate_reporting.expected_selection_revision),
        (SELECT count(*) FROM corporate_reporting.corporate_release_eligibility_revision),
        (SELECT count(*) FROM corporate_reporting.corporate_release),
        (SELECT count(*) FROM corporate_reporting.corporate_release_item),
        (SELECT count(*) FROM corporate_reporting.corporate_rights_revision),
        (SELECT count(*) FROM corporate_reporting.corporate_quality_gate_revision),
        (SELECT count(*) FROM corporate_reporting.corporate_publication_reservation),
        (SELECT count(*) FROM corporate_reporting.corporate_publication_completion));
    """) == "[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]"
    assert _psql(
        task223_postgres,
        "SELECT assertion_status FROM corporate_reporting.filing_relationship_revision;",
    ) == "proposed"
    authority = CorporateAuthorityRef(uuid.uuid4())
    store = PostgresCorporateAuthorityStore(task223_postgres)
    with pytest.raises(AmbiguousSelection, match="missing, inactive, or incomplete"):
        store.resolve(authority)
    publication_target = tmp_path / "must-not-publish.json"
    with pytest.raises(AmbiguousSelection, match="missing, inactive, or incomplete"):
        publish_database_anchored(authority=authority, store=store, target=publication_target)
    assert not publication_target.exists()
    assert _psql(
        task223_postgres,
        "SELECT (SELECT count(*) FROM corporate_reporting.corporate_publication_reservation)"
        " || ',' || (SELECT count(*) FROM corporate_reporting.corporate_publication_completion);",
    ) == "0,0"

    before = _psql(task223_postgres, "SELECT count(*) FROM corporate_reporting.filing_submission;")
    with pytest.raises(IdentityConflict):
        load_corporate_filings_to_postgres(
            (replace(first, source_manifest_sha256="f" * 64),),
            database_url=task223_postgres, knowledge_cutoff=cutoff, governance_closure=False,
        )
    assert _psql(task223_postgres, "SELECT count(*) FROM corporate_reporting.filing_submission;") == before

    failed_accession = "0000000002-24-000003"
    failed_report = parse_inline_instance(
        second_path, accession=failed_accession, dts_manifest_sha256=first.dts_manifest_sha256,
    )
    failed = replace(
        second, accession=failed_accession, source_manifest_sha256="4" * 64,
        report=failed_report, accepted_at="2024-04-01T12:00:00Z", filed_date="2024-04-01",
        relationship_original_accession="0000000002-20-999999", relationship_status="proposed",
    )
    with pytest.raises(PostgreSQLLoadError):
        load_corporate_filings_to_postgres(
            (failed,), database_url=task223_postgres, knowledge_cutoff=cutoff, governance_closure=False,
        )
    assert _psql(
        task223_postgres,
        f"SELECT count(*) FROM corporate_reporting.filing_submission WHERE accession='{failed_accession}';",
    ) == "0"
