from __future__ import annotations

import json

import tools.task214_bis_dsr_credit_cycle_phase2_campaign as task214


def test_frozen_candidate_universe_counts_and_identity_rule():
    pred = task214.write_prediction()
    assert pred["provider_dataset"] == "BIS:WS_DSR"
    assert pred["series_key_dimensions"] == ["FREQ", "BORROWERS_CTY", "DSR_BORROWERS"]
    assert pred["expected_candidate_series"] == 66
    assert pred["period_range"]["quarters"] == 44
    assert pred["expected_candidate_cells"] == 2904
    assert pred["expected_provider_valued_facts"] == 2904
    assert pred["expected_explicit_missing_facts"] == 0
    assert "DSR_BORROWERS" in pred["canonical_indicator_rule"]
    assert "BORROWERS_CTY/territory" in pred["canonical_indicator_rule"]


def test_quarter_periods_cover_exact_window():
    periods = task214.quarter_periods()
    assert len(periods) == 44
    assert periods[0][:4] == (2015, 1, "2015-Q1", "2015-Q1")
    assert periods[-1][:4] == (2025, 4, "2025-Q4", "2025-Q4")
    assert periods[0][4:] == ("2015-01-01", "2015-03-31")
    assert periods[-1][4:] == ("2025-10-01", "2025-12-31")


def test_indicator_identity_removes_only_territory_and_preserves_sector_unit_frequency():
    h = task214.canonical_indicator_code("H")
    n = task214.canonical_indicator_code("N")
    p = task214.canonical_indicator_code("P")
    assert h == "BIS:WS_DSR:DEBT_SERVICE_RATIO:HOUSEHOLDS_NPISHS:PERCENT:Q"
    assert n == "BIS:WS_DSR:DEBT_SERVICE_RATIO:NONFINANCIAL_CORPORATIONS:PERCENT:Q"
    assert p == "BIS:WS_DSR:DEBT_SERVICE_RATIO:PRIVATE_NONFINANCIAL_SECTOR:PERCENT:Q"
    assert ":US" not in h and ":JP" not in p
    assert len({h, n, p}) == 3


def test_snapshot_release_key_uses_prepared_timestamp_not_query_window_or_campaign_scope():
    key = task214.release_key_from_provider_metadata({"prepared": "2026-07-12T14:57:51Z"}, "abc123")
    assert key == "bis-ws-dsr-snapshot-prepared-20260712t145751z"
    assert "2015" not in key
    assert "2025" not in key
    assert "task" not in key.lower()


def test_normalize_fixture_preserves_provider_dimensions_and_candidate_reconciliation(tmp_path, monkeypatch):
    raw_xml = '''<?xml version="1.0" encoding="UTF-8"?>
<message:StructureSpecificData xmlns:message="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/message" xmlns:ss="http://www.sdmx.org/resources/sdmxml/schemas/v2_1/data/structurespecific" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <message:Header>
    <message:ID>IDREFfixture</message:ID>
    <message:Prepared>2026-07-12T14:57:51Z</message:Prepared>
    <message:Sender id="BIS" />
    <message:Structure structureID="BIS_WS_DSR_1_0" namespace="urn:sdmx:org.sdmx.infomodel.datastructure.Dataflow=BIS:WS_DSR(1.0):ObsLevelDim:TIME_PERIOD" dimensionAtObservation="TIME_PERIOD" />
    <message:DataSetAction>Information</message:DataSetAction>
  </message:Header>
  <message:DataSet UNIT_MULT="0" UNIT_MEASURE="367" ss:dataScope="DataStructure" ss:structureRef="BIS_WS_DSR_1_0" xsi:type="ns1:DataSetType">
    <Series FREQ="Q" BORROWERS_CTY="US" DSR_BORROWERS="P" TITLE_TS="United States - Private non-financial sector" DECIMALS="1">
      <Obs TIME_PERIOD="2015-Q1" OBS_VALUE="15.1" OBS_STATUS="A" OBS_CONF="F" />
      <Obs TIME_PERIOD="2015-Q2" OBS_VALUE="15.2" OBS_STATUS="A" OBS_CONF="F" />
    </Series>
  </message:DataSet>
</message:StructureSpecificData>
'''
    raw = tmp_path / "raw.xml"
    meta = tmp_path / "raw-metadata.json"
    raw.write_text(raw_xml, encoding="utf-8")
    meta.write_text(json.dumps({
        "source_url": "https://stats.bis.org/api/v2/data/dataflow/BIS/WS_DSR/1.0/Q.US.P?startPeriod=2015-Q1&endPeriod=2015-Q2",
        "request_parameters": {"dataflow": "WS_DSR", "version": "1.0", "key": "Q.US.P", "startPeriod": "2015-Q1", "endPeriod": "2015-Q2"},
        "http_status": 200,
        "content_type": "application/xml;charset=UTF-8",
        "acquired_at_utc": "2026-07-12T14:58:00+00:00",
    }), encoding="utf-8")
    monkeypatch.setattr(task214, "RAW_PATH", raw)
    monkeypatch.setattr(task214, "RAW_META_PATH", meta)
    monkeypatch.setattr(task214, "AREAS", {"US": ("USA", "United States")})
    monkeypatch.setattr(task214, "BORROWER_SECTORS", {"P": ("PRIVATE_NONFINANCIAL_SECTOR", "Private non-financial sector")})
    monkeypatch.setattr(task214, "SERIES_KEYS", (("US", "P"),))
    monkeypatch.setattr(task214, "START_PERIOD", "2015-Q1")
    monkeypatch.setattr(task214, "END_PERIOD", "2015-Q2")
    norm = task214.normalize()
    assert norm["provider_dataset_code"] == "BIS:WS_DSR"
    assert norm["release_key"] == "bis-ws-dsr-snapshot-prepared-20260712t145751z"
    assert norm["candidate_cell_count"] == 2
    assert norm["observed_value_count"] == 2
    assert norm["explicit_missing_value_count"] == 0
    row = norm["rows"][0]
    assert row["provider_indicator_code"] == "BIS:WS_DSR:DEBT_SERVICE_RATIO:PRIVATE_NONFINANCIAL_SECTOR:PERCENT:Q"
    assert row["territory_code"] == "USA"
    assert row["attributes"]["dsr_borrowers"] == "P"
    assert row["attributes"]["borrowers_cty"] == "US"
    assert row["attributes"]["unit_measure_provider_code"] == "367"


def test_values_sql_contains_quarter_not_month():
    row = {
        "provider_indicator_code": "BIS:WS_DSR:DEBT_SERVICE_RATIO:PRIVATE_NONFINANCIAL_SECTOR:PERCENT:Q",
        "provider_indicator_label": "Debt service ratio - Private non-financial sector",
        "territory_code": "USA",
        "territory_label": "United States",
        "provider_period_code": "2025-Q4",
        "period_year": 2025,
        "period_quarter": 4,
        "value": "15.2",
        "unit_code": "PERCENT",
        "unit_label": "Percent",
        "observation_status": "observed",
        "decimal_precision": 1,
        "attribute_hash": "abc",
        "attributes": {"DSR_BORROWERS": "P"},
        "source_payload": {},
    }
    sql = task214.values_sql([row])
    assert "2025-Q4" in sql
    assert ", 4," in sql
