from __future__ import annotations

import hashlib
from pathlib import Path

from macroforge.contract_drift import validate_observed_package_contract
from macroforge.imf_mfs_ir import build_imf_mfs_ir_observed_package, normalize_imf_mfs_ir_fixture
from macroforge.observed_ingestion import canonical_attribute_hash, compare_observed_packages, observed_package_fingerprint

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_FIXTURE = PROJECT_ROOT / "data" / "raw" / "imf_mfs_ir" / "imf-mfs-ir-usa-jpn-mfs166-2024m01-2024m03-raw.xml"
METADATA_FIXTURE = PROJECT_ROOT / "data" / "raw" / "imf_mfs_ir" / "imf-mfs-ir-dataflow-references-20260630.xml"
SOURCE_URLS = (
    "https://api.imf.org/external/sdmx/2.1/data/MFS_IR/USA+JPN.MFS166_RT_PT_A_PT.M?startPeriod=2024-01&endPeriod=2024-03",
)
METADATA_URL = "https://api.imf.org/external/sdmx/2.1/dataflow/all/MFS_IR/latest?references=all"
CONTENT_TYPE = "application/xml"

SAMPLE_XML = b'''<?xml version="1.0" encoding="UTF-8"?>
<message:StructureSpecificData
  xmlns:ss="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/structurespecific"
  xmlns:message="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message"
  xmlns:common="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/common"
  xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <message:Header>
    <message:ID>task-056-test-message</message:ID>
    <message:Test>false</message:Test>
    <message:Prepared>2026-06-30T07:22:59Z</message:Prepared>
    <message:Sender id="iData"/>
    <message:Structure structureID="IMF.STA_MFS_IR_9_0_0" dimensionAtObservation="TIME_PERIOD">
      <common:StructureUsage>
        <Ref agencyID="IMF.STA" id="MFS_IR" version="9.0.0"/>
      </common:StructureUsage>
    </message:Structure>
    <message:DataSetAction>Replace</message:DataSetAction>
  </message:Header>
  <message:DataSet ss:dataScope="DataStructure" ss:structureRef="IMF.STA_MFS_IR_9_0_0" action="Replace" LANGUAGE="EN" PUBLISHER="IMF" UPDATE_DATE="2026-06-30T02:38:30.045945Z" PUBLICATION_DATE="2026-06-30T02:38:30.002910100Z" CONTACT_POINT="datahelp@imf.org" DEPARTMENT="STA" TOPIC_DATASET="G00">
    <Series COUNTRY="USA" INDICATOR="MFS166_RT_PT_A_PT" FREQUENCY="M" IFS_FLAG="true" OVERLAP="OL" SCALE="0" ACCESS_SHARING_LEVEL="PUBLIC_OPEN" SECURITY_CLASSIFICATION="PUB">
      <Obs TIME_PERIOD="2024-M01" OBS_VALUE="5.375" DERIVATION_TYPE="O"/>
      <Obs TIME_PERIOD="2024-M02" OBS_VALUE="5.375" DERIVATION_TYPE="O"/>
      <Obs TIME_PERIOD="2024-M03" OBS_VALUE="5.375" DERIVATION_TYPE="O"/>
    </Series>
    <Series COUNTRY="JPN" INDICATOR="MFS166_RT_PT_A_PT" FREQUENCY="M" IFS_FLAG="true" OVERLAP="OL" SCALE="0" ACCESS_SHARING_LEVEL="PUBLIC_OPEN" SECURITY_CLASSIFICATION="PUB">
      <Obs TIME_PERIOD="2024-M01" OBS_VALUE="-0.1" DERIVATION_TYPE="O"/>
      <Obs TIME_PERIOD="2024-M02" OBS_VALUE="-0.1" DERIVATION_TYPE="O"/>
      <Obs TIME_PERIOD="2024-M03" OBS_VALUE="0.05" DERIVATION_TYPE="O"/>
    </Series>
  </message:DataSet>
</message:StructureSpecificData>
'''

SAMPLE_METADATA_XML = b'''<?xml version="1.0" encoding="UTF-8"?>
<mes:Structure
  xmlns:mes="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message"
  xmlns:str="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/structure"
  xmlns:com="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/common"
  xmlns:xml="http://www.w3.org/XML/1998/namespace">
  <mes:Structures>
    <str:Dataflows>
      <str:Dataflow agencyID="IMF.STA" id="MFS_IR" version="9.0.0" isFinal="true">
        <com:Name xml:lang="en">Monetary and Financial Statistics (MFS), Interest Rate</com:Name>
      </str:Dataflow>
    </str:Dataflows>
    <str:DataStructures>
      <str:DataStructure agencyID="IMF.STA" id="DSD_MFS_IR" version="9.0.0" isFinal="true">
        <str:DataStructureComponents>
          <str:DimensionList>
            <str:Dimension id="COUNTRY" position="0"/>
            <str:Dimension id="INDICATOR" position="1"/>
            <str:Dimension id="FREQUENCY" position="2"/>
            <str:TimeDimension id="TIME_PERIOD"/>
          </str:DimensionList>
        </str:DataStructureComponents>
      </str:DataStructure>
    </str:DataStructures>
    <str:Codelists>
      <str:Codelist id="CL_MFS_COUNTRY"><str:Code id="USA"><com:Name xml:lang="en">United States</com:Name></str:Code><str:Code id="JPN"><com:Name xml:lang="en">Japan</com:Name></str:Code></str:Codelist>
      <str:Codelist id="CL_MFS_IR_INDICATOR"><str:Code id="MFS166_RT_PT_A_PT"><com:Name xml:lang="en">Central bank policy rate</com:Name></str:Code></str:Codelist>
      <str:Codelist id="CL_FREQ"><str:Code id="M"><com:Name xml:lang="en">Monthly</com:Name></str:Code></str:Codelist>
    </str:Codelists>
  </mes:Structures>
</mes:Structure>
'''


def _normalized_from_sample() -> dict:
    return normalize_imf_mfs_ir_fixture(
        SAMPLE_XML,
        metadata_payload=SAMPLE_METADATA_XML,
        raw_artifact_path="data/raw/imf_mfs_ir/imf-mfs-ir-usa-jpn-mfs166-2024m01-2024m03-raw.xml",
        raw_sha256=hashlib.sha256(SAMPLE_XML).hexdigest(),
        metadata_artifact_path="data/raw/imf_mfs_ir/imf-mfs-ir-dataflow-references-20260630.xml",
        metadata_sha256=hashlib.sha256(SAMPLE_METADATA_XML).hexdigest(),
        source_urls=SOURCE_URLS,
        metadata_url=METADATA_URL,
        content_type=CONTENT_TYPE,
    )


def test_imf_mfs_ir_fixture_normalizes_source_specific_structure_specific_sdmx_metadata_without_sdmx_layer():
    normalized = _normalized_from_sample()

    assert normalized["source_code"] == "IMF_MFS_IR"
    assert normalized["provider_dataset_code"] == "MFS_IR"
    assert normalized["dataflow_code"] == "MFS_IR"
    assert normalized["dataflow_version"] == "9.0.0"
    assert normalized["frequency"] == "M"
    assert normalized["period_range"] == "2024-M01-2024-M03"
    assert normalized["row_count"] == 6
    assert normalized["expected_row_count"] == 6
    assert normalized["input_filters"] == {
        "dataflow": "MFS_IR",
        "countries": ["USA", "JPN"],
        "indicator": "MFS166_RT_PT_A_PT",
        "frequency": "M",
        "startPeriod": "2024-01",
        "endPeriod": "2024-03",
        "scope": "bounded TASK-056 IMF MFS_IR architectural evidence slice",
    }
    assert normalized["provider_metadata"] == {
        "message_id": "task-056-test-message",
        "prepared": "2026-06-30T07:22:59Z",
        "sender": "iData",
        "structure_id": "IMF.STA_MFS_IR_9_0_0",
        "dataset_action": "Replace",
        "dataset_attributes": {
            "LANGUAGE": "EN",
            "PUBLISHER": "IMF",
            "UPDATE_DATE": "2026-06-30T02:38:30.045945Z",
            "PUBLICATION_DATE": "2026-06-30T02:38:30.002910100Z",
            "CONTACT_POINT": "datahelp@imf.org",
            "DEPARTMENT": "STA",
            "TOPIC_DATASET": "G00",
        },
        "dimension_at_observation": "TIME_PERIOD",
        "dataflow": {
            "agency_id": "IMF.STA",
            "id": "MFS_IR",
            "version": "9.0.0",
            "name": "Monetary and Financial Statistics (MFS), Interest Rate",
        },
        "data_structure": {"agency_id": "IMF.STA", "id": "DSD_MFS_IR", "version": "9.0.0"},
        "dimension_order": ["COUNTRY", "INDICATOR", "FREQUENCY", "TIME_PERIOD"],
        "codelists": {
            "CL_MFS_COUNTRY": {"USA": "United States", "JPN": "Japan"},
            "CL_MFS_IR_INDICATOR": {"MFS166_RT_PT_A_PT": "Central bank policy rate"},
            "CL_FREQ": {"M": "Monthly"},
        },
    }

    expected_values = {
        ("USA", "2024-M01"): 5.375,
        ("USA", "2024-M02"): 5.375,
        ("USA", "2024-M03"): 5.375,
        ("JPN", "2024-M01"): -0.1,
        ("JPN", "2024-M02"): -0.1,
        ("JPN", "2024-M03"): 0.05,
    }
    assert {(row["territory_code"], row["provider_period_code"]): row["value"] for row in normalized["rows"]} == expected_values
    first = normalized["rows"][0]
    assert first["provider_indicator_code"] == "MFS166_RT_PT_A_PT"
    assert first["provider_indicator_label"] == "Central bank policy rate"
    assert first["territory_code"] == "JPN"
    assert first["territory_label"] == "Japan"
    assert first["unit_code"] == "PERCENT"
    assert first["unit_label"] == "Percent"
    assert first["attributes"]["derivation_type"] == "O"
    assert first["attributes"]["series_key"] == "JPN.MFS166_RT_PT_A_PT.M"
    assert first["source_payload"]["series_attributes"]["ACCESS_SHARING_LEVEL"] == "PUBLIC_OPEN"
    assert first["source_payload"]["obs_attributes"] == {"TIME_PERIOD": "2024-M01", "OBS_VALUE": "-0.1", "DERIVATION_TYPE": "O"}


def test_imf_mfs_ir_observed_package_satisfies_existing_contract_without_contract_evolution():
    package = build_imf_mfs_ir_observed_package(_normalized_from_sample())

    assert package.source_code == "IMF_MFS_IR"
    assert package.source_name == "International Monetary Fund bounded MFS_IR interest-rate SDMX evidence slice"
    assert package.source_home_url == "https://www.imf.org/"
    assert package.provider_dataset_code == "MFS_IR"
    assert package.release_key.startswith("IMF_MFS_IR:MFS_IR:2024-M01-2024-M03:")
    assert package.row_count == 6
    assert package.expected_row_count == 6
    assert package.input_filters == _normalized_from_sample()["input_filters"]
    assert package.raw_evidence["source_urls"] == list(SOURCE_URLS)
    assert package.raw_evidence["metadata_url"] == METADATA_URL
    assert package.raw_evidence["raw_artifact_path"] == "data/raw/imf_mfs_ir/imf-mfs-ir-usa-jpn-mfs166-2024m01-2024m03-raw.xml"
    assert package.raw_evidence["metadata_artifact_path"] == "data/raw/imf_mfs_ir/imf-mfs-ir-dataflow-references-20260630.xml"
    assert len(package.raw_evidence["raw_sha256"]) == 64
    assert len(package.raw_evidence["metadata_sha256"]) == 64
    assert package.raw_evidence["provider_metadata"] == _normalized_from_sample()["provider_metadata"]

    observation = package.observations[0]
    assert observation.provider_indicator_code == "MFS166_RT_PT_A_PT"
    assert observation.provider_indicator_label == "Central bank policy rate"
    assert observation.provider_territory_code == "JPN"
    assert observation.provider_territory_label == "Japan"
    assert observation.provider_period_code == "2024-M01"
    assert observation.frequency == "M"
    assert observation.period_year == 2024
    assert observation.period_quarter is None
    assert observation.period_month == 1
    assert observation.unit_code == "PERCENT"
    assert observation.unit_label == "Percent"
    assert observation.value == -0.1
    assert observation.observation_status == "observed"
    assert observation.decimal_precision == 1
    assert observation.attribute_hash == canonical_attribute_hash(observation.attributes)

    report = validate_observed_package_contract(package)
    assert report.valid is True
    assert report.issues == ()


def test_imf_mfs_ir_observed_package_replay_is_deterministic():
    package = build_imf_mfs_ir_observed_package(_normalized_from_sample())
    replayed = build_imf_mfs_ir_observed_package(_normalized_from_sample())

    comparison = compare_observed_packages(package, replayed)

    assert comparison.equivalent is True
    assert comparison.left_fingerprint == comparison.right_fingerprint
    assert comparison.row_count_match is True
    assert comparison.expected_row_count_match is True
    assert comparison.observation_count_match is True
    assert comparison.differing_observations == ()
    assert len(observed_package_fingerprint(package)) == 64


def test_imf_mfs_ir_module_remains_bounded_source_specific_not_sdmx_or_imf_framework():
    source = (PROJECT_ROOT / "src" / "macroforge" / "imf_mfs_ir.py").read_text(encoding="utf-8")

    forbidden = [
        "class SdmxInterpretationLayer",
        "class GenericSdmxAdapter",
        "class ImfClient",
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


def test_project_imf_mfs_ir_fixture_preserves_live_bounded_evidence_when_present():
    if not RAW_FIXTURE.exists() or not METADATA_FIXTURE.exists():
        return

    raw_payload = RAW_FIXTURE.read_bytes()
    metadata_payload = METADATA_FIXTURE.read_bytes()
    normalized = normalize_imf_mfs_ir_fixture(
        raw_payload,
        metadata_payload=metadata_payload,
        raw_artifact_path=str(RAW_FIXTURE.relative_to(PROJECT_ROOT)),
        raw_sha256=hashlib.sha256(raw_payload).hexdigest(),
        metadata_artifact_path=str(METADATA_FIXTURE.relative_to(PROJECT_ROOT)),
        metadata_sha256=hashlib.sha256(metadata_payload).hexdigest(),
        source_urls=SOURCE_URLS,
        metadata_url=METADATA_URL,
        content_type=CONTENT_TYPE,
    )

    assert normalized["provider_dataset_code"] == "MFS_IR"
    assert normalized["dataflow_version"] == "9.0.0"
    assert normalized["row_count"] == 6
    assert {row["territory_code"] for row in normalized["rows"]} == {"USA", "JPN"}
    assert {row["provider_period_code"] for row in normalized["rows"]} == {"2024-M01", "2024-M02", "2024-M03"}
    assert validate_observed_package_contract(build_imf_mfs_ir_observed_package(normalized)).valid is True
