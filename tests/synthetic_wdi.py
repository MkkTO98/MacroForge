"""Deterministic, independently authored WDI-shaped test evidence.

The payloads model only the structural contracts exercised by the tests. They
contain no acquired provider observations, provider response bytes, or provider
URLs. WDI indicator and country codes retained by bounded source contracts are
identifiers, not copied observation payloads.
"""

from __future__ import annotations

import copy
import itertools
import json
from functools import lru_cache
from typing import Any


YEARS_2000_2023 = tuple(str(year) for year in range(2000, 2024))
SYNTHETIC_SOURCE_URL = "https://example.invalid/macroforge/synthetic-wdi"

FAMILY_SPECS: dict[str, dict[str, Any]] = {
    "macro_indicators": {
        "scope": {
            "task": "TASK-129",
            "mode": "Operational Capability Maturation",
            "countries": ["USA", "DNK", "DEU", "JPN", "CHN", "IND"],
            "indicators": ["NY.GDP.MKTP.CD", "SP.POP.TOTL", "FP.CPI.TOTL.ZG"],
            "date_range": "2019:2023",
            "expected_observation_count": 90,
        },
        "years": tuple(str(year) for year in range(2019, 2024)),
        "missing": False,
    },
    "operational_phase1": {
        "scope": {
            "task": "TASK-132",
            "mode": "Operational Capability Expansion",
            "phase": "WDI Phase 1",
            "indicators": ["NY.GDP.MKTP.CD", "SP.POP.TOTL", "FP.CPI.TOTL.ZG"],
            "date_range": "2000:2023",
            "expected_observation_count": 15_624,
        },
        "years": YEARS_2000_2023,
        "country_count": 217,
        "missing": True,
    },
    "demographics_phase1": {
        "scope": {
            "task": "TASK-133",
            "mode": "Operational Capability Expansion",
            "phase": "WDI Demographics Phase 1",
            "indicators": [
                "SP.POP.TOTL", "SP.POP.GROW", "SP.POP.0014.TO.ZS",
                "SP.POP.1564.TO.ZS", "SP.POP.65UP.TO.ZS",
                "SP.DYN.TFRT.IN", "SP.DYN.LE00.IN", "SP.URB.TOTL.IN.ZS",
            ],
            "date_range": "2000:2023",
            "expected_observation_count": 41_664,
            "non_goals": ["Controlled_Expansion", "KnowledgeForge_implementation", "full_WDI_catalog_ingestion"],
        },
        "years": YEARS_2000_2023,
        "country_count": 217,
        "missing": True,
    },
    "energy_phase1": {
        "scope": {
            "task": "TASK-134",
            "mode": "Operational Capability Expansion",
            "phase": "WDI Energy Phase 1",
            "strategic_criterion": "Knowledge Leverage",
            "indicators": ["EG.USE.PCAP.KG.OE", "EG.ELC.COAL.ZS"],
            "date_range": "2000:2023",
            "expected_observation_count": 10_416,
        },
        "years": YEARS_2000_2023,
        "country_count": 217,
        "missing": True,
    },
    "trade_core": {
        "scope": {
            "task": "TASK-142",
            "mode": "Operational Repository Construction",
            "section": "Trade",
            "section_status_target": "Developing",
            "phase": "WDI Trade Core Operational Dataset",
            "indicators": ["NE.EXP.GNFS.CD", "NE.IMP.GNFS.CD", "NE.EXP.GNFS.ZS", "NE.IMP.GNFS.ZS"],
            "date_range": "2000:2023",
            "expected_observation_count": 20_832,
            "non_goals": ["Controlled_Expansion", "KnowledgeForge_implementation", "full_WDI_catalog_ingestion", "trade_framework"],
        },
        "years": YEARS_2000_2023,
        "country_count": 217,
        "missing": True,
    },
    "financial_accounts_core": {
        "scope": {
            "task": "TASK-143",
            "mode": "Operational Repository Construction",
            "section": "Financial Accounts",
            "section_status_target": "Developing",
            "phase": "WDI Financial Accounts Core Operational Dataset",
            "indicators": ["FS.AST.PRVT.GD.ZS", "FM.LBL.BMNY.GD.ZS", "CM.MKT.LCAP.GD.ZS", "CM.MKT.LDOM.NO"],
            "date_range": "2000:2023",
            "expected_observation_count": 20_832,
            "non_goals": ["Controlled_Expansion", "KnowledgeForge_implementation", "full_WDI_catalog_ingestion", "financial_accounts_framework"],
        },
        "years": YEARS_2000_2023,
        "country_count": 217,
        "missing": True,
    },
}


def _synthetic_country_codes(count: int) -> list[str]:
    codes = ["X" + a + b for a, b in itertools.product("ABCDEFGHIJKLMNOPQRSTUVWXYZ", repeat=2)]
    return codes[:count]


def _country_name(code: str) -> str:
    return f"Synthetic Territory {code}"


def _country_id(code: str) -> str:
    return {"USA": "US", "DNK": "DK", "DEU": "DE", "JPN": "JP", "CHN": "CN", "IND": "IN"}.get(
        code, code[-2:]
    )


def _catalog(countries: list[str]) -> dict[str, Any]:
    return {
        "countries": [
            {
                "id": code,
                "iso2Code": _country_id(code),
                "name": _country_name(code),
                "region": {"id": "SYN", "value": "Synthetic Region"},
                "incomeLevel": {"id": "SYN", "value": "Synthetic Income Group"},
            }
            for code in countries
        ]
    }


def _metadata(total: int) -> dict[str, Any]:
    return {
        "page": 1,
        "pages": 1,
        "per_page": total,
        "total": total,
        "sourceid": "SYNTHETIC-TEST",
        "lastupdated": "2099-01-01",
    }


def _observations(
    indicator: str,
    countries: list[str],
    years: tuple[str, ...],
    indicator_index: int,
    *,
    missing: bool,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for country_index, country in enumerate(countries):
        for year_index, year in enumerate(years):
            is_missing = missing and country_index == len(countries) - 1 and year_index == len(years) - 1
            rows.append(
                {
                    "indicator": {"id": indicator, "value": f"Synthetic Indicator {indicator_index + 1}"},
                    "country": {"id": _country_id(country), "value": _country_name(country)},
                    "countryiso3code": country,
                    "date": year,
                    "value": None if is_missing else indicator_index * 1_000_000 + country_index * 100 + year_index + 0.25,
                    "unit": "",
                    "obs_status": "",
                    "decimal": 2,
                }
            )
    return rows


def _raw_family(spec: dict[str, Any]) -> dict[str, Any]:
    scope = copy.deepcopy(spec["scope"])
    countries = list(scope.get("countries") or _synthetic_country_codes(spec["country_count"]))
    scope["countries"] = countries
    scope["country_count"] = len(countries)
    years = tuple(spec["years"])
    requests = []
    for index, indicator in enumerate(scope["indicators"]):
        observations = _observations(indicator, countries, years, index, missing=spec["missing"])
        requests.append(
            {
                "indicator_code": indicator,
                "url": f"{SYNTHETIC_SOURCE_URL}/{indicator}",
                "response": [_metadata(len(observations)), observations],
            }
        )
    return {"scope": scope, "country_catalog": _catalog(countries), "requests": requests}


def _normalized_smoke() -> dict[str, Any]:
    countries = ["USA", "DNK"]
    indicators = ["NY.GDP.MKTP.CD", "SP.POP.TOTL"]
    years = ("2020", "2021")
    rows = []
    for indicator_index, indicator in enumerate(indicators):
        for country_index, country in enumerate(countries):
            for year_index, year in enumerate(years):
                rows.append(
                    {
                        "source": "World Bank WDI",
                        "indicator_id": indicator,
                        "indicator_name": f"Synthetic Indicator {indicator_index + 1}",
                        "country_id": _country_id(country),
                        "country_name": _country_name(country),
                        "countryiso3code": country,
                        "date": year,
                        "value": indicator_index * 1000 + country_index * 10 + year_index + 0.25,
                        "unit": None,
                        "obs_status": None,
                        "decimal": 2,
                    }
                )
    rows.sort(key=lambda row: (row["indicator_id"], row["countryiso3code"], -int(row["date"])))
    return {
        "source": "World Bank World Development Indicators",
        "support_bundle": "authored synthetic fixture factory",
        "created_at_utc": None,
        "countries": countries,
        "indicators": indicators,
        "date_range": "2020:2021",
        "expected_row_count": 8,
        "row_count": 8,
        "rows": rows,
        "raw_artifacts": [
            {
                "indicator": indicator,
                "url": f"{SYNTHETIC_SOURCE_URL}/{indicator}",
                "status": "synthetic",
                "content_type": "application/json",
                "bytes": 0,
                "sha256": "synthetic-authored-no-provider-payload",
                "row_count": 4,
                "source_metadata": _metadata(4),
                "raw_file": f"synthetic-{index + 1}.json",
            }
            for index, indicator in enumerate(indicators)
        ],
    }


def _energy_bounded() -> dict[str, Any]:
    scope = "bounded TASK-096 WDI energy use and coal-electricity evidence slice"
    countries = ["USA", "CHN"]
    years = ("2020", "2021")
    indicators = ["EG.USE.PCAP.KG.OE", "EG.ELC.COAL.ZS"]
    requests = []
    for index, indicator in enumerate(indicators):
        observations = _observations(indicator, countries, years, index, missing=False)
        requests.append(
            {
                "indicator_code": indicator,
                "url": f"{SYNTHETIC_SOURCE_URL}/{indicator}",
                "response": [_metadata(len(observations)), observations],
            }
        )
    return {"scope": scope, "requests": requests}


@lru_cache(maxsize=None)
def _cached_fixture(family: str) -> dict[str, Any]:
    if family == "normalized_smoke":
        return _normalized_smoke()
    if family == "energy_bounded":
        return _energy_bounded()
    try:
        return _raw_family(FAMILY_SPECS[family])
    except KeyError as exc:
        raise ValueError(f"unknown synthetic WDI fixture family: {family}") from exc


def build_synthetic_wdi_fixture(family: str) -> dict[str, Any]:
    """Return an isolated copy of deterministic synthetic evidence for ``family``."""

    return copy.deepcopy(_cached_fixture(family))


def write_synthetic_wdi_fixture(path: str | Any, family: str) -> Any:
    """Write canonical synthetic evidence and return the destination path."""

    from pathlib import Path

    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(synthetic_fixture_json(family), encoding="utf-8")
    return destination


def synthetic_fixture_json(family: str) -> str:
    """Serialize a family canonically for raw-payload normalizers and hashing tests."""

    return json.dumps(build_synthetic_wdi_fixture(family), indent=2, sort_keys=True) + "\n"
