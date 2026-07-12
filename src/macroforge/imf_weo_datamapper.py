from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Iterable

SOURCE_CODE = "IMF_WEO_DATAMAPPER_API_V1"
SOURCE_NAME = "IMF WEO DataMapper API v1"
SOURCE_HOME_URL = "https://www.imf.org/en/Publications/WEO"
PROVIDER_DATASET_CODE = "IMF:WEO:DATAMAPPER"
API_SURFACE = "IMF DataMapper API v1"
VALUE_STATUS_UNSPECIFIED = "provider_current_weo_value_status_unspecified"
CONSERVATIVE_COUNTRY_CHUNK_SIZE = 25


def slug_text(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def slug_unit(unit: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", unit.strip().upper()).strip("_") or "UNSPECIFIED"


def decimal_precision(value: Any) -> int:
    if value is None:
        return 0
    text = str(value)
    return len(text.split(".", 1)[1]) if "." in text else 0


def release_evidence_from_indicator_meta(
    indicators: dict[str, Any], acquired_at: str | None, api_payloads: Iterable[Any]
) -> dict[str, Any]:
    sources = sorted({str(v.get("source")) for v in indicators.values() if isinstance(v, dict) and v.get("source")})
    last_modified = sorted({str(v.get("last-modified")) for v in indicators.values() if isinstance(v, dict) and v.get("last-modified")})
    versions = sorted({str(p.get("version")) for p in api_payloads if isinstance(p, dict) and p.get("version") is not None})
    release_source = sources[0] if len(sources) == 1 else "unknown-weo-release"
    release_key = slug_text(release_source) if release_source != "unknown-weo-release" else "unknown-weo-release-" + hashlib.sha256(json.dumps(sources, sort_keys=True).encode()).hexdigest()[:12]
    return {
        "provider_release_source": release_source,
        "release_key": release_key,
        "provider_publication_date": None,
        "indicator_last_modified_values": last_modified,
        "api_identity": {"surface": "IMF DataMapper API", "versions": versions or ["1"]},
        "api_exposes_edition_metadata_directly": bool(sources),
        "api_exposes_row_level_value_status": False,
        "acquired_at_utc": acquired_at,
    }


def run_key_for_release(prefix: str, release_key: str) -> str:
    return f"{prefix}-{release_key}"


def explicit_missing_reason(year_present: bool, value: Any) -> str | None:
    if value is not None:
        return None
    return "year_key_absent_from_otherwise_valid_country_indicator_series" if not year_present else "explicit_null_or_missing_value_in_country_indicator_series"


def canonical_indicator_id(indicator_code: str) -> str:
    return f"IMF_WEO:{indicator_code}"


def attribute_hash(attributes: dict[str, Any]) -> str:
    return hashlib.sha256(json.dumps(attributes, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def partition_rows_by_indicator(norm: dict[str, Any], *, output_dir: Path, project_root: Path) -> dict[str, Any]:
    """Write deterministic indicator partitions and return a manifest.

    Contract is WEO/DataMapper-specific: rows must use TASK-209/211 normalized row keys.
    The function writes into output_dir supplied by caller; callers are responsible for using
    attempt-specific dirs then atomically promoting active manifests.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    partitions = []
    rows_by_indicator: dict[str, list[dict[str, Any]]] = {}
    for row in norm.get("rows", []):
        rows_by_indicator.setdefault(row["indicator_code"], []).append(row)
    total_rows = total_observed = total_missing = 0
    seen_keys: set[tuple[str, str, str]] = set()
    for indicator in sorted(rows_by_indicator):
        rows = sorted(rows_by_indicator[indicator], key=lambda r: (r["indicator_code"], r["territory_code"], r["provider_period_code"]))
        for row in rows:
            key = (row["indicator_code"], row["territory_code"], row["provider_period_code"])
            if key in seen_keys:
                raise ValueError(f"duplicate normalized WEO partition row key: {key}")
            seen_keys.add(key)
        payload = {k: v for k, v in norm.items() if k != "rows"}
        payload["partition_identity"] = indicator
        payload["rows"] = rows
        path = output_dir / f"{indicator}.json"
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n")
        observed = sum(1 for r in rows if r["observation_status"] == "observed")
        missing = sum(1 for r in rows if r["observation_status"] == "missing")
        territories = sorted({r["territory_code"] for r in rows})
        periods = sorted({r["provider_period_code"] for r in rows})
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        try:
            rel_path = path.relative_to(project_root).as_posix()
        except ValueError:
            rel_path = str(path)
        partitions.append({
            "partition_identity": indicator,
            "path": rel_path,
            "row_count": len(rows),
            "observed_count": observed,
            "explicit_missing_count": missing,
            "territory_count": len(territories),
            "territory_coverage": territories,
            "period_coverage": periods,
            "byte_size": path.stat().st_size,
            "sha256": digest,
        })
        total_rows += len(rows)
        total_observed += observed
        total_missing += missing
    if total_rows != norm.get("row_count"):
        raise ValueError(f"partition row total mismatch: {total_rows} != {norm.get('row_count')}")
    if total_observed != norm.get("observed_provider_value_count"):
        raise ValueError("partition observed total mismatch")
    if total_missing != norm.get("explicit_missing_fact_count"):
        raise ValueError("partition explicit-missing total mismatch")
    return {
        "partition_scheme": "indicator_code",
        "partition_count": len(partitions),
        "partitions": partitions,
        "partition_totals": {
            "row_count": total_rows,
            "observed_provider_value_count": total_observed,
            "explicit_missing_fact_count": total_missing,
        },
    }


def load_partitioned_rows(manifest: dict[str, Any], *, project_root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str]] = set()
    for part in sorted(manifest["partitions"], key=lambda p: p["partition_identity"]):
        path = project_root / part["path"]
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != part["sha256"]:
            raise ValueError(f"partition checksum mismatch: {part['path']}")
        payload = json.loads(path.read_text())
        part_rows = payload["rows"]
        if len(part_rows) != part["row_count"]:
            raise ValueError(f"partition row count mismatch: {part['path']}")
        for row in part_rows:
            key = (row["indicator_code"], row["territory_code"], row["provider_period_code"])
            if key in seen:
                raise ValueError(f"duplicate row across WEO partitions: {key}")
            seen.add(key)
            rows.append(row)
    rows.sort(key=lambda r: (r["indicator_code"], r["territory_code"], r["provider_period_code"]))
    return rows
