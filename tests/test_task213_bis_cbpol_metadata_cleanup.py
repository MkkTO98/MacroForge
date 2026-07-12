from __future__ import annotations

import importlib.util
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "task213_bis_cbpol_metadata_cleanup.py"
spec = importlib.util.spec_from_file_location("task213_bis_cbpol_metadata_cleanup", MODULE_PATH)
assert spec is not None
cleanup = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(cleanup)


def test_task213_cleanup_scope_constants_are_bounded() -> None:
    assert cleanup.SOURCE_CODE == "BIS_PUBLIC_SDMX_API"
    assert cleanup.DATASET_CODE == "BIS:WS_CBPOL"
    assert cleanup.OBSOLETE_RELEASE_KEY == "bis-ws-cbpol-current-snapshot-2015m01-2026m06"
    assert cleanup.CANONICAL_RELEASE_KEY == "bis-ws-cbpol-snapshot-prepared-20260712t114554z"
    assert cleanup.OBSOLETE_INDICATOR_PATTERN == "BIS:WS_CBPOL:M.%"
    assert cleanup.CANONICAL_INDICATOR_CODE == "BIS:WS_CBPOL:CENTRAL_BANK_POLICY_RATE:PERCENT:M"


def test_task213_cleanup_requires_all_preconditions() -> None:
    audit = {
        "delete_preconditions": {
            "obsolete_release_resolved_exactly_one": True,
            "obsolete_indicators_resolved_exactly_36": True,
            "canonical_release_resolved_exactly_one": True,
            "canonical_indicator_resolved_exactly_one": True,
            "obsolete_release_external_references_zero": True,
            "obsolete_indicators_external_indicator_id_references_zero": True,
            "obsolete_indicator_external_exact_code_occurrences_zero": True,
        }
    }
    assert cleanup.preconditions_pass(audit)
    audit["delete_preconditions"]["obsolete_release_external_references_zero"] = False
    assert not cleanup.preconditions_pass(audit)


def test_task213_snapshot_terminology_is_not_official_publication_release() -> None:
    source = MODULE_PATH.read_text(encoding="utf-8")
    assert "acquired BIS response snapshot/as-of identity based on SDMX message Prepared timestamp" in source
    assert "not an official BIS publication release" in source
