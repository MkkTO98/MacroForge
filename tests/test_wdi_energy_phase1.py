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
from macroforge.wdi_energy_use_coal_electricity import (
    ENERGY_PHASE1_COUNTRY_COUNT,
    ENERGY_PHASE1_EXPECTED_OBSERVATION_COUNT,
    ENERGY_PHASE1_RAW_SHA256,
    build_wdi_energy_phase1_observed_package,
    build_wdi_energy_phase1_refresh_delta_report,
    normalize_wdi_energy_phase1_fixture,
    refresh_delta_report_fingerprint,
    write_wdi_energy_phase1_normalized_artifact,
    write_wdi_energy_phase1_refresh_manifest,
)
from macroforge.wdi_loader import load_wdi_energy_phase1_to_postgres

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BASE_MIGRATION = PROJECT_ROOT / "db/migrations/001_v0_schema_foundation.sql"
CANONICAL_DOMAIN_MIGRATION = PROJECT_ROOT / "db/migrations/003_canonical_domain_dimensions.sql"
HISTORICAL_FALSE_PROVENANCE_FINGERPRINT = "22311f016f808ad6d633bbeb8e6bbb2f5a2b206c6691b02008aa9215c375ac5f"
EXPECTED_FINGERPRINT = "e6d49e4ee3613e1df0406165570258a4c9747ac80aa48d1803f780e65be7565c"
EXPECTED_REFRESH_FINGERPRINT = "fa297d6479a6eacb20bad57a8d3bbac3eede533fda493c0ae965bdc79c743472"


def _payload() -> dict:
    from synthetic_wdi import build_synthetic_wdi_fixture

    return build_synthetic_wdi_fixture("energy_phase1")


def _provenance() -> dict:
    from synthetic_wdi import synthetic_fixture_bytes, synthetic_fixture_provenance

    return {"raw_artifact_path": synthetic_fixture_provenance("energy_phase1")["raw_artifact_path"], "raw_payload": synthetic_fixture_bytes("energy_phase1")}


def _has_postgres_cli() -> bool:
    return all(shutil.which(command) for command in ("createdb", "dropdb", "psql"))


def test_wdi_energy_phase1_fixture_is_persisted_with_expected_hash_and_scope() -> None:
    payload = _payload()
    assert payload["scope"]["task"] == "TASK-134"
    assert payload["scope"]["mode"] == "Operational Capability Expansion"
    assert payload["scope"]["strategic_criterion"] == "Knowledge Leverage"
    assert payload["scope"]["country_count"] == ENERGY_PHASE1_COUNTRY_COUNT == 217
    assert payload["scope"]["indicators"] == ["EG.USE.PCAP.KG.OE", "EG.ELC.COAL.ZS"]
    assert payload["scope"]["expected_observation_count"] == ENERGY_PHASE1_EXPECTED_OBSERVATION_COUNT == 10416
    assert [len(request["response"][1]) for request in payload["requests"]] == [5208, 5208]
    assert all(request["url"].startswith("https://example.invalid/") for request in payload["requests"])


def test_wdi_energy_phase1_normalizes_loader_compatible_rows() -> None:
    normalized = normalize_wdi_energy_phase1_fixture(_payload(), **_provenance())
    from synthetic_wdi import synthetic_fixture_provenance

    provenance = synthetic_fixture_provenance("energy_phase1")
    assert normalized["raw_fixture_path"] == provenance["raw_artifact_path"]
    assert normalized["raw_sha256"] == provenance["raw_sha256"]
    assert normalized["raw_sha256"] != ENERGY_PHASE1_RAW_SHA256
    assert normalized["source"] == "World Bank World Development Indicators"
    assert normalized["row_count"] == ENERGY_PHASE1_EXPECTED_OBSERVATION_COUNT
    assert normalized["expected_row_count"] == ENERGY_PHASE1_EXPECTED_OBSERVATION_COUNT
    assert normalized["operational_scope"]["task"] == "TASK-134"
    assert normalized["operational_scope"]["knowledge_leverage"] == "energy_security_foundation"
    assert normalized["indicators"] == ["EG.USE.PCAP.KG.OE", "EG.ELC.COAL.ZS"]
    assert len({row["countryiso3code"] for row in normalized["rows"]}) == ENERGY_PHASE1_COUNTRY_COUNT
    assert all(row["coverage_level"] == "wdi_energy_phase1_operational_expansion" for row in normalized["rows"])
    assert any(row["value"] is None for row in normalized["rows"])


def test_wdi_energy_phase1_builds_deterministic_observed_package() -> None:
    left = build_wdi_energy_phase1_observed_package(_payload(), **_provenance())
    right = build_wdi_energy_phase1_observed_package(_payload(), **_provenance())
    assert left.source_code == "WDI"
    assert left.provider_dataset_code == "WDI"
    assert left.row_count == ENERGY_PHASE1_EXPECTED_OBSERVATION_COUNT
    assert left.expected_row_count == ENERGY_PHASE1_EXPECTED_OBSERVATION_COUNT
    assert validate_observed_package_contract(left).valid is True
    assert compare_observed_packages(left, right).equivalent is True
    assert observed_package_fingerprint(left) == EXPECTED_FINGERPRINT
    assert EXPECTED_FINGERPRINT != HISTORICAL_FALSE_PROVENANCE_FINGERPRINT
    assert left.raw_evidence["raw_artifact_path"] == _provenance()["raw_artifact_path"]
    assert left.raw_evidence["raw_sha256"] == __import__("synthetic_wdi").synthetic_fixture_provenance("energy_phase1")["raw_sha256"]


def test_wdi_energy_phase1_writes_manifest_and_refresh_delta(tmp_path: Path) -> None:
    normalized_path = tmp_path / "normalized.json"
    manifest_path = tmp_path / "manifest.json"
    normalized = write_wdi_energy_phase1_normalized_artifact(_payload(), normalized_path, **_provenance())
    manifest = write_wdi_energy_phase1_refresh_manifest(_payload(), manifest_path, normalized_path=normalized_path, **_provenance())
    assert normalized_path.exists()
    assert manifest_path.exists()
    assert manifest["task"] == "TASK-134"
    assert manifest["mode"] == "Operational Capability Expansion"
    assert manifest["knowledge_leverage"] == "energy_security_foundation"
    assert manifest["row_count"] == ENERGY_PHASE1_EXPECTED_OBSERVATION_COUNT
    assert manifest["country_count"] == ENERGY_PHASE1_COUNTRY_COUNT
    assert manifest["package_fingerprint"] == EXPECTED_FINGERPRINT

    current = copy.deepcopy(normalized)
    current["rows"][0] = dict(current["rows"][0], value=(current["rows"][0]["value"] or 0) + 1)
    removed = current["rows"].pop(1)
    added = dict(removed, countryiso3code="ZZZ", country_id="ZZ", country_name="Synthetic Test Country")
    current["rows"].append(added)
    current["row_count"] = len(current["rows"])
    current["expected_row_count"] = len(current["rows"])
    report = build_wdi_energy_phase1_refresh_delta_report(normalized, current)
    assert report["task"] == "TASK-134"
    assert report["capability"] == "WDI energy operational foundation"
    assert report["updated_count"] == 1
    assert report["removed_count"] == 1
    assert report["added_count"] == 1
    assert report["changed_count"] == 3
    assert refresh_delta_report_fingerprint(report) == EXPECTED_REFRESH_FINGERPRINT


def test_wdi_energy_phase1_loads_to_isolated_postgres_and_is_idempotent(tmp_path: Path) -> None:
    if not _has_postgres_cli():
        return
    normalized_path = tmp_path / "wdi-energy-phase1-normalized.json"
    write_wdi_energy_phase1_normalized_artifact(_payload(), normalized_path, **_provenance())
    db_name = f"macroforge_test_task134_{uuid.uuid4().hex[:12]}"
    try:
        subprocess.run(["createdb", db_name], check=True, capture_output=True, text=True)
        for migration in (BASE_MIGRATION, CANONICAL_DOMAIN_MIGRATION):
            subprocess.run(["psql", "-v", "ON_ERROR_STOP=1", "-d", db_name, "-f", str(migration)], check=True, capture_output=True, text=True)
        first = load_wdi_energy_phase1_to_postgres(db_name, normalized_path, run_key="task-134-test-load")
        second = load_wdi_energy_phase1_to_postgres(db_name, normalized_path, run_key="task-134-test-load")
        assert first["staging_rows"] == ENERGY_PHASE1_EXPECTED_OBSERVATION_COUNT
        assert first["fact_rows"] == ENERGY_PHASE1_EXPECTED_OBSERVATION_COUNT
        assert second["staging_rows"] == ENERGY_PHASE1_EXPECTED_OBSERVATION_COUNT
        assert second["fact_rows"] == ENERGY_PHASE1_EXPECTED_OBSERVATION_COUNT
        assert second["lineage_events"] >= first["lineage_events"]
        assert second["quality_checks"] >= first["quality_checks"]
    finally:
        subprocess.run(["dropdb", "--if-exists", db_name], capture_output=True, text=True)


def test_wdi_energy_phase1_does_not_create_forbidden_scope() -> None:
    forbidden_paths = [
        PROJECT_ROOT / "src/macroforge/wdi_client.py",
        PROJECT_ROOT / "src/macroforge/energy_framework.py",
        PROJECT_ROOT / "src/macroforge/energy_ontology.py",
        PROJECT_ROOT / "src/macroforge/knowledgeforge_energy_semantics.py",
        PROJECT_ROOT / "src/macroforge/wdi_energy_loader.py",
        PROJECT_ROOT / "src/macroforge/controlled_expansion.py",
    ]
    assert not any(path.exists() for path in forbidden_paths)
