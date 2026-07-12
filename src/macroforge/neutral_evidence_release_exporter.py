from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from dataclasses import dataclass
from decimal import Decimal
from pathlib import Path
from typing import Any

CONTRACT_IDENTITY = "macroforge.neutral_evidence_release_export.v1"
CONTRACT_VERSION = "1.0"
EXPORTER_VERSION = "macroforge-neutral-evidence-release-exporter-v1"
DEFAULT_DATABASE = "macroforge"
DEFAULT_OUTPUT_DIR = Path("artifacts/exports/neutral-evidence-release/task-210-wdi-trade-share-dnk-swe-nor-1990-2024")

WDI_INDICATOR_METADATA = {
    "NE.EXP.GNFS.ZS": {
        "unit": "percent of GDP",
        "definition": "Exports of goods and services (% of GDP)",
    },
    "NE.IMP.GNFS.ZS": {
        "unit": "percent of GDP",
        "definition": "Imports of goods and services (% of GDP)",
    },
}

PRIVATE_LEAKAGE_TERMS = (
    "curated.",
    "meta.",
    "staging.",
    "dataset_release_id",
    "pipeline_run_id",
    "source_id",
    "password",
    "credential",
)


@dataclass(frozen=True)
class ExportScope:
    provider_dataset_code: str
    indicators: tuple[str, ...]
    entities: tuple[str, ...]
    start_year: int
    end_year: int
    frequency: str = "annual"

    def periods(self) -> tuple[str, ...]:
        return tuple(str(year) for year in range(self.start_year, self.end_year + 1))


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_canonical(value: Any) -> str:
    return "sha256:" + sha256_bytes(canonical_json(value).encode("utf-8"))


def _sql_array(values: tuple[str, ...]) -> str:
    escaped = ["'" + value.replace("'", "''") + "'" for value in values]
    return "ARRAY[" + ",".join(escaped) + "]"


def _run_psql_json(db_name: str, sql: str) -> Any:
    proc = subprocess.run(
        ["psql", "-v", "ON_ERROR_STOP=1", "-d", db_name, "-At", "-c", sql],
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or proc.stdout.strip())
    text = proc.stdout.strip()
    if not text:
        return None
    return json.loads(text)


def _source_frequency(scope: ExportScope) -> str:
    return "A" if scope.frequency == "annual" else scope.frequency


def _public_frequency(source_frequency: str) -> str:
    return "annual" if source_frequency == "A" else source_frequency


def _selection_payload(scope: ExportScope) -> dict[str, Any]:
    return {
        "provider_dataset_code": scope.provider_dataset_code,
        "indicators": list(scope.indicators),
        "entities": list(scope.entities),
        "periods": list(scope.periods()),
        "frequency": scope.frequency,
    }


def _query_rows(db_name: str, scope: ExportScope) -> list[dict[str, Any]]:
    source_frequency = _source_frequency(scope)
    sql = f"""
WITH selected AS (
  SELECT
    s.source_code,
    s.source_name,
    s.source_home_url,
    dr.provider_dataset_code,
    dr.release_key,
    dr.release_date::text AS release_date,
    dr.source_url,
    dr.raw_artifact_path,
    dr.raw_sha256,
    dr.metadata,
    pr.run_key,
    pr.pipeline_name,
    pr.status AS run_status,
    pr.input_parameters,
    pr.artifact_manifest,
    i.source_indicator_code AS indicator,
    i.indicator_name,
    COALESCE(i.description, '') AS indicator_description,
    t.iso3_code AS entity,
    t.territory_name AS entity_name,
    p.frequency,
    p.period_year,
    u.unit_code,
    u.unit_name,
    f.value::text AS value,
    f.observation_status,
    f.as_of_date::text AS as_of_date
  FROM curated.fact_observation f
  JOIN meta.source s ON f.source_id=s.source_id
  JOIN meta.dataset_release dr ON f.dataset_release_id=dr.dataset_release_id
  LEFT JOIN meta.pipeline_run pr ON pr.pipeline_run_id=f.pipeline_run_id
  JOIN curated.dim_indicator i ON f.indicator_id=i.indicator_id
  JOIN curated.dim_territory t ON f.territory_id=t.territory_id
  JOIN curated.dim_period p ON f.period_id=p.period_id
  JOIN curated.dim_unit u ON f.unit_id=u.unit_id
  WHERE s.source_code='WDI'
    AND dr.provider_dataset_code = '{scope.provider_dataset_code.replace("'", "''")}'
    AND i.source_indicator_code = ANY({_sql_array(scope.indicators)})
    AND t.iso3_code = ANY({_sql_array(scope.entities)})
    AND p.frequency = '{source_frequency.replace("'", "''")}'
    AND p.period_year BETWEEN {int(scope.start_year)} AND {int(scope.end_year)}
)
SELECT COALESCE(json_agg(row_to_json(selected) ORDER BY indicator, entity, period_year), '[]'::json)::text
FROM selected;
"""
    rows = _run_psql_json(db_name, sql) or []
    return rows


def _normalize_value(value: Any) -> str | None:
    if value is None:
        return None
    decimal = Decimal(str(value))
    return format(decimal.normalize(), "f")


def _item_from_row(row: dict[str, Any]) -> dict[str, Any]:
    metadata = WDI_INDICATOR_METADATA.get(row["indicator"], {})
    status = row["observation_status"]
    missing = status != "observed"
    item = {
        "item_id": f"wdi:{row['entity']}:{row['indicator']}:{row['period_year']}",
        "provider_identity": "World Bank",
        "dataset_identity": "World Development Indicators",
        "source_provider_dataset_code": row["provider_dataset_code"],
        "entity": row["entity"],
        "entity_label": row["entity_name"],
        "indicator": row["indicator"],
        "indicator_label": row["indicator_name"],
        "period": str(row["period_year"]),
        "frequency": _public_frequency(row["frequency"]),
        "unit": metadata.get("unit") or row.get("unit_name") or row.get("unit_code") or "unknown",
        "definition": metadata.get("definition") or row.get("indicator_description") or row.get("indicator_name"),
        "value": None if missing else _normalize_value(row.get("value")),
        "missing": missing,
        "observation_status": status,
        "provenance": {
            "source_code": row["source_code"],
            "provider_dataset_code": row["provider_dataset_code"],
            "release_key": row["release_key"],
            "run_key": row.get("run_key"),
            "as_of_date": row.get("as_of_date"),
        },
    }
    item["item_fingerprint"] = item_fingerprint(item)
    return item


def item_fingerprint(item: dict[str, Any]) -> str:
    payload = {k: v for k, v in item.items() if k != "item_fingerprint"}
    return sha256_canonical(payload)


def _release_metadata(rows: list[dict[str, Any]]) -> dict[str, Any]:
    release_keys = sorted({row["release_key"] for row in rows})
    run_keys = sorted({row.get("run_key") for row in rows if row.get("run_key")})
    statuses = sorted({row.get("run_status") for row in rows if row.get("run_status")})
    raw_artifacts = sorted({row.get("raw_artifact_path") for row in rows if row.get("raw_artifact_path")})
    raw_sha256 = sorted({row.get("raw_sha256") for row in rows if row.get("raw_sha256")})
    return {
        "source_release_keys": release_keys,
        "source_run_keys": run_keys,
        "run_statuses": statuses,
        "raw_artifact_paths": raw_artifacts,
        "raw_sha256": raw_sha256,
        "lineage": {
            "provider_release": release_keys,
            "macroforge_ingestion_runs": run_keys,
            "macroforge_canonical_snapshot": "current local MacroForge PostgreSQL canonical observation snapshot at export time",
            "bounded_downstream_export": "selection-scoped immutable JSON export",
        },
        "quality_status": "eligible_only_if_all_source_runs_succeeded" if statuses == ["succeeded"] else "requires_review",
    }


def build_neutral_evidence_release_export(db_name: str, scope: ExportScope, *, created_at: str) -> dict[str, Any]:
    rows = _query_rows(db_name, scope)
    expected = len(scope.indicators) * len(scope.entities) * len(scope.periods())
    if len(rows) != expected:
        raise ValueError(f"selection returned {len(rows)} rows; expected {expected}")
    if {row.get("run_status") for row in rows} - {"succeeded"}:
        raise ValueError("export scope includes non-succeeded or unknown ingestion run status")
    items = [_item_from_row(row) for row in rows]
    selection = _selection_payload(scope)
    release_metadata = _release_metadata(rows)
    document = {
        "contract_identity": CONTRACT_IDENTITY,
        "contract_version": CONTRACT_VERSION,
        "producing_system": "MacroForge",
        "exporter_version": EXPORTER_VERSION,
        "release_identity": f"macroforge-wdi-{scope.start_year}-{scope.end_year}-" + sha256_canonical(selection)[7:23],
        "original_provider": {
            "provider_identity": "World Bank",
            "dataset_identity": "World Development Indicators",
            "provider_dataset_code": scope.provider_dataset_code,
            "source_release_or_vintage": release_metadata["source_release_keys"],
        },
        "predecessor_release_identity": None,
        "publication_metadata": {
            "producer": "MacroForge",
            "operational_created_at_excluded_from_deterministic_identity": True,
        },
        "selection": selection,
        "release_metadata": release_metadata,
        "items": items,
        "operational_metadata": {"created_at": created_at},
    }
    recompute_document_fingerprints(document)
    return document


def _fingerprint_document_payload(document: dict[str, Any]) -> dict[str, Any]:
    excluded = {"release_fingerprint", "operational_metadata"}
    return {k: v for k, v in document.items() if k not in excluded}


def recompute_document_fingerprints(document: dict[str, Any]) -> None:
    for item in document.get("items", []):
        item["item_fingerprint"] = item_fingerprint(item)
    document["selection_fingerprint"] = sha256_canonical(document["selection"])
    document["release_fingerprint"] = sha256_canonical(_fingerprint_document_payload(document))


def validate_export_document(document: dict[str, Any]) -> dict[str, Any]:
    errors: list[str] = []
    if document.get("contract_identity") != CONTRACT_IDENTITY:
        errors.append("contract_identity_mismatch")
    if document.get("contract_version") != CONTRACT_VERSION:
        errors.append("contract_version_mismatch")
    items = document.get("items") or []
    item_ids = [item.get("item_id") for item in items]
    if len(item_ids) != len(set(item_ids)):
        errors.append("duplicate_item_id")
    keys = [(item.get("indicator"), item.get("entity"), item.get("period"), item.get("frequency")) for item in items]
    if len(keys) != len(set(keys)):
        errors.append("duplicate_observation_key")
    for item in items:
        if item.get("item_fingerprint") != item_fingerprint(item):
            errors.append("item_fingerprint_mismatch")
            break
        missing = item.get("observation_status") != "observed"
        if item.get("missing") is not missing:
            errors.append("missingness_status_mismatch")
            break
        required = ["entity", "indicator", "period", "frequency", "unit", "definition", "provenance"]
        if any(item.get(field) in (None, "", []) for field in required):
            errors.append("missing_required_item_field")
            break
    expected_selection_fp = sha256_canonical(document.get("selection"))
    if document.get("selection_fingerprint") != expected_selection_fp:
        errors.append("selection_fingerprint_mismatch")
    expected_release_fp = sha256_canonical(_fingerprint_document_payload(document))
    if document.get("release_fingerprint") != expected_release_fp:
        errors.append("release_fingerprint_mismatch")
    serialized = json.dumps(document, sort_keys=True, ensure_ascii=False)
    leaked = sorted(term for term in PRIVATE_LEAKAGE_TERMS if term in serialized)
    if leaked:
        errors.append("private_or_sensitive_identifier_leakage:" + ",".join(leaked))
    return {"valid": not errors, "errors": errors, "item_count": len(items), "release_fingerprint": document.get("release_fingerprint")}


def write_export(db_name: str, scope: ExportScope, output_path: Path, *, manifest_path: Path | None = None, created_at: str) -> dict[str, Any]:
    document = build_neutral_evidence_release_export(db_name, scope, created_at=created_at)
    validation = validate_export_document(document)
    if not validation["valid"]:
        raise ValueError(validation)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(document, sort_keys=True, indent=2, ensure_ascii=False) + "\n"
    output_path.write_text(content)
    manifest = {
        "valid": validation["valid"],
        "contract_identity": CONTRACT_IDENTITY,
        "contract_version": CONTRACT_VERSION,
        "export_path": str(output_path),
        "item_count": len(document["items"]),
        "release_identity": document["release_identity"],
        "selection_fingerprint": document["selection_fingerprint"],
        "release_fingerprint": document["release_fingerprint"],
        "export_sha256": sha256_bytes(content.encode("utf-8")),
        "validation": validation,
    }
    if manifest_path:
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(json.dumps(manifest, sort_keys=True, indent=2, ensure_ascii=False) + "\n")
    return manifest


def default_scope() -> ExportScope:
    return ExportScope(
        provider_dataset_code="WDI",
        indicators=("NE.EXP.GNFS.ZS", "NE.IMP.GNFS.ZS"),
        entities=("DNK", "SWE", "NOR"),
        start_year=1990,
        end_year=2024,
        frequency="annual",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="MacroForge neutral evidence-release exporter")
    parser.add_argument("--database", default=DEFAULT_DATABASE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_DIR / "macroforge-wdi-trade-share-dnk-swe-nor-1990-2024.neutral-release.json")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_OUTPUT_DIR / "manifest.json")
    parser.add_argument("--created-at", default="2026-07-11T00:00:00Z")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("export")
    sub.add_parser("validate")
    args = parser.parse_args()
    if args.command == "export":
        result = write_export(args.database, default_scope(), args.output, manifest_path=args.manifest, created_at=args.created_at)
    elif args.command == "validate":
        document = json.loads(args.output.read_text())
        result = validate_export_document(document)
    else:
        raise AssertionError(args.command)
    print(json.dumps(result, sort_keys=True, indent=2, ensure_ascii=False))
    return 0 if result.get("valid", True) else 2


if __name__ == "__main__":
    raise SystemExit(main())
