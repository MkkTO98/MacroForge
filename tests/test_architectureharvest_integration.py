from __future__ import annotations

import json
from pathlib import Path
from typing import Any, cast

PROJECT_ROOT = Path(__file__).resolve().parents[1]
MANIFEST_PATH = PROJECT_ROOT / "artifacts" / "manifests" / "canonical_assets.json"

ALLOWED_ROLES = {"raw", "staging", "canonical", "report", "mapping", "validation"}
ALLOWED_STATUSES = {"proposed", "provisional", "accepted", "rejected", "retired"}
REQUIRED_FIELDS = {
    "asset_key",
    "role",
    "status",
    "owner_or_review_authority",
    "source_provider_evidence_pointers",
    "related_artifact_paths",
    "canonical_concept_or_mapping_pointer",
    "version",
    "supersedes",
    "superseded_by",
    "notes_caveats",
}


def _manifest() -> dict[str, Any]:
    return cast(dict[str, Any], json.loads(MANIFEST_PATH.read_text(encoding="utf-8")))


def test_generated_project_architectureharvest_placeholders_exist():
    required_paths = [
        PROJECT_ROOT / "architecture" / "architecture_state.md",
        PROJECT_ROOT / "architecture" / "architectureharvest" / "relevance_map.yaml",
        PROJECT_ROOT / "architecture" / "architectureharvest" / "adoption_candidates.md",
        PROJECT_ROOT / "architecture" / "architectureharvest" / "rejected_candidates.md",
        PROJECT_ROOT / "architecture" / "architectureharvest" / "review_history.md",
    ]

    for path in required_paths:
        assert path.exists(), f"missing {path.relative_to(PROJECT_ROOT)}"
        assert path.read_text(encoding="utf-8").strip(), f"empty {path.relative_to(PROJECT_ROOT)}"

    relevance_map = (PROJECT_ROOT / "architecture" / "architectureharvest" / "relevance_map.yaml").read_text(
        encoding="utf-8"
    )
    assert "consult_required_during" in relevance_map
    assert "active" in relevance_map


def test_canonical_asset_manifest_parses_and_uses_required_shape():
    manifest = _manifest()

    assert manifest["schema_version"] == 1
    assert manifest["registry_id"] == "macroforge-canonical-assets"
    assert manifest["implementation_scope"] == "MF-AH-REV-001-narrow-file-backed-registry"
    assets = manifest["assets"]
    assert isinstance(assets, list)
    assert assets

    keys = [asset["asset_key"] for asset in assets]
    assert len(keys) == len(set(keys))

    for asset in assets:
        assert REQUIRED_FIELDS <= set(asset)
        assert asset["role"] in ALLOWED_ROLES
        assert asset["status"] in ALLOWED_STATUSES
        assert asset["owner_or_review_authority"]
        assert isinstance(asset["source_provider_evidence_pointers"], list)
        assert isinstance(asset["related_artifact_paths"], list)
        assert isinstance(asset["notes_caveats"], list)


def test_canonical_asset_manifest_references_existing_artifacts():
    manifest = _manifest()

    for asset in manifest["assets"]:
        for field in ("source_provider_evidence_pointers", "related_artifact_paths"):
            for rel_path in asset[field]:
                if rel_path in {"unknown", "pending_review", None}:
                    continue
                assert (PROJECT_ROOT / rel_path).exists(), f"{asset['asset_key']} references missing {rel_path}"


def test_canonical_asset_manifest_keeps_provider_identity_out_of_canonical_truth():
    manifest = _manifest()
    provider_tokens = {"WDI", "OECD", "EUROSTAT", "NY.GDP.MKTP.CD", "B1GQ", "namq_10_gdp"}

    canonical_assets = [asset for asset in manifest["assets"] if asset["role"] == "canonical"]
    assert canonical_assets

    for asset in canonical_assets:
        assert not any(token in asset["asset_key"] for token in provider_tokens)
        assert asset["source_provider_evidence_pointers"] == []
        assert asset["canonical_concept_or_mapping_pointer"].startswith(
            ("canonical_concept:", "canonical_domain_schema:")
        )

    mapping_assets = [asset for asset in manifest["assets"] if asset["role"] == "mapping"]
    assert mapping_assets
    assert all(
        asset["canonical_concept_or_mapping_pointer"].startswith(("mapping:", "provider_mapping_schema:"))
        for asset in mapping_assets
    )
