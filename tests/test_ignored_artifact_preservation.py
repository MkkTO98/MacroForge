from __future__ import annotations

import copy
import importlib.util
import json
import marshal
import os
import socket
import stat
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "check_coherence.py"
spec = importlib.util.spec_from_file_location("check_coherence_ignored_artifacts", MODULE_PATH)
assert spec and spec.loader
coherence = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = coherence
spec.loader.exec_module(coherence)

_ABSENT = object()


def _git(root: Path, *args: str) -> bytes:
    return subprocess.run(
        ["git", *args], cwd=root, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    ).stdout


def _policy(protected: list[dict] | None = None) -> dict:
    return {
        "schema": "macroforge-ignored-artifact-policy-v1",
        "protected_artifacts": protected or [],
        "disposable_classes": ["pytest-cache", "python-bytecode"],
    }


def _protected(path: str = "local/evidence.bin", **overrides: object) -> dict:
    value: dict[str, object] = {
        "path": path,
        "classification": "local operational evidence",
        "governing_reason": "required to reproduce the bounded task decision",
        "owner": "TASK-PF-TEST",
        "producing_mechanism": "synthetic test fixture",
        "lifecycle_semantics": "preserve exactly until explicit supersession",
        "content_origin": "authored",
        "publication_expectation": "local-only",
    }
    value.update(overrides)
    return value


def _pyc_bytes(source: str = "value = 1") -> bytes:
    return importlib.util.MAGIC_NUMBER + (b"\x00" * 12) + marshal.dumps(compile(source, "fixture.py", "exec"))


class IgnoredArtifactPreservationTests(unittest.TestCase):
    def setUp(self) -> None:
        self._td = tempfile.TemporaryDirectory()
        self.root = Path(self._td.name)
        _git(self.root, "init", "-q")
        _git(self.root, "config", "user.name", "Test")
        _git(self.root, "config", "user.email", "test@example.invalid")
        (self.root / ".gitignore").write_text(
            "local/\n.pytest_cache/\n__pycache__/\n*.pyc\n", encoding="utf-8"
        )
        (self.root / "tracked.txt").write_text("tracked\n", encoding="utf-8")
        _git(self.root, "add", ".gitignore", "tracked.txt")
        _git(self.root, "commit", "-qm", "fixture")
        cache_tag = self.root / ".pytest_cache" / "CACHEDIR.TAG"
        cache_tag.parent.mkdir(parents=True, exist_ok=True)
        cache_tag.write_text(
            "Signature: 8a477f597d28d172789f06886806bc55\n", encoding="utf-8"
        )

    def tearDown(self) -> None:
        self._td.cleanup()

    def _write(self, rel: str, data: bytes) -> Path:
        path = self.root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        path.chmod(0o644)
        return path

    def _capture(self, policy: dict, candidates: tuple[str, ...] = ()) -> dict:
        return coherence.capture_non_git_artifact_preservation(
            self.root, policy, authored_candidate_paths=candidates
        )

    def _compare(self, baseline: dict, current: dict) -> dict:
        return coherence.compare_non_git_artifact_preservation(
            baseline,
            current,
            expected_baseline_identity=baseline["evidence_identity"],
        )

    def test_declared_protected_artifact_is_deterministic_and_timestamp_immune(self) -> None:
        path = self._write("local/evidence.bin", b"bounded evidence\n")
        first = self._capture(_policy([_protected()]))
        time.sleep(0.01)
        os.utime(path, None)
        second = self._capture(_policy([_protected()]))
        self.assertEqual(first["status"], "pass")
        self.assertEqual(first["protected_identity"], second["protected_identity"])
        self.assertEqual(first["protected_artifacts"], second["protected_artifacts"])
        record = first["protected_artifacts"][0]
        self.assertEqual(record["path"], "local/evidence.bin")
        self.assertEqual(record["size"], len(b"bounded evidence\n"))
        self.assertRegex(record["sha256"], r"^[0-9a-f]{64}$")
        self.assertEqual(record["mode"], "100644")
        self.assertNotIn("mtime", record)

    def test_protected_byte_change_and_removal_fail_comparison(self) -> None:
        path = self._write("local/evidence.bin", b"before")
        baseline = self._capture(_policy([_protected()]))
        path.write_bytes(b"after")
        changed_snapshot = self._capture(_policy([_protected()]))
        changed = self._compare(baseline, changed_snapshot)
        path.unlink()
        missing_snapshot = self._capture(_policy([_protected()]))
        missing = self._compare(baseline, missing_snapshot)
        self.assertEqual(changed["status"], "fail")
        self.assertEqual(changed["changed_protected_artifacts"], ["local/evidence.bin"])
        self.assertEqual(missing_snapshot["status"], "fail")
        self.assertEqual(missing["missing_protected_artifacts"], ["local/evidence.bin"])

    def test_disposable_cache_bytes_and_membership_do_not_change_protected_identity(self) -> None:
        self._write("local/evidence.bin", b"stable")
        cache = self._write(".pytest_cache/v/cache/nodeids", b"one")
        before = self._capture(_policy([_protected()]))
        cache.write_bytes(b"two")
        self._write(f"__pycache__/new.{sys.implementation.cache_tag}.pyc", _pyc_bytes())
        after = self._capture(_policy([_protected()]))
        result = self._compare(before, after)
        self.assertEqual(before["protected_identity"], after["protected_identity"])
        self.assertEqual(result["status"], "pass")
        self.assertTrue(result["accepted_disposable_churn"]["membership_changed"])
        self.assertNotIn("sha256", after["disposable_classes"]["pytest-cache"])

    def test_new_ignored_unclassified_non_disposable_file_fails_closed(self) -> None:
        self._write("local/unknown.dat", b"not declared")
        snapshot = self._capture(_policy())
        self.assertEqual(snapshot["status"], "fail")
        self.assertEqual(snapshot["diagnostics"]["new_unclassified_ignored_artifacts"], ["local/unknown.dat"])

    def test_authored_candidate_cannot_be_disguised_as_disposable_cache(self) -> None:
        disguised = ".pytest_cache/v/cache/nodeids"
        self._write(disguised, b"authored candidate")
        snapshot = self._capture(_policy(), (disguised,))
        self.assertEqual(snapshot["status"], "fail")
        self.assertEqual(snapshot["diagnostics"]["authored_candidates_disguised_as_disposable"], [disguised])
        boundary = coherence.verify_publication_boundary([disguised], [disguised])
        self.assertEqual(boundary["status"], "pass")
        self.assertEqual(snapshot["publication_scope"], [disguised])

    def test_unsafe_policy_paths_symlinks_modes_and_binary_require_explicit_safe_declarations(self) -> None:
        unsafe = self._capture(_policy([_protected("../escape")]))
        self.assertEqual(unsafe["status"], "fail")
        target = self._write("target.txt", b"target")
        link = self.root / "local" / "link"
        link.parent.mkdir(parents=True, exist_ok=True)
        link.symlink_to(target)
        symlink = self._capture(_policy([_protected("local/link")]))
        self.assertEqual(symlink["status"], "fail")
        executable = self._write("local/executable.bin", b"#!/bin/sh\n")
        executable.chmod(0o755)
        mode = self._capture(_policy([_protected("local/executable.bin")]))
        self.assertEqual(mode["status"], "fail")
        link.unlink()
        executable.unlink()
        target.unlink()
        binary = self._write("local/provider.bin", b"\x00provider")
        binary_policy = _policy([_protected(
            "local/provider.bin",
            content_origin="provider-originated payload",
            rights_status="unknown/pending review",
        )])
        blocked_binary = self._capture(binary_policy)
        self.assertEqual(blocked_binary["status"], "fail")
        binary_policy["protected_artifacts"][0]["allow_binary"] = True
        allowed_binary = self._capture(binary_policy)
        self.assertEqual(allowed_binary["status"], "pass")
        self.assertTrue(allowed_binary["protected_artifacts"][0]["binary"])
        self.assertEqual(binary.read_bytes(), b"\x00provider")

    def test_nul_delimited_git_status_handles_newline_and_tab_in_path(self) -> None:
        unusual = "local/line\nbreak\tname.bin"
        self._write(unusual, b"unusual")
        snapshot = self._capture(_policy([_protected(unusual)]))
        self.assertEqual(snapshot["status"], "pass")
        self.assertEqual(snapshot["protected_artifacts"][0]["path"], unusual)
        self.assertEqual(snapshot["observation"]["transport"], "git-ls-files-z")

    def test_capture_and_comparison_use_compatible_canonical_identities(self) -> None:
        self._write("local/evidence.bin", b"same")
        first = self._capture(_policy([_protected()]))
        second = self._capture(copy.deepcopy(_policy([_protected()])))
        result = self._compare(first, second)
        self.assertEqual(result["status"], "pass")
        self.assertEqual(result["baseline_protected_identity"], result["current_protected_identity"])
        self.assertEqual(first["canonicalization"], second["canonicalization"])

    def test_cli_capture_and_compare_reuse_coherence_entry_point(self) -> None:
        self._write("local/evidence.bin", b"stable")
        with tempfile.TemporaryDirectory() as evidence_dir:
            evidence = Path(evidence_dir)
            policy_path = evidence / "policy.json"
            baseline_path = evidence / "baseline.json"
            policy_path.write_text(
                json.dumps(_policy([_protected()])), encoding="utf-8"
            )
            baseline = self._capture(_policy([_protected()]))
            baseline_path.write_text(json.dumps(baseline), encoding="utf-8")
            env = os.environ.copy()
            env["PYTHONDONTWRITEBYTECODE"] = "1"
            cp = subprocess.run(
                [
                    sys.executable,
                    str(MODULE_PATH),
                    "--project",
                    str(self.root),
                    "--ignored-artifact-policy",
                    str(policy_path),
                    "--ignored-artifact-baseline",
                    str(baseline_path),
                    "--ignored-artifact-baseline-identity",
                    baseline["evidence_identity"],
                ],
                cwd=self.root,
                env=env,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
        payload = json.loads(cp.stdout)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["ignored_artifact_preservation"]["comparison"]["status"], "pass")

    def test_lifecycle_cli_integrates_preservation_without_merging_publication_scope(self) -> None:
        self._write("local/evidence.bin", b"stable")
        self._write("candidate.py", b"print('candidate')\n")
        record = {
            "output_families": [
                {
                    "name": "authored candidate",
                    "role": "authored tools",
                    "paths": ["candidate.py"],
                    "terminal_disposition": "git-durable project truth",
                    "content_origin": "authored",
                }
            ]
        }
        with tempfile.TemporaryDirectory() as evidence_dir:
            evidence = Path(evidence_dir)
            paths = {
                "policy": evidence / "policy.json",
                "record": evidence / "record.json",
                "boundary": evidence / "boundary.json",
            }
            paths["policy"].write_text(json.dumps(_policy([_protected()])), encoding="utf-8")
            paths["record"].write_text(json.dumps(record), encoding="utf-8")
            paths["boundary"].write_text(json.dumps(["candidate.py"]), encoding="utf-8")
            env = os.environ.copy()
            env["PYTHONDONTWRITEBYTECODE"] = "1"
            cp = subprocess.run(
                [
                    sys.executable,
                    str(MODULE_PATH),
                    "--project",
                    str(self.root),
                    "--lifecycle-closeout",
                    str(paths["record"]),
                    "--publication-boundary",
                    str(paths["boundary"]),
                    "--ignored-artifact-policy",
                    str(paths["policy"]),
                ],
                cwd=self.root,
                env=env,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        self.assertEqual(cp.returncode, 0, cp.stdout + cp.stderr)
        payload = json.loads(cp.stdout)
        self.assertEqual(payload["publication_boundary"]["status"], "pass")
        self.assertEqual(payload["ignored_artifact_preservation"]["status"], "pass")
        self.assertEqual(
            payload["ignored_artifact_preservation"]["capture"]["publication_scope"],
            ["candidate.py"],
        )
        self.assertFalse(
            "candidate.py"
            in {
                item["path"]
                for item in payload["ignored_artifact_preservation"]["capture"]["protected_artifacts"]
            }
        )

    def test_cache_name_without_owned_structure_fails_closed(self) -> None:
        self._write(".pytest_cache/provider-payload.bin", b"not pytest-owned")
        snapshot = self._capture(_policy())
        self.assertEqual(snapshot["status"], "fail")
        self.assertIn(
            ".pytest_cache/provider-payload.bin",
            snapshot["diagnostics"]["new_unclassified_ignored_artifacts"],
        )

    def test_policy_schema_rejects_unknown_fields_and_string_booleans(self) -> None:
        self._write("local/evidence.bin", b"stable")
        declaration = _protected(allow_binary="false", accidental_field="not governed")
        snapshot = self._capture(_policy([declaration]))
        self.assertEqual(snapshot["status"], "fail")
        self.assertTrue(any("unknown fields" in item for item in snapshot["errors"]))
        boolean_snapshot = self._capture(_policy([_protected(allow_binary="false")]))
        self.assertEqual(boolean_snapshot["status"], "fail")
        self.assertTrue(any("must be a boolean" in item for item in boolean_snapshot["errors"]))

    def test_forged_snapshot_identity_fails_comparison(self) -> None:
        self._write("local/evidence.bin", b"stable")
        baseline = self._capture(_policy([_protected()]))
        forged = copy.deepcopy(baseline)
        forged["protected_artifacts"][0]["sha256"] = "0" * 64
        result = self._compare(baseline, forged)
        self.assertEqual(result["status"], "fail")
        self.assertTrue(any("identity" in item for item in result["errors"]))

    def test_recomputed_forged_baseline_fails_external_identity_anchor(self) -> None:
        path = self._write("local/evidence.bin", b"before")
        original = self._capture(_policy([_protected()]))
        path.write_bytes(b"after")
        current = self._capture(_policy([_protected()]))
        forged_baseline = copy.deepcopy(current)
        result = coherence.compare_non_git_artifact_preservation(
            forged_baseline,
            current,
            expected_baseline_identity=original["evidence_identity"],
        )
        self.assertEqual(result["status"], "fail")
        self.assertTrue(any("caller-supplied" in item for item in result["errors"]))

    def test_malformed_nested_snapshot_fails_without_exception(self) -> None:
        self._write("local/evidence.bin", b"stable")
        baseline = self._capture(_policy([_protected()]))
        malformed = copy.deepcopy(baseline)
        malformed["disposable_classes"]["pytest-cache"] = ["not", "an", "object"]
        malformed["evidence_identity"] = coherence._snapshot_evidence_identity(malformed)
        result = self._compare(baseline, malformed)
        self.assertEqual(result["status"], "fail")
        self.assertTrue(any("disposable-class summary" in item for item in result["errors"]))

    def test_nul_path_parser_rejects_truncation_and_preserves_unusual_names(self) -> None:
        paths, errors = coherence._parse_nul_path_list(b"line\nbreak\tname\x00", "test")
        self.assertEqual(errors, [])
        self.assertEqual(paths, ["line\nbreak\tname"])
        _, truncated_errors = coherence._parse_nul_path_list(b"unterminated", "test")
        self.assertTrue(any("unterminated" in item for item in truncated_errors))

    def test_cli_reports_invalid_policy_as_machine_readable_failure(self) -> None:
        with tempfile.TemporaryDirectory() as evidence_dir:
            invalid = Path(evidence_dir) / "invalid.json"
            invalid.write_text("{", encoding="utf-8")
            cp = subprocess.run(
                [sys.executable, str(MODULE_PATH), "--project", str(self.root), "--ignored-artifact-policy", str(invalid)],
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertEqual(cp.returncode, 2)
        payload = json.loads(cp.stdout)
        self.assertEqual(payload["status"], "fail")
        self.assertIn("input failure", payload["ignored_artifact_preservation"]["errors"][0])

    def test_lifecycle_cli_reports_malformed_input_as_json(self) -> None:
        with tempfile.TemporaryDirectory() as evidence_dir:
            invalid = Path(evidence_dir) / "lifecycle.json"
            invalid.write_text("{", encoding="utf-8")
            cp = subprocess.run(
                [sys.executable, str(MODULE_PATH), "--project", str(self.root), "--lifecycle-closeout", str(invalid)],
                text=True,
                capture_output=True,
                check=False,
            )
        self.assertEqual(cp.returncode, 2)
        payload = json.loads(cp.stdout)
        self.assertEqual(payload["status"], "fail")
        self.assertIn("coherence input failure", payload["errors"][0])

    def test_historical_incomplete_snapshot_remains_qualified_while_new_cache_churn_passes(self) -> None:
        self._write("local/evidence.bin", b"stable")
        baseline = coherence.qualify_historical_non_git_snapshot(
            self._capture(_policy([_protected()])),
            "ACKNOWLEDGED NON-MATERIAL PREFLIGHT EVIDENCE LIMITATION",
        )
        baseline["disposable_classes"] = {name: {**summary, "count": 0, "membership_sha256": None, "sample_paths": []} for name, summary in baseline["disposable_classes"].items()}
        baseline["evidence_identity"] = coherence._snapshot_evidence_identity(baseline)
        self._write(".pytest_cache/v/cache/nodeids", b"later cache")
        current = self._capture(_policy([_protected()]))
        result = self._compare(baseline, current)
        self.assertEqual(result["status"], "pass")
        self.assertEqual(
            result["historical_evidence_qualification"],
            "ACKNOWLEDGED NON-MATERIAL PREFLIGHT EVIDENCE LIMITATION",
        )
        self.assertTrue(result["accepted_disposable_churn"]["membership_changed"])
        self.assertFalse(result["claims_complete_historical_ignored_enumeration"])

    def test_git_administrative_component_is_rejected_without_substring_overreach(self) -> None:
        rejected = (".git/config", "nested/.git/config", "a/.git/b")
        for path in rejected:
            with self.subTest(path=path):
                normalized, error = coherence._safe_project_relative_path(path)
                self.assertIsNone(normalized)
                self.assertIn("Git administrative state", error or "")
        accepted = (".github/workflows/test.yml", "nested/.gitkeep", "legit.git/config")
        for path in accepted:
            with self.subTest(path=path):
                self.assertEqual(coherence._safe_project_relative_path(path), (path, None))
        for path in ("../escape", "a/../escape", "/absolute", "a//b", "./a"):
            with self.subTest(path=path):
                self.assertIsNotNone(coherence._safe_project_relative_path(path)[1])

    def test_pyc_container_rejects_invalid_pep552_flags_and_trailing_bytes(self) -> None:
        valid = _pyc_bytes()
        for flags in (2, 4, 0xFFFFFFFF):
            path = f"__pycache__/bad{flags}.{sys.implementation.cache_tag}.pyc"
            malformed = valid[:4] + flags.to_bytes(4, "little") + valid[8:]
            self._write(path, malformed)
            with self.subTest(flags=flags):
                self.assertIsNone(
                    coherence._recognized_disposable_class(self.root, path, {"python-bytecode"})
                )
        trailing_path = f"__pycache__/trailing.{sys.implementation.cache_tag}.pyc"
        self._write(trailing_path, valid + b"trailing")
        self.assertIsNone(
            coherence._recognized_disposable_class(self.root, trailing_path, {"python-bytecode"})
        )

    def test_pyc_container_accepts_supported_timestamp_and_hash_headers_only(self) -> None:
        payload = marshal.dumps(compile("value = 1", "fixture.py", "exec"))
        cases = {
            "timestamp": importlib.util.MAGIC_NUMBER + (0).to_bytes(4, "little") + b"\x00" * 8 + payload,
            "unchecked_hash": importlib.util.MAGIC_NUMBER + (1).to_bytes(4, "little") + b"h" * 8 + payload,
            "checked_hash": importlib.util.MAGIC_NUMBER + (3).to_bytes(4, "little") + b"h" * 8 + payload,
        }
        for label, data in cases.items():
            path = f"__pycache__/{label}.{sys.implementation.cache_tag}.pyc"
            self._write(path, data)
            with self.subTest(label=label):
                self.assertEqual(
                    coherence._recognized_disposable_class(self.root, path, {"python-bytecode"}),
                    "python-bytecode",
                )
        for label, data in {
            "short": importlib.util.MAGIC_NUMBER + b"\x00" * 11,
            "wrong_magic": b"BAD!" + cases["timestamp"][4:],
            "bad_marshal": cases["timestamp"][:16] + b"not-marshal",
        }.items():
            path = f"__pycache__/{label}.{sys.implementation.cache_tag}.pyc"
            self._write(path, data)
            with self.subTest(label=label):
                self.assertIsNone(
                    coherence._recognized_disposable_class(self.root, path, {"python-bytecode"})
                )

    def test_pyc_container_rejects_oversized_valid_payload_before_unmarshal(self) -> None:
        path = f"__pycache__/oversized.{sys.implementation.cache_tag}.pyc"
        self._write(path, _pyc_bytes() + b"\x00" * (16 * 1024 * 1024))
        self.assertIsNone(
            coherence._recognized_disposable_class(self.root, path, {"python-bytecode"})
        )

    def test_pyc_validation_is_non_executing_and_has_deterministic_rejection_diagnostics(self) -> None:
        sentinel = self.root / "executed.txt"
        source = f"from pathlib import Path\nPath({str(sentinel)!r}).write_text('executed')\n"
        data = (
            importlib.util.MAGIC_NUMBER
            + (0).to_bytes(4, "little")
            + b"\x00" * 8
            + marshal.dumps(compile(source, "fixture.py", "exec"))
        )
        valid_path = f"__pycache__/nonexecuting.{sys.implementation.cache_tag}.pyc"
        self._write(valid_path, data)
        self.assertEqual(
            coherence._recognized_disposable_class(self.root, valid_path, {"python-bytecode"}),
            "python-bytecode",
        )
        self.assertFalse(sentinel.exists())

        malformed_path = f"__pycache__/malformed.{sys.implementation.cache_tag}.pyc"
        self._write(malformed_path, data + b"trailing")
        raw = os.fsencode(malformed_path) + b"\x00"
        first = coherence.capture_non_git_artifact_preservation(
            self.root,
            _policy(),
            authored_candidate_paths=(),
            ignored_paths_z=raw,
            untracked_paths_z=b"",
        )
        second = coherence.capture_non_git_artifact_preservation(
            self.root,
            _policy(),
            authored_candidate_paths=(),
            ignored_paths_z=raw,
            untracked_paths_z=b"",
        )
        self.assertEqual(first["status"], "fail")
        self.assertEqual(first["errors"], second["errors"])
        self.assertTrue(any(malformed_path in item for item in first["errors"]))
        self.assertFalse(sentinel.exists())

    def test_pyc_container_rejects_truncated_timestamp_and_hash_headers(self) -> None:
        prefixes = {
            "timestamp": importlib.util.MAGIC_NUMBER + (0).to_bytes(4, "little") + b"\x00" * 7,
            "unchecked_hash": importlib.util.MAGIC_NUMBER + (1).to_bytes(4, "little") + b"h" * 7,
            "checked_hash": importlib.util.MAGIC_NUMBER + (3).to_bytes(4, "little") + b"h" * 7,
        }
        for label, data in prefixes.items():
            path = f"__pycache__/truncated-{label}.{sys.implementation.cache_tag}.pyc"
            self._write(path, data)
            with self.subTest(label=label):
                self.assertIsNone(
                    coherence._recognized_disposable_class(self.root, path, {"python-bytecode"})
                )

    def test_git_mode_rejects_special_bits_and_normalizes_safe_regular_modes(self) -> None:
        regular = stat.S_IFREG
        self.assertEqual(coherence._git_mode(regular | 0o600), "100644")
        self.assertEqual(coherence._git_mode(regular | 0o644), "100644")
        self.assertEqual(coherence._git_mode(regular | 0o700), "100755")
        for special in (stat.S_ISUID, stat.S_ISGID, stat.S_ISVTX):
            with self.subTest(special=special):
                with self.assertRaises(ValueError):
                    coherence._git_mode(regular | 0o644 | special)
        for file_type in (stat.S_IFDIR, stat.S_IFIFO, stat.S_IFSOCK, stat.S_IFCHR, stat.S_IFBLK):
            with self.subTest(file_type=file_type):
                with self.assertRaises(ValueError):
                    coherence._git_mode(file_type | 0o644)

    def test_capture_rejects_special_mode_and_honors_explicit_executable_transition(self) -> None:
        path = self._write("local/tool.bin", b"#!/bin/sh\n")
        path.chmod(0o4644)
        unsafe = self._capture(_policy([_protected("local/tool.bin")]))
        self.assertEqual(unsafe["status"], "fail")
        path.chmod(0o755)
        blocked = self._capture(_policy([_protected("local/tool.bin")]))
        allowed = self._capture(_policy([_protected("local/tool.bin", allow_executable=True)]))
        self.assertEqual(blocked["status"], "fail")
        self.assertEqual(allowed["status"], "pass")
        self.assertEqual(allowed["protected_artifacts"][0]["mode"], "100755")

    def test_provider_rights_use_existing_canonical_classifications(self) -> None:
        self._write("local/provider.bin", b"provider")
        accepted = (
            "unknown/pending review",
            "unknown/pending review where provider redistribution has not been affirmatively classified",
            coherence.PERMITTED_RIGHTS_STATUS,
        )
        for value in accepted:
            with self.subTest(value=value):
                snapshot = self._capture(_policy([_protected(
                    "local/provider.bin",
                    content_origin="provider-originated payload",
                    rights_status=value,
                )]))
                self.assertEqual(snapshot["status"], "pass", snapshot["errors"])
        for value in (None, "", "   ", "arbitrary authority", 7):
            declaration = _protected(
                "local/provider.bin",
                content_origin="provider-originated payload",
            )
            if value is not None:
                declaration["rights_status"] = value
            with self.subTest(value=value):
                snapshot = self._capture(_policy([declaration]))
                self.assertEqual(snapshot["status"], "fail")
                self.assertTrue(any("rights_status" in item for item in snapshot["errors"]))

    def test_declared_candidate_must_exist_in_tracked_or_observed_scope(self) -> None:
        missing = self._capture(_policy(), ("missing.py",))
        self.assertEqual(missing["status"], "fail")
        self.assertTrue(any("missing.py" in item for item in missing["errors"]))
        excluded = self._write("excluded.py", b"x = 1\n")
        self.assertTrue(excluded.is_file())
        excluded_snapshot = coherence.capture_non_git_artifact_preservation(
            self.root,
            _policy(),
            authored_candidate_paths=("excluded.py",),
            ignored_paths_z=b"",
            untracked_paths_z=b"",
        )
        self.assertEqual(excluded_snapshot["status"], "fail")
        excluded.unlink()
        tracked = self._capture(_policy(), ("tracked.txt",))
        self.assertEqual(tracked["status"], "pass", tracked["errors"])

    def test_declared_candidate_rejects_directory_symlinks_and_duplicate_spelling(self) -> None:
        (self.root / "candidate-dir").mkdir()
        directory = self._capture(_policy(), ("candidate-dir",))
        self.assertEqual(directory["status"], "fail")
        target = self._write("target.py", b"x = 1\n")
        (self.root / "candidate-link.py").symlink_to(target)
        link = coherence.capture_non_git_artifact_preservation(
            self.root,
            _policy(),
            authored_candidate_paths=("candidate-link.py",),
            ignored_paths_z=b"",
            untracked_paths_z=b"candidate-link.py\x00",
        )
        self.assertEqual(link["status"], "fail")
        real_dir = self.root / "real-dir"
        real_dir.mkdir()
        (real_dir / "child.py").write_text("x = 1\n", encoding="utf-8")
        (self.root / "linked-dir").symlink_to(real_dir, target_is_directory=True)
        ancestor_link = coherence.capture_non_git_artifact_preservation(
            self.root,
            _policy(),
            authored_candidate_paths=("linked-dir/child.py",),
            ignored_paths_z=b"",
            untracked_paths_z=b"linked-dir/child.py\x00",
        )
        self.assertEqual(ancestor_link["status"], "fail")
        duplicate = self._capture(_policy(), ("tracked.txt", "tracked.txt"))
        self.assertEqual(duplicate["status"], "fail")
        normalized_collision = self._capture(_policy(), ("tracked.txt", "a/../tracked.txt"))
        self.assertEqual(normalized_collision["status"], "fail")

    def test_snapshot_expected_identity_is_explicitly_caller_supplied_not_authenticated(self) -> None:
        self._write("local/evidence.bin", b"stable")
        baseline = self._capture(_policy([_protected()]))
        result = self._compare(baseline, copy.deepcopy(baseline))
        self.assertEqual(result["expected_identity_authority"], "caller-supplied assertion")
        forged = copy.deepcopy(baseline)
        forged["evidence_identity"] = "0" * 64
        rejected = coherence.compare_non_git_artifact_preservation(
            forged,
            baseline,
            expected_baseline_identity=baseline["evidence_identity"],
        )
        self.assertEqual(rejected["status"], "fail")
        self.assertFalse(any("external" in item or "authenticated" in item for item in rejected["errors"]))

    def test_special_files_reject_promptly_and_regular_files_preserve_modes(self) -> None:
        probe = """
import importlib.util
from pathlib import Path
spec = importlib.util.spec_from_file_location('probe_coherence', {module!r})
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
module._read_regular_file_no_follow(Path({root!r}), {path!r})
"""
        fifo = self.root / "local" / "no-writer.fifo"
        fifo.parent.mkdir(parents=True, exist_ok=True)
        os.mkfifo(fifo)
        with self.assertRaises(subprocess.CalledProcessError):
            subprocess.run(
                [sys.executable, "-c", probe.format(module=str(MODULE_PATH), root=str(self.root), path="local/no-writer.fifo")],
                check=True,
                timeout=1,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

        writer_fifo = self.root / "local" / "writer.fifo"
        os.mkfifo(writer_fifo)
        writer_fd = os.open(writer_fifo, os.O_RDWR | os.O_NONBLOCK)
        try:
            with self.assertRaises(ValueError):
                coherence._read_regular_file_no_follow(self.root, "local/writer.fifo")
        finally:
            os.close(writer_fd)

        socket_path = self.root / "local" / "probe.socket"
        with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as server:
            server.bind(str(socket_path))
            with self.assertRaises(ValueError):
                coherence._read_regular_file_no_follow(self.root, "local/probe.socket")
        (self.root / "local" / "directory").mkdir()
        with self.assertRaises(ValueError):
            coherence._read_regular_file_no_follow(self.root, "local/directory")
        regular = self._write("local/regular.txt", b"regular")
        self.assertEqual(coherence._read_regular_file_no_follow(self.root, "local/regular.txt")[0], b"regular")
        regular.chmod(0o755)
        data, st = coherence._read_regular_file_no_follow(self.root, "local/regular.txt")
        self.assertEqual(data, b"regular")
        self.assertEqual(coherence._git_mode(st.st_mode), "100755")
        (self.root / "local" / "regular-link").symlink_to(regular)
        with self.assertRaises((OSError, ValueError)):
            coherence._read_regular_file_no_follow(self.root, "local/regular-link")

        race_path = self._write("local/race.txt", b"pinned")
        replacement = self._write("local/replacement.txt", b"replacement")
        original_open = coherence._open_beneath_no_symlink
        replaced = False
        def replace_after_pin(root: Path, path: str, flags: int) -> int:
            nonlocal replaced
            descriptor = original_open(root, path, flags)
            if path == "local/race.txt" and flags & os.O_PATH and not replaced:
                os.replace(replacement, race_path)
                replaced = True
            return descriptor
        setattr(coherence, "_open_beneath_no_symlink", replace_after_pin)
        try:
            race_data, _ = coherence._read_regular_file_no_follow(self.root, "local/race.txt")
        finally:
            setattr(coherence, "_open_beneath_no_symlink", original_open)
        self.assertEqual(race_data, b"pinned")
        self.assertEqual(race_path.read_bytes(), b"replacement")

    def test_supplied_observations_require_canonical_independent_git_agreement(self) -> None:
        self._write("local/evidence.bin", b"evidence")
        self._write(".pytest_cache/v/cache/nodeids", b"[]")
        policy = _policy([_protected()])
        ignored = _git(self.root, "ls-files", "--others", "--ignored", "--exclude-standard", "-z")
        untracked = _git(self.root, "ls-files", "--others", "--exclude-standard", "-z")

        discovered = self._capture(policy)
        self.assertEqual(discovered["status"], "pass", discovered["errors"])
        self.assertEqual(discovered["observation"]["provenance"], "independent-git-discovery")
        self.assertTrue(discovered["observation"]["ignored_enumeration_complete"])

        matching = coherence.capture_non_git_artifact_preservation(
            self.root, policy, ignored_paths_z=ignored, untracked_paths_z=untracked
        )
        self.assertEqual(matching["status"], "pass", matching["errors"])
        self.assertEqual(
            matching["observation"]["provenance"],
            "caller-supplied-verified-against-independent-git-discovery",
        )
        self.assertTrue(matching["observation"]["ignored_enumeration_complete"])

        ignored_fields = [field for field in ignored.split(b"\x00") if field]
        malformed_cases = {
            "empty": (b"", b""),
            "incomplete": (b"\x00".join(ignored_fields[:-1]) + (b"\x00" if ignored_fields[:-1] else b""), untracked),
            "extra": (ignored + b"ghost\x00", untracked),
            "reordered": (b"\x00".join(reversed(ignored_fields)) + b"\x00", untracked),
            "duplicate": (ignored + ignored_fields[0] + b"\x00", untracked),
            "unterminated": (ignored[:-1], untracked),
        }
        for label, (supplied_ignored, supplied_untracked) in malformed_cases.items():
            with self.subTest(label=label):
                snapshot = coherence.capture_non_git_artifact_preservation(
                    self.root,
                    policy,
                    ignored_paths_z=supplied_ignored,
                    untracked_paths_z=supplied_untracked,
                )
                self.assertEqual(snapshot["status"], "fail")
                self.assertFalse(snapshot["observation"]["ignored_enumeration_complete"])
                self.assertEqual(snapshot["observation"]["transport"], "caller-supplied-nul-path-lists")

    def test_one_sided_observation_arguments_are_always_incomplete_and_unverified(self) -> None:
        policy = _policy()

        def assert_one_sided(**kwargs: bytes) -> None:
            snapshot = coherence.capture_non_git_artifact_preservation(self.root, policy, **kwargs)
            observation = snapshot["observation"]
            self.assertEqual(snapshot["status"], "fail", snapshot)
            self.assertIn(
                "ignored_paths_z and untracked_paths_z must be supplied together",
                snapshot["errors"],
            )
            self.assertFalse(observation["ignored_enumeration_complete"])
            self.assertEqual(observation["provenance"], "caller-supplied-unverified")
            self.assertNotEqual(
                observation["provenance"],
                "caller-supplied-verified-against-independent-git-discovery",
            )
            self.assertTrue(observation["caller_supplied_observations"])

        ignored = _git(self.root, "ls-files", "--others", "--ignored", "--exclude-standard", "-z")
        untracked = _git(self.root, "ls-files", "--others", "--exclude-standard", "-z")
        self.assertTrue(ignored)
        self.assertEqual(untracked, b"")

        assert_one_sided(ignored_paths_z=ignored)
        assert_one_sided(ignored_paths_z=b"")
        assert_one_sided(untracked_paths_z=b"")

        loose = self._write("loose.txt", b"untracked")
        ignored_nonempty = _git(self.root, "ls-files", "--others", "--ignored", "--exclude-standard", "-z")
        untracked_nonempty = _git(self.root, "ls-files", "--others", "--exclude-standard", "-z")
        self.assertTrue(ignored_nonempty)
        self.assertTrue(untracked_nonempty)
        assert_one_sided(ignored_paths_z=ignored_nonempty)
        assert_one_sided(untracked_paths_z=untracked_nonempty)

        marker = self.root / ".pytest_cache" / "CACHEDIR.TAG"
        marker.unlink()
        marker.parent.rmdir()
        self.assertEqual(
            _git(self.root, "ls-files", "--others", "--ignored", "--exclude-standard", "-z"),
            b"",
        )
        assert_one_sided(untracked_paths_z=untracked_nonempty)
        assert_one_sided(ignored_paths_z=b"")

        loose.unlink()
        self.assertEqual(_git(self.root, "ls-files", "--others", "--exclude-standard", "-z"), b"")
        both_empty = coherence.capture_non_git_artifact_preservation(
            self.root, policy, ignored_paths_z=b"", untracked_paths_z=b""
        )
        self.assertEqual(both_empty["status"], "pass", both_empty["errors"])
        self.assertTrue(both_empty["observation"]["ignored_enumeration_complete"])
        self.assertEqual(
            both_empty["observation"]["provenance"],
            "caller-supplied-verified-against-independent-git-discovery",
        )

    def test_discovery_command_failure_cannot_produce_complete_evidence(self) -> None:
        original_run = coherence.subprocess.run
        def failed_git(*args: object, **kwargs: object) -> subprocess.CompletedProcess[bytes]:
            command = args[0]
            if isinstance(command, list) and command[:2] == ["git", "ls-files"]:
                return subprocess.CompletedProcess(command, 7, b"", b"failure")
            return original_run(*args, **kwargs)
        coherence.subprocess.run = failed_git
        try:
            snapshot = self._capture(_policy())
        finally:
            coherence.subprocess.run = original_run
        self.assertEqual(snapshot["status"], "fail")
        self.assertFalse(snapshot["observation"]["ignored_enumeration_complete"])
        self.assertTrue(any("Git" in error and "exit 7" in error for error in snapshot["errors"]))

    def test_pytest_marker_has_exact_bounded_contract_and_rejects_unsafe_markers(self) -> None:
        marker = self.root / ".pytest_cache" / "CACHEDIR.TAG"
        member = self._write(".pytest_cache/README.md", b"cache")
        self.assertEqual(
            coherence._recognized_disposable_class(self.root, ".pytest_cache/README.md", {"pytest-cache"}),
            "pytest-cache",
        )
        marker.write_bytes(b"Signature: 8a477f597d28d172789f06886806bc55")
        self.assertIsNone(coherence._recognized_disposable_class(self.root, ".pytest_cache/README.md", {"pytest-cache"}))
        marker.write_bytes(b"malformed\n")
        self.assertIsNone(coherence._recognized_disposable_class(self.root, ".pytest_cache/README.md", {"pytest-cache"}))
        marker.write_bytes(b"Signature: 8a477f597d28d172789f06886806bc55\n")
        with marker.open("r+b") as handle:
            handle.truncate(coherence.MAX_PYTEST_CACHE_MARKER_BYTES + 1)
        self.assertIsNone(coherence._recognized_disposable_class(self.root, ".pytest_cache/README.md", {"pytest-cache"}))
        with marker.open("wb") as handle:
            handle.write(b"Signature: 8a477f597d28d172789f06886806bc55\n")
            handle.truncate(64 * 1024 * 1024)
        started = time.monotonic()
        self.assertIsNone(coherence._recognized_disposable_class(self.root, ".pytest_cache/README.md", {"pytest-cache"}))
        self.assertLess(time.monotonic() - started, 1.0)
        marker.unlink()
        marker.symlink_to(member)
        self.assertIsNone(coherence._recognized_disposable_class(self.root, ".pytest_cache/README.md", {"pytest-cache"}))
        marker.unlink()
        self.assertIsNone(coherence._recognized_disposable_class(self.root, ".pytest_cache/README.md", {"pytest-cache"}))
        os.mkfifo(marker)
        started = time.monotonic()
        self.assertIsNone(coherence._recognized_disposable_class(self.root, ".pytest_cache/README.md", {"pytest-cache"}))
        self.assertLess(time.monotonic() - started, 1.0)

    def test_bounded_governance_record_uses_durable_authorship_scoped_claims(self) -> None:
        report_path = ROOT / "artifacts" / "reports" / "R-20260801-ignored-artifact-preservation-governance-closeout.json"
        record = json.loads(report_path.read_text(encoding="utf-8"))
        boundary = list(record["output_families"][0]["paths"])
        result = coherence.validate_lifecycle_closeout(record, boundary)
        self.assertEqual(result["status"], "pass", result["errors"])
        self.assertEqual(record["lifecycle_profile"], coherence.IGNORED_ARTIFACT_LIFECYCLE_PROFILE)
        self.assertEqual(record["publication"]["transition_model"], "state-conditioned-publication-v1")
        self.assertEqual(
            record["publication"]["candidate_identity_binding"],
            "external-review-binds-exact-candidate-bytes",
        )
        self.assertEqual(
            record["publication"]["remote_publication_requirement"],
            "exact-commit-verified-at-authoritative-remote",
        )
        self.assertEqual(record["publication"]["successor_activation"], "never-implicit")
        self.assertEqual(record["candidate_state"]["representation"], "transition-invariant-candidate-record")
        self.assertEqual(
            record["candidate_state"]["commit_publication_separation"],
            "local-commit-is-not-verified-remote-publication",
        )
        self.assertEqual([event["sequence"] for event in record["events"]], list(range(1, 17)))
        self.assertEqual(record["events"][1]["disposition"], "blocked-no-publication")
        self.assertEqual(record["events"][3]["disposition"], "blocked-no-publication")
        self.assertEqual(record["events"][5]["disposition"], "blocked-no-publication")
        self.assertEqual(record["events"][6]["disposition"], "bounded-correction-implemented")
        self.assertEqual(record["events"][7]["disposition"], "blocked-no-publication")
        self.assertEqual(record["events"][8]["disposition"], "bounded-correction-implemented")
        self.assertEqual(
            record["events"][6]["verification_state"],
            "internal-verification-complete-independent-audit-pending-at-correction",
        )
        self.assertEqual(
            record["events"][8]["verification_state"],
            "internal-verification-complete-independent-reaudit-pending-at-correction",
        )
        self.assertEqual(record["events"][11]["disposition"], "blocked-no-publication")
        self.assertEqual(record["events"][14]["findings"], ["publication-transition-fixed-point-defect"])
        self.assertEqual(record["events"][15]["event_type"], "sixth-corrective-pass")
        self.assertFalse(any(event["publication_occurred"] for event in record["events"]))
        self.assertTrue(all(event["publication_authority"] == "not-granted" for event in record["events"]))
        self.assertEqual(record["reproducibility"]["scope"], "prospective-bounded")
        self.assertEqual(record["reproducibility"]["historical_completeness"], "not-claimed")

    def test_record_specific_profile_rejects_every_noncanonical_output_family_shape(self) -> None:
        report_path = ROOT / "artifacts" / "reports" / "R-20260801-ignored-artifact-preservation-governance-closeout.json"
        valid = json.loads(report_path.read_text(encoding="utf-8"))
        canonical_boundary = list(valid["output_families"][0]["paths"])
        canonical_family = copy.deepcopy(valid["output_families"][0])

        def assert_rejected(name: str, families: object, boundary: list[str] | None = None) -> None:
            record = copy.deepcopy(valid)
            if families is _ABSENT:
                record.pop("output_families", None)
            else:
                record["output_families"] = families
            result = coherence.validate_lifecycle_closeout(
                record,
                canonical_boundary if boundary is None else boundary,
            )
            self.assertEqual(result["status"], "fail", f"{name}: {result}")

        minimally_valid_generic = {
            "name": "extra generated record",
            "role": "generated report",
            "paths": ["extra/generated.json"],
            "terminal_disposition": "generated/rebuildable",
            "content_origin": "generated",
        }
        claim_bearing = {
            "name": "extra authored truth",
            "role": "authored implementation",
            "paths": ["extra/authority.py"],
            "terminal_disposition": "git-durable project truth",
            "content_origin": "authored",
        }
        cases = (
            ("absent", _ABSENT, None),
            ("null", None, None),
            ("non-list", {"family": canonical_family}, None),
            ("empty", [], None),
            ("two otherwise-valid families", [canonical_family, copy.deepcopy(canonical_family)], None),
            ("valid plus minimal generic", [canonical_family, minimally_valid_generic], None),
            ("valid plus claim-bearing", [canonical_family, claim_bearing], None),
            (
                "claim-bearing plus matching expanded boundary",
                [canonical_family, claim_bearing],
                sorted(canonical_boundary + ["extra/authority.py"], key=os.fsencode),
            ),
        )
        for name, families, boundary in cases:
            with self.subTest(name=name):
                assert_rejected(name, families, boundary)

        legitimate = coherence.validate_lifecycle_closeout(valid, canonical_boundary)
        self.assertEqual(legitimate["status"], "pass", legitimate["errors"])

    def test_record_specific_profile_anchors_report_and_supplied_boundary_to_code_owned_paths(self) -> None:
        report_path = ROOT / "artifacts" / "reports" / "R-20260801-ignored-artifact-preservation-governance-closeout.json"
        valid = json.loads(report_path.read_text(encoding="utf-8"))
        canonical = list(valid["output_families"][0]["paths"])

        def validate(report_paths: list[str], boundary: list[str]) -> dict:
            record = copy.deepcopy(valid)
            record["output_families"][0]["paths"] = report_paths
            return coherence.validate_lifecycle_closeout(record, boundary)

        arbitrary = [f"arbitrary/p{i:02d}.txt" for i in range(15)]
        one_replaced = sorted(canonical[:-1] + ["arbitrary/replacement.txt"], key=os.fsencode)
        omitted = canonical[:-1]
        added = sorted(canonical + ["arbitrary/addition.txt"], key=os.fsencode)
        duplicated = canonical[:-1] + [canonical[-2]]
        reordered = list(reversed(canonical))
        altered_spelling = sorted(
            ["./" + canonical[0], *canonical[1:]], key=os.fsencode
        )
        absolute = sorted(["/" + canonical[0], *canonical[1:]], key=os.fsencode)
        traversal_alias = sorted(
            ["state/../" + canonical[0], *canonical[1:]], key=os.fsencode
        )
        cases = (
            ("arbitrary matching substitution", arbitrary, arbitrary),
            ("one-path matching substitution", one_replaced, one_replaced),
            ("omission", omitted, omitted),
            ("addition", added, added),
            ("duplicate", duplicated, canonical),
            ("reordering", reordered, canonical),
            ("altered spelling", altered_spelling, altered_spelling),
            ("absolute substitution", absolute, absolute),
            ("traversal alias", traversal_alias, traversal_alias),
            ("canonical report altered supplied boundary", canonical, one_replaced),
            ("altered report canonical supplied boundary", one_replaced, canonical),
        )
        for name, report_paths, boundary in cases:
            with self.subTest(name=name):
                result = validate(report_paths, boundary)
                self.assertEqual(result["status"], "fail", f"{name}: {result}")

        legitimate = validate(canonical, canonical)
        self.assertEqual(legitimate["status"], "pass", legitimate["errors"])

    def test_bounded_governance_validator_rejects_publication_sensitive_or_contradictory_claims(self) -> None:
        report_path = ROOT / "artifacts" / "reports" / "R-20260801-ignored-artifact-preservation-governance-closeout.json"
        valid = json.loads(report_path.read_text(encoding="utf-8"))
        boundary = list(valid["output_families"][0]["paths"])

        def mutation(name: str, apply: object) -> None:
            record = copy.deepcopy(valid)
            apply(record)  # type: ignore[operator]
            result = coherence.validate_lifecycle_closeout(record, boundary)
            self.assertEqual(result["status"], "fail", f"{name}: {result}")
            self.assertTrue(result["errors"], name)

        cases = {
            "top-level publication authority": lambda r: r.__setitem__("publication_authority_granted", True),
            "top-level published state": lambda r: r.__setitem__("publication_state", "published"),
            "pushed at authorship": lambda r: r["candidate_state"].__setitem__("pushed", True),
            "corrective authority": lambda r: r["events"][4].__setitem__("publication_authority", "granted"),
            "authority prose": lambda r: r.__setitem__("authority_note_at_authorship", "This record grants publication authority."),
            "contradictory publication event": lambda r: r["events"].append({"sequence": 6, "date": "2026-08-02", "event_type": "publication-complete", "disposition": "published", "publication_authority": "granted", "publication_occurred": True, "state": {"staged": True, "committed": True, "pushed": True}}),
            "retroactive prospective claim": lambda r: r["reproducibility"].__setitem__("retroactive_proof", "complete"),
            "false historical proof": lambda r: r["reproducibility"].__setitem__("historical_completeness", "complete"),
        }
        for name, apply in cases.items():
            with self.subTest(name=name):
                mutation(name, apply)

        if valid.get("lifecycle_profile") == "macroforge-ignored-artifact-governance-lifecycle-v3":
            nested_unknown = copy.deepcopy(valid)
            nested_unknown["publication"]["trusted"] = True
            result = coherence.validate_lifecycle_closeout(nested_unknown, boundary)
            self.assertEqual(result["status"], "fail")
            self.assertTrue(any("unknown" in error for error in result["errors"]))

    def test_closed_lifecycle_profile_preserves_exact_history_and_transition_invariant(self) -> None:
        report_path = ROOT / "artifacts" / "reports" / "R-20260801-ignored-artifact-preservation-governance-closeout.json"
        valid = json.loads(report_path.read_text(encoding="utf-8"))
        boundary = list(coherence.IGNORED_ARTIFACT_GOVERNANCE_CANONICAL_PATHS)
        result = coherence.validate_lifecycle_closeout(valid, boundary)
        self.assertEqual(result["status"], "pass", result["errors"])

        def rejected(name: str, mutate: object) -> None:
            candidate = copy.deepcopy(valid)
            mutate(candidate)  # type: ignore[operator]
            outcome = coherence.validate_lifecycle_closeout(candidate, boundary)
            self.assertEqual(outcome["status"], "fail", f"{name}: {outcome}")

        cases = {
            "history omission": lambda r: r["events"].pop(10),
            "history addition": lambda r: r["events"].append(copy.deepcopy(r["events"][-1])),
            "history reorder": lambda r: r["events"].__setitem__(slice(14, 16), list(reversed(r["events"][14:16]))),
            "blocked review rewritten pass": lambda r: r["events"][14].__setitem__("disposition", "passed-no-publication-authority"),
            "blocked finding removed": lambda r: r["events"][14].pop("findings"),
            "review directly grants authority": lambda r: r["events"][14].__setitem__("publication_authority", "granted"),
            "commit treated as publication": lambda r: r["publication"].__setitem__("remote_publication_requirement", "local-commit"),
            "implicit successor": lambda r: r["publication"].__setitem__("successor_activation", "automatic"),
            "live-verdict representation": lambda r: r["candidate_state"].__setitem__("representation", "pending-review"),
        }
        for name, mutate in cases.items():
            with self.subTest(name=name):
                rejected(name, mutate)

        commentary = copy.deepcopy(valid)
        commentary["non_authoritative_commentary"].append(
            "This arbitrary prose says publication passed and grants authority."
        )
        outcome = coherence.validate_lifecycle_closeout(commentary, boundary)
        self.assertEqual(outcome["status"], "pass", outcome["errors"])

        exact_pass = {
            "schema": "macroforge-external-publication-review-v1",
            "verdict": "PASS",
            "authenticated": True,
            "byte_recoverable": True,
            "candidate_identity_match": True,
            "ambiguous": False,
        }
        block = {**exact_pass, "verdict": "BLOCK"}
        different_bytes = {**exact_pass, "candidate_identity_match": False}

        cases = (
            ("working-tree-candidate", None, "independent-review-required", False, "pass"),
            ("working-tree-candidate", block, "correction-required", False, "pass"),
            ("working-tree-candidate", different_bytes, "independent-review-required", False, "fail"),
            ("working-tree-candidate", exact_pass, "bounded-publication-permitted", True, "pass"),
            ("local-commit-ahead-of-authoritative-remote", exact_pass, "push-and-verify-remote", False, "pass"),
            ("verified-authoritative-remote-equality", exact_pass, "workstream-closed", False, "pass"),
        )
        for repository_condition, evidence, transition, permitted, status in cases:
            with self.subTest(repository_condition=repository_condition, transition=transition):
                result = coherence.evaluate_publication_transition(repository_condition, evidence)
                self.assertEqual(result["status"], status, result)
                self.assertEqual(result["required_transition"], transition, result)
                self.assertIs(result["publication_permitted"], permitted, result)
                self.assertIs(result["successor_activated"], False, result)

        malformed = (
            {},
            {**exact_pass, "verdict": "MAYBE"},
            {**exact_pass, "authenticated": False},
            {**exact_pass, "byte_recoverable": False},
            {**exact_pass, "ambiguous": True},
            {**exact_pass, "extra_claim": True},
            [exact_pass],
        )
        for evidence in malformed:
            with self.subTest(malformed=evidence):
                result = coherence.evaluate_publication_transition("working-tree-candidate", evidence)
                self.assertEqual(result["status"], "fail", result)
                self.assertFalse(result["publication_permitted"], result)

        for condition in (
            "local-commit-ahead-of-authoritative-remote",
            "verified-authoritative-remote-equality",
        ):
            for evidence in (None, block, different_bytes):
                with self.subTest(condition=condition, evidence=evidence):
                    result = coherence.evaluate_publication_transition(condition, evidence)
                    self.assertEqual(result["status"], "fail", result)
                    self.assertFalse(result["publication_permitted"], result)
                    self.assertFalse(result["successor_activated"], result)

        unknown = coherence.evaluate_publication_transition("unknown-repository-state", exact_pass)
        self.assertEqual(unknown["status"], "fail", unknown)
        self.assertFalse(unknown["publication_permitted"], unknown)


if __name__ == "__main__":
    unittest.main()
