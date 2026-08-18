#!/usr/bin/env python3
"""Build the bounded TASK-222 Corporate Portfolio v1 manifest.

Provider bytes are held only in process memory.  The output contains normalized
metadata, URLs, lengths, hashes, relationships, dispositions, and compatibility
outcomes -- never SEC document bodies.
"""
from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import time
from typing import Any
import urllib.error
import urllib.request
from urllib.parse import urljoin

from macroforge.sec_corporate_portfolio import (
    ACCEPTANCE_CUTOFF,
    ALLOWED_FORMS,
    ISSUERS,
    PackageLimits,
    acquisition_url_allowed,
    build_portfolio_manifest,
    canonical_manifest_identity,
    enrich_package_result,
    validate_package,
)

ROOT = Path(__file__).resolve().parents[1]
SUBMISSIONS_ROOT = "https://data.sec.gov/submissions/"
ARCHIVES_ROOT = "https://www.sec.gov/Archives/edgar/data/"


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def configured_sec_identity() -> str:
    value = subprocess.run(
        ["git", "config", "--get", "macroforge.secUserAgent"],
        cwd=ROOT,
        check=False,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
    ).stdout.strip()
    suitable = 10 <= len(value) <= 256 and "@" in value and not any(ord(char) < 32 or ord(char) == 127 for char in value)
    if not suitable:
        raise RuntimeError("macroforge.secUserAgent is absent or structurally unsuitable")
    return value


class BoundedAcquisitionFailure(OSError):
    def __init__(self, reason: str) -> None:
        super().__init__(reason)
        self.reason = reason


class _PolicyRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Reject an out-of-policy redirect target before opening it."""

    def redirect_request(
        self,
        req: urllib.request.Request,
        fp: Any,
        code: int,
        msg: str,
        headers: Any,
        newurl: str,
    ) -> urllib.request.Request | None:
        target = urljoin(req.full_url, newurl)
        if not acquisition_url_allowed(target):
            raise BoundedAcquisitionFailure("request_policy_rejected")
        return super().redirect_request(req, fp, code, msg, headers, target)


class BoundedFetcher:
    def __init__(
        self,
        user_agent: str,
        *,
        minimum_interval_seconds: float = 0.12,
        max_response_bytes: int = 64 * 1024 * 1024,
        request_timeout_seconds: float = 10.0,
        max_attempts: int = 2,
    ) -> None:
        self._user_agent = user_agent
        self._minimum_interval = minimum_interval_seconds
        self._max_response_bytes = max_response_bytes
        self._request_timeout_seconds = request_timeout_seconds
        self._max_attempts = max_attempts
        self._opener = urllib.request.build_opener(_PolicyRedirectHandler())
        self._last_request = 0.0
        self._cache: dict[str, bytes] = {}
        self._failures: dict[str, str] = {}
        self.observations: dict[str, dict[str, Any]] = {}

    def __call__(self, url: str) -> bytes:
        if not acquisition_url_allowed(url):
            reason = "request_policy_rejected"
            self._failures[url] = reason
            raise BoundedAcquisitionFailure(reason)
        if url in self._cache:
            return self._cache[url]
        if url in self._failures:
            raise BoundedAcquisitionFailure(self._failures[url])
        reason = "network_failure"
        body: bytes | None = None
        final_url: str | None = None
        status: int | None = None
        for attempt in range(self._max_attempts):
            elapsed = time.monotonic() - self._last_request
            if elapsed < self._minimum_interval:
                time.sleep(self._minimum_interval - elapsed)
            request = urllib.request.Request(
                url,
                headers={
                    "User-Agent": self._user_agent,
                    "Accept-Encoding": "identity",
                    "Accept": "application/json,application/xhtml+xml,application/xml,text/html,*/*;q=0.1",
                },
            )
            try:
                with self._opener.open(request, timeout=self._request_timeout_seconds) as response:
                    response_url = response.geturl()
                    if not isinstance(response_url, str) or not acquisition_url_allowed(response_url):
                        reason = "request_policy_rejected"
                        raise BoundedAcquisitionFailure(reason)
                    final_url = response_url
                    candidate = response.read(self._max_response_bytes + 1)
                    if len(candidate) > self._max_response_bytes:
                        reason = "response_byte_bound"
                        raise BoundedAcquisitionFailure(reason)
                    body = candidate
                    status = response.status
                break
            except BoundedAcquisitionFailure as exc:
                reason = exc.reason
                self._failures[url] = reason
                raise
            except urllib.error.HTTPError as exc:
                reason = f"http_{exc.code}"
                if attempt + 1 == self._max_attempts:
                    self._failures[url] = reason
                    raise BoundedAcquisitionFailure(reason) from exc
            except (urllib.error.URLError, TimeoutError, OSError) as exc:
                reason = "timeout" if isinstance(getattr(exc, "reason", exc), TimeoutError) else "network_failure"
                if attempt + 1 == self._max_attempts:
                    self._failures[url] = reason
                    raise BoundedAcquisitionFailure(reason) from exc
            finally:
                self._last_request = time.monotonic()
        if body is None or final_url is None or status is None:
            raise AssertionError("bounded acquisition loop ended without result or failure")
        self._cache[url] = body
        self.observations[url] = {
            "requested_url": url,
            "final_url": final_url,
            "http_status": status,
            "byte_length": len(body),
            "sha256": sha256(body).hexdigest(),
            "method": "bounded_exact_url_get",
        }
        return body

    def retrieval_evidence(self, url: str) -> dict[str, Any]:
        """Return immutable metadata for the completed bounded acquisition."""

        return dict(self.observations[url])

    def discard_prefix(self, prefix: str) -> None:
        """Release unique filing bodies after their metadata has been recorded."""

        for url in [candidate for candidate in self._cache if candidate.startswith(prefix)]:
            del self._cache[url]


def submissions_rows(payload: dict[str, Any], cik: str) -> list[dict[str, Any]]:
    recent = payload["filings"]["recent"]
    keys = list(recent)
    return [{"cik": cik, **dict(zip(keys, values))} for values in zip(*(recent[key] for key in keys))]


def accession_base(cik: str, accession: str) -> str:
    return f"{ARCHIVES_ROOT}{int(cik)}/{accession.replace('-', '')}/"


def stripped(value: dict[str, Any]) -> dict[str, Any]:
    return {key: item for key, item in value.items() if key != "canonical_json"}


def build(
    output: Path,
    *,
    max_documents: int,
    max_external_documents: int,
    max_depth: int,
    max_total_bytes: int,
) -> dict[str, Any]:
    fetch = BoundedFetcher(configured_sec_identity())
    all_rows: list[dict[str, Any]] = []
    submissions_sources: list[dict[str, Any]] = []

    for issuer in ISSUERS:
        cik = issuer["cik"]
        url = f"{SUBMISSIONS_ROOT}CIK{cik}.json"
        body = fetch(url)
        payload = json.loads(body)
        all_rows.extend(submissions_rows(payload, cik))
        submissions_sources.append(fetch.observations[url])
        for file_record in payload.get("filings", {}).get("files", []):
            filing_from = str(file_record.get("filingFrom") or "")
            filing_to = str(file_record.get("filingTo") or "")
            if filing_to >= "2021-01-01" and filing_from <= "2026-06-30":
                supplemental_url = SUBMISSIONS_ROOT + str(file_record["name"])
                supplemental_body = fetch(supplemental_url)
                all_rows.extend(submissions_rows(json.loads(supplemental_body), cik))
                submissions_sources.append(fetch.observations[supplemental_url])

    accession_manifest = build_portfolio_manifest(all_rows)
    if not accession_manifest["corpus_accepted"]:
        payload = {
            "schema": "macroforge.corporate-portfolio-v1.validation-report.v1",
            "acceptance_cutoff": ACCEPTANCE_CUTOFF,
            "corpus_accepted": False,
            "accession_disposition_manifest": stripped(accession_manifest),
            "package_results": [],
            "package_outcome_counts": {},
            "source_observations": {"submissions": sorted(submissions_sources, key=lambda row: row["requested_url"]), "filing_indexes": []},
            "discrepancies": accession_manifest["discrepancies"],
        }
        payload["manifest_sha256"] = canonical_manifest_identity(payload)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(canonical_json(payload) + "\n")
        raise RuntimeError("current SEC submissions evidence differs from frozen corpus expectations")

    by_accession: dict[str, dict[str, Any]] = {}
    for row in all_rows:
        accession = str(row.get("accessionNumber") or "")
        if accession and str(row.get("form") or "") in ALLOWED_FORMS:
            by_accession.setdefault(accession, row)

    limits = PackageLimits(
        max_documents=max_documents,
        max_external_documents=max_external_documents,
        max_depth=max_depth,
        max_total_bytes=max_total_bytes,
    )
    package_results: list[dict[str, Any]] = []
    index_sources: list[dict[str, Any]] = []
    for position, filing_act in enumerate(accession_manifest["filing_acts"], start=1):
        accession = filing_act["accession"]
        source = by_accession[accession]
        filing = {
            "cik": filing_act["cik"],
            "accessionNumber": accession,
            "form": filing_act["form"],
            "reportDate": filing_act["report_date"],
            "acceptanceDateTime": filing_act["accepted_at"],
            "primaryDocument": filing_act["primary_document"],
            "isXBRL": int(source.get("isXBRL") or 0),
            "isInlineXBRL": int(source.get("isInlineXBRL") or 0),
        }
        index_url = accession_base(filing_act["cik"], accession) + "index.json"
        try:
            index_body = fetch(index_url)
            index = json.loads(index_body)
            index_sources.append(fetch.observations[index_url])
            result = validate_package(filing, index, fetch, limits=limits)
        except (urllib.error.URLError, TimeoutError, OSError, json.JSONDecodeError) as exc:
            result = validate_package(
                filing,
                {"directory": {"item": []}},
                fetch,
                limits=limits,
            )
            result["outcome"] = "acquisition failure"
            result["issues"] = [{"code": "index_acquisition_failed", "detail": type(exc).__name__, "url": index_url}]
            result.pop("canonical_json", None)
            result.pop("manifest_sha256", None)
            canonical = canonical_json(result)
            result["manifest_sha256"] = sha256(canonical.encode()).hexdigest()
        result = enrich_package_result(result, filing_act, fetch.observations.get(index_url))
        package_results.append(result)
        fetch.discard_prefix(accession_base(filing_act["cik"], accession))
        if position % 25 == 0 or position == 311:
            print(f"[{position:03d}/311] last_outcome={result['outcome']}", flush=True)

    outcome_counts = dict(sorted(Counter(result["outcome"] for result in package_results).items()))
    unresolved = [
        {
            "accession": result["accession"],
            "outcome": result["outcome"],
            "issues": result["issues"],
        }
        for result in package_results
        if result["outcome"] != "compatible"
    ]
    payload = {
        "schema": "macroforge.corporate-portfolio-v1.validation-report.v1",
        "acceptance_cutoff": ACCEPTANCE_CUTOFF,
        "corpus_accepted": True,
        "accession_disposition_manifest": stripped(accession_manifest),
        "package_results": sorted(package_results, key=lambda row: row["accession"]),
        "package_outcome_counts": outcome_counts,
        "unresolved_dependencies_and_incompatibilities": unresolved,
        "source_observations": {
            "submissions": sorted(submissions_sources, key=lambda row: row["requested_url"]),
            "filing_indexes": sorted(index_sources, key=lambda row: row["requested_url"]),
        },
        "provider_bodies_persisted": False,
        "governed_postgresql_touched": False,
        "discrepancies": [],
    }
    payload["manifest_sha256"] = canonical_manifest_identity(payload)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(canonical_json(payload) + "\n")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-documents", type=int, default=96)
    parser.add_argument("--max-external-documents", type=int, default=64)
    parser.add_argument("--max-depth", type=int, default=12)
    parser.add_argument("--max-total-bytes", type=int, default=256 * 1024 * 1024)
    args = parser.parse_args()
    report = build(
        args.output,
        max_documents=args.max_documents,
        max_external_documents=args.max_external_documents,
        max_depth=args.max_depth,
        max_total_bytes=args.max_total_bytes,
    )
    print(canonical_json({
        "output": str(args.output),
        "manifest_sha256": report["manifest_sha256"],
        "counts": report["accession_disposition_manifest"]["counts"],
        "package_outcome_counts": report["package_outcome_counts"],
        "unresolved_count": len(report["unresolved_dependencies_and_incompatibilities"]),
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
