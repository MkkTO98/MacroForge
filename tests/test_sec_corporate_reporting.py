from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from macroforge.sec_corporate_reporting import (
    ManifestError,
    ParserInvariantError,
    compare_filings,
    parse_extension_schema,
    parse_instance,
    validate_protected_manifest,
)

FIXTURES = Path(__file__).parent / "fixtures" / "sec_corporate_reporting"
PROTECTED = Path("/tmp/macroforge-corporate-gatos-freeze-6DQdCj")


def test_compact_occurrences_slots_dimensions_typed_units_and_conflict() -> None:
    report = parse_instance(FIXTURES / "compact-instance.xml", accession="0000000001-24-000001", dts_manifest_sha256="a" * 64)
    assert report.metrics == {
        "context_count": 3, "instant_context_count": 2, "duration_context_count": 1,
        "dimensioned_context_count": 3, "typed_member_count": 1, "unit_count": 2,
        "fact_count": 5, "semantic_slot_count": 4, "duplicate_slot_count": 1,
        "duplicate_occurrence_excess": 1, "conflicting_slot_count": 0,
    }
    explicit = report.contexts["two-axis"].dimensions
    assert len(explicit) == 2 and explicit[0].axis != explicit[1].axis
    assert report.contexts["two-axis"].semantic_hash != report.contexts["one-axis"].semantic_hash
    typed = report.contexts["typed"].dimensions[0]
    assert typed.member_kind == "typed" and typed.typed_member_sha256
    usd_per_share = report.units["usd-per-share"]
    assert usd_per_share.numerator == ("{http://www.xbrl.org/2003/iso4217}USD",)
    assert usd_per_share.denominator == ("{http://www.xbrl.org/2003/instance}shares",)
    # Occurrence identity includes ordinal while semantic slot does not.
    duplicates = [s for s in report.slots.values() if len(s.occurrences) == 2][0]
    assert len({o.occurrence_sha256 for o in duplicates.occurrences}) == 2

    conflict = parse_instance(FIXTURES / "compact-conflict.xml", accession="0000000001-24-000001", dts_manifest_sha256="a" * 64)
    bad = [s for s in conflict.slots.values() if s.status == "conflict"]
    assert len(bad) == 1 and bad[0].selected_occurrence is None and len(bad[0].occurrences) == 2


def test_malformed_divide_and_parser_drift() -> None:
    with pytest.raises(ParserInvariantError, match="divide"):
        parse_instance(FIXTURES / "malformed-divide.xml", accession="0000000001-24-000001", dts_manifest_sha256="a" * 64)
    baseline = parse_instance(FIXTURES / "compact-instance.xml", accession="0000000001-24-000001", dts_manifest_sha256="a" * 64)
    drift = baseline.classify_drift({**baseline.metrics, "fact_count": 6})
    assert drift.status == "review" and "fact_count" in drift.changed_metrics
    assert baseline.metrics_sha256 == hashlib.sha256(baseline.canonical_metrics_bytes).hexdigest()


def test_typed_xml_canonicalization_and_qname_expansion_are_semantic(tmp_path: Path) -> None:
    source = (FIXTURES / "compact-instance.xml").read_text()
    # Prefix and boundary whitespace are serialization choices, not typed values.
    equivalent = source.replace('xmlns:ex="http://example.test/typed"',
                                'xmlns:alternate="http://example.test/typed"')
    equivalent = equivalent.replace('dimension="ex:LegalEntityAxis"',
                                    'dimension="alternate:LegalEntityAxis"')
    equivalent = equivalent.replace('<ex:identifier code="A"> Alpha </ex:identifier>',
                                    '<alternate:identifier code="A">Alpha</alternate:identifier>')
    equivalent_path = tmp_path / "equivalent.xml"
    equivalent_path.write_text(equivalent)
    changed_path = tmp_path / "changed.xml"
    changed_path.write_text(equivalent.replace('code="A"', 'code="B"'))
    baseline = parse_instance(FIXTURES / "compact-instance.xml", accession="0000000001-24-000001",
                              dts_manifest_sha256="a" * 64)
    same = parse_instance(equivalent_path, accession=baseline.accession, dts_manifest_sha256="a" * 64)
    changed = parse_instance(changed_path, accession=baseline.accession, dts_manifest_sha256="a" * 64)
    typed = baseline.contexts["typed"].dimensions[0]
    assert typed.typed_member_sha256 == same.contexts["typed"].dimensions[0].typed_member_sha256
    assert typed.typed_member_sha256 != changed.contexts["typed"].dimensions[0].typed_member_sha256
    assert baseline.units["usd"].numerator == ("{http://www.xbrl.org/2003/iso4217}USD",)


def test_typed_member_xsi_type_qname_canonicalization_is_namespace_semantic_and_replayable(
    tmp_path: Path,
) -> None:
    source = (FIXTURES / "compact-instance.xml").read_text()

    def typed_variant(name: str, *, type_prefix: str, type_namespace: str,
                      guard: str = "literal:colon") -> Path:
        xml = source.replace(
            'xmlns:ex="http://example.test/typed"',
            'xmlns:ex="http://example.test/typed" '
            'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" '
            f'xmlns:{type_prefix}="{type_namespace}"',
        ).replace(
            '<ex:identifier code="A"> Alpha </ex:identifier>',
            f'<ex:identifier code="A" xsi:type="{type_prefix}:IdentifierType" '
            f'guard="{guard}"> Alpha </ex:identifier>',
        )
        path = tmp_path / name
        path.write_text(xml)
        return path

    baseline_path = typed_variant("type-a.xml", type_prefix="typeA", type_namespace="urn:typed:type")
    prefix_equivalent_path = typed_variant(
        "type-b.xml", type_prefix="typeB", type_namespace="urn:typed:type",
    )
    namespace_different_path = typed_variant(
        "type-other-ns.xml", type_prefix="typeA", type_namespace="urn:typed:other",
    )
    non_qname_colon_path = typed_variant(
        "guard-changed.xml", type_prefix="typeA", type_namespace="urn:typed:type",
        guard="other:colon",
    )

    def typed_hash(path: Path) -> str | None:
        report = parse_instance(
            path, accession="0000000001-24-000001", dts_manifest_sha256="a" * 64,
        )
        return report.contexts["typed"].dimensions[0].typed_member_sha256

    baseline_hash = typed_hash(baseline_path)
    assert typed_hash(prefix_equivalent_path) == baseline_hash
    assert typed_hash(namespace_different_path) != baseline_hash
    # A colon does not by itself make an arbitrary attribute QName-valued.
    assert typed_hash(non_qname_colon_path) != baseline_hash
    assert typed_hash(baseline_path) == baseline_hash


def test_qname_resolution_uses_each_elements_in_scope_namespace_bindings(tmp_path: Path) -> None:
    instance = tmp_path / "rebound-prefixes.xml"
    instance.write_text(
        '''<xbrli:xbrl xmlns:xbrli="http://www.xbrl.org/2003/instance"
             xmlns:xbrldi="http://xbrl.org/2006/xbrldi" xmlns:ex="urn:facts">
          <xbrli:context id="a">
            <xbrli:entity><xbrli:identifier scheme="test">entity</xbrli:identifier>
              <xbrli:segment xmlns:q="urn:dimension:a">
                <xbrldi:explicitMember dimension="q:Axis">q:Member</xbrldi:explicitMember>
              </xbrli:segment>
            </xbrli:entity>
            <xbrli:period><xbrli:instant>2024-12-31</xbrli:instant></xbrli:period>
          </xbrli:context>
          <xbrli:context id="b">
            <xbrli:entity><xbrli:identifier scheme="test">entity</xbrli:identifier>
              <xbrli:segment xmlns:q="urn:dimension:b">
                <xbrldi:explicitMember dimension="q:Axis">q:Member</xbrldi:explicitMember>
              </xbrli:segment>
            </xbrli:entity>
            <xbrli:period><xbrli:instant>2024-12-31</xbrli:instant></xbrli:period>
          </xbrli:context>
          <xbrli:unit id="ua"><xbrli:measure xmlns:q="urn:unit:a">q:Measure</xbrli:measure></xbrli:unit>
          <xbrli:unit id="ub"><xbrli:measure xmlns:q="urn:unit:b">q:Measure</xbrli:measure></xbrli:unit>
          <ex:Amount contextRef="a" unitRef="ua">1</ex:Amount>
          <ex:Amount contextRef="b" unitRef="ub">2</ex:Amount>
        </xbrli:xbrl>'''
    )

    report = parse_instance(
        instance, accession="0000000001-24-000001", dts_manifest_sha256="a" * 64,
    )

    dimension_a = report.contexts["a"].dimensions[0]
    dimension_b = report.contexts["b"].dimensions[0]
    assert (dimension_a.axis, dimension_a.member) == (
        "{urn:dimension:a}Axis", "{urn:dimension:a}Member",
    )
    assert (dimension_b.axis, dimension_b.member) == (
        "{urn:dimension:b}Axis", "{urn:dimension:b}Member",
    )
    assert report.units["ua"].numerator == ("{urn:unit:a}Measure",)
    assert report.units["ub"].numerator == ("{urn:unit:b}Measure",)


def test_nested_xsi_type_qnames_rebind_same_prefix_restore_ancestor_and_replay(
    tmp_path: Path,
) -> None:
    def write_variant(name: str, *, prefix: str, inner_namespace: str) -> Path:
        path = tmp_path / name
        path.write_text(
            f'''<xbrli:xbrl xmlns:xbrli="http://www.xbrl.org/2003/instance"
                 xmlns:xbrldi="http://xbrl.org/2006/xbrldi" xmlns:ex="urn:typed"
                 xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
              <xbrli:context id="typed">
                <xbrli:entity><xbrli:identifier scheme="test">entity</xbrli:identifier>
                  <xbrli:segment><xbrldi:typedMember dimension="ex:Axis">
                    <ex:value xmlns:{prefix}="urn:type:outer" xsi:type="{prefix}:OuterType">
                      <ex:nested xmlns:{prefix}="{inner_namespace}"
                        xsi:type="{prefix}:InnerType">content</ex:nested>
                      <ex:restored xsi:type="{prefix}:RestoredType">after</ex:restored>
                    </ex:value>
                  </xbrldi:typedMember></xbrli:segment>
                </xbrli:entity>
                <xbrli:period><xbrli:instant>2024-12-31</xbrli:instant></xbrli:period>
              </xbrli:context>
              <ex:Amount contextRef="typed">1</ex:Amount>
            </xbrli:xbrl>'''
        )
        return path

    type_a = write_variant("type-a.xml", prefix="q", inner_namespace="urn:type:inner")
    alias_equivalent = write_variant(
        "type-alias.xml", prefix="alias", inner_namespace="urn:type:inner",
    )
    other_namespace = write_variant(
        "type-other.xml", prefix="q", inner_namespace="urn:type:other",
    )
    source_before = type_a.read_bytes()

    def parse(path: Path):
        return parse_instance(
            path, accession="0000000001-24-000001", dts_manifest_sha256="a" * 64,
        )

    baseline = parse(type_a)
    replay = parse(type_a)
    equivalent = parse(alias_equivalent)
    changed = parse(other_namespace)
    baseline_context = baseline.contexts["typed"]
    baseline_dimension = baseline_context.dimensions[0]
    canonical = baseline_dimension.typed_member_canonical_xml

    assert canonical is not None
    assert "{urn:type:outer}OuterType" in canonical
    assert "{urn:type:inner}InnerType" in canonical
    # The sibling after the nested rebinding sees the restored ancestor binding.
    assert "{urn:type:outer}RestoredType" in canonical
    assert type_a.read_bytes() == source_before

    def deterministic_output(report):
        return (
            report.contexts["typed"].dimensions[0].typed_member_canonical_xml,
            report.contexts["typed"].semantic_hash,
            tuple((key, slot.status,
                   tuple(item.occurrence_sha256 for item in slot.occurrences))
                  for key, slot in sorted(report.slots.items())),
            report.parser_output_sha256,
            report.computed_parser_output_sha256,
        )

    assert deterministic_output(replay) == deterministic_output(baseline)
    assert deterministic_output(equivalent) == deterministic_output(baseline)
    assert changed.contexts["typed"].dimensions[0].typed_member_canonical_xml != canonical
    assert changed.contexts["typed"].semantic_hash != baseline_context.semantic_hash
    assert set(changed.slots) != set(baseline.slots)
    assert changed.parser_output_sha256 != baseline.parser_output_sha256
    assert baseline.parser_output_sha256 == baseline.computed_parser_output_sha256


def test_extension_schema_qnames_use_each_declarations_element_scope(tmp_path: Path) -> None:
    def write_schema(name: str, *, local_prefix: str) -> Path:
        path = tmp_path / name
        path.write_text(
            f'''<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
                 xmlns:q="urn:root" targetNamespace="urn:extension">
              <xs:element name="LocallyRebound" xmlns:{local_prefix}="urn:local"
                type="{local_prefix}:LocalType"
                substitutionGroup="{local_prefix}:LocalItem"/>
              <xs:element name="AncestorRestored" type="q:RootType"
                substitutionGroup="q:RootItem"/>
            </xs:schema>'''
        )
        return path

    schema = write_schema("schema-q.xsd", local_prefix="q")
    alias_schema = write_schema("schema-alias.xsd", local_prefix="alias")
    declarations = parse_extension_schema(schema)
    alias_declarations = parse_extension_schema(alias_schema)

    assert [(item["local_name"], item["data_type_qname"],
             item["substitution_group_qname"]) for item in declarations] == [
        ("LocallyRebound", "{urn:local}LocalType", "{urn:local}LocalItem"),
        ("AncestorRestored", "{urn:root}RootType", "{urn:root}RootItem"),
    ]
    # Declaration identity is semantic for the QName-valued attributes too.
    assert [item["declaration_sha256"] for item in alias_declarations] == [
        item["declaration_sha256"] for item in declarations
    ]


def test_protected_manifest_and_authoritative_counts_and_changes() -> None:
    if not PROTECTED.exists():
        pytest.skip("protected fixture unavailable (never treated as pass)")
    manifest = PROTECTED / "derived" / "evidence-inventory.json"
    verified = validate_protected_manifest(PROTECTED, manifest)
    assert verified.filing_chain_count == 17 and verified.filing_document_count == 14
    original = parse_instance(PROTECTED / "original/gato-20211231x10k_htm.xml", accession="0001104659-23-034448", dts_manifest_sha256="0" * 64)
    amendment = parse_instance(PROTECTED / "amendment/gato-20211231x10ka_htm.xml", accession="0001104659-23-074911", dts_manifest_sha256="1" * 64)
    assert len(parse_extension_schema(PROTECTED / "original/gato-20211231.xsd")) == 119
    assert len(parse_extension_schema(PROTECTED / "amendment/gato-20211231.xsd")) == 127
    with pytest.raises(ParserInvariantError, match="explicit equivalence"):
        compare_filings(original, amendment)
    assert (original.metrics["context_count"], original.metrics["unit_count"], original.metrics["fact_count"], original.metrics["semantic_slot_count"]) == (182, 8, 737, 714)
    assert (amendment.metrics["context_count"], amendment.metrics["unit_count"], amendment.metrics["fact_count"], amendment.metrics["semantic_slot_count"]) == (200, 8, 831, 771)
    comparison = compare_filings(original, amendment, allow_qname_correspondence=True)
    assert (comparison.common_slots, comparison.original_only, comparison.amendment_only, comparison.changed_common) == (703, 11, 68, 102)
    assert comparison.representative_changes["Assets"] == ("367111000", "345248000")
    assert comparison.representative_changes["EarningsPerShareDiluted"] == ("-0.68", "-1.03")
    assert comparison.representative_changes["ImpairmentOfInvestmentInAffiliates"] == ("51564000", "80348000")
    assert comparison.representative_changes["AmendmentFlag"] == ("false", "true")


def test_manifest_fails_on_n_plus_one_byte_change(tmp_path: Path) -> None:
    root = tmp_path / "fixture"
    root.mkdir()
    payload = root / "evidence.xml"
    payload.write_bytes(b"one")
    manifest = root / "manifest.json"
    manifest.write_text('{"records":[{"path":"evidence.xml","bytes":3,"sha256":"7692c3ad3540bb803c020b3aee66cd8887123234ea0c6e7143c0add73ff431ed","category":"filing_chain","role":"sec_rendered_xbrl_instance"}]}')
    validate_protected_manifest(root, manifest)
    payload.write_bytes(b"ond")
    with pytest.raises(ManifestError, match="sha256"):
        validate_protected_manifest(root, manifest)
