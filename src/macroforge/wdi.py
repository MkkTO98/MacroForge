from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path
from typing import Any

DEFAULT_SOURCE = "World Bank WDI"
DEFAULT_EXPECTED_ROW_COUNT = 8


def _empty_to_none(value: Any) -> Any:
    return None if value == "" else value


def normalize_worldbank_payload(raw_payload: str | bytes, *, source: str = DEFAULT_SOURCE) -> list[dict[str, Any]]:
    """Normalize a World Bank API JSON payload into source-shaped observation rows.

    Expected API shape is `[metadata, observations]` as provided by the World Bank v2 API.
    This function intentionally preserves source field names such as `countryiso3code`
    because TASK-005 is a raw/staging evidence slice, not a curated loader.
    """
    if isinstance(raw_payload, bytes):
        raw_payload = raw_payload.decode("utf-8")
    payload = json.loads(raw_payload)
    if not isinstance(payload, list) or len(payload) != 2 or not isinstance(payload[1], list):
        raise ValueError("World Bank payload must be [metadata, observations]")

    rows: list[dict[str, Any]] = []
    for item in payload[1]:
        indicator = item.get("indicator") or {}
        country = item.get("country") or {}
        rows.append(
            {
                "source": source,
                "indicator_id": indicator.get("id"),
                "indicator_name": indicator.get("value"),
                "country_id": country.get("id"),
                "country_name": country.get("value"),
                "countryiso3code": item.get("countryiso3code"),
                "date": item.get("date"),
                "value": item.get("value"),
                "unit": _empty_to_none(item.get("unit")),
                "obs_status": _empty_to_none(item.get("obs_status")),
                "decimal": item.get("decimal"),
            }
        )
    return rows


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_smoke_result_from_bundle(bundle_dir: str | Path) -> dict[str, Any]:
    bundle = Path(bundle_dir)
    manifest_path = bundle / "manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

    raw_artifacts: list[dict[str, Any]] = []
    rows: list[dict[str, Any]] = []
    for entry in manifest["entries"]:
        raw_path = Path(entry["raw_path"])
        if not raw_path.exists():
            raw_path = bundle / raw_path.name
        payload = raw_path.read_bytes()
        observed_sha = hashlib.sha256(payload).hexdigest()
        if observed_sha != entry["sha256"]:
            raise ValueError(f"Checksum mismatch for {raw_path}: {observed_sha} != {entry['sha256']}")
        if len(payload) != entry["bytes"]:
            raise ValueError(f"Byte count mismatch for {raw_path}: {len(payload)} != {entry['bytes']}")
        normalized = normalize_worldbank_payload(payload, source=DEFAULT_SOURCE)
        if len(normalized) != entry["row_count"]:
            raise ValueError(f"Row count mismatch for {raw_path}: {len(normalized)} != {entry['row_count']}")
        rows.extend(normalized)
        raw_artifacts.append(
            {
                "indicator": entry["indicator"],
                "url": entry["url"],
                "status": entry["status"],
                "content_type": entry["content_type"],
                "bytes": entry["bytes"],
                "sha256": entry["sha256"],
                "row_count": entry["row_count"],
                "source_metadata": entry["metadata"],
                "raw_file": raw_path.name,
            }
        )

    return {
        "source": DEFAULT_SOURCE,
        "support_bundle": str(bundle),
        "created_at_utc": manifest.get("created_at_utc"),
        "countries": manifest["countries"],
        "indicators": manifest["indicators"],
        "date_range": manifest["date_range"],
        "expected_row_count": DEFAULT_EXPECTED_ROW_COUNT,
        "row_count": len(rows),
        "rows": rows,
        "raw_artifacts": raw_artifacts,
    }


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def render_markdown_report(result: dict[str, Any]) -> str:
    artifact_lines = "\n".join(
        f"- `{a['indicator']}`: status {a['status']}, {a['bytes']} bytes, sha256 `{a['sha256']}`, rows {a['row_count']}"
        for a in result["raw_artifacts"]
    )
    sample_lines = "\n".join(
        f"| {r['indicator_id']} | {r['countryiso3code']} | {r['date']} | {r['value']} |"
        for r in result["rows"]
    )
    return f"""# World Bank WDI smoke slice

## Result

- Source: {result['source']}
- Countries: {', '.join(result['countries'])}
- Indicators: {', '.join(result['indicators'])}
- Date range: {result['date_range']}
- Observations: {result['row_count']} observations
- Expected observations: {result['expected_row_count']}
- Network policy: no network call was made by this session; raw payloads came from the live support bundle recorded in `artifacts/handoffs/wdi-live-smoke-support-20260602/`.

## Raw artifacts

{artifact_lines}

## Normalized rows

| indicator | country | year | value |
| --- | --- | --- | ---: |
{sample_lines}
"""


def write_smoke_artifacts_from_bundle(bundle_dir: str | Path, output_root: str | Path) -> dict[str, str]:
    bundle = Path(bundle_dir)
    output = Path(output_root)
    result = build_smoke_result_from_bundle(bundle)

    raw_dir = output / "raw" / "wdi"
    metadata_dir = output / "metadata" / "wdi"
    reports_dir = output / "reports"
    raw_dir.mkdir(parents=True, exist_ok=True)
    metadata_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    for artifact in result["raw_artifacts"]:
        source_path = bundle / artifact["raw_file"]
        destination = raw_dir / artifact["raw_file"]
        shutil.copy2(source_path, destination)

    manifest_copy = json.loads((bundle / "manifest.json").read_text(encoding="utf-8"))
    _write_json(metadata_dir / "wdi-smoke-manifest.json", manifest_copy)
    _write_json(metadata_dir / "wdi-smoke-normalized.json", result)
    report_path = reports_dir / "wdi-smoke-report.md"
    report_path.write_text(render_markdown_report(result), encoding="utf-8")

    return {
        "raw_dir": str(raw_dir),
        "metadata_manifest": str(metadata_dir / "wdi-smoke-manifest.json"),
        "normalized": str(metadata_dir / "wdi-smoke-normalized.json"),
        "report": str(report_path),
    }


def write_project_smoke_artifacts_from_bundle(bundle_dir: str | Path, project_root: str | Path) -> dict[str, str]:
    """Write TASK-005 artifacts into MacroForge's project layout."""
    bundle = Path(bundle_dir)
    project = Path(project_root)
    result = build_smoke_result_from_bundle(bundle)

    raw_dir = project / "data" / "raw" / "wdi"
    metadata_dir = project / "data" / "metadata" / "wdi"
    report_path = project / "artifacts" / "reports" / "wdi-smoke-20260602.md"
    raw_dir.mkdir(parents=True, exist_ok=True)
    metadata_dir.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    for artifact in result["raw_artifacts"]:
        shutil.copy2(bundle / artifact["raw_file"], raw_dir / artifact["raw_file"])

    _write_json(metadata_dir / "wdi-smoke-manifest.json", json.loads((bundle / "manifest.json").read_text(encoding="utf-8")))
    _write_json(metadata_dir / "wdi-smoke-normalized.json", result)
    report_path.write_text(render_markdown_report(result), encoding="utf-8")

    return {
        "raw_dir": str(raw_dir),
        "metadata_manifest": str(metadata_dir / "wdi-smoke-manifest.json"),
        "normalized": str(metadata_dir / "wdi-smoke-normalized.json"),
        "report": str(report_path),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="MacroForge WDI smoke artifact utilities")
    sub = parser.add_subparsers(dest="command", required=True)
    smoke = sub.add_parser("smoke-from-bundle", help="write TASK-005 smoke artifacts from a support bundle")
    smoke.add_argument("--bundle", required=True)
    smoke.add_argument("--output-root", default=".")
    smoke.add_argument("--project-layout", action="store_true", help="write into data/raw, data/metadata, and artifacts/reports under output root")
    args = parser.parse_args(argv)

    if args.command == "smoke-from-bundle":
        if args.project_layout:
            paths = write_project_smoke_artifacts_from_bundle(args.bundle, args.output_root)
        else:
            paths = write_smoke_artifacts_from_bundle(args.bundle, args.output_root)
        print(json.dumps(paths, indent=2, sort_keys=True))
        return 0
    raise AssertionError(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
