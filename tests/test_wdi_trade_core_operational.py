from __future__ import annotations

import copy
import hashlib
import json
import shutil
import subprocess
import uuid
from pathlib import Path

from macroforge.contract_drift import validate_observed_package_contract
from macroforge.observed_ingestion import compare_observed_packages, observed_package_fingerprint
from macroforge.wdi_loader import load_wdi_trade_core_operational_to_postgres
from macroforge.wdi_trade_core import (
    TRADE_CORE_COUNTRY_COUNT,
    TRADE_CORE_EXPECTED_OBSERVATION_COUNT,
    TRADE_CORE_INDICATORS,
    TRADE_CORE_RAW_SHA256,
    build_wdi_trade_core_observed_package,
    build_wdi_trade_core_refresh_delta_report,
    normalize_wdi_trade_core_fixture,
    refresh_delta_report_fingerprint,
    write_wdi_trade_core_normalized_artifact,
    write_wdi_trade_core_refresh_manifest,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BASE_MIGRATION = PROJECT_ROOT / "db/migrations/001_v0_schema_foundation.sql"
CANONICAL_DOMAIN_MIGRATION = PROJECT_ROOT / "db/migrations/003_canonical_domain_dimensions.sql"
EXPECTED_FINGERPRINT = "2edfae577e5b95257a92ca4d219f4281d55c8d6ca9eb5663b479f43e36694228"
EXPECTED_REFRESH_FINGERPRINT = "8ac6e7e4d5f000e3138ce6f2136c5d72c2ac13206f0b6ca88e6ac562909f4c36"


def _payload() -> dict:
    from synthetic_wdi import build_synthetic_wdi_fixture

    return build_synthetic_wdi_fixture("trade_core")


def test_wdi_trade_core_fixture_is_persisted_and_bounded() -> None:
    payload = _payload()
    scope = payload["scope"]
    assert scope["task"] == "TASK-142"
    assert scope["mode"] == "Operational Repository Construction"
    assert scope["section"] == "Trade"
    assert scope["section_status_target"] == "Developing"
    assert scope["country_count"] == TRADE_CORE_COUNTRY_COUNT
    assert scope["indicators"] == TRADE_CORE_INDICATORS
    assert scope["expected_observation_count"] == TRADE_CORE_EXPECTED_OBSERVATION_COUNT
    assert len(payload["requests"]) == len(TRADE_CORE_INDICATORS)
    assert all(len(request["response"][1]) == TRADE_CORE_COUNTRY_COUNT * 24 for request in payload["requests"])
    assert all(request["url"].startswith("https://example.invalid/") for request in payload["requests"])
    forbidden = " ".join(scope["non_goals"])
    assert "Controlled_Expansion" in forbidden
    assert "KnowledgeForge_implementation" in forbidden
    assert "full_WDI_catalog_ingestion" in forbidden
    assert "trade_framework" in forbidden


def test_wdi_trade_core_normalizes_loader_compatible_rows() -> None:
    normalized = normalize_wdi_trade_core_fixture(_payload())
    assert normalized["row_count"] == TRADE_CORE_EXPECTED_OBSERVATION_COUNT
    assert normalized["expected_row_count"] == TRADE_CORE_EXPECTED_OBSERVATION_COUNT
    assert normalized["date_range"] == "2000:2023"
    assert len(normalized["countries"]) == TRADE_CORE_COUNTRY_COUNT
    assert normalized["indicators"] == TRADE_CORE_INDICATORS
    assert len(normalized["raw_artifacts"]) == len(TRADE_CORE_INDICATORS)
    first = normalized["rows"][0]
    assert first["indicator_id"] == "NE.EXP.GNFS.CD"
    assert first["countryiso3code"] == "XAA"
    assert first["date"] == "2000"
    assert first["trade_concept"] == "exports_goods_services_current_usd"
    assert first["trade_flow"] == "exports"
    assert first["unit"] == "CURRENT_USD"
    assert "region_id" in first
    assert "income_level_id" in first


def test_wdi_trade_core_builds_deterministic_observed_package() -> None:
    left = build_wdi_trade_core_observed_package(_payload())
    right = build_wdi_trade_core_observed_package(_payload())
    assert left.source_code == "WDI"
    assert left.provider_dataset_code == "WDI"
    assert left.row_count == TRADE_CORE_EXPECTED_OBSERVATION_COUNT
    assert left.expected_row_count == TRADE_CORE_EXPECTED_OBSERVATION_COUNT
    assert validate_observed_package_contract(left).valid is True
    assert compare_observed_packages(left, right).equivalent is True
    assert observed_package_fingerprint(left) == EXPECTED_FINGERPRINT
    assert observed_package_fingerprint(left) == observed_package_fingerprint(right)


def test_wdi_trade_core_writes_manifest_and_refresh_delta(tmp_path: Path) -> None:
    normalized_path = tmp_path / "normalized.json"
    manifest_path = tmp_path / "manifest.json"
    normalized = write_wdi_trade_core_normalized_artifact(_payload(), normalized_path)
    manifest = write_wdi_trade_core_refresh_manifest(_payload(), manifest_path, normalized_path=normalized_path)
    assert normalized_path.exists()
    assert manifest_path.exists()
    assert manifest["task"] == "TASK-142"
    assert manifest["mode"] == "Operational Repository Construction"
    assert manifest["repository_section"] == "Trade"
    assert manifest["section_status_target"] == "Developing"
    assert manifest["row_count"] == TRADE_CORE_EXPECTED_OBSERVATION_COUNT
    assert manifest["country_count"] == TRADE_CORE_COUNTRY_COUNT
    assert manifest["package_fingerprint"] == EXPECTED_FINGERPRINT

    current = copy.deepcopy(normalized)
    current["rows"][0] = dict(current["rows"][0], value=(current["rows"][0]["value"] or 0) + 1)
    removed = current["rows"].pop(1)
    added = dict(removed, countryiso3code="ZZZ", country_id="ZZ", country_name="Synthetic Test Country")
    current["rows"].append(added)
    current["row_count"] = len(current["rows"])
    current["expected_row_count"] = len(current["rows"])
    report = build_wdi_trade_core_refresh_delta_report(normalized, current)
    assert report["task"] == "TASK-142"
    assert report["capability"] == "WDI trade core operational repository section"
    assert report["updated_count"] == 1
    assert report["removed_count"] == 1
    assert report["added_count"] == 1
    assert report["changed_count"] == 3
    assert refresh_delta_report_fingerprint(report) == EXPECTED_REFRESH_FINGERPRINT


def test_wdi_trade_core_loads_to_postgres_when_available(tmp_path: Path) -> None:
    if not all(shutil.which(command) for command in ["createdb", "dropdb", "psql"]):
        return
    db_name = f"macroforge_task142_verify_{uuid.uuid4().hex[:12]}"
    normalized_path = tmp_path / "normalized.json"
    write_wdi_trade_core_normalized_artifact(_payload(), normalized_path)
    try:
        subprocess.run(["createdb", db_name], check=True, capture_output=True, text=True)
        for migration in [BASE_MIGRATION, CANONICAL_DOMAIN_MIGRATION]:
            subprocess.run(["psql", "-v", "ON_ERROR_STOP=1", "-d", db_name, "-f", str(migration)], check=True, capture_output=True, text=True)
        counts = load_wdi_trade_core_operational_to_postgres(db_name, normalized_path, run_key="task-142-wdi-trade-core-test")
        assert counts == {
            "staging_rows": TRADE_CORE_EXPECTED_OBSERVATION_COUNT,
            "fact_rows": TRADE_CORE_EXPECTED_OBSERVATION_COUNT,
            "lineage_events": 2,
            "quality_checks": 2,
        }
        second = load_wdi_trade_core_operational_to_postgres(db_name, normalized_path, run_key="task-142-wdi-trade-core-test")
        assert second["staging_rows"] == TRADE_CORE_EXPECTED_OBSERVATION_COUNT
        assert second["fact_rows"] == TRADE_CORE_EXPECTED_OBSERVATION_COUNT
    finally:
        subprocess.run(["dropdb", "--if-exists", db_name], capture_output=True, text=True)


def test_wdi_trade_core_does_not_create_forbidden_frameworks() -> None:
    forbidden_paths = [
        PROJECT_ROOT / "src/macroforge/trade_framework.py",
        PROJECT_ROOT / "src/macroforge/product_taxonomy.py",
        PROJECT_ROOT / "src/macroforge/partner_hierarchy.py",
        PROJECT_ROOT / "src/macroforge/knowledgeforge_trade.py",
        PROJECT_ROOT / "src/macroforge/wdi_full_catalog_loader.py",
        PROJECT_ROOT / "src/macroforge/controlled_expansion.py",
    ]
    assert not any(path.exists() for path in forbidden_paths)
