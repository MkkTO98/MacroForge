from __future__ import annotations

import datetime as dt
import hashlib
import json
import shutil
import urllib.request
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET


BIS_SOURCE_CODE = "BIS_PUBLIC_SDMX_API"
BIS_SOURCE_NAME = "Bank for International Settlements public SDMX API"
BIS_SOURCE_HOME_URL = "https://www.bis.org/"
BIS_SNAPSHOT_MEANING = "acquired BIS SDMX response snapshot/as-of identity from Prepared timestamp, not official publication release"


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def attr_hash(attrs: dict[str, Any]) -> str:
    return sha256_bytes(json.dumps(attrs, sort_keys=True, separators=(",", ":")).encode("utf-8"))


def rel(path: Path, project_root: Path) -> str:
    try:
        return path.relative_to(project_root).as_posix()
    except ValueError:
        return path.as_posix()


def prepared_to_snapshot_key(dataflow_code: str, prepared: str | None) -> str:
    """Build a BIS acquired-response snapshot key from provider `Prepared` evidence.

    The key deliberately excludes query windows, run keys, campaign scope, and
    official-publication language. TASK-213/TASK-214/TASK-215 evidence supports
    the provider `Prepared` timestamp as the stable acquired-response identity;
    missing or malformed Prepared evidence blocks deterministic snapshot identity
    instead of falling back to speculative alternatives.
    """
    if not prepared:
        raise ValueError("cannot derive BIS snapshot identity without provider Prepared timestamp")
    try:
        parsed = dt.datetime.strptime(prepared, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError as exc:
        raise ValueError(f"malformed BIS Prepared timestamp: {prepared!r}") from exc
    slug = dataflow_code.lower().replace("_", "-")
    token = parsed.strftime("%Y%m%dt%H%M%Sz").lower()
    return f"bis-{slug}-snapshot-prepared-{token}"


def provider_metadata(root: ET.Element, *, dataflow_code: str, dataflow_version: str, raw_meta: dict[str, Any]) -> dict[str, Any]:
    header = next((e for e in root.iter() if local_name(e.tag) == "Header"), None)
    dataset = next((e for e in root.iter() if local_name(e.tag) == "DataSet"), None)

    def child_text(local: str) -> str | None:
        if header is None:
            return None
        for child in header:
            if local_name(child.tag) == local and child.text:
                return child.text.strip()
        return None

    sender = next((e for e in header.iter() if local_name(e.tag) == "Sender"), None) if header is not None else None
    structure = next((e for e in header.iter() if local_name(e.tag) == "Structure"), None) if header is not None else None
    dataset_attrs = {}
    if dataset is not None:
        keep = {"UNIT_MULT", "UNIT_MEASURE", "COLLECTION", "DECIMALS"}
        dataset_attrs = {local_name(k): dataset.attrib[k] for k in sorted(dataset.attrib) if local_name(k) in keep}
    return {
        "message_id": child_text("ID"),
        "prepared": child_text("Prepared"),
        "sender": sender.attrib.get("id") if sender is not None else None,
        "dataset_action": child_text("DataSetAction"),
        "dataset_id": child_text("DataSetID"),
        "extracted": child_text("Extracted"),
        "reporting_begin": child_text("ReportingBegin"),
        "reporting_end": child_text("ReportingEnd"),
        "structure_id": structure.attrib.get("structureID") if structure is not None else None,
        "structure_namespace": structure.attrib.get("namespace") if structure is not None else None,
        "dimension_at_observation": structure.attrib.get("dimensionAtObservation") if structure is not None else None,
        "dataflow": {"agency_id": "BIS", "id": dataflow_code, "version": dataflow_version},
        "dataset_attributes": dataset_attrs,
        "http_status": raw_meta.get("http_status"),
        "content_type": raw_meta.get("content_type"),
        "acquired_at_utc": raw_meta.get("acquired_at_utc"),
    }


def bis_data_url(dataflow_code: str, dataflow_version: str, key: str, *, start_period: str, end_period: str) -> str:
    return f"https://stats.bis.org/api/v2/data/dataflow/BIS/{dataflow_code}/{dataflow_version}/{key}?startPeriod={start_period}&endPeriod={end_period}"


def fetch_to_attempt(*, url: str, raw_dir: Path, active_raw_path: Path, active_meta_path: Path, task_id: str, request_parameters: dict[str, Any], user_agent: str, timeout: int = 120) -> dict[str, Any]:
    attempt_id = dt.datetime.now(dt.timezone.utc).strftime("attempt-%Y%m%dT%H%M%SZ")
    attempt_dir = raw_dir / "_attempts" / attempt_id
    attempt_dir.mkdir(parents=True, exist_ok=True)
    acquired_at = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    req = urllib.request.Request(url, headers={"User-Agent": user_agent})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            raw = response.read()
            status = response.status
            headers = dict(response.headers.items())
    except Exception as exc:
        err = {"task": task_id, "status": "acquisition_error", "source_url": url, "acquired_at_utc": acquired_at, "error_type": type(exc).__name__, "error": str(exc)}
        (attempt_dir / "acquisition-error.json").write_text(json.dumps(err, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        raise
    (attempt_dir / active_raw_path.name).write_bytes(raw)
    meta = {
        "task": task_id,
        "status": "acquired",
        "source_url": url,
        "request_parameters": request_parameters,
        "acquired_at_utc": acquired_at,
        "http_status": status,
        "headers": headers,
        "raw_sha256": sha256_bytes(raw),
        "raw_bytes": len(raw),
        "attempt_id": attempt_id,
        "content_type": headers.get("Content-Type"),
    }
    (attempt_dir / active_meta_path.name).write_text(json.dumps(meta, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tmp_dir = raw_dir / ".active.tmp"
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)
    tmp_dir.mkdir(parents=True)
    (tmp_dir / active_raw_path.name).write_bytes(raw)
    (tmp_dir / active_meta_path.name).write_text(json.dumps(meta, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    active_dir = active_raw_path.parent
    if active_dir.exists():
        shutil.rmtree(active_dir)
    tmp_dir.replace(active_dir)
    return meta


def quarter_periods(start_period: str, end_period: str) -> list[tuple[int, int, str, str, str, str]]:
    out: list[tuple[int, int, str, str, str, str]] = []
    start_y, start_q = int(start_period[:4]), int(start_period[-1])
    end_y, end_q = int(end_period[:4]), int(end_period[-1])
    y, q = start_y, start_q
    while (y, q) <= (end_y, end_q):
        provider = f"{y}-Q{q}"
        start_month = 1 + (q - 1) * 3
        end_month = start_month + 2
        end_day = 31 if end_month in {3, 12} else 30
        out.append((y, q, provider, provider, f"{y}-{start_month:02d}-01", f"{y}-{end_month:02d}-{end_day:02d}"))
        q += 1
        if q == 5:
            y += 1
            q = 1
    return out


def series_key_without_territory(attrs: dict[str, str], dimensions: list[str], territory_dimension: str) -> tuple[str, ...]:
    return tuple(attrs.get(dim, "") for dim in dimensions if dim != territory_dimension)
