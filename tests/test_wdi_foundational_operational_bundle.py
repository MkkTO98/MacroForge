from __future__ import annotations

import json
import shutil
import subprocess
import uuid
from pathlib import Path

from macroforge import wdi_foundational_operational_bundle as bundle_module
from macroforge.wdi_foundational_operational_bundle import (
    BUNDLE_COMPONENTS,
    BUNDLE_EXPECTED_INDICATOR_COUNT,
    BUNDLE_EXPECTED_OBSERVATION_COUNT,
    BUNDLE_EXPECTED_PERIOD_RANGE,
    build_wdi_foundational_bundle_manifest,
    load_wdi_foundational_bundle_to_postgres,
    manifest_fingerprint,
    write_wdi_foundational_bundle_manifest,
)
from synthetic_wdi import write_synthetic_wdi_fixture

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BASE_MIGRATION = PROJECT_ROOT / "db/migrations/001_v0_schema_foundation.sql"
CANONICAL_DOMAIN_MIGRATION = PROJECT_ROOT / "db/migrations/003_canonical_domain_dimensions.sql"
EXPECTED_MANIFEST_FINGERPRINT = "987396d00972d5e727176e349f0a79b6b7f5d9639d74b8b4b43e115da5213fea"


def _install_synthetic_bundle(monkeypatch, tmp_path: Path) -> None:
    macro = write_synthetic_wdi_fixture(
        tmp_path / "data/raw/wdi_operational_phase1/wdi-phase1-all-countries-3i-2000-2023.json",
        "operational_phase1",
    )
    demographics = write_synthetic_wdi_fixture(
        tmp_path / "data/raw/wdi_demographics_phase1/wdi-demographics-phase1-all-countries-8i-2000-2023.json",
        "demographics_phase1",
    )
    energy = write_synthetic_wdi_fixture(
        tmp_path / "data/raw/wdi_energy_phase1/wdi-energy-phase1-all-countries-2i-2000-2023.json",
        "energy_phase1",
    )
    monkeypatch.setattr(bundle_module, "PROJECT_ROOT", tmp_path)
    monkeypatch.setattr(bundle_module, "MACRO_FIXTURE", macro)
    monkeypatch.setattr(bundle_module, "DEMOGRAPHICS_FIXTURE", demographics)
    monkeypatch.setattr(bundle_module, "ENERGY_FIXTURE", energy)


def _postgres_available() -> bool:
    return all(shutil.which(command) for command in ("createdb", "dropdb", "psql"))


def _psql(db_name: str, sql: str) -> str:
    return subprocess.run(
        ["psql", "-v", "ON_ERROR_STOP=1", "-d", db_name, "-At", "-c", sql],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def test_wdi_foundational_bundle_manifest_is_bounded_and_knowledgeforge_useful(
    monkeypatch, tmp_path: Path
) -> None:
    _install_synthetic_bundle(monkeypatch, tmp_path)
    manifest = build_wdi_foundational_bundle_manifest()
    assert manifest["task"] == "TASK-139"
    assert manifest["mode"] == "Operational Dataset Construction"
    assert manifest["strategic_criterion"] == "Expected Knowledge Leverage"
    assert manifest["component_count"] == 3
    assert manifest["components"] == BUNDLE_COMPONENTS
    assert manifest["row_count"] == BUNDLE_EXPECTED_OBSERVATION_COUNT == 67704
    # Macro Phase 1 and Demographics Phase 1 both include SP.POP.TOTL.
    assert manifest["indicator_count"] == BUNDLE_EXPECTED_INDICATOR_COUNT == 12
    assert manifest["period_range"] == BUNDLE_EXPECTED_PERIOD_RANGE == "2000:2023"
    assert "cross_country_macro_context" in manifest["knowledgeforge_analyses_enabled"]
    assert "demographic_vulnerability_screening" in manifest["knowledgeforge_analyses_enabled"]
    assert "energy_security_context" in manifest["knowledgeforge_analyses_enabled"]
    forbidden = " ".join(manifest["non_goals"])
    assert "full_WDI_catalog_ingestion" in forbidden
    assert "KnowledgeForge_implementation" in forbidden
    assert "architecture_redesign" in forbidden


def test_wdi_foundational_bundle_manifest_is_deterministic_and_persistable(
    monkeypatch, tmp_path: Path
) -> None:
    _install_synthetic_bundle(monkeypatch, tmp_path)
    left = build_wdi_foundational_bundle_manifest()
    right = build_wdi_foundational_bundle_manifest()
    assert left == right
    assert manifest_fingerprint(left) == manifest_fingerprint(right)
    assert len(manifest_fingerprint(left)) == 64
    out = tmp_path / "wdi-foundational-bundle-manifest.json"
    written = write_wdi_foundational_bundle_manifest(out)
    assert out.exists()
    assert json.loads(out.read_text()) == written == left


def test_wdi_foundational_bundle_loads_all_components_to_postgres_when_available(
    monkeypatch, tmp_path: Path
) -> None:
    if not _postgres_available():
        return
    db_name = f"macroforge_task139_bundle_{uuid.uuid4().hex[:12]}"
    manifest_path = tmp_path / "wdi-foundational-bundle-manifest.json"
    _install_synthetic_bundle(monkeypatch, tmp_path)
    try:
        subprocess.run(["createdb", db_name], check=True, capture_output=True, text=True)
        for migration in (BASE_MIGRATION, CANONICAL_DOMAIN_MIGRATION):
            subprocess.run(["psql", "-v", "ON_ERROR_STOP=1", "-d", db_name, "-f", str(migration)], check=True, capture_output=True, text=True)
        first = load_wdi_foundational_bundle_to_postgres(
            db_name,
            manifest_path=manifest_path,
            normalized_dir=tmp_path / "normalized",
            load_report_path=None,
            run_key_prefix="task-139-test",
        )
        second = load_wdi_foundational_bundle_to_postgres(
            db_name,
            manifest_path=manifest_path,
            normalized_dir=tmp_path / "normalized",
            load_report_path=None,
            run_key_prefix="task-139-test",
        )
        assert first["row_count"] == BUNDLE_EXPECTED_OBSERVATION_COUNT
        assert second["row_count"] == BUNDLE_EXPECTED_OBSERVATION_COUNT
        assert first["component_count"] == 3
        assert second["component_count"] == 3
        assert manifest_path.exists()
        counts = _psql(
            db_name,
            """
            SELECT
              (SELECT count(*) FROM staging.wdi_observation),
              (SELECT count(*) FROM curated.fact_observation),
              (SELECT count(DISTINCT source_indicator_code) FROM curated.dim_indicator),
              (SELECT count(DISTINCT canonical_territory_code) FROM curated.dim_territory),
              (SELECT count(DISTINCT period_year) FROM curated.dim_period);
            """,
        )
        staging_rows, fact_rows, indicators, territories, periods = [int(value) for value in counts.split("|")]
        assert staging_rows == BUNDLE_EXPECTED_OBSERVATION_COUNT
        assert fact_rows == BUNDLE_EXPECTED_OBSERVATION_COUNT
        assert indicators == BUNDLE_EXPECTED_INDICATOR_COUNT
        assert territories == 217
        assert periods == 24
    finally:
        subprocess.run(["dropdb", "--if-exists", db_name], capture_output=True, text=True)


def test_wdi_foundational_bundle_does_not_create_forbidden_scope() -> None:
    forbidden_paths = [
        PROJECT_ROOT / "src/macroforge/wdi_client.py",
        PROJECT_ROOT / "src/macroforge/wdi_provider_registry.py",
        PROJECT_ROOT / "src/macroforge/wdi_full_catalog_loader.py",
        PROJECT_ROOT / "src/macroforge/knowledgeforge_query_layer.py",
        PROJECT_ROOT / "src/macroforge/controlled_expansion.py",
    ]
    assert not any(path.exists() for path in forbidden_paths)
