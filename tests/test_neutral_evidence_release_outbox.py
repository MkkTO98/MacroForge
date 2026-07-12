from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

from macroforge import neutral_evidence_release_exporter as exporter
from macroforge import neutral_evidence_release_outbox as outbox


PILOT_SUBSCRIPTION_ID = "macroforge-wdi-trade-share-dnk-swe-nor-annual-v1"
PILOT_RUN_KEY = "task-176-repository-growth-historical-scaling-rerun"
PILOT_RELEASE_KEY = "WDI:2026-07-01:1990:2024"


def _sample_document(release_identity: str = "macroforge-test-release") -> dict:
    item = {
        "item_id": "wdi:DNK:NE.EXP.GNFS.ZS:1990",
        "provider_identity": "World Bank",
        "dataset_identity": "World Development Indicators",
        "source_provider_dataset_code": "WDI",
        "entity": "DNK",
        "entity_label": "Denmark",
        "indicator": "NE.EXP.GNFS.ZS",
        "indicator_label": "Exports of goods and services (% of GDP)",
        "period": "1990",
        "frequency": "annual",
        "unit": "percent of GDP",
        "definition": "Exports of goods and services (% of GDP)",
        "value": "35.1",
        "missing": False,
        "observation_status": "observed",
        "provenance": {"source_code": "WDI", "provider_dataset_code": "WDI", "release_key": PILOT_RELEASE_KEY, "run_key": PILOT_RUN_KEY},
    }
    item["item_fingerprint"] = exporter.item_fingerprint(item)
    document = {
        "contract_identity": exporter.CONTRACT_IDENTITY,
        "contract_version": exporter.CONTRACT_VERSION,
        "producing_system": "MacroForge",
        "exporter_version": exporter.EXPORTER_VERSION,
        "release_identity": release_identity,
        "original_provider": {
            "provider_identity": "World Bank",
            "dataset_identity": "World Development Indicators",
            "provider_dataset_code": "WDI",
            "source_release_or_vintage": [PILOT_RELEASE_KEY],
        },
        "predecessor_release_identity": None,
        "publication_metadata": {"producer": "MacroForge", "operational_created_at_excluded_from_deterministic_identity": True},
        "selection": {
            "provider_dataset_code": "WDI",
            "indicators": ["NE.EXP.GNFS.ZS"],
            "entities": ["DNK"],
            "periods": ["1990"],
            "frequency": "annual",
        },
        "release_metadata": {
            "source_release_keys": [PILOT_RELEASE_KEY],
            "source_run_keys": [PILOT_RUN_KEY],
            "run_statuses": ["succeeded"],
            "quality_status": "eligible_only_if_all_source_runs_succeeded",
        },
        "items": [item],
        "operational_metadata": {"created_at": "2026-07-11T00:00:00Z"},
    }
    exporter.recompute_document_fingerprints(document)
    return document


def test_default_subscription_registry_is_consumer_neutral_and_fingerprint_stable():
    registry = outbox.load_subscription_registry(Path("config/neutral_evidence_release_subscriptions.json"))
    subscription = registry.require_enabled(PILOT_SUBSCRIPTION_ID)

    assert subscription.subscription_id == PILOT_SUBSCRIPTION_ID
    assert subscription.provider_source == "WDI"
    assert subscription.dataset == "WDI"
    assert subscription.indicators == ("NE.EXP.GNFS.ZS", "NE.IMP.GNFS.ZS")
    assert subscription.entities == ("DNK", "SWE", "NOR")
    assert subscription.period_policy["type"] == "available_canonical_scope"
    assert subscription.output_format == "single_json"
    assert subscription.enabled is True
    assert subscription.selection_fingerprint == outbox.subscription_selection_fingerprint(subscription)
    serialized = json.dumps(subscription.raw, sort_keys=True).lower()
    assert "knowledgeforge" not in serialized
    assert "correlation" not in serialized
    assert "pearson" not in serialized


@pytest.mark.parametrize(
    "state, expected",
    [
        ({"run_key": PILOT_RUN_KEY, "release_key": PILOT_RELEASE_KEY, "run_status": "succeeded", "failed_quality_checks": 0, "fact_count": 210, "expected_count": 210, "release_complete": True}, True),
        ({"run_key": PILOT_RUN_KEY, "release_key": PILOT_RELEASE_KEY, "run_status": "failed", "failed_quality_checks": 0, "fact_count": 210, "expected_count": 210, "release_complete": True}, False),
        ({"run_key": PILOT_RUN_KEY, "release_key": PILOT_RELEASE_KEY, "run_status": "succeeded", "failed_quality_checks": 1, "fact_count": 210, "expected_count": 210, "release_complete": True}, False),
        ({"run_key": PILOT_RUN_KEY, "release_key": PILOT_RELEASE_KEY, "run_status": "succeeded", "failed_quality_checks": 0, "fact_count": 209, "expected_count": 210, "release_complete": True}, False),
        ({"run_key": "", "release_key": PILOT_RELEASE_KEY, "run_status": "succeeded", "failed_quality_checks": 0, "fact_count": 210, "expected_count": 210, "release_complete": True}, False),
        ({"run_key": PILOT_RUN_KEY, "release_key": PILOT_RELEASE_KEY, "run_status": "succeeded", "failed_quality_checks": 0, "fact_count": 210, "expected_count": 210, "release_complete": False}, False),
    ],
)
def test_closeout_eligibility_fails_closed_for_incomplete_or_failed_states(state, expected):
    result = outbox.evaluate_closeout_eligibility(state)
    assert result.eligible is expected
    if not expected:
        assert result.reason


def test_atomic_publication_is_idempotent_and_conflicts_fail_closed(tmp_path: Path):
    subscription = outbox.load_subscription_registry(Path("config/neutral_evidence_release_subscriptions.json")).require_enabled(PILOT_SUBSCRIPTION_ID)
    document = _sample_document()

    first = outbox.publish_validated_export(document, subscription, tmp_path / "outbox", created_at="2026-07-11T00:00:00Z")
    second = outbox.publish_validated_export(document, subscription, tmp_path / "outbox", created_at="2026-07-11T01:00:00Z")

    assert first.status == "published"
    assert second.status == "published"
    assert second.publication_action == "already_published_identical"
    assert first.export_sha256 == second.export_sha256
    assert first.export_path.read_bytes() == second.export_path.read_bytes()
    assert not list((tmp_path / "outbox" / "_staging").glob("*"))
    assert len((tmp_path / "outbox" / "export-status-registry.jsonl").read_text().splitlines()) == 2

    conflicting = _sample_document()
    conflicting["items"][0]["value"] = "999"
    exporter.recompute_document_fingerprints(conflicting)
    with pytest.raises(outbox.PublicationConflictError):
        outbox.publish_validated_export(conflicting, subscription, tmp_path / "outbox", created_at="2026-07-11T02:00:00Z")


@pytest.mark.parametrize(
    "previous,current,expected",
    [
        ({"selection_fingerprint": "s1", "release_fingerprint": "r1", "contract_version": "1.0", "items": [{"indicator": "A", "entity": "X", "period": "2000", "value": "1", "unit": "u", "definition": "d"}]}, {"selection_fingerprint": "s1", "release_fingerprint": "r1", "contract_version": "1.0", "items": [{"indicator": "A", "entity": "X", "period": "2000", "value": "1", "unit": "u", "definition": "d"}]}, "identical_export_rerun"),
        ({"selection_fingerprint": "s1", "release_fingerprint": "r1", "contract_version": "1.0", "items": [{"indicator": "A", "entity": "X", "period": "2000", "value": "1", "unit": "u", "definition": "d"}]}, {"selection_fingerprint": "s1", "release_fingerprint": "r2", "contract_version": "1.0", "items": [{"indicator": "A", "entity": "X", "period": "2000", "value": "1", "unit": "u", "definition": "d"}, {"indicator": "A", "entity": "X", "period": "2001", "value": "2", "unit": "u", "definition": "d"}]}, "appended_observations_successor"),
        ({"selection_fingerprint": "s1", "release_fingerprint": "r1", "contract_version": "1.0", "items": [{"indicator": "A", "entity": "X", "period": "2000", "value": "1", "unit": "u", "definition": "d"}]}, {"selection_fingerprint": "s1", "release_fingerprint": "r2", "contract_version": "1.0", "items": [{"indicator": "A", "entity": "X", "period": "2000", "value": "2", "unit": "u", "definition": "d"}]}, "historical_revision_successor"),
        ({"selection_fingerprint": "s1", "release_fingerprint": "r1", "contract_version": "1.0", "items": [{"indicator": "A", "entity": "X", "period": "2000", "value": "1", "unit": "u", "definition": "d"}]}, {"selection_fingerprint": "s2", "release_fingerprint": "r2", "contract_version": "1.0", "items": [{"indicator": "B", "entity": "X", "period": "2000", "value": "1", "unit": "u", "definition": "d"}]}, "selection_change_new_stream"),
        ({"selection_fingerprint": "s1", "release_fingerprint": "r1", "contract_version": "1.0", "items": [{"indicator": "A", "entity": "X", "period": "2000", "value": "1", "unit": "u", "definition": "d"}]}, {"selection_fingerprint": "s1", "release_fingerprint": "r2", "contract_version": "1.0", "items": [{"indicator": "A", "entity": "X", "period": "2000", "value": "1", "unit": "u", "definition": "changed"}]}, "metadata_only_successor"),
        ({"selection_fingerprint": "s1", "release_fingerprint": "r1", "contract_version": "1.0", "items": []}, {"selection_fingerprint": "s1", "release_fingerprint": "r2", "contract_version": "2.0", "items": []}, "exporter_or_contract_version_change"),
    ],
)
def test_successor_semantics_are_explicit(previous, current, expected):
    assert outbox.classify_successor(previous, current) == expected


def test_disabled_missing_subscription_and_publication_failures_do_not_publish(tmp_path: Path, monkeypatch):
    registry_path = tmp_path / "subscriptions.json"
    raw = json.loads(Path("config/neutral_evidence_release_subscriptions.json").read_text())
    raw["subscriptions"][0]["enabled"] = False
    registry_path.write_text(json.dumps(raw))
    registry = outbox.load_subscription_registry(registry_path)
    with pytest.raises(ValueError, match="disabled_subscription"):
        registry.require_enabled(PILOT_SUBSCRIPTION_ID)
    with pytest.raises(KeyError, match="missing_subscription"):
        registry.require_enabled("missing")

    enabled = outbox.load_subscription_registry(Path("config/neutral_evidence_release_subscriptions.json")).require_enabled(PILOT_SUBSCRIPTION_ID)
    invalid = _sample_document("invalid-release")
    invalid["items"][0]["item_fingerprint"] = "sha256:bad"
    with pytest.raises(ValueError):
        outbox.publish_validated_export(invalid, enabled, tmp_path / "outbox", created_at="2026-07-11T00:00:00Z")
    assert not list((tmp_path / "outbox").glob("**/*.neutral-release.json"))

    def broken_replace(_src, _dst):
        raise OSError("simulated publication failure")

    monkeypatch.setattr(outbox.os, "replace", broken_replace)
    with pytest.raises(OSError, match="simulated publication failure"):
        outbox.publish_validated_export(_sample_document("publication-failure"), enabled, tmp_path / "outbox", created_at="2026-07-11T00:00:00Z")
    assert not list((tmp_path / "outbox" / "_staging").glob("*"))
    assert not list((tmp_path / "outbox").glob("**/publication-failure.neutral-release.json"))


def test_real_completed_closeout_trigger_publishes_pilot_equivalent_export(tmp_path: Path):
    if shutil.which("psql") is None:
        pytest.skip("psql unavailable")
    probe = subprocess.run(["psql", "-d", "macroforge", "-At", "-c", "SELECT 1"], text=True, capture_output=True)
    if probe.returncode != 0:
        pytest.skip("macroforge database unavailable")

    result = outbox.run_closeout_export_trigger(
        database="macroforge",
        release_key=PILOT_RELEASE_KEY,
        run_key=PILOT_RUN_KEY,
        subscription_id=PILOT_SUBSCRIPTION_ID,
        registry_path=Path("config/neutral_evidence_release_subscriptions.json"),
        outbox_dir=tmp_path / "outbox",
        created_at="2026-07-11T00:00:00Z",
    )
    prior = json.loads(Path("artifacts/exports/neutral-evidence-release/task-210-wdi-trade-share-dnk-swe-nor-1990-2024/manifest.json").read_text())

    assert result.status == "published"
    assert result.release_fingerprint == prior["release_fingerprint"]
    assert result.selection_fingerprint == prior["selection_fingerprint"]
    assert result.export_sha256 == prior["export_sha256"]
    assert result.item_count == 210
    assert result.predecessor_release_identity is None

    rerun = outbox.run_closeout_export_trigger(
        database="macroforge",
        release_key=PILOT_RELEASE_KEY,
        run_key=PILOT_RUN_KEY,
        subscription_id=PILOT_SUBSCRIPTION_ID,
        registry_path=Path("config/neutral_evidence_release_subscriptions.json"),
        outbox_dir=tmp_path / "outbox",
        created_at="2026-07-11T01:00:00Z",
    )
    assert rerun.publication_action == "already_published_identical"
