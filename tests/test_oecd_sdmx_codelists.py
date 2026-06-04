from __future__ import annotations

import hashlib
import json
from pathlib import Path

from macroforge import oecd_sdmx

STRUCTURE_XML = Path("tests/fixtures/oecd_sdmx_naag_structure_sample.xml").read_bytes()
STRUCTURE_ENDPOINT = "https://sdmx.oecd.org/public/rest/v1/dataflow/OECD.SDD.NAD/all/latest"


def test_parse_codelist_labels_filters_bounded_oecd_smoke_codes():
    result = oecd_sdmx.parse_codelist_labels(
        STRUCTURE_XML,
        endpoint=STRUCTURE_ENDPOINT,
        artifact_path=Path("data/raw/oecd_sdmx/oecd_sdmx_naag_structure_20260604.xml"),
    )

    assert result["source_code"] == "OECD_NAAG"
    assert result["provider_dataset_code"] == "OECD.SDD.NAD,DSD_NAAG@DF_NAAG_I"
    assert result["raw_metadata"] == {
        "endpoint": STRUCTURE_ENDPOINT,
        "content_type": "application/vnd.sdmx.structure+xml; version=2.1; charset=utf-8",
        "bytes": len(STRUCTURE_XML),
        "sha256": hashlib.sha256(STRUCTURE_XML).hexdigest(),
        "raw_artifact_path": "data/raw/oecd_sdmx/oecd_sdmx_naag_structure_20260604.xml",
    }
    assert result["codelists"] == {
        "MEASURE": {
            "codelist_id": "CL_MEASURE",
            "codelist_name": "Measure",
            "codes": {
                "B1GQ": {
                    "label": "Gross domestic product",
                    "description": "GDP, expenditure approach, current prices.",
                }
            },
        },
        "REF_AREA": {
            "codelist_id": "CL_REF_AREA",
            "codelist_name": "Reference area",
            "codes": {
                "AUS": {"label": "Australia", "description": None},
                "USA": {"label": "United States", "description": None},
            },
        },
        "UNIT_MEASURE": {
            "codelist_id": "CL_UNIT_MEASURE",
            "codelist_name": "Unit of measure",
            "codes": {
                "USD_EXC": {"label": "US dollars, exchange rate converted", "description": None},
                "USD_PPP": {"label": "US dollars, PPP converted", "description": None},
            },
        },
        "CONF_STATUS": {
            "codelist_id": "CL_CONF_STATUS",
            "codelist_name": "Confidentiality status",
            "codes": {"F": {"label": "Free for publication", "description": None}},
        },
        "OBS_STATUS": {
            "codelist_id": "CL_OBS_STATUS",
            "codelist_name": "Observation status",
            "codes": {"A": {"label": "Normal value", "description": None}},
        },
        "DECIMALS": {
            "codelist_id": None,
            "codelist_name": None,
            "codes": {"2": {"label": None, "description": "No codelist label found in bounded structure fixture."}},
        },
    }
    assert result["limitations"] == [
        "Bounded to currently observed OECD/SDMX smoke-slice codes; not a broad codelist harvest.",
        "DECIMALS is preserved as an observed attribute value when no codelist entry is present.",
        "No PostgreSQL schema change or live macro write is implied by this metadata evidence.",
    ]


def test_render_codelist_markdown_report_lists_labels_and_boundaries():
    result = oecd_sdmx.parse_codelist_labels(STRUCTURE_XML, endpoint=STRUCTURE_ENDPOINT)

    report = oecd_sdmx.render_codelist_markdown_report(result)

    assert "# OECD/SDMX codelist and label enrichment" in report
    assert "Raw SHA-256" in report
    assert "| MEASURE | B1GQ | Gross domestic product | GDP, expenditure approach, current prices. |" in report
    assert "| REF_AREA | USA | United States |  |" in report
    assert "No PostgreSQL schema change" in report
    assert "not a generalized SDMX/source framework" in report


def test_write_project_codelist_artifacts_uses_macroforge_layout(tmp_path):
    paths = oecd_sdmx.write_project_codelist_artifacts(
        STRUCTURE_XML,
        project_root=tmp_path,
        endpoint=STRUCTURE_ENDPOINT,
    )

    raw_path = Path(paths["raw_structure_artifact"])
    normalized_path = Path(paths["normalized_labels"])
    report_path = Path(paths["report"])

    assert raw_path == tmp_path / "data" / "raw" / "oecd_sdmx" / "oecd_sdmx_naag_structure_20260604.xml"
    assert normalized_path == tmp_path / "data" / "metadata" / "oecd_sdmx" / "oecd-sdmx-codelist-labels-20260604.json"
    assert report_path == tmp_path / "artifacts" / "reports" / "oecd-sdmx-codelist-labels-20260604.md"
    assert raw_path.read_bytes() == STRUCTURE_XML

    normalized = json.loads(normalized_path.read_text(encoding="utf-8"))
    assert normalized["codelists"]["MEASURE"]["codes"]["B1GQ"]["label"] == "Gross domestic product"
    assert normalized["raw_metadata"]["bytes"] == len(STRUCTURE_XML)
    assert "OECD/SDMX codelist and label enrichment" in report_path.read_text(encoding="utf-8")


def test_cli_writes_project_codelist_artifacts_from_fixture_without_live_fetch(tmp_path, capsys):
    fixture = tmp_path / "structure.xml"
    fixture.write_bytes(STRUCTURE_XML)

    exit_code = oecd_sdmx.main(
        [
            "--input-structure-xml",
            str(fixture),
            "--project-root",
            str(tmp_path),
            "--write-codelist-labels",
            "--structure-endpoint",
            STRUCTURE_ENDPOINT,
        ]
    )

    assert exit_code == 0
    paths = json.loads(capsys.readouterr().out)
    assert Path(paths["raw_structure_artifact"]).read_bytes() == STRUCTURE_XML
    assert Path(paths["normalized_labels"]).name == "oecd-sdmx-codelist-labels-20260604.json"
    assert not (tmp_path / "raw").exists()
    assert not (tmp_path / "metadata").exists()
    assert not (tmp_path / "reports").exists()
