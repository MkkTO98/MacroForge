from __future__ import annotations

import hashlib
from pathlib import Path

from macroforge.contract_drift import validate_observed_package_contract
from macroforge.observed_ingestion import canonical_attribute_hash, compare_observed_packages, observed_package_fingerprint
from macroforge.un_comtrade_trade import (
    build_un_comtrade_trade_observed_package,
    normalize_un_comtrade_trade_fixture,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_FIXTURE = PROJECT_ROOT / "data" / "raw" / "un_comtrade_trade" / "un-comtrade-usa-jpn-total-goods-2023-import-export.json"
SOURCE_URL = "https://comtradeapi.un.org/public/v1/preview/C/A/HS?cmdCode=TOTAL&flowCode=M,X&reporterCode=842&period=2023&partnerCode=392&includeDesc=true"
CONTENT_TYPE = "application/json; charset=utf-8"

SAMPLE_JSON = b'''{"elapsedTime":"2.06 secs","count":2,"data":[{"typeCode":"C","freqCode":"A","refPeriodId":20230101,"refYear":2023,"refMonth":52,"period":"2023","reporterCode":842,"reporterISO":"USA","reporterDesc":"USA","flowCode":"M","flowDesc":"Import","partnerCode":392,"partnerISO":"JPN","partnerDesc":"Japan","partner2Code":0,"partner2ISO":"W00","partner2Desc":"World","classificationCode":"H6","classificationSearchCode":"HS","isOriginalClassification":true,"cmdCode":"TOTAL","cmdDesc":"All Commodities","aggrLevel":0,"isLeaf":false,"isAggregate":true,"customsCode":"C00","customsDesc":"TOTAL CPC","mosCode":"0","motCode":0,"motDesc":"TOTAL MOT","qtyUnitCode":-1,"qtyUnitAbbr":"N/A","qty":0,"isQtyEstimated":false,"altQtyUnitCode":-1,"altQtyUnitAbbr":"N/A","altQty":0,"isAltQtyEstimated":false,"netWgt":0,"isNetWgtEstimated":true,"grossWgt":0,"isGrossWgtEstimated":false,"fobvalue":null,"cifvalue":151580564290,"primaryValue":151580564290,"isReported":false,"legacyEstimationFlag":4},{"typeCode":"C","freqCode":"A","refPeriodId":20230101,"refYear":2023,"refMonth":52,"period":"2023","reporterCode":842,"reporterISO":"USA","reporterDesc":"USA","flowCode":"X","flowDesc":"Export","partnerCode":392,"partnerISO":"JPN","partnerDesc":"Japan","partner2Code":0,"partner2ISO":"W00","partner2Desc":"World","classificationCode":"H6","classificationSearchCode":"HS","isOriginalClassification":true,"cmdCode":"TOTAL","cmdDesc":"All Commodities","aggrLevel":0,"isLeaf":false,"isAggregate":true,"customsCode":"C00","customsDesc":"TOTAL CPC","mosCode":"0","motCode":0,"motDesc":"TOTAL MOT","qtyUnitCode":-1,"qtyUnitAbbr":"N/A","qty":0,"isQtyEstimated":false,"altQtyUnitCode":-1,"altQtyUnitAbbr":"N/A","altQty":0,"isAltQtyEstimated":false,"netWgt":0,"isNetWgtEstimated":true,"grossWgt":0,"isGrossWgtEstimated":false,"fobvalue":76154045176,"cifvalue":null,"primaryValue":76154045176,"isReported":false,"legacyEstimationFlag":4}],"error":""}'''


def _normalized_from_sample() -> dict:
    return normalize_un_comtrade_trade_fixture(
        SAMPLE_JSON,
        raw_artifact_path="data/raw/un_comtrade_trade/un-comtrade-usa-jpn-total-goods-2023-import-export.json",
        raw_sha256=hashlib.sha256(SAMPLE_JSON).hexdigest(),
        source_url=SOURCE_URL,
        content_type=CONTENT_TYPE,
    )


def test_un_comtrade_trade_fixture_normalizes_bounded_bilateral_trade_slice():
    normalized = _normalized_from_sample()

    assert normalized["source_code"] == "UN_COMTRADE_TRADE"
    assert normalized["provider_dataset_code"] == "UN_COMTRADE:PUBLIC_PREVIEW:C:A:HS"
    assert normalized["frequency"] == "A"
    assert normalized["period_range"] == "2023-2023"
    assert normalized["row_count"] == 2
    assert normalized["expected_row_count"] == 2
    assert normalized["input_filters"] == {
        "typeCode": "C",
        "freqCode": "A",
        "classification": "HS",
        "reporterCode": 842,
        "reporterISO": "USA",
        "partnerCode": 392,
        "partnerISO": "JPN",
        "flowCode": ["M", "X"],
        "cmdCode": "TOTAL",
        "period": "2023",
        "includeDesc": True,
        "scope": "bounded TASK-060 UN Comtrade bilateral total-goods trade evidence slice",
    }
    assert {(row["trade_direction_code"], row["value"]) for row in normalized["rows"]} == {
        ("M", 151580564290),
        ("X", 76154045176),
    }

    import_row = normalized["rows"][0]
    assert import_row["provider_indicator_code"] == "TRADE_VALUE_TOTAL_GOODS_M"
    assert import_row["provider_indicator_label"] == "Import trade value, total goods"
    assert import_row["territory_code"] == "USA"
    assert import_row["territory_label"] == "USA"
    assert import_row["provider_period_code"] == "2023"
    assert import_row["unit_code"] == "CURRENT_USD"
    assert import_row["unit_label"] == "Current US dollars"
    assert import_row["decimal_precision"] == 0
    assert import_row["attributes"] == {
        "source_provider": "UN Comtrade",
        "reporterCode": 842,
        "reporterISO": "USA",
        "reporterDesc": "USA",
        "partnerCode": 392,
        "partnerISO": "JPN",
        "partnerDesc": "Japan",
        "flowCode": "M",
        "flowDesc": "Import",
        "cmdCode": "TOTAL",
        "cmdDesc": "All Commodities",
        "classificationCode": "H6",
        "classificationSearchCode": "HS",
        "aggrLevel": 0,
        "isAggregate": True,
        "isOriginalClassification": True,
        "value_basis": "cifvalue",
        "fobvalue": None,
        "cifvalue": 151580564290,
        "qtyUnitCode": -1,
        "qtyUnitAbbr": "N/A",
        "qty": 0,
        "netWgt": 0,
        "grossWgt": 0,
        "isReported": False,
        "legacyEstimationFlag": 4,
    }


def test_un_comtrade_trade_observed_package_satisfies_existing_contract_without_contract_evolution():
    package = build_un_comtrade_trade_observed_package(_normalized_from_sample())

    assert package.source_code == "UN_COMTRADE_TRADE"
    assert package.source_name == "UN Comtrade bounded bilateral total-goods trade evidence slice"
    assert package.source_home_url == "https://comtradeplus.un.org/"
    assert package.provider_dataset_code == "UN_COMTRADE:PUBLIC_PREVIEW:C:A:HS"
    assert package.release_key.startswith("UN_COMTRADE_TRADE:TOTAL:USA:JPN:2023-2023:")
    assert package.row_count == 2
    assert package.expected_row_count == 2
    assert package.raw_evidence["source_url"] == SOURCE_URL
    assert package.raw_evidence["raw_artifact_path"] == "data/raw/un_comtrade_trade/un-comtrade-usa-jpn-total-goods-2023-import-export.json"
    assert len(package.raw_evidence["raw_sha256"]) == 64

    observation = package.observations[0]
    assert observation.provider_indicator_code == "TRADE_VALUE_TOTAL_GOODS_M"
    assert observation.provider_indicator_label == "Import trade value, total goods"
    assert observation.provider_territory_code == "USA"
    assert observation.provider_territory_label == "USA"
    assert observation.provider_period_code == "2023"
    assert observation.frequency == "A"
    assert observation.period_year == 2023
    assert observation.unit_code == "CURRENT_USD"
    assert observation.unit_label == "Current US dollars"
    assert observation.value == 151580564290
    assert observation.observation_status == "observed"
    assert observation.decimal_precision == 0
    assert observation.attribute_hash == canonical_attribute_hash(observation.attributes)

    report = validate_observed_package_contract(package)
    assert report.valid is True
    assert report.issues == ()


def test_un_comtrade_trade_replay_and_fingerprint_are_deterministic():
    package = build_un_comtrade_trade_observed_package(_normalized_from_sample())
    replayed = build_un_comtrade_trade_observed_package(_normalized_from_sample())

    comparison = compare_observed_packages(package, replayed)

    assert comparison.equivalent is True
    assert comparison.left_fingerprint == comparison.right_fingerprint
    assert comparison.row_count_match is True
    assert comparison.expected_row_count_match is True
    assert comparison.observation_count_match is True
    assert comparison.differing_observations == ()
    assert len(observed_package_fingerprint(package)) == 64


def test_un_comtrade_trade_module_remains_bounded_source_specific_not_trade_or_provider_framework():
    source = (PROJECT_ROOT / "src" / "macroforge" / "un_comtrade_trade.py").read_text(encoding="utf-8")

    forbidden = [
        "class TradeFramework",
        "class ProductClassificationFramework",
        "class ComtradeClient",
        "class BaseSource",
        "class SourcePlugin",
        "PluginRegistry",
        "CREATE TABLE",
        "INSERT INTO",
        "requests.get",
        "urllib.request",
        "sqlalchemy",
        "api_key",
        "mirror_trade",
        "trade_balance",
    ]
    for token in forbidden:
        assert token not in source


def test_project_un_comtrade_trade_fixture_preserves_live_bounded_evidence_when_present():
    if not RAW_FIXTURE.exists():
        return

    raw_payload = RAW_FIXTURE.read_bytes()
    normalized = normalize_un_comtrade_trade_fixture(
        raw_payload,
        raw_artifact_path=str(RAW_FIXTURE.relative_to(PROJECT_ROOT)),
        raw_sha256=hashlib.sha256(raw_payload).hexdigest(),
        source_url=SOURCE_URL,
        content_type=CONTENT_TYPE,
    )
    package = build_un_comtrade_trade_observed_package(normalized)

    assert normalized["row_count"] == 2
    assert {(row["trade_direction_code"], row["value"]) for row in normalized["rows"]} == {
        ("M", 151580564290),
        ("X", 76154045176),
    }
    assert package.row_count == 2
    assert observed_package_fingerprint(package) == observed_package_fingerprint(build_un_comtrade_trade_observed_package(normalized))
