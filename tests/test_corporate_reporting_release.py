"""TASK-221 RED contract for authority-resolved build and anchored publication.

Expected production API (intentionally absent before remediation A):

    build_private_release(*, authority: CorporateAuthorityRef,
                          store: PostgresCorporateAuthorityStore) -> CorporateRelease
    publish_database_anchored(*, authority: CorporateAuthorityRef,
                              store: PostgresCorporateAuthorityStore,
                              target: Path) -> PublicationAct

Caller-authored ReleasePolicy/ExpectedSelection/ReleaseEligibility/
AuthorityRevisions/ReleaseAuthorityEvidence/ReleaseItem values are request views at
most and can never be trust anchors.  A publication act is persisted in PostgreSQL;
a repeat returns that original act or is rejected, and never appends another act.
"""
from dataclasses import asdict, dataclass, replace
from hashlib import sha256
import inspect
import json
from pathlib import Path
import pickle
from typing import Any, Mapping

import pytest

import macroforge.corporate_reporting_release as release_module
from macroforge.corporate_reporting_release import (
    AuthorityRevisions, EligibilityError, ExpectedSelection, ReleaseAuthorityEvidence,
    ReleaseEligibility, ReleaseItem, ReleasePolicy, build_private_release,
    publish_database_anchored,
    publish_local_immutable,
)

H = lambda c: c * 64


def _root(value: Mapping[str, Any]) -> str:
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def _evidence() -> ReleaseAuthorityEvidence:
    return ReleaseAuthorityEvidence(
        source_manifest={
            "schema": "macroforge-corporate-source-manifest-v1", "provider": "SEC",
            "source_set_id": "task221-synthetic",
            "documents": [{"accession": "0001104659-23-074911", "sha256": H("1")}],
        },
        quality_decision={
            "schema": "macroforge-corporate-quality-decision-v1", "decision_id": "quality-r1",
            "status": "accepted", "knowledge_snapshot_id": "snapshot-1",
            "checks": [{"check_id": "closure", "status": "passed", "evidence_sha256": H("2")}],
        },
    )


def _contract():
    evidence = _evidence()
    policy = ReleasePolicy("policy-1", "private-analysis-v1", H("a"))
    expected = ExpectedSelection("expected-r1", H("b"), "accepted", ("assets",))
    eligibility = ReleaseEligibility(
        "eligibility-r1", "eligible", (), "policy-1", "expected-r1", "snapshot-1",
        _root(evidence.source_manifest), _root(evidence.quality_decision),
    )
    authority = AuthorityRevisions("parser-r1", "expected-r1", "snapshot-1")
    return policy, expected, eligibility, authority, evidence


def _item(**changes: Any) -> ReleaseItem:
    values: dict[str, Any] = {
        "item_key": "assets", "provider": "SEC", "accession": "0001104659-23-074911",
        "report_period": "2021-12-31", "canonical_concept": "TASK221_SYNTHETIC_ASSETS",
        "scope": "consolidated_registrant", "dimensions": (),
        "unit": {"numerator": ["USD"], "denominator": []}, "state": "reported", "value": "1",
        "mapping_evidence_fingerprint": H("e"), "resolution_evidence_fingerprint": H("f"),
        "source_occurrence_fingerprints": (H("1"),), "parser_selection_revision_id": "parser-r1",
        "resolution_revision_id": "resolution-r1", "mapping_revision_id": "mapping-r1",
        "absence_revision_id": None,
    }
    values.update(changes)
    return ReleaseItem(**values)


def _legacy_build(**changes: Any):
    policy, expected, eligibility, authority, evidence = _contract()
    args = {
        "eligibility": eligibility, "policy": policy, "expected_selection": expected,
        "authority": authority, "authority_evidence": evidence,
    }
    args.update(changes)
    return release_module._build_private_release_from_values(
        "sub-r1", "2023-07-01T00:00:00Z", (_item(),), **args,
    )


def test_expected_build_api_accepts_only_database_store_and_authority_reference() -> None:
    parameters = inspect.signature(build_private_release).parameters
    assert tuple(parameters) == ("authority", "store")
    assert all(parameter.kind is inspect.Parameter.KEYWORD_ONLY for parameter in parameters.values())


def test_expected_database_anchored_publisher_api_is_public() -> None:
    assert hasattr(release_module, "publish_database_anchored"), "missing proposed database-anchored publication API"


@pytest.mark.parametrize("copy_kind", ("original", "replace", "pickle"))
def test_caller_authored_reconstructed_or_pickled_authority_cannot_self_authorize(copy_kind: str) -> None:
    policy, expected, eligibility, authority, evidence = _contract()
    if copy_kind == "replace":
        authority = replace(authority)
        eligibility = replace(eligibility)
    elif copy_kind == "pickle":
        authority, eligibility, policy, expected, evidence = pickle.loads(
            pickle.dumps((authority, eligibility, policy, expected, evidence))
        )
    with pytest.raises((TypeError, EligibilityError), match="store|authority reference|database|trust|unexpected keyword"):
        build_private_release(
            "sub-r1", "2023-07-01T00:00:00Z", (_item(),), eligibility=eligibility,
            policy=policy, expected_selection=expected, authority=authority,
            authority_evidence=evidence,
        )


def test_former_authority_free_publisher_rejects_self_consistent_release_without_side_effects(
    tmp_path: Path,
) -> None:
    """Digest self-consistency is evidence, never filesystem publication authority."""
    release = _legacy_build()
    target = tmp_path / "release.json"
    with pytest.raises((TypeError, EligibilityError), match="authority|database|disabled|governed"):
        publish_local_immutable(target, release)
    assert list(tmp_path.iterdir()) == []


def test_governed_publisher_accepts_no_caller_release_or_canonical_json() -> None:
    parameters = inspect.signature(publish_database_anchored).parameters
    assert tuple(parameters) == ("authority", "store", "target")
    assert all(parameter.kind is inspect.Parameter.KEYWORD_ONLY for parameter in parameters.values())


def test_no_module_level_publication_metadata_writer_remains_callable() -> None:
    assert not hasattr(release_module, "_append_status")


def test_lifecycle_sql_exists_only_inside_the_complete_governed_publisher() -> None:
    import macroforge.corporate_reporting_queries as query_module

    lifecycle_relations = (
        "corporate_publication_reservation", "corporate_publication_completion",
    )
    query_source = inspect.getsource(query_module)
    assert all(relation not in query_source for relation in lifecycle_relations)
    assert not hasattr(query_module.PostgresCorporateAuthorityStore, "record_publication")
    assert not hasattr(query_module.PostgresCorporateAuthorityStore, "complete_publication")
    assert not hasattr(query_module.PostgresCorporateAuthorityStore, "_sql")

    publisher_source = inspect.getsource(publish_database_anchored)
    assert all(relation in publisher_source for relation in lifecycle_relations)
    for name, value in vars(release_module).items():
        if name == "publish_database_anchored" or not inspect.isfunction(value):
            continue
        source = inspect.getsource(value)
        assert all(relation not in source for relation in lifecycle_relations), name


@pytest.mark.parametrize(
    "changes",
    (
        {"dimensions": ({"axis": "{urn:test}Axis", "member_kind": "explicit",
                         "explicit_member": "{urn:test}Member", "typed_member": None,
                         "internal_dimension_id": "secret"},)},
        {"dimensions": ({"axis": "{urn:test}Axis", "member_kind": "typed", "explicit_member": None,
                         "typed_member": {"sha256": H("2"), "internal_xml": "<secret/>"}},)},
        {"unit": {"numerator": ["USD"], "denominator": [], "internal_unit_id": "secret"}},
    ),
)
def test_release_item_dimension_typed_member_and_unit_are_recursive_allowlists(changes: dict[str, Any]) -> None:
    with pytest.raises(EligibilityError, match="unknown|internal|allowlist"):
        _legacy_build() if not changes else release_module._build_private_release_from_values(
            "sub-r1", "cutoff", (_item(**changes),),
            eligibility=_contract()[2], policy=_contract()[0], expected_selection=_contract()[1],
            authority=_contract()[3], authority_evidence=_contract()[4],
        )


@pytest.mark.parametrize(
    ("container", "internal_key"),
    (
        ("source_refs", "internal_locator"),
        ("mapping", "internal_assertion_id"),
        ("equivalence", "internal_equivalence_sql"),
        ("quality", "internal_quality_sql"),
    ),
)
def test_source_mapping_equivalence_and_quality_are_recognized_recursive_allowlists(
    container: str, internal_key: str,
) -> None:
    raw = asdict(_item())
    external: dict[str, Any] = {
        "source_refs": ({"occurrence_sha256": H("1"), internal_key: "secret"},),
        "mapping": {"revision_id": "mapping-r1", "evidence_sha256": H("e"), internal_key: "secret"},
        "equivalence": {"revision_id": "equivalence-r1", "evidence_sha256": H("d"), internal_key: "secret"},
        "quality": {"decision_sha256": H("c"), "evidence_sha256": H("d"), internal_key: "secret"},
    }
    raw[container] = external[container]
    with pytest.raises(EligibilityError, match=internal_key):
        ReleaseItem.from_mapping(raw)


def test_top_level_item_and_authority_metadata_extra_fields_cannot_leak() -> None:
    @dataclass(frozen=True)
    class ExtendedItem(ReleaseItem):
        internal_source_locator: str = "/private/document.xml"

    extended = ExtendedItem(**asdict(_item()))
    payload = _legacy_build().payload
    assert b"internal_source_locator" not in payload
    assert b"/private/document.xml" not in payload

    policy, expected, eligibility, authority, evidence = _contract()
    poisoned = ReleaseAuthorityEvidence(
        source_manifest={**evidence.source_manifest, "internal_bucket": "secret"},
        quality_decision=evidence.quality_decision,
    )
    with pytest.raises(EligibilityError, match="internal_bucket"):
        release_module._build_private_release_from_values(
            "sub", "cutoff", (extended,), eligibility=eligibility, policy=policy,
            expected_selection=expected, authority=authority, authority_evidence=poisoned,
        )


def test_extended_item_is_rejected_not_silently_projected() -> None:
    @dataclass(frozen=True)
    class ExtendedItem(ReleaseItem):
        internal_source_locator: str = "/private/document.xml"

    extended = ExtendedItem(**asdict(_item()))
    policy, expected, eligibility, authority, evidence = _contract()
    with pytest.raises(EligibilityError, match="exact ReleaseItem|subclass"):
        release_module._build_private_release_from_values(
            "sub", "cutoff", (extended,), eligibility=eligibility, policy=policy,
            expected_selection=expected, authority=authority, authority_evidence=evidence,
        )
