from __future__ import annotations

import copy
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

from macroforge import neutral_evidence_release_exporter as exporter

DB_NAME = "macroforge"
SCOPE = exporter.ExportScope(
    provider_dataset_code="WDI",
    indicators=("NE.EXP.GNFS.ZS", "NE.IMP.GNFS.ZS"),
    entities=("DNK", "SWE", "NOR"),
    start_year=1990,
    end_year=2024,
    frequency="annual",
)


def _require_database() -> None:
    if shutil.which("psql") is None:
        pytest.skip("psql unavailable")
    probe = subprocess.run(["psql", "-d", DB_NAME, "-At", "-c", "SELECT 1"], text=True, capture_output=True)
    if probe.returncode != 0:
        pytest.skip("macroforge database unavailable")


def _export() -> dict:
    _require_database()
    return exporter.build_neutral_evidence_release_export(DB_NAME, SCOPE, created_at="2026-07-11T00:00:00Z")


def test_real_wdi_scope_exports_210_self_describing_items_without_private_schema_leakage():
    document = _export()

    assert document["contract_identity"] == exporter.CONTRACT_IDENTITY
    assert document["producing_system"] == "MacroForge"
    assert document["original_provider"]["provider_identity"] == "World Bank"
    assert document["original_provider"]["dataset_identity"] == "World Development Indicators"
    assert document["selection"]["indicators"] == ["NE.EXP.GNFS.ZS", "NE.IMP.GNFS.ZS"]
    assert document["selection"]["entities"] == ["DNK", "SWE", "NOR"]
    assert document["selection"]["periods"] == [str(y) for y in range(1990, 2025)]
    assert len(document["items"]) == 210
    assert len({item["item_id"] for item in document["items"]}) == 210
    assert all(item["frequency"] == "annual" for item in document["items"])
    assert all(item["unit"] and item["definition"] for item in document["items"])
    assert all(item["missing"] is (item["observation_status"] != "observed") for item in document["items"])
    assert exporter.validate_export_document(document)["valid"] is True
    serialized = json.dumps(document, sort_keys=True)
    forbidden = ["curated.", "meta.", "staging.", "dataset_release_id", "pipeline_run_id", "source_id", "postgres", "credential"]
    assert not [term for term in forbidden if term in serialized]


def test_deterministic_rerun_and_timestamp_exclusion_are_stable():
    first = _export()
    second = exporter.build_neutral_evidence_release_export(DB_NAME, SCOPE, created_at="2026-07-11T01:02:03Z")

    assert first["release_fingerprint"] == second["release_fingerprint"]
    assert first["selection_fingerprint"] == second["selection_fingerprint"]
    assert first["items"] == second["items"]
    assert first["operational_metadata"]["created_at"] != second["operational_metadata"]["created_at"]


def test_selection_and_observation_changes_change_fingerprints():
    document = _export()
    narrowed_scope = exporter.ExportScope(
        provider_dataset_code="WDI",
        indicators=("NE.EXP.GNFS.ZS",),
        entities=("DNK", "SWE", "NOR"),
        start_year=1990,
        end_year=2024,
        frequency="annual",
    )
    narrowed = exporter.build_neutral_evidence_release_export(DB_NAME, narrowed_scope, created_at="2026-07-11T00:00:00Z")
    mutated = copy.deepcopy(document)
    mutated["items"][0]["value"] = str(float(mutated["items"][0]["value"]) + 1.0)
    exporter.recompute_document_fingerprints(mutated)

    assert narrowed["selection_fingerprint"] != document["selection_fingerprint"]
    assert narrowed["release_fingerprint"] != document["release_fingerprint"]
    assert mutated["items"][0]["item_fingerprint"] != document["items"][0]["item_fingerprint"]
    assert mutated["release_fingerprint"] != document["release_fingerprint"]


def test_validator_rejects_duplicates_and_fingerprint_mismatch():
    document = _export()
    duplicated = copy.deepcopy(document)
    duplicated["items"].append(copy.deepcopy(duplicated["items"][0]))
    assert exporter.validate_export_document(duplicated)["valid"] is False

    mismatched = copy.deepcopy(document)
    mismatched["items"][0]["item_fingerprint"] = "sha256:bad"
    assert exporter.validate_export_document(mismatched)["valid"] is False


def test_writer_outputs_manifest_and_rerun_stable_artifact():
    _require_database()
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "export.json"
        manifest = Path(tmp) / "manifest.json"
        result = exporter.write_export(DB_NAME, SCOPE, out, manifest_path=manifest, created_at="2026-07-11T00:00:00Z")
        first_bytes = out.read_bytes()
        first_manifest = json.loads(manifest.read_text())
        second = exporter.write_export(DB_NAME, SCOPE, out, manifest_path=manifest, created_at="2026-07-11T12:00:00Z")

    assert result["valid"] is True
    assert second["release_fingerprint"] == result["release_fingerprint"]
    assert first_manifest["item_count"] == 210
    assert first_manifest["release_fingerprint"] == result["release_fingerprint"]
    assert first_manifest["export_sha256"] == exporter.sha256_bytes(first_bytes)
