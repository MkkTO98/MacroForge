from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "check_coherence.py"
spec = importlib.util.spec_from_file_location("check_coherence", MODULE_PATH)
assert spec and spec.loader
coherence = importlib.util.module_from_spec(spec)
sys.modules["check_coherence"] = coherence
spec.loader.exec_module(coherence)


def _complete_closeout_record() -> dict:
    return {
        "output_families": [
            {"name": "authored implementation", "role": "authored implementation", "paths": ["src/example.py"], "terminal_disposition": "git-durable project truth", "content_origin": "authored"},
            {"name": "local provider evidence", "role": "evidence", "paths": ["data/raw/provider/private.json"], "terminal_disposition": "local/provider evidence", "content_origin": "provider-originated payload", "rights_status": "unknown/pending review", "publication_expectation": "local-only"},
            {"name": "generated report", "role": "generated report", "paths": ["artifacts/reports/generated.json"], "terminal_disposition": "generated/rebuildable", "content_origin": "synthetic"},
        ]
    }


def _write_json(path: Path, payload: object) -> Path:
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path


def _run_cli(tmp_path: Path, record: dict, boundary: object | None = None, *extra: str) -> subprocess.CompletedProcess[str]:
    record_path = _write_json(tmp_path / "closeout.json", record)
    args = [sys.executable, str(MODULE_PATH), "--project", str(ROOT), "--lifecycle-closeout", str(record_path)]
    if boundary is not None:
        boundary_path = _write_json(tmp_path / "boundary.json", boundary)
        args.extend(["--publication-boundary", str(boundary_path)])
    args.extend(extra)
    env = os.environ.copy(); env["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(args, cwd=ROOT, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def _cli_json(cp: subprocess.CompletedProcess[str]) -> dict:
    if not cp.stdout:
        raise AssertionError(cp.stderr)
    return json.loads(cp.stdout)


class LifecycleCloseoutCoherenceTests(unittest.TestCase):
    def test_lifecycle_closeout_passes_with_accounted_output_families(self) -> None:
        result = coherence.validate_lifecycle_closeout(_complete_closeout_record(), {"src/example.py"})
        self.assertEqual(result["status"], "pass")
        self.assertFalse(result["grandfathered_legacy_record"])

    def test_declared_git_durable_family_missing_from_publication_boundary_fails(self) -> None:
        result = coherence.validate_lifecycle_closeout(_complete_closeout_record(), set())
        self.assertEqual(result["status"], "fail")
        self.assertIn("missing from publication boundary", "\n".join(result["errors"]))

    def test_local_provider_evidence_and_generated_output_do_not_have_to_be_staged(self) -> None:
        result = coherence.validate_lifecycle_closeout(_complete_closeout_record(), {"src/example.py"})
        self.assertEqual(result["status"], "pass")

    def test_unknown_rights_provider_payload_cannot_be_publicly_published(self) -> None:
        record = {"output_families": [{"name": "new provider payload", "role": "evidence", "paths": ["data/raw/provider/new.json"], "terminal_disposition": "git-durable project truth", "content_origin": "provider-originated payload", "rights_status": "unknown/pending review"}]}
        result = coherence.validate_lifecycle_closeout(record, {"data/raw/provider/new.json"})
        self.assertEqual(result["status"], "fail")
        self.assertIn("requires rights_status", "\n".join(result["errors"]))

    def test_authored_code_publication_not_blocked_by_local_provider_evidence(self) -> None:
        result = coherence.validate_lifecycle_closeout(_complete_closeout_record(), {"src/example.py"})
        self.assertEqual(result["status"], "pass")

    def test_production_change_full_reproducibility_requires_durable_authored_outputs_or_exception(self) -> None:
        record = {"production_postgresql_state_changed": True, "reproducibility_claim": "full", "output_families": [{"name": "authored implementation", "role": "authored implementation", "paths": ["src/not_published.py"], "terminal_disposition": "pending decision", "content_origin": "authored"}]}
        result = coherence.validate_lifecycle_closeout(record, set())
        record["bounded_reproducibility_exception"] = {"reason": "publication deferred but exact source hash recorded", "recovery_evidence": "sha256:abc123 in task closeout", "owner": "TASK-X", "reconsideration_trigger": "before cleanup or next public release"}
        excepted = coherence.validate_lifecycle_closeout(record, set())
        self.assertEqual(result["status"], "fail")
        self.assertEqual(excepted["status"], "pass")

    def test_content_sensitive_fingerprint_detects_same_status_content_change(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "already_modified.py"
            path.write_text("value = 1\n", encoding="utf-8")
            before = coherence.content_sensitive_file_fingerprints([path])
            path.write_text("value = 2\n", encoding="utf-8")
            after = coherence.content_sensitive_file_fingerprints([path])
        self.assertNotEqual(before[str(path)]["sha256"], after[str(path)]["sha256"])

    def test_unauthorized_additional_publication_paths_are_rejected(self) -> None:
        result = coherence.validate_lifecycle_closeout(_complete_closeout_record(), {"src/example.py", "README.md"})
        self.assertEqual(result["status"], "fail")
        self.assertIn("undeclared paths", "\n".join(result["errors"]))

    def test_legacy_task_artifacts_without_output_families_require_explicit_legacy_mode(self) -> None:
        normal = coherence.validate_lifecycle_closeout({"legacy_record": True, "status": "complete"})
        legacy = coherence.validate_lifecycle_closeout({"legacy_record": True, "status": "complete"}, legacy_mode=True)
        self.assertEqual(normal["status"], "fail")
        self.assertEqual(legacy["status"], "pass")
        self.assertTrue(legacy["grandfathered_legacy_record"])

    def test_publication_boundary_helper_reports_missing_and_unauthorized_paths(self) -> None:
        result = coherence.verify_publication_boundary(["src/example.py", "tests/test_example.py"], ["src/example.py", "README.md"])
        self.assertEqual(result, {"status": "fail", "missing": ["tests/test_example.py"], "unauthorized": ["README.md"]})

    def test_cli_end_to_end_required_behaviors(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            t = Path(td)
            cases = [
                (_complete_closeout_record(), ["src/example.py"], (), 0, "valid forward closeout"),
                ({"status": "complete"}, None, (), 2, "forward omission fails"),
                ({"legacy_record": True, "status": "complete"}, None, ("--legacy-record",), 0, "explicit legacy passes"),
                ({"legacy_record": True, "reopened_historical_task": True, "status": "complete"}, None, ("--legacy-record",), 2, "reopened historical fails"),
                (_complete_closeout_record(), [], (), 2, "missing declared durable path fails"),
                (_complete_closeout_record(), ["src/example.py", "README.md"], (), 2, "unauthorized path fails"),
            ]
            for record, boundary, extra, expected, label in cases:
                cp = _run_cli(t, record, boundary, *extra)
                self.assertEqual(0 if cp.returncode == 0 else 2, expected, label + cp.stdout + cp.stderr)

    def test_cli_provider_rights_and_pg_reproducibility_behaviors(self) -> None:
        provider_unknown = {"output_families": [{"name": "provider payload", "paths": ["data/raw/new.json"], "terminal_disposition": "git-durable project truth", "content_origin": "provider-originated payload", "rights_status": "unknown/pending review"}]}
        provider_no_ref = {"output_families": [{"name": "provider payload", "paths": ["data/raw/new.json"], "terminal_disposition": "git-durable project truth", "content_origin": "provider-originated payload", "rights_status": "permitted with evidence"}]}
        authored = {"output_families": [{"name": "tooling", "paths": ["tools/example.py"], "terminal_disposition": "git-durable project truth", "content_origin": "authored", "role": "authored tools"}]}
        pg_bad = {"production_postgresql_state_changed": True, "reproducibility_claim": "full", "output_families": [{"name": "tooling", "paths": ["tools/not_published.py"], "terminal_disposition": "pending decision", "content_origin": "authored", "role": "authored tools"}]}
        pg_ok = json.loads(json.dumps(pg_bad)); pg_ok["bounded_reproducibility_exception"] = {"reason": "tool publication intentionally deferred", "recovery_evidence": "external archive sha256 abc123", "owner": "TASK-X", "reconsideration_trigger": "before cleanup"}
        with tempfile.TemporaryDirectory() as td:
            t = Path(td)
            self.assertNotEqual(_run_cli(t, provider_unknown, ["data/raw/new.json"]).returncode, 0)
            self.assertNotEqual(_run_cli(t, provider_no_ref, ["data/raw/new.json"]).returncode, 0)
            self.assertEqual(_run_cli(t, authored, ["tools/example.py"]).returncode, 0)
            self.assertNotEqual(_run_cli(t, pg_bad, []).returncode, 0)
            self.assertEqual(_run_cli(t, pg_ok, []).returncode, 0)

    def test_cli_content_fingerprint_changes_for_same_path(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            t = Path(td); tracked_like = t / "already_modified.py"
            tracked_like.write_text("x = 1\n", encoding="utf-8")
            before = _run_cli(t, _complete_closeout_record(), ["src/example.py"], "--fingerprint-path", str(tracked_like))
            tracked_like.write_text("x = 2\n", encoding="utf-8")
            after = _run_cli(t, _complete_closeout_record(), ["src/example.py"], "--fingerprint-path", str(tracked_like))
            self.assertNotEqual(_cli_json(before)["content_sensitive_fingerprints"][str(tracked_like)]["sha256"], _cli_json(after)["content_sensitive_fingerprints"][str(tracked_like)]["sha256"])

    def test_ordinary_check_coherence_json_remains_backward_compatible(self) -> None:
        env = os.environ.copy(); env["PYTHONDONTWRITEBYTECODE"] = "1"
        cp = subprocess.run([sys.executable, str(MODULE_PATH), "--project", str(ROOT), "--json"], cwd=ROOT, env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.assertIn(cp.returncode, (0, 2))
        payload = json.loads(cp.stdout)
        self.assertEqual(sorted(payload), ["blocks", "mode", "warnings"])
        self.assertIsInstance(payload["blocks"], list)
        self.assertIsInstance(payload["warnings"], list)

    def test_cli_validation_failure_returns_nonzero_status(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            cp = _run_cli(Path(td), {"status": "complete"})
        self.assertNotEqual(cp.returncode, 0)

    def test_cli_empty_output_families_cannot_bypass_forward_closeout(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            cp = _run_cli(Path(td), {"status": "complete", "output_families": []})
        self.assertNotEqual(cp.returncode, 0)
        self.assertIn("must not be empty", cp.stdout)

    def test_cli_rejects_publication_validation_without_closeout_input(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            boundary = _write_json(Path(td) / "boundary.json", ["src/example.py"])
            env = os.environ.copy(); env["PYTHONDONTWRITEBYTECODE"] = "1"
            cp = subprocess.run(
                [sys.executable, str(MODULE_PATH), "--project", str(ROOT), "--publication-boundary", str(boundary)],
                cwd=Path(td), env=env, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            )
        self.assertNotEqual(cp.returncode, 0)
        self.assertIn("requires --lifecycle-closeout", cp.stderr)

    def test_cli_resolves_project_relative_fingerprint_paths_and_blocks_missing_paths(self) -> None:
        with tempfile.TemporaryDirectory() as td:
            t = Path(td)
            present = _run_cli(
                t,
                _complete_closeout_record(),
                ["src/example.py"],
                "--fingerprint-path", "CONSTITUTION.md",
            )
            missing = _run_cli(
                t,
                _complete_closeout_record(),
                ["src/example.py"],
                "--fingerprint-path", "does-not-exist.txt",
            )
        present_payload = _cli_json(present)
        self.assertEqual(present.returncode, 0)
        self.assertIsNotNone(present_payload["content_sensitive_fingerprints"]["CONSTITUTION.md"]["sha256"])
        self.assertEqual(present_payload["content_sensitive_fingerprints"]["CONSTITUTION.md"]["scope"], "project-relative")
        self.assertNotEqual(missing.returncode, 0)
        self.assertIn("fingerprint path is unavailable", missing.stdout)

    def test_cli_honors_complete_per_family_publication_deferral(self) -> None:
        record = _complete_closeout_record()
        record["output_families"][0]["deferred_paths"] = ["src/example.py"]
        record["output_families"][0]["bounded_exception"] = {
            "reason": "bounded publication delay",
            "recovery_evidence": "sha256:abc123",
            "owner": "TASK-X",
            "reconsideration_trigger": "next publication review",
        }
        with tempfile.TemporaryDirectory() as td:
            cp = _run_cli(Path(td), record, [])
        self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
        self.assertEqual(_cli_json(cp)["publication_boundary"]["deferred"], ["src/example.py"])


if __name__ == "__main__":
    unittest.main()
