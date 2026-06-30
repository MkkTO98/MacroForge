from __future__ import annotations

import hashlib
from pathlib import Path

from macroforge.contract_drift import validate_observed_package_contract
from macroforge.ecb_sdw import build_ecb_exr_observed_package, normalize_ecb_exr_fixture
from macroforge.observed_ingestion import canonical_attribute_hash, compare_observed_packages, observed_package_fingerprint

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_FIXTURE = PROJECT_ROOT / "data" / "raw" / "ecb_sdw" / "ecb-exr-usd-eur-2026-05-raw.xml"
SOURCE_URL = "https://data-api.ecb.europa.eu/service/data/EXR/M.USD.EUR.SP00.A?startPeriod=2026-05&endPeriod=2026-05"
CONTENT_TYPE = "application/vnd.sdmx.genericdata+xml;version=2.1"

SAMPLE_XML = b'''<?xml version="1.0" encoding="UTF-8"?>
<message:GenericData
  xmlns:message="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message"
  xmlns:common="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/common"
  xmlns:generic="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic">
  <message:Header>
    <message:ID>task-055-test-message</message:ID>
    <message:Prepared>2026-06-29T13:09:43.526+02:00</message:Prepared>
    <message:Sender id="ECB"/>
    <message:Structure structureID="ECB_EXR1" dimensionAtObservation="TIME_PERIOD">
      <common:Structure>
        <URN>urn:sdmx:org.sdmx.infomodel.datastructure.DataStructure=ECB:ECB_EXR1(1.0)</URN>
      </common:Structure>
    </message:Structure>
  </message:Header>
  <message:DataSet action="Replace" validFromDate="2026-06-29T13:09:43.526+02:00" structureRef="ECB_EXR1">
    <generic:Series>
      <generic:SeriesKey>
        <generic:Value id="FREQ" value="M"/>
        <generic:Value id="CURRENCY" value="USD"/>
        <generic:Value id="CURRENCY_DENOM" value="EUR"/>
        <generic:Value id="EXR_TYPE" value="SP00"/>
        <generic:Value id="EXR_SUFFIX" value="A"/>
      </generic:SeriesKey>
      <generic:Attributes>
        <generic:Value id="DECIMALS" value="4"/>
        <generic:Value id="TITLE_COMPL" value="ECB reference exchange rate, US dollar/Euro, 2.15 pm (C.E.T.)"/>
        <generic:Value id="UNIT_MULT" value="0"/>
        <generic:Value id="TITLE" value="US dollar/Euro ECB reference exchange rate"/>
        <generic:Value id="SOURCE_AGENCY" value="4F0"/>
        <generic:Value id="UNIT" value="USD"/>
        <generic:Value id="TIME_FORMAT" value="P1M"/>
        <generic:Value id="COLLECTION" value="A"/>
        <generic:Value id="UNIT_INDEX_BASE" value="99Q1=100"/>
      </generic:Attributes>
      <generic:Obs>
        <generic:ObsDimension value="2026-05"/>
        <generic:ObsValue value="1.16732"/>
        <generic:Attributes>
          <generic:Value id="OBS_STATUS" value="A"/>
          <generic:Value id="OBS_CONF" value="F"/>
        </generic:Attributes>
      </generic:Obs>
    </generic:Series>
  </message:DataSet>
</message:GenericData>
'''


def _normalized_from_sample() -> dict:
    return normalize_ecb_exr_fixture(
        SAMPLE_XML,
        raw_artifact_path="data/raw/ecb_sdw/ecb-exr-usd-eur-2026-05-raw.xml",
        raw_sha256=hashlib.sha256(SAMPLE_XML).hexdigest(),
        source_url=SOURCE_URL,
        content_type=CONTENT_TYPE,
    )


def test_ecb_exr_fixture_normalizes_source_specific_sdmx_metadata_without_sdmx_layer():
    normalized = _normalized_from_sample()

    assert normalized["source_code"] == "ECB_SDW"
    assert normalized["provider_dataset_code"] == "EXR:M.USD.EUR.SP00.A"
    assert normalized["dataflow_code"] == "EXR"
    assert normalized["frequency"] == "M"
    assert normalized["period_range"] == "2026-M05-2026-M05"
    assert normalized["row_count"] == 1
    assert normalized["expected_row_count"] == 1
    assert normalized["input_filters"] == {
        "dataflow": "EXR",
        "series_key": "M.USD.EUR.SP00.A",
        "startPeriod": "2026-05",
        "endPeriod": "2026-05",
        "scope": "bounded TASK-055 architectural experiment",
    }
    assert normalized["provider_metadata"] == {
        "message_id": "task-055-test-message",
        "prepared": "2026-06-29T13:09:43.526+02:00",
        "sender": "ECB",
        "structure_id": "ECB_EXR1",
        "structure_urn": "urn:sdmx:org.sdmx.infomodel.datastructure.DataStructure=ECB:ECB_EXR1(1.0)",
        "dataset_action": "Replace",
        "valid_from_date": "2026-06-29T13:09:43.526+02:00",
        "dimension_at_observation": "TIME_PERIOD",
    }

    assert normalized["rows"] == [
        {
            "dataflow_code": "EXR",
            "series_key": "M.USD.EUR.SP00.A",
            "provider_indicator_code": "EXR:USD_EUR:SP00:A",
            "provider_indicator_label": "US dollar/Euro ECB reference exchange rate",
            "currency": "USD",
            "currency_denom": "EUR",
            "exr_type": "SP00",
            "exr_suffix": "A",
            "territory_code": "ECB_AREA",
            "territory_label": "European Central Bank statistical area",
            "provider_period_code": "2026-M05",
            "frequency": "M",
            "period_year": 2026,
            "period_month": 5,
            "unit_code": "USD_PER_EUR",
            "unit_label": "US dollar per euro",
            "value": 1.16732,
            "observation_status": "observed",
            "decimal_precision": 5,
            "attributes": {
                "dataflow_code": "EXR",
                "series_key": "M.USD.EUR.SP00.A",
                "frequency": "M",
                "currency": "USD",
                "currency_denom": "EUR",
                "exr_type": "SP00",
                "exr_suffix": "A",
                "decimals": "4",
                "title_compl": "ECB reference exchange rate, US dollar/Euro, 2.15 pm (C.E.T.)",
                "unit_mult": "0",
                "title": "US dollar/Euro ECB reference exchange rate",
                "source_agency": "4F0",
                "unit": "USD",
                "time_format": "P1M",
                "collection": "A",
                "unit_index_base": "99Q1=100",
                "obs_status": "A",
                "obs_conf": "F",
                "dimension_at_observation": "TIME_PERIOD",
            },
            "source_payload": {
                "series_dimensions": {
                    "FREQ": "M",
                    "CURRENCY": "USD",
                    "CURRENCY_DENOM": "EUR",
                    "EXR_TYPE": "SP00",
                    "EXR_SUFFIX": "A",
                },
                "series_attributes": {
                    "DECIMALS": "4",
                    "TITLE_COMPL": "ECB reference exchange rate, US dollar/Euro, 2.15 pm (C.E.T.)",
                    "UNIT_MULT": "0",
                    "TITLE": "US dollar/Euro ECB reference exchange rate",
                    "SOURCE_AGENCY": "4F0",
                    "UNIT": "USD",
                    "TIME_FORMAT": "P1M",
                    "COLLECTION": "A",
                    "UNIT_INDEX_BASE": "99Q1=100",
                },
                "obs_dimension": {"TIME_PERIOD": "2026-05"},
                "obs_value": "1.16732",
                "obs_attributes": {"OBS_STATUS": "A", "OBS_CONF": "F"},
            },
        }
    ]


def test_ecb_exr_observed_package_satisfies_existing_contract_without_contract_evolution():
    package = build_ecb_exr_observed_package(_normalized_from_sample())

    assert package.source_code == "ECB_SDW"
    assert package.source_name == "European Central Bank Statistical Data Warehouse bounded exchange-rate evidence slice"
    assert package.source_home_url == "https://data.ecb.europa.eu/"
    assert package.provider_dataset_code == "EXR:M.USD.EUR.SP00.A"
    assert package.release_key.startswith("ECB_SDW:EXR:M.USD.EUR.SP00.A:2026-M05-2026-M05:")
    assert package.row_count == 1
    assert package.expected_row_count == 1
    assert package.input_filters == _normalized_from_sample()["input_filters"]
    assert package.raw_evidence["source_url"] == SOURCE_URL
    assert package.raw_evidence["raw_artifact_path"] == "data/raw/ecb_sdw/ecb-exr-usd-eur-2026-05-raw.xml"
    assert len(package.raw_evidence["raw_sha256"]) == 64
    assert package.raw_evidence["provider_metadata"] == _normalized_from_sample()["provider_metadata"]

    observation = package.observations[0]
    assert observation.provider_indicator_code == "EXR:USD_EUR:SP00:A"
    assert observation.provider_indicator_label == "US dollar/Euro ECB reference exchange rate"
    assert observation.provider_territory_code == "ECB_AREA"
    assert observation.provider_territory_label == "European Central Bank statistical area"
    assert observation.provider_period_code == "2026-M05"
    assert observation.frequency == "M"
    assert observation.period_year == 2026
    assert observation.period_quarter is None
    assert observation.period_month == 5
    assert observation.unit_code == "USD_PER_EUR"
    assert observation.unit_label == "US dollar per euro"
    assert observation.value == 1.16732
    assert observation.observation_status == "observed"
    assert observation.decimal_precision == 5
    assert observation.attribute_hash == canonical_attribute_hash(observation.attributes)

    report = validate_observed_package_contract(package)
    assert report.valid is True
    assert report.issues == ()


def test_ecb_exr_observed_package_replay_is_deterministic():
    package = build_ecb_exr_observed_package(_normalized_from_sample())
    replayed = build_ecb_exr_observed_package(_normalized_from_sample())

    comparison = compare_observed_packages(package, replayed)

    assert comparison.equivalent is True
    assert comparison.left_fingerprint == comparison.right_fingerprint
    assert comparison.row_count_match is True
    assert comparison.expected_row_count_match is True
    assert comparison.observation_count_match is True
    assert comparison.differing_observations == ()
    assert len(observed_package_fingerprint(package)) == 64


def test_ecb_module_remains_bounded_source_specific_not_sdmx_interpretation_layer():
    source = (PROJECT_ROOT / "src" / "macroforge" / "ecb_sdw.py").read_text(encoding="utf-8")

    forbidden = [
        "class SdmxInterpretationLayer",
        "class GenericSdmxAdapter",
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


def test_project_ecb_fixture_preserves_live_bounded_evidence_when_present():
    if not RAW_FIXTURE.exists():
        return

    raw_payload = RAW_FIXTURE.read_bytes()
    normalized = normalize_ecb_exr_fixture(
        raw_payload,
        raw_artifact_path=str(RAW_FIXTURE.relative_to(PROJECT_ROOT)),
        raw_sha256=hashlib.sha256(raw_payload).hexdigest(),
        source_url=SOURCE_URL,
        content_type=CONTENT_TYPE,
    )

    assert normalized["provider_dataset_code"] == "EXR:M.USD.EUR.SP00.A"
    assert normalized["row_count"] == 1
    assert normalized["rows"][0]["provider_period_code"] == "2026-M05"
    assert normalized["rows"][0]["frequency"] == "M"
    assert validate_observed_package_contract(build_ecb_exr_observed_package(normalized)).valid is True
