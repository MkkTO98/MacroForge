from __future__ import annotations

import hashlib
import json
from pathlib import Path

from macroforge import wdi

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SUPPORT = PROJECT_ROOT / "artifacts" / "handoffs" / "wdi-live-smoke-support-20260602"
MANIFEST = SUPPORT / "manifest.json"
GDP_RAW = SUPPORT / "worldbank_wdi_NY.GDP.MKTP.CD_USA_DNK_2020_2021_raw.json"
POP_RAW = SUPPORT / "worldbank_wdi_SP.POP.TOTL_USA_DNK_2020_2021_raw.json"


def test_support_bundle_raw_checksums_match_manifest():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    by_indicator = {entry["indicator"]: entry for entry in manifest["entries"]}

    for indicator, path in {
        "NY.GDP.MKTP.CD": GDP_RAW,
        "SP.POP.TOTL": POP_RAW,
    }.items():
        payload = path.read_bytes()
        assert len(payload) == by_indicator[indicator]["bytes"]
        assert hashlib.sha256(payload).hexdigest() == by_indicator[indicator]["sha256"]


def test_normalize_worldbank_payload_produces_source_shaped_rows():
    raw_payload = GDP_RAW.read_text(encoding="utf-8")

    rows = wdi.normalize_worldbank_payload(raw_payload, source="World Bank WDI")

    assert len(rows) == 4
    assert rows[0] == {
        "source": "World Bank WDI",
        "indicator_id": "NY.GDP.MKTP.CD",
        "indicator_name": "GDP (current US$)",
        "country_id": "DK",
        "country_name": "Denmark",
        "countryiso3code": "DNK",
        "date": "2021",
        "value": 406110162088.054,
        "unit": None,
        "obs_status": None,
        "decimal": 0,
    }


def test_build_smoke_result_from_support_bundle_has_expected_8_rows():
    result = wdi.build_smoke_result_from_bundle(SUPPORT)

    assert result["row_count"] == 8
    assert result["expected_row_count"] == 8
    assert result["countries"] == ["USA", "DNK"]
    assert result["indicators"] == ["NY.GDP.MKTP.CD", "SP.POP.TOTL"]
    assert {row["countryiso3code"] for row in result["rows"]} == {"USA", "DNK"}
    assert {row["indicator_id"] for row in result["rows"]} == {"NY.GDP.MKTP.CD", "SP.POP.TOTL"}
    assert {row["date"] for row in result["rows"]} == {"2020", "2021"}


def test_write_smoke_artifacts_writes_raw_copies_manifest_normalized_rows_and_report(tmp_path):
    output = wdi.write_smoke_artifacts_from_bundle(SUPPORT, tmp_path)

    raw_dir = tmp_path / "raw" / "wdi"
    metadata_dir = tmp_path / "metadata" / "wdi"
    report_path = tmp_path / "reports" / "wdi-smoke-report.md"

    assert (raw_dir / GDP_RAW.name).exists()
    assert (raw_dir / POP_RAW.name).exists()
    assert (metadata_dir / "wdi-smoke-manifest.json").exists()
    assert (metadata_dir / "wdi-smoke-normalized.json").exists()
    assert report_path.exists()

    normalized = json.loads((metadata_dir / "wdi-smoke-normalized.json").read_text(encoding="utf-8"))
    assert normalized["row_count"] == 8
    assert normalized["raw_artifacts"][0]["sha256"] == "fe79eb846324a5d69df9518844e08b41add5377ac4f968208bd1152898d91167"

    report = report_path.read_text(encoding="utf-8")
    assert "World Bank WDI smoke slice" in report
    assert "8 observations" in report
    assert "NY.GDP.MKTP.CD" in report
    assert "SP.POP.TOTL" in report
