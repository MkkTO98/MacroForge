from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
import tomllib
import unittest
from pathlib import Path
from typing import Any, Callable


PROJECT_ROOT = Path(__file__).resolve().parents[1]
PYPROJECT = PROJECT_ROOT / "pyproject.toml"
LOCKFILE = PROJECT_ROOT / "uv.lock"
CANONICAL_PROVISION = "uv sync --locked --group test"
CANONICAL_TEST_PREFIX = "uv run --locked --group test pytest"
PUBLIC_REGISTRY = "https://pypi.org/simple"
PUBLIC_ARTIFACT_PREFIX = "https://files.pythonhosted.org/"
NAME_PATTERN = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9_.-]*[A-Za-z0-9])?$")
SHA256_PATTERN = re.compile(r"^sha256:[0-9a-f]{64}$")
EXPECTED_REQUIREMENTS = {"pytest": ">=8,<9", "pyyaml": ">=6,<7"}
AUTHORITATIVE_VERIFICATION_DOCS = (
    PROJECT_ROOT / "README.md",
    PROJECT_ROOT / "docs" / "runbooks" / "wdi-v1-runbook.md",
    PROJECT_ROOT / "docs" / "architecture" / "observed-ingestion-representation.md",
)
DEPENDENCY_GUIDANCE_TOOLS = (
    PROJECT_ROOT / "tools" / "install.sh",
    PROJECT_ROOT / "tools" / "run.py",
    PROJECT_ROOT / "tools" / "select_model.py",
)


def _load_toml(path: Path) -> dict[str, Any]:
    with path.open("rb") as handle:
        return tomllib.load(handle)


def _normalize_name(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()


def _requirement_by_name(requirements: list[str]) -> dict[str, str]:
    result: dict[str, str] = {}
    for requirement in requirements:
        match = re.fullmatch(r"([A-Za-z0-9_.-]+)(.*)", requirement)
        if not match:
            raise AssertionError(f"unparseable requirement: {requirement!r}")
        name = _normalize_name(match.group(1))
        if name in result:
            raise AssertionError(f"duplicate direct dependency declaration: {name}")
        result[name] = match.group(2)
    return result


def _supported_major_interval(specifier: str) -> tuple[int, int]:
    match = re.fullmatch(r">=(\d+),<(\d+)", specifier)
    if not match:
        raise AssertionError(f"unsupported direct requirement interval: {specifier!r}")
    lower, upper = (int(value) for value in match.groups())
    if upper <= lower:
        raise AssertionError(f"empty direct requirement interval: {specifier!r}")
    return lower, upper


def _version_major(version: str) -> int:
    match = re.match(r"^(\d+)(?:\.|$)", version)
    if not match:
        raise AssertionError(f"locked version lacks a numeric major: {version!r}")
    return int(match.group(1))


def _validate_dependency_entry(dependency: object) -> dict[str, Any]:
    if not isinstance(dependency, dict):
        raise AssertionError(f"lock dependency entry must be a table: {dependency!r}")
    name = dependency.get("name")
    if not isinstance(name, str) or not NAME_PATTERN.fullmatch(name):
        raise AssertionError(f"invalid lock dependency name: {name!r}")
    for field in ("version", "specifier", "marker"):
        value = dependency.get(field)
        if value is not None and (not isinstance(value, str) or not value.strip()):
            raise AssertionError(f"invalid lock dependency {field}: {value!r}")
    source = dependency.get("source")
    if source is not None and not isinstance(source, dict):
        raise AssertionError(f"invalid lock dependency source: {source!r}")
    return dependency


def _validate_artifact(artifact: object) -> None:
    if not isinstance(artifact, dict):
        raise AssertionError(f"locked distribution must be a table: {artifact!r}")
    url = artifact.get("url")
    digest = artifact.get("hash")
    if not isinstance(url, str) or not url.startswith(PUBLIC_ARTIFACT_PREFIX):
        raise AssertionError(f"non-public or mutable distribution URL: {url!r}")
    if not isinstance(digest, str) or not SHA256_PATTERN.fullmatch(digest):
        raise AssertionError(f"distribution lacks SHA-256 integrity metadata: {digest!r}")


def _validate_package_source(package: dict[str, Any]) -> None:
    source = package.get("source")
    if source == {"virtual": "."}:
        if _normalize_name(package.get("name", "")) != "macroforge":
            raise AssertionError("only the local MacroForge project may use a virtual source")
        return
    if source != {"registry": PUBLIC_REGISTRY}:
        raise AssertionError(f"package uses an unapproved source: {source!r}")
    artifacts = [*([package["sdist"]] if "sdist" in package else []), *package.get("wheels", [])]
    if not artifacts:
        raise AssertionError(f"registry package lacks immutable distributions: {package.get('name')!r}")
    for artifact in artifacts:
        _validate_artifact(artifact)


def _dependency_resolves(dependency: dict[str, Any], packages: list[dict[str, Any]]) -> bool:
    for package in packages:
        if _normalize_name(package.get("name", "")) != _normalize_name(dependency["name"]):
            continue
        if "version" in dependency and package.get("version") != dependency["version"]:
            continue
        if "source" in dependency and package.get("source") != dependency["source"]:
            continue
        return True
    return False


def _validate_lock_governance(project: dict[str, Any], lock: dict[str, Any]) -> None:
    declared = _requirement_by_name(project["dependency-groups"]["test"])
    if declared != EXPECTED_REQUIREMENTS:
        raise AssertionError(
            f"test dependency group must equal the durable direct policy: {EXPECTED_REQUIREMENTS!r}"
        )
    packages = lock.get("package")
    if not isinstance(packages, list) or not packages:
        raise AssertionError("uv.lock must contain package records")

    seen_records: set[tuple[str, str, str]] = set()
    by_name: dict[str, list[dict[str, Any]]] = {}
    for package in packages:
        if not isinstance(package, dict):
            raise AssertionError(f"lock package must be a table: {package!r}")
        name = package.get("name")
        version = package.get("version")
        if not isinstance(name, str) or not NAME_PATTERN.fullmatch(name):
            raise AssertionError(f"invalid lock package name: {name!r}")
        if not isinstance(version, str) or not version.strip():
            raise AssertionError(f"invalid lock package version for {name!r}: {version!r}")
        normalized_name = _normalize_name(name)
        identity = (normalized_name, version, repr(package.get("source")))
        if identity in seen_records:
            raise AssertionError(f"duplicate lock package identity: {identity!r}")
        seen_records.add(identity)
        by_name.setdefault(normalized_name, []).append(package)
        _validate_package_source(package)
        for dependency in package.get("dependencies", []):
            _validate_dependency_entry(dependency)

    project_packages = by_name.get("macroforge", [])
    if len(project_packages) != 1:
        raise AssertionError("uv.lock must contain exactly one MacroForge project package")
    locked_project = project_packages[0]
    locked_direct = locked_project.get("dev-dependencies", {}).get("test")
    metadata_direct = locked_project.get("metadata", {}).get("requires-dev", {}).get("test")
    if not isinstance(locked_direct, list) or not isinstance(metadata_direct, list):
        raise AssertionError("project lock metadata must represent the test dependency group")

    locked_direct_entries = [_validate_dependency_entry(entry) for entry in locked_direct]
    metadata_entries = [_validate_dependency_entry(entry) for entry in metadata_direct]
    locked_names = {_normalize_name(entry["name"]) for entry in locked_direct_entries}
    metadata_specifiers: dict[str, object] = {}
    for entry in metadata_entries:
        name = _normalize_name(entry["name"])
        if name in metadata_specifiers:
            raise AssertionError(f"duplicate lock metadata direct dependency: {name}")
        metadata_specifiers[name] = entry.get("specifier")
    if locked_names != set(declared):
        raise AssertionError("locked project test dependencies differ from the declared test group")
    if metadata_specifiers != declared:
        raise AssertionError("locked project requirement metadata differs from pyproject.toml")

    for name, specifier in declared.items():
        candidates = by_name.get(name, [])
        if not candidates:
            raise AssertionError(f"declared direct dependency is absent from uv.lock: {name}")
        lower, upper = _supported_major_interval(specifier)
        for package in candidates:
            major = _version_major(package["version"])
            if not lower <= major < upper:
                raise AssertionError(
                    f"locked {name} version {package['version']} is outside {specifier}"
                )

    for package in packages:
        for dependency in package.get("dependencies", []):
            entry = _validate_dependency_entry(dependency)
            if not _dependency_resolves(entry, packages):
                raise AssertionError(
                    f"dangling lock dependency from {package['name']}: {entry!r}"
                )
    for dependency in locked_direct_entries:
        if not _dependency_resolves(dependency, packages):
            raise AssertionError(f"unresolved direct test dependency: {dependency!r}")


def _run_uv(project_root: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    uv = shutil.which("uv")
    if uv is None:
        raise AssertionError("uv is required for semantic lock validation")
    return subprocess.run(
        [uv, *arguments],
        cwd=project_root,
        check=False,
        capture_output=True,
        text=True,
        timeout=120,
    )


def _validate_dependency_governance(project_root: Path) -> None:
    project = _load_toml(project_root / "pyproject.toml")
    lock = _load_toml(project_root / "uv.lock")
    if lock.get("requires-python") != project["project"]["requires-python"]:
        raise AssertionError("uv.lock requires-python differs from pyproject.toml")
    _validate_lock_governance(project, lock)
    result = _run_uv(project_root, "lock", "--check")
    if result.returncode != 0:
        detail = (result.stderr or result.stdout).strip()
        raise AssertionError(f"uv rejected semantic lock validity: {detail}")


def _temporary_project() -> tempfile.TemporaryDirectory[str]:
    directory = tempfile.TemporaryDirectory(prefix="macroforge-dependency-governance-")
    root = Path(directory.name)
    shutil.copy2(PYPROJECT, root / "pyproject.toml")
    shutil.copy2(LOCKFILE, root / "uv.lock")
    return directory


def _replace_once(path: Path, pattern: str, replacement: str, *, flags: int = 0) -> None:
    text = path.read_text(encoding="utf-8")
    updated, count = re.subn(pattern, replacement, text, count=1, flags=flags)
    if count != 1:
        raise AssertionError(f"mutation pattern did not match exactly once: {pattern!r}")
    path.write_text(updated, encoding="utf-8")


class DependencyGovernanceTest(unittest.TestCase):
    def test_combined_gate_accepts_current_governed_lock(self) -> None:
        _validate_dependency_governance(PROJECT_ROOT)

    def test_bounded_test_group_is_declared_for_python_311(self) -> None:
        project = _load_toml(PYPROJECT)
        self.assertEqual(project["project"]["requires-python"], ">=3.11")
        self.assertEqual(
            _requirement_by_name(project["dependency-groups"]["test"]),
            EXPECTED_REQUIREMENTS,
        )

    def test_combined_gate_rejects_required_negative_mutations(self) -> None:
        mutations: list[tuple[str, Callable[[Path], None], str]] = [
            (
                "semantically invalid locked version",
                lambda root: _replace_once(
                    root / "uv.lock",
                    r'(\[\[package\]\]\nname = "pytest"\nversion = ")[^"]+(")',
                    r"\g<1>8.invalid\2",
                ),
                "uv rejected semantic lock validity",
            ),
            (
                "missing required direct dependency",
                lambda root: _replace_once(
                    root / "pyproject.toml", r'^\s*"PyYAML>=6,<7",\n', "", flags=re.MULTILINE
                ),
                "durable direct policy",
            ),
            (
                "unsupported direct dependency major",
                lambda root: _replace_once(
                    root / "uv.lock",
                    r'(\[\[package\]\]\nname = "pytest"\nversion = ")[^"]+(")',
                    r"\g<1>9.0.0\2",
                ),
                "outside >=8,<9",
            ),
            (
                "dangling dependency reference",
                lambda root: _replace_once(
                    root / "uv.lock",
                    r'(dependencies = \[\n\s*\{ name = ")[^"]+("[^\n]*\},)',
                    r"\g<1>requests\2",
                ),
                "dangling lock dependency",
            ),
            (
                "duplicate direct dependency declaration",
                lambda root: _replace_once(
                    root / "pyproject.toml",
                    r'(^\s*"pytest>=8,<9",\n)',
                    r'\1    "pytest>=9,<10",\n',
                    flags=re.MULTILINE,
                ),
                "duplicate direct dependency declaration",
            ),
            (
                "unexpected package source",
                lambda root: _replace_once(
                    root / "uv.lock",
                    re.escape(f'source = {{ registry = "{PUBLIC_REGISTRY}" }}'),
                    'source = { registry = "https://pypi.org/legacy" }',
                ),
                "unapproved source",
            ),
            (
                "malformed SHA-256 metadata",
                lambda root: _replace_once(
                    root / "uv.lock", r'hash = "sha256:[0-9a-f]{64}"', 'hash = "sha256:bad"'
                ),
                "lacks SHA-256 integrity metadata",
            ),
            (
                "missing SHA-256 metadata",
                lambda root: _replace_once(
                    root / "uv.lock", r', hash = "sha256:[0-9a-f]{64}"', ""
                ),
                "lacks SHA-256 integrity metadata",
            ),
        ]
        for label, mutate, expected_error in mutations:
            with self.subTest(label=label), _temporary_project() as directory:
                root = Path(directory)
                mutate(root)
                with self.assertRaisesRegex(AssertionError, expected_error):
                    _validate_dependency_governance(root)

    def test_uv_generated_historical_cutoff_resolution_is_compatible_evolution(self) -> None:
        with _temporary_project() as directory:
            root = Path(directory)
            original_lock = (root / "uv.lock").read_bytes()
            with (root / "pyproject.toml").open("a", encoding="utf-8") as handle:
                handle.write('\n[tool.uv]\nexclude-newer = "2025-01-01T00:00:00Z"\n')
            result = _run_uv(root, "lock", "--upgrade")
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            self.assertNotEqual((root / "uv.lock").read_bytes(), original_lock)
            _validate_dependency_governance(root)

    def test_authoritative_verification_docs_use_locked_commands(self) -> None:
        for path in AUTHORITATIVE_VERIFICATION_DOCS:
            text = path.read_text(encoding="utf-8")
            self.assertIn(CANONICAL_PROVISION, text, path)
            self.assertIn(CANONICAL_TEST_PREFIX, text, path)
            self.assertNotIn("uvx", text, path)

    def test_setup_and_runtime_guidance_do_not_install_unlocked_test_dependencies(self) -> None:
        install = (PROJECT_ROOT / "tools" / "install.sh").read_text(encoding="utf-8")
        self.assertIn(CANONICAL_PROVISION, install)
        self.assertIn("uv run --locked --group test python tools/check_coherence.py", install)
        self.assertNotIn("uv pip install", install)
        self.assertNotRegex(install, r"(?i)(pytest|pyyaml)\s*[><=]")
        self.assertNotIn(r"\\n'", install)

        for path in DEPENDENCY_GUIDANCE_TOOLS[1:]:
            text = path.read_text(encoding="utf-8")
            self.assertIn(CANONICAL_PROVISION, text, path)
            self.assertNotIn("uvx", text, path)
            self.assertNotIn("uv pip install", text, path)


if __name__ == "__main__":
    unittest.main()
