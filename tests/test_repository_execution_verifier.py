from __future__ import annotations

import importlib.util
import json
import sys
from argparse import Namespace
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "repository_execution_verifier.py"
spec = importlib.util.spec_from_file_location("repository_execution_verifier", MODULE_PATH)
assert spec and spec.loader
verifier = importlib.util.module_from_spec(spec)
sys.modules["repository_execution_verifier"] = verifier
spec.loader.exec_module(verifier)


def test_summarize_normalized_campaign_requires_classified_exclusions() -> None:
    normalized = {
        "task": "TASK-X",
        "campaign": "Test Campaign",
        "indicator_count": 1,
        "excluded_indicators": ["BAD.IND"],
        "row_count": 10,
        "observed_value_count": 8,
        "missing_value_count": 2,
        "country_count": 2,
        "date_range": "2000:2004",
        "support_bundle": "data/raw/test.json",
        "operational_scope": {"candidate_count": 2, "confidence_cell": "annual scalar"},
        "evidence_manifest": [
            {"indicator": "GOOD.IND", "classification": "compatible"},
            {"indicator": "BAD.IND", "classification": "provider_unavailable"},
        ],
    }

    summary = verifier.summarize_normalized_campaign(normalized)

    assert summary["candidate_count"] == 2
    assert summary["indicator_count"] == 1
    assert summary["excluded_count"] == 1
    assert summary["unclassified_exclusions"] == ["BAD.IND"]


def test_verify_passes_without_database_for_classified_campaign(tmp_path: Path) -> None:
    raw_path = tmp_path / "raw.json"
    normalized_path = tmp_path / "normalized.json"
    task_path = tmp_path / "TASK-X.md"
    report_path = tmp_path / "task-x-report.json"

    raw_path.write_text(json.dumps({"requests": []}), encoding="utf-8")
    task_path.write_text("# TASK-X\n", encoding="utf-8")
    report_path.write_text(json.dumps({"ok": True}), encoding="utf-8")
    normalized_path.write_text(
        json.dumps(
            {
                "task": "TASK-X",
                "campaign": "Test Campaign",
                "indicator_count": 1,
                "excluded_indicators": ["BAD.IND"],
                "row_count": 10,
                "observed_value_count": 8,
                "missing_value_count": 2,
                "country_count": 2,
                "date_range": "2000:2004",
                "support_bundle": str(raw_path),
                "operational_scope": {"candidate_count": 2, "confidence_cell": "annual scalar"},
                "evidence_manifest": [
                    {"indicator": "GOOD.IND", "classification": "compatible"},
                    {
                        "indicator": "BAD.IND",
                        "classification": "provider_unavailable",
                        "provider_evidence_category": "zero_observations_within_requested_scope",
                    },
                ],
            }
        ),
        encoding="utf-8",
    )

    result = verifier.verify(
        Namespace(
            task_id="TASK-X",
            normalized=str(normalized_path),
            raw=str(raw_path),
            task_artifact=str(task_path),
            report_glob=str(report_path),
            database=None,
            run_key=None,
            check_wdi_duplicates=False,
            output=None,
        )
    )

    assert result["status"] == "pass"
    assert result["json_reports"]["valid_count"] == 1
    assert result["normalized_summary"]["unclassified_exclusions"] == []
    assert str(raw_path) in result["artifact_sha256"]
