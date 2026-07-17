from __future__ import annotations

import copy
import hashlib
import json
import shutil
import subprocess
import uuid
from pathlib import Path

from macroforge.observed_ingestion import compare_observed_packages, observed_package_fingerprint
from macroforge.wdi_loader import load_wdi_operational_phase1_to_postgres
from macroforge.wdi_observed import (
    PHASE1_COUNTRY_COUNT,
    PHASE1_EXPECTED_OBSERVATION_COUNT,
    PHASE1_RAW_SHA256,
    build_wdi_operational_phase1_observed_package,
    build_wdi_operational_phase1_refresh_delta_report,
    normalize_wdi_operational_phase1_fixture,
    refresh_delta_report_fingerprint,
    write_wdi_operational_phase1_normalized_artifact,
    write_wdi_operational_phase1_refresh_manifest,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BASE_MIGRATION = PROJECT_ROOT / "db/migrations/001_v0_schema_foundation.sql"
CANONICAL_DOMAIN_MIGRATION = PROJECT_ROOT / "db/migrations/003_canonical_domain_dimensions.sql"
EXPECTED_FINGERPRINT = "5b6bdf25264a12ea51a83d48b8ffd6cfbb5f3541044be129f8a6f72f1096f58c"
EXPECTED_REFRESH_FINGERPRINT = "f19f544a235d78d3590e46b24682cf434ef8b17c68871d6223b1de9a4bf43f42"


def _payload() -> dict:
    from synthetic_wdi import build_synthetic_wdi_fixture

    return build_synthetic_wdi_fixture("operational_phase1")


def _postgres_available() -> bool:
    return all(shutil.which(cmd) for cmd in ["createdb", "dropdb", "psql"])


def _psql(db_name: str, sql: str) -> str:
    return subprocess.run(
        ["psql", "-v", "ON_ERROR_STOP=1", "-d", db_name, "-At", "-c", sql],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def test_wdi_phase1_fixture_is_persisted_and_bounded() -> None:
    payload = _payload()
    assert payload["scope"]["task"] == "TASK-132"
    assert payload["scope"]["mode"] == "Operational Capability Expansion"
    assert payload["scope"]["country_count"] == PHASE1_COUNTRY_COUNT
    assert payload["scope"]["expected_observation_count"] == PHASE1_EXPECTED_OBSERVATION_COUNT
    assert payload["scope"]["indicators"] == ["NY.GDP.MKTP.CD", "SP.POP.TOTL", "FP.CPI.TOTL.ZG"]
    assert payload["scope"]["date_range"] == "2000:2023"
    assert all(request["url"].startswith("https://example.invalid/") for request in payload["requests"])


def test_wdi_phase1_normalizes_all_non_aggregate_country_macro_coverage() -> None:
    normalized = normalize_wdi_operational_phase1_fixture(_payload())
    assert normalized["operational_scope"]["phase"] == "WDI Phase 1"
    assert normalized["operational_scope"]["expansion_level"] == "all_non_aggregate_countries_validated_macro_set_2000_2023"
    assert normalized["row_count"] == PHASE1_EXPECTED_OBSERVATION_COUNT
    assert normalized["expected_row_count"] == PHASE1_EXPECTED_OBSERVATION_COUNT
    assert len(normalized["countries"]) == PHASE1_COUNTRY_COUNT
    assert normalized["countries"][0] == "XAA"
    assert normalized["countries"][-1] == "XII"
    assert len({(row["indicator_id"], row["countryiso3code"], row["date"]) for row in normalized["rows"]}) == PHASE1_EXPECTED_OBSERVATION_COUNT
    missing = [row for row in normalized["rows"] if row["value"] is None]
    observed = [row for row in normalized["rows"] if row["value"] is not None]
    assert missing
    assert observed
    assert len(missing) + len(observed) == PHASE1_EXPECTED_OBSERVATION_COUNT


def test_wdi_phase1_builds_deterministic_observed_package() -> None:
    left = build_wdi_operational_phase1_observed_package(_payload())
    right = build_wdi_operational_phase1_observed_package(_payload())
    assert left.source_code == "WDI"
    assert left.provider_dataset_code == "WDI"
    assert left.row_count == PHASE1_EXPECTED_OBSERVATION_COUNT
    assert left.expected_row_count == PHASE1_EXPECTED_OBSERVATION_COUNT
    assert compare_observed_packages(left, right).equivalent is True
    assert observed_package_fingerprint(left) == EXPECTED_FINGERPRINT


def test_wdi_phase1_writes_normalized_manifest_and_refresh_delta(tmp_path: Path) -> None:
    normalized_path = tmp_path / "normalized.json"
    manifest_path = tmp_path / "manifest.json"
    normalized = write_wdi_operational_phase1_normalized_artifact(_payload(), normalized_path)
    manifest = write_wdi_operational_phase1_refresh_manifest(_payload(), manifest_path, normalized_path=normalized_path)
    assert normalized_path.exists()
    assert manifest_path.exists()
    assert manifest["task"] == "TASK-132"
    assert manifest["mode"] == "Operational Capability Expansion"
    assert manifest["row_count"] == PHASE1_EXPECTED_OBSERVATION_COUNT
    assert manifest["country_count"] == PHASE1_COUNTRY_COUNT
    assert manifest["package_fingerprint"] == EXPECTED_FINGERPRINT

    current = copy.deepcopy(normalized)
    current["rows"][0] = dict(current["rows"][0], value=(current["rows"][0]["value"] or 0) + 1)
    removed = current["rows"].pop(1)
    added = dict(removed, countryiso3code="ZZZ", country_id="ZZ", country_name="Synthetic Test Country")
    current["rows"].append(added)
    current["row_count"] = len(current["rows"])
    current["expected_row_count"] = len(current["rows"])
    report = build_wdi_operational_phase1_refresh_delta_report(normalized, current)
    assert report["task"] == "TASK-132"
    assert report["updated_count"] == 1
    assert report["removed_count"] == 1
    assert report["added_count"] == 1
    assert report["changed_count"] == 3
    assert refresh_delta_report_fingerprint(report) == EXPECTED_REFRESH_FINGERPRINT


def test_wdi_phase1_loads_to_isolated_postgres_when_available(tmp_path: Path) -> None:
    if not _postgres_available():
        return
    db_name = f"macroforge_wdi_phase1_test_{uuid.uuid4().hex[:12]}"
    normalized_path = tmp_path / "normalized.json"
    write_wdi_operational_phase1_normalized_artifact(_payload(), normalized_path)
    try:
        try:
            subprocess.run(["createdb", db_name], check=True, capture_output=True, text=True)
        except subprocess.CalledProcessError as exc:
            if "could not connect" in exc.stderr.lower() or "role" in exc.stderr.lower():
                return
            raise
        for migration in [BASE_MIGRATION, CANONICAL_DOMAIN_MIGRATION]:
            subprocess.run(["psql", "-v", "ON_ERROR_STOP=1", "-d", db_name, "-f", str(migration)], check=True, capture_output=True, text=True)
        first = load_wdi_operational_phase1_to_postgres(db_name, normalized_path, run_key="task-132-phase1-test")
        second = load_wdi_operational_phase1_to_postgres(db_name, normalized_path, run_key="task-132-phase1-test")
        assert first["staging_rows"] == PHASE1_EXPECTED_OBSERVATION_COUNT
        assert first["fact_rows"] == PHASE1_EXPECTED_OBSERVATION_COUNT
        assert second["staging_rows"] == PHASE1_EXPECTED_OBSERVATION_COUNT
        assert second["fact_rows"] == PHASE1_EXPECTED_OBSERVATION_COUNT
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
        assert shapes == f"3|{PHASE1_COUNTRY_COUNT}|24|24|{PHASE1_COUNTRY_COUNT}|2"
    finally:
        subprocess.run(["dropdb", "--if-exists", db_name], capture_output=True, text=True)


def test_wdi_phase1_does_not_create_forbidden_expansion_scope() -> None:
    forbidden_paths = [PROJECT_ROOT / "src" / "macroforge" / name for name in ["wdi_client.py", "wdi_bulk_ingestion.py", "wdi_all_indicators_loader.py", "knowledgeforge_query_api.py", "controlled_expansion_pipeline.py", "provider_registry.py", "canonical_indicator_ontology.py", "scheduled_refresh_daemon.py", "wdi_full_catalog_ingestion.py"]]
    assert not any(path.exists() for path in forbidden_paths)
