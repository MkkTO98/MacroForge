from __future__ import annotations

import json
import os
import shutil
import subprocess
import uuid
from pathlib import Path

from macroforge import eurostat_namq_loader, oecd_sdmx_loader, wdi_loader
from macroforge.deterministic_change_verification import verify_loaded_observed_package
from macroforge.observed_ingestion import (
    build_eurostat_observed_package,
    build_oecd_observed_package,
    build_wdi_observed_package,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
BASE_MIGRATION = PROJECT_ROOT / "db" / "migrations" / "001_v0_schema_foundation.sql"
OECD_MIGRATION = PROJECT_ROOT / "db" / "migrations" / "002_oecd_sdmx_staging.sql"
CANONICAL_DOMAIN_MIGRATION = PROJECT_ROOT / "db" / "migrations" / "003_canonical_domain_dimensions.sql"
EUROSTAT_MIGRATION = PROJECT_ROOT / "db" / "migrations" / "004_eurostat_namq_staging.sql"
WDI_NORMALIZED = PROJECT_ROOT / "data" / "metadata" / "wdi" / "wdi-smoke-normalized.json"
OECD_NORMALIZED = PROJECT_ROOT / "data" / "metadata" / "oecd_sdmx" / "oecd-sdmx-smoke-normalized.json"
EUROSTAT_NORMALIZED = PROJECT_ROOT / "data" / "metadata" / "eurostat" / "eurostat-namq-10-gdp-architecture-spike-normalized.json"


def _postgres_available() -> bool:
    return all(shutil.which(cmd) for cmd in ["createdb", "dropdb", "psql"])


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_loaded_canonical_ingestion_matches_observed_packages_for_all_supported_sources():
    if not _postgres_available():
        return

    db_name = f"macroforge_change_verification_test_{uuid.uuid4().hex[:12]}"
    try:
        subprocess.run(["createdb", db_name], check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as exc:
        if "could not connect" in exc.stderr.lower() or "role" in exc.stderr.lower():
            return
        raise

    try:
        for migration in [BASE_MIGRATION, OECD_MIGRATION, CANONICAL_DOMAIN_MIGRATION, EUROSTAT_MIGRATION]:
            subprocess.run(
                ["psql", "-v", "ON_ERROR_STOP=1", "-d", db_name, "-f", str(migration)],
                check=True,
                capture_output=True,
                text=True,
            )

        wdi_loader.load_wdi_smoke_to_postgres(db_name, WDI_NORMALIZED, run_key="deterministic-verification-wdi")
        oecd_sdmx_loader.load_oecd_sdmx_smoke_to_postgres(
            db_name,
            OECD_NORMALIZED,
            run_key="deterministic-verification-oecd",
            as_of_date="2026-06-03",
        )
        eurostat_namq_loader.load_eurostat_namq_smoke_to_postgres(
            db_name,
            EUROSTAT_NORMALIZED,
            run_key="deterministic-verification-eurostat",
            as_of_date="2026-06-04",
        )

        expected_packages = [
            build_wdi_observed_package(_load(WDI_NORMALIZED)),
            build_oecd_observed_package(_load(OECD_NORMALIZED)),
            build_eurostat_observed_package(_load(EUROSTAT_NORMALIZED)),
        ]

        comparisons = {
            package.source_code: verify_loaded_observed_package(db_name, package)
            for package in expected_packages
        }

        assert set(comparisons) == {"WDI", "OECD_NAAG", "EUROSTAT_NAMQ_GDP"}
        for source_code, comparison in comparisons.items():
            assert comparison.equivalent is True, source_code
            assert comparison.left_fingerprint == comparison.right_fingerprint
            assert comparison.row_count_match is True
            assert comparison.expected_row_count_match is True
            assert comparison.observation_count_match is True
            assert comparison.differing_observations == ()
    finally:
        subprocess.run(["dropdb", "--if-exists", db_name], capture_output=True, text=True)
