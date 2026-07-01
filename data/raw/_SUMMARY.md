# Folder Summary: data/raw

## Purpose
Immutable raw source artifacts and checksums from pipeline runs.

## Contains
<!-- PROJECTFORGE:BEGIN-CONTAINS -->
- `bea/`
- `bis_cbpol/`
- `bls/`
- `ecb_sdw/`
- `eurostat/`
- `eurostat_energy_balance/`
- `fred_yield_curve/`
- `eurostat_input_output/`
- `imf_bop_financial_account/`
- `imf_mfs_ir/`
- `oecd_sdmx/`
- `treasury/`
- `un_comtrade_trade/`
- `wdi/`
- `wdi_demographics/`
<!-- PROJECTFORGE:END-CONTAINS -->

## Active Work
- Contains TASK-005 WDI raw payload copies from the live support bundle.
- Contains TASK-012 fixture-backed OECD/SDMX raw XML evidence at `oecd_sdmx/oecd_sdmx_naag_2020_2021_raw.xml`.
- Contains TASK-019 bounded OECD/SDMX structure/codelist XML evidence at `oecd_sdmx/oecd_sdmx_naag_structure_20260604.xml`.
- Contains TASK-020 Eurostat raw JSON architecture-spike evidence at `eurostat/eurostat-namq-10-gdp-2023q1-2023q2-raw.json`.
- Contains TASK-051 bounded BLS monthly CPI architectural experiment evidence under `bls/`.
- Contains TASK-053 bounded BEA NIPA iTableCore evidence under `bea/`.
- Contains TASK-054 bounded U.S. Treasury Fiscal Data average-interest-rates evidence under `treasury/`.
- Contains TASK-055 bounded ECB SDW EXR monthly EUR/USD SDMX evidence under `ecb_sdw/`.
- Contains TASK-056 bounded IMF MFS_IR interest-rate SDMX evidence under `imf_mfs_ir/`.
- Contains TASK-057 bounded BIS WS_CBPOL central-bank-policy-rate SDMX evidence under `bis_cbpol/`.
- Contains TASK-058 bounded ALFRED GDP revision-vintage CSV evidence under `alfred_gdp_vintage/`.
- Contains TASK-059 bounded ILOSTAT unemployment-rate JSON evidence under `ilostat_unemployment/`.
- Contains TASK-060 bounded UN Comtrade bilateral total-goods trade JSON evidence under `un_comtrade_trade/`.
- Contains TASK-061 bounded WDI demographic foundation JSON evidence under `wdi_demographics/`.
- Contains TASK-062 bounded Eurostat input-output matrix JSON-stat evidence under `eurostat_input_output/`.
- Contains TASK-063 bounded IMF BOP financial-account SDMX XML evidence under `imf_bop_financial_account/`.
- Contains TASK-064 bounded Eurostat energy balance JSON-stat evidence under `eurostat_energy_balance/`.
- Contains TASK-065 bounded FRED monthly U.S. Treasury yield-curve CSV evidence under `fred_yield_curve/`.

## Needs Attention
- Raw files remain ignored by git by default, except the bounded OECD/Eurostat/BLS/BEA/Treasury/ECB/IMF/BIS/ALFRED/ILOSTAT/UN Comtrade/WDI demographic/Eurostat input-output/IMF BOP financial-account/Eurostat energy-balance/FRED yield-curve fixture evidence explicitly unignored for clean-clone reconstruction.
