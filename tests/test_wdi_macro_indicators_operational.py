from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import uuid
from pathlib import Path

from macroforge.observed_ingestion import compare_observed_packages, observed_package_fingerprint
from macroforge.wdi_observed import (
    EXPECTED_OBSERVATION_COUNT,
    build_wdi_macro_indicators_observed_package,
    normalize_wdi_macro_indicators_fixture,
    write_wdi_macro_indicators_normalized_artifact,
    write_wdi_macro_indicators_refresh_manifest,
)
from macroforge.wdi_loader import load_wdi_macro_indicators_to_postgres
from synthetic_wdi import build_synthetic_wdi_fixture, synthetic_fixture_bytes, synthetic_fixture_provenance

PROJECT_ROOT = Path(__file__).resolve().parents[1]

HISTORICAL_PROVIDER_RAW_SHA256 = "c3695cae253eafa0436942c48e50dcb262d80a0b5f5f8933cdd4acff6f3cba5f"
HISTORICAL_FALSE_PROVENANCE_FINGERPRINT = "4df65129b38d6518cd8d0d8bc7e77f44c98f9abea352b697145124ce9e3033bb"
EXPECTED_FINGERPRINT = "31d6aea6d047a02c5e37a06de7556360b98979ca26b6724d5b817c9b68eb99ee"
BASE_MIGRATION = PROJECT_ROOT / "db/migrations/001_v0_schema_foundation.sql"
CANONICAL_DOMAIN_MIGRATION = PROJECT_ROOT / "db/migrations/003_canonical_domain_dimensions.sql"


def _payload() -> dict:
    return build_synthetic_wdi_fixture("macro_indicators")


def _provenance() -> dict:
    return {"raw_artifact_path": synthetic_fixture_provenance("macro_indicators")["raw_artifact_path"], "raw_payload": synthetic_fixture_bytes("macro_indicators")}


def _postgres_available() -> bool:
    return all(shutil.which(cmd) for cmd in ["createdb", "dropdb", "psql"])


def _psql(db_name: str, sql: str) -> str:
    return subprocess.run(
        ["psql", "-v", "ON_ERROR_STOP=1", "-d", db_name, "-At", "-c", sql],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def test_wdi_macro_indicators_fixture_is_persisted_and_bounded() -> None:
    payload = _payload()
    assert payload["scope"]["task"] == "TASK-129"
    assert payload["scope"]["mode"] == "Operational Capability Maturation"
    assert payload["scope"]["expected_observation_count"] == EXPECTED_OBSERVATION_COUNT
    assert all(request["url"].startswith("https://example.invalid/") for request in payload["requests"])


def test_wdi_macro_indicators_normalizes_operational_coverage() -> None:
    normalized = normalize_wdi_macro_indicators_fixture(_payload(), **_provenance())
    provenance = synthetic_fixture_provenance("macro_indicators")
    assert normalized["raw_fixture_path"] == provenance["raw_artifact_path"]
    assert normalized["raw_sha256"] == provenance["raw_sha256"]
    assert normalized["raw_sha256"] != HISTORICAL_PROVIDER_RAW_SHA256
    assert normalized["row_count"] == EXPECTED_OBSERVATION_COUNT
    assert normalized["expected_row_count"] == EXPECTED_OBSERVATION_COUNT
    assert normalized["countries"] == ["USA", "DNK", "DEU", "JPN", "CHN", "IND"]
    assert normalized["indicators"] == ["NY.GDP.MKTP.CD", "SP.POP.TOTL", "FP.CPI.TOTL.ZG"]
    assert normalized["date_range"] == "2019:2023"
    assert normalized["operational_scope"]["maturation_track"] == "Track B"
    assert normalized["operational_scope"]["coverage_level"] == "bounded_operational_v1"
    assert len({(row["indicator_id"], row["countryiso3code"], row["date"]) for row in normalized["rows"]}) == EXPECTED_OBSERVATION_COUNT
    assert all(row["value"] is not None for row in normalized["rows"])


def test_wdi_macro_indicators_builds_deterministic_observed_package() -> None:
    left = build_wdi_macro_indicators_observed_package(_payload(), **_provenance())
    right = build_wdi_macro_indicators_observed_package(_payload(), **_provenance())
    assert left.source_code == "WDI"
    assert left.provider_dataset_code == "WDI"
    assert left.row_count == EXPECTED_OBSERVATION_COUNT
    assert compare_observed_packages(left, right).equivalent is True
    assert observed_package_fingerprint(left) == EXPECTED_FINGERPRINT
    assert EXPECTED_FINGERPRINT != HISTORICAL_FALSE_PROVENANCE_FINGERPRINT
    assert left.raw_evidence["raw_artifact_path"] == _provenance()["raw_artifact_path"]
    assert left.raw_evidence["raw_sha256"] == synthetic_fixture_provenance("macro_indicators")["raw_sha256"]


def test_wdi_macro_indicators_writes_normalized_and_refresh_manifest(tmp_path: Path) -> None:
    normalized_path = tmp_path / "normalized.json"
    manifest_path = tmp_path / "refresh-manifest.json"
    normalized = write_wdi_macro_indicators_normalized_artifact(_payload(), normalized_path, **_provenance())
    manifest = write_wdi_macro_indicators_refresh_manifest(_payload(), manifest_path, normalized_path=normalized_path, **_provenance())
    assert normalized_path.exists()
    assert manifest_path.exists()
    assert normalized["row_count"] == EXPECTED_OBSERVATION_COUNT
    assert manifest["task"] == "TASK-129"
    assert manifest["status"] == "succeeded"
    assert manifest["raw_sha256"] == synthetic_fixture_provenance("macro_indicators")["raw_sha256"]
    assert manifest["raw_sha256"] != HISTORICAL_PROVIDER_RAW_SHA256
    assert manifest["row_count"] == EXPECTED_OBSERVATION_COUNT
    assert manifest["package_fingerprint"] == EXPECTED_FINGERPRINT
    assert manifest["refresh_procedure"] == "bounded_manual_refresh_with_deterministic_manifest"


def test_wdi_macro_indicators_loads_to_isolated_postgres_when_available(tmp_path: Path) -> None:
    if not _postgres_available():
        return
    db_name = f"macroforge_wdi_macro_test_{uuid.uuid4().hex[:12]}"
    normalized_path = tmp_path / "normalized.json"
    write_wdi_macro_indicators_normalized_artifact(_payload(), normalized_path, **_provenance())
    try:
        try:
            subprocess.run(["createdb", db_name], check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as exc:
            if "could not connect" in exc.stderr.lower() or "role" in exc.stderr.lower():
                return
            raise
        for migration in [BASE_MIGRATION, CANONICAL_DOMAIN_MIGRATION]:
            subprocess.run(["psql", "-v", "ON_ERROR_STOP=1", "-d", db_name, "-f", str(migration)], check=True, capture_output=True, text=True)
        first = load_wdi_macro_indicators_to_postgres(db_name, normalized_path, run_key="task-129-operational-test")
        second = load_wdi_macro_indicators_to_postgres(db_name, normalized_path, run_key="task-129-operational-test")
        assert first["staging_rows"] == EXPECTED_OBSERVATION_COUNT
        assert first["fact_rows"] == EXPECTED_OBSERVATION_COUNT
        assert second["staging_rows"] == EXPECTED_OBSERVATION_COUNT
        assert second["fact_rows"] == EXPECTED_OBSERVATION_COUNT
        shapes = _psql(
            db_name,
            """
            SELECT
              (SELECT count(*) FROM curated.dim_indicator),
              (SELECT count(*) FROM curated.dim_territory),
              (SELECT count(*) FROM curated.dim_period),
              (SELECT count(*) FROM meta.provider_period_mapping),
              (SELECT count(*) FROM meta.provider_territory_mapping),
              (SELECT count(*) FROM meta.quality_check WHERE check_status = 'pass')
            """,
        )
        assert shapes == "3|6|5|5|6|2"
    finally:
        subprocess.run(["dropdb", "--if-exists", db_name], capture_output=True, text=True)


def test_wdi_macro_indicators_does_not_create_forbidden_operational_scope() -> None:
    forbidden_paths = [PROJECT_ROOT / "src" / "macroforge" / name for name in ["wdi_client.py", "wdi_bulk_ingestion.py", "wdi_all_indicators_loader.py", "knowledgeforge_query_api.py", "controlled_expansion_pipeline.py", "provider_registry.py", "canonical_indicator_ontology.py", "scheduled_refresh_daemon.py"]]
    assert not any(path.exists() for path in forbidden_paths)
