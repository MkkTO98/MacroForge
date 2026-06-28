from __future__ import annotations

import json
from dataclasses import dataclass, replace
from typing import Any

from macroforge.contract_drift import ContractDriftReport, validate_observed_package_contract
from macroforge.db_helpers import psql_scalar
from macroforge.observed_ingestion import (
    ObservedIngestionPackage,
    ObservedObservation,
    ObservedPackageComparison,
    compare_observed_packages,
)


@dataclass(frozen=True)
class LoadedObservedPackageContractVerification:
    """Deterministic verification evidence for one expected and reconstructed package."""

    expected_contract_report: ContractDriftReport
    loaded_contract_report: ContractDriftReport
    comparison: ObservedPackageComparison


def verify_loaded_observed_package(
    db_name: str,
    expected_package: ObservedIngestionPackage,
) -> ObservedPackageComparison:
    """Compare an expected observed package with the package reconstructed after canonical loading.

    This is a narrow deterministic proof helper for the current WDI/OECD/Eurostat paths.
    It intentionally does not introduce a generalized ingestion framework or loader API.
    """

    observed_package = _loaded_observed_package(db_name, expected_package)
    return compare_observed_packages(expected_package, observed_package)


def verify_loaded_observed_package_contracts(
    db_name: str,
    expected_package: ObservedIngestionPackage,
) -> LoadedObservedPackageContractVerification:
    """Validate expected and reconstructed packages, then compare them deterministically."""

    loaded_package = _loaded_observed_package(db_name, expected_package)
    return LoadedObservedPackageContractVerification(
        expected_contract_report=validate_observed_package_contract(expected_package),
        loaded_contract_report=validate_observed_package_contract(loaded_package),
        comparison=compare_observed_packages(expected_package, loaded_package),
    )


def _loaded_observed_package(db_name: str, expected_package: ObservedIngestionPackage) -> ObservedIngestionPackage:
    source_code = expected_package.source_code
    if source_code == "WDI":
        observations = _wdi_loaded_observations(db_name)
        row_count = _table_count(db_name, "staging.wdi_observation")
    elif source_code == "OECD_NAAG":
        observations = _oecd_loaded_observations(db_name)
        row_count = _table_count(db_name, "staging.oecd_sdmx_observation")
    elif source_code == "EUROSTAT_NAMQ_GDP":
        observations = _eurostat_loaded_observations(db_name)
        row_count = _table_count(db_name, "staging.eurostat_namq_observation")
    else:
        raise ValueError(f"Unsupported source for deterministic verification: {source_code}")

    return replace(
        expected_package,
        row_count=row_count,
        observations=tuple(observations),
    )


def _table_count(db_name: str, table_name: str) -> int:
    return int(psql_scalar(db_name, f"SELECT count(*) FROM {table_name}"))


def _json_rows(db_name: str, sql: str) -> list[dict[str, Any]]:
    payload = psql_scalar(db_name, sql)
    return json.loads(payload or "[]")


def _wdi_loaded_observations(db_name: str) -> list[ObservedObservation]:
    rows = _json_rows(
        db_name,
        """
        WITH source_row AS (
            SELECT source_id FROM meta.source WHERE source_code = 'WDI'
        )
        SELECT COALESCE(jsonb_agg(jsonb_build_object(
            'provider_indicator_code', i.source_indicator_code,
            'provider_indicator_label', i.indicator_name,
            'provider_territory_code', t.iso3_code,
            'provider_territory_label', swo.country_name,
            'provider_period_code', p.period_year::text,
            'frequency', p.frequency,
            'unit_code', u.unit_code,
            'value', fo.value,
            'observation_status', fo.observation_status,
            'attributes', '{}'::jsonb,
            'source_payload', swo.source_payload,
            'attribute_hash', 'empty',
            'period_year', p.period_year,
            'period_quarter', NULL,
            'unit_label', NULL,
            'decimal_precision', swo.decimal_precision
        ) ORDER BY i.source_indicator_code, t.iso3_code, p.period_year DESC), '[]'::jsonb)::text
        FROM curated.fact_observation fo
        JOIN source_row s ON fo.source_id = s.source_id
        JOIN curated.dim_indicator i ON fo.indicator_id = i.indicator_id
        JOIN curated.dim_territory t ON fo.territory_id = t.territory_id
        JOIN curated.dim_period p ON fo.period_id = p.period_id
        JOIN curated.dim_unit u ON fo.unit_id = u.unit_id
        JOIN staging.wdi_observation swo
          ON swo.pipeline_run_id = fo.pipeline_run_id
         AND swo.indicator_code = i.source_indicator_code
         AND swo.country_code = t.iso3_code
         AND swo.period_year = p.period_year;
        """,
    )
    return [ObservedObservation(**row) for row in rows]


def _oecd_loaded_observations(db_name: str) -> list[ObservedObservation]:
    rows = _json_rows(
        db_name,
        """
        WITH source_row AS (
            SELECT source_id FROM meta.source WHERE source_code = 'OECD_NAAG'
        )
        SELECT COALESCE(jsonb_agg(jsonb_build_object(
            'provider_indicator_code', i.source_indicator_code,
            'provider_indicator_label', i.indicator_name,
            'provider_territory_code', t.iso3_code,
            'provider_territory_label', t.iso3_code,
            'provider_period_code', p.period_year::text,
            'frequency', p.frequency,
            'unit_code', u.unit_code,
            'value', fo.value,
            'observation_status', fo.observation_status,
            'attributes', a.attributes,
            'source_payload', oso.source_payload,
            'attribute_hash', a.attribute_hash,
            'period_year', p.period_year,
            'period_quarter', NULL,
            'unit_label', NULL,
            'decimal_precision', oso.decimal_precision
        ) ORDER BY u.unit_code, p.period_year, t.iso3_code), '[]'::jsonb)::text
        FROM curated.fact_observation fo
        JOIN source_row s ON fo.source_id = s.source_id
        JOIN curated.dim_indicator i ON fo.indicator_id = i.indicator_id
        JOIN curated.dim_territory t ON fo.territory_id = t.territory_id
        JOIN curated.dim_period p ON fo.period_id = p.period_id
        JOIN curated.dim_unit u ON fo.unit_id = u.unit_id
        JOIN curated.dim_attribute_set a ON fo.attribute_set_id = a.attribute_set_id
        JOIN staging.oecd_sdmx_observation oso
          ON oso.pipeline_run_id = fo.pipeline_run_id
         AND oso.measure_code = i.source_indicator_code
         AND oso.ref_area_code = t.iso3_code
         AND oso.period_year = p.period_year
         AND oso.unit_measure_code = u.unit_code;
        """,
    )
    return [ObservedObservation(**row) for row in rows]


def _eurostat_loaded_observations(db_name: str) -> list[ObservedObservation]:
    rows = _json_rows(
        db_name,
        """
        WITH source_row AS (
            SELECT source_id FROM meta.source WHERE source_code = 'EUROSTAT_NAMQ_GDP'
        )
        SELECT COALESCE(jsonb_agg(jsonb_build_object(
            'provider_indicator_code', i.source_indicator_code,
            'provider_indicator_label', i.indicator_name,
            'provider_territory_code', etm.provider_territory_code,
            'provider_territory_label', en.provider_geo_name,
            'provider_period_code', epm.provider_period_code,
            'frequency', p.frequency,
            'unit_code', u.unit_code,
            'value', fo.value,
            'observation_status', fo.observation_status,
            'attributes', a.attributes,
            'source_payload', en.source_payload,
            'attribute_hash', a.attribute_hash,
            'period_year', p.period_year,
            'period_quarter', p.period_quarter,
            'unit_label', u.unit_name,
            'decimal_precision', en.decimal_precision
        ) ORDER BY etm.provider_territory_code, epm.provider_period_code), '[]'::jsonb)::text
        FROM curated.fact_observation fo
        JOIN source_row s ON fo.source_id = s.source_id
        JOIN curated.dim_indicator i ON fo.indicator_id = i.indicator_id
        JOIN curated.dim_territory t ON fo.territory_id = t.territory_id
        JOIN curated.dim_period p ON fo.period_id = p.period_id
        JOIN curated.dim_unit u ON fo.unit_id = u.unit_id
        JOIN curated.dim_attribute_set a ON fo.attribute_set_id = a.attribute_set_id
        JOIN meta.provider_territory_mapping etm
          ON etm.source_id = s.source_id
         AND etm.territory_id = t.territory_id
         AND etm.provider_dataset_code = 'namq_10_gdp'
        JOIN meta.provider_period_mapping epm
          ON epm.source_id = s.source_id
         AND epm.period_id = p.period_id
         AND epm.provider_dataset_code = 'namq_10_gdp'
        JOIN staging.eurostat_namq_observation en
          ON en.pipeline_run_id = fo.pipeline_run_id
         AND en.national_accounts_item_code = i.source_indicator_code
         AND en.provider_geo_code = etm.provider_territory_code
         AND en.provider_period_code = epm.provider_period_code
         AND en.unit_code = u.unit_code;
        """,
    )
    return [ObservedObservation(**row) for row in rows]
