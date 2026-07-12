from __future__ import annotations

import json
import urllib.error
from pathlib import Path
from xml.etree import ElementTree as ET

import pytest

from macroforge import bis_sdmx


def _sample_root(prepared: str = "2026-07-12T16:27:52Z") -> ET.Element:
    xml = f'''<message:StructureSpecificData xmlns:message="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message" xmlns:ss="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/structurespecific">
      <message:Header>
        <message:ID>msg-1</message:ID>
        <message:Prepared>{prepared}</message:Prepared>
        <message:Sender id="BIS" />
        <message:Structure structureID="BIS_WS_CREDIT_GAP_1_0" namespace="urn:bis" dimensionAtObservation="TIME_PERIOD" />
        <message:DataSetAction>Information</message:DataSetAction>
        <message:DataSetID>DS-1</message:DataSetID>
        <message:Extracted>2026-07-12T16:28:00Z</message:Extracted>
        <message:ReportingBegin>2010-Q1</message:ReportingBegin>
        <message:ReportingEnd>2025-Q4</message:ReportingEnd>
      </message:Header>
      <message:DataSet UNIT_MEASURE="770" UNIT_MULT="0" COLLECTION="E" DECIMALS="1" ss:structureRef="BIS_WS_CREDIT_GAP_1_0" />
    </message:StructureSpecificData>'''
    return ET.fromstring(xml)


def test_canonical_bis_source_constants_are_source_not_campaign_identity():
    assert bis_sdmx.BIS_SOURCE_CODE == "BIS_PUBLIC_SDMX_API"
    assert "Bank for International Settlements" in bis_sdmx.BIS_SOURCE_NAME
    assert bis_sdmx.BIS_SOURCE_HOME_URL == "https://www.bis.org/"
    assert "Prepared" in bis_sdmx.BIS_SNAPSHOT_MEANING
    assert "official publication release" in bis_sdmx.BIS_SNAPSHOT_MEANING


def test_prepared_timestamp_parses_to_deterministic_acquired_snapshot_key():
    assert bis_sdmx.prepared_to_snapshot_key("WS_CREDIT_GAP", "2026-07-12T16:27:52Z") == "bis-ws-credit-gap-snapshot-prepared-20260712t162752z"
    assert bis_sdmx.prepared_to_snapshot_key("WS_DSR", "2026-07-12T15:07:28Z") == "bis-ws-dsr-snapshot-prepared-20260712t150728z"


@pytest.mark.parametrize("prepared", [None, "", "2026-07-12", "2026-07-12T16:27:52+00:00", "not-a-timestamp"])
def test_malformed_or_missing_prepared_blocks_snapshot_identity(prepared):
    with pytest.raises(ValueError):
        bis_sdmx.prepared_to_snapshot_key("WS_CREDIT_GAP", prepared)


def test_response_metadata_extracts_header_structure_dataset_and_http_evidence():
    meta = bis_sdmx.provider_metadata(
        _sample_root(),
        dataflow_code="WS_CREDIT_GAP",
        dataflow_version="1.0",
        raw_meta={"http_status": 200, "content_type": "application/vnd.sdmx.structurespecificdata+xml", "acquired_at_utc": "2026-07-12T16:28:01+00:00"},
    )
    assert meta["message_id"] == "msg-1"
    assert meta["prepared"] == "2026-07-12T16:27:52Z"
    assert meta["sender"] == "BIS"
    assert meta["dataset_action"] == "Information"
    assert meta["dataset_id"] == "DS-1"
    assert meta["extracted"] == "2026-07-12T16:28:00Z"
    assert meta["reporting_begin"] == "2010-Q1"
    assert meta["reporting_end"] == "2025-Q4"
    assert meta["structure_id"] == "BIS_WS_CREDIT_GAP_1_0"
    assert meta["structure_namespace"] == "urn:bis"
    assert meta["dimension_at_observation"] == "TIME_PERIOD"
    assert meta["dataflow"] == {"agency_id": "BIS", "id": "WS_CREDIT_GAP", "version": "1.0"}
    assert meta["dataset_attributes"] == {"COLLECTION": "E", "DECIMALS": "1", "UNIT_MEASURE": "770", "UNIT_MULT": "0"}
    assert meta["http_status"] == 200
    assert meta["content_type"] == "application/vnd.sdmx.structurespecificdata+xml"
    assert meta["acquired_at_utc"] == "2026-07-12T16:28:01+00:00"


def test_quarterly_period_normalization_uses_calendar_quarter_bounds():
    assert bis_sdmx.quarter_periods("2025-Q3", "2026-Q1") == [
        (2025, 3, "2025-Q3", "2025-Q3", "2025-07-01", "2025-09-30"),
        (2025, 4, "2025-Q4", "2025-Q4", "2025-10-01", "2025-12-31"),
        (2026, 1, "2026-Q1", "2026-Q1", "2026-01-01", "2026-03-31"),
    ]


def test_series_key_semantics_remove_only_territory_and_preserve_non_territory_order():
    dims = ["FREQ", "BORROWERS_CTY", "TC_BORROWERS", "TC_LENDERS", "CG_DTYPE"]
    attrs = {"FREQ": "Q", "BORROWERS_CTY": "US", "TC_BORROWERS": "P", "TC_LENDERS": "A", "CG_DTYPE": "C"}
    assert bis_sdmx.series_key_without_territory(attrs, dims, "BORROWERS_CTY") == ("Q", "P", "A", "C")


def test_distinct_non_territory_dimensions_produce_distinct_semantic_identities():
    dims = ["FREQ", "BORROWERS_CTY", "TC_BORROWERS", "TC_LENDERS", "CG_DTYPE"]
    base = {"FREQ": "Q", "BORROWERS_CTY": "US", "TC_BORROWERS": "P", "TC_LENDERS": "A", "CG_DTYPE": "C"}
    ratio = dict(base, CG_DTYPE="R")
    households = dict(base, TC_BORROWERS="H")
    assert bis_sdmx.series_key_without_territory(base, dims, "BORROWERS_CTY") != bis_sdmx.series_key_without_territory(ratio, dims, "BORROWERS_CTY")
    assert bis_sdmx.series_key_without_territory(base, dims, "BORROWERS_CTY") != bis_sdmx.series_key_without_territory(households, dims, "BORROWERS_CTY")


def test_bis_data_url_is_dataflow_specific_and_preserves_query_window_outside_snapshot_identity():
    url = bis_sdmx.bis_data_url("WS_CREDIT_GAP", "1.0", "Q..P.A.C", start_period="2010-Q1", end_period="2025-Q4")
    assert url == "https://stats.bis.org/api/v2/data/dataflow/BIS/WS_CREDIT_GAP/1.0/Q..P.A.C?startPeriod=2010-Q1&endPeriod=2025-Q4"
    assert "2010-Q1" not in bis_sdmx.prepared_to_snapshot_key("WS_CREDIT_GAP", "2026-07-12T16:27:52Z")


def test_attempt_specific_paths_and_atomic_active_artifact_promotion(monkeypatch, tmp_path):
    raw_dir = tmp_path / "raw"
    active_raw = raw_dir / "active" / "sample.xml"
    active_meta = raw_dir / "active" / "sample-metadata.json"

    class Response:
        status = 200
        headers = {"Content-Type": "text/xml"}
        def __enter__(self): return self
        def __exit__(self, exc_type, exc, tb): return False
        def read(self): return b"<ok/>"

    monkeypatch.setattr(bis_sdmx.urllib.request, "urlopen", lambda req, timeout: Response())
    meta = bis_sdmx.fetch_to_attempt(
        url="https://stats.bis.org/api/v2/data/dataflow/BIS/WS_CREDIT_GAP/1.0/Q..P.A.C?startPeriod=2010-Q1&endPeriod=2025-Q4",
        raw_dir=raw_dir,
        active_raw_path=active_raw,
        active_meta_path=active_meta,
        task_id="TASK-215",
        request_parameters={"key": "Q..P.A.C"},
        user_agent="test",
    )
    assert meta["attempt_id"].startswith("attempt-")
    assert (raw_dir / "_attempts" / meta["attempt_id"] / active_raw.name).read_bytes() == b"<ok/>"
    assert active_raw.read_bytes() == b"<ok/>"
    assert json.loads(active_meta.read_text())["raw_sha256"] == bis_sdmx.sha256_bytes(b"<ok/>")


def test_failed_promotion_does_not_replace_existing_active_evidence(monkeypatch, tmp_path):
    raw_dir = tmp_path / "raw"
    active_raw = raw_dir / "active" / "sample.xml"
    active_meta = raw_dir / "active" / "sample-metadata.json"
    active_raw.parent.mkdir(parents=True)
    active_raw.write_bytes(b"existing")
    active_meta.write_text('{"status":"existing"}\n')

    def fail(*args, **kwargs):
        raise urllib.error.URLError("transport failed")

    monkeypatch.setattr(bis_sdmx.urllib.request, "urlopen", fail)
    with pytest.raises(urllib.error.URLError):
        bis_sdmx.fetch_to_attempt(
            url="https://stats.bis.org/api/v2/data/dataflow/BIS/WS_CREDIT_GAP/1.0/Q..P.A.C?startPeriod=2010-Q1&endPeriod=2025-Q4",
            raw_dir=raw_dir,
            active_raw_path=active_raw,
            active_meta_path=active_meta,
            task_id="TASK-215",
            request_parameters={"key": "Q..P.A.C"},
            user_agent="test",
        )
    assert active_raw.read_bytes() == b"existing"
    assert json.loads(active_meta.read_text()) == {"status": "existing"}
    assert list((raw_dir / "_attempts").glob("*/acquisition-error.json"))


def test_checksum_hash_path_and_local_name_helpers_are_deterministic(tmp_path):
    p = tmp_path / "artifact.txt"
    p.write_bytes(b"abc")
    assert bis_sdmx.sha256_bytes(b"abc") == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"
    assert bis_sdmx.sha256_file(p) == bis_sdmx.sha256_bytes(b"abc")
    assert bis_sdmx.attr_hash({"b": 2, "a": 1}) == bis_sdmx.attr_hash({"a": 1, "b": 2})
    assert bis_sdmx.rel(p, tmp_path) == "artifact.txt"
    assert bis_sdmx.local_name("{urn:test}Prepared") == "Prepared"
