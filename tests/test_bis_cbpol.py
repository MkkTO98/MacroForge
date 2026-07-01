from __future__ import annotations

import hashlib
from pathlib import Path

from macroforge.bis_cbpol import build_bis_cbpol_observed_package, normalize_bis_cbpol_fixture
from macroforge.contract_drift import validate_observed_package_contract
from macroforge.observed_ingestion import canonical_attribute_hash, compare_observed_packages, observed_package_fingerprint

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_FIXTURE = PROJECT_ROOT / "data" / "raw" / "bis_cbpol" / "bis-cbpol-us-jp-2024m01-2024m03-raw.xml"
SOURCE_URL = "https://stats.bis.org/api/v2/data/dataflow/BIS/WS_CBPOL/1.0/M.US+JP?startPeriod=2024-01&endPeriod=2024-03"
CONTENT_TYPE = "application/xml"

SAMPLE_XML = b'''<?xml version="1.0" encoding="UTF-8"?>
<message:StructureSpecificData
  xmlns:ss="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/structurespecific"
  xmlns:message="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message"
  xmlns:common="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/common">
  <message:Header>
    <message:ID>IDREF-test-bis-cbpol</message:ID>
    <message:Test>false</message:Test>
    <message:Prepared>2026-06-30T08:00:00Z</message:Prepared>
    <message:Sender id="BIS"/>
    <message:Structure structureID="BIS_WS_CBPOL_1_0" namespace="urn:sdmx:org.sdmx.infomodel.datastructure.Dataflow=BIS:WS_CBPOL(1.0):ObsLevelDim:TIME_PERIOD" dimensionAtObservation="TIME_PERIOD">
      <common:StructureUsage>
        <Ref agencyID="BIS" id="WS_CBPOL" version="1.0"/>
      </common:StructureUsage>
    </message:Structure>
    <message:DataSetAction>Replace</message:DataSetAction>
  </message:Header>
  <message:DataSet UNIT_MULT="0" UNIT_MEASURE="368" ss:dataScope="DataStructure" ss:structureRef="BIS_WS_CBPOL_1_0">
    <Series FREQ="M" REF_AREA="JP" SOURCE_REF="Bank of Japan" COMPILATION="From 21 Sep 2016 to 20 Mar 2024: short-term policy interest rate at minus 0.1%; from 21 Mar 2024 to 31 July: around 0 to 0.1 %." DECIMALS="4" TITLE=" Central bank policy rates - Japan - Monthly - End of period">
      <Obs TIME_PERIOD="2024-01" OBS_VALUE="-0.1" OBS_STATUS="A" OBS_CONF="F"/>
      <Obs TIME_PERIOD="2024-02" OBS_VALUE="-0.1" OBS_STATUS="A" OBS_CONF="F"/>
      <Obs TIME_PERIOD="2024-03" OBS_VALUE="0.05" OBS_STATUS="A" OBS_CONF="F"/>
    </Series>
    <Series FREQ="M" REF_AREA="US" SOURCE_REF="US Federal Reserve System" COMPILATION="From 19 Dec 1985 onwards: mid-point of the Federal Reserve target rate." DECIMALS="4" TITLE=" Central bank policy rates - United States - Monthly - End of period">
      <Obs TIME_PERIOD="2024-01" OBS_VALUE="5.375" OBS_STATUS="A" OBS_CONF="F"/>
      <Obs TIME_PERIOD="2024-02" OBS_VALUE="5.375" OBS_STATUS="A" OBS_CONF="F"/>
      <Obs TIME_PERIOD="2024-03" OBS_VALUE="5.375" OBS_STATUS="A" OBS_CONF="F"/>
    </Series>
  </message:DataSet>
</message:StructureSpecificData>
'''


def _normalized_from_sample() -> dict:
    return normalize_bis_cbpol_fixture(
        SAMPLE_XML,
        raw_artifact_path="data/raw/bis_cbpol/bis-cbpol-us-jp-2024m01-2024m03-raw.xml",
        raw_sha256=hashlib.sha256(SAMPLE_XML).hexdigest(),
        source_url=SOURCE_URL,
        content_type=CONTENT_TYPE,
    )


def test_bis_cbpol_fixture_normalizes_structure_specific_policy_rate_metadata_without_sdmx_layer():
    normalized = _normalized_from_sample()

    assert normalized["source_code"] == "BIS_CBPOL"
    assert normalized["provider_dataset_code"] == "BIS:WS_CBPOL"
    assert normalized["dataflow_code"] == "WS_CBPOL"
    assert normalized["dataflow_version"] == "1.0"
    assert normalized["frequency"] == "M"
    assert normalized["period_range"] == "2024-M01-2024-M03"
    assert normalized["row_count"] == 6
    assert normalized["expected_row_count"] == 6
    assert normalized["input_filters"] == {
        "dataflow": "WS_CBPOL",
        "reference_areas": ["US", "JP"],
        "frequency": "M",
        "startPeriod": "2024-01",
        "endPeriod": "2024-03",
        "scope": "bounded TASK-057 BIS WS_CBPOL architectural evidence slice",
    }
    assert normalized["provider_metadata"] == {
        "message_id": "IDREF-test-bis-cbpol",
        "prepared": "2026-06-30T08:00:00Z",
        "sender": "BIS",
        "structure_id": "BIS_WS_CBPOL_1_0",
        "structure_namespace": "urn:sdmx:org.sdmx.infomodel.datastructure.Dataflow=BIS:WS_CBPOL(1.0):ObsLevelDim:TIME_PERIOD",
        "dataset_action": "Replace",
        "dataset_attributes": {"UNIT_MULT": "0", "UNIT_MEASURE": "368"},
        "dimension_at_observation": "TIME_PERIOD",
        "dataflow": {"agency_id": "BIS", "id": "WS_CBPOL", "version": "1.0"},
    }
    assert {(row["territory_code"], row["provider_period_code"]): row["value"] for row in normalized["rows"]} == {
        ("JP", "2024-M01"): -0.1,
        ("JP", "2024-M02"): -0.1,
        ("JP", "2024-M03"): 0.05,
        ("US", "2024-M01"): 5.375,
        ("US", "2024-M02"): 5.375,
        ("US", "2024-M03"): 5.375,
    }
    first = normalized["rows"][0]
    assert first["provider_indicator_code"] == "WS_CBPOL:POLICY_RATE"
    assert first["provider_indicator_label"] == "Central bank policy rates"
    assert first["territory_code"] == "JP"
    assert first["territory_label"] == "Japan"
    assert first["unit_code"] == "PERCENT"
    assert first["unit_label"] == "Percent"
    assert first["attributes"]["obs_status"] == "A"
    assert first["attributes"]["obs_conf"] == "F"
    assert first["attributes"]["series_key"] == "M.JP"
    assert first["source_payload"]["series_attributes"]["SOURCE_REF"] == "Bank of Japan"
    assert first["source_payload"]["obs_attributes"] == {"TIME_PERIOD": "2024-01", "OBS_VALUE": "-0.1", "OBS_STATUS": "A", "OBS_CONF": "F"}


def test_bis_cbpol_observed_package_satisfies_existing_contract_without_contract_evolution():
    package = build_bis_cbpol_observed_package(_normalized_from_sample())

    assert package.source_code == "BIS_CBPOL"
    assert package.source_name == "Bank for International Settlements bounded central bank policy rates SDMX evidence slice"
    assert package.source_home_url == "https://www.bis.org/"
    assert package.provider_dataset_code == "BIS:WS_CBPOL"
    assert package.release_key.startswith("BIS_CBPOL:WS_CBPOL:2024-M01-2024-M03:")
    assert package.row_count == 6
    assert package.expected_row_count == 6
    assert package.input_filters == _normalized_from_sample()["input_filters"]
    assert package.raw_evidence["source_url"] == SOURCE_URL
    assert package.raw_evidence["raw_artifact_path"] == "data/raw/bis_cbpol/bis-cbpol-us-jp-2024m01-2024m03-raw.xml"
    assert len(package.raw_evidence["raw_sha256"]) == 64
    assert package.raw_evidence["provider_metadata"] == _normalized_from_sample()["provider_metadata"]

    observation = package.observations[0]
    assert observation.provider_indicator_code == "WS_CBPOL:POLICY_RATE"
    assert observation.provider_indicator_label == "Central bank policy rates"
    assert observation.provider_territory_code == "JP"
    assert observation.provider_territory_label == "Japan"
    assert observation.provider_period_code == "2024-M01"
    assert observation.frequency == "M"
    assert observation.period_year == 2024
    assert observation.period_month == 1
    assert observation.unit_code == "PERCENT"
    assert observation.value == -0.1
    assert observation.observation_status == "observed"
    assert observation.decimal_precision == 1
    assert observation.attribute_hash == canonical_attribute_hash(observation.attributes)

    report = validate_observed_package_contract(package)
    assert report.valid is True
    assert report.issues == ()


def test_bis_cbpol_observed_package_replay_is_deterministic():
    package = build_bis_cbpol_observed_package(_normalized_from_sample())
    replayed = build_bis_cbpol_observed_package(_normalized_from_sample())

    comparison = compare_observed_packages(package, replayed)

    assert comparison.equivalent is True
    assert comparison.left_fingerprint == comparison.right_fingerprint
    assert comparison.row_count_match is True
    assert comparison.expected_row_count_match is True
    assert comparison.observation_count_match is True
    assert comparison.differing_observations == ()
    assert len(observed_package_fingerprint(package)) == 64


def test_bis_cbpol_module_remains_bounded_source_specific_not_sdmx_or_bis_framework():
    source = (PROJECT_ROOT / "src" / "macroforge" / "bis_cbpol.py").read_text(encoding="utf-8")

    forbidden = [
        "class SdmxInterpretationLayer",
        "class GenericSdmxAdapter",
        "class BisClient",
        "class BaseSource",
        "class SourcePlugin",
        "PluginRegistry",
        "staging.sdmx",
        "CREATE TABLE",
        "INSERT INTO",
        "requests.get",
        "urllib.request",
        "sqlalchemy",
    ]
    for token in forbidden:
        assert token not in source


def test_project_bis_cbpol_fixture_preserves_live_bounded_evidence_when_present():
    if not RAW_FIXTURE.exists():
        return

    raw_payload = RAW_FIXTURE.read_bytes()
    normalized = normalize_bis_cbpol_fixture(
        raw_payload,
        raw_artifact_path=str(RAW_FIXTURE.relative_to(PROJECT_ROOT)),
        raw_sha256=hashlib.sha256(raw_payload).hexdigest(),
        source_url=SOURCE_URL,
        content_type=CONTENT_TYPE,
    )
    package = build_bis_cbpol_observed_package(normalized)

    assert normalized["row_count"] == 6
    assert package.row_count == 6
    assert package.observations[0].provider_territory_code == "JP"
    assert package.observations[-1].provider_territory_code == "US"
    assert observed_package_fingerprint(package) == observed_package_fingerprint(build_bis_cbpol_observed_package(normalized))
