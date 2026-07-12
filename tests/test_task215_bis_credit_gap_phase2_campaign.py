from __future__ import annotations

import json
from xml.etree import ElementTree as ET

from macroforge import bis_sdmx
import tools.task215_bis_credit_gap_phase2_campaign as task215


def test_next_task_and_frozen_candidate_universe_counts():
    pred = task215.write_prediction()
    assert pred["task"] == "TASK-215"
    assert pred["provider_dataset"] == "BIS:WS_CREDIT_GAP"
    assert pred["series_key_dimensions"] == ["FREQ", "BORROWERS_CTY", "TC_BORROWERS", "TC_LENDERS", "CG_DTYPE"]
    assert pred["period_range"]["quarters"] == 64
    assert pred["expected_candidate_series"] == 43
    assert pred["expected_candidate_cells"] == 2752
    assert pred["expected_provider_valued_facts"] == 2752
    assert pred["expected_explicit_missing_facts"] == 0
    assert pred["expected_exclusions"]["aggregates"] == 1
    assert pred["selection_exclusions"][0]["provider_code"] == "XM"


def test_credit_gap_indicator_identity_removes_only_territory_and_preserves_material_dimensions():
    code = task215.canonical_indicator_code("P", "A", "C")
    assert code == "BIS:WS_CREDIT_GAP:CREDIT_TO_GDP_GAP_ACTUAL_MINUS_TREND:PRIVATE_NONFINANCIAL_SECTOR:ALL_SECTORS:PERCENTAGE_POINTS:Q"
    assert ":US" not in code and ":JP" not in code
    assert "PERCENTAGE_POINTS" in code
    assert "CREDIT_TO_GDP_GAP" in code


def test_shared_bis_snapshot_helper_excludes_query_window_and_campaign_scope():
    key = bis_sdmx.prepared_to_snapshot_key("WS_CREDIT_GAP", "2026-07-12T14:57:25Z")
    assert key == "bis-ws-credit-gap-snapshot-prepared-20260712t145725z"
    assert "2010" not in key
    assert "2025" not in key
    assert "task" not in key.lower()


def test_shared_series_key_helper_removes_only_territory_dimension():
    attrs = {"FREQ": "Q", "BORROWERS_CTY": "US", "TC_BORROWERS": "P", "TC_LENDERS": "A", "CG_DTYPE": "C"}
    remaining = bis_sdmx.series_key_without_territory(attrs, task215.SERIES_KEY_DIMENSIONS, task215.TERRITORY_DIMENSION)
    assert remaining == ("Q", "P", "A", "C")


def test_provider_metadata_helper_extracts_prepared_dataset_unit_and_structure():
    xml = '''<message:StructureSpecificData xmlns:message="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message" xmlns:ss="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/structurespecific">
      <message:Header><message:ID>x</message:ID><message:Prepared>2026-07-12T14:57:25Z</message:Prepared><message:Sender id="BIS"/><message:Structure structureID="BIS_WS_CREDIT_GAP_1_0" namespace="n" dimensionAtObservation="TIME_PERIOD"/><message:DataSetAction>Information</message:DataSetAction></message:Header>
      <message:DataSet UNIT_MEASURE="770" UNIT_MULT="0" COLLECTION="E" DECIMALS="1" ss:structureRef="BIS_WS_CREDIT_GAP_1_0" />
    </message:StructureSpecificData>'''
    meta = bis_sdmx.provider_metadata(ET.fromstring(xml), dataflow_code="WS_CREDIT_GAP", dataflow_version="1.0", raw_meta={"http_status": 200, "content_type": "xml", "acquired_at_utc": "now"})
    assert meta["prepared"] == "2026-07-12T14:57:25Z"
    assert meta["structure_id"] == "BIS_WS_CREDIT_GAP_1_0"
    assert meta["dataset_attributes"]["UNIT_MEASURE"] == "770"
    assert meta["dataset_attributes"]["COLLECTION"] == "E"


def test_normalize_fixture_candidate_reconciliation_and_explicit_missing(tmp_path, monkeypatch):
    raw_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<message:StructureSpecificData xmlns:message="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message" xmlns:ss="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/structurespecific">
  <message:Header><message:ID>x</message:ID><message:Prepared>2026-07-12T14:57:25Z</message:Prepared><message:Sender id="BIS"/><message:Structure structureID="BIS_WS_CREDIT_GAP_1_0" namespace="n" dimensionAtObservation="TIME_PERIOD"/><message:DataSetAction>Information</message:DataSetAction></message:Header>
  <message:DataSet UNIT_MEASURE="770" UNIT_MULT="0" COLLECTION="E" DECIMALS="1" ss:structureRef="BIS_WS_CREDIT_GAP_1_0">
    <Series FREQ="Q" BORROWERS_CTY="US" TC_BORROWERS="P" TC_LENDERS="A" CG_DTYPE="C" TITLE_TS="United States gap">
      <Obs TIME_PERIOD="2010-Q1" OBS_VALUE="1.2" OBS_STATUS="A" OBS_CONF="F" />
      <Obs TIME_PERIOD="2010-Q2" OBS_VALUE="1.3" OBS_STATUS="A" OBS_CONF="F" />
    </Series>
  </message:DataSet>
</message:StructureSpecificData>'''
    raw = tmp_path / "raw.xml"
    meta = tmp_path / "raw-metadata.json"
    raw.write_text(raw_xml, encoding="utf-8")
    meta.write_text(json.dumps({"source_url": "https://example", "request_parameters": {}, "http_status": 200, "content_type": "xml", "acquired_at_utc": "2026-07-12T00:00:00+00:00"}), encoding="utf-8")
    monkeypatch.setattr(task215, "RAW_PATH", raw)
    monkeypatch.setattr(task215, "RAW_META_PATH", meta)
    monkeypatch.setattr(task215, "AREAS", {"US": ("USA", "United States")})
    monkeypatch.setattr(task215, "SERIES_KEYS", (("US", "P", "A", "C"),))
    monkeypatch.setattr(task215, "START_PERIOD", "2010-Q1")
    monkeypatch.setattr(task215, "END_PERIOD", "2010-Q2")
    norm = task215.normalize()
    assert norm["candidate_cell_count"] == 2
    assert norm["observed_value_count"] == 2
    assert norm["explicit_missing_value_count"] == 0
    row = norm["rows"][0]
    assert row["provider_indicator_code"] == task215.canonical_indicator_code()
    assert row["territory_code"] == "USA"
    assert row["attributes"]["tc_borrowers"] == "P"
    assert row["attributes"]["tc_lenders"] == "A"
    assert row["attributes"]["cg_dtype"] == "C"


def test_values_sql_contains_quarter_and_percentage_point_unit():
    row = {"provider_indicator_code": task215.canonical_indicator_code(), "provider_indicator_label": "Credit gap", "territory_code": "USA", "territory_label": "United States", "provider_period_code": "2025-Q4", "period_year": 2025, "period_quarter": 4, "value": "1.0", "unit_code": "PERCENTAGE_POINTS", "unit_label": "Percentage points", "observation_status": "observed", "decimal_precision": 1, "attribute_hash": "abc", "attributes": {"cg_dtype": "C"}, "source_payload": {}}
    sql = task215.values_sql([row])
    assert "2025-Q4" in sql
    assert "PERCENTAGE_POINTS" in sql
    assert ", 4," in sql
