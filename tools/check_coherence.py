#!/usr/bin/env python3
"""ProjectForge coherence checker.

Supports root factory projects and generated projects. Root mode validates the
ProjectForge factory contract; generated mode validates the lighter project-local
contract produced by `tools/new_project.py`.
"""
from __future__ import annotations
import argparse, copy, hashlib, importlib.util, io, json, marshal, os, re, stat, subprocess, sys, types
from pathlib import Path, PurePosixPath
from typing import Any

TERMINAL_DISPOSITIONS = {
    'git-durable project truth',
    'local/provider evidence',
    'generated/rebuildable',
    'external archive',
    'pending decision',
}
PROVIDER_CONTENT_ORIGINS = {
    'provider-originated payload',
    'derived/normalized provider payload',
    'provider-originated',
    'provider-derived',
}
PERMITTED_RIGHTS_STATUS = 'permitted with evidence'
CANONICAL_PROVIDER_RIGHTS_STATUSES = {
    PERMITTED_RIGHTS_STATUS,
    'unknown/pending review',
    'unknown/pending review where provider redistribution has not been affirmatively classified',
}
GIT_DURABLE_DISPOSITION = 'git-durable project truth'
AUTHORSHIP_ORIGINS = {'authored', 'synthetic', 'synthetic fixture', 'not applicable'}

ROOT_REQUIRED = [
 'CONSTITUTION.md','projectforge.yaml','state/active_goal.md','state/project_state.md',
 'state/architecture.md','permissions/allowlist.yaml','permissions/denylist.yaml',
 'permissions/escalation_rules.yaml','context/context_policy.yaml','simulation/dry_run_policy.yaml',
 'recovery/escalation_policy.yaml','recovery/continuity_framework.md',
 'automation/orchestration_schedule.yaml','docs/OPERATOR_MANUAL.md','tools/architecture_reality_audit.py','tools/recover_session.py'
]

GENERATED_REQUIRED = [
 'CONSTITUTION.md','AGENTS.md','project.yaml','state/active_goal.md','state/project_state.md',
 'state/architecture.md','permissions/allowlist.yaml','permissions/denylist.yaml',
 'permissions/escalation_rules.yaml','context/context_policy.yaml','simulation/dry_run_policy.yaml',
 'recovery/escalation_policy.yaml','recovery/continuity_framework.md',
 'workspace_config.yaml','tools/check_coherence.py','tools/run.py','tools/architecture_reality_audit.py','tools/recover_session.py',
 'architecture/architecture_state.md','architecture/metaharvest/relevance_map.yaml',
 'architecture/metaharvest/adoption_candidates.md','architecture/metaharvest/rejected_candidates.md',
 'architecture/metaharvest/review_history.md'
]


def has_text(path: Path, needle: str) -> bool:
    return path.exists() and needle.lower() in path.read_text(encoding='utf-8', errors='replace').lower()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open('rb') as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def content_sensitive_file_fingerprints(
    paths: list[str | Path],
    *,
    base_dir: str | Path | None = None,
) -> dict[str, dict[str, str | int | None]]:
    """Return deterministic fingerprints for an explicit bounded path set.

    CLI callers resolve relative paths against the selected project rather than
    the shell's current working directory. The function does not discover or
    print file contents and deliberately does not follow symlinks.
    """
    base = Path(base_dir).resolve() if base_dir is not None else None
    result: dict[str, dict[str, str | int | None]] = {}
    for raw_path in paths:
        requested = Path(raw_path)
        path = requested if requested.is_absolute() or base is None else base / requested
        scope = 'absolute' if requested.is_absolute() else ('project-relative' if base is not None else 'cwd-relative')
        if path.is_file() and not path.is_symlink():
            result[str(requested)] = {
                'sha256': sha256_file(path),
                'size': path.stat().st_size,
                'scope': scope,
                'resolved_path': str(path.resolve()),
            }
        else:
            result[str(requested)] = {
                'sha256': None,
                'size': None,
                'scope': scope,
                'resolved_path': str(path.resolve(strict=False)),
            }
    return result


IGNORED_ARTIFACT_POLICY_SCHEMA = 'macroforge-ignored-artifact-policy-v1'
IGNORED_ARTIFACT_SNAPSHOT_SCHEMA = 'macroforge-non-git-artifact-preservation-v1'
KNOWN_DISPOSABLE_CLASSES = {'pytest-cache', 'python-bytecode'}
PROTECTED_DECLARATION_FIELDS = {
    'path', 'classification', 'governing_reason', 'owner',
    'producing_mechanism', 'lifecycle_semantics', 'content_origin',
    'publication_expectation',
}
PROTECTED_OPTIONAL_FIELDS = {'rights_status', 'allow_binary', 'allow_executable'}
POLICY_FIELDS = {'schema', 'protected_artifacts', 'disposable_classes'}
ALLOWED_PROTECTED_ORIGINS = AUTHORSHIP_ORIGINS | PROVIDER_CONTENT_ORIGINS
MAX_DISPOSABLE_PYC_BYTES = 16 * 1024 * 1024
PYTEST_CACHE_MARKER_SIGNATURE = b'Signature: 8a477f597d28d172789f06886806bc55\n'
# CACHEDIR.TAG is inspected only for the standardized 47-byte signature line.
# The 512-byte cap preserves room for the format's optional explanatory header
# while preventing a cache marker from becoming an unbounded memory input.
MAX_PYTEST_CACHE_MARKER_BYTES = 512
IGNORED_ARTIFACT_LIFECYCLE_PROFILE = 'macroforge-ignored-artifact-governance-lifecycle-v3'
IGNORED_ARTIFACT_GOVERNANCE_CANONICAL_PATHS = (
    'artifacts/reports/R-20260801-ignored-artifact-preservation-governance-closeout.json',
    'artifacts/reports/_SUMMARY.md',
    'artifacts/tasks/TASK-PF-20260801-ignored-artifact-preservation-governance.md',
    'artifacts/tasks/_SUMMARY.md',
    'context/_SUMMARY.md',
    'context/latest_handoff.md',
    'recovery/_SUMMARY.md',
    'recovery/continuity_framework.md',
    'state/_SUMMARY.md',
    'state/active_goal.md',
    'state/project_state.md',
    'tests/_SUMMARY.md',
    'tests/test_ignored_artifact_preservation.py',
    'tools/_SUMMARY.md',
    'tools/check_coherence.py',
)
PUBLICATION_REPOSITORY_CONDITIONS = {
    'working-tree-candidate',
    'local-commit-ahead-of-authoritative-remote',
    'verified-authoritative-remote-equality',
}
PUBLICATION_REVIEW_EVIDENCE_FIELDS = {
    'schema', 'verdict', 'authenticated', 'byte_recoverable',
    'candidate_identity_match', 'ambiguous',
}


def evaluate_publication_transition(
    repository_condition: str,
    review_evidence: Any = None,
) -> dict[str, Any]:
    """Fail-closed evaluation of the lifecycle publication fixed point.

    The caller must derive ``repository_condition`` and evidence authentication
    from independent Git and external-session observations. This evaluator owns
    only the closed transition semantics; it never treats caller agreement or a
    local commit as proof of remote publication.
    """
    result: dict[str, Any] = {
        'status': 'fail',
        'repository_condition': repository_condition,
        'required_transition': 'independent-review-required',
        'publication_permitted': False,
        'workstream_closed': False,
        'successor_activated': False,
        'errors': [],
    }
    if repository_condition not in PUBLICATION_REPOSITORY_CONDITIONS:
        result['errors'].append('repository_condition is not an enumerated authenticated state')
        return result

    if review_evidence is None:
        if repository_condition == 'working-tree-candidate':
            result['status'] = 'pass'
            return result
        result['errors'].append('post-review repository state requires exact authenticated PASS evidence')
        return result

    if not isinstance(review_evidence, dict):
        result['errors'].append('review_evidence must be an object or null')
        return result
    missing = sorted(PUBLICATION_REVIEW_EVIDENCE_FIELDS - set(review_evidence))
    unknown = sorted(set(review_evidence) - PUBLICATION_REVIEW_EVIDENCE_FIELDS)
    if missing:
        result['errors'].append(f'review_evidence missing required fields: {missing}')
    if unknown:
        result['errors'].append(f'review_evidence has unknown claim-bearing fields: {unknown}')
    if missing or unknown:
        return result
    if review_evidence.get('schema') != 'macroforge-external-publication-review-v1':
        result['errors'].append('review_evidence.schema is not recognized')
    if review_evidence.get('verdict') not in {'PASS', 'BLOCK'}:
        result['errors'].append("review_evidence.verdict must be 'PASS' or 'BLOCK'")
    for field in ('authenticated', 'byte_recoverable', 'candidate_identity_match', 'ambiguous'):
        if not isinstance(review_evidence.get(field), bool):
            result['errors'].append(f'review_evidence.{field} must be boolean')
    if result['errors']:
        return result
    if review_evidence['authenticated'] is not True:
        result['errors'].append('review evidence is not authenticated')
    if review_evidence['byte_recoverable'] is not True:
        result['errors'].append('review evidence is not byte-recoverable')
    if review_evidence['ambiguous'] is not False:
        result['errors'].append('review evidence is ambiguous')
    if review_evidence['candidate_identity_match'] is not True:
        result['errors'].append('review evidence does not bind to the exact candidate')
    if result['errors']:
        return result

    if review_evidence['verdict'] == 'BLOCK':
        result['required_transition'] = 'correction-required'
        if repository_condition == 'working-tree-candidate':
            result['status'] = 'pass'
        else:
            result['errors'].append('a blocked candidate cannot advance to commit or remote publication')
        return result

    result['status'] = 'pass'
    if repository_condition == 'working-tree-candidate':
        result['required_transition'] = 'bounded-publication-permitted'
        result['publication_permitted'] = True
    elif repository_condition == 'local-commit-ahead-of-authoritative-remote':
        result['required_transition'] = 'push-and-verify-remote'
    else:
        result['required_transition'] = 'workstream-closed'
        result['workstream_closed'] = True
    return result


def _canonical_json_sha256(value: Any) -> str:
    payload = json.dumps(value, allow_nan=False, ensure_ascii=True, separators=(',', ':'), sort_keys=True).encode('ascii')
    return hashlib.sha256(payload).hexdigest()


def _path_sort_key(path: str) -> bytes:
    return os.fsencode(path)


def _safe_project_relative_path(raw: Any) -> tuple[str | None, str | None]:
    if not isinstance(raw, str) or not raw or '\x00' in raw:
        return None, 'path must be a non-empty NUL-free string'
    path = PurePosixPath(raw)
    if path.is_absolute() or any(part in {'', '.', '..'} for part in path.parts):
        return None, 'path must be a normalized project-relative path without dot segments'
    if '.git' in path.parts:
        return None, 'path must not address Git administrative state'
    normalized = path.as_posix()
    if normalized != raw:
        return None, 'path must use canonical POSIX project-relative spelling'
    return normalized, None


def _git_mode(st_mode: int) -> str:
    if not stat.S_ISREG(st_mode):
        raise ValueError('only regular-file modes are supported')
    if st_mode & (stat.S_ISUID | stat.S_ISGID | stat.S_ISVTX):
        raise ValueError('setuid, setgid, and sticky modes are unsupported')
    return '100755' if stat.S_IMODE(st_mode) & 0o111 else '100644'


def _open_beneath_no_symlink(root: Path, path: str, final_flags: int) -> int:
    """Open a repository-relative path without following any path-component symlink."""
    parts = PurePosixPath(path).parts
    if not parts:
        raise ValueError('empty path')
    directory_fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY)
    try:
        for part in parts[:-1]:
            next_fd = os.open(
                part,
                os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                dir_fd=directory_fd,
            )
            os.close(directory_fd)
            directory_fd = next_fd
        return os.open(parts[-1], final_flags | os.O_NOFOLLOW, dir_fd=directory_fd)
    finally:
        os.close(directory_fd)


def _lstat_without_symlink_components(root: Path, path: str) -> os.stat_result:
    flags = getattr(os, 'O_PATH', os.O_RDONLY)
    fd = _open_beneath_no_symlink(root, path, flags)
    try:
        st = os.fstat(fd)
        if stat.S_ISLNK(st.st_mode):
            raise ValueError(f'{path}: symlink path components are not allowed')
        return st
    finally:
        os.close(fd)


def _open_verified_regular_file_no_follow(root: Path, path: str) -> tuple[int, os.stat_result]:
    """Pin and validate a regular inode before opening it for ordinary reads.

    Linux ``O_PATH`` cannot block on FIFOs or activate devices. Reopening the
    pinned inode through ``/proc/self/fd`` avoids a second pathname lookup, so a
    replacement after inspection cannot redirect the read to another object.
    """
    if not hasattr(os, 'O_PATH'):
        raise OSError('safe regular-file inspection requires Linux O_PATH')
    metadata_fd = _open_beneath_no_symlink(root, path, os.O_PATH | os.O_CLOEXEC)
    try:
        metadata_st = os.fstat(metadata_fd)
        if stat.S_ISLNK(metadata_st.st_mode):
            raise ValueError(f'{path}: symlink path components are not allowed')
        if not stat.S_ISREG(metadata_st.st_mode):
            raise ValueError(f'{path}: expected a regular file')
        _git_mode(metadata_st.st_mode)
        proc_path = f'/proc/self/fd/{metadata_fd}'
        descriptor = os.open(proc_path, os.O_RDONLY | os.O_CLOEXEC)
        try:
            opened_st = os.fstat(descriptor)
            pinned_identity = (metadata_st.st_dev, metadata_st.st_ino, metadata_st.st_mode)
            opened_identity = (opened_st.st_dev, opened_st.st_ino, opened_st.st_mode)
            if opened_identity != pinned_identity:
                raise ValueError(f'{path}: regular file identity or mode changed before reading')
            _git_mode(opened_st.st_mode)
            return descriptor, opened_st
        except BaseException:
            os.close(descriptor)
            raise
    finally:
        os.close(metadata_fd)


def _read_regular_file_no_follow(
    root: Path,
    path: str,
    *,
    max_bytes: int | None = None,
) -> tuple[bytes, os.stat_result]:
    descriptor, st = _open_verified_regular_file_no_follow(root, path)
    try:
        if max_bytes is not None and st.st_size > max_bytes:
            raise ValueError(f'{path}: regular file exceeds the accepted {max_bytes}-byte limit')
        with os.fdopen(descriptor, 'rb', closefd=False) as handle:
            data = handle.read() if max_bytes is None else handle.read(max_bytes + 1)
        if max_bytes is not None and len(data) > max_bytes:
            raise ValueError(f'{path}: regular file exceeds the accepted {max_bytes}-byte limit')
        final_st = os.fstat(descriptor)
        if (final_st.st_dev, final_st.st_ino, final_st.st_mode) != (st.st_dev, st.st_ino, st.st_mode):
            raise ValueError(f'{path}: regular file identity or mode changed while reading')
        return data, final_st
    finally:
        os.close(descriptor)


def _hash_regular_file_no_follow(root: Path, path: str) -> tuple[str, int, bool, os.stat_result]:
    descriptor, st = _open_verified_regular_file_no_follow(root, path)
    digest = hashlib.sha256()
    size = 0
    binary = False
    try:
        with os.fdopen(descriptor, 'rb', closefd=False) as handle:
            for chunk in iter(lambda: handle.read(1024 * 1024), b''):
                digest.update(chunk)
                size += len(chunk)
                binary = binary or b'\x00' in chunk
        final_st = os.fstat(descriptor)
        if (final_st.st_dev, final_st.st_ino, final_st.st_mode) != (st.st_dev, st.st_ino, st.st_mode):
            raise ValueError(f'{path}: regular file identity or mode changed while hashing')
        return digest.hexdigest(), size, binary, final_st
    finally:
        os.close(descriptor)


def _parse_nul_path_list(raw: bytes, label: str) -> tuple[list[str], list[str]]:
    """Parse a complete Git `-z` path list without newline or quoting assumptions."""
    errors: list[str] = []
    if raw and not raw.endswith(b'\x00'):
        return [], [f'{label}: NUL-delimited path list is unterminated']
    fields = raw[:-1].split(b'\x00') if raw else []
    paths: list[str] = []
    for field in fields:
        if not field:
            errors.append(f'{label}: empty path record is invalid')
            continue
        path = os.fsdecode(field)
        normalized, error = _safe_project_relative_path(path)
        if error:
            errors.append(f'{path!r}: unsafe {label} path: {error}')
        elif normalized is not None:
            paths.append(normalized)
    if len(set(paths)) != len(paths):
        errors.append(f'{label}: duplicate path records are invalid')
    ordered = sorted(set(paths), key=_path_sort_key)
    if len(paths) == len(set(paths)) and paths != ordered:
        errors.append(f'{label}: path records must use ascending os.fsencode(path) order')
    return ordered, errors


def _pytest_cache_root(path: str) -> str | None:
    parts = PurePosixPath(path).parts
    for index, part in enumerate(parts):
        if part == '.pytest_cache':
            return PurePosixPath(*parts[: index + 1]).as_posix()
    return None


def _recognized_disposable_class(root: Path, path: str, enabled: set[str]) -> str | None:
    """Classify only structurally valid, narrowly owned cache artifacts."""
    parts = PurePosixPath(path).parts
    if 'pytest-cache' in enabled:
        cache_root = _pytest_cache_root(path)
        if cache_root is not None:
            root_parts = PurePosixPath(cache_root).parts
            relative = PurePosixPath(*parts[len(root_parts):]).as_posix()
            allowed_members = {
                'CACHEDIR.TAG', '.gitignore', 'README.md',
                'v/cache/nodeids', 'v/cache/lastfailed', 'v/cache/stepwise',
                'v/cache/durations', 'v/cache/durations_n',
            }
            if relative in allowed_members:
                marker_path = f'{cache_root}/CACHEDIR.TAG'
                try:
                    marker, _ = _read_regular_file_no_follow(
                        root, marker_path, max_bytes=MAX_PYTEST_CACHE_MARKER_BYTES
                    )
                    _lstat_without_symlink_components(root, path)
                    if marker.startswith(PYTEST_CACHE_MARKER_SIGNATURE):
                        return 'pytest-cache'
                except (FileNotFoundError, OSError, ValueError):
                    return None
    if 'python-bytecode' in enabled and '__pycache__' in parts:
        filename = parts[-1]
        cache_tag = re.escape(sys.implementation.cache_tag or '')
        if re.fullmatch(rf'.+\.{cache_tag}(?:\.opt-[0-9]+)?\.pyc', filename):
            try:
                data, pyc_st = _read_regular_file_no_follow(
                    root, path, max_bytes=MAX_DISPOSABLE_PYC_BYTES
                )
                if _git_mode(pyc_st.st_mode) != '100644':
                    return None
                if len(data) < 16 or data[:4] != importlib.util.MAGIC_NUMBER:
                    return None
                flags = int.from_bytes(data[4:8], 'little')
                if flags & ~0b11 or flags == 0b10:
                    return None
                payload = io.BytesIO(data[16:])
                code = marshal.load(payload)
                if isinstance(code, types.CodeType) and payload.tell() == len(data) - 16:
                    return 'python-bytecode'
            except (EOFError, FileNotFoundError, MemoryError, OSError, OverflowError, TypeError, ValueError):
                return None
    return None


def _bounded_membership_summary(paths: list[str]) -> dict[str, Any]:
    ordered = sorted(paths, key=_path_sort_key)
    encoded = [os.fsencode(path) for path in ordered]
    payload = b'\x00'.join(encoded) + (b'\x00' if encoded else b'')
    return {
        'count': len(ordered),
        'membership_sha256': hashlib.sha256(payload).hexdigest(),
        'sample_paths': ordered[:20],
        'sample_truncated': len(ordered) > 20,
    }


def capture_non_git_artifact_preservation(
    project_root: str | Path,
    policy: dict[str, Any],
    *,
    authored_candidate_paths: list[str] | tuple[str, ...] | set[str] = (),
    ignored_paths_z: bytes | None = None,
    untracked_paths_z: bytes | None = None,
) -> dict[str, Any]:
    """Capture one deterministic non-Git preservation snapshot.

    Protected artifacts are exact-content evidence. Recognized disposable caches
    contribute only class membership summaries and never content hashes. Authored
    publication candidates remain a separate scope. Repository discovery uses
    complete NUL-delimited Git path lists and does not follow symlinks.
    """
    root = Path(project_root).resolve()
    errors: list[str] = []
    if not isinstance(policy, dict):
        errors.append('policy must be an object')
        policy = {}
    unknown_policy_fields = sorted(set(policy) - POLICY_FIELDS)
    if unknown_policy_fields:
        errors.append(f'unknown policy fields: {unknown_policy_fields}')
    if policy.get('schema') != IGNORED_ARTIFACT_POLICY_SCHEMA:
        errors.append(f'policy schema must be {IGNORED_ARTIFACT_POLICY_SCHEMA!r}')
    raw_classes = policy.get('disposable_classes', [])
    if not isinstance(raw_classes, list) or not all(isinstance(item, str) and item for item in raw_classes):
        errors.append('disposable_classes must be a list of non-empty class names')
        raw_classes = []
    if len(raw_classes) != len(set(raw_classes)):
        errors.append('disposable_classes must not contain duplicates')
    enabled_classes = set(raw_classes)
    unknown_classes = sorted(enabled_classes - KNOWN_DISPOSABLE_CLASSES)
    if unknown_classes:
        errors.append(f'unknown disposable classes: {unknown_classes}')
    declarations = policy.get('protected_artifacts', [])
    if not isinstance(declarations, list):
        errors.append('protected_artifacts must be a list')
        declarations = []

    candidate_set: set[str] = set()
    for raw in authored_candidate_paths:
        normalized, error = _safe_project_relative_path(raw)
        if error:
            errors.append(f'{raw!r}: unsafe authored candidate path: {error}')
        elif normalized is not None:
            if normalized in candidate_set:
                errors.append(f'duplicate authored candidate path: {normalized}')
            candidate_set.add(normalized)

    protected_by_path: dict[str, dict[str, Any]] = {}
    for index, declaration in enumerate(declarations):
        if not isinstance(declaration, dict):
            errors.append(f'protected_artifacts[{index}] must be an object')
            continue
        unknown_fields = sorted(set(declaration) - PROTECTED_DECLARATION_FIELDS - PROTECTED_OPTIONAL_FIELDS)
        if unknown_fields:
            errors.append(f'protected_artifacts[{index}] has unknown fields: {unknown_fields}')
            continue
        missing_fields = sorted(
            field for field in PROTECTED_DECLARATION_FIELDS
            if not isinstance(declaration.get(field), str) or not declaration.get(field)
        )
        if missing_fields:
            errors.append(f'protected_artifacts[{index}] requires non-empty string fields: {missing_fields}')
            continue
        invalid_boolean = False
        for boolean_field in ('allow_binary', 'allow_executable'):
            if boolean_field in declaration and not isinstance(declaration[boolean_field], bool):
                errors.append(f'protected_artifacts[{index}].{boolean_field} must be a boolean')
                invalid_boolean = True
        if invalid_boolean:
            continue
        normalized, error = _safe_project_relative_path(declaration.get('path'))
        if error:
            errors.append(f'protected_artifacts[{index}]: {error}')
            continue
        assert normalized is not None
        if normalized in protected_by_path:
            errors.append(f'duplicate protected artifact declaration: {normalized}')
            continue
        if normalized in candidate_set:
            errors.append(f'{normalized}: path cannot be both protected non-Git evidence and an authored candidate')
            continue
        origin = declaration.get('content_origin')
        if origin not in ALLOWED_PROTECTED_ORIGINS:
            errors.append(f'{normalized}: unknown content_origin {origin!r}')
            continue
        if declaration.get('publication_expectation') != 'local-only':
            errors.append(f'{normalized}: protected non-Git evidence must have publication_expectation="local-only"')
            continue
        rights_status = declaration.get('rights_status')
        valid_rights_status = (
            isinstance(rights_status, str)
            and rights_status in CANONICAL_PROVIDER_RIGHTS_STATUSES
        )
        if rights_status is not None and not valid_rights_status:
            errors.append(
                f'{normalized}: rights_status must use an existing canonical classification; '
                f'got {rights_status!r}'
            )
            continue
        if origin in PROVIDER_CONTENT_ORIGINS and not valid_rights_status:
            errors.append(f'{normalized}: provider evidence requires a canonical rights_status')
            continue
        protected_by_path[normalized] = dict(declaration, path=normalized)

    normalized_policy = {
        'schema': IGNORED_ARTIFACT_POLICY_SCHEMA,
        'protected_artifacts': [protected_by_path[path] for path in sorted(protected_by_path, key=_path_sort_key)],
        'disposable_classes': sorted(enabled_classes & KNOWN_DISPOSABLE_CLASSES),
    }
    policy_sha256 = _canonical_json_sha256(normalized_policy)

    ignored_supplied = ignored_paths_z is not None
    untracked_supplied = untracked_paths_z is not None
    caller_supplied_any = ignored_supplied or untracked_supplied
    caller_supplied_both = ignored_supplied and untracked_supplied
    observation_provenance = 'independent-git-discovery'
    observation_transport = 'git-ls-files-z'
    if caller_supplied_any:
        observation_provenance = 'caller-supplied-unverified'
        observation_transport = 'caller-supplied-nul-path-lists'
        if not caller_supplied_both:
            errors.append('ignored_paths_z and untracked_paths_z must be supplied together')
        # Defaults exist only so malformed partial input can produce bounded diagnostics;
        # explicit suppliedness, never byte equality with these defaults, owns verification.
        ignored_paths_z = ignored_paths_z if ignored_supplied else b''
        untracked_paths_z = untracked_paths_z if untracked_supplied else b''

    commands = {
        'untracked': ['git', 'ls-files', '--others', '--exclude-standard', '-z'],
        'ignored': ['git', 'ls-files', '--others', '--ignored', '--exclude-standard', '-z'],
    }
    discovered_outputs: dict[str, bytes] = {}
    discovery_complete = True
    for label, command in commands.items():
        try:
            completed = subprocess.run(
                command, cwd=root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False
            )
        except OSError as exc:
            errors.append(f'Git {label} discovery failed: {exc}')
            discovery_complete = False
            discovered_outputs[label] = b''
            continue
        if completed.returncode:
            errors.append(f'Git {label} discovery failed with exit {completed.returncode}')
            discovery_complete = False
            discovered_outputs[label] = b''
        else:
            discovered_outputs[label] = completed.stdout

    if not caller_supplied_any:
        untracked_paths_z = discovered_outputs['untracked']
        ignored_paths_z = discovered_outputs['ignored']
    assert ignored_paths_z is not None and untracked_paths_z is not None
    ignored_paths, ignored_errors = _parse_nul_path_list(ignored_paths_z, 'ignored')
    untracked_paths, untracked_errors = _parse_nul_path_list(untracked_paths_z, 'untracked')
    errors.extend(ignored_errors)
    errors.extend(untracked_errors)

    observation_complete = (
        discovery_complete
        and not ignored_errors
        and not untracked_errors
        and (not caller_supplied_any or caller_supplied_both)
    )
    if caller_supplied_both:
        if discovery_complete and (
            ignored_paths_z != discovered_outputs['ignored']
            or untracked_paths_z != discovered_outputs['untracked']
        ):
            errors.append('caller-supplied observations do not exactly match independent Git discovery')
            observation_complete = False
        elif observation_complete:
            observation_provenance = 'caller-supplied-verified-against-independent-git-discovery'

    overlap = sorted(set(ignored_paths) & set(untracked_paths), key=_path_sort_key)
    if overlap:
        errors.append(f'Git discovery classified paths as both ignored and untracked: {overlap}')
        observation_complete = False
    observed = {path: 'ignored' for path in ignored_paths}
    observed.update({path: 'untracked' for path in untracked_paths})

    candidate_scope: dict[str, str] = {}
    unsafe_observed: list[str] = []
    for path in sorted(candidate_set, key=_path_sort_key):
        try:
            candidate_st = _lstat_without_symlink_components(root, path)
            _git_mode(candidate_st.st_mode)
        except (FileNotFoundError, OSError, ValueError):
            unsafe_observed.append(path)
            errors.append(f'{path}: authored candidate is missing, unsafe, or not a supported regular file')
            continue
        if path in observed:
            candidate_scope[path] = observed[path]
            continue
        try:
            tracked = subprocess.run(
                ['git', 'ls-files', '--error-unmatch', '--', path],
                cwd=root,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                check=False,
            )
        except OSError as exc:
            errors.append(f'{path}: Git tracked-candidate check failed: {exc}')
            continue
        if tracked.returncode == 0:
            candidate_scope[path] = 'tracked'
        else:
            errors.append(
                f'{path}: authored candidate is excluded from the applicable tracked, ignored, and untracked population'
            )

    protected_records: list[dict[str, Any]] = []
    missing_protected: list[str] = []
    for path in sorted(protected_by_path, key=_path_sort_key):
        declaration = protected_by_path[path]
        if path not in observed:
            missing_protected.append(path)
            errors.append(f'{path}: declared protected artifact is missing or not observed as ignored/untracked')
            continue
        try:
            sha256, size, binary, st = _hash_regular_file_no_follow(root, path)
            mode = _git_mode(st.st_mode)
        except (FileNotFoundError, OSError, ValueError):
            missing_protected.append(path)
            unsafe_observed.append(path)
            errors.append(f'{path}: protected artifact is unavailable, unsafe, or not a regular file')
            continue
        if stat.S_IMODE(st.st_mode) & 0o111 and declaration.get('allow_executable') is not True:
            unsafe_observed.append(path)
            errors.append(f'{path}: executable protected artifact requires allow_executable=true')
            continue
        if binary and declaration.get('allow_binary') is not True:
            unsafe_observed.append(path)
            errors.append(f'{path}: binary protected artifact requires allow_binary=true')
            continue
        record = {
            'path': path,
            'observed_status': observed[path],
            'classification': declaration['classification'],
            'governing_reason': declaration['governing_reason'],
            'owner': declaration['owner'],
            'producing_mechanism': declaration['producing_mechanism'],
            'lifecycle_semantics': declaration['lifecycle_semantics'],
            'content_origin': declaration['content_origin'],
            'publication_expectation': declaration['publication_expectation'],
            'mode': mode,
            'size': size,
            'sha256': sha256,
            'binary': binary,
        }
        if declaration.get('rights_status'):
            record['rights_status'] = declaration['rights_status']
        protected_records.append(record)

    disposable_paths: dict[str, list[str]] = {name: [] for name in sorted(enabled_classes & KNOWN_DISPOSABLE_CLASSES)}
    authored_observed = sorted(candidate_scope, key=_path_sort_key)
    disguised: list[str] = []
    unclassified_ignored: list[str] = []
    unclassified_untracked: list[str] = []
    for path in sorted(observed, key=_path_sort_key):
        if path in protected_by_path:
            continue
        disposable_class = _recognized_disposable_class(root, path, enabled_classes)
        if path in candidate_set:
            if disposable_class is not None:
                disguised.append(path)
                errors.append(f'{path}: authored candidate cannot be classified as disposable cache material')
            continue
        if observed[path] == 'ignored' and disposable_class is not None:
            try:
                st = _lstat_without_symlink_components(root, path)
                mode = _git_mode(st.st_mode)
            except (FileNotFoundError, OSError, ValueError):
                unsafe_observed.append(path)
                errors.append(f'{path}: disposable cache member is unavailable or unsafe')
                continue
            if mode != '100644':
                unsafe_observed.append(path)
                errors.append(f'{path}: disposable cache member has unsafe type or mode')
                continue
            disposable_paths[disposable_class].append(path)
        elif observed[path] == 'ignored':
            unclassified_ignored.append(path)
            errors.append(f'{path}: ignored artifact is neither protected nor recognized disposable residue')
        else:
            unclassified_untracked.append(path)
            errors.append(f'{path}: untracked artifact is neither protected nor an authored candidate')

    protected_records.sort(key=lambda item: _path_sort_key(str(item['path'])))
    protected_identity_payload = {
        'schema': IGNORED_ARTIFACT_SNAPSHOT_SCHEMA,
        'policy_sha256': policy_sha256,
        'protected_artifacts': protected_records,
    }
    disposable_summary = {
        name: _bounded_membership_summary(paths)
        for name, paths in sorted(disposable_paths.items())
    }
    snapshot = {
        'schema': IGNORED_ARTIFACT_SNAPSHOT_SCHEMA,
        'status': 'fail' if errors else 'pass',
        'policy_sha256': policy_sha256,
        'protected_identity': _canonical_json_sha256(protected_identity_payload),
        'protected_artifacts': protected_records,
        'disposable_classes': disposable_summary,
        'publication_scope': sorted(candidate_set, key=_path_sort_key),
        'working_tree_scope': {
            'observed_non_git_count': len(observed),
            'authored_candidate_count': len(authored_observed),
            'protected_count': len(protected_records),
            'disposable_count': sum(summary['count'] for summary in disposable_summary.values()),
        },
        'observation': {
            'transport': observation_transport,
            'provenance': observation_provenance,
            'independent_git_discovery_completed': discovery_complete,
            'caller_supplied_observations': caller_supplied_any,
            'ignored_enumeration_complete': observation_complete,
            'path_selection': 'independent canonical Git ignored/untracked discovery; caller-supplied lists are complete only after exact independent agreement',
        },
        'canonicalization': {
            'ordering': 'ascending os.fsencode(path) bytes',
            'protected_identity': 'SHA-256 of ASCII canonical JSON (sorted keys, compact separators, ensure_ascii) containing schema, normalized policy SHA-256, and protected records',
            'evidence_identity': 'SHA-256 of the complete snapshot except the evidence_identity field itself',
            'disposable_membership': 'SHA-256 of sorted os.fsencode(path) values joined and terminated by NUL; cache bytes are not hashed',
            'timestamps_in_identity': False,
        },
        'diagnostics': {
            'missing_protected_artifacts': sorted(set(missing_protected), key=_path_sort_key),
            'changed_protected_artifacts': [],
            'new_unclassified_ignored_artifacts': sorted(unclassified_ignored, key=_path_sort_key),
            'new_unclassified_untracked_artifacts': sorted(unclassified_untracked, key=_path_sort_key),
            'authored_candidates_disguised_as_disposable': sorted(disguised, key=_path_sort_key),
            'unsafe_paths_types_or_modes': sorted(set(unsafe_observed), key=_path_sort_key),
            'accepted_disposable_cache_churn': disposable_summary,
        },
        'errors': errors,
    }
    snapshot['evidence_identity'] = _snapshot_evidence_identity(snapshot)
    return snapshot


def _snapshot_evidence_identity(snapshot: dict[str, Any]) -> str:
    evidence = copy.deepcopy(snapshot)
    evidence.pop('evidence_identity', None)
    return _canonical_json_sha256(evidence)


def qualify_historical_non_git_snapshot(snapshot: dict[str, Any], qualification: str) -> dict[str, Any]:
    """Create an integrity-bound, explicitly incomplete historical snapshot."""
    if not isinstance(qualification, str) or not qualification:
        raise ValueError('historical qualification must be a non-empty string')
    qualified = copy.deepcopy(snapshot)
    observation = qualified.get('observation')
    if not isinstance(observation, dict):
        raise ValueError('snapshot observation must be an object')
    observation['ignored_enumeration_complete'] = False
    observation['qualification'] = qualification
    qualified['evidence_identity'] = _snapshot_evidence_identity(qualified)
    return qualified


def _snapshot_validation_errors(snapshot: Any, label: str) -> list[str]:
    errors: list[str] = []
    if not isinstance(snapshot, dict):
        return [f'{label} snapshot must be an object']
    required = {
        'schema', 'status', 'policy_sha256', 'protected_identity',
        'protected_artifacts', 'disposable_classes', 'publication_scope',
        'working_tree_scope', 'observation', 'canonicalization', 'diagnostics',
        'errors', 'evidence_identity',
    }
    missing = sorted(required - set(snapshot))
    unknown = sorted(set(snapshot) - required)
    if missing:
        errors.append(f'{label} snapshot missing fields: {missing}')
    if unknown:
        errors.append(f'{label} snapshot has unknown fields: {unknown}')
    if snapshot.get('schema') != IGNORED_ARTIFACT_SNAPSHOT_SCHEMA:
        errors.append(f'{label} snapshot schema is unsupported')
    if snapshot.get('status') != 'pass':
        errors.append(f'{label} snapshot status must be pass')
    for field in ('policy_sha256', 'protected_identity', 'evidence_identity'):
        value = snapshot.get(field)
        if not isinstance(value, str) or re.fullmatch(r'[0-9a-f]{64}', value) is None:
            errors.append(f'{label} {field} must be a lowercase SHA-256')

    record_required = PROTECTED_DECLARATION_FIELDS | {
        'observed_status', 'mode', 'size', 'sha256', 'binary',
    }
    record_allowed = record_required | {'rights_status'}
    records = snapshot.get('protected_artifacts')
    if not isinstance(records, list) or not all(isinstance(item, dict) for item in records):
        errors.append(f'{label} protected_artifacts must be a list of objects')
        records = []
    paths: list[str] = []
    for index, item in enumerate(records):
        item_missing = sorted(record_required - set(item))
        item_unknown = sorted(set(item) - record_allowed)
        if item_missing or item_unknown:
            errors.append(f'{label} protected record {index} has missing={item_missing} unknown={item_unknown}')
            continue
        path = item.get('path')
        normalized, path_error = _safe_project_relative_path(path) if isinstance(path, str) else (None, 'not a string')
        if path_error or normalized != path:
            errors.append(f'{label} protected record {index} has an unsafe path')
        else:
            paths.append(path)
        for field in PROTECTED_DECLARATION_FIELDS - {'path'}:
            if not isinstance(item.get(field), str) or not item[field]:
                errors.append(f'{label} protected record {index} field {field} must be a non-empty string')
        if item.get('observed_status') not in {'ignored', 'untracked'}:
            errors.append(f'{label} protected record {index} observed_status is invalid')
        if item.get('mode') not in {'100644', '100755'}:
            errors.append(f'{label} protected record {index} mode is invalid or unsupported')
        if type(item.get('size')) is not int or item['size'] < 0:
            errors.append(f'{label} protected record {index} size is invalid')
        if not isinstance(item.get('sha256'), str) or re.fullmatch(r'[0-9a-f]{64}', item['sha256']) is None:
            errors.append(f'{label} protected record {index} sha256 is invalid')
        if type(item.get('binary')) is not bool:
            errors.append(f'{label} protected record {index} binary must be a boolean')
        rights_status = item.get('rights_status')
        if 'rights_status' in item and (
            not isinstance(rights_status, str)
            or rights_status not in CANONICAL_PROVIDER_RIGHTS_STATUSES
        ):
            errors.append(f'{label} protected record {index} rights_status is invalid')
        if item.get('content_origin') in PROVIDER_CONTENT_ORIGINS and rights_status not in CANONICAL_PROVIDER_RIGHTS_STATUSES:
            errors.append(f'{label} protected record {index} provider evidence requires a canonical rights_status')
    if len(paths) != len(records) or len(paths) != len(set(paths)) or paths != sorted(paths, key=_path_sort_key):
        errors.append(f'{label} protected_artifacts must have unique canonically ordered paths')

    def validate_disposable(value: Any, location: str) -> None:
        if not isinstance(value, dict):
            errors.append(f'{location} must be an object')
            return
        for name, summary in value.items():
            if name not in KNOWN_DISPOSABLE_CLASSES or not isinstance(summary, dict):
                errors.append(f'{location}.{name} is not a recognized disposable-class summary')
                continue
            if set(summary) != {'count', 'membership_sha256', 'sample_paths', 'sample_truncated'}:
                errors.append(f'{location}.{name} has invalid fields')
                continue
            if type(summary.get('count')) is not int or summary['count'] < 0:
                errors.append(f'{location}.{name}.count is invalid')
            if type(summary.get('sample_truncated')) is not bool:
                errors.append(f'{location}.{name}.sample_truncated must be a boolean')
            membership = summary.get('membership_sha256')
            if membership is not None and (not isinstance(membership, str) or re.fullmatch(r'[0-9a-f]{64}', membership) is None):
                errors.append(f'{location}.{name}.membership_sha256 is invalid')
            samples = summary.get('sample_paths')
            if not isinstance(samples, list) or not all(isinstance(path, str) for path in samples) or len(samples) > 20:
                errors.append(f'{location}.{name}.sample_paths is invalid')
            elif samples != sorted(set(samples), key=_path_sort_key):
                errors.append(f'{location}.{name}.sample_paths is not canonically ordered')

    validate_disposable(snapshot.get('disposable_classes'), f'{label}.disposable_classes')
    publication_scope = snapshot.get('publication_scope')
    if not isinstance(publication_scope, list) or not all(isinstance(path, str) for path in publication_scope):
        errors.append(f'{label} publication_scope must be a list of paths')
    elif publication_scope != sorted(set(publication_scope), key=_path_sort_key):
        errors.append(f'{label} publication_scope is not canonically ordered')
    working = snapshot.get('working_tree_scope')
    working_fields = {'observed_non_git_count', 'authored_candidate_count', 'protected_count', 'disposable_count'}
    if not isinstance(working, dict) or set(working) != working_fields:
        errors.append(f'{label} working_tree_scope has invalid fields')
    elif any(type(working[name]) is not int or working[name] < 0 for name in working):
        errors.append(f'{label} working_tree_scope counts are invalid')
    observation = snapshot.get('observation')
    observation_required = {
        'transport', 'provenance', 'independent_git_discovery_completed',
        'caller_supplied_observations', 'path_selection', 'ignored_enumeration_complete',
    }
    observation_allowed = observation_required | {'qualification'}
    if not isinstance(observation, dict) or not observation_required.issubset(observation) or not set(observation).issubset(observation_allowed):
        errors.append(f'{label} observation has invalid fields')
    else:
        expected_selection = 'independent canonical Git ignored/untracked discovery; caller-supplied lists are complete only after exact independent agreement'
        if observation.get('path_selection') != expected_selection:
            errors.append(f'{label} observation path_selection is invalid')
        provenance = observation.get('provenance')
        transport = observation.get('transport')
        independent = observation.get('independent_git_discovery_completed')
        caller_supplied = observation.get('caller_supplied_observations')
        complete = observation.get('ignored_enumeration_complete')
        if provenance not in {
            'independent-git-discovery',
            'caller-supplied-unverified',
            'caller-supplied-verified-against-independent-git-discovery',
        }:
            errors.append(f'{label} observation provenance is invalid')
        if type(independent) is not bool or type(caller_supplied) is not bool or type(complete) is not bool:
            errors.append(f'{label} observation completeness flags must be booleans')
        if provenance == 'independent-git-discovery' and (transport != 'git-ls-files-z' or caller_supplied is not False):
            errors.append(f'{label} independent observation transport/provenance is contradictory')
        if isinstance(provenance, str) and provenance.startswith('caller-supplied') and (
            transport != 'caller-supplied-nul-path-lists' or caller_supplied is not True
        ):
            errors.append(f'{label} caller-supplied observation transport/provenance is contradictory')
        if complete is True and (
            independent is not True
            or provenance == 'caller-supplied-unverified'
        ):
            errors.append(f'{label} complete observation lacks independent Git authority')
        qualification = observation.get('qualification')
        if complete is False and snapshot.get('status') == 'pass' and (
            not isinstance(qualification, str) or not qualification
        ):
            errors.append(f'{label} incomplete historical evidence requires a non-empty qualification')
        if complete is True and qualification is not None:
            errors.append(f'{label} complete evidence must not carry an incomplete-evidence qualification')
    canonicalization = snapshot.get('canonicalization')
    expected_canonicalization = {
        'ordering': 'ascending os.fsencode(path) bytes',
        'protected_identity': 'SHA-256 of ASCII canonical JSON (sorted keys, compact separators, ensure_ascii) containing schema, normalized policy SHA-256, and protected records',
        'evidence_identity': 'SHA-256 of the complete snapshot except the evidence_identity field itself',
        'disposable_membership': 'SHA-256 of sorted os.fsencode(path) values joined and terminated by NUL; cache bytes are not hashed',
        'timestamps_in_identity': False,
    }
    if canonicalization != expected_canonicalization:
        errors.append(f'{label} canonicalization contract is invalid')
    diagnostics = snapshot.get('diagnostics')
    diagnostic_lists = {
        'missing_protected_artifacts', 'changed_protected_artifacts',
        'new_unclassified_ignored_artifacts', 'new_unclassified_untracked_artifacts',
        'authored_candidates_disguised_as_disposable', 'unsafe_paths_types_or_modes',
    }
    if not isinstance(diagnostics, dict) or set(diagnostics) != diagnostic_lists | {'accepted_disposable_cache_churn'}:
        errors.append(f'{label} diagnostics has invalid fields')
    else:
        for field in diagnostic_lists:
            value = diagnostics.get(field)
            if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
                errors.append(f'{label} diagnostics.{field} must be a list of strings')
        validate_disposable(diagnostics.get('accepted_disposable_cache_churn'), f'{label}.diagnostics.accepted_disposable_cache_churn')
    snapshot_errors = snapshot.get('errors')
    if not isinstance(snapshot_errors, list) or not all(isinstance(item, str) for item in snapshot_errors):
        errors.append(f'{label} errors must be a list of strings')

    try:
        expected_protected = _canonical_json_sha256({
            'schema': IGNORED_ARTIFACT_SNAPSHOT_SCHEMA,
            'policy_sha256': snapshot.get('policy_sha256'),
            'protected_artifacts': records,
        })
        expected_evidence = _snapshot_evidence_identity(snapshot)
    except (TypeError, ValueError):
        errors.append(f'{label} snapshot cannot be canonically fingerprinted')
    else:
        if snapshot.get('protected_identity') != expected_protected:
            errors.append(f'{label} protected_identity does not match canonical protected records')
        if snapshot.get('evidence_identity') != expected_evidence:
            errors.append(f'{label} evidence_identity does not match the complete snapshot')
    return errors


def compare_non_git_artifact_preservation(
    baseline: dict[str, Any],
    current: dict[str, Any],
    *,
    expected_baseline_identity: str | None,
) -> dict[str, Any]:
    """Compare snapshots against an invocation-supplied expected identity.

    The expected value is separate from the baseline document, but this function
    does not authenticate the caller or establish durable external authority.
    """
    errors = _snapshot_validation_errors(baseline, 'baseline')
    errors.extend(_snapshot_validation_errors(current, 'current'))
    if not isinstance(expected_baseline_identity, str) or re.fullmatch(r'[0-9a-f]{64}', expected_baseline_identity) is None:
        errors.append('a caller-supplied expected baseline evidence identity is required')
    elif isinstance(baseline, dict) and baseline.get('evidence_identity') != expected_baseline_identity:
        errors.append('baseline evidence identity does not match the caller-supplied expected identity')
    if errors:
        current_diagnostics = current.get('diagnostics') if isinstance(current, dict) else {}
        current_diagnostics = current_diagnostics if isinstance(current_diagnostics, dict) else {}
        missing_diagnostic = current_diagnostics.get('missing_protected_artifacts')
        changed_diagnostic = current_diagnostics.get('changed_protected_artifacts')
        missing_diagnostic = missing_diagnostic if isinstance(missing_diagnostic, list) else []
        changed_diagnostic = changed_diagnostic if isinstance(changed_diagnostic, list) else []
        return {
            'schema': IGNORED_ARTIFACT_SNAPSHOT_SCHEMA,
            'status': 'fail',
            'baseline_protected_identity': baseline.get('protected_identity') if isinstance(baseline, dict) else None,
            'current_protected_identity': current.get('protected_identity') if isinstance(current, dict) else None,
            'missing_protected_artifacts': missing_diagnostic,
            'unexpected_newly_protected_artifacts': [],
            'changed_protected_artifacts': changed_diagnostic,
            'accepted_disposable_churn': {'membership_changed': False, 'classes': {}},
            'historical_evidence_qualification': None,
            'claims_complete_historical_ignored_enumeration': False,
            'publication_scope_compared': False,
            'expected_identity_authority': 'caller-supplied assertion',
            'errors': errors,
        }
    if baseline.get('policy_sha256') != current.get('policy_sha256'):
        errors.append('baseline and current policy identities differ')

    def by_path(snapshot: Any) -> dict[str, dict[str, Any]]:
        if not isinstance(snapshot, dict) or not isinstance(snapshot.get('protected_artifacts'), list):
            return {}
        result: dict[str, dict[str, Any]] = {}
        for record in snapshot['protected_artifacts']:
            if isinstance(record, dict) and isinstance(record.get('path'), str):
                result[record['path']] = record
        return result

    before = by_path(baseline)
    after = by_path(current)
    missing = sorted(set(before) - set(after), key=_path_sort_key)
    added = sorted(set(after) - set(before), key=_path_sort_key)
    changed = sorted(
        (path for path in set(before) & set(after) if before[path] != after[path]),
        key=_path_sort_key,
    )
    if missing:
        errors.append(f'missing protected artifacts: {missing}')
    if added:
        errors.append(f'unexpected newly protected artifacts: {added}')
    if changed:
        errors.append(f'changed protected artifacts: {changed}')
    if (
        isinstance(baseline, dict)
        and isinstance(current, dict)
        and baseline.get('protected_identity') != current.get('protected_identity')
    ):
        errors.append('baseline and current protected identities differ')

    before_disposable = baseline.get('disposable_classes') if isinstance(baseline, dict) else {}
    after_disposable = current.get('disposable_classes') if isinstance(current, dict) else {}
    before_disposable = before_disposable if isinstance(before_disposable, dict) else {}
    after_disposable = after_disposable if isinstance(after_disposable, dict) else {}
    class_names = sorted(set(before_disposable) | set(after_disposable))
    churn_by_class: dict[str, Any] = {}
    membership_changed = False
    for name in class_names:
        before_summary = before_disposable.get(name) or {'count': 0, 'membership_sha256': None}
        after_summary = after_disposable.get(name) or {'count': 0, 'membership_sha256': None}
        changed_membership = before_summary.get('membership_sha256') != after_summary.get('membership_sha256')
        membership_changed = membership_changed or changed_membership
        churn_by_class[name] = {
            'before_count': before_summary.get('count', 0),
            'after_count': after_summary.get('count', 0),
            'membership_changed': changed_membership,
        }

    baseline_observation = baseline.get('observation') if isinstance(baseline, dict) else {}
    current_observation = current.get('observation') if isinstance(current, dict) else {}
    baseline_complete = baseline_observation.get('ignored_enumeration_complete') is True if isinstance(baseline_observation, dict) else False
    current_complete = current_observation.get('ignored_enumeration_complete') is True if isinstance(current_observation, dict) else False
    qualification = baseline_observation.get('qualification') if isinstance(baseline_observation, dict) and not baseline_complete else None
    return {
        'schema': IGNORED_ARTIFACT_SNAPSHOT_SCHEMA,
        'status': 'fail' if errors else 'pass',
        'baseline_protected_identity': baseline.get('protected_identity') if isinstance(baseline, dict) else None,
        'current_protected_identity': current.get('protected_identity') if isinstance(current, dict) else None,
        'missing_protected_artifacts': missing,
        'unexpected_newly_protected_artifacts': added,
        'changed_protected_artifacts': changed,
        'accepted_disposable_churn': {
            'membership_changed': membership_changed,
            'classes': churn_by_class,
        },
        'historical_evidence_qualification': qualification,
        'claims_complete_historical_ignored_enumeration': baseline_complete and current_complete,
        'publication_scope_compared': False,
        'expected_identity_authority': 'caller-supplied assertion',
        'errors': errors,
    }


def _family_paths(family: dict[str, Any]) -> set[str]:
    values: list[Any] = []
    for key in ('paths', 'representative_paths', 'exact_paths'):
        raw = family.get(key)
        if isinstance(raw, list):
            values.extend(raw)
    manifest = family.get('manifest_ref') or family.get('publication_manifest')
    if isinstance(manifest, str):
        values.append(manifest)
    return {str(value) for value in values if value}


def _exception_complete(exception: Any) -> bool:
    if not isinstance(exception, dict):
        return False
    return all(exception.get(key) for key in ('reason', 'recovery_evidence', 'owner', 'reconsideration_trigger'))


def _declared_git_durable_paths(record: dict[str, Any]) -> set[str]:
    paths: set[str] = set()
    for family in record.get('output_families') or []:
        if isinstance(family, dict) and family.get('terminal_disposition') == GIT_DURABLE_DISPOSITION:
            paths.update(_family_paths(family))
    return paths


def _deferred_git_durable_paths(record: dict[str, Any]) -> set[str]:
    paths: set[str] = set()
    for family in record.get('output_families') or []:
        if (
            isinstance(family, dict)
            and family.get('terminal_disposition') == GIT_DURABLE_DISPOSITION
            and _exception_complete(family.get('bounded_exception'))
        ):
            paths.update(str(path) for path in family.get('deferred_paths') or [])
    return paths


def _closed_object_fields(value: Any, expected: set[str], label: str, errors: list[str]) -> bool:
    if not isinstance(value, dict):
        errors.append(f'{label} must be an object')
        return False
    missing = sorted(expected - set(value))
    unknown = sorted(set(value) - expected)
    if missing:
        errors.append(f'{label} missing required fields: {missing}')
    if unknown:
        errors.append(f'{label} has unknown claim-bearing fields: {unknown}')
    return not missing and not unknown


def _validate_ignored_artifact_lifecycle_profile(record: dict[str, Any], errors: list[str]) -> None:
    """Validate the closed v3 transition-invariant semantic profile."""
    top_fields = {
        'record_type', 'lifecycle_profile', 'task_identity', 'title',
        'authority_baseline', 'publication', 'candidate_state', 'events',
        'reproducibility', 'assurance_boundaries', 'wdi_correction_treatment',
        'output_families', 'non_authoritative_commentary',
    }
    if not _closed_object_fields(record, top_fields, 'lifecycle profile', errors):
        return
    exact_scalars = {
        'record_type': 'bounded-governance-closeout',
        'lifecycle_profile': IGNORED_ARTIFACT_LIFECYCLE_PROFILE,
        'task_identity': 'TASK-PF-20260801',
        'title': 'Ignored-artifact preservation governance',
    }
    for field, expected in exact_scalars.items():
        if record.get(field) != expected:
            errors.append(f'{field} must be {expected!r}')

    exact_objects = {
        'authority_baseline': {
            'branch': 'main',
            'commit': '37cbbbd076926a1dfcecaab11a4c03305d123284',
            'publication_state': 'published',
        },
        'reproducibility': {
            'scope': 'prospective-bounded',
            'historical_completeness': 'not-claimed',
            'retroactive_proof': 'not-available',
            'observation_completeness_authority': 'independent-git-discovery-required',
        },
        'assurance_boundaries': {
            'provider_rights': 'caller-classified-not-independently-established',
            'snapshot_identity': 'caller-supplied-baseline-assertion-not-publication-authority',
            'publication_scope': 'separate-from-preservation-scope',
            'production_postgresql': 'unchanged-read-only-verification-only',
        },
        'wdi_correction_treatment': {
            'reopened': False,
            'amended': False,
            'superseded': False,
            'reviewed_again': False,
            'published_commit_preserved': '37cbbbd076926a1dfcecaab11a4c03305d123284',
        },
    }
    for label, expected in exact_objects.items():
        value = record.get(label)
        _closed_object_fields(value, set(expected), label, errors)
        if isinstance(value, dict):
            for field, expected_value in expected.items():
                if value.get(field) != expected_value:
                    errors.append(f'{label}.{field} must be {expected_value!r}')

    publication = record.get('publication')
    expected_publication = {
        'transition_model': 'state-conditioned-publication-v1',
        'candidate_identity_binding': 'external-review-binds-exact-candidate-bytes',
        'review_evidence_authority': 'authenticated-byte-recoverable-external-evidence',
        'remote_publication_requirement': 'exact-commit-verified-at-authoritative-remote',
        'successor_activation': 'never-implicit',
    }
    publication_closed = _closed_object_fields(
        publication, set(expected_publication), 'publication', errors
    )
    if publication_closed and isinstance(publication, dict):
        for field, expected in expected_publication.items():
            if publication.get(field) != expected:
                errors.append(f'publication.{field} must be {expected!r}')

    candidate = record.get('candidate_state')
    expected_candidate = {
        'representation': 'transition-invariant-candidate-record',
        'review_verdict_authority': 'authenticated-external-evidence',
        'commit_publication_separation': 'local-commit-is-not-verified-remote-publication',
        'current_state_derivation': 'authenticated-git-and-review-evidence',
    }
    candidate_closed = _closed_object_fields(
        candidate, set(expected_candidate), 'candidate_state', errors
    )
    if candidate_closed and isinstance(candidate, dict):
        for field, expected in expected_candidate.items():
            if candidate.get(field) != expected:
                errors.append(f'candidate_state.{field} must be {expected!r}')

    event_specs: tuple[tuple[str, str, tuple[str, ...] | None, str | None], ...] = (
        ('initial-authorship', 'implementation-complete-unpublished', None, None),
        ('first-independent-publication-review', 'blocked-no-publication', (
            'publication-sensitive-lifecycle-wording', 'overbroad-reproducibility',
            'nested-git-path-overreach', 'mode-validation-gap', 'pyc-validation-gap',
            'snapshot-authority-overclaim', 'provider-rights-vocabulary-gap',
            'absent-candidate-acceptance',
        ), None),
        ('first-corrective-pass', 'bounded-correction-implemented', None, None),
        ('second-independent-publication-review', 'blocked-no-publication', (
            'lifecycle-profile-open-world', 'blocking-special-file-open',
            'caller-supplied-observation-false-completeness',
            'unbounded-pytest-marker-read',
        ), None),
        ('second-corrective-pass', 'bounded-correction-implemented', None,
         'superseded-by-subsequent-blocked-audit'),
        ('third-independent-implementation-audit', 'blocked-no-publication', (
            'output-families-cardinality-bypass',
            'canonical-boundary-authority-bypass',
            'stale-lifecycle-truth',
        ), None),
        ('third-corrective-pass', 'bounded-correction-implemented', None,
         'internal-verification-complete-independent-audit-pending-at-correction'),
        ('first-independent-correction-audit', 'blocked-no-publication', (
            'caller-supplied-partial-pair-false-completeness',
        ), None),
        ('fourth-corrective-pass', 'bounded-correction-implemented', None,
         'internal-verification-complete-independent-reaudit-pending-at-correction'),
        ('first-independent-correction-reaudit', 'passed-no-publication-authority', None, None),
        ('first-independent-closeout-consistency-audit', 'passed-no-publication-authority', None, None),
        ('third-independent-publication-review', 'blocked-no-publication', (
            'stale-lifecycle-current-pointer-wording',
        ), None),
        ('fifth-corrective-pass', 'bounded-correction-implemented', None,
         'internal-verification-complete-independent-delta-audit-pending-at-correction'),
        ('independent-lifecycle-delta-audit', 'passed-no-publication-authority', None, None),
        ('fourth-independent-publication-review', 'blocked-no-publication', (
            'publication-transition-fixed-point-defect',
        ), None),
        ('sixth-corrective-pass', 'bounded-correction-implemented', None,
         'internal-verification-complete-independent-transition-audit-required-at-correction'),
    )
    events = record.get('events')
    if not isinstance(events, list) or len(events) != len(event_specs):
        errors.append('events must contain the exact 16-event closed lifecycle history')
    else:
        for index, (event_type, disposition, findings, verification_state) in enumerate(event_specs):
            event = events[index]
            fields = {
                'sequence', 'date', 'event_type', 'disposition',
                'publication_authority', 'publication_occurred', 'state',
            }
            if findings is not None:
                fields.add('findings')
            if verification_state is not None:
                fields.add('verification_state')
            label = f'events[{index}]'
            if not _closed_object_fields(event, fields, label, errors):
                continue
            expected_date = (
                '2026-08-01' if index == 0
                else '2026-08-02' if index <= 6
                else '2026-08-08'
            )
            expected_values = {
                'sequence': index + 1,
                'date': expected_date,
                'event_type': event_type,
                'disposition': disposition,
                'publication_authority': 'not-granted',
                'publication_occurred': False,
            }
            for field, expected_value in expected_values.items():
                if event.get(field) != expected_value:
                    errors.append(f'{label}.{field} must be {expected_value!r}')
            if event.get('state') != {'staged': False, 'committed': False, 'pushed': False}:
                errors.append(f'{label}.state must preserve the exact historical event state')
            if isinstance(findings, tuple) and event.get('findings') != list(findings):
                errors.append(f'{label}.findings must contain the exact ordered controlled finding set')
            if verification_state is not None and event.get('verification_state') != verification_state:
                errors.append(f'{label}.verification_state must be {verification_state!r}')

    families = record.get('output_families')
    if not isinstance(families, list) or len(families) != 1:
        errors.append('output_families must be a list containing exactly one object for this lifecycle profile')
    elif not isinstance(families[0], dict):
        errors.append('output_families[0] must be an object for this lifecycle profile')
    else:
        family = families[0]
        family_fields = {'name', 'role', 'terminal_disposition', 'content_origin', 'paths'}
        _closed_object_fields(family, family_fields, 'output_families[0]', errors)
        expected_family = {
            'name': 'bounded ignored-artifact governance candidate',
            'role': 'authored implementation, tests, doctrine, lifecycle, state, handoff, and affected summaries',
            'terminal_disposition': GIT_DURABLE_DISPOSITION,
            'content_origin': 'authored',
        }
        for field, expected in expected_family.items():
            if family.get(field) != expected:
                errors.append(f'output_families[0].{field} must be {expected!r}')
        paths = family.get('paths')
        if paths != list(IGNORED_ARTIFACT_GOVERNANCE_CANONICAL_PATHS):
            errors.append(
                'output_families[0].paths must equal the code-owned canonical 15-path boundary'
            )

    commentary = record.get('non_authoritative_commentary')
    if not isinstance(commentary, list) or not commentary or not all(
        isinstance(item, str) and item for item in commentary
    ):
        errors.append('non_authoritative_commentary must be a non-empty list of strings')


def validate_lifecycle_closeout(
    record: dict[str, Any],
    publication_boundary: set[str] | list[str] | tuple[str, ...] | None = None,
    *,
    public_publication: bool = True,
    legacy_mode: bool = False,
) -> dict[str, Any]:
    """Validate a MacroForge lifecycle-closeout record.

    Normal forward mode is strict: omitted `output_families` is a lifecycle
    block. Historical records may be grandfathered only when the caller
    explicitly requests legacy mode and the record is not being reopened.
    """
    errors: list[str] = []
    warnings: list[str] = []
    families = record.get('output_families')
    reopened = bool(record.get('reopened_historical_task') or record.get('reopened_historical_record'))
    explicit_legacy = bool(record.get('legacy_record') or record.get('historical_record'))
    if families is None:
        if legacy_mode and explicit_legacy and not reopened:
            return {'status': 'pass', 'grandfathered_legacy_record': True, 'errors': errors, 'warnings': warnings}
        return {
            'status': 'fail',
            'grandfathered_legacy_record': False,
            'errors': ['output_families is required for forward lifecycle closeout; legacy handling must be explicit'],
            'warnings': warnings,
        }
    if not isinstance(families, list):
        return {'status': 'fail', 'grandfathered_legacy_record': False, 'errors': ['output_families must be a list'], 'warnings': warnings}
    if not families:
        return {'status': 'fail', 'grandfathered_legacy_record': False, 'errors': ['output_families must not be empty for forward lifecycle closeout'], 'warnings': warnings}

    record_specific_profile = (
        record.get('record_type') == 'bounded-governance-closeout'
        and record.get('lifecycle_profile') == IGNORED_ARTIFACT_LIFECYCLE_PROFILE
    )
    if record_specific_profile:
        _validate_ignored_artifact_lifecycle_profile(record, errors)
        if publication_boundary is not None and (
            not isinstance(publication_boundary, (list, tuple))
            or tuple(publication_boundary) != IGNORED_ARTIFACT_GOVERNANCE_CANONICAL_PATHS
        ):
            errors.append(
                'supplied publication boundary must equal the code-owned canonical 15-path tuple in canonical order'
            )

    boundary = {str(path) for path in publication_boundary} if publication_boundary is not None else None
    declared_git_paths: set[str] = set()
    authored_nondurable: list[str] = []
    for index, family in enumerate(families):
        if not isinstance(family, dict):
            errors.append(f'output_families[{index}] must be an object')
            continue
        name = str(family.get('name') or f'output_families[{index}]')
        disposition = family.get('terminal_disposition')
        if disposition not in TERMINAL_DISPOSITIONS:
            errors.append(f'{name}: terminal_disposition must be one of {sorted(TERMINAL_DISPOSITIONS)}')
        paths = _family_paths(family)
        if disposition == GIT_DURABLE_DISPOSITION:
            if not paths:
                errors.append(f'{name}: Git-durable family must declare representative/root paths or an exact manifest reference')
            declared_git_paths.update(paths)
            if boundary is not None:
                deferred = {str(path) for path in family.get('deferred_paths') or []}
                missing = sorted(path for path in paths if path not in boundary and path not in deferred)
                if missing and not _exception_complete(family.get('bounded_exception')):
                    errors.append(f'{name}: declared Git-durable paths missing from publication boundary: {missing}')
        elif boundary is not None and any(path in boundary for path in paths):
            warnings.append(f'{name}: non-Git-durable family appears in publication boundary; verify this is intentional')

        origin = family.get('content_origin')
        rights_status = family.get('rights_status')
        included = bool(boundary is not None and paths and paths.issubset(boundary)) or family.get('publication_expectation') in {'public', 'publish now'}
        if public_publication and origin in PROVIDER_CONTENT_ORIGINS and included:
            if rights_status != PERMITTED_RIGHTS_STATUS:
                errors.append(f"{name}: provider-originated public publication requires rights_status='{PERMITTED_RIGHTS_STATUS}', got {rights_status!r}")
            if not family.get('rights_evidence_ref'):
                errors.append(f'{name}: permitted provider publication requires rights_evidence_ref')
        if (family.get('role') in {'authored implementation', 'authored tests', 'authored tools'} or origin == 'authored') and disposition != GIT_DURABLE_DISPOSITION:
            authored_nondurable.append(name)

    if boundary is not None:
        authorized_extra = {str(path) for path in record.get('authorized_extra_publication_paths') or []}
        extra = sorted(path for path in boundary if path not in declared_git_paths and path not in authorized_extra)
        if extra:
            errors.append(f'publication boundary contains undeclared paths: {extra}')
    if record.get('record_type') == 'bounded-governance-closeout':
        if record.get('lifecycle_profile') != IGNORED_ARTIFACT_LIFECYCLE_PROFILE:
            errors.append(
                f'bounded-governance-closeout requires lifecycle_profile={IGNORED_ARTIFACT_LIFECYCLE_PROFILE!r}'
            )

    if record.get('production_postgresql_state_changed') and record.get('reproducibility_claim') == 'full':
        exception = record.get('bounded_reproducibility_exception')
        if authored_nondurable and not _exception_complete(exception):
            errors.append('production PostgreSQL change cannot claim full reproducibility while authored source/tests/tools are non-durable without a complete bounded_reproducibility_exception')
    return {'status': 'fail' if errors else 'pass', 'grandfathered_legacy_record': False, 'errors': errors, 'warnings': warnings}


def verify_publication_boundary(declared_git_durable_paths: list[str], publication_boundary: list[str], *, deferred_paths: list[str] | None = None) -> dict[str, Any]:
    declared = {str(path) for path in declared_git_durable_paths}
    boundary = {str(path) for path in publication_boundary}
    deferred = {str(path) for path in (deferred_paths or [])}
    missing = sorted(path for path in declared if path not in boundary and path not in deferred)
    unauthorized = sorted(path for path in boundary if path not in declared)
    result: dict[str, Any] = {'status': 'fail' if missing or unauthorized else 'pass', 'missing': missing, 'unauthorized': unauthorized}
    if deferred:
        result['deferred'] = sorted(path for path in deferred if path in declared)
    return result


def _load_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding='utf-8'))


def _extract_path_list(value: Any) -> list[str]:
    if isinstance(value, list):
        if all(isinstance(item, str) for item in value):
            return [str(item) for item in value]
        result: list[str] = []
        for item in value:
            if isinstance(item, dict):
                raw = item.get('path') or item.get('file')
                if raw:
                    result.append(str(raw))
        return result
    if isinstance(value, dict):
        for key in ('paths', 'publication_boundary', 'staged_paths', 'files', 'included_paths'):
            if key in value:
                return _extract_path_list(value[key])
        if 'actions' in value:
            return _extract_path_list(value['actions'])
    raise ValueError('publication boundary manifest must be a path list or object containing paths/staged_paths/files/included_paths/actions')


def _ignored_artifact_preservation_section(
    ns: argparse.Namespace,
    root: Path,
    publication_boundary: list[str] | None,
) -> dict[str, Any]:
    try:
        policy = _load_json(ns.ignored_artifact_policy)
        snapshot = capture_non_git_artifact_preservation(
            root,
            policy,
            authored_candidate_paths=publication_boundary or [],
        )
        section: dict[str, Any] = {'capture': snapshot}
        if ns.ignored_artifact_baseline:
            section['comparison'] = compare_non_git_artifact_preservation(
                _load_json(ns.ignored_artifact_baseline),
                snapshot,
                expected_baseline_identity=ns.ignored_artifact_baseline_identity,
            )
        section['status'] = 'fail' if (
            snapshot.get('status') == 'fail'
            or section.get('comparison', {}).get('status') == 'fail'
        ) else 'pass'
        return section
    except (AttributeError, KeyError, OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
        return {'status': 'fail', 'errors': [f'ignored-artifact preservation input failure: {exc}']}


def ignored_artifact_preservation_cli(ns: argparse.Namespace) -> int:
    root = Path(ns.project).resolve()
    try:
        boundary = _extract_path_list(_load_json(ns.publication_boundary)) if ns.publication_boundary else None
    except (AttributeError, KeyError, OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
        result = {'status': 'fail', 'errors': [f'publication-boundary input failure: {exc}']}
        print(json.dumps(result, indent=2, sort_keys=True))
        return 2
    section = _ignored_artifact_preservation_section(ns, root, boundary)
    result = {'status': section['status'], 'ignored_artifact_preservation': section}
    print(json.dumps(result, indent=2, sort_keys=True))
    return 2 if result['status'] == 'fail' else 0


def lifecycle_closeout_cli(ns: argparse.Namespace) -> int:
    root = Path(ns.project).resolve()
    record = _load_json(ns.lifecycle_closeout)
    boundary = None
    if ns.publication_boundary:
        boundary = _extract_path_list(_load_json(ns.publication_boundary))
    result = validate_lifecycle_closeout(
        record,
        boundary,
        public_publication=not ns.private_publication,
        legacy_mode=ns.legacy_record,
    )
    if boundary is not None:
        record_specific_profile = (
            record.get('record_type') == 'bounded-governance-closeout'
            and record.get('lifecycle_profile') == IGNORED_ARTIFACT_LIFECYCLE_PROFILE
        )
        declared_for_boundary: list[str] = (
            [str(path) for path in IGNORED_ARTIFACT_GOVERNANCE_CANONICAL_PATHS]
            if record_specific_profile
            else sorted(_declared_git_durable_paths(record))
        )
        result['publication_boundary'] = verify_publication_boundary(
            declared_for_boundary,
            [str(path) for path in boundary],
            deferred_paths=[] if record_specific_profile else sorted(
                _deferred_git_durable_paths(record)
                | {str(path) for path in record.get('deferred_publication_paths') or []}
            ),
        )
        if record_specific_profile:
            canonical_order_match = tuple(boundary) == IGNORED_ARTIFACT_GOVERNANCE_CANONICAL_PATHS
            result['publication_boundary']['canonical_order_match'] = canonical_order_match
            if not canonical_order_match:
                result['publication_boundary']['status'] = 'fail'
                result['errors'].append(
                    'publication boundary does not equal the code-owned canonical tuple in canonical order'
                )
        if result['publication_boundary']['status'] == 'fail':
            result['status'] = 'fail'
            for path in result['publication_boundary'].get('missing', []):
                if not any(path in error for error in result['errors']):
                    result['errors'].append(f'publication boundary missing declared Git-durable path: {path}')
            for path in result['publication_boundary'].get('unauthorized', []):
                if not any(path in error for error in result['errors']):
                    result['errors'].append(f'publication boundary contains undeclared path: {path}')
    if ns.fingerprint_path:
        fingerprints = content_sensitive_file_fingerprints(
            [Path(path) for path in ns.fingerprint_path],
            base_dir=root,
        )
        result['content_sensitive_fingerprints'] = fingerprints
        result['fingerprint_scope'] = {
            'base_dir': str(root),
            'count': len(fingerprints),
            'exclusions': [],
            'method': 'SHA-256 over regular-file bytes; symlinks and unavailable paths are not followed',
            'requested_paths': list(ns.fingerprint_path),
        }
        unavailable = sorted(path for path, evidence in fingerprints.items() if evidence['sha256'] is None)
        for path in unavailable:
            result['errors'].append(f'{path}: fingerprint path is unavailable or is not a regular non-symlink file')
        if unavailable:
            result['status'] = 'fail'
    if ns.ignored_artifact_policy:
        preservation = _ignored_artifact_preservation_section(ns, root, boundary)
        result['ignored_artifact_preservation'] = preservation
        if preservation['status'] == 'fail':
            result['status'] = 'fail'
            result['errors'].append('ignored-artifact preservation validation failed')
    print(json.dumps(result, indent=2, sort_keys=True))
    return 2 if result.get('status') == 'fail' else 0


def detect_mode(root: Path) -> str:
    if (root / 'projectforge.yaml').exists():
        return 'root'
    return 'generated'


def check_common(root: Path, blocks: list[str], warns: list[str]) -> None:
    if (root/'logs'/'index').exists(): warns.append('logs/index exists; SQLite indexing should be opt-in, not default')
    if (root/'tools'/'update_folder_summaries.py').exists(): warns.append('legacy update_folder_summaries.py present; use update_context_summaries.py')
    if not has_text(root/'permissions'/'escalation_rules.yaml','push_requires_human_approval'):
        blocks.append('manual GitHub push rule missing from permissions/escalation_rules.yaml')
    if (root/'workspace').exists() and (root/'project.yaml').exists():
        py=(root/'project.yaml').read_text(encoding='utf-8', errors='replace').lower()
        if 'meta_project: true' not in py:
            warns.append('project contains workspace/; generated projects should usually use workspace_config.yaml instead')
    v=root/'tools'/'validate_dry_run.py'
    if v.exists():
        import importlib.util
        spec=importlib.util.spec_from_file_location('projectforge_validate_dry_run', v)
        mod=importlib.util.module_from_spec(spec)
        assert spec and spec.loader
        spec.loader.exec_module(mod)
        for report in (root/'simulation'/'dry_runs').glob('*.md') if (root/'simulation'/'dry_runs').exists() else []:
            if report.name in {'README.md','_SUMMARY.md'}:
                continue
            errs=mod.validate(report)
            if errs: blocks.append(f'invalid dry-run report: {report}: {errs[0]}')
    if not has_text(root/'logs'/'logging_policy.yaml', 'raw events') and not has_text(root/'logs'/'logging_policy.yaml', 'raw_operational_record'):
        warns.append('logging policy does not clearly define logs as raw operational records')
    if not has_text(root/'recovery'/'continuity_framework.md', 'Standard ProjectForge closeout contract'):
        blocks.append('continuity framework missing standard closeout contract')
    if not has_text(root/'recovery'/'continuity_framework.md', 'Recover project state and continue work'):
        blocks.append('continuity framework missing fresh-session recovery command contract')
    if not has_text(root/'recovery'/'continuity_framework.md', 'Forward output-family closeout sufficiency'):
        blocks.append('continuity framework missing forward output-family closeout sufficiency contract')
    if not has_text(root/'recovery'/'continuity_framework.md', 'git-durable project truth'):
        blocks.append('continuity framework missing lifecycle terminal disposition vocabulary')
    if not has_text(root/'recovery'/'continuity_framework.md', 'Public accessibility is not redistribution permission'):
        blocks.append('continuity framework missing provider-rights publication gate')
    if not has_text(root/'context'/'context_policy.yaml', 'standard_closeout_order'):
        blocks.append('context policy missing standard continuity closeout order')
    if not has_text(root/'context'/'context_policy.yaml', 'standard_closeout_command'):
        blocks.append('context policy missing standard closeout command')
    run_context_health(root, blocks, warns)


def run_context_health(root: Path, blocks: list[str], warns: list[str]) -> None:
    checker = root / 'tools' / 'context_health.py'
    if not checker.exists():
        warns.append('tools/context_health.py missing; context-size hygiene is not automated')
        return
    spec = importlib.util.spec_from_file_location('projectforge_context_health', checker)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    report = mod.check(root)
    blocks.extend(f'context health: {item}' for item in report.get('blocks', []))
    warns.extend(f'context health: {item}' for item in report.get('warnings', []))


def check_root(root: Path):
    blocks=[]; warns=[]
    for rel in ROOT_REQUIRED:
        if not (root/rel).exists(): blocks.append(f'missing required file: {rel}')
    check_common(root, blocks, warns)
    if not has_text(root/'automation'/'orchestration_schedule.yaml', 'check_coherence'):
        blocks.append('automation schedule does not run check_coherence')
    if not has_text(root/'automation'/'orchestration_schedule.yaml', 'validate_dry_run'):
        blocks.append('automation schedule does not run validate_dry_run')
    if not has_text(root/'automation'/'orchestration_schedule.yaml', 'review_metrics'):
        blocks.append('automation schedule does not run review_metrics')
    if not has_text(root/'automation'/'orchestration_schedule.yaml', 'architecture_reality_audit'):
        blocks.append('automation schedule does not run architecture_reality_audit')
    expected_projects_root = str((root/'workspace'/'projects').resolve())
    if not has_text(root/'workspace'/'workspace_policy.yaml', expected_projects_root):
        blocks.append('workspace policy does not contain configured generated projects path')
    return blocks, warns


def check_generated(root: Path):
    blocks=[]; warns=[]
    for rel in GENERATED_REQUIRED:
        if not (root/rel).exists(): blocks.append(f'missing required file: {rel}')
    check_common(root, blocks, warns)
    if (root/'tools'/'new_project.py').exists():
        warns.append('generated project contains factory-only tools/new_project.py; prefer parent ProjectForge for scaffolding')
    if not has_text(root/'workspace_config.yaml', 'projectforge_root'):
        blocks.append('workspace_config.yaml must record parent projectforge_root')
    if has_text(root/'state'/'active_goal.md', 'Project:') and not has_text(root/'state'/'active_goal.md', 'Purpose'):
        warns.append('state/active_goal.md appears underpopulated')
    relevance_map = root/'architecture'/'metaharvest'/'relevance_map.yaml'
    if not has_text(relevance_map, 'consult_required_during'):
        blocks.append('metaharvest relevance_map.yaml missing consultation trigger list')
    if not has_text(relevance_map, 'active'):
        blocks.append('metaharvest relevance_map.yaml missing active/staleness statuses')
    return blocks, warns


def check(root: Path, mode: str = 'auto'):
    if mode == 'auto':
        mode = detect_mode(root)
    if mode == 'root':
        return check_root(root)
    if mode == 'generated':
        return check_generated(root)
    raise ValueError(f'unknown mode: {mode}')


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--project', default='.')
    ap.add_argument('--mode', choices=['auto','root','generated'], default='auto')
    ap.add_argument('--json', action='store_true')
    ap.add_argument('--lifecycle-closeout', help='validate a forward task closeout JSON record')
    ap.add_argument('--publication-boundary', help='optional JSON publication boundary manifest/path list')
    ap.add_argument('--legacy-record', action='store_true', help='explicitly validate a non-reopened historical record using legacy handling')
    ap.add_argument('--private-publication', action='store_true', help='do not apply public provider-redistribution rights gate')
    ap.add_argument('--fingerprint-path', action='append', default=[], help='include content-sensitive SHA-256 for this bounded path in lifecycle output')
    ap.add_argument('--ignored-artifact-policy', help='JSON policy for protected non-Git artifacts and recognized disposable classes')
    ap.add_argument('--ignored-artifact-baseline', help='optional prior preservation snapshot JSON to compare with the current capture')
    ap.add_argument('--ignored-artifact-baseline-identity', help='caller-supplied SHA-256 evidence_identity expected for --ignored-artifact-baseline; this assertion is not independently authenticated')
    ns=ap.parse_args()
    lifecycle_only = ns.legacy_record or ns.private_publication or ns.fingerprint_path
    if not ns.lifecycle_closeout and lifecycle_only:
        ap.error('use of --legacy-record/--private-publication/--fingerprint-path requires --lifecycle-closeout')
    if ns.publication_boundary and not (ns.lifecycle_closeout or ns.ignored_artifact_policy):
        ap.error('--publication-boundary requires --lifecycle-closeout or --ignored-artifact-policy')
    if ns.ignored_artifact_baseline and not ns.ignored_artifact_policy:
        ap.error('--ignored-artifact-baseline requires --ignored-artifact-policy')
    if bool(ns.ignored_artifact_baseline) != bool(ns.ignored_artifact_baseline_identity):
        ap.error('--ignored-artifact-baseline and --ignored-artifact-baseline-identity are required together')
    try:
        if ns.lifecycle_closeout:
            return lifecycle_closeout_cli(ns)
        if ns.ignored_artifact_policy:
            return ignored_artifact_preservation_cli(ns)
    except (AttributeError, KeyError, OSError, TypeError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({'status': 'fail', 'errors': [f'coherence input failure: {exc}']}, indent=2, sort_keys=True))
        return 2
    root=Path(ns.project).resolve(); blocks,warns=check(root, ns.mode)
    if ns.json:
        print(json.dumps({'mode': ns.mode if ns.mode != 'auto' else detect_mode(root), 'blocks':blocks,'warnings':warns}, indent=2))
    else:
        for b in blocks: print(f'BLOCK: {b}', file=sys.stderr)
        for w in warns: print(f'WARN: {w}')
        print(f'coherence: {len(blocks)} block(s), {len(warns)} warning(s)')
    return 2 if blocks else 0
if __name__=='__main__': raise SystemExit(main())
