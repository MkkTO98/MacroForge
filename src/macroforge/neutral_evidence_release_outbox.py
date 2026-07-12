from __future__ import annotations

import argparse
import json
import os
import shutil
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from macroforge import neutral_evidence_release_exporter as exporter

DEFAULT_REGISTRY_PATH = Path("config/neutral_evidence_release_subscriptions.json")
DEFAULT_OUTBOX_DIR = Path("artifacts/exports/neutral-evidence-release/outbox")
STATUS_REGISTRY_NAME = "export-status-registry.jsonl"


class PublicationConflictError(RuntimeError):
    pass


@dataclass(frozen=True)
class Subscription:
    raw: dict[str, Any]

    @property
    def subscription_id(self) -> str:
        return self.raw["subscription_id"]

    @property
    def subscription_version(self) -> str:
        return self.raw["subscription_version"]

    @property
    def provider_source(self) -> str:
        return self.raw["provider_source"]

    @property
    def dataset(self) -> str:
        return self.raw["dataset"]

    @property
    def indicators(self) -> tuple[str, ...]:
        return tuple(self.raw["indicators"])

    @property
    def entities(self) -> tuple[str, ...]:
        return tuple(self.raw["entities"])

    @property
    def period_policy(self) -> dict[str, Any]:
        return dict(self.raw["period_policy"])

    @property
    def frequency(self) -> str:
        return self.raw["frequency"]

    @property
    def output_format(self) -> str:
        return self.raw["output_format"]

    @property
    def enabled(self) -> bool:
        return bool(self.raw.get("enabled"))

    @property
    def selection_fingerprint(self) -> str:
        return subscription_selection_fingerprint(self)


@dataclass(frozen=True)
class SubscriptionRegistry:
    raw: dict[str, Any]
    subscriptions: dict[str, Subscription]

    def require_enabled(self, subscription_id: str) -> Subscription:
        subscription = self.subscriptions.get(subscription_id)
        if subscription is None:
            raise KeyError(f"missing_subscription:{subscription_id}")
        if not subscription.enabled:
            raise ValueError(f"disabled_subscription:{subscription_id}")
        return subscription


@dataclass(frozen=True)
class EligibilityResult:
    eligible: bool
    reason: str | None
    state: dict[str, Any]


@dataclass(frozen=True)
class PublicationResult:
    status: str
    publication_action: str
    export_identity: str
    release_identity: str
    release_fingerprint: str
    selection_fingerprint: str
    export_sha256: str
    item_count: int
    predecessor_release_identity: str | None
    export_path: Path
    manifest_path: Path
    status_registry_path: Path


@dataclass(frozen=True)
class TriggerResult:
    status: str
    publication_action: str
    release_identity: str
    release_fingerprint: str
    selection_fingerprint: str
    export_sha256: str
    item_count: int
    predecessor_release_identity: str | None
    export_path: Path
    manifest_path: Path
    status_registry_path: Path
    eligibility: dict[str, Any]
    subscription_id: str


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def load_subscription_registry(path: Path = DEFAULT_REGISTRY_PATH) -> SubscriptionRegistry:
    raw = json.loads(path.read_text())
    subscriptions = {item["subscription_id"]: Subscription(item) for item in raw.get("subscriptions", [])}
    return SubscriptionRegistry(raw=raw, subscriptions=subscriptions)


def subscription_selection_fingerprint(subscription: Subscription) -> str:
    payload = {
        "subscription_id": subscription.subscription_id,
        "subscription_version": subscription.subscription_version,
        "provider_source": subscription.provider_source,
        "dataset": subscription.dataset,
        "indicators": list(subscription.indicators),
        "entities": list(subscription.entities),
        "period_policy": subscription.period_policy,
        "frequency": subscription.frequency,
        "include_observed": subscription.raw.get("include_observed"),
        "include_missing": subscription.raw.get("include_missing"),
        "output_format": subscription.output_format,
    }
    return exporter.sha256_canonical(payload)


def evaluate_closeout_eligibility(state: dict[str, Any]) -> EligibilityResult:
    if not state.get("run_key"):
        return EligibilityResult(False, "missing_run_identity", state)
    if not state.get("release_key"):
        return EligibilityResult(False, "missing_release_identity", state)
    if state.get("run_status") != "succeeded":
        return EligibilityResult(False, "run_not_succeeded", state)
    if int(state.get("failed_quality_checks") or 0) != 0:
        return EligibilityResult(False, "quality_failed", state)
    if not state.get("release_complete", True):
        return EligibilityResult(False, "release_not_complete", state)
    if int(state.get("fact_count") or -1) != int(state.get("expected_count") or -2):
        return EligibilityResult(False, "partial_or_incomplete_selection", state)
    return EligibilityResult(True, None, state)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _safe_slug(value: str) -> str:
    return "".join(ch if ch.isalnum() or ch in "-." else "-" for ch in value).strip("-")


def _status_registry_path(outbox_dir: Path) -> Path:
    return outbox_dir / STATUS_REGISTRY_NAME


def _append_registry(outbox_dir: Path, entry: dict[str, Any]) -> Path:
    path = _status_registry_path(outbox_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(canonical_json(entry) + "\n")
    return path


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text())


def _manifest_for(document: dict[str, Any], export_path: Path, content: str, validation: dict[str, Any], subscription: Subscription, *, created_at: str) -> dict[str, Any]:
    return {
        "valid": validation["valid"],
        "contract_identity": exporter.CONTRACT_IDENTITY,
        "contract_version": exporter.CONTRACT_VERSION,
        "exporter_version": exporter.EXPORTER_VERSION,
        "subscription_id": subscription.subscription_id,
        "subscription_version": subscription.subscription_version,
        "subscription_selection_fingerprint": subscription.selection_fingerprint,
        "export_path": str(export_path),
        "item_count": len(document["items"]),
        "release_identity": document["release_identity"],
        "selection_fingerprint": document["selection_fingerprint"],
        "release_fingerprint": document["release_fingerprint"],
        "export_sha256": exporter.sha256_bytes(content.encode("utf-8")),
        "predecessor_release_identity": document.get("predecessor_release_identity"),
        "publication_status": "published",
        "operational_published_at": created_at,
        "validation": validation,
    }


def publish_validated_export(document: dict[str, Any], subscription: Subscription, outbox_dir: Path, *, created_at: str | None = None) -> PublicationResult:
    created_at = created_at or _now()
    validation = exporter.validate_export_document(document)
    release_identity = document["release_identity"]
    export_identity = f"{subscription.subscription_id}--{release_identity}"
    target_dir = outbox_dir / subscription.subscription_id / release_identity
    export_path = target_dir / f"{release_identity}.neutral-release.json"
    manifest_path = target_dir / "manifest.json"
    status_path = _status_registry_path(outbox_dir)

    if not validation["valid"]:
        _append_registry(outbox_dir, {
            "status": "failed",
            "failure_reason": "export_validation_failure",
            "validation": validation,
            "subscription_id": subscription.subscription_id,
            "release_identity": release_identity,
            "operational_timestamp": created_at,
            "retryable": True,
        })
        raise ValueError(validation)

    content = json.dumps(document, sort_keys=True, indent=2, ensure_ascii=False) + "\n"
    new_manifest = _manifest_for(document, export_path, content, validation, subscription, created_at=created_at)

    if manifest_path.exists() and export_path.exists():
        existing_manifest = _read_json(manifest_path)
        if existing_manifest.get("release_fingerprint") == document.get("release_fingerprint"):
            _append_registry(outbox_dir, _registry_entry(document, subscription, existing_manifest, "published", "already_published_identical", created_at))
            return _publication_result(document, existing_manifest, subscription, export_path, manifest_path, status_path, "published", "already_published_identical")
        _append_registry(outbox_dir, _registry_entry(document, subscription, new_manifest, "failed", "conflicting_release_identity", created_at))
        raise PublicationConflictError(f"conflicting_release_identity:{release_identity}")

    staging_root = outbox_dir / "_staging"
    staging_dir = staging_root / f"{_safe_slug(export_identity)}.tmp"
    if staging_dir.exists():
        shutil.rmtree(staging_dir)
    staging_dir.mkdir(parents=True, exist_ok=False)
    try:
        staged_export = staging_dir / export_path.name
        staged_manifest = staging_dir / manifest_path.name
        staged_export.write_text(content)
        staged_manifest.write_text(json.dumps(new_manifest, sort_keys=True, indent=2, ensure_ascii=False) + "\n")
        staged_doc = json.loads(staged_export.read_text())
        staged_validation = exporter.validate_export_document(staged_doc)
        if not staged_validation["valid"]:
            raise ValueError(staged_validation)
        target_dir.parent.mkdir(parents=True, exist_ok=True)
        os.replace(staging_dir, target_dir)
    except Exception:
        if staging_dir.exists():
            shutil.rmtree(staging_dir)
        _append_registry(outbox_dir, _registry_entry(document, subscription, new_manifest, "failed", "publication_failure", created_at))
        raise
    finally:
        if staging_dir.exists():
            shutil.rmtree(staging_dir)
    _append_registry(outbox_dir, _registry_entry(document, subscription, new_manifest, "published", "published_new_release", created_at))
    return _publication_result(document, new_manifest, subscription, export_path, manifest_path, status_path, "published", "published_new_release")


def _registry_entry(document: dict[str, Any], subscription: Subscription, manifest: dict[str, Any], status: str, action: str, created_at: str) -> dict[str, Any]:
    return {
        "release_run_identity": document.get("release_metadata", {}).get("source_run_keys", []),
        "source_release_identity": document.get("release_metadata", {}).get("source_release_keys", []),
        "subscription_id": subscription.subscription_id,
        "subscription_version": subscription.subscription_version,
        "export_identity": f"{subscription.subscription_id}--{document['release_identity']}",
        "release_identity": document["release_identity"],
        "contract_identity": document.get("contract_identity"),
        "contract_version": document.get("contract_version"),
        "selection_fingerprint": document.get("selection_fingerprint"),
        "release_fingerprint": document.get("release_fingerprint"),
        "export_file_hash": manifest.get("export_sha256"),
        "predecessor_release_identity": document.get("predecessor_release_identity"),
        "status": status,
        "publication_action": action,
        "publication_location": manifest.get("export_path"),
        "failure_or_retry_reason": None if status == "published" else action,
        "operational_timestamp": created_at,
    }


def _publication_result(document: dict[str, Any], manifest: dict[str, Any], subscription: Subscription, export_path: Path, manifest_path: Path, status_path: Path, status: str, action: str) -> PublicationResult:
    return PublicationResult(
        status=status,
        publication_action=action,
        export_identity=f"{subscription.subscription_id}--{document['release_identity']}",
        release_identity=document["release_identity"],
        release_fingerprint=manifest["release_fingerprint"],
        selection_fingerprint=manifest["selection_fingerprint"],
        export_sha256=manifest["export_sha256"],
        item_count=int(manifest["item_count"]),
        predecessor_release_identity=manifest.get("predecessor_release_identity"),
        export_path=export_path,
        manifest_path=manifest_path,
        status_registry_path=status_path,
    )


def _observation_key(item: dict[str, Any]) -> tuple[Any, ...]:
    return (item.get("indicator"), item.get("entity"), item.get("period"), item.get("frequency"))


def classify_successor(previous: dict[str, Any], current: dict[str, Any]) -> str:
    if previous.get("contract_version") != current.get("contract_version"):
        return "exporter_or_contract_version_change"
    if previous.get("selection_fingerprint") != current.get("selection_fingerprint"):
        return "selection_change_new_stream"
    if previous.get("release_fingerprint") == current.get("release_fingerprint"):
        return "identical_export_rerun"
    prev_items = {_observation_key(item): item for item in previous.get("items", [])}
    cur_items = {_observation_key(item): item for item in current.get("items", [])}
    prev_keys = set(prev_items)
    cur_keys = set(cur_items)
    if prev_keys < cur_keys:
        return "appended_observations_successor"
    if cur_keys < prev_keys:
        return "removed_or_invalidated_observations_successor"
    for key in prev_keys & cur_keys:
        p, c = prev_items[key], cur_items[key]
        if p.get("value") != c.get("value") or p.get("missing") != c.get("missing") or p.get("observation_status") != c.get("observation_status"):
            return "historical_revision_successor"
        if p.get("unit") != c.get("unit"):
            return "unit_change_successor"
        if p.get("definition") != c.get("definition"):
            return "metadata_only_successor"
    return "metadata_only_successor"


def _sql_array(values: tuple[str, ...]) -> str:
    escaped = ["'" + value.replace("'", "''") + "'" for value in values]
    return "ARRAY[" + ",".join(escaped) + "]"


def discover_scope(database: str, subscription: Subscription, release_key: str, run_key: str) -> tuple[exporter.ExportScope, dict[str, Any]]:
    frequency = "A" if subscription.frequency == "annual" else subscription.frequency
    sql = f"""
WITH selected AS (
  SELECT p.period_year, f.observation_status
  FROM curated.fact_observation f
  JOIN meta.dataset_release dr ON f.dataset_release_id=dr.dataset_release_id
  JOIN meta.pipeline_run pr ON f.pipeline_run_id=pr.pipeline_run_id
  JOIN meta.source s ON f.source_id=s.source_id
  JOIN curated.dim_indicator i ON f.indicator_id=i.indicator_id
  JOIN curated.dim_territory t ON f.territory_id=t.territory_id
  JOIN curated.dim_period p ON f.period_id=p.period_id
  WHERE s.source_code='{subscription.provider_source.replace("'", "''")}'
    AND dr.provider_dataset_code='{subscription.dataset.replace("'", "''")}'
    AND dr.release_key='{release_key.replace("'", "''")}'
    AND pr.run_key='{run_key.replace("'", "''")}'
    AND i.source_indicator_code=ANY({_sql_array(subscription.indicators)})
    AND t.iso3_code=ANY({_sql_array(subscription.entities)})
    AND p.frequency='{frequency}'
)
SELECT json_build_object('min_period', min(period_year), 'max_period', max(period_year), 'fact_count', count(*), 'observed_count', count(*) FILTER (WHERE observation_status='observed'), 'missing_count', count(*) FILTER (WHERE observation_status<>'observed'))::text FROM selected;
"""
    state = exporter._run_psql_json(database, sql) or {}
    if state.get("min_period") is None or state.get("max_period") is None:
        raise ValueError("missing_subscription_scope")
    min_period = max(int(subscription.period_policy.get("minimum_period", state["min_period"])), int(state["min_period"]))
    max_period = int(state["max_period"])
    scope = exporter.ExportScope(
        provider_dataset_code=subscription.dataset,
        indicators=subscription.indicators,
        entities=subscription.entities,
        start_year=min_period,
        end_year=max_period,
        frequency=subscription.frequency,
    )
    expected = len(scope.indicators) * len(scope.entities) * len(scope.periods())
    state["expected_count"] = expected
    return scope, state


def query_closeout_state(database: str, subscription: Subscription, release_key: str, run_key: str, scope_state: dict[str, Any]) -> dict[str, Any]:
    sql = f"""
WITH run AS (
 SELECT pr.pipeline_run_id, pr.run_key, pr.status AS run_status, pr.finished_at, dr.release_key, dr.provider_dataset_code, s.source_code
 FROM meta.pipeline_run pr
 JOIN meta.dataset_release dr ON pr.dataset_release_id=dr.dataset_release_id
 JOIN meta.source s ON pr.source_id=s.source_id
 WHERE pr.run_key='{run_key.replace("'", "''")}' AND dr.release_key='{release_key.replace("'", "''")}' AND s.source_code='{subscription.provider_source.replace("'", "''")}'
), qc AS (
 SELECT count(*) FILTER (WHERE check_status <> 'pass') AS failed_quality_checks FROM meta.quality_check qc JOIN run r ON qc.pipeline_run_id=r.pipeline_run_id
)
SELECT json_build_object('run_key', (SELECT run_key FROM run), 'release_key', (SELECT release_key FROM run), 'run_status', (SELECT run_status FROM run), 'failed_quality_checks', COALESCE((SELECT failed_quality_checks FROM qc), 0), 'fact_count', {int(scope_state.get('fact_count') or 0)}, 'expected_count', {int(scope_state.get('expected_count') or -1)}, 'release_complete', true)::text;
"""
    return exporter._run_psql_json(database, sql) or {"run_key": run_key, "release_key": release_key, "run_status": None, "failed_quality_checks": 999, "fact_count": 0, "expected_count": scope_state.get("expected_count", -1), "release_complete": False}


def run_closeout_export_trigger(*, database: str, release_key: str, run_key: str, subscription_id: str, registry_path: Path = DEFAULT_REGISTRY_PATH, outbox_dir: Path = DEFAULT_OUTBOX_DIR, created_at: str | None = None) -> TriggerResult:
    created_at = created_at or _now()
    registry = load_subscription_registry(registry_path)
    subscription = registry.require_enabled(subscription_id)
    scope, scope_state = discover_scope(database, subscription, release_key, run_key)
    closeout_state = query_closeout_state(database, subscription, release_key, run_key, scope_state)
    eligibility = evaluate_closeout_eligibility(closeout_state)
    if not eligibility.eligible:
        _append_registry(outbox_dir, {"subscription_id": subscription.subscription_id, "source_release_identity": release_key, "release_run_identity": run_key, "status": "not_requested", "publication_action": "ineligible_closeout", "failure_or_retry_reason": eligibility.reason, "operational_timestamp": created_at})
        raise ValueError(f"ineligible_closeout:{eligibility.reason}")
    document = exporter.build_neutral_evidence_release_export(database, scope, created_at=created_at)
    result = publish_validated_export(document, subscription, outbox_dir, created_at=created_at)
    return TriggerResult(
        status=result.status,
        publication_action=result.publication_action,
        release_identity=result.release_identity,
        release_fingerprint=result.release_fingerprint,
        selection_fingerprint=result.selection_fingerprint,
        export_sha256=result.export_sha256,
        item_count=result.item_count,
        predecessor_release_identity=result.predecessor_release_identity,
        export_path=result.export_path,
        manifest_path=result.manifest_path,
        status_registry_path=result.status_registry_path,
        eligibility={"eligible": eligibility.eligible, "reason": eligibility.reason, "state": eligibility.state},
        subscription_id=subscription.subscription_id,
    )


def result_to_dict(result: TriggerResult | PublicationResult) -> dict[str, Any]:
    data = result.__dict__.copy()
    for key in ("export_path", "manifest_path", "status_registry_path"):
        if key in data:
            data[key] = str(data[key])
    return data


def main() -> int:
    parser = argparse.ArgumentParser(description="Publish MacroForge neutral evidence releases after canonical closeout")
    parser.add_argument("--database", default=exporter.DEFAULT_DATABASE)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY_PATH)
    parser.add_argument("--outbox", type=Path, default=DEFAULT_OUTBOX_DIR)
    parser.add_argument("--subscription-id", required=True)
    parser.add_argument("--release-key", required=True)
    parser.add_argument("--run-key", required=True)
    parser.add_argument("--created-at", default=None)
    args = parser.parse_args()
    result = run_closeout_export_trigger(
        database=args.database,
        release_key=args.release_key,
        run_key=args.run_key,
        subscription_id=args.subscription_id,
        registry_path=args.registry,
        outbox_dir=args.outbox,
        created_at=args.created_at,
    )
    print(json.dumps(result_to_dict(result), sort_keys=True, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
