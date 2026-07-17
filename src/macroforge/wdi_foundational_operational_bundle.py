from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Callable

from macroforge.wdi_energy_use_coal_electricity import (
    ENERGY_PHASE1_EXPECTED_OBSERVATION_COUNT,
    build_wdi_energy_phase1_observed_package,
    write_wdi_energy_phase1_normalized_artifact,
)
from macroforge.wdi_demographics import (
    DEMOGRAPHICS_PHASE1_EXPECTED_OBSERVATION_COUNT,
    build_wdi_demographics_phase1_observed_package,
    write_wdi_demographics_phase1_normalized_artifact,
)
from macroforge.wdi_loader import (
    load_wdi_demographics_phase1_to_postgres,
    load_wdi_energy_phase1_to_postgres,
    load_wdi_operational_phase1_to_postgres,
)
from macroforge.wdi_observed import (
    PHASE1_EXPECTED_OBSERVATION_COUNT,
    build_wdi_operational_phase1_observed_package,
    write_wdi_operational_phase1_normalized_artifact,
)

PROJECT_ROOT = Path(__file__).resolve().parents[2]

MACRO_FIXTURE = PROJECT_ROOT / "data/raw/wdi_operational_phase1/wdi-phase1-all-countries-3i-2000-2023.json"
DEMOGRAPHICS_FIXTURE = PROJECT_ROOT / "data/raw/wdi_demographics_phase1/wdi-demographics-phase1-all-countries-8i-2000-2023.json"
ENERGY_FIXTURE = PROJECT_ROOT / "data/raw/wdi_energy_phase1/wdi-energy-phase1-all-countries-2i-2000-2023.json"
DEFAULT_MANIFEST_PATH = PROJECT_ROOT / "artifacts/reports/task-139-wdi-foundational-operational-bundle-manifest.json"
DEFAULT_LOAD_REPORT_PATH = PROJECT_ROOT / "artifacts/reports/task-139-wdi-foundational-operational-bundle-load-report.json"
DEFAULT_NORMALIZED_DIR = PROJECT_ROOT / "data/processed/wdi_foundational_operational_bundle"

BUNDLE_COMPONENTS = ["macro_phase1", "demographics_phase1", "energy_phase1"]
BUNDLE_EXPECTED_OBSERVATION_COUNT = (
    PHASE1_EXPECTED_OBSERVATION_COUNT
    + DEMOGRAPHICS_PHASE1_EXPECTED_OBSERVATION_COUNT
    + ENERGY_PHASE1_EXPECTED_OBSERVATION_COUNT
)
BUNDLE_EXPECTED_INDICATOR_COUNT = 12
BUNDLE_EXPECTED_PERIOD_RANGE = "2000:2023"


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _component_manifest(
    *,
    component: str,
    fixture_path: Path,
    expected_rows: int,
    package_builder: Callable[[dict[str, Any]], Any],
) -> dict[str, Any]:
    payload = _read_json(fixture_path)
    package = package_builder(payload)
    indicators = sorted({obs.provider_indicator_code for obs in package.observations})
    countries = sorted({obs.provider_territory_code for obs in package.observations})
    years = sorted({obs.period_year for obs in package.observations})
    return {
        "component": component,
        "fixture_path": fixture_path.relative_to(PROJECT_ROOT).as_posix(),
        "raw_sha256": _sha256(fixture_path),
        "row_count": package.row_count,
        "expected_row_count": expected_rows,
        "indicator_count": len(indicators),
        "indicators": indicators,
        "country_count": len(countries),
        "period_range": f"{years[0]}:{years[-1]}",
        "release_key": package.release_key,
    }


def build_wdi_foundational_bundle_manifest() -> dict[str, Any]:
    components = [
        _component_manifest(
            component="macro_phase1",
            fixture_path=MACRO_FIXTURE,
            expected_rows=PHASE1_EXPECTED_OBSERVATION_COUNT,
            package_builder=build_wdi_operational_phase1_observed_package,
        ),
        _component_manifest(
            component="demographics_phase1",
            fixture_path=DEMOGRAPHICS_FIXTURE,
            expected_rows=DEMOGRAPHICS_PHASE1_EXPECTED_OBSERVATION_COUNT,
            package_builder=build_wdi_demographics_phase1_observed_package,
        ),
        _component_manifest(
            component="energy_phase1",
            fixture_path=ENERGY_FIXTURE,
            expected_rows=ENERGY_PHASE1_EXPECTED_OBSERVATION_COUNT,
            package_builder=build_wdi_energy_phase1_observed_package,
        ),
    ]
    all_indicators = sorted({indicator for component in components for indicator in component["indicators"]})
    countries = {component["country_count"] for component in components}
    period_ranges = {component["period_range"] for component in components}
    row_count = sum(component["row_count"] for component in components)
    manifest = {
        "task": "TASK-139",
        "mode": "Operational Dataset Construction",
        "strategic_criterion": "Expected Knowledge Leverage",
        "dataset": "WDI Foundational Operational Bundle",
        "components": BUNDLE_COMPONENTS,
        "component_count": len(components),
        "component_manifests": components,
        "row_count": row_count,
        "expected_row_count": BUNDLE_EXPECTED_OBSERVATION_COUNT,
        "indicator_count": len(all_indicators),
        "indicators": all_indicators,
        "country_count": min(countries) if len(countries) == 1 else sorted(countries),
        "period_range": next(iter(period_ranges)) if len(period_ranges) == 1 else sorted(period_ranges),
        "knowledgeforge_analyses_enabled": [
            "cross_country_macro_context",
            "growth_inflation_population_baselines",
            "demographic_vulnerability_screening",
            "aging_and_dependency_context",
            "energy_security_context",
            "coal_electricity_exposure_context",
            "macro_demographic_energy_country_comparison",
        ],
        "non_goals": [
            "full_WDI_catalog_ingestion",
            "new_WDI_acquisition",
            "generic_WDI_client",
            "provider_registry",
            "scheduler_or_daemon",
            "KnowledgeForge_implementation",
            "canonical_ontology",
            "architecture_redesign",
        ],
    }
    manifest["manifest_fingerprint"] = manifest_fingerprint(manifest, include_self=False)
    return manifest


def manifest_fingerprint(manifest: dict[str, Any], *, include_self: bool = True) -> str:
    payload = dict(manifest)
    if not include_self:
        payload.pop("manifest_fingerprint", None)
    blob = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def write_wdi_foundational_bundle_manifest(path: str | Path = DEFAULT_MANIFEST_PATH) -> dict[str, Any]:
    manifest = build_wdi_foundational_bundle_manifest()
    out = Path(path)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(manifest, sort_keys=True, indent=2), encoding="utf-8")
    return manifest


def _write_normalized_artifacts(normalized_dir: Path) -> dict[str, Path]:
    normalized_dir.mkdir(parents=True, exist_ok=True)
    paths = {
        "macro_phase1": normalized_dir / "wdi-macro-phase1-normalized.json",
        "demographics_phase1": normalized_dir / "wdi-demographics-phase1-normalized.json",
        "energy_phase1": normalized_dir / "wdi-energy-phase1-normalized.json",
    }
    write_wdi_operational_phase1_normalized_artifact(_read_json(MACRO_FIXTURE), paths["macro_phase1"])
    write_wdi_demographics_phase1_normalized_artifact(_read_json(DEMOGRAPHICS_FIXTURE), paths["demographics_phase1"])
    write_wdi_energy_phase1_normalized_artifact(_read_json(ENERGY_FIXTURE), paths["energy_phase1"])
    return paths


def load_wdi_foundational_bundle_to_postgres(
    db_name: str,
    *,
    manifest_path: str | Path = DEFAULT_MANIFEST_PATH,
    normalized_dir: str | Path = DEFAULT_NORMALIZED_DIR,
    load_report_path: str | Path | None = DEFAULT_LOAD_REPORT_PATH,
    run_key_prefix: str = "task-139-wdi-foundational-bundle",
) -> dict[str, Any]:
    paths = _write_normalized_artifacts(Path(normalized_dir))
    component_loads = {
        "macro_phase1": load_wdi_operational_phase1_to_postgres(
            db_name, paths["macro_phase1"], run_key=f"{run_key_prefix}-macro"
        ),
        "demographics_phase1": load_wdi_demographics_phase1_to_postgres(
            db_name, paths["demographics_phase1"], run_key=f"{run_key_prefix}-demographics"
        ),
        "energy_phase1": load_wdi_energy_phase1_to_postgres(
            db_name, paths["energy_phase1"], run_key=f"{run_key_prefix}-energy"
        ),
    }
    manifest = write_wdi_foundational_bundle_manifest(manifest_path)
    report = {
        "task": "TASK-139",
        "mode": "Operational Dataset Construction",
        "status": "succeeded",
        "component_count": len(component_loads),
        "components": BUNDLE_COMPONENTS,
        "component_loads": component_loads,
        "row_count": manifest["row_count"],
        "fact_rows_reported_by_components": component_loads["energy_phase1"]["fact_rows"],
        "manifest_path": Path(manifest_path).as_posix(),
        "normalized_artifacts": {key: path.as_posix() for key, path in paths.items()},
        "manifest_fingerprint": manifest["manifest_fingerprint"],
    }
    if load_report_path is not None:
        out = Path(load_report_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(report, sort_keys=True, indent=2), encoding="utf-8")
    return report
