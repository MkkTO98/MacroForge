from __future__ import annotations

import hashlib
from pathlib import Path

from macroforge.contract_drift import validate_observed_package_contract
from macroforge.imf_bop_financial_account import (
    build_imf_bop_financial_account_observed_package,
    normalize_imf_bop_financial_account_fixture,
)
from macroforge.observed_ingestion import canonical_attribute_hash, compare_observed_packages, observed_package_fingerprint

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_FIXTURE = PROJECT_ROOT / "data" / "raw" / "imf_bop_financial_account" / "imf-bop-financial-account-usa-jpn-2022-2023.xml"
METADATA_FIXTURE = PROJECT_ROOT / "data" / "raw" / "imf_bop_financial_account" / "imf-bop-dataflow-references-20260701.xml"
SOURCE_URLS = (
    "https://api.imf.org/external/sdmx/2.1/data/BOP/USA+JPN.A_NFA_T+L_NIL_T.D_F+P_F.USD.A?startPeriod=2022&endPeriod=2023",
)
METADATA_URL = "https://api.imf.org/external/sdmx/2.1/dataflow/all/BOP/latest?references=all"
CONTENT_TYPE = "application/xml"

SAMPLE_XML = b'''<?xml version="1.0" encoding="UTF-8"?>
<message:StructureSpecificData
  xmlns:ss="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/structurespecific"
  xmlns:message="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message"
  xmlns:common="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/common">
  <message:Header>
    <message:ID>task-063-test-message</message:ID>
    <message:Test>false</message:Test>
    <message:Prepared>2026-07-01T05:36:06Z</message:Prepared>
    <message:Sender id="iData"/>
    <message:Structure structureID="IMF.STA_BOP_21_0_0" dimensionAtObservation="TIME_PERIOD">
      <common:StructureUsage><Ref agencyID="IMF.STA" id="BOP" version="21.0.0"/></common:StructureUsage>
    </message:Structure>
    <message:DataSetAction>Replace</message:DataSetAction>
  </message:Header>
  <message:DataSet ss:dataScope="DataStructure" ss:structureRef="IMF.STA_BOP_21_0_0" action="Replace" LANGUAGE="EN" PUBLISHER="IMF" UPDATE_DATE="2026-06-30T20:39:05.245380300Z" PUBLICATION_DATE="2026-06-30T20:39:05.198174500Z" CONTACT_POINT="datahelp@imf.org" DEPARTMENT="STA" TOPIC_DATASET="F32,F32_FA" SHORT_SOURCE_CITATION="Country authorities; IMF Staff Estimates" SUGGESTED_CITATION="International Monetary Fund. Balance of Payments and International Investment Position Statistics (BOP/IIP).">
    <Series COUNTRY="JPN" BOP_ACCOUNTING_ENTRY="A_NFA_T" INDICATOR="D_F" UNIT="USD" FREQUENCY="A" IFS_FLAG="true" SCALE="6" METHODOLOGY="BPM6">
      <Obs TIME_PERIOD="2022" OBS_VALUE="174943442053.1513" DERIVATION_TYPE="O" PRECISION="6" ACCESS_SHARING_LEVEL="PUBLIC_OPEN" SECURITY_CLASSIFICATION="PUB"/>
      <Obs TIME_PERIOD="2023" OBS_VALUE="197021932253.1695" DERIVATION_TYPE="O" PRECISION="6" ACCESS_SHARING_LEVEL="PUBLIC_OPEN" SECURITY_CLASSIFICATION="PUB"/>
    </Series>
    <Series COUNTRY="JPN" BOP_ACCOUNTING_ENTRY="A_NFA_T" INDICATOR="P_F" UNIT="USD" FREQUENCY="A" IFS_FLAG="true" SCALE="6" METHODOLOGY="BPM6">
      <Obs TIME_PERIOD="2022" OBS_VALUE="-174260174818.3375" DERIVATION_TYPE="O" PRECISION="6" ACCESS_SHARING_LEVEL="PUBLIC_OPEN" SECURITY_CLASSIFICATION="PUB"/>
      <Obs TIME_PERIOD="2023" OBS_VALUE="128577217467.2247" DERIVATION_TYPE="O" PRECISION="6" ACCESS_SHARING_LEVEL="PUBLIC_OPEN" SECURITY_CLASSIFICATION="PUB"/>
    </Series>
    <Series COUNTRY="JPN" BOP_ACCOUNTING_ENTRY="L_NIL_T" INDICATOR="D_F" UNIT="USD" FREQUENCY="A" SCALE="6" METHODOLOGY="BPM6">
      <Obs TIME_PERIOD="2022" OBS_VALUE="48153832744.05864" DERIVATION_TYPE="O" PRECISION="6" ACCESS_SHARING_LEVEL="PUBLIC_OPEN" SECURITY_CLASSIFICATION="PUB"/>
      <Obs TIME_PERIOD="2023" OBS_VALUE="20007989122.90426" DERIVATION_TYPE="O" PRECISION="6" ACCESS_SHARING_LEVEL="PUBLIC_OPEN" SECURITY_CLASSIFICATION="PUB"/>
    </Series>
    <Series COUNTRY="JPN" BOP_ACCOUNTING_ENTRY="L_NIL_T" INDICATOR="P_F" UNIT="USD" FREQUENCY="A" SCALE="6" METHODOLOGY="BPM6">
      <Obs TIME_PERIOD="2022" OBS_VALUE="-36385993731.04897" DERIVATION_TYPE="O" PRECISION="6" ACCESS_SHARING_LEVEL="PUBLIC_OPEN" SECURITY_CLASSIFICATION="PUB"/>
      <Obs TIME_PERIOD="2023" OBS_VALUE="-67875050304.30682" DERIVATION_TYPE="O" PRECISION="6" ACCESS_SHARING_LEVEL="PUBLIC_OPEN" SECURITY_CLASSIFICATION="PUB"/>
    </Series>
    <Series COUNTRY="USA" BOP_ACCOUNTING_ENTRY="A_NFA_T" INDICATOR="D_F" UNIT="USD" FREQUENCY="A" IFS_FLAG="true" SCALE="6" METHODOLOGY="BPM6">
      <Obs TIME_PERIOD="2022" OBS_VALUE="388847000000" DERIVATION_TYPE="O" PRECISION="6" ACCESS_SHARING_LEVEL="PUBLIC_OPEN" SECURITY_CLASSIFICATION="PUB"/>
      <Obs TIME_PERIOD="2023" OBS_VALUE="351085000000" DERIVATION_TYPE="O" PRECISION="6" ACCESS_SHARING_LEVEL="PUBLIC_OPEN" SECURITY_CLASSIFICATION="PUB"/>
    </Series>
    <Series COUNTRY="USA" BOP_ACCOUNTING_ENTRY="A_NFA_T" INDICATOR="P_F" UNIT="USD" FREQUENCY="A" IFS_FLAG="true" SCALE="6" METHODOLOGY="BPM6">
      <Obs TIME_PERIOD="2022" OBS_VALUE="322040000000" DERIVATION_TYPE="O" PRECISION="6" ACCESS_SHARING_LEVEL="PUBLIC_OPEN" SECURITY_CLASSIFICATION="PUB"/>
      <Obs TIME_PERIOD="2023" OBS_VALUE="116670000000" DERIVATION_TYPE="O" PRECISION="6" ACCESS_SHARING_LEVEL="PUBLIC_OPEN" SECURITY_CLASSIFICATION="PUB"/>
    </Series>
    <Series COUNTRY="USA" BOP_ACCOUNTING_ENTRY="L_NIL_T" INDICATOR="D_F" UNIT="USD" FREQUENCY="A" SCALE="6" METHODOLOGY="BPM6">
      <Obs TIME_PERIOD="2022" OBS_VALUE="416890000000" DERIVATION_TYPE="O" PRECISION="6" ACCESS_SHARING_LEVEL="PUBLIC_OPEN" SECURITY_CLASSIFICATION="PUB"/>
      <Obs TIME_PERIOD="2023" OBS_VALUE="361944000000" DERIVATION_TYPE="O" PRECISION="6" ACCESS_SHARING_LEVEL="PUBLIC_OPEN" SECURITY_CLASSIFICATION="PUB"/>
    </Series>
    <Series COUNTRY="USA" BOP_ACCOUNTING_ENTRY="L_NIL_T" INDICATOR="P_F" UNIT="USD" FREQUENCY="A" SCALE="6" METHODOLOGY="BPM6">
      <Obs TIME_PERIOD="2022" OBS_VALUE="760383000000" DERIVATION_TYPE="O" PRECISION="6" ACCESS_SHARING_LEVEL="PUBLIC_OPEN" SECURITY_CLASSIFICATION="PUB"/>
      <Obs TIME_PERIOD="2023" OBS_VALUE="1300772000000" DERIVATION_TYPE="O" PRECISION="6" ACCESS_SHARING_LEVEL="PUBLIC_OPEN" SECURITY_CLASSIFICATION="PUB"/>
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
      <str:Dataflow agencyID="IMF.STA" id="BOP" version="21.0.0" isFinal="true"><com:Name xml:lang="en">Balance of Payments (BOP)</com:Name></str:Dataflow>
    </str:Dataflows>
    <str:DataStructures>
      <str:DataStructure agencyID="IMF.STA" id="DSD_BOP" version="24.0.0" isFinal="true">
        <str:DataStructureComponents>
          <str:DimensionList>
            <str:Dimension id="COUNTRY" position="0"/>
            <str:Dimension id="BOP_ACCOUNTING_ENTRY" position="1"/>
            <str:Dimension id="INDICATOR" position="2"/>
            <str:Dimension id="UNIT" position="3"/>
            <str:Dimension id="FREQUENCY" position="4"/>
            <str:TimeDimension id="TIME_PERIOD"/>
          </str:DimensionList>
        </str:DataStructureComponents>
      </str:DataStructure>
    </str:DataStructures>
    <str:Codelists>
      <str:Codelist id="CL_BOP_COUNTRY"><str:Code id="USA"><com:Name xml:lang="en">United States</com:Name></str:Code><str:Code id="JPN"><com:Name xml:lang="en">Japan</com:Name></str:Code></str:Codelist>
      <str:Codelist id="CL_BOP_ACCOUNTING_ENTRY"><str:Code id="A_NFA_T"><com:Name xml:lang="en">Assets, Net acquisition of financial assets</com:Name></str:Code><str:Code id="L_NIL_T"><com:Name xml:lang="en">Liabilities, Net incurrence of liabilities</com:Name></str:Code></str:Codelist>
      <str:Codelist id="CL_BOP_INDICATOR"><str:Code id="D_F"><com:Name xml:lang="en">Direct investment, Total financial assets/liabilities</com:Name></str:Code><str:Code id="P_F"><com:Name xml:lang="en">Portfolio investment, Total financial assets/liabilities</com:Name></str:Code></str:Codelist>
      <str:Codelist id="CL_UNIT"><str:Code id="USD"><com:Name xml:lang="en">US dollar</com:Name></str:Code></str:Codelist>
      <str:Codelist id="CL_FREQ"><str:Code id="A"><com:Name xml:lang="en">Annual</com:Name></str:Code></str:Codelist>
    </str:Codelists>
  </mes:Structures>
</mes:Structure>
'''


def _normalized_from_sample() -> dict:
    return normalize_imf_bop_financial_account_fixture(
        SAMPLE_XML,
        metadata_payload=SAMPLE_METADATA_XML,
        raw_artifact_path="data/raw/imf_bop_financial_account/imf-bop-financial-account-usa-jpn-2022-2023.xml",
        raw_sha256=hashlib.sha256(SAMPLE_XML).hexdigest(),
        metadata_artifact_path="data/raw/imf_bop_financial_account/imf-bop-dataflow-references-20260701.xml",
        metadata_sha256=hashlib.sha256(SAMPLE_METADATA_XML).hexdigest(),
        source_urls=SOURCE_URLS,
        metadata_url=METADATA_URL,
        content_type=CONTENT_TYPE,
    )


def test_imf_bop_financial_account_fixture_normalizes_asset_liability_investment_flow_structure_without_bop_framework():
    normalized = _normalized_from_sample()

    assert normalized["source_code"] == "IMF_BOP_FINANCIAL_ACCOUNT"
    assert normalized["provider_dataset_code"] == "BOP"
    assert normalized["dataflow_code"] == "BOP"
    assert normalized["dataflow_version"] == "21.0.0"
    assert normalized["frequency"] == "A"
    assert normalized["period_range"] == "2022-2023"
    assert normalized["row_count"] == 16
    assert normalized["expected_row_count"] == 16
    assert normalized["input_filters"] == {
        "dataflow": "BOP",
        "countries": ["USA", "JPN"],
        "accounting_entries": ["A_NFA_T", "L_NIL_T"],
        "indicators": ["D_F", "P_F"],
        "unit": "USD",
        "frequency": "A",
        "startPeriod": "2022",
        "endPeriod": "2023",
        "scope": "bounded TASK-063 IMF BOP financial-account evidence slice",
    }
    assert normalized["provider_metadata"] == {
        "message_id": "task-063-test-message",
        "prepared": "2026-07-01T05:36:06Z",
        "sender": "iData",
        "structure_id": "IMF.STA_BOP_21_0_0",
        "dataset_action": "Replace",
        "dataset_attributes": {
            "LANGUAGE": "EN",
            "PUBLISHER": "IMF",
            "UPDATE_DATE": "2026-06-30T20:39:05.245380300Z",
            "PUBLICATION_DATE": "2026-06-30T20:39:05.198174500Z",
            "CONTACT_POINT": "datahelp@imf.org",
            "DEPARTMENT": "STA",
            "TOPIC_DATASET": "F32,F32_FA",
            "SHORT_SOURCE_CITATION": "Country authorities; IMF Staff Estimates",
            "SUGGESTED_CITATION": "International Monetary Fund. Balance of Payments and International Investment Position Statistics (BOP/IIP).",
        },
        "dimension_at_observation": "TIME_PERIOD",
        "dataflow": {"agency_id": "IMF.STA", "id": "BOP", "version": "21.0.0", "name": "Balance of Payments (BOP)"},
        "data_structure": {"agency_id": "IMF.STA", "id": "DSD_BOP", "version": "24.0.0"},
        "dimension_order": ["COUNTRY", "BOP_ACCOUNTING_ENTRY", "INDICATOR", "UNIT", "FREQUENCY", "TIME_PERIOD"],
        "codelists": {
            "CL_BOP_COUNTRY": {"USA": "United States", "JPN": "Japan"},
            "CL_BOP_ACCOUNTING_ENTRY": {
                "A_NFA_T": "Assets, Net acquisition of financial assets",
                "L_NIL_T": "Liabilities, Net incurrence of liabilities",
            },
            "CL_BOP_INDICATOR": {
                "D_F": "Direct investment, Total financial assets/liabilities",
                "P_F": "Portfolio investment, Total financial assets/liabilities",
            },
            "CL_UNIT": {"USD": "US dollar"},
            "CL_FREQ": {"A": "Annual"},
        },
    }

    expected_values = {
        ("JPN", "A_NFA_T", "D_F", "2022"): 174943442053.1513,
        ("JPN", "A_NFA_T", "P_F", "2022"): -174260174818.3375,
        ("JPN", "L_NIL_T", "D_F", "2023"): 20007989122.90426,
        ("USA", "L_NIL_T", "P_F", "2023"): 1300772000000.0,
    }
    actual_values = {
        (row["territory_code"], row["accounting_entry_code"], row["investment_category_code"], row["provider_period_code"]): row["value"]
        for row in normalized["rows"]
    }
    for key, value in expected_values.items():
        assert actual_values[key] == value

    first = normalized["rows"][0]
    assert first["provider_indicator_code"] == "BOP:A_NFA_T:D_F"
    assert first["provider_indicator_label"] == "Assets, Net acquisition of financial assets — Direct investment, Total financial assets/liabilities"
    assert first["territory_code"] == "JPN"
    assert first["territory_label"] == "Japan"
    assert first["unit_code"] == "USD"
    assert first["unit_label"] == "US dollar"
    assert first["attributes"]["financial_account_side"] == "asset"
    assert first["attributes"]["accounting_entry_code"] == "A_NFA_T"
    assert first["attributes"]["investment_category_code"] == "D_F"
    assert first["attributes"]["methodology"] == "BPM6"
    assert first["attributes"]["scale"] == "6"
    assert first["attributes"]["series_key"] == "JPN.A_NFA_T.D_F.USD.A"
    assert first["source_payload"]["series_attributes"]["BOP_ACCOUNTING_ENTRY"] == "A_NFA_T"
    assert first["source_payload"]["obs_attributes"] == {
        "TIME_PERIOD": "2022",
        "OBS_VALUE": "174943442053.1513",
        "DERIVATION_TYPE": "O",
        "PRECISION": "6",
        "ACCESS_SHARING_LEVEL": "PUBLIC_OPEN",
        "SECURITY_CLASSIFICATION": "PUB",
    }


def test_imf_bop_financial_account_observed_package_satisfies_existing_contract_without_contract_evolution():
    normalized = _normalized_from_sample()
    package = build_imf_bop_financial_account_observed_package(normalized)

    assert package.source_code == "IMF_BOP_FINANCIAL_ACCOUNT"
    assert package.source_name == "International Monetary Fund bounded BOP financial-account evidence slice"
    assert package.source_home_url == "https://www.imf.org/"
    assert package.provider_dataset_code == "BOP"
    assert package.release_key.startswith("IMF_BOP_FINANCIAL_ACCOUNT:BOP:2022-2023:")
    assert package.row_count == 16
    assert package.expected_row_count == 16
    assert package.input_filters == normalized["input_filters"]
    assert package.raw_evidence["source_urls"] == list(SOURCE_URLS)
    assert package.raw_evidence["metadata_url"] == METADATA_URL
    assert package.raw_evidence["raw_artifact_path"] == "data/raw/imf_bop_financial_account/imf-bop-financial-account-usa-jpn-2022-2023.xml"
    assert package.raw_evidence["metadata_artifact_path"] == "data/raw/imf_bop_financial_account/imf-bop-dataflow-references-20260701.xml"
    assert len(package.raw_evidence["raw_sha256"]) == 64
    assert len(package.raw_evidence["metadata_sha256"]) == 64
    assert package.raw_evidence["provider_metadata"] == normalized["provider_metadata"]

    observation = package.observations[0]
    assert observation.provider_indicator_code == "BOP:A_NFA_T:D_F"
    assert observation.provider_indicator_label == "Assets, Net acquisition of financial assets — Direct investment, Total financial assets/liabilities"
    assert observation.provider_territory_code == "JPN"
    assert observation.provider_territory_label == "Japan"
    assert observation.provider_period_code == "2022"
    assert observation.frequency == "A"
    assert observation.period_year == 2022
    assert observation.unit_code == "USD"
    assert observation.unit_label == "US dollar"
    assert observation.value == 174943442053.1513
    assert observation.observation_status == "observed"
    assert observation.decimal_precision == 4
    assert observation.attribute_hash == canonical_attribute_hash(observation.attributes)

    report = validate_observed_package_contract(package)
    assert report.valid is True
    assert report.issues == ()


def test_imf_bop_financial_account_observed_package_replay_is_deterministic():
    package = build_imf_bop_financial_account_observed_package(_normalized_from_sample())
    replayed = build_imf_bop_financial_account_observed_package(_normalized_from_sample())

    comparison = compare_observed_packages(package, replayed)

    assert comparison.equivalent is True
    assert comparison.left_fingerprint == comparison.right_fingerprint
    assert comparison.row_count_match is True
    assert comparison.expected_row_count_match is True
    assert comparison.observation_count_match is True
    assert comparison.differing_observations == ()
    assert len(observed_package_fingerprint(package)) == 64


def test_imf_bop_financial_account_fixture_files_exist_and_match_expected_bounded_scope():
    assert RAW_FIXTURE.exists()
    assert METADATA_FIXTURE.exists()
    raw_payload = RAW_FIXTURE.read_bytes()
    metadata_payload = METADATA_FIXTURE.read_bytes()
    normalized = normalize_imf_bop_financial_account_fixture(
        raw_payload,
        metadata_payload=metadata_payload,
        raw_artifact_path="data/raw/imf_bop_financial_account/imf-bop-financial-account-usa-jpn-2022-2023.xml",
        raw_sha256=hashlib.sha256(raw_payload).hexdigest(),
        metadata_artifact_path="data/raw/imf_bop_financial_account/imf-bop-dataflow-references-20260701.xml",
        metadata_sha256=hashlib.sha256(metadata_payload).hexdigest(),
        source_urls=SOURCE_URLS,
        metadata_url=METADATA_URL,
        content_type=CONTENT_TYPE,
    )

    assert normalized["row_count"] == 16
    assert normalized["input_filters"]["countries"] == ["USA", "JPN"]
    assert normalized["input_filters"]["accounting_entries"] == ["A_NFA_T", "L_NIL_T"]
    assert normalized["input_filters"]["indicators"] == ["D_F", "P_F"]


def test_imf_bop_financial_account_slice_does_not_create_generic_financial_or_sdmx_infrastructure():
    forbidden_paths = [
        PROJECT_ROOT / "src" / "macroforge" / "balance_of_payments.py",
        PROJECT_ROOT / "src" / "macroforge" / "financial_account.py",
        PROJECT_ROOT / "src" / "macroforge" / "financial_flows.py",
        PROJECT_ROOT / "src" / "macroforge" / "sdmx.py",
        PROJECT_ROOT / "src" / "macroforge" / "canonical_bop_loader.py",
        PROJECT_ROOT / "src" / "macroforge" / "imf.py",
    ]
    for forbidden_path in forbidden_paths:
        assert not forbidden_path.exists(), f"TASK-063 must remain source-specific; unexpected generic file: {forbidden_path}"
