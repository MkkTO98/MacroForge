from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, cast

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from tools.architecture_reality_audit import check, render_markdown

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


def test_generated_project_metaharvest_placeholders_exist():
    required_paths = [
        PROJECT_ROOT / "architecture" / "architecture_state.md",
        PROJECT_ROOT / "architecture" / "metaharvest" / "relevance_map.yaml",
        PROJECT_ROOT / "architecture" / "metaharvest" / "adoption_candidates.md",
        PROJECT_ROOT / "architecture" / "metaharvest" / "rejected_candidates.md",
        PROJECT_ROOT / "architecture" / "metaharvest" / "review_history.md",
    ]

    for path in required_paths:
        assert path.exists(), f"missing {path.relative_to(PROJECT_ROOT)}"
        assert path.read_text(encoding="utf-8").strip(), f"empty {path.relative_to(PROJECT_ROOT)}"

    relevance_map = (PROJECT_ROOT / "architecture" / "metaharvest" / "relevance_map.yaml").read_text(
        encoding="utf-8"
    )
    assert "consult_required_during" in relevance_map
    assert "active" in relevance_map


def test_architecture_reality_audit_report_uses_stable_project_identity():
    report = check(PROJECT_ROOT)
    markdown = render_markdown(report)

    assert report["project"] == "MacroForge"
    assert "Project: MacroForge" in markdown
    assert "/home/" not in markdown


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



def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _run(cmd: list[str], cwd: Path, *, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, cwd=cwd, text=True, capture_output=True, timeout=60, check=True, env=env)


def _make_audit_fixture(tmp_path: Path, *, git: bool = True, declared_agents: bool = False, declared_metrics: bool = False) -> Path:
    root = tmp_path / "fixture"
    root.mkdir(parents=True)
    for rel in ["tools", "artifacts/reports", "artifacts/tasks", "state", "context", "instructions", "logs"]:
        (root / rel).mkdir(parents=True, exist_ok=True)
    shutil.copy2(PROJECT_ROOT / "tools" / "architecture_reality_audit.py", root / "tools" / "architecture_reality_audit.py")
    for tool in ["check_coherence.py", "context_health.py", "build_context.py"]:
        _write(root / "tools" / tool, "# fixture placeholder\n")
    project_yaml = "name: MacroForge\n"
    if declared_agents:
        project_yaml += "owns_agent_role_instructions: true\n"
    if declared_metrics:
        project_yaml += "owns_metrics_policy: true\n"
    _write(root / "project.yaml", project_yaml)
    _write(root / "AGENTS.md", "Architecture-to-Reality Audit every 5-10 completed tasks before major architecture changes before major governance reviews\n")
    _write(root / "context" / "context_policy.yaml", "context_loading_hierarchy:\n  - state\narchitecture_reality_audit:\n  cadence: every 5-10 completed tasks\n")
    _write(root / "instructions" / "GENERAL_INSTRUCTIONS.md", "Architecture-to-Reality Audit every 5-10 completed tasks before major architecture changes before major governance reviews\n")
    _write(root / "state" / "active_goal.md", "current\n")
    _write(root / "state" / "project_state.md", "current\n")
    _write(root / "state" / "architecture.md", "current\n")
    _write(root / "logs" / "logging_policy.yaml", "raw operational logs\n")
    if git:
        _run(["git", "init"], root)
        _run(["git", "config", "user.email", "test@example.invalid"], root)
        _run(["git", "config", "user.name", "Test"], root)
    return root


def _commit(root: Path, message: str, date: str) -> None:
    _run(["git", "add", "."], root)
    env = {
        "GIT_AUTHOR_DATE": f"{date}T12:00:00+0000",
        "GIT_COMMITTER_DATE": f"{date}T12:00:00+0000",
    }
    _run(["git", "commit", "-m", message], root, env=env)


def _audit(root: Path) -> dict[str, Any]:
    result = subprocess.run(
        ["python3", "tools/architecture_reality_audit.py", "--project", ".", "--json"],
        cwd=root,
        text=True,
        capture_output=True,
        timeout=60,
    )
    assert result.stdout, result.stderr
    return cast(dict[str, Any], json.loads(result.stdout))


def test_audit_cadence_fresh_clone_does_not_count_historical_tasks_from_mtimes(tmp_path: Path):
    root = _make_audit_fixture(tmp_path)
    _write(root / "artifacts" / "reports" / "R-20260713-architecture-reality-audit.md", "# audit\n")
    for index in range(12):
        _write(root / "artifacts" / "tasks" / f"TASK-{index:03d}.md", "status: completed\n")
    _commit(root, "historical tasks", "2026-07-12")
    clone = tmp_path / "clone"
    _run(["git", "clone", str(root), str(clone)], tmp_path)

    report = _audit(clone)

    assert report["completed_tasks_since_latest_audit"] == 0
    assert report["completed_tasks_unknown_temporal_position"] == 0
    assert not report["blocks"]
    assert not [f for f in report["warnings"] if "completed task" in f["message"]]


def test_audit_cadence_tracked_tasks_after_and_before_audit(tmp_path: Path):
    root = _make_audit_fixture(tmp_path)
    _write(root / "artifacts" / "reports" / "R-20260713-architecture-reality-audit.md", "# audit\n")
    _write(root / "artifacts" / "tasks" / "TASK-OLD.md", "status: completed\n")
    _commit(root, "old task", "2026-07-13")
    _write(root / "artifacts" / "tasks" / "TASK-NEW.md", "status: completed\n")
    _commit(root, "new task", "2026-07-14")

    report = _audit(root)

    assert report["completed_tasks_since_latest_audit"] == 1
    assert report["completed_tasks_unknown_temporal_position"] == 0
    assert report["cadence_fully_determined"] is True


def test_audit_cadence_untracked_explicit_post_audit_completion_date_is_counted(tmp_path: Path):
    root = _make_audit_fixture(tmp_path)
    _write(root / "artifacts" / "reports" / "R-20260713-architecture-reality-audit.md", "# audit\n")
    _commit(root, "audit", "2026-07-13")
    _write(root / "artifacts" / "tasks" / "TASK-UNTRACKED.md", "status: completed\ncompleted: 2026-07-14\n")

    report = _audit(root)

    assert report["completed_tasks_since_latest_audit"] == 1
    assert report["completed_tasks_unknown_temporal_position"] == 0


def test_audit_cadence_untracked_dated_filename_is_counted(tmp_path: Path):
    root = _make_audit_fixture(tmp_path)
    _write(root / "artifacts" / "reports" / "R-20260713-architecture-reality-audit.md", "# audit\n")
    _commit(root, "audit", "2026-07-13")
    _write(root / "artifacts" / "tasks" / "TASK-20260714-untracked.md", "status: completed\n")

    report = _audit(root)

    assert report["completed_tasks_since_latest_audit"] == 1
    assert report["completed_tasks_unknown_temporal_position"] == 0


def test_audit_cadence_untracked_undated_task_is_indeterminate(tmp_path: Path):
    root = _make_audit_fixture(tmp_path)
    _write(root / "artifacts" / "reports" / "R-20260713-architecture-reality-audit.md", "# audit\n")
    _commit(root, "audit", "2026-07-13")
    _write(root / "artifacts" / "tasks" / "TASK-UNTRACKED.md", "status: completed\n")

    report = _audit(root)

    assert report["completed_tasks_since_latest_audit"] == 0
    assert report["completed_tasks_unknown_temporal_position"] == 1
    assert report["cadence_fully_determined"] is False
    assert any("unknown temporal position" in f["message"] for f in report["warnings"])


def test_audit_cadence_non_git_tree_uses_dated_tasks_and_flags_undatable_tasks(tmp_path: Path):
    root = _make_audit_fixture(tmp_path, git=False)
    _write(root / "artifacts" / "reports" / "R-20260713-architecture-reality-audit.md", "# audit\n")
    _write(root / "artifacts" / "tasks" / "TASK-20260714-dated.md", "status: completed\n")
    _write(root / "artifacts" / "tasks" / "TASK-UNDATED.md", "status: completed\n")

    report = _audit(root)

    assert report["completed_tasks_since_latest_audit"] == 1
    assert report["completed_tasks_unknown_temporal_position"] == 1
    assert any("unknown temporal position" in f["message"] for f in report["warnings"])


def test_audit_cadence_threshold_warning_and_block_remain_effective(tmp_path: Path):
    warn_root = _make_audit_fixture(tmp_path / "warn")
    _write(warn_root / "artifacts" / "reports" / "R-20260713-architecture-reality-audit.md", "# audit\n")
    _commit(warn_root, "audit", "2026-07-13")
    for index in range(5):
        _write(warn_root / "artifacts" / "tasks" / f"TASK-WARN-{index}.md", "status: completed\n")
    _commit(warn_root, "five tasks", "2026-07-14")
    warn_report = _audit(warn_root)
    assert warn_report["completed_tasks_since_latest_audit"] == 5
    assert any("5 completed task" in f["message"] for f in warn_report["warnings"])
    assert not warn_report["blocks"]

    block_root = _make_audit_fixture(tmp_path / "block")
    _write(block_root / "artifacts" / "reports" / "R-20260713-architecture-reality-audit.md", "# audit\n")
    _commit(block_root, "audit", "2026-07-13")
    for index in range(10):
        _write(block_root / "artifacts" / "tasks" / f"TASK-BLOCK-{index}.md", "status: completed\n")
    _commit(block_root, "ten tasks", "2026-07-14")
    block_report = _audit(block_root)
    assert block_report["completed_tasks_since_latest_audit"] == 10
    assert any("10 completed task" in f["message"] for f in block_report["blocks"])


def test_unowned_obsolete_agents_and_metrics_scaffolds_do_not_warn(tmp_path: Path):
    root = _make_audit_fixture(tmp_path, git=False)
    _write(root / "artifacts" / "reports" / "R-20260713-architecture-reality-audit.md", "# audit\n")

    report = _audit(root)
    messages = [f["message"] for f in report["warnings"] + report["blocks"]]

    assert not any("agent" in message.lower() for message in messages)
    assert not any("metrics" in message.lower() for message in messages)


def test_declared_owned_agent_and_metrics_responsibilities_still_warn_when_missing(tmp_path: Path):
    root = _make_audit_fixture(tmp_path, git=False, declared_agents=True, declared_metrics=True)
    _write(root / "artifacts" / "reports" / "R-20260713-architecture-reality-audit.md", "# audit\n")

    report = _audit(root)
    messages = [f["message"] for f in report["warnings"]]

    assert any("agent-role instruction responsibility" in message for message in messages)
    assert any("metrics-policy responsibility" in message for message in messages)


def test_candidate_audit_has_no_blocks_no_obsolete_scaffold_warnings_and_no_local_paths(tmp_path: Path):
    root = _make_audit_fixture(tmp_path, git=False)
    _write(root / "artifacts" / "reports" / "R-20260713-architecture-reality-audit.md", "# audit\n")

    report = _audit(root)
    messages = [f["message"] for f in report["warnings"] + report["blocks"]]
    markdown = render_markdown(report)

    assert report["project"] == "MacroForge"
    assert report["completed_tasks_since_latest_audit"] == 0
    assert report["completed_tasks_unknown_temporal_position"] == 0
    assert report["cadence_fully_determined"] is True
    assert not report["blocks"]
    assert not any("No role agent instruction files" in message for message in messages)
    assert not any("metrics policy does not clearly define" in message for message in messages)
    assert "/home/" not in markdown
