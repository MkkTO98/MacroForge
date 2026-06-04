from __future__ import annotations

import hashlib
import json
from pathlib import Path

from macroforge import oecd_sdmx

SAMPLE_XML = b'''<?xml version="1.0" encoding="UTF-8"?>
<message:GenericData
  xmlns:message="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message"
  xmlns:generic="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/generic">
  <message:DataSet>
    <generic:Series>
      <generic:SeriesKey>
        <generic:Value id="FREQ" value="A"/>
        <generic:Value id="REF_AREA" value="AUS"/>
        <generic:Value id="MEASURE" value="B1GQ"/>
        <generic:Value id="UNIT_MEASURE" value="USD_EXC"/>
        <generic:Value id="CHAPTER" value="NAAG_I"/>
      </generic:SeriesKey>
      <generic:Obs>
        <generic:ObsDimension id="TIME_PERIOD" value="2020"/>
        <generic:ObsValue value="1439.0230643897"/>
        <generic:Attributes>
          <generic:Value id="CONF_STATUS" value="F"/>
          <generic:Value id="DECIMALS" value="2"/>
          <generic:Value id="OBS_STATUS" value="A"/>
        </generic:Attributes>
      </generic:Obs>
      <generic:Obs>
        <generic:ObsDimension id="TIME_PERIOD" value="2021"/>
        <generic:ObsValue value="1552.667"/>
        <generic:Attributes>
          <generic:Value id="CONF_STATUS" value="F"/>
          <generic:Value id="DECIMALS" value="2"/>
          <generic:Value id="OBS_STATUS" value="A"/>
        </generic:Attributes>
      </generic:Obs>
    </generic:Series>
    <generic:Series>
      <generic:SeriesKey>
        <generic:Value id="FREQ" value="A"/>
        <generic:Value id="REF_AREA" value="USA"/>
        <generic:Value id="MEASURE" value="B1GQ"/>
        <generic:Value id="UNIT_MEASURE" value="USD_EXC"/>
        <generic:Value id="CHAPTER" value="NAAG_I"/>
      </generic:SeriesKey>
      <generic:Obs>
        <generic:ObsDimension id="TIME_PERIOD" value="2020"/>
        <generic:ObsValue value="21322.95"/>
        <generic:Attributes>
          <generic:Value id="CONF_STATUS" value="F"/>
          <generic:Value id="DECIMALS" value="2"/>
          <generic:Value id="OBS_STATUS" value="A"/>
        </generic:Attributes>
      </generic:Obs>
    </generic:Series>
    <generic:Series>
      <generic:SeriesKey>
        <generic:Value id="FREQ" value="A"/>
        <generic:Value id="REF_AREA" value="DNK"/>
        <generic:Value id="MEASURE" value="B1GQ"/>
        <generic:Value id="UNIT_MEASURE" value="DKK"/>
        <generic:Value id="CHAPTER" value="NAAG_I"/>
      </generic:SeriesKey>
      <generic:Obs>
        <generic:ObsDimension id="TIME_PERIOD" value="2020"/>
        <generic:ObsValue value="2321.0"/>
        <generic:Attributes>
          <generic:Value id="CONF_STATUS" value="F"/>
          <generic:Value id="DECIMALS" value="1"/>
          <generic:Value id="OBS_STATUS" value="A"/>
        </generic:Attributes>
      </generic:Obs>
    </generic:Series>
  </message:DataSet>
</message:GenericData>
'''

ENDPOINT = "https://sdmx.oecd.org/public/rest/v1/data/OECD.SDD.NAD,DSD_NAAG@DF_NAAG_I/.?startPeriod=2020&endPeriod=2021"


def test_raw_metadata_records_endpoint_bytes_content_type_and_checksum():
    metadata = oecd_sdmx.build_raw_metadata(
        SAMPLE_XML,
        endpoint=ENDPOINT,
        content_type="application/vnd.sdmx.genericdata+xml; version=2.1; charset=utf-8",
        artifact_path=Path("data/raw/oecd_sdmx/sample.xml"),
    )

    assert metadata == {
        "endpoint": ENDPOINT,
        "content_type": "application/vnd.sdmx.genericdata+xml; version=2.1; charset=utf-8",
        "bytes": len(SAMPLE_XML),
        "sha256": hashlib.sha256(SAMPLE_XML).hexdigest(),
        "raw_artifact_path": "data/raw/oecd_sdmx/sample.xml",
    }


def test_parse_genericdata_observations_preserves_series_dimensions_obs_dimension_value_and_attributes():
    observations = oecd_sdmx.parse_genericdata_observations(SAMPLE_XML)

    assert len(observations) == 4
    assert observations[0] == {
        "series_dimensions": {
            "FREQ": "A",
            "REF_AREA": "AUS",
            "MEASURE": "B1GQ",
            "UNIT_MEASURE": "USD_EXC",
            "CHAPTER": "NAAG_I",
        },
        "obs_dimension": {"TIME_PERIOD": "2020"},
        "obs_value": "1439.0230643897",
        "attributes": {"CONF_STATUS": "F", "DECIMALS": "2", "OBS_STATUS": "A"},
    }


def test_normalize_sdmx_payload_filters_bounded_subset_to_source_contract_shape():
    result = oecd_sdmx.normalize_sdmx_payload(
        SAMPLE_XML,
        endpoint=ENDPOINT,
        content_type="application/vnd.sdmx.genericdata+xml; version=2.1; charset=utf-8",
        territory_codes={"AUS", "USA"},
        measure_codes={"B1GQ"},
    )

    assert result["source_code"] == "OECD_NAAG"
    assert result["provider_dataset_code"] == "OECD.SDD.NAD,DSD_NAAG@DF_NAAG_I"
    assert result["raw_metadata"]["sha256"] == hashlib.sha256(SAMPLE_XML).hexdigest()
    assert result["row_count"] == 3
    assert result["filters"] == {"territory_codes": ["AUS", "USA"], "measure_codes": ["B1GQ"]}
    assert result["rows"][0] == {
        "source_code": "OECD_NAAG",
        "provider_dataset_code": "OECD.SDD.NAD,DSD_NAAG@DF_NAAG_I",
        "indicator_code": "B1GQ",
        "territory_code": "AUS",
        "period": "2020",
        "frequency": "A",
        "value": 1439.0230643897,
        "unit": "USD_EXC",
        "attributes": {"CONF_STATUS": "F", "DECIMALS": "2", "OBS_STATUS": "A"},
        "source_payload": {
            "series_dimensions": {
                "FREQ": "A",
                "REF_AREA": "AUS",
                "MEASURE": "B1GQ",
                "UNIT_MEASURE": "USD_EXC",
                "CHAPTER": "NAAG_I",
            },
            "obs_dimension": {"TIME_PERIOD": "2020"},
            "obs_value": "1439.0230643897",
        },
    }
    assert {row["territory_code"] for row in result["rows"]} == {"AUS", "USA"}


def test_write_smoke_artifacts_writes_normalized_json_and_contract_report(tmp_path):
    paths = oecd_sdmx.write_smoke_artifacts(
        SAMPLE_XML,
        output_root=tmp_path,
        endpoint=ENDPOINT,
        content_type="application/vnd.sdmx.genericdata+xml; version=2.1; charset=utf-8",
        territory_codes={"AUS", "USA"},
        measure_codes={"B1GQ"},
    )

    raw_path = Path(paths["raw_artifact"])
    normalized_path = Path(paths["normalized"])
    report_path = Path(paths["report"])
    assert raw_path.exists()
    assert normalized_path.exists()
    assert report_path.exists()
    assert raw_path.read_bytes() == SAMPLE_XML

    normalized = json.loads(normalized_path.read_text(encoding="utf-8"))
    assert normalized["row_count"] == 3
    assert normalized["raw_metadata"]["bytes"] == len(SAMPLE_XML)

    report = report_path.read_text(encoding="utf-8")
    assert "OECD/SDMX smoke evidence slice" in report
    assert "Source contract mapping" in report
    assert "3 observations" in report
    assert "No PostgreSQL schema change" in report
    assert "B1GQ" in report


def test_write_project_smoke_artifacts_uses_macroforge_data_and_report_layout(tmp_path):
    paths = oecd_sdmx.write_project_smoke_artifacts(
        SAMPLE_XML,
        project_root=tmp_path,
        endpoint=ENDPOINT,
        content_type="application/vnd.sdmx.genericdata+xml; version=2.1; charset=utf-8",
        territory_codes={"AUS", "USA"},
        measure_codes={"B1GQ"},
    )

    assert Path(paths["raw_artifact"]) == tmp_path / "data" / "raw" / "oecd_sdmx" / "oecd_sdmx_naag_2020_2021_raw.xml"
    assert Path(paths["normalized"]) == tmp_path / "data" / "metadata" / "oecd_sdmx" / "oecd-sdmx-smoke-normalized.json"
    assert Path(paths["report"]) == tmp_path / "artifacts" / "reports" / "oecd-sdmx-smoke-20260603.md"
    assert Path(paths["raw_artifact"]).read_bytes() == SAMPLE_XML
    assert json.loads(Path(paths["normalized"]).read_text(encoding="utf-8"))["row_count"] == 3
    assert "OECD/SDMX smoke evidence slice" in Path(paths["report"]).read_text(encoding="utf-8")


def test_cli_project_root_writes_project_layout_without_generic_root_dirs(tmp_path, capsys):
    source_xml = tmp_path / "fixture.xml"
    source_xml.write_bytes(SAMPLE_XML)

    exit_code = oecd_sdmx.main(
        [
            "--input-xml",
            str(source_xml),
            "--project-root",
            str(tmp_path),
        ]
    )

    assert exit_code == 0
    paths = json.loads(capsys.readouterr().out)
    assert Path(paths["raw_artifact"]) == tmp_path / "data" / "raw" / "oecd_sdmx" / "oecd_sdmx_naag_2020_2021_raw.xml"
    assert Path(paths["normalized"]) == tmp_path / "data" / "metadata" / "oecd_sdmx" / "oecd-sdmx-smoke-normalized.json"
    assert Path(paths["report"]) == tmp_path / "artifacts" / "reports" / "oecd-sdmx-smoke-20260603.md"
    assert not (tmp_path / "raw").exists()
    assert not (tmp_path / "metadata").exists()
    assert not (tmp_path / "reports").exists()
    normalized = json.loads(Path(paths["normalized"]).read_text(encoding="utf-8"))
    assert normalized["row_count"] == 3
    assert normalized["filters"] == {"territory_codes": ["AUS", "USA"], "measure_codes": ["B1GQ"]}


def test_fetch_payload_sends_user_agent_required_by_oecd(monkeypatch):
    captured = {}

    class FakeResponse:
        headers = {"content-type": "application/xml"}

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def read(self):
            return SAMPLE_XML

    def fake_urlopen(request, timeout):
        captured["headers"] = dict(request.header_items())
        captured["timeout"] = timeout
        return FakeResponse()

    monkeypatch.setattr(oecd_sdmx.urllib.request, "urlopen", fake_urlopen)

    payload, content_type = oecd_sdmx.fetch_payload(ENDPOINT, timeout=12)

    assert payload == SAMPLE_XML
    assert content_type == "application/xml"
    assert captured["timeout"] == 12
    assert captured["headers"]["User-agent"].startswith("MacroForge/")
