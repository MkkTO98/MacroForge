#!/usr/bin/env python3
"""ProjectForge coherence checker.

Supports root factory projects and generated projects. Root mode validates the
ProjectForge factory contract; generated mode validates the lighter project-local
contract produced by `tools/new_project.py`.
"""
from __future__ import annotations
import argparse, hashlib, importlib.util, json, sys
from pathlib import Path
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
        result['publication_boundary'] = verify_publication_boundary(
            sorted(_declared_git_durable_paths(record)),
            [str(path) for path in boundary],
            deferred_paths=sorted(
                _deferred_git_durable_paths(record)
                | {str(path) for path in record.get('deferred_publication_paths') or []}
            ),
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
    ns=ap.parse_args()
    if not ns.lifecycle_closeout and (ns.publication_boundary or ns.legacy_record or ns.private_publication or ns.fingerprint_path):
        ap.error('use of --publication-boundary/--legacy-record/--private-publication/--fingerprint-path requires --lifecycle-closeout')
    if ns.lifecycle_closeout:
        return lifecycle_closeout_cli(ns)
    root=Path(ns.project).resolve(); blocks,warns=check(root, ns.mode)
    if ns.json:
        print(json.dumps({'mode': ns.mode if ns.mode != 'auto' else detect_mode(root), 'blocks':blocks,'warnings':warns}, indent=2))
    else:
        for b in blocks: print(f'BLOCK: {b}', file=sys.stderr)
        for w in warns: print(f'WARN: {w}')
        print(f'coherence: {len(blocks)} block(s), {len(warns)} warning(s)')
    return 2 if blocks else 0
if __name__=='__main__': raise SystemExit(main())
